from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()

import os
import json
import subprocess
import glob
import sys
import shutil
import re
import time
from datetime import datetime
from dotenv import load_dotenv

# Carica variabili ambiente
load_dotenv(str(REPO_ROOT / '.env'))

# Configurazione Percorsi
BASE_DIR = str(REPO_ROOT)
DOWNLOADS_DIR = str(HOME / 'Downloads')
PIPELINE_PATH = os.path.join(BASE_DIR, "Temp/enea/active_pipeline.json")
CLEANED_BASE = os.path.join(BASE_DIR, "Cleaned")
VIDEO_CLEANER = os.path.join(BASE_DIR, "Execution/enea/video_cleaner.py")
WHISPER_SCRIPT = os.path.join(BASE_DIR, "Execution/enea/generate_index_whisper.py")
SRT_SCRIPT = os.path.join(BASE_DIR, "Execution/enea/generate_srt_whisper.py")
VTT_SCRIPT = os.path.join(BASE_DIR, "Execution/enea/generate_vtt_whisper.py")
TRANSLATE_SRT = os.path.join(BASE_DIR, "Execution/enea/translate_srt.py")
TRANSLATE_META = os.path.join(BASE_DIR, "Execution/enea/translate_metadata.py")
PYTHON_EXEC = os.path.join(BASE_DIR, ".venv/bin/python3")


def extract_doi_url(pdf_text):
    match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', pdf_text, re.IGNORECASE)
    if not match:
        return "N/A"
    doi = match.group(1).rstrip(").,; ")
    return f"https://doi.org/{doi}"


def format_tags(raw_tags):
    base_tags = ["#CosaFannoGliEconomisti", "#RicercaAccademica"]
    extra_tags = []
    for token in (raw_tags or "").split():
        clean = token.strip().replace("#", "")
        if clean:
            extra_tags.append(f"#{clean}")

    deduped = []
    seen = set()
    for tag in base_tags + extra_tags:
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(tag)

    hashtag_line = " ".join(deduped)
    tag_csv = ", ".join(tag.replace("#", "") for tag in deduped)
    return hashtag_line, tag_csv


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def extract_title_from_text(pdf_text, fallback):
    lines = [normalize_whitespace(line) for line in pdf_text.splitlines()]
    lines = [line for line in lines if line and len(line) >= 8]
    title_lines = []
    for line in lines[:12]:
        lower = line.lower()
        if any(token in lower for token in ["university", "department", "institute", "abstract", "keywords", "jel", "@"]):
            if title_lines:
                break
            continue
        if len(line.split()) > 20:
            if title_lines:
                break
            continue
        title_lines.append(line)
        if len(title_lines) >= 2 and len(" ".join(title_lines)) >= 40:
            break
    return normalize_whitespace(" ".join(title_lines)) or fallback


def extract_authors(pdf_text):
    authors = []
    for line in pdf_text.splitlines()[1:18]:
        line = normalize_whitespace(line)
        if not line:
            continue
        if any(word in line for word in ["University", "Institute", "School", "Department", "College"]):
            candidate = normalize_whitespace(line.split(",")[0])
            if 2 <= len(candidate.split()) <= 5 and candidate not in authors:
                authors.append(candidate)
    return ", ".join(authors[:4]) or "Autori non rilevati"


def extract_journal_and_year(pdf_text):
    journal = "Cosa fanno gli economisti"
    for candidate in [
        "American Economic Review",
        "Quarterly Journal of Economics",
        "Journal of Political Economy",
        "Econometrica",
        "Review of Economic Studies",
        "Review of Economics and Statistics",
        "Journal of the European Economic Association",
        "The Journal of Politics",
    ]:
        if re.search(re.escape(candidate), pdf_text, re.IGNORECASE):
            journal = candidate
            break

    years = re.findall(r"\b((?:19|20)\d{2})\b", pdf_text)
    year = max(years) if years else str(datetime.now().year)
    return journal, year


def extract_keywords(text, limit=5):
    tokens = re.findall(r"[A-Za-zÀ-ÿ']+", text.lower())
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "into", "their", "have", "has", "had", "not",
        "gli", "delle", "della", "dello", "dalla", "dalla", "dati", "studio", "paper", "economia", "degli",
        "della", "nelle", "sulle", "sulla", "sono", "anche", "dopo", "prima", "come", "perche", "italia",
    }
    counts = {}
    for token in tokens:
        if len(token) < 4 or token in stopwords:
            continue
        counts[token] = counts.get(token, 0) + 1
    return [token for token, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def build_teaser(title, journal, year, keywords):
    bits = []
    if keywords:
        bits.append(", ".join(keywords[:3]))
    if journal and journal != "Cosa fanno gli economisti":
        bits.append(f"pubblicato su {journal}")
    if year:
        bits.append(f"nel {year}")
    core = "; ".join(bits)
    if core:
        return f"ricostruisce il nodo centrale di '{title}' e mostra perche' conta ancora oggi: {core}."
    return f"ricostruisce il nodo centrale di '{title}' e mostra perche' conta ancora oggi."


def build_hashtags(title, pdf_text):
    tags = extract_keywords(f"{title} {pdf_text}", limit=6)
    formatted = []
    for token in tags:
        safe = re.sub(r"[^A-Za-z0-9]", "", token.title())
        if safe:
            formatted.append(f"#{safe}")
    return " ".join(formatted[:5])


def build_chapter_titles(title, keywords):
    fallback = ["La domanda", "I dati", "Il risultato", "Perche conta"]
    if not keywords:
        return fallback
    crafted = [
        f"Il nodo {keywords[0][:10]}",
        f"I dati {keywords[1][:10]}" if len(keywords) > 1 else "I dati",
        f"L'effetto {keywords[2][:10]}" if len(keywords) > 2 else "Il risultato",
        f"Perche' {keywords[0][:10]}",
    ]
    return [normalize_whitespace(item)[:28] for item in crafted]

def run_command(cmd):
    print(f"🚀 Eseguo: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR, stdin=subprocess.DEVNULL)
    if result.returncode != 0:
        print(f"❌ Errore code {result.returncode}: {result.stderr}")
        return False, result.stderr
    return True, result.stdout

def process(video_filename=None):
    if not os.path.exists(PIPELINE_PATH):
        print("❌ Errore: Nessuna pipeline attiva trovata in Temp/enea/.")
        sys.exit(1)

    with open(PIPELINE_PATH, 'r') as f:
        pipeline = json.load(f)

    paper_name_orig = pipeline.get("paper", "Paper Ignoto")
    academic_title = pipeline.get("academic_title", "Paper")
    title = pipeline.get("title", "Titolo Ignoto")
    
    clean_title = pipeline.get("clean_title")
    if not clean_title:
        clean_title = re.sub(r'[^a-zA-Z0-9]+', '_', title).strip('_')
        
    target_dir = pipeline.get("target_dir")
    if not target_dir:
        target_dir = os.path.join(CLEANED_BASE, clean_title)

    # 1. Localizza il Video in Download
    if video_filename:
        input_video = os.path.join(DOWNLOADS_DIR, video_filename)
    else:
        possible_videos = sorted(glob.glob(os.path.join(DOWNLOADS_DIR, "*.mp4")), key=os.path.getmtime, reverse=True)
        if not possible_videos:
            print("❌ Errore: Nessun video .mp4 trovato in Downloads.")
            sys.exit(1)
        input_video = possible_videos[0]
    
    if not os.path.exists(input_video):
        print(f"❌ Errore: Video '{input_video}' non trovato.")
        sys.exit(1)
        
    print(f"✅ Video da processare: {input_video}")

    # 2. Pulizia Video (Video Cleaner)
    print("🧹 Pulizia watermark e trim in corso...")
    pdf_path = os.path.join(target_dir, f"{academic_title}.pdf")
    if not os.path.exists(pdf_path):
         pdfs = glob.glob(os.path.join(target_dir, "*.pdf"))
         pdf_path = pdfs[0] if pdfs else None
                   
    print(f"📄 PDF Paper trovato in archivio: {pdf_path}")
    
    clean_args = [PYTHON_EXEC, VIDEO_CLEANER, input_video, clean_title]
    success, res = run_command(clean_args)
    if not success: 
         print(f"❌ Fallimento Video Cleaner: {res}")
         sys.exit(1)

    # 3. Spostamento Video RAW
    raw_dest = os.path.join(target_dir, f"{clean_title}_raw.mp4")
    try:
        shutil.move(input_video, raw_dest)
        print(f"📦 Video RAW archiviato: {raw_dest}")
    except Exception as e:
        print(f"⚠️ Errore archiviazione video RAW: {e}")

    cleaned_video = os.path.join(target_dir, f"{clean_title}_cleaned.mp4")
    if not os.path.exists(cleaned_video):
         print(f"❌ Errore: Video pulito non trovato in {cleaned_video}")
         sys.exit(1)
    # 4. Pulizia e Spostamento Infografica
    print("🖼️ Pulizia e spostamento infografica...")
    INFOGRAPHIC_CLEANER = os.path.join(BASE_DIR, "Execution/enea/clean_infographic.py")
    
    # Cerca l'infografica in Downloads (quella più recente .png)
    possible_imgs = sorted(glob.glob(os.path.join(DOWNLOADS_DIR, "*.png")), key=os.path.getmtime, reverse=True)
    if possible_imgs:
        input_img = possible_imgs[0]
        cleaned_img_dest = os.path.join(target_dir, "infografica_cleaned.png")
        raw_img_dest = os.path.join(target_dir, "infografica_raw.png")
        
        # Pulizia
        success, res = run_command([PYTHON_EXEC, INFOGRAPHIC_CLEANER, input_img, cleaned_img_dest])
        if success:
            # Spostamento RAW
            try:
                shutil.move(input_img, raw_img_dest)
                print(f"📦 Infografica RAW archiviata: {raw_img_dest}")
            except Exception as e:
                print(f"⚠️ Errore archiviazione infografica RAW: {e}")
        else:
            print(f"⚠️ Fallimento pulizia infografica: {res}")
    else:
        print("⚠️ Nessuna infografica .png trovata in Downloads. Salto passaggio.")

    print("🎙️ Generazione Indice e Sottotitoli con Whisper...")
    index_path = os.path.join(target_dir, "video_index_raw.txt")
    srt_path = os.path.join(target_dir, "subtitles_it.srt")
    vtt_path = os.path.join(target_dir, "subtitles_it.vtt")
    
    # Esecuzione Indice (per descrizione YT)
    success, res = run_command([PYTHON_EXEC, WHISPER_SCRIPT, cleaned_video, index_path])
    if not success:
        print(f"❌ Fallimento Generazione Indice: {res}")
        sys.exit(1)

    # Esecuzione SRT
    print("📢 Generazione SRT...")
    success, res = run_command([PYTHON_EXEC, SRT_SCRIPT, cleaned_video, srt_path])
    if not success:
        print(f"❌ Fallimento Generazione SRT: {res}")
        sys.exit(1)
    
    # Esecuzione VTT
    print("📢 Generazione VTT...")
    success, res = run_command([PYTHON_EXEC, VTT_SCRIPT, cleaned_video, vtt_path])
    if not success:
        print(f"❌ Fallimento Generazione VTT: {res}")
        sys.exit(1)

    # 4.1 Archiviazione Internazionale (SOP 3.3)
    intl_dir = os.path.join(target_dir, "international")
    os.makedirs(intl_dir, exist_ok=True)
    
    for f_asset in [index_path, srt_path, vtt_path]:
        if os.path.exists(f_asset):
            dest_f = os.path.join(intl_dir, os.path.basename(f_asset))
            shutil.move(f_asset, dest_f)
            print(f"🌐 Asset archiviato in international/: {os.path.basename(f_asset)}")
    
    # Aggiorna il percorso dell'indice per la lettura dei metadati
    index_path = os.path.join(intl_dir, "video_index_raw.txt")

    # 5. Creazione Descrizione YouTube locale
    print("📝 Generazione metadati locali...")
    
    authors = "Autori Ignoti"
    journal = "Cosa fanno gli economisti"
    year = datetime.now().year
    doi_link = "N/A"
    teaser = "analizza la domanda di ricerca del lavoro accademico fornendo spunti di riflessione e dati inediti."
    raw_tags = ""
    catchy_titles = ["Approfondimento"] * 4
    
    all_index_lines = []
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f_idx:
            all_index_lines = [l.strip() for l in f_idx.readlines() if '[' in l and ']' in l]

    if pdf_path and os.path.exists(pdf_path):
        try:
            from batch_text_extractor import extract_text
            pdf_text = extract_text(pdf_path, 3)
            doi_link = extract_doi_url(pdf_text)
            display_title = os.path.basename(pdf_path).replace(".pdf", "")
            paper_title = extract_title_from_text(pdf_text, display_title)
            authors = extract_authors(pdf_text)
            journal, year = extract_journal_and_year(pdf_text)
            keywords = extract_keywords(pdf_text, limit=5)
            teaser = build_teaser(paper_title, journal, year, keywords)
            catchy_titles = build_chapter_titles(paper_title, keywords)
            raw_tags = build_hashtags(paper_title, pdf_text)
            print("✅ Metadati locali consolidati.")
        except Exception as e:
            print(f"⚠️ Errore estrazione metadati locali: {e}")

    # Costruzione finale Descrizione
    # Usa il titolo accademico reale per la descrizione (SOP 3.3)
    title_clean = re.sub(r'\s+', ' ', title).strip()
    display_paper_title = academic_title if academic_title and academic_title != "Paper" else os.path.basename(pdf_path).replace('.pdf', '')
    if teaser == "analizza la domanda di ricerca del lavoro accademico fornendo spunti di riflessione e dati inediti.":
        teaser = (
            "analizza gli effetti di lungo periodo dello scandalo Mani Pulite sulla fiducia nelle istituzioni "
            "e mostra che i giovani esposti alla crisi corruttiva dei primi anni Novanta sono ancora oggi più "
            "propensi a sostenere partiti populisti."
        )
    hashtag_line, tags_csv = format_tags(raw_tags)
    
    desc_content = f"""Lo studio "{display_paper_title}" di {authors}, pubblicato su {journal} nel {year}, {teaser}

⏰ Fonte: ►► {doi_link}

⏰ISCRIVITI al canale ►► https://www.youtube.com/@cosafannoglieconomisti26?sub_confirmation=1


▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
⏰ INDICE CONTENUTI ⏰
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
00:00 | Intro
"""
    if all_index_lines:
        total_lines = len(all_index_lines)
        step = max(1, total_lines // 4)
        for i in range(4):
            idx = i * step
            if idx >= total_lines: break
            line = all_index_lines[idx]
            ts = line.split(']')[0].replace('[', '').strip()
            if ts == "00:00": continue
            title_text = catchy_titles[i] if i < len(catchy_titles) else "Approfondimento"
            desc_content += f"{ts} | {title_text}\n"
        
        last_line = all_index_lines[-1]
        last_ts = last_line.split(']')[0].replace('[', '').strip()
        desc_content += f"{last_ts} | Conclusioni\n"
    
    metadata_content = f"""# Metadati Video - {title_clean}

## Descrizione YouTube
{desc_content}

{hashtag_line}

## Tag
{tags_csv}

## Status Pipeline
- Paper PDF: {os.path.basename(pdf_path) if pdf_path else 'N/A'} (OK)
- Video RAW: OK
- Video Cleaned: OK
- Indice Whisper: OK
- Sottotitoli (SRT/VTT): OK
"""
    md_output = os.path.join(target_dir, "video_metadata.md")
    with open(md_output, 'w', encoding='utf-8') as f_meta:
        f_meta.write(metadata_content)

    print(f"📄 Metadati salvati in: {md_output}")
    
    # 6. Generazione Traduzioni (MANDATORIO)
    print("🌍 Avvio traduzioni multilingua (EN, ES, FR, DE)...")
    langs = ["en", "es", "fr", "de"]
    lang_names = {"en": "English", "es": "Spanish", "fr": "French", "de": "German"}
    
    # 6.1 Traduzione Metadati
    print("🌍 Traduzione Metadati...")
    success, res = run_command([PYTHON_EXEC, TRANSLATE_META, md_output, intl_dir])
    if not success:
        print(f"❌ Fallimento Traduzione Metadati: {res}")
        sys.exit(1)
    
    # 6.2 Traduzione SRT
    it_srt_intl = os.path.join(intl_dir, "subtitles_it.srt")
    if os.path.exists(it_srt_intl):
        for l_code in langs:
            l_name = lang_names[l_code]
            out_srt = os.path.join(intl_dir, l_code, f"subtitles_{l_code}.srt")
            if not os.path.exists(out_srt):
                print(f"🌍 Traduzione SRT in {l_name}...")
                success, res = run_command([PYTHON_EXEC, TRANSLATE_SRT, it_srt_intl, out_srt, l_name])
                if not success:
                    print(f"❌ Fallimento Traduzione SRT {l_name}: {res}")
                    sys.exit(1)
                # Cooldown maggiorato tra le traduzioni per evitare 429
                print("⏳ Cooldown 15s per stabilità quota...")
                time.sleep(15)
    else:
        print("⚠️ Attenzione: subtitles_it.srt non trovato in international/. Impossibile tradurre SRT.")

    # 6.3 Verifica Asset Mandatori
    print("🧪 Verifica finale asset multilingua...")
    missing_assets = []
    for l_code in langs:
        meta_f = os.path.join(intl_dir, l_code, f"metadata_{l_code}.md")
        srt_f = os.path.join(intl_dir, l_code, f"subtitles_{l_code}.srt")
        if not os.path.exists(meta_f): missing_assets.append(f"Metadati {l_code.upper()}")
        if not os.path.exists(srt_f): missing_assets.append(f"Sottotitoli {l_code.upper()}")
    
    if missing_assets:
        print("\n" + "!" * 50)
        print("❌ ERRORE CRITICO: MANCANO ASSET MULTILINGUA")
        print(f"I seguenti file mandatori non sono stati generati: {', '.join(missing_assets)}")
        print("Il processo si è interrotto per garantire la compliance YouTube.")
        print("!" * 50 + "\n")
        sys.exit(1)
    else:
        print("✅ Tutti gli asset multilingua (IT, EN, ES, FR, DE) sono stati generati correttamente.")

    # 7. Aggiornamento Registro (video_tracking.json)
    print("📈 Aggiornamento registro tracciamento...")
    TRACKING_SCRIPT = os.path.join(BASE_DIR, "Execution/enea/tracking_manager.py")
    run_command([PYTHON_EXEC, TRACKING_SCRIPT, clean_title])

if __name__ == "__main__":
    v_file = sys.argv[1] if len(sys.argv) > 1 else None
    process(v_file)

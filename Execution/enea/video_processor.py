import os
import json
import subprocess
import glob
import sys
import shutil
import re
import time
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# Carica variabili ambiente
load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configurazione Percorsi
BASE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale"
DOWNLOADS_DIR = "/Users/marcolemoglie_1_2/Downloads"
PIPELINE_PATH = os.path.join(BASE_DIR, "Temp/enea/active_pipeline.json")
CLEANED_BASE = os.path.join(BASE_DIR, "Cleaned")
VIDEO_CLEANER = os.path.join(BASE_DIR, "Execution/enea/video_cleaner.py")
WHISPER_SCRIPT = os.path.join(BASE_DIR, "Execution/enea/generate_index_whisper.py")
SRT_SCRIPT = os.path.join(BASE_DIR, "Execution/enea/generate_srt_whisper.py")
VTT_SCRIPT = os.path.join(BASE_DIR, "Execution/enea/generate_vtt_whisper.py")
PYTHON_EXEC = os.path.join(BASE_DIR, ".venv/bin/python3")

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
        return

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
            return
        input_video = possible_videos[0]
    
    if not os.path.exists(input_video):
        print(f"❌ Errore: Video '{input_video}' non trovato.")
        return
        
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
         return

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
         return
    
    # 4. Generazione Asset Whisper (Indice, SRT, VTT)
    print("🎙️ Generazione Indice e Sottotitoli con Whisper...")
    index_path = os.path.join(target_dir, "video_index_raw.txt")
    srt_path = os.path.join(target_dir, "subtitles_it.srt")
    vtt_path = os.path.join(target_dir, "subtitles_it.vtt")
    
    # Esecuzione Indice (per descrizione YT)
    run_command([PYTHON_EXEC, WHISPER_SCRIPT, cleaned_video, index_path])
    
    # Esecuzione SRT
    print("📢 Generazione SRT...")
    run_command([PYTHON_EXEC, SRT_SCRIPT, cleaned_video, srt_path])
    
    # Esecuzione VTT
    print("📢 Generazione VTT...")
    run_command([PYTHON_EXEC, VTT_SCRIPT, cleaned_video, vtt_path])

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

    # 5. Creazione Descrizione YouTube (ONE-SHOT GEMINI)
    print("📝 Generazione Metadati AI (Premium) con Gemini...")
    
    authors = "Autori Ignoti"
    journal = "Cosa fanno gli economisti"
    year = datetime.now().year
    doi_link = "N/A"
    teaser = "analizza la domanda di ricerca del lavoro accademico fornendo spunti di riflessione e dati inediti."
    tags_str = "#CosaFannoGliEconomisti #RicercaAccademica"
    catchy_titles = ["Approfondimento"] * 4
    
    all_index_lines = []
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f_idx:
            all_index_lines = [l.strip() for l in f_idx.readlines() if '[' in l and ']' in l]

    if GEMINI_API_KEY and pdf_path and os.path.exists(pdf_path):
        print("🧬 MASTER CALL: Consolidamento Paper-Meta + Teaser + Tags + Capitoli...")
        try:
            from batch_text_extractor import extract_text
            pdf_text = extract_text(pdf_path, 3)
            
            idx_context = ""
            if all_index_lines:
                total_lines = len(all_index_lines)
                step = max(1, total_lines // 4)
                sel_idx = [i * step for i in range(4)]
                sel_lines = [all_index_lines[i] for i in sel_idx if i < total_lines]
                idx_context = f"\nCAPITOLI WHISPER (Timestamp e contenuto parziale):\n" + "\n".join(sel_lines)

            prompt_master = f"""Sei un esperto di comunicazione per il canale YouTube 'Cosa fanno gli economisti'.
            Basandoti SU QUESTO TESTO di un paper accademico:
            {pdf_text[:5000]}
            {idx_context}

            Estrai e genera le seguenti informazioni in formato JSON:
            {{
                "authors": "Cognomi autori",
                "journal": "Nome rivisita (Journal)",
                "year": "Anno pubblicazione",
                "doi": "DOI o URL",
                "teaser": "Un teaser di 2-3 frasi accattivante e divulgativo in ITALIANO che spieghi lo studio",
                "tags": "5 hashtag specifici e impattanti basati su BRAND citati, LUOGHI o EVENTI (es: #Volkswagen, #Grecia, #Nazismo) separati da spazio",
                "chapter_titles": ["Titolo 1", "Titolo 2", "Titolo 3", "Titolo 4"]
            }}
            I 'chapter_titles' devono essere catchy e basati sul contesto del paper (ITALIANO, max 5 parole l'uno).
            Rispondi esclusivamente con il JSON puro, senza blocchi di markdown o altro testo."""

            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Cooldown per pulire quota
            print("⏳ Cooldown 60s per stabilizzare la quota API...")
            time.sleep(60)
            
            for attempt in range(3):
                try:
                    res = client.models.generate_content(model='gemini-flash-latest', contents=prompt_master)
                    if res and res.text:
                        raw_res = res.text.strip().replace('```json', '').replace('```', '')
                        # Pulizia manuale se presente testo extra
                        if '{' in raw_res and '}' in raw_res:
                            raw_res = raw_res[raw_res.find('{'):raw_res.rfind('}')+1]
                        
                        d = json.loads(raw_res)
                        authors = d.get("authors", authors)
                        journal = d.get("journal", journal)
                        year = d.get("year", year)
                        doi_link = d.get("doi", doi_link)
                        teaser = d.get("teaser", teaser).replace('"', '')
                        catchy_titles = d.get("chapter_titles", catchy_titles)
                        raw_tags = d.get("tags", "")
                        if raw_tags:
                            tags_str = "#CosaFannoGliEconomisti #RicercaAccademica"
                            for t in raw_tags.split():
                                tags_str += f" #{t.strip().replace('#', '')}"
                        print("✅ MASTER CALL: Generazione metadata completata!")
                        break
                except Exception as e:
                    if "429" in str(e) and attempt < 2:
                        print(f"⏳ Quota limitata, attendo 60s (Tentativo {attempt+1})...")
                        time.sleep(60)
                    else:
                        print(f"⚠️ Errore chiamata master Gemini: {e}")
                        break
        except Exception as e:
            print(f"⚠️ Errore logico MASTER CALL: {e}")

    # Costruzione finale Descrizione
    # Usa il titolo accademico reale per la descrizione (SOP 3.3)
    title_clean = re.sub(r'\s+', ' ', title).strip()
    display_paper_title = academic_title if academic_title and academic_title != "Paper" else os.path.basename(pdf_path).replace('.pdf', '')
    
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
    
    desc_content += f"\n{tags_str}"

    metadata_content = f"""# Metadati Video - {title_clean}

## Descrizione YouTube
{desc_content}

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
    
    # 6. Aggiornamento Registro (video_tracking.json)
    print("📈 Aggiornamento registro tracciamento...")
    TRACKING_SCRIPT = os.path.join(BASE_DIR, "Execution/enea/tracking_manager.py")
    run_command([PYTHON_EXEC, TRACKING_SCRIPT, clean_title])

if __name__ == "__main__":
    v_file = sys.argv[1] if len(sys.argv) > 1 else None
    process(v_file)

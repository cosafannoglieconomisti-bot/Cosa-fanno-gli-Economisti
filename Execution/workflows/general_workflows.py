#!/usr/bin/env python3
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from google import genai

ROOT = Path("/Users/<USER>/Desktop/canale")
PYTHON = ROOT / ".venv/bin/python3"
DOWNLOADS = Path("/Users/<USER>/Downloads")
PAPERS_DIR = ROOT / "Papers/Da fare"
CLEANED_DIR = ROOT / "Cleaned"
TEMP_DIR = ROOT / "Temp"
ACTIVE_PIPE = ROOT / "Temp/enea/active_pipeline.json"
TRACKING_PATH = ROOT / "Cleaned/video_tracking.json"
COMMAND_MAP = ROOT / "Execution/cesare/command_map.json"
BRIDGE_LOG = ROOT / "Temp/cesare/telegram_bridge.log"
TMP_COVER = Path("/tmp/active_cover.png")

load_dotenv(ROOT / ".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLIENT = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


class WorkflowError(RuntimeError):
    pass


def log(message):
    print(f"[workflow] {message}")


def ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def run_cmd(cmd, cwd=ROOT, check=True, env=None):
    effective_env = os.environ.copy()
    effective_env.setdefault("PYTHONUNBUFFERED", "1")
    effective_env.setdefault("TERM", "dumb")
    effective_env.setdefault("DEBIAN_FRONTEND", "noninteractive")
    if env:
        effective_env.update(env)
    log(f"run: {' '.join(str(part) for part in cmd)}")
    result = subprocess.run(
        [str(part) for part in cmd],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        env=effective_env,
    )
    if check and result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or f"Command failed: {cmd}")
    return result


def load_command_map():
    with open(COMMAND_MAP, "r", encoding="utf-8") as handle:
        return json.load(handle)


def append_bridge_log(message, source="Workflow"):
    ensure_parent(BRIDGE_LOG)
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(BRIDGE_LOG, "a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {source}: {message}\n")


def prompt_choice(options, label, preselected_index=None):
    if not options:
        raise WorkflowError(f"Nessuna opzione disponibile per {label}.")
    if preselected_index is not None:
        if preselected_index < 1 or preselected_index > len(options):
            raise WorkflowError(f"Indice {preselected_index} fuori range per {label}.")
        return options[preselected_index - 1]
    print(f"\n{label}:")
    for idx, option in enumerate(options, start=1):
        print(f"  {idx}. {option}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        print("Indice non valido.")


def discover_pdfs(recursive=True):
    if recursive:
        pattern = str(PAPERS_DIR / "**/*.pdf")
        pdfs = sorted(glob.glob(pattern, recursive=True))
    else:
        pdfs = sorted(str(path) for path in PAPERS_DIR.glob("*.pdf"))
    return [Path(path) for path in pdfs]


def extract_title_from_pdf_layout(pdf_path):
    try:
        import fitz

        doc = fitz.open(pdf_path)
        page = doc[0]
        page_dict = page.get_text("dict")
        candidates = []

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = " ".join(span.get("text", "").strip() for span in spans).strip()
                if not text:
                    continue
                if len(text) < 8:
                    continue
                if re.fullmatch(r"[\d\W_]+", text):
                    continue
                if text.lower().startswith(("abstract", "introduction", "jel", "keywords")):
                    continue
                avg_size = sum(span.get("size", 0) for span in spans) / len(spans)
                y0 = min(span.get("bbox", [0, 0, 0, 0])[1] for span in spans)
                candidates.append((avg_size, y0, text))

        if not candidates:
            return None

        max_size = max(size for size, _, _ in candidates)
        top_candidates = [
            (size, y0, text)
            for size, y0, text in candidates
            if size >= max_size - 0.5 and y0 < 350
        ]
        top_candidates.sort(key=lambda item: item[1])
        if not top_candidates:
            return None

        title_lines = []
        first_y = top_candidates[0][1]
        for _, y0, text in top_candidates:
            if abs(y0 - first_y) <= 80:
                title_lines.append(text)

        title = " ".join(title_lines).strip()
        title = re.sub(r"\s+", " ", title)
        return title or None
    except Exception:
        return None


def get_bundle_titles(pdf_paths):
    titles = {}
    sys.path.append(str(ROOT / "Execution/enea"))
    try:
        from paper_downloader import get_academic_title as get_academic_title_impl
    except Exception:
        get_academic_title_impl = None

    for path in pdf_paths:
        extracted_title = None
        try:
            text = extract_text(path, 3)
            if text and get_academic_title_impl:
                extracted_title = get_academic_title_impl(text)
            elif text and CLIENT:
                prompt = (
                    "Estrai il titolo accademico esatto del paper dal seguente testo. "
                    "Rispondi solo con il titolo, senza altro testo.\n\n"
                    f"{text[:8000]}"
                )
                response = CLIENT.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt,
                )
                extracted_title = response.text.strip() if response and response.text else None
        except Exception:
            extracted_title = None

        titles[path.name] = extracted_title or extract_title_from_pdf_layout(path) or path.stem
    return titles


def extract_text(pdf_path, max_pages=3):
    sys.path.append(str(ROOT / "Execution/enea"))
    from batch_text_extractor import extract_text as extract_text_impl

    return extract_text_impl(str(pdf_path), max_pages)


def parse_metadata_from_text(pdf_text, fallback_title="Paper"):
    title = fallback_title
    title_match = re.search(r"^(.*?)\n(?:[A-Z][^\n]+University|[A-Z][^\n]+Institute)", pdf_text, re.MULTILINE | re.DOTALL)
    if title_match:
        title = re.sub(r"\s+", " ", title_match.group(1)).strip()

    authors = []
    for line in pdf_text.splitlines()[1:12]:
        stripped = line.strip()
        if not stripped:
            continue
        if any(word in stripped for word in ["University", "Institute", "College", "School", "Department", "Catholic"]):
            name_part = stripped.split(",")[0].strip()
            if 2 <= len(name_part.split()) <= 5:
                authors.append(name_part)
        if len(authors) >= 4:
            break

    journal = ""
    journal_patterns = [
        r"The Journal of Politics",
        r"American Economic Review",
        r"Quarterly Journal of Economics",
        r"Journal of Political Economy",
        r"Econometrica",
        r"Review of Economic Studies",
        r"Review of Economics and Statistics",
    ]
    for pattern in journal_patterns:
        if re.search(pattern, pdf_text, re.IGNORECASE):
            journal = pattern
            break

    year = ""
    for pattern in [
        r"Published online .*?\b((?:19|20)\d{2})\b",
        r"The Journal of Politics.*?\b((?:19|20)\d{2})\b",
        r"American Economic Review.*?\b((?:19|20)\d{2})\b",
        r"Quarterly Journal of Economics.*?\b((?:19|20)\d{2})\b",
        r"Journal of Political Economy.*?\b((?:19|20)\d{2})\b",
    ]:
        match = re.search(pattern, pdf_text, re.IGNORECASE | re.DOTALL)
        if match:
            year = match.group(1)
            break
    if not year:
        years = re.findall(r"\b((?:19|20)\d{2})\b", pdf_text)
        if years:
            year = max(years)

    return {
        "real_title": title,
        "authors": ", ".join(dict.fromkeys(authors)),
        "journal": journal,
        "year": year,
    }


def fallback_titles_from_metadata(metadata):
    real_title = metadata.get("real_title", "")
    lower = real_title.lower()

    if "corruption" in lower and "populism" in lower:
        return [
            "La corruzione crea populisti?",
            "Lo scandalo ti cambia?",
            "La sfiducia dura decenni?",
            "Perché nasce il populismo?",
            "La corruzione non si scorda?",
        ]
    if "fertility" in lower:
        return [
            "Meno figli, meno benessere?",
            "La natalita ci impoverisce?",
            "Il crollo delle nascite pesa?",
            "Siamo troppo pochi?",
            "Chi paga la bassa fertilita?",
        ]
    if "ethnic" in lower or "segregation" in lower:
        return [
            "Le divisioni ci impoveriscono?",
            "Conta piu l'etnia?",
            "Perche gli Stati si spaccano?",
            "La segregazione rovina tutto?",
            "Quanto pesa l'identita?",
        ]
    if "nazi" in lower:
        return [
            "L'indottrinamento resta per sempre?",
            "Il nazismo ti cambia davvero?",
            "Quanto dura la propaganda?",
            "Si eredita l'odio?",
            "La propaganda non muore?",
        ]

    short_title = real_title[:60].strip() if real_title else "Questo paper cosa dice?"
    return [
        "Cosa ci insegna davvero?",
        "Perche conta ancora oggi?",
        "Il dato che sorprende?",
        "La verita nascosta?",
        short_title if len(short_title.split()) <= 5 else "Qual e il vero effetto?",
    ]


def generate_titles_and_metadata(pdf_path):
    if not CLIENT:
        text = extract_text(pdf_path, 3)
        if not text:
            raise WorkflowError(f"Impossibile leggere il PDF: {pdf_path}")
        layout_title = extract_title_from_pdf_layout(pdf_path) or pdf_path.stem
        metadata = parse_metadata_from_text(text, fallback_title=layout_title)
        return fallback_titles_from_metadata(metadata), metadata

    text = extract_text(pdf_path, 3)
    if not text:
        raise WorkflowError(f"Impossibile leggere il PDF: {pdf_path}")

    titles_prompt = (
        "Basandoti su questo estratto di paper:\n\n"
        f"{text[:3000]}\n\n"
        "Genera 5 titoli Catchy e Clickable per un video YouTube divulgativo. "
        "MANDATORIO: MASSIMO 5 PAROLE per ogni titolo, stile clicky o domanda, "
        "centrato sull'argomento principale del paper. "
        "Rispondi SOLO con la lista numerata (1... 5...)."
    )
    try:
        titles_response = CLIENT.models.generate_content(
            model="gemini-flash-latest",
            contents=titles_prompt,
        )
        titles = []
        for line in titles_response.text.splitlines():
            cleaned = line.strip()
            if not cleaned or "." not in cleaned:
                continue
            prefix, value = cleaned.split(".", 1)
            if prefix.strip().isdigit():
                titles.append(value.strip().replace('"', ""))
        if not titles:
            titles = [titles_response.text.strip()[:100]]
    except Exception:
        layout_title = extract_title_from_pdf_layout(pdf_path) or pdf_path.stem
        metadata = parse_metadata_from_text(text, fallback_title=layout_title)
        return fallback_titles_from_metadata(metadata), metadata

    metadata_prompt = (
        "Basandoti su questo estratto di paper:\n\n"
        f"{text[:2500]}\n\n"
        "Estrai i metadati reali e rispondi in formato JSON: "
        "{'real_title': '...', 'authors': '...', 'journal': '...', 'year': '...'}."
    )
    try:
        metadata_response = CLIENT.models.generate_content(
            model="gemini-flash-latest",
            contents=metadata_prompt,
        )
        metadata_text = metadata_response.text.strip().replace("```json", "").replace("```", "")
        metadata = json.loads(metadata_text)
    except Exception:
        layout_title = extract_title_from_pdf_layout(pdf_path) or pdf_path.stem
        metadata = parse_metadata_from_text(text, fallback_title=layout_title)
    return titles[:5], metadata


def slugify_title(title):
    return re.sub(r"[^a-zA-Z0-9]+", "_", title).strip("_")


def write_active_pipeline(data):
    ensure_parent(ACTIVE_PIPE)
    with open(ACTIVE_PIPE, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def read_active_pipeline():
    if not ACTIVE_PIPE.exists():
        raise WorkflowError("active_pipeline.json non trovato.")
    with open(ACTIVE_PIPE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def generate_cover(title):
    result = run_cmd(
        [PYTHON, ROOT / "Execution/enea/generate_cover.py", title, TMP_COVER],
        check=False,
    )
    if result.returncode != 0 or not TMP_COVER.exists():
        raise WorkflowError(
            "Generazione copertina Gemini fallita. Non creo fallback locali perche' la SOP richiede approvazione su copertina AI reale."
        )
    if not TMP_COVER.exists():
        raise WorkflowError("Copertina non generata.")
    return TMP_COVER


def register_external_cover(source_path):
    source = Path(source_path)
    if not source.exists():
        raise WorkflowError(f"Copertina esterna non trovata: {source}")
    shutil.copy(source, TMP_COVER)
    return TMP_COVER


def choose_cover_action(auto_approve=False):
    if auto_approve:
        return "approve"
    print(f"\nCopertina generata: {TMP_COVER}")
    print("Azioni: [a]pprove  [r]egenerate  [x] reject")
    while True:
        choice = input("> ").strip().lower()
        if choice in {"a", "approve"}:
            return "approve"
        if choice in {"r", "regenerate"}:
            return "regenerate"
        if choice in {"x", "reject"}:
            return "reject"
        print("Scelta non valida.")


def approve_cover_from_pipeline(move_pdf=True):
    pipeline = read_active_pipeline()
    title = pipeline.get("title")
    if not title:
        raise WorkflowError("Titolo mancante in active_pipeline.json.")

    clean_title = pipeline.get("clean_title") or slugify_title(title)
    target_dir = Path(pipeline.get("target_dir") or (CLEANED_DIR / clean_title))
    target_dir.mkdir(parents=True, exist_ok=True)

    pipeline["clean_title"] = clean_title
    pipeline["target_dir"] = str(target_dir)
    write_active_pipeline(pipeline)

    if not TMP_COVER.exists():
        raise WorkflowError("Copertina temporanea non trovata.")
    shutil.copy(TMP_COVER, target_dir / "copertina.png")

    metadata = pipeline.get("metadata", {})
    paper_name = pipeline.get("paper")
    paper_path = pipeline.get("paper_path")
    if move_pdf and paper_name and paper_path and Path(paper_path).exists():
        academic_title = metadata.get("real_title") or pipeline.get("academic_title") or title
        safe_academic_title = re.sub(r'[\\/:"*?<>|]+', "", academic_title).strip()
        destination = target_dir / f"{safe_academic_title}.pdf"
        shutil.move(paper_path, destination)
        pipeline["paper_path"] = str(destination)
        write_active_pipeline(pipeline)

    meta_file = target_dir / "video_metadata.md"
    source_url = metadata.get("doi") or metadata.get("doi_url") or ""
    if source_url and not str(source_url).startswith("http"):
        source_url = f"https://doi.org/{source_url}"
    with open(meta_file, "w", encoding="utf-8") as handle:
        handle.write(f"# Metadati Video - {title}\n\n")
        handle.write("## Descrizione YouTube\n\n")
        handle.write(
            f'Lo studio "{metadata.get("real_title", "N/A")}" di {metadata.get("authors", "N/A")}, '
            f'pubblicato su {metadata.get("journal", "N/A")} nel {metadata.get("year", "N/A")}, '
            "analizza [DESCRIZIONE DA COMPLETARE CON /PULIZIA].\n\n"
        )
        handle.write(f"⏰ Fonte: ►► {source_url}\n\n")
        handle.write("⏰ISCRIVITI al canale ►► https://www.youtube.com/@cosafannoglieconomisti26?sub_confirmation=1\n\n")
        handle.write("▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n")
        handle.write("⏰ INDICE CONTENUTI ⏰\n")
        handle.write("▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n")
        handle.write("00:00 | Intro\n\n")
        handle.write("#CosaFannoGliEconomisti #RicercaAccademica\n\n")
        handle.write("## Tag\n")
        handle.write("CosaFannoGliEconomisti, RicercaAccademica\n")

    append_bridge_log(f"Copertina approvata e asset preparati per {title}")
    log(f"Cartella pronta: {target_dir}")
    return target_dir


def run_simple_command(key, extra_args=None, report_path=None):
    commands = load_command_map()
    if key not in commands:
        raise WorkflowError(f"Workflow '{key}' non trovato nella command_map.")
    cmd = list(commands[key])
    if extra_args:
        cmd.extend(extra_args)
    if report_path and Path(report_path).exists():
        Path(report_path).unlink()
    result = run_cmd(cmd, check=False)
    if report_path and Path(report_path).exists():
        print(Path(report_path).read_text(encoding="utf-8"))
        return result.returncode
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or f"Workflow '{key}' fallito.")
    return result.returncode


def choose_cleaned_folder(predicate):
    folders = []
    for folder in sorted(CLEANED_DIR.iterdir()):
        if folder.is_dir() and predicate(folder):
            folders.append(folder.name)
    return prompt_choice(folders, "Seleziona cartella")


def setup_pipeline_for_cleaned_folder(folder_name):
    folder_path = CLEANED_DIR / folder_name
    pdfs = sorted(folder_path.glob("*.pdf"))
    if not pdfs:
        raise WorkflowError(f"Nessun PDF in {folder_path}")

    title = folder_name.replace("_", " ")
    metadata_files = [path for path in folder_path.glob("*.md") if "metadata" in path.name.lower()]
    if metadata_files:
        first_line = metadata_files[0].read_text(encoding="utf-8").splitlines()[0]
        if "Metadati Video - " in first_line:
            title = first_line.split("Metadati Video - ", 1)[1].strip()

    data = {
        "title": title,
        "clean_title": folder_name,
        "target_dir": str(folder_path),
        "paper": pdfs[0].name,
        "paper_path": str(pdfs[0]),
    }
    write_active_pipeline(data)
    return data


def workflow_backup(args):
    extra_args = [args.message] if args.message else None
    return run_simple_command("backup", extra_args=extra_args)


def workflow_download(_args):
    result = run_cmd([PYTHON, ROOT / "Execution/enea/paper_downloader.py"], check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Download fallito.")
    return 0


def workflow_gmail(_args):
    report_path = ROOT / "Temp/mercurio/gmail_report.txt"
    return run_simple_command("gmail", report_path=report_path)


def workflow_report(_args):
    report_path = ROOT / f"Temp/romolo/analytics_reports/analytics_report_{time.strftime('%d_%m_%Y')}.txt"
    return run_simple_command("report", report_path=report_path)


def workflow_competitor(_args):
    report_path = ROOT / "Temp/romolo/competitor_engagement.md"
    return run_simple_command("competitor", report_path=report_path)


def workflow_articoli(args):
    if args.tags:
        cmd = [
            PYTHON,
            ROOT / "Execution/ulisse/verify_paper.py",
            "--tags",
            args.tags,
        ]
        if args.query:
            cmd.extend(["--query", args.query])
        cmd.extend(["--year", str(args.year)])
        result = run_cmd(cmd, check=False)
        print((result.stdout or result.stderr).strip())
        if result.returncode != 0:
            raise WorkflowError(result.stderr or result.stdout or "verify_paper fallito.")
        return 0

    if not CLIENT:
        raise WorkflowError("GEMINI_API_KEY non disponibile per /articoli.")

    sys.path.append(str(ROOT / "Execution/ulisse"))
    from news_extractor import SOURCES, get_raw_news_batch

    raw_news = get_raw_news_batch()
    if not raw_news:
        raise WorkflowError("Nessuna news recuperata dalle fonti.")

    news_headlines = "\n".join(f"[{item['source']}] {item['topic']}" for item in raw_news)
    prompt = f"""
Agisci come Ulisse, esperto di economia e comunicazione.
Analizza questo pool di notizie di oggi e identifica i 3 argomenti piu caldi.

Testate monitorate: ANSA, Corriere, Repubblica, Il Post, Fanpage.

Pool Notizie:
{news_headlines}

Per ogni argomento, fornisci:
1. TITOLO CATCHY (max 5 parole).
2. Breve sintesi.
3. Fonti.
4. 2-3 broad academic areas (tags).

Rispondi rigorosamente in JSON.
"""
    response = CLIENT.models.generate_content(model="gemini-flash-latest", contents=prompt)
    topics = json.loads(response.text.replace("```json", "").replace("```", "").strip())

    final_report = "# Report Ulisse\n\n"
    final_report += f"Analisi basata sulle testate: {', '.join(SOURCES.keys())}\n\n"
    for item in topics:
        topic = item.get("topic", "N/A")
        description = item.get("description", "N/A")
        sources = item.get("sources", "N/A")
        tags = ",".join(item.get("tags", []))
        final_report += f"## {topic}\n\n{description}\n\nFonti: {sources}\n\nTag: {tags}\n\n"
        verify_cmd = [
            PYTHON,
            ROOT / "Execution/ulisse/verify_paper.py",
            "--tags",
            tags,
            "--query",
            topic,
        ]
        verified = run_cmd(verify_cmd, check=False)
        final_report += (verified.stdout or verified.stderr).strip() + "\n\n"

    report_path = ROOT / f"Temp/ulisse/temi_hot_matched_{datetime.now().strftime('%d_%m_%Y_%H%M')}.txt"
    ensure_parent(report_path)
    report_path.write_text(final_report, encoding="utf-8")
    print(final_report)
    log(f"Report salvato in {report_path}")
    return 0


def workflow_paper(args):
    pdf_paths = discover_pdfs(recursive=True)
    if not pdf_paths:
        raise WorkflowError("Nessun PDF trovato in Papers/Da fare.")

    titles_map = get_bundle_titles(pdf_paths)
    options = [f"{titles_map.get(path.name, path.stem)}" for path in pdf_paths]
    selected_label = prompt_choice(options, "Seleziona paper", preselected_index=args.paper_index)
    selected_idx = options.index(selected_label)
    selected_pdf = pdf_paths[selected_idx]

    titles, metadata = generate_titles_and_metadata(selected_pdf)
    print("\nMetadati rilevati:")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    selected_title = prompt_choice(titles, "Seleziona titolo catchy", preselected_index=args.title_index)

    clean_title = slugify_title(selected_title)
    target_dir = CLEANED_DIR / clean_title
    pipeline = {
        "title": selected_title,
        "clean_title": clean_title,
        "target_dir": str(target_dir),
        "paper": selected_pdf.name,
        "paper_path": str(selected_pdf),
        "metadata": metadata,
        "academic_title": metadata.get("real_title", "Paper"),
        "status": "cover_pending_approval",
    }
    write_active_pipeline(pipeline)

    generate_cover(selected_title)
    if args.approve_cover:
        approve_cover_from_pipeline(move_pdf=True)
        return 0

    print(f"\nCopertina generata in: {TMP_COVER}")
    print("Approvala esplicitamente prima di archiviare il paper.")
    return 0


def workflow_copertina(args):
    if args.folder:
        setup_pipeline_for_cleaned_folder(args.folder)
    pipeline = read_active_pipeline()
    title = pipeline.get("title")
    if not title:
        raise WorkflowError("Titolo mancante in active_pipeline.json.")
    while True:
        generate_cover(title)
        action = choose_cover_action(auto_approve=args.approve_cover)
        if action == "approve":
            approve_cover_from_pipeline(move_pdf=False)
            break
        if action == "reject":
            log("Copertina rifiutata.")
            break
    return 0


def workflow_produzione(args):
    folder = args.folder
    if not folder:
        folder = choose_cleaned_folder(
            lambda path: any(path.glob("*.pdf")) and not any(path.glob("*.mp4"))
        )
    setup_pipeline_for_cleaned_folder(folder)
    result = run_cmd([PYTHON, ROOT / "Execution/enea/notebooklm_orchestrator.py"], check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Produzione fallita.")
    return 0


def workflow_pulizia(args):
    video = args.video
    if not video:
        recent = []
        now = time.time()
        for path in DOWNLOADS.glob("*_raw.mp4"):
            if now - path.stat().st_mtime < 86400:
                recent.append(path.name)
        recent.sort(key=lambda name: (DOWNLOADS / name).stat().st_mtime, reverse=True)
        video = prompt_choice(recent, "Seleziona video raw")
    result = run_cmd([PYTHON, ROOT / "Execution/enea/video_processor.py", video], check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Pulizia fallita.")
    return 0


def ready_upload_folders():
    folders = []
    for path in sorted(CLEANED_DIR.iterdir()):
        if not path.is_dir():
            continue
        files = {file.name for file in path.iterdir()}
        if any(name.endswith("_cleaned.mp4") for name in files) and "video_metadata.md" in files:
            folders.append(path.name)
    return folders


def workflow_upload(args):
    folder = args.folder or prompt_choice(ready_upload_folders(), "Seleziona video da caricare")
    folder_path = CLEANED_DIR / folder
    meta_path = folder_path / "video_metadata.md"
    thumb_path = folder_path / "copertina.png"
    videos = sorted(folder_path.glob("*_cleaned.mp4"))
    if not videos:
        raise WorkflowError(f"Nessun video pulito in {folder_path}")
    title = folder.replace("_", " ")
    first_line = meta_path.read_text(encoding="utf-8").splitlines()[0]
    if "Metadati Video - " in first_line:
        title = first_line.replace("#", "").replace("Metadati Video - ", "").strip()
    publish_at = args.schedule
    if not publish_at:
        tomorrow = datetime.now() + timedelta(days=1)
        publish_at = tomorrow.strftime("%Y-%m-%dT08:00:00+01:00")
    auth_cmd = [PYTHON, ROOT / "Execution/enea/youtube_auth.py"]
    if args.force_auth:
        auth_cmd.append("--force")
    auth_result = run_cmd(auth_cmd, cwd=ROOT, check=False)
    print((auth_result.stdout or auth_result.stderr).strip())
    if auth_result.returncode != 0:
        raise WorkflowError(
            auth_result.stderr
            or auth_result.stdout
            or "Autenticazione YouTube fallita. Esegui `./workflow youtube-auth`."
        )
    cmd = [
        PYTHON,
        ROOT / "Execution/enea/youtube_uploader.py",
        videos[0],
        title,
        meta_path,
        "--thumbnail",
        thumb_path,
        "--schedule",
        publish_at,
    ]
    result = run_cmd(cmd, cwd=ROOT / "Execution/credentials", check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Upload fallito.")
    return 0


def workflow_youtube_auth(args):
    cmd = [PYTHON, ROOT / "Execution/enea/youtube_auth.py"]
    if args.force:
        cmd.append("--force")
    result = run_cmd(cmd, cwd=ROOT, check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Autenticazione YouTube fallita.")
    return 0


def workflow_instagram(args):
    cmd = [
        PYTHON,
        ROOT / "Execution/marcello/buffer_post_single.py",
        "--platform",
        "instagram",
    ]
    if args.video_id:
        cmd.extend(["--video-id", args.video_id])
    if args.hour is not None:
        cmd.extend(["--hour", str(args.hour)])
    if args.dry_run:
        cmd.append("--dry-run")
    result = run_cmd(cmd, check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Instagram workflow fallito.")
    return 0


def playlist_candidates():
    tracking = {}
    if TRACKING_PATH.exists():
        with open(TRACKING_PATH, "r", encoding="utf-8") as handle:
            tracking = json.load(handle)
    folders = []
    for path in sorted(CLEANED_DIR.iterdir()):
        if not path.is_dir():
            continue
        info = tracking.get(path.name, {})
        if info.get("youtube_id") and not info.get("playlist"):
            folders.append(path.name)
    return folders


def workflow_playlist(args):
    folder = args.folder or prompt_choice(playlist_candidates(), "Seleziona video per playlist")
    result = run_cmd([PYTHON, ROOT / "Execution/romolo/catalog_video.py", folder], cwd=ROOT / "Execution/romolo", check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Playlist fallita.")
    return 0


def workflow_shorts(_args):
    result = run_cmd([PYTHON, ROOT / "Execution/romolo/batch_update_shorts.py"], check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Shorts workflow fallito.")
    return 0


def workflow_list(_args):
    workflows = [
        "download",
        "backup",
        "gmail",
        "report",
        "articoli",
        "paper",
        "copertina",
        "produzione",
        "pulizia",
        "youtube-auth",
        "upload",
        "instagram",
        "playlist",
        "shorts",
        "competitor",
    ]
    print("\n".join(workflows))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Workflow runner generale per canale")
    subparsers = parser.add_subparsers(dest="workflow", required=True)

    subparsers.add_parser("list")
    subparsers.add_parser("download")

    backup = subparsers.add_parser("backup")
    backup.add_argument("--message")

    subparsers.add_parser("gmail")
    subparsers.add_parser("report")
    subparsers.add_parser("competitor")

    articoli = subparsers.add_parser("articoli")
    articoli.add_argument("--tags")
    articoli.add_argument("--query")
    articoli.add_argument("--year", type=int, default=2000)

    paper = subparsers.add_parser("paper")
    paper.add_argument("--paper-index", type=int)
    paper.add_argument("--title-index", type=int)
    paper.add_argument("--approve-cover", action="store_true")

    copertina = subparsers.add_parser("copertina")
    copertina.add_argument("--folder")
    copertina.add_argument("--approve-cover", action="store_true")

    produzione = subparsers.add_parser("produzione")
    produzione.add_argument("--folder")

    pulizia = subparsers.add_parser("pulizia")
    pulizia.add_argument("--video")

    youtube_auth = subparsers.add_parser("youtube-auth")
    youtube_auth.add_argument("--force", action="store_true")

    upload = subparsers.add_parser("upload")
    upload.add_argument("--folder")
    upload.add_argument("--schedule")
    upload.add_argument("--force-auth", action="store_true")

    instagram = subparsers.add_parser("instagram")
    instagram.add_argument("--video-id")
    instagram.add_argument("--hour", type=int)
    instagram.add_argument("--dry-run", action="store_true")

    playlist = subparsers.add_parser("playlist")
    playlist.add_argument("--folder")

    subparsers.add_parser("shorts")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "list": workflow_list,
        "download": workflow_download,
        "backup": workflow_backup,
        "gmail": workflow_gmail,
        "report": workflow_report,
        "articoli": workflow_articoli,
        "paper": workflow_paper,
        "copertina": workflow_copertina,
        "produzione": workflow_produzione,
        "pulizia": workflow_pulizia,
        "youtube-auth": workflow_youtube_auth,
        "upload": workflow_upload,
        "instagram": workflow_instagram,
        "playlist": workflow_playlist,
        "shorts": workflow_shorts,
        "competitor": workflow_competitor,
    }
    try:
        return handlers[args.workflow](args)
    except WorkflowError as error:
        print(f"❌ {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Orchestratore produzione NotebookLM: long video + infografica + short (opzionale).

TEST path: 1 short per paper (`{clean_title}_short1_raw.mp4`), estensibile a N.
Richiede notebooklm-mcp-cli>=0.11.7 (`--format short`).
"""
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()

import argparse
import json
import os
import subprocess
import time
import sys
import re
import shutil

ACTIVE_PIPE = str(REPO_ROOT / "Temp" / "enea" / "active_pipeline.json")
DOWNLOADS_DEFAULT = str(HOME / "Downloads")

sys.path.insert(0, str(REPO_ROOT / "Execution" / "enea"))
from short_assets import (  # noqa: E402
    acquire_short_fallback_message,
    copy_short_raw_to_project,
    find_short_raw_in_downloads,
    nlm_bin,
    short_raw_name,
    upsert_short_tracking,
)


def log(msg):
    print(f"[ORCHESTRATOR] {msg}")
    sys.stdout.flush()


def run_cmd(args):
    try:
        clean_args = [str(a).strip() for a in args]
        env = os.environ.copy()
        env["COLUMNS"] = "250"
        # Preferisci nlm del venv anche se PATH punta a system 0.7.x
        res = subprocess.check_output(clean_args, stderr=subprocess.STDOUT, env=env).decode()
        return res.replace("\r", " ").replace("\n", " ")
    except subprocess.CalledProcessError as e:
        log(f"ERRORE COMANDO: {' '.join(args)}")
        out = e.output.decode() if e.output else "Nessun output"
        cleaned_out = out.replace("\r", " ").replace("\n", " ")
        log(f"OUTPUT: {cleaned_out}")
        return None


def run_cmd_with_retry(args, max_retries=3, delay=5):
    for i in range(max_retries):
        res = run_cmd(args)
        if res and "Error" not in res:
            return res
        if i < max_retries - 1:
            log(f"Tentativo {i+1} fallito. Riprovo tra {delay}s...")
            time.sleep(delay)
    return None


def sanitize_filename(filepath):
    dir_name = os.path.dirname(filepath)
    base_name = os.path.basename(filepath)
    safe_base = re.sub(r'[:*?"<>|]', " ", base_name).replace("'", "'").strip()
    safe_base = re.sub(r"\s+", " ", safe_base)
    safe_path = os.path.join(dir_name, safe_base)
    if filepath != safe_path:
        try:
            os.rename(filepath, safe_path)
            log(f"File sanificato: {os.path.basename(safe_path)}")
        except Exception as e:
            log(f"Impossibile rinominare il file: {e}")
            return filepath
    return safe_path


def parse_artifacts(status_res):
    if not status_res:
        return []
    try:
        data = json.loads(status_res[status_res.find("{") :] if "{" in status_res else status_res)
        if isinstance(data, dict):
            return data.get("artifacts", []) or []
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def artifact_completed(art):
    status = str(art.get("status", "")).lower()
    return status in {"completed", "complete", "ready", "done"}


def is_video_art(art):
    t = str(art.get("type", "")).lower()
    return t in {"video", "audio", "video_overview", "studio_video"}


def is_short_art(art):
    """Best-effort: format/title/metadata indicano short."""
    blob = json.dumps(art, ensure_ascii=False).lower()
    return any(token in blob for token in ("short", "vertical", "format_short", "video_format_short"))


def is_infographic_art(art):
    t = str(art.get("type", "")).lower()
    return "infographic" in t


def extract_art_id(art):
    return art.get("id") or art.get("artifact_id") or art.get("studio_id")


def create_and_download_short(nb_id, title, clean_title, target_dir, index=1):
    """Crea short via nlm --format short, scarica come {clean_title}_shortN_raw.mp4."""
    nlm = nlm_bin()
    short_prompt = (
        f"Per favore parla in Italiano. Formato Short verticale (9:16), max ~60 secondi. "
        f"Hook immediato sul risultato del paper. "
        f"**MANDATORIO: Il TITOLO in sovrimpressione DEVE essere ESATTAMENTE: '{title}'.**"
    )
    log(f"Generazione Short #{index} (--format short)...")
    res = run_cmd_with_retry(
        [
            nlm, "create", "video", nb_id,
            "--format", "short",
            "--focus", short_prompt,
            "--language", "it",
            "-y",
        ]
    )
    if not res:
        log("CLI short fallita. Fallback Downloads / UI.")
        log(acquire_short_fallback_message(clean_title, index))
        fallback = find_short_raw_in_downloads(clean_title, index)
        if fallback:
            copy_short_raw_to_project(fallback, Path(target_dir), clean_title, index)
            log(f"SHORT acquisito da Downloads: {fallback}")
            return str(fallback)
        return None

    log("Generazione Short avviata. Polling...")
    short_id = None
    for _ in range(60):
        status_res = run_cmd_with_retry([nlm, "status", "artifacts", nb_id, "-j"])
        arts = parse_artifacts(status_res)
        short_candidates = [a for a in arts if is_video_art(a) and is_short_art(a) and artifact_completed(a)]
        if short_candidates:
            short_id = extract_art_id(short_candidates[-1])
            break
        # Se non riusciamo a distinguere, aspetta e alla fine usa l'ultimo video completed != long
        time.sleep(30)

    output_file = short_raw_name(clean_title, index)
    output_path = os.path.join(str(HOME / "Downloads"), output_file)

    if not short_id:
        # Ultimo tentativo: qualunque video completed; download con --id se disponibile
        status_res = run_cmd([nlm, "status", "artifacts", nb_id, "-j"])
        arts = parse_artifacts(status_res)
        completed_videos = [a for a in arts if is_video_art(a) and artifact_completed(a)]
        if len(completed_videos) >= 2:
            short_id = extract_art_id(completed_videos[-1])
            log(f"Short artifact ID (fallback ultimo video): {short_id}")
        elif completed_videos:
            log("ATTENZIONE: un solo video completed — download potrebbe sovrascrivere il long.")
            short_id = extract_art_id(completed_videos[-1])

    dl_args = [nlm, "download", "video", nb_id, "--output", output_path]
    if short_id:
        dl_args.extend(["--id", str(short_id)])

    res = run_cmd(dl_args)
    if res and os.path.exists(output_path):
        log(f"DOWNLOAD SHORT COMPLETATO: {output_path}")
        copy_short_raw_to_project(Path(output_path), Path(target_dir), clean_title, index)
        try:
            upsert_short_tracking(
                Path(target_dir).name,
                angle=index,
                status="Raw acquisito",
                local_path=str(Path(target_dir) / output_file),
            )
        except Exception as exc:
            log(f"Tracking short non aggiornato: {exc}")
        return output_path

    log("Download short fallito. Provo fallback Downloads...")
    log(acquire_short_fallback_message(clean_title, index))
    fallback = find_short_raw_in_downloads(clean_title, index)
    if fallback:
        copy_short_raw_to_project(fallback, Path(target_dir), clean_title, index)
        log(f"SHORT acquisito da Downloads: {fallback}")
        return str(fallback)
    return None


def main(with_short=False, short_count=1):
    if not os.path.exists(ACTIVE_PIPE):
        log("ERRORE: active_pipeline.json non trovato. Lancia /paper su Telegram prima.")
        return 1

    with open(ACTIVE_PIPE, "r", encoding="utf-8") as f:
        pipe = json.load(f)

    title = pipe.get("title")
    pdf_path = pipe.get("paper_path")
    target_dir = pipe.get("target_dir", DOWNLOADS_DEFAULT)

    if not title or not pdf_path:
        log("ERRORE: Dati mancanti in active_pipeline.json (title o paper_path).")
        return 1

    nlm = nlm_bin()
    log(f"Usando nlm: {nlm}")
    log(f"Avvio produzione per: {title}")

    pdf_path = sanitize_filename(pdf_path)
    log(f"Usando PDF: {pdf_path}")
    clean_title = pipe.get("clean_title", title.replace(" ", "_"))
    os.makedirs(target_dir, exist_ok=True)

    # 1. Creazione Notebook
    log("Creazione Notebook...")
    res = run_cmd_with_retry([nlm, "create", "notebook", title])
    if not res:
        log("ERRORE: Impossibile creare il notebook dopo vari tentativi.")
        return 1

    try:
        nb_id = None
        json_start = res.find("{")
        if json_start >= 0:
            data = json.loads(res[json_start:])
            nb_id = data.get("notebook_id") or data.get("id")
        if not nb_id:
            match = re.search(r"ID:\s*([a-fA-F0-9-]+)", res)
            nb_id = match.group(1).strip() if match else res.split("ID:")[1].strip().split()[0].replace(")", "")
        log(f"Notebook creato: {nb_id}")
    except Exception as e:
        log(f"Impossibile estrarre ID Notebook: {e} | Output: {res}")
        return 1

    # 2. Upload Paper
    log("Caricamento PDF (Locale)...")
    res = run_cmd_with_retry([nlm, "source", "add", nb_id, "--file", pdf_path])

    if not res or "Error" in res:
        log("Caricamento locale fallito. Provo copia in Google Drive SYNC folder...")
        drive_sync_dir = str(HOME / "Google Drive" / "Papers")
        try:
            os.makedirs(drive_sync_dir, exist_ok=True)
            drive_dest = os.path.join(drive_sync_dir, os.path.basename(pdf_path))
            shutil.copy2(pdf_path, drive_dest)
            log(f"FILE COPIATO IN DRIVE SYNC: {drive_dest}")
            log("ATTENZIONE: nlm ha fallito l'upload. Caricare manualmente su NotebookLM da Drive e riprovare.")
            return 1
        except Exception as drive_err:
            log(f"Errore copia Drive: {drive_err}")
            return 1

    log("Paper caricato con successo.")
    log("Attendo 45 secondi per permettere a NotebookLM di indicizzare il documento...")
    time.sleep(45)

    # 3. Generazione Video LONG (explainer)
    video_prompt = (
        f"Per favore parla in Italiano. Sei un host di podcast coinvolgente che spiega paper di economia. "
        f"Sii energico ma accurato. Usa possibilmente le figure del paper senza ritoccarle, esprimi i numeri "
        f"a parole, usa un linguaggio non roboante. **MANDATORIO: Il TITOLO in sovrimpressione nel video DEVE "
        f"essere ESATTAMENTE: '{title}'. Non riassumere o alterare il titolo.**"
    )
    log("Generazione Video Overview (explainer)...")
    res = run_cmd_with_retry(
        [nlm, "create", "video", nb_id, "--focus", video_prompt, "--language", "it", "-y"]
    )
    if not res:
        return 1
    log("Generazione Video avviata.")

    # 4. Infografica square
    info_prompt = (
        "Lingua: Italiano perfetto. Tono: Semplice, divulgativo ma scientificamente chiaro. "
        "Stile grafico: Estremamente accattivante, ricco di disegni ed emoji (molto visivo, "
        "ad esempio in stile sketch_note o simile, evitando griglie, tabelle o blocchi grigi noiosi). "
        "REGOLE DI CONTENUTO: Spiega in modo conciso ma logicamente completo lo studio: "
        "1. IL DILEMMA: Qual è il problema che il paper vuole risolvere? "
        "(Usa un linguaggio semplice, es. \"Gli amici cambiano il voto?\"). "
        "2. LA SCOPERTA: I dati e le scoperte principali in modo logico e consequenziale "
        "(es. \"L'effetto del gruppo di amici è forte e misurabile\"). "
        "3. LA MORALE: Perché questa ricerca è importante per la vita reale "
        "(es. \"Le opinioni nascono nel gruppo, non da soli\"). "
        "REGOLE VISIVE: - Niente muri di testo densi o frasi lunghe e complesse. "
        "- Ricco di elementi grafici (disegni, icone, emoji). "
        "- Usa SOLO elenchi puntati brevissimi (pochi punti chiari) ed emoji pertinenti. "
        "- Formato: Quadrata."
    )
    log("Generazione Infografica...")
    res_info = run_cmd_with_retry(
        [
            nlm, "create", "infographic", nb_id,
            "--orientation", "square",
            "--detail", "detailed",
            "--style", "sketch_note",
            "--focus", info_prompt,
            "--language", "it",
            "-y",
        ]
    )
    if not res_info:
        log("ATTENZIONE: Generazione Infografica fallita (errore server). Procedo comunque con il video.")
    else:
        log("Generazione Infografica avviata.")

    # 5. Polling long + info
    log("In attesa del completamento asset long/infografica...")
    video_ready = False
    info_ready = False
    info_requested = bool(res_info)
    long_video_id = None

    for _ in range(60):
        status_res = run_cmd_with_retry([nlm, "status", "artifacts", nb_id, "-j"])
        arts = parse_artifacts(status_res)
        for art in arts:
            if is_video_art(art) and artifact_completed(art) and not is_short_art(art):
                video_ready = True
                long_video_id = extract_art_id(art) or long_video_id
            if is_infographic_art(art) and artifact_completed(art):
                info_ready = True
        if not arts and status_res:
            if "video" in status_res.lower() and "completed" in status_res.lower():
                video_ready = True
            if "infographic" in status_res.lower() and "completed" in status_res.lower():
                info_ready = True
        if video_ready and (info_ready or not info_requested):
            break
        time.sleep(30)

    # 6. Download Video LONG
    if video_ready:
        log("Video long pronto. Download in Downloads...")
        output_file = f"{clean_title}_raw.mp4"
        output_path = os.path.join(str(HOME / "Downloads"), output_file)
        dl_args = [nlm, "download", "video", nb_id, "--output", output_path]
        if long_video_id:
            dl_args.extend(["--id", str(long_video_id)])
        res = run_cmd(dl_args)
        if res:
            log(f"DOWNLOAD VIDEO COMPLETATO: {output_path}")
            shutil.copy(output_path, os.path.join(target_dir, output_file))
            log(f"COPIA ARCHIVIO COMPLETATA: {target_dir}")
    else:
        log("TIMEOUT o Errore durante la generazione del Video long.")

    # 7. Download Infografica
    if info_ready:
        log("Infografica pronta. Download in Downloads...")
        info_file = f"{clean_title}_infografica.png"
        dl_info_path = os.path.join(str(HOME / "Downloads"), info_file)
        res = run_cmd([nlm, "download", "infographic", nb_id, "--output", dl_info_path])
        if res:
            log(f"DOWNLOAD INFOGRAFICA COMPLETATO: {dl_info_path}")
            shutil.copy(dl_info_path, os.path.join(target_dir, info_file))
            log(f"COPIA INFOGRAFICA ARCHIVIO COMPLETATA: {target_dir}")
    elif res_info:
        log("Infografica non ancora pronta o fallita durante il polling.")

    # 8. Short(s) — TEST: 1; estensibile con --short-count
    if with_short:
        count = max(1, int(short_count or 1))
        for idx in range(1, count + 1):
            create_and_download_short(nb_id, title, clean_title, target_dir, index=idx)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Produzione NotebookLM (long + info + short)")
    parser.add_argument(
        "--with-short",
        "--short",
        dest="with_short",
        action="store_true",
        help="Dopo long+infografica genera/acquisisce Short (--format short)",
    )
    parser.add_argument(
        "--short-count",
        type=int,
        default=1,
        help="Numero di short da generare (default 1, TEST path)",
    )
    args = parser.parse_args()
    sys.exit(main(with_short=args.with_short, short_count=args.short_count) or 0)

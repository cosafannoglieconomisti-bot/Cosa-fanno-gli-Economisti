#!/usr/bin/env python3
import json
import os
import subprocess
import time
import sys
import re

# Percorsi Mandatori
ACTIVE_PIPE = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/active_pipeline.json"
DOWNLOADS_DEFAULT = "/Users/marcolemoglie_1_2/Downloads"

def log(msg):
    print(f"[ORCHESTRATOR] {msg}")
    sys.stdout.flush()

def run_cmd(args):
    try:
        # Pulisci argomenti da possibili junk characters
        clean_args = [str(a).strip() for a in args]
        # Forza una larghezza terminale ampia per evitare wrapping degli ID
        env = os.environ.copy()
        env["COLUMNS"] = "250"
        res = subprocess.check_output(clean_args, stderr=subprocess.STDOUT, env=env).decode()
        # Rimuovi newline e carriage return per evitare troncamenti negli ID
        return res.replace("\r", " ").replace("\n", " ")
    except subprocess.CalledProcessError as e:
        log(f"ERRORE COMANDO: {' '.join(args)}")
        out = e.output.decode() if e.output else "Nessun output"
        # Evita backslash in f-string per compatibilità Python 3.11
        cleaned_out = out.replace('\r', ' ').replace('\n', ' ')
        log(f"OUTPUT: {cleaned_out}")
        return None

def run_cmd_with_retry(args, max_retries=3, delay=5):
    """Esegue un comando con tentativi multipli in caso di timeout intermittenti."""
    for i in range(max_retries):
        res = run_cmd(args)
        if res and "Error" not in res:
            return res
        if i < max_retries - 1:
            log(f"Tentativo {i+1} fallito. Riprovo tra {delay}s...")
            time.sleep(delay)
    return None

def sanitize_filename(filepath):
    """Rimuove caratteri problematici (es: colons) dal nome file per evitare errori CLI."""
    dir_name = os.path.dirname(filepath)
    base_name = os.path.basename(filepath)
    # Sanificazione: rimuovi ':' e altri caratteri ostici
    safe_base = re.sub(r'[:*?"<>|]', ' ', base_name).replace('’', "'").strip()
    # Riduci gli spazi multipli
    safe_base = re.sub(r'\s+', ' ', safe_base)
    safe_path = os.path.join(dir_name, safe_base)
    if filepath != safe_path:
        try:
            os.rename(filepath, safe_path)
            log(f"File sanificato: {os.path.basename(safe_path)}")
        except Exception as e:
            log(f"Impossibile rinominare il file: {e}")
            return filepath
    return safe_path

def main():
    if not os.path.exists(ACTIVE_PIPE):
        log("ERRORE: active_pipeline.json non trovato. Lancia /paper su Telegram prima.")
        return

    with open(ACTIVE_PIPE, 'r') as f:
        pipe = json.load(f)

    title = pipe.get('title')
    pdf_path = pipe.get('paper_path')
    target_dir = pipe.get('target_dir', DOWNLOADS_DEFAULT)
    
    if not title or not pdf_path:
        log("ERRORE: Dati mancanti in active_pipeline.json (title o paper_path).")
        return

    log(f"Avvio produzione per: {title}")
    
    # 0. Sanificazione File
    pdf_path = sanitize_filename(pdf_path)
    log(f"Usando PDF: {pdf_path}")

    # 1. Creazione Notebook (Positional TITLE)
    log("Creazione Notebook...")
    res = run_cmd_with_retry(["nlm", "create", "notebook", title])
    if not res: 
        log("ERRORE: Impossibile creare il notebook dopo vari tentativi.")
        return
    
    # Estrazione UUID robusta
    try:
        match = re.search(r"ID:\s*([a-fA-F0-9-]+)", res)
        nb_id = match.group(1).strip() if match else res.split("ID:")[1].strip().split()[0].replace(')', '')
        log(f"Notebook creato: {nb_id}")
    except Exception as e:
        log(f"Impossibile estrarre ID Notebook: {e} | Output: {res}")
        return

    # 2. Upload Paper (SINTASSI CORRETTA: nlm source add NB_ID --file PATH)
    log("Caricamento PDF (Locale)...")
    res = run_cmd_with_retry(["nlm", "source", "add", nb_id, "--file", pdf_path])
    
    if not res or "Error" in res:
        log("Caricamento locale fallito. Provo copia in Google Drive SYNC folder...")
        import shutil
        drive_sync_dir = "/Users/marcolemoglie_1_2/Google Drive/Papers"
        try:
            os.makedirs(drive_sync_dir, exist_ok=True)
            drive_dest = os.path.join(drive_sync_dir, os.path.basename(pdf_path))
            shutil.copy2(pdf_path, drive_dest)
            log(f"FILE COPIATO IN DRIVE SYNC: {drive_dest}")
            log("ATTENZIONE: nlm ha fallito l'upload. Caricare manualmente su NotebookLM da Drive e riprovare.")
            return
        except Exception as drive_err:
            log(f"Errore copia Drive: {drive_err}")
            return
    
    log("Paper caricato con successo.")

    # 3. Generazione Video (Positional ID)
    video_prompt = f"Please speak Italian. You are a conversational and engaging podcast host explaining economics papers. Be energetic but accurate. Usare possibilmente le figure del paper senza ritoccarle, esprimere i numeri a parole, linguaggio non roboante. **MANDATORIO: Il TITOLO in sovrimpressione nel video DEVE essere ESATTAMENTE: '{title}'. Non riassumere o alterare il titolo.**"
    log("Generazione Video Overview...")
    res = run_cmd_with_retry(["nlm", "create", "video", nb_id, "--focus", video_prompt, "-y"])
    if not res: return
    log("Generazione Video avviata.")

    # 4. Generazione Infografica (Positional ID) - Resiliente carachters
    info_prompt = "Lingua: Italiano. Stile: Moderna, pulita. Tono: Divulgativo. FOCUS: 1. IL DILEMMA 2. LA SCOPERTA 3. LA MORALE. REGOLE: Niente muri di testo. Emoji e grafici. Formato: Quadrata."

    log("Generazione Infografica...")
    # Usiamo un blocco try-except o semplicemente non usciamo se res è None
    res_info = run_cmd_with_retry(["nlm", "create", "infographic", nb_id, "--orientation", "square", "--detail", "detailed", "--focus", info_prompt, "-y"])
    if not res_info:
        log("ATTENZIONE: Generazione Infografica fallita (errore server). Procedo comunque con il video.")
    else:
        log("Generazione Infografica avviata.")

    # 5. Polling Stato
    log("In attesa del completamento asset...")
    video_ready = False
    info_ready = False
    
    for _ in range(60): # ~30 minuti per paper lunghi o server lenti
        status_res = run_cmd_with_retry(["nlm", "status", "artifacts", nb_id, "-j"])
        if status_res:
            try:
                data = json.loads(status_res)
                artifacts = data.get('artifacts', []) if isinstance(data, dict) else data
                for art in artifacts:
                    if art.get('type') == 'audio' or art.get('type') == 'video':
                        if art.get('status') == 'completed': video_ready = True
                    if art.get('type') == 'infographic' and art.get('status') == 'completed':
                        info_ready = True
            except:
                if "video" in status_res.lower() and "completed" in status_res.lower(): video_ready = True
                if "infographic" in status_res.lower() and "completed" in status_res.lower(): info_ready = True
        
        if video_ready: break # Usciamo se almeno il video è pronto per non far aspettare troppo
        time.sleep(30)

    # 6. Download Video
    if video_ready:
        log("Video pronto. Inizio download in Downloads...")
        clean_title = pipe.get('clean_title', title.replace(' ', '_'))
        output_file = f"{clean_title}_raw.mp4"
        # Download in ~/Downloads per compatibilità SOP (Step 3)
        output_path = os.path.join(os.path.expanduser("~/Downloads"), output_file)
        res = run_cmd(["nlm", "download", "video", nb_id, "--output", output_path])
        if res: 
            log(f"DOWNLOAD VIDEO COMPLETATO: {output_path}")
            # Copia anche in cartella Cleaned per archivio (SOP Step 5)
            import shutil
            shutil.copy(output_path, os.path.join(target_dir, output_file))
            log(f"COPIA ARCHIVIO COMPLETATA: {target_dir}")
    else:
        log("TIMEOUT o Errore durante la generazione del Video.")

    # 7. Download Infografica (Se pronta)
    if info_ready:
        log("Infografica pronta. Inizio download in Downloads...")
        info_file = f"{clean_title}_infografica.png"
        dl_info_path = os.path.join(os.path.expanduser("~/Downloads"), info_file)
        res = run_cmd(["nlm", "download", "infographic", nb_id, "--output", dl_info_path])
        if res: 
            log(f"DOWNLOAD INFOGRAFICA COMPLETATO: {dl_info_path}")
            import shutil
            shutil.copy(dl_info_path, os.path.join(target_dir, info_file))
            log(f"COPIA INFOGRAFICA ARCHIVIO COMPLETATA: {target_dir}")
    elif res_info:
        log("Infografica non ancora pronta o fallita durante il polling.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import os
import subprocess
import time
import sys
import re
import shutil

# Percorsi Mandatori
ACTIVE_PIPE = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/active_pipeline.json"
DOWNLOADS_DEFAULT = "/Users/marcolemoglie_1_2/Downloads"
CLI_PATH = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook-press"

def log(msg):
    print(f"[ORCHESTRATOR] {msg}")
    sys.stdout.flush()

def run_cmd(args):
    try:
        clean_args = [str(a).strip() for a in args]
        env = os.environ.copy()
        env["COLUMNS"] = "250"
        res = subprocess.check_output(clean_args, stderr=subprocess.STDOUT, env=env).decode()
        return res
    except subprocess.CalledProcessError as e:
        log(f"ERRORE COMANDO: {' '.join(args)}")
        out = e.output.decode() if e.output else "Nessun output"
        cleaned_out = out.replace('\r', ' ').replace('\n', ' ')
        log(f"OUTPUT: {cleaned_out}")
        return None

def main():
    if not os.path.exists(ACTIVE_PIPE):
        log("ERRORE: active_pipeline.json non trovato. Lancia /paper su Telegram prima.")
        return

    with open(ACTIVE_PIPE, 'r') as f:
        pipe = json.load(f)

    title = pipe.get('title')
    pdf_path = pipe.get('paper_path')
    target_dir = pipe.get('target_dir', DOWNLOADS_DEFAULT)
    clean_title = pipe.get('clean_title', title.replace(' ', '_'))
    notebook_id = pipe.get('notebook_id')
    
    if not title or not pdf_path:
        log("ERRORE: Dati mancanti in active_pipeline.json (title o paper_path).")
        return

    log(f"Avvio produzione per: {title}")
    log(f"Usando PDF: {pdf_path}")

    # 1. Ingestion & creation via notebook-press CLI
    log("Ingestione paper e creazione notebook via notebook-press...")
    upload_cmd = [CLI_PATH, "upload", pdf_path, "--title", title]
    if notebook_id:
        upload_cmd += ["--notebook-id", notebook_id]
    res = run_cmd(upload_cmd)
    if not res:
        log("ERRORE: Ingestione fallita.")
        return
        
    try:
        json_match = re.search(r'(\{.*\})', res, re.DOTALL)
        json_str = json_match.group(1) if json_match else res
        data = json.loads(json_str)
        nb_id = data.get("notebook_id")
        if not nb_id:
            raise ValueError("Notebook ID non trovato nella risposta JSON")
        log(f"Notebook creato/recuperato: {nb_id}")
        
        # Salva notebook_id in active_pipeline.json
        if notebook_id != nb_id:
            pipe['notebook_id'] = nb_id
            with open(ACTIVE_PIPE, 'w') as f:
                json.dump(pipe, f, indent=4)
    except Exception as e:
        log(f"Impossibile analizzare risposta upload: {e} | Output: {res}")
        return

    # 2. Trigger video overview via notebook-press CLI
    video_prompt = f"Per favore parla in Italiano. Sei un host di podcast coinvolgente che spiega paper di economia. Sii energico ma accurato. Usa possibilmente le figure del paper senza ritoccarle, esprimi i numeri a parole, usa un linguaggio non roboante. **MANDATORIO: Il TITOLO in sovrimpressione nel video DEVE essere ESATTAMENTE: '{title}'. Non riassumere o alterare il titolo.**"
    log("Generazione Video Overview...")
    res = run_cmd([CLI_PATH, "generate", nb_id, "--type", "video", "--focus", video_prompt])
    if not res:
        log("ERRORE: Impossibile avviare generazione video.")
        return
    log("Generazione Video avviata.")

    # 3. Trigger infographic via notebook-press CLI
    info_prompt = "Lingua: Italiano. Stile: Moderna, pulita. Tono: Divulgativo. FOCUS: 1. IL DILEMMA 2. LA SCOPERTA 3. LA MORALE. REGOLE: Niente muri di testo. Emoji e grafici. Formato: Quadrata."
    log("Generazione Infografica...")
    res_info = run_cmd([CLI_PATH, "generate", nb_id, "--type", "infographic", "--focus", info_prompt])
    if not res_info:
        log("ATTENZIONE: Generazione Infografica non avviata o non supportata.")
    else:
        log("Generazione Infografica avviata.")

    # 4. Polling via notebook-press CLI
    log("In attesa del completamento asset...")
    video_ready = False
    info_ready = False
    
    for _ in range(60): # ~30 minuti
        status_res = run_cmd([CLI_PATH, "status", nb_id])
        if status_res:
            try:
                json_match = re.search(r'(\{.*\})', status_res, re.DOTALL)
                json_str = json_match.group(1) if json_match else status_res
                status_data = json.loads(json_str)
                if status_data.get("status") == "success":
                    v_status = status_data["video"]["status"]
                    i_status = status_data["infographic"]["status"]
                    log(f"Stato polling -> Video: {v_status} | Infografica: {i_status}")
                    
                    if v_status == "completed":
                        video_ready = True
                    if i_status == "completed":
                        info_ready = True
            except Exception as e:
                log(f"Errore parsing status: {e}")
                
        if video_ready:
            break
        time.sleep(30)

    # 5. Download Video via notebook-press CLI
    output_file = f"{clean_title}_raw.mp4"
    output_path = os.path.join(os.path.expanduser("~/Downloads"), output_file)
    
    if video_ready:
        log(f"Video pronto. Inizio download sicuro in: {output_path}")
        res = run_cmd([CLI_PATH, "download", nb_id, "video", "--output", output_path])
        if res and "success" in res:
            log(f"DOWNLOAD VIDEO COMPLETATO: {output_path}")
            shutil_copy_path = os.path.join(target_dir, output_file)
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(output_path, shutil_copy_path)
            log(f"COPIA ARCHIVIO COMPLETATA: {target_dir}")
        else:
            log("ERRORE: Download video fallito tramite tutti i metodi.")
    else:
        log("TIMEOUT o Errore durante la generazione del Video.")

    # 6. Download Infografica via notebook-press CLI
    info_file = f"{clean_title}_infografica.png"
    dl_info_path = os.path.join(os.path.expanduser("~/Downloads"), info_file)
    
    if info_ready:
        log(f"Infografica pronta. Inizio download sicuro in: {dl_info_path}")
        res = run_cmd([CLI_PATH, "download", nb_id, "infographic", "--output", dl_info_path])
        if res and "success" in res:
            log(f"DOWNLOAD INFOGRAFICA COMPLETATO: {dl_info_path}")
            shutil_info_path = os.path.join(target_dir, info_file)
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(dl_info_path, shutil_info_path)
            log(f"COPIA INFOGRAFICA ARCHIVIO COMPLETATA: {target_dir}")
        else:
            log("ERRORE: Download infografica fallito tramite tutti i metodi.")
    elif res_info:
        log("Infografica non ancora pronta o fallita durante il polling.")

if __name__ == "__main__":
    main()

import os
import subprocess
import sys
import shutil
from pathlib import Path

def process_video_and_archive(input_video_path, paper_name, base_cleaned_dir, paper_pdf_path=None, trim_seconds=2.5):
    """
    Rimuove gli ultimi 'trim_seconds' secondi, offusca il watermark,
    e salva il risultato in Cleaned/{paper_name}/. Sposta anche il PDF originale.
    """
    if not os.path.exists(input_video_path):
        print(f"Errore: Video input non trovato: {input_video_path}")
        return False
        
    print(f"Processando {input_video_path} per {paper_name}...")
    
    # Crea cartella di destinazione
    target_dir = os.path.join(base_cleaned_dir, paper_name)
    os.makedirs(target_dir, exist_ok=True)
    
    output_video_path = os.path.join(target_dir, f"{paper_name}_cleaned.mp4")
    
    # 1. Ottieni la durata e risoluzione totale del video usando ffprobe
    ffprobe_path = '/opt/homebrew/bin/ffprobe'
    probe_cmd = [
        ffprobe_path, '-v', 'error', '-select_streams', 'v:0', 
        '-show_entries', 'format=duration:stream=width,height', 
        '-of', 'default=noprint_wrappers=1:nokey=1', input_video_path
    ]
    
    result = None
    try:
        result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        # ffprobe output lines usually: width, height, duration
        vid_w = int(lines[0])
        vid_h = int(lines[1])
        total_duration = float(lines[2])
    except Exception as e:
        output = result.stdout if result else "N/A"
        print(f"Errore nel calcolo di durata/risoluzione del file: {e}\nOutput: {output}")
        return False
        
    new_duration = total_duration - trim_seconds
    if new_duration <= 0:
        print("Errore: Il video è troppo corto per il trim richiesto.")
        return False
    
    # Calcolo esatto dei pixel per il watermark in basso a destra
    box_w = 230
    box_h = 80
    delogo_x = vid_w - 250
    delogo_y = vid_h - 100
    
    # Assicurati che non vada fuori i bordi
    if delogo_x < 0: delogo_x = 0
    if delogo_y < 0: delogo_y = 0
    
    # FFMPEG: Usa un box di sfuocatura in basso a destra con coordinate assolute
    delogo_filter = f"delogo=x={delogo_x}:y={delogo_y}:w={box_w}:h={box_h}" 
    ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
    ffmpeg_cmd = [
        ffmpeg_path, '-y', '-loglevel', 'error',
        '-i', input_video_path,
        '-t', str(new_duration),
        '-vf', delogo_filter,
        '-c:a', 'copy', # Copia l'audio senza riconvertire
        output_video_path
    ]
    
    try:
        print("Inizio conversione video con FFmpeg (modalità quiet)...")
        # Capturiamo l'output per evitare di saturare la pipe del padre
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"Successo! Video pulito salvato in {output_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Errore FFmpeg: {e}")
        return False

    # Spostamento del PDF se fornito
    if paper_pdf_path and os.path.exists(paper_pdf_path):
        pdf_dest = os.path.join(target_dir, os.path.basename(paper_pdf_path))
        shutil.move(paper_pdf_path, pdf_dest)
        print(f"PDF originale spostato in {pdf_dest}")
        
    # Spostamento anche del video originale (opzionale, per ora lo teniamo lì o eliminiamo? Lo spostiamo raw)
    # raw_dest = os.path.join(target_dir, f"{paper_name}_raw.mp4")
    # shutil.move(input_video_path, raw_dest)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python video_cleaner.py <input_video.mp4> <paper_name_senza_ext> [percorso_pdf_originale]")
    else:
        in_video = sys.argv[1]
        p_name = sys.argv[2]
        pdf_path = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Add support for custom trim
        trim = 2.5
        # Parse if 4th arg is present, or check if pdf_path was skipped
        if len(sys.argv) > 3:
             # Try to parse last arg as float if it's there
             try:
                 trim = float(sys.argv[-1])
                 # If last arg was trim, then pdf_path is sys.argv[3] only if len > 4
                 if len(sys.argv) > 4:
                     pdf_path = sys.argv[3]
                 else:
                     pdf_path = None # It was trim
             except ValueError:
                 pass # Not a number, keep default

        base_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
        # Since process_video_and_archive takes trim_seconds as optional kwarg
        process_video_and_archive(in_video, p_name, base_dir, pdf_path, trim_seconds=trim)

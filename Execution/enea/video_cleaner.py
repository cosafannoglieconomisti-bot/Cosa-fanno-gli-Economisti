import os
import subprocess
import sys
import shutil
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_TRIM_SECONDS = 3.8  # ~3.5–4s: non tagliare la voce di chiusura (evitare 2.5s aggressivo)


def estimate_outro_trim_seconds(
    input_video_path,
    ffmpeg_path,
    total_duration,
    default=DEFAULT_TRIM_SECONDS,
    min_trim=3.2,
    max_trim=4.5,
    window=0.05,
):
    """Stima il taglio outro guidato da RMS audio sugli ultimi ~6s.

    Obiettivo: tenere la frase di chiusura; tagliare solo silenzio/jingle finale.
    Se l'analisi fallisce, usa default (~3.8s). Mai sotto min_trim / sopra max_trim.
    """
    import struct
    import tempfile

    if total_duration < (min_trim + 1.0):
        return default

    analyze = min(6.0, max(4.0, total_duration * 0.12))
    start = max(0.0, total_duration - analyze)
    sample_rate = 8000
    try:
        with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as tmp:
            raw_path = tmp.name
        cmd = [
            ffmpeg_path, "-y", "-loglevel", "error",
            "-ss", f"{start:.3f}", "-i", input_video_path,
            "-t", f"{analyze:.3f}",
            "-ac", "1", "-ar", str(sample_rate),
            "-f", "s16le", raw_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        data = Path(raw_path).read_bytes()
        try:
            os.unlink(raw_path)
        except OSError:
            pass
        if len(data) < sample_rate:  # <1s
            return default
        n = len(data) // 2
        samples = struct.unpack(f"<{n}h", data[: n * 2])
        win = max(1, int(sample_rate * window))
        # RMS per finestra dalla fine verso l'inizio
        speech_thresh = 500.0  # s16 amp empirica
        last_speech_offset = None  # secondi dall'inizio del segmento analizzato
        for i in range((n // win) - 1, -1, -1):
            chunk = samples[i * win : (i + 1) * win]
            if not chunk:
                continue
            mean_sq = sum(s * s for s in chunk) / len(chunk)
            rms = mean_sq ** 0.5
            if rms >= speech_thresh:
                last_speech_offset = (i + 1) * window
                break
        if last_speech_offset is None:
            trim = default
        else:
            # secondi dopo l'ultima voce fino a fine file + piccolo padding
            silence_tail = analyze - last_speech_offset
            trim = silence_tail + 0.35
        trim = max(min_trim, min(max_trim, trim))
        print(f"Trim outro RMS-guidato: {trim:.2f}s (default={default}, finestra={analyze:.1f}s)")
        return trim
    except Exception as exc:
        print(f"Trim outro: fallback {default}s ({exc})")
        return default


def process_video_and_archive(input_video_path, paper_name, base_cleaned_dir, paper_pdf_path=None, trim_seconds=None, output_filename=None, target_subdir=None):
    """
    Taglia l'outro (~3.5–4s, RMS-guidato; NON 2.5s aggressivo che taglia la voce),
    copre il watermark NotebookLM con fill SOLIDO (colore campionato dallo sfondo;
    NON delogo soft che lascia macchie), e salva in Cleaned/{paper_name}/.

    output_filename: es. '{paper}_short1_cleaned.mp4' (default: '{paper}_cleaned.mp4')
    target_subdir: sottocartella opzionale (es. 'shorts') dentro Cleaned/{paper_name}/
    trim_seconds: se None, stima RMS; altrimenti usa il valore passato (clamp 3.2–4.5).
    """
    if not os.path.exists(input_video_path):
        print(f"Errore: Video input non trovato: {input_video_path}")
        return False
        
    print(f"Processando {input_video_path} per {paper_name}...")
    
    # Crea cartella di destinazione
    target_dir = os.path.join(base_cleaned_dir, paper_name)
    if target_subdir:
        target_dir = os.path.join(target_dir, target_subdir)
    os.makedirs(target_dir, exist_ok=True)
    
    out_name = output_filename or f"{paper_name}_cleaned.mp4"
    output_video_path = os.path.join(target_dir, out_name)
    
    # 1. Ottieni la durata e risoluzione totale del video usando ffprobe
    ffprobe_path = shutil.which("ffprobe")
    if not ffprobe_path:
        print("Errore: ffprobe non trovato. Installalo con: brew install ffmpeg")
        return False
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

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        print("Errore: ffmpeg non trovato. Installalo con: brew install ffmpeg")
        return False

    if trim_seconds is None:
        trim_seconds = estimate_outro_trim_seconds(
            input_video_path, ffmpeg_path, total_duration
        )
    else:
        trim_seconds = max(3.2, min(4.5, float(trim_seconds)))
        print(f"Trim outro forzato: {trim_seconds:.2f}s")

    new_duration = total_duration - trim_seconds
    if new_duration <= 0:
        print("Errore: Il video è troppo corto per il trim richiesto.")
        return False
    
    # Watermark NotebookLM: box proporzionale (portrait/vertical-aware)
    try:
        from short_assets import delogo_box_for_resolution
        delogo_x, delogo_y, box_w, box_h = delogo_box_for_resolution(vid_w, vid_h)
    except Exception:
        if vid_h > vid_w:
            box_w = max(170, int(vid_w * 0.30))
            box_h = max(40, int(vid_h * 0.04))
            delogo_x = max(0, vid_w - box_w - max(4, int(vid_w * 0.008)))
            delogo_y = max(0, vid_h - box_h - max(4, int(vid_h * 0.006)))
        else:
            box_w = max(220, int(vid_w * 0.23))
            box_h = max(30, int(vid_h * 0.05))
            delogo_x = max(0, vid_w - box_w - 2)
            delogo_y = max(0, vid_h - box_h - 2)
    print(f"Cover watermark SOLIDO {'verticale' if vid_h > vid_w else 'orizzontale'}: {vid_w}x{vid_h} box=({delogo_x},{delogo_y},{box_w},{box_h})")

    # Campiona colore dominante subito SOPRA il badge (sfondo locale), poi drawbox solido.
    # SOP approvata: fill solido (NO delogo soft / macchie).
    sample_color = "0xF2F2F2"
    try:
        from PIL import Image
        import tempfile
        sample_t = min(5.0, max(0.5, new_duration * 0.15))
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            frame_path = tmp.name
        subprocess.run(
            [
                ffmpeg_path, "-y", "-loglevel", "error",
                "-ss", str(sample_t), "-i", input_video_path,
                "-frames:v", "1", frame_path,
            ],
            check=True,
        )
        im = Image.open(frame_path).convert("RGB")
        sx0 = delogo_x
        sx1 = min(vid_w, delogo_x + box_w)
        sy1 = max(1, delogo_y)
        sy0 = max(0, sy1 - max(8, box_h))
        crop = im.crop((sx0, sy0, sx1, sy1))
        # mediana per canale
        pixels = list(crop.getdata())
        if pixels:
            rs = sorted(px[0] for px in pixels)
            gs = sorted(px[1] for px in pixels)
            bs = sorted(px[2] for px in pixels)
            mid = len(pixels) // 2
            sample_color = f"0x{rs[mid]:02X}{gs[mid]:02X}{bs[mid]:02X}"
        try:
            os.unlink(frame_path)
        except OSError:
            pass
        print(f"Colore cover watermark: {sample_color} (sample t={sample_t:.1f}s)")
    except Exception as exc:
        print(f"Fallback colore cover ({exc})")

    cover_filter = (
        f"drawbox=x={delogo_x}:y={delogo_y}:w={box_w}:h={box_h}"
        f":color={sample_color}@1.0:t=fill"
    )
    ffmpeg_cmd = [
        ffmpeg_path, '-y', '-loglevel', 'error',
        '-i', input_video_path,
        '-t', str(new_duration),
        '-vf', cover_filter,
        '-c:a', 'copy',
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
        print("Uso: python video_cleaner.py <input_video.mp4> <paper_name_senza_ext> [percorso_pdf_originale] [--short]")
    else:
        in_video = sys.argv[1]
        p_name = sys.argv[2]
        pdf_path = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Default: RMS-guidato (~3.5–4s). Passa un float esplicito per forzare.
        trim = None
        if len(sys.argv) > 3:
             try:
                 trim = float(sys.argv[-1])
                 if len(sys.argv) > 4:
                     pdf_path = sys.argv[3]
                 else:
                     pdf_path = None
             except ValueError:
                 pass

        base_dir = str(REPO_ROOT / 'Cleaned')
        is_short = "--short" in sys.argv or "_short" in os.path.basename(in_video).lower()
        out_name = None
        if is_short:
            try:
                from short_assets import short_cleaned_name, parse_short_index_from_filename
                idx = parse_short_index_from_filename(os.path.basename(in_video))
                out_name = short_cleaned_name(p_name, idx)
            except Exception:
                out_name = f"{p_name}_short1_cleaned.mp4"
        # Short cleaned in root progetto per discovery upload
        # Se pdf_path era un flag (--short), ignoralo
        if pdf_path and str(pdf_path).startswith("--"):
            pdf_path = None
        process_video_and_archive(
            in_video, p_name, base_dir, pdf_path, trim_seconds=trim,
            output_filename=out_name,
        )

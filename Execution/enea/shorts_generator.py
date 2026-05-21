import os
import subprocess
import sys
import json
import re

# Configurazione
BASE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale"
FFMPEG = "ffmpeg"

def run_ffmpeg(cmd):
    print(f"🚀 Eseguo FFmpeg: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Errore FFmpeg: {result.stderr}")
        return False
    return True

def generate_short(video_path, srt_path=None, output_path=None, start_time="00:00:00", duration=59):
    if not os.path.exists(video_path):
        print(f"❌ Video non trovato: {video_path}")
        return False

    if not output_path:
        output_path = video_path.replace(".mp4", "_short.mp4")

    # Filtro Video: Crop a 9:16 (centrale) e Scale a 1080x1920
    # Formula: crop=ih*9/16:ih (ritaglio verticale basato sull'altezza)
    video_filter = "crop=ih*9/16:ih,scale=1080:1920"
    
    # Aggiunta Sottotitoli se presenti
    if srt_path and os.path.exists(srt_path):
        # Proviamo a vedere se il filtro è supportato, altrimenti procediamo senza
        temp_filter = video_filter + f",subtitles=filename='{srt_path}'"
        test_cmd = [FFMPEG, "-filters"]
        res = subprocess.run(test_cmd, capture_output=True, text=True)
        if "subtitles" in res.stdout:
            video_filter += f",subtitles=filename='{srt_path}':force_style='Alignment=2,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=1'"
        else:
            print("⚠️ Warning: Il filtro 'subtitles' non è supportato da questo FFmpeg. Genero lo Short senza sottotitoli impressi.")

    cmd = [
        FFMPEG, "-y",
        "-ss", start_time,
        "-i", video_path,
        "-t", str(duration),
        "-vf", video_filter,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "copy",
        output_path
    ]

    return run_ffmpeg(cmd)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 shorts_generator.py <video_path> [srt_path] [start_time]")
        sys.exit(1)

    v_path = sys.argv[1]
    s_path = sys.argv[2] if len(sys.argv) > 2 else None
    t_start = sys.argv[3] if len(sys.argv) > 3 else "00:00:00"
    
    success = generate_short(v_path, s_path, start_time=t_start)
    if success:
        print(f"✨ Short generato con successo: {v_path.replace('.mp4', '_short.mp4')}")
    else:
        print("❌ Fallimento nella generazione dello Short.")

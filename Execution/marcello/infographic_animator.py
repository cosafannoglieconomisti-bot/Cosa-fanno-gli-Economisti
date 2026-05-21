import os
import subprocess
import sys

# Configurazione
FFMPEG = "ffmpeg"

def animate_infographic(img_path, output_path=None, duration=10):
    if not os.path.exists(img_path):
        print(f"❌ Immagine non trovata: {img_path}")
        return False

    if not output_path:
        output_path = img_path.replace(".png", "_reel.mp4")

    # Effetto Ken Burns (Zoom progressivo)
    # zoompan: zoom progressivo da 1.0 a 1.2 in 10 secondi (250 frame a 25fps)
    video_filter = f"zoompan=z='min(zoom+0.001,1.2)':d={duration*25}:s=1080x1920,fade=t=in:st=0:d=1,fade=t=out:st={duration-1}:d=1"

    cmd = [
        FFMPEG, "-y",
        "-loop", "1",
        "-i", img_path,
        "-c:v", "libx264",
        "-t", str(duration),
        "-vf", video_filter,
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        output_path
    ]

    print(f"🚀 Generazione Reel animato: {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Errore FFmpeg: {result.stderr}")
        return False
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 infographic_animator.py <img_path> [duration]")
        sys.exit(1)

    i_path = sys.argv[1]
    dur = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    success = animate_infographic(i_path, duration=dur)
    if success:
        print(f"✨ Reel generato con successo!")
    else:
        print("❌ Fallimento nella generazione del Reel.")

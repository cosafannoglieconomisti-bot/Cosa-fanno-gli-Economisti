import sys
import os
from faster_whisper import WhisperModel

def format_timestamp(seconds):
    """Converte i secondi nel formato SRT: HH:MM:SS,mmm"""
    td_h = int(seconds // 3600)
    td_m = int((seconds % 3600) // 60)
    td_s = int(seconds % 60)
    td_ms = int((seconds % 1) * 1000)
    return f"{td_h:02d}:{td_m:02d}:{td_s:02d},{td_ms:03d}"

def generate_srt(video_path, output_srt):
    print(f"Caricamento modello Whisper ('base') per {video_path}...")
    model = WhisperModel("base", device="cpu", compute_type="float32")

    print("Trascrizione video in corso per generazione SRT...")
    segments, info = model.transcribe(video_path, beam_size=5, language="it")

    with open(output_srt, "w", encoding="utf-8") as f:
        counter = 1
        for segment in segments:
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            text = segment.text.strip()
            
            f.write(f"{counter}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
            
            print(f"[{start}] {text}")
            counter += 1

    print(f"\n✅ File SRT salvato in: {output_srt}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_srt_whisper.py <video_path> <output_srt>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_srt = sys.argv[2]
    generate_srt(video_path, output_srt)

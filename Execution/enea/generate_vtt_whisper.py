import sys
import os
from faster_whisper import WhisperModel

def format_timestamp_vtt(seconds):
    """Converte i secondi nel formato VTT: HH:MM:SS.mmm"""
    td_h = int(seconds // 3600)
    td_m = int((seconds % 3600) // 60)
    td_s = int(seconds % 60)
    td_ms = int((seconds % 1) * 1000)
    return f"{td_h:02d}:{td_m:02d}:{td_s:02d}.{td_ms:03d}"

def generate_vtt(video_path, output_vtt):
    print(f"Caricamento modello Whisper ('base') per {video_path}...")
    model = WhisperModel("base", device="cpu", compute_type="float32")

    print("Trascrizione video in corso per generazione VTT...")
    segments, info = model.transcribe(video_path, beam_size=5, language="it")

    with open(output_vtt, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for segment in segments:
            start = format_timestamp_vtt(segment.start)
            end = format_timestamp_vtt(segment.end)
            text = segment.text.strip()
            
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
            
            print(f"[{start}] {text}")

    print(f"\n✅ File VTT salvato in: {output_vtt}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_vtt_whisper.py <video_path> <output_vtt>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_vtt = sys.argv[2]
    generate_vtt(video_path, output_vtt)

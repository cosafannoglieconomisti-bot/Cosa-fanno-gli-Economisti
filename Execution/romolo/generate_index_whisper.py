import sys
import os

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("ERROR: faster-whisper not installed yet. Please wait.")
    sys.exit(1)

def generate_index(video_path, output_log):
    print(f"Loading Whisper model ('base') for {video_path}...")
    # 'base' size is good for speed/accuracy balance.
    model = WhisperModel("base", device="cpu", compute_type="float32")

    print("Transcribing video...")
    segments, info = model.transcribe(video_path, beam_size=5, language="it")

    print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")

    with open(output_log, "w") as f:
        f.write(f"=== TRASCRITTO CON TIMESTAMP ===\n")
        f.write(f"Video: {os.path.basename(video_path)}\n\n")
        for segment in segments:
            start_m = int(segment.start // 60)
            start_s = int(segment.start % 60)
            timestamp = f"[{start_m:02d}:{start_s:02d}]"
            f.write(f"{timestamp} {segment.text.strip()}\n")
            # Print to stdout too for verification
            print(f"{timestamp} {segment.text.strip()}")

    print(f"\nSaved raw index to {output_log}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_index_whisper.py <video_path> <output_log>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_log = sys.argv[2]
    generate_index(video_path, output_log)

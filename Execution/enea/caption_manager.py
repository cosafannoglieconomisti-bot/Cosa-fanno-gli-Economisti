import os
import sys
import subprocess
import json
import glob
from pathlib import Path

# Configurazione Percorsi
BASE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale"
EXEC_DIR = os.path.join(BASE_DIR, "Execution")
CLEANED_DIR = os.path.join(BASE_DIR, "Cleaned")
PYTHON_BIN = os.path.join(BASE_DIR, ".venv/bin/python3")

# Tools
DOWNLOADER = os.path.join(EXEC_DIR, "romolo/download_transcript.py")
TRANSLATOR = os.path.join(EXEC_DIR, "enea/translate_srt.py")
UPLOADER = os.path.join(EXEC_DIR, "romolo/update_video_localization.py")

# Mappa Progetti
PROJECTS = {
    "Il_Talento_Non_Ha_Genere": "rIT-o-aWI8k",
    "Il_Pallone_Unisce_le_Nazioni": "y4zWdljXoPY",
    "Dalle_Guerre_ai_Capolavori": "n_8eHt5ZjXY"
}

LANGUAGES = ["en", "es", "fr", "de"]

def run_command(cmd):
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.stdout, result.returncode

def process_video(project_name, video_id):
    print(f"\n🚀 --- Processing: {project_name} ({video_id}) ---")
    project_path = os.path.join(CLEANED_DIR, project_name)
    intl_path = os.path.join(project_path, "international")
    os.makedirs(intl_path, exist_ok=True)

    # 1. Download Italian SRT
    it_srt_path = os.path.join(project_path, "subtitles_it.srt")
    
    print(f"📡 Step 1: Downloading Italian captions for {video_id}...")
    # Use the script with format=srt and direct output path
    # We call it as a module or as a subprocess
    download_cmd = [PYTHON_BIN, DOWNLOADER, video_id, "--format", "srt", "--output", it_srt_path]
    stdout, code = run_command(download_cmd)
    
    if code != 0 or not os.path.exists(it_srt_path):
        print(f"❌ Failed to download Italian SRT for {video_id}")
        return

    # 2. Translation & Organization
    for lang in LANGUAGES:
        lang_dir = os.path.join(intl_path, lang)
        os.makedirs(lang_dir, exist_ok=True)
        out_srt = os.path.join(lang_dir, f"subtitles_{lang}.srt")
        
        print(f"🌍 Step 2: Translating to {lang} -> {out_srt}...")
        translate_cmd = [PYTHON_BIN, TRANSLATOR, it_srt_path, out_srt, lang]
        stdout, code = run_command(translate_cmd)
        
        if code != 0:
            print(f"⚠️ Warning: Failed to translate {lang} for {video_id}")
            continue
            
    # 3. Upload
    print(f"⬆️ Step 3: Uploading localized captions...")
    # update_video_localization.py handles the discovery of files in the intl_path
    uploader_cmd = [PYTHON_BIN, UPLOADER, "--video_id", video_id, "--intl_path", intl_path]
    stdout, code = run_command(uploader_cmd)
    
    if code == 0:
        print(f"✅ SUCCESS: All operations completed for {project_name}")
    else:
        print(f"❌ Error during upload for {project_name}")

if __name__ == "__main__":
    print("🎬 Caption Manager Batch Execution Started")
    for proj, vid in PROJECTS.items():
        process_video(proj, vid)
    print("\n🏁 Batch processing finished.")

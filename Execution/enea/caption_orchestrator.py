import os
import subprocess
import time

# Percorsi
BASE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale"
EXEC_DIR = os.path.join(BASE_DIR, "Execution")
CLEANED_DIR = os.path.join(BASE_DIR, "Cleaned")
PYTHON_BIN = os.path.join(BASE_DIR, ".venv/bin/python3")

# Target Projects
PROJECTS = {
    "Dalle_Guerre_ai_Capolavori": {"id": "n_8eHt5ZjXY", "langs": ["en", "es", "fr", "de"]},
    "Il_Talento_Non_Ha_Genere": {"id": "CkMiVsvnP0U", "langs": ["en", "es", "fr", "de"]},
    "Il_Pallone_Unisce_le_Nazioni": {"id": "y4zWdljXoPY", "langs": ["es", "fr", "de"]} # EN already exists
}

def run_translation(project):
    it_srt = os.path.join(CLEANED_DIR, project, "subtitles_it.srt")
    if not os.path.exists(it_srt):
        print(f"❌ Skipping {project}: IT SRT not found.")
        return
    
    for lang_code in PROJECTS[project]["langs"]:
        lang_name = {"en": "English", "es": "Spanish", "fr": "French", "de": "German"}[lang_code]
        out_srt = os.path.join(CLEANED_DIR, project, "international", lang_code, f"subtitles_{lang_code}.srt")
        
        if os.path.exists(out_srt):
            print(f"⏩ {project} ({lang_code}) already exists. Skipping.")
            continue
            
        print(f"🌍 Translating {project} to {lang_name}...")
        cmd = [PYTHON_BIN, os.path.join(EXEC_DIR, "enea/translate_srt.py"), it_srt, out_srt, lang_name]
        try:
            subprocess.run(cmd, check=True)
            time.sleep(10) # Wait a bit between translations to avoid rate limits
        except subprocess.CalledProcessError:
            print(f"❌ Failed translation for {project} ({lang_code})")

def run_upload(project):
    video_id = PROJECTS[project]["id"]
    intl_dir = os.path.join(CLEANED_DIR, project, "international")
    
    if not os.path.exists(intl_dir):
        return

    for lang_code in os.listdir(intl_dir):
        lang_path = os.path.join(intl_dir, lang_code)
        if not os.path.isdir(lang_path): continue
        
        srt_file = os.path.join(lang_path, f"subtitles_{lang_code}.srt")
        if os.path.exists(srt_file):
            print(f"📤 Uploading {lang_code} subtitles for {project} (ID: {video_id})...")
            # Using the existing update_video_localization logic via a small script or subprocess
            cmd = [PYTHON_BIN, os.path.join(EXEC_DIR, "romolo/update_video_localization.py"), "--video-id", video_id, "--captions", srt_file, "--language", lang_code]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                print(f"❌ Failed upload for {project} ({lang_code})")

if __name__ == "__main__":
    for proj in PROJECTS:
        run_translation(proj)
        run_upload(proj)
    print("✨ Subtitle Orchestration Complete.")

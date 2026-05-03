import os
import sys
import glob
import shutil
from pathlib import Path

# Configurazione Percorsi
BASE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale"
CLEANED_DIR = os.path.join(BASE_DIR, "Cleaned")
EXEC_DIR = os.path.join(BASE_DIR, "Execution")
PYTHON_BIN = os.path.join(BASE_DIR, ".venv/bin/python3")
TRACKING_MANAGER = os.path.join(EXEC_DIR, "enea/tracking_manager.py")

def cleanup_project(project_name, dry_run=False):
    project_path = os.path.join(CLEANED_DIR, project_name)
    if not os.path.exists(project_path):
        print(f"❌ Project not found: {project_path}")
        return False

    print(f"\n🧹 --- Cleaning Project: {project_name} {'(DRY RUN)' if dry_run else ''} ---")
    
    # 1. Ensure international/ exists
    intl_path = os.path.join(project_path, "international")
    if not dry_run:
        os.makedirs(intl_path, exist_ok=True)

    # 2. Archive transcripts/subtitles if they are in the root
    text_extensions = ['*.txt', '*.srt', '*.vtt']
    for ext in text_extensions:
        for file_path in glob.glob(os.path.join(project_path, ext)):
            filename = os.path.basename(file_path)
            # Mandatory preservation files to NOT move
            if filename == "video_metadata.md": 
                continue
            
            dest = os.path.join(intl_path, filename)
            print(f"📦 Archiving: {filename} -> international/")
            if not dry_run:
                shutil.move(file_path, dest)

    # 3. Identify files to DELETE
    to_delete_patterns = [
        '*_raw.mp4', 
        '*_cleaned.mp4', 
        'infografica_raw.png',
        'audio_raw.wav',
        '*.log',
        '*_assets.json',
        '*.pdf'
    ]
    
    deleted_count = 0
    for pattern in to_delete_patterns:
        for file_path in glob.glob(os.path.join(project_path, pattern)):
            filename = os.path.basename(file_path)
            print(f"🗑️ Deleting: {filename}")
            if not dry_run:
                os.remove(file_path)
            deleted_count += 1

    # 4. Final Audit (Logging status)
    if not dry_run:
        import subprocess
        try:
            print(f"📝 Updating tracking status for {project_name}...")
            # Use the CLI interface of tracking_manager.py
            subprocess.run([PYTHON_BIN, TRACKING_MANAGER, project_name, "status", "Pulito"], check=True)
        except Exception as e:
            print(f"⚠️ Warning: Could not update tracking JSON: {e}")

    print(f"✨ Cleanup finished. {deleted_count} files removed.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python video_cleanup.py <project_name> [--dry-run]")
        sys.exit(1)
    
    proj = sys.argv[1]
    is_dry = "--dry-run" in sys.argv
    cleanup_project(proj, is_dry)

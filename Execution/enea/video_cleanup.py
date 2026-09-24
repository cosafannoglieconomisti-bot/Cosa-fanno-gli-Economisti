import os
import sys
import glob
import shutil
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

# Configurazione Percorsi
BASE_DIR = str(REPO_ROOT)
CLEANED_DIR = os.path.join(BASE_DIR, "Cleaned")
EXEC_DIR = os.path.join(BASE_DIR, "Execution")
PYTHON_BIN = os.path.join(BASE_DIR, ".venv/bin/python3")
TRACKING_MANAGER = os.path.join(EXEC_DIR, "enea/tracking_manager.py")

# KEEP: copertina.png, *infografica*.png (cleaned), video_metadata.md,
#       international/, shorts/international/ (testuali).
# DELETE: mp4 (root + shorts/**), pdf, infografica_raw, wav/log/jpg upload, _old_* dirs.


def _delete_file(path, dry_run=False):
    print(f"🗑️ Deleting: {os.path.relpath(path, BASE_DIR)}")
    if not dry_run:
        os.remove(path)


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
    text_extensions = ["*.txt", "*.srt", "*.vtt"]
    for ext in text_extensions:
        for file_path in glob.glob(os.path.join(project_path, ext)):
            filename = os.path.basename(file_path)
            if filename == "video_metadata.md":
                continue
            dest = os.path.join(intl_path, filename)
            print(f"📦 Archiving: {filename} -> international/")
            if not dry_run:
                shutil.move(file_path, dest)

    # 3. Identify files to DELETE in project root
    to_delete_patterns = [
        "*_raw.mp4",
        "*_cleaned.mp4",
        "infografica_raw.png",
        "audio_raw.wav",
        "copertina_upload.jpg",
        "copertina.jpg",
        "*.log",
        "*_assets.json",
        "*.pdf",
        "*.mp4",
        "*.wav",
    ]

    deleted_count = 0
    for pattern in to_delete_patterns:
        for file_path in glob.glob(os.path.join(project_path, pattern)):
            filename = os.path.basename(file_path)
            # Keep cleaned infographic / cover pngs — only mp4/pdf/raw patterns above
            if filename.lower().endswith(".png") and "infografica" in filename.lower() and "raw" not in filename.lower():
                continue
            _delete_file(file_path, dry_run=dry_run)
            deleted_count += 1

    # 4. Recursively delete ALL mp4 under shorts/ (raw + cleaned)
    shorts_dir = os.path.join(project_path, "shorts")
    if os.path.isdir(shorts_dir):
        for root, _dirs, files in os.walk(shorts_dir):
            for name in files:
                if name.lower().endswith(".mp4"):
                    _delete_file(os.path.join(root, name), dry_run=dry_run)
                    deleted_count += 1

    # 5. Optional: remove _old_* dirs under the project
    for entry in os.listdir(project_path):
        full = os.path.join(project_path, entry)
        if os.path.isdir(full) and entry.startswith("_old"):
            print(f"🗑️ Removing old dir: {entry}/")
            if not dry_run:
                shutil.rmtree(full)
            deleted_count += 1

    # 6. Root leftovers matching project name
    print("🧹 Scanning root directory for leftovers...")
    for pattern in ["*.mp4", "*.wav", "*.pdf"]:
        for file_path in glob.glob(os.path.join(BASE_DIR, pattern)):
            filename = os.path.basename(file_path)
            if project_name.lower() in filename.lower() or "download" in filename.lower():
                _delete_file(file_path, dry_run=dry_run)
                deleted_count += 1

    # 7. Tracking -> Pulito
    if not dry_run:
        import subprocess
        try:
            print(f"📝 Updating tracking status for {project_name}...")
            subprocess.run([PYTHON_BIN, TRACKING_MANAGER, project_name, "status", "Pulito"], check=True)
        except Exception as e:
            print(f"⚠️ Warning: Could not update tracking JSON: {e}")

    print(f"✨ Cleanup finished. {deleted_count} files/dirs removed.")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python video_cleanup.py <project_name> [--dry-run]")
        sys.exit(1)

    proj = sys.argv[1]
    is_dry = "--dry-run" in sys.argv
    ok = cleanup_project(proj, is_dry)
    sys.exit(0 if ok else 1)

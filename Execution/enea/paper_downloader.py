import os
import shutil
import time
import re
import argparse
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()

from dotenv import load_dotenv
import fitz  # PyMuPDF

# Configuration
BASE_DIR = REPO_ROOT
DOWNLOADS_DIR = HOME / "Downloads"
TARGET_DIR = BASE_DIR / "Papers/Da fare"
CLEANED_DIR = BASE_DIR / "Cleaned"
ENV_PATH = BASE_DIR / ".env"

# Load environment variables
load_dotenv(ENV_PATH)

def extract_text(pdf_path, max_pages=3):
    """Extracts first few pages of text from PDF."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for i in range(min(len(doc), max_pages)):
            text += doc[i].get_text()
        return text
    except Exception as e:
        print(f"❌ Error reading {pdf_path.name}: {e}")
        return ""

def get_academic_title(pdf_text):
    """Estrae il titolo accademico con regole locali dal testo del PDF."""
    cleaned_lines = []
    for raw_line in pdf_text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line or len(line) < 8:
            continue
        if line.lower().startswith(("abstract", "introduction", "jel", "keywords", "contents")):
            continue
        if re.fullmatch(r"[\d\W_]+", line):
            continue
        cleaned_lines.append(line)

    if not cleaned_lines:
        return None

    title_lines = []
    for line in cleaned_lines[:12]:
        lower = line.lower()
        if any(token in lower for token in ["university", "department", "institute", "@", "http://", "https://"]):
            if title_lines:
                break
            continue
        if len(line.split()) > 20:
            if title_lines:
                break
            continue
        title_lines.append(line)
        if len(" ".join(title_lines)) >= 40 and len(title_lines) >= 2:
            break

    title = " ".join(title_lines).strip()
    if title.endswith(":") and len(cleaned_lines) > len(title_lines):
        title = f"{title} {cleaned_lines[len(title_lines)].rstrip('*†‡∗')}".strip()
    title = re.sub(r"\s+", " ", title)
    return title or None

def sanitize_filename(name):
    """Sanitizes the filename for Unix/Mac systems."""
    # Remove invalid characters
    clean = re.sub(r'[/\\?%*:|"<>!]', '', name)
    # Replace whitespace and repeated underscores
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def is_duplicate(title, target_dir):
    """Checks if a paper with an heart-beat title already exists."""
    clean_title = sanitize_filename(title).lower()
    # Check in Da Fare
    for file in target_dir.glob("*.pdf"):
        if sanitize_filename(file.stem).lower() == clean_title:
            return True
    
    # Optional: Check in Cleaned (subfolders)
    for folder in CLEANED_DIR.iterdir():
        if folder.is_dir() and sanitize_filename(folder.name).lower() == clean_title:
            return True
            
    return False

def main():
    parser = argparse.ArgumentParser(description="Scarica PDF recenti da Downloads in Papers/Da fare")
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Finestra in giorni per PDF in Downloads (default: 1)",
    )
    args = parser.parse_args()

    print("🚀 Running /download workflow...")
    
    if not DOWNLOADS_DIR.exists():
        print(f"❌ Error: Downloads directory not found at {DOWNLOADS_DIR}")
        return

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    now = time.time()
    window_sec = max(1, args.days) * 24 * 60 * 60
    
    pdfs_in_downloads = list(DOWNLOADS_DIR.glob("*.pdf"))
    recent_pdfs = [f for f in pdfs_in_downloads if (now - f.stat().st_mtime) <= window_sec]
    skipped_old = len(pdfs_in_downloads) - len(recent_pdfs)
    
    if not recent_pdfs:
        msg = f"✅ No recent PDFs found in Downloads (last {args.days} day(s))."
        if skipped_old:
            msg += f" {skipped_old} PDF più vecchi ignorati."
        print(msg)
        return

    print(f"🔍 Found {len(recent_pdfs)} PDFs in Downloads from the last {args.days} day(s).")
    if skipped_old:
        print(f"ℹ️ {skipped_old} PDF scartati perché più vecchi di {args.days} giorno/i.")
    
    moved_count = 0
    
    for pdf in recent_pdfs:
        print(f"\n📄 Processing: {pdf.name}")
        
        # 1. Extract text
        text = extract_text(pdf)
        if not text:
            print(f"⚠️ Skipping {pdf.name} (could not extract text).")
            continue
            
        # 2. Extract Academic Title
        academic_title = get_academic_title(text)
        if not academic_title:
            print(f"⚠️ Could not extract title for {pdf.name}. Using original name.")
            academic_title = pdf.stem
            
        print(f"✨ Detected Title: {academic_title}")
        
        # 3. Check for duplicates
        if is_duplicate(academic_title, TARGET_DIR):
            print(f"⏭️ Skipping {pdf.name} (duplicate detected in Papers or Cleaned).")
            continue
            
        # 4. Move and Rename
        clean_name = sanitize_filename(academic_title) + ".pdf"
        dest_path = TARGET_DIR / clean_name
        
        try:
            shutil.move(str(pdf), str(dest_path))
            print(f"✅ Moved: {pdf.name} -> Papers/Da fare/{clean_name}")
            moved_count += 1
        except Exception as e:
            print(f"❌ Error moving file {pdf.name}: {e}")

    print(f"\n✨ Workflow completed. {moved_count} papers ingested successfully.")

if __name__ == "__main__":
    main()

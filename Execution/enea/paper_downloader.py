import os
import shutil
import time
import re
from pathlib import Path
from google import genai
from dotenv import load_dotenv
import fitz  # PyMuPDF

# Configuration
BASE_DIR = Path("/Users/marcolemoglie_1_2/Desktop/canale")
DOWNLOADS_DIR = Path("/Users/marcolemoglie_1_2/Downloads")
TARGET_DIR = BASE_DIR / "Papers/Da fare"
CLEANED_DIR = BASE_DIR / "Cleaned"
ENV_PATH = BASE_DIR / ".env"

# Load environment variables
load_dotenv(ENV_PATH)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
    """Uses Gemini to extract the real academic title from text."""
    if not GEMINI_API_KEY:
        print("⚠️ Warning: GEMINI_API_KEY not found. Using filename as title.")
        return None

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""Extract the exact academic title of the paper from the following text (first 3 pages).
    Output ONLY the title, nothing else. No punctuation at the end.
    
    TEXT:
    {pdf_text[:10000]}
    """
    
    try:
        response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"⚠️ Gemini API Error: {e}")
    return None

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
    print("🚀 Running /download workflow...")
    
    if not DOWNLOADS_DIR.exists():
        print(f"❌ Error: Downloads directory not found at {DOWNLOADS_DIR}")
        return

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    now = time.time()
    one_day_sec = 24 * 60 * 60
    
    pdfs_in_downloads = list(DOWNLOADS_DIR.glob("*.pdf"))
    recent_pdfs = [f for f in pdfs_in_downloads if (now - f.stat().st_mtime) <= one_day_sec]
    
    if not recent_pdfs:
        print("✅ No recent PDFs found in Downloads (last 24h).")
        return

    print(f"🔍 Found {len(recent_pdfs)} PDFs in Downloads from the last 24h.")
    
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

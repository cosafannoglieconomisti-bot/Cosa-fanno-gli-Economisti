import fitz
import os

def get_pdf_title(path):
    try:
        doc = fitz.open(path)
        meta_title = doc.metadata.get('title')
        if meta_title and len(meta_title.strip()) > 3 and not meta_title.lower().startswith('aer.'):
            return meta_title
        
        page = doc[0]
        text = page.get_text()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            return lines[0][:80]
    except Exception:
        pass
    return os.path.basename(path)

full_path = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare"
for f in os.listdir(full_path):
    if f.endswith(".pdf"):
        print(f"[{f}] -> {get_pdf_title(os.path.join(full_path, f))}")

import os
import json
import re
from datetime import datetime

# Paths
BASE_DIR = os.path.expanduser("~/.gemini/antigravity")
CONV_DIR = os.path.join(BASE_DIR, "conversations")
BRAIN_DIR = os.path.join(BASE_DIR, "brain")
OUTPUT_FILE = os.path.join(BASE_DIR, "history_index.json")

def extract_title_from_md(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Look for first H1 or major title
            match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if match:
                return match.group(1).split("[")[0].strip()
    except Exception:
        pass
    return None

def reindex():
    print(f"[INFO] Scansione cartella: {CONV_DIR}")
    if not os.path.exists(CONV_DIR):
        print(f"[ERROR] Cartella conversazioni mancante: {CONV_DIR}")
        return

    history = []
    
    for filename in os.listdir(CONV_DIR):
        if filename.endswith(".pb"):
            conv_id = filename.replace(".pb", "")
            file_path = os.path.join(CONV_DIR, filename)
            
            # Metadata from file stats
            mtime = os.path.getmtime(file_path)
            last_modified = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            # Try to find a title in brain folder
            title = None
            brain_path = os.path.join(BRAIN_DIR, conv_id)
            if os.path.exists(brain_path):
                # Search priority: implementation_plan > task > walkthrough
                for md_file in ["implementation_plan.md", "task.md", "walkthrough.md"]:
                    title = extract_title_from_md(os.path.join(brain_path, md_file))
                    if title:
                        break
            
            history.append({
                "id": conv_id,
                "title": title or f"Conversazione {conv_id[:8]}...",
                "last_modified": last_modified,
                "timestamp": mtime
            })

    # Sort by recent first
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    
    print(f"[SUCCESS] Indice ricostruito con {len(history)} sessioni.")
    print(f"[INFO] Risultato salvato in: {OUTPUT_FILE}")

if __name__ == "__main__":
    reindex()

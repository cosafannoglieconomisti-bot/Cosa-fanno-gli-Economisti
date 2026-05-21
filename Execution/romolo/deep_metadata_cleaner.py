import os
import json
import re
import sys

# Aggiungi il path per importare i moduli romolo
sys.path.append("/Users/marcolemoglie_1_2/Desktop/canale")
from Execution.romolo.internal_linker import find_related_videos

CLEANED_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
TRACKING_FILE = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/video_tracking.json"

FORBIDDEN_TAGS = ["#Socialismo", "#Destra", "#Sinistra", "#Amore", "#Documenti", "#730", "#CIE"]

def deep_clean():
    if not os.path.exists(TRACKING_FILE):
        print("❌ Tracking file non trovato.")
        return

    with open(TRACKING_FILE, "r", encoding="utf-8") as f:
        archive = json.load(f)

    for folder in os.listdir(CLEANED_DIR):
        folder_path = os.path.join(CLEANED_DIR, folder)
        if not os.path.isdir(folder_path): continue
        
        meta_path = os.path.join(folder_path, "video_metadata.md")
        if not os.path.exists(meta_path): continue

        print(f"🧹 Pulizia profonda: {folder}...")
        
        with open(meta_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Pulizia TAG Allucinati
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith("#"):
                # Rimuovi tag proibiti
                for ft in FORBIDDEN_TAGS:
                    line = re.sub(rf"{ft}\b", "", line, flags=re.IGNORECASE)
                # Pulisci spazi multipli
                line = re.sub(r"\s+", " ", line).strip()
            new_lines.append(line)
        content = "\n".join(new_lines)

        # 2. Rifacimento INTERNAL LINKS (Stretta Playlist)
        # Identifica la sezione GUARDA ANCHE
        if "📺 GUARDA ANCHE:" in content:
            related = find_related_videos(folder, archive, count=2)
            if related:
                links_text = "📺 GUARDA ANCHE:\n"
                for r_title, r_url in related:
                    links_text += f"► {r_title}: {r_url}\n"
                
                # Sostituzione con regex per coprire il blocco fino alla riga vuota o Fonte
                pattern = r"📺 GUARDA ANCHE:.*?(?=\n\n|⏰ Fonte:)"
                content = re.sub(pattern, links_text.strip(), content, flags=re.DOTALL)

        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    deep_clean()

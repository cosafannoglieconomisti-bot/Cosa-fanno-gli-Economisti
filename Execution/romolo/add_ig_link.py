import os
import re

CLEANED_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
IG_LINK = "📸 Infografica completa su Instagram: https://www.instagram.com/cosafannoglieconomisti/"

def add_ig_link_to_metadata():
    for folder in os.listdir(CLEANED_DIR):
        folder_path = os.path.join(CLEANED_DIR, folder)
        if not os.path.isdir(folder_path): continue
        
        meta_path = os.path.join(folder_path, "video_metadata.md")
        if not os.path.exists(meta_path): continue

        with open(meta_path, "r", encoding="utf-8") as f:
            content = f.read()

        if IG_LINK not in content:
            print(f"🔗 Aggiunta link Instagram: {folder}...")
            # Regex flessibile: ⏰ seguito da spazi opzionali, poi Fonte/Fonti/ISCRIVITI/FONTI in ogni case
            parts = re.split(r"(⏰\s*(Fonte|Fonti|ISCRIVITI|FONTI|FONTE))", content, 1, flags=re.IGNORECASE)
            if len(parts) >= 2:
                before = parts[0].strip()
                delimiter = parts[1]
                after = parts[len(parts)-1]
                
                new_content = before + "\n\n" + IG_LINK + "\n\n" + delimiter + after
                
                with open(meta_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

if __name__ == "__main__":
    add_ig_link_to_metadata()

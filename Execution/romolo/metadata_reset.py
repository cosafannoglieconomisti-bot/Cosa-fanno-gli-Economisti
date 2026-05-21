import os
import re

CLEANED_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"

def reset_metadata():
    for folder in os.listdir(CLEANED_DIR):
        folder_path = os.path.join(CLEANED_DIR, folder)
        if not os.path.isdir(folder_path): continue
        
        meta_path = os.path.join(folder_path, "video_metadata.md")
        if not os.path.exists(meta_path): continue

        print(f"♻️ Ripristino metadati: {folder}...")
        
        with open(meta_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Rimuovi la sezione GUARDA ANCHE interamente
        # pattern: da "📺 GUARDA ANCHE:" fino alla riga vuota successiva o Fonte
        pattern = r"📺 GUARDA ANCHE:.*?(?=\n\n|⏰ Fonte:|⏰ISCRIVITI)"
        content = re.sub(pattern, "", content, flags=re.DOTALL)
        
        # Pulisci eventuali doppie righe vuote create dalla rimozione
        content = re.sub(r"\n{3,}", "\n\n", content)

        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    reset_metadata()

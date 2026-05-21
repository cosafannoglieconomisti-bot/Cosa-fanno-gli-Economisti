import os
import json
import re
import sys

sys.path.append("/Users/marcolemoglie_1_2/Desktop/canale")
from Execution.romolo.internal_linker import find_related_videos

CLEANED_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
TRACKING_FILE = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/video_tracking.json"

# Parole da rimuovere ovunque (allucinazioni ricorrenti)
JUNK_PATTERNS = [
    r"#730Precompilato", r"#730", r"#CIE", r"#Documenti", r"#IdentitàDigitale",
    r"Video Metadati -", r"Metadati #", r"verità #", r"culturale #", r"Questione le Amiamo tasse\?"
]

def heal_metadata():
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

        print(f"🩹 Healing: {folder}...")
        
        with open(meta_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines: continue

        # 1. Reset Header
        lines[0] = f"# Metadati Video - {folder}\n"
        
        # 2. Cleanup generalizzato (rimozione junk patterns)
        new_lines = []
        for line in lines:
            # Se è la riga della descrizione YouTube, puliscila da tag messi a caso
            if line.startswith("## Descrizione YouTube"):
                line = "## Descrizione YouTube\n"
            
            # Applica rimozione junk
            for pattern in JUNK_PATTERNS:
                line = re.sub(pattern, "", line, flags=re.IGNORECASE)
            
            # Pulisci spazi extra e cancelletti solitari
            line = re.sub(r"\s+#\s+", " ", line)
            line = re.sub(r" {2,}", " ", line)
            
            new_lines.append(line)

        content = "".join(new_lines)

        # 3. Rifacimento INTERNAL LINKS (per sicurezza, usiamo il nuovo linker)
        if "📺 GUARDA ANCHE:" in content:
            related = find_related_videos(folder, archive, count=2)
            if related:
                links_text = "📺 GUARDA ANCHE:\n"
                for r_title, r_url in related:
                    links_text += f"► {r_title}: {r_url}\n"
                
                # Regex robusta per sostituire il blocco
                pattern = r"📺 GUARDA ANCHE:.*?(?=\n\n|⏰ Fonte:|⏰ISCRIVITI)"
                content = re.sub(pattern, links_text + "\n", content, flags=re.DOTALL)

        # 4. Pulizia Hashtag finali (Rimuovi Socialismo se non pertinente)
        # Se il folder non è "Socialismo_la_causa_del_Fascismo", rimuoviamo #Socialismo
        if folder != "Socialismo_la_causa_del_Fascismo":
            content = re.sub(r"#Socialismo\b", "", content, flags=re.IGNORECASE)

        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    heal_metadata()

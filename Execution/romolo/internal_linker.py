import os
import json
import re

# Configurazione
CANALE_ROOT = "/Users/marcolemoglie_1_2/Desktop/canale"
TRACKING_FILE = os.path.join(CANALE_ROOT, "Cleaned/video_tracking.json")

def find_related_videos(current_title, archive, count=2):
    current_data = archive.get(current_title)
    if not current_data: return []
    
    current_playlist = current_data.get("playlist")
    related = []
    
    # Logica di matching RIGIDA: Solo stessa playlist
    for title, data in archive.items():
        if title != current_title and data.get("playlist") == current_playlist:
            if data.get("youtube_url"):
                related.append((title, data.get("youtube_url")))
        if len(related) >= count: break
            
    return related[:count]

def update_metadata_with_links():
    if not os.path.exists(TRACKING_FILE):
        print("❌ video_tracking.json non trovato.")
        return

    with open(TRACKING_FILE, 'r') as f:
        archive = json.load(f)

    updated_count = 0
    for title, data in archive.items():
        # Cerca il file metadata nella cartella Cleaned/[Titolo]
        clean_title = title.replace(" ", "_") # Convenzione cartelle
        # Cerchiamo la cartella che contiene il titolo
        folder_path = None
        for d in os.listdir(os.path.join(CANALE_ROOT, "Cleaned")):
            if title in d or d in title:
                folder_path = os.path.join(CANALE_ROOT, "Cleaned", d)
                break
        
        if not folder_path or not os.path.isdir(folder_path):
            continue
            
        metadata_file = os.path.join(folder_path, "video_metadata.md")
        if not os.path.exists(metadata_file):
            # Prova a cercare file che iniziano con video_metadata
            for f in os.listdir(folder_path):
                if f.startswith("video_metadata"):
                    metadata_file = os.path.join(folder_path, f)
                    break
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                content = f.read()
            
            # Se ha già i link correlati, saltiamo o aggiorniamo? Per ora saltiamo per sicurezza
            if "📺 GUARDA ANCHE:" in content:
                continue
                
            related = find_related_videos(title, archive)
            if not related: continue
            
            links_text = "\n\n📺 GUARDA ANCHE:\n"
            for r_title, r_url in related:
                links_text += f"► {r_title}: {r_url}\n"
            
            # Inserimento dopo il primo paragrafo della descrizione
            # Cerchiamo la fine del paragrafo che inizia con "Lo studio..."
            match = re.search(r'(Lo studio.*?\.)\n', content, re.DOTALL)
            if match:
                new_content = content[:match.end()] + links_text + content[match.end():]
                with open(metadata_file, 'w') as f:
                    f.write(new_content)
                print(f"✅ Aggiornato internal linking per: {title}")
                updated_count += 1

    print(f"🚀 Total video aggiornati: {updated_count}")

if __name__ == "__main__":
    update_metadata_with_links()

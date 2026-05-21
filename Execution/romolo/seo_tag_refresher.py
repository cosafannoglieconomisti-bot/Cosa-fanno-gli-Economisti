import os
import json
import sys
import re
from google import genai
from dotenv import load_dotenv

# Path per import news
sys.path.append("/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse")
from news_extractor import get_raw_news_batch

# Configurazione
load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CANALE_ROOT = "/Users/marcolemoglie_1_2/Desktop/canale"
TRACKING_FILE = os.path.join(CANALE_ROOT, "Cleaned/video_tracking.json")

def refresh_tags():
    if not GEMINI_API_KEY:
        print("❌ API Key mancante.")
        return

    with open(TRACKING_FILE, 'r') as f:
        archive = json.load(f)

    print("📰 Recupero trend attuali...")
    news = get_raw_news_batch()
    news_context = "\n".join([n['topic'] for n in news[:10]])

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    updated_count = 0
    for title, data in archive.items():
        # Troviamo la cartella
        folder_path = None
        for d in os.listdir(os.path.join(CANALE_ROOT, "Cleaned")):
            if title in d or d in title:
                folder_path = os.path.join(CANALE_ROOT, "Cleaned", d)
                break
        
        if not folder_path or not os.path.isdir(folder_path): continue
        
        metadata_file = os.path.join(folder_path, "video_metadata.md")
        if not os.path.exists(metadata_file):
            for f in os.listdir(folder_path):
                if f.startswith("video_metadata"):
                    metadata_file = os.path.join(folder_path, f)
                    break
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                content = f.read()

            # Chiediamo a Gemini se c'è un match e quali tag aggiungere
            prompt = f"""Analizza questo titolo video di ricerca economica: "{title}" 
            e queste news di oggi:
            {news_context}
            
            Se c'è una correlazione STRETTA tra il tema della ricerca economica e la news, suggerisci 3 hashtag SEO (formato #Tag).
            REGOLE MANDATORIE:
            1. Usa solo termini ECONOMICI, STATISTICI o ACCADEMICI (es: #Welfare, #Dati, #Microeconomia).
            2. Evita ASSOLUTAMENTE etichette politiche, ideologie o termini generici come #socialismo, #destra, #sinistra.
            3. Se non c'è una correlazione evidente e seria, rispondi 'NONE'.
            Rispondi solo con i tag o 'NONE'."""

            try:
                response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
                tags = response.text.strip()
                
                if "NONE" not in tags and "#" in tags:
                    # Pulizia tag esistenti (solo quelli in fondo)
                    # Cerchiamo l'ultima riga di tag
                    lines = content.splitlines()
                    new_lines = []
                    tag_line_found = False
                    for line in lines:
                        if line.startswith("#") and not tag_line_found:
                            # Aggiungiamo i nuovi tag a quelli esistenti
                            existing_tags = line.split()
                            new_tags = tags.split()
                            combined = list(set(existing_tags + new_tags))
                            new_lines.append(" ".join(combined[:10])) # Max 10 tag
                            tag_line_found = True
                        else:
                            new_lines.append(line)
                    
                    if not tag_line_found:
                        new_lines.append("\n" + tags)
                    
                    with open(metadata_file, 'w') as f:
                        f.write("\n".join(new_lines))
                    print(f"🏷️ Tag aggiornati per: {title}")
                    updated_count += 1
            except:
                continue

    print(f"🚀 SEO Refresh completato. Video ottimizzati: {updated_count}")

if __name__ == "__main__":
    refresh_tags()

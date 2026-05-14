import os
import json
import pickle
import sys
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Configurazione percorsi
BASE_DIR = '/Users/marcolemoglie_1_2/Desktop/canale'
CRED_DIR = os.path.join(BASE_DIR, 'Execution/credentials')
load_dotenv(dotenv_path=os.path.join(CRED_DIR, '.env'))

def get_youtube_service():
    token_path = os.path.join(CRED_DIR, 'token_youtube.pickle')
    if not os.path.exists(token_path):
        print(f"❌ Errore: Token non trovato in {token_path}")
        sys.exit(1)
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

# Metadati statici corretti (SOP: Link in riga isolata, Titolo catchy)
CORRECTIONS = {
    "DSucrUBXJws": {
        "title": "L'aratro ha creato il patriarcato? 🚜",
        "description": "Scopri come un'innovazione agricola millenaria ha plasmato i ruoli di genere.\n\nVideo completo qui: https://youtu.be/gzk8eMmJVfs\n\n#CosaFannoGliEconomisti #Aratro #Patriarcato"
    },
    "TE2601I7Y1c": {
        "title": "Dio blocca la democrazia? ⛪️\ufe0f🗳\ufe0f",
        "description": "Le credenze religiose possono ostacolare la transizione democratica?\n\nVideo completo qui: https://youtu.be/BFW6hmE5WiQ\n\n#CosaFannoGliEconomisti #Democrazia #Religione"
    },
    "_D02ygxnHGk": {
        "title": "La Mafia al Nord: come avviene? 📈",
        "description": "Non solo Sud: ecco come il crimine organizzato colonizza l'economia ricca.\n\nVideo completo qui: https://youtu.be/9zwAeofGwKE\n\n#CosaFannoGliEconomisti #Mafia #Economia"
    }
}

def main(real_run=False):
    youtube = get_youtube_service()
    
    for v_id, meta in CORRECTIONS.items():
        print(f"\n--- Analisi Video ID: {v_id} ---")
        print(f"Titolo Target: {meta['title']}")
        
        if real_run:
            try:
                # Recupera snippet attuale
                video_response = youtube.videos().list(part="snippet", id=v_id).execute()
                if not video_response['items']:
                    print(f"⚠️ Video {v_id} non trovato su YouTube.")
                    continue
                
                snippet = video_response['items'][0]['snippet']
                
                # Aggiorna solo se diverso (opzionale, ma utile per quota)
                if snippet['title'] == meta['title'] and snippet['description'] == meta['description']:
                    print(f"✅ Metadati già corretti per {v_id}. Salto.")
                    continue
                
                snippet['title'] = meta['title'][:100]
                snippet['description'] = meta['description']
                
                youtube.videos().update(
                    part="snippet",
                    body={"id": v_id, "snippet": snippet}
                ).execute()
                print(f"🚀 AGGIORNATO con successo!")
            except Exception as e:
                if "quotaExceeded" in str(e):
                    print(f"❌ QUOTA ESAURITA: Impossibile procedere oltre.")
                    break
                print(f"❌ Errore durante l'aggiornamento di {v_id}: {e}")
        else:
            print("🔍 [DRY RUN] Lo script aggiornerebbe questo video se eseguito con --real")
            print(f"DESCRIZIONE:\n{meta['description']}")

if __name__ == "__main__":
    is_real = "--real" in sys.argv
    main(real_run=is_real)

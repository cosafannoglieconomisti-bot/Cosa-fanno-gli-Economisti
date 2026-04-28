import os
import requests
from dotenv import load_dotenv

load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/.env")
api_key = os.getenv("SUPERMEMORY_API_KEY")
project_id = os.getenv("SUPERMEMORY_PROJECT_ID")

def verify_recall(query):
    print(f"\nInterrogazione Supermemory per: '{query}'...")
    url = "https://api.supermemory.ai/v3/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "x-sm-project": project_id
    }
    payload = {
        "q": query,
        "searchMode": "hybrid",
        "limit": 3
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            print(f"✅ Trovati {len(results)} risultati!")
            for i, res in enumerate(results):
                content = res.get("content", "")[:200]
                print(f" [{i+1}] {content}...")
        else:
            print("❌ Nessun risultato trovato.")
    else:
        print(f"❌ Errore API ({response.status_code}): {response.text}")

if __name__ == "__main__":
    # Test 1: Stili
    verify_recall("Qual'è lo stile delle copertine?")
    # Test 2: Archivio
    verify_recall("Paper sulla discriminazione dei nomi")
    # Test 3: Pipeline
    verify_recall("Cosa c'è in programma per il paper Folklore?")

import os
import requests
from dotenv import load_dotenv

load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/.env")
api_key = os.getenv("SUPERMEMORY_API_KEY")
project_id = os.getenv("SUPERMEMORY_PROJECT_ID")

def query_sm(query):
    url = "https://api.supermemory.ai/v3/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "x-sm-project": project_id
    }
    payload = {
        "q": query,
        "searchMode": "hybrid",
        "limit": 5
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        results = response.json().get("results", [])
        for i, res in enumerate(results):
            print(f"--- Risultato {i+1} ---")
            print(res.get("content", ""))
            print("\n")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    query_sm("come sbloccare download notebooklm mcp o nlm cli")

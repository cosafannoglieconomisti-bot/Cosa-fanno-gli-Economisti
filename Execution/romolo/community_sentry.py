import os
import json
import pickle
from google import genai
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

# Config
REPO_ROOT = "/Users/marcolemoglie_1_2/Desktop/canale"
CLEANED_DIR = os.path.join(REPO_ROOT, "Cleaned")
TRACKING_FILE = os.path.join(CLEANED_DIR, "video_tracking.json")
DRAFT_FILE = os.path.join(REPO_ROOT, "Temp/romolo/draft_replies.md")

def get_video_metadata(folder_name):
    path = os.path.join(CLEANED_DIR, folder_name, "video_metadata.md")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def run_sentry():
    print("🛡️ Community Sentry: Analisi commenti in corso...")
    
    # Importa funzioni da romolo_manage_channel per coerenza
    import sys
    sys.path.append(os.path.join(REPO_ROOT, "Execution/romolo"))
    from romolo_manage_channel import get_authenticated_service, SCOPES, get_channel_id, get_recent_comments

    youtube = get_authenticated_service('youtube', 'v3', SCOPES)
    channel_id = get_channel_id(youtube)
    comments = get_recent_comments(youtube, channel_id)
    
    if not comments:
        print("✅ Nessun nuovo commento da gestire.")
        return

    # Carica tracking per matchare video_id -> folder_name
    with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
        tracking = json.load(f)
    
    id_to_folder = {v.get('youtube_id'): k for k, v in tracking.items() if v.get('youtube_id')}

    drafts = []
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    for item in comments:
        snippet = item['snippet']['topLevelComment']['snippet']
        v_id = snippet.get('videoId')
        author = snippet['authorDisplayName']
        text = snippet['textOriginal']
        
        # Se ha già risposte, saltiamo (semplificazione)
        if item.get('replies'): continue

        folder = id_to_folder.get(v_id)
        context = ""
        if folder:
            context = get_video_metadata(folder)
        
        prompt = f"""Sei l'autore del canale 'Cosa fanno gli economisti'. 
Hai ricevuto questo commento da {author}: "{text}"
Sotto il video: {folder if folder else 'Video sconosciuto'}.

Dati di contesto del video (se disponibili):
{context[:2000]}

Scrivi una risposta garbata, professionale e 'high-value'. 
Se il commento è una domanda, rispondi usando i dati del paper. 
Se è un complimento, ringrazia e aggiungi una curiosità dal paper.
La risposta deve essere breve (max 3 frasi).
"""
        try:
            response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
            reply_text = response.text.strip()
            drafts.append({
                "author": author,
                "comment": text,
                "video": folder,
                "draft": reply_text,
                "comment_id": item['id']
            })
        except:
            continue

    if drafts:
        os.makedirs(os.path.dirname(DRAFT_FILE), exist_ok=True)
        with open(DRAFT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# 🛡️ Bozze Risposte Community Sentry ({len(drafts)})\n\n")
            for d in drafts:
                f.write(f"### Da: {d['author']}\n")
                f.write(f"**Commento**: {d['comment']}\n")
                f.write(f"**Video**: {d['video']}\n")
                f.write(f"**BOZZA**: {d['draft']}\n")
                f.write(f"*(ID: {d['comment_id']})*\n\n---\n\n")
        print(f"✅ Generate {len(drafts)} bozze in: {DRAFT_FILE}")

if __name__ == "__main__":
    run_sentry()

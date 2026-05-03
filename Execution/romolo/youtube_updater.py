import os
import sys
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']

def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def parse_metadata(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    description = ""
    tags = []
    
    state = None
    desc_lines = []
    
    for line in lines:
        if line.startswith("## Proposte Titoli"):
            state = "titoli"
            continue
        elif line.startswith("## Descrizione"):
            state = "desc"
            continue
        elif line.startswith("## Tag"):
            state = "tags"
            continue
            
        if state == "desc":
            if not line.startswith("##") and line.strip() != "":
                desc_lines.append(line)
        elif state == "tags":
            if line.strip():
                tags = [t.strip() for t in line.split(',') if t.strip()]
                
    description = "".join(desc_lines).strip()
    return description, tags

def update_video(youtube, video_id, title, description, tags, category_id="27"):
    body = {
        'id': video_id,
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        }
    }
    
    print(f"Updating video {video_id}...")
    try:
        response = youtube.videos().update(
            part="snippet",
            body=body
        ).execute()
        print(f"Aggiornamento completato con successo per il video ID: {response['id']}")
    except Exception as e:
        print(f"Errore durante l'aggiornamento: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python youtube_updater.py <video_id> <new_title> <metadata_file_md>")
        sys.exit(1)
        
    v_id = sys.argv[1]
    title = sys.argv[2]
    md_file = sys.argv[3]
    
    desc, tags = parse_metadata(md_file)
    yt = get_authenticated_service()
    update_video(yt, v_id, title, desc, tags)

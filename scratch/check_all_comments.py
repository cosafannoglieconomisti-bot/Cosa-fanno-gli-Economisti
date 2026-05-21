import os
import pickle
import json
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv

ROOT_PATH = "/Users/marcolemoglie_1_2/Desktop/canale"
load_dotenv(os.path.join(ROOT_PATH, 'Execution/credentials/.env'))

def get_authenticated_service():
    creds = None
    token_file = os.path.join(ROOT_PATH, "Execution/romolo/.tmp/tokens/token_youtube.pickle")
    if not os.path.exists(token_file):
        token_file = os.path.join(ROOT_PATH, "Execution/credentials/token.pickle")
    
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        else:
            print("Token non valido o mancante.")
            return None
            
    return build('youtube', 'v3', credentials=creds)

def main():
    youtube = get_authenticated_service()
    if not youtube: return

    # Recupera l'ID del canale
    ch_res = youtube.channels().list(mine=True, part='id').execute()
    channel_id = ch_res['items'][0]['id']
    print(f"Checking comments for channel: {channel_id}")

    try:
        # Usa allThreadsAtChannelId per vedere tutti i thread del canale
        results = youtube.commentThreads().list(
            part='snippet,replies',
            allThreadsAtChannelId=channel_id,
            maxResults=50,
            order='time'
        ).execute()

        items = results.get('items', [])
        if not items:
            print("Nessun commento trovato con allThreadsAtChannelId.")
        
        for item in items:
            snippet = item['snippet']['topLevelComment']['snippet']
            author = snippet['authorDisplayName']
            text = snippet['textOriginal']
            published = snippet['publishedAt']
            video_id = snippet.get('videoId', 'N/A')
            comment_id = item['id']
            
            # Controlla se abbiamo risposto (semplice check sulle replies)
            has_replies = 'replies' in item
            
            print(f"---")
            print(f"Autore: {author}")
            print(f"Data: {published}")
            print(f"Video ID: {video_id}")
            print(f"Commento: {text}")
            print(f"Risposto: {'Sì' if has_replies else 'No'}")
            print(f"ID Thread: {comment_id}")

    except Exception as e:
        print(f"Errore nel recupero commenti: {e}")

if __name__ == "__main__":
    main()

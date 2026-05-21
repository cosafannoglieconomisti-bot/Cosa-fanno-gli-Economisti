import os
import json
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

ROOT_PATH = "/Users/marcolemoglie_1_2/Desktop/canale"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

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
        else:
            return None
            
    return build('youtube', 'v3', credentials=creds)

def list_playlists():
    youtube = get_authenticated_service()
    if not youtube:
        print("Errore autenticazione")
        return
        
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    response = request.execute()
    
    print(f"Trovate {len(response.get('items', []))} playlist:")
    for item in response.get("items", []):
        print(f"- {item['snippet']['title']} (ID: {item['id']})")

if __name__ == "__main__":
    list_playlists()

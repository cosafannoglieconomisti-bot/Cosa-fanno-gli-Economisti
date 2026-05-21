import os
import json
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

ROOT_PATH = "/Users/marcolemoglie_1_2/Desktop/canale"

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

def check_playlist_items(playlist_id):
    youtube = get_authenticated_service()
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    print(f"Playlist {playlist_id} ha {len(response.get('items', []))} video:")
    for item in response.get("items", []):
        print(f"- {item['snippet']['title']} ({item['snippet']['resourceId']['videoId']})")

if __name__ == "__main__":
    # Test with "Economia del Crimine e Mafie"
    check_playlist_items("PLsnEaIfKp6RGjMnxvVNyZK5ys55Yr5J8v")

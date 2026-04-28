import os
import pickle
from googleapiclient.discovery import build

def get_authenticated_service():
    # Absolute path to the token file in Romolo folder
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def list_videos():
    youtube = get_authenticated_service()
    request = youtube.search().list(
        part="snippet",
        forMine=True,
        type="video",
        maxResults=50
    )
    response = request.execute()
    print("--- INIZIO LISTA VIDEO ---")
    for item in response.get('items', []):
        if 'videoId' in item['id']:
            print(f"ID: {item['id']['videoId']} | Title: {item['snippet']['title']}")
    print("--- FINE LISTA VIDEO ---")

if __name__ == "__main__":
    list_videos()

import os
import pickle
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def list_videos():
    youtube = get_authenticated_service()
    
    # 1. Get channel Uploads Playlist ID
    channels_resp = youtube.channels().list(
        part="contentDetails",
        mine=True
    ).execute()
    
    uploads_playlist_id = channels_resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    print(f"ID Playlist Uploads: {uploads_playlist_id}")

    # 2. List items in playlist
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=50
    )
    response = request.execute()
    
    print("--- INIZIO LISTA VIDEO (PlaylistItems) ---")
    for item in response.get('items', []):
        vid_id = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        print(f"ID: {vid_id} | Title: {title}")
    print("--- FINE LISTA VIDEO ---")

if __name__ == "__main__":
    list_videos()

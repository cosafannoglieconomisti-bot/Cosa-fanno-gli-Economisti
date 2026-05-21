import pickle
import json
import os
from googleapiclient.discovery import build

def list_all():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    youtube = build('youtube', 'v3', credentials=creds)
    
    channels_response = youtube.channels().list(mine=True, part='contentDetails').execute()
    uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    next_page_token = None
    while True:
        response = youtube.playlistItems().list(
            part='snippet', 
            playlistId=uploads_playlist_id, 
            maxResults=50, 
            pageToken=next_page_token
        ).execute()
        
        for item in response.get('items', []):
            print(f"{item['snippet']['resourceId']['videoId']} | {item['snippet']['title']}")
            
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

if __name__ == "__main__":
    list_all()

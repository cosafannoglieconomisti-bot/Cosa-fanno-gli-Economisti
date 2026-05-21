import os
import pickle
import json
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def list_videos():
    youtube = get_authenticated_service()
    # Get uploads playlist ID
    channels_response = youtube.channels().list(
        mine=True,
        part="contentDetails"
    ).execute()
    
    uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    print(f"Uploads Playlist ID: {uploads_playlist_id}")
    
    # List playlist items
    videos = []
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response.get('items', []):
            vid_id = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            description = item['snippet'].get('description', '')
            print(f"ID: {vid_id} - Title: {title}")
            videos.append({"id": vid_id, "title": title, "description": description})
            
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
            
    output_path = '/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/videos_list_updated.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)
    print(f"Aggiornato file: {output_path} (Totale: {len(videos)} video)")

if __name__ == "__main__":
    list_videos()



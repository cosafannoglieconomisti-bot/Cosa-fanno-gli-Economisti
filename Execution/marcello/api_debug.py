import os
import pickle
import json
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def debug_videos():
    youtube = get_authenticated_service()
    
    # 1. Get uploads playlist ID
    channels_response = youtube.channels().list(
        mine=True,
        part="contentDetails"
    ).execute()
    
    uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    print(f"Uploads Playlist ID: {uploads_playlist_id}")
    
    # 2. List playlist items (exhaustive with pagination)
    videos_playlist = []
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response.get('items', []):
            vid_id = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            videos_playlist.append({"id": vid_id, "title": title})
            
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    print(f"\nTrovati {len(videos_playlist)} video nella Playlist Uploads:")
    for v in videos_playlist:
        print(f" - {v['id']}: {v['title']}")

    # 3. Try standard search as fallback
    print("\n--- TEST SEARCH API ---")
    search_request = youtube.search().list(
        part="snippet",
        forMine=True,
        type="video",
        maxResults=50
    )
    search_response = search_request.execute()
    search_videos = []
    for item in search_response.get('items', []):
         search_videos.append({"id": item['id']['videoId'], "title": item['snippet']['title']})
         
    print(f"Trovati {len(search_videos)} video in Search:")
    for v in search_videos:
        print(f" - {v['id']}: {v['title']}")

if __name__ == "__main__":
    debug_videos()

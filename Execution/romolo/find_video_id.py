import os
import pickle
import json
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def search_video():
    youtube = get_authenticated_service()
    
    # Get channel ID first
    channels_response = youtube.channels().list(mine=True, part='id').execute()
    channel_id = channels_response['items'][0]['id']
    print(f"Channel ID: {channel_id}")
    
    # Search for videos with keyword 'Hitler' or 'Ascesa'
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        q="Hitler",
        type="video",
        maxResults=5
    )
    response = request.execute()
    
    found = False
    for item in response.get('items', []):
        vid_id = item['id']['videoId']
        title = item['snippet']['title']
        print(f"FOUND: ID: {vid_id} - Title: {title}")
        found = True
        
    if not found:
        print("No videos found with query 'Hitler'. Trying 'Ascesa'...")
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            q="Ascesa",
            type="video",
            maxResults=5
        )
        response = request.execute()
        for item in response.get('items', []):
            vid_id = item['id']['videoId']
            title = item['snippet']['title']
            print(f"FOUND: ID: {vid_id} - Title: {title}")

if __name__ == "__main__":
    search_video()

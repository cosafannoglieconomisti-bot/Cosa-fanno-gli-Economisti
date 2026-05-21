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
            return None
            
    return build('youtube', 'v3', credentials=creds)

def main():
    youtube = get_authenticated_service()
    if not youtube: return

    print("Fetching channel info...")
    ch_res = youtube.channels().list(mine=True, part='id').execute()
    channel_id = ch_res['items'][0]['id']

    print(f"Fetching last 15 videos for channel {channel_id}...")
    videos = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        type='video',
        order='date',
        maxResults=15
    ).execute()

    for v in videos.get('items', []):
        video_id = v['id']['videoId']
        title = v['snippet']['title']
        print(f"\nChecking video: {title} ({video_id})")
        
        try:
            comments = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                maxResults=10
            ).execute()
            
            items = comments.get('items', [])
            if not items:
                # print("  No comments.")
                continue
                
            for item in items:
                snippet = item['snippet']['topLevelComment']['snippet']
                author = snippet['authorDisplayName']
                text = snippet['textOriginal']
                pub = snippet['publishedAt']
                
                # Check for replies
                replies_count = item['snippet']['totalReplyCount']
                if replies_count == 0:
                    print(f"  [NEW] {author}: {text}")
                else:
                    print(f"  [REPLIED] {author}: {text}")
                
        except Exception as e:
            pass

if __name__ == "__main__":
    main()

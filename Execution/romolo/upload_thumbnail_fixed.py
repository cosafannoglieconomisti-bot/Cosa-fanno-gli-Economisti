import os
import pickle
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def get_authenticated_service():
    creds = None
    token_file = 'Execution/credentials/token_youtube.pickle'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def set_thumbnail(youtube, video_id, thumbnail_path):
    print(f"Uploading thumbnail {thumbnail_path} for video {video_id}...")
    try:
        print("Preparazione richiesta...")
        request = youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        )
        print("Inizio esecuzione richiesta API...")
        response = request.execute()
        print("Richiesta API completata!")
        print(f"Thumbnail uploaded successfully for video ID: {video_id}")
    except Exception as e:
        print(f"Error uploading thumbnail: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python upload_thumbnail_fixed.py <video_id> <thumbnail_path>")
        sys.exit(1)
        
    v_id = sys.argv[1]
    thumb_path = sys.argv[2]
    
    youtube = get_authenticated_service()
    set_thumbnail(youtube, v_id, thumb_path)

import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def upload_short():
    youtube = get_authenticated_service()
    
    video_path = '/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/L_ascesa_del_Male/short_intro_20s.mp4'
    title = "L'ascesa del Male - Intro #shorts"
    description = "La borsa di Berlino e Hitler. #shorts #hitler #economia"
    schedule_time_iso = '2026-03-19T08:00:00Z' # 9:00 AM CET
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['shorts', 'hitler', 'economia'],
            'categoryId': '27' # Education
        },
        'status': {
            'privacyStatus': 'private', # Must be private to set publishAt
            'publishAt': schedule_time_iso,
            'selfDeclaredMadeForKids': False
        }
    }

    print(f"Uploading Short: {video_path}")
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )
    
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
            
    video_id = response['id']
    print(f"Short Uploaded And Scheduled! ID: {video_id}")
    print(f"Scheduled for: {schedule_time_iso}")
    print(f"Link: https://youtu.be/{video_id}")

if __name__ == "__main__":
    upload_short()

import os
import pickle
import sys
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes required for uploading and setting thumbnails
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def get_authenticated_service(creds_dir):
    creds = None
    token_path = os.path.join(creds_dir, 'token.pickle')
    secrets_path = os.path.join(creds_dir, 'client_secrets.json')
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def parse_metadata_v2(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple extraction based on bold labels
    title = ""
    if "**Titolo:**" in content:
        title = content.split("**Titolo:**")[1].split("\n")[0].strip()
    
    description = ""
    if "**Descrizione:**" in content:
        description = content.split("**Descrizione:**")[1].split("**Tag:**")[0].strip()
    
    tags = []
    if "**Tag:**" in content:
        tags_str = content.split("**Tag:**")[1].strip()
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        
    return title, description, tags

def upload_and_schedule(youtube, video_path, thumb_path, title, description, tags, schedule_time_iso):
    """
    schedule_time_iso: Format 'YYYY-MM-DDTHH:MM:SSZ' (UTC)
    """
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '27' # Education
        },
        'status': {
            'privacyStatus': 'private', # Must be private to set publishAt
            'publishAt': schedule_time_iso,
            'selfDeclaredMadeForKids': False
        }
    }

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )
    
    print(f"Uploading video: {video_path}")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
            
    video_id = response['id']
    print(f"Video Uploaded! ID: {video_id}")

    # Upload thumbnail
    if thumb_path and os.path.exists(thumb_path):
        print(f"Uploading thumbnail: {thumb_path}")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumb_path)
        ).execute()
        print("Thumbnail uploaded!")

    print(f"Video scheduled for: {schedule_time_iso}")
    print(f"Link: https://youtu.be/{video_id}")
    return video_id

if __name__ == '__main__':
    # Usage: python youtube_scheduler_v2.py <video_file> <thumb_file> <metadata_file> <schedule_iso>
    if len(sys.argv) < 5:
        print("Usage: python youtube_scheduler_v2.py <video_file> <thumb_file> <metadata_file> <schedule_iso>")
        sys.exit(1)
        
    v_file = sys.argv[1]
    t_file = sys.argv[2]
    m_file = sys.argv[3]
    s_time = sys.argv[4] # e.g. 2026-03-15T08:00:00Z
    
    creds_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials"
    
    try:
        title, desc, tags = parse_metadata_v2(m_file)
        if not title:
            title = "Video Economia" # Fallback
            
        youtube = get_authenticated_service(creds_dir)
        upload_and_schedule(youtube, v_file, t_file, title, desc, tags, s_time)
    except Exception as e:
        print(f"Error: {e}")

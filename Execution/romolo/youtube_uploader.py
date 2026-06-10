import os
import pickle
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def parse_metadata(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    description = ""
    tags = []
    
    state = None
    desc_lines = []
    
    for line in lines:
        if line.startswith("## Proposte Titoli"):
            state = "titoli"
            continue
        elif line.startswith("## Descrizione"):
            state = "desc"
            continue
        elif line.startswith("## Tag"):
            state = "tags"
            continue
            
        if state == "desc":
            if not line.startswith("##") and line.strip() != "":
                desc_lines.append(line)
        elif state == "tags":
            if line.strip():
                tags = [t.strip() for t in line.split(',') if t.strip()]
                
    description = "".join(desc_lines).strip()
    return description, tags

def initialize_upload(youtube, file_path, title, description, tags, privacy_status="private"):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '27' # Education
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    
    print(f"Uploading {file_path} to YouTube...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
            
    print(f"Upload Complete! Video ID: {response['id']}")
    print(f"Link: https://youtu.be/{response['id']}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Uso: python youtube_uploader.py <video_file> <title> <metadata_file_md>")
        sys.exit(1)
        
    video_file = sys.argv[1]
    title = sys.argv[2]
    md_file = sys.argv[3]
    
    try:
        desc, tags = parse_metadata(md_file)
        youtube = get_authenticated_service()
        initialize_upload(youtube, video_file, title, desc, tags)
    except Exception as e:
        print(f"An error occurred: {e}")

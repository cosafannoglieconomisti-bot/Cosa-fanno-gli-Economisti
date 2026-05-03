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

def parse_metadata(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    description = ""
    tags = []
    state = None
    desc_lines = []
    for line in lines:
        if line.startswith("## Descrizione"):
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

def upload_video(youtube, file_path, title, description, tags, publish_at_iso=None):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '27' # Education
        },
        'status': {
            'privacyStatus': 'private' if publish_at_iso else 'public'
        }
    }
    if publish_at_iso:
        body['status']['publishAt'] = publish_at_iso

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
    video_file = sys.argv[1]
    title = sys.argv[2]
    md_file = sys.argv[3]
    publish_at = sys.argv[4]
    
    desc, tags = parse_metadata(md_file)
    youtube = get_authenticated_service()
    upload_video(youtube, video_file, title, desc, tags, publish_at)

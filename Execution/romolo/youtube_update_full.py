import os
import sys
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def get_authenticated_service():
    # Use ABSOLUTE PATH for token
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    if not os.path.exists(token_path):
        print(f"Error: Token not found at {token_path}")
        sys.exit(1)
        
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def parse_metadata_v2(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title = ""
    if "**Titolo:**" in content:
        title = content.split("**Titolo:**")[1].split("\n")[0].strip()
    
    description = ""
    if "**Descrizione:**" in content:
        desc_part = content.split("**Descrizione:**")[1]
        # Keep everything including tags, just remove the **Tag:** label
        description = desc_part.replace("**Tag:**", "").strip()
    
    tags = []
    if "**Tag:**" in content:
        tags_str = content.split("**Tag:**")[1].strip()
        # Tags are hashtag space separated usually, or comma.
        # Let's clean up hashtags
        tags = [t.strip().replace('#', '') for t in tags_str.split(' ') if t.strip()]
        
    return title, description, tags

def update_video_complete(youtube, video_id, title, description, tags, thumbnail_path, schedule_time_iso=None):
    # 1. Update Snippet and Status (Title, Desc, Tags, Schedule)
    body = {
        'id': video_id,
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '27' # Education
        }
    }
    
    print("--- BODY DA INVIARE A YOUTUBE ---")
    import json
    print(json.dumps(body, indent=2, ensure_ascii=False))
    print("-----------------------------------")
    
    parts = "snippet"
    
    if schedule_time_iso:
        body['status'] = {
            'privacyStatus': 'private', # Required for scheduled
            'publishAt': schedule_time_iso
        }
        parts += ",status"
        
    print(f"Updating video {video_id} metadata and status...")
    try:
        response = youtube.videos().update(
            part=parts,
            body=body
        ).execute()
        print(f"Metadata updated successfully.")
    except Exception as e:
        print(f"Error updating video metadata: {e}")
        return False

    # 2. Update Thumbnail
    if thumbnail_path and os.path.exists(thumbnail_path):
        print(f"Uploading thumbnail: {thumbnail_path}...")
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("Thumbnail uploaded successfully.")
        except Exception as e:
            print(f"Error uploading thumbnail: {e}")
            return False
    else:
        print(f"Thumbnail not uploaded: file not found or empty.")

    print(f"Video updated and scheduled for: {schedule_time_iso}")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python3 youtube_update_full.py <video_id> <metadata_file> <thumbnail_file> [schedule_iso]")
        print("Example schedule_iso: 2026-03-25T08:00:00Z")
        sys.exit(1)
        
    v_id = sys.argv[1]
    md_file = sys.argv[2]
    thumb_file = sys.argv[3]
    s_time = sys.argv[4] if len(sys.argv) > 4 else None
    
    try:
        title, desc, tags = parse_metadata_v2(md_file)
        if not title:
            print("Error: Could not extract title from metadata")
            sys.exit(1)
            
        print(f"Title: {title}")
        print(f"Tags: {tags}")
        
        yt = get_authenticated_service()
        update_video_complete(yt, v_id, title, desc, tags, thumb_file, s_time)
        
    except Exception as e:
        print(f"An error occurred: {e}")

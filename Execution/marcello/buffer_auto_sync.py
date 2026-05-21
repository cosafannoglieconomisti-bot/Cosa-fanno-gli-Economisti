import os
import json
import subprocess
import pickle
import re
import time
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta

# Configuration
BUFFER_ACCESS_TOKEN = [REDACTED]
FB_PROFILE_ID = "69baada37be9f8b1716baa0d"
HISTORY_FILE = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/marcello/facebook_history.json"
CLEANED_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
TOKEN_FILE = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/.tmp/tokens/token_youtube.pickle"

def get_youtube_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"posted_videos": []}

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4)

def normalize_title(text):
    """Normalizes all-caps titles to Title Case."""
    def tcase(match):
        t = match.group(0)
        return t.title() if (t.isupper() and len(t) > 10) else t
    return re.sub(r'\"([^\"]+)\"', tcase, text)

def schedule_via_curl(video_id, text, unix_ts):
    """Uses cURL as a robust fallback for Buffer API v1 500 errors."""
    cmd = [
        "curl", "-s", "-X", "POST",
        f"https://api.bufferapp.com/1/updates/create.json?access_token={BUFFER_ACCESS_TOKEN}",
        "-d", f"text={text}",
        "-d", f"profile_ids[]={FB_PROFILE_ID}",
        "-d", f"media[link]=https://www.youtube.com/watch?v={video_id}",
        "-d", f"media[picture]=https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        "-d", f"scheduled_at={unix_ts}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if "success\":true" in res.stdout:
        return True
    else:
        print(f"CURL ERROR Output: {res.stdout}")
        return False

def run_sync():
    youtube = get_youtube_service()
    history = load_history()
    
    uploads_id = youtube.channels().list(mine=True, part='contentDetails').execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    response = youtube.playlistItems().list(part="snippet", playlistId=uploads_id, maxResults=15).execute()
    
    # Base: March 31, 09:30 AM
    base_ts = int(time.mktime(time.strptime("2026-03-31 09:30:00", "%Y-%m-%d %H:%M:%S")))
    interval = 3 * 3600
    
    scheduled_count = 0
    for item in response.get('items', []):
        video_id = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        
        if "#shorts" in title.lower() or video_id in history['posted_videos']:
            continue
            
        matched_folder = None
        for folder in os.listdir(CLEANED_DIR):
            if folder.startswith('.') or not os.path.isdir(os.path.join(CLEANED_DIR, folder)): continue
            tclean = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
            words = [w for w in tclean.split() if len(w) > 3]
            if words and any(w in folder.lower() for w in words[:3]):
                matched_folder = folder
                break
        
        if matched_folder:
            metadata_path = os.path.join(CLEANED_DIR, matched_folder, "video_metadata.md")
            if os.path.exists(metadata_path):
                print(f"Syncing: {title}")
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    match = re.search(r'(Lo studio \"[^\n]+)', content, re.IGNORECASE)
                    if match:
                        sop_caption = normalize_title(match.group(1).split('\n\n')[0].replace('**', '').strip())
                    else:
                        sop_caption = [p.strip() for p in content.split("## Descrizione YouTube")[1].split("⏰ Fonte")[0].split('\n\n') if p.strip()][0]
                except:
                    sop_caption = f"Approfondimento: {title}"

                full_text = f"{sop_caption}\n\nVideo completo qui: https://www.youtube.com/watch?v={video_id}\n\n#CosaFannoGliEconomisti #Economia #Ricerca"
                
                ts = base_ts + (scheduled_count * interval)
                if schedule_via_curl(video_id, full_text, ts):
                    print(f"SUCCESS: Scheduled at {datetime.fromtimestamp(ts)}")
                    history['posted_videos'].append(video_id)
                    scheduled_count += 1
                else:
                    print("FAILED")
        
    save_history(history)
    print(f"Batch completed: {scheduled_count}")

if __name__ == "__main__":
    run_sync()

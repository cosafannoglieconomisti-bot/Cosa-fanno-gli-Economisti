import os
import pickle
import json
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

import re

def parse_duration(duration):
    # Regex for ISO 8601 duration: P[nD][T[nH][nM][nS]]
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return 0
    h, m, s = match.groups()
    return int(h or 0) * 3600 + int(m or 0) * 60 + int(s or 0)

def main():
    json_path = '/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/videos_list_updated.json'
    if not os.path.exists(json_path):
        print("Error: JSON file not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        videos = json.load(f)

    youtube = get_authenticated_service()
    
    shorts = []
    video_ids = [v['id'] for v in videos]
    
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        response = youtube.videos().list(
            part="snippet,contentDetails",
            id=",".join(batch_ids)
        ).execute()
        
        for item in response.get('items', []):
            duration_raw = item['contentDetails']['duration']
            duration_seconds = parse_duration(duration_raw)
            
            if duration_seconds < 60:
                shorts.append({
                    "id": item['id'],
                    "title": item['snippet']['title'],
                    "description": item['snippet']['description'],
                    "duration": duration_seconds
                })

    output_path = '/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/shorts_list.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(shorts, f, ensure_ascii=False, indent=4)
    print(f"Found {len(shorts)} shorts. Saved to {output_path}")

if __name__ == "__main__":
    main()

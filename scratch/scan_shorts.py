import os
import pickle
import re
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def is_generic_title(title):
    # Matches dates like "11 aprile 2026", "Apr 11, 2024", etc.
    # This is a bit simplified, but covers common cases mentioned in SOP.
    date_patterns = [
        r'\d{1,2}\s+[a-z]{3,}\s+\d{4}', # 11 aprile 2026
        r'[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}', # Apr 11, 2024
        r'\d{2}/\d{2}/\d{4}', # 11/04/2026
        r'^Short$',
        r'\.mp4$'
    ]
    for p in date_patterns:
        if re.search(p, title, re.IGNORECASE):
            return True
    return False

def list_bad_shorts():
    youtube = get_authenticated_service()
    
    request = youtube.search().list(
        part="snippet",
        channelId="UCTSmD2o3P7LMTTcMT3G7hPg", # COSA FANNO GLI ECONOMISTI
        maxResults=50,
        order="date",
        type="video"
    )
    response = request.execute()
    
    bad_shorts = []
    for item in response.get('items', []):
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        description = item['snippet']['description']
        
        # Check duration to see if it's a short (< 60s)
        video_res = youtube.videos().list(part="contentDetails", id=video_id).execute()
        duration = video_res['items'][0]['contentDetails']['duration']
        # YouTube duration is PT#M#S
        is_short = False
        if 'PT' in duration:
            if 'H' not in duration and 'M' not in duration: # < 1 min if no H and no M
                is_short = True
            elif 'M' in duration:
                minutes = int(re.search(r'(\d+)M', duration).group(1)) if 'M' in duration else 0
                if minutes == 0: is_short = True
        
        if is_short:
            if is_generic_title(title) or "Video completo qui:" not in description:
                bad_shorts.append({
                    "id": video_id,
                    "title": title,
                    "description": description
                })
    
    return bad_shorts

if __name__ == "__main__":
    shorts = list_bad_shorts()
    print(f"Trovati {len(shorts)} shorts da ottimizzare:")
    for s in shorts:
        print(f"- [{s['id']}] {s['title']}")

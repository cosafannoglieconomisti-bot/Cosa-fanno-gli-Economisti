import os
import pickle
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def find_parent_videos():
    youtube = get_authenticated_service()
    
    # List long-form videos
    request = youtube.search().list(
        part="snippet",
        channelId="UCTSmD2o3P7LMTTcMT3G7hPg",
        maxResults=50,
        order="date",
        type="video"
    )
    response = request.execute()
    
    videos = []
    for item in response.get('items', []):
        v_id = item['id']['videoId']
        title = item['snippet']['title']
        # Check duration
        video_res = youtube.videos().list(part="contentDetails", id=v_id).execute()
        duration = video_res['items'][0]['contentDetails']['duration']
        # YouTube duration is PT#M#S
        if 'M' in duration or 'H' in duration:
            videos.append({"id": v_id, "title": title})
    
    return videos

if __name__ == "__main__":
    vids = find_parent_videos()
    for v in vids:
        print(f"[{v['id']}] {v['title']}")

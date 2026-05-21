
import pickle
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def full_audit():
    youtube = get_authenticated_service()
    
    # 1. Get all videos from uploads playlist
    ch_res = youtube.channels().list(part="contentDetails", mine=True).execute()
    uploads_id = ch_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    videos = []
    next_page_token = None
    while True:
        res = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        videos.extend(res['items'])
        next_page_token = res.get('nextPageToken')
        if not next_page_token:
            break
            
    print(f"{'ID':<15} | {'Title':<40} | {'Duration':<10}")
    print("-" * 70)
    
    # Get durations in batch
    for i in range(0, len(videos), 50):
        ids = [v['contentDetails']['videoId'] for v in videos[i:i+50]]
        v_res = youtube.videos().list(part="contentDetails,snippet", id=",".join(ids)).execute()
        for v in v_res['items']:
            print(f"{v['id']:<15} | {v['snippet']['title'][:40]:<40} | {v['contentDetails']['duration']:<10}")
            print(f"DESC: {v['snippet']['description'][:80]}...")
            print("-" * 20)

if __name__ == '__main__':
    full_audit()

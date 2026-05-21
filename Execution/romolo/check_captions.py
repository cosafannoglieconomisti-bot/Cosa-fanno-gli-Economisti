import os
import pickle
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def get_transcript_status(video_id):
    youtube = get_authenticated_service()
    try:
        captions = youtube.captions().list(
            part="snippet",
            videoId=video_id
        ).execute()
        
        if captions.get('items'):
            for c in captions['items']:
                print(f"Found caption: {c['snippet']['language']} ({c['snippet']['trackKind']})")
        else:
            print("No captions found for this video.")
    except Exception as e:
        print(f"Error checking captions: {e}")

if __name__ == "__main__":
    video_id = "jxrA4RvsaPc"
    get_transcript_status(video_id)

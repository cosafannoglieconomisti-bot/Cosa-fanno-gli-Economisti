import os
import pickle
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def get_schedule():
    youtube = get_authenticated_service()
    video_id = 'TKw-6Jm7C9g'
    
    response = youtube.videos().list(
        part="status",
        id=video_id
    ).execute()
    
    if 'items' in response and response['items']:
        status = response['items'][0].get('status', {})
        publish_at = status.get('publishAt', 'Not scheduled or already public')
        privacy = status.get('privacyStatus')
        print(f"Video ID: {video_id}")
        print(f"Privacy Status: {privacy}")
        print(f"Scheduled for (PublishAt): {publish_at}")
    else:
        print(f"Video with ID {video_id} not found.")

if __name__ == "__main__":
    get_schedule()

import os
import pickle
import json
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def main():
    youtube = get_authenticated_service()
    # Test with the short ID we know has a related video
    video_id = "xE3a4gtq7ls"
    
    response = youtube.videos().list(
        part="snippet,contentDetails,status,statistics,player,topicDetails,recordingDetails,liveStreamingDetails,localizations",
        id=video_id
    ).execute()
    
    print(json.dumps(response, indent=4))

if __name__ == "__main__":
    main()

import os
import pickle
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def check_duration(video_id):
    youtube = get_authenticated_service()
    request = youtube.videos().list(part="contentDetails,snippet", id=video_id)
    response = request.execute()
    for item in response.get('items', []):
        print(f"ID: {item['id']} | Title: {item['snippet']['title']} | Duration: {item['contentDetails']['duration']}")

if __name__ == "__main__":
    check_duration("BFW6hmE5WiQ")

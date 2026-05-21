import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_service():
    with open('/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle', 'rb') as token:
        credentials = pickle.load(token)
    return build('youtube', 'v3', credentials=credentials)

def check_shorts():
    service = get_service()
    shorts_ids = ['DSucrUBXJws', 'TE2601I7Y1c']
    try:
        request = service.videos().list(
            part="snippet",
            id=",".join(shorts_ids)
        )
        response = request.execute()
        
        for item in response.get('items', []):
            print(f"ID: {item['id']}")
            print(f"Title: {item['snippet']['title']}")
            print(f"Description: {item['snippet']['description']}")
            print("-" * 20)
            
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")

if __name__ == "__main__":
    check_shorts()

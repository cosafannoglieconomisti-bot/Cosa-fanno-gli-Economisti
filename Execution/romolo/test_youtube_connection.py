import pickle
import os
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def test():
    creds = None
    token_file = 'Execution/credentials/token_youtube.pickle'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds:
        print("No token found.")
        return

    if creds and creds.expired and creds.refresh_token:
        print("Refreshing token...")
        creds.refresh(Request())
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    service = build('youtube', 'v3', credentials=creds)
    try:
        results = service.channels().list(mine=True, part='snippet').execute()
        print(f"Connected to channel: {results['items'][0]['snippet']['title']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()

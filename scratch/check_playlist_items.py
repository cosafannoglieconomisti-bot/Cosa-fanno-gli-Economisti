import os
import pickle
from googleapiclient.discovery import build

token_file = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token.pickle"
with open(token_file, 'rb') as token:
    creds = pickle.load(token)

youtube = build('youtube', 'v3', credentials=creds)

pl_id = "PLsnEaIfKp6RGjMnxvVNyZK5ys55Yr5J8v"
try:
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=pl_id,
        maxResults=50
    )
    response = request.execute()
    print(f"Items in {pl_id}: {len(response.get('items', []))}")
except Exception as e:
    print(f"Error: {e}")

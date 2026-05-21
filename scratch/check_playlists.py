import os
import pickle
from googleapiclient.discovery import build

token_file = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token.pickle"
with open(token_file, 'rb') as token:
    creds = pickle.load(token)

youtube = build('youtube', 'v3', credentials=creds)

request = youtube.playlists().list(
    part="snippet",
    mine=True,
    maxResults=50
)
response = request.execute()
for item in response.get("items", []):
    print(f"Title: {item['snippet']['title']}, ID: {item['id']}")

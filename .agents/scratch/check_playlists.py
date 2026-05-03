import os
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

TOKEN_PATH = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token.pickle"

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

def check_video_playlists(video_id):
    youtube = get_authenticated_service()
    
    # Get all playlists for the channel
    playlists = {}
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    response = request.execute()
    for item in response.get("items", []):
        playlists[item["id"]] = item["snippet"]["title"]
    
    # Check each playlist for the video
    found_in = []
    for pl_id, pl_title in playlists.items():
        req = youtube.playlistItems().list(part="snippet", playlistId=pl_id, videoId=video_id)
        res = req.execute()
        if res.get("items"):
            found_in.append(pl_title)
            
    return found_in

if __name__ == "__main__":
    vid = "YoEIAPvWrZI"
    found = check_video_playlists(vid)
    print(f"Video {vid} found in playlists: {found}")


import pickle
from googleapiclient.discovery import build

def check_quota():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    youtube = build('youtube', 'v3', credentials=creds)
    try:
        # Simple call to list one video to check quota
        youtube.videos().list(part="id", id="DSucrUBXJws").execute()
        print("Quota available.")
    except Exception as e:
        print(f"Quota issue: {e}")

if __name__ == "__main__":
    check_quota()

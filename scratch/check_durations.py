
import pickle
import re
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def parse_duration(duration_str):
    # PT#M#S
    match = re.search(r'PT(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match: return 0
    minutes = int(match.group(1)) if match.group(1) else 0
    seconds = int(match.group(2)) if match.group(2) else 0
    return minutes * 60 + seconds

def check_durations():
    youtube = get_authenticated_service()
    ids = ["RWOMLttjSGw", "TkBdxKizXBw", "U3GRvQR612Q"]
    v_res = youtube.videos().list(part="contentDetails,snippet", id=",".join(ids)).execute()
    for v in v_res['items']:
        dur = parse_duration(v['contentDetails']['duration'])
        print(f"ID: {v['id']} | Title: {v['snippet']['title']} | Duration: {dur}s")

if __name__ == '__main__':
    check_durations()

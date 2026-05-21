
import pickle
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def audit_shorts():
    youtube = get_authenticated_service()
    shorts_ids = [
        "DSucrUBXJws", "TE2601I7Y1c", "TkBdxKizXBw", "U3GRvQR612Q", "D-j41dR110M",
        "1qdybzlRfCc", "rcHDZvJ91Pg", "6VVXlgYa7jo", "Og-odPugBgQ", "PR3IQI-eybg",
        "-YELM0HZQ40", "_g_BKiot5_0", "_D02ygxnHGk", "16GHafTZ5-4", "M_4e4I_ql8U",
        "GdFZMvtHLbo", "-LJwjNCwqbc", "k4qDIQIPtBo", "pgAn6mnOoxA", "J3Vj4cAL4cE",
        "Hi5IYPlJmkY", "jxrA4RvsaPc", "SpgBjx6hiH4", "2soQGo7N-_k", "eO0DCsYr6PA",
        "RCcIxMaYmIw", "RCfHNwxZYv4", "O7SpDhbLKZo", "U_ZEqCF-wbw", "tGEsjsvVGiM"
    ]
    
    results = youtube.videos().list(
        part="snippet",
        id=",".join(shorts_ids)
    ).execute()
    
    for item in results.get('items', []):
        video_id = item['id']
        title = item['snippet']['title']
        description = item['snippet']['description']
        print(f"ID: {video_id}")
        print(f"TITLE: {title}")
        print(f"DESC: {description[:100]}...")
        print("-" * 20)

if __name__ == '__main__':
    audit_shorts()

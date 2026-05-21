import os
import pickle
import json
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def check_dates():
    youtube = get_authenticated_service()
    
    with open('/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/shorts_list.json', 'r') as f:
        shorts = json.load(f)
        
    ids = [s['id'] for s in shorts]
    
    results = []
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        response = youtube.videos().list(part="snippet", id=",".join(batch)).execute()
        for item in response.get('items', []):
            results.append({
                "id": item['id'],
                "title": item['snippet']['title'],
                "publishedAt": item['snippet']['publishedAt']
            })
            
    # Sort by publishedAt descending
    results.sort(key=lambda x: x['publishedAt'], reverse=True)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    check_dates()


import json
import os
import pickle
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def update_shorts():
    youtube = get_authenticated_service()
    
    shorts_list_path = '/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/shorts_list.json'
    if not os.path.exists(shorts_list_path):
        print("Error: shorts_list.json not found.")
        return
        
    with open(shorts_list_path, 'r') as f:
        shorts = json.load(f)
    
    success_count = 0
    fail_count = 0
    
    for i, short in enumerate(shorts):
        video_id = short['id']
        title = short['title']
        description = short['description']
        
        print(f"[{i+1}/{len(shorts)}] Updating {video_id}: {title}...")
        
        try:
            # First, get current snippet to avoid overwriting other fields like tags or category
            v_res = youtube.videos().list(part="snippet", id=video_id).execute()
            if not v_res['items']:
                print(f"Error: Video {video_id} not found.")
                fail_count += 1
                continue
                
            snippet = v_res['items'][0]['snippet']
            snippet['title'] = title
            snippet['description'] = description
            
            # Update
            youtube.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": snippet
                }
            ).execute()
            
            print(f"✅ Success!")
            success_count += 1
            time.sleep(0.5)
            
        except HttpError as e:
            if e.resp.status == 403:
                print("❌ Quota exceeded. Stopping.")
                break
            else:
                print(f"❌ Error updating {video_id}: {e}")
                fail_count += 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            fail_count += 1
            
    print(f"\nBatch completed. Success: {success_count}, Failed: {fail_count}")

if __name__ == '__main__':
    update_shorts()

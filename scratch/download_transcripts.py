import os
import pickle
import json
from googleapiclient.discovery import build
import sys

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def download_transcript(video_id):
    youtube = get_authenticated_service()
    try:
        captions = youtube.captions().list(part="snippet", videoId=video_id).execute()
        if not captions.get('items'):
            print(f"No captions found for {video_id}")
            return None
        
        # Try to find 'it' caption
        caption_id = None
        for item in captions['items']:
            if item['snippet']['language'] == 'it':
                caption_id = item['id']
                break
        
        if not caption_id:
            caption_id = captions['items'][0]['id']
            print(f"Using {captions['items'][0]['snippet']['language']} for {video_id}")
            
        request = youtube.captions().download(id=caption_id)
        content = request.execute()
        
        output_path = f'/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/transcript_{video_id}.vtt'
        with open(output_path, 'wb') as f:
            f.write(content)
        print(f"Downloaded transcript to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading transcript for {video_id}: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        download_transcript(sys.argv[1])
    else:
        # Default for the two suspected ones
        download_transcript("DSucrUBXJws")
        download_transcript("TE2601I7Y1c")

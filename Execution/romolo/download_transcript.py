import os
import pickle
import json
import sys
import argparse
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def download_caption(video_id, format='srt', output_path=None):
    youtube = get_authenticated_service()
    try:
        # 1. Get the list of captions
        captions = youtube.captions().list(
            part="snippet",
            videoId=video_id
        ).execute()
        
        caption_id = None
        # Prioritize manual Italian captions, fallback to ASR
        all_caps = captions.get('items', [])
        
        # Try manual IT first
        for item in all_caps:
            if item['snippet']['language'] == 'it' and item['snippet'].get('trackKind') != 'asr':
                caption_id = item['id']
                break
        
        # Fallback to IT asr if manual not found
        if not caption_id:
            for item in all_caps:
                if item['snippet']['language'] == 'it':
                    caption_id = item['id']
                    break
        
        if not caption_id:
            print(f"❌ No suitable Italian caption found for {video_id}.")
            return None
            
        print(f"📡 Downloading caption ID: {caption_id} ({format})")
        
        # 2. Download the literal text
        request = youtube.captions().download(
            id=caption_id,
            tfmt=format
        )
        content = request.execute()
        
        # content is bytes
        text = content.decode('utf-8')
        
        if not output_path:
            output_path = f'/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/transcript_{video_id}.{format}'
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✅ Transcript saved to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error downloading caption: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video_id", help="YouTube Video ID")
    parser.add_argument("--format", default="srt", help="Output format (srt or vtt)")
    parser.add_argument("--output", help="Optional output path")
    args = parser.parse_args()
    
    download_caption(args.video_id, args.format, args.output)

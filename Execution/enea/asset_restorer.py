import os
import json
import pickle
import requests
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CLEANED_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
TRACKING_FILE = os.path.join(CLEANED_DIR, "video_tracking.json")
TOKEN_PATH = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token.pickle"

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        else:
            print("Error: YouTube credentials not found or expired.")
            return None
    return build('youtube', 'v3', credentials=creds, static_discovery=False)

def download_image(url, output_path):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Error downloading image: {e}")
    return False

def restore_and_cleanup():
    youtube = get_authenticated_service()
    if not youtube:
        return

    if not os.path.exists(TRACKING_FILE):
        print("Error: video_tracking.json not found")
        return

    with open(TRACKING_FILE, "r", encoding="utf-8") as f:
        tracking = json.load(f)

    for folder, info in tracking.items():
        folder_path = os.path.join(CLEANED_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        video_id = info.get("youtube_id", "")
        if not video_id:
            print(f"⚠️ Missing YouTube ID for {folder}")
            continue

        print(f"🔍 Processing: {folder} (ID: {video_id})")
        
        # 1. Recupero Metadati e Cover da YouTube
        try:
            res = youtube.videos().list(id=video_id, part='snippet').execute()
            if res.get('items'):
                snippet = res['items'][0]['snippet']
                
                # Metadata
                md_path = os.path.join(folder_path, "video_metadata.md")
                if not os.path.exists(md_path):
                    description = snippet.get('description', '')
                    title = snippet.get('title', '')
                    with open(md_path, "w", encoding="utf-8") as f_md:
                        f_md.write(f"# {title}\n\n## Descrizione YouTube\n\n{description}\n")
                    print(f"  ✅ Metadata ripristinato.")

                # Cover
                cover_path = os.path.join(folder_path, "copertina.png")
                existing_covers = [f for f in os.listdir(folder_path) if f.lower() in ["copertina.png", "thumbnail.png", "cover.png"]]
                if not existing_covers:
                    thumbnails = snippet.get('thumbnails', {})
                    # Preferenza ordine qualità
                    thumb_url = thumbnails.get('maxres', {}).get('url') or \
                                thumbnails.get('high', {}).get('url') or \
                                thumbnails.get('default', {}).get('url')
                    if thumb_url and download_image(thumb_url, cover_path):
                        print(f"  ✅ Copertina scaricata da YouTube.")
            else:
                print(f"  ❌ Video non trovato su YouTube.")
        except Exception as e:
            print(f"  ❌ Errore API YouTube per {folder}: {e}")

        # 2. Cleanup file non necessari
        files = os.listdir(folder_path)
        for f in files:
            f_path = os.path.join(folder_path, f)
            # Regole di eliminazione: video, audio, sottotitoli, log, e file raw
            if f.endswith((".mp4", ".wav", ".srt", ".vtt", ".txt", ".json")) and f != "video_tracking.json":
                if "metadata" not in f.lower() and "tracking" not in f.lower():
                    try:
                        os.remove(f_path)
                        print(f"  🗑️ Eliminato: {f}")
                    except Exception as e:
                        print(f"  ⚠️ Impossibile eliminare {f}: {e}")
            elif "_raw.png" in f.lower() or "whisper" in f.lower():
                try:
                    os.remove(f_path)
                    print(f"  🗑️ Eliminato: {f}")
                except Exception as e:
                    print(f"  ⚠️ Impossibile eliminare {f}: {e}")

    print("\n✨ Fase 1 (YouTube + Cleanup) completata.")

if __name__ == "__main__":
    restore_and_cleanup()

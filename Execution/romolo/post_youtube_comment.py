import os
import sys
import json
from googleapiclient.discovery import build
from dotenv import load_dotenv

sys.path.append("/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo")
from romolo_manage_channel import get_authenticated_service, SCOPES

HISTORY_FILE = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/competitor_comment_history.json"

def record_comment_history(video_id):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            pass
    if video_id not in history:
        history.append(video_id)
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"⚠️ Errore salvataggio cronologia commenti: {e}")

def post_top_level_comment(video_id, text):
    youtube = get_authenticated_service('youtube', 'v3', SCOPES)
    try:
        youtube.commentThreads().insert(
            part='snippet',
            body={
                'snippet': {
                    'videoId': video_id,
                    'topLevelComment': {
                        'snippet': {
                            'textOriginal': text
                        }
                    }
                }
            }
        ).execute()
        print(f"✅ Commento pubblicato con successo sul video {video_id}")
        record_comment_history(video_id)
    except Exception as e:
        print(f"❌ Errore nella pubblicazione del commento: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python post_youtube_comment.py <video_id> <testo>")
        sys.exit(1)
    
    v_id = sys.argv[1]
    msg = sys.argv[2]
    post_top_level_comment(v_id, msg)

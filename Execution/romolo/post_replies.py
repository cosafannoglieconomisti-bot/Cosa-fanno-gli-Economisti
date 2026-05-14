
import os
from dotenv import load_dotenv
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.readonly'
]

def get_authenticated_service():
    creds = None
    romolo_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo"
    token_file = os.path.join(romolo_dir, ".tmp", "tokens", 'token_youtube.pickle')
    
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secrets_path = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/client_secrets.json"
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def find_comment_and_reply(youtube, author_name, reply_text, video_id=None):
    if video_id:
        results = youtube.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()
    else:
        # Search across recent videos if no video_id provided
        channels_response = youtube.channels().list(mine=True, part='id').execute()
        channel_id = channels_response['items'][0]['id']
        videos = youtube.search().list(part='id', channelId=channel_id, order='date', type='video', maxResults=5).execute()
        items = []
        for v in videos.get('items', []):
            vid = v['id'].get('videoId')
            if vid:
                res = youtube.commentThreads().list(part='snippet,replies', videoId=vid, maxResults=20).execute()
                items.extend(res.get('items', []))
        results = {'items': items}

    for item in results.get('items', []):
        top_comment = item['snippet']['topLevelComment']
        author = top_comment['snippet']['authorDisplayName']
        # print(f"DEBUG: Found author '{author}'")
        
        # Check top level comment
        if author.strip('@').lower() == author_name.strip('@').lower():
            print(f"Found comment by {author} (ID: {top_comment['id']})")
            reply_to(youtube, top_comment['id'], reply_text)
            return True
            
        # Check replies
        if 'replies' in item:
            for reply in item['replies']['comments']:
                r_author = reply['snippet']['authorDisplayName']
                # print(f"DEBUG: Found reply author '{r_author}'")
                if r_author.strip('@').lower() == author_name.strip('@').lower():
                    print(f"Found reply by {r_author} (ID: {reply['id']})")
                    reply_to(youtube, top_comment['id'], reply_text)
                    return True
    return False

def reply_to(youtube, parent_id, text):
    try:
        youtube.comments().insert(
            part='snippet',
            body={
                'snippet': {
                    'parentId': parent_id,
                    'textOriginal': text
                }
            }
        ).execute()
        print(f"Replied successfully to {parent_id}")
    except Exception as e:
        print(f"Error replying: {e}")

if __name__ == "__main__":
    youtube = get_authenticated_service()
    
    # Reply to LiaBarsou
    # lia_text = "Grazie del commento, Lia! Hai toccato un tasto molto sensibile e reale. La frustrazione per la mancanza di meritocrazia è un tema centrale nel dibattito economico attuale. Proprio per questo, stiamo preparando dei video basati su dati e ricerche recenti che approfondiscono esattamente questo aspetto (anche confrontando l'Italia con l'estero). Resta sintonizzata!"
    # print("Replying to LiaBarsou...")
    # find_comment_and_reply(youtube, "LiaBarsou", lia_text)
    
    # Reply to ZZapFerioli
    zzap_text = "Ottimo punto tecnico. In effetti la 'fuga' fiscale è spesso un'opzione accessibile solo a chi ha grandi capitali, mentre chi lavora sul territorio resta bloccato e subisce il prelievo, indipendentemente dalle proprie idee sulle tasse. È proprio questa asimmetria nella mobilità tra capitale e lavoro che crea le distorsioni più profonde nel sistema. Grazie per lo spunto."
    print("Replying to ZZapFerioli_f4ckthewoke...")
    find_comment_and_reply(youtube, "ZZapFerioli_f4ckthewoke", zzap_text, video_id="7cHt_oLI4_k")

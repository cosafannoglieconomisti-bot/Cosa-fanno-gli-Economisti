import os
import json
import pickle
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Root path for absolute references
ROOT_PATH = "/Users/marcolemoglie_1_2/Desktop/canale"
load_dotenv(os.path.join(ROOT_PATH, 'Execution/credentials/.env'))

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube'
]

PLAYLISTS_CONFIG_PATH = os.path.join(ROOT_PATH, "Execution/romolo/playlist_config.json")

def load_playlist_config():
    if os.path.exists(PLAYLISTS_CONFIG_PATH):
        with open(PLAYLISTS_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"playlists": {}}

CONFIG = load_playlist_config()
PLAYLISTS_MAP = {k: v["videos"] for k, v in CONFIG["playlists"].items() if k != "I Migliori Video di Cosa Fanno Gli Economisti"}
CATCHY_DESCRIPTIONS = {k: v["description"] for k, v in CONFIG["playlists"].items()}

def get_authenticated_service():
    creds = None
    # Prefer token_youtube.pickle in romolo .tmp folder if it exists
    token_file = os.path.join(ROOT_PATH, "Execution/romolo/.tmp/tokens/token_youtube.pickle")
    if not os.path.exists(token_file):
        token_file = os.path.join(ROOT_PATH, "Execution/credentials/token.pickle")
    
    print(f"Utilizzo file token: {token_file}")
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        else:
            client_secrets_path = os.path.join(ROOT_PATH, "Execution/credentials/client_secrets.json")
            if not os.path.exists(client_secrets_path):
                print(f"File client_secrets.json non trovato in {client_secrets_path}")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
            
    return build('youtube', 'v3', credentials=creds)

def load_video_tracking():
    tracking_path = os.path.join(ROOT_PATH, "Cleaned/video_tracking.json")
    if os.path.exists(tracking_path):
        with open(tracking_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_video_tracking(tracking):
    tracking_path = os.path.join(ROOT_PATH, "Cleaned/video_tracking.json")
    with open(tracking_path, 'w', encoding='utf-8') as f:
        json.dump(tracking, f, indent=4)
    print("video_tracking.json aggiornato con successo.")

def get_channel_playlists(youtube):
    playlists = {}
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response.get("items", []):
            playlists[item["snippet"]["title"]] = item["id"]
        request = youtube.playlists().list_next(request, response)
    return playlists

def create_playlist(youtube, title, description=""):
    print(f"Creazione playlist: {title}")
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": title,
            "description": description
          },
          "status": {
            "privacyStatus": "public"
          }
        }
    )
    response = request.execute()
    return response["id"]

def update_playlist_description(youtube, playlist_id, title, description):
    print(f"Aggiornamento descrizione playlist: {title}")
    youtube.playlists().update(
        part="snippet",
        body={
            "id": playlist_id,
            "snippet": {
                "title": title,
                "description": description
            }
        }
    ).execute()

def get_playlist_items(youtube, playlist_id):
    items = set()
    try:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        )
        while request:
            response = request.execute()
            for item in response.get("items", []):
                items.add(item["snippet"]["resourceId"]["videoId"])
            request = youtube.playlistItems().list_next(request, response)
    except Exception as e:
        print(f"⚠️ Avviso: Impossibile recuperare item della playlist {playlist_id}: {e}")
    return items

def get_video_titles(youtube, video_ids):
    titles = {}
    if not video_ids:
        return titles
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        response = youtube.videos().list(
            part="snippet",
            id=",".join(chunk)
        ).execute()
        for item in response.get("items", []):
            titles[item["id"]] = item["snippet"]["title"]
    return titles

def add_video_to_playlist(youtube, playlist_id, video_id):
    print(f"Aggiunta video {video_id} alla playlist {playlist_id}")
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
    except Exception as e:
        print(f"Errore nell'aggiunta del video {video_id}: {e}")

def get_top_videos(youtube, max_results=5):
    try:
        channels_response = youtube.channels().list(mine=True, part='contentDetails').execute()
        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        video_ids = []
        request = youtube.playlistItems().list(part='snippet', playlistId=uploads_playlist_id, maxResults=50)
        while request and len(video_ids) < 100:
            response = request.execute()
            for item in response.get('items', []):
                video_ids.append(item['snippet']['resourceId']['videoId'])
            request = youtube.playlistItems().list_next(request, response)
            
        if not video_ids:
            return []
            
        top_videos = []
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i+50]
            stats_response = youtube.videos().list(part='statistics', id=','.join(chunk)).execute()
            for item in stats_response.get('items', []):
                view_count = int(item['statistics'].get('viewCount', 0))
                top_videos.append((item['id'], view_count))
                
        top_videos.sort(key=lambda x: x[1], reverse=True)
        return [v[0] for v in top_videos[:max_results]]
    except Exception as e:
        print(f"⚠️ Errore nel recupero top video: {e}")
        return []

def main():
    youtube = get_authenticated_service()
    if not youtube:
        print("Errore di autenticazione.")
        return

    tracking = load_video_tracking()
    existing_playlists = get_channel_playlists(youtube)
    
    # 1. Crea e popola le 7 playlist tematiche
    for pl_title, video_keys in PLAYLISTS_MAP.items():
        vids_in_pl = []
        for key in video_keys:
            if key in tracking:
                vid_id = tracking[key].get("youtube_id")
                if vid_id and vid_id != "Da pubblicare" and vid_id != "":
                    vids_in_pl.append(vid_id)
                    # Aggiorna il tracking localmente
                    tracking[key]["playlist"] = pl_title
        
        if not vids_in_pl:
            print(f"Nessun video trovato per la playlist: {pl_title}")
            continue

        # Get real titles for the description
        titles_map = get_video_titles(youtube, vids_in_pl)
        
        # Construct description
        base_desc = CATCHY_DESCRIPTIONS.get(pl_title, "")
        video_list_str = "\n".join([f"- {titles_map[vid]}" for vid in vids_in_pl if vid in titles_map])
        full_description = f"{base_desc}\n\nIn questa playlist:\n{video_list_str}"
        
        if pl_title in existing_playlists:
            pl_id = existing_playlists[pl_title]
            print(f"Playlist trovata: {pl_title} ({pl_id})")
            try:
                update_playlist_description(youtube, pl_id, pl_title, full_description)
            except Exception as e:
                print(f"⚠️ Errore aggiornamento descrizione: {e}. Tento ricreazione...")
                pl_id = create_playlist(youtube, pl_title, full_description)
        else:
            pl_id = create_playlist(youtube, pl_title, full_description)
            existing_playlists[pl_title] = pl_id
            
        existing_items = get_playlist_items(youtube, pl_id)
        
        for vid in vids_in_pl:
            if vid not in existing_items:
                add_video_to_playlist(youtube, pl_id, vid)
            else:
                print(f"Video {vid} già presente in {pl_title}")

    # 2. Crea e popola la playlist "I Migliori Video"
    best_pl_title = "I Migliori Video di Cosa Fanno Gli Economisti"
    print("Recupero dei video più visti...")
    top_vids = get_top_videos(youtube, 5)
    best_titles_map = get_video_titles(youtube, top_vids)
    
    best_base_desc = CATCHY_DESCRIPTIONS.get(best_pl_title, "")
    best_video_list_str = "\n".join([f"- {best_titles_map[vid]}" for vid in top_vids if vid in best_titles_map])
    best_full_description = f"{best_base_desc}\n\nIn questa playlist:\n{best_video_list_str}"

    if best_pl_title in existing_playlists:
        best_pl_id = existing_playlists[best_pl_title]
        print(f"Playlist trovata: {best_pl_title} ({best_pl_id})")
        try:
            update_playlist_description(youtube, best_pl_id, best_pl_title, best_full_description)
        except Exception as e:
             print(f"⚠️ Errore aggiornamento descrizione top: {e}")
    else:
        best_pl_id = create_playlist(youtube, best_pl_title, best_full_description)
        
    best_existing_items = get_playlist_items(youtube, best_pl_id)
    
    for vid in top_vids:
        if vid not in best_existing_items:
            add_video_to_playlist(youtube, best_pl_id, vid)
        else:
            print(f"Top Video {vid} già presente in {best_pl_title}")

    # Salva il tracking aggiornato
    save_video_tracking(tracking)
    print("Creazione e popolamento playlist completato!")

if __name__ == "__main__":
    main()

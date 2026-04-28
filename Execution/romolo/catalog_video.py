import os
import sys
import json
import pickle
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google import genai

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

PLAYLISTS_CONFIG = load_playlist_config()
PLAYLISTS_TITLES = list(PLAYLISTS_CONFIG["playlists"].keys())

def get_authenticated_service():
    creds = None
    # Flexible token path
    token_file = os.path.join(ROOT_PATH, "Execution/romolo/.tmp/tokens/token_youtube.pickle")
    if not os.path.exists(token_file):
        token_file = os.path.join(ROOT_PATH, "Execution/credentials/token.pickle")
    
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
                print(f"File client_secrets.json non trovato.")
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
    print(f"Creazione nuova playlist: {title}")
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

def refresh_playlist_description(youtube, playlist_id, playlist_title):
    print(f"Aggiornamento descrizione per playlist: {playlist_title}")
    try:
        # 1. Recupera tutti i video nella playlist
        video_ids = []
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        )
        while request:
            response = request.execute()
            for item in response.get("items", []):
                video_ids.append(item["snippet"]["resourceId"]["videoId"])
            request = youtube.playlistItems().list_next(request, response)
            
        if not video_ids:
            return

        # 2. Recupera i titoli reali
        titles = {}
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i+50]
            v_resp = youtube.videos().list(part="snippet", id=",".join(chunk)).execute()
            for item in v_resp.get("items", []):
                titles[item["id"]] = item["snippet"]["title"]
        
        # 3. Costruisci descrizione
        base_desc = PLAYLISTS_CONFIG["playlists"].get(playlist_title, {}).get("description", "")
        if not base_desc:
            base_desc = f"Video relativi a {playlist_title} - Cosa fanno gli economisti"
            
        video_list_str = "\n".join([f"- {titles[vid]}" for vid in video_ids if vid in titles])
        full_description = f"{base_desc}\n\nIn questa playlist:\n{video_list_str}"
        
        # 4. Update
        youtube.playlists().update(
            part="snippet",
            body={
                "id": playlist_id,
                "snippet": {
                    "title": playlist_title,
                    "description": full_description
                }
            }
        ).execute()
        print("Descrizione playlist aggiornata con i titoli dei video.")
    except Exception as e:
        print(f"⚠️ Errore durante il refresh della descrizione: {e}")

def add_video_to_playlist(youtube, playlist_id, video_id):
    try:
        # Controlla se è già presente
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            videoId=video_id
        )
        response = request.execute()
        if response.get("items"):
            print(f"Video {video_id} già presente nella playlist.")
            return True

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
        print(f"Video {video_id} aggiunto con successo alla playlist {playlist_id}.")
        return True
    except Exception as e:
        print(f"Errore nell'aggiunta del video {video_id}: {e}")
        return False

def categorize_video_with_gemini(video_title, video_description=""):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY non trovata.")
        return PLAYLISTS_TITLES[0] # Fallback
        
    client = genai.Client(api_key=api_key)
    playlists_str = "\n".join([f"- {p}" for p in PLAYLISTS_TITLES])
    
    prompt = f"""
Sei un assistente editoriale per il canale YouTube "Cosa fanno gli economisti".
Il tuo compito è categorizzare un nuovo video in una delle playlist tematiche esistenti.

Titolo del video: "{video_title}"
Descrizione/Contenuto: "{video_description}"

Le playlist predefinite sono:
{playlists_str}

Rispondi con il nome della playlist più adatta. 
IMPORTANTE: Se nessuna delle playlist esistenti è adatta all'argomento (es. è un tema totalmente nuovo come "Intelligenza Artificiale" o "Economia dell'Ambiente"), puoi proporre un NUOVO nome per una playlist (max 4-5 parole, stile accademico ma divulgativo).

Rispondi SOLO ed ESCLUSIVAMENTE con il nome della playlist, senza virgolette e senza testo aggiuntivo.
"""
    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        chosen = response.text.strip()
        return chosen
    except Exception as e:
        print(f"Errore Gemini: {e}")
        return PLAYLISTS_TITLES[1] # fallback

def main():
    if len(sys.argv) < 2:
        print("Uso: python catalog_video.py <Nome_Video_o_Youtube_ID>")
        sys.exit(1)
        
    target = sys.argv[1]
    
    youtube = get_authenticated_service()
    if not youtube:
        print("Errore auth YouTube.")
        sys.exit(1)
        
    tracking = load_video_tracking()
    
    # Trova il video nel tracking
    video_key = None
    youtube_id = None
    
    # Prova a cercare prima per ID
    for k, v in tracking.items():
        if v.get("youtube_id") == target:
            video_key = k
            youtube_id = target
            break
            
    # Se non trovato per ID, prova per chiave
    if not video_key and target in tracking:
        video_key = target
        youtube_id = tracking[target].get("youtube_id")
        
    if not youtube_id:
        print(f"Errore: Impossibile trovare lo youtube_id per '{target}' in video_tracking.json.")
        if len(target) == 11:
            youtube_id = target
            video_key = "Ignoto_" + target
        else:
            sys.exit(1)
            
    print(f"Video identificato: {video_key} (ID: {youtube_id})")
    
    # Recupera metadati per dare a Gemini info migliori
    video_title = video_key.replace("_", " ")
    video_desc = ""
    metadata_path = os.path.join(ROOT_PATH, f"Cleaned/{video_key}/video_metadata.md")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            video_desc = f.read()[:500]
            
    # Categorizza
    chosen_playlist = categorize_video_with_gemini(video_title, video_desc)
    print(f"Playlist scelta: {chosen_playlist}")
    
    # Trova l'ID della playlist su YouTube
    existing_playlists = get_channel_playlists(youtube)
    playlist_id = None
    
    # Cerca corrispondenza esatta (case insensitive)
    for title, pl_id in existing_playlists.items():
        if title.lower() == chosen_playlist.lower():
            playlist_id = pl_id
            chosen_playlist = title # Usa il titolo esatto esistente
            break
            
    if not playlist_id:
        print(f"Playlist '{chosen_playlist}' non trovata. Creazione in corso...")
        playlist_id = create_playlist(youtube, chosen_playlist, f"Video relativi a {chosen_playlist} - Cosa fanno gli economisti")
        
    # Aggiungi
    success = add_video_to_playlist(youtube, playlist_id, youtube_id)
    if success:
        # Refresh description with titles
        refresh_playlist_description(youtube, playlist_id, chosen_playlist)
        
        if video_key in tracking:
            tracking[video_key]["playlist"] = chosen_playlist
            save_video_tracking(tracking)
            print("Tracking aggiornato.")

if __name__ == "__main__":
    main()

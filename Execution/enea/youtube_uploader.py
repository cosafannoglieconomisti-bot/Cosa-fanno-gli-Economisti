import os
import pickle
import sys
import argparse
import datetime
import subprocess
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CREDENTIALS_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials"
TOKEN_PATH = os.path.join(CREDENTIALS_DIR, "token.pickle")
PYTHON_BIN = "/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3"
LOCALIZER_SCRIPT = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/update_video_localization.py"

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(TOKEN_PATH, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                raise Exception(f"Errore refresh token: {e}")
        else:
            raise Exception("Credenziali YouTube mancanti o scadute. Riesegui l'autenticazione manualmente.")
    
    return build('youtube', 'v3', credentials=creds, static_discovery=False)

def run_captions_upload(video_id, video_path):
    """Esegue automaticamente il caricamento dei sottotitoli se presente la cartella international/"""
    project_root = os.path.dirname(video_path)
    intl_path = os.path.join(project_root, "international")
    
    if not os.path.exists(intl_path):
        print(f"ℹ️ Nessuna cartella international/ trovata in {project_root}. Salto upload sottotitoli.")
        return

    print(f"🚀 Avvio caricamento sottotitoli mandatorio per {video_id}...")
    
    # Fix temporaneo: assicura che subtitles_it.srt sia visibile nella root per lo script localizer
    it_srt_root = os.path.join(project_root, "subtitles_it.srt")
    it_srt_intl = os.path.join(intl_path, "subtitles_it.srt")
    
    symlink_created = False
    if not os.path.exists(it_srt_root) and os.path.exists(it_srt_intl):
        print("🔗 Creazione symlink temporaneo per subtitles_it.srt")
        os.symlink(it_srt_intl, it_srt_root)
        symlink_created = True
        
    try:
        cmd = [PYTHON_BIN, LOCALIZER_SCRIPT, "--video_id", video_id, "--intl_path", intl_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sottotitoli e Localizzazioni caricati con successo per {video_id}")
            print(result.stdout)
        else:
            print(f"⚠️ Errore durante il caricamento sottotitoli: {result.stderr}")
    except Exception as e:
        print(f"❌ Errore critico nel processo sottotitoli: {e}")
    finally:
        if symlink_created and os.path.islink(it_srt_root):
            os.unlink(it_srt_root)


def parse_metadata(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    description = ""
    tags = []
    
    # Parsing semplificato per il nuovo formato video_metadata.md
    if "## Descrizione YouTube" in content:
        description = content.split("## Descrizione YouTube")[1].split("##")[0].strip()
    
    if "## Tag" in content:
        tag_line = content.split("## Tag")[1].split("##")[0].strip()
        tags = [t.strip().replace('#', '') for t in tag_line.split(',') if t.strip()]
                
    return description, tags

def initialize_upload(youtube, file_path, title, description, tags, privacy_status="private", publish_at=None):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '27' # Education
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }
    
    if publish_at:
        body['status']['publishAt'] = publish_at
        body['status']['privacyStatus'] = 'private' # Obbligatorio per scheduling

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    
    print(f"Uploading {file_path} to YouTube...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
            
    video_id = response['id']
    print(f"Upload Complete! Video ID: {video_id}")
    return video_id

def set_thumbnail(youtube, video_id, thumb_path):
    if not os.path.exists(thumb_path):
        print(f"⚠️ Thumbnail non trovato in {thumb_path}. Cerco alternative...")
        tdir = os.path.dirname(thumb_path)
        for alt in ["thumbnail.png", "cover.png", "copertina.png", "thumbnail.jpg"]:
            alt_p = os.path.join(tdir, alt)
            if os.path.exists(alt_p):
                thumb_path = alt_p
                print(f"✅ Trovata alternativa: {thumb_path}")
                break
        else:
            print("❌ Nessuna copertina trovata in tutta la cartella.")
            return
    
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumb_path)
    ).execute()
    print(f"✅ Thumbnail caricato: {thumb_path}")

def get_published_titles(youtube):
    try:
        channels_res = youtube.channels().list(mine=True, part='contentDetails').execute()
        uploads_playlist_id = channels_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        titles = []
        playlist_res = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet',
            maxResults=50
        ).execute()
        
        for item in playlist_res['items']:
            titles.append(item['snippet']['title'])
        return titles
    except Exception as e:
        print(f"⚠️ Errore nel recupero titoli pubblicati: {e}")
        return []

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="Percorso del file video")
    parser.add_argument("title", help="Titolo del video")
    parser.add_argument("metadata", help="Percorso del file .md con la descrizione")
    parser.add_argument("--thumbnail", help="Percorso della copertina .png")
    parser.add_argument("--schedule", help="Data/Ora pubblicazione ISO 8601 (es. 2026-03-27T08:00:00+01:00)")
    
    args = parser.parse_args()
    
    try:
        desc, tags = parse_metadata(args.metadata)
        youtube = get_authenticated_service()
        
        video_id = initialize_upload(youtube, args.video, args.title, desc, tags, publish_at=args.schedule)
        
        if args.thumbnail:
            set_thumbnail(youtube, video_id, args.thumbnail)
            
        # Step MANDATORIO: Caricamento Sottotitoli
        run_captions_upload(video_id, args.video)
            
        # Step: Aggiornamento Tracking e Catalogazione Automatica Playlist
        folder_name = os.path.basename(os.path.dirname(args.video))
        if folder_name:
            print(f"Aggiornamento tracking per {folder_name} con youtube_id: {video_id}")
            subprocess.run([
                PYTHON_BIN, 
                "/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/tracking_manager.py", 
                folder_name, 
                "youtube_id", 
                video_id
            ])
            print("Avvio catalogazione automatica playlist...")
            subprocess.run([
                PYTHON_BIN,
                "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/catalog_video.py",
                folder_name
            ])
            
    except Exception as e:
        print(f"❌ Fallimento critico: {e}")
        sys.exit(1)

import os
import pickle
import sys
import argparse
import glob
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configurazione Percorsi
CREDENTIALS_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials"
TOKEN_PATH = os.path.join(CREDENTIALS_DIR, "token.pickle")

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
            raise Exception("Credenziali YouTube non valide. Effettua l'autenticazione manuale.")
            
    return build('youtube', 'v3', credentials=creds, static_discovery=False)

def parse_intl_metadata(md_path):
    """Estrae Titolo e Descrizione in modo robusto."""
    if not os.path.exists(md_path):
        return None, None
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    title = ""
    description = ""
    
    # Estrazione Titolo (cerca dopo il primo trattino nella prima riga)
    first_line = content.split('\n')[0]
    if '-' in first_line:
        raw_title = first_line.split('-', 1)[1].strip()
        # Rimuove (EN), (ES), ecc.
        for suffix in ["(EN)", "(ES)", "(FR)", "(DE)", "(IT)"]:
            raw_title = raw_title.replace(suffix, "")
        title = raw_title.strip()
    
    # Estrazione Descrizione (tutto ciò che sta tra ## Descri... o ## Beschr... e la sezione successiva ##)
    if "##" in content:
        parts = content.split("##")
        for part in parts:
            part_lower = part.lower()
            # Gestisce Description, Descripción (descri) e Beschreibung (beschr)
            if "descri" in part_lower or "beschr" in part_lower:
                # Prende le righe dopo la prima (l'intestazione)
                lines = part.strip().split('\n')[1:]
                description = "\n".join(lines).strip()
                break
                
    return title, description

def parse_it_metadata(md_path):
    """Estrae Titolo e Descrizione dal formato video_metadata.md (Italiano)."""
    if not os.path.exists(md_path):
        return None, None
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    title = ""
    # Estrae titolo dal primo h1 (# Metadati Video - Titolo)
    first_line = content.split('\n')[0]
    if '-' in first_line:
        title = first_line.split('-', 1)[1].strip()
        
    description = ""
    if "## Descrizione YouTube" in content:
        # Prende tutto tra ## Descrizione YouTube e la sezione successiva ##
        description = content.split("## Descrizione YouTube")[1].split("##")[0].strip()
        
    return title, description

def update_video_localizations(youtube, video_id, intl_root):
    """Aggiorna i metadati localizzati del video."""
    video_response = youtube.videos().list(
        part="snippet,localizations",
        id=video_id
    ).execute()
    
    if not video_response['items']:
        print(f"❌ Video {video_id} non trovato.")
        return
        
    video_item = video_response['items'][0]
    snippet = video_item['snippet']
    localizations = video_item.get('localizations', {})
    
    # 1. Aggiornamento Metadati Italiani (Snippet Principale)
    # Rimuoviamo il trailing slash per calcolare correttamente la root del progetto
    project_root = os.path.dirname(intl_root.rstrip('/'))
    main_md = os.path.join(project_root, "video_metadata.md")
    it_title, it_desc = parse_it_metadata(main_md)
    if it_title and it_desc:
        snippet['title'] = it_title
        snippet['description'] = it_desc
        print(f"✅ Metadati IT (Snippet) preparati: {it_title[:30]}...")
    
    # 2. Aggiornamento Metadati Internazionali
    languages = ['en', 'es', 'fr', 'de']
    for lang in languages:
        md_file = os.path.join(intl_root, lang, f"metadata_{lang}.md")
        title, desc = parse_intl_metadata(md_file)
        
        if title and desc:
            localizations[lang] = {'title': title, 'description': desc}
            print(f"✅ Metadati {lang} preparati: {title[:30]}...")
        else:
            print(f"❌ ERRORE: Metadati {lang} mandatori mancanti o non validi in {md_file}")
            return False

    snippet['defaultLanguage'] = 'it'
    body = {'id': video_id, 'snippet': snippet, 'localizations': localizations}
    
    try:
        youtube.videos().update(part="snippet,localizations", body=body).execute()
        print(f"🚀 Localizzazioni e Snippet aggiornati per {video_id}!")
        return True
    except Exception as e:
        print(f"❌ Errore aggiornamento localizzazioni: {e}")
        return False

def upload_captions(youtube, video_id, intl_root):
    """Carica o aggiorna i sottotitoli evitando conflitti 409."""
    # Recupera tracce esistenti
    current_caps = youtube.captions().list(part="snippet", videoId=video_id).execute().get('items', [])
    existing_langs = {item['snippet']['language']: item['id'] for item in current_caps if item['snippet'].get('trackKind') != 'asr'}

    # Aggiunto 'it' per caricare anche i sottotitoli italiani originali
    languages = ['it', 'en', 'es', 'fr', 'de']
    names = {
        'it': 'Italiano (Originale)',
        'en': 'English (Official)', 
        'es': 'Español (Oficial)',
        'fr': 'Français (Officiel)', 
        'de': 'Deutsch (Offiziell)'
    }
    
    # Rimuoviamo il trailing slash per calcolare correttamente la root del progetto
    project_root = os.path.dirname(intl_root.rstrip('/'))
    
    for lang in languages:
        if lang == 'it':
            # Cerca il file subtitles_it.srt nella root del progetto o quello generato da Whisper
            srt_file = os.path.join(project_root, "subtitles_it.srt")
            if not os.path.exists(srt_file):
                # Fallback al nome file lungo se non rinominato
                possible_its = glob.glob(os.path.join(project_root, "*cleaned.it.srt"))
                if possible_its: srt_file = possible_its[0]
                else: 
                    print(f"⚠️ Sottotitoli IT non trovati, salto.")
                    continue
        else:
            srt_file = os.path.join(intl_root, lang, f"subtitles_{lang}.srt")
            
        if not os.path.exists(srt_file):
            if lang in ['en', 'es', 'fr', 'de']:
                print(f"❌ ERRORE: Sottotitoli mandatori {lang} mancanti in {srt_file}")
                return False
            continue
            
        media = MediaFileUpload(srt_file, mimetype='application/x-subrip')
        body = {'snippet': {'videoId': video_id, 'language': lang, 'name': names[lang], 'isDraft': False}}
        
        try:
            if lang in existing_langs:
                print(f"🔄 Aggiornamento sottotitoli {lang} (ID: {existing_langs[lang]})...")
                youtube.captions().update(part="snippet", body={'id': existing_langs[lang], 'snippet': body['snippet']}, media_body=media).execute()
            else:
                print(f"⏳ Caricamento nuovi sottotitoli {lang}...")
                youtube.captions().insert(part="snippet", body=body, media_body=media).execute()
            print(f"✅ Sottotitoli {lang} OK.")
        except Exception as e:
            print(f"❌ Errore {lang}: {e}")
            return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_id", required=True)
    parser.add_argument("--intl_path", required=True)
    args = parser.parse_args()
    
    service = get_authenticated_service()
    s1 = update_video_localizations(service, args.video_id, args.intl_path)
    s2 = upload_captions(service, args.video_id, args.intl_path)
    
    if not s1 or not s2:
        print("❌ ERRORE: Uno o più passaggi di localizzazione sono falliti.")
        sys.exit(1)
    
    print("✅ Localizzazione completata con successo.")
    sys.exit(0)

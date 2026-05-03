import os
from dotenv import load_dotenv
import pickle
from google import genai

load_dotenv()
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes necessari per YouTube Data API e YouTube Analytics API
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/youtube.readonly'
]

def get_authenticated_service(service_name, version, scopes):
    creds = None
    romolo_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo"
    token_folder = os.path.join(romolo_dir, ".tmp", "tokens")
    os.makedirs(token_folder, exist_ok=True)
    token_file = os.path.join(token_folder, f'token_{service_name}.pickle')
    
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
    return build(service_name, version, credentials=creds)

def get_analytics(youtube_analytics):
    # Dati degli ultimi 30 giorni
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    result = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,estimatedMinutesWatched,averageViewDuration,subscribersGained',
        dimensions='day'
    ).execute()
    
    return result

def get_channel_id(youtube):
    channels_response = youtube.channels().list(mine=True, part='id').execute()
    return channels_response['items'][0]['id']

def get_recent_comments(youtube, channel_id):
    # Prova diversi parametri per ottenere i commenti
    for param in ['allThreadsAtChannelId', 'channelId']:
        try:
            print(f"DEBUG: Provando {param}...")
            kwargs = {
                'part': 'snippet,replies',
                'maxResults': 20
            }
            # Se allThreadsAtChannelId fallisce con TypeError, lo saltiamo
            if param == 'allThreadsAtChannelId':
                try:
                    kwargs[param] = channel_id
                    results = youtube.commentThreads().list(**kwargs).execute()
                    return results.get('items', [])
                except TypeError:
                    continue
            else:
                kwargs[param] = channel_id
                results = youtube.commentThreads().list(**kwargs).execute()
                return results.get('items', [])
        except Exception as e:
            print(f"DEBUG: Fallito con {param}: {e}")
    
    # Fallback: prendiamo gli ultimi 5 video e i loro commenti
    all_comments = []
    try:
        print("DEBUG: Provo recupero commenti per video recenti...")
        videos = youtube.search().list(part='id', channelId=channel_id, order='date', type='video', maxResults=5).execute()
        for v in videos.get('items', []):
            v_id = v['id'].get('videoId')
            if not v_id: continue
            try:
                res = youtube.commentThreads().list(part='snippet,replies', videoId=v_id, maxResults=5).execute()
                all_comments.extend(res.get('items', []))
            except:
                continue
        return all_comments
    except Exception as e:
        print(f"DEBUG: Fallito recupero commenti per video: {e}")
    
    return []

def reply_to_comment(youtube, parent_id, text):
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
        print(f"Replied to comment {parent_id}")
    except Exception as e:
        print(f"Errore nella risposta: {e}")

def generate_report(analytics_data, comments, ai_tips, total_subs):
    # Salva nella cartella Romolo con data (.tmp)
    romolo_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo"
    report_folder = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/analytics_reports"
    os.makedirs(report_folder, exist_ok=True)
    filename = f"analytics_report_{datetime.now().strftime('%d_%m_%Y')}.txt"
    report_path = os.path.join(report_folder, filename)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"--- CANALE: COSA FANNO GLI ECONOMISTI - REPORT ROMOLO {datetime.now().strftime('%d/%m/%Y %H:%M')} ---\n\n")
        
        f.write("== ANALYTICS (Ultimi 30 giorni) ==\n")
        f.write(f"- Iscritti Totali: {total_subs}\n")
        if 'rows' in analytics_data:
            rows = analytics_data['rows']
            views = sum(r[1] for r in rows)
            minutes = sum(r[2] for r in rows)
            subs_gained = sum(r[4] for r in rows)
            f.write(f"- Views Totali: {views}\n")
            f.write(f"- Tempo di visione (min): {minutes}\n")
            f.write(f"- Nuovi Iscritti: {subs_gained}\n")
            if total_subs > subs_gained:
                starting_subs = total_subs - subs_gained
                growth_rate = (subs_gained / starting_subs) * 100
                f.write(f"- Tasso di Crescita: +{growth_rate:.1f}%\n")
        else:
            f.write("[!] Dati Analytics non disponibili.\n")
            f.write("    >>> NOTA: Devi abilitare la 'YouTube Analytics API' nel Google Cloud Console.\n")
        
        f.write("\n== COMMENTI RECENTI ==\n")
        if not comments:
            f.write("- Nessun nuovo commento trovato.\n")
        for item in comments:
            snippet = item['snippet']['topLevelComment']['snippet']
            author = snippet['authorDisplayName']
            text = snippet['textDisplay']
            f.write(f"- {author}: \"{text}\"\n")
            
        f.write("\n== CONSIGLI STRATEGICI DI CRESCITA (AI SMM Expert) ==\n")
        f.write(ai_tips + "\n")

if __name__ == "__main__":
    youtube = get_authenticated_service('youtube', 'v3', SCOPES)
    try:
        youtube_analytics = get_authenticated_service('youtubeAnalytics', 'v2', SCOPES)
        analytics_data = get_analytics(youtube_analytics)
    except Exception as e:
        print(f"Errore Analytics: {e}")
        analytics_data = {}

    channel_id = get_channel_id(youtube)
    channel_stats = youtube.channels().list(mine=True, part='statistics').execute()
    total_subs = int(channel_stats['items'][0]['statistics']['subscriberCount'])
    comments = get_recent_comments(youtube, channel_id)
    
    # Generazione Consigli con AI
    ai_tips = "Nessun consiglio generato per assenza di API Key."
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""Sei un Social Media Manager con 10 anni di esperienza, specializzato in YouTube Divulgazione.
Dati del canale:
- Iscritti totali: {total_subs}

Dati degli ultimi 30 giorni (JSON):
{json.dumps(analytics_data, indent=2, default=str)}

Commenti recenti (JSON):
{json.dumps(comments, indent=2, default=str)}

Fornisci 3 consigli strategici molto dettagliati, critici e AZIONABILI (Actionable) per far crescere il canale 'Cosa fanno gli economisti'.
Parla del tasso di interazione, degli argomenti da cavalcare e di strategie di SEO/Copertine.
"""
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )
            ai_tips = response.text
        except Exception as e:
            ai_tips = f"Errore generazione consigli: {e}"

    generate_report(analytics_data, comments, ai_tips, total_subs)
    
    print("Gestione canale completata da Romolo.")

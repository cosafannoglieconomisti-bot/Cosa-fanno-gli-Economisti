from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import json
import os
import pickle
from datetime import datetime, timedelta

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def get_authenticated_service(service_name, version, scopes):
    creds = None
    romolo_dir = str(REPO_ROOT / 'Execution' / 'romolo')
    token_folder = os.path.join(romolo_dir, ".tmp", "tokens")
    os.makedirs(token_folder, exist_ok=True)
    token_file = os.path.join(token_folder, f"token_{service_name}.pickle")

    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secrets_path = str(REPO_ROOT / 'Execution' / 'credentials' / 'client_secrets.json')
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)
    return build(service_name, version, credentials=creds)


def get_analytics(youtube_analytics):
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    return youtube_analytics.reports().query(
        ids="channel==MINE",
        startDate=start_date,
        endDate=end_date,
        metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained",
        dimensions="day",
    ).execute()


def get_channel_id(youtube):
    channels_response = youtube.channels().list(mine=True, part="id").execute()
    return channels_response["items"][0]["id"]


def get_recent_comments(youtube, channel_id):
    all_comments = []
    try:
        videos = youtube.search().list(part="id", channelId=channel_id, order="date", type="video", maxResults=5).execute()
        for video in videos.get("items", []):
            video_id = video["id"].get("videoId")
            if not video_id:
                continue
            try:
                result = youtube.commentThreads().list(part="snippet,replies", videoId=video_id, maxResults=5).execute()
                all_comments.extend(result.get("items", []))
            except Exception:
                continue
    except Exception as exc:
        print(f"DEBUG: Fallito recupero commenti per video: {exc}")
    return all_comments


def collect_comment_keywords(comments):
    tokens = {}
    for item in comments:
        text = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")
        for token in text.lower().split():
            token = "".join(ch for ch in token if ch.isalnum())
            if len(token) < 5:
                continue
            tokens[token] = tokens.get(token, 0) + 1
    return [token for token, _ in sorted(tokens.items(), key=lambda item: (-item[1], item[0]))[:5]]


def build_actionable_tips(analytics_data, comments, total_subs):
    tips = []
    rows = analytics_data.get("rows", [])
    if rows:
        views = sum(row[1] for row in rows)
        minutes = sum(row[2] for row in rows)
        avg_minutes = round(minutes / max(views, 1), 2)
        tips.append(f"Retention: la media minuti per view e' {avg_minutes}; verifica i primi 30 secondi dei video con calo forte.")
    keywords = collect_comment_keywords(comments)
    if keywords:
        tips.append(f"Commenti: tornano spesso {', '.join(keywords[:3])}; usa questi temi per titoli, short e community post.")
    tips.append(f"Crescita: con {total_subs} iscritti, concentra il calendario su serie coerenti e playlist tematiche aggiornate.")
    return "\n".join(f"- {tip}" for tip in tips)


def generate_report(analytics_data, comments, ai_tips, total_subs):
    report_folder = str(REPO_ROOT / 'Temp' / 'romolo' / 'analytics_reports')
    os.makedirs(report_folder, exist_ok=True)
    filename = f"analytics_report_{datetime.now().strftime('%d_%m_%Y')}.txt"
    report_path = os.path.join(report_folder, filename)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(f"--- CANALE: COSA FANNO GLI ECONOMISTI - REPORT ROMOLO {datetime.now().strftime('%d/%m/%Y %H:%M')} ---\n\n")
        handle.write("== ANALYTICS (Ultimi 30 giorni) ==\n")
        handle.write(f"- Iscritti Totali: {total_subs}\n")
        if "rows" in analytics_data:
            rows = analytics_data["rows"]
            views = sum(row[1] for row in rows)
            minutes = sum(row[2] for row in rows)
            subs_gained = sum(row[4] for row in rows)
            handle.write(f"- Views Totali: {views}\n")
            handle.write(f"- Tempo di visione (min): {minutes}\n")
            handle.write(f"- Nuovi Iscritti: {subs_gained}\n")
        else:
            handle.write("[!] Dati Analytics non disponibili.\n")

        handle.write("\n== COMMENTI RECENTI ==\n")
        if not comments:
            handle.write("- Nessun nuovo commento trovato.\n")
        for item in comments:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            handle.write(f"- {snippet['authorDisplayName']}: \"{snippet['textDisplay']}\"\n")

        handle.write("\n== CONSIGLI STRATEGICI DI CRESCITA ==\n")
        handle.write(ai_tips + "\n")


if __name__ == "__main__":
    youtube = get_authenticated_service("youtube", "v3", SCOPES)
    try:
        youtube_analytics = get_authenticated_service("youtubeAnalytics", "v2", SCOPES)
        analytics_data = get_analytics(youtube_analytics)
    except Exception as exc:
        print(f"Errore Analytics: {exc}")
        analytics_data = {}

    channel_id = get_channel_id(youtube)
    channel_stats = youtube.channels().list(mine=True, part="statistics").execute()
    total_subs = int(channel_stats["items"][0]["statistics"]["subscriberCount"])
    comments = get_recent_comments(youtube, channel_id)
    ai_tips = build_actionable_tips(analytics_data, comments, total_subs)
    generate_report(analytics_data, comments, ai_tips, total_subs)
    print("Gestione canale completata da Romolo.")

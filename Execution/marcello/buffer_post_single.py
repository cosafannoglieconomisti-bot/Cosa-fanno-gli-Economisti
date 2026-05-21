"""
buffer_post_single.py — Posta UN singolo video su Buffer/Facebook.

Formato didascalia (SOP Marcello — CONTRATTO IMMUTABILE):
  [Titolo del VIDEO YouTube — esattamente come su YouTube]
  [Autori], [Journal] ([Anno])

  [Prima parte descrizione YouTube — frase "Lo studio \"TITOLO PAPER ACCADEMICO\"..."]

  ▶ https://www.youtube.com/watch?v=[VIDEO_ID]

  #tag1 #tag2 #tag3

NOTA: la riga 1 è SEMPRE il titolo del VIDEO, non il titolo accademico del paper.
Il titolo del paper accademico appare solo all'interno della descrizione ("Lo studio...").
Rego SOP: il campo "Lo studio\"...\"" nel video_metadata.md DEVE contenere
il titolo ACCADEMICO REALE del paper, non il titolo del video.

USAGE:
  python3 buffer_post_single.py                  # usa il primo video non ancora postato
  python3 buffer_post_single.py --dry-run        # stampa senza inviare
  python3 buffer_post_single.py --video-id XYZ   # forza un video specifico
  python3 buffer_post_single.py --hour 10        # programma alle 10:00 (default 09:00)
"""

import os
import re
import json
import time
import pickle
import argparse
import requests
import subprocess
import urllib.parse
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from dotenv import load_dotenv

# ── Config ──────────────────────────────────────────────────────────────────
# Carica segreti da .env
env_path = os.path.join(os.path.dirname(__file__), "..", "credentials", ".env")
load_dotenv(env_path)

BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
FB_PROFILE_ID       = os.getenv("FB_PROFILE_ID")
IG_PROFILE_ID       = os.getenv("IG_PROFILE_ID")
BUFFER_ORG_ID       = os.getenv("BUFFER_ORG_ID")

BUFFER_GRAPHQL_URL  = "https://api.buffer.com/graphql"
REPO_BASE_URL       = "https://raw.githubusercontent.com/cosafannoglieconomisti-bot/Cosa-fanno-gli-Economisti/main"
HISTORY_DIR         = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/marcello"
CLEANED_DIR         = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
TOKEN_FILE          = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/.tmp/tokens/token_youtube.pickle"
TRACKING_FILE       = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/video_tracking.json"
# ─────────────────────────────────────────────────────────────────────────────


def get_youtube_service():
    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def load_history(platform="facebook"):
    history_file = os.path.join(HISTORY_DIR, f"{platform}_history.json")
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"posted_videos": []}


def save_history(history, platform="facebook"):
    history_file = os.path.join(HISTORY_DIR, f"{platform}_history.json")
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)


def is_short(title: str) -> bool:
    return "#shorts" in title.lower() or "shorts" in title.lower()


def find_infographic_asset(folder_path: str) -> str | None:
    """Cerca un'infografica (PNG) nella cartella del paper."""
    # Priorità a nomi specifici
    priorities = ["infografica.png", "infografica_cleaned.png", "infografica_quadrata.png", "infografica_verticale.png"]
    for p in priorities:
        if os.path.exists(os.path.join(folder_path, p)):
            return p
    # Fallback: primo PNG non thumbnail/cover
    for f in os.listdir(folder_path):
        if f.endswith(".png") and "thumb" not in f.lower() and "cover" not in f.lower() and "copertina" not in f.lower():
            return f
    return None


def find_metadata_path(video_title: str) -> str | None:
    """Cerca il file video_metadata.md nella cartella Cleaned corrispondente al titolo video."""
    # Normalizza il titolo per il match fuzzy
    title_words = [w.lower() for w in re.split(r'[^a-zA-Zàèéìòù]+', video_title) if len(w) > 3]

    for folder in sorted(os.listdir(CLEANED_DIR)):
        if folder.startswith("."):
            continue
        folder_lower = folder.lower()
        # match: almeno 2 delle prime 3 parole significative del titolo video si trovano nel folder
        matches = sum(1 for w in title_words[:4] if w in folder_lower)
        if matches >= 2:
            candidate = os.path.join(CLEANED_DIR, folder, "video_metadata.md")
            if os.path.exists(candidate):
                return candidate
    return None


def parse_metadata(path: str) -> dict:
    """
    Estrae dal file video_metadata.md:
      - paper_title  : titolo accademico del paper (in title case, no caps lock)
      - authors      : stringa autori
      - journal      : nome della rivista
      - year         : anno di pubblicazione
      - description  : prima frase della descrizione YouTube (la frase "Lo studio…")
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    result = {
        "paper_title": "",
        "authors":     "",
        "journal":     "",
        "year":        "",
        "description": "",
        "tags":        "",
        "instagram_url": None,
    }

    # Cerca la sezione Descrizione YouTube
    desc_section = ""
    if "## Descrizione YouTube" in content:
        desc_section = content.split("## Descrizione YouTube")[1]
        # Prendi solo il primo blocco (fino a ⏰ o ## successivo)
        for sep in ["⏰", "##", "▬"]:
            if sep in desc_section:
                desc_section = desc_section.split(sep)[0]
        desc_section = desc_section.strip()
    else:
        # Formato alternativo: cerca direttamente "Lo studio"
        match = re.search(r'(Lo studio .+?)(?:\n\n|⏰|##|▬)', content, re.DOTALL)
        if match:
            desc_section = match.group(1).strip()

    # Il testo della descrizione è il primo paragrafo non vuoto
    for para in desc_section.split("\n\n"):
        para = para.strip()
        if para.startswith("Lo studio"):
            result["description"] = para
            break

    if not result["description"]:
        result["description"] = desc_section.split("\n")[0].strip()

    # Estrai titolo accademico: Lo studio "TITOLO" di AUTORI...
    desc = result["description"]

    # Titolo paper — gestisce sia virgolette ASCII (") che curly (“”)
    title_match = re.search(r'Lo studio ["\u201c]([^"\u201d]+)["\u201d]', desc)
    if title_match:
        raw_title = title_match.group(1).strip()
        # Converti in title case se tutto maiuscolo o quasi (> 50% uppercase)
        upper_ratio = sum(1 for c in raw_title if c.isupper()) / max(len(raw_title), 1)
        result["paper_title"] = raw_title.title() if upper_ratio > 0.5 else raw_title

    # Normalizza il titolo nella stringa desc per estrarre correttamente autori/journal
    def _normalize_caps_quotes(text):
        def repl(m):
            inner = m.group(1)
            up_ratio = sum(1 for c in inner if c.isupper()) / max(len(inner), 1)
            return f'"{inner.title()}"' if up_ratio > 0.5 else f'"{inner}"'
        return re.sub(r'["\u201c]([^"\u201d]+)["\u201d]', repl, text)
    
    desc_normalized = _normalize_caps_quotes(desc)
    result["description"] = desc_normalized

    # Autori: dopo chiusura virgolette e "di"
    authors_match = re.search(
        r'["\u201d]\s+di\s+([^,]+(?:,\s+[^,]+)*?)(?:,\s+pubblicato)',
        desc_normalized, re.IGNORECASE
    )
    if authors_match:
        result["authors"] = authors_match.group(1).strip()

    # Journal: dopo "su " e prima di " nel "
    journal_match = re.search(r'pubblicato su \*?([^*\n]+?)\*? nel', desc, re.IGNORECASE)
    if journal_match:
        result["journal"] = journal_match.group(1).strip()

    # Anno: "nel YYYY"
    year_match = re.search(r'\bnel\s+(\d{4})\b', desc, re.IGNORECASE)
    if year_match:
        result["year"] = year_match.group(1)

    # Tag: cerca la riga con hashtag social
    tag_line = ""
    for line in content.splitlines():
        line_stripped = line.strip()
        if re.match(r'^#[A-Za-zÀ-ÿ0-9]', line_stripped) and line_stripped.count("#") >= 2:
            tag_line = line_stripped
            break
    if not tag_line:
        hashtag_match = re.search(r'(#[A-Za-zÀ-ÿ0-9]+(?:\s+#[A-Za-zÀ-ÿ0-9]+){2,})', content)
        if hashtag_match:
            tag_line = hashtag_match.group(1).strip()
    result["tags"] = tag_line if tag_line else "#CosaFannoGliEconomisti #Economia #Ricerca"

    # Instagram Link: cerca la riga con l'infografica
    ig_match = re.search(r'📸\s*Infografica.*?\s*(https://www\.instagram\.com/p/[a-zA-Z0-9_-]+/?(?:\s|$))', content, re.IGNORECASE)
    if ig_match:
        result["instagram_url"] = ig_match.group(1).strip()

    return result


def build_caption(meta: dict, video_id: str, platform: str = "facebook", video_title: str = "", ig_url: str = None, yt_url: str = None, bridge: str = None) -> str:
    """Costruisce la didascalia nel formato SOP (Diverso per FB e IG)."""
    
    description = bridge if bridge else meta.get("description", "")
    video_url = yt_url if yt_url else f"https://www.youtube.com/watch?v={video_id}"
    tags = meta.get("tags", "")

    if platform == "facebook":
        # Formato Deterministico Facebook (Traffic Bridge FB -> IG -> YT)
        parts = [description, ""]
        
        # Sempre aggiungi link Instagram (priorità: override > metadata > canale)
        ig_link = ig_url if ig_url else (meta.get("instagram_url") if meta.get("instagram_url") else "https://www.instagram.com/cosafannoglieconomisti/")
        parts.append(f"📸 Infografica completa su Instagram: {ig_link}")
        
        parts.append(f"▶ Approfondimento Video: {video_url}")
        parts.append("")
        parts.append(tags)
        return "\n".join(parts).strip()
    
    # Formato Standard Instagram (Semplificato)
    parts = []
    if description:
        parts.append(description)
        parts.append("")
    
    parts.append("Link in bio 🔗")
    parts.append("")
    parts.append(tags)

    return "\n".join(parts).strip()


def get_schedule_ts(hour: int = 9, days: int = 1) -> int:
    """Restituisce il timestamp Unix per X giorni nel futuro all'ora specificata (Europe/Rome)."""
    local_tz = timezone(timedelta(hours=2))  # Europe/Rome
    target_date = datetime.now(local_tz).replace(hour=hour, minute=0, second=0, microsecond=0)
    target_date += timedelta(days=days)
    return int(target_date.timestamp())


def post_to_buffer(caption: str, video_id: str, platform: str = "facebook", dry_run: bool = False, scheduled_ts: int = None, image_url: str = None) -> bool:
    """Invia il post a Buffer via GraphQL API (nuovo endpoint Beta)."""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    channel_id = IG_PROFILE_ID if platform == "instagram" else FB_PROFILE_ID

    if scheduled_ts is None:
        scheduled_ts = get_schedule_ts()

    scheduled_human = datetime.fromtimestamp(scheduled_ts, tz=timezone(timedelta(hours=2))).strftime("%Y-%m-%d %H:%M:%S (Europe/Rome)")
    # GraphQL usa ISO8601 UTC
    scheduled_iso = datetime.fromtimestamp(scheduled_ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if dry_run:
        print("\n" + "="*60)
        print(f"DRY RUN — {platform.upper()} Post:")
        print("="*60)
        print(caption)
        print("="*60)
        if image_url: print(f"Asset Image : {image_url}")
        print(f"Link video  : {video_url}")
        print(f"Programmato : {scheduled_human}")
        return True

    # ── Tenta prima con GraphQL API Beta ────────────────────────────────────
    headers = {
        "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # Costruisci attachmentUrl (video per FB, immagine per IG)
    attachment_url = image_url if image_url else video_url

    mutation = """
    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess {
          post {
            id
            status
          }
        }
        ... on NotFoundError {
          message
        }
        ... on UnauthorizedError {
          message
        }
        ... on InvalidInputError {
          message
        }
        ... on LimitReachedError {
          message
        }
        ... on UnexpectedError {
          message
        }
      }
    }
    """

    variables = {
        "input": {
            "channelId": channel_id,
            "text": caption,
            "schedulingType": "automatic",
            "mode": "customScheduled",
            "dueAt": scheduled_iso,
        }
    }


    # Metadata specifico per piattaforma
    if platform == "instagram":
        variables["input"]["metadata"] = {
            "instagram": {
                "type": "post",
                "shouldShareToFeed": True,
            }
        }
    elif platform == "facebook":
        variables["input"]["metadata"] = {
            "facebook": {
                "type": "post"
            }
        }


    # Asset immagine (MANDATORIO per FB/IG secondo nuova policy)
    if image_url:
        variables["input"]["assets"] = {
            "images": [{"url": image_url}]
        }
    elif platform == "facebook":
        # Fallback se non c'è immagine? Per ora manteniamo link, ma la SOP dice di avere sempre copertina
        variables["input"]["assets"] = {
            "link": {"url": video_url}
        }


    print(f"Invio a Buffer GraphQL ({platform})...")
    try:
        resp = requests.post(
            BUFFER_GRAPHQL_URL,
            json={"query": mutation, "variables": variables},
            headers=headers,
            timeout=20,
        )
        data = resp.json()

        # Controlla errori GraphQL di schema/sintassi
        if "errors" in data and resp.status_code != 200:
            print(f"❌ Errore HTTP {resp.status_code}: {resp.text[:500]}")
            return False
        if "errors" in data:
            print(f"❌ GraphQL schema errors: {data['errors']}")
            return False

        if "data" in data:
            gql_data = data["data"].get("createPost", {})
            # PostActionFailure: ha userErrors
            user_errors = gql_data.get("userErrors", [])
            if user_errors:
                print(f"❌ GraphQL userErrors: {user_errors}")
                return False
            # PostActionSuccess: ha post
            post_obj = gql_data.get("post")
            if post_obj:
                print(f"✅ Successo GraphQL! Post ID: {post_obj['id']} — programmato per {scheduled_human}")
                return True
            # Se la risposta è vuota ma status 200, considera successo parziale
            print(f"⚠️ Risposta GraphQL inattesa: {data}")
            return False

        print(f"❌ Risposta inattesa: HTTP {resp.status_code} — {resp.text[:300]}")
        return False

    except Exception as e:
        print(f"❌ Eccezione: {e}")
        return False


def run(video_id_override=None, dry_run=False, scheduled_hour=9, platform="facebook", days_ahead=1, folder_name_override=None, ig_url=None, yt_url=None, bridge=None):
    history = load_history(platform=platform)

    # ... (logica locale o YT API come prima) ...
    if folder_name_override:
        metadata_path = os.path.join(CLEANED_DIR, folder_name_override, "video_metadata.md")
        # ...
        if not os.path.exists(metadata_path):
            print(f"❌ Metadata non trovato in: {metadata_path}")
            return
        
        if video_id_override:
            video_id = video_id_override
        else:
            if os.path.exists(TRACKING_FILE):
                with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
                    tracking = json.load(f)
                video_id = tracking.get(folder_name_override, {}).get("youtube_id")
                # Se non c'è nel tracking, e abbiamo yt_url, possiamo estrarlo
                if not video_id and yt_url:
                    match = re.search(r"v=([a-zA-Z0-9_-]{11})", yt_url)
                    if match: video_id = match.group(1)
                
                if not video_id and not yt_url:
                    print(f"❌ Impossibile trovare youtube_id per '{folder_name_override}' nel registro.")
                    return
            else:
                video_id = "UNKNOWN"
        
        video_title = folder_name_override
    else:
        # ... logic standard YT
        yt = get_youtube_service()
        if video_id_override:
            video_id = video_id_override
            resp = yt.videos().list(part="snippet", id=video_id).execute()
            video_title = resp["items"][0]["snippet"]["title"] if resp.get("items") else "Video"
        else:
            # ... logic automatica
            uploads_id = yt.channels().list(mine=True, part="contentDetails").execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            items = yt.playlistItems().list(part="snippet", playlistId=uploads_id, maxResults=50).execute()["items"]
            video_id, video_title = None, None
            for item in items:
                vid, title = item["snippet"]["resourceId"]["videoId"], item["snippet"]["title"]
                if not is_short(title) and vid not in history["posted_videos"]:
                    video_id, video_title = vid, title
                    break
            if not video_id: return

        metadata_path = find_metadata_path(video_title)
        if not metadata_path: return

    meta = parse_metadata(metadata_path)
    caption = build_caption(meta, video_id, platform=platform, video_title=video_title, ig_url=ig_url, yt_url=yt_url, bridge=bridge)

    # Asset Immagine
    image_url = None
    folder = os.path.dirname(metadata_path)
    if platform == "instagram":
        asset = find_infographic_asset(folder)
    else:
        all_files = os.listdir(folder)
        image_files = [f for f in all_files if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        asset = None
        for c_name in ["copertina.png", "copertina.jpg", "thumbnail.png", "cover.png"]:
            if c_name in image_files:
                asset = c_name
                break
        if not asset and image_files: asset = image_files[0]

    if asset:
        folder_name = os.path.basename(folder)
        image_url = f"{REPO_BASE_URL}/Cleaned/{urllib.parse.quote(folder_name)}/{urllib.parse.quote(asset)}"

    success = post_to_buffer(caption, video_id, platform=platform, dry_run=dry_run, 
                            scheduled_ts=get_schedule_ts(hour=scheduled_hour, days=days_ahead), image_url=image_url)

    if success and not dry_run:
        history["posted_videos"].append(video_id)
        save_history(history, platform=platform)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-id", default=None)
    parser.add_argument("--folder-name", default=None)
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--hour",     type=int, default=10)
    parser.add_argument("--days-ahead", type=int, default=1)
    parser.add_argument("--platform", choices=["facebook", "instagram"], default="facebook")
    parser.add_argument("--ig-url", default=None, help="URL Instagram dell'infografica")
    parser.add_argument("--yt-url", default=None, help="URL YouTube del video")
    parser.add_argument("--bridge", default=None, help="Custom hook (bridge) per il post")
    args = parser.parse_args()

    run(
        video_id_override=args.video_id,
        dry_run=args.dry_run,
        scheduled_hour=args.hour,
        platform=args.platform,
        days_ahead=args.days_ahead,
        folder_name_override=args.folder_name,
        ig_url=args.ig_url,
        yt_url=args.yt_url,
        bridge=args.bridge
    )

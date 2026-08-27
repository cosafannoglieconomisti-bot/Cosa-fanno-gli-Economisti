from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import json
import os
import pickle
import re
import sys
import time

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv(dotenv_path=str(REPO_ROOT / 'Execution' / 'credentials' / '.env'))


def get_youtube_service():
    token_path = str(REPO_ROOT / 'Execution' / 'credentials' / 'token_youtube.pickle')
    with open(token_path, "rb") as token:
        creds = pickle.load(token)
    return build("youtube", "v3", credentials=creds)


def is_date_title(title):
    date_patterns = [
        r"^\d{1,2}\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+\d{4}$",
        r"^\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}$",
        r"^[A-Za-z]{3}\s\d{1,2},\s\d{4}$",
    ]
    return any(re.match(pattern, title, re.IGNORECASE) for pattern in date_patterns)


def normalize_tokens(text):
    text = re.sub(r"[^a-zA-Z0-9àèéìòù ]+", " ", text.lower())
    stopwords = {"il", "lo", "la", "i", "gli", "le", "un", "una", "uno", "di", "del", "della", "dei", "e", "in", "con", "per", "su", "che"}
    return [token for token in text.split() if len(token) > 3 and token not in stopwords]


def build_specific_tags(parent_title, transcript):
    base = ["#shorts", "#economia"]
    tokens = normalize_tokens(f"{parent_title} {transcript}")
    extras = []
    for token in tokens:
        candidate = "#" + re.sub(r"[^A-Za-z0-9]", "", token.title())
        if candidate not in base and candidate not in extras:
            extras.append(candidate)
        if len(extras) == 2:
            break
    return " ".join(base + extras)


def generate_metadata(original_title, parent_title, parent_context, transcript=""):
    parent_clean = parent_title.replace("_", " ")
    title_tokens = normalize_tokens(f"{original_title} {transcript}")[:5]
    if title_tokens:
        title = " ".join(token.capitalize() for token in title_tokens[:4])
    else:
        title = parent_clean[:60]
    hook = f"Un estratto dal paper su {parent_clean.lower()}."
    tags = build_specific_tags(parent_clean, transcript or parent_context)
    return {"title": title[:60], "hook": hook, "tags": tags}


def find_parent_video(video_id, title, tracking):
    overrides = {
        "RWOMLttjSGw": "Dalle_Guerre_ai_Capolavori",
        "M_4e4I_ql8U": "Quando_la_Chiesa_fermo_l_Italia",
        "16GHafTZ5-4": "Regolarizzare_gli_immigrati_riduce_il_crimine",
        "-YELM0HZQ40": "Figli_o_Pensione_La_Scelta",
        "_g_BKiot5_0": "La_Chiesa_frena_l_integrazione",
        "_D02ygxnHGk": "Mafia_e_Sviluppo_Pinotti_2015",
        "TkBdxKizXBw": "I_prof_sono_razzisti",
        "U3GRvQR612Q": "Il_comunismo_ti_cambia_la_mente",
        "DSucrUBXJws": "Laratro_ha_creato_il_patriarcato",
        "TE2601I7Y1c": "Dio_blocca_la_democrazia",
    }
    if video_id in overrides:
        return overrides[video_id]

    keywords = set(normalize_tokens(title))
    best_match = None
    max_overlap = 0
    for key in tracking.keys():
        key_words = set(normalize_tokens(key.replace("_", " ")))
        overlap = len(keywords & key_words)
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = key
    return best_match if max_overlap >= 1 else None


def main(dry_run=True):
    youtube = get_youtube_service()
    tracking_path = str(REPO_ROOT / 'Cleaned' / 'video_tracking.json')
    full_list_path = str(REPO_ROOT / 'Temp' / 'romolo' / 'videos_list_updated.json')
    shorts_list_path = str(REPO_ROOT / 'Temp' / 'romolo' / 'shorts_list.json')

    with open(tracking_path, "r", encoding="utf-8") as handle:
        tracking = json.load(handle)

    verified_shorts = {}
    if os.path.exists(shorts_list_path):
        with open(shorts_list_path, "r", encoding="utf-8") as handle:
            for short in json.load(handle):
                verified_shorts[short["id"]] = short

    candidates = set()
    for short_id, short in verified_shorts.items():
        desc = short.get("description", "")
        title = short.get("title", "")
        if "https://youtu.be/" not in desc or is_date_title(title):
            candidates.add(short_id)

    to_update = []
    for short_id in candidates:
        short = verified_shorts.get(short_id, {})
        title = short.get("title")
        if not title and os.path.exists(full_list_path):
            with open(full_list_path, "r", encoding="utf-8") as handle:
                for item in json.load(handle):
                    if item["id"] == short_id:
                        title = item["title"]
                        break
        if not title:
            title = "Short"
        parent_key = find_parent_video(short_id, title, tracking)
        if parent_key:
            to_update.append({"id": short_id, "title": title, "parent_key": parent_key, "description": short.get("description", "")})

    for item in to_update:
        print(f"\nProcessing {item['id']} ({item['title']})...")
        parent_key = item["parent_key"]
        parent_data = tracking.get(parent_key, {})
        parent_id = parent_data.get("youtube_id")
        if not parent_id:
            print(f"Skipping {item['id']}: Parent video ID not found.")
            continue

        transcript = ""
        transcript_path = f"/Users/<USER>/Desktop/canale/Temp/romolo/transcript_{item['id']}.srt"
        if os.path.exists(transcript_path):
            with open(transcript_path, "r", encoding="utf-8") as handle:
                transcript = handle.read()

        if item["description"] and "https://youtu.be/" in item["description"] and not is_date_title(item["title"]):
            new_title = item["title"]
            final_description = item["description"]
        else:
            new_meta = generate_metadata(item["title"], parent_key, str(parent_data), transcript)
            new_title = new_meta["title"]
            final_description = f"{new_meta['hook']}\n\nVideo completo qui: https://youtu.be/{parent_id}\n\n{new_meta['tags']}"

        print(f"NEW TITLE: {new_title}")
        print(f"NEW DESC: {final_description}")

        if not dry_run:
            try:
                video_response = youtube.videos().list(part="snippet", id=item["id"]).execute()
                snippet = video_response["items"][0]["snippet"]
                snippet["title"] = new_title[:100]
                snippet["description"] = final_description
                youtube.videos().update(part="snippet", body={"id": item["id"], "snippet": snippet}).execute()
                print(f"✅ Updated {item['id']}")
            except Exception as exc:
                print(f"❌ Error updating {item['id']}: {exc}")

        time.sleep(2)


if __name__ == "__main__":
    dry_run = "--real" not in sys.argv
    main(dry_run=dry_run)

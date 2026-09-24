#!/usr/bin/env python3
"""Upload YouTube Short generico (non one-off).

Uso:
  python upload_short.py --folder CleanedTitle --long-id VIDEO_ID
  python upload_short.py --video path.mp4 --title "Hook #shorts" --long-id ID [--schedule ISO]

Richiede che il long-form abbia già youtube_id (passato come --long-id o letto dal tracking).
"""
from __future__ import annotations

import argparse
import os
import pickle
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Execution" / "enea"))

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

from short_assets import (  # noqa: E402
    build_short_description,
    build_short_title,
    find_short_cleaned,
    upsert_short_tracking,
)
from tracking_manager import load_data  # noqa: E402

CREDENTIALS_DIR = REPO_ROOT / "Execution" / "credentials"
TOKEN_PATH = CREDENTIALS_DIR / "token.pickle"
LEGACY_TOKEN = CREDENTIALS_DIR / "token_youtube.pickle"


def get_authenticated_service():
    token_path = TOKEN_PATH if TOKEN_PATH.exists() else LEGACY_TOKEN
    if not token_path.exists():
        raise SystemExit(
            "Credenziali YouTube mancanti. Esegui ./workflow youtube-auth"
        )
    with open(token_path, "rb") as token:
        creds = pickle.load(token)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
        else:
            raise SystemExit("Token YouTube non valido. ./workflow youtube-auth --force")
    return build("youtube", "v3", credentials=creds, static_discovery=False)


def resolve_long_id(folder: str | None, long_id: str | None) -> str:
    if long_id:
        return long_id
    if not folder:
        raise SystemExit("--long-id obbligatorio se --folder assente")
    data = load_data()
    entry = data.get(folder, {})
    vid = entry.get("youtube_id") or ""
    if not vid:
        raise SystemExit(
            f"youtube_id long-form mancante per '{folder}'. "
            "Carica prima il video lungo, poi lo short."
        )
    return vid


def default_schedule_iso() -> str:
    # Short tipicamente poche ore dopo il long (domani 12:00 Europe/Rome ≈ 10:00Z in estate)
    tomorrow = datetime.utcnow() + timedelta(days=1)
    return tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def upload_short(
    video_path: Path,
    title: str,
    description: str,
    schedule_iso: str | None,
    tags: list[str] | None = None,
) -> str:
    youtube = get_authenticated_service()
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags or ["shorts", "economia", "CosaFannoGliEconomisti"],
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "private" if schedule_iso else "private",
            "selfDeclaredMadeForKids": False,
        },
    }
    if schedule_iso:
        body["status"]["publishAt"] = schedule_iso
        body["status"]["privacyStatus"] = "private"

    print(f"Uploading Short: {video_path}")
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
    )
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    video_id = response["id"]
    print(f"Short Uploaded! ID: {video_id}")
    print(f"Link: https://youtube.com/shorts/{video_id}")
    return video_id


def main():
    parser = argparse.ArgumentParser(description="Upload YouTube Short generico")
    parser.add_argument("--folder", help="Nome cartella in Cleaned/")
    parser.add_argument("--video", help="Path al *_shortN_cleaned.mp4")
    parser.add_argument("--title", help="Titolo Short")
    parser.add_argument("--long-id", dest="long_id", help="YouTube ID del video long-form")
    parser.add_argument("--angle", default="1", help="Indice short (default 1)")
    parser.add_argument("--schedule", help="publishAt ISO8601 UTC")
    parser.add_argument("--hook", help="Prima riga descrizione")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    folder = args.folder
    if args.video:
        video_path = Path(args.video)
        if not folder:
            folder = video_path.parent.name
    else:
        if not folder:
            raise SystemExit("Serve --folder oppure --video")
        video_path = find_short_cleaned(REPO_ROOT / "Cleaned" / folder, args.angle)
        if not video_path:
            raise SystemExit(f"Nessun short cleaned in Cleaned/{folder}")

    if not video_path.exists():
        raise SystemExit(f"Video non trovato: {video_path}")

    long_id = resolve_long_id(folder, args.long_id)
    title = args.title or build_short_title(folder.replace("_", " "), args.angle)
    description = build_short_description(long_id, hook=args.hook)
    schedule = args.schedule or default_schedule_iso()

    print(f"Long ID: {long_id}")
    print(f"Title: {title}")
    print(f"Schedule: {schedule}")
    print("--- description ---")
    print(description)
    print("-------------------")

    if args.dry_run:
        print("DRY RUN — upload non eseguito")
        return 0

    short_id = upload_short(video_path, title, description, schedule)
    upsert_short_tracking(
        folder,
        short_id=short_id,
        youtube_url=f"https://youtube.com/shorts/{short_id}",
        angle=args.angle,
        status="Uploaded",
        local_path=str(video_path),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
import argparse
import pickle
import subprocess
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

ROOT = REPO_ROOT
CREDENTIALS_DIR = ROOT / "Execution/credentials"
PRIMARY_TOKEN = CREDENTIALS_DIR / "token.pickle"
LEGACY_YT_TOKEN = CREDENTIALS_DIR / "token_youtube.pickle"
LEGACY_BUFFER_TOKEN = ROOT / "Execution/romolo/.tmp/tokens/token_youtube.pickle"
CLIENT_SECRETS = CREDENTIALS_DIR / "client_secrets.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_credentials(token_path: Path):
    if not token_path.exists():
        return None
    with token_path.open("rb") as handle:
        return pickle.load(handle)


def save_credentials(creds, token_path: Path) -> None:
    ensure_parent(token_path)
    with token_path.open("wb") as handle:
        pickle.dump(creds, handle)


def acquire_credentials(force_reauth: bool = False):
    print(f"[youtube-auth] force_reauth={force_reauth}", flush=True)
    creds = None if force_reauth else load_credentials(PRIMARY_TOKEN)
    if creds and creds.valid:
        print("[youtube-auth] using existing valid token", flush=True)
        return creds, "existing_valid_token"

    if creds and creds.expired and creds.refresh_token and not force_reauth:
        try:
            print("[youtube-auth] trying refresh on primary token", flush=True)
            creds.refresh(Request())
            save_credentials(creds, PRIMARY_TOKEN)
            return creds, "refreshed_token"
        except Exception:
            print("[youtube-auth] refresh failed, falling back to interactive OAuth", flush=True)
            pass

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
    print("[youtube-auth] starting interactive OAuth on localhost", flush=True)
    creds = flow.run_local_server(
        host="localhost",
        port=0,
        open_browser=False,
        authorization_prompt_message="",
        success_message="Autenticazione completata. Puoi chiudere questa finestra.",
    )
    save_credentials(creds, PRIMARY_TOKEN)
    return creds, "interactive_oauth"


def validate_credentials(creds) -> str:
    service = build("youtube", "v3", credentials=creds, static_discovery=False)
    response = service.channels().list(part="snippet", mine=True).execute()
    items = response.get("items", [])
    if not items:
        raise RuntimeError("Nessun canale YouTube associato alle credenziali.")
    return items[0]["snippet"]["title"]


def sync_legacy_tokens() -> None:
    creds = load_credentials(PRIMARY_TOKEN)
    for path in (LEGACY_YT_TOKEN, LEGACY_BUFFER_TOKEN):
        save_credentials(creds, path)


def main():
    parser = argparse.ArgumentParser(description="Bootstrap/Riautenticazione OAuth YouTube")
    parser.add_argument("--force", action="store_true", help="Forza il login interattivo anche se esiste un token.")
    parser.add_argument(
        "--no-legacy-sync",
        action="store_true",
        help="Non copiare il token rigenerato nei path legacy ancora usati da alcuni script.",
    )
    args = parser.parse_args()

    if not CLIENT_SECRETS.exists():
        raise SystemExit(f"client_secrets.json mancante: {CLIENT_SECRETS}")

    print(f"[youtube-auth] client_secrets={CLIENT_SECRETS}", flush=True)
    print(f"[youtube-auth] primary_token={PRIMARY_TOKEN}", flush=True)
    if args.force:
        print("[youtube-auth] forcing browser login flow", flush=True)

    if args.force:
        try:
            subprocess.Popen(["open", "https://accounts.google.com/"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    creds, mode = acquire_credentials(force_reauth=args.force)
    channel_title = validate_credentials(creds)
    if not args.no_legacy_sync:
        sync_legacy_tokens()

    print(f"[youtube-auth] mode={mode}")
    print(f"[youtube-auth] primary_token={PRIMARY_TOKEN}")
    if not args.no_legacy_sync:
        print("[youtube-auth] synced_legacy_tokens=2")
    print(f"[youtube-auth] channel={channel_title}")


if __name__ == "__main__":
    main()

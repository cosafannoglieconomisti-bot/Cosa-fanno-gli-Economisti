from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime

sys.path.append(str(REPO_ROOT / 'Execution' / 'romolo'))
from romolo_manage_channel import get_authenticated_service, SCOPES

HISTORY_FILE = str(REPO_ROOT / 'Temp' / 'romolo' / 'competitor_comment_history.json')
PROPOSALS_JSON = str(REPO_ROOT / 'Temp' / 'romolo' / 'competitor_proposals.json')

# ATTENZIONE: questo script PUBBLICA commenti pubblici sul canale.
# Va lanciato SOLO dopo approvazione esplicita di Marco in chat (SOP /competitor).


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def record_comment_history(video_ids):
    """Unica scrittura dello storico: rilegge, unisce e salva in modo atomico.

    Evita la race documentata in AGENT_MEMORY (2026-06-25): in batch si chiama una
    sola volta a fine giro con tutti gli ID pubblicati.
    """
    if isinstance(video_ids, str):
        video_ids = [video_ids]
    history = load_history()
    added = [vid for vid in video_ids if vid not in history]
    if not added:
        return
    history.extend(added)
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(HISTORY_FILE), suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
        os.replace(tmp_path, HISTORY_FILE)
    except Exception as e:
        print(f"⚠️ Errore salvataggio cronologia commenti: {e}")


def insert_comment(youtube, video_id, text):
    return youtube.commentThreads().insert(
        part='snippet',
        body={
            'snippet': {
                'videoId': video_id,
                'topLevelComment': {
                    'snippet': {
                        'textOriginal': text
                    }
                }
            }
        }
    ).execute()


def post_top_level_comment(video_id, text):
    """Modalita' singola (retro-compatibile): pubblica un commento e aggiorna lo storico."""
    youtube = get_authenticated_service('youtube', 'v3', SCOPES)
    try:
        response = insert_comment(youtube, video_id, text)
        print(f"✅ Commento pubblicato con successo sul video {video_id} (comment id: {response.get('id', '?')})")
        record_comment_history([video_id])
    except Exception as e:
        print(f"❌ Errore nella pubblicazione del commento: {e}")


def post_batch(proposals_path, only=None):
    """Modalita' batch: pubblica le proposte approvate e scrive lo storico UNA volta a fine giro.

    Pubblica gli elementi con `"approved": true` nel JSON, oppure quelli indicati con --only.
    Il testo pubblicato e' il campo `comment` (modificabile a mano prima del lancio).
    """
    with open(proposals_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    proposals = data.get('proposals', []) if isinstance(data, dict) else data
    if only:
        selected = [p for p in proposals if p.get('index') in only]
    else:
        selected = [p for p in proposals if p.get('approved') is True]
    if not selected:
        print("⚠️ Nessuna proposta approvata da pubblicare (usa --only o imposta approved=true).")
        return 1

    already = set(load_history())
    youtube = get_authenticated_service('youtube', 'v3', SCOPES)
    posted, failed, results = [], [], []
    for proposal in selected:
        video_id = proposal['video_id']
        if video_id in already:
            print(f"↩️ Saltato {video_id}: già commentato in passato.")
            results.append({'index': proposal.get('index'), 'video_id': video_id, 'status': 'skipped_already_commented'})
            continue
        try:
            # Nessun retry automatico: un errore (es. commenti disattivati) si registra e si passa oltre.
            response = insert_comment(youtube, video_id, proposal['comment'])
            comment_id = response.get('id', '')
            posted.append(video_id)
            results.append({'index': proposal.get('index'), 'video_id': video_id, 'status': 'posted', 'comment_id': comment_id})
            print(f"✅ Pubblicato su {video_id} ({proposal.get('channel', '')}) · comment id: {comment_id}")
        except Exception as e:
            failed.append(video_id)
            results.append({'index': proposal.get('index'), 'video_id': video_id, 'status': 'error', 'error': str(e)[:500]})
            print(f"❌ Errore su {video_id}: {e}")
    record_comment_history(posted)
    results_path = os.path.join(os.path.dirname(HISTORY_FILE), f"competitor_post_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    try:
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Errore salvataggio risultati: {e}")
    print(f"📌 Batch completato: {len(posted)} pubblicati, {len(failed)} errori. Storico aggiornato una sola volta. Risultati: {results_path}")
    return 0 if not failed else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pubblica commenti /competitor (solo dopo approvazione di Marco).")
    parser.add_argument('video_id', nargs='?', help="Modalita' singola: ID video")
    parser.add_argument('text', nargs='?', help="Modalita' singola: testo del commento")
    parser.add_argument('--batch', nargs='?', const=PROPOSALS_JSON, help="Pubblica le proposte approvate dal JSON (default Temp/romolo/competitor_proposals.json)")
    parser.add_argument('--only', help="Indici delle proposte approvate, es. 1,3,5")
    args = parser.parse_args()

    if args.batch:
        only = {int(x) for x in args.only.split(',') if x.strip()} if args.only else None
        sys.exit(post_batch(args.batch, only))
    if not args.video_id or not args.text:
        print("Uso: python post_youtube_comment.py <video_id> <testo>  |  --batch [file.json] [--only 1,3,5]")
        sys.exit(1)
    post_top_level_comment(args.video_id, args.text)

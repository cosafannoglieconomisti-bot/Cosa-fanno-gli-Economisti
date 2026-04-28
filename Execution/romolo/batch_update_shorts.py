import os
import sys
import pickle
import re
import argparse
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def clean_title(title):
    return re.sub(r'#\S+', '', title).strip()

def format_description(hook, link_id, tags):
    description = f"{hook}\n\nVideo completo qui: https://youtu.be/{link_id}\n\n{tags}"
    return description

def update_shorts_metadata(youtube, video_id, new_title, new_description, dry_run=False):
    print(f"\n--- ELABORAZIONE SHORTS: {video_id} ---")
    print(f"TITOLO: {new_title}")
    print(f"DESC: {new_description.splitlines()[0]} [...]")
    
    if dry_run:
        print("[DRY RUN] Nessuna modifica applicata.")
        return True
    
    try:
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()
        
        if not video_response.get('items'):
            print(f"❌ Video {video_id} non trovato.")
            return False
            
        snippet = video_response['items'][0]['snippet']
        snippet['title'] = new_title
        snippet['description'] = new_description
        
        youtube.videos().update(
            part="snippet",
            body={"id": video_id, "snippet": snippet}
        ).execute()
        
        print(f"✅ Video {video_id} aggiornato.")
        return True
    except Exception as e:
        print(f"❌ Errore su {video_id}: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", help="Video ID of the Short")
    parser.add_argument("--title", help="New catchy title")
    parser.add_argument("--hook", help="Short description hook")
    parser.add_argument("--link_id", help="ID of the long-form video")
    parser.add_argument("--tags", help="Hashtags string", default="#shorts #economia")
    parser.add_argument("--dry-run", action="store_true", help="Do not apply changes")
    
    args = parser.parse_args()
    
    youtube = get_authenticated_service()
    
    if args.id and args.title and args.hook and args.link_id:
        final_title = clean_title(args.title)
        final_desc = format_description(args.hook, args.link_id, args.tags)
        update_shorts_metadata(youtube, args.id, final_title, final_desc, dry_run=args.dry_run)
    else:
        # Fallback to hardcoded list for backward compatibility or batch runs
        updates = [
            {"id": "GdFZMvtHLbo", "title": "Il talento è cieco? La rivoluzione nelle orchestre 🎻", "hook": "Per anni si è pensato che le donne non potessero suonare come gli uomini. Poi è arrivato un semplice oggetto a cambiare tutto: una tenda. Scopri come le audizioni alla cieca hanno rivoluzionato la musica.", "link_id": "CkMiVsvnP0U", "tags": "#shorts #economia #musica #genderbias"},
            {"id": "-LJwjNCwqbc", "title": "Il calcio può fermare una guerra? ⚽🇸🇱", "hook": "Può una semplice qualificazione alla Coppa d'Africa ridurre il rischio di conflitti civili del 9%? La scienza dice di sì: ecco come il calcio costruisce le nazioni.", "link_id": "y4zWdljXoPY", "tags": "#shorts #economia #calcio #storia #pace"}
        ]
        for up in updates:
            final_title = clean_title(up['title'])
            final_desc = format_description(up['hook'], up['link_id'], up['tags'])
            update_shorts_metadata(youtube, up['id'], final_title, final_desc, dry_run=args.dry_run)

    print("\nOperazione completata.")


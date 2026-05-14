import json
import os
import urllib.request
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_")

#Paths
base_dir = "/Users/marcolemoglie_1_2/Desktop/canale"
videos_list_path = os.path.join(base_dir, "Temp/romolo/videos_list_updated.json")
output_dir = os.path.join(base_dir, "Execution/marcello/Copertine")

os.makedirs(output_dir, exist_ok=True)

with open(videos_list_path, 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"Trovati {len(videos)} video. Scarico le copertine...")

for video in videos:
    vid_id = video['id']
    title = video['title']
    safe_title = sanitize_filename(title)
    output_path = os.path.join(output_dir, f"{safe_title}.jpg")
    
    # Try maxres first
    url_maxres = f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg"
    url_hq = f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
    
    try:
        print(f"Scarico {title} ({vid_id})...")
        # Check size or just try download
        urllib.request.urlretrieve(url_maxres, output_path)
        # Verify if it's too small (fallback)
        if os.path.getsize(output_path) < 2000: # 2KB usually fallback
            print(f"Fallback a hqdefault per {vid_id}...")
            urllib.request.urlretrieve(url_hq, output_path)
    except Exception as e:
        print(f"Errore {vid_id}: {e}")
        try:
             urllib.request.urlretrieve(url_hq, output_path)
        except Exception as e2:
             print(f"Errore definitivo {vid_id}: {e2}")

print("Completato.")

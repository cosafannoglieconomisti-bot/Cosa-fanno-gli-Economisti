import os
import json
import requests
import datetime
import pytz
from urllib.parse import quote

from dotenv import load_dotenv

# Configuration
env_path = os.path.join(os.path.dirname(__file__), "..", "credentials", ".env")
load_dotenv(env_path)

BUFFER_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
IG_PROFILE_ID = os.getenv("IG_PROFILE_ID")
REPO_BASE_URL = "https://raw.githubusercontent.com/cosafannoglieconomisti-bot/Cosa-fanno-gli-Economisti/main"
CLEANED_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"

# Mapping of Paper Folders to Infographics and YT Links
PAPERS = [
    {
        "folder": "Memoria_di_sangue_il_legame_shock_tra_eccidi_nazisti_e_mercato_dell_auto_moderno",
        "asset": "Infografica_naziauto.png",
        "youtube": "https://www.youtube.com/watch?v=N4LxEfdrzUw"
    },
    {
        "folder": "La_Peste_Nera_il_segreto_nascosto_che_ha_cambiato_lEuropa_per_sempre",
        "asset": "infografica_peste.png",
        "youtube": "https://www.youtube.com/watch?v=mgl1pjzW8Uc"
    },
    {
        "folder": "Socialismo_la_causa_del_Fascismo",
        "asset": "infografica.png",
        "youtube": "https://www.youtube.com/watch?v=69QiFXrPghY"
    },
    {
        "folder": "Folklore_guida_per_l_economia",
        "asset": "infografica.png",
        "youtube": "https://www.youtube.com/watch?v=7sNESUojy0w"
    },
    {
        "folder": "Dai_narcos_al_petrolio_perche",
        "asset": "infografica_cleaned.png",
        "youtube": "https://www.youtube.com/watch?v=F0O5v-vL7-0"
    },
    {
        "folder": "Stato_Assente_Mafia_Presente",
        "asset": "infografica_quadrata.png",
        "youtube": "https://www.youtube.com/watch?v=tnVy81nzx5s"
    }
]

def get_metadata_caption(folder_path):
    metadata_path = os.path.join(folder_path, "video_metadata.md")
    if not os.path.exists(metadata_path):
        # Fallback to searching for any .md starting with video_metadata
        for f in os.listdir(folder_path):
            if f.startswith("video_metadata") and f.endswith(".md"):
                metadata_path = os.path.join(folder_path, f)
                break
    
    if not os.path.exists(metadata_path):
        return None, []

    with open(metadata_path, 'r') as f:
        content = f.read()
    
    # Extract study paragraph (starts with Lo studio...)
    import re
    # Match the paragraph starting with "Lo studio" until the first empty line or specific marker
    match = re.search(r'(Lo studio ".*?".*?)(?:\n\n|\⏰|$)', content, re.DOTALL)
    caption_intro = match.group(1).strip() if match else ""
    
    # Extract tags
    tags = re.findall(r'#\w+', content)
    return caption_intro, tags

def schedule_posts():
    tz = pytz.timezone('Europe/Rome')
    # Start tomorrow at 10:00 AM
    start_date = datetime.datetime.now(tz) + datetime.timedelta(days=1)
    start_time = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
    
    for i, paper in enumerate(PAPERS):
        folder_path = os.path.join(CLEANED_DIR, paper["folder"])
        caption_intro, tags = get_metadata_caption(folder_path)
        
        if not caption_intro:
            print(f"❌ Impossibile trovare i metadati per {paper['folder']}. Salto.")
            continue
            
        # Clean tags (keep unique, exclude shorts)
        unique_tags = list(dict.fromkeys(tags))
        if "#shorts" in unique_tags: unique_tags.remove("#shorts")
        if "#CosaFannoGliEconomisti" not in unique_tags: unique_tags.insert(0, "#CosaFannoGliEconomisti")
        
        # Build final caption
        caption = f"{caption_intro}\n\n▶ {paper['youtube']}\n\nLink in Bio 🔗\n\n{' '.join(unique_tags)}"
        
        # Build image URL
        # We need the relative path from root to the asset
        # Local dir is /Users/marcolemoglie_1_2/Desktop/canale
        # Path on GH: Cleaned/Folder/Asset
        asset_rel_path = f"Cleaned/{paper['folder']}/{paper['asset']}"
        image_url = f"{REPO_BASE_URL}/{quote(asset_rel_path)}"
        
        # Scheduling time
        post_time = start_time + datetime.timedelta(days=i)
        timestamp = int(post_time.timestamp())
        
        print(f"--- Scheduling Post {i+1} ---")
        print(f"Paper: {paper['folder']}")
        print(f"Scheduled at: {post_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Image: {image_url}")
        
        # Buffer API Call
        payload = {
            "profile_ids[]": IG_PROFILE_ID,
            "text": caption,
            "media[picture]": image_url,
            "scheduled_at": timestamp
        }
        
        headers = {
            "Authorization": f"Bearer {BUFFER_TOKEN}"
        }
        
        # In a real run, we'd use requests.post
        # For verification, I'll print the request first or run it if everything looks OK.
        # Note: IG needs an image, so media[picture] is correct.
        
        response = requests.post("https://api.bufferapp.com/1/updates/create.json", data=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Post schedulato con successo! (ID: {response.json().get('updates', [{}])[0].get('id')})")
        else:
            print(f"❌ Errore durante lo scheduling: {response.text}")

if __name__ == "__main__":
    schedule_posts()

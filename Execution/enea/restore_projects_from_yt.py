
import os
import pickle
import json
import requests
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

TOKEN_FILE = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/.tmp/tokens/token_youtube.pickle"
CLEANED_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"

def get_youtube_service():
    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def restore_project(video_id, folder_name):
    youtube = get_youtube_service()
    print(f"--- Restoring {folder_name} ({video_id}) ---")
    
    # 1. Get snippet and localizations
    video_response = youtube.videos().list(
        part="snippet,status,localizations",
        id=video_id
    ).execute()
    
    if not video_response["items"]:
        print(f"Error: Video {video_id} not found.")
        return
    
    item = video_response["items"][0]
    snippet = item["snippet"]
    localizations = item.get("localizations", {})
    
    folder_path = os.path.join(CLEANED_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # 2. Reconstruct video_metadata.md
    metadata_content = f"# {snippet['title']}\n\n## Descrizione YouTube\n{snippet['description']}\n"
    with open(os.path.join(folder_path, "video_metadata.md"), "w", encoding="utf-8") as f:
        f.write(metadata_content)
    
    # 3. Handle international/ (Localizations)
    intl_dir = os.path.join(folder_path, "international")
    os.makedirs(intl_dir, exist_ok=True)
    
    for lang, data in localizations.items():
        lang_dir = os.path.join(intl_dir, lang)
        os.makedirs(lang_dir, exist_ok=True)
        with open(os.path.join(lang_dir, f"metadata_{lang}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # 4. Download Thumbnail
    thumbnails = snippet.get("thumbnails", {})
    best_thumb = thumbnails.get("maxres") or thumbnails.get("high") or thumbnails.get("default")
    if best_thumb:
        img_data = requests.get(best_thumb["url"]).content
        with open(os.path.join(folder_path, "copertina.png"), "wb") as f:
            f.write(img_data)
        print(f"Thumbnail saved for {folder_name}")

    # 5. Get and Download Captions
    captions_response = youtube.captions().list(
        part="snippet",
        videoId=video_id
    ).execute()
    
    for cap in captions_response.get("items", []):
        lang = cap["snippet"]["language"]
        cap_id = cap["id"]
        try:
            srt_data = youtube.captions().download(id=cap_id, tfmt="srt").execute()
            lang_dir = os.path.join(intl_dir, lang)
            os.makedirs(lang_dir, exist_ok=True)
            with open(os.path.join(lang_dir, f"subtitles_{lang}.srt"), "wb") as f:
                f.write(srt_data)
            if lang == "it":
                with open(os.path.join(intl_dir, "subtitles_it.srt"), "wb") as f:
                    f.write(srt_data)
            print(f"Downloaded caption {lang} for {folder_name}")
        except Exception as e:
            print(f"Could not download caption {lang}: {e}")

    print(f"Done restoring {folder_name}")

if __name__ == "__main__":
    projects = [
        ("9zwAeofGwKE", "Perche_scacciare_la_Mafia_paga"),
        ("F5iW5cpbbdw", "Quando_la_Chiesa_fermo_l_Italia"),
        ("KyA_Pu8BPhE", "La_Chiesa_frena_l_integrazione")
    ]
    for vid, folder in projects:
        restore_project(vid, folder)

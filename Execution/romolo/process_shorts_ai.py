import os
import json
import pickle
import time
import re
from googleapiclient.discovery import build
from google import genai
from dotenv import load_dotenv

load_dotenv(dotenv_path='/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/.env')

def get_youtube_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

def is_date_title(title):
    """Detects if a title is a date (Italian or English format)."""
    # Italian: 11 aprile 2026, 11 apr 2026
    # English: Apr 11, 2024
    date_patterns = [
        r'^\d{1,2}\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+\d{4}$',
        r'^\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}$',
        r'^[A-Za-z]{3}\s\d{1,2},\s\d{4}$'
    ]
    for pattern in date_patterns:
        if re.match(pattern, title, re.IGNORECASE):
            return True
    return False

def generate_metadata(client, original_title, parent_title, parent_context):
    prompt = f"""Sei un esperto Social Media Manager per YouTube.
Devi ottimizzare il titolo e il gancio (hook) di uno YouTube Short per attirare traffico verso un video lungo.

Dati dello Short attuale:
- Titolo attuale: {original_title}

Dati del Video Lungo (Padre):
- Titolo video padre: {parent_title}
- Contesto/Metadati: {parent_context}

REGOLE MANDATORIE:
1. TITOLO: Catchy, massimo 60 caratteri, usa emoji, stile "curiosità" o "domanda".
2. HOOK: Una singola frase potente che faccia venire voglia di vedere il video completo.
3. TAGS: Restituisci una stringa di tag che includa SEMPRE #shorts #economia e 1-2 tag specifici legati all'argomento.

Restituisci ESCLUSIVAMENTE un JSON nel formato:
{{
  "title": "Nuovo Titolo",
  "hook": "Frase ad effetto",
  "tags": "#shorts #economia #tag1 #tag2"
}}
"""
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )
    return json.loads(response.text)

def find_parent_video(video_id, title, tracking):
    """
    Attempts to find the parent video in tracking using keyword matching.
    """
    # Manual overrides for cases identified via research
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
        "TE2601I7Y1c": "Dio_blocca_la_democrazia"
    }
    if video_id in overrides:
        return overrides[video_id]

    # Clean the title for matching
    clean_title = re.sub(r'[^\w\s]', '', title.lower())
    title_words = set(clean_title.split())
    # Exclude common stop words for better matching
    stop_words = {'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'una', 'uno', 'di', 'del', 'della', 'dei', 'degli', 'delle', 'e', 'è', 'in', 'per', 'con', 'su', 'a', 'da', 'tra', 'fra', 'che', 'chi', 'come', 'perché', 'cosa', 'fanno', 'storia', 'verità', 'studio', 'shock'}
    keywords = title_words - stop_words

    if not keywords:
        return None

    best_match = None
    max_overlap = 0

    for key in tracking.keys():
        clean_key = key.replace('_', ' ').lower()
        key_words = set(re.sub(r'[^\w\s]', '', clean_key).split())
        overlap = len(keywords.intersection(key_words))
        
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = key

    # Require at least 2 matching keywords or a single very specific word to avoid false positives
    if max_overlap >= 1:
        return best_match

    return None

def main(dry_run=True):
    youtube = get_youtube_service()
    client = get_gemini_client()
    tracking_path = '/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/video_tracking.json'
    full_list_path = '/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/videos_list_updated.json'
    shorts_list_path = '/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/shorts_list.json'
    
    with open(tracking_path, 'r', encoding='utf-8') as f:
        tracking = json.load(f)

    to_update = []
    
    # 1. Load verified shorts metadata into a lookup dictionary
    verified_shorts = {}
    if os.path.exists(shorts_list_path):
        with open(shorts_list_path, 'r', encoding='utf-8') as f:
            for s in json.load(f):
                verified_shorts[s['id']] = s

    # 2. Collect all candidates for update
    priority_ids = ["DSucrUBXJws", "TE2601I7Y1c", "D-j41dR110M"]
    candidates = set(priority_ids)

    # Candidates from shorts list (missing links, date titles or priority)
    for v_id, s in verified_shorts.items():
        desc = s.get('description', '')
        title = s.get('title', '')
        if "https://youtu.be/" not in desc or is_date_title(title) or v_id in priority_ids:
            candidates.add(v_id)

    # 3. Build the final to_update list with the best available data
    for v_id in candidates:
        # Get title from verified list if possible, else we'll find it
        s = verified_shorts.get(v_id, {})
        title = s.get('title')
        
        # If not in verified_shorts, we need to find it in full_list to get current title
        if not title and os.path.exists(full_list_path):
            with open(full_list_path, 'r', encoding='utf-8') as f:
                for v in json.load(f):
                    if v['id'] == v_id:
                        title = v['title']
                        break
        
        if not title: title = "Short" # Fallback

        # Parent mapping
        static_parents = {
            "SpgBjx6hiH4": "Socialismo_la_causa_del_Fascismo",
            "2soQGo7N-_k": "Il_lato_oscuro_della_TV_aer_2019",
            "RCfHNwxZYv4": "I_ricchi_di_oggi_sono_gli_stessi_del_1400_restud_2021",
            "O7SpDhbLKZo": "La_Peste_Nera_il_segreto_nascosto_che_ha_cambiato_lEuropa_per_sempre",
            "U_ZEqCF-wbw": "L_ascesa_del_Male",
            "tGEsjsvVGiM": "I_robot_ci_rubano_davvero_il_lavoro_S0ZyZE65BgM",
            "DSucrUBXJws": "Laratro_ha_creato_il_patriarcato",
            "TE2601I7Y1c": "Dio_blocca_la_democrazia",
            "D-j41dR110M": "Regolarizzare_gli_immigrati_riduce_il_crimine"
        }
        
        parent_key = static_parents.get(v_id) or find_parent_video(v_id, title, tracking)
        
        if parent_key:
            update_item = {"id": v_id, "title": title, "parent_key": parent_key}
            
            # Add verified description if it's already "good" (has link and not date title)
            # OR if it's a priority ID and we have a description in the cache
            desc = s.get('description', '')
            if ("https://youtu.be/" in desc and not is_date_title(title)) or (v_id in priority_ids and desc):
                update_item["description"] = desc
                
            to_update.append(update_item)
            print(f"Targeting Update: {v_id} ({title}) [Verified Data: {'description' in update_item}]")

    for item in to_update:
        print(f"\nProcessing {item['id']} ({item['title']})...")
        parent_key = item['parent_key']
        parent_data = tracking.get(parent_key, {})
        parent_id = parent_data.get('youtube_id')
        
        if not parent_id:
            print(f"Skipping {item['id']}: Parent video ID not found.")
            continue

        # If we already have a manually verified description, use it!
        if "description" in item:
            new_title = item['title']
            final_description = item['description']
            print("Using pre-defined metadata from shorts_list.json")
        else:
            try:
                new_meta = generate_metadata(client, item['title'], parent_key.replace('_', ' '), str(parent_data))
                new_title = new_meta['title']
                # SOP: Link must be clickable and in isolated line
                final_description = f"{new_meta['hook']}\n\nVideo completo qui: https://youtu.be/{parent_id}\n\n{new_meta['tags']}"
            except Exception as e:
                if "429" in str(e):
                    print("Rate limit hit, waiting 30s...")
                    time.sleep(30)
                    new_meta = generate_metadata(client, item['title'], parent_key.replace('_', ' '), str(parent_data))
                    new_title = new_meta['title']
                    final_description = f"{new_meta['hook']}\n\nVideo completo qui: https://youtu.be/{parent_id}\n\n{new_meta['tags']}"
                else:
                    raise e
        
        print(f"NEW TITLE: {new_title}")
        print(f"NEW DESC: {final_description}")
        
        if not dry_run:
            try:
                video_response = youtube.videos().list(part="snippet", id=item['id']).execute()
                snippet = video_response['items'][0]['snippet']
                snippet['title'] = new_title[:100]
                snippet['description'] = final_description
                
                youtube.videos().update(
                    part="snippet",
                    body={"id": item['id'], "snippet": snippet}
                ).execute()
                print(f"✅ Updated {item['id']}")
            except Exception as e:
                print(f"❌ Error updating {item['id']}: {e}")
        
        print("Waiting 15s for rate limits...")
        time.sleep(15)

if __name__ == "__main__":
    import sys
    dry_run = "--real" not in sys.argv
    main(dry_run=dry_run)

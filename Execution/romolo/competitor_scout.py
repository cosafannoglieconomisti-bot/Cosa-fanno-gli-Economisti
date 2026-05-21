import os
import json
import random
import re
import time
from googleapiclient.discovery import build
from dotenv import load_dotenv
from google import genai

load_dotenv()

REPO_ROOT = "/Users/marcolemoglie_1_2/Desktop/canale"
SCOUT_FILE = os.path.join(REPO_ROOT, "Temp/romolo/competitor_engagement.md")
TRACKING_FILE = os.path.join(REPO_ROOT, "Cleaned/video_tracking.json")
HISTORY_FILE = os.path.join(REPO_ROOT, "Temp/romolo/competitor_comment_history.json")

# Canali Competitor/Complementari target
TARGET_CHANNELS = [
    "Will Media", "Geopop", "Starting Finance", "Factanza", 
    "Breaking Italy", "Liberi Oltre", "Michele Boldrin", "L'Avvocato dell'Atomo",
    "Nova Lectio", "Rick DuFer", "Giopizzi", "Pillole di Economia", 
    "Il Sole 24 Ore", "WesaChannel"
]

def get_authenticated_service():
    from romolo_manage_channel import get_authenticated_service as auth
    return auth('youtube', 'v3', ['https://www.googleapis.com/auth/youtube.force-ssl'])

def load_comment_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def call_gemini_with_retry(client, model, contents, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=model, contents=contents)
            return response
        except Exception as e:
            print(f"⚠️ Errore chiamata Gemini (tentativo {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None

def scout_competitors():
    print("🔍 Scouting competitor e video rilevanti...")
    youtube = get_authenticated_service()
    history = load_comment_history()
    
    candidates = []
    # Cerca gli ultimi video dai canali target
    for channel in TARGET_CHANNELS:
        try:
            # Trova l'ID del canale
            search_channel = youtube.search().list(q=channel, type='channel', part='id', maxResults=1).execute()
            if not search_channel['items']: continue
            channel_id = search_channel['items'][0]['id']['channelId']

            # Prendi i video più recenti (3 anziché 2 per dare più possibilità dopo il filtro duplicati)
            request = youtube.search().list(
                channelId=channel_id,
                part="snippet",
                type="video",
                maxResults=3,
                order="date"
            )
            response = request.execute()
            for item in response.get('items', []):
                v_id = item['id']['videoId']
                if v_id in history:
                    print(f"⏭️ Salto video già commentato: {item['snippet']['title']} ({v_id})")
                    continue
                candidates.append({
                    "title": item['snippet']['title'],
                    "channel": item['snippet']['channelTitle'],
                    "video_id": v_id,
                    "description": item['snippet']['description']
                })
        except Exception as e:
            print(f"⚠️ Errore su {channel}: {e}")

    if not candidates:
        print("⚠️ Nessun video candidato idoneo trovato (tutti già commentati o nessun risultato).")
        return

    # Generazione Commenti via Gemini
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    proposals = []

    # Carica tracking per trovare tutti i nostri video disponibili
    with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
        tracking = json.load(f)
    
    our_videos_list = [k for k, v in tracking.items() if v.get("youtube_url") and v.get("youtube_url") != "Da fare"]
    
    # Prompt per il matching semantico
    matching_prompt = f"""Ho una lista di video del mio canale: {our_videos_list}

Per ognuno dei seguenti video dei miei competitor, dimmi qual è il video del MIO canale che meglio si sposa con il tema trattato. 
Se non c'è un match sensato, scrivi "NESSUNO".

Video Competitor:
"""
    for i, c in enumerate(candidates):
        matching_prompt += f"{i}. {c['channel']}: {c['title']}\n"
    
    matching_prompt += "\nRispondi in formato JSON: [{\"index\": 0, \"match\": \"Nome_Video\"}, ...]"

    response = call_gemini_with_retry(client, 'gemini-flash-latest', matching_prompt)
    if not response:
        print("⚠️ Impossibile completare il matching semantico con Gemini.")
        return

    try:
        # Pulisci l'output JSON (rimuovi ```json ... ```)
        json_str = re.search(r'\[.*\]', response.text, re.DOTALL).group(0)
        matches = json.loads(json_str)
    except Exception as e:
        print(f"⚠️ Errore parsing matching Gemini: {e}")
        return

    for m in matches:
        idx = m['index']
        match_name = m['match']
        
        if match_name == "NESSUNO" or match_name not in tracking:
            continue
            
        v = candidates[idx]
        paper_url = tracking[match_name].get('youtube_url', '')
        
        prompt = f"""Sei l'autore di 'Cosa fanno gli economisti', un canale che divulga paper accademici con rigore e tono divulgativo.
Stai guardando il video di {v['channel']} intitolato: "{v['title']}".

Il tuo obiettivo è lasciare un commento di ALTO VALORE che stimoli la discussione.
Abbiamo un video nel nostro archivio che approfondisce ESATTAMENTE questo tema o un aspetto cruciale: "{match_name}"
URL del nostro video: {paper_url}

Scrivi un commento garbato (max 2-3 frasi) che:
1. Apprezzi sinceramente il video del competitor.
2. Aggiunga un'osservazione scientifica/economica basata sul paper che abbiamo analizzato noi.
3. Inserisca NATURALMENTE il link al nostro video alla fine del commento come approfondimento (es: "Se vi interessa il tema, abbiamo approfondito la ricerca accademica qui: [URL]").
4. Tono: Professionale, curioso, non arrogante.
"""
        resp_comment = call_gemini_with_retry(client, 'gemini-flash-latest', prompt)
        if not resp_comment:
            print(f"⚠️ Errore generazione commento per: {v['title']}")
            continue
            
        comment = resp_comment.text.strip()
        proposals.append({
            "competitor_video": v['title'],
            "competitor_channel": v['channel'],
            "url": f"https://www.youtube.com/watch?v={v['video_id']}",
            "proposed_comment": comment,
            "related_paper": match_name,
            "our_video_url": paper_url
        })

    if proposals:
        # Prendi i primi 5 (o meno)
        proposals = proposals[:5]
        os.makedirs(os.path.dirname(SCOUT_FILE), exist_ok=True)
        with open(SCOUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# 🔍 Scouting Competitor & Proposte Commenti ({len(proposals)})\n\n")
            f.write("> [!IMPORTANT]\n> Approva o modifica i commenti qui sotto prima di pubblicarli.\n\n")
            for i, p in enumerate(proposals, 1):
                f.write(f"## {i}. Video: [{p['competitor_video']}]({p['url']})\n")
                f.write(f"**Canale**: {p['competitor_channel']}\n")
                f.write(f"**Il nostro video correlato**: [{p['related_paper']}]({p['our_video_url']})\n")
                f.write(f"**PROPOSTA COMMENTO**:\n> {p['proposed_comment']}\n\n")
                f.write("---\n\n")
        print(f"✅ Proposte salvate in: {SCOUT_FILE}")

if __name__ == "__main__":
    scout_competitors()

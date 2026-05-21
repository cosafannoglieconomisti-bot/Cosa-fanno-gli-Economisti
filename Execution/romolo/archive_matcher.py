import os
import json
import sys
from google import genai
from dotenv import load_dotenv

# Aggiungi il path per importare news_extractor
sys.path.append("/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse")
from news_extractor import get_raw_news_batch

# Configurazione
load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TRACKING_FILE = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/video_tracking.json"

def match_archive():
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY non trovata.")
        return

    # 1. Carica Archivio
    with open(TRACKING_FILE, 'r') as f:
        archive = json.load(f)
    
    # Crea una lista compatta dell'archivio per Gemini (Titoli e Playlist)
    archive_list = []
    for title, data in archive.items():
        archive_list.append({
            "title": title,
            "playlist": data.get("playlist", "Generale")
        })

    # 2. Carica News
    print("📰 Recupero notizie del giorno...")
    news = get_raw_news_batch()
    if not news:
        print("⚠️ Nessuna notizia trovata.")
        return

    news_text = "\n".join([f"- {n['topic']}: {n['description']}" for n in news[:15]])

    # 3. Chiamata Gemini per Matching
    print("🧠 Matching semantico in corso...")
    prompt = f"""Sei un esperto Social Media Manager per il canale 'Cosa fanno gli economisti'.
    Abbiamo queste notizie calde oggi in Italia:
    {news_text}

    E abbiamo questo archivio di video già pubblicati:
    {json.dumps(archive_list[:200], indent=2)}

    Trova i 3 abbinamenti migliori (MATCH) per creare un 'TRAFFIC BRIDGE' tra Facebook e Instagram.
    Per ogni match, scrivi:
    1. La NOTIZIA di riferimento.
    2. Il VIDEO d'archivio correlato.
    3. Un "HOOK" di 2 frasi che inviti l'utente su Facebook a:
       - Vedere l'infografica completa su Instagram (usa il segnaposto [IG_LINK]).
       - Approfondire con il video su YouTube (usa il segnaposto [YT_LINK]).

    Formato output JSON:
    [
      {{
        "news": "Titolo Notizia",
        "video": "Titolo Video Archivio",
        "hook": "Testo del post social con [IG_LINK] e [YT_LINK]"
      }}
    ]
    Rispondi solo con il JSON puro."""

    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
        raw_res = response.text.strip().replace('```json', '').replace('```', '')
        matches = json.loads(raw_res)
        
        queue_data = []
        print("\n🚀 STRATEGIA DI CRESCITA - TRAFFIC BRIDGE FB -> IG 🚀")
        print("======================================================")
        for m in matches:
            v_title = m['video']
            v_data = archive.get(v_title, {})
            
            # Sostituzione segnaposto con link reali
            ig_raw = v_data.get("instagram_url", "")
            # Se è una stringa di stato (es: "Postato (Foto)") o vuota, usa il profilo del canale
            if "instagram.com" not in ig_raw.lower():
                ig_raw = "https://www.instagram.com/cosafannoglieconomisti/"
            
            final_hook = m['hook'].replace("[IG_LINK]", ig_raw)
            final_hook = final_hook.replace("[YT_LINK]", v_data.get("youtube_url", "Lavori in corso su YT"))
            
            print(f"📌 NEWS: {m['news']}")
            print(f"🎬 ARCHIVIO: {v_title}")
            print(f"✍️ HOOK FB (CON DOPPIO LINK):")
            print(final_hook)
            print("-" * 50)
            
            queue_data.append({
                "news": m['news'],
                "video": v_title,
                "hook": final_hook,
                "instagram_url": ig_raw,
                "youtube_url": v_data.get("youtube_url", "")
            })
            
        # Salvataggio su file
        queue_path = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/crescita/social_bridge_queue.json"
        os.makedirs(os.path.dirname(queue_path), exist_ok=True)
        with open(queue_path, 'w', encoding='utf-8') as f_queue:
            json.dump(queue_data, f_queue, indent=4, ensure_ascii=False)
        print(f"💾 Coda Social Bridge salvata con successo in: {queue_path}")
            
    except Exception as e:
        print(f"❌ Errore durante il matching: {e}")

if __name__ == "__main__":
    match_archive()

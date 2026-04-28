import os
import sys
import time
from datetime import datetime
import json
import threading
import logging # Added by user instruction
import subprocess
import telebot
from telebot import types
from dotenv import load_dotenv
from google import genai
# Per Ulisse news extraction
sys.path.append("/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse")
sys.path.append("/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea")
from news_extractor import get_hot_topics, get_raw_news_batch, SOURCES
from youtube_uploader import get_authenticated_service, get_published_titles
from batch_text_extractor import extract_text

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_ID = os.getenv("ALLOWED_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not ALLOWED_ID or not GEMINI_API_KEY:
    print("❌ Cesare: Variabili d'ambiente (TOKEN, ID, KEY) mancanti nel file .env")
    exit(1)

CESARE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/cesare"
ASSETS_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/assets"
OVERRIDE_PATH = os.path.join(ASSETS_DIR, "override_cover.png")
HUB_PATH = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/cesare/notifications_hub.json"
MAP_PATH = os.path.join(CESARE_DIR, "command_map.json")
BACKLOG_PATH = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/cesare/backlog.txt"
BRIDGE_LOG = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/cesare/telegram_bridge.log"
PYTHON_PATH = "/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3"

user_sessions = {}  # {chat_id: {"paper": "...", "titles": []}}
CACHE_PATH = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/cesare/upload_cache.json"
PROCESS_STATUS = {"articoli": False}

def load_upload_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_upload_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, 'w') as f: json.dump(cache, f)

UPLOAD_CACHE = load_upload_cache()
SESSION_CACHE = {} # {short_id: full_name} per sessioni correnti (/paper, /pulizia)
import hashlib

def send_safe_message(chat_id, text, **kwargs):
    """Prova a inviare con Markdown, altrimenti ripulisce e invia come plain text."""
    log_to_bridge(text, "Cesare (Bot)", source="Bridge")
    try:
        return bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        if "can't parse entities" in str(e).lower():
            # Fallback a testo piano rimuovendo parse_mode
            kwargs.pop('parse_mode', None)
            return bot.send_message(chat_id, text, **kwargs)
        raise e

def send_and_log(chat_id, text, **kwargs):
    """Alias per send_safe_message che enfatizza il logging."""
    return send_safe_message(chat_id, text, **kwargs)

def reply_and_log(message, text, **kwargs):
    """Risponde a un messaggio e logga nel bridge."""
    log_to_bridge(text, "Cesare (Bot Reply)", source="Bridge")
    try:
        return bot.reply_to(message, text, **kwargs)
    except Exception as e:
        if "can't parse entities" in str(e).lower():
            kwargs.pop('parse_mode', None)
            return bot.reply_to(message, text, **kwargs)
        raise e

def load_commands():
    if os.path.exists(MAP_PATH):
        try:
            with open(MAP_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

bot = telebot.TeleBot(TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

def log_to_bridge(message_text, username, source="Telegram"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {source} (@{username}): {message_text}\n"
    with open(BRIDGE_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(f"[{timestamp}] 🌉 Bridge: {source} (@{username}): {message_text[:50]}...")

def get_bundle_titles(pdf_paths):
    import fitz
    context = "Questi sono i contenuti iniziali di alcuni paper. Per ciascuno, identifica il titolo accademico effettivo (es. 'How the West Invented Fertility Restriction').\n\n"
    for path in pdf_paths:
        try:
            doc = fitz.open(path)
            page = doc[0]
            context += f"--- FILE: {os.path.basename(path)} ---\n{page.get_text()[:1000]}\n\n"
        except Exception:
            context += f"--- FILE: {os.path.basename(path)} ---\n[Errore]\n\n"
    prompt = context + "\nRispondi esclusivamente con un elenco nel formato 'FILENAME: TITOLO', una riga per file. Non aggiungere altro."
    try:
         response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
         lines = response.text.split('\n')
         titles_map = {}
         for line in lines:
              if ':' in line:
                    parts = line.split(':', 1)
                    titles_map[parts[0].strip()] = parts[1].strip()
         return titles_map
    except Exception:
         return {}

def run_and_get_output(key, report_path=None):
    commands = load_commands()
    if key not in commands:
        return f"⚠️ Comando '{key}' non trovato nella mappa."
    try:
        if report_path and os.path.exists(report_path):
            try: os.remove(report_path) 
            except: pass
        result = subprocess.run(commands[key], capture_output=True, text=True, cwd="/Users/marcolemoglie_1_2/Desktop/canale", stdin=subprocess.DEVNULL)
        if report_path and os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"❌ Errore Subprocess: {e}"

def run_and_get_output_with_arg(key, arg):
    commands = load_commands()
    if key not in commands:
        return f"⚠️ Comando '{key}' non trovato nella mappa."
    try:
        cmd = list(commands[key])
        cmd.append(arg)
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/Users/marcolemoglie_1_2/Desktop/canale", stdin=subprocess.DEVNULL)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"❌ Errore Subprocess: {e}"

def generate_cover_native(title):
    tmp_path = "/tmp/active_cover.png"
    cmd = [
        "/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3",
        "/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/generate_cover.py",
        title, tmp_path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return tmp_path
    except Exception as e:
        log_to_bridge(f"Errore generazione copertina: {e}", "Cesare (System)", source="Bridge")
        return None

def clear_temp_cover(delete_override=False):
    """Pulisce i file temporanei. L'override viene rimosso solo se richiesto esplicitamente."""
    temp_p = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/temp_cover.png"
    if os.path.exists(temp_p):
        try: os.remove(temp_p)
        except: pass
    if delete_override and os.path.exists(OVERRIDE_PATH):
        try:
            os.remove(OVERRIDE_PATH)
            log_to_bridge("PULIZIA: Override rimosso.", "Cesare", source="Bridge")
        except: pass

# --- TELEGRAM HANDLERS ---

@bot.message_handler(func=lambda m: str(m.chat.id) == ALLOWED_ID)
def handle_message(message):
    user_msg = message.text
    username = message.from_user.username or "Utente"
    
    # Bridge Logging (Input)
    log_to_bridge(user_msg, username, source="Telegram")
    
    user_msg_stripped = user_msg.strip()
    
    # 1. Slash Commands
    if user_msg_stripped.startswith('/'):
        cmd = user_msg_stripped.split()[0]
        
        if cmd == '/backup':
            bot.send_chat_action(message.chat.id, 'typing')
            def run_backup():
                sent = reply_and_log(message, "⏳ Esecuzione backup su GitHub...")
                res = run_and_get_output('backup')
                reply_and_log(message, res[:4000])
                log_to_bridge(res[:500], "Cesare (System)", source="Bridge")
            threading.Thread(target=run_backup).start()
            return

        elif cmd == '/gmail':
            bot.send_chat_action(message.chat.id, 'typing')
            def run_gmail():
                reply_and_log(message, "⏳ Recupero email...")
                res = run_and_get_output('gmail', report_path="/Users/marcolemoglie_1_2/Desktop/canale/Temp/mercurio/gmail_report.txt")
                send_and_log(message.chat.id, res[:4000])
                log_to_bridge("Gmail Report Generato", "Cesare (System)", source="Bridge")
            threading.Thread(target=run_gmail).start()
            return

        elif cmd == '/report':
            bot.send_chat_action(message.chat.id, 'typing')
            def run_report():
                reply_and_log(message, "⏳ Generazione report YouTube...")
                rep_path = f"/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/analytics_reports/analytics_report_{time.strftime('%d_%m_%Y')}.txt"
                res = run_and_get_output('report', report_path=rep_path)
                send_and_log(message.chat.id, res[:4000])
                log_to_bridge("YouTube Report Generato", "Cesare (System)", source="Bridge")
            threading.Thread(target=run_report).start()
            return

        elif cmd == '/articoli':
            if PROCESS_STATUS["articoli"]:
                reply_and_log(message, "⚠️ Ulisse è già al lavoro su un report. Attendi il completamento.")
                return
                
            reply_and_log(message, "⏳ Ricerca news hot e matching accademico in corso (Ulisse)...")
            log_to_bridge("Avvio ricerca Articoli (Ulisse)", username, source="Telegram")
            
            def run_articoli():
                PROCESS_STATUS["articoli"] = True
                try:
                    # 1. Deterministic News Batch Extraction (5 SOP Sources)
                    raw_news = get_raw_news_batch()
                    if not raw_news:
                        send_and_log(message.chat.id, "⚠️ Impossibile recuperare news dalle fonti SOP. Riprovo più tardi.")
                        return

                    # 2. Consensus Discovery & Semantic Tag Extraction
                    # Inviamo il pool di titoli a Gemini per identificare i 3 temi dominanti e aree accademiche
                    news_headlines = "\n".join([f"[{n['source']}] {n['topic']}" for n in raw_news])
                    prompt_consensus = f"""
                    Agisci come Ulisse, esperto di economia e comunicazione.
                    Analizza questo pool di notizie di oggi e identifica i 3 ARGOMENTI PIÙ CALDI (CONSENSUS) basandoti sulla loro ricorrenza tra le fonti o rilevanza macroeconomica.
                    
                    Testate monitorate: ANSA, Corriere, Repubblica, Il Post, Fanpage.
                    
                    Pool Notizie:
                    Identifica i 3 argomenti più caldi (Consensus) basandoti sulla ricorrenza tra queste testate.
                    {news_headlines}
                    
                    Per ogni argomento, fornisci:
                    1. TITOLO CATCHY (MANDATORIO: MASSIMO 5 PAROLE, stile 'clicky' o domanda, centrato sull'argomento economico/sociale del paper).
                    2. Breve sintesi (tono divulgativo/accattivante, 2 righe max).
                    3. Fonti che ne parlano (es: ANSA, Corriere).
                    4. 2-3 Broad Academic Areas (TAGS) per il matching (es: 'Public Economics', 'Labor Economics', 'Political Economy'). 
                       SII ESTREMAMENTE SELETTIVO: I tag devono riflettere l'area economica core del tema per evitare allucinazioni in fase di ricerca.
                    
                    Rispondi rigorosamente in JSON:
                    [
                      {{
                        "topic": "TITOLO BREVE (MAX 5 PAROLE)",
                        "description": "Sintesi dell'argomento...",
                        "sources": "ANSA, Corriere",
                        "tags": ["Public Economics", "Labor Economics"]
                      }},
                      ...
                    ]
                    """
                    
                    try:
                        res_batch = client.models.generate_content(
                            model='gemini-flash-latest',
                            contents=prompt_consensus
                        )
                        raw_content = res_batch.text.replace('```json', '').replace('```', '').strip()
                        topics_list = json.loads(raw_content)
                    except Exception as e:
                        err_str = str(e).lower()
                        if "429" in err_str or "resource_exhausted" in err_str:
                            time.sleep(2) # Retry logic
                            try:
                                res_batch = client.models.generate_content(
                                    model='gemini-flash-latest',
                                    contents=prompt_consensus
                                )
                                raw_content = res_batch.text.replace('```json', '').replace('```', '').strip()
                                topics_list = json.loads(raw_content)
                            except:
                                send_and_log(message.chat.id, "⚠️ Quota Gemini esaurita. Riprova tra poco.")
                                return
                        else:
                            send_and_log(message.chat.id, f"❌ Errore Gemini (Consensus): {str(e)}")
                            return

                    # 3. Deterministic Verification for each topic
                    final_report = "# 📰 Report Ulisse: Consensus & Paper Accademici\n\n"
                    final_report += f"Analisi basata sulle testate: {', '.join(SOURCES.keys())}\n\n"
                    
                    python_bin = "/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3"
                    verify_script = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse/verify_paper.py"
                    
                    for item in topics_list:
                        sources = item.get("sources", "N/A")
                        topic = item.get("topic", "N/A")
                        desc = item.get("description", "N/A")
                        tags_list = item.get("tags", [])
                        
                        final_report += f"### 📌 {topic}\n"
                        final_report += f"_{desc}_\n"
                        final_report += f"**Fonti**: {sources} | **Target**: `{', '.join(tags_list)}`\n\n"
                        
                        # Esegue lo script di verifica
                        tags_str = ",".join(tags_list)
                        log_to_bridge(f"Verifica paper per AREA: {tags_str} | TOPIC: {topic}", "Cesare (System)", source="Bridge")
                        cmd_verify = [python_bin, verify_script, "--tags", tags_str, "--query", topic]
                        v_proc = subprocess.run(cmd_verify, capture_output=True, text=True)
                        
                        if v_proc.returncode == 0:
                            v_out = v_proc.stdout
                            if "---JSON_START---" in v_out:
                                start_idx = v_out.find("---JSON_START---") + len("---JSON_START---")
                                end_idx = v_out.find("---JSON_END---")
                                match = json.loads(v_out[start_idx:end_idx])
                                final_report += f"- **{match['title']}** ({match['year']})\n  _{match['authors']}_\n  *{match['journal']}*\n  🔗 [Leggi qui]({match['url']})\n\n"
                            else:
                                final_report += "> [!NOTE]\n> Nessun matching verificato trovato nei Top Journals per quest'area accademica oggi.\n\n"
                        else:
                            if "[✘ FALLITO]" in v_proc.stdout:
                                final_report += "> [!NOTE]\n> Nessun articolo nei Top Journals corrisponde a quest'area semantica.\n\n"
                            else:
                                final_report += f"⚠️ Errore tecnico verifica: {v_proc.stderr or v_proc.stdout}\n\n"
                    
                    # Salva report
                    report_name = f"temi_hot_matched_{datetime.now().strftime('%d_%m_%Y_%H%M')}.txt"
                    report_path = f"/Users/marcolemoglie_1_2/Desktop/canale/Temp/ulisse/{report_name}"
                    os.makedirs(os.path.dirname(report_path), exist_ok=True)
                    with open(report_path, 'w') as f:
                        f.write(final_report)
                    
                    # Format finale per Telegram (Markdown V2 support workaround via Plain text if complex)
                    send_and_log(message.chat.id, f"✅ Report Ulisse Completato!\n\n{final_report}")
                    log_to_bridge(f"Report Ulisse {report_name} completato (Consensus Mode)", "Cesare (System)", source="Bridge")
                except Exception as e:
                    send_and_log(message.chat.id, f"❌ Errore Ulisse: {e}")
                    log_to_bridge(f"Errore Ulisse: {e}", "Cesare (System)", source="Bridge")
                finally:
                    PROCESS_STATUS["articoli"] = False

            threading.Thread(target=run_articoli).start()
            return

        elif cmd == '/paper':
            bot.send_chat_action(message.chat.id, 'typing')
            def run_paper_menu():
                try:
                    paper_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare"
                    if not os.path.exists(paper_dir):
                        reply_and_log(message, "❌ Directory 'Papers/Da fare' non trovata!")
                        return
                    pdfs = [f for f in os.listdir(paper_dir) if f.endswith(".pdf")]
                    if not pdfs:
                        reply_and_log(message, "📂 Nessun paper in 'Da fare'.")
                        return
                    reply_and_log(message, "🔍 Analisi PDF e recupero titoli in corso...")
                    log_to_bridge("Richiesta elenco Paper", username, source="Telegram")
                    titles_map = get_bundle_titles([os.path.join(paper_dir, p) for p in pdfs])
                    markup = types.InlineKeyboardMarkup()
                    for pdf in pdfs:
                        t = titles_map.get(pdf, pdf)
                        short_id = hashlib.md5(pdf.encode()).hexdigest()[:12]
                        SESSION_CACHE[short_id] = pdf
                        markup.add(types.InlineKeyboardButton(text=f"📄 {t[:50]}", callback_data=f"paper_select:{short_id}"))
                    send_and_log(message.chat.id, "Scegli un paper:", reply_markup=markup)
                except Exception as e:
                    send_and_log(message.chat.id, f"❌ Errore Paper Menu: {e}")
                    log_to_bridge(f"Errore Paper Menu: {e}", "Cesare (System)", source="Bridge")
            
            threading.Thread(target=run_paper_menu).start()
            return

        elif cmd == '/pulizia':
            dl_dir = "/Users/marcolemoglie_1_2/Downloads"
            now = time.time()
            vids_with_time = []
            if os.path.exists(dl_dir):
                for f in os.listdir(dl_dir):
                    # Filtro AGGRESSIVO: Solo video prodotti da NotebookLM (*_raw.mp4)
                    if f.lower().endswith("_raw.mp4"):
                        fpath = os.path.join(dl_dir, f)
                        mtime = os.path.getmtime(fpath)
                        # Solo ultime 24 ore (SOP Aggiornata)
                        if (now - mtime) < 86400:
                            vids_with_time.append((f, mtime))
            
            # Ordina per data (più recente in alto)
            vids_with_time.sort(key=lambda x: x[1], reverse=True)
            vids = [v[0] for v in vids_with_time]
            
            if not vids:
                reply_and_log(message, "📂 Nessun video `*_raw.mp4` trovato in Downloads nelle ultime 24 ore.")
                return
            
            log_to_bridge("Richiesta elenco Pulizia (Filtrata 24h)", username, source="Telegram")
            markup = types.InlineKeyboardMarkup()
            for v in vids[:10]:
                short_id = hashlib.md5(v.encode()).hexdigest()[:12]
                SESSION_CACHE[short_id] = v
                markup.add(types.InlineKeyboardButton(text=f"🎬 {v[:50]}", callback_data=f"pulizia_select:{short_id}"))
            send_and_log(message.chat.id, "Scegli il video RAW da pulire (SOP 3):", reply_markup=markup)
            return

        elif cmd == '/copertina':
            bot.send_chat_action(message.chat.id, 'typing')
            def run_cover_menu():
                try:
                    cleaned_root = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
                    folders_with_time = []
                    for folder in os.listdir(cleaned_root):
                        f_path = os.path.join(cleaned_root, folder)
                        if os.path.isdir(f_path):
                            files = os.listdir(f_path)
                            has_pdf = any(f.endswith('.pdf') for f in files)
                            if has_pdf:
                                mtime = os.path.getmtime(f_path)
                                # Carica titolo da metadati se possibile
                                display_title = folder.replace('_', ' ')
                                try:
                                    meta_p = os.path.join(f_path, "video_metadata.md")
                                    if os.path.exists(meta_p):
                                        with open(meta_p, 'r') as fm:
                                            fl = fm.readline()
                                            if "Metadati Video - " in fl:
                                                display_title = fl.split("Metadati Video - ")[1].strip()
                                except: pass
                                folders_with_time.append({"id": folder, "title": display_title, "mtime": mtime})
                    
                    if not folders_with_time:
                        send_and_log(message.chat.id, "📭 Nessun paper trovato in Cleaned (usa prima /paper).")
                        return

                    # ORDINA PER DATA (PIÙ RECENTE PRIMA)
                    folders_with_time.sort(key=lambda x: x['mtime'], reverse=True)
                    ready_folders = folders_with_time[:10]

                    log_to_bridge("Richiesta Menu Copertina", username, source="Telegram")
                    markup = types.InlineKeyboardMarkup()
                    for obj in ready_folders:
                        short_id = hashlib.md5(obj['id'].encode()).hexdigest()[:12]
                        SESSION_CACHE[short_id] = obj['id']
                        markup.add(types.InlineKeyboardButton(text=f"🎨 {obj['title'][:50]}", callback_data=f"cover_select:{short_id}"))
                    send_and_log(message.chat.id, "Scegli il paper per cui generare la copertina:", reply_markup=markup)
                except Exception as e:
                    send_and_log(message.chat.id, f"❌ Errore menu copertina: {e}")

            threading.Thread(target=run_cover_menu).start()
            return

        elif cmd == '/upload':
            bot.send_chat_action(message.chat.id, 'typing')
            
            def run_upload_menu():
                try:
                    # 1. Recupera titoli già pubblicati (Thread Safe - Abs Paths)
                    published_titles = []
                    try:
                        y_svc = get_authenticated_service()
                        published_titles = get_published_titles(y_svc)
                    except Exception as e:
                        log_to_bridge(f"Errore recupero titoli YT: {e}", "Cesare (System)", source="Bridge")
                    
                    # 2. Recupera cartelle locali
                    cleaned_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
                    folders = [f for f in os.listdir(cleaned_dir) if os.path.isdir(os.path.join(cleaned_dir, f)) and not f.startswith(".")]
                    
                    # 3. Chiedi a Gemini di filtrare semanticamente
                    excluded_folders = []
                    if published_titles and folders:
                        prompt_filter = f"""
                        Agisci come assistente di produzione per un canale YouTube accademico.
                        Il tuo compito è identificare quali di queste cartelle locali corrispondono a video GIÀ PUBBLICATI sul canale.
                        Sii AGGRESSIVO nel matching: se i termini chiave (es: 'Mafia', 'Istituzioni', 'Robot', 'Hitler') coincidono significativamente, considera il video come già pubblicato.
                        
                        CARTELLE LOCALI: {folders}
                        TITOLI ATTUALI SU YT: {published_titles}
                        
                        Rispondi SOLO con i nomi delle cartelle da ESCLUDERE (perché già presenti su YT), separati da virgola. Se non trovi corrispondenze, rispondi 'NESSUNA'.
                        """
                        try:
                            res_f = client.models.generate_content(model='gemini-flash-latest', contents=prompt_filter)
                            res_text = res_f.text.strip()
                            if "NESSUNA" not in res_text:
                                excluded_folders = [s.strip().replace("`", "").replace('"', '') for s in res_text.split(',') if s.strip()]
                            log_to_bridge(f"Filtro IA Esclusioni: {excluded_folders}", "Cesare (System)", source="Bridge")
                        except Exception as e:
                            log_to_bridge(f"Errore filtro IA: {e}", "Cesare (System)", source="Bridge")

                    ready_folders = []
                    UPLOAD_CACHE.clear()
                    import hashlib
                    
                    for f in folders:
                        if f in excluded_folders: continue
                        tdir = os.path.join(cleaned_dir, f)
                        files = os.listdir(tdir)
                        if any(v.endswith("_cleaned.mp4") for v in files) and "video_metadata.md" in files:
                            title = f
                            try:
                                with open(os.path.join(tdir, "video_metadata.md"), 'r', encoding='utf-8') as fm:
                                    fl = fm.readline()
                                    if "Metadati Video - " in fl: title = fl.split("Metadati Video - ")[1].strip()
                            except: pass
                            short_id = hashlib.md5(f.encode()).hexdigest()[:12]
                            UPLOAD_CACHE[short_id] = f
                            ready_folders.append({"id": short_id, "title": title})

                    if not ready_folders:
                        send_and_log(message.chat.id, "📂 Nessun video nuovo trovato o tutti già pubblicati.")
                        return

                    log_to_bridge(f"Proponendo {len(ready_folders)} video filtrati", username, source="Bridge")
                    save_upload_cache(UPLOAD_CACHE) # Persisti
                    markup = types.InlineKeyboardMarkup()
                    for obj in ready_folders[:10]:
                        markup.add(types.InlineKeyboardButton(text=f"🚀 {obj['title'][:50]}", callback_data=f"upload_select:{obj['id']}"))
                    send_and_log(message.chat.id, "Scegli video da caricare:", reply_markup=markup)
                except Exception as e:
                    send_and_log(message.chat.id, f"❌ Errore processamento /upload: {e}")
                    log_to_bridge(f"CRASH /upload thread: {e}", "Cesare (System)", source="Bridge")

            threading.Thread(target=run_upload_menu).start()
            return

        elif cmd == '/produzione':
            bot.send_chat_action(message.chat.id, 'typing')
            def run_produzione_menu():
                try:
                    cleaned_root = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
                    ready_folders = []
                    for folder in os.listdir(cleaned_root):
                        f_path = os.path.join(cleaned_root, folder)
                        if os.path.isdir(f_path):
                            # Deve avere un PDF e NON avere video
                            files = os.listdir(f_path)
                            has_pdf = any(f.endswith('.pdf') for f in files)
                            has_video = any(f.endswith('.mp4') for f in files)
                            if has_pdf and not has_video:
                                ready_folders.append({"id": folder, "title": folder.replace('_', ' ')})
                    
                    if not ready_folders:
                        send_and_log(message.chat.id, "📭 Nessun paper pronto per la produzione (usa prima /paper e approva la copertina).")
                        return

                    markup = types.InlineKeyboardMarkup()
                    for obj in ready_folders[:10]:
                        # Telegram limit 64 bytes for callback_data. Use prefix + short ID.
                        short_id = f"p_{ready_folders.index(obj)}"
                        SESSION_CACHE[short_id] = obj['id']
                        markup.add(types.InlineKeyboardButton(text=f"🎬 {obj['title'][:50]}", callback_data=f"produzione_select:{short_id}"))
                    send_and_log(message.chat.id, "Scegli il paper da produrre (NotebookLM):", reply_markup=markup)
                except Exception as e:
                    send_and_log(message.chat.id, f"❌ Errore menu produzione: {e}")

            threading.Thread(target=run_produzione_menu).start()
            return

        elif cmd == '/playlist':
            bot.send_chat_action(message.chat.id, 'typing')
            def run_playlist_menu():
                try:
                    cleaned_root = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
                    tracking_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/video_tracking.json"
                    
                    tracking = {}
                    if os.path.exists(tracking_path):
                        with open(tracking_path, 'r', encoding='utf-8') as f:
                            tracking = json.load(f)
                            
                    ready_folders = []
                    for folder in os.listdir(cleaned_root):
                        f_path = os.path.join(cleaned_root, folder)
                        if os.path.isdir(f_path):
                            # Selezioniamo i video in Cleaned che hanno uno youtube_id ma NON hanno ancora una playlist assegnata in tracking
                            video_info = tracking.get(folder, {})
                            if video_info.get("youtube_id") and not video_info.get("playlist"):
                                ready_folders.append({"id": folder, "title": folder.replace('_', ' ')})
                                
                    if not ready_folders:
                        send_and_log(message.chat.id, "📭 Nessun video pronto per la catalogazione in playlist (tutti i video caricati sono già catalogati).")
                        return

                    markup = types.InlineKeyboardMarkup()
                    for obj in ready_folders[:10]:
                        short_id = f"pl_{ready_folders.index(obj)}"
                        SESSION_CACHE[short_id] = obj['id']
                        markup.add(types.InlineKeyboardButton(text=f"📂 {obj['title'][:50]}", callback_data=f"playlist_select:{short_id}"))
                    send_and_log(message.chat.id, "Scegli il video da catalogare in una Playlist:", reply_markup=markup)
                except Exception as e:
                    send_and_log(message.chat.id, f"❌ Errore menu playlist: {e}")

            threading.Thread(target=run_playlist_menu).start()
            return

        # Fallback per comandi non riconosciuti (evita trigger accidentali dell'IA)
        reply_and_log(message, f"⚠️ Comando `{cmd}` non riconosciuto. Usa `/paper`, `/produzione`, `/pulizia`, `/articoli`, `/backup`, `/gmail`, `/report`, `/copertina`, `/upload` o `/playlist`.")
        log_to_bridge(f"Comando non riconosciuto: {cmd}", username, source="Telegram")
        return

    # 2. Gemini Auto-Responder (con CONTESTO ATTIVO)
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        # Recupero contesto attivo
        active_ctx = "Nessun paper attivo al momento. L'utente deve lanciare /paper."
        pipe_p = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/active_pipeline.json"
        if os.path.exists(pipe_p):
            with open(pipe_p, 'r') as f:
                pipe = json.load(f)
                active_ctx = f"Paper attivo: '{pipe.get('paper')}' | Titolo YouTube: '{pipe.get('title')}' | Metadati: {pipe.get('metadata')}. Parla sempre in Italiano."
        
        persona = f"""Sei Cesare, il Master Agent proattivo del canale 'Cosa fanno gli economisti'. Aiuta Marco nei suoi task. 
        CONTESTO ATTIVO: {active_ctx}
        Se l'utente si riferisce alla 'Peste Nera', fagli notare gentilmente che quel video è già stato completato e ora stiamo lavorando sul paper sopra indicato."""
        
        response = client.models.generate_content(model='gemini-flash-latest', contents=f"{persona}\n\nUtente: {user_msg}")
        reply = response.text
        send_safe_message(message.chat.id, reply, parse_mode="Markdown")
        log_to_bridge(reply, "Cesare (AI)", source="Bridge")
    except Exception as e:
        # Già gestito in parte da send_safe_message, ma qui catturiamo errori di generazione
        reply_and_log(message, f"❌ Errore Cesare: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data
    chat_id = call.message.chat.id
    
    if data.startswith("cover_select:"):
        short_id = data.split(":", 1)[1]
        folder_name = SESSION_CACHE.get(short_id)
        if not folder_name:
            send_and_log(chat_id, "❌ Sessione scaduta. Rilancia `/copertina`.")
            return
            
        def run_cover_gen():
            try:
                # Recupera titolo dai metadati
                f_path = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Cleaned", folder_name)
                title = folder_name.replace('_', ' ')
                paper_file = ""
                for f in os.listdir(f_path):
                    if f.endswith(".md") and "metadata" in f:
                        with open(os.path.join(f_path, f), 'r') as fm:
                            fl = fm.readline()
                            if "Metadati Video - " in fl: title = fl.split("Metadati Video - ")[1].strip()
                    if f.endswith(".pdf"): paper_file = f

                # Sincronizza active_pipeline per coerenza
                pipe_p = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/active_pipeline.json"
                pipe_data = {
                    "title": title,
                    "clean_title": folder_name,
                    "target_dir": f_path,
                    "paper": paper_file
                }
                with open(pipe_p, 'w') as f: json.dump(pipe_data, f, indent=4)

                send_and_log(chat_id, f"🎨 Generazione copertina per: `{title}`...")
                clear_temp_cover(delete_override=False) # Mantieni override se l'assistente lo ha appena messo
                img = generate_cover_native(title)
                if img:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton("✅ Approva", callback_data="cover_approve"),
                        types.InlineKeyboardButton("🔄 Rigenera", callback_data="cover_regenerate")
                    )
                    markup.add(types.InlineKeyboardButton("❌ Rifiuta", callback_data="cover_reject"))
                    with open(img, 'rb') as f_img:
                        bot.send_photo(chat_id, f_img, caption=f"🖼️ Copertina per: {title}", reply_markup=markup)
                else:
                    send_and_log(chat_id, "❌ Errore durante la generazione dell'immagine.")
            except Exception as e:
                send_and_log(chat_id, f"❌ Errore Generazione: {e}")

        threading.Thread(target=run_cover_gen).start()
        return

    if data.startswith("produzione_select:"):
        short_id = data.split(":", 1)[1]
        folder_name = SESSION_CACHE.get(short_id)
        if not folder_name:
            send_and_log(chat_id, "❌ Sessione scaduta. Rilancia `/produzione`.")
            return
            
        send_and_log(chat_id, f"🚀 Avvio produzione per `{folder_name}`...")
        
        def run_orch():
            try:
                # 1. Trova il PDF nella cartella
                folder_path = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Cleaned", folder_name)
                files = os.listdir(folder_path)
                pdf_file = next((f for f in files if f.endswith('.pdf')), None)
                if not pdf_file:
                    send_and_log(chat_id, "❌ Errore: PDF non trovato nella cartella.")
                    return
                
                # 2. Aggiorna active_pipeline.json per l'orchestratore
                pipe_p = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/active_pipeline.json"
                pipe_data = {
                    "title": folder_name.replace('_', ' '),
                    "paper": pdf_file,
                    "paper_path": os.path.join(folder_path, pdf_file),
                    "target_dir": folder_path
                }
                os.makedirs(os.path.dirname(pipe_p), exist_ok=True)
                with open(pipe_p, 'w') as f:
                    json.dump(pipe_data, f, indent=4)

                # 3. Lancia Orchestratore
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                res = subprocess.check_output([PYTHON_PATH, "/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebooklm_orchestrator.py"], env=env, stderr=subprocess.STDOUT).decode()
                # Tronca a 2500 per essere sicuri al 100% che rientri nei limiti di Telegram con formattazione
                send_and_log(chat_id, f"✅ Produzione completata per `{folder_name}`!\n\n{res[:2500]}")
            except Exception as e:
                msg = str(e.output.decode() if hasattr(e, 'output') else e)
                send_and_log(chat_id, f"❌ Errore Produzione:\n{msg[:3000]}")

        threading.Thread(target=run_orch).start()
        return

    if data.startswith("pulizia_select:"):
        short_id = data.split(":", 1)[1]
        vid = SESSION_CACHE.get(short_id)
        if not vid:
            send_and_log(chat_id, "❌ Sessione pulizia scaduta. Rilancia `/pulizia`.")
            return
            
        send_and_log(chat_id, f"🧹 Avvio pulizia per `{vid}`...")
        def run_p():
            res = run_and_get_output_with_arg('pulizia', vid)
            send_and_log(chat_id, f"✅ Fine pulizia!\n\n{res[:2000]}")
        threading.Thread(target=run_p).start()

    elif data.startswith("paper_select:"):
        short_id = data.split(":", 1)[1]
        pdf = SESSION_CACHE.get(short_id)
        if not pdf:
            send_and_log(chat_id, "❌ Sessione paper scaduta. Rilancia `/paper`.")
            return

        send_and_log(chat_id, f"📖 Analisi `{pdf}`...")
        
        def run_title_generation():
            try:
                paper_path = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare", pdf)
                text = extract_text(paper_path, 3)
                if not text:
                    send_and_log(chat_id, "⚠️ Impossibile leggere il PDF per i titoli. Uso titoli di default.")
                    titles = ["Economia e Società", "L'impatto dei dati", "Ricerca Avanzata", "Sviluppo Locale", "Politiche Pubbliche"]
                else:
                    prompt = f"Basandoti su questo estratto di paper:\n\n{text[:3000]}\n\nGenera 5 titoli Catchy e Clickable per un video YouTube divulgativo. MANDATORIO: MASSIMO 5 PAROLE per ogni titolo, stile 'clicky' o domanda, centrato sull'argomento principale del paper. Rispondi SOLO con la lista numerata (1... 5...)."
                    res = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
                    lines = [ln.strip() for ln in res.text.split('\n') if ln.strip() and any(ln.strip().startswith(str(d)) for d in range(1,6))]
                    titles = [ln.split('.', 1)[1].strip().replace('"', '') for ln in lines if '.' in ln]
                    if not titles: titles = [res.text[:100]] # Fallback
                
                user_sessions[chat_id] = {"paper": pdf, "titles": titles}
                
                # --- [SOP 1 Step 3] Estrazione Metadati Reali ---
                meta_prompt = f"Basandoti su questo estratto di paper:\n\n{text[:2500]}\n\nEstrai i metadati reali e rispondi in formato JSON: {'{'}'real_title': '...', 'authors': '...', 'journal': '...', 'year': '...' {'}'}. SII ESTREMAMENTE PRECISO E DETERMINISTICO."
                try:
                    meta_res = client.models.generate_content(model='gemini-flash-latest', contents=meta_prompt)
                    metadata = json.loads(meta_res.text.strip().replace('```json', '').replace('```', ''))
                    user_sessions[chat_id]["metadata"] = metadata
                    meta_msg = f"🔍 **Metadati Rilevati (SOP 1):**\n📄 **Titolo:** {metadata.get('real_title')}\n👥 **Autori:** {metadata.get('authors')}\n🏛 **Journal:** {metadata.get('journal')} ({metadata.get('year')})"
                    send_and_log(chat_id, meta_msg, parse_mode="Markdown")
                except Exception as e:
                    send_and_log(chat_id, f"⚠️ Errore metadati: {e}")

                markup = types.InlineKeyboardMarkup()
                for i, t in enumerate(titles[:5]):
                    markup.add(types.InlineKeyboardButton(f"{i+1}. {t}", callback_data=f"paper_title:{i}"))
                send_and_log(chat_id, "Seleziona il titolo catchy (SOP 1):", reply_markup=markup)
            except Exception as e:
                send_and_log(chat_id, f"❌ Errore generazione titoli: {e}")

        threading.Thread(target=run_title_generation).start()

    elif data.startswith("paper_title:"):
        idx = int(data.split(":")[1])
        session = user_sessions.get(chat_id)
        if session:
            title = session["titles"][idx]
            send_and_log(chat_id, f"✅ Titolo scelto: {title}\nUsa `/copertina` per proseguire.")
            clear_temp_cover(delete_override=True) # Nuovo paper, cancella tutto
            import re
            clean_title = re.sub(r'[^a-zA-Z0-9]+', '_', title).strip('_')
            target_dir = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Cleaned", clean_title)
            
            pipe_data = {
                "title": title, 
                "clean_title": clean_title,
                "target_dir": target_dir,
                "paper": session["paper"],
                "paper_path": os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare", session["paper"]),
                "metadata": session.get("metadata", {}),
                "academic_title": session.get("metadata", {}).get("real_title", "Paper")
            }
            with open("/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/active_pipeline.json", 'w') as f:
                json.dump(pipe_data, f, indent=4)

    elif data == "cover_approve":
        bot.send_chat_action(chat_id, 'typing')
        def run_approve():
            try:
                pipe_p = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/active_pipeline.json"
                if os.path.exists(pipe_p):
                    with open(pipe_p, 'r') as f:
                        pipe = json.load(f)
                    
                    title = pipe.get("title")
                    if not title:
                        send_and_log(chat_id, "❌ Errore: Titolo non trovato nella pipeline.")
                        return
                        
                    import re
                    clean_title = re.sub(r'[^a-zA-Z0-9]+', '_', title).strip('_')
                    target_dir = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Cleaned", clean_title)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Aggiorna Pipeline con target_dir definitivo
                    pipe["target_dir"] = target_dir
                    pipe["clean_title"] = clean_title
                    with open(pipe_p, 'w') as f:
                        json.dump(pipe, f, indent=4)
                    
                    src = "/tmp/active_cover.png"
                    dest = os.path.join(target_dir, "copertina.png")
                    if os.path.exists(src):
                        import shutil
                        shutil.copy(src, dest)
                        
                        paper_name = pipe.get("paper")
                        metadata = pipe.get("metadata", {})
                        
                        # [SOP 1 Step 3] Spostamento e Rinomina PDF
                        if paper_name:
                            paper_src = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare", paper_name)
                            # Usa il Titolo Scelto per il Nome File (SOP 1 Step 5)
                            paper_dest = os.path.join(target_dir, f"{title}.pdf")
                            if os.path.exists(paper_src):
                                shutil.move(paper_src, paper_dest)
                                log_to_bridge(f"Paper archiviato e rinominato: {paper_dest}", "Cesare (System)", source="Bridge")
                        
                        # [SOP 1 Step 4] Salvataggio Metadati
                        meta_file = os.path.join(target_dir, "video_metadata.md")
                        with open(meta_file, 'w', encoding='utf-8') as mf:
                            mf.write(f"# Metadati Video - {title}\n\n")
                            mf.write(f"📄 **Titolo Originale:** {metadata.get('real_title', 'N/A')}\n")
                            mf.write(f"👥 **Autori:** {metadata.get('authors', 'N/A')}\n")
                            mf.write(f"🏛 **Journal:** {metadata.get('journal', 'N/A')} ({metadata.get('year', 'N/A')})\n\n")
                            mf.write(f"--- \nGenerato via SOP 1\n")
                        
                        send_and_log(chat_id, f"✅ Copertina approvata, Paper archiviato e Metadati salvati!\nCartella: `{target_dir}`\n\nOra puoi usare `/produzione`!")
                        clear_temp_cover(delete_override=True) # Fine sessione
                    else:
                        send_and_log(chat_id, "⚠️ Errore: copertina temporanea non trovata.")
                else:
                    send_and_log(chat_id, "✅ Copertina approvata!")
            except Exception as e:
                send_and_log(chat_id, f"❌ Errore Approvazione: {e}")
                log_to_bridge(f"Errore Approvazione: {e}", "Cesare (System)", source="Bridge")
        
        threading.Thread(target=run_approve).start()

    elif data == "cover_regenerate":
        bot.send_chat_action(chat_id, 'upload_photo')
        def run_regen():
            try:
                pipe_p = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/active_pipeline.json"
                if os.path.exists(pipe_p):
                    with open(pipe_p, 'r') as f: pipe = json.load(f)
                    title = pipe.get("title")
                    clear_temp_cover(delete_override=True) # Rigenera = cancella override
                    img = generate_cover_native(title)
                    if img:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(
                            types.InlineKeyboardButton("✅ Approva", callback_data="cover_approve"),
                            types.InlineKeyboardButton("🔄 Rigenera", callback_data="cover_regenerate")
                        )
                        markup.add(types.InlineKeyboardButton("❌ Rifiuta", callback_data="cover_reject"))
                        with open(img, 'rb') as f_img:
                            bot.send_photo(chat_id, f_img, caption=f"🔄 Nuova versione per: {title}", reply_markup=markup)
                else:
                    send_and_log(chat_id, "❌ Sessione scaduta.")
            except Exception as e:
                send_and_log(chat_id, f"❌ Errore Rigenerazione: {e}")
                log_to_bridge(f"Errore Rigenerazione: {e}", "Cesare (System)", source="Bridge")

        threading.Thread(target=run_regen).start()

    elif data == "cover_reject":
        send_and_log(chat_id, "❌ Copertina rifiutata. Puoi riprovare con `/copertina` o cambiare paper.")
        log_to_bridge("Copertina Rifiutata", "Cesare (User)", source="Telegram")
        clear_temp_cover(delete_override=True)

    elif data.startswith("upload_select:"):
        short_id = data.split(":", 1)[1]
        fid = UPLOAD_CACHE.get(short_id)
        if not fid:
            send_and_log(chat_id, "❌ Sessione scaduta (ID non trovato). Rilancia `/upload`.")
            return
            
        log_to_bridge(f"Selezione Video per Upload: {fid}", "Cesare (User)", source="Telegram")
            
        tdir = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Cleaned", fid)
        
        # Ricerca flessibile Metadati
        meta_p = os.path.join(tdir, "video_metadata.md")
        if not os.path.exists(meta_p):
            # Cerca qualsiasi .md che non sia lo script
            m_files = [f for f in os.listdir(tdir) if f.endswith(".md") and "script" not in f.lower()]
            if m_files: meta_p = os.path.join(tdir, m_files[0])
            
        # Ricerca flessibile Thumbnail
        thumb_p = os.path.join(tdir, "copertina.png")
        if not os.path.exists(thumb_p):
            for n in ["thumbnail.png", "cover.png", "thumbnail.jpg"]:
                if os.path.exists(os.path.join(tdir, n)):
                    thumb_p = os.path.join(tdir, n)
                    break
        
        vids = [f for f in os.listdir(tdir) if f.endswith("_cleaned.mp4")]
        if not vids:
            send_and_log(chat_id, "❌ Video non trovato.")
            return
        vpath = os.path.join(tdir, vids[0])
        
        title = fid
        try:
            with open(meta_p, 'r', encoding='utf-8') as fm:
                fl = fm.readline()
                if "Metadati" in fl or "# " in fl:
                    # Cerca di estrarre un titolo pulito
                    title = fl.replace("Metadati Video - ", "").replace("#", "").strip()
        except: pass

        send_and_log(chat_id, f"🚀 Avvio Upload YouTube per: **{title}**...")
        
        def run_u():
            import datetime
            tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1))
            publish_at = tomorrow.strftime("%Y-%m-%dT08:00:00+01:00")
            cmd = [
                "/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3",
                "/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/youtube_uploader.py",
                vpath, title, meta_p, "--thumbnail", thumb_p, "--schedule", publish_at
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, cwd="/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials", stdin=subprocess.DEVNULL)
                out = res.stdout if res.returncode == 0 else res.stderr
                send_and_log(chat_id, f"✅ Upload completato!\n\n{out[:1000]}")
                log_to_bridge(f"Upload YouTube Completato {title}", "Cesare (System)", source="Bridge")
            except Exception as e:
                send_and_log(chat_id, f"❌ Errore Upload: {e}")

        threading.Thread(target=run_u).start()

    elif data.startswith("playlist_select:"):
        short_id = data.split(":", 1)[1]
        fid = SESSION_CACHE.get(short_id)
        if not fid:
            send_and_log(chat_id, "❌ Sessione scaduta. Rilancia `/playlist`.")
            return
            
        send_and_log(chat_id, f"📂 Avvio catalogazione in playlist per: **{fid.replace('_', ' ')}**...")
        
        def run_playlist():
            cmd = [
                "/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3",
                "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/catalog_video.py",
                fid
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, cwd="/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo", stdin=subprocess.DEVNULL)
                out = res.stdout if res.returncode == 0 else res.stderr
                send_and_log(chat_id, f"✅ Catalogazione completata!\n\n{out[:1000]}")
                log_to_bridge(f"Catalogazione Playlist Completata {fid}", "Cesare (System)", source="Bridge")
            except Exception as e:
                send_and_log(chat_id, f"❌ Errore Catalogazione Playlist: {e}")

        threading.Thread(target=run_playlist).start()

@bot.message_handler(func=lambda m: str(m.chat.id) != ALLOWED_ID)
def unauthorized(m):
    reply_and_log(m, "🔒 Non autorizzato.")

# Thread Notifiche Hub (Semplificato)
def poll_hub():
    while True:
        if os.path.exists(HUB_PATH):
            try:
                with open(HUB_PATH, 'r+') as f:
                    data = json.load(f)
                    if data:
                        for item in data:
                            send_and_log(ALLOWED_ID, f"🔔 **HUB**: {item.get('message')}")
                        f.seek(0); f.truncate(); json.dump([], f)
            except: pass
        time.sleep(10)

threading.Thread(target=poll_hub, daemon=True).start()

print("🤖 Cesare Online (Interactive Bridge)...")
bot.infinity_polling()

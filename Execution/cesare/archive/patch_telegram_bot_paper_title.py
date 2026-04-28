# patch_telegram_bot_paper_title.py
import os

bot_path = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/cesare/telegram_bot.py"

with open(bot_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Aggiungi Helper get_bundle_titles
helper_code = """
def get_bundle_titles(pdf_paths):
    import fitz
    context = "Questi sono i contenuti iniziali di alcuni paper. Per ciascuno, identifica il titolo accademico effettivo (es. 'How the West Invented Fertility Restriction').\\n\\n"
    for path in pdf_paths:
        try:
            doc = fitz.open(path)
            page = doc[0]
            context += f"--- FILE: {os.path.basename(path)} ---\\n{page.get_text()[:1000]}\\n\\n"
        except Exception:
            context += f"--- FILE: {os.path.basename(path)} ---\\n[Errore]\\n\\n"
    prompt = context + "\\nRispondi esclusivamente con un elenco nel formato 'FILENAME: TITOLO', una riga per file. Non aggiungere altro."
    try:
         response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
         lines = response.text.split('\\n')
         titles_map = {}
         for line in lines:
              if ':' in line:
                    parts = line.split(':', 1)
                    titles_map[parts[0].strip()] = parts[1].strip()
         return titles_map
    except Exception:
         return {}
"""

if "def get_bundle_titles" not in content:
    # Inserisci dopo la definizione di client = genai.Client(...)
    if "client = genai.Client(api_key=GEMINI_API_KEY)" in content:
        content = content.replace("client = genai.Client(api_key=GEMINI_API_KEY)", "client = genai.Client(api_key=GEMINI_API_KEY)\n" + helper_code)

# 2. Aggiorna il comando /paper per usare i titoli
old_paper_cmd = """    elif user_msg_stripped == '/paper':
        paper_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare"
        try:
            pdfs = [f for f in os.listdir(paper_dir) if f.endswith(".pdf")]
            if not pdfs:
                bot.reply_to(message, "📂 Nessun paper trovato in 'Da fare'.")
                return
                
            from telebot import types
            keyboard = types.InlineKeyboardMarkup()
            for pdf in pdfs:
                keyboard.add(types.InlineKeyboardButton(text=pdf, callback_data=f"paper_select:{pdf}"))
            bot.send_message(message.chat.id, "Seleziona un paper da processare:", reply_markup=keyboard)
        except Exception as e:
            bot.reply_to(message, f"❌ Errore lettura paper: {e}")
        return"""

new_paper_cmd = """    elif user_msg_stripped == '/paper':
        paper_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare"
        try:
            pdfs = [f for f in os.listdir(paper_dir) if f.endswith(".pdf")]
            if not pdfs:
                bot.reply_to(message, "📂 Nessun paper trovato in 'Da fare'.")
                return
                
            status_msg = bot.reply_to(message, "⏳ Analisi paper e recupero titoli in corso...")
            
            # Recupera i titoli
            paths = [os.path.join(paper_dir, f) for f in pdfs]
            titles_map = get_bundle_titles(paths)
            
            from telebot import types
            keyboard = types.InlineKeyboardMarkup()
            for pdf in pdfs:
                title = titles_map.get(pdf, pdf)
                # Forza accenti o caratteri speciali ad essere puliti
                keyboard.add(types.InlineKeyboardButton(text=f"📄 {title[:55]}", callback_data=f"paper_select:{pdf}"))
                
            bot.delete_message(message.chat.id, status_msg.message_id)
            bot.send_message(message.chat.id, "Seleziona un paper da processare:", reply_markup=keyboard)
        except Exception as e:
            bot.reply_to(message, f"❌ Errore lettura paper: {e}")
        return"""

if "status_msg = bot.reply_to(message," not in content:
    content = content.replace(old_paper_cmd, new_paper_cmd)

with open(bot_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch Titoli applicata!")

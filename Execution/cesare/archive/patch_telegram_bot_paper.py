# patch_telegram_bot_paper.py
import os

bot_path = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/cesare/telegram_bot.py"

with open(bot_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inserisci Import Datetime
if "from datetime import datetime" not in content:
    content = content.replace("import time", "import time\nfrom datetime import datetime")

# 2. Inserisci Stato Globale (se non presente)
if "user_sessions = {}" not in content:
    old_state = 'BACKLOG_PATH = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/cesare/backlog.txt"'
    new_state = old_state + '\nuser_sessions = {}  # {chat_id: {"paper": "...", "titles": []}}'
    content = content.replace(old_state, new_state)

# 3. Inserisci Callback handlers per Enea
callback_marker = '    action_data = call.data'
callback_payload = """    action_data = call.data
    
    # --- PIPELINE ENEA INTERATTIVA: SELEZIONE PAPER ---
    if action_data.startswith("paper_select:"):
        file_name = action_data.split(":", 1)[1]
        chat_id = call.message.chat.id
        try:
            bot.answer_callback_query(call.id, f"Elaborazione {file_name}...")
        except: pass
        bot.send_message(chat_id, f"📖 **Enea**: Estrazione testo per `{file_name}`...")
        
        user_sessions[chat_id] = {"paper": file_name, "titles": []}
        
        # Estrai testo
        subprocess.run([
            "/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3",
            "/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/batch_text_extractor.py",
            file_name
        ])
        
        txt_path = f"/tmp/{file_name}.txt"
        if not os.path.exists(txt_path):
            bot.send_message(chat_id, f"❌ Errore nell'estrazione del testo per {file_name}.")
            return
            
        with open(txt_path, 'r', encoding='utf-8') as f_txt:
            paper_text = f_txt.read()[:3000] # Limite prompt
            
        bot.send_message(chat_id, "🤖 **Gemini**: Generazione 5 titoli catchy...")
        prompt = f"Sei Enea. Leggi questo estratto di un paper e proponi **5 titoli catchy** per un video YouTube. Rispondi solo con una riga per ogni titolo (1-5), senza commenti.\\n\\nESTRATTO:\\n{paper_text}"
        
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            titles = [t.strip().split(".", 1)[-1].strip() for t in response.text.split("\\n") if t.strip()][:5]
            user_sessions[chat_id]["titles"] = titles
            
            from telebot import types
            keyboard = types.InlineKeyboardMarkup()
            for idx, title in enumerate(titles):
                keyboard.add(types.InlineKeyboardButton(text=f"{idx+1}. {title[:40]}...", callback_data=f"paper_title:{idx}"))
            bot.send_message(chat_id, "Seleziona il titolo definitivo:", reply_markup=keyboard)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Errore nella generazione dei titoli: {e}")
            
    elif action_data.startswith("paper_title:"):
        idx = int(action_data.split(":", 1)[1])
        chat_id = call.message.chat.id
        session = user_sessions.get(chat_id)
        
        if not session or "titles" not in session or idx >= len(session["titles"]):
                bot.send_message(chat_id, "❌ Sessione scaduta o titolo non valido. Ripeti `/paper`.")
                return
                
        selected = session["titles"][idx]
        paper = session["paper"]
        try: bot.answer_callback_query(call.id, f"Selezionato: {selected}")
        except: pass
        bot.send_message(chat_id, f"✅ **Titolo Scelto**: {selected}")
        
        # Crea cartella Cleaned/[Titolo]
        clean_title = "".join([c if c.isalnum() or c in (' ', '_', '-') else '' for c in selected]).replace(' ', '_')
        dir_path = f"/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/{clean_title}"
        os.makedirs(dir_path, exist_ok=True)
        
        # Salva metadati
        metadata_content = f"# Metadati Video\\n\\nPaper: {paper}\\nTitolo: {selected}\\nData: {datetime.now().strftime('%Y-%m-%d')}\\n"
        with open(os.path.join(dir_path, "video_metadata.md"), 'w', encoding='utf-8') as f_meta:
                f_meta.write(metadata_content)
                
        # Crea Temp/enea per evitare errori di cartella
        os.makedirs("/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea", exist_ok=True)
        active_pipe = {"paper": paper, "title": selected, "clean_title": clean_title, "dir": dir_path}
        with open("/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/active_pipeline.json", 'w', encoding='utf-8') as f_pipe:
                import json
                json.dump(active_pipe, f_pipe)
                
        bot.send_message(chat_id, f"📁 Cartella creata: `Cleaned/{clean_title}`\\nPuoi procedere con `/copertina`!")
"""

if "paper_select:" not in content:
    content = content.replace(callback_marker, callback_payload)

# 4. Inserisci comando /paper e /copertina in handle_message
command_marker = "    elif user_msg_stripped == '/report':"
command_payload = """    elif user_msg_stripped == '/paper':
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
        return
        
    elif user_msg_stripped == '/copertina':
        # Da implementare nel prossimo step
        bot.reply_to(message, "🛠️ Comando `/copertina` in fase di sviluppo. Finisci prima `/paper`!")
        return
        
    elif user_msg_stripped == '/report':"""

if "'/paper'" not in content:
    content = content.replace(command_marker, command_payload)

with open(bot_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applicata per Enea!")

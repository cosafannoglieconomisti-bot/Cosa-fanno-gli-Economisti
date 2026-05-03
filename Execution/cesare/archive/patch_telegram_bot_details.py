import os

filepath = 'Execution/cesare/telegram_bot.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "elif user_msg_stripped == '/articoli':"
end_marker = "prompt = f\"\"\""

new_logic = """elif user_msg_stripped == '/articoli':
        bot.reply_to(message, "⏳ Ricerca 5 notizie hot in corso (Google Search)...")
        
        ALLOWED_JOURNALS = [
            "Nature", "Science", "PNAS", 
            "AER", "American Economic Review", 
            "QJE", "Quarterly Journal of Economics", 
            "JPE", "Journal of Political Economy", 
            "Econometrica", "REStud", "Review of Economic Studies",
            "REStat", "Review of Economics and Statistics", 
            "JEEA", "Journal of the European Economic Association", 
            "EJ", "Economic Journal", 
            "AEJ: Applied", "AEJ: Policy", 
            "JPubE", "Journal of Public Economics", 
            "JDE", "Journal of Development Economics", 
            "JOLE", "Journal of Labor Economics", 
            "JHR", "Journal of Human Resources", 
            "JFE", "Journal of Financial Economics", 
            "JME", "Journal of Monetary Economics",
            "APSR", "AJPS", "JOP"
        ]

        try:
            # 1. Recupero Notizie
            prompt_news = "Sei un giornalista. Cerca le 5 notizie (hot topics) più importanti di oggi in Italia (usa ANSA o Repubblica). Ritorna solo un elenco numerato dove ogni riga ha questo formato: 'Numero. Titolo News | Descrizione: Breve riassunto di 2 frasi'."
            response_news = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_news,
                config={"tools": [{"google_search": {}}]}
            )
            raw_news = response_news.text
            topics = [line.strip() for line in raw_news.split('\\n') if line.strip() and line[0].isdigit()]
            
            if not topics:
                 bot.reply_to(message, f"⚠️ Non ho trovato un elenco numerato di notizie. Ecco cosa ha risposto Gemini:\\n\\n{raw_news[:1000]}")
                 return

            bot.send_message(message.chat.id, f"✅ Trovate {len(topics[:5])} notizie. Ora procedo alla ricerca e verifica dei paper accademici correlati (operazione lenta)...")
            
            report_lines = []
            report_lines.append(f"📊 **REPORT ULISSE - NEWS & MATCHING ACCADEMICO** ({time.strftime('%d/%m/%Y')})\\n")
            report_lines.append("="*40)
            
            verified_count = 0
            for i, topic in enumerate(topics[:5], 1):
                # Estrai Titolo e Descrizione
                # Numero. Titolo News | Descrizione: ...
                if '|' in topic:
                     parts_topic = [p.strip() for p in topic.split('|', 1)]
                     news_title = parts_topic[0].split('.', 1)[1].strip() if '.' in parts_topic[0] else parts_topic[0]
                     news_desc = parts_topic[1]
                else:
                     news_title = topic.split('.', 1)[1].strip() if '.' in topic else topic
                     news_desc = "Descrizione non fornita"

                report_lines.append(f"\\n🔥 **ARGOMENTO {i}**: {news_title}")
                report_lines.append(f"💬 **Descrizione**: {news_desc}")
                
                # 2. Ricerca Paper
                prompt_paper = "Sei un ricercatore di Economia. Trova 3 articoli accademici correlati a questo tema: \\"" + news_title + "\\" da riviste prestigiose dal 2000 ad oggi. Rispondi solo in questo formato (una riga per paper): Titolo | Autori | Journal | Giustificazione del matching"
                
                res_paper = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_paper)
                paper_lines = [l.strip() for l in res_paper.text.split('\\n') if '|' in l]
                
                verified_paper_found = False
                for pline in paper_lines:
                     parts = [p.strip() for p in pline.split('|')]
                     if len(parts) < 3: continue
                     title, authors, journal = parts[0], parts[1], parts[2]
                     justification = parts[3] if len(parts) > 3 else "Giustificazione non trovata"
                     
                     # Filtro Journal
                     journal_ok = False
                     for aj in ALLOWED_JOURNALS:
                          if aj.lower() in journal.lower():
                               journal_ok = True
                               break
                               
                     if not journal_ok:
                          continue
                          
                     # 3. Verifica Determinista
                     script_path = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse/verify_paper.py"
                     res_verify = subprocess.run(
                         ["python3", script_path, "--title", title, "--authors", authors],
                         capture_output=True, text=True
                     )
                     
                     if res_verify.returncode == 0:
                         link = "Link non rilevato"
                         for line in res_verify.stdout.split('\\n'):
                             if "Link" in line:
                                 link = line.split(":", 1)[1].strip()
                                 break
                         
                         report_lines.append(f"✅ **[VERIFICATO: {journal}]**")
                         report_lines.append(f"   📄 Titolo: {title}")
                         report_lines.append(f"   👥 Autori: {authors}")
                         report_lines.append(f"   💡 **Giustificazione**: {justification}")
                         report_lines.append(f"   🔗 Link: {link}")
                         verified_paper_found = True
                         verified_count += 1
                         break
                         
                if not verified_paper_found:
                     report_lines.append(f"⚠️ **[NON VERIFICATO]** Nessun paper candidato ha superato i controlli o i filtri Journal.")

            report_text = '\\n'.join(report_lines)
            
            folder_path = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/ulisse/selezione argomenti"
            os.makedirs(folder_path, exist_ok=True)
            filename = f"temi_hot_matched_verificati_{time.strftime('%d_%m_%Y')}.txt"
            filepath = os.path.join(folder_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_text)
                
            bot.send_message(message.chat.id, f"✅ Report generato e verificato ({verified_count} articoli confermati)!\\nSalvato in `Temp/ulisse/.../{filename}`")
            bot.send_message(message.chat.id, f"📄 **ANTEPRIMA**:\\n\\n{report_text[:3900]}")
            return

        except Exception as e:
             bot.reply_to(message, f"❌ Errore Chaining/Verifica del report: {e}")
        return

    """

parts = content.split(start_marker)
before = parts[0]
after = parts[1]

sub_parts = after.split(end_marker)
# Preserve the bot prompt handler correctly
after_bot_prompt = end_marker + sub_parts[1]

updated_content = before + new_logic + "\n    " + after_bot_prompt

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("Logic chained perfected with details!")

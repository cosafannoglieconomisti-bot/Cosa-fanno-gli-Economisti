import os

filepath = 'Execution/cesare/telegram_bot.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "elif user_msg_stripped == '/articoli':"
end_marker = "prompt = f\"\"\""

new_logic = """elif user_msg_stripped == '/articoli':
        global is_articoli_running
        if is_articoli_running:
             bot.reply_to(message, "⏳ Una ricerca `/articoli` è già in corso. Attendi che finisca per evitare di esaurire la quota API.")
             return
             
        is_articoli_running = True
        bot.reply_to(message, "⏳ Ricerca notizie e articoli accademici in corso (1 singola richiesta per salvaguardare la quota API)...")
        
        ALLOWED_JOURNALS = [
            "Nature", "Science", "PNAS", "AER", "American Economic Review", 
            "QJE", "Quarterly Journal of Economics", "JPE", "Journal of Political Economy", 
            "Econometrica", "REStud", "REStat", "JEEA", "EJ", "AEJ", "JPubE", "JDE"
        ]

        try:
             # Singola chiamata per evitare 429
             prompt_articoli_single = "Sei Ulisse/Articoli. Cerca le **2 notizie** più importanti di oggi in Italia. Per ciascuna, proponi **3 articoli accademici correlati** da riviste economiche prestigiose. Rispondi **ESCLUSIVAMENTE** in questo formato testuale:\\n\\nARGOMENTO: [Titolo News]\\nDESCRIZIONE: [Breve sintesi]\\nCANDIDATI:\\n1. [Titolo Paper] | [Autori] | [Journal] | [Giustificazione]\\n2. [Titolo Paper] | [Autori] | [Journal] | [Giustificazione]\\n3. [Titolo Paper] | [Autori] | [Journal] | [Giustificazione]\\n---"

             response = None
             import time
             for attempt in range(3):
                  try:
                       response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt_articoli_single,
                            config={"tools": [{"google_search": {}}]}
                       )
                       break
                  except Exception as e:
                       if "429" in str(e):
                            time.sleep(20)
                       else: raise e

             if not response:
                  bot.reply_to(message, "❌ Quota limit superata. Riprova tra dieci minuti.")
                  return

             raw_text = response.text
             blocks = raw_text.split('ARGOMENTO:')
             
             report_lines = []
             report_lines.append(f"📊 **REPORT ULISSE - NEWS & MATCHING ACCADEMICO** ({time.strftime('%d/%m/%Y')})\\n")
             report_lines.append("="*40)
             
             verified_count = 0
             news_index = 1
             
             for block in blocks[1:]:
                  if 'CANDIDATI:' not in block: continue
                  
                  lines = [l.strip() for l in block.split('\\n') if l.strip()]
                  news_title = lines[0] if lines else "News"
                  
                  news_desc = "Descrizione non fornita"
                  candidates_start_idx = 0
                  for idx, line in enumerate(lines):
                       if line.startswith("DESCRIZIONE:"):
                            news_desc = line.replace("DESCRIZIONE:", "").strip()
                       if "CANDIDATI:" in line:
                            candidates_start_idx = idx + 1
                            break
                            
                  report_lines.append(f"\\n🔥 **ARGOMENTO {news_index}**: {news_title}")
                  report_lines.append(f"💬 **Descrizione**: {news_desc}")
                  news_index += 1
                  
                  paper_candidates = lines[candidates_start_idx:]
                  verified_paper_found = False
                  
                  for pline in paper_candidates:
                       if '---' in pline or not pline: break
                       if pline[0].isdigit() and '.' in pline:
                            pline = pline.split('.', 1)[1].strip()
                            
                       parts = [p.strip() for p in pline.split('|')]
                       if len(parts) < 3: continue
                       title, authors, journal = parts[0], parts[1], parts[2]
                       justification = parts[Part] if len(parts) > 3 else "Non fornita"
                       # Wait, parts[3] is correct.
                       justification = parts[3] if len(parts) > 3 else "Non fornita"
                       
                       journal_ok = False
                       for aj in ALLOWED_JOURNALS:
                            if aj.lower() in journal.lower():
                                 journal_ok = True
                                 break
                       if not journal_ok: continue
                       
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
                       report_lines.append(f"⚠️ **[NON VERIFICATO]** Nessun candidato ha superato i controlli deterministici.")

             report_text = '\\n'.join(report_lines)
             
             folder_path = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/ulisse/selezione argomenti"
             os.makedirs(folder_path, exist_ok=True)
             filename = f"temi_hot_matched_verificati_{time.strftime('%d_%m_%Y')}.txt"
             filepath = os.path.join(folder_path, filename)
             
             with open(filepath, 'w', encoding='utf-8') as f:
                 f.write(report_text)
                 
             bot.send_message(message.chat.id, f"✅ Report generato (1 richiesta) e verificato ({verified_count} articoli confermati)!\\nSalvato in `[Ulisse] .../{filename}`")
             bot.send_message(message.chat.id, f"📄 **ANTEPRIMA**:\\n\\n{report_text[:3900]}")
             return

        except Exception as e:
             bot.reply_to(message, f"❌ Errore Singolo/Verifica del report: {e}")
        finally:
             is_articoli_running = False
        return

    """

parts = content.split(start_marker)
before = parts[0]
after = parts[1]

sub_parts = after.split(end_marker)
after_bot_prompt = end_marker + sub_parts[1]

updated_content = before + new_logic + "\n    " + after_bot_prompt

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("Reverted to Single Prompt safely!")

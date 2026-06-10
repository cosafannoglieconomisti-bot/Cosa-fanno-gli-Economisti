import os

filepath = 'Execution/cesare/telegram_bot.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Trovare la riga:
# res_paper = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_paper)

# Sostituiremo il blocco:
#                 res_paper = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_paper)
#                 paper_lines = [l.strip() for l in res_paper.text.split('\\n') if '|' in l]

target_block = """                res_paper = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_paper)
                paper_lines = [l.strip() for l in res_paper.text.split('\\n') if '|' in l]"""

replacement_block = """                # Retry Backoff per evitare 429 Rate Limit
                res_paper = None
                import time
                for attempt in range(3):
                    try:
                        time.sleep(1.5) # Delay precauzionale tra le chiamate
                        res_paper = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_paper)
                        break
                    except Exception as e:
                        if "429" in str(e):
                             print(f"[*] 429 rilevato per topic {i}, attendo 5 secondi (tentativo {attempt+1}/3)...")
                             time.sleep(5)
                        else:
                             raise e
                
                if not res_paper:
                     report_lines.append(f"⚠️ **[NON DISPONIBILE]** Impossibile recuperare paper (Rate Limit API).")
                     continue

                paper_lines = [l.strip() for l in res_paper.text.split('\\n') if '|' in l]"""

if target_block in content:
    content = content.replace(target_block, replacement_block)
    print("Backoff added successfully via simple replace!")
else:
    print("Target block not found precisely. Using split marker strategy.")
    # Fallback split strategy
    start_marker = "prompt_paper = \"Sei un ricercatore di Economia."
    # We find where prompt_paper is defined
    parts = content.split("res_paper = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_paper)")
    if len(parts) > 1:
         before = parts[0]
         after = parts[1]
         # after starts with \n                paper_lines = ...
         sub_after = after.split("paper_lines = [l.strip() for l in res_paper.text.split('\\n') if '|' in l]", 1)
         rest = sub_after[1]
         
         updated_content = before + """# Retry Backoff per evitare 429 Rate Limit
                res_paper = None
                import time
                for attempt in range(3):
                    try:
                        time.sleep(1.5)
                        res_paper = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_paper)
                        break
                    except Exception as e:
                        if "429" in str(e):
                             time.sleep(5)
                        else:
                             raise e
                if not res_paper:
                     report_lines.append(f"⚠️ **[NON DISPONIBILE]** Impossibile recuperare paper (Rate Limit API).")
                     continue
                paper_lines = [l.strip() for l in res_paper.text.split('\\n') if '|' in l]""" + rest
         content = updated_content
         print("Backoff added via split strategy!")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

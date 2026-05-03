import os

filepath = 'Execution/cesare/telegram_bot.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Trovare il blocco del Prompt 1:
#             response_news = client.models.generate_content(
#                 model='gemini-2.5-flash',
#                 contents=prompt_news,
#                 config={"tools": [{"google_search": {}}]}
#             )

target_block = """            response_news = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_news,
                config={"tools": [{"google_search": {}}]}
            )"""

replacement_block = """            # Retry Backoff per Step 1 News
            response_news = None
            import time
            for attempt in range(3):
                try:
                    response_news = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_news,
                        config={"tools": [{"google_search": {}}]}
                    )
                    break
                except Exception as e:
                    if "429" in str(e):
                         print(f"[*] 429 su News, attendo 10 secondi (tentativo {attempt+1}/3)...")
                         time.sleep(10)
                    else:
                         raise e
            if not response_news:
                  bot.reply_to(message, "❌ Quota limit superata anche dopo i tentativi (News). Riprova tra un minuto.")
                  return"""

# Sostituiamo nel content
if target_block in content:
    content = content.replace(target_block, replacement_block)
    print("Backoff added to Prompt 1 successfully!")
else:
    # Se non lo trova per l'indentazione, usiamo un replace più lasco
    print("Target block Prompt 1 not found precisely. Search and Replace safely.")
    # Trova la riga response_news = ... e config=...
    # split marker strategy
    parts = content.split("response_news = client.models.generate_content(")
    if len(parts) > 1:
         before = parts[0]
         after = parts[1]
         sub_after = after.split("config={\"tools\": [{\"google_search\": {}}]}\n            )", 1)
         rest = sub_after[1]
         
         updated_content = before + """response_news = None
            import time
            for _attempt in range(3):
                try:
                    response_news = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_news,
                        config={"tools": [{"google_search": {}}]}
                    )
                    break
                except Exception as e:
                    if "429" in str(e):
                         time.sleep(10)
                    else:
                         raise e
            if not response_news:
                  bot.reply_to(message, "❌ Quota limit superata anche dopo i tentativi (News). Riprova tra un minuto.")
                  return""" + rest
         content = updated_content
         print("Backoff added via split strategy.")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

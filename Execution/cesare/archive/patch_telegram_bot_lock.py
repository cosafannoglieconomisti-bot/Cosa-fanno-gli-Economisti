import os

filepath = 'Execution/cesare/telegram_bot.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inserisci la variabile globale prima del handler
setup_block = """# ---------------------------------------------------------
# MESSAGE HANDLER: COMANDI GENERALI
# ---------------------------------------------------------
is_articoli_running = False # Lock anti-spam per /articoli
@bot.message_handler(func=lambda m: str(m.chat.id) == ALLOWED_ID)"""

content = content.replace("""# ---------------------------------------------------------
# MESSAGE HANDLER: COMANDI GENERALI
# ---------------------------------------------------------
@bot.message_handler(func=lambda m: str(m.chat.id) == ALLOWED_ID)""", setup_block)

# 2. Modifica il blocco /articoli per usare il lock
target_articoli = "elif user_msg_stripped == '/articoli':"

replacement_articoli = """elif user_msg_stripped == '/articoli':
        global is_articoli_running
        if is_articoli_running:
             bot.reply_to(message, "⏳ Una ricerca `/articoli` è già in corso. Attendi che finisca (operazione lenta) per evitare di esaurire la quota API.")
             return
             
        is_articoli_running = True
        try:
            bot.reply_to(message, "⏳ Ricerca 2 notizie hot in corso (Google Search)...")"""

# Sappiamo che dopo target_articoli c'è: bot.reply_to(message, "⏳ Ricerca 5 news..." o "⏳ Ricerca 2 notizie...")
# Sostituiamo solo la riga dell'elif e la prima riga di risposta per iniettare il blocco.
# In telegram_bot.py c'è:
# elif user_msg_stripped == '/articoli':
#         bot.reply_to(message, "⏳ Ricerca 5 notizie hot..." o "⏳ Ricerca 2 notizie hot...")

import re
content = re.sub(r"elif user_msg_stripped == '/articoli':\s*bot\.reply_to\(message, \"⏳ Ricerca .* notizie hot in corso.*\"\)", replacement_articoli, content)

# 3. Aggiungi il finally prima del return per sbloccare la variabile
target_end = """        except Exception as e:
             bot.reply_to(message, f"❌ Errore Chaining/Verifica del report: {e}")
        return"""

replacement_end = """        except Exception as e:
             bot.reply_to(message, f"❌ Errore Chaining/Verifica del report: {e}")
        finally:
             global is_articoli_running
             is_articoli_running = False
        return"""

content = content.replace(target_end, replacement_end)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Lock added successfully to prevent rate limits from spam triggers!")

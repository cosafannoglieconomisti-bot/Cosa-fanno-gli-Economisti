import os

filepath = 'Execution/cesare/telegram_bot.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Rimuovi la variabile booleana e inserisci il Lock
content = content.replace("is_articoli_running = False # Lock anti-spam per /articoli", "articoli_lock = threading.Lock()  # Lock atomico per /articoli")

# 2. Modifica la gestione del lock all'entrata del comando
old_entry_block = """elif user_msg_stripped == '/articoli':
        global is_articoli_running
        if is_articoli_running:
             bot.reply_to(message, "⏳ Una ricerca `/articoli` è già in corso. Attendi che finisca per evitare di esaurire la quota API.")
             return
             
        is_articoli_running = True
        bot.reply_to(message, "⏳ Ricerca notizie e articoli accademici in corso (1 singola richiesta per salvaguardare la quota API)...")"""

new_entry_block = """elif user_msg_stripped == '/articoli':
        if articoli_lock.locked():
             bot.reply_to(message, "⏳ Una ricerca `/articoli` è già in corso. Attendi che finisca per evitare di esaurire la quota API.")
             return
             
        # Eseguiamo il blocco in un thread-lock atomico
        with articoli_lock:
             bot.reply_to(message, "⏳ Ricerca notizie e articoli accademici in corso (1 singola richiesta per salvaguardare la quota API)...")"""

if old_entry_block in content:
    content = content.replace(old_entry_block, new_entry_block)
    print("Locked entry updated successfully!")
else:
    print("Warning: old_entry_block not found precisely with spacing. Using relative splits.")

# 3. Rimuovi is_articoli_running dal blocco finally che avevamo aggiunto
old_finally = """        except Exception as e:
             bot.reply_to(message, f"❌ Errore Singolo/Verifica del report: {e}")
        finally:
             is_articoli_running = False
        return"""

new_finally = """        except Exception as e:
             bot.reply_to(message, f"❌ Errore Singolo/Verifica del report: {e}")
        return"""

content = content.replace(old_finally, new_finally)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Thread Lock added successfully to prevent race condition parallel executions!")

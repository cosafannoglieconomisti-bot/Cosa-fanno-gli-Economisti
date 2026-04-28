import os
import telebot

def load_env_manual(path):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

# Carica il file .env
env_path = "/Users/marcolemoglie_1_2/Desktop/canale/.env"
load_env_manual(env_path)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
ALLOWED_ID = os.environ.get("ALLOWED_ID") or os.environ.get("ALLOWED_CHAT_ID")

if not TOKEN or not ALLOWED_ID:
    print("Errore: Credenziali mancanti.")
    exit(1)

bot = telebot.TeleBot(TOKEN)
bot.send_message(ALLOWED_ID, "🤖 **Cesare: Aggiornamento applicato!**\\n\\nRiprova `/copertina` adesso. Se c'è un errore, il bot te lo scriverà in chiaro!")
print("Messaggio di ping inviato a Telegram!")

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
    print(f"Errore: Variabili TELEGRAM_TOKEN o ALLOWED_ID mancanti. Trovato TOKEN={TOKEN is not None}")
    exit(1)

bot = telebot.TeleBot(TOKEN)
img_path = "/Users/marcolemoglie_1_2/.gemini/antigravity/brain/0af43b21-861e-4e08-b0e0-47fcc2fd4d30/cover_v3_grouped_title_retry_1774393779129.png"

if os.path.exists(img_path):
    with open(img_path, 'rb') as f:
         bot.send_photo(ALLOWED_ID, f, caption="🖼️ **Ecco la copertina generata con il titolo esatto!**\n\nTi piace? Rispondi qui al prompt per approvarla o rifarla!")
    print("Copertina inviata a Telegram con successo!")
else:
    print(f"Errore: Immagine non trovata in {img_path}")

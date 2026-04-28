import os
import sys
import telebot
from datetime import datetime
from dotenv import load_dotenv

# Configurazione
BASE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale"
load_dotenv(os.path.join(BASE_DIR, ".env"))
TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_ID = os.getenv("ALLOWED_CHAT_ID")
BRIDGE_LOG = os.path.join(BASE_DIR, "Temp/cesare/telegram_bridge.log")

def log_response(text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] Antigravity (IA): {text}\n"
    try:
        with open(BRIDGE_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"⚠️ Errore logging bridge: {e}")

def send_message(text):
    if not TOKEN or not ALLOWED_ID:
        print("❌ Errore: Variabili TELEGRAM_TOKEN o ALLOWED_CHAT_ID mancanti.")
        return False
    
    try:
        bot = telebot.TeleBot(TOKEN)
        
        # Gestione split messaggi lunghi (> 4096 char)
        if len(text) > 4000:
            chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                bot.send_message(ALLOWED_ID, chunk, parse_mode="HTML")
        else:
            bot.send_message(ALLOWED_ID, text, parse_mode="HTML")
            
        log_response(text)
        print(f"✅ Messaggio inviato e loggato: {text[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Errore invio Telegram: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 bridge_send.py 'messaggio'")
    else:
        msg = " ".join(sys.argv[1:])
        send_message(msg)

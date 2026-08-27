from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import os
import telebot
from dotenv import load_dotenv

load_dotenv(str(REPO_ROOT / '.env'))
TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_ID = os.getenv("ALLOWED_CHAT_ID")

bot = telebot.TeleBot(TOKEN)
try:
    with open(str(REPO_ROOT / 'Temp' / 'ulisse' / 'test_send.txt'), 'w') as f:
        f.write('Test file content')
    
    with open(str(REPO_ROOT / 'Temp' / 'ulisse' / 'test_send.txt'), 'rb') as doc:
        bot.send_document(ALLOWED_ID, doc, caption="Test bot connectivity")
    print("SUCCESS")
except Exception as e:
    print(f"FAILURE: {e}")

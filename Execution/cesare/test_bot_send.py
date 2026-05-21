import os
import telebot
from dotenv import load_dotenv

load_dotenv('/Users/marcolemoglie_1_2/Desktop/canale/.env')
TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_ID = os.getenv("ALLOWED_CHAT_ID")

bot = telebot.TeleBot(TOKEN)
try:
    with open('/Users/marcolemoglie_1_2/Desktop/canale/Temp/ulisse/test_send.txt', 'w') as f:
        f.write('Test file content')
    
    with open('/Users/marcolemoglie_1_2/Desktop/canale/Temp/ulisse/test_send.txt', 'rb') as doc:
        bot.send_document(ALLOWED_ID, doc, caption="Test bot connectivity")
    print("SUCCESS")
except Exception as e:
    print(f"FAILURE: {e}")

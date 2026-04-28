import os
import time
import subprocess
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY mancante")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

ALLOWED_JOURNALS = [
    "Nature", "Science", "PNAS", "AER", "American Economic Review", 
    "QJE", "Quarterly Journal of Economics", "JPE", "Journal of Political Economy", 
    "Econometrica", "REStud", "REStat", "JEEA", "EJ", "AEJ", "JPubE", "JDE"
]

prompt_articoli_single = """Sei Ulisse/Articoli. Cerca le **2 notizie** più importanti di oggi in Italia (usa ANSA o Repubblica).
Per ciascuna notizia, proponi **3 articoli accademici correlati** da riviste economiche prestigiose (dal 2000 ad oggi).

⚠️ **IMPORTANTE**: Rispondi **ESCLUSIVAMENTE** in questo formato testuale (un blocco per notizia):

ARGOMENTO: [Titolo News]
DESCRIZIONE: [Breve sintesi della news in due frasi]
CANDIDATI:
1. [Titolo Paper] | [Autori] | [Journal] | [Perché l'articolo è legato alla news]
2. [Titolo Paper] | [Autori] | [Journal] | [Perché l'articolo è legato alla news]
3. [Titolo Paper] | [Autori] | [Journal] | [Perché l'articolo è legato alla news]
---
"""

print("[*] Esecuzione chiamata Gemini con Grounding...")
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_articoli_single,
        config={"tools": [{"google_search": {}}]}
    )
    print("✅ Risposta ricevuta!")
    print(response.text[:1000] + "...")
except Exception as e:
    print(f"❌ Errore: {e}")

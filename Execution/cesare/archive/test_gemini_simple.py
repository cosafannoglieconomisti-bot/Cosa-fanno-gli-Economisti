import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

prompt_articoli_simple = """
Sei Ulisse/Articoli, l'agente dedicato alla ricerca dei temi "hot" dalle news e al matching con la letteratura accademica per il canale 'Cosa fanno gli economisti'.

COMPITO:
1. Cerca le 5 notizie (hot topics) più importanti di oggi in Italia (usa ANSA, Corriere, Repubblica o fonti attendibili).
2. Per ciascuna notizia, trova 3 articoli accademici correlati (con titolo e autori) dal 2000 ad oggi che siano un match da riviste di Economia o Scienze Politiche prestigiose.

RISPOSTA:
Rispondi in formato testo libero (bullet points), separando chiaramente ciascun argomento con una riga vuota.
Esempio:
---
ARGOMENTO: [Sintesi News]
FONTE: [Link/Nome]
PAPER 1: [Titolo] | [Autori] | [Journal]
PAPER 2: [Titolo] | [Autori] | [Journal]
PAPER 3: [Titolo] | [Autori] | [Journal]
---
"""

try:
    print("Inviando richiesta SIMPLE a Gemini...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_articoli_simple,
        config={
            "tools": [{"google_search": {}}]
        }
    )
    print("✅ Successo SIMPLE!")
    print(response.text)
except Exception as e:
    print(f"❌ Errore SIMPLE: {e}")

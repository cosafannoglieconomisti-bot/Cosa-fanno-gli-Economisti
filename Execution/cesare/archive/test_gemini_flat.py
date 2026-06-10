import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

prompt_articoli_flat = """
Sei Ulisse/Articoli, l'agente dedicato alla ricerca dei temi "hot" dalle news e al matching con la letteratura accademica.

COMPITO:
1. Cerca le 5 notizie (hot topics) più importanti di oggi in Italia (usa ANSA, Corriere, Repubblica o fonti attendibili).
2. Per ciascuna notizia, trova 3 articoli accademici correlati (con titolo e autori) dal 2000 ad oggi che siano un match.

⚠️ **MANDATORIO: RESTRIZIONE JOURNAL** ⚠️
Devi selezionare articoli **ESCLUSIVAMENTE** dalle seguenti riviste scientifiche:
- **Top Generalist**: Nature, Science, PNAS.
- **Top 5 Economics**: AER, QJE, JPE, Econometrica, REStud.
- **Top Economics**: REStat, JEEA, EJ, AEJ: Applied, AEJ: Policy, JPubE, JDE, JOLE, JHR, JFE, JME.
- **Top Science/Political**: APSR, AJPS, JOP.

**NON proporre articoli fuori da questo elenco.**

RISPOSTA:
Rispondi in formato testo libero (bullet points), separando chiaramente ciascun argomento con una riga vuota.
Esempio:
---
ARGOMENTO: [Sintesi News]
FONTE: [Link/Nome]
PAPER 1: [Titolo] | [Autori]
PAPER 2: [Titolo] | [Autori]
PAPER 3: [Titolo] | [Autori]
---
"""

try:
    print("Inviando richiesta FLAT a Gemini...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_articoli_flat,
        config={
            "tools": [{"google_search": {}}]
        }
    )
    print("✅ Successo FLAT!")
    print(response.text)
except Exception as e:
    print(f"❌ Errore FLAT: {e}")

import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Manca GEMINI_API_KEY")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

prompt_articoli = """
Sei Ulisse/Articoli, l'agente dedicato alla ricerca dei temi "hot" dalle news e al matching con la letteratura accademica per il canale 'Cosa fanno gli economisti'.

COMPITO:
1. Cerca le 5 notizie (hot topics) più importanti di oggi in Italia (usa ANSA, Corriere, Repubblica o fonti attendibili).
2. Per ciascuna notizia, trova 3 articoli accademici correlati (con titolo e autori) dal 2000 ad oggi che siano un match.

⚠️ **MANDATORIO: RESTRIZIONE JOURNAL** ⚠️
Devi selezionare articoli **ESCLUSIVAMENTE** dalle seguenti riviste scientifiche:
- **Top Generalist**: Nature, Science, PNAS.
- **Top 5 Economics**: AER (American Economic Review), QJE (Quarterly Journal of Economics), JPE (Journal of Political Economy), Econometrica, REStud (Review of Economic Studies).
- **Top Economics (High Prestige)**: REStat (Review of Economics and Statistics), JEEA (Journal of the European Economic Association), EJ (Economic Journal), AEJ: Applied, AEJ: Policy.
- **Top Field Economics**: JPubE (Journal of Public Economics), JDE (Journal of Development Economics), JOLE (Journal of Labor Economics), JHR (Journal of Human Resources), JFE (Journal of Financial Economics), JME (Journal of Monetary Economics).
- **Top Science/Political**: APSR, AJPS, JOP.

**NON proporre articoli fuori da questo elenco.** Se non trovi un match forte in queste testate, lascia l'array "papers" vuoto per quel topic.

RISPOSTA:
Ritorna SOLO un array JSON strutturato in questo modo, senza alcun markdown o testo di contorno (solo il JSON):
[
  {
    "topic": "Sintesi della news...",
    "source": "Ansa/Corriere...",
    "papers": [
      {"title": "Titolo Articolo 1", "authors": "Autori"},
      {"title": "Titolo Articolo 2", "authors": "Autori"},
      {"title": "Titolo Articolo 3", "authors": "Autori"}
    ]
  }
]
"""

try:
    print("Inviando richiesta a Gemini...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_articoli,
        config={
            "tools": [{"google_search": {}}]
        }
    )
    print("✅ Successo!")
    print(response.text)
except Exception as e:
    print(f"❌ Errore: {e}")

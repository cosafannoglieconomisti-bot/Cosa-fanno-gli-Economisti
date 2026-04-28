import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def run_chaining_test():
    # 1. Cerca le news (Grounding abilitato)
    prompt_news = "Sei un giornalista italiano. Cerca le 5 notizie (hot topics) più importanti di oggi in Italia (usa ANSA o Repubblica). Ritorna solo un elenco numerato."
    
    try:
        print("1. Recupero 5 notizie (Grounding)...")
        res_news = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_news,
            config={"tools": [{"google_search": {}}]}
        )
        print("✅ Notizie recuperate:")
        print(res_news.text)
        
        topics = [line.strip() for line in res_news.text.split('\n') if line.strip() and line[0].isdigit()]
        
        for i, topic in enumerate(topics[:5], 1):
             print(f"\n2. Ricerca Paper per Topic {i}: {topic}...")
             prompt_paper = f"""
             Sei un ricercatore di Economia. Trova 3 articoli accademici correlati a questo tema: "{topic}"
             da riviste prestigiose (AER, QJE, Nature) dal 2000 ad oggi.
             Rispondi solo con: Titolo | Autori | Journal
             """
             res_paper = client.models.generate_content(
                 model='gemini-2.5-flash',
                 contents=prompt_paper,
                 # Grounding NON strettamente necessario per la ricerca di paper storici/database generici, 
                 # ma possiamo lasciarlo disabilitato o abilitato. Proviamo DISABILITATO.
             )
             print(f"✅ Risposta:")
             print(res_paper.text)
             
    except Exception as e:
        print(f"❌ Errore Chaining: {e}")

if __name__ == '__main__':
    run_chaining_test()

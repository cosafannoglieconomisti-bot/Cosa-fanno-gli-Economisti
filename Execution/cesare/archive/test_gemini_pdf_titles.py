import fitz
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def get_bundle_titles(pdf_paths):
    context = "Questi sono i contenuti iniziali di alcuni paper. Per ciascuno, identifica il titolo accademico effettivo (es. 'How the West Invented Fertility Restriction').\n\n"
    
    for path in pdf_paths:
        try:
            doc = fitz.open(path)
            # Leggi i primi 1000 caratteri di testo
            page = doc[0]
            text = page.get_text()[:1000]
            context += f"--- FILE: {os.path.basename(path)} ---\n{text}\n\n"
        except Exception as e:
            context += f"--- FILE: {os.path.basename(path)} ---\n[Errore di lettura: {e}]\n\n"
            
    prompt = context + "\nRispondi esclusivamente con un elenco nel formato 'FILENAME: TITOLO', una riga per file. Non aggiungere altro."
    
    try:
         response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
         print(f"\n--- RAW GEMINI OUTPUT ---\n{response.text}\n--- END RAW ---\n")
         lines = response.text.split('\n')
         titles_map = {}
         for line in lines:
              if ':' in line:
                    parts = line.split(':', 1)
                    file_name = parts[0].strip()
                    title = parts[1].strip()
                    titles_map[file_name] = title
         return titles_map
    except Exception as e:
         print(f"Errore Gemini: {e}")
         return {}

full_path = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare"
pdfs = [os.path.join(full_path, f) for f in os.listdir(full_path) if f.endswith(".pdf")]

map_titles = get_bundle_titles(pdfs)
for k, v in map_titles.items():
    print(f"{k} => {v}")

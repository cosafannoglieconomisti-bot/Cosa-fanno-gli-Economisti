import os
import sys
import time
from google import genai
from dotenv import load_dotenv

load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def translate_metadata(input_path, output_dir, target_langs):
    if not GEMINI_API_KEY:
        print("❌ API Key non trovata.")
        return False

    with open(input_path, 'r', encoding='utf-8') as f:
        it_content = f.read()

    # Estrazione Titolo e Descrizione originali (IT)
    it_title = it_content.split('\n')[0].split('-', 1)[1].strip()
    it_desc = it_content.split("## Descrizione YouTube")[1].split("##")[0].strip()

    client = genai.Client(api_key=GEMINI_API_KEY)

    for lang in target_langs:
        print(f"🌍 Traduzione Metadati in {lang}...")
        
        prompt = f"""You are a professional translator and YouTube expert.
        Translate the following YouTube Title and Description from Italian to {lang.upper()}.
        
        MANDATORY RULES:
        1. Keep the same meaning and professional-academic yet catchy tone.
        2. DO NOT translate the names of the authors, journals, or DOI links.
        3. Keep the same structure (Description, then the info section).
        4. TRANSLATE the catchy chapter titles in the Index section too.
        5. Output ONLY a valid Markdown content in the following format:
        
        # Metadati Video - [Translated Title] ({lang.upper()})
        
        ## Descrizione YouTube
        [Translated Description]
        
        TITLE TO TRANSLATE:
        {it_title}
        
        DESCRIPTION TO TRANSLATE:
        {it_desc}
        """

        success = False
        for attempt in range(5):
            try:
                response = client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=prompt
                )
                if response and response.text:
                    translated_content = response.text.strip().replace('```markdown', '').replace('```', '')
                    
                    lang_dir = os.path.join(output_dir, lang)
                    os.makedirs(lang_dir, exist_ok=True)
                    out_path = os.path.join(lang_dir, f"metadata_{lang}.md")
                    
                    with open(out_path, 'w', encoding='utf-8') as f_out:
                        f_out.write(translated_content)
                    
                    print(f"✅ Metadati {lang} salvati in {out_path}")
                    success = True
                    break
                else:
                    print(f"⚠️ Risposta vuota per {lang}, riprovo...")
            except Exception as e:
                print(f"❌ Errore durante traduzione {lang}: {e}. Riprovo in 15s...")
                time.sleep(15)
        
        if not success:
            print(f"⛔ Fallita traduzione definitiva per {lang}")

    return True

if __name__ == "__main__":
    # Esempio: python translate_metadata.py video_metadata.md international/
    input_file = sys.argv[1]
    out_root = sys.argv[2]
    langs = ["en", "es", "fr", "de"]
    translate_metadata(input_file, out_root, langs)

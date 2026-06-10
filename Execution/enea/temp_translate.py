import os
import sys
import time
from google import genai
from dotenv import load_dotenv

load_dotenv("/Users/<USER>/Desktop/canale/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def translate_metadata(input_path, output_dir, target_langs):
    with open(input_path, 'r', encoding='utf-8') as f:
        it_content = f.read()

    it_title = it_content.split('\n')[0].split('-', 1)[1].strip()
    it_desc = it_content.split("## Descrizione YouTube")[1].split("##")[0].strip()

    client = genai.Client(api_key=GEMINI_API_KEY)

    for lang in target_langs:
        print(f"Traduzione in {lang}...")
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

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            translated_content = response.text.strip().replace('```markdown', '').replace('```', '')
            
            lang_dir = os.path.join(output_dir, lang)
            os.makedirs(lang_dir, exist_ok=True)
            out_path = os.path.join(lang_dir, f"metadata_{lang}.md")
            
            with open(out_path, 'w', encoding='utf-8') as f_out:
                f_out.write(translated_content)
            print(f"Salvato {out_path}")
            time.sleep(10)
        except Exception as e:
            print(f"Errore {lang}: {e}")

if __name__ == "__main__":
    translate_metadata(sys.argv[1], sys.argv[2], ["es", "fr", "de"])

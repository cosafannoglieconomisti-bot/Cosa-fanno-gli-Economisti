import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)

def translate_text(text, target_lang):
    if not text: return ""
    client = get_client()
    prompt = f"""You are a professional social media manager and translator. 
    Translate the following YouTube video description into {target_lang}.
    
    RULES:
    1. Keep the same structure, emojis, and links.
    2. Maintain the catchy, divulgative tone.
    3. Translate the title, main description, and table of contents.
    4. Output ONLY the translated text.
    5. Do NOT include markdown blocks like ```markdown.

    TEXT TO TRANSLATE:
    {text}
    """
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-flash-latest', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    safety_settings=[types.SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='OFF')]
                )
            )
            if response and response.text:
                return response.text.strip().replace('```markdown', '').replace('```', '')
        except Exception as e:
            print(f"Error translating to {target_lang}: {e}")
            time.sleep(5)
    return ""

def harmonize_mafia():
    project_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Perche_scacciare_la_Mafia_paga"
    intl_path = os.path.join(project_path, "international")
    langs = ["en", "es", "fr", "de"]
    
    for lang in langs:
        json_path = os.path.join(intl_path, lang, f"metadata_{lang}.json")
        md_path = os.path.join(intl_path, lang, f"metadata_{lang}.md")
        
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(data.get("description", ""))
            print(f"✅ Mafia: Created {md_path}")

def harmonize_integrazione():
    project_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/La_Chiesa_frena_l_integrazione"
    main_md = os.path.join(project_path, "video_metadata.md")
    intl_path = os.path.join(project_path, "international")
    langs = ["en", "es", "fr", "de"]
    
    if not os.path.exists(main_md): return
    
    with open(main_md, "r", encoding="utf-8") as f:
        it_content = f.read()

    for lang in langs:
        print(f"🌍 Translating Integrazione to {lang}...")
        translated = translate_text(it_content, lang)
        if not translated: continue
        
        lang_dir = os.path.join(intl_path, lang)
        os.makedirs(lang_dir, exist_ok=True)
        
        # Save .md
        md_path = os.path.join(lang_dir, f"metadata_{lang}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(translated)
            
        # Extract title (first line)
        lines = translated.split("\n")
        title = lines[0].replace("# ", "").strip()
        
        # Save .json
        json_path = os.path.join(lang_dir, f"metadata_{lang}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"title": title, "description": translated}, f, indent=4)
            
        print(f"✅ Integrazione: Created metadata files for {lang}")

if __name__ == "__main__":
    harmonize_mafia()
    harmonize_integrazione()

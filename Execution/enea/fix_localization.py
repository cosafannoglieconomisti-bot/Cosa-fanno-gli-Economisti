import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def translate_content(text, target_lang):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""Translate this YouTube metadata from Italian to {target_lang}. 
    Preserve the structure, especially the INDICE CONTENUTI and timestamps. 
    TRANSLATE the catchy titles of the chapters. 
    DO NOT translate author names (Goldin, Rouse, Michalopoulos, etc.), journals (AER, QJE, etc.) or DOI links. 
    Preserve emojis.
    Output ONLY the markdown content.
    
    CONTENT:
    {text}
    """
    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        return response.text.strip().replace('```markdown', '').replace('```', '')
    except Exception as e:
        print(f"Error translating to {target_lang}: {e}")
        return None

def fix_localization(project_folder):
    print(f"--- Auditing {project_folder} ---")
    it_metadata_path = os.path.join(project_folder, "video_metadata.md")
    if not os.path.exists(it_metadata_path):
        print(f"Error: video_metadata.md not found in {project_folder}")
        return

    with open(it_metadata_path, 'r', encoding='utf-8') as f:
        it_content = f.read()

    target_langs = ["en", "es", "fr", "de"]
    intl_dir = os.path.join(project_folder, "international")
    
    # Check for IT metadata in IT folder (SOP requirement)
    it_dir = os.path.join(intl_dir, "it")
    os.makedirs(it_dir, exist_ok=True)
    it_md_target = os.path.join(it_dir, "metadata_it.md")
    if not os.path.exists(it_md_target):
        with open(it_md_target, 'w', encoding='utf-8') as f:
            f.write(it_content)
        print(f"✅ Created metadata_it.md in {it_dir}")

    for lang in target_langs:
        lang_dir = os.path.join(intl_dir, lang)
        os.makedirs(lang_dir, exist_ok=True)
        md_path = os.path.join(lang_dir, f"metadata_{lang}.md")
        
        if not os.path.exists(md_path) or "Il_Talento_Non_Ha_Genere" in project_folder:
            print(f"Generating translation for {lang}...")
            translation = translate_content(it_content, lang)
            if translation:
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(translation)
                print(f"✅ Saved metadata_{lang}.md")

if __name__ == "__main__":
    projects = [
        "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Il_Talento_Non_Ha_Genere",
        "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Perche_scacciare_la_Mafia_paga",
        "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/La_Chiesa_frena_l_integrazione"
    ]
    for p in projects:
        fix_localization(p)

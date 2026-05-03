import os
import sys
import time
from google import genai
from dotenv import load_dotenv

load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PROJECTS = [
    "Dalle_Guerre_ai_Capolavori",
    "Regolarizzare_gli_immigrati_riduce_il_crimine",
    "Il_Talento_Non_Ha_Genere",
    "Il_Pallone_Unisce_le_Nazioni"
]

LANGS = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German"
}

def translate_metadata(project_name):
    it_md = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Cleaned", project_name, "video_metadata.md")
    if not os.path.exists(it_md):
        print(f"❌ IT Metadata not found for {project_name}")
        return

    with open(it_md, "r", encoding="utf-8") as f:
        it_content = f.read()

    for lang_code, lang_name in LANGS.items():
        out_path = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Cleaned", project_name, "international", lang_code, f"metadata_{lang_code}.md")
        if os.path.exists(out_path):
            print(f"⏩ {project_name} {lang_code} already exists.")
            continue

        print(f"🌍 Translating {project_name} metadata to {lang_name}...")
        
        prompt = f"""You are a professional translator and YouTube SEO expert.
        Take the following Italian YouTube video metadata and translate it into {lang_name}.
        
        INPUT CONTENT:
        {it_content}
        
        RULES:
        1. Output ONLY a markdown file in this exact format:
        # Video Metadata - [Translated catchy title] ({lang_code.upper()})
        
        ## Description
        [Translated SEO-friendly description including study details, DOI link, etc.]
        
        2. Keep the links and tags intact (translate the meaning of tags if possible, but keep the # symbol).
        3. Do NOT include any intro/outro or markdown code blocks (no ```markdown).
        4. Focus on making the title catchy and the description professional.
        """

        client = genai.Client(api_key=GEMINI_API_KEY)
        success = False
        for attempt in range(3):
            try:
                from google.genai import types
                response = client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=prompt
                )
                if response and response.text:
                    translated_content = response.text.strip().replace('```markdown', '').replace('```', '')
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, "w", encoding="utf-8") as f_out:
                        f_out.write(translated_content)
                    print(f"✅ Saved metadata_{lang_code}.md")
                    success = True
                    break
                time.sleep(5)
            except Exception as e:
                print(f"⚠️ Error: {e}")
                time.sleep(5)
        
        if not success:
            print(f"❌ Failed to translate {project_name} to {lang_name}")
        
        time.sleep(2) # Throttle

if __name__ == "__main__":
    for p in PROJECTS:
        translate_metadata(p)

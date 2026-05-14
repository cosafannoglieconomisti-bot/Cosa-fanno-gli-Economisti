import os
import sys
import json
import time
from google import genai
from dotenv import load_dotenv

load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
print("DEBUG: Script loading...", flush=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"DEBUG: API Key loaded: {'Yes' if GEMINI_API_KEY else 'No'}", flush=True)

def translate_srt(input_path, output_path, target_lang):
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found in .env")
        return False

    if not os.path.exists(input_path):
        print(f"❌ Error: File not found {input_path}")
        return False

    print(f"🌍 Translating {input_path} to {target_lang}...")
    
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # No chunking needed for small SRT files (Gemini Flash has 1M context)
    prompt = f"""You are a professional translator. Translate the following SRT subtitle file into {target_lang}.
    MANDATORY RULES:
    1. Keep the exact same SRT structure (Index, Timestamp, Text).
    2. DO NOT change the timestamps or indices.
    3. Translate ONLY the text part (Italian -> {target_lang}).
    4. Maintain the exact same number of blocks as the input.
    5. Output ONLY the translated SRT content.
    6. Do NOT include any markdown code blocks (no ```srt).

    CONTENT TO TRANSLATE:
    {content}
    """

    success = False
    client = genai.Client(api_key=GEMINI_API_KEY)
    delay = 10  # Start with 10s delay if it fails
    
    for attempt in range(7): # Increased to 7 attempts
        try:
            print(f"📡 Sending whole file to Gemini ({target_lang}, Attempt {attempt+1})...", flush=True)
            from google.genai import types
            response = client.models.generate_content(
                model='gemini-flash-latest', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    safety_settings=[
                        types.SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='OFF'),
                        types.SafetySetting(category='HARM_CATEGORY_DANGEROUS_CONTENT', threshold='OFF'),
                        types.SafetySetting(category='HARM_CATEGORY_HARASSMENT', threshold='OFF'),
                        types.SafetySetting(category='HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold='OFF'),
                    ]
                )
            )
            
            if response and response.text:
                resp_text = response.text.strip().replace('```srt', '').replace('```', '')
                translated_content = resp_text
                print(f"✅ Received translation for {target_lang}", flush=True)
                success = True
                break
            else:
                print(f"⚠️ Empty response or safety block for {target_lang}. Sleeping {delay}s...", flush=True)
                time.sleep(delay)
                delay *= 2
        except Exception as e:
            if "429" in str(e) or "503" in str(e) or "quota" in str(e).lower():
                print(f"⚠️ API LOAD ERROR (429/503) for {target_lang}. Sleeping {delay}s...", flush=True)
                time.sleep(delay)
                delay *= 2
            else:
                print(f"❌ Error during translation ({target_lang}, attempt {attempt+1}): {e}", flush=True)
                time.sleep(5)
    
    if not success:
        print(f"⛔ CRITICAL: Failed to translate {target_lang}")
        return False

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(translated_content)
    
    print(f"🎉 SUCCESS: {target_lang} SRT saved to {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python translate_srt.py <input.srt> <output.srt> <target_language>")
        sys.exit(1)
    
    inp, out, lang = sys.argv[1], sys.argv[2], sys.argv[3]
    success = translate_srt(inp, out, lang)
    if not success:
        sys.exit(1)

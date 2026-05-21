import os
import sys
from google import genai
from dotenv import load_dotenv

# Try both locations for .env
load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def main():
    if not GEMINI_API_KEY:
        print("❌ Error: API Key not found")
        return

    client = genai.Client(api_key=GEMINI_API_KEY)
    input_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Amore_o_documenti_La_verita/international/subtitles_it.srt"
    output_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Amore_o_documenti_La_verita/international/subtitles_en.srt"
    
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"🌍 Translating to EN using gemini-2.0-flash...")
    prompt = f"Translate the following SRT file to English. Keep structure, timestamps, and indices. Output ONLY the SRT content.\n\n{content}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        if response and response.text:
            translated = response.text.strip().replace('```srt', '').replace('```', '')
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(translated)
            print(f"✅ Success: Saved to {output_path}")
        else:
            print("❌ Empty response")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

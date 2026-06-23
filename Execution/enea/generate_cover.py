import os, sys, json, time, random
from google import genai
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv("/Users/<USER>/Desktop/canale/.env")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ASSETS_DIR = "/Users/<USER>/Desktop/canale/Temp/assets"
OVERRIDE_PATH = os.path.join(ASSETS_DIR, "override_cover.png")

def generate_cover(title, output_path="/tmp/active_cover.png"):
    if os.path.exists(OVERRIDE_PATH):
        import shutil
        shutil.copy(OVERRIDE_PATH, output_path)
        print(f"🚀 [OVERRIDE] Usando copertina Premium dell'Assistente: {output_path}")
        return output_path

    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        try:
            context_prompt = f"""
            Describe a striking, high-contrast comic book cover illustration for the topic: '{title}'.
            Style: High-contrast comic, vibrant orange, black and white palette. 
            Focus on symbolic elements (e.g. historical figures, dramatic shadows, urban or social unrest).
            NO TEXT in the description. Max 15 words.
            """
            context_response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=context_prompt
            )
            context = context_response.text.strip()
            
            prompt = f"""
            A premium comic book cover illustration. Format: exactly Square 1:1.
            Palette: STRICTLY ONLY BLACK, ORANGE AND WHITE. You must use vibrant orange.
            Style: High-contrast comic book cover graphic novel style, bold ink shadows, halftone dots, dramatic lighting. 
            Subject: {context}. 
            Integrated Title Text: '{title.upper()}'. 
            The ONLY text allowed is EXACTLY '{title.upper()}'. The text MUST be natively integrated into the comic art itself (like a classic comic book masthead), NOT on a flat solid color block.
            The lettering must be bold, dynamic comic-book style text.
            CRITICAL: NO watermarks, NO barcodes, NO publisher logos, NO dates, NO extra words in corners. 
            Clean, professional graphic design.
            """
            
            print(f"[*] Tentativo Imagen 4.0 (Topic: {title})...")
            result = client.models.generate_images(
                model='imagen-4.0-fast-generate-001',
                prompt=prompt,
                config=dict(numberOfImages=1, aspectRatio="1:1", outputMimeType="image/png")
            )
            
            if result.generated_images:
                with open(output_path, 'wb') as f:
                    f.write(result.generated_images[0].image.image_bytes)
                
                # SOP: Enforce 1:1 and remove edge watermarks via slight center crop (Inpainting alternative)
                img = Image.open(output_path)
                w, h = img.size
                if w != 1024 or h != 1024:
                    img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
                
                # Crop 4% off the edges to remove barcodes/corner logos without using black boxes
                crop_margin = int(1024 * 0.04)
                img_cropped = img.crop((crop_margin, crop_margin, 1024 - crop_margin, 1024 - crop_margin))
                img_final = img_cropped.resize((1024, 1024), Image.Resampling.LANCZOS)
                img_final.save(output_path)
                
                print(f"✅ Successo Imagen (Cropped edges for watermark removal): {output_path}")
                return output_path
        except Exception as e:
            print(f"⚠️ Imagen Error: {e}")

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "TEST TITOLO"
    o = sys.argv[2] if len(sys.argv) > 2 else "/tmp/active_cover.png"
    generate_cover(t, o)

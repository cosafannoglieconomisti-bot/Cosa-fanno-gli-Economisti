import os
import sys
import json
import time
import random
from google import genai
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Carica .env dalla root del progetto
load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/.env")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ASSETS_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/assets"
OVERRIDE_PATH = os.path.join(ASSETS_DIR, "override_cover.png")

def generate_cover(title, output_path="/tmp/active_cover.png"):
    # --- 0. MECCANISMO DI OVERRIDE (ASSISTANT OVERDRIVE) ---
    # Se Antigravity ha generato una copertina perfetta, la usiamo subito.
    if os.path.exists(OVERRIDE_PATH):
        import shutil
        shutil.copy(OVERRIDE_PATH, output_path)
        # Non cancelliamo qui per permettere rigenerazioni se necessario, 
        # ma l'assistente lo farà dopo la conferma.
        print(f"🚀 [OVERRIDE] Usando copertina Premium dell'Assistente: {output_path}")
        return output_path

    # --- 1. TENTA LA GENERAZIONE NATIVA AI (IMAGEN 4.0) ---
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        try:
            # Recupero contesto artistico Breve
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
            
            # Prompt Imagen Potenziato
            prompt = f"""
            A premium comic book cover illustration. 
            Palette: STRICTLY ONLY BLACK, ORANGE AND WHITE. 
            Style: High-contrast comic book cover, bold ink shadows, dramatic lighting. 
            Subject: {context}. 
            Integrated Title Text: '{title.upper()}'. 
            The text must be part of the comic design, bold and impactful, using white or orange for maximum contrast.
            CRITICAL: NO watermarks, NO barcodes, NO price tags, NO volume numbers, NO editor logos, NO dates. 
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
                    f.write(result.generated_images[0].image_bytes)
                print(f"✅ Successo Imagen: {output_path}")
                return output_path
        except Exception as e:
            print(f"⚠️ Imagen Error: {e}")

    # --- 2. FALLBACK MINIMALISTA (NO TEMPLATE STATICI) ---
    print("[*] Fallback: Generazione Grafica Minimale...")
    # Crea un'immagine bianca/arancione con testo se Imagen fallisce
    img = Image.new('RGB', (1024, 1024), color=(255, 255, 255)) # Bianco fallback
    draw = ImageDraw.Draw(img)
    
    # Sfondo arancio parziale o pattern
    draw.rectangle([0, 0, 1024, 200], fill=(255, 140, 0)) # Header Arancio
    
    # Font IMPACT (Standard Mac)
    font_path = "/System/Library/Fonts/Supplemental/Impact.ttf"
    if not os.path.exists(font_path): font_path = "/System/Library/Fonts/Helvetica.ttc"
    
    import textwrap
    font_size = 140
    lines = textwrap.wrap(title.upper(), width=10)
    
    while font_size > 60:
        font = ImageFont.truetype(font_path, font_size)
        total_h = sum([draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1] + 20 for l in lines])
        if total_h < 850: break
        font_size -= 10

    y = (1024 - total_h) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
        x = (1024 - w) // 2
        draw.text((x+5, y+5), line, font=font, fill=(0,0,0,100)) # Shadow
        draw.text((x, y), line, font=font, fill=(0, 0, 0)) # Text
        y += h + 30

    img.save(output_path)
    return output_path

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "TEST TITOLO"
    o = sys.argv[2] if len(sys.argv) > 2 else "/tmp/active_cover.png"
    generate_cover(t, o)

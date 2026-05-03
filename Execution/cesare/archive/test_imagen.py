import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_cover(title):
    prompt = f"""Comic book style cover, orange and black monochrome color palette. High contrast. 
    An impactful illustration about the Black Plague (Peste Nera) shaping Europe's history. 
    Include the exact large text integrated inside the image: '{title}'. 
    The text must be integrated in the composition."""
    
    print(f"Generando copertina per: {title}...")
    try:
         result = client.models.generate_images(
              model='imagen-4.0-fast-generate-001',
              prompt=prompt,
              config=dict(
                   numberOfImages=1,
                   aspectRatio="16:9",
                   outputMimeType="image/png"
              )
         )
         for idx, generated_image in enumerate(result.generated_images):
              out_path = f"/tmp/test_cover_{idx}.png"
              with open(out_path, 'wb') as f:
                   f.write(generated_image.image_bytes)
              print(f"Salvata in {out_path}")
              return out_path
    except Exception as e:
         print(f"Errore Imagen: {e}")
         return None

generate_cover("La Peste Nera: Il Segreto")

import os
import glob
from PIL import Image

def resize_thumbnail():
    # Usa glob per evitare problemi di normalizzazione caratteri su Mac
    search_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/*citt*perdute*bronzo*2019"
    folders = glob.glob(search_path)
    
    if not folders:
        print("ERRORE: Cartella non trovata con glob.")
        return
        
    img_dir = folders[0]
    input_path = os.path.join(img_dir, "thumbnail.png")
    output_path = os.path.join(img_dir, "thumbnail_1280x720.png")

    if not os.path.exists(input_path):
        print(f"ERRORE: File non trovato a {input_path}")
        return

    # 1. Carica Immagine
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    print(f"Dimensione originale: {w}x{h}px")

    # 2. Ridimensiona a 720x720 (mantiene proporzioni quadrate, scala altezza)
    img_resized = img.resize((720, 720), Image.Resampling.LANCZOS)

    # 3. Crea Canvas Nero 1280x720 (Standard YouTube 16:9)
    # YouTube richiede 16:9 per il caricamento desktop corretto
    canvas = Image.new("RGBA", (1280, 720), (0, 0, 0, 255))

    # 4. Centra l'immagine nel canvas
    x_offset = (1280 - 720) // 2
    y_offset = 0
    canvas.paste(img_resized, (x_offset, y_offset), img_resized)

    # 5. Salva
    canvas.save(output_path, "PNG")
    print(f"Salvata copertina 1280x720: {output_path}")

if __name__ == "__main__":
    resize_thumbnail()

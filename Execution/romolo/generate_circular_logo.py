import os
from PIL import Image, ImageDraw

def process_logo_tight():
    input_path = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/Logo_canale_transparente.png"
    output_transparent = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/Logo_canale_tondo_trasparente.png"
    output = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/Logo_canale_tondo_nero.png"

    if not os.path.exists(input_path):
        print(f"ERRORE: File non trovato a {input_path}")
        return

    # 1. Carica Immagine
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size

    # 2. Trova il bounding box del cerchio Arancione
    # Scansioniamo per trovare i pixel arancioni (R elevato, G medio, B basso)
    pixels = img.load()
    x_min, y_min = width, height
    x_max, y_max = 0, 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # Condizione per identificare l'Arancione (es. Cerchio e Elementi)
            if r > 200 and 100 < g < 180 and b < 80:
                if x < x_min: x_min = x
                if x > x_max: x_max = x
                if y < y_min: y_min = y
                if y > y_max: y_max = y

    print(f"Bbox arancione trovato: x={x_min}-{x_max}, y={y_min}-{y_max}")

    # Escludiamo il caso in cui non trovi nulla
    if x_max <= x_min or y_max <= y_min:
        print("Parametri arancione non rilevati, uso dimensione intera.")
        x_min, y_min, x_max, y_max = 0, 0, width, height
    else:
        # Stringiamo di 2 pixel all'interno per eliminare qualsiasi residuo o sfumatura esterna
        x_min = x_min + 2
        y_min = y_min + 2
        x_max = x_max - 2
        y_max = y_max - 2

    # 3. Ritaglia l'immagine sul box dell'arancione (Rende il Cerchio aderente ai bordi)
    img_cropped = img.crop((x_min, y_min, x_max, y_max))
    c_width, c_height = img_cropped.size
    print(f"Dimensione ritagliata: {c_width}x{c_height}px")

    # 4. Crea Maschera Circolare che tocca perfettamente i bordi del nuovo ritaglio
    mask = Image.new("L", (c_width, c_height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, c_width, c_height), fill=255)

    # --- VERSION 1: TRASPARENTE FUORI ---
    # Creiamo un canvas totalmente trasparente
    img_transparent = Image.new("RGBA", (c_width, c_height), (0, 0, 0, 0))
    # Incolla l'immagine originale usando la maschera (mantiene trasparenza interna!)
    img_transparent.paste(img_cropped, (0, 0), mask)
    img_transparent.save(output_transparent, "PNG")
    print(f"Salvato trasparente: {output_transparent}")

    # --- VERSION 2: SFONDO NERO INTERNO ---
    black_bg = Image.new("RGBA", (c_width, c_height), (0, 0, 0, 255))
    
    # Rimuoviamo lo sfondo bianco/trasparente originale per metterlo su nero
    # Creiamo un frame pulito solo con gli elementi arancioni
    cropped_pixels = img_cropped.load()
    for y in range(c_height):
        for x in range(c_width):
            r, g, b, a = cropped_pixels[x, y]
            if r > 200 and g > 200 and b > 200: # Bianco
                cropped_pixels[x, y] = (0, 0, 0, 0) # Trasparente

    black_bg.paste(img_cropped, (0, 0), img_cropped)
    # Riapplica la maschera per assicurare bordi tondi
    black_bg.putalpha(mask)
    black_bg.save(output, "PNG")
    print(f"Salvato nero: {output}")

if __name__ == "__main__":
    process_logo_tight()

import os
import sys
from PIL import Image, ImageDraw

def clean_infographic(input_path, output_path=None):
    """
    Rimuove il watermark di NotebookLM nell'angolo in basso a destra seguendo la SOP 2.1.
    Copre il watermark con il colore di sfondo dominante del riquadro.
    """
    if not os.path.exists(input_path):
        print(f"Errore: File non trovato {input_path}")
        return False
        
    if output_path is None:
        output_path = input_path

    try:
        img = Image.open(input_path).convert("RGBA")
        w, h = img.size
        
        # Area watermark dinamica (basata sulla risoluzione)
        # NotebookLM watermark è circa il 4% della larghezza e 2% dell'altezza.
        # Ridotto per evitare di cancellare contenuti utili (SOP 2.1 Fix)
        box_w = int(w * 0.15)
        box_h = int(h * 0.014)

        
        # Analisi colore dominante appena sopra il watermark per consistenza
        sample_x = w - 5
        sample_y = h - box_h - 5
        if sample_y < 0: sample_y = 0
        
        bg_color = img.getpixel((sample_x, sample_y))
        
        draw = ImageDraw.Draw(img)
        # Disegna il rettangolo coprente (Bottom Right)
        # Spostato leggermente di 1px per coprire meglio il bordo
        draw.rectangle([w - box_w - 2, h - box_h - 2, w, h], fill=bg_color)
        
        # Salva (se PNG originario o converte in JPG se necessario, per ora teniamo PNG)
        img.save(output_path, "PNG")
        print(f"✅ Infografica pulita salvata in: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Errore durante la pulizia dell'infografica: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python clean_infographic.py <percorso_immagine> [percorso_output]")
    else:
        inp = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else None
        clean_infographic(inp, out)

import os
from PIL import Image, ImageDraw, ImageFont

mafia_bg = "/Users/marcolemoglie_1_2/.gemini/antigravity/brain/5bc8acda-cbd4-4b83-920f-32154964403a/mafia_inc_bg_retry_1774089277005.png"
mafia_out = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Mafia_Inc_restat_2021/thumbnail_v3.png"

arch_bg = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Le_città_perdute_dell_età_del_bronzo_qje_2019/thumbnail.png"
arch_out = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Le_città_perdute_dell_età_del_bronzo_qje_2019/thumbnail_v3.png"

font_path = "/System/Library/Fonts/Supplemental/Impact.ttf"

def draw_stroke_text(draw, x, y, text, font, fill_color, stroke_color=(0,0,0,255), thickness=5):
    # Drow stroke
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx*dx + dy*dy <= thickness*thickness:
                 draw.text((x + dx, y + dy), text, fill=stroke_color, font=font)
    # Draw top fill
    draw.text((x, y), text, fill=fill_color, font=font)

def process_mafia():
    if not os.path.exists(mafia_bg): return
    img = Image.open(mafia_bg).convert("RGBA")
    w, h = img.size

    # 1. Ritaglio Quadrato (Manteniamo l'altezza o larghezza minore)
    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    img_square = img.crop((left, top, left + size, top + size))
    print(f"Mafia Inc: Ritagliato a {size}x{size}")

    draw = ImageDraw.Draw(img_square)
    font_size = int(size / 11) # Dimensioni proporzionali
    font = ImageFont.truetype(font_path, font_size)

    # 2. Testo integrato
    draw_stroke_text(draw, 50, 40, "MAFIA INC.: COME", font, (255, 153, 0))
    draw_stroke_text(draw, 50, 40 + font_size + 10, "LA CRIMINALITA' INVESTE", font, (255, 153, 0))
    # Terza riga se serve
    draw_stroke_text(draw, 50, 40 + (font_size + 10)*2, "NELL'ECONOMIA LEGALE", font, (255, 153, 0))

    img_square.save(mafia_out, "PNG")
    print(f"Salvata Mafia v3: {mafia_out}")

def process_archeo():
    if not os.path.exists(arch_bg): return
    img = Image.open(arch_bg).convert("RGBA")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    font_size = int(w / 16) # Leggermente più piccolo per integrarsi
    font = ImageFont.truetype(font_path, font_size)

    # Aggiungiamo SOLO l'estensione del titolo integrata sotto "LE CITTÀ PERDUTE"
    # Ispezionando l'immagine, LE CITTÀ PERDUTE è in alto. Aggiungiamo sotto:
    draw_stroke_text(draw, (w - draw.textlength("DELL'ETA' DEL BRONZO", font=font))//2, 230, "DELL'ETA' DEL BRONZO", font, (255, 153, 0))

    img.save(arch_out, "PNG")
    print(f"Salvata Archeo v3: {arch_out}")

if __name__ == "__main__":
    process_mafia()
    process_archeo()

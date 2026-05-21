from PIL import Image, ImageDraw

def clean_mafia():
    # Mafia Inc image
    img_path = "/Users/marcolemoglie_1_2/.gemini/antigravity/brain/5bc8acda-cbd4-4b83-920f-32154964403a/mafia_inc_final_1774101368577.png"
    out_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Mafia_Inc_restat_2021/thumbnail_v4.png"
    img = Image.open(img_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # Bottom left "BLACK & ORANGE 15€ VOL 1"
    # It's at the very bottom left corner. Paint black.
    box_w = int(w * 0.16)
    box_h = int(h * 0.22)
    draw.rectangle([0, h - box_h, box_w, h], fill=(0, 0, 0, 255))
    
    # Bottom right "MAFIA COMICS"
    box_w2 = int(w * 0.15)
    box_h2 = int(h * 0.18)
    draw.rectangle([w - box_w2, h - box_h2, w, h], fill=(0, 0, 0, 255))
    
    img.save(out_path, "PNG")
    print(f"Salvata Mafia pulita: {out_path}")

def clean_archeo():
    # Archeologia image
    img_path = "/Users/marcolemoglie_1_2/.gemini/antigravity/brain/5bc8acda-cbd4-4b83-920f-32154964403a/archeologia_final_1774101386637.png"
    out_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Le_città_perdute_dell_età_del_bronzo_qje_2019/thumbnail_v4.png"
    img = Image.open(img_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # Top right "N. 1 | GENNAIO 2024"
    # Paint it using the black background color
    box_w = int(w * 0.35)
    box_h = int(h * 0.10)
    draw.rectangle([w - box_w, 0, w, box_h], fill=(0, 0, 0, 255))
    
    # Bottom left "SAGGISTICA A FUMETTI"
    # This sits on an orange or dark ground. We'll use a very dark color from the bottom left
    # or just black, since bottom edges are often dark. Let's paint black.
    box_w2 = int(w * 0.38)
    box_h2 = int(h * 0.08)
    # Just to be safe, grab color from just above the text
    bg_color = img.getpixel((int(w * 0.05), h - box_h2 - 10))
    draw.rectangle([0, h - box_h2, box_w2, h], fill=bg_color)
    
    img.save(out_path, "PNG")
    print(f"Salvata Archeo pulita: {out_path}")

clean_mafia()
clean_archeo()

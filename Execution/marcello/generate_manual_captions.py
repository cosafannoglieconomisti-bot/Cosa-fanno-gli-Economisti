import os

def load_video_data():
    mappings = {}
    base_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
    
    meta_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == "video_metadata.md":
                meta_files.append(os.path.join(root, file))
    
    for meta_file in meta_files:
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            title = ""
            desc = []
            in_desc = False
            for line in content.split('\n'):
                # Pulizia formato
                l = line.replace("**", "").replace("#", "").strip()
                l_lower = l.lower()
                
                if l_lower.startswith("titolo:") or l_lower.startswith("titolo "):
                    title = l.split(":", 1)[1].strip() if ":" in l else l.replace("Titolo", "").strip()
                elif l_lower.startswith("descrizione:") or l_lower == "descrizione":
                    in_desc = True
                    # Aggiunge il testo sulla stessa riga se esiste (es: Descrizione: Lo studio...)
                    parts = l.split(":", 1)
                    if len(parts) > 1 and parts[1].strip():
                        desc.append(parts[1].strip())
                elif in_desc:
                    # Triggers ferma-descrizione per evitare boilerplate di YouTube
                    stop_markers = ["⏰", "fonte", "iscriviti", "http", "thumbnail:", "video:", "schedule:", "tag", "---", "==="]
                    if any(marker in l_lower for marker in stop_markers):
                        in_desc = False
                        continue
                    
                    if l: # Evita righe vuote multiple
                        desc.append(l)

            if title and desc:
                key = title.upper().replace('?', '').replace('!', '')
                mappings[key] = {
                    "title": title,
                    "description": " ".join(desc).strip(),
                }
        except Exception as e:
             pass
             
    return mappings

def run():
    video_database = load_video_data()

    # Tutti i 16 video totali (incluso Barone Mocetti)
    links = {
        "QUANDO LE CITT": "https://www.youtube.com/watch?v=Tv4znJpN_tk",
        "MAFIA E SVILUPPO": "https://www.youtube.com/watch?v=wi8TmC6WRRo",
        "OSCURO DELLA TV": "https://www.youtube.com/watch?v=LIgZxg-CMWY",
        "I ROBOT": "https://www.youtube.com/watch?v=S0ZyZE65BgM",
        "LA CORRUZIONE": "https://www.youtube.com/watch?v=Fa27rfGRweY",
        "MAFIA INC": "https://www.youtube.com/watch?v=hSj0RytzsJQ",
        "TAGLIARE GLI AIUTI": "https://www.youtube.com/watch?v=Rcjwqblw9aI",
        "LA CICALA": "https://www.youtube.com/watch?v=06TeI4ehwBw",
        "ARCHEOLOGIA ECONOMICA": "https://www.youtube.com/watch?v=OfLZjHHVhuI",
        "STATO ED IL CRIMINE": "https://www.youtube.com/watch?v=K1mbkAwVfNI",
        "NOMI E DISCRIMINAZIONE": "https://www.youtube.com/watch?v=85M2SSwB3V8",
        "TERREMOTO": "https://www.youtube.com/watch?v=mkOByDD32Q4",
        "CLIENTELISMO": "https://www.youtube.com/watch?v=BEZV_qvJ3C0",
        "MOGANO INSANGUINATO": "https://www.youtube.com/watch?v=sDG-9Olw7Lg",
        "ISTITUZIONI N": "https://www.youtube.com/watch?v=zAwp-Sswzdw",
        "I RICCHI": "https://www.youtube.com/watch?v=7SeVerAABeg"  # Barone Mocetti
    }
    
    output_lines = ["=== 16 TESTI PER LE FOTO FACEBOOK (COPIA E INCOLLA) ===\n\n"]
    
    for k, v in links.items():
        selected_desc = ""
        for db_k, db_v in video_database.items():
            if k in db_k:
                selected_desc = db_v["description"]
                break
        
        if not selected_desc:
            selected_desc = f"[Descrizione non trovata, inserire manualmente] {k.title()}"
            
        full_text = f"--- {k} ---\n{selected_desc}\n\nLink al video: {v}\n\n"
        output_lines.append(full_text)
        output_lines.append("---------------------------------------------------------------------------------\n\n")

    out_path = "/Users/marcolemoglie_1_2/Desktop/TESTI_FACEBOOK_DA_COPIARE.txt"
    with open(out_path, "w", encoding='utf-8') as f:
        f.writelines(output_lines)
        
    print(f"Generato con successo in {out_path}")

if __name__ == "__main__":
    run()

import os
import shutil
import json
from datetime import datetime

# Config
BASE_DIR = "/Users/<USER>/Desktop/canale"
CLEANED_DIR = os.path.join(BASE_DIR, "Cleaned")
PAPERS_DIR = os.path.join(BASE_DIR, "Papers/Da fare")
TRACKING_FILE = os.path.join(CLEANED_DIR, "video_tracking.json")
PIPELINE_FILE = os.path.join(BASE_DIR, "active_pipeline.json")

title_scelto = "Mafia ed elezioni: come funziona?"
folder_name = "Mafia_ed_elezioni_come_funziona"
target_dir = os.path.join(CLEANED_DIR, folder_name)

os.makedirs(target_dir, exist_ok=True)

# 1. Sposta e Rinomina il PDF
src_pdf = os.path.join(PAPERS_DIR, "Organized_Crime,_Pre-electoral_Violence,_and_Politics.pdf")
dest_pdf = os.path.join(target_dir, "Organized Crime, Violence, and Politics.pdf")
if os.path.exists(src_pdf):
    shutil.move(src_pdf, dest_pdf)
    print(f"✅ Spostato PDF a: {dest_pdf}")
else:
    print(f"⚠️ PDF sorgente non trovato in: {src_pdf}")

# 2. Copia la copertina
src_cover = "/tmp/active_cover.png"
dest_cover = os.path.join(target_dir, "copertina.png")
if os.path.exists(src_cover):
    shutil.copy(src_cover, dest_cover)
    print(f"✅ Copiata copertina a: {dest_cover}")
else:
    print(f"⚠️ Copertina non trovata in: {src_cover}")

# 3. Scrivi video_metadata.md
metadata_path = os.path.join(target_dir, "video_metadata.md")
metadata_content = f"""# Metadati Video - Mafia ed elezioni: come funziona?

## Descrizione YouTube
Lo studio "Organized Crime, Violence, and Politics" di Alesina, Piccolo, Pinotti, pubblicato su Review of Economic Studies nel 2019, analizza come le organizzazioni criminali usino strategicamente la violenza pre-elettorale per influenzare i risultati politici e spaventare i candidati. La violenza si intensifica quando il risultato elettorale è incerto, riducendo i voti per i partiti di sinistra (storicamente contrari alle mafie) e spaventando i politici eletti, i quali riducono i propri interventi in parlamento contro la mafia.

⏰ Fonte: ►► https://doi.org/10.1093/restud/rdy036

⏰ISCRIVITI al canale ►► https://www.youtube.com/@cosafannoglieconomisti26?sub_confirmation=1


▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
⏰ INDICE CONTENUTI ⏰
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
00:00 | Intro
01:30 | La violenza come segnale strategico
03:15 | Regole elettorali e incentivi alla mafia
05:00 | L'effetto sui voti e sulla sinistra
06:30 | La paura in Parlamento
08:00 | Conclusioni

#CosaFannoGliEconomisti #Mafia #Elezioni #RicercaAccademica #Politica #Sociologia #Alesina

## Tag
CosaFannoGliEconomisti, Mafia, Elezioni, RicercaAccademica, Politica, Sociologia, Alesina

## Status Pipeline
- Paper PDF: Organized Crime, Violence, and Politics.pdf (OK)
- Video RAW: Da fare
- Video Cleaned: Da fare
- Indice Whisper: Da fare
- Sottotitoli (SRT/VTT): Da fare
"""

with open(metadata_path, 'w', encoding='utf-8') as f:
    f.write(metadata_content)
print(f"✅ Scritto video_metadata.md a: {metadata_path}")

# 4. Aggiorna video_tracking.json
if os.path.exists(TRACKING_FILE):
    with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
        tracking = json.load(f)
else:
    tracking = {}

tracking[folder_name] = {
    "youtube_id": "",
    "youtube_url": "",
    "facebook_url": "Da fare",
    "instagram_url": "Da fare",
    "facebook_cover_status": "Da fare",
    "playlist": "Economia del Crimine e Mafie",
    "last_updated": datetime.now().isoformat(),
    "status": "In Corso"
}

with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
    json.dump(tracking, f, indent=4, ensure_ascii=False)
print("✅ Aggiornato video_tracking.json")

# 5. Aggiorna active_pipeline.json
pipeline_data = {
    "active_video": folder_name,
    "paper_title": "Organized Crime, Violence, and Politics",
    "step": 1,
    "last_updated": datetime.now().isoformat(),
    "title": title_scelto,
    "paper_path": dest_pdf,
    "target_dir": target_dir,
    "clean_title": folder_name
}

with open(PIPELINE_FILE, 'w', encoding='utf-8') as f:
    json.dump(pipeline_data, f, indent=4, ensure_ascii=False)
print("✅ Aggiornato active_pipeline.json")

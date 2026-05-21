import json
import os
import shutil
from datetime import datetime

# Percorso Univoco del Registro
TRACKING_FILE = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/video_tracking.json"
BACKUP_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/backups"

def ensure_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    if os.path.exists(TRACKING_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"video_tracking_backup_{timestamp}.json")
        shutil.copy2(TRACKING_FILE, backup_path)
        # Mantieni solo gli ultimi 10 backup
        backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.startswith("video_tracking_backup")], key=os.path.getmtime)
        if len(backups) > 10:
            for old_b in backups[:-10]:
                os.remove(old_b)

def load_data():
    if not os.path.exists(TRACKING_FILE):
        return {}
    with open(TRACKING_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    ensure_backup()
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def update_entry(project_name, key=None, value=None, full_entry=None):
    """
    Aggiorna o crea una voce nel registro in modo deterministico.
    """
    data = load_data()
    now = datetime.now().isoformat()
    
    if project_name not in data:
        # Inizializza nuovo progetto (Long-form)
        data[project_name] = {
            "youtube_id": "",
            "youtube_url": "Da pubblicare",
            "facebook_url": "Da fare",
            "instagram_url": "Da fare",
            "facebook_cover_status": "Mancante",
            "playlist": "Da assegnare",
            "last_updated": now
        }
    
    if full_entry:
        data[project_name].update(full_entry)
    elif key and value is not None:
        data[project_name][key] = value
        
    data[project_name]["last_updated"] = now
    
    # Rendi deterministico l'ordine alfabetico delle chiavi primarie
    sorted_data = dict(sorted(data.items()))
    
    save_data(sorted_data)
    print(f"✅ Registro aggiornato per: {project_name}")

def delete_entry(project_name):
    data = load_data()
    if project_name in data:
        del data[project_name]
        save_data(data)
        print(f"🗑️ Voce eliminata: {project_name}")
    else:
        print(f"⚠️ Progetto non trovato: {project_name}")

if __name__ == "__main__":
    import sys
    # Esempio uso CLI: python3 tracking_manager.py "Project_Name" "youtube_id" "ID123"
    if len(sys.argv) >= 4:
        p_name = sys.argv[1]
        k = sys.argv[2]
        v = sys.argv[3]
        update_entry(p_name, key=k, value=v)
    elif len(sys.argv) == 3 and sys.argv[1] == "--delete":
        delete_entry(sys.argv[2])
    elif len(sys.argv) == 2:
        # Inizializzazione semplice
        update_entry(sys.argv[1])

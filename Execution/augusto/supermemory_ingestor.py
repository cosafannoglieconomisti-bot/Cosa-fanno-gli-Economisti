import os
import json
import logging
from pathlib import Path
from supermemory import Supermemory
from dotenv import load_dotenv

# Configurazione Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Caricamento credenziali
load_dotenv("/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/.env")
api_key = os.getenv("SUPERMEMORY_API_KEY")
project_id = os.getenv("SUPERMEMORY_PROJECT_ID")

if not api_key:
    logger.error("SUPERMEMORY_API_KEY non trovata nel file .env")
    exit(1)

# Inizializzazione Supermemory
sm = Supermemory(
    api_key=api_key,
    default_headers={"x-sm-project": project_id}
)

STYLES = {
    "thumbnail_style": "Formato Comics (Nero/Arancio/Bianco). La copertina deve riportare il titolo scelto.",
    "social_caption_style": """[Didascalia YouTube — paragrafo 'Lo studio ... analizza ...' estratto da video_metadata.md]

▶ https://www.youtube.com/watch?v=[VIDEO_ID]

[Tag reali del video da video_metadata.md — mai generati dall'IA]""",
    "youtube_description_style": """Lo studio 'TITOLO ACCADEMICO REALE DEL PAPER' di COGNOMI AUTORI DEL PAPER, pubblicato su NOME DELLA RIVISTA nel ANNO DI PUBBLICAZIONE, analizza IN POCHE PAROLE QUAL'è LA DOMANDA DI RICERCA...

⏰ Fonte: ►► [Link DOI certificato o Journal page]

⏰ISCRIVITI al canale ►► https://www.youtube.com/@cosafannoglieconomisti26?sub_confirmation=1

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
⏰ INDICE CONTENUTI ⏰
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
00:00 | Intro
XX:XX | [Titolo Capitolo]
XX:XX | Conclusioni

#tag1 #tag2 #tag3"""
}

def ingest_styles():
    logger.info("Ingestione Stili...")
    for key, value in STYLES.items():
        sm.add(
            content=f"Style Reference for {key.replace('_', ' ').title()}:\n{value}",
            container_tags=["style", "sop", "guidelines"],
            metadata={"type": "style", "key": key}
        )

def ingest_archive():
    logger.info("Ingestione Archivio (Cleaned/)...")
    base_path = Path("/Users/marcolemoglie_1_2/Desktop/canale/Cleaned")
    if not base_path.exists():
        logger.warning(f"Percorso {base_path} non trovato.")
        return

    for item in base_path.iterdir():
        if item.is_dir():
            # Cerca metadati o usa il nome della cartella
            metadata_file = list(item.glob("video_metadata*.md"))
            content = f"Project Folder: {item.name}"
            if metadata_file:
                try:
                    with open(metadata_file[0], 'r') as f:
                        content += f"\nMetadata Summary:\n{f.read()[:500]}..." # Taglia per risparmiare token
                except:
                    pass
            
            sm.add(
                content=f"Completed Paper Archive Entry: {content}",
                container_tags=["archive", "completed", "paper"],
                metadata={"folder": item.name, "type": "archive_entry"}
            )

def ingest_pipeline():
    logger.info("Ingestione Stato Pipeline (video_tracking.json)...")
    tracking_file = Path("/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/video_tracking.json")
    if tracking_file.exists():
        with open(tracking_file, 'r') as f:
            data = json.load(f)
            for title, info in data.items():
                sm.add(
                    content=f"Pipeline Status for {title}: {json.dumps(info, indent=2)}",
                    container_tags=["pipeline", "status", "tracking"],
                    metadata={"title": title, "youtube_id": info.get("youtube_id", "N/A")}
                )

def ingest_playlists():
    logger.info("Ingestione Configurazione Playlist...")
    config_file = Path("/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/playlist_config.json")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for title, info in data.get("playlists", {}).items():
                sm.add(
                    content=f"Playlist Configuration for {title}:\nDescription: {info.get('description')}\nVideos assigned: {', '.join(info.get('videos', []))}",
                    container_tags=["playlist", "configuration", "mapping"],
                    metadata={"title": title, "type": "playlist_config"}
                )

def ingest_upcoming():
    logger.info("Ingestione Paper Future (Papers/Da fare Portfoli)...")
    todo_path = Path("/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare")
    if todo_path.exists():
        for item in todo_path.rglob("*.pdf"):
            sm.add(
                content=f"Upcoming Paper in Pipeline (including subfolders): {item.name}",
                container_tags=["upcoming", "da_fare", "paper"],
                metadata={"filename": item.name, "type": "todo", "path": str(item)}
            )

if __name__ == "__main__":
    try:
        ingest_styles()
        ingest_archive()
        ingest_pipeline()
        ingest_playlists()
        ingest_upcoming()
        logger.info("Ingestione completata con successo!")
    except Exception as e:
        logger.error(f"Errore durante l'ingestione: {e}")

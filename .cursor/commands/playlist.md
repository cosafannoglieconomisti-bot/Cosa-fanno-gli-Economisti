# /playlist — Catalogazione video nelle playlist YouTube

Agente Romolo: assegna un video alla playlist tematica corretta.

## Prima di iniziare
- Leggi `Cleaned/video_tracking.json` per l'ID YouTube.
- Chiedi quale cartella `Cleaned/` o youtube_id usare se non specificato.

## Procedura
1. Recupera metadati da `video_metadata.md`
2. Gemini determina playlist (es. "Economia del Crimine e Mafie", "Storia Economica e Sviluppo")
3. Aggiorna playlist via YouTube API
4. Salva esito in `video_tracking.json`

## Esecuzione
```bash
export TERM=dumb DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
/Users/<USER>/Desktop/canale/.venv/bin/python3 \
  /Users/<USER>/Desktop/canale/Execution/romolo/catalog_video.py "NOME_CARTELLA_O_YOUTUBE_ID"
```

Fallback se categoria incerta: "Economia Politica e Istituzioni" + notifica all'utente.

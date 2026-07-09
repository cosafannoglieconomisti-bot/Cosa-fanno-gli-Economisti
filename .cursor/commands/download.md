# /download — Ingestione paper da Downloads

Esegui il workflow di scansione e organizzazione PDF.

## Prima di iniziare
- Leggi `GEMINI.md` (SOP 0: Ingestione Paper).
- Usa solo: `/Users/<USER>/Desktop/canale/.venv/bin/python3`

## Procedura
1. Cerca PDF in `~/Downloads` modificati nelle ultime **24 ore**.
2. Escludi duplicati già in `Papers/Da fare/` o `Cleaned/`.
3. Estrai titolo accademico reale (prime 3 pagine + Gemini Flash).
4. Rinomina e sposta in `Papers/Da fare/`.

## Esecuzione
```bash
export TERM=dumb DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
/Users/<USER>/Desktop/canale/.venv/bin/python3 \
  /Users/<USER>/Desktop/canale/Execution/enea/paper_downloader.py
```

Riporta quanti paper trovati, spostati e rinominati.

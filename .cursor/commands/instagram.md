# /instagram — Programmazione post Instagram via Buffer

Agente Marcello: programma post IG con infografica del paper. Dal 2026-08-31 Instagram e' l'unico social Buffer nel closeout di `/upload`; Facebook e' sospeso.

## Prima di iniziare — MANDATORIO
- Leggi `Cleaned/video_tracking.json`
- Esegui `/backup` prima se le immagini non sono su GitHub (Buffer fetch da raw URL)

## Procedura
1. Seleziona ultimo video YT non ancora su Instagram (escludi Shorts)
2. Usa `infografica_cleaned.png` da `Cleaned/[Titolo]/`
3. Didascalia: Title Case header, divider, "Lo studio...", link, hashtag
4. Programma via Buffer (default domani 10:00)
5. Aggiorna `instagram_url` in `video_tracking.json`

## Esecuzione
```bash
export TERM=dumb DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
/Users/<USER>/Desktop/canale/.venv/bin/python3 \
  /Users/<USER>/Desktop/canale/Execution/marcello/buffer_post_single.py --platform instagram --hour 10
```

Dry-run opzionale: aggiungi `--dry-run`

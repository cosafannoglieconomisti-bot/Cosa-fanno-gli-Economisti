# /competitor — Scouting competitor e commenti di alto valore

Agente Romolo: trova video caldi e propone commenti che citano paper accademici e linkano il canale.

## Prima di iniziare
- Leggi `Cleaned/video_tracking.json` e storico `Temp/romolo/competitor_comment_history.json`.
- Priorità: video pubblicati negli **ultimi 30 giorni**.

## Procedura
1. Esegui scouting ibrido (keywords + canali target italiani)
2. Genera proposte in `Temp/romolo/competitor_engagement.md`
3. **Mostra all'utente per approvazione** (MANDATORIO)
4. Dopo approvazione, pubblica con `post_youtube_comment.py`
5. Aggiorna `competitor_comment_history.json`

## Script
```bash
export TERM=dumb DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
/Users/<USER>/Desktop/canale/.venv/bin/python3 \
  /Users/<USER>/Desktop/canale/Execution/romolo/competitor_scout.py
```

Non pubblicare commenti senza revisione esplicita dell'utente.

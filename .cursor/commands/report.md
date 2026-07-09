# /report — Analytics YouTube e consigli strategici

Agente Romolo: report mensile del canale con consigli SEO/actionable.

## Esecuzione
```bash
export TERM=dumb DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
/Users/<USER>/Desktop/canale/.venv/bin/python3 \
  /Users/<USER>/Desktop/canale/Execution/romolo/romolo_manage_channel.py
```

## Output atteso
- Visualizzazioni, watch time, iscritti, commenti recenti
- 3 consigli strategici azionabili (SEO, argomenti, thumbnail)
- Presenta il report in modo leggibile in chat

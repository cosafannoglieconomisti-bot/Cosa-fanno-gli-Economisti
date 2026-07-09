# /gmail — Lettura e sintesi email del canale

Agente Mercurio: scarica email Gmail e riporta sintesi in chat.

## Esecuzione
```bash
export TERM=dumb DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
/Users/<USER>/Desktop/canale/.venv/bin/python3 \
  /Users/<USER>/Desktop/canale/Execution/mercurio/mercurio_gmail_manager.py
```

## Dopo l'esecuzione
- Leggi `Temp/mercurio/gmail_report.txt`
- Riassumi in chat: mittenti rilevanti, oggetti urgenti, azioni richieste
- Non stampare token o credenziali

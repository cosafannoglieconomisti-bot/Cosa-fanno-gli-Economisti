# /backup — Sincronizzazione GitHub (con offuscamento)

Esegui backup sicuro del workspace su GitHub.

## Prima di iniziare
- I file locali **non** vengono modificati; solo lo staging viene offuscato.
- I `.mp4` sono esclusi dal push.

## Procedura
1. Staging di `.agents`, `Directives`, `Execution`, `GEMINI.md`, `Cleaned/` (senza video)
2. Offuscamento token/API key in `.md`, `.py`, `.txt`, `.json`
3. Force push su `origin main`

## Esecuzione
```bash
export TERM=dumb DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
/Users/<USER>/Desktop/canale/.venv/bin/python3 \
  /Users/<USER>/Desktop/canale/Execution/mercurio/mercurio_github_sync.py
```

Alternativa incrementale (delta, meno timeout): `Execution/mercurio/mercurio_targeted_sync.py`

Riporta esito push e eventuali errori.

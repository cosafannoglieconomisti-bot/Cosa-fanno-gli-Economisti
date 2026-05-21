---
description: Sincronizza le modifiche su GitHub (con offuscamento dati sensibili)
---

Questo workflow esegue il backup automatico del workspace su GitHub, garantendo la protezione dei dati sensibili.

1. **Esecuzione (Master Bot)**:
   - L'utente lancia il comando `/backup` dal Bot Telegram.
   - Il bot invoca lo script `mercurio_github_sync.py`.

2. **Sicurezza e Staging**:
   - Lo script crea una copia temporanea del workspace (**Staging Area**), includendo le cartelle core e `Cleaned/`.
   - **Filtro Video**: Tutti i file `.mp4` vengono filtrati e rimossi dallo staging prima del push.
   - Esegue l'**offuscamento automatico** (REDACTION) di token, API key e ID sensibili nei file `.md`, `.py`, `.txt` e `.json`.
   - I file locali sul Mac **NON vengono modificati**; la versione originale rimane intatta e funzionante.

3. **Sincronizzazione (Git)**:
   - Lo script sincronizza la versione pulita su GitHub con un force push su `origin main`.
   - Include automaticamente il file `README.md` informativo.

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/cesare/telegram_bot.py` (Orchestra il comando)
2. `Execution/mercurio/mercurio_github_sync.py` (Esegue lo staging, l'offuscamento e il push)

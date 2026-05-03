---
description: Produzione Video e Infografica su NotebookLM
---

# /produzione Workflow (Enea)

## Descrizione
Questo workflow gestisce esclusivamente la generazione e l'acquisizione degli asset grezzi da NotebookLM.

## Procedura Deterministica
1. **Lancio**: Digita `/produzione` su Telegram.
2. **Selezione**: Scegli un paper dalla lista proposta (solo quelli con metadati e copertina ma senza video).
3. **Automazione NotebookLM (Browser)**:
   - Apri [NotebookLM](https://notebooklm.google.com/).
   - Crea/Apri Notebook e carica il PDF del paper.
   - Genera **Video Overview** (Prompt: *"MANDATORIO: Il TITOLO in sovrimpressione... [Titolo Scelto]"*).
   - Genera **Infografica Quadrata Dettagliata**.
4. **Download**: Scarica il Video Overview (.mp4) e l'Infografica (.png) in `~/Downloads`. 
5. **Fine Workflow**: Una volta scaricati i file grezzi (`*_raw.mp4` e l'immagine), il workflow `/produzione` è **TERMINATO**. Ogni operazione successiva (pulizia, trimmaggio, ecc.) appartiene al workflow `/pulizia`.

## 📋 File Python Utilizzati
- `Execution/cesare/telegram_bot.py` (Lancio workflow)
- `Execution/enea/notebooklm_asset_downloader.py` (Download Asset)
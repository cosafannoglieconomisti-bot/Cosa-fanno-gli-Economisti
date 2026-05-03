---
description: Programma un post su Instagram via Buffer API
---

Questo workflow gestisce la programmazione di post su Instagram utilizzando l'infografica del paper come asset visivo.

1.  **Identificazione Contenuto**: Lo script seleziona automaticamente l'ultimo video pubblicato su YouTube che non è ancora stato programmato su Instagram (escludendo gli Shorts).
2.  **Asset Discovery**: Il sistema cerca un'infografica (`.png`) nella cartella `Cleaned/` corrispondente.
3.  **Generazione Didascalia**: La didascalia viene formattata seguendo la SOP (Header Title Case, Divider, Descrizione "Lo studio...", Link, Tag).
4.  **Programmazione**: Il post viene inviato a Buffer per la pubblicazione (default domani ore 10:00).
5.  **Aggiornamento Registro**: Lo script aggiorna automaticamente `instagram_url` in `Cleaned/video_tracking.json` con lo stato "Post Programmato (Buffer)". In caso di fallimento, eseguire manualmente via `tracking_manager.py`.

### Esecuzione

// turbo
1. Esegui il comando di programmazione (Instagram):
   ```bash
   /Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 /Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/buffer_post_single.py --platform instagram --hour 10
   ```

2. Verifica l'anteprima (Dry-Run opzionale):
   ```bash
   /Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 /Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/buffer_post_single.py --platform instagram --dry-run
   ```

### SOP Regole Mandatorie
- **Titolo (Header)**: Sempre in **Title Case** (es: "Narcos e Petrolio", non "NARCOS E PETROLIO").
- **Asset**: Deve essere un'immagine diretta via URL GitHub Raw (gestito automaticamente dallo script).
- **History**: Lo script registra il video in `instagram_history.json` per evitare duplicati.

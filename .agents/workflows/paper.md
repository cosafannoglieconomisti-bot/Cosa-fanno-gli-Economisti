---
description: Selezione Paper ed Estrazione Titoli Catchy
---

Questo workflow gestisce la scelta iniziale del paper e la generazione del titolo per il video tramite Bot Telegram.

1. **Selezione Paper**:
   - L'utente lancia `/paper` su Telegram.
   - Il bot analizza i PDF in `Papers/Da fare/` (**ricorsivamente**, includendo tutte le sottocartelle) usando Gemini per proporre i **Titoli reali** sui pulsanti.
   - L'utente seleziona il paper.

2. **Generazione Titoli (Gemini)**:
   - Il bot estrae il testo (prime 3 pagine) tramite `batch_text_extractor.py`.
   - Propone 5 opzioni di titoli "catchy" nel corpo del messaggio. **MANDATORIO**: Ogni titolo deve essere di **massimo 5 parole** e in stile **catchy/domanda**.

3. **Archiviazione PDF e Cartella**:
   - L'utente clicca su `🔢 Opzione [X]`.
   - Il bot recupera il **Titolo Accademico** reale del paper tramite Gemini.
   - Crea la cartella `Cleaned/[Titolo_Scelto]`.
   - **Sposta e Rinomina** il PDF originale da `Papers/Da fare/` a `Cleaned/[Titolo_Scelto]/[Titolo_Accademico].pdf`.
   - Salva i metadati in `video_metadata.md` e lo stato in `active_pipeline.json`.

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/cesare/telegram_bot.py` (Gestione Comandi e Menu)
2. `Execution/enea/batch_text_extractor.py` (Estrazione testo PDF specifico)

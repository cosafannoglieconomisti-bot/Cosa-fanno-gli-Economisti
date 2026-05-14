---
description: Selezione Paper, Titoli Catchy e Generazione Copertina
---

Questo workflow gestisce l'intero setup iniziale: scelta del paper, generazione del titolo e creazione della copertina approvata.

1. **Selezione Paper**:
   - L'utente lancia `/paper` su Telegram.
   - Il bot analizza i PDF in `Papers/Da fare/` (**ricorsivamente**) e propone i titoli reali.
   - L'utente seleziona il paper.

2. **Generazione Titoli (Gemini)**:
   - Il bot estrae il testo tramite `batch_text_extractor.py`.
   - Propone 5 opzioni di titoli "catchy" (massimo 5 parole, stile domanda).

3. **Generazione e Approvazione Copertina**:
   - Una volta scelto il titolo, il sistema lancia immediatamente `generate_cover.py`.
   - Il bot invia la proposta di copertina in stile Comic (Arancio/Nero/Bianco) con il titolo integrato.
   - L'utente può cliccare su `✅ Approva` o `🔄 Rigenera`.

4. **Setup Cartella e Archiviazione**:
   - All'approvazione della copertina, il bot:
     - Recupera il **Titolo Accademico** reale.
     - Crea la cartella `Cleaned/[Titolo_Scelto]`.
     - **Sposta e Rinomina** il PDF originale in `Cleaned/[Titolo_Scelto]/[Titolo_Accademico].pdf`.
     - Salva `copertina.png` nella cartella.
     - Inizializza `video_metadata.md` con i dati estratti (Autori, Rivista, Anno, DOI).
     - Salva lo stato in `active_pipeline.json`.

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/cesare/telegram_bot.py` (Gestione Menu e Workflow)
2. `Execution/enea/batch_text_extractor.py` (Estrazione testo PDF)
3. `Execution/enea/generate_cover.py` (Generazione Immagine AI)

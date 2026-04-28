---
description: Workflow /pulizia per processamento video e metadati
---

Il workflow `/pulizia` automatizza la fase di post-processing del video e dell'infografica scaricati da NotebookLM.

### Procedura Operativa

1.  **Assicurati che la pipeline sia attiva**: Lancia prima `/paper` per selezionare il paper e il titolo.
2.  **Verifica Asset**: I file scaricati da NotebookLM (`*_raw.mp4` e l'infografica `.png`) devono trovarsi nella cartella `Downloads` dell'utente Mac.

### Procedura Deterministica

1.  **Lancio**: Digita `/pulizia` su Telegram.
2.  **Selezione Video**: Il bot mostra un elenco dei file `*_raw.mp4` trovati in `Downloads` nelle ultime **24 ore**, ordinati dal più recente. Scegli quello corretto dal menu inline.
3.  **Esecuzione Automatica (`video_processor.py`)**:
    -   **Cleaning Video**: Rimuove watermark e trimmaggio (2.5s).
    -   **Cleaning Infografica**: Rimozione automatica watermark NotebookLM dall'immagine (`clean_infographic.py`).
    -   **Sottotitoli & Indice**: Generazione automatica di `video_index_raw.txt`, `subtitles_it.srt` e `subtitles_it.vtt` tramite Whisper.
    -   **Archiviazione RAW**: Sposta il file originale (rinominato in `*_raw.mp4`) nella cartella di riferimento `Cleaned/[Titolo]/`.
    -   **Archiviazione Cleaned**: Sposta il video pulito (`*_cleaned.mp4`) e l'infografica pulita nella stessa cartella.
    -   **Archiviazione Internazionale**: Sposta tutti i file di testo (`.txt`, `.srt`, `.vtt`) nella sottocartella `international/`.
4.  **Metadati**: Genera `video_metadata.md` con la descrizione YouTube completa.
    -   **Indice**: Massimo 6 capitoli (Intro, 4 intermedi, Conclusioni).
    -   **Conclusioni (Timestamp)**: Il minutaggio delle Conclusioni **DEVE** essere dinamico, corrispondente all'inizio dell'ultimo segmento trascritto (no `XX:XX`).
    -   **Titoli**: Generati via Gemini per essere tematici e rappresentativi (non semplici frammenti).
5.  **Notifica Finale**: Il bot invia un messaggio di conferma su Telegram al termine di tutte le operazioni.
6.  **Aggiornamento Registro**: La pipeline aggiorna automaticamente `Cleaned/video_tracking.json` tramite `tracking_manager.py`.
7.  **Archiviazione Internazionale**: Durante la pulizia, i file di trascrizione e sottotitoli (SRT, VTT, TXT) vengono spostati in `international/` per preservarli dal cleanup finale del repository.

### Requisiti
- File `active_pipeline.json` in `Temp/enea/`.
- Video `.mp4` e Infografica `.png` presenti in `Downloads`.

## 📋 File Python Utilizzati
1. `Execution/enea/video_processor.py`
2. `Execution/enea/generate_index_whisper.py`
3. `Execution/enea/video_cleaner.py`
4. `Execution/enea/clean_infographic.py`
5. `Execution/enea/video_cleanup.py` (Archiviazione Asset)

---
description: Workflow /upload per pubblicazione YouTube con Asset Detection intelligente
---

Il workflow `/upload` gestisce la pubblicazione e programmazione dei video su YouTube, automatizzando la ricerca di copertine e metadati.

### Procedura Operativa

1.  **Preparazione**: Assicurati che la cartella `Cleaned/[Titolo]` contenga il video pulito, almeno un'immagine (`copertina.png` o `thumbnail.png`) e il file dei metadati.
2.  **Lancio**: Digita `/upload` su Telegram.

### Procedura Deterministica

1.  **Filtro IA (Semantic Filtering)**: 
    - Il bot recupera la lista dei video già pubblicati sul canale via YouTube API.
    - Usa Gemini per confrontare i nomi delle cartelle locali con i titoli online.
    - Mostra solo i video **non ancora pubblicati**, evitando duplicati.
2.  **Selezione**: Scegli il video dal menu inline (ID persistenti anche dopo riavvio bot).
3.  **Asset Detection Flessibile**:
    - **Metadati**: Cerca `video_metadata.md` o qualsiasi `.md` descrittivo.
    - **Copertina**: Cerca in ordine `copertina.png`, `thumbnail.png`, `cover.png`.
4.  **Esecuzione in Background (Threading)**:
    - L'upload viene avviato in un thread separato per mantenere il bot 100% reattivo.
    - Il bot notifica immediatamente l'avvio sul Bridge Log.
5.  **Programmazione**: Il video viene programmato automaticamente per le **08:00 AM del giorno successivo** (ora italiana).
6.  **Aggiornamento Registro**: Lo script `youtube_uploader.py` (o l'agente) deve aggiornare il campo `youtube_id` e lo status nel file `Cleaned/video_tracking.json`.
7.  **Caricamento Sottotitoli (MANDATORIO)**: Il sistema deve automaticamente (o tramite l'agente) caricare le tracce professionali presenti nella sottocartella `international/` del progetto via `update_video_localization.py`.
8.  **Mandatory Cleanup (MANDATORIO)**: Una volta confermato l'upload, è **obbligatorio** eseguire la pulizia deterministica tramite lo script `Execution/enea/video_cleanup.py`. Questo passaggio rimuove i file `.mp4` (raw e cleaned), l'infografica raw e il **PDF del paper**, archiviando gli asset rimanenti in `international/` e impostando lo status del progetto a `Pulito`.


### Requisiti
- Credenziali in `Execution/credentials/token.pickle`.
- Almeno un file `.mp4` e un `.png` nella cartella `Cleaned/`.

## 📋 File Python Utilizzati
1. `Execution/cesare/telegram_bot.py` (Interfaccia e Filtro IA)
2. `Execution/enea/youtube_uploader.py` (Logica di Upload e Auth non-interattiva)
3. `Execution/romolo/update_video_localization.py` (Upload Sottotitoli e Localizzazioni)
4. `Execution/enea/tracking_manager.py` (Aggiornamento Registro)
5. `Execution/enea/video_cleanup.py` (Pulizia Post-Upload)

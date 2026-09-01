---
description: Workflow /upload per pubblicazione YouTube + Instagram e Cleanup Root
---

Il workflow `/upload` gestisce la pubblicazione automatizzata su **YouTube e Instagram**, seguita dalla pulizia della root del canale.

**Facebook e' sospeso** (decisione 2026-08-31). Non programmare post FB via Buffer. Closeout completo = YouTube + Instagram + cleanup + tracking `Pulito`.

### Procedura Operativa

1.  **Preparazione**: Assicurati che la cartella `Cleaned/[Titolo]` contenga il video pulito, `copertina.png`, `infografica_cleaned.png` e i metadati.
2.  **Lancio**: Digita `/upload` in chat (o `./workflow upload`).

### Procedura Deterministica

1.  **Filtro IA (Semantic Filtering)**: 
    - Il bot recupera la lista dei video pubblicati su YouTube.
    - Mostra solo i video locali **non ancora online**.
2.  **Upload YouTube**:
    - Upload in background (Threading).
    - Caricamento Sottotitoli IT+Multilingua (`international/`).
3.  **Collocazione Playlist (MANDATORIO)**:
    - Esecuzione automatica di `catalog_video.py`.
    - Assegnazione a una delle 8 playlist tematiche (es: "Economia del Crimine", "Storia Economica").
    - Aggiornamento della descrizione della playlist con il nuovo titolo.
4.  **Programmazione Social (Automatico)**:
    - **Instagram**: Programmazione post via Buffer con `infografica_cleaned.png`.
    - **Facebook**: **sospeso**. Non lanciare Buffer FB. Segnare `facebook_url` / `facebook_cover_status` come `Sospeso` se ancora pendenti.
5.  **Mandatory Root Cleanup**:
    - Lo script `video_cleanup.py` viene eseguito automaticamente alla fine.
    - **Rimozione**: Cancella file `.mp4` residui dalla root e dalle cartelle progetto.
    - **Archiviazione**: Sposta asset testuali in `international/`.
6.  **Aggiornamento Registro**: Aggiorna `video_tracking.json` con lo status `Pulito` e i link/ID YouTube + Instagram.

### Requisiti
- Credenziali Buffer (Instagram) e YouTube attive.
- Asset multilingua pronti in `international/`.

## 📋 File Python Utilizzati
1. `Execution/cesare/telegram_bot.py` (Interfaccia)
2. `Execution/enea/youtube_uploader.py` (Upload YouTube)
3. `Execution/romolo/update_video_localization.py` (Localizzazione)
4. `Execution/romolo/catalog_video.py` (Playlist)
5. `Execution/marcello/buffer_post_single.py --platform instagram`
6. `Execution/enea/video_cleanup.py` (Cleanup Finale)

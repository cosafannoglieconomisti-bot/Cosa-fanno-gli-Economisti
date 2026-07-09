# /pulizia — Post-processing video, infografica e multilingua

Esegui il workflow **Step 3** dopo `/produzione`.

## Prima di iniziare
- Leggi `GEMINI.md` e `Directives/enea/produzione_video.md`.
- Verifica `Temp/enea/active_pipeline.json` e asset in `~/Downloads` o `Cleaned/[Titolo]/`.
- Usa solo: `/Users/<USER>/Desktop/canale/.venv/bin/python3`

## Procedura (`video_processor.py`)
1. Rimuovi watermark video (FFmpeg) e trim 2.5s → `*_cleaned.mp4`
2. Rimuovi watermark infografica → `infografica_cleaned.png`
3. Genera sottotitoli e indice Whisper → `international/`
4. Traduci metadati e sottotitoli in **EN, ES, FR, DE** (blocca se fallisce)
5. Genera `video_metadata.md` (max 6 capitoli, timestamp conclusioni dinamici)
6. Aggiorna `Cleaned/video_tracking.json` via `tracking_manager.py`

## Script (ordine)
1. `Execution/enea/video_processor.py`
2. `Execution/enea/generate_index_whisper.py`
3. `Execution/enea/video_cleaner.py`
4. `Execution/enea/clean_infographic.py`

Non passare a `/upload` finché mancano asset multilingua in `international/`.

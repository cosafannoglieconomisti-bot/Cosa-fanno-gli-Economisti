# /upload — Pubblicazione YouTube + Instagram e cleanup

Esegui il workflow **Step 4**: YouTube, playlist, Buffer Instagram, pulizia asset.

**Facebook e' sospeso** (decisione 2026-08-31). Non programmare post FB via Buffer. Piattaforme attive: YouTube e Instagram.

## Prima di iniziare — MANDATORIO
- Leggi `Cleaned/video_tracking.json` e verifica che il video non sia già pubblicato.
- Leggi `GEMINI.md` (SOP upload).
- Esegui `/backup` su GitHub **prima** di Buffer se le immagini non sono ancora su origin (Buffer le scarica da GitHub raw). Per Instagram serve `infografica_cleaned.png`.
- Usa solo: `/Users/<USER>/Desktop/canale/.venv/bin/python3`

## Procedura
1. Valida asset in `Cleaned/[Titolo]/` (video cleaned, copertina, infografica_cleaned, international/)
2. Upload YouTube + sottotitoli multilingua
3. Cataloga playlist con `catalog_video.py`
4. Programma **solo Instagram** (infografica) via Buffer: `buffer_post_single.py --platform instagram`
5. Segna Facebook nel tracking come `Sospeso` (`facebook_url`, `facebook_cover_status`) se ancora `Da fare`/`Mancante`
6. Esegui `video_cleanup.py` (rimuove MP4/PDF raw)
7. Aggiorna `video_tracking.json` → stato `Pulito`

## Script (ordine)
1. `Execution/enea/youtube_uploader.py`
2. `Execution/romolo/update_video_localization.py`
3. `Execution/romolo/catalog_video.py`
4. `Execution/marcello/buffer_post_single.py --platform instagram`
5. `Execution/enea/video_cleanup.py`

Non lanciare `buffer_post_single.py --platform facebook` salvo deroga esplicita dell'utente (`--force-facebook`).

Chiedi quale cartella `Cleaned/` pubblicare se non è evidente da `active_pipeline.json`.

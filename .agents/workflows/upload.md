---
description: Workflow /upload — YT long → assets GitHub → Buffer IG → Short → Reel → cleanup
---

Il workflow `/upload` pubblica in ordine **deterministico** su YouTube + Instagram, poi pulisce mp4/pdf.

**Facebook è sospeso** (2026-08-31). Closeout = YT long + IG post + (opz.) Short/Reel + cleanup + tracking `Pulito`.

## Checklist deterministica (NON saltare passi)

1. **YT long** — `youtube_uploader.py` (schedule). Serve `youtube_id` prima di Short/Reel.
2. **Push Buffer assets** — `git add Cleaned/{folder}` (png/md/srt/vtt/txt; **mp4 esclusi** da gitignore) + `Cleaned/video_tracking.json` → commit `Buffer assets: {folder}` → `git push origin HEAD:main` (**no force**). Serve a `raw.githubusercontent.com` per l’infografica IG.
3. **Buffer IG infografica** — `buffer_post_single.py --platform instagram` con PNG pubblico.
4. **YT Short** (se esiste `*_short*_cleaned.mp4`, default **1 short/paper**) — `upload_short.py` con `Video completo qui: https://youtu.be/[LONG_ID]`; aggiorna placeholder in `shorts/international/short1_metadata.md`.
5. **Host short mp4 pubblico** — `litter.catbox.moe` (HTTPS diretto `video/mp4`). **NON** usare `youtube.com/shorts` come media (Buffer rifiuta).
6. **Buffer Reel** — `buffer_post_single.py --content-type reel --video-url <litter-url>`; tag **solo specifici** da metadata.
7. **Cleanup** — `video_cleanup.py {folder}`: cancella `*.mp4` (anche `shorts/**`), `*.pdf`, `infografica_raw`, opz. `_old_*`; tiene copertina/infografica cleaned/metadata/`international/`/`shorts/international/`; tracking → **Pulito**.
8. **Facebook** — resta `Sospeso`.

Se Buffer IG fallisce a metà ma YT long è ok: continua Short/Reel e **esegui comunque cleanup** (mp4+pdf non devono restare dopo YT publish riuscito).

### CLI
```bash
./workflow upload --folder Titolo_Cartella
./workflow upload --folder Titolo_Cartella --skip-short
./workflow upload --folder Titolo_Cartella --reel-dry-run
```

### Requisiti
- Credenziali YouTube + Buffer IG; asset multilingua in `international/`; PNG already cleaned.

## File Python
1. `Execution/workflows/general_workflows.py` (`workflow_upload`)
2. `Execution/enea/youtube_uploader.py`
3. `Execution/marcello/buffer_post_single.py`
4. `Execution/enea/upload_short.py`
5. `Execution/enea/video_cleanup.py`

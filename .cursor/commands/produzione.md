# /produzione — Produzione video e infografica (NotebookLM)

Esegui il workflow **Step 2** (agente Enea). Genera e scarica asset grezzi da NotebookLM.

## Prima di iniziare
- Leggi `GEMINI.md` e `Directives/enea/produzione_video.md`.
- Verifica `Temp/enea/active_pipeline.json` (o chiedi quale video in `Cleaned/` usare).
- Leggi `Cleaned/video_tracking.json`.
- Lingua **obbligatoria: ITALIANO** su NotebookLM.

## Procedura
1. Seleziona paper con copertina e metadati ma senza video.
2. Carica **solo** il PDF del paper su NotebookLM (account `cosafannoglieconomisti@gmail.com`).
3. Genera **Video Overview** (titolo in sovrimpressione = titolo scelto, esatto).
4. Genera **Infografica quadrata dettagliata** (stile sketch_note).
5. Scarica `*_raw.mp4` e infografica in `~/Downloads`, poi archivia in `Cleaned/[Titolo]/`.

## Script
- `Execution/enea/notebooklm_orchestrator.py` (preferito se MCP/CLI disponibili)
- `Execution/enea/notebooklm_asset_downloader.py` (download asset)

**Fine workflow**: con file grezzi in locale. Pulizia watermark → `/pulizia`.

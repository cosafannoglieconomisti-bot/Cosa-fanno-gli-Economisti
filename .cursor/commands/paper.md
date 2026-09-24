# /paper — Selezione paper, titoli catchy e copertina

Esegui il workflow **Step 1** del canale "Cosa fanno gli economisti".

## Prima di iniziare
- Leggi `GEMINI.md` e `Directives/enea/produzione_video.md`.
- Usa solo: `/Users/<USER>/Desktop/canale/.venv/bin/python3`
- Leggi `Cleaned/video_tracking.json` se serve contesto pubblicazione.

## Procedura
1. Scansiona **ricorsivamente** i PDF in `Papers/Da fare/` e proponi i titoli accademici reali.
2. Estrai il testo con `Execution/enea/batch_text_extractor.py`.
3. Proponi 5 titoli catchy (max 5 parole, stile domanda).
4. Dopo scelta titolo, genera copertina **16:9 only** (es. 1280×720) con ChatGPT/Codex native `image_gen` → `Temp/assets/override_cover.png`; poi `Execution/enea/generate_cover.py` **copia solo** (stile comic arancio/nero/bianco + testo nativo). Non Gemini/Imagen/.env. Infografiche restano 1:1.
5. All'approvazione:
   - Crea `Cleaned/[Titolo_Scelto]/`
   - Sposta/rinomina PDF → `Cleaned/[Titolo_Scelto]/[Titolo_Accademico].pdf`
   - Salva `copertina.png` e inizializza `video_metadata.md`
   - Aggiorna `Temp/enea/active_pipeline.json` e `Cleaned/video_tracking.json`

## Script (ordine)
1. `Execution/enea/batch_text_extractor.py`
2. ChatGPT/Codex `image_gen` → `Temp/assets/override_cover.png`
3. `Execution/enea/generate_cover.py` (copy-only dell'override)

Non inventare paper o metadati. Chiedi conferma su titolo e copertina prima di procedere.

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
4. Dopo scelta titolo, genera copertina con `Execution/enea/generate_cover.py` (stile comic arancio/nero/bianco).
5. All'approvazione:
   - Crea `Cleaned/[Titolo_Scelto]/`
   - Sposta/rinomina PDF → `Cleaned/[Titolo_Scelto]/[Titolo_Accademico].pdf`
   - Salva `copertina.png` e inizializza `video_metadata.md`
   - Aggiorna `Temp/enea/active_pipeline.json` e `Cleaned/video_tracking.json`

## Script (ordine)
1. `Execution/enea/batch_text_extractor.py`
2. `Execution/enea/generate_cover.py`

Non inventare paper o metadati. Chiedi conferma su titolo e copertina prima di procedere.

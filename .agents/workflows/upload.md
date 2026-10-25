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

## Regola: Short → Video correlato (2026-10-14, Marco)
- Ogni Short va collegato al suo video lungo come **«Video correlato»** in YouTube Studio (Short → Dettagli → Video correlato).
- La YouTube Data API v3 non espone questo campo: il passaggio è manuale (Studio, o browser loggato come canale). `./workflow upload` stampa il promemoria con il link del long.
- Lo Short deve avere anche le tracce sottotitoli IT/EN/ES/FR/DE caricate (verifica con captions.list).


## 2026-10-15 (Standard HyperFrames long+Short)
**Standard pipeline (vale anche per la routine Dom/Mer 11):**
1. `/paper`: anti-doppione → titolo → cover → metadata (gate invariati).
2. `/produzione --with-short`: NotebookLM genera long + short + infografica. **Dei video NLM si usa SOLO l'audio della narrazione**; l'infografica NLM resta quella pubblicata.
3. `/pulizia` sul long (e sullo short): trim solo del watermark/outro, voce di chiusura intatta; da qui i sottotitoli IT + traduzioni EN/ES/FR/DE (file separati, mai bruciati).
4. Audio dai file cleaned → trascrizione con tempi (faster-whisper) → `storyboard_long.md` e `storyboard.md` (Short) in `Temp/enea/hyperframes_<slug>/`.
5. **GATE storyboard long** e **GATE storyboard Short**: Marco approva ciascuno prima di generare le immagini.
6. Immagini 16:9 (stile unico per il paper, volti disegnati, contenuto concreto) → HyperFrames: long 1920x1080 (`long_hyperframes_v8/gen_long.py`), Short 1080x1920 (`short_hyperframes_v8/gen4.py`); SUBS=False, pan/zoom e transizioni variate → encode per telefono.
7. QA + anteprima a Marco → `/upload` con i file HyperFrames al posto di `*_cleaned.mp4` / `short1_cleaned.mp4`; caption, metadata, orari (YT 9, IG 10, Short/Reel 12) e tracking invariati.
Strumenti solo gratuiti. SOP dettagliato: `wiki/workflows/short_hyperframes.md`.



## 2026-10-15 23:26 (RIPRISTINO pipeline NotebookLM, HyperFrames in STANDBY)
**Decisione di Marco: annulla e sostituisce la voce "2026-10-15 (Standard HyperFrames long+Short)".**
- Il nuovo formato HyperFrames (slideshow illustrato e infografica dinamica) NON è ancora pronto.
- Routine «Canale pipeline Dom/Mer 11» e produzioni standard: **vecchia pipeline tutta NotebookLM**. Video lungo, Short e infografica sono quelli NLM. `/pulizia` taglia solo watermark/outro NLM, con la voce di chiusura intatta. Sottotitoli IT + EN/ES/FR/DE come file separati, mai impressi. Marco approva prima di caricare o programmare (YT 9, IG 10, Short/Reel 12).
- Flag nell'orchestrator: `VIDEO_ENGINE` (env, default `notebooklm`). Con `VIDEO_ENGINE=hyperframes` si riattiva il promemoria HYPERFRAMES_NEXT. Non usarlo finché Marco non lo dice.
- Restano attive le regole di narrazione nel prompt NLM (NARRATION_NO_SCREEN): la voce non fa riferimento a ciò che si vede, numeri detti in modo generale e approssimato, nessuna citazione di sezioni, tabelle, capitoli o figure del paper.
- **STANDBY, non cancellare:** box `/workspace/canale/templates/{hf_engine.py,short_hyperframes_v8,long_hyperframes_v8}`, `/workspace/hyperframes_test/proj_edilizia*`, `/workspace/canale/Temp/enea/hyperframes_edilizia/`.
- Nei prossimi giorni si lavora sulla qualità del formato. Banco di prova: Dipoppa «Edilizia e migranti: così la mafia sale al Nord». Marco ha approvato la qualità delle immagini dello Short slideshow v2 e del lungo slideshow. La prova a infografica dinamica non lo convince ancora. Si sostituirà la pipeline solo quando lungo e corto saranno stabili e a Marco piaceranno.
- **Regole emerse per il nuovo formato:** transizioni morbide e di tanti tipi (mai due che si alternano). La panoramica segue il verso di lettura dell'immagine (di solito da sinistra a destra). Il crop resta sulla parte dell'immagine che corrisponde alla frase detta. Nessuna cifra scritta nelle immagini (i numeri solo nella voce). Nessun testo o sottotitolo impresso nel video. I personaggi hanno sempre il volto disegnato. Stile unico per paper, contenuto concreto. Storyboard approvato da Marco prima delle immagini.


---
description: Workflow /produzione — NotebookLM long + infografica + short opzionale
---

Genera e scarica asset grezzi. **Non** pulisce né carica.

## Checklist

1. Copertina **già approvata** da Marco; cartella `Cleaned/[Titolo]` pronta.
2. NotebookLM: Video Overview long + Infografica quadrata (sketch_note).
3. Download in `~/Downloads`: `*_raw.mp4`, `*_infografica.png`.
4. **Short (default 1/paper, salvo richiesta Marco di più)**:  
   `./workflow produzione --folder X --with-short` → richiede **notebooklm-mcp-cli ≥ 0.11.7** (`nlm create video --format short`).  
   Output: `{clean_title}_short1_raw.mp4`. Fallback UI se CLI fallisce.
5. Fine `/produzione` → passa a `/pulizia` (long+short).

```bash
./workflow produzione --folder Titolo_Cartella
./workflow produzione --folder Titolo_Cartella --with-short
./workflow produzione --folder Titolo_Cartella --with-short --short-count 1
```

## File Python
- `Execution/enea/notebooklm_orchestrator.py`
- `Execution/enea/short_assets.py`


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


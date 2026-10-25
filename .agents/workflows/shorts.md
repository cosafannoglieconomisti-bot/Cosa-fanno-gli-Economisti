---
description: Distingue SEO Shorts legacy vs produzione Short NotebookLM
---

## Due percorsi distinti

### A) Produzione Short NLM (nuovo contenuto, 1/paper default)
Pipeline principale: `/produzione --with-short` → `/pulizia --short` → dentro `/upload` (dopo YT long).
- Script: `notebooklm_orchestrator.py`, `short_assets.py`, `upload_short.py`, Buffer Reel via litter.catbox.
- Descrizione: `Video completo qui: https://youtu.be/[LONG_ID]`.
- Tracking: `shorts[]` **nested** sotto la riga long (mai top-level).

### B) `/shorts` SEO-only (legacy)
Ottimizza titoli/descrizioni di Short **già online** con titoli generici/data.
- Script: `Execution/romolo/batch_update_shorts.py`.
- Non genera né carica nuovi Short NLM.

---
description: Workflow /shorts per l'assegnazione automatica di titoli e descrizioni "hook"
---

Il workflow `/shorts` automatizza l'ottimizzazione SEO dei video brevi (Shorts) caricati sul canale, assicurando che ogni clip funga da gancio (hook) per i contenuti long-form corrispondenti.

### Procedura Operativa

1.  **Scansione Canale**: Il sistema recupera l'elenco di tutti i video del canale YouTube.
2.  **Identificazione Shorts**: Filtra i video con durata inferiore ai 60 secondi che presentano titoli generici (es. date come "11 aprile 2026", "Short", nomi file) o descrizioni incomplete. **I titoli-data sono la priorità assoluta di ottimizzazione.**
3.  **Analisi Contenuto**:
    -   Recupera la trascrizione dello Short via YouTube API (se disponibile) o tramite analisi audio (`Whisper`).
    -   Utilizza Gemini per identificare il tema economico/accademico trattato nella clip.
4.  **Matching Semantico**:
    -   Confronta il tema dello Short con i database dei video caricati (`Cleaned/` o titoli playlist).
    -   Identifica il video long-form "padre" che tratta lo stesso paper accademico.
5.  **Generazione Metadati (SOP Part 11)**:
    -   **Titolo**: Crea un titolo "Catchy" (Hook) di massimo 60 caratteri.
    -   **Descrizione**: Inserisce obbligatoriamente il link cliccabile `Video completo qui: https://youtu.be/[ID]` in una riga isolata (solitamente la seconda), preceduta da un hook potente e seguita da hashtag strategici (#shorts #economia #storia).
6.  **Aggiornamento**: Esegue il comando di update via YouTube Data API (`batch_update_shorts.py`).

### Casi Limite
- **Nessuna trascrizione**: Se l'audio manca o non è leggibile, il sistema richiede l'intervento manuale dell'utente su Telegram.
- **Matching multiplo**: In caso di ambiguità (es. due video sulla Mafia), il sistema sceglie il più recente o chiede conferma via bridge.

### Requisiti
- Accesso alle credenziali YouTube (`token_youtube.pickle`).
- Script `Execution/romolo/batch_update_shorts.py` aggiornato.

---

## 📋 File Python Utilizzati
1. `Execution/romolo/romolo_manage_channel.py` (Listing)
2. `Execution/romolo/batch_update_shorts.py` (Update)
3. `Execution/enea/generate_index_whisper.py` (Analisi opzionale)


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


# Enea — Produzione Video e Gestione Papers

Responsabile della produzione video e della gestione della libreria dei paper. Si occupa della pulizia dei video, della gestione di `Cleaned/` (ora a root) e di `Papers/`.

---

## 0. Workflow /paper (Selezione, Titolo, Copertina, Metadata)

La pipeline video inizia con la scelta del paper, il titolo catchy, la copertina 16:9 e l'approvazione metadata. La control plane primaria e' Codex chat; Telegram/Cesare e' legacy.

### SOP: Selezione e Setup Iniziale (gate order obbligatorio)

1. **Select paper**: `/paper` in Codex chat oppure `./workflow paper`. Codex elenca i PDF in `Papers/Da fare/` (**ricorsivamente**) e propone i **titoli accademici reali** del paper, non i nomi file. Marco seleziona il paper.
2. **Choose catchy title (approval)**: Codex estrae il testo (prime 3 pagine) con `batch_text_extractor.py` e propone 5 titoli catchy (max 5 parole, stile domanda). Marco approva (o modifica) il titolo.
3. **Generate + approve 16:9 cover**: Una volta scelto il titolo, Codex genera la copertina **16:9** (ChatGPT/Codex native `image_gen` → `Temp/assets/override_cover.png` → `generate_cover.py` copia solo; SOP comic arancio/nero/bianco + testo nativo). Marco approva o dice `rigenera`. **Non** archiviare ancora in `Cleaned/`.
4. **Draft + APPROVE METADATA (gate duro)**: Prima di qualsiasi archiviazione, Codex redige un **draft** `video_metadata.md` dal PDF e lo mostra a Marco. Il draft DEVE contenere:
   - **Titolo accademico reale** (dal PDF, non inventato)
   - **ALL authors** dal PDF (**vietato** auto-hallucinare / omettere / abbreviare elenchi)
   - **Journal**, **year**, **DOI** (dal PDF / fonti reali)
   - **YT description draft** che inizia con **«Lo studio…»**
   - **Content-specific tags only** (niente tag generici canale/journal-as-hashtag)
   - Marco deve dare **approvazione esplicita metadata** (o edit + re-approve). **Vietato** creare `Cleaned/`, spostare il PDF, scrivere il `video_metadata.md` finale, o avviare `/produzione` / attiva produzione **prima** di questa approvazione.
5. **Archive only after metadata approved**: Solo dopo metadata OK: crea `Cleaned/[Titolo_Scelto]`, sposta/rinomina PDF in `Cleaned/[Titolo_Scelto]/[Titolo_Accademico].pdf`, salva `copertina.png`, scrive il **final** `video_metadata.md`, aggiorna `active_pipeline.json`. Poi si può avviare produzione.

> [!IMPORTANT]
> **GATE METADATA**: `/paper` / Dom-Mer automation richiede che Marco **APPROVE METADATA** (draft `video_metadata.md`) **BEFORE** archiving to Cleaned e **BEFORE** starting produzione. Ordine: paper → titolo → cover → **metadata approve** → Cleaned archive → produzione.

6. **Titolo Forzato**: Il titolo catchy approvato diventa l'identificativo univoco per tutto il processo NotebookLM.

---

## 1. Pipeline di Generazione: NotebookLM

### Step 1: Forzatura Titolo (MANDATORIO)

Per garantire che NotebookLM generi il video con il titolo esatto scelto dall'utente:

1. **Rinominare temporaneamente** il file PDF con il `[Titolo Scelto]` prima dell'upload.
2. Oppure rinominare il Notebook stesso nell'interfaccia con il `[Titolo Scelto]` esatto.

### Step 2: Caricamento

Su NotebookLM, caricare il PDF tramite **Google Drive**.

### Step 3: Generazione Video (SOLO VIDEO)

> [!IMPORTANT]
> **BASTA OVERVIEW AUDIO**. L'utente esige **SOLO ed ESCLUSIVAMENTE la Video Overview**. Non generare mai la sola traccia audio.

**Prompt Ridigo (da inserire nel box di personalizzazione)**:
*"Please speak Italian. You are a conversational and engaging podcast host explaining economics papers. Be energetic but accurate. Usare possibilmente le figure del paper senza ritoccarle, esprimere i numeri a parole, linguaggio non roboante. **MANDATORIO: Il TITOLO in sovrimpressione nel video DEVE essere ESATTAMENTE: '[Titolo Scelto]'. Non riassumere o alterare il titolo.**"*

### Step 4: Download Asset Video & Infografica (MANDATORIO)

Per scaricare il VIDEO e l'INFOGRAFICA in modo affidabile, seguire la [SOP Download Deterministico](file:///Users/<USER>/Desktop/canale/Directives/enea/SOP_Download_Deterministico.md).

Questa procedura utilizza lo script `Execution/enea/notebooklm_asset_downloader.py` e garantisce la massima qualità originale. 



## SOP: NotebookLM Short (verticale, TEST 1/paper)

1. CLI (preferita, `notebooklm-mcp-cli>=0.11.7`): `nlm create video <nb> --format short --language it -y` via `notebooklm_orchestrator.py --with-short`.
2. Output raw: `{clean_title}_short1_raw.mp4` in `~/Downloads` (+ copia in `Cleaned/[Titolo]/` e `shorts/`).
3. Fallback UI: se la CLI fallisce, genera Short verticale in NotebookLM Studio, scarica e rinomina esattamente `{clean_title}_short1_raw.mp4`.
4. Pulizia: `./workflow pulizia --video {clean_title}_short1_raw.mp4` (delogo portrait-aware).
5. Upload Short **solo dopo** che il long ha `youtube_id`, descrizione con `Video completo qui: https://youtu.be/[LONG_ID]`.
6. Tracking nested sotto la riga long-form: `shorts: [{id, youtube_url, angle, status, ig_reel_url}]` — **non** creare voci top-level Short (conflitto GEMINI Part 12).

> [!IMPORTANT]
> **FINE WORKFLOW /PRODUZIONE**: Una volta che il video (`*_raw.mp4`) e l'infografica sono stati scaricati nella cartella `Downloads` dell'utente, il workflow `/produzione` è considerato **CONCLUSO**. Non procedere con la pulizia o l'archiviazione automatica in questa fase. Tutta la logica di post-processing (rimozione watermark, trimmaggio, ecc.) appartiene al workflow `/pulizia`.

---

## SOP: Generazione Infografica Quadrata

- **Enea** crea **una sola infografica quadrata (Square)** per ogni paper su NotebookLM (nel pannello Studio/Notebook Guide).
- **Livello di Dettaglio**: Selezionare **Dettagliato** (Dettagliato).
- **Prompt (Box "Descrivi uno stile, un colore o un punto focale")**:
  ```text
  Lingua: Italiano perfetto. Tono: Semplice, divulgativo ma scientificamente chiaro.
  Stile grafico: Estremamente accattivante, ricco di disegni ed emoji (molto visivo, ad esempio in stile sketch_note o simile, evitando griglie, tabelle o blocchi grigi noiosi).
  Varia il linguaggio visivo da un video all'altro (non ripetere sempre lo stesso layout/palette); resta sempre accattivante e ricco di disegni.

  REGOLE DI CONTENUTO:
  Spiega in modo conciso ma logicamente completo lo studio:
  1. IL DILEMMA: Qual è il problema che il paper vuole risolvere? (Usa un linguaggio semplice, es. "Gli amici cambiano il voto?").
  2. LA SCOPERTA: I dati e le scoperte principali in modo logico e consequenziale (es. "L'effetto del gruppo di amici è forte e misurabile").
  3. LA MORALE: Perché questa ricerca è importante per la vita reale (es. "Le opinioni nascono nel gruppo, non da soli").

  REGOLE VISIVE:
  - Niente muri di testo densi o frasi lunghe e complesse.
  - Ricco di elementi grafici (disegni, icone, emoji).
  - Usa SOLO elenchi puntati brevissimi (pochi punti chiari) ed emoji pertinenti.
  - **Formato**: Quadrata.
  ```
- **Salvataggio**: Generare l'infografica ma **NON scaricarla**. L'utente provvederà al download manuale in `~/Downloads`. Solo dopo il download manuale sarà possibile procedere con la pulizia watermark tramite `clean_infographic.py`.

### 2.1 Rimozione Watermark (NotebookLM) dalle Infografiche

> [!IMPORTANT]
> Tutte le infografiche NotebookLM hanno un watermark nell'angolo in basso a destra. Va **rimosso** prima di considerare il file definitivo.

- **Logica**: Rilevare il riquadro del watermark nell'angolo assoluto in basso a destra e **coprirlo con il colore di sfondo dominante** del riquadro (*Solid Fill*).
- **Automatizzazione**: Utilizzare uno script Python (PIL) per tracciare il colore di livello di sfondo dominante e coprire il watermark, garantendo un risultato pulito senza aloni.
- **Consolidamento**: Conservare SOLO il file dell'infografica pulito. Eliminare file raw intermedi dopo l'applicazione.

---

## SOP: Video Cleaning (FFmpeg)

### Obiettivo

Applicare logo/sfocatura sul watermark in basso a destra e trimmare l'outro di NotebookLM (2.5 secondi).

### Esecuzione

- **Script**: `execution/video_cleaner.py`
- **Input**: `<input_video.mp4> <paper_name_senza_ext> [percorso_pdf_originale]`
- **Output**: Salva il video pulito in `/Users/<USER>/Desktop/canale/Cleaned/[NomePaper]/[NomePaper]_cleaned.mp4`.

### Esempio di Utilizzo

```bash
python execution/video_cleaner.py ~/Downloads/video.mp4 L_ascesa_del_Male /path/to/paper.pdf
```

## 📋 File Python Utilizzati (In Ordine di Esecuzione)

1. `Execution/cesare/telegram_bot.py` (Interazione Bot e Stato)
2. `Execution/enea/batch_text_extractor.py` (Estrae testo PDF)
3. `image_gen` / motore immagine Codex (Generazione Copertina primaria)
4. `Execution/enea/generate_cover.py` (Legacy fallback, non raccomandato)
3. `Execution/enea/notebooklm_asset_downloader.py` (Download Video Nativo)
4. `Execution/enea/video_cleaner.py` (Pulizia Video/Watermark FFmpeg)
5. `Execution/enea/generate_index_whisper.py` (Generazione Indice)
6. `Execution/enea/clean_infographic.py` (Pulizia Watermark Infografica PIL) [Dopo Download Manuale]
7. `Execution/enea/youtube_uploader.py` (Upload YouTube)
8. `Execution/romolo/catalog_video.py` (Collocazione Playlist)
9. `Execution/marcello/buffer_post_single.py --platform instagram` (Instagram; Facebook sospeso)
10. `Execution/enea/video_cleanup.py` (Pulizia Root e Asset)

---

## SOP: Generazione Copertina (Thumbnail)

Quando è richiesta la creazione di una miniatura per YouTube, utilizzare le seguenti linee guida strutturali per il prompt Text-to-Image del tool immagine approvato:

- **Formato**: **16:9 only** (es. 1280×720). Vietato 1:1 come formato primario delle copertine/thumbnail. (Le **infografiche** restano quadrati 1:1.)
- **Motore**: ChatGPT/Codex native `image_gen` → salvare in `Temp/assets/override_cover.png` → `generate_cover.py` **copia solo** l'override. **NON** usare Gemini/Imagen né API keys da `.env` per le copertine.
- **Stile Visivo**: Graphic novel comic book style (stile fumetto), palette colori vibrante arancione, nero e bianco. Altissimo contrasto, stile vettoriale.
- **Soggetto**: Un'illustrazione a tema con il paper.
- **Testo Integrato (MANDATORIO)**: Il titolo ESATTO del video deve essere richiesto come **testo nativo integrato** nel prompt dell'AI (senza aggiungere fasce nere o font standard in post-produzione). Il testo deve essere preferibilmente bianco o arancione con contorni neri per risaltare, fondendosi in modo naturale con l'illustrazione.
- **Esempio di Prompt Base**: *"Comic book style YouTube thumbnail cover, 16:9 widescreen, orange and black monochrome color palette. High contrast. [Descrizione Scena]. Include the exact large text integrated inside the image as part of the comic cover: '[TITOLO ESATTO]'. The text must be in orange or black, fully integrated in the composition."*
- **Inpainting (Correzione)**: Qualora l'AI generi testi "spazzatura" (watermark o diciture casuali ai bordi), questi vanno rimossi tramite inpainting intelligente (Generative Fill) ripristinando il background sottostante, in modo che l'immagine rimanga pulita, identica e senza "toppe" coprenti di colore solido.

## SOP: Rimozione Watermark (NotebookLM) dalle Infografiche Quadrati Nativa

1. **Scelta dell'URL**: Estrarre l'URL diretto `lh3.googleusercontent.com` con `shadow_dom` dall'overlay dell'infografica (indici card row 0).
2. **Download Diretto**: Intercettare il download nativo bypassando sandboxes tramite tasti CMD+S nel file macro.
3. **Rimozione Tight Mask**: Eseguire il clean spec con un offset ridotto (W-130, H-45) per cancellare solo il pixel badge watermark.

## SOP: Pulizia video (default approvati post-Ambiente_o_consenso)

- **Watermark**: cover/fill solido, colore campionato dallo sfondo accanto al badge. Vietato delogo soft (macchie).
- **Trim outro**: ~3.5–4s guidato da RMS audio; tenere la voce di chiusura; non usare 2.5s aggressivo.
- Implementazione: `video_cleaner.py` + `short_assets.delogo_box_for_resolution` (box per drawbox fill).
- Cleanup finale post-upload: `video_cleanup.py` cancella anche `shorts/**/*.mp4` e `*.pdf`.

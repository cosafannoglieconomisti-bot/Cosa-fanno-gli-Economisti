# Enea — Produzione Video e Gestione Papers

Responsabile della produzione video e della gestione della libreria dei paper. Si occupa della pulizia dei video, della gestione di `Cleaned/` (ora a root) e di `Papers/`.

---

## 0. Selezione Paper e Titolo (Interattiva Telegram)

Prima di passare a NotebookLM, la selezione del paper e la definizione del titolo avvengono interattivamente tramite il Bot Telegram.

### SOP: Selezione Titolo Catchy

1. **Comando**: `/paper` su Telegram.
2. **Visualizzazione**: Il bot legge i file `.pdf` in `Papers/Da fare/` (**ricorsivamente**, includendo tutte le sottocartelle), ricava il Titolo effettivo (usando Gemini) e lo mostra sui pulsanti.
3. **Approvazione**: L'utente clicca il paper. Enea estrae il testo (prime 3 pagine) con `batch_text_extractor.py` e chiede a Gemini 5 titoli catchy. **MANDATORIO**: Ogni proposta deve essere di **massimo 5 parole** e in stile **catchy/domanda**.
4. **Consolidamento**: L'utente clicca su un'opzione numerata. Il bot crea la cartella `Cleaned/[Titolo_Scelto]`, inizializza `video_metadata.md` e salva la sessione attiva in `active_pipeline.json`.

---

## 0.5 Generazione Copertina (Interattiva Telegram)

Dopo la selezione del titolo, la copertina viene generata e approvata direttamente su Telegram prima di passare a NotebookLM.

### SOP: Generazione e Approvazione

1. **Comando**: `/copertina` su Telegram.
2. **Visione**: Il bot invia la copertina per il titolo attivo.
3. **Decisione**:
   - `✅ Approvata`: Cliccalo per salvare direttamente in `Cleaned/[Titolo]/thumbnail.png`.
   - `🔄 Rigenera`: Cliccalo per creare un'altra variante.

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

Per scaricare il VIDEO e l'INFOGRAFICA in modo affidabile, seguire la [SOP Download Deterministico](file:///Users/marcolemoglie_1_2/Desktop/canale/Directives/enea/SOP_Download_Deterministico.md).

Questa procedura utilizza lo script `Execution/enea/notebooklm_asset_downloader.py` e garantisce la massima qualità originale. 

> [!IMPORTANT]
> **FINE WORKFLOW /PRODUZIONE**: Una volta che il video (`*_raw.mp4`) e l'infografica sono stati scaricati nella cartella `Downloads` dell'utente, il workflow `/produzione` è considerato **CONCLUSO**. Non procedere con la pulizia o l'archiviazione automatica in questa fase. Tutta la logica di post-processing (rimozione watermark, trimmaggio, ecc.) appartiene al workflow `/pulizia`.

---

## SOP: Generazione Infografica Quadrata

- **Enea** crea **una sola infografica quadrata (Square)** per ogni paper su NotebookLM (nel pannello Studio/Notebook Guide).
- **Livello di Dettaglio**: Selezionare **Dettagliato** (Dettagliato).
- **Prompt (Box "Descrivi uno stile, un colore o un punto focale")**:
  ```text
  Lingua: Italiano. Stile: Infografica moderna, pulita e minimale (tipo Dashboard o Post LinkedIn/Instagram). Tono: Divulgativo ed energetico. Colori: Vivaci ma professionali, ad alto contrasto per facilitare la lettura. 

  FOCUS DEL CONTENUTO:
  1. IL DILEMMA: Qual è il problema che il paper vuole risolvere? (Usa un linguaggio semplice).
  2. LA SCOPERTA: I dati più sorprendenti. Esprimi i numeri in modo visivo (es. "1 su 3" invece di "33%").
  3. LA MORALE: Perché questa ricerca è importante per noi tutti nella vita reale?

  REGOLE VISIVE:
  - Niente muri di testo densi.
  - Usa il piu possibile immagini, sennò che infografica è?
  - Usa SOLO elenchi puntati brevi ed emoji per ogni sezione.
  - Enfatizza i titoli e i numeri chiave.
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
- **Output**: Salva il video pulito in `/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/[NomePaper]/[NomePaper]_cleaned.mp4`.

### Esempio di Utilizzo

```bash
python execution/video_cleaner.py ~/Downloads/video.mp4 L_ascesa_del_Male /path/to/paper.pdf
```

## 📋 File Python Utilizzati (In Ordine di Esecuzione)

1. `Execution/cesare/telegram_bot.py` (Interazione Bot e Stato)
2. `Execution/enea/batch_text_extractor.py` (Estrae testo PDF)
3. `Execution/enea/notebooklm_asset_downloader.py` (Download Video Nativo)
4. `Execution/enea/video_cleaner.py` (Pulizia Video/Watermark FFmpeg)
5. `Execution/enea/generate_index_whisper.py` (Generazione Indice)
6. `Execution/enea/clean_infographic.py` (Pulizia Watermark Infografica PIL) [Dopo Download Manuale]
7. `Execution/enea/youtube_uploader.py` (Upload YouTube)

---

## SOP: Generazione Copertina (Thumbnail)

Quando è richiesta la creazione di una miniatura per YouTube, utilizzare le seguenti linee guida strutturali per il prompt Text-to-Image (es. Midjourney / Imagen 3):

- **Formato**: Quadrato 1:1 (es. 1024x1024 o 640x640 per retrocompatibilità).
- **Stile Visivo**: Graphic novel comic book style (stile fumetto), palette colori vibrante arancione, nero e bianco. Altissimo contrasto, stile vettoriale.
- **Soggetto**: Un'illustrazione a tema con il paper.
- **Testo Integrato (MANDATORIO)**: Il titolo ESATTO del video deve essere richiesto come **testo nativo integrato** nel prompt dell'AI (senza aggiungere fasce nere o font standard in post-produzione). Il testo deve essere preferibilmente bianco o arancione con contorni neri per risaltare, fondendosi in modo naturale con l'illustrazione.
- **Esempio di Prompt Base**: *"Comic book style cover, orange and black monochrome color palette. High contrast. [Descrizione Scena]. Include the exact large text integrated inside the image as part of the comic cover: '[TITOLO ESATTO]'. The text must be in orange or black, fully integrated in the composition."*
- **Inpainting (Correzione)**: Qualora l'AI generi testi "spazzatura" (watermark o diciture casuali ai bordi), questi vanno rimossi tramite inpainting intelligente (Generative Fill) ripristinando il background sottostante, in modo che l'immagine rimanga pulita, identica e senza "toppe" coprenti di colore solido.

## SOP: Rimozione Watermark (NotebookLM) dalle Infografiche Quadrati Nativa

1. **Scelta dell'URL**: Estrarre l'URL diretto `lh3.googleusercontent.com` con `shadow_dom` dall'overlay dell'infografica (indici card row 0).
2. **Download Diretto**: Intercettare il download nativo bypassando sandboxes tramite tasti CMD+S nel file macro.
3. **Rimozione Tight Mask**: Eseguire il clean spec con un offset ridotto (W-130, H-45) per cancellare solo il pixel badge watermark.

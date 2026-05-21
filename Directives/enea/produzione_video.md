# Enea — Produzione Video e Gestione Papers

Responsabile della produzione video e della gestione della libreria dei paper. Si occupa della pulizia dei video, della gestione di `Cleaned/` (ora a root) e di `Papers/`.

---

## 0. Workflow /paper (Selezione, Titolo e Copertina)

La pipeline video inizia con la scelta del paper, la definizione del titolo e la creazione della copertina, tutto gestito interattivamente via Telegram.

### SOP: Selezione e Setup Iniziale

1. **Comando**: `/paper` su Telegram.
2. **Scelta Paper**: Il bot elenca i PDF in `Papers/Da fare/` (**ricorsivamente**). L'utente seleziona il paper.
3. **Titoli Catchy**: Il bot estrae il testo (prime 3 pagine) con `batch_text_extractor.py` e propone 5 titoli catchy (max 5 parole, stile domanda).
4. **Generazione Copertina**: Una volta scelto il titolo, il bot lancia immediatamente `generate_cover.py` per proporre una copertina (Comic Style, Orange/Black/White) con il titolo integrato.
5. **Approvazione e Archiviazione**:
   - `✅ Approva`: Il bot recupera il **Titolo Accademico** reale del paper, crea la cartella `Cleaned/[Titolo_Scelto]`, sposta e rinomina il PDF in quella cartella, salva `copertina.png` e inizializza `video_metadata.md`.
   - `🔄 Rigenera`: Il bot genera una nuova variante della copertina.
6. **Titolo Forzato**: Il titolo approvato diventa l'identificativo univoco per tutto il processo NotebookLM.

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
3. `Execution/enea/generate_cover.py` (Generazione Copertina AI)
3. `Execution/enea/notebooklm_asset_downloader.py` (Download Video Nativo)
4. `Execution/enea/video_cleaner.py` (Pulizia Video/Watermark FFmpeg)
5. `Execution/enea/generate_index_whisper.py` (Generazione Indice)
6. `Execution/enea/clean_infographic.py` (Pulizia Watermark Infografica PIL) [Dopo Download Manuale]
7. `Execution/enea/youtube_uploader.py` (Upload YouTube)
8. `Execution/romolo/catalog_video.py` (Collocazione Playlist)
9. `Execution/marcello/buffer_post_single.py` (Upload Facebook & Instagram)
10. `Execution/enea/video_cleanup.py` (Pulizia Root e Asset)

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

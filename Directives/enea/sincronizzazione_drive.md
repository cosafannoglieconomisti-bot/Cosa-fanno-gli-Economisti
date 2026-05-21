# Enea SOP — Sincronizzazione e Upload via Google Drive

Questa direttiva descrive la procedura standard per alimentare NotebookLM superando i blocchi delle finestre di dialogo native di macOS.

---

## 📅 Flusso Operativo

### Step 1: Preparazione File (Copia Locale)
Prima di interagire con il browser, il file PDF del paper deve essere copiato nella cartella locale di Google Drive (File stream) installata sul Mac.
- **Percorso di origine**: `Cleaned/` o `Papers/`
- **Destinazione**: `/Users/marcolemoglie_1_2/Library/CloudStorage/GoogleDrive-[Utenza]/Il mio Drive/`
- **Comando di riferimento**:
  ```bash
  cp "[Percorso_Originale_PDF]" "[Percorso_Google_Drive]/Il mio Drive/"
  ```
- **Buffer**: Attendere sempre ~10-15 secondi per consentire l'allineamento cloud del client desktop.

---

### Step 2: Selezione su NotebookLM
All'interno del Quaderno di NotebookLM (Dashboard o Workspace vuota):

1. **Clic sulla fonte "Drive"**: 
   - Utilizzare i selettori HTML standard per cliccare sul bottone `drive Drive` o `Drive` (DOM accessibile).
2. **Aggancio del Picker Iframe (Navigazione Meccanica)**:
   - Essendo il Picker di Google un dominio Cross-Origin (CORS protetto), i selettori Javascript non possono leggerne la lista.
   - **Soluzione**: Simulare la pressione tastiera o clic coordinate native:
     - **Tab / Freccia Giù**: Per posizionarsi sul primo file della lista "Recenti" (che è sempre l'ultimo inserito).
     - **Spacebar / Enter**: Per selezionare il file.
     - **Inviare Enter finale**: Per confermare la scelta (Pulsante "Seleziona").

---

### Step 3: Verifica Caricamento
1. Attendere 10 secondi per l'indicizzazione.
2. Effettuare una scansione col testuale sulla barra `Fonti` per rintracciare il nome del file.
3. Procedere con la generazione audio o video overview come descritto in `produzione_video.md`.

## 📋 File Python Utilizzati
- `Execution/enea/batch_text_extractor.py` (Analisi e Metadati)
- `Execution/enea/video_cleaner.py` (Video Cleaning)
- `Execution/enea/generate_index_whisper.py` (Generazione Indice)
- `Execution/enea/youtube_uploader.py` (Upload YouTube)

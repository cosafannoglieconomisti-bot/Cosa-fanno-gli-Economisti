# Workflow: /download

Scarica e organizza i PDF dei paper dalla cartella Downloads del sistema.

## Obiettivo
Ingerire automaticamente i nuovi paper scaricati nell'ultimo giorno, estraendo il titolo accademico reale e spostandoli nella cartella di lavoro `Papers/Da fare/`.

## Trigger
- `/download`: Avvia il processo di scansione e organizzazione.

## Step del Workflow

1. **Scansione Downloads**: Cerca file `.pdf` scaricati/modificati nelle ultime 24 ore nella cartella `~/Downloads`.
2. **Filtro Duplicati**: Ignora i file che sono già presenti in `Papers/Da fare/` o che sono già stati processati e archiviati in `Cleaned/`.
3. **Estrazione Titolo (AI)**: Per ogni nuovo paper, estrae il testo delle prime 3 pagine e usa Gemini Flash per identificare il **Titolo Accademico Reale**.
4. **Organizzazione**: Rinomina il file con il titolo pulito e lo sposta in `Papers/Da fare/`.

## Tool Utilizzati
- `Execution/enea/paper_downloader.py`: Script di gestione file e integrazione AI.

## Output Attesi
- Conferma del numero di paper trovati e spostati con successo.
- File rinominati correttamente in `Papers/Da fare/`.

// turbo
// run: /Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 /Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/paper_downloader.py

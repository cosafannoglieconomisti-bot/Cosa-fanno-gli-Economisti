# Romolo — Gestione Canale YouTube

Responsabile dell'upload dei video, della gestione dei metadati, delle miniature e dell'interazione con l'API di YouTube (Analytics, commenti).

---

## Task Ricorrenti

1.  **Analytics Report**: Ogni volta che viene chiesto di "gestire il canale", Romolo deve generare un report dettagliato (`analytics_report.txt`) con metriche di performance e commenti.
2.  **Gestione Commenti**: Risposta automatica e gentile ai nuovi commenti sul canale per favorire la community.

---

## SOP: Generazione Indice (Whisper)

### Obiettivo
Estrarre la trascrizione del video per creare capitoli automatici con timestamp precisi.

### Esecuzione
- **Script**: `execution/generate_index_whisper.py`
- **Input**: `<video_path> <output_log_txt>`
- **Output**: Genera un file `.tmp/output_log.txt` con la trascrizione a blocchi e timestamp.

> [!IMPORTANT]
> **Formato Mandatorio** per l'indice finale (da incollare nella descrizione):
> - `00:00 | Intro` (Senza testo aggiuntivo)
> - `XX:XX | [Titolo Capitolo]`
> - `XX:XX | Conclusioni` (Senza testo aggiuntivo)

---

## 📋 File Python Utilizzati
- `Execution/romolo/generate_index_whisper.py`

## SOP: Upload Video e Metadati

### Obiettivo
Caricare un video (Lungo) su YouTube con privacy `scheduled` (programmata).

### 🕒 Regole di Programmazione (MANDATORIO)
- **Orario**: Il video **Lungo** va programmato per le **9:00 del giorno successivo** al caricamento.

### Esecuzione
- **Script**: `execution/youtube_uploader.py`
- **Input**: `<video_file> <title> <metadata_file_md>`
- **Output**: Carica il video e restituisce il Video ID.

### Esempio di Utilizzo
```bash
python execution/youtube_uploader.py Cleaned/Paper1/video.mp4 "Mio Titolo" .tmp/metadata.md
```

## SOP: Report Canale (Analytics + Consigli AI)

### Obiettivo
Generare un report con i dati degli ultimi 30 giorni e consigli strategici di crescita avanzati forniti da un LLM che simula un Social Media Manager esperto.

### Esecuzione
- **Script**: `Execution/romolo/romolo_manage_channel.py`
- **Output**: Genera un file `.txt` in `Temp/romolo/analytics_reports/` che viene poi intercettato e inviato dal bot Telegram. *(I messaggi che superano il limite dei 4096 caratteri vengono automaticamente suddivisi dal bot)*.

---

## SOP: Ottimizzazione YouTube Shorts (High-Conversion)

### Obiettivo
Trasformare ogni Short in un gancio (hook) per i video long-form, massimizzando il cross-traffic e gli iscritti.

### Regole SEO (MANDATORIO)
1.  **Titolo Hook**: Massimo 60 caratteri. Deve contenere una domanda o una curiosità forte (es: *"Mafia: nata per colpa della siccità?"*). Include hashtag `#shorts` e `#economia`.
2.  **Descrizione**:
    -   **Riga 1**: Deve contenere il link al video completo: `Video completo qui: https://youtu.be/[ID]`.
    -   **Riga 2**: Breve testo di valore aggiunto.
    -   **Hashtag**: Sempre includere `#shorts`, `#economia` e 1-2 tag specifici.

### Esecuzione Automatica
- **Workflow**: `/shorts`
- **Script**: `Execution/romolo/batch_update_shorts.py`
- **Logica**: Mapping basato su trascrizione e matching semantico con i video in `Cleaned/`.

## SOP: Gestione Playlist Tematiche

### Obiettivo
Organizzare i video lunghi del canale in 8 playlist tematiche predefinite per massimizzare la discoverability e l'organizzazione dei contenuti.

### Categorie (MANDATORIO)
1. Economia del Crimine e Mafie
2. Economia Politica e Istituzioni
3. Storia Economica e Sviluppo
4. Economia della Cultura, Società e Religione
5. Economia del Lavoro, Discriminazione e Disuguaglianze
6. Economia Pubblica, Welfare e Demografia
7. Economia dei Media e dello Sport
8. Top Video (Cosa Fanno Gli Economisti)

### Inizializzazione (Una-Tantum)
- **Script**: `Execution/romolo/create_playlists_batch.py`
- **Output**: Crea le playlist sul canale e assegna retroattivamente i video.

### Esecuzione Automatica (Nuovi Video)
- **Workflow**: `/playlist` via Telegram
- **Script**: `Execution/romolo/catalog_video.py`
- **Logica**: Utilizza Gemini per categorizzare il video basandosi sul titolo e sui metadati, poi lo aggiunge alla playlist YouTube appropriata e aggiorna il file `video_tracking.json`.

---

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/cesare/telegram_bot.py` (Intercetta i comandi `/report`, `/shorts` e `/playlist`)
2. `Execution/romolo/romolo_manage_channel.py` (Listing e Analytics)
3. `Execution/romolo/batch_update_shorts.py` (Update metadati via API)
4. `Execution/romolo/create_playlists_batch.py` (Inizializzazione Playlist)
5. `Execution/romolo/catalog_video.py` (Catalogazione nuovi video)

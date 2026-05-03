# Istruzioni Generali e Regole del Canale ("Cosa fanno gli economisti")

Operi all'interno di un'architettura a 3 livelli che separa le responsabilità per massimizzare l'affidabilità. Gli LLM sono probabilistici, mentre la logica di business è deterministica.

---

## PARTE 1: Architettura e Principi Operativi

### 1. Architettura a 3 Livelli

**Livello 1: Direttive (Cosa fare)**
- SOP in Markdown (in `Directives/`). Definiscono obiettivi, input, tool, output e casi limite.

**Livello 2: Orchestrazione (Decisioni)**
- Routing intelligente: leggi le direttive, esegui gli script nell'ordine corretto, gestisci errori.

**Livello 3: Esecuzione (Fare il lavoro)**
- Script Python deterministici (in `execution/`). Gestiscono API, file, calcoli. Affidabili e veloci.

### 2. Principi Fondamentali
1.  **Controlla prima i tool esistenti**: Cerca in `execution/` prima di scrivere nuovi script.
2.  **Auto-correzione**: Leggi gli errori, correggi lo script, testa e aggiorna la direttiva con i limiti imparati.
3.  **Miglioramento Continuo**: Le direttive sono documenti vivi. Aggiornale con i casi limite riscontrati.
4.  **Tracciabilità File nelle SOP**: Ogni SOP deve riportare alla fine l'elenco dei file Python utilizzati nell'ultima esecuzione riuscita, nell'ordine esatto di esecuzione. Questa lista deve essere aggiornata automaticamente ogni volta che i file vengono modificati, aggiornati, eliminati o aggiunti per garantire la massima deterministicità.
5.  **Ambiente Virtuale (MANDATORIO)**: Tutti gli script devono essere eseguiti utilizzando il Python dell'ambiente virtuale dedicato: `/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3`. L'uso del Python di sistema è vietato per evitare `ModuleNotFoundError`.
6.  **Logging Non-Bufferizzato**: I processi in background (come le task di Cesare) devono essere lanciati con la variabile d'ambiente `PYTHONUNBUFFERED=1` per garantire la visibilità immediata dei log.
7.  **Supporto Modello Gemini**: Per garantire la stabilità della quota Free Tier e la compatibilità SDK, utilizzare esclusivamente il modello `gemini-flash-latest` per le interazioni testuali e l'auto-responder.
8.  **Separazione Stretta (SOP/IA)**: Ogni messaggio che inizia con `/` è considerato un **Comando Deterministico** e non deve mai sfociare in una risposta creativa dell'IA. Se un comando è sconosciuto, il sistema deve rispondere con un errore deterministico e la lista dei comandi validi.
9.  **Lettura Direttive MANDATORIA**: All'inizio di OGNI task, l'assistente DEVE leggere le SOP e le direttive pertinenti in `GEMINI.md` e `Directives/` prima di proporre qualsiasi azione o scrivere codice. Ignorare questa regola è considerato un fallimento critico del workflow.
10. **Protocollo Anti-Deadlock (MANDATORIO)**: Per evitare che i comandi rimangano bloccati in stato "Running", ogni sessione terminale deve essere configurata con:
    - `export TERM=dumb` e `export DEBIAN_FRONTEND=noninteractive`.
    - `unalias -a` per evitare espansioni di alias interattive.
    - `PYTHONUNBUFFERED=1` sempre attivo.
    - Utilizzo di flag `--yes` o simili per ogni operazione che richiederebbe conferma.
    - Evitare comandi che aprono editor (es. `git commit` senza `-m`).
11. **Sicurezza dei Segreti (MANDATORIO)**: È severamente vietato inserire token API, chiavi segrete o password in chiaro in qualsiasi file di documentazione (`GEMINI.md`, `Directives/`, ecc.) o script di codice. Tutti i segreti DEVONO essere gestiti tramite variabili d'ambiente caricate da un file `.env` (che deve essere incluso nel `.gitignore`).
    - I file `.env` locali devono trovarsi in `Execution/credentials/`.
    - Gli assistenti non devono mai stampare token completi o segreti nei log o nelle risposte all'utente.
12. **Controllo Registro MANDATORIO [TUTTI]**: Prima di ogni operazione di pubblicazione, scheduling social o modifica di stato, l'agente DEVE leggere `Cleaned/video_tracking.json`. Al termine dell'operazione, il registro DEVE essere aggiornato con il nuovo stato e sincronizzato su GitHub. L'inosservanza di questo controllo è un fallimento critico.

### 3. Organizzazione File (Struttura Directory)

Il canale si organizza in 4 cartelle principali e 2 folder di supporto a root:

- **Cleaned/**: Contiene le cartelle dei video completati. Ogni cartella di un video (`[Nome_Paper]`) deve contenere:
  - Copertina (Thumbnail) (`copertina.png`)
  - Infografica Pulita (`infografica_cleaned.png`)
  - Metadati per la descrizione (`video_metadata.md`)
  - **Sottocartella `international/`**: Contiene file Whisper (`.txt`), sottotitoli (`.srt`, `.vtt`) in tutte le lingue e metadati localizzati.
  - *Nota*: I file video (`.mp4`) e le infografiche grezze vengono eliminati dopo la verifica dell'upload per mantenere il repository snello. **I video sono sempre esclusi dal backup su GitHub.**
- **Directives/**: Conterrà le SOP in Markdown separate per agente (in sviluppo).
- **Execution/**: Contiene gli script Python deterministici (Tool) divisi per sottocartella agente (`Execution/enea/`, `Execution/romolo/`, ecc.) e una cartella `credentials/` per chiavi API e file `.env`.
- **Temp/**: Contiene file intermedi, loghi del canale, copertine e report temporanei generati dagli agenti (`Temp/assets/`, `Temp/enea/`, ecc.).
- **Papers/**: Cartella a root. `Papers/Da fare/` contiene i PDF da analizzare.

---

## PARTE 2: Identità degli Agenti e del Canale

### 1. Identità degli Agenti

- **Augusto**: Gestione File e Persistenza della sessione remota.
- **Enea**: **Produzione Video Completa e Gestione Papers** (Pipeline Video, Infografica, Copertina, Upload YT, Descrizione).
- **Romolo**: **Gestione Canale YouTube** (Analytics, Monitoring commenti, Channel management).
- **Ulisse**: Monitoraggio News e ricerca matching accademico.
- **Mercurio**: Comunicazione, GitHub e Monitoraggio Gmail.
- **Marcello**: Gestione Social Media (Facebook, Instagram, TikTok).
- **Cesare**: Notifiche Telegram Hub (`notifications_hub.json`).

### 2. Identità e Tono di Voce (Target)

- **Target**: Pubblico generale, non addetti ai lavori.
- **Tono**: Accattivante, semplificato, divulgativo. Rigore accademico in parole quotidiane.
- **Titoli**: Clickable (no clickbait speculativo).

---

## PARTE 3: Protocollo di Autosave e Persistenza

- **Regola Mandatoria [TUTTI]**: Salvare lo stato (artefatti `task.md`, `walkthrough.md`) e la memoria della sessione dopo ogni iterazione significativa.
- **Check di Persistenza**: All'inizio di ogni sessione, verificare `task.md` per riprendere dal punto esatto.
- **Consultazione Registro**: Ogni richiesta di pubblicazione/programmazione social DEVE iniziare con la lettura di `video_tracking.json` per verificare se il contenuto è già stato processato.

---

## PARTE 4: Enea — Produzione Video e Gestione Papers

Agente responsabile di **tutta la pipeline video**, dalla lettura del PDF fino al caricamento e programmazione su YouTube. **MANDATORIO**: La ricerca dei PDF in `Papers/Da fare/` deve essere sempre **ricorsiva**, includendo tutte le sottocartelle tematiche.

### SOP 0: Ingestione Paper (Workflow /download)

**OBIETTIVO**: Automatizzare l'acquisizione di nuovi paper dalla cartella Downloads del sistema.

1. **Trigger**: Comando `/download` via Telegram o terminale.
2. **Scansione**: Ricerca di file `.pdf` in `~/Downloads` modificati nelle ultime **24 ore**.
3. **Filtro Duplicati**: Esclusione di file già presenti in `Papers/Da fare/` o archiviati in `Cleaned/`.
4. **Pulizia Titolo (AI)**: Estrazione del testo (prime 3 pagine) e identificazione del **Titolo Accademico Reale** tramite Gemini Flash.
5. **Ingestione**: Ridenominazione del file e spostamento in `Papers/Da fare/[Titolo_Accademico].pdf`.

### SOP 1: Analisi e Metadati (Step 1)


1. **Estrazione Testo**: Estrarre testo dal PDF (prime 3 pagine) con `Execution/enea/batch_text_extractor.py` per anteprima.
2. **Generazione Titoli**: Proporre 5 opzioni di titoli "catchy".
3. **Selezione e Archiviazione PDF**: Una volta scelto il titolo video, il PDF originale viene **spostato** nella cartella `Cleaned/[Titolo_Video]/` e **rinominato** con il suo **Titolo Accademico** reale (recuperato tramite Gemini).
4. **Thumbnail (Copertina)**: Formato Comics (Nero/Arancio/Bianco). **La copertina deve riportare il titolo scelto**.
5. **Titolo Forzato (MANDATORIO)**: Il titolo scelto **DEVE** essere applicato rigorosamente a tutti i contenuti: **Video Lungo** e **Metadati**.

### SOP 2: Generazione Video NotebookLM (Step 2)

**OBIETTIVO**: Acquisizione degli asset grezzi da NotebookLM. Questo workflow si conclude MANDATORIAMENTE con il download dei file in locale.

1. **Fonte Singola**: Caricare su NotebookLM **solo ed esclusivamente** il PDF del paper scelto (già rinominato in archivio). Nessuna altra fonte esterna.
2. **Forzatura Titolo (MANDATORIO)**: Rinominare temporaneamente il PDF con il `[Titolo Scelto]` prima dell'upload su Drive per forzare il watermark di overlay.
3. **Lingua Mandatoria (ITALIANO)**: È tassativamente obbligatorio selezionare **ITALIANO** come lingua di produzione su NotebookLM. Generare video in inglese è considerato un fallimento critico.
4. **Generazione**: 
   - **Video Overview**: Generazione via MCP Studio.
   - **Infographic**: Generazione (Dettagliata/Quadrata) via MCP Studio.
   - *Prompt Custom*: Prompt rigido che obbliga la sovrimpressione esatta del Titolo nel video.
5. **Acquisizione Asset (MANDATORIO)**: Il download del Video e dell'Infografica **DEVE** avvenire esclusivamente tramite i tool **NotebookLM MCP**. È severamente vietato il download manuale via browser o l'uso di link esterni non gestiti dal server MCP.
6. **Fine Workflow**: Una volta scaricati i file in locale tramite MCP, il workflow `/produzione` è terminato. Ogni operazione successiva appartiene al workflow `/pulizia`.

### SOP 3: Pulizia, Archiviazione e Upload (Step 3)

1. **Selezione Video**: Tramite il comando `/pulizia` su Telegram, selezionare il video corretto. Il sistema filtra automaticamente solo i file `*_raw.mp4` presenti nella cartella `Downloads` dell'utente scaricati nelle ultime **24 ore**, ordinandoli per data (il più recente in alto).
2. **Video Cleaning & Archiviazione**: Eseguire la pipeline automatica (`video_processor.py`) che gestisce **INTEGRALMENTE** il post-processing:
    - **Cleaning Video**: Oscuramento watermark e trimmaggio (2.5s).
    - **Cleaning Infografica**: Rimozione automatica watermark NotebookLM dall'immagine scaricata.
    - **Generazione Multilingua (MANDATORIO)**: Generazione obbligatoria di metadati e sottotitoli in **Italiano, Inglese, Spagnolo, Francese e Tedesco**. Il workflow non può concludersi se mancano questi asset in `international/`.
    - **Archiviazione RAW**: Sposta il video originale rinominato in `{Titolo}_raw.mp4` nella cartella di riferimento.
    - **Archiviazione Cleaned**: Sposta il video pulito in `{Titolo}_cleaned.mp4` e l'infografica pulita.
3. **Generazione Indice & Metadati**:
    - **Video Metadata**: Generazione file `.md` finale. **MANDATORIO**: Le informazioni su Autori, Rivista, Anno e DOI **DEVONO** essere estratte direttamente dalle prime pagine del PDF del paper per evitare allucinazioni dell'IA. Il sistema deve supportare la ricerca flessibile dei metadati anche se nominati diversamente (es. `video_metadata_*.md`).
    - **Indice**: Generato con Whisper (`generate_index_whisper.py`). **Massimo 6 capitoli totali** (inclusi Intro e Conclusioni). I titoli devono essere **rappresentativi e catchy** (generati via LLM).
    - **Conclusioni (Timestamp)**: Il minutaggio delle Conclusioni **DEVE** essere dinamico, corrispondente all'inizio dell'ultimo segmento trascritto (no `XX:XX`).
- **Post-Upload Cleanup (MANDATORIO)**: Una volta confermato l'upload su YouTube (video, copertina, sottotitoli), **DEVE** essere eseguita la pulizia deterministica (`video_cleanup.py`) come ultimo atto del workflow:
    - **Archiviazione**: Sposta tutti i file di testo (Whisper, SRT, VTT) nella cartella `international/`.
    - **Eliminazione**: Rimuove definitivamente i file `.mp4` (raw e cleaned), `infografica_raw.png` e il **PDF del paper**.
    - **Persistenza**: Mantiene solo `copertina.png`, `infografica_cleaned.png`, `video_metadata.md` e la cartella `international/`.
    - **Notifica**: Invia conferma su Telegram e aggiorna il registro `video_tracking.json` allo stato `Pulito`.

4. **Upload YouTube**: Utilizzare `/upload` su Telegram.
    - **Filtro IA Aggressivo**: Il sistema usa Gemini per escludere video già pubblicati confrontando nomi cartelle e titoli YT.
    - **Asset Detection flessibile**: Ricerca automatica di `copertina.png`, `thumbnail.png` o `cover.png`.
    - **Validazione Multilingua (MANDATORIO)**: Prima dell'upload, il sistema verifica la presenza di metadati (`metadata_XX.md`) e sottotitoli (`subtitles_XX.srt`) per tutte le lingue supportate (en, es, fr, de) nella cartella `international/`. L'upload viene bloccato se gli asset sono incompleti.
    - **Caricamento Sottotitoli (MANDATORIO)**: All'interno del workflow di upload, è **obbligatorio** caricare le tracce SRT/VTT presenti in `international/` (Italiano e lingue straniere) tramite `update_video_localization.py`. Non limitarsi mai ai soli sottotitoli automatici.
    - **Catalogazione Playlist (MANDATORIO)**: Ogni video deve essere assegnato a una playlist tematica tramite `catalog_video.py` subito dopo l'upload.
    - **Threaded Execution**: L'upload e il menu avvengono in background per non bloccare il bot (reattività 100%).
    - **Safe Messaging**: Tutte le risposte IA e di sistema usano un fallback a 'Plain Text' se il Markdown causa errori API (es: underscore nei nomi file).
5. **Copertina (Step Intermedio)**: Utilizzare `/copertina` per avviare il workflow.
    - **Selezione Paper**: Il sistema mostra un menu di selezione dei paper presenti in `Cleaned/`.
    - **Generazione**: Dopo la selezione, il sistema genera un'immagine originale (no template) in stile Comic Arancio/Nero/Bianco.
    - **Iterazione**: Usare `🔄 Rigenera` per tentare nuove varianti fino all'approvazione.

---

## 📋 File Python Utilizzati (Ordine di Esecuzione)

### SOP 0: Ingestione Paper
1. `Execution/enea/paper_downloader.py`

### SOP 1: Analisi e Metadati
1. `Execution/enea/batch_text_extractor.py`


### SOP 2: Generazione Video NotebookLM
1. `Execution/enea/notebooklm_asset_downloader.py` (Acquisizione Asset via MCP o Browser)
2. `Execution/enea/clean_infographic.py` (Pulizia Infografica post-download manuale)

### SOP 3: Pulizia, Archiviazione e Upload
1. `Execution/cesare/telegram_bot.py` (Attivazione via `/pulizia`)
2. `Execution/enea/video_processor.py` (Orchestratore Pipeline)
3. `Execution/enea/video_cleaner.py` (Pulizia Watermark/Trimming)
4. `Execution/enea/generate_index_whisper.py` (Trascrizione e Indice)
5. `Execution/enea/youtube_uploader.py` (Upload e Programmazione)
6. `Execution/enea/video_cleanup.py` (Pulizia Post-Upload e Archiviazione)
7. `Execution/enea/caption_manager.py` (Gestione e Traduzione Sottotitoli)

## SOP: Enea — Template Descrizione Video

```text
Lo studio "TITOLO ACCADEMICO REALE DEL PAPER" di COGNOMI AUTORI DEL PAPER, pubblicato su NOME DELLA RIVISTA nel ANNO DI PUBBLICAZIONE, analizza IN POCHE PAROLE QUAL'è LA DOMANDA DI RICERCA...

(Lasciare riga vuota)

⏰ Fonte: ►► [Link DOI certificato o Journal page]

(Lasciare riga vuota)

⏰ISCRIVITI al canale ►► https://www.youtube.com/@cosafannoglieconomisti26?sub_confirmation=1


(Lasciare riga vuota)

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
⏰ INDICE CONTENUTI ⏰
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
00:00 | Intro
XX:XX | [Titolo Capitolo]
XX:XX | Conclusioni

(Lasciare riga vuota)

#tag1 #tag2 #tag3
```

---

## PARTE 5: Romolo — Gestione Canale YouTube

Competente solo per il monitoraggio, analytics, commenti e salute generale del canale.

### Task Ricorrenti

1. **Analytics Report**: Generare report periodici (`analytics_report.txt`) con metriche di performance e commenti rilevanti (usare `Execution/romolo/romolo_manage_channel.py`).
2. **Gestione Commenti**: Monitorare e rispondere in modo garbato e divulgativo per favorire la community.
3. **Aggiornamento Metadati**: Eventuale ottimizzazione di tag/titoli posteriori basati sulla performance.

---

## 📋 File Python Utilizzati
- `Execution/romolo/romolo_manage_channel.py` (Analytics e Monitoraggio)

### SOP: Gestione Playlist Tematiche
Organizzare i video in 8 playlist tematiche predefinite per massimizzare la discoverability.
1. **Categorie**: "Economia del Crimine e Mafie", "Economia Politica e Istituzioni", "Storia Economica e Sviluppo", "Economia della Cultura, Società e Religione", "Economia del Lavoro, Discriminazione e Disuguaglianze", "Economia Pubblica, Welfare e Demografia", "Economia dei Media e dello Sport", "I Migliori Video di Cosa Fanno Gli Economisti".
2. **Descrizioni Catchy**: Ogni playlist deve avere una descrizione accattivante che include l'elenco dei titoli dei video contenuti. Questa operazione è automatizzata dagli script.
3. **Configurazione Centrale**: `Execution/romolo/playlist_config.json` contiene le descrizioni base e la mappatura iniziale.
4. **Inizializzazione**: `Execution/romolo/create_playlists_batch.py` per creare/aggiornare massivamente le playlist e le loro descrizioni.
5. **Esecuzione Automatica**: `Execution/romolo/catalog_video.py` eseguito via `/playlist` su Telegram. Cataloga il video e **aggiorna automaticamente la descrizione della playlist** per includere il nuovo titolo.

## 📋 File Python Utilizzati (Playlist)
- `Execution/romolo/playlist_config.json` (Configurazione Centrale)
- `Execution/romolo/create_playlists_batch.py` (Inizializzazione/Sincronizzazione Batch)
- `Execution/romolo/catalog_video.py` (Catalogazione e Refresh Descrizione)
## PARTE 6: Marcello — Gestione Social Media

Agente dedicato al cross-posting su Facebook via Buffer API. **Un video alla volta. Nessuna automazione batch senza approvazione esplicita.**

### SOP: Pubblicazione Video YouTube su Facebook (Buffer API v1)

#### Regola 0 — Script Unico Autorizzato
Lo script **`Execution/marcello/buffer_post_single.py`** e' l'unico strumento autorizzato per il posting su Buffer.
`buffer_auto_sync.py` e `buffer_sync_today.py` sono **deprecati per il posting**.

#### Regola 1 — Formato Didascalia (CONTRATTO IMMUTABILE)
```
[Didascalia YouTube — paragrafo "Lo studio ... analizza ..." estratto da video_metadata.md]

▶ https://www.youtube.com/watch?v=[VIDEO_ID]

[Tag reali del video da video_metadata.md — mai generati dall'IA]
```
Esempio validato (Folklore):
```
Lo studio "Folklore" di Michalopoulos e Xue, pubblicato su The Quarterly Journal of Economics nel 2021, analizza l'importanza economica delle tradizioni orali...

▶ https://www.youtube.com/watch?v=7sNESUojy0w

#CosaFannoGliEconomisti #Folklore #QJE
```

#### Regola 2 — Procedura di Esecuzione (ordine obbligatorio)
1. **Verifica Registro MANDATORIA**: Caricare `Cleaned/video_tracking.json` e verificare che lo stato del video NON sia già "Postato" o "Completato". In caso di discrepanza con la richiesta utente, segnalare e fermarsi.
2. **Cross-Check Mandatorio (Anti-Duplicati)**: Verificare SEMPRE che lo stato sia "Da fare" in `video_tracking.json` E che l'ID YouTube del video non sia presente in `instagram_history.json`. L'uso di override (`--video-id`) non esenta da questo controllo.
3. Pre-check: verificare coda Buffer < 10 post
4. Dry run OBBLIGATORIO: `python3 buffer_post_single.py --dry-run`
5. Verificare output: **La didascalia deve iniziare direttamente con "Lo studio..."** (senza titoli o autori sopra).
6. Post reale: `python3 buffer_post_single.py`
7. Verifica post-invio: coda Buffer deve avere il post corretto.
8. **Aggiornamento Registro**: Al successo del post, segnare immediatamente il video come "Postato" nel registro.

#### Regola 3 — Parametri API Buffer (Sicuri)
- Endpoint: `https://api.bufferapp.com/1/updates/create.json` (POST)
- Token: Caricato da ambiente tramite `.env` (**NON inserire mai in chiaro qui**)
- Profile ID Facebook: Caricato da ambiente tramite `.env`
- **media[link]** = URL YouTube completo inserito nella DIDASCALIA (testo).
- **media[picture]** = Usare SEMPRE la `copertina.png` come foto caricata.
- **MANDATORIO**: NON usare più l'anteprima video dinamica su Facebook. I post devono essere caricati come **FOTO** (Cover) con il link YouTube nel testo per massimizzare la visibilità.
- **scheduled_at** = Unix timestamp, default domani 09:00 Europe/Rome

#### Regola 4 — Casi Limite Documentati
- `code:1023` coda piena: svuotare con `destroy.json` su tutti i pending, poi postare
- `500` body vuoto: era causato da curl, risolto usando `requests`
- Duplicati in coda: tenersi `updates[0]` (il piu' recente), eliminare gli altri
- Metadata non trovato: controllare cartella corrispondente in `Cleaned/` manualmente

### Crescita e Networking
Marcello segue batch (1-2/giorno) di account rilevanti, salvando report in `Temp/marcello/followed_pages_report.txt`.

---

## 📋 File Python Utilizzati (Marcello)
- `Execution/marcello/buffer_post_single.py` (unico script autorizzato per posting Buffer)

## PARTE 7: Ulisse — Monitoraggio News e Ricerca Accademica

Ricerca i temi "hot" dalle news quotidiane e i rispettivi paper accademici di riferimento.

### Procedura di Matching Accademico

### PROCEDURA DI MATCHING ACCADEMICO (per Ulisse /articoli)

1. **Notizie (BATCH DETERMINISTICO)**: Cesare/Ulisse raccoglie il pool di news dalle 5 fonti SOP: **ANSA, Corriere, Repubblica, Il Post, Fanpage**. Non usa più il grounding diretto per evitare quote instabili.
2. **Consensus Discovery**: Tramite Gemini (`gemini-flash-latest`), il sistema identifica i **3 argomenti più caldi (Consensus)**. **MANDATORIO**: Titoli estremamente "catchy", massimo **5 parole**, stile clicky o domanda, centrati sull'argomento economico del paper.
3. **Matching Semantico (TAG-BASED)**: Per ogni argomento di consenso, estrarre **Broad Academic Areas** (es. 'Labor Economics', 'Public Policy') invece di tag troppo specifici. I tag devono essere **strettamente coerenti** con l'area economica del tema per evitare allucinazioni. Interpellare OpenAlex (via `verify_paper.py`) con logica **OR** tra i tag per massimizzare il matching.
    - **Journal**: Solo Top Journals (AER, QJE, JPE, Econometrica, REStud, JEP, AEJ, REStat, JEEA, Nature, Science, PNAS, etc.).
    - **Anno**: Dal **2000 in poi**.
4. **Verifica (MANDATORIA)**: Eseguire lo script deterministico `Execution/ulisse/verify_paper.py`. Il report deve mostrare lo stato `[✔ VERIFICATO]` o una nota informativa se nessun match è trovato.
5. **Formattazione**: Salvare la lista (Consensus Topics + Match verificato) in `Temp/ulisse/` con naming `temi_hot_matched_GG_MM_AAAA_HHMM.txt`.

---

## 📋 File Python Utilizzati
1. `Execution/ulisse/news_extractor.py` (Estrattore Batch Batch)
2. `Execution/cesare/telegram_bot.py` (Orchestratore Consensus & Tagging)
3. `Execution/ulisse/verify_paper.py` (Matching Semantico Determinizzato)

## PARTE 8: Mercurio — Comunicazione e Sincronizzazione GitHub

Responsabile del monitoraggio della casella email e del backup del codice.

- **Gmail Manager**: Legge email non lette e genera un report in `Temp/mercurio/gmail_report.txt` (via `Execution/mercurio/mercurio_gmail_manager.py`).
- **GitHub Sync**: Esegue `/backup` per sincronizzare le cartelle di progetto (incluso `Cleaned/`, escludendo i video `.mp4`) con il repository remoto.

---

## 📋 File Python Utilizzati
- `Execution/mercurio/mercurio_gmail_manager.py` (Gmail Report)
- `Execution/mercurio/mercurio_github_sync.py` (Backup GitHub)

## PARTE 9: Cesare — Gestione Telegram

Agente dedicato alla comunicazione e notifiche di status via bot Telegram.

- **Hub Notifiche**: Monitora `Temp/cesare/notifications_hub.json` per alert e approvazioni inline (es. upload schedulato).
- **Bot**: Esegue notifiche in background o riceve comandi `/articoli`, `/gmail`, `/report`.

---

## 📋 File Python Utilizzati
- `Execution/cesare/telegram_bot.py` (Hub Notifiche / Bot)

## PARTE 10: Augusto — Gestione File e Persistenza

Agente specializzato nella pulizia remota, persistenza di sessione e backup dei file RAW intermedi prima della pulizia, salvaguardando la struttura delle cartelle definite nella PARTE 1.

---

## PARTE 11: Romolo — Ottimizzazione YouTube Shorts

Procedura mandatoria per massimizzare il cross-traffic tra clip brevi e contenuti long-form.

### SOP: Metadati Shorts (SEO & Conversion)

1.  **Titolo Hook (Catchy)**: Sostituire titoli generici con ganci testuali forti. **MANDATORIO**: Nessun hashtag nel titolo. Massimo 60 caratteri.
2.  **Descrizione a Conversione**:
    -   **Riga 1 (MANDATORIA)**: Gancio breve o sintesi del video (Hook).
    -   **Riga 2**: `Video completo qui: https://youtu.be/[ID_VIDEO_LUNGO]`
    -   **Separazione**: Una riga vuota prima dei tag.
    -   **Hashtag Strategici**: Includere sempre `#shorts` e `#economia`, più 1-2 tag specifici. I tag devono andare tutti in fondo alla descrizione.
3.  **Hashtag Strategici**: Includere sempre `#shorts` e `#economia`, più 1-2 tag specifici (es: `#storia`, `#mafia`, `#tecnologia`).
4.  **Associazione Semantica**: In caso di dubbi sulla mappatura, verificare la trascrizione dello Short per identificare il paper e il video long-form corrispondente in `Cleaned/`.
5.  **Titoli-Data (Trigger Prioritario)**: Video con titoli tipo "11 aprile 2026" o "Apr 11, 2024" devono essere identificati come "non ottimali" dal workflow `/shorts` e aggiornati prioritariamente seguendo i punti 1 e 2.
6.  **Clickability Link**: Il link al video lungo `https://youtu.be/[ID]` deve essere inserito in una riga isolata (solitamente la seconda) per garantire che i sistemi mobile lo rendano cliccabile immediatamente.

## 📋 File Python Utilizzati
- `Execution/romolo/batch_update_shorts.py` (Aggiornamento Massivo Metadati)

---

## 🌉 Chat-Telegram Bridge (Collaborazione AI-Utente)

Per consentire una collaborazione fluida tra l'assistente AI (Antigravity) e l'utente via Telegram:

1. **Incoming (Telegram -> Antigravity)**: Ogni messaggio inviato dall'utente autorizzato viene loggato in tempo reale in `Temp/cesare/telegram_bridge.log`. Antigravity monitora questo file per leggere i comandi o le risposte dell'utente.
2. **Outgoing (Antigravity -> Telegram)**: Antigravity risponde all'utente usando lo script `Execution/cesare/bridge_send.py "messaggio"`. Questo script logga automaticamente la risposta in `telegram_bridge.log`. **Tutti i comandi di sistema (slash commands) loggano deterministicamente il proprio output nel bridge.**
3. **Auto-Responder**: Cesare utilizza il modello `gemini-flash-latest` per rispondere in modo proattivo ai messaggi non-comando, mantenendo la sincronia con il log del bridge.

### 📋 File Python Utilizzati
- `Execution/cesare/bridge_send.py` (Invio messaggi a Telegram)
- `Execution/cesare/telegram_bot.py` (Orchestratore Bridge e Auto-Responder - Multi-threaded & Safe)
- `Execution/enea/video_processor.py` (Orchestratore Pipeline con Metadati Dinamici)
- `/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3` (Interprete Mandatorio)
- `Execution/enea/tracking_manager.py` (Gestore Registro Univoco)

---

## PARTE 12: Gestione del Registro Univoco (video_tracking.json)

Il file `Cleaned/video_tracking.json` è la **Fonte di Verità (Source of Truth)** definitiva per lo stato di ogni progetto long-form del canale.

### 1. Regole Mandatorie di Aggiornamento (100% Deterministico)
1.  **Inizializzazione**: Ogni nuovo progetto processato via `/pulizia` deve essere immediatamente registrato nel JSON con i campi di base (YouTube ID vuoto, status "Da fare").
2.  **Sincronizzazione Pubblicazione**: Dopo ogni operazione di upload o programmazione (`/upload`, `/facebook`, `/instagram`), il registro **DEVE** essere aggiornato con l'URL o la data di programmazione specifica.
3.  **Persistenza**: Nessuna modifica manuale al file è autorizzata senza aver prima creato un backup automatico (gestito da `tracking_manager.py`).
4.  **Esclusione Short**: I video in formato **Shorts** (durata < 60s) **NON** devono essere inclusi in questo registro per mantenere la distinzione netta tra i flussi di lavoro.

### 2. Strumenti di Gestione
L'unico strumento autorizzato per la manipolazione programmatica del registro è lo script:
`Execution/enea/tracking_manager.py`.
Qualsiasi nuovo script di automazione deve integrare chiamate a questo gestore per garantire la coerenza dei dati.

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.

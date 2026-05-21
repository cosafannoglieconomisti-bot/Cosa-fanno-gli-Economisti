# 🎓 CODEX INSTRUCTIONS — Cosa fanno gli Economisti

> Queste istruzioni descrivono **completamente** il progetto del canale YouTube "Cosa fanno gli Economisti" (`@cosafannoglieconomisti26`). Leggile interamente prima di intervenire su qualsiasi file o processo.

---

## 0. CONTESTO GENERALE

**Cosa fanno gli Economisti** è un canale YouTube italiano di divulgazione scientifica in economia. Ogni video trasforma un paper accademico (AER, QJE, Econometrica, ecc.) in un contenuto accessibile al grande pubblico, con tono semplice ma rigore scientifico.

- **Repo GitHub**: `cosafannoglieconomisti-bot/Cosa-fanno-gli-Economisti`
- **Workspace locale (Mac)**: `/Users/marcolemoglie_1_2/Desktop/canale`
- **Python venv OBBLIGATORIO**: `/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3`
  - ❌ Non usare mai il Python di sistema — causerà `ModuleNotFoundError`
- **Account Gmail canale**: `cosafannoglieconomisti@gmail.com`
- **Bot Telegram**: interfaccia principale dell'utente (Cesare)
- **Modello AI**: `gemini-flash-latest` (quota Free Tier — non usare modelli più pesanti)

---

## 1. ARCHITETTURA A 3 LIVELLI

Il sistema segue una separazione netta tra conoscenza, logica e azione:

| Livello | Nome | Dove | Cosa fa |
|---------|------|------|---------|
| 1 | **Direttive** | `GEMINI.md`, `Directives/` | Definisce obiettivi, SOP, regole operative |
| 2 | **Orchestrazione** | Agente AI (tu / Codex) | Legge le direttive, decide l'ordine di esecuzione, gestisce errori |
| 3 | **Esecuzione** | `Execution/*/` (script Python) | Esegue deterministicamente: API, file, calcoli |

> [!IMPORTANT]
> Prima di ogni task, **leggi sempre** `GEMINI.md` e le direttive pertinenti in `Directives/`. Non proporre codice senza aver prima capito le SOP.

---

## 2. STRUTTURA DIRECTORY

```
/Users/marcolemoglie_1_2/Desktop/canale/
├── GEMINI.md                  # Regole master e SOP (LEGGI SEMPRE PRIMA)
├── README.md                  # Documentazione pubblica (va su GitHub)
├── .env                       # Segreti (LOCALE, mai committato)
├── .gitignore                 # Esclude .env, .venv, token*.pickle, *.mp4, Papers/
├── .venv/                     # Python virtual environment
├── .agents/
│   └── workflows/             # File Markdown dei workflow slash-command
├── Cleaned/                   # Archivio video completati
│   ├── video_tracking.json    # REGISTRO CENTRALE (leggi sempre prima di pubblicare)
│   └── [Nome_Video]/          # Una cartella per video
│       ├── copertina.png
│       ├── infografica_cleaned.png
│       ├── video_metadata.md
│       └── international/     # SRT, VTT, metadata in IT/EN/ES/FR/DE
├── Directives/                # SOP per agente
│   └── SOP_Crescita.md
├── Execution/                 # Script Python deterministici
│   ├── credentials/           # Token OAuth e .env dei segreti
│   ├── augusto/
│   ├── cesare/                # Bot Telegram (telegram_bot.py)
│   ├── enea/                  # Pipeline video completa
│   ├── marcello/              # Social media (Buffer API)
│   ├── mercurio/              # GitHub sync + Gmail
│   ├── romolo/                # YouTube analytics + playlist
│   └── ulisse/                # News + matching accademico
├── Papers/
│   └── Da fare/               # PDF da processare (ricerca RICORSIVA)
└── Temp/                      # File intermedi (non va su GitHub)
    ├── enea/
    │   └── active_pipeline.json  # Stato pipeline corrente
    └── ulisse/
```

---

## 3. GESTIONE CREDENZIALI E SEGRETI

### Regola d'oro
❌ **Mai** inserire token, chiavi API o password in chiaro in file `.md`, `.py` o `.json`.  
✅ Tutti i segreti stanno in `Execution/credentials/.env` (e nel `.env` root), caricati con `python-dotenv`.

### File di credenziali (locali, NON nel repo)
| File | Cosa contiene |
|------|--------------|
| `.env` (root) | `GEMINI_API_KEY`, variabili principali |
| `Execution/credentials/.env` | Variabili aggiuntive per singoli script |
| `Execution/credentials/client_secrets.json` | OAuth2 YouTube/Google |
| `Execution/credentials/token.pickle` | Token OAuth YouTube (upload) |
| `Execution/credentials/token_youtube.pickle` | Token YouTube Data API |
| `Execution/credentials/token_youtubeAnalytics.pickle` | Token YouTube Analytics |
| `Execution/credentials/token_gmail.pickle` | Token Gmail API |

### Token scaduti
Se uno script YouTube fallisce con `Errore refresh token`, i token sono scaduti. L'utente deve rieseguire il flusso OAuth manualmente in locale. Non tentare di rigenerare token in automatico.

---

## 4. AGENTI E LORO RESPONSABILITÀ

| Agente | Script principale | Responsabilità |
|--------|------------------|----------------|
| **Cesare** | `Execution/cesare/telegram_bot.py` | Bot Telegram hub — orchestra tutti i comandi |
| **Enea** | `Execution/enea/*` | Pipeline video completa: paper → upload YouTube |
| **Romolo** | `Execution/romolo/*` | Analytics YouTube, playlist, shorts, commenti |
| **Marcello** | `Execution/marcello/buffer_post_single.py` | Facebook e Instagram via Buffer API |
| **Ulisse** | `Execution/ulisse/*` | News + matching paper accademici |
| **Mercurio** | `Execution/mercurio/*` | GitHub backup + Gmail |
| **Augusto** | `Execution/augusto/*` | Gestione file e persistenza sessione |

### Bot Telegram (Cesare)
Il file `Execution/cesare/command_map.json` mappa ogni slash-command al suo script Python:
```json
{
  "backup":    [".venv/bin/python3", "Execution/mercurio/mercurio_github_sync.py"],
  "gmail":     [".venv/bin/python3", "Execution/mercurio/mercurio_gmail_manager.py"],
  "report":    [".venv/bin/python3", "Execution/romolo/romolo_manage_channel.py"],
  "pulizia":   [".venv/bin/python3", "Execution/enea/video_processor.py"],
  "produzione":[".venv/bin/python3", "Execution/enea/notebooklm_orchestrator.py"],
  "articoli":  [".venv/bin/python3", "Execution/ulisse/verify_paper.py"],
  "copertina": [".venv/bin/python3", "Execution/enea/generate_cover.py"],
  "crescita":  [".venv/bin/python3", "Execution/romolo/crescita_orchestrator.py"]
}
```

> [!NOTE]
> Ogni messaggio che inizia con `/` è un **Comando Deterministico**. Non deve mai generare una risposta creativa dell'AI. Se il comando è sconosciuto, rispondi con un errore e la lista dei comandi validi.

---

## 5. PIPELINE VIDEO COMPLETA — PASSO PER PASSO

La pipeline di un video si divide in **4 SOP** eseguite in sequenza.

---

### SOP 0 — `/download` (Ingestione Paper)

**Trigger**: comando `/download` su Telegram.  
**Script**: `Execution/enea/paper_downloader.py`

**Cosa fa:**
1. Scansiona `~/Downloads` cercando PDF modificati nelle ultime 24 ore
2. Esclude file già presenti in `Papers/Da fare/` o `Cleaned/`
3. Estrae il testo delle prime 3 pagine con Gemini per identificare o confermare il **Titolo Accademico Reale**
4. Rinomina il file e lo sposta in `Papers/Da fare/[Titolo_Accademico].pdf`

```bash
# Esecuzione manuale
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/paper_downloader.py
```

---

### SOP 1 — `/paper` (Selezione Paper, Titolo e Copertina)

**Script in ordine**: `telegram_bot.py` → `batch_text_extractor.py` → `generate_cover.py`

**Cosa fa:**
1. Il bot scansiona `Papers/Da fare/` **ricorsivamente** (incluse sottocartelle tematiche)
2. Propone i paper all'utente via Telegram
3. Estrae il testo del paper scelto → propone **5 titoli catchy** (max 5 parole, stile domanda)
4. Genera **copertina in stile Comic** (Arancio/Nero/Bianco) con il titolo integrato
5. L'utente approva (`✅ Approva`) o rigenera (`🔄 Rigenera`)
6. All'approvazione:
   - Recupera il Titolo Accademico Reale
   - Crea `Cleaned/[Titolo_Scelto]/`
   - **Sposta e rinomina** il PDF → `Cleaned/[Titolo_Scelto]/[Titolo_Accademico].pdf`
   - Salva `copertina.png` nella cartella
   - Inizializza `video_metadata.md` con Autori, Rivista, Anno, DOI estratti dal PDF
   - Scrive `Temp/enea/active_pipeline.json` (stato pipeline attivo)

> [!CAUTION]
> Il titolo scelto **DEVE** essere applicato rigorosamente a TUTTI i contenuti successivi. Non alterarlo mai.

**Struttura `active_pipeline.json`:**
```json
{
  "paper": "Nome Paper Originale",
  "academic_title": "Titolo Accademico Reale",
  "title": "Titolo Video Scelto",
  "clean_title": "Titolo_Video_Scelto_underscored",
  "target_dir": "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Titolo_Video_Scelto"
}
```

---

## SOP 2 — `/produzione` (Generazione Video NotebookLM)

**Script**: `Execution/enea/notebooklm_orchestrator.py`, `notebook_press.py`

**Cosa fa:**
1. Carica su NotebookLM **solo ed esclusivamente** il PDF del paper (nessun'altra fonte)
2. Rinomina temporaneamente il PDF con il `[Titolo Scelto]` prima dell'upload su Drive (per forzare il watermark nel video)
3. Genera il **Video Overview** in **ITALIANO** (critico: mai inglese)
4. Genera l'**Infografica Quadrata Dettagliata** in italiano
5. Scarica i file grezzi in `~/Downloads` con `notebook_press.py`

**Prompt video (rigido):**
```
Per favore parla in Italiano. Sei un host di podcast coinvolgente che spiega paper di economia.
Sii energico ma accurato. **MANDATORIO: Il TITOLO in sovrimpressione nel video DEVE essere
ESATTAMENTE: '[Titolo Scelto]'. Non riassumere o alterare il titolo.**
```

#### CLI `notebook_press.py` — Sottocomandi

```bash
PYTHON=/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3
SCRIPT=/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebook_press.py

# Verifica autenticazione
$PYTHON $SCRIPT auth

# Refresh cookie da Chrome (porta 9222 aperta)
$PYTHON $SCRIPT auth --refresh

# Upload PDF su Drive e aggiunta a notebook
$PYTHON $SCRIPT upload /path/paper.pdf --title "Titolo Scelto"

# Genera video
$PYTHON $SCRIPT generate <notebook_id> --type video --focus "..."

# Controlla stato generazione
$PYTHON $SCRIPT status <notebook_id>

# Download asset (con fallback automatico)
$PYTHON $SCRIPT download <notebook_id> video --output ~/Downloads/Titolo_raw.mp4
$PYTHON $SCRIPT download <notebook_id> infographic --output ~/Downloads/Titolo_infografica.png

# Pipeline end-to-end automatica
$PYTHON $SCRIPT sync /path/paper.pdf --title "Titolo Scelto" --clean-title "Titolo_Pulito"
```

> [!WARNING]
> **Problema Cookie / Redirect CDN (Bug risolto)**: In caso di download corrotti (file di pochi KB con HTML dentro), il refresh dei cookie deve usare il comando CDP `Network.getAllCookies` (NON `Network.getCookies`). Questo preserva il dominio iniziale `.google.com` e permette al client HTTP `httpx` di seguire i redirect verso `*.googleusercontent.com`. Il `notebook_press.py` gestisce questo automaticamente con `auth --refresh`.

**Prerequisito Chrome per refresh cookie:**
```bash
# Aprire Chrome con debug remoto attivo
open -a "Google Chrome" --args --remote-debugging-port=9222
# Navigare su notebooklm.google.com e accedere all'account
# Poi eseguire: $PYTHON $SCRIPT auth --refresh
```

**Fine SOP 2**: Una volta scaricati `*_raw.mp4` e l'infografica `.png` in `~/Downloads`, la SOP 2 è TERMINATA. Ogni operazione successiva è SOP 3.

---

### SOP 3 — `/pulizia` (Post-processing, Archiviazione, Metadati Multilingua)

**Script in ordine**:
1. `Execution/enea/video_processor.py` (orchestratore principale)
2. `Execution/enea/video_cleaner.py` (pulizia watermark + trim)
3. `Execution/enea/clean_infographic.py` (pulizia watermark infografica)
4. `Execution/enea/generate_index_whisper.py` (indice capitoli)
5. `Execution/enea/generate_srt_whisper.py` (sottotitoli IT)
6. `Execution/enea/generate_vtt_whisper.py` (sottotitoli VTT IT)
7. `Execution/enea/translate_srt.py` (traduzione SRT in EN/ES/FR/DE)
8. `Execution/enea/translate_metadata.py` (traduzione metadati)
9. `Execution/enea/tracking_manager.py` (aggiornamento registro)

**Cosa fa `video_processor.py`:**

```
1. Legge active_pipeline.json → recupera titolo e cartella di destinazione
2. Individua il video più recente in ~/Downloads (*_raw.mp4)
3. Pulizia Video: rimozione watermark + trim 2.5s iniziali (video_cleaner.py)
4. Archivia video raw → Cleaned/[Titolo]/[clean_title]_raw.mp4
5. Pulizia Infografica: rimozione watermark NotebookLM (clean_infographic.py)
6. Genera indice Whisper (max 6 capitoli: Intro + 4 + Conclusioni)
7. Genera SRT italiano e VTT italiano
8. Archivia SRT/VTT/TXT → Cleaned/[Titolo]/international/
9. Genera video_metadata.md con descrizione YouTube completa (via Gemini ONE-SHOT)
   - Autori, Rivista, Anno, DOI estratti dal PDF (NON allucinati dall'AI)
   - Teaser divulgativo in italiano
   - 5 hashtag specifici
   - Indice con timestamp dinamici
   - Timestamp Conclusioni = inizio ULTIMO segmento Whisper (mai XX:XX)
10. Traduce metadata in EN, ES, FR, DE → international/[lang]/metadata_[lang].md
11. Traduce SRT in EN, ES, FR, DE → international/[lang]/subtitles_[lang].srt
12. Verifica asset mandatori: blocca il processo se manca qualcosa
13. Aggiorna video_tracking.json
```

> [!CAUTION]
> Il processo si interrompe con `sys.exit(1)` se **mancano asset multilingua**. Non bypassare questo controllo.

**Esecuzione manuale:**
```bash
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/video_processor.py
# Oppure con file specifico:
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/video_processor.py "nome_file_raw.mp4"
```

**Struttura cartella finale dopo `/pulizia`:**
```
Cleaned/[Titolo_Video]/
├── copertina.png
├── infografica_cleaned.png
├── infografica_raw.png
├── video_metadata.md
├── [clean_title]_raw.mp4
├── [clean_title]_cleaned.mp4
├── [Titolo_Accademico].pdf
└── international/
    ├── video_index_raw.txt
    ├── subtitles_it.srt
    ├── subtitles_it.vtt
    ├── en/
    │   ├── metadata_en.md
    │   └── subtitles_en.srt
    ├── es/ (stessa struttura)
    ├── fr/ (stessa struttura)
    └── de/ (stessa struttura)
```

#### Template `video_metadata.md` (formato obbligatorio)
```markdown
# Metadati Video - [Titolo Video]

## Descrizione YouTube
Lo studio "[Titolo Accademico Reale del Paper]" di [Cognomi Autori], pubblicato su [Rivista] nel [Anno], [teaser 2-3 frasi].

⏰ Fonte: ►► [URL DOI]

⏰ISCRIVITI al canale ►► https://www.youtube.com/@cosafannoglieconomisti26?sub_confirmation=1


▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
⏰ INDICE CONTENUTI ⏰
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
00:00 | Intro
XX:XX | [Titolo Capitolo 1]
XX:XX | [Titolo Capitolo 2]
XX:XX | [Titolo Capitolo 3]
XX:XX | [Titolo Capitolo 4]
XX:XX | Conclusioni

#CosaFannoGliEconomisti #Tag1 #Tag2

## Tag
CosaFannoGliEconomisti, Tag1, Tag2

## Status Pipeline
- Paper PDF: [nome].pdf (OK)
- Video RAW: OK
- Video Cleaned: OK
- Indice Whisper: OK
- Sottotitoli (SRT/VTT): OK
```

---

### SOP 3b — `/upload` (Upload Multi-Piattaforma + Cleanup)

**Script in ordine**:
1. `Execution/cesare/telegram_bot.py` (interfaccia)
2. `Execution/enea/youtube_uploader.py` (upload YouTube)
3. `Execution/romolo/update_video_localization.py` (sottotitoli multilingua)
4. `Execution/romolo/catalog_video.py` (assegnazione playlist)
5. `Execution/marcello/buffer_post_single.py` (FB + IG)
6. `Execution/enea/video_cleanup.py` (cleanup finale)

**Cosa fa:**

#### 1. Filtro AI (anti-duplicati)
Prima dell'upload, il bot recupera i titoli già pubblicati su YouTube e mostra solo i video locali **non ancora online**.

#### 2. Upload YouTube (`youtube_uploader.py`)
```bash
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/youtube_uploader.py \
  /path/to/[clean_title]_cleaned.mp4 \
  "Titolo Video" \
  /path/to/video_metadata.md \
  --thumbnail /path/to/copertina.png \
  --schedule "2026-05-22T09:00:00+02:00"
```

Prima dell'upload, lo script **blocca** se mancano asset multilingua. Dopo l'upload:
- Carica sottotitoli IT + EN + ES + FR + DE
- Aggiorna `video_tracking.json` con `youtube_id`
- Lancia automaticamente `catalog_video.py`

#### 3. Catalogazione Playlist (`catalog_video.py`)
8 playlist tematiche predefinite (configurate in `Execution/romolo/playlist_config.json`):
- "Economia del Crimine e Mafie"
- "Economia Politica e Istituzioni"
- "Storia Economica e Sviluppo"
- "Economia della Cultura, Società e Religione"
- "Economia del Lavoro, Discriminazione e Disuguaglianze"
- "Economia Pubblica, Welfare e Demografia"
- "Economia dei Media e dello Sport"
- "I Migliori Video di Cosa Fanno Gli Economisti"

> [!IMPORTANT]
> Gli **YouTube Shorts** (durata ≤ 120s o verticali) non vanno mai inseriti nelle playlist tematiche.

#### 4. Post su Facebook e Instagram (`buffer_post_single.py`)

**Script UNICO autorizzato per Buffer**. `buffer_auto_sync.py` e `buffer_sync_today.py` sono **deprecati**.

```bash
# Facebook (default)
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/buffer_post_single.py

# Instagram
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/buffer_post_single.py \
  --platform instagram --hour 10

# Dry run (obbligatorio prima del post reale)
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/buffer_post_single.py \
  --dry-run
```

**Formato didascalia Facebook (contratto immutabile):**
```
Lo studio "[Titolo Accademico]" di [Autori], pubblicato su [Rivista] nel [Anno], analizza ...

▶ https://www.youtube.com/watch?v=[VIDEO_ID]

#CosaFannoGliEconomisti #Tag1 #Tag2
```
> La didascalia **DEVE** iniziare con "Lo studio..." — senza titoli o autori sopra.  
> Il post Facebook usa **sempre** `copertina.png` come immagine (non anteprima video dinamica).  
> Il post Instagram usa **sempre** `infografica_cleaned.png`.

**Procedura sicura Buffer:**
1. Leggi `video_tracking.json` → verifica stato `Da fare`
2. Dry run obbligatorio
3. La didascalia deve iniziare con "Lo studio..."
4. Post reale
5. Aggiorna `video_tracking.json` con stato "Postato"

**Errori Buffer noti e soluzioni:**
- `code:1023` coda piena → svuota con `destroy.json` su tutti i pending, poi riposta
- `500` body vuoto → era causato da `curl`; risolto usando la libreria `requests` Python
- Duplicati in coda → tieni `updates[0]` (il più recente), elimina gli altri

#### 5. Post-Upload Cleanup (`video_cleanup.py`)
Eseguito automaticamente alla fine:
- Archivia file Whisper/SRT/VTT in `international/`
- **Elimina definitivamente** `*_raw.mp4`, `*_cleaned.mp4` dalla cartella progetto e dalla root
- Elimina `infografica_raw.png` e il PDF del paper
- **Mantiene**: `copertina.png`, `infografica_cleaned.png`, `video_metadata.md`, cartella `international/`
- Imposta stato `Pulito` in `video_tracking.json`

---

## 6. REGISTRO CENTRALE — `video_tracking.json`

> [!CAUTION]
> Prima di **ogni** operazione di pubblicazione, scheduling social o modifica di stato, devi leggere `Cleaned/video_tracking.json`. Dopo l'operazione, aggiorna il registro e sincronizza su GitHub con `/backup`.

Campi principali per ogni video:
```json
{
  "titolo": "Nome Cartella Video",
  "youtube_id": "abc123xyz",
  "youtube_url": "https://www.youtube.com/watch?v=abc123xyz",
  "stato": "Pulito",
  "instagram_url": "Da fare",
  "facebook_url": "Da fare",
  "playlist": "Storia Economica e Sviluppo"
}
```

---

## 7. TUTTI I WORKFLOW SLASH-COMMAND (15 comandi supportati)

Il bot Telegram (Cesare) e Codex supportano 15 comandi specifici per coprire tutte le fasi operative del canale:

| Comando | Agente | Script principale | Obiettivo / Descrizione |
|---------|--------|-------------------|-------------------------|
| `/download` | Enea | `paper_downloader.py` | SOP 0: Scansiona `~/Downloads` per paper delle ultime 24h, pulisce il titolo con Gemini, e li ingerisce ricorsivamente in `Papers/Da fare/`. |
| `/paper` | Enea | `batch_text_extractor.py`, `generate_cover.py` | SOP 1: Seleziona paper, propone 5 titoli catchy (max 5 parole), genera copertina Comics (Arancio/Nero/Bianco) e setup cartella `Cleaned/`. |
| `/produzione` | Enea | `notebook_press.py` (sottocomando `sync` o `generate`) | SOP 2: Upload PDF su Drive, genera Video Overview e Infografica in italiano su NotebookLM, e scarica in locale. |
| `/pulizia` | Enea | `video_processor.py` | SOP 3: Rileva `*_raw.mp4`, esegue rimozione watermark e trimmaggio, pulisce infografica, genera indici e sottotitoli multilingua (IT/EN/ES/FR/DE). |
| `/upload` | Enea/Mercurio | `youtube_uploader.py`, `video_cleanup.py` | SOP 3b: Carica video schedulato su YT, carica SRT multilingua, lancia catalogazione playlist, pubblica social e fa cleanup completo (cancella mp4/raw). |
| `/instagram` | Marcello | `buffer_post_single.py` | Programma post su Instagram con infografica pulita, didascalia Title Case, invio programmato ore 10:00 del giorno dopo via Buffer API. |
| `/playlist` | Romolo | `catalog_video.py` | Associa video alle 8 playlist tematiche di YouTube (escludendo gli Shorts) aggiornando automaticamente le descrizioni delle playlist. |
| `/articoli` | Ulisse | `news_extractor.py`, `verify_paper.py` | News-jacking: estrae news calde da 5 fonti, estrae tag macro-aree e interroga OpenAlex cercando paper verificati su Top Journal (AER, QJE, ecc.). |
| `/report` | Romolo | `romolo_manage_channel.py` | Raccoglie analytics del canale YT (views, watch time, commenti) e genera report strategico via bot Telegram. |
| `/shorts` | Romolo | `batch_update_shorts.py` | Ottimizza YouTube Shorts con titoli/date generiche collegandoli al rispettivo video long-form "padre" tramite YouTube API. |
| `/gmail` | Mercurio | `mercurio_gmail_manager.py` | Scansiona email non lette, genera sintesi in `Temp/` ed invia report riassuntivo su Telegram. |
| `/backup` | Mercurio | `mercurio_github_sync.py` | Staging e backup su GitHub offuscando token/API in tutti i file testuali. Esclude definitivamente file `.mp4` e `.pdf`. |
| `/crescita` | Romolo/Marcello | `crescita_orchestrator.py` | Strategia "Authority Cycle": unisce news di Ulisse, aggiorna tag SEO dei video affini, internal linking descrizioni e prepara code Buffer. |
| `/bridge` | Marcello | `buffer_post_single.py` | Seleziona video d'archivio e programma post FB/IG news-jacking inserendo aggancio notizia + link video YT e infografica IG. |
| `/competitor` | Romolo | `competitor_scout.py` | Scansiona 14 canali competitor (Will, Geopop, ecc.), estrae video recenti, e propone 5 commenti colti che citano paper e linkano il canale. |

---

## 8. REGOLE OPERATIVE CRITICHE (ANTI-DEADLOCK)

### Variabili ambiente obbligatorie per processi in background
```bash
export TERM=dumb
export DEBIAN_FRONTEND=noninteractive
export PYTHONUNBUFFERED=1
unalias -a
```

### Pattern sicuro per eseguire script
```python
# Tutti gli script usano questo pattern
result = subprocess.run(
    [PYTHON_EXEC, script_path, *args],
    capture_output=True, text=True,
    cwd=BASE_DIR, stdin=subprocess.DEVNULL
)
```
- `stdin=subprocess.DEVNULL` → evita blocchi in attesa di input.
- Mai `git commit` senza `-m` → aprirebbe un editor interattivo.
- Usare sempre flag `--yes` / `-y` per operazioni che richiedono conferma.

### Quota API Gemini (Free Tier)
- Modello: **`gemini-flash-latest`** (non usare modelli più pesanti).
- Cooldown obbligatorio di **60 secondi** prima di chiamate Gemini pesanti in `video_processor.py`.
- Retry automatico con backoff su errore 429 (max 3 tentativi, +60s tra ognuno).
- Cooldown **15 secondi** tra traduzioni SRT consecutive.

---

## 9. AUTO-AGGIORNAMENTO (Principio Miglioramento Continuo)

Ogni SOP e workflow è un **documento vivo**. Quando incontri un nuovo caso limite o risolvi un bug:

1. **Aggiorna il file workflow** in `.agents/workflows/[comando].md`.
2. **Aggiorna `GEMINI.md`** nella sezione pertinente (casi limite, problemi risolti).
3. **Aggiorna la lista File Python** in fondo alla SOP corrispondente in `GEMINI.md`.
4. **Aggiorna `README.md`** se il cambiamento è architetturale.
5. Esegui `/backup` per sincronizzare su GitHub.

---

## 10. PIPELINE NOTEBOOKLM ED AUTO-HEALING COOKIE/DOWNLOAD

La pipeline con NotebookLM è integrata tramite il CLI `notebook_press.py`. Ecco come sono stati risolti i problemi architetturali di upload e download:

### 1. Il problema del Download Corrotto (File HTML CDN)
*   **Sintomo**: Il download di video/infografica restituiva file di pochi KB con codice HTML di login/errore Google.
*   **Causa**: NotebookLM ospita i file su server CDN `*.googleusercontent.com`. Il download richiede l'autenticazione tramite cookie di sessione. Estrarre i cookie con script base cattura solo cookie con validità locale, ma i redirect CDN richiedono cookie settati sul dominio radice `.google.com`.
*   **Soluzione**: `notebook_press.py auth --refresh` si collega a una sessione di Google Chrome attiva con debug remoto abilitato (porta `9222`) ed utilizza il comando CDP (Chrome DevTools Protocol) **`Network.getAllCookies`** (e non `Network.getCookies`) per estrarre l'intero set globale di cookie.
*   **Auto-healing e Fallback**: In caso di download fallito o corrotto, `notebook_press.py` avvia il fallback:
    1. Esegue `auth --refresh` per aggiornare i cookie da Chrome.
    2. Istanzia una sessione HTTP `requests` o `httpx` impostando esplicitamente i cookie sui domini `.google.com` e `.googleusercontent.com`.
    3. Segue i redirect con `allow_redirects=True` ed effettua il download in streaming salvando il file corretto in locale.

### 2. Google Drive Sync e Polling macOS xattr
*   **Sintomo**: Impossibile ottenere l'ID Google Drive dei file caricati prima che Drive Desktop sincronizzasse completamente.
*   **Soluzione**: Lo script `notebook_press.py upload` copia il PDF locale nella cartella di Drive locale:
    `/Users/marcolemoglie_1_2/Library/CloudStorage/GoogleDrive-cosafannoglieconomisti@gmail.com/Il mio Drive/Papers`
    e avvia un loop di polling che esegue il comando di sistema macOS:
    `xattr -p com.google.drivefs.item-id#S [percorso_file]`
    Appena Drive Desktop assegna l'ID univoco di sincronizzazione cloud, lo script lo intercetta e avvia immediatamente l'ingestione su NotebookLM via `nlm source add` senza attese arbitrarie.

---

## 11. STRUTTURA MEMORIA CENTRALIZZATA: SUPERMEMORY

Il progetto integra l'API di **SuperMemory** (`https://api.supermemory.ai`) per memorizzare le linee guida e lo stato storico del canale, rendendoli accessibili semanticamente a Codex e ad altri agenti.

### Credenziali (.env)
```env
SUPERMEMORY_API_KEY="sm_key_..."
SUPERMEMORY_PROJECT_ID="sm_project_..."
```

### Script di Gestione
1.  **Ingestione (`Execution/augusto/supermemory_ingestor.py`)**:
    Invia ed aggiorna la conoscenza condivisa su SuperMemory organizzandola in 5 canali principali:
    -   **Stili & Layout (`style`)**: Thumbnail Comics, didascalie Buffer, format descrizioni YouTube.
    -   **Archivio Storico (`archive`)**: Riassunto di tutti i video già completati in `Cleaned/`.
    -   **Pipeline Status (`pipeline`)**: Stato in tempo reale di `video_tracking.json`.
    -   **Configurazione Playlist (`playlist`)**: Elenco e descrizione delle 8 playlist tematiche.
    -   **Paper Future (`upcoming`)**: Elenco dei file PDF pronti per essere processati in `Papers/Da fare`.
2.  **Verifica / Query (`Execution/augusto/supermemory_verifier.py`)**:
    Interroga il database semantico via API POST `/v3/search` in `hybrid` mode con header `x-sm-project: project_id`. Permette di verificare istantaneamente se una regola o stile è correttamente mappato in memoria.

---

## 12. PRINCIPIO CAVEMAN SPEAK (EFFICIENZA TOKEN)

Per ridurre i consumi di token del 60-75% e massimizzare la reattività, Codex segue il **Principio Caveman Speak**:

1.  ❌ **No filler words**: Elimina convenevoli, preamboli o saluti ("Certamente, sono felice di aiutarti...", "Ecco a te il codice richiesto...").
2.  ✅ **Sintassi schematica**: Rispondi in modo asciutto, diretto e tecnico.
3.  ✅ **Focus codice**: Mostra codice secco o comandi pronti da copiare.
4.  ✅ **Elenchi sintetici**: Usa elenchi puntati con frasi cortissime.
5.  *Esempio*: Invece di una lunga spiegazione, scrivi: "Eseguito backup. Offuscati 3 token. Push completato."

---

## 13. CODE REVIEW GRAPH (`.code-review-graph/`)

Il progetto traccia il grafo di dipendenze del codice all'interno di `.code-review-graph/` utilizzando l'MCP server **`code-review-graph`**.

### Flusso di Lavoro Sicuro
1.  **Pre-check**: Prima di modificare qualsiasi script shared o helper in `Execution/`, lancia `get_impact_radius_tool` tramite MCP per verificare quali altri moduli dipendono dal file che stai modificando.
2.  **Modifica**: Effettua le modifiche rispettando i contratti stabiliti.
3.  **Aggiornamento**: Al termine, ricostruisci il grafo per catturare i nuovi import ed allineare la conoscenza di Codex:
    ```bash
    # Tramite strumento MCP o eseguendo:
    build_or_update_graph_tool (repo_path: "/Users/marcolemoglie_1_2/Desktop/canale")
    ```

---

## 14. GITHUB — STRUTTURA REPO E POLICY

-   **Repo**: `cosafannoglieconomisti-bot/Cosa-fanno-gli-Economisti`
-   **Branch**: `main` (unico branch, force push autorizzato da `/backup`).
-   **Cosa è nel repo**: `Directives/`, `Execution/`, `.agents/`, `Cleaned/` (solo metadati, no video), `GEMINI.md`, `README.md`.
-   **Cosa NON è nel repo** (`.gitignore`):
    -   `.env` (tutti i segreti)
    -   `.venv/` (virtual environment)
    -   `token*.pickle`, `client_secrets.json`
    -   `*.mp4` (video)
    -   `Papers/` (PDF)
    -   `Temp/` (file intermedi)
    -   `.code-review-graph/`

> [!IMPORTANT]
> Il backup offusca automaticamente i segreti prima del push. I file locali non vengono mai modificati. Non fare push manuali senza passare per `mercurio_github_sync.py`.

---

## 15. QUICK REFERENCE — COMANDI FREQUENTI

```bash
VENV=/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3
BASE=/Users/marcolemoglie_1_2/Desktop/canale

# Avviare il bot Telegram (processo in background con log visibili)
PYTHONUNBUFFERED=1 $VENV $BASE/Execution/cesare/telegram_bot.py

# Ingestione nuovi paper (SOP 0)
$VENV $BASE/Execution/enea/paper_downloader.py

# Selezionare paper e generare copertina (SOP 1)
$VENV $BASE/Execution/enea/generate_cover.py

# Eseguire sync completo NotebookLM (SOP 2)
$VENV $BASE/Execution/enea/notebook_press.py sync "/percorso/paper.pdf" --title "Titolo Scelto" --clean-title "Titolo_Pulito"

# Refresh manuale dei cookie NotebookLM da Chrome
$VENV $BASE/Execution/enea/notebook_press.py auth --refresh

# Processare un video scaricato manualmente (SOP 3)
$VENV $BASE/Execution/enea/video_processor.py

# Upload YouTube + catalogazione playlist + localizzazione
$VENV $BASE/Execution/enea/youtube_uploader.py "$BASE/Cleaned/[Titolo]/[clean_title]_cleaned.mp4" "[Titolo Video]" "$BASE/Cleaned/[Titolo]/video_metadata.md" --thumbnail "$BASE/Cleaned/[Titolo]/copertina.png"

# Programmare post Instagram (Buffer)
$VENV $BASE/Execution/marcello/buffer_post_single.py --platform instagram --hour 10

# Schedulare post Facebook (Buffer dry run obbligatorio)
$VENV $BASE/Execution/marcello/buffer_post_single.py --dry-run

# Eseguire ciclo di crescita "Authority Cycle" (SEO, Internal Linking, Social Bridge)
$VENV $BASE/Execution/romolo/crescita_orchestrator.py

# Ingestione base di conoscenza su SuperMemory
$VENV $BASE/Execution/augusto/supermemory_ingestor.py

# Backup GitHub offuscato
$VENV $BASE/Execution/mercurio/mercurio_github_sync.py
```

---

## 16. CHECKLIST PRIMA DI OGNI INTERVENTO

- [ ] Ho letto `GEMINI.md` e le SOP rilevanti?
- [ ] Sto usando `.venv/bin/python3` e non il Python di sistema?
- [ ] Ho letto `video_tracking.json` prima di operazioni di pubblicazione?
- [ ] I segreti restano nel `.env` e non finiscono nei file sorgente?
- [ ] Ho aggiornato il file SOP/workflow con eventuali nuovi casi limite?
- [ ] Ho eseguito `/backup` dopo modifiche significative?
- [ ] Se è un processo in background, ho impostato `PYTHONUNBUFFERED=1`?
- [ ] Per Buffer, ho fatto dry-run prima del post reale?
- [ ] La didascalia Facebook inizia con "Lo studio..."?
- [ ] NotebookLM è configurato in italiano (non inglese)?
- [ ] Ho verificato l'impatto sul codice con `code-review-graph` prima di toccare funzioni helper?

---

*Documento generato il 21/05/2026 — Aggiornare ad ogni modifica architetturale significativa.*

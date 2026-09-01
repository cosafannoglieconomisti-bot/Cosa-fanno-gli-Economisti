# Cosa fanno gli Economisti 🇮🇹 📈

Benvenuti nel repository ufficiale di **"Cosa fanno gli economisti"**, il canale dedicato alla divulgazione scientifica in ambito economico. Qui gestiamo tutta la logica di automazione che trasforma complessi paper accademici in video coinvolgenti, infografiche e contenuti social.

## 🚀 Visione del Progetto
Il nostro obiettivo è rendere la ricerca economica di alto livello (AER, QJE, Econometrica, ecc.) accessibile a tutti, mantenendo il rigore scientifico ma utilizzando un tono divulgativo e accattivante.

## 🏗️ Architettura a 3 Livelli
Operiamo su un'architettura progettata per massimizzare l'affidabilità:
1.  **Direttive (Livello 1)**: SOP in Markdown che definiscono *cosa* fare (obiettivi, input, output).
2.  **Orchestrazione (Livello 2)**: Routing operativo gestito da Codex/chat e dai workflow locali, che decidono *come* eseguire le direttive.
3.  **Esecuzione (Livello 3)**: Script Python deterministici che svolgono il lavoro pesante (API, editing video, calcoli).

## 🤖 La Squadra degli Agenti
Il sistema è coordinato da diversi "agenti" specializzati:
- **Enea**: Produzione video completa, gestione paper e upload YouTube.
- **Romolo**: Analytics, gestione commenti e ottimizzazione Shorts.
- **Marcello**: Social Media manager (Instagram attivo; Facebook sospeso dal 2026-08-31; TikTok).
- **Ulisse**: Monitoraggio news e matching con la letteratura accademica.
- **Cesare**: Interfaccia Telegram Hub e notifiche.
- **Mercurio**: Backup GitHub, Gmail e comunicazioni.
- **Augusto**: Gestione persistenza e pulizia file.

## 🛠️ Automazione e Sicurezza
I commit e i push in questo repository sono generati automaticamente tramite il comando `/backup`. 

## Codex Control Plane
Da ora il punto di ingresso operativo principale non e' piu il bot Telegram Cesare ma la chat Codex, anche da mobile.

- Per avviare i workflow basta scrivere in chat richieste come `avvia workflow paper`, `fai produzione`, `esegui pulizia`, `fai upload`, `genera report`, `controlla gmail`, `scouting competitor`, `fai backup`.
- Codex esegue i workflow locali tramite il runner generale `./workflow` o invocando direttamente gli script di `Execution/` quando serve un controllo piu fine.
- Cesare resta codice storico nel repository, ma non e' piu la control plane raccomandata per l'operativita' quotidiana.
- I workflow attivi sono stati riportati a una logica locale e deterministica: niente dipendenza operativa da Gemini per `/paper`, `/pulizia`, playlist, report e traduzioni.
- **Copertine**: la superficie primaria da oggi e' il motore immagine nativo di Codex/OpenAI, non Gemini/Imagen. La copertina va sempre mostrata e approvata prima di qualunque archiviazione in `Cleaned/`.

## Terminal Workflows
I workflow principali del bot Telegram sono ora richiamabili anche direttamente dal terminale, senza dipendere da Cesare:

```bash
./workflow list
./workflow paper
./workflow produzione
./workflow pulizia
./workflow upload
```

Il runner generale vive in `Execution/workflows/general_workflows.py` e copre anche `backup`, `gmail`, `report`, `articoli`, `copertina`, `playlist` e `competitor`.

### Regola OAuth YouTube
- Il token autorevole per YouTube upload e' `Execution/credentials/token.pickle`.
- Prima di `/upload`, eseguire sempre il preflight `./workflow youtube-auth`.
- Se Google rifiuta il refresh token (`invalid_grant`), usare `./workflow youtube-auth --force` per riaprire il login browser e rigenerare il token.
- **App Google in modalità Test:** i permessi OAuth scadono dopo ~7 giorni; se vedi `invalid_grant`, rifare `./workflow youtube-auth --force`.
- I file legacy `Execution/credentials/token_youtube.pickle` e `Execution/romolo/.tmp/tokens/token_youtube.pickle` non sono fonti di verita': vengono solo sincronizzati dal token principale per compatibilita' temporanea.

### 📁 Struttura del Backup
Il backup include tutte le cartelle logiche del canale:
- `Directives/`, `Execution/`, `.agents/`: Logica, istruzioni e script.
- `Cleaned/`: Archivio di metadati, infografiche e sottotitoli dei video pubblicati.
- **Esclusione Video**: I file `.mp4` sono sempre esclusi dal backup per massimizzare la velocità e il risparmio di spazio.

> [!IMPORTANT]
> **Sicurezza dei Dati**: token e chiavi API vanno solo in `.env` (mai nel repository). L'hook pre-push blocca percorsi macOS reali e pattern di segreti nei file tracciati; non sostituisce la revoca di token esposti in commit precedenti.

## Installazione

Per chi clona il repository da zero:

1. **Python 3.11** — vedi `.python-version` (`pyenv install` se usi pyenv).
2. **Virtualenv** — `python3 -m venv .venv && source .venv/bin/activate`
3. **Dipendenze** — `pip install -r requirements.txt`
4. **Programmi esterni**
   - `ffmpeg` — es. `brew install ffmpeg` (Mac) o pacchetto di sistema
   - `nlm` — CLI NotebookLM: `pip install notebooklm-mcp-cli` (poi `nlm login`)
5. **Configurazione** — `cp .env.example .env` e compila le variabili (vedi commenti nel file)
6. **Cartelle locali** — create automaticamente da `./setup.sh`, oppure manualmente:
   `Papers/Da fare`, `Temp/enea`, `Temp/assets`, `Temp/cesare`, `Execution/credentials`
7. **YouTube** — credenziali Google OAuth in `Execution/credentials/`; verifica con `./workflow youtube-auth`
8. **Verifica** — `./workflow list` deve elencare i comandi disponibili

Setup rapido: `./setup.sh`

### Modelli Whisper (primo uso)

I comandi di trascrizione (`pulizia`) scaricano automaticamente il modello `base` di faster-whisper (~150 MB) al primo avvio. L'operazione può richiedere alcuni minuti e sembra un blocco — è normale.

---
*Creato con ❤️ per la divulgazione economica.*

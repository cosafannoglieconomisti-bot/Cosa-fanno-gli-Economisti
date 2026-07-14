# Cosa fanno gli Economisti 🇮🇹 📈

Benvenuti nel repository ufficiale di **"Cosa fanno gli economisti"**, il canale dedicato alla divulgazione scientifica in ambito economico. Qui gestiamo tutta la logica di automazione che trasforma complessi paper accademici in video coinvolgenti, infografiche e contenuti social.

## 🚀 Visione del Progetto
Il nostro obiettivo è rendere la ricerca economica di alto livello (AER, QJE, Econometrica, ecc.) accessibile a tutti, mantenendo il rigore scientifico ma utilizzando un tono divulgativo e accattivante.

## 🏗️ Architettura a 3 Livelli
Operiamo su un'architettura progettata per massimizzare l'affidabilità:
1.  **Direttive (Livello 1)**: SOP in Markdown che definiscono *cosa* fare (obiettivi, input, output).
2.  **Orchestrazione (Livello 2)**: Routing intelligente gestito da agenti AI che decidono *come* eseguire le direttive.
3.  **Esecuzione (Livello 3)**: Script Python deterministici che svolgono il lavoro pesante (API, editing video, calcoli).

## 🤖 La Squadra degli Agenti
Il sistema è coordinato da diversi "agenti" specializzati:
- **Enea**: Produzione video completa, gestione paper e upload YouTube.
- **Romolo**: Analytics, gestione commenti e ottimizzazione Shorts.
- **Marcello**: Social Media manager (Facebook, Instagram, TikTok).
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
- I file legacy `Execution/credentials/token_youtube.pickle` e `Execution/romolo/.tmp/tokens/token_youtube.pickle` non sono fonti di verita': vengono solo sincronizzati dal token principale per compatibilita' temporanea.

### 📁 Struttura del Backup
Il backup include tutte le cartelle logiche del canale:
- `Directives/`, `Execution/`, `.agents/`: Logica, istruzioni e script.
- `Cleaned/`: Archivio di metadati, infografiche e sottotitoli dei video pubblicati.
- **Esclusione Video**: I file `.mp4` sono sempre esclusi dal backup per massimizzare la velocità e il risparmio di spazio.

> [!IMPORTANT]
> **Sicurezza dei Dati**: Per proteggere l'integrità del canale, tutti i token API, le chiavi private e gli ID sensibili vengono **automaticamente offuscati** durante la fase di backup. Il codice che vedi qui è pronto per l'ispezione, ma i dati di produzione rimangono protetti in locale.

---
*Creato con ❤️ per la divulgazione economica.*

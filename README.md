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

### 📁 Struttura del Backup
Il backup include tutte le cartelle logiche del canale:
- `Directives/`, `Execution/`, `.agents/`: Logica, istruzioni e script.
- `Cleaned/`: Archivio di metadati, infografiche e sottotitoli dei video pubblicati.
- **Esclusione Video**: I file `.mp4` sono sempre esclusi dal backup per massimizzare la velocità e il risparmio di spazio.

> [!IMPORTANT]
> **Sicurezza dei Dati**: Per proteggere l'integrità del canale, tutti i token API, le chiavi private e gli ID sensibili vengono **automaticamente offuscati** durante la fase di backup. Il codice che vedi qui è pronto per l'ispezione, ma i dati di produzione rimangono protetti in locale.

---
*Creato con ❤️ per la divulgazione economica.*

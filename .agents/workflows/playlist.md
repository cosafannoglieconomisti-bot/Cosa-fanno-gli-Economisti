# Workflow: /playlist

**Agente Responsabile**: Romolo (via Cesare)

**Obiettivo**: Catalogare automaticamente i nuovi video all'interno delle playlist tematiche di YouTube o aggiungerli a una esistente basandosi sui metadati del paper.

## 1. Trigger
L'utente invia il comando `/playlist` seguito dal nome della cartella del video in `Cleaned/` oppure selezionandolo da un menu interattivo generato dal bot.

## 2. Azioni Eseguite dallo Script (`catalog_video.py`)
1. **Recupero Metadati**: Cerca in `Cleaned/video_tracking.json` l'ID YouTube corrispondente al video indicato.
2. **Consultazione Gemini**: Passa a Gemini il titolo del paper e la descrizione (`video_metadata.md`). Gemini, seguendo il suo prompt system per l'agente Romolo, stabilisce la categoria economica più adatta (es. "Economia del Crimine e Mafie", "Storia Economica e Sviluppo", ecc.).
3. **Integrazione API YouTube**: Autenticazione OAuth e aggiornamento della playlist indicata aggiungendo l'`youtube_id` del video.
4. **Persistenza**: Salva in `video_tracking.json` l'esito della categorizzazione per non ripeterla in futuro.

## 3. Gestione Fallback
Se l'API fallisce o la categoria non è riconosciuta, il video viene provvisoriamente inserito in "Economia Politica e Istituzioni" e viene mandata una notifica tramite Telegram all'utente.

## 4. Esecuzione Batch Iniziale
Al momento della configurazione, tutte le playlist sono state popolate automaticamente eseguendo in locale lo script `Execution/romolo/create_playlists_batch.py`, il quale ha assegnato retroattivamente ogni video alla playlist corretta.

## Comandi Manuali Associati
*Esecuzione per singolo video dal terminale (per debug):*
```bash
python3 Execution/romolo/catalog_video.py "Nome_Cartella_Video_o_Youtube_ID"
```

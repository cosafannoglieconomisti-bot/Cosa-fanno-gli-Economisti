# Marcello — Directive: Pubblicazione Facebook via Buffer API

**Versione**: 2.0 — Deterministica  
**Agente**: Marcello  
**Script principale**: `Execution/marcello/buffer_post_single.py`

---

## OBIETTIVO

Pubblicare i video del canale YouTube su Facebook in modo automatico, deterministico e conforme alle SOP. Un video alla volta. Nessuna improvvisazione dell'IA sulla didascalia.

---

## INPUT

| Input | Fonte |
|-------|-------|
| Lista video YouTube (non-Shorts) | API YouTube v3 (`token_youtube.pickle`) |
| Metadati video (titolo paper, autori, rivista, anno, descrizione, tag) | `Cleaned/[cartella]/video_metadata.md` |
| Storico post già pubblicati | `Temp/marcello/facebook_history.json` |
| Token Buffer | Hardcoded in `buffer_post_single.py` |
| Profile ID Facebook (Buffer) | `69baada37be9f8b1716baa0d` |

---

## TOOL / SCRIPT

**Script unico**: `Execution/marcello/buffer_post_single.py`

Nessun altro script deve essere usato per postare su Facebook via Buffer. `buffer_auto_sync.py` e `buffer_sync_today.py` sono **deprecati** per il posting (rimangono per riferimento storico).

---

## OUTPUT

Un post programmato su Buffer per la pagina Facebook "Cosa fanno gli Economisti" con:
- Data: domani alle 09:00 Europe/Rome (o intervallo di 3 ore per video successivi)
- Anteprima YouTube generata automaticamente da Facebook via OG tags

---

## PROCEDURA STEP-BY-STEP (100% deterministica)

### Pre-check (SEMPRE prima di procedere)
```
1. Verificare che la coda Buffer abbia slot disponibili (< 10 post)
2. Leggere facebook_history.json per sapere quali video sono già stati postati
```

### Esecuzione
```
1. DRY RUN obbligatorio:
   python3 buffer_post_single.py --dry-run
   
2. Verificare nell'output del dry run:
   ✓ **Riga 1**: Deve iniziare con "Lo studio \"TITOLO ACCADEMICO\"..."
   ✓ **Senza Header**: Non devono esserci titoli o autori sopra la descrizione.
   ✓ Il titolo accademico nella descrizione = titolo REALE del paper (non del video)
   ✓ tags: hashtag reali del video (non generici)
   ✓ Link: https://www.youtube.com/watch?v=[ID] (non youtu.be)
   ✓ Scheduled: domani 09:00 Europe/Rome (o ora specificata)

3. POST REALE (solo se dry run è OK):
   python3 buffer_post_single.py

4. Verificare che l'history sia aggiornata:
   Temp/marcello/facebook_history.json deve contenere il nuovo video_id
```

---

### Formato Didascalia (CONTRATTO IMMUTABILE):
```
[Descrizione YouTube — paragrafo "Lo studio \"TITOLO PAPER\" di AUTORI...analizza..."]

▶ https://www.youtube.com/watch?v=[VIDEO_ID]

[Tag estratti da video_metadata.md — mai generati dall'IA]
```

**Esempio validato (Folklore):**
```
Lo studio "Folklore" di Michalopoulos e Xue, pubblicato su The Quarterly Journal di Economics nel 2021, analizza l'importanza economica delle tradizioni orali. Attraverso lo studio dei miti di centinaia di gruppi etnici, i ricercatori dimostrano come le storie tramandate per millenni influenzino ancora oggi la fiducia, l'attitudine al rischio e i ruoli di genere, plasmando lo sviluppo economico delle nazioni.

▶ https://www.youtube.com/watch?v=7sNESUojy0w

#CosaFannoGliEconomisti #Folklore #QJE
```

⚠️ **Regola SOP sulla riga di inizio**:
Il post **DEVE** iniziare direttamente con la stringa `Lo studio "..."`. Non aggiungere titoli, autori o righe vuote in testa.
La riga 1 della caption deve essere estratta dal campo `description` del metadata.

---

## PARAMETRI API BUFFER (immutabili)

| Parametro | Valore | Note |
|-----------|--------|------|
| Endpoint | `https://api.bufferapp.com/1/updates/create.json` | API v1 |
| Metodo | POST | |
| `access_token` | `MUSsM5Rne1WFTFKRR8wHjP7u8aKOMY08lNZoeNZxChB` | Token Marcello |
| `profile_ids[]` | `69baada37be9f8b1716baa0d` | Pagina Facebook |
| `text` | Caption completa (multilinea) | Encoding automatico via `requests` |
| `media[link]` | URL YouTube completo | Genera anteprima video su Facebook |
| `scheduled_at` | Unix timestamp | Domani 09:00 Europe/Rome |
| `shorten` | `false` | Non accorciare link |
| **NON usare** | `media[picture]` | Sovrascrive l'anteprima video dinamica |
| **NON usare** | `now=true` | Causa invio immediato non voluto |

---

## GESTIONE ERRORI

| Codice / Messaggio | Causa | Azione |
|--------------------|-------|--------|
| `code: 1023` — "10 scheduled post limit" | Coda piena | Svuotare coda con destroy.json, poi postare |
| `500` con body vuoto | Problema encoding testo | Script usa `requests` (non curl) — verificare connessione |
| Metadata non trovato | Nome cartella non corrisponde al titolo YT | Controllare Cleaned/ manualmente e aggiustare matching |
| Duplicati in coda | Post inviato più volte | Controllare coda, tenersi il più recente, eliminare gli altri |
| `"success": false` | Token scaduto | Aggiornare token su buffer.com e in GEMINI.md |

---

## LIMITI E VINCOLI

- **Piano Free Buffer**: max 10 post in coda contemporaneamente
- **Un video alla volta**: la procedura deve essere ripetuta per ogni video. MAI batch automatico senza approvazione esplicita dell'utente
- **Shorts esclusi**: video con `#shorts` nel titolo vengono ignorati automaticamente
- **No allucinazioni**: la didascalia viene estratta meccanicamente da `video_metadata.md`. MAI generarla da zero
- **Tag reali**: usare sempre quelli presenti in `video_metadata.md`, non generici

---

## CASI LIMITE DOCUMENTATI

### Caso 1: Coda piena al momento del post (2026-03-30)
**Situazione**: 10 post errati in coda da run precedenti.  
**Soluzione**: Chiamata `destroy.json` su tutti gli update pending, poi postare il video corretto.  
**Prevenzione**: Il dry run deve includere un check della coda prima del post reale.

### Caso 2: curl vs requests (2026-03-30)
**Situazione**: `curl --data-urlencode` restituiva risposta vuota (`500` silenzioso) con testo multilinea italiano (apostrofi, accenti).  
**Soluzione**: Usare `requests.post()` di Python con `data={}` dict — encoding automatico corretto.  
**Regola**: Non usare mai curl per il posting. Usare solo `requests`.

### Caso 3: 3 duplicati in coda (2026-03-30)
**Situazione**: Retry dello script aveva creato 3 copie dello stesso post (errori silenti di curl avevano comunque accodato i post).  
**Soluzione**: Tenersi il più recente (`updates[0]` = il più recente), eliminare gli altri.

### Caso 4: Titolo video invece di titolo accademico nei metadata (bug noto)
**Situazione**: In alcuni `video_metadata.md` il campo `Lo studio "..."` riporta il titolo del video YouTube invece del titolo accademico reale del paper.  
**Esempio**: *La Peste Nera* → `Lo studio "La Peste Nera: il segreto..."` invece di `Lo studio "How the West 'Invented' Fertility Restriction"` (Voigtländer e Voth, AER 2013, DOI: 10.1257/aer.103.6.2227).  
**Soluzione**: Correggere manualmente il `video_metadata.md` prima del posting.  
**Prevenzione**: La SOP Enea deve estrarre il titolo accademico direttamente dal PDF del paper.

---

## 📋 File Python Utilizzati (ordine di esecuzione)
1. `Execution/marcello/buffer_post_single.py` (unico script autorizzato per posting su Buffer)

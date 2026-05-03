---
description: Programmazione di UN singolo video YouTube su Facebook via Buffer API (SOP Marcello)
---

# Workflow `/facebook` — Pubblicazione Facebook via Buffer API

// turbo-all

## Prerequisiti (controllare sempre prima di iniziare)
1. Verificare che la coda Buffer non sia piena (max 10 post su piano Free):
   ```bash
   /Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 -c "
   import requests, json
   TOKEN = [REDACTED]
   FB_ID = '69baada37be9f8b1716baa0d'
   r = requests.get(f'https://api.bufferapp.com/1/profiles/{FB_ID}/updates/pending.json?access_token={TOKEN}&count=10', timeout=10)
   n = len(r.json().get('updates', []))
   print(f'Post in coda: {n}/10')
   "
   ```
   - Se la coda è piena (10/10), **svuotarla** prima di procedere con lo step di svuotamento coda (vedi sotto).

---

## Step 1 — Dry Run (MANDATORIO prima di ogni post reale)

```bash
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/buffer_post_single.py \
  --dry-run
```

**Verificare nell'output:**
- **Visualizza**: Controlla bene l'anteprima della didascalia. **Deve iniziare direttamente con "Lo studio..."**. Se c'è un titolo, lo script è rotto.
- **Link**: Deve mostrare l'anteprima corretta di Facebook (genera un overlay nel log se possibile).
- Descrizione = prima parte della descrizione YouTube (`Lo studio "TITOLO PAPER" di ... analizza ...`)
- Il titolo tra virgolette nella descrizione = titolo ACCADEMICO REALE (non titolo del video)
- Tag estratti dal file `video_metadata.md` del video (non generici)
- Link YouTube corretto
- Data programmazione = domani alle 09:00 Europe/Rome (o orario convenuto)

---

## Step 2 — Post Reale

Solo dopo aver verificato il dry run:

```bash
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/buffer_post_single.py
```

✅ Se l'output contiene `"success":true` → post programmato, history aggiornata automaticamente.  
❌ Se fallisce → leggere il messaggio di errore e gestirlo (vedi sezione Errori).

---

## Step 3 — Verifica post-invio

```bash
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 -c "
import requests, json
TOKEN = [REDACTED]
FB_ID = '69baada37be9f8b1716baa0d'
r = requests.get(f'https://api.bufferapp.com/1/profiles/{FB_ID}/updates/pending.json?access_token={TOKEN}&count=10', timeout=10)
for u in r.json().get('updates', []):
    print(u['id'], '|', u.get('scheduled_at'), '|', u.get('text','')[:80].replace(chr(10),' '))
"
```

Confermare che nella coda sia presente UN SOLO post relativo al video appena programmato.

---

## Step 4 — Sincronizzazione Registro

```bash
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/tracking_manager.py \
  "[Project_Name]" "facebook_url" "[URL_O_PROGRAMMATO]"
```
Aggiornare mandatoriamente lo stato su `video_tracking.json` per garantire il determinismo del registro.

---

## Svuotamento Coda (se piena o con duplicati)

```bash
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 -c "
import requests, json
TOKEN = [REDACTED]
FB_ID = '69baada37be9f8b1716baa0d'
r = requests.get(f'https://api.bufferapp.com/1/profiles/{FB_ID}/updates/pending.json?access_token={TOKEN}&count=10', timeout=10)
updates = r.json().get('updates', [])
print(f'Elimino {len(updates)} post...')
for u in updates:
    d = requests.post(f'https://api.bufferapp.com/1/updates/{u[\"id\"]}/destroy.json', data={'access_token': TOKEN}, timeout=10)
    print('✅' if d.json().get('success') else '❌', u['id'])
"
```

> **ATTENZIONE**: Questo cancella TUTTI i post in coda. Usare solo se la coda contiene post errati.

---

## Forzare un video specifico (per ID YouTube)

```bash
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 \
  /Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/buffer_post_single.py \
  --video-id [ID_YOUTUBE] --dry-run
```

---

## REGOLE MANDATORIE (SOP Marcello — da non derogare mai)

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
⚠️ **Regola SOP sulla riga di inizio**: Il post **DEVE** iniziare direttamente con la stringa `Lo studio "..."`. Non aggiungere titoli, autori o righe vuote in testa.
Lo studio "..."` nei metadata**:
Il titolo tra virgolette nella frase `Lo studio "..." di Autori...` in `video_metadata.md`
deve essere il **titolo ACCADEMICO REALE** del paper, NON il titolo del video YouTube.
Se i due coincidono per errore (come in *La Peste Nera*), il metadata va corretto manualmente.

### Regole tecniche:
- **API**: Buffer API v1 — `https://api.bufferapp.com/1/updates/create.json`
- **Token**: `MUSsM5Rne1WFTFKRR8wHjP7u8aKOMY08lNZoeNZxChB`
- **Profile ID Facebook**: `69baada37be9f8b1716baa0d`
- **Anteprima Facebook**: Usare **SEMPRE** `media[picture]=COPERTINA` per caricare la copertina come foto. Il link YouTube deve essere presente solo nel testo della didascalia. NON usare più l'anteprima dinamica (link attachment).
- **Programmazione**: Sempre con `scheduled_at=[UNIX_TIMESTAMP]`. Default: domani ore 09:00 Europe/Rome.
- **Un video alla volta**: MAI postare batch. Verificare sempre il dry run prima del post reale.
- **Shorts esclusi**: I video con `#shorts` nel titolo devono essere ignorati (filtro applicato dallo script).
- **History**: Il file `Temp/marcello/facebook_history.json` traccia i video già postati. Aggiornarlo dopo ogni post riuscito.
- **Fonte Metadati**: Sempre e solo da `Cleaned/[cartella_video]/video_metadata.md`. Mai generare didascalie da zero con l'IA.

---

## Gestione Errori

| Errore | Causa | Soluzione |
|--------|-------|-----------|
| `code: 1023` — limite 10 post | Coda piena | Eseguire lo svuotamento coda, poi ripetere |
| `500` con body vuoto | Testo con caratteri speciali | Lo script usa `requests` con encoding automatico |
| `"success": false` | Token scaduto o revocato | Verificare il token su buffer.com |
| Metadata non trovato | Cartella non matchata | Controllare nome cartella in `Cleaned/` |
| Duplicati in coda | Post inviato più volte | Tenersi il più recente, eliminare gli altri |

---

## 📋 File Python Utilizzati (ordine di esecuzione)
1. `Execution/marcello/buffer_post_single.py` (Post singolo video su Buffer — script principale)

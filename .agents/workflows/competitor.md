---
description: Scouting competitor e proposte commenti di alto valore correlati ai paper (routine Lun/Mer/Ven 10:51)
---

# Workflow: /competitor

**OBIETTIVO**: Identificare 5 video recenti di competitor/canali affini e proporre commenti di alto valore che citano un paper accademico e linkano un video del canale "Cosa fanno gli economisti".

## Cadenza (routine)
- **Lunedì, Mercoledì, Venerdì alle 10:51 Europe/Rome** (routine Grok Bot creata il 2026-10-08).
- La routine esegue solo lo scouting (`./workflow competitor`) e manda a Marco in chat le proposte. **Non pubblica nulla da sola.**

## Regole fisse
- **Approvazione MANDATORIA di Marco in chat prima di qualsiasi pubblicazione.** Nessun commento parte senza un suo ok esplicito su quali proposte (es. "vai con 1, 3 e 5") ed eventuali modifiche al testo.
- **Regola 30 giorni** (DECISIONS 2026-06-05): si commentano solo video pubblicati al massimo 30 giorni fa. Lo script passa `publishedAfter = ora - 30 giorni` a tutte le ricerche (canali fissi e keyword) e ricontrolla la data lato client.
- **Titolo editoriale** (DECISIONS 2026-07-16): il link al nostro video usa il titolo editoriale del video; il titolo del paper solo come supporto. Tono variato, umano, giovane, cordiale, non seriale.
- **Niente spam**: max 5 proposte per giro, max 1 per canale e 1 per nostro video; mai due volte lo stesso video (storico `Temp/romolo/competitor_comment_history.json`). Non limitarsi sempre agli stessi account.
- Scartare in revisione video fuori tema, non in italiano o con match debole.

## Canali fissi (`TARGET_CHANNELS_MAP` in `Execution/romolo/competitor_scout.py`)
Channel ID verificati il 2026-10-08 (feed RSS 200 + `channels.list`). Mai aggiungere un ID non verificato.

| Canale | Channel ID | Handle |
|---|---|---|
| Will Media | UCZM5aON36Iw0o0ngTaQSWVA | @willmedia |
| I podcast di Will Media | UCFg4BxczDuIRtBeuo46DE8g | @willmedia-podcast |
| Geopop | UCx7EWheHmjCW3vX8K2d09vg | @geopop |
| Starting Finance | UCBahpZUV9wGy0ZdiVL2rqCA | @startingfinance |
| Factanza Media | UCBdiMDTxwgNXz4PQa0uUhGw | @factanzamedia |
| Breaking Italy | UC4V3oCikXeSqYQr0hBMARwg | @breakingitaly |
| LiberiOltre | UCrdEJmK5bgFte04-UF7o29Q | @liberioltre |
| Nova Lectio | UCRCWJCFoZUvkkWzIqzfBy6g | @novalectio |
| Michele Boldrin | UCMOiTfbUXxUFqJJtCQGHrrA | @micheleboldrin |
| ORA! | UCJ1kdZmbCGxMVnWIahisqjA | @ora.italia |
| Mr. RIP | UCBOtZaVafz_5OmUrqJAVStQ | @mr_rip |
| Limes Rivista Italiana di Geopolitica | UCgG9BnqkGnU-ouYa5eAOdEw | @limesgeopolitics |
| WesaChannel | UCaM-zH6ji5kWncFMaBBc7Yg | @wesachannel |
| Scacchiere Globale | UC8_OU41iCKb6Ri847Ea4JTQ | @scacchiereglobale |
| What's up Economy | UCnE113MJbg0sY5Ji0ZOOtcw | @whatsupeconomy |
| Il Post | UCGe1EHmk2SHt9fnpIRchvqg | @ilpostvideo |
| Osservatorio CPI | UCEKOjs5vHu9pZoV2jR0NGlQ | @osservatoriocpi |

## Procedura Operativa

1. **Scouting (automatico nella routine)**: `./workflow competitor` → `Execution/romolo/competitor_scout.py`.
   - Auth non interattiva: token `Execution/credentials/token.pickle` (fallback legacy). Se il token non è valido lo script si ferma con l'istruzione `./workflow youtube-auth` (nessun browser in automatico).
   - Ricerca ibrida: ultimi 3 video (≤30 gg) di ogni canale fisso + 6 keyword tematiche a caso (≤30 gg, `regionCode=IT`, lingua it).
   - Rimuove duplicati e video già commentati (storico JSON).
   - Quota: circa 23 `search.list` ≈ **2.300 unità** per giro (limite giornaliero standard 10.000).
2. **Proposte**: matching locale con il catalogo (`Cleaned/video_tracking.json` + `video_metadata.md`), commento generato da template variati.
   - Report leggibile: `Temp/romolo/competitor_engagement.md` (con data di pubblicazione, candidati e quota).
   - Versione macchina: `Temp/romolo/competitor_proposals.json` (campi `index`, `video_id`, `comment`, `approved`).
3. **Revisione di Marco in chat (MANDATORIA)**: mandare a Marco le 5 proposte. Lui approva, scarta o modifica il testo. Senza ok esplicito ci si ferma qui.
4. **Pubblicazione (solo dopo ok)**:
   - Riportare le modifiche di Marco nel campo `comment` del JSON, poi:
     `.venv/bin/python3 Execution/romolo/post_youtube_comment.py --batch --only 1,3,5`
   - Il batch salta i video già commentati, prosegue se un video ha i commenti disattivati e **scrive lo storico una sola volta a fine giro** (scrittura atomica con merge), evitando la race documentata il 2026-06-25.
   - La modalità singola `post_youtube_comment.py <video_id> "<testo>"` resta per i casi isolati (aggiorna lo storico subito, anche lei in modo atomico).
5. **Log**: aggiungere in `canale_LOG.md` (Brain) data, numero commenti pubblicati e canali.

## File Python Utilizzati
1. `Execution/romolo/competitor_scout.py` (scouting + report + JSON proposte)
2. `Execution/romolo/post_youtube_comment.py` (pubblicazione, solo dopo approvazione)

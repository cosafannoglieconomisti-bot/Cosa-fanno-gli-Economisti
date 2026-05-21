# SOP: Strategia di Crescita — "The Authority Cycle"

**OBIETTIVO**: Trasformare il canale da una collezione di video isolati in un ecosistema autorevole e interconnesso che massimizzi la Session Duration (YouTube) e la Relevance (Social).

---

## 1. Modulo SEO Semantico (Tag & Keywords)

L'indicizzazione di YouTube si basa pesantemente sulle prime 3 righe della descrizione e sugli hashtag.
- **Regola**: Ogni volta che un tema diventa "caldo" (rilevato da Ulisse), il sistema deve aggiornare i tag in fondo ai `video_metadata.md` dei video correlati.
- **Formato Tag**: Sempre 3-5 hashtag in fondo al file. Devono includere sempre `#CosaFannoGliEconomisti` + 2 tag di categoria + 1-2 tag legati al trend del momento.

## 2. Modulo Internal Linking (Cluster di Contenuti)

Il "Binge-watching" è il segnale #1 per la crescita.
- **Regola**: Ogni descrizione video DEVE contenere una sezione "Ti potrebbe interessare anche" con 2 link ad altri video del canale.
- **Logica di Matching**: Basata sulla playlist di appartenenza o su similarità semantica (es. se parli di "Tasse", linka il video sulle "Pensioni").

## 3. Modulo Social Bridge (News-Jacking)

Uso strategico delle infografiche per commentare la cronaca.
- **Regola**: Ogni mattina, `archive_matcher.py` identifica i 3 match migliori.
- **Output**: Generazione di un file `Temp/crescita/social_bridge_queue.json` pronto per Marcello (Buffer).
- **Contratto Hook**: L'aggancio deve essere: "Notizia del giorno" -> "Domanda/Problema" -> "Soluzione scientifica nel nostro studio".

---

## 4. Trigger di Esecuzione (Automazione)

Il workflow `/crescita` deve essere eseguito:
1. **Ogni Mattina**: All'apertura del workspace (check news vs archivio).
2. **Post-Produzione**: Appena un video viene caricato (per linkarlo nei video vecchi e viceversa).

---

## 📋 File Python Utilizzati
1. `Execution/romolo/seo_tag_refresher.py`
2. `Execution/romolo/internal_linker.py`
3. `Execution/romolo/social_bridge_engine.py`
4. `Execution/romolo/crescita_orchestrator.py`

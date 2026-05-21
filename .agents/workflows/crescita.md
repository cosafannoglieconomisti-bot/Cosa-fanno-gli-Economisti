# Workflow /crescita — Ottimizzazione e Crescita Canale

**OBIETTIVO**: Eseguire la manutenzione SEO e la strategia di ri-pubblicazione dell'archivio.

---

## Fasi del Workflow

### 1. Sincronizzazione Trend (Ulisse)
- Il sistema recupera le ultime news tramite `news_extractor.py`.
- Identifica i temi caldi che hanno un riscontro nell'archivio.

### 2. Manutenzione SEO (Romolo)
- Esegue `seo_tag_refresher.py` per aggiornare gli hashtag dei video in target.
- Esegue `internal_linker.py` per aggiornare i suggerimenti di visione nelle descrizioni, includendo l'ultimo video pubblicato.

### 3. Preparazione Social Bridge (Marcello)
- Esegue `social_bridge_engine.py`.
- Genera i post pronti per Buffer che collegano la notizia del giorno a un'infografica d'archivio.

### 4. Report Finale
- Mostra all'utente un riassunto delle ottimizzazioni effettuate:
    - Video aggiornati (SEO).
    - Nuovi post pronti per la programmazione.

---

## Comandi Correlati
- `/crescita`: Esegue l'intero ciclo di ottimizzazione.
- `/articoli`: (Già esistente) fornisce la base news per il matching.

# Sistema "Crescita" (The Authority Cycle)

Questo modulo gestisce l'ottimizzazione SEO e la strategia di engagement del canale in modo semi-autonomo.

## Componenti

1. **`seo_tag_refresher.py`**:
   - Analizza le news del giorno.
   - Identifica i video d'archivio correlati.
   - Aggiorna gli hashtag nelle descrizioni dei video per intercettare i trend di ricerca attuali.

2. **`internal_linker.py`**:
   - Analizza l'archivio video.
   - Inserisce link "Guarda anche" nelle descrizioni per creare cluster di contenuti.
   - Massimizza il tempo di permanenza degli utenti (Binge-watching signals).

3. **`archive_matcher.py`**:
   - Genera suggerimenti per post social (Facebook/Instagram) collegando news e archivio.
   - Fornisce un "Hook" professionale basato sui dati.

4. **`crescita_orchestrator.py`**:
   - L'unico punto di ingresso per il workflow. Esegue tutti i moduli in sequenza.

## Utilizzo

Il sistema viene eseguito automaticamente:
- Ogni mattina all'avvio della sessione.
- Dopo ogni pubblicazione di un nuovo video (tramite `video_processor.py`).

Per esecuzione manuale:
```bash
/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3 Execution/romolo/crescita_orchestrator.py
```

# Workflow: /competitor

**OBIETTIVO**: Identificare 5 video di competitor/canali affini e proporre commenti di alto valore che citano un paper accademico e linkano un video del canale "Cosa fanno gli economisti".

## Procedura Operativa

1. **Scansione Competitor**:
   - Eseguire lo script `Execution/romolo/competitor_scout.py`.
   - Lo script cerca video recenti (ultimi 7 giorni) da canali target tra cui: Will Media, Geopop, Starting Finance, Factanza, Breaking Italy, Liberi Oltre, Michele Boldrin, L'Avvocato dell'Atomo, Nova Lectio, Rick DuFer, Giopizzi, Pillole di Economia, Il Sole 24 Ore, WesaChannel.
   - Seleziona 5 video casuali tra quelli trovati.

2. **Generazione Proposte**:
   - Per ogni video, lo script identifica un paper correlato nel nostro archivio.
   - Genera una proposta di commento via Gemini Flash.
   - Salva il report in `Temp/romolo/competitor_engagement.md`.

3. **Revisione Utente (MANDATORIA)**:
   - Mostrare all'utente il contenuto di `competitor_engagement.md`.
   - L'utente deve approvare o modificare i commenti.

4. **Pubblicazione**:
   - Una volta approvati, i commenti vengono pubblicati (procedura manuale o via script `post_youtube_comment.py` se implementato per canali esterni).

## File Python Utilizzati
1. `Execution/romolo/competitor_scout.py`

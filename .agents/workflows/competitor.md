---
description: Scouting competitor e proposte commenti di alto valore correlati ai paper
---

# Workflow: /competitor

**OBIETTIVO**: Identificare 5 video di competitor/canali affini e proporre commenti di alto valore che citano un paper accademico e linkano un video del canale "Cosa fanno gli economisti".

## Procedura Operativa

1. **Scansione Competitor & Ricerca Ibrida (Quota Saving)**:
   - Eseguire lo script `Execution/romolo/competitor_scout.py`.
   - Lo script adotta una **strategia ibrida ed efficiente** per salvare la quota giornaliera dell'API di YouTube ed allargare il bacino di video trovati:
     - **Ricerca Semantica per Parole Chiave**: Campiona casualmente keywords tematiche estratte dall'archivio del canale (es. *tasse, previdenza, meritocrazia, demografia, criminalità, automazione*) per cercare video caldi e attinenti da **qualsiasi canale YouTube in lingua italiana**.
     - **Campionamento Canali Target**: Monitora una lista estesa di canali di rilievo (es. *Starting Finance, Will Media, Geopop, ORA!, Mr. Rip, Limes, WesaChannel, Michele Boldrin, ecc.*) pre-caricando i loro **Channel ID fissi** per eliminare chiamate API ridondanti di risoluzione del nome.
   - Raccoglie i candidati e rimuove i duplicati o i video già commentati attingendo allo storico `Temp/romolo/competitor_comment_history.json`.

2. **Generazione Proposte**:
   - Per ogni video idoneo, lo script identifica un paper correlato nel nostro archivio.
   - Genera una proposta di commento di alto valore via Gemini Flash.
   - Salva il report in `Temp/romolo/competitor_engagement.md`.

3. **Revisione Utente (MANDATORIA)**:
   - Mostrare all'utente il contenuto di `competitor_engagement.md`.
   - L'utente deve approvare o modificare i commenti.

4. **Pubblicazione**:
   - Una volta approvati, i commenti vengono inviati alle API di YouTube tramite lo script `Execution/romolo/post_youtube_comment.py` per essere pubblicati automaticamente sotto i video scelti.
   - Lo script inserisce automaticamente gli ID dei video commentati nel registro storico `competitor_comment_history.json`.

## File Python Utilizzati
1. `Execution/romolo/competitor_scout.py`

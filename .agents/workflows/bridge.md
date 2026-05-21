# Workflow: /bridge

**OBIETTIVO**: Automatizzare la creazione di "Social Bridge" (re-post di video d'archivio su Facebook/Instagram) per generare traffico ricorrente verso YouTube e Instagram.

## Procedura Operativa

1. **Selezione Video Archivio**:
   - Leggere `Cleaned/video_tracking.json`.
   - Identificare video con stato `facebook_url == "Postato"` ma che non vengono ri-proposti da tempo (o basandosi su temi attuali).
   - Alternativamente, l'utente può specificare un `video_id`.

2. **Aggiornamento Link Instagram**:
   - Verificare che in `video_metadata.md` sia presente il link all'infografica specifica su Instagram (`https://www.instagram.com/p/...`).
   - Se manca o è rotto, aggiornarlo prima di procedere.

3. **Creazione Hook & Scheduling**:
   - Eseguire `Execution/marcello/buffer_post_single.py`.
   - Parametri necessari:
     - `--video-id`: ID del video YouTube.
     - `--bridge`: "Hook" strategico (testo accattivante che collega il tema a una curiosità o notizia).
     - `--days-ahead`: Giorni di differimento.
     - `--hour`: Ora di pubblicazione (default 09:00).

4. **Validazione**:
   - Eseguire un `--dry-run` per verificare che la didascalia includa il link corretto all'infografica IG e al video YT.

## File Python Utilizzati
1. `Execution/marcello/buffer_post_single.py`

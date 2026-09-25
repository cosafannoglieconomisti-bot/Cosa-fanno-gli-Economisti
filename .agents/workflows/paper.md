---
description: Selezione Paper, Titoli Catchy, Copertina 16:9 e Gate Metadata
---

Questo workflow gestisce il setup iniziale: scelta paper, titolo catchy, copertina 16:9, **draft+approve metadata**, poi solo dopo archiviazione in `Cleaned/`.

1. **Selezione Paper**:
   - L'utente lancia `/paper` in Codex chat o `./workflow paper`.
   - Codex analizza i PDF in `Papers/Da fare/` (**ricorsivamente**) e propone i titoli accademici reali.
   - L'utente seleziona il paper.

2. **Generazione Titoli (approval)**:
   - Il bot estrae il testo tramite `batch_text_extractor.py`.
   - Propone 5 opzioni di titoli "catchy" (massimo 5 parole, stile domanda).
   - Marco approva (o modifica) il titolo.

3. **Generazione e Approvazione Copertina**:
   - Una volta scelto il titolo, Codex genera la copertina **16:9 only** (es. 1280×720) con ChatGPT/Codex native `image_gen` → `Temp/assets/override_cover.png` → `generate_cover.py` copia solo; SOP comic arancio/nero/bianco + testo nativo. Non Gemini/Imagen/.env keys.
   - Le **infografiche** restano quadrati 1:1; solo le **copertine/thumbnail** sono 16:9.
   - La copertina viene mostrata all'utente e va approvata esplicitamente (`approva` / `rigenera`).
   - **Non** creare ancora `Cleaned/` né spostare il PDF.

4. **Draft video_metadata.md + APPROVE METADATA (gate duro)**:
   - Codex redige un draft `video_metadata.md` dal PDF e lo mostra a Marco.
   - Obbligatori: titolo accademico reale; **ALL authors dal PDF** (no auto-hallucination); journal; year; DOI; YT description che inizia con **«Lo studio…»**; **content-specific tags only**.
   - Serve **approvazione esplicita metadata** (o edit + re-approve) **BEFORE** Cleaned archive e **BEFORE** `/produzione` / attiva produzione / Dom-Mer automation.

5. **Setup Cartella e Archiviazione (solo post-metadata OK)**:
   - Solo dopo metadata approvato, Codex:
     - Crea la cartella `Cleaned/[Titolo_Scelto]`.
     - **Sposta e Rinomina** il PDF originale in `Cleaned/[Titolo_Scelto]/[Titolo_Accademico].pdf`.
     - Salva `copertina.png` nella cartella.
     - Scrive il **final** `video_metadata.md`.
     - Salva lo stato in `active_pipeline.json`.

> [!IMPORTANT]
> Gate order `/paper`: (1) select paper → (2) catchy title approval → (3) 16:9 cover approval → (4) **APPROVE METADATA** → (5) Cleaned archive. Vietato archiviare o avviare produzione prima del gate metadata.

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/workflows/general_workflows.py` (Runner workflow)
2. `Execution/enea/batch_text_extractor.py` (Estrazione testo PDF)
3. `image_gen` / motore immagine Codex (Generazione Immagine primaria)
4. `Execution/enea/generate_cover.py` (Legacy fallback, non raccomandato)

## Gate approvazione (obbligatori)
- **Titolo**: approvazione esplicita di Marco.
- **Copertina 16:9**: approvazione esplicita; nessuna archiviazione in `Cleaned/` solo per la cover.
- **Metadata (`video_metadata.md` draft)**: approvazione esplicita **prima** di Cleaned e **prima** di produzione (Dom-Mer). Autori completi dal PDF; no hallucination.
- **Infografica**: se rigenerata in `/pulizia` o dopo, richiedere di nuovo approvazione prima di upload/Buffer.

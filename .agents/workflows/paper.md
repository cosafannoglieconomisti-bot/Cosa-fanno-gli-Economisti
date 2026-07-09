---
description: Selezione Paper, Titoli Catchy e Generazione Copertina
---

Questo workflow gestisce l'intero setup iniziale: scelta del paper, generazione del titolo e creazione della copertina approvata.

1. **Selezione Paper**:
   - L'utente lancia `/paper` in Codex chat o `./workflow paper`.
   - Codex analizza i PDF in `Papers/Da fare/` (**ricorsivamente**) e propone i titoli accademici reali.
   - L'utente seleziona il paper.

2. **Generazione Titoli (Gemini)**:
   - Il bot estrae il testo tramite `batch_text_extractor.py`.
   - Propone 5 opzioni di titoli "catchy" (massimo 5 parole, stile domanda).

3. **Generazione e Approvazione Copertina**:
   - Una volta scelto il titolo, Codex genera una copertina in stile Comic (Arancio/Nero/Bianco) con il motore immagine nativo OpenAI/Codex.
   - La copertina viene mostrata all'utente per approvazione esplicita.
   - L'utente può dire `approva` o `rigenera`.

4. **Setup Cartella e Archiviazione**:
   - All'approvazione della copertina, il bot:
     - Recupera il **Titolo Accademico** reale.
     - Crea la cartella `Cleaned/[Titolo_Scelto]`.
     - **Sposta e Rinomina** il PDF originale in `Cleaned/[Titolo_Scelto]/[Titolo_Accademico].pdf`.
     - Salva `copertina.png` nella cartella.
     - Inizializza `video_metadata.md` con i dati estratti (Autori, Rivista, Anno, DOI).
     - Salva lo stato in `active_pipeline.json`.

> [!IMPORTANT]
> Nessuna archiviazione in `Cleaned/` deve avvenire prima dell'approvazione esplicita della copertina.

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/workflows/general_workflows.py` (Runner workflow)
2. `Execution/enea/batch_text_extractor.py` (Estrazione testo PDF)
3. `image_gen` / motore immagine Codex (Generazione Immagine primaria)
4. `Execution/enea/generate_cover.py` (Legacy fallback, non raccomandato)

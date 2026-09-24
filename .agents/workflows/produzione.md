---
description: Workflow /produzione — NotebookLM long + infografica + short opzionale
---

Genera e scarica asset grezzi. **Non** pulisce né carica.

## Checklist

1. Copertina **già approvata** da Marco; cartella `Cleaned/[Titolo]` pronta.
2. NotebookLM: Video Overview long + Infografica quadrata (sketch_note).
3. Download in `~/Downloads`: `*_raw.mp4`, `*_infografica.png`.
4. **Short (default 1/paper, salvo richiesta Marco di più)**:  
   `./workflow produzione --folder X --with-short` → richiede **notebooklm-mcp-cli ≥ 0.11.7** (`nlm create video --format short`).  
   Output: `{clean_title}_short1_raw.mp4`. Fallback UI se CLI fallisce.
5. Fine `/produzione` → passa a `/pulizia` (long+short).

```bash
./workflow produzione --folder Titolo_Cartella
./workflow produzione --folder Titolo_Cartella --with-short
./workflow produzione --folder Titolo_Cartella --with-short --short-count 1
```

## File Python
- `Execution/enea/notebooklm_orchestrator.py`
- `Execution/enea/short_assets.py`

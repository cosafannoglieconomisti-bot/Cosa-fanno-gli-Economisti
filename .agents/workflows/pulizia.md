---
description: Workflow /pulizia — watermark cover solido, trim RMS ~3.5–4s, short, metadata
---

Post-processing di video + infografica NotebookLM. **Non** fa upload né cleanup finale (quello è `/upload`).

## Checklist long

1. Pipeline attiva (`/paper` + copertina approvata).
2. Input in `~/Downloads`: `*_raw.mp4` + infografica.
3. `./workflow pulizia` / `video_processor.py`:
   - **Watermark**: cover/fill **solido** con colore campionato dallo sfondo (NO delogo soft → macchie).
   - **Trim outro**: ~**3.5–4s**, guidato da **RMS audio**; **non** usare 2.5s aggressivo che taglia la voce di chiusura.
   - Infografica: `clean_infographic.py` → `infografica_cleaned.png`.
   - Whisper IT + traduzioni EN/ES/FR/DE in `international/`.
   - `video_metadata.md` con **tag specifici di contenuto** (es. AreaB, Milano, Lega). Vietati: `#CosaFannoGliEconomisti`, `#APSR`, journal-name-as-hashtag.
4. Gate: se rigeneri l’infografica, fai approvare a Marco prima di procedere.

## Checklist short (default 1/paper)

1. Input: `{clean_title}_short1_raw.mp4` in Downloads (da `/produzione --with-short`, nlm≥0.11.7).
2. `./workflow pulizia --video …_short1_raw.mp4` oppure `--also-short` dopo il long.
3. Output: `{clean_title}_short1_cleaned.mp4` + `Cleaned/[Titolo]/shorts/international/`.
4. Stessi default watermark (cover solido portrait-aware) e trim RMS.
5. Tracking nested: `shorts[{angle, status: Cleaned, …}]` sotto la riga long.

```bash
./workflow pulizia --video Titolo_short1_raw.mp4
./workflow pulizia --also-short
```

## File Python
1. `Execution/enea/video_processor.py`
2. `Execution/enea/video_cleaner.py` (cover solido + trim RMS)
3. `Execution/enea/short_assets.py`
4. `Execution/enea/clean_infographic.py`

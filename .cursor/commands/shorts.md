# /shorts — Ottimizzazione titoli e descrizioni Shorts

Agente Romolo: ottimizza Shorts con titoli-data generici o descrizioni incomplete.

## Priorità
- Titoli tipo "11 aprile 2026" o "Short" → **priorità assoluta**
- Durata < 60 secondi

## Procedura
1. Lista video canale, filtra Shorts da ottimizzare
2. Analizza contenuto (trascrizione YT o Whisper)
3. Match con video long-form padre in `Cleaned/`
4. Genera titolo hook (max 60 char) e descrizione con link `Video completo qui: https://youtu.be/[ID]`
5. Aggiorna via `batch_update_shorts.py`

## Script
1. `Execution/romolo/romolo_manage_channel.py` (listing)
2. `Execution/romolo/batch_update_shorts.py` (update)
3. `Execution/enea/generate_index_whisper.py` (se serve analisi audio)

Chiedi conferma prima di aggiornamenti batch massivi.

---
description: Crea il report Ulisse (News + Matching Accademico)
---

Questo workflow raccoglie le notizie del giorno e cerca articoli scientifici associabili, ottimizzato per evitare errori 429.

1. **Esecuzione (Master Bot)**: 
   - L'operazione viene lanciata dal bot Telegram con `/articoli`.
   - Ulisse scarica il batch completo di news dalle 5 fonti SOP (**ANSA, Corriere, Repubblica, Il Post, Fanpage**).
   - Gemini identifica i **3 temi di consenso** e genera **TITOLI CATCHY (MANDATORIO: MAX 5 PAROLE)**.
   - Generazione delle **Broad Academic Areas** (es: *Health Economics*). **MANDATORIO**: I tag devono essere selezionati per garantire la coerenza semantica con il topic ed evitare allucinazioni.

2. **Verifica Determinista (Loop Locale)**:
   - Python esegue `verify_paper.py` per ogni tema usando una logica **OR** sui tag per massimizzare il matching nei Top Journal.

3. **Report**:
   - Salva la lista in `Temp/ulisse/temi_hot_matched_GG_MM_AAAA_HHMM.txt`.

## 📋 File Python Utilizzati
1. `Execution/cesare/telegram_bot.py` (Lancia la richiesta unificata a Gemini)
2. `Execution/ulisse/verify_paper.py` (Verifica deterministicamente l'esistenza dei paper estratti nel ciclo locale di Python)

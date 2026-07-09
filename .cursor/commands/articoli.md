# /articoli — Report Ulisse (news + matching accademico)

Agente Ulisse: raccoglie notizie del giorno e abbina paper accademici.

## Prima di iniziare
- Leggi `Directives/ulisse/` se presente e `GEMINI.md`.
- Usa solo: `/Users/<USER>/Desktop/canale/.venv/bin/python3`

## Procedura
1. Scarica news da **ANSA, Corriere, Repubblica, Il Post, Fanpage**
2. Identifica 3 temi di consenso con titoli catchy (max 5 parole)
3. Genera Broad Academic Areas coerenti semanticamente
4. Verifica paper con `verify_paper.py` (logica OR sui tag)
5. Salva report in `Temp/ulisse/temi_hot_matched_*.txt`

## Script
1. Orchestrazione via `Execution/cesare/telegram_bot.py` o script Ulisse dedicati
2. `Execution/ulisse/verify_paper.py`

Riporta i 3 temi con paper matchati e link alle fonti.

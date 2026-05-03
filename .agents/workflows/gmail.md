---
description: Leggi e sintetizza le email del canale da Gmail
---

Questo workflow scarica le ultime email da Gmail e le riporta in chat, ottimizzato per messaggi lunghi.

1. **Esecuzione (Master Bot)**:
   - L'utente lancia il comando `/gmail` dal Bot Telegram.
   - Il bot invoca lo script `mercurio_gmail_manager.py`.

2. **Raccolta Dati (Gmail API)**:
   - Lo script sonda le email non lette (mittente, oggetto, snippet).
   - Salva un report `.txt` in `Temp/mercurio/gmail_report.txt`.

3. **Invio (Suddivisione Messaggi)**:
   - Il bot legge il Report. Se supera la soglia di Telegram (4096 caratteri), lo divide in più tranche e le invia consecutivamente per garantire la ricezione.

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/cesare/telegram_bot.py` (Orchestra il comando)
2. `Execution/mercurio/mercurio_gmail_manager.py` (Interroga Gmail API)

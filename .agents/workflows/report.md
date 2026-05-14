---
description: Crea il report del canale YouTube (Analytics + Strategie)
---

Questo workflow raccoglie le statistiche del canale dell'ultimo mese e rilascia consigli strategici avanzati tramite Consulenza AI.

1. **Esecuzione (Master Bot)**:
   - L'utente lancia `/report`.
   - Il bot invoca lo script `romolo_manage_channel.py`.

2. **Raccolta Dati (YouTube API)**:
   - Lo script sonda visualizzazioni, watch time, iscritti e gli ultimi commenti per diagnosticare lo stato di salute.

3. **Consulenza AI (Gemini SMM Expert)**:
   - Gemini legge i dati aggregati e rilascia 3 consigli strategici AZIONABILI (Actionable) in stile Social Media Manager esperto (SEO, argomenti, clickbait-worthy thumbnails).

4. **Invia (Suddivisione Messaggi)**:
   - Salva il Report. Se il contenuto supera la soglia di Telegram (4096 caratteri), il bot lo divide automaticamente e lo invia in più tranche consecutive per garantire la ricezione.

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/cesare/telegram_bot.py` (Orchestra il comando)
2. `Execution/romolo/romolo_manage_channel.py` (Lancia le API e la consulenza AI con Gemini)

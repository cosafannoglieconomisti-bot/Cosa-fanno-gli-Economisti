---
description: Generazione e approvazione della copertina video direttamente da Telegram
---

# /copertina Workflow (Standalone)

## Descrizione
Questo workflow consente di generare, visionare e approvare la copertina del video senza uscire da Telegram.

## Procedura Deterministica
1.  **Avvio**: L'utente lancia `/copertina`.
2.  **Selezione**: Il bot mostra i paper pronti in `Cleaned/`. L'utente seleziona quello desiderato.
3.  **Generazione**: Il sistema lancia `generate_cover.py` con prompt potenziato (Comic Style, Orange/Black/White).
4.  **Revisione**:
    -   `✅ Approva`: Copia l'immagine come `copertina.png` nella cartella del paper.
    -   `🔄 Rigenera`: Cancella i temporanei e genera una nuova proposta originale.
    -   `❌ Rifiuta`: Annulla l'operazione e pulisce i file.

## 📋 File Python Utilizzati
- `Execution/cesare/telegram_bot.py` (Gestione Callback `/copertina`)

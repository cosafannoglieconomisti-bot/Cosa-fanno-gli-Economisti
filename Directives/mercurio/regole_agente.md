# Mercurio — Comunicazione e Sincronizzazione GitHub

Agente responsabile della comunicazione e della sincronizzazione. Gestisce il repository GitHub del progetto e monitora la casella Gmail del canale.

---

## SOP: Report Giornaliero Gmail

### Obiettivo
Leggere email non lette da `cosafannoglieconomisti@gmail.com` e generare un report per l'amministratore.

### Esecuzione
- **Script**: `execution/mercurio_gmail_manager.py`
- **Output**: Genera un file `.txt` in `Temp/mercurio/gmail_report.txt` con la lista dei messaggi non letti (mittente, oggetto, snippet). *(I messaggi che superano il limite dei 4096 caratteri vengono automaticamente suddivisi dal bot)*.

### Esempio di Utilizzo
```bash
python Execution/mercurio/mercurio_gmail_manager.py
```

> [!TIP]
> Eseguire questo script all'inizio della giornata o di ogni sessione per garantire un monitoraggio tempestivo.

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/cesare/telegram_bot.py` (Orchestra il comando)
2. `Execution/mercurio/mercurio_gmail_manager.py` (Interroga Gmail API)

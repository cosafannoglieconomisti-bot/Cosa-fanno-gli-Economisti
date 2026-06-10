# Cesare — Gestione Telegram

Agente dedicato alla comunicazione e controllo via Telegram. Gestisce la ricezione di comandi remoti e l'invio di notifiche di status tramite Telegram Bot.

---

## SOP: Hub Notifiche e Approvazioni

### Obiettivo
Inviare alert o chiedere autorizzazioni al proprietario del canale tramite Telegram.

### Funzionamento
Per inviare un messaggio o richiedere approvazione, accodare un oggetto in `notifications_hub.json` con la seguente struttura:

```json
[
  {
    "message": "Testo del messaggio", 
    "require_approval": true, 
    "action_key": "chiave_azione"
  }
]
```

#### Regole:
- Se `require_approval` è `true`, Cesare invierà bottoni Inline "Approva/Rifiuta".
- Se approvato, Cesare eseguirà il comando mappato in `command_map.json` associato a `action_key`.

### Esecuzione (Il Bot)
- **Script**: `execution/telegram_bot.py`
- **Distanza**: Gira in background monitorando l'hub.

## 📋 File Python Utilizzati
- `Execution/cesare/telegram_bot.py`

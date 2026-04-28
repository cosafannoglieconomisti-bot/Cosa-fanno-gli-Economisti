# Mercurio — Sincronizzazione GitHub

Agente Mercurio è responsabile del backup del canale su GitHub.

---

## SOP: Backup su GitHub

### Obiettivo
Sincronizzare tutte le modifiche del workspace con il repository GitHub remoto (`origin/main`).

### Prerequisiti
- Git installato.
- Remote `origin` configurato con un Token di accesso valido.

### Esecuzione
Eseguire lo script Python da qualsiasi posizione (lo script troverà automaticamente la radice del repository):

```bash
python3 Execution/mercurio/mercurio_github_sync.py ["Messaggio di commit opzionale"]
```

Oppure usa il comando rapido:
```bash
./Execution/mercurio/backup.sh ["Messaggio di commit opzionale"]
```

### Comportamento
1.  **Staging Selettivo**: Crea una copia temporanea includendo le cartelle core (`.agents`, `Directives`, `Execution`) e la cartella `Cleaned/`.
2.  **Filtro Video**: Esclude automaticamente tutti i file `.mp4` per evitare di appesantire il repository GitHub.
3.  **Sanificazione**: Esegue l'offuscamento di dati sensibili (Token, API Key) nei file sorgente.
4.  **Push Deterministico**: Inizializza un nuovo repository in staging e lo pusha forzatamente su `origin main`.

> [!WARNING]
> Se il `push` fallisce, verifica che il token nel remote URL non sia scaduto.

## 📋 File Python Utilizzati (In Ordine di Esecuzione)
1. `Execution/cesare/telegram_bot.py` (Orchestra il comando)
2. `Execution/mercurio/mercurio_github_sync.py` (Esegue `git add`, `commit` e `push`)

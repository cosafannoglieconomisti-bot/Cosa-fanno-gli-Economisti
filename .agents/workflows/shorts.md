---
description: Workflow /shorts per l'assegnazione automatica di titoli e descrizioni "hook"
---

Il workflow `/shorts` automatizza l'ottimizzazione SEO dei video brevi (Shorts) caricati sul canale, assicurando che ogni clip funga da gancio (hook) per i contenuti long-form corrispondenti.

### Procedura Operativa

1.  **Scansione Canale**: Il sistema recupera l'elenco di tutti i video del canale YouTube.
2.  **Identificazione Shorts**: Filtra i video con durata inferiore ai 60 secondi che presentano titoli generici (es. date come "11 aprile 2026", "Short", nomi file) o descrizioni incomplete. **I titoli-data sono la priorità assoluta di ottimizzazione.**
3.  **Analisi Contenuto**:
    -   Recupera la trascrizione dello Short via YouTube API (se disponibile) o tramite analisi audio (`Whisper`).
    -   Utilizza Gemini per identificare il tema economico/accademico trattato nella clip.
4.  **Matching Semantico**:
    -   Confronta il tema dello Short con i database dei video caricati (`Cleaned/` o titoli playlist).
    -   Identifica il video long-form "padre" che tratta lo stesso paper accademico.
5.  **Generazione Metadati (SOP Part 11)**:
    -   **Titolo**: Crea un titolo "Catchy" (Hook) di massimo 60 caratteri.
    -   **Descrizione**: Inserisce obbligatoriamente il link cliccabile `Video completo qui: https://youtu.be/[ID]` in una riga isolata (solitamente la seconda), preceduta da un hook potente e seguita da hashtag strategici (#shorts #economia #storia).
6.  **Aggiornamento**: Esegue il comando di update via YouTube Data API (`batch_update_shorts.py`).

### Casi Limite
- **Nessuna trascrizione**: Se l'audio manca o non è leggibile, il sistema richiede l'intervento manuale dell'utente su Telegram.
- **Matching multiplo**: In caso di ambiguità (es. due video sulla Mafia), il sistema sceglie il più recente o chiede conferma via bridge.

### Requisiti
- Accesso alle credenziali YouTube (`token_youtube.pickle`).
- Script `Execution/romolo/batch_update_shorts.py` aggiornato.

---

## 📋 File Python Utilizzati
1. `Execution/romolo/romolo_manage_channel.py` (Listing)
2. `Execution/romolo/batch_update_shorts.py` (Update)
3. `Execution/enea/generate_index_whisper.py` (Analisi opzionale)

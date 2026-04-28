# SOP: Download Asset Deterministico (NotebookLM)

Questa procedura garantisce il download binario originale di Video e Infografiche, eliminando la necessità di screenshot o registrazioni manuali.

## Strumenti Necessari
- Script: `Execution/enea/notebooklm_asset_downloader.py`
- Browser con Developer Tools (Network Log).

## Procedura Operativa

### 1. Intercettazione dell'Asset
1. Aprire il notebook su NotebookLM.
2. Aprire l'anteprima dell'asset desiderato (Video Overview o Infografica).
3. Aprire i **Developer Tools** (F12) e andare sulla scheda **Network**.
4. Filtrare le richieste:
   - **Video**: Cerca `videoplayback`.
   - **Infografica**: Cerca `rd-notebooklm`.
5. Individuare la riga con la dimensione maggiore o con l'URL che punta a `lh3.googleusercontent.com`.

### 2. Estrazione Credenziali
1. Cliccare con il tasto destro sulla richiesta -> **Copy** -> **Copy URL**.
2. Nel pannello a destra (**Headers**), scorrere fino a **Request Headers**.
3. Copiare l'intero valore del campo `Cookie`.

### 3. Esecuzione Download
Eseguire lo script Python passando i dati estratti:

```bash
python Execution/enea/notebooklm_asset_downloader.py \
  --url "URL_COPIATO" \
  --output "/Users/marcolemoglie_1_2/Downloads/nome_file_nativo.mp4" \
  --cookies "VALORE_COOKIE_COPIATO"
```

## Troubleshooting
- **400 Bad Request**: I cookie potrebbero contenere caratteri non validi o essere troppo lunghi. Assicurarsi di copiare solo il valore del campo `Cookie`.
- **403 Forbidden**: L'URL o i Cookie sono scaduti. Ri-eseguire l'intercettazione.
- **HTML restituito**: L'identità di sessione è persa. Effettuare un refresh della pagina NotebookLM.

---
**Ultima esecuzione riuscita con:**
- `Execution/enea/notebooklm_asset_downloader.py`

# Direttive Ulisse — Monitoraggio News e Matching Accademico

Agente responsabile di trovare i temi "hot" dalle news quotidiane e i rispettivi paper accademici di riferimento. Opera integrando search deterministico e verifica via OpenAlex.

---

### PROCEDURA DI MATCHING ACCADEMICO (per Ulisse /articoli)

1. **Notizie (BATCH DETERMINISTICO)**: Ulisse esegue `get_raw_news_batch()` per monitorare **ANSA, Corriere, Repubblica, Il Post, Fanpage**.
2. **Consensus Discovery**: Identifica i **3 argomenti più caldi**. **MANDATORIO**: Titoli estremamente "catchy", massimo **5 parole**, stile domanda o clicky, centrati sull'aspetto economico/sociale.
3. **Estrazione Tag Semantici**: Estrae **Aree Accademiche Ampie** (es: 'Public Economics'). **MANDATORIO**: I tag devono essere selezionati con estrema attenzione (selezione "core") per garantire la coerenza semantica con il topic ed evitare allucinazioni incrociate (es. no tag 'Energy' per temi su 'Pensioni').
4. **Matching (OR LOGIC)**: Interpella OpenAlex filtrando rigorosamente per:
    - **Journal**: Solo Top Journals autorizzati via ISSN/Nome (Whitelist in calce).
    - **Logica**: Use **OR** tra i tag generati per massimizzare la probabilità di trovare un articolo rilevante in un Top Journal.
    - **Anno**: Solo pubblicazioni dal **2000 in poi**.
5. **Verifica (MANDATORIA)**: Esegue lo script `Execution/ulisse/verify_paper.py`. Se non viene trovato alcun match, riportare correttamente `[✘ Nessun match nei Top Journals dal 2000]` invece di inventare dati.
6. **Formattazione**: Salva il report finale in `Temp/ulisse/` con naming `temi_hot_matched_GG_MM_AAAA_HHMM.txt`.

---

### Whitelist Journal Autorizzati

Prediligere rigorosamente le seguenti testate (Top 5 + High Impact):
- **Economia**: AER, QJE, JPE, Econometrica, REStud, JEP, AEJ (Applied, Policy, Macro, Micro), REStat, JEEA, JME, JOLE, Economic Journal.
- **Multidisciplinari**: Nature, Science, PNAS.

---

### Error Handling e Allucinazioni

- **MANDATORIO**: Mai proporre un paper che non sia passato attraverso la verifica deterministica dello script.
- Se lo script non trova match per un argomento, Ulisse deve riportare `[✘ Nessun match nei Top Journals dal 2000]` invece di inventare dati.
- In caso di errore API, riprovare con tag più generici una sola volta.

---
description: Risposte alle mail di segnalazione/outreach agli economisti (routine oraria feriale 9:46–18:46)
---

# Workflow: /risposte_mail_segnalazione

**OBIETTIVO**: Rispondere quasi subito agli economisti (e a chiunque scriva al canale) che rispondono alle nostre email di segnalazione «Your paper on Cosa fanno gli Economisti…». Le risposte vengono preparate come bozze che Marco rivede e invia lui, una alla volta.

## Routine
- **Nome**: «Canale risposte mail segnalazione» (cartella routine `canale-risposte-mail-segnalazione`).
- **Cadenza**: **ogni ora nei giorni feriali (lun–ven), dalle 9:46 alle 18:46 Europe/Rome** (cron `46 9-18 * * 1-5`). Gmail non permette un vero trigger su nuova mail, quindi si controlla ogni ora per rispondere quasi in tempo reale.
- **Casella**: `cosafannoglieconomisti@gmail.com` (connettore Gmail del canale, `user-Gmail--canale`). **NON** l'account Gmail personale di Marco (`user-Gmail`).
- **Destinatario del risultato**: Marco nella chat di Grok Bot. Se non c'è niente da rispondere (e nessun indirizzo da aggiornare), la routine non scrive nulla.

### Storia cambi
| Data | Cadenza |
|---|---|
| 2026-10-08 | Creata: settimanale, **martedì 08:53** |
| 2026-10-08 | Spostata a **giornaliera feriale 10:46** (Marco: «una volta al giorno la mattina alle 11») |
| 2026-10-08 | Spostata a **oraria feriale 9:46–18:46** (Marco: deve scattare quasi a ogni mail nuova) |

## Regole fisse
- **Nessun invio automatico.** Ogni risposta passa da una card bozza che Marco rivede, può modificare e invia lui.
- **Una card alla volta**: la successiva solo dopo che Marco ha inviato o scartato la precedente. Mai tante card insieme.
- Prima di proporre una bozza: controllare nel thread che non abbiamo già risposto dopo l'ultimo messaggio ricevuto e che non ci sia già una bozza in attesa per lo stesso thread.
- Ignorare bounce, auto-reply, out-of-office e risposte che chiudono la conversazione (solo un emoji, «grazie, ciao» dopo una nostra risposta).
- **Mai inventare indirizzi email.** Se un bounce o una risposta indica un nuovo indirizzo di un autore: aggiornare la coda outreach e il Brain, e segnalarlo a Marco.

## Formato delle bozze
- **Risposta nel thread originale** (reply al messaggio ricevuto), stessi destinatari e cc rilevanti.
- Intestazione verso Marco: a chi è indirizzata e, se sono più di una, **«N su Totale»** (es. «Questa è per Raffaele Saggio, con Fenizia in copia, 17 su 34»).
- **Tono**: inglese per chi scrive in inglese, italiano per chi scrive in italiano; corta e cordiale. Ruben è un amico: tono amichevole. Arnstein Aassve si saluta «Arnie».
- **Firma**: «Marco».
- Nessun invio senza OK: Marco preme Invia sulla card (se dice «manda» per una card aperta, la si invia invariata dal connettore canale e gli si dice di non premere Invia sulla card).

## Testo dell'automazione (verbatim)
```
Controllo ogni ora (giorni feriali, 9:46–18:46) della casella del canale «Cosa fanno gli economisti» (cosafannoglieconomisti@gmail.com, il connettore Gmail del canale, NON l'account Gmail personale di Marco). Serve a rispondere quasi subito quando arriva una mail nuova.

Obiettivo: trovare le risposte arrivate dall'ultimo controllo alle nostre email di segnalazione/outreach agli economisti (thread tipo «Your paper on Cosa fanno gli Economisti…») e a qualsiasi altro thread del canale ancora senza nostra risposta che ne richieda una, poi preparare le risposte per Marco. Prima di proporre una bozza, controlla nel thread che non abbiamo già risposto dopo l'ultimo messaggio ricevuto, e che non ci sia già una bozza in attesa per lo stesso thread in questa chat.

Regole:
- Scrivi a Marco sempre in italiano, breve e caldo.
- Ignora bounce, auto-reply, out-of-office e risposte che chiudono la conversazione (solo un emoji, «grazie, ciao» dopo una nostra risposta): non serve risposta. Se un bounce o una risposta indica un nuovo indirizzo di un autore, aggiorna la lista/coda outreach del repo canale sul Mac (Desktop/canale) e il Brain (areas/Other/canale) e segnalalo a Marco. Non inventare mai indirizzi email.
- Per ogni thread che merita risposta prepara una bozza nel tono giusto: inglese per chi scrive in inglese, italiano per chi scrive in italiano; corta, cordiale, firmata «Marco». Ruben è un amico: tono amichevole. Arnstein Aassve si saluta «Arnie». Rispondi nel thread originale (reply), con gli stessi destinatari e cc rilevanti.
- NON inviare nessuna email da solo. Ogni risposta passa da una card bozza che Marco rivede, può modificare e invia lui.
- Mostra le bozze UNA ALLA VOLTA: la successiva solo dopo che Marco ha inviato o scartato la precedente. Mai tante card insieme. Indica a chi è indirizzata e, se sono più di una, «N su Totale».
- Quando ci sono state risposte, annota nel Brain (canale_LOG.md) quante sono arrivate e quante inviate.

Destinatario del risultato: Marco in questa chat di Grok Bot. Se non ci sono risposte nuove che richiedono una replica (e nessun indirizzo da aggiornare), non scrivere nulla.
```

## Coda outreach (dove aggiornare gli indirizzi)
- Al 2026-10-08 la coda outreach vive sul **box Grok Bot**, non nel repo del Mac: `/workspace/canale/author_outreach_queue.csv` (colonne `contact_emails`, `contact_verification_notes`), più `Temp/contacts_master.json`, `author_outreach_resend_drafts.md`, `author_outreach_send_log.md` e `author_outreach_README.md` nella stessa cartella.
- Per cambiare un indirizzo: sostituirlo in `contact_emails` e aggiungere una nota datata con la fonte in `contact_verification_notes`. Indirizzi alternativi solo nelle note (`contact_emails` va tutto in To: niente doppi invii).
- Esempio 2026-10-08: Mounu Prem (Francisco Muñoz) `francisco.munoz@eief.it` (rimbalza) → `fmmunoz.ma@gmail.com`; Gianluca Russo alternativo `russo.gianluca.eco@gmail.com` (solo nota).

## Procedura Operativa
1. **Ricerca thread**: `search_threads` sul connettore canale per i messaggi arrivati dall'ultimo controllo (es. `in:inbox newer_than:1d`), soprattutto i thread «Your paper on Cosa fanno gli Economisti…».
2. **Filtro**: scartare bounce, auto-reply, out-of-office, chiusure; scartare i thread in cui abbiamo già risposto dopo l'ultimo messaggio ricevuto o con una bozza già in attesa.
3. **Indirizzi**: se emerge un nuovo indirizzo verificato, aggiornare la coda outreach e il Brain e dirlo a Marco.
4. **Bozze**: una card per thread (reply nel thread, `replyToMessageId` dell'ultimo messaggio ricevuto, stessi destinatari e cc rilevanti), mostrata una alla volta con «N su Totale».
5. **Log**: annotare in `canale_LOG.md` (Brain) quante risposte sono arrivate e quante sono state inviate.

## Link
- Competitor (altra routine di crescita): [competitor](competitor.md)
- Pipeline produzione: [weekly-automation](weekly-automation.md)

# SOP: Autenticazione YouTube OAuth

Questa procedura definisce il contratto operativo per l'autenticazione YouTube del progetto `canale`.

## Regola Autorevole
- Il token YouTube **autorevole** del progetto e' `Execution/credentials/token.pickle`.
- I path legacy `Execution/credentials/token_youtube.pickle` e `Execution/romolo/.tmp/tokens/token_youtube.pickle` non sono una seconda fonte di verita': vanno solo sincronizzati dal token principale per compatibilita' con script storici.

## Entry Point Obbligatorio
- Prima di `/upload`, eseguire il preflight:

```bash
./workflow youtube-auth
```

- Se il refresh token e' revocato/scaduto o si vuole forzare il login browser:

```bash
./workflow youtube-auth --force
```

## Comportamento Atteso
1. Se `Execution/credentials/token.pickle` e' ancora valido, il workflow non deve aprire alcun browser.
2. Se il token e' scaduto ma refreshabile, il workflow deve rigenerarlo in place.
3. Se Google risponde `invalid_grant` o il refresh non e' possibile, il workflow deve aprire un login OAuth interattivo e salvare il nuovo token nel path principale.
4. Dopo la rigenerazione, il token principale deve essere copiato anche nei path legacy finche' esistono script non migrati.

## Error Policy
- `invalid_grant` significa problema di **refresh token OAuth**, non di API key.
- In questo caso non rilanciare ciecamente `/upload`: prima riautenticare con `./workflow youtube-auth --force`.
- Non stampare mai token completi o segreti nei log.

## Integrazione con `/upload`
- `/upload` deve eseguire `youtube-auth` come preflight.
- Se il preflight fallisce, `/upload` deve fermarsi prima di qualunque chiamata YouTube o Buffer.

## Note di Migrazione
- `Execution/marcello/buffer_post_single.py` deve leggere il token YouTube dal path principale.
- I path legacy restano solo come fallback temporaneo per script storici ancora non migrati.

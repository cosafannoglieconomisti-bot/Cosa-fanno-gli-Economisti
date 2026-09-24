---
description: Buffer Instagram — post infografica e Reel (FB sospeso)
---

Instagram è l’unico social Buffer nel closeout `/upload`. Facebook sospeso.

## Post (infografica)

1. **Prima**: asset pubblici su `origin/main` (`Cleaned/{folder}/*.png` via push Buffer assets).
2. `buffer_post_single.py --platform instagram --folder-name X`
3. Caption SOP Marcello; tag **solo specifici** dal metadata.
4. Tracking: `instagram_url`.

## Reel

1. Serve short cleaned locale + YT long già pubblicato.
2. Hosta mp4 su **litter.catbox.moe** (HTTPS diretto). **Non** passare `youtube.com/shorts` come media.
3. `buffer_post_single.py --platform instagram --content-type reel --folder-name X --video-url https://litter.catbox.moe/...`  
   oppure `--upload-local path/to/short_cleaned.mp4`
4. Tracking nested: `shorts[].ig_reel_url`.

```bash
./workflow instagram --folder-name Titolo --hour 10
./workflow instagram --folder-name Titolo --content-type reel --video-url URL
```

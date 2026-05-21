import asyncio
import sys
from playwright.async_api import async_playwright
import os

async def main():
    url = sys.argv[1]
    output_path = sys.argv[2]
    
    # Usa il profilo Chrome in cui l'utente è loggato, per avere i cookie giusti!
    user_data_dir = "/Users/marcolemoglie_1_2/.gemini/antigravity-browser-profile"
    
    print(f"[*] Avvio download Playwright per: {url}")
    print(f"[*] Destinazione: {output_path}")
    
    async with async_playwright() as p:
        # Usa il contesto persistente per condividere l'autenticazione
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
            ]
        )
        
        page = await browser.new_page()
        
        # Intercetta la risposta
        response = await page.goto(url, wait_until="networkidle")
        
        if not response:
            print("[!] Errore: Nessuna risposta ricevuta.")
            await browser.close()
            sys.exit(1)
            
        print(f"[*] Stato HTTP: {response.status}")
        
        # Leggi il corpo della risposta
        body = await response.body()
        
        if response.status == 200:
            if b"<!doctype html>" in body.lower() and b"botguard" in body.lower():
                print("[!] Attenzione: Pagina Botguard rilevata. Attendo che il JS risolva...")
                await page.wait_for_timeout(5000) # Aspetta che il redirect accada
                # Ottieni il nuovo URL
                new_url = page.url
                if new_url != url:
                    print(f"[*] Redirect a: {new_url}")
                    # Vai alla nuova pagina e scarica
                    response = await page.goto(new_url, wait_until="networkidle")
                    body = await response.body()
            
            with open(output_path, "wb") as f:
                f.write(body)
            print(f"[+] Download completato! ({len(body)} bytes)")
        else:
            print(f"[!] Errore: Stato HTTP {response.status}")
            
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 downloader.py <URL> <OUTPUT_PATH>")
        sys.exit(1)
    asyncio.run(main())

import asyncio
import sys
from playwright.async_api import async_playwright
import os

async def main():
    url = sys.argv[1]
    output_path = sys.argv[2]
    
    user_data_dir = os.path.expanduser("~/.gemini/antigravity-browser-profile")
    
    print(f"[*] Avvio download Playwright (Warm-up mode) per: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = await browser.new_page()
        
        # Warm up session
        print("[*] Warming up session at notebooklm.google.com...")
        await page.goto("https://notebooklm.google.com/", wait_until="networkidle")
        
        print(f"[*] Navigazione al download URL: {url}")
        
        # Intercetta il download o la risposta
        async with page.expect_response(lambda response: response.url == url or "lh3.googleusercontent.com" in response.url, timeout=60000) as response_info:
            await page.goto(url)
            response = await response_info.value
            
            print(f"[*] Stato HTTP: {response.status}")
            body = await response.body()
            
            if response.status == 200:
                if b"<!doctype html>" in body.lower() and b"sign in" in body.lower():
                    print("[!] Sessione non valida. Redirect al login.")
                else:
                    with open(output_path, "wb") as f:
                        f.write(body)
                    print(f"[+] Download completato! ({len(body)} bytes)")
            else:
                print(f"[!] Errore: Stato HTTP {response.status}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

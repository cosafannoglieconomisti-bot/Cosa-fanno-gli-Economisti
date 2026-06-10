import asyncio
import sys
import json
import os
from playwright.async_api import async_playwright

async def main():
    url = sys.argv[1]
    output_path = sys.argv[2]
    
    auth_path = os.path.expanduser("~/.notebooklm-mcp/auth.json")
    with open(auth_path) as f:
        auth_data = json.load(f)
    
    cookies_dict = auth_data.get("cookies", {})
    
    playwright_cookies = []
    for name, value in cookies_dict.items():
        # Set for both domains
        for domain in [".google.com", ".googleusercontent.com"]:
            playwright_cookies.append({
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/",
                "secure": True,
                "sameSite": "None"
            })
    
    print(f"[*] Avvio download Playwright per: {url}")
    print(f"[*] Destinazione: {output_path}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        await context.add_cookies(playwright_cookies)
        
        page = await context.new_page()
        
        # Intercetta la risposta
        try:
            async with page.expect_response(lambda response: response.url == url or "lh3.googleusercontent.com" in response.url, timeout=60000) as response_info:
                await page.goto(url, wait_until="commit")
                response = await response_info.value
                
                print(f"[*] Stato HTTP: {response.status}")
                body = await response.body()
                
                if response.status == 200:
                    # Verifica se è HTML (errore)
                    if b"<!doctype html>" in body.lower() and (b"botguard" in body.lower() or b"sign in" in body.lower()):
                        print("[!] Rilevata pagina di login/botguard. Il download ha fallito.")
                        print(f"[*] URL finale: {page.url}")
                        await browser.close()
                        sys.exit(1)
                    
                    with open(output_path, "wb") as f:
                        f.write(body)
                    print(f"[+] Download completato! ({len(body)} bytes)")
                else:
                    print(f"[!] Errore: Stato HTTP {response.status}")
        except Exception as e:
            print(f"[!] Eccezione: {str(e)}")
            
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 downloader.py <URL> <OUTPUT_PATH>")
        sys.exit(1)
    asyncio.run(main())

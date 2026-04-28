import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # headless=False lets the user see it and solve any 2FA
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.facebook.com")
        print("Pagina caricata. Controllo Login...")
        await asyncio.sleep(4)

        # Cookie consent workaround
        try:
            await page.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('button, div[role="button"], span'));
                const acceptBtn = buttons.find(b => b.innerText.includes('Accetta') || b.innerText.includes('Consenti') || b.textContent.includes('Accetta tutti'));
                if (acceptBtn) acceptBtn.click();
            }""")
            await asyncio.sleep(2)
        except:
            pass

        # Check for login fields
        email_field = await page.query_selector("input[name='email']")
        if email_field:
            print("Inserimento credenziali...")
            await page.fill("input[name='email']", "cosafannoglieconomisti@gmail.com")
            await page.fill("input[name='pass']", "3aVZQf#Skx&*reP")
            print("Invio form...")
            await page.keyboard.press("Enter")
            await asyncio.sleep(8)
            print("Login completato.")
            print("\n=== ATTENZIONE UTENTE ===")
            print("Se sulla finestra di Chrome vedi un popup di login o cookie (tipo 'Vedi altro di...'),")
            print("per please CHIUDILO oppure ACCEDI manualmente.")
            print("Lo script attenderà 15 secondi per darti tempo di liberare la visuale...\n")
            await asyncio.sleep(15)

        print("Navigazione alla pagina...")
        await page.goto("https://www.facebook.com/profile.php?id=61579548543222")
        await asyncio.sleep(8)

        # Ensure page identity is loaded or switch dialog if needed
        # (Standard profile should loads, just ready to post)

        descrizione = """Lo studio "Intergenerational Mobility in the Very Long Run: Florence 1427–2011" di Guglielmo Barone e Sauro Mocetti, pubblicato su The Review of Economic Studies nel 2021, analizza la mobilità sociale a Firenze su un arco di sei secoli. Collegando gli antenati del 1427 ai discendenti del 2011 tramite i cognomi, i ricercatori rispondono a una domanda affascinante: la ricchezza e lo status sociale persistono nel lunghissimo periodo? I risultati mostrano un'elasticità positiva e significativa per reddito e ricchezza reale, evidenziando l'esistenza di dinastie nelle professioni d'élite e persino un "glass floor" (pavimento di vetro) che protegge i ricchi dalla discesa sociale.

Link al video: https://www.youtube.com/watch?v=7SeVerAABeg"""

        image_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/I_ricchi_di_oggi_sono_gli_stessi_del_1400_restud_2021/thumbnail_definitiva.png"

        print("\n--- INIZIO POST 1 (LINK) ---")
        # Click Creator Box
        await page.evaluate("""() => {
            const elements = Array.from(document.querySelectorAll('span, div'));
            const target = elements.find(e => e.innerText.includes('A cosa stai pensando') || e.innerText.includes('Condividi un pensiero'));
            if (target) target.click();
        }""")
        await asyncio.sleep(4)

        print("Scrittura testo Post 1...")
        await page.keyboard.type(descrizione)
        print("Attesa generazione anteprima (10s)...")
        await asyncio.sleep(10)

        # Click Publish
        await page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll('div[role="button"], span'));
            const pubBtn = buttons.find(b => b.innerText === 'Pubblica' || b.textContent === 'Pubblica');
            if (pubBtn) pubBtn.click();
        }""")
        print("Invio Post 1...")
        await asyncio.sleep(15)
        
        print("\n--- INIZIO POST 2 (FOTO) ---")
        # Click Foto/video button
        await page.evaluate("""() => {
            const elements = Array.from(document.querySelectorAll('span, div'));
            const target = elements.find(e => e.innerText.includes('Foto/video'));
            if (target) target.click();
        }""")
        await asyncio.sleep(5)

        # WAIT FOR INPUT ELEMENT TO RENDER
        try:
            print("Attesa rendering input file...")
            await page.wait_for_selector("input[type='file']", timeout=10000)
        except Exception as e:
            print(f"ERRORE: Timeout nell'attesa dell'input file. {e}")
            await page.screenshot(path='/Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/facebook_debug_photo.png')
            print("Screenshot diagnostico salvato.")

        # Set input file
        file_inputs = await page.query_selector_all("input[type='file']")
        if file_inputs:
            await file_inputs[0].set_input_files(image_path)
            print("Foto caricata.")
            await asyncio.sleep(4)

            print("Scrittura didascalia...")
            # Playwright types into active element or targeted creator
            await page.keyboard.type(descrizione)
            await asyncio.sleep(2)

            # Click Publish
            await page.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('div[role="button"], span'));
                const pubBtn = buttons.find(b => b.innerText === 'Pubblica' || b.textContent === 'Pubblica');
                if (pubBtn) pubBtn.click();
            }""")
            print("Invio Post 2...")
            await asyncio.sleep(10)
        else:
            print("ERRORE: Input file non trovato!")

        await browser.close()
        print("\n--- Sync completato! ---")

if __name__ == "__main__":
    asyncio.run(run())

import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
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

        # ROBUST LOGIN (Matches standard form OR modal overlay)
        # Using input types which are global
        email_field = await page.query_selector("input[name='email'], input[type='text'], [placeholder*='E-mail']")
        pass_field = await page.query_selector("input[name='pass'], input[type='password'], [placeholder*='Password']")

        if email_field and pass_field:
            print("Modulo di Login rilevato (Modulo o Modal). Inserimento credenziali...")
            await email_field.fill("cosafannoglieconomisti@gmail.com")
            await pass_field.fill("3aVZQf#Skx&*reP")
            await page.keyboard.press("Enter")
            print("Invio credenziali...")
            await asyncio.sleep(10)

        # Look for login modal to dismiss if still present as overlay
        try:
            await page.evaluate("""() => {
                // Find and click Close 'X' if a random modal popped
                const closeBtn = document.querySelector('div[aria-label="Chiudi"], div[role="button"] i');
                if (closeBtn) closeBtn.click();
            }""")
        except:
            pass

        print("\n=== ATTENZIONE UTENTE ===")
        print("Se sulla finestra di Chrome subentra una seconda verifica o un blocco,")
        print("per favore RISOLVILO TU a mano o chiudilo.")
        print("Lo script attenderà 10 secondi per consentirti di sbloccare la visuale...\n")
        await asyncio.sleep(10)

        print("Navigazione alla pagina...")
        await page.goto("https://www.facebook.com/profile.php?id=61579548543222")
        await asyncio.sleep(8)

        descrizione = """Lo studio "Intergenerational Mobility in the Very Long Run: Florence 1427–2011" di Guglielmo Barone e Sauro Mocetti, pubblicato su The Review of Economic Studies nel 2021, analizza la mobilità sociale a Firenze su un arco di sei secoli. Collegando gli antenati del 1427 ai discendenti del 2011 tramite i cognomi, i ricercatori rispondono a una domanda affascinante: la ricchezza e lo status sociale persistono nel lunghissimo periodo? I risultati mostrano un'elasticità positiva e significativa per reddito e ricchezza reale, evidenziando l'esistenza di dinastie nelle professioni d'élite e persino un \"glass floor\" (pavimento di vetro) che protegge i ricchi dalla discesa sociale.

Link al video: https://www.youtube.com/watch?v=7SeVerAABeg"""

        image_path = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/I_ricchi_di_oggi_sono_gli_stessi_del_1400_restud_2021/thumbnail_definitiva.png"

        print("\n--- INIZIO CARICAMENTO FOTO ---")
        # Click Foto/video button
        await page.evaluate("""() => {
            const elements = Array.from(document.querySelectorAll('span, div'));
            const target = elements.find(e => e.innerText.includes('Foto/video'));
            if (target) target.click();
        }""")
        await asyncio.sleep(6)

        # WAIT FOR INPUT ELEMENT
        try:
            print("Attesa rendering input file...")
            await page.wait_for_selector("input[type='file']", timeout=10000)
        except Exception as e:
             print(f"Avviso: wait_for_selector timeout ({e}). Tentativo diretto...")

        # Set input file
        file_inputs = await page.query_selector_all("input[type='file']")
        if file_inputs:
            await file_inputs[0].set_input_files(image_path)
            print("Foto selezionata e caricata.")
            await asyncio.sleep(4)

            print("Scrittura didascalia...")
            await page.keyboard.type(descrizione)
            await asyncio.sleep(2)

            # Click Publish
            await page.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('div[role="button"], span'));
                const pubBtn = buttons.find(b => b.innerText === 'Pubblica' || b.textContent === 'Pubblica');
                if (pubBtn) pubBtn.click();
            }""")
            print("Invio Post...")
            await asyncio.sleep(12)
            print("\n--- Caricamento Foto Completato! ---")
        else:
            print("ERRORE: Input file non trovato!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

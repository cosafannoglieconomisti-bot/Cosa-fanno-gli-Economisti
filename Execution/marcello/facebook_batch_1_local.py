import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # We run headful so if Facebook asks for 2FA or verification, the user can see it!
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.facebook.com")
        print("Pagina caricata. Controllo Login...")

        # Cookie consent workaround (dispatchEvent click if modal is present)
        try:
            await page.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('button, div[role="button"]'));
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
            await page.click("button[name='login']")
            await page.wait_for_navigation()
            print("Login completato.")

        # Switch to Page ID
        await page.goto("https://www.facebook.com/profile.php?id=61579548543222")
        print("Pagina profilo caricata.")
        await asyncio.sleep(5)

        # Batch 1 Items
        items = [
            {
                "path": "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Mafia_Inc_restat_2021/thumbnail.png",
                "link": "https://www.youtube.com/watch?v=hSj0RytzsJQ"
            },
            {
                "path": "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Togliere_i_sussidi_ai_giovani_li_spinge_a_lavorare_di_più_aer_2016/thumbnail.png",
                "link": "https://www.youtube.com/watch?v=Rcjwqblw9aI"
            },
            {
                "path": "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/La_Cicala_e_la_Formica_qje_2024/thumbnail.png",
                "link": "https://www.youtube.com/watch?v=06TeI4ehwBw"
            }
        ]

        for i, item in enumerate(items):
            print(f"\n--- Caricamento {i+1}/3: {os.path.basename(item['path'])} ---")
            
            # Click Post Box "A cosa stai pensando" or Foto/video
            await page.evaluate("""() => {
                const elements = Array.from(document.querySelectorAll('span, div'));
                const target = elements.find(e => e.innerText.includes('A cosa stai pensando') || e.innerText.includes('Foto/video'));
                if (target) target.click();
            }""")
            await asyncio.sleep(4)

            # Upload File
            # Look for input[type='file']
            file_inputs = await page.query_selector_all("input[type='file']")
            if file_inputs:
                await file_inputs[0].set_input_files(item['path'])
                print("File caricato.")
                await asyncio.sleep(3)
            else:
                print("ERRORE: Input file non trovato!")
                continue

            # Description empty - Direct Publish
            await page.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('div[role="button"], span'));
                const pubBtn = buttons.find(b => b.innerText === 'Pubblica' || b.textContent === 'Pubblica');
                if (pubBtn) pubBtn.click();
            }""")
            print("Invio post...")
            await asyncio.sleep(10)

            # Add Link Comment
            print("Aggiunta commento...")
            await page.evaluate(f"""() => {{
                // Find top post comment box
                const commentBoxes = document.querySelectorAll('div[role="textbox"]');
                if (commentBoxes.length > 0) {{
                    commentBoxes[0].focus();
                    document.execCommand('insertText', false, 'Link: {item["link"]}');
                    // Find submit button (usually an arrow icon or Enter)
                }}
            }}""")
            # Press enter to submit
            await page.keyboard.press("Enter")
            print("Commento inviato.")
            await asyncio.sleep(5)

        await browser.close()
        print("\n--- Batch 1 completato! ---")

if __name__ == "__main__":
    asyncio.run(run())

import asyncio
import os
import glob
from playwright.async_api import async_playwright

def load_video_data():
    mappings = {}
    base_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
    
    # Locate all video_metadata.md files using os.walk (robust against square brackets)
    meta_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == "video_metadata.md":
                meta_files.append(os.path.join(root, file))
    
    for meta_file in meta_files:
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            title = ""
            desc = ""
            in_desc = False
            for line in content.split('\n'):
                l = line.replace("**", "").strip()
                if l.lower().startswith("titolo:"):
                    title = l.split(":", 1)[1].strip()
                elif l.lower().startswith("descrizione:"):
                    desc = l.split(":", 1)[1].strip()
                    in_desc = True
                elif in_desc and l.strip() and not l.startswith("Tag:") and "http" not in l:
                    desc += " " + l.strip()

            # Guess YouTube ID/Link from list if possible, or append known direct pairs
            # To simplify, we will match loaded descriptions using substrings of titles
            if title and desc:
                key = title.upper().replace('?', '').replace('!', '')
                mappings[key] = {
                    "title": title,
                    "description": desc.strip(),
                }
        except Exception as e:
             print(f"Errore caricando {meta_file}: {e}")
             
    return mappings

async def run():
    video_database = load_video_data()
    print(f"Caricati {len(video_database)} video dal computer.")

    # Hardcoded manual link mappings for fallback verification
    links = {
        "I RICCHI DI OGGI": "https://www.youtube.com/watch?v=7SeVerAABeg",
        "MAFIA E SVILUPPO": "https://www.youtube.com/watch?v=wi8TmC6WRRo",
        "LATO OSCURO DELLA TV": "https://www.youtube.com/watch?v=LIgZxg-CMWY",
        "I ROBOT": "https://www.youtube.com/watch?v=S0ZyZE65BgM",
        "LA CORRUZIONE": "https://www.youtube.com/watch?v=Fa27rfGRweY",
        "TAGLIARE GLI AIUTI": "https://www.youtube.com/watch?v=Rcjwqblw9aI",
        "LA CICALA": "https://www.youtube.com/watch?v=06TeI4ehwBw",
        "ARCHEOLOGIA ECONOMICA": "https://www.youtube.com/watch?v=OfLZjHHVhuI",
        "LO STATO ED IL CRIMINE ORGANIZZATO": "https://www.youtube.com/watch?v=K1mbkAwVfNI",
        "NOMI E DISCRIMINAZIONE": "https://www.youtube.com/watch?v=85M2SSwB3V8",
        "TERREMOTO": "https://www.youtube.com/watch?v=mkOByDD32Q4",
        "CLIENTELISMO": "https://www.youtube.com/watch?v=BEZV_qvJ3C0",
        "MOGANO INSANGUINATO": "https://www.youtube.com/watch?v=sDG-9Olw7Lg",
        "ISTITUZIONI": "https://www.youtube.com/watch?v=zAwp-Sswzdw"
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.facebook.com")
        await asyncio.sleep(4)

        # ROBUST LOGIN (Matches standard form OR modal overlay)
        email_field = await page.query_selector("input[name='email'], input[type='text'], [placeholder*='E-mail']")
        pass_field = await page.query_selector("input[name='pass'], input[type='password'], [placeholder*='Password']")

        if email_field and pass_field:
            print("Modulo di Login rilevato (Modulo o Modal). Inserimento credenziali...")
            await email_field.fill("cosafannoglieconomisti@gmail.com")
            await pass_field.fill("3aVZQf#Skx&*reP")
            await page.keyboard.press("Enter")
            print("Invio credenziali...")
            await asyncio.sleep(10)

        try:
            await page.evaluate("""() => {
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

        print("Navigazione alla galleria foto...")
        await page.goto("https://www.facebook.com/profile.php?id=61579548543222&sk=photos")
        await asyncio.sleep(8)

        images = await page.query_selector_all("img")
        print(f"Trovate {len(images)} foto.")

        for i, img in enumerate(images):
            try:
                alt = await img.get_attribute("alt")
                if not alt or "text" not in alt.lower() and "testo" not in alt.lower():
                    continue

                alt_upper = alt.upper()
                selected_key = None
                selected_link = None
                selected_desc = ""

                for k, v in links.items():
                    if k in alt_upper:
                        selected_key = k
                        selected_link = v
                        break

                if not selected_key:
                     continue

                # Find rich description
                for k, v in video_database.items():
                    if selected_key in k:
                        selected_desc = v["description"]
                        break

                if not selected_desc:
                    selected_desc = f"{selected_key.title()}"

                print(f"\n--- Trovata corrispondenza: {selected_key} (Foto index {i}) ---")

                # Open Photo
                await img.click()
                await asyncio.sleep(5)

                # Click Modifica on the right side panel
                await page.evaluate("""() => {
                    const buttons = Array.from(document.querySelectorAll('div[role="button"], span'));
                    const editBtn = buttons.find(b => b.innerText.includes('Modifica') || b.textContent.includes('Modifica'));
                    if (editBtn) editBtn.click();
                }""")
                await asyncio.sleep(3)

                # Focus description box and type
                # Facebook description textarea usually is the focused active textarea
                full_text = f"{selected_desc}\n\nLink al video: {selected_link}"
                await page.keyboard.type(full_text)
                await asyncio.sleep(2)

                # Click Done/Save
                await page.evaluate("""() => {
                    const buttons = Array.from(document.querySelectorAll('div[role="button"], span'));
                    const doneBtn = buttons.find(b => b.innerText.includes('Modifica completata') || b.textContent.includes('Modifica completata'));
                    if (doneBtn) doneBtn.click();
                }""")
                print("Descrizione aggiornata.")
                await asyncio.sleep(8)

                # Close Theater View (click backdrop or X)
                await page.keyboard.press("Escape")
                await asyncio.sleep(3)

            except Exception as e:
                print(f"Errore su foto index {i}: {e}")
                try: await page.keyboard.press("Escape") 
                except: pass

        await browser.close()
        print("\n--- Backlog aggiornato! ---")

if __name__ == "__main__":
    asyncio.run(run())

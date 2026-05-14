import asyncio
import os
import sys
from playwright.async_api import async_playwright

def load_video_data():
    mappings = {}
    base_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
    
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

    print("\n--- TENTATIVO DI CONNESSIONE A CHROME ---")
    try:
        async with async_playwright() as p:
            # Connect to existing Chrome instance running on port 9222
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            contexts = browser.contexts
            if not contexts:
                print("Nessun context trovato nel browser. Assicurati che Chrome sia aperto.")
                return
            context = contexts[0]
            
            # Find an existing Facebook page or open a new one
            pages = context.pages
            page = None
            for p_obj in pages:
                if "facebook.com" in p_obj.url:
                    page = p_obj
                    break
            
            if not page:
                page = await context.new_page()

            print("Navigazione alla galleria foto di Facebook...")
            await page.goto("https://www.facebook.com/profile.php?id=61579548543222&sk=photos")
            await page.wait_for_load_state('networkidle', timeout=15000)
            await asyncio.sleep(5)

            images = await page.query_selector_all("img")
            print(f"Trovate {len(images)} foto nella galleria.")

            for i, img in enumerate(images):
                try:
                    alt = await img.get_attribute("alt")
                    if not alt or ("text" not in alt.lower() and "testo" not in alt.lower()):
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

                    for k, v in video_database.items():
                        if selected_key in k:
                            selected_desc = v["description"]
                            break

                    if not selected_desc:
                        selected_desc = f"{selected_key.title()}"

                    print(f"\n--- Aggiornamento: {selected_key} (Indice {i}) ---")

                    # Open Photo
                    await page.evaluate("(el) => el.click()", img)
                    await asyncio.sleep(4)

                    # Click Modifica
                    await page.evaluate("""() => {
                        const buttons = Array.from(document.querySelectorAll('div[role="button"], span'));
                        const editBtn = buttons.find(b => b.innerText.includes('Modifica') || b.textContent.includes('Modifica'));
                        if (editBtn) editBtn.click();
                    }""")
                    await asyncio.sleep(3)

                    full_text = f"{selected_desc}\n\nLink al video: {selected_link}"
                    try:
                        await page.keyboard.type(full_text)
                    except Exception as type_e:
                        print(f"Impossibile digitare: {type_e}")

                    await asyncio.sleep(2)

                    # Click Modifica completata
                    await page.evaluate("""() => {
                        const buttons = Array.from(document.querySelectorAll('div[role="button"], span'));
                        const doneBtn = buttons.find(b => b.innerText.includes('Modifica completata') || b.textContent.includes('Modifica completata'));
                        if (doneBtn) doneBtn.click();
                    }""")
                    print("Didascalia salvata.")
                    await asyncio.sleep(6)

                    # Close Theater View
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(3)

                except Exception as e:
                    print(f"Errore foto indice {i}: {e}")
                    try: await page.keyboard.press("Escape") 
                    except: pass

            await browser.close()
            print("\n--- Aggiornamento copertine completato! ---")
    except Exception as e:
        print(f"ERRORE DI CONNESSIONE: Impossibile connettersi a Chrome ({e}).")
        print("Ti sei assicurato di aver avviato Chrome dal terminale con il comando fornito?")

if __name__ == "__main__":
    asyncio.run(run())

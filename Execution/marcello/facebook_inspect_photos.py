import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.facebook.com")
        await asyncio.sleep(4)

        # Basic form check
        email_field = await page.query_selector("input[name='email']")
        if email_field:
            print("Inserimento credenziali...")
            await page.fill("input[name='email']", "cosafannoglieconomisti@gmail.com")
            await page.fill("input[name='pass']", "3aVZQf#Skx&*reP")
            await page.keyboard.press("Enter")
            await asyncio.sleep(10)

        print("Navigazione alla galleria foto...")
        await page.goto("https://www.facebook.com/profile.php?id=61579548543222&sk=photos")
        await asyncio.sleep(8)

        # Read images and Alt texts
        print("--- GRIGLIA FOTO ---")
        images = await page.query_selector_all("img")
        for i, img in enumerate(images):
            alt = await img.get_attribute("alt")
            src = await img.get_attribute("src")
            print(f"[{i}] Alt: {alt} | Src (short): {src[:40] if src else 'None'}...")

        await page.screenshot(path='/Users/marcolemoglie_1_2/Desktop/canale/Execution/marcello/facebook_inspect_photos.png')
        print("Screenshot salvato.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

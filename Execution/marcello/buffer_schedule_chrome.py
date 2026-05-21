import asyncio
import os
import sys
import re
import argparse
import json
from datetime import datetime, timezone, timedelta
from playwright.async_api import async_playwright

TRACKING_FILE = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/video_tracking.json"

def parse_metadata(path: str) -> dict:
    """Estrae i metadati seguendo la SOP Marcello di buffer_post_single.py."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    result = {
        "paper_title": "",
        "authors":     "",
        "journal":     "",
        "year":        "",
        "description": "",
        "tags":        "",
    }

    desc_section = ""
    if "## Descrizione YouTube" in content:
        desc_section = content.split("## Descrizione YouTube")[1]
        for sep in ["⏰", "##", "▬"]:
            if sep in desc_section:
                desc_section = desc_section.split(sep)[0]
        desc_section = desc_section.strip()
    else:
        match = re.search(r'(Lo studio .+?)(?:\n\n|⏰|##|▬)', content, re.DOTALL)
        if match:
            desc_section = match.group(1).strip()

    for para in desc_section.split("\n\n"):
        para = para.strip()
        if para.startswith("Lo studio"):
            result["description"] = para
            break

    if not result["description"]:
        result["description"] = desc_section.split("\n")[0].strip()

    desc = result["description"]
    # Normalizzazione Titolo Paper (No Header in IG, ma serve per tag)
    title_match = re.search(r'Lo studio ["\u201c]([^"\u201d]+)["\u201d]', desc)
    if title_match:
        raw_title = title_match.group(1).strip()
        upper_ratio = sum(1 for c in raw_title if c.isupper()) / max(len(raw_title), 1)
        result["paper_title"] = raw_title.title() if upper_ratio > 0.5 else raw_title

    def _normalize_caps_quotes(text):
        def repl(m):
            inner = m.group(1)
            up_ratio = sum(1 for c in inner if c.isupper()) / max(len(inner), 1)
            return f'"{inner.title()}"' if up_ratio > 0.5 else f'"{inner}"'
        return re.sub(r'["\u201c]([^"\u201d]+)["\u201d]', repl, text)
    
    desc_normalized = _normalize_caps_quotes(desc)
    result["description"] = desc_normalized

    tag_line = ""
    for line in content.splitlines():
        line_stripped = line.strip()
        if re.match(r'^#[A-Za-zÀ-ÿ0-9]', line_stripped) and line_stripped.count("#") >= 2:
            tag_line = line_stripped
            break
    if not tag_line:
        hashtag_match = re.search(r'(#[A-Za-zÀ-ÿ0-9]+(?:\s+#[A-Za-zÀ-ÿ0-9]+){2,})', content)
        if hashtag_match:
            tag_line = hashtag_match.group(1).strip()
    result["tags"] = tag_line if tag_line else "#CosaFannoGliEconomisti #Economia #Ricerca"

    return result

def build_caption(meta: dict, video_id: str, video_title: str = "") -> str:
    """Costruisce la didascalia nel formato SOP Instagram (Semplificato)."""
    description = meta.get("description", "")
    tags = meta.get("tags", "")
    
    parts = []
    # Inizia direttamente con "Lo studio..."
    if description:
        parts.append(description)
        parts.append("")
    
    # Niente Header, niente Separatore, niente YouTube URL
    parts.append("Link in bio 🔗")
    parts.append("")
    
    # Mantenimento Hashtags
    parts.append(tags)

    return "\n".join(parts).strip()

def load_video_data(target_folder=None):
    mappings = []
    base_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
    
    folders = [target_folder] if target_folder else sorted(os.listdir(base_dir))
    
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path): continue
        
        meta_file = os.path.join(folder_path, "video_metadata.md")
        if not os.path.exists(meta_file): continue
        
        try:
            meta = parse_metadata(meta_file)
            
            # Find infographic
            img_path = ""
            for file in os.listdir(folder_path):
                if "infografica" in file.lower() and file.lower().endswith(".png"):
                    img_path = os.path.join(folder_path, file)
                    break
            
            video_id = "QGC9Wl9Rkpo" # Placeholder
            
            if meta["paper_title"] and img_path:
                mappings.append({
                    "folder": folder,
                    "caption": build_caption(meta, video_id),
                    "img_path": img_path,
                    "title": meta["paper_title"]
                })
        except Exception as e:
            print(f"Errore caricando {folder}: {e}")
            
    return mappings

async def run(target_folder=None, dry_run=False, hour=10, day=7, skip_timer=False):
    print(f"Avvio script di scheduling Buffer (Chrome Bypass) per folder: {target_folder or 'ALL'}")
    video_database = load_video_data(target_folder)
    
    if not video_database:
        print("Nessun dato trovato da processare.")
        return

    if dry_run:
        for item in video_database:
            print(f"\nDRY RUN — {item['folder']}:")
            print("="*60)
            print(item['caption'])
            print("="*60)
            print(f"Image: {item['img_path']}")
        return

    async with async_playwright() as p:
        print("Connettendo a Chrome su localhost:9222...")
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = await context.new_page()
            
            # Navigate
            await page.goto("https://publish.buffer.com/", timeout=60000)
            await asyncio.sleep(5)
            
            # Se c'è un composer aperto, chiudilo
            close_btn = page.locator('button[aria-label="Close"]').first
            if await close_btn.count() > 0:
                print("🔧 Trovato composer aperto, chiusura in corso...")
                await close_btn.click(force=True)
                await asyncio.sleep(2)
            
            # Vai alla coda specifica
            await page.goto("https://publish.buffer.com/channels/69bbf1fd7be9f8b171714642/schedule", timeout=60000)
            await asyncio.sleep(5)
            
            for item in video_database:
                print(f"=== Creazione Post per: {item['title']} ===")
                # 1. New Post
                await page.locator('button:has-text("New Post")').first.click(force=True)
                await asyncio.sleep(5)
                
                # 2. Channel Selection (IG Only)
                ig_id = '69bbf1fd7be9f8b171714642'
                fb_id = '69baada37be9f8b1716baa0d'
                fb_btn = page.locator(f'button[id="{fb_id}"]').first
                ig_btn = page.locator(f'button[id="{ig_id}"]').first
                if await fb_btn.count() > 0 and await fb_btn.get_attribute('aria-pressed') == 'true':
                    await fb_btn.click(force=True)
                if await ig_btn.count() > 0 and await ig_btn.get_attribute('aria-pressed') == 'false':
                    await ig_btn.click(force=True)
                
                # 3. Text
                await page.locator('div[aria-label="composer textbox"]').first.fill(item["caption"])
                await asyncio.sleep(2)
                
                # 4. Image
                async with page.expect_file_chooser(timeout=60000) as fc_info:
                    await page.locator('button:has-text("Select to upload files")').first.click(force=True)
                file_chooser = await fc_info.value
                await file_chooser.set_files(item["img_path"])
                print(f"📸 Immagine caricata: {item['img_path']}")
                await asyncio.sleep(15) 
                
                # 5. Set Date and Time
                if not skip_timer:
                    print("Aprendo dropdown scheduling...")
                    dropdown_trigger = page.locator('button.publish_scheduleSelectorTrigger_A8-nX').first
                    await dropdown_trigger.click(force=True)
                    await asyncio.sleep(4)
                    
                    print("Seleziono Set Date and Time...")
                    set_date_btn = page.get_by_text("Set Date and Time").first
                    await set_date_btn.click(force=True)
                    await asyncio.sleep(4)
                    
                    # Selezione più precisa del giorno nel calendario di Buffer
                    print(f"Seleziono giorno {day}...")
                    calendar_cells = page.locator('button.publish_calendarCell_K6-X9').filter(has_text=str(day))
                    # Filtriamo per assicurarci di non cliccare celle di altri mesi (che sono spesso disabilitate o hanno opacità diversa)
                    target_day = None
                    for i in range(await calendar_cells.count()):
                        cell = calendar_cells.nth(i)
                        if "outside" not in (await cell.get_attribute("class") or "").lower():
                            target_day = cell
                            break
                    
                    if target_day:
                        await target_day.click(force=True)
                    else:
                        # Fallback al selettore vecchio se quello specifico fallisce
                        await page.locator(f'button:has-text("{day}")').filter(has_not=page.locator('span')).first.click(force=True)
                    await asyncio.sleep(3)
                    
                    print(f"Imposto ora {hour}:00 AM...")
                    # Prova il selettore più comune
                    time_trigger = page.locator('div[aria-label="Time selector"]').first
                    if await time_trigger.count() == 0:
                        time_trigger = page.locator('input[aria-label="Time selector"]').first
                    
                    await time_trigger.wait_for(state="attached", timeout=60000)
                    await time_trigger.scroll_into_view_if_needed()
                    await time_trigger.click(force=True)
                    await asyncio.sleep(3)
                    
                    # Svuota e digita l'ora
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Backspace")
                    await page.keyboard.type(f"{hour}:00 AM", delay=100)
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(4)
                    
                    print("Clicco Done...")
                    done_btn = page.locator('button:has-text("Done")').first
                    await done_btn.click(force=True)
                    await asyncio.sleep(4)
                else:
                    print("⏩ Saltando selettore orario (Add to Queue diretto)...")
                
                print("Clicco Schedule Post finale...")
                final_btn = page.locator('button:has-text("Schedule Post")').first
                # Se non trovato col testo, prova la classe specifica
                if await final_btn.count() == 0:
                    final_btn = page.locator('.publish_schedulePostButton_8XRSX').first
                
                await final_btn.wait_for(state="visible", timeout=30000)
                await final_btn.click(force=True)
                await asyncio.sleep(8) # Attesa per il processing finale
                print(f"✅ Successo! Post programmato per {item['folder']}")
                
                # AGGIORNAMENTO TRACKING CENTRALIZZATO
                if os.path.exists(TRACKING_FILE):
                    try:
                        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
                            tracking = json.load(f)
                        if item['folder'] in tracking:
                            tracking[item['folder']]["instagram_url"] = "Post Programmato (Buffer)"
                            tracking[item['folder']]["last_updated"] = datetime.now().isoformat()
                            with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
                                json.dump(tracking, f, indent=4, ensure_ascii=False)
                            print(f"📊 Tracking aggiornato per: {item['folder']}")
                    except Exception as e:
                        print(f"⚠️ Errore aggiornamento tracking: {e}")

                await asyncio.sleep(10)
                
            await page.close()
        except Exception as e:
            print(f"❌ Errore critico: {e}")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--hour", type=int, default=10)
    parser.add_argument("--day", type=int, default=7)
    parser.add_argument("--skip-timer", action="store_true")
    args = parser.parse_args()
    
    asyncio.run(run(target_folder=args.folder, dry_run=args.dry_run, hour=args.hour, day=args.day, skip_timer=args.skip_timer))

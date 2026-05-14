import asyncio
import os
import sys
import csv
from playwright.async_api import async_playwright

async def run(csv_path):
    if not os.path.exists(csv_path):
        print(f"ERRORE: Il file CSV {csv_path} non esiste.")
        return

    # Leggi i dati usando il modulo csv integrato
    rows = []
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    print(f"Caricate {len(rows)} righe dal CSV.")

    async with async_playwright() as p:
        print("\n=== AVVIO AUTOMAZIONE CANVA ===")
        print("Apertura browser con PROFILO PERSISTENTE per salvare i cookie (headless=False)...")
        
        # Cartella dedicata per salvare la sessione evitare loop Cloudflare
        user_data_dir = "/Users/marcolemoglie_1_2/Desktop/canale/.tmp/canva_profile"
        os.makedirs(user_data_dir, exist_ok=True)

        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else await context.new_page()

        await page.goto("https://www.canva.com/login")
        
        print("\n--- AZIONE RICHIESTA ---")
        print("1. Accedi a Canva o sblocca eventuali Captcha nella finestra che si è aperta.")
        print("2. Una volta arrivato sulla DASHBOARD di Canva, torna qui e premi INVIO.")
        input("\nPremi [INVIO] quando sei loggato e vedi la Dashboard di Canva per continuare...")

        print("\nContinuo l'automazione...")

        # 1. Crea un progetto Video
        print("Navigazione per creare un nuovo Video (16:9)...")
        await page.goto("https://www.canva.com/create/videos/")
        await asyncio.sleep(5)

        # Clicca "Crea un video" (Spesso ha testo 'Crea un video' o bottone primario)
        try:
            await page.click("text=Crea un video", timeout=10000)
            print("Cliccato 'Crea un video'.")
        except Exception as e:
            print("Bottone 'Crea un video' non trovato con testo esatto, provo a cercare nella pagina...")
            # Fallback opzionale o manuale
            print("Per favore, se non si è aperto l'editor, clicca tu su 'Crea un video'.")
        
        await asyncio.sleep(8)
        print("Editor Video aperto.")

        print("\n--- ISTRUZIONI PER COMPLETARE LA CREAZIONE IN BLOCCO (BULK CREATE) ---")
        print("Dal momento che Canva usa un’interfaccia Canvas/Dinamica, la via più sicura è:")
        print("1. Nella barra laterale sinistra, clicca su 'App' (in basso).")
        print("2. Cerca 'Creazione in blocco' (Bulk Create).")
        print("3. Clicca 'Inserisci dati manualmente'.")
        print("4. Copia i dati qui sotto e incollali nella tabella di Canva.")
        print("\n--- DATI DA INCOLLARE ---")
        
        # Stampa i dati in formato tab-separated per un facile copia-incolla nella griglia di Canva
        print("Titolo\tDettaglio")
        for row in rows:
            print(f"{row['Titolo']}\t{row['Dettaglio']}")
        print("------------------------")

        print("\n5. Collega i dati alle caselle di testo sulla prima slide.")
        print("6. Genera le pagine.")
        print("\nLo script rimarrà aperto per farti finire. Chiudi la finestra per completare.")

        # Mantieni lo script vivo per non chiudere il browser subito
        while True:
            await asyncio.sleep(10)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python canva_automated_generator.py <percorso_csv>")
        sys.exit(1)
        
    csv_input = sys.argv[1]
    asyncio.run(run(csv_input))

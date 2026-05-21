
import os
import shutil
import time
from pathlib import Path

# Configurazione
DOWNLOADS_DIR = Path("/Users/marcolemoglie_1_2/Downloads")
TARGET_DIR = Path("/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare")
PAPERS_DATABASE = Path("/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse/papers_database")

def get_recent_pdfs(max_age_minutes=60):
    """Trova i PDF scaricati recentemente nella cartella Downloads."""
    recent_pdfs = []
    now = time.time()
    
    if not DOWNLOADS_DIR.exists():
        print(f"Errore: Cartella Downloads non trovata in {DOWNLOADS_DIR}")
        return []

    for file in DOWNLOADS_DIR.glob("*.pdf"):
        mtime = file.stat().st_mtime
        if (now - mtime) / 60 <= max_age_minutes:
            recent_pdfs.append(file)
            
    return sorted(recent_pdfs, key=lambda x: x.stat().st_mtime, reverse=True)

def main():
    print("🚀 Avvio Scansione Paper Scaricati...")
    
    pdfs = get_recent_pdfs()
    
    if not pdfs:
        print("❌ Nessun PDF recente trovato negli ultimi 60 minuti.")
        return

    print(f"🔍 Trovati {len(pdfs)} PDF recenti:")
    for i, pdf in enumerate(pdfs):
        print(f"  {i+1}. {pdf.name}")

    confirm = input("\nVuoi spostare questi file in 'Papers/Da fare'? (y/n): ")
    if confirm.lower() != 'y':
        print("Operazione annullata.")
        return

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    for pdf in pdfs:
        dest = TARGET_DIR / pdf.name
        try:
            shutil.move(str(pdf), str(dest))
            print(f"✅ Spostato: {pdf.name} -> Papers/Da fare/")
        except Exception as e:
            print(f"❌ Errore durante lo spostamento di {pdf.name}: {e}")

    print("\n✨ Operazione completata.")

if __name__ == "__main__":
    main()

import fitz
import sys
import os

def extract_text(pdf_path, max_pages=3):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for i in range(min(len(doc), max_pages)):
            text += doc[i].get_text()
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

if __name__ == "__main__":
    folder = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare"
    
    # Supporto per file singolo come argomento
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        path = os.path.join(folder, target_file)
        if os.path.exists(path):
            txt = extract_text(path, 3)
            # Use basename to avoid errors with subdirectories in /tmp
            safe_filename = os.path.basename(target_file)
            with open(f"/tmp/{safe_filename}.txt", 'w', encoding='utf-8') as out:
                out.write(txt)
            print(f"Estratto Salvato: /tmp/{safe_filename}.txt")
        else:
            print(f"Errore: File {target_file} non trovato.")
        sys.exit(0)

    # Comportamento di default (processa tutto ricorsivamente)
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith(".pdf"):
                path = os.path.join(root, f)
                print(f"\n--- Estratto per {f} ---")
                txt = extract_text(path, 3)
                # Mantieni il salvataggio in /tmp/ con il nome del file
                with open(f"/tmp/{f}.txt", 'w', encoding='utf-8') as out:
                    out.write(txt)
                print(f"Salvato /tmp/{f}.txt (Length: {len(txt)})")


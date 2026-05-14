import fitz
import sys
import os

pdf_files = [
    "aer.20150958.pdf",
    "gulino-masera-2023-contagious-dishonesty-corruption-scandals-and-supermarket-theft.pdf",
    "rdz009.pdf",
    "rest_a_01323.pdf",
    "The Economic Journal - 2015 - Pinotti - The Economic Costs of Organised Crime  Evidence from Southern Italy.pdf"
]

folder = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare"
out_folder = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da_fare_txt"

os.makedirs(out_folder, exist_ok=True)

for f in pdf_files:
    pdf_path = os.path.join(folder, f)
    txt_path = os.path.join(out_folder, f.replace(".pdf", ".txt"))
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n"
        with open(txt_path, 'w', encoding='utf-8') as out:
            out.write(text)
        print(f"Estratto full text per {f} -> {txt_path} (Lunghezza: {len(text)})")
    except Exception as e:
        print(f"Errore su {f}: {e}")

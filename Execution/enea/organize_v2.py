import os
import json
import shutil
import re

# Config
JSON_INPUT = "/tmp/final_hub_data_60_v2.json"
SOURCE_DIR = os.path.expanduser("~/Downloads")
TARGET_BASE = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare/"

ACRONYMS = {
    "American Economic Review": "AER",
    "Quarterly Journal of Economics": "QJE",
    "Journal of Political Economy": "JPE",
    "Review of Economic Studies": "REStud",
    "Econometrica": "ECTA",
    "Journal of the European Economic Association": "JEEA",
    "Economic Journal": "EJ",
    "AEJ Applied Economics": "AEJ_App",
    "AEJ Economic Policy": "AEJ_Pol",
    "Review of Economics and Statistics": "REStat"
}

def clean_name(text):
    return re.sub(r"[^a-zA-Z0-9 ]", " ", text).lower().strip()

def get_acronym(journal):
    for k, v in ACRONYMS.items():
        if k.lower() in journal.lower(): return v
    return "".join([w[0].upper() for w in journal.split() if w[0].isalpha()])

def main():
    if not os.path.exists(JSON_INPUT):
        print(f"Error: {JSON_INPUT} not found")
        return
    
    with open(JSON_INPUT, "r") as f:
        data = json.load(f)

    all_papers = []
    for section in data:
        cat = section["category"]
        for p in section["papers"]:
            p["target_category"] = cat
            all_papers.append(p)

    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".pdf")]
    moved_count = 0

    print(f"Scanning {len(files)} files in Downloads...")

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        file_clean = clean_name(filename)
        file_words = set([w for w in file_clean.split() if len(w) > 3])
        
        match = None
        for p in all_papers:
            # 1. DOI Segment Match (ID like qjaf006)
            doi = p.get("doi", "")
            doi_segments = [s for s in doi.split("/") if len(s) > 4]
            for seg in doi_segments:
                if clean_name(seg).replace(" ", "") in file_clean.replace(" ", ""):
                    match = p
                    break
            if match: break

            # 2. Word-based Title Match
            title_clean = clean_name(p["title"])
            title_words = set([w for w in title_clean.split() if len(w) > 3])
            intersection = title_words.intersection(file_words)
            # If at least 3 significant words match, or 50% of title words
            if len(intersection) >= min(3, len(title_words)):
                match = p
                break

        if match:
            cat = match["target_category"]
            acro = get_acronym(match["journal"])
            year = match["year"]
            
            # Professionally Cleaned Title slug
            words = re.sub(r"[^a-zA-Z0-9 ]", "", match["title"]).split()
            slug = "_".join(words[:5]) # 5 words for better readability
            new_name = f"{slug}_{acro}_{year}.pdf"
            
            target_dir = os.path.join(TARGET_BASE, cat)
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, new_name)
            
            print(f"Organizing: {filename} -> {cat}/{new_name}")
            shutil.move(file_path, target_path)
            moved_count += 1

    print(f"\nOperazione completata: {moved_count} paper archiviati.")

if __name__ == "__main__":
    main()

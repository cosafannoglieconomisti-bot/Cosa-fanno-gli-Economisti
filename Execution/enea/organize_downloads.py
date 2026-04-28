import os
import json
import shutil
import re

# Config
JSON_INPUT = "/tmp/papers_to_review_italy_v4.json"
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
    "Review of Economics and Statistics": "REStat",
    "Journal of Labor Economics": "JOLE",
    "Journal of Public Economics": "JPubE"
}

def clean_name(text):
    return re.sub(r"[^a-zA-Z0-9 ]", "", text).lower().strip()

def get_acronym(journal):
    # Try exact match first
    if journal in ACRONYMS:
        return ACRONYMS[journal]
    # Try fuzzy match
    for k, v in ACRONYMS.items():
        if k.lower() in journal.lower():
            return v
    # Fallback to initials
    return "".join([w[0].upper() for w in journal.split() if w[0].isalpha()])

def main():
    if not os.path.exists(JSON_INPUT):
        print(f"Error: missing {JSON_INPUT}")
        return

    with open(JSON_INPUT, "r") as f:
        categories = json.load(f)

    # Flatten for easier matching
    all_papers = []
    for cat, papers in categories.items():
        for p in papers:
            p["target_category"] = cat
            all_papers.append(p)

    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".pdf")]
    
    moved_count = 0
    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        file_clean = clean_name(filename)
        
        match_found = None
        for p in all_papers:
            title_clean = clean_name(p["title"])
            title_words = set([w for w in title_clean.split() if len(w) > 3])
            file_words = set([w for w in file_clean.split() if len(w) > 3])
            intersection = title_words.intersection(file_words)
            
            # Confidence check: at least 3 matching significant words
            if len(intersection) >= min(3, len(title_words)):
                match_found = p
                break
            
            # DOI fallback (if user saved as DOI)
            if p.get("doi"):
                doi_clean = clean_name(p["doi"])
                if doi_clean in file_clean:
                    match_found = p
                    break

        if match_found:
            cat = match_found["target_category"]
            year = match_found["year"]
            journal_raw = match_found["journal"]
            acronym = get_acronym(journal_raw)
            
            # Professionally Cleaned Title
            title_words = match_found["title"].split()
            short_title = "_".join(title_words[:6]) # First 6 words for slug
            short_title = re.sub(r"[^a-zA-Z0-9_]", "", short_title.replace(" ", "_"))
            
            # Format: Title_ACRONYM_YEAR.pdf
            new_name = f"{short_title}_{acronym}_{year}.pdf"
            
            target_dir = os.path.join(TARGET_BASE, cat)
            os.makedirs(target_dir, exist_ok=True)
            
            target_path = os.path.join(target_dir, new_name)
            
            print(f"Archiving: {filename} -> {cat}/{new_name}")
            shutil.move(file_path, target_path)
            moved_count += 1

    print(f"\nOperazione completata. Archivati {moved_count} paper con successo.")

if __name__ == "__main__":
    main()

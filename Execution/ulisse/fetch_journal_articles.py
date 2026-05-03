#!/usr/bin/env python3
import os
import sys
import requests
import json
import time

# Whitelist Journal (ISSN) - Coerente con verify_paper.py
JOURNAL_MAP = {
    "American_Economic_Review": ["0002-8282", "1944-7981"],
    "Quarterly_Journal_of_Economics": ["0033-5533", "1531-4650"],
    "Journal_of_Political_Economy": ["0022-3808", "1537-534X"],
    "Econometrica": ["0012-9682", "1468-0262"],
    "Review_of_Economic_Studies": ["0034-6527", "1467-937X"],
    "AEJ_Applied_Economics": ["1945-7731", "1945-774X"],
    "AEJ_Economic_Policy": ["1945-7707", "1945-7715"],
    "AEJ_Macroeconomics": ["1945-7669", "1945-7677"],
    "AEJ_Microeconomics": ["1945-7685", "1945-7693"],
    "Journal_of_Economic_Perspectives": ["0895-3309", "1944-7965"],
    "Review_of_Economics_and_Statistics": ["0034-6535", "1530-9142"],
    "Journal_of_the_European_Economic_Association": ["1542-4766", "1542-4774"],
    "Journal_of_Monetary_Economics": ["0304-3932", "1873-1295"],
    "Journal_of_Labor_Economics": ["0734-306X", "1537-5307"],
    "Nature": ["0028-0836", "1476-4687"],
    "Science": ["0036-8075", "1095-9203"],
    "PNAS": ["0027-8424", "1091-6490"],
    "Economic_Journal": ["0013-0133", "1468-0297"]
}

# Cartella Database
DB_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse/papers_database/"

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return "N/A"
    try:
        word_index = {}
        for word, positions in inverted_index.items():
            for pos in positions:
                word_index[pos] = word
        return " ".join([word_index[i] for i in sorted(word_index.keys())])
    except:
        return "N/A"

def fetch_journal_papers(journal_name, issns, start_year=2010):
    print(f"\n[*] Scaricamento: {journal_name} (dal {start_year})")
    
    file_path = os.path.join(DB_DIR, f"{journal_name}.txt")
    existing_dois = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("DOI:"):
                    existing_dois.add(line.strip().replace("DOI:", ""))

    # Quote API e Filtro
    # Per Nature/Science/PNAS aggiungiamo un filtro concettuale 'Economics'
    filter_query = f"primary_location.source.issn:{'|'.join(issns)},publication_year:>{start_year-1},type:article"
    if journal_name in ["Nature", "Science", "PNAS"]:
        filter_query += ",concepts.id:C162324751" # OpenAlex ID for Economics
        
    cursor = "*"
    count_new = 0
    
    while cursor:
        url = f"https://api.openalex.org/works?filter={filter_query}&per_page=100&cursor={cursor}"
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print(f"[!] Errore API: {response.status_code}")
                break
                
            data = response.json()
            results = data.get("results", [])
            next_cursor = data.get("meta", {}).get("next_cursor")
            
            if not results:
                break
                
            with open(file_path, "a", encoding="utf-8") as f:
                for paper in results:
                    doi = paper.get("doi") or f"id: {paper.get('id')}"
                    if doi in existing_dois:
                        continue
                    
                    title = paper.get("title", "N/A")
                    year = paper.get("publication_year", "N/A")
                    abstract = reconstruct_abstract(paper.get("abstract_inverted_index"))
                    
                    f.write(f"--- ARTICLE START ---\n")
                    f.write(f"TITLE: {title}\n")
                    f.write(f"YEAR: {year}\n")
                    f.write(f"DOI: {doi}\n")
                    f.write(f"ABSTRACT: {abstract}\n")
                    f.write(f"--- ARTICLE END ---\n\n")
                    
                    existing_dois.add(doi)
                    count_new += 1
            
            print(f"[*] Processati {len(results)} articoli... (Cursor: {cursor[:10]}...)")
            
            if cursor == next_cursor: # Fine paginazione
                break
            cursor = next_cursor
            time.sleep(0.1) # Breve pausa per rate-limit
            
        except Exception as e:
            print(f"[!] Eccezione: {e}")
            break
            
    print(f"[✔] Completato: {journal_name}. Aggiunti {count_new} nuovi articoli.")

def main():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    # Se passato un journal specifico da riga di comando
    target_journal = sys.argv[1] if len(sys.argv) > 1 else None
    
    if target_journal:
        if target_journal in JOURNAL_MAP:
            fetch_journal_papers(target_journal, JOURNAL_MAP[target_journal])
        else:
            print(f"[!] Journal '{target_journal}' non trovato in whitelist.")
    else:
        # Loop su tutti i journal
        for name, issns in JOURNAL_MAP.items():
            fetch_journal_papers(name, issns)

if __name__ == "__main__":
    main()

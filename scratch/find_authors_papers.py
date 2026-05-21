import os
import re

DATABASE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse/papers_database"
AUTHORS = ["Adda", "Pinotti", "D'Adda"]

def parse_articles(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    articles = re.split(r'--- ARTICLE START ---', content)
    parsed = []
    for art in articles:
        if not art.strip():
            continue
        
        # Extract fields
        title_match = re.search(r'TITLE: (.*)', art)
        year_match = re.search(r'YEAR: (\d{4})', art)
        doi_match = re.search(r'DOI: (.*)', art)
        abstract_match = re.search(r'ABSTRACT: (.*)', art, re.DOTALL)
        
        if title_match and year_match:
            title = title_match.group(1).strip()
            year = int(year_match.group(1))
            doi = doi_match.group(1).strip() if doi_match else "N/A"
            abstract = abstract_match.group(1).strip() if abstract_match else ""
            abstract = abstract.split('--- ARTICLE END ---')[0].strip()
            
            parsed.append({
                'title': title,
                'year': year,
                'doi': doi,
                'abstract': abstract,
                'journal': os.path.basename(file_path).replace('.txt', '').replace('_', ' ')
            })
    return parsed

found_papers = []

for filename in os.listdir(DATABASE_DIR):
    if filename.endswith('.txt'):
        path = os.path.join(DATABASE_DIR, filename)
        articles = parse_articles(path)
        for art in articles:
            # Check if any author name is in title or abstract
            text = (art['title'] + " " + art['abstract']).lower()
            if any(author.lower() in text for author in AUTHORS):
                # Exclude articles that are just lists of referees
                if "acknowledges the assistance of" in text or "recent referees" in text:
                    continue
                found_papers.append(art)

# Sort by year descending
found_papers.sort(key=lambda x: x['year'], reverse=True)

for p in found_papers:
    print(f"### {p['title']}")
    print(f"- **Journal**: {p['journal']}")
    print(f"- **Anno**: {p['year']}")
    print(f"- **DOI**: {p['doi']}")
    print(f"- **Abstract**: {p['abstract'][:500]}...")
    print("\n---\n")

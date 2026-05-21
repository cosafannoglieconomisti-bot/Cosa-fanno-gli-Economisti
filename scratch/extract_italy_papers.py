import os
import re

DATABASE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse/papers_database"
START_YEAR = 2015

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
            # Remove trailing '--- ARTICLE END ---' from abstract if it's there
            abstract = abstract.split('--- ARTICLE END ---')[0].strip()
            
            parsed.append({
                'title': title,
                'year': year,
                'doi': doi,
                'abstract': abstract,
                'journal': os.path.basename(file_path).replace('.txt', '').replace('_', ' ')
            })
    return parsed

def is_empirical(article):
    text = (article['title'] + " " + article['abstract']).lower()
    empirical_keywords = [
        'data', 'estimate', 'evidence', 'empirical', 'experiment', 'regression', 
        'causal', 'identification', 'rdd', 'difference-in-difference', 'iv', 
        'survey', 'microdata', 'panel', 'econometric', 'test', 'result'
    ]
    return any(kw in text for kw in empirical_keywords)

def concerns_italy(article):
    text = (article['title'] + " " + article['abstract']).lower()
    return 'italy' in text or 'italian' in text

all_italy_papers = []

for filename in os.listdir(DATABASE_DIR):
    if filename.endswith('.txt'):
        path = os.path.join(DATABASE_DIR, filename)
        articles = parse_articles(path)
        for art in articles:
            if art['year'] >= START_YEAR and concerns_italy(art) and is_empirical(art):
                all_italy_papers.append(art)

# Sort by year descending
all_italy_papers.sort(key=lambda x: x['year'], reverse=True)

print(f"# Lista Paper Empirici su Italia (2015-{START_YEAR+11})\n")
for p in all_italy_papers:
    print(f"## {p['title']}")
    print(f"- **Journal**: {p['journal']}")
    print(f"- **Anno**: {p['year']}")
    print(f"- **DOI**: {p['doi']}")
    print(f"- **Abstract**: {p['abstract'][:300]}...")
    print("\n---\n")

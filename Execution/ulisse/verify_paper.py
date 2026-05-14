#!/usr/bin/env python3
import sys
import argparse
import requests
import json
import unicodedata

# Whitelist ISSN dei Top Journals (Incluso Online ISSN)
JOURNAL_ISSNS = {
    "0002-8282": "American Economic Review", "1944-7981": "American Economic Review",
    "0033-5533": "Quarterly Journal of Economics", "1531-4650": "Quarterly Journal of Economics",
    "0022-3808": "Journal of Political Economy", "1537-534X": "Journal of Political Economy",
    "0012-9682": "Econometrica", "1468-0262": "Econometrica",
    "0034-6527": "Review of Economic Studies", "1467-937X": "Review of Economic Studies",
    "1945-7731": "AEJ: Applied Economics", "1945-774X": "AEJ: Applied Economics",
    "1945-7707": "AEJ: Economic Policy", "1945-7715": "AEJ: Economic Policy",
    "1945-7669": "AEJ: Macroeconomics", "1945-7677": "AEJ: Macroeconomics",
    "1945-7685": "AEJ: Microeconomics", "1945-7693": "AEJ: Microeconomics",
    "0895-3309": "Journal of Economic Perspectives", "1944-7965": "Journal of Economic Perspectives",
    "0034-6535": "Review of Economics and Statistics", "1530-9142": "Review of Economics and Statistics",
    "1542-4766": "Journal of the European Economic Association", "1542-4774": "Journal of the European Economic Association",
    "0304-3932": "Journal of Monetary Economics", "1873-1295": "Journal of Monetary Economics",
    "0734-306X": "Journal of Labor Economics", "1537-5307": "Journal of Labor Economics",
    "0028-0836": "Nature", "1476-4687": "Nature",
    "0036-8075": "Science", "1095-9203": "Science",
    "0027-8424": "PNAS", "1091-6490": "PNAS",
    "0013-0133": "Economic Journal", "1468-0297": "Economic Journal"
}

# Whitelist Nomi (Fallback nominale SOLO ESATTO)
JOURNAL_WHITELIST = list(set(JOURNAL_ISSNS.values()))

def strip_accents(text):
    if not text: return ""
    try: text = str(text)
    except: return text
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def query_openalex_by_tags(tags, topic=None, year_min=2000):
    # Trasforma i tag separati da virgola in una ricerca OR per massimizzare il matching semantico
    # Esempio: "Labor Economics,Public Policy" -> "Labor Economics" OR "Public Policy"
    tag_list = [t.strip().replace(':', ' ') for t in tags.split(',') if t.strip()]
    if not tag_list: return []
    
    # Query con OR tra i tag
    tags_query = " OR ".join([f'"{t}"' for t in tag_list])
    
    # Se presente un topic, lo usiamo in AND per forzare la rilevanza contestuale
    if topic:
        search_query = f'("{topic}") AND ({tags_query})'
    else:
        search_query = tags_query
        
    url = f"https://api.openalex.org/works?filter=title_and_abstract.search:{search_query},publication_year:>{year_min-1},type:article&per_page=100&sort=relevance_score:desc"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json().get("results", [])
    except Exception as e:
         print(f"[*] Errore OpenAlex: {e}")
    return []

def is_journal_allowed(cand):
    location = cand.get("primary_location")
    if location and location.get("source"):
        source = location.get("source")
        issns = source.get("issn", [])
        
        # 1. Check ISSNs
        if issns:
            for issn in issns:
                if issn in JOURNAL_ISSNS:
                    return True, JOURNAL_ISSNS[issn]
        
        # 2. Check Name (Exact)
        display_name = source.get("display_name", "")
        if display_name:
            clean_j = display_name.lower().strip()
            for allowed in JOURNAL_WHITELIST:
                if clean_j == allowed.lower().strip():
                    return True, allowed
                
    return False, None

def verify_and_match(tags, topic=None, year_min=2000):
    print(f"[*] Avvio ricerca per TOPIC: '{topic}' | TAGS: '{tags}' (Post-{year_min})")
    
    results = query_openalex_by_tags(tags, topic, year_min)
    if not results:
        # Se fallisce con il topic (troppo specifico), riprova solo con i tags
        print("[*] Re-tentativo solo con TAGS...")
        results = query_openalex_by_tags(tags, None, year_min)
        
    if not results:
        return None

    for cand in results:
        title = cand.get("title", "")
        year = cand.get("publication_year", 0)
        
        allowed, official_name = is_journal_allowed(cand)
        if not allowed:
            continue

        print(f"[*] Match Trovalo: '{title[:60]}...' su '{official_name}' ({year})")

        if year < year_min:
            continue

        authors_list = [a.get("author", {}).get("display_name", "N/A") for a in cand.get("authorships", [])]
        doi = cand.get("doi")
        doi_url = doi if (doi and doi.startswith("http")) else f"https://doi.org/{doi.replace('https://doi.org/', '')}" if doi else ""
        landing_url = cand.get("primary_location", {}).get("landing_page_url") or doi_url

        print(f"\n[✔ VERIFICATO] Risultato trovato in Top Journal!")
        return {
            "title": title,
            "authors": ", ".join(authors_list),
            "journal": official_name,
            "year": year,
            "url": landing_url,
            "doi": doi_url
        }

    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tags", required=True, help="Tag separati da virgola")
    parser.add_argument("--query", help="Topic/Soggetto principale")
    parser.add_argument("--year", type=int, default=2000)
    args = parser.parse_args()
    
    match = verify_and_match(args.tags, args.query, args.year)
    if match:
        print("---JSON_START---")
        print(json.dumps(match))
        print("---JSON_END---")
        sys.exit(0)
    else:
        print("\n[✘ FALLITO] Nessun articolo nei Top Journals corrisponde a questi tag.")
        sys.exit(1)

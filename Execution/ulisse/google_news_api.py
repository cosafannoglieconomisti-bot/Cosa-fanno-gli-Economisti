#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
import json
import re
import sys
import argparse
from datetime import datetime

def clean_html(text):
    if not text: return ""
    # Rimuove CDATA e tag HTML
    text = text.replace("<![CDATA[", "").replace("]]>", "")
    return re.sub('<[^<]+?>', '', text).strip()

def fetch_google_news(query, hl='it', gl='IT', ceid='IT:it'):
    """
    Recupera news da Google News tramite RSS e le restituisce in formato JSON.
    """
    base_url = "https://news.google.com/rss/search"
    params = {
        'q': query,
        'hl': hl,
        'gl': gl,
        'ceid': ceid
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        response = requests.get(base_url, params=params, timeout=15, headers=headers)
        
        if response.status_code != 200:
            return {"error": f"HTTP Error {response.status_code}", "results": []}
            
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        results = []
        for item in items:
            title = clean_html(item.find('title').text) if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
            source_node = item.find('source')
            source = source_node.text if source_node is not None else "Unknown"
            
            # Formattazione data (opzionale)
            try:
                dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                pub_date_iso = dt.isoformat()
            except:
                pub_date_iso = pub_date

            results.append({
                "title": title,
                "link": link,
                "published": pub_date_iso,
                "source": source
            })
            
        return {
            "query": query,
            "count": len(results),
            "last_updated": datetime.now().isoformat(),
            "results": results
        }
        
    except Exception as e:
        return {"error": str(e), "results": []}

def main():
    parser = argparse.ArgumentParser(description="Google News to JSON Extractor")
    parser.add_argument("--query", type=str, required=True, help="Query di ricerca (es: 'economia', 'site:ilpost.it')")
    parser.add_argument("--hl", type=str, default="it", help="Lingua (default: it)")
    parser.add_argument("--gl", type=str, default="IT", help="Paese (default: IT)")
    parser.add_argument("--output", type=str, help="Percorso file di output (opzionale)")
    
    args = parser.parse_args()
    
    data = fetch_google_news(args.query, hl=args.hl, gl=args.gl)
    
    json_output = json.dumps(data, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"Risultati salvati in: {args.output}")
    else:
        print(json_output)

if __name__ == "__main__":
    main()

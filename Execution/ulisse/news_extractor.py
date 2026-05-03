#!/usr/bin/env python3
import requests
import re
import xml.etree.ElementTree as ET
from datetime import datetime

# STRETTAMENTE 5 FONTI SOP
SOURCES = {
    "ANSA": "https://www.ansa.it/sito/notizie/economia/economia_rss.xml",
    "Corriere": "https://xml2.corriereobjects.it/rss/economia.xml",
    "Repubblica": "https://www.repubblica.it/rss/economia/rss2.0.xml",
    "Il Post": "https://www.ilpost.it/feed",
    "Fanpage": "https://news.google.com/rss/search?q=site:fanpage.it+when:1d&hl=it&gl=IT&ceid=IT:it"
}

def clean_html(text):
    if not text: return ""
    # Rimuove CDATA e tag HTML
    text = text.replace("<![CDATA[", "").replace("]]>", "")
    return re.sub('<[^<]+?>', '', text).strip()

def fetch_rss(name, url, count=10):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://www.google.com/'
        }
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code != 200:
            print(f"[{name}] HTTP Error: {response.status_code}")
            return []
            
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        results = []
        for item in items[:count]:
            title = clean_html(item.find('title').text) if item.find('title') is not None else ""
            desc_node = item.find('description')
            description = clean_html(desc_node.text) if desc_node is not None else ""
            
            # Filtro base per assicurarsi che sia economia per testate generaliste
            content_lower = (title + description).lower()
            if name in ["Il Post", "Fanpage"]:
                keywords = ["econom", "finanz", "mercato", "banca", "pil", "tasse", "aziend", "lavoro", "bonus", "fisco", "pensioni", "governo"]
                if not any(kw in content_lower for kw in keywords):
                    continue

            results.append({
                "source": name,
                "topic": title,
                "description": description[:300] + "..." if len(description) > 300 else description
            })
        return results
    except Exception as e:
        print(f"[{name}] Errore: {e}")
        return []

def get_raw_news_batch():
    """Recupera un pool completo di notizie da tutte le fonti SOP per la logica di consenso."""
    all_news = []
    for name, url in SOURCES.items():
        all_news.extend(fetch_rss(name, url, count=10))
    return all_news

def get_hot_topics(total_count=3):
    """Fallback per compatibilità con versioni precedenti, restituisce i primi N articoli del batch."""
    news = get_raw_news_batch()
    return news[:total_count]

if __name__ == "__main__":
    import json
    news = get_raw_news_batch()
    print(f"Recuperate {len(news)} notizie totali dalle 5 fonti SOP.")
    if news:
        print("Esempio prima notizia:")
        print(json.dumps(news[0], indent=2))

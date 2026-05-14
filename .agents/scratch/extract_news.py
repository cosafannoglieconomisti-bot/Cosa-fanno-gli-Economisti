import sys
import os
sys.path.append('/Users/marcolemoglie_1_2/Desktop/canale/Execution/ulisse')
from news_extractor import get_raw_news_batch
import json

news = get_raw_news_batch()
os.makedirs('/Users/marcolemoglie_1_2/Desktop/canale/Temp/ulisse', exist_ok=True)
output_path = '/Users/marcolemoglie_1_2/Desktop/canale/Temp/ulisse/current_news.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(news, f, indent=2, ensure_ascii=False)
print(f"News saved to {output_path}")

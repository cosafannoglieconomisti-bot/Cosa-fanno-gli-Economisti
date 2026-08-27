from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import sys
import os
sys.path.append(str(REPO_ROOT / 'Execution' / 'ulisse'))
from news_extractor import get_raw_news_batch
import json

news = get_raw_news_batch()
os.makedirs(str(REPO_ROOT / 'Temp' / 'ulisse'), exist_ok=True)
output_path = str(REPO_ROOT / 'Temp' / 'ulisse' / 'current_news.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(news, f, indent=2, ensure_ascii=False)
print(f"News saved to {output_path}")

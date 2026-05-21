
import json
import re

def list_shorts():
    with open('/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/shorts_list.json', 'r') as f:
        shorts = json.load(f)
    
    print(f"{'ID':<15} | {'Title':<40} | {'Link ID':<15}")
    print("-" * 75)
    for s in shorts:
        desc = s.get('description', '')
        link_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', desc)
        link_id = link_match.group(1) if link_match else "NONE"
        print(f"{s['id']:<15} | {s['title'][:40]:<40} | {link_id:<15}")

if __name__ == '__main__':
    list_shorts()

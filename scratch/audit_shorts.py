import json

path = '/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/shorts_list.json'
with open(path, 'r', encoding='utf-8') as f:
    shorts = json.load(f)

print(f"Total Shorts: {len(shorts)}")
missing_link = []
for s in shorts:
    if "https://youtu.be/" not in s.get('description', ''):
        missing_link.append(s)

print(f"Shorts with missing links: {len(missing_link)}")
for s in missing_link:
    print(f"- {s.get('id')} ({s.get('title')})")

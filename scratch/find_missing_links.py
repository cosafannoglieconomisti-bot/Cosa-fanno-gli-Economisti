import json

def find_missing_links():
    shorts_path = '/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/shorts_list.json'
    with open(shorts_path, 'r', encoding='utf-8') as f:
        shorts = json.load(f)
    
    missing = []
    for s in shorts:
        desc = s.get('description', '')
        if "https://youtu.be/" not in desc and "Video completo qui" not in desc:
            missing.append(s)
            
    print(f"Found {len(missing)} shorts missing links.")
    for m in missing:
        print(f"ID: {m['id']} | Title: {m['title']}")

if __name__ == "__main__":
    find_missing_links()

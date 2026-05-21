
import json
import os
import re

def verify_all():
    with open('/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/shorts_list.json', 'r') as f:
        shorts = json.load(f)
    
    # Load long videos to get their titles
    with open('/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/videos_list_updated.json', 'r') as f:
        long_vids = {v['id']: v['title'] for v in json.load(f)}
    
    print(f"{'Short ID':<15} | {'Short Title':<30} | {'Linked Long Title'}")
    print("-" * 100)
    
    for s in shorts:
        desc = s.get('description', '')
        link_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', desc)
        link_id = link_match.group(1) if link_match else None
        long_title = long_vids.get(link_id, "NOT FOUND") if link_id else "NO LINK"
        
        # Get transcript snippet
        transcript_path = f"/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/transcript_{s['id']}.srt"
        snippet = "NO TRANSCRIPT"
        if os.path.exists(transcript_path):
            with open(transcript_path, 'r', encoding='utf-8') as tf:
                lines = tf.readlines()
                # Find the first text line (after timestamp)
                for line in lines:
                    if not line.strip().isdigit() and '-->' not in line and line.strip():
                        snippet = line.strip()
                        break
        
        print(f"{s['id']:<15} | {s['title'][:30]:<30} | {long_title}")
        print(f"   CONTENT: {snippet}")
        print("-" * 100)

if __name__ == '__main__':
    verify_all()

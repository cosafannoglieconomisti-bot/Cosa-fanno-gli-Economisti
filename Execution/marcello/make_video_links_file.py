from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import json
import os

base_dir = str(REPO_ROOT)
videos_updated_path = os.path.join(base_dir, "Temp/romolo/videos_list_updated.json")
output_path = os.path.join(base_dir, "Execution/marcello/lista_video_link.txt")

with open(videos_updated_path, 'r', encoding='utf-8') as f:
    videos = json.load(f)

lines = []
for video in videos:
    lines.append(f"Titolo: {video['title']}")
    lines.append(f"Video ID: {video['id']}")
    lines.append(f"Link: https://youtu.be/{video['id']}")
    lines.append("-" * 40)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print(f"File generato: {output_path}")

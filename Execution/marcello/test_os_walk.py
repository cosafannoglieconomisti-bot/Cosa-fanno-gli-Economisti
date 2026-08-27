from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import os
base_dir = str(REPO_ROOT / 'Cleaned')
print(f"Checking path: {base_dir}")
count = 0
for root, dirs, files in os.walk(base_dir):
    print(f"Found root: {root}")
    for f in files:
        if f == "video_metadata.md":
            print(f"  -> FOUND: {f}")
            count += 1
print(f"Total found: {count}")

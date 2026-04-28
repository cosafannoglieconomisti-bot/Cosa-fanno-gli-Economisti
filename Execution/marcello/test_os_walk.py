import os
base_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"
print(f"Checking path: {base_dir}")
count = 0
for root, dirs, files in os.walk(base_dir):
    print(f"Found root: {root}")
    for f in files:
        if f == "video_metadata.md":
            print(f"  -> FOUND: {f}")
            count += 1
print(f"Total found: {count}")

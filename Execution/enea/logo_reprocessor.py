from PIL import Image
import os
from collections import deque

# Paths
INPUT_PATH = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/assets/Logo_canale_transparente.png"
OUTPUT_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/assets/trials"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the original logo
orig = Image.open(INPUT_PATH).convert("RGBA")
width, height = orig.size
bbox_orig = orig.getbbox() # (103, 88, 965, 911)
src_pixels = orig.load()

# 1. Identify all components using BFS
visited = set()
components = []

for y in range(height):
    for x in range(width):
        r, g, b, a = src_pixels[x, y]
        # Any non-transparent pixel
        if a > 20 and (x, y) not in visited:
            comp = []
            queue = deque([(x, y)])
            visited.add((x, y))
            while queue:
                cx, cy = queue.popleft()
                comp.append((cx, cy))
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        na = src_pixels[nx, ny][3]
                        if na > 20 and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
            components.append(comp)

# 2. Select ONLY components that do NOT touch the boundary of the original bbox
# The ring spans exactly from min_x to max_x and min_y to max_y of the whole thing.
internal_components = []
for comp in components:
    c_min_x = min(p[0] for p in comp)
    c_max_x = max(p[0] for p in comp)
    c_min_y = min(p[1] for p in comp)
    c_max_y = max(p[1] for p in comp)
    
    # If it doesn't touch the very edges of the total logo content
    if c_min_x > bbox_orig[0] + 5 and c_max_x < bbox_orig[2] - 5 and \
       c_min_y > bbox_orig[1] + 5 and c_max_y < bbox_orig[3] - 5:
        internal_components.append(comp)

# 3. Reconstruct
new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
new_p = new_img.load()
for comp in internal_components:
    for x, y in comp:
        new_p[x, y] = src_pixels[x, y]

# Final crop and scale
bbox_final = new_img.getbbox()
if bbox_final:
    logo_cleaned = new_img.crop(bbox_final)
else:
    logo_cleaned = new_img

target_size = 1080
canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 255))
# Scale to fill 70% (was 75%) for extra safety in circular crops
padding_ratio = 0.70
scale_factor = (target_size * padding_ratio) / max(logo_cleaned.size)
new_size = (int(logo_cleaned.width * scale_factor), int(logo_cleaned.height * scale_factor))
resized_logo = logo_cleaned.resize(new_size, Image.Resampling.LANCZOS)
paste_pos = ((target_size - resized_logo.width) // 2, (target_size - resized_logo.height) // 2)
canvas.paste(resized_logo, paste_pos, resized_logo)

# Save
output_path = os.path.join("/Users/marcolemoglie_1_2/Desktop/canale/Temp/assets", "Logo_canale_quadrato.png")
canvas.save(output_path)
print(f"Logo saved to: {output_path}")
print(f"Num internal components: {len(internal_components)}")
print(f"Final BBox: {bbox_final}")

import cv2
import numpy as np
from collections import Counter

def get_dominant_color(image_path):
    img = cv2.imread(image_path)
    # Convert to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Reshape the image to be a list of pixels
    pixels = img.reshape(-1, 3)
    
    # Remove black/white background pixels to find the orange
    # Orange is roughly R > 200, G > 100, B < 100
    orange_pixels = [p for p in pixels if p[0] > 200 and p[1] > 100 and p[2] < 100]
    
    if not orange_pixels:
        # Fallback if specific profile fails, look for most common non-white
        non_white = [p for p in pixels if not (p[0] > 240 and p[1] > 240 and p[2] > 240)]
        orange_pixels = non_white

    if not orange_pixels:
         return "No color found"

    # Find the most common pixel
    color_counts = Counter([tuple(p) for p in orange_pixels])
    dominant = color_counts.most_common(1)[0][0]
    
    # Convert to Hex
    return '#{:02x}{:02x}{:02x}'.format(dominant[0], dominant[1], dominant[2])

print("Dominant Orange Hex:", get_dominant_color('/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo/logo_canale.jpeg'))

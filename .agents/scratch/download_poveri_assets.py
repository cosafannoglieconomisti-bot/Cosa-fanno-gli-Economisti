import os
import requests
import json

# Setup
notebook_id = "693591f6-e2b0-45e2-b235-113d42a1af64"
video_url = "https://lh3.googleusercontent.com/notebooklm/AKXwDQGq7d8b8dSyF2nZNgMBpFah8TnyUT8WbanpsaXn8bCwJdEj460w8-7lzis5gJ6yJkMGGLcpiv5G1XjgP88gpcl8v2gxFv_BWm5hiclX4gnA5Occnwo_CcIEWAEDSh64HtYsrgqCZdwypjBI97kgEhAHAbagzp8=m22-dv"
infographic_url = "https://lh3.googleusercontent.com/notebooklm/AKXwDQGxgV25x_zismcaQjSFAXPX4pK1MWIev9q7edjixarwRX74ul_VASvhTEDmHjQTO0LY7MjiZ68wJ3VXxGotnfOXRl_jb_J_9mu3omawIc9E0Q_o3Vo4V8Kt2FKfAnQEA2PzTnDmSiS9EHEzm2wjne9EnynmheE=w2048-d-h2048-mp2"
target_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Poveri_in_Pensione"
auth_path = "/Users/marcolemoglie_1_2/.notebooklm-mcp/auth.json"

# Load cookies
with open(auth_path, 'r') as f:
    auth_data = json.load(f)

cookies_dict = auth_data['cookies']
cookie_header = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])

headers = {
    "Cookie": cookie_header,
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def download_file(url, filename):
    print(f"Downloading {filename}...")
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        filepath = os.path.join(target_dir, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {filename} to {filepath}")
        return True
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")
        print(response.text[:500])
        return False

# Execution
download_file(video_url, "Poveri_in_Pensione_raw.mp4")
download_file(infographic_url, "infografica_raw.png")

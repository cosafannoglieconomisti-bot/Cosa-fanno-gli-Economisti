import subprocess
import os
import json

notebook_id = "e7fb498e-5f32-4f35-976f-4b356c7e34cc"
video_url = "https://lh3.googleusercontent.com/notebooklm/AKXwDQFJLgeRFxzDj8QwjHfv_AOa4S4r1wPw-B0A_QzsP797mWLMwBY0Ac7ipanKO1sIwIZexDpXvDpVRKgc4uYWwAVqnOCi_aW9OUlXlR4HiK6FNlKWmJTOHDvdgZr4UHMpongxHyAG9RMX9jU-l-BmOhcswsGaqg4=m22-dv"
info_url = "https://lh3.googleusercontent.com/notebooklm/AKXwDQFciM3cajfC-c9rd_dEkhgFyaj6XAOQcqakQJJCvk5mgMaSlrHK4pvcJ_1svXHy4KUHVz4HDo27VtLlkMtAqckyG90mW1TUVlAagBMOBMvmbBZbIHeJi6rEgR167NTapzihNHymc_4-SrXVEodoxJ382O8fMnY=w2048-d-h2048-mp2"

auth_path = os.path.expanduser('~/.notebooklm-mcp/auth.json')
with open(auth_path) as f:
    auth = json.load(f)
cookies_str = '; '.join([f"{k}={v}" for k, v in auth['cookies'].items()])

downloader_path = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebooklm_asset_downloader.py"

print("[*] Scaricando Video...")
v_res = subprocess.run([
    "python3", downloader_path,
    "--url", video_url,
    "--output", "/Users/marcolemoglie_1_2/Downloads/Poveri_in_Pensione_raw.mp4",
    "--cookies", cookies_str
])

print("\n[*] Scaricando Infografica...")
i_res = subprocess.run([
    "python3", downloader_path,
    "--url", info_url,
    "--output", "/Users/marcolemoglie_1_2/Downloads/infografica_raw.png",
    "--cookies", cookies_str
])

if v_res.returncode == 0 and i_res.returncode == 0:
    print("\n[SUCCESS] Entrambi gli asset sono stati scaricati in ~/Downloads/")
else:
    print("\n[ERROR] Uno o più download sono falliti.")

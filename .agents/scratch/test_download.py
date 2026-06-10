import requests
import json
import os

auth_path = os.path.expanduser('~/.notebooklm-mcp/auth.json')
with open(auth_path) as f:
    auth = json.load(f)

cookies = auth['cookies']
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Referer': 'https://notebooklm.google.com/',
}

url = "https://lh3.googleusercontent.com/notebooklm/AKXwDQFJLgeRFxzDj8QwjHfv_AOa4S4r1wPw-B0A_QzsP797mWLMwBY0Ac7ipanKO1sIwIZexDpXvDpVRKgc4uYWwAVqnOCi_aW9OUlXlR4HiK6FNlKWmJTOHDvdgZr4UHMpongxHyAG9RMX9jU-l-BmOhcswsGaqg4=m22-dv"
r = requests.get(url, cookies=cookies, headers=headers, stream=True, allow_redirects=True)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type')}")

if 'video' in r.headers.get('Content-Type', '').lower():
    with open('/tmp/test_video.mp4', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024):
            f.write(chunk)
    print(f"Success! Size: {os.path.getsize('/tmp/test_video.mp4')}")
else:
    print("Failed to get video.")
    print(r.text[:500])

import requests
import sys

cookies_file = '/Users/marcolemoglie_1_2/Desktop/canale/cookies.txt'
with open(cookies_file, 'r') as f:
    cookie_str = f.read().strip()

headers = {
    'Cookie': cookie_str,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

url = "https://lh3.googleusercontent.com/notebooklm/AKXwDQFf-iVkId494XBvJA5uVmA0hGptetklKCTDXrADvYIILVGfB0mhOf9OuNspLn1MCCzhR44bpvIRavjRwGzoFyWeCMZax0Eok39S6DNGfvtykpj1awml0axiAE2hLv-SGUg-LXbRRjWpDTUf6_AZxkFAa46_sJM=w2048-d-h2048-mp2"

print(f"[*] Testing URL: {url}")
try:
    response = requests.get(url, headers=headers, allow_redirects=True, stream=True)
    print(f"[*] Final URL: {response.url}")
    print(f"[*] Status Code: {response.status_code}")
    print(f"[*] Content-Type: {response.headers.get('Content-Type')}")
    
    if 'text/html' in response.headers.get('Content-Type', ''):
        print("[!] Still getting HTML. Checking for Login text...")
        chunk = next(response.iter_content(chunk_size=1024)).decode('utf-8', errors='ignore')
        if 'ServiceLogin' in chunk or 'Sign in' in chunk:
            print("[!] AUTH FAILED: Redirected to Login.")
        else:
            print(f"[?] HTML content preview: {chunk[:200]}")
    else:
        print("[+] SUCCESS! Binary content detected.")
except Exception as e:
    print(f"[!] Exception: {e}")

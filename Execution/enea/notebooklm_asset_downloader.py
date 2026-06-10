import requests
import sys
import os
import argparse

def download_asset(url, output_path, cookies_str):
    """
    Downloads a NotebookLM asset (Video or Infographic) using session cookies.
    """
    # Filter cookies to avoid bloated headers that cause 400 Bad Request
    # Only keep essential session cookies if possible, but for now we use the string
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": "https://notebooklm.google.com/",
        "Cookie": cookies_str,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site"
    }

    print(f"[*] Avvio download di: {url}")
    print(f"[*] Destinazione: {output_path}")

    try:
        with requests.get(url, headers=headers, stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            content_type = r.headers.get('Content-Type', '')
            print(f"[*] Content-Type rilevato: {content_type}")
            
            if 'text/html' in content_type:
                print("[!] ERRORE: L'URL ha restituito un documento HTML invece di un file binario.")
                print("[!] Suggerimento: L'URL o i Cookie potrebbero essere scaduti. Ri-estrarli dal Network Log.")
                sys.exit(1)

            with open(output_path, 'wb') as f:
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            done = int(50 * downloaded / total_size)
                            sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} bytes")
                            sys.stdout.flush()
        
        print(f"\n[+] Download completato con successo: {output_path}")
        print(f"[+] Dimensione finale: {os.path.getsize(output_path)} bytes")
        
    except Exception as e:
        print(f"\n[!] ERRORE critico durante il download: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NotebookLM Asset Downloader Blindato")
    parser.add_argument("--url", required=True, help="URL diretto (da Network Log)")
    parser.add_argument("--output", required=True, help="Percorso locale")
    parser.add_argument("--cookies", required=True, help="Cookie Header completo")

    args = parser.parse_args()
    download_asset(args.url, args.output, args.cookies)

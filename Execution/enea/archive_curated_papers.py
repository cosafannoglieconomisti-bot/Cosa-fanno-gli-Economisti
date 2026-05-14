import json
import os
import subprocess
import time
import requests

# Config
JSON_INPUT = "/tmp/papers_to_download_60.json"
BASE_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Papers/Da fare/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def clean_title(title):
    t = title.split("*")[0].strip()
    return "".join([c if c.isalnum() or c in " _-" else "_" for c in t]).replace("  ", " ").replace(" ", "_").strip("_")

def get_pdf_url(journal, doi):
    if not doi or doi == "NOT_FOUND":
        return None
    
    # DOI might be a full URL, we need only the path part
    doi_path = doi.replace("https://doi.org/", "").strip()
    
    if journal == "American_Economic_Review":
        # pattern: https://www.aeaweb.org/articles/pdf/doi/10.1257/aer.20191234
        return f"https://www.aeaweb.org/articles/pdf/doi/{doi_path}"
    
    elif journal == "Journal_of_Political_Economy":
        # pattern: https://www.journals.uchicago.edu/doi/pdf/10.1086/712431
        return f"https://www.journals.uchicago.edu/doi/pdf/{doi_path}"
    
    elif journal == "Quarterly_Journal_of_Economics":
        # These are tricky, usually need following the DOI to find the PDF ID
        return f"https://doi.org/{doi_path}" # Fallback to DOI redirect
    
    elif journal == "Review_of_Economic_Studies":
        return f"https://doi.org/{doi_path}" # Fallback
    
    elif journal == "Econometrica":
        # Wiley pattern: https://onlinelibrary.wiley.com/doi/pdfdirect/10.3982/ECTA12345
        return f"https://onlinelibrary.wiley.com/doi/pdfdirect/{doi_path}"
    
    return f"https://doi.org/{doi_path}"

def main():
    if not os.path.exists(JSON_INPUT):
        print(f"Error: {JSON_INPUT} not exists.")
        return

    with open(JSON_INPUT, "r") as f:
        papers = json.load(f)

    report = []
    
    for p in papers:
        title = p["title"]
        category = p["category"]
        journal = p["journal"]
        year = p["year"]
        doi = p["doi"]
        
        target_folder = os.path.join(BASE_DIR, category)
        pdf_name = f"{journal}_{year}_{clean_title(title)[:80]}.pdf"
        target_path = os.path.join(target_folder, pdf_name)
        
        if os.path.exists(target_path):
            print(f"[SKIP] Already exists: {pdf_name}")
            report.append({"title": title, "status": "exists"})
            continue
            
        url = get_pdf_url(journal, doi)
        if not url:
            print(f"[ERROR] No URL/DOI for: {title}")
            report.append({"title": title, "status": "no_doi"})
            continue
            
        print(f"[START] Downloading {title} from {url}")
        
        # Sequentially try to download
        try:
            # We use curl because it's better for redirects and cookie handling in local env
            # -L follows redirects
            # -A sets user agent
            # -k allows insecure (sometimes needed for academic proxies)
            cmd = ["curl", "-L", "-A", USER_AGENT, "-o", target_path, url]
            
            # For journals like QJE/REStud, we might need to be smart about the URL
            # but for now we try the DOI redirect directly.
            
            subprocess.run(cmd, check=True, timeout=30, capture_output=True)
            
            # Verify it's a PDF
            if os.path.exists(target_path) and os.path.getsize(target_path) > 5000:
                # Basic check: content starts with %PDF
                with open(target_path, "rb") as bf:
                    head = bf.read(4)
                if head == b"%PDF":
                    print(f"[SUCCESS] Downloaded: {pdf_name}")
                    report.append({"title": title, "status": "success", "file": pdf_name})
                else:
                    print(f"[FAIL] Not a PDF (likely paywall/redirect): {pdf_name}")
                    os.remove(target_path)
                    report.append({"title": title, "status": "not_a_pdf"})
            else:
                print(f"[FAIL] Download failed or file too small: {pdf_name}")
                if os.path.exists(target_path): os.remove(target_path)
                report.append({"title": title, "status": "fail_size"})
                
        except Exception as e:
            print(f"[ERROR] Execption for {title}: {str(e)}")
            report.append({"title": title, "status": f"error: {str(e)}"})
            
        # Small delay to avoid aggressive rate limiting
        time.sleep(1)

    # Save final report
    with open("/tmp/download_report.json", "w") as rf:
        json.dump(report, rf, indent=2)
    
    print("\n" + "="*20)
    print("DOWNLOAD TASK COMPLETE")
    success_count = len([r for r in report if r["status"] == "success"])
    print(f"Total Success: {success_count}/{len(papers)}")

if __name__ == "__main__":
    main()

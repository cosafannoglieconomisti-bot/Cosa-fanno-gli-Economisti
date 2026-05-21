import subprocess
import json
import concurrent.futures

NLM_PATH = "/Library/Frameworks/Python.framework/Versions/3.13/bin/nlm"

def get_notebooks():
    result = subprocess.run([NLM_PATH, "list", "notebooks", "--json"], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_artifacts(notebook_id):
    result = subprocess.run([NLM_PATH, "list", "artifacts", notebook_id, "--json"], capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return []

def main():
    notebooks = get_notebooks()
    print(f"Found {len(notebooks)} notebooks. Scanning for video/infographic...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_nb = {executor.submit(get_artifacts, nb['id']): nb for nb in notebooks}
        for future in concurrent.futures.as_completed(future_to_nb):
            nb = future_to_nb[future]
            artifacts = future.result()
            for art in artifacts:
                if art['type'] in ['video', 'infographic']:
                    print(f"MATCH FOUND!")
                    print(f"Notebook: {nb['title']} ({nb['id']})")
                    print(f"Artifact: {art['type']} ({art['id']}) - Status: {art['status']}")
                    print("-" * 20)

if __name__ == "__main__":
    main()

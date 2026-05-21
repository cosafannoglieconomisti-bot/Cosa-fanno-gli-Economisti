import subprocess
import json
import re

def run_cmd(args):
    try:
        res = subprocess.check_output(args, stderr=subprocess.STDOUT).decode()
        return res
    except:
        return None

def main():
    nlm_path = "/Library/Frameworks/Python.framework/Versions/3.13/bin/nlm"
    res = subprocess.check_output([nlm_path, "list", "notebooks"]).decode()
    
    # Extract IDs using regex
    ids = re.findall(r"([a-f0-9-]{36})", res)
    
    for nb_id in ids:
        print(f"Checking {nb_id}...")
        try:
            status = subprocess.check_output([nlm_path, "status", "artifacts", nb_id]).decode()
            if "Artifact ID:" in status:
                print(f"  FOUND ARTIFACTS in {nb_id}:")
                print(status)
        except:
            pass

if __name__ == "__main__":
    main()

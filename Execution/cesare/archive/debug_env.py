from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[3]

import os

def load_env_manual(path):
    with open(path, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env_manual(str(REPO_ROOT / '.env'))
print("Chiavi trovate in .env:")
for k in os.environ:
    if "TELEGRAM" in k or "ID" in k:
        print(f"-> {k}")

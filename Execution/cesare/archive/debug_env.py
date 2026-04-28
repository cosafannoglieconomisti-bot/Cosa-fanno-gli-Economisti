import os

def load_env_manual(path):
    with open(path, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env_manual("/Users/marcolemoglie_1_2/Desktop/canale/.env")
print("Chiavi trovate in .env:")
for k in os.environ:
    if "TELEGRAM" in k or "ID" in k:
        print(f"-> {k}")

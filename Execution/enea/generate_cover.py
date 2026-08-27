from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import os
import shutil
import sys

ASSETS_DIR = str(REPO_ROOT / 'Temp' / 'assets')
OVERRIDE_PATH = os.path.join(ASSETS_DIR, "override_cover.png")

def generate_cover(title, output_path="/tmp/active_cover.png"):
    if os.path.exists(OVERRIDE_PATH):
        shutil.copy(OVERRIDE_PATH, output_path)
        print(f"✅ Copertina copiata da override locale: {output_path}")
        return output_path
    raise FileNotFoundError(
        f"Copertina override non trovata: {OVERRIDE_PATH}. "
        f"Genera o salva manualmente una cover approvata con titolo '{title}' in quel path."
    )

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "TEST TITOLO"
    o = sys.argv[2] if len(sys.argv) > 2 else "/tmp/active_cover.png"
    generate_cover(t, o)

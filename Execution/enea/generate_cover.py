from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import os
import shutil
import sys

ASSETS_DIR = REPO_ROOT / "Temp" / "assets"
OVERRIDE_PATH = ASSETS_DIR / "override_cover.png"


def generate_cover(title, output_path="/tmp/active_cover.png"):
    """Copia la copertina approvata generata in Codex/GPT.

    Il motore immagine è quello interno di GPT/Codex, non Imagen/Gemini.
    Salva l'asset approvato in Temp/assets/override_cover.png prima di
    lanciare ./workflow copertina o ./workflow paper.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if OVERRIDE_PATH.exists():
        shutil.copy(OVERRIDE_PATH, output_path)
        print(f"✅ Copertina copiata da override locale: {output_path}")
        return output_path

    raise FileNotFoundError(
        f"Copertina non trovata in {OVERRIDE_PATH}. "
        f"Genera la cover con GPT/Codex, salvala lì e riprova. Titolo: '{title}'"
    )


if __name__ == "__main__":
    cover_title = sys.argv[1] if len(sys.argv) > 1 else "TEST TITOLO"
    cover_output = sys.argv[2] if len(sys.argv) > 2 else "/tmp/active_cover.png"
    generate_cover(cover_title, cover_output)

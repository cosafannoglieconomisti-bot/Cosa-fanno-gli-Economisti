from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import os

from translate_metadata import translate_metadata


PROJECTS = [
    "Dalle_Guerre_ai_Capolavori",
    "Regolarizzare_gli_immigrati_riduce_il_crimine",
    "Il_Talento_Non_Ha_Genere",
    "Il_Pallone_Unisce_le_Nazioni",
]


if __name__ == "__main__":
    base_dir = str(REPO_ROOT / 'Cleaned')
    for project in PROJECTS:
        it_md = os.path.join(base_dir, project, "video_metadata.md")
        intl_dir = os.path.join(base_dir, project, "international")
        if os.path.exists(it_md):
            translate_metadata(it_md, intl_dir, ["en", "es", "fr", "de"])

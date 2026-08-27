from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import os

from translate_metadata import translate_metadata


def fix_localization(project_folder):
    print(f"--- Auditing {project_folder} ---")
    it_metadata_path = os.path.join(project_folder, "video_metadata.md")
    if not os.path.exists(it_metadata_path):
        print(f"Error: video_metadata.md not found in {project_folder}")
        return

    intl_dir = os.path.join(project_folder, "international")
    os.makedirs(intl_dir, exist_ok=True)

    it_dir = os.path.join(intl_dir, "it")
    os.makedirs(it_dir, exist_ok=True)
    it_md_target = os.path.join(it_dir, "metadata_it.md")
    if not os.path.exists(it_md_target):
        with open(it_metadata_path, "r", encoding="utf-8") as src, open(it_md_target, "w", encoding="utf-8") as dst:
            dst.write(src.read())
        print(f"✅ Created metadata_it.md in {it_dir}")

    translate_metadata(it_metadata_path, intl_dir, ["en", "es", "fr", "de"])


if __name__ == "__main__":
    projects = [
        str(REPO_ROOT / 'Cleaned' / 'Il_Talento_Non_Ha_Genere'),
        str(REPO_ROOT / 'Cleaned' / 'Perche_scacciare_la_Mafia_paga'),
        str(REPO_ROOT / 'Cleaned' / 'La_Chiesa_frena_l_integrazione'),
    ]
    for project in projects:
        fix_localization(project)

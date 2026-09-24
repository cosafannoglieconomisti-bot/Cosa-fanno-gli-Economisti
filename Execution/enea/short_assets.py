#!/usr/bin/env python3
"""Utilità condivise per NotebookLM Short / YouTube Shorts / Instagram Reel.

Convenzioni nomi (TEST: 1 short; estensibile a N):
  Downloads / Cleaned:
    {clean_title}_short1_raw.mp4
    {clean_title}_short1_cleaned.mp4
    {clean_title}_short2_raw.mp4   # futuro
  Asset testuali short:
    Cleaned/[Titolo]/shorts/international/

Tracking (nested sotto la riga long-form, NON top-level):
  shorts: [{id, youtube_url, angle, status, ig_reel_url}]
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
DOWNLOADS = HOME / "Downloads"
CLEANED_DIR = REPO_ROOT / "Cleaned"
TRACKING_FILE = CLEANED_DIR / "video_tracking.json"
VENV_NLM = REPO_ROOT / ".venv" / "bin" / "nlm"

DEFAULT_ANGLE = "1"
SHORT_RAW_RE = re.compile(r"_short(\d+)_raw\.mp4$", re.IGNORECASE)
SHORT_CLEANED_RE = re.compile(r"_short(\d+)_cleaned\.mp4$", re.IGNORECASE)


def log(msg: str) -> None:
    print(f"[short] {msg}")


def nlm_bin() -> str:
    """Preferisci nlm del venv repo (>=0.11.7 con --format short)."""
    if VENV_NLM.exists():
        return str(VENV_NLM)
    found = shutil.which("nlm")
    if not found:
        raise FileNotFoundError("nlm non trovato (installa notebooklm-mcp-cli>=0.11.7 nel .venv)")
    return found


def normalize_index(angle: str | int | None) -> int:
    if angle is None or angle == "" or angle == "default":
        return 1
    if isinstance(angle, int):
        return max(1, angle)
    text = str(angle).strip().lower()
    if text.isdigit():
        return max(1, int(text))
    match = re.search(r"(\d+)", text)
    return max(1, int(match.group(1))) if match else 1


def short_raw_name(clean_title: str, angle: str | int | None = None) -> str:
    idx = normalize_index(angle)
    return f"{clean_title}_short{idx}_raw.mp4"


def short_cleaned_name(clean_title: str, angle: str | int | None = None) -> str:
    idx = normalize_index(angle)
    return f"{clean_title}_short{idx}_cleaned.mp4"


def is_short_raw_filename(name: str) -> bool:
    return bool(SHORT_RAW_RE.search(name))


def is_short_cleaned_filename(name: str) -> bool:
    return bool(SHORT_CLEANED_RE.search(name))


def parse_short_index_from_filename(name: str) -> int:
    match = SHORT_RAW_RE.search(name) or SHORT_CLEANED_RE.search(name)
    return int(match.group(1)) if match else 1


def find_short_raw_in_downloads(
    clean_title: str | None = None,
    angle: str | int | None = None,
    max_age_hours: float = 72.0,
) -> Path | None:
    """Cerca {title}_shortN_raw.mp4 in Downloads."""
    now = datetime.now().timestamp()
    max_age = max_age_hours * 3600
    idx = normalize_index(angle)

    if clean_title:
        preferred = DOWNLOADS / short_raw_name(clean_title, idx)
        if preferred.exists():
            return preferred

    candidates: list[Path] = []
    for path in DOWNLOADS.glob("*_short*_raw.mp4"):
        if now - path.stat().st_mtime > max_age:
            continue
        if not is_short_raw_filename(path.name):
            continue
        candidates.append(path)

    if clean_title:
        titled = [p for p in candidates if p.name.startswith(f"{clean_title}_short")]
        if titled:
            # Prefer matching index
            for p in titled:
                if parse_short_index_from_filename(p.name) == idx:
                    return p
            return sorted(titled, key=lambda p: p.stat().st_mtime, reverse=True)[0]

    if candidates:
        return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return None


def find_short_cleaned(folder: Path, angle: str | int | None = None) -> Path | None:
    clean_title = folder.name
    preferred = folder / short_cleaned_name(clean_title, angle)
    if preferred.exists():
        return preferred
    # Also check shorts/ subfolder
    alt = folder / "shorts" / short_cleaned_name(clean_title, angle)
    if alt.exists():
        return alt
    matches = sorted(folder.glob("*_short*_cleaned.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def probe_video_size(path: Path) -> tuple[int, int, float] | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    cmd = [
        ffprobe,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "format=duration:stream=width,height",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
        if len(lines) < 3:
            return None
        return int(lines[0]), int(lines[1]), float(lines[2])
    except Exception:
        return None


def is_vertical(path: Path) -> bool:
    probed = probe_video_size(path)
    if not probed:
        return True
    width, height, _ = probed
    return height > width


def delogo_box_for_resolution(width: int, height: int) -> tuple[int, int, int, int]:
    """(x, y, w, h) box cover SOLIDO per badge NotebookLM — flush bottom-right, tight.

    Usato con drawbox fill (colore campionato), NON delogo soft (macchie).
    Misure tipiche (test Ambiente_o_consenso):
    - 720x1280: testo circa x=508..694 y=1237..1270
    - 1280x720: testo circa x=1000..1279 y=701..719
    """
    if height > width:  # portrait / Short
        box_w = max(175, int(width * 0.27))
        box_h = max(34, int(height * 0.028))
        margin_x = max(6, int(width * 0.01))
        margin_y = max(6, int(height * 0.005))
    else:  # landscape / long
        box_w = max(250, int(width * 0.225))
        box_h = max(22, int(height * 0.032))
        margin_x = max(2, int(width * 0.002))
        margin_y = max(2, int(height * 0.003))
    x = max(0, width - box_w - margin_x)
    y = max(0, height - box_h - margin_y)
    return x, y, box_w, box_h


def build_short_description(
    long_id: str,
    hook: str | None = None,
    extra_hashtags: str | None = None,
) -> str:
    hook_line = (hook or "Il paper in 60 secondi.").strip()
    tags = extra_hashtags or "#shorts"  # no generici canale/journal; tag specifici dal metadata long
    return (
        f"{hook_line}\n\n"
        f"Video completo qui: https://youtu.be/{long_id}\n\n"
        f"{tags}"
    ).strip()


def build_short_title(base_title: str, angle: str | int | None = None) -> str:
    title = base_title.strip()
    if "#shorts" not in title.lower():
        title = f"{title} #shorts"
    idx = normalize_index(angle)
    if idx > 1:
        title = f"{title} ({idx})"
    return title[:100]


def ensure_shorts_dirs(target_dir: Path) -> dict[str, Path]:
    shorts_dir = target_dir / "shorts"
    intl = shorts_dir / "international"
    shorts_dir.mkdir(parents=True, exist_ok=True)
    intl.mkdir(parents=True, exist_ok=True)
    return {"shorts": shorts_dir, "international": intl}


def acquire_short_fallback_message(clean_title: str, angle: str | int | None = None) -> str:
    name = short_raw_name(clean_title, angle)
    return (
        "FALLBACK SHORT (UI NotebookLM):\n"
        "1. Apri il notebook su https://notebooklm.google.com/\n"
        "2. In Studio genera Video Overview con formato Short (verticale).\n"
        f"3. Scarica in ~/Downloads e rinomina esattamente: {name}\n"
        f"4. Poi: ./workflow pulizia --video {name}\n"
        "CLI preferita (nlm>=0.11.7): nlm create video <nb> --format short -y"
    )


def copy_short_raw_to_project(
    src: Path, target_dir: Path, clean_title: str, angle: str | int | None = None
) -> Path:
    dirs = ensure_shorts_dirs(target_dir)
    dest = dirs["shorts"] / short_raw_name(clean_title, angle)
    shutil.copy2(src, dest)
    root_copy = target_dir / short_raw_name(clean_title, angle)
    if src.resolve() != root_copy.resolve():
        shutil.copy2(src, root_copy)
    return dest


def upsert_short_tracking(
    project_name: str,
    *,
    short_id: str = "",
    youtube_url: str = "",
    angle: str | int | None = None,
    status: str = "Da fare",
    ig_reel_url: str = "Da fare",
    local_path: str = "",
) -> dict:
    """Aggiorna shorts[] nested sotto la riga long-form (no top-level Short rows)."""
    from tracking_manager import load_data, save_data, update_entry

    update_entry(project_name)
    data = load_data()
    entry = data.setdefault(project_name, {})
    shorts = entry.get("shorts")
    if not isinstance(shorts, list):
        shorts = []

    angle_key = str(normalize_index(angle))
    found = None
    for item in shorts:
        if isinstance(item, dict) and str(item.get("angle", "1")) == angle_key:
            found = item
            break
    if found is None:
        found = {
            "id": "",
            "youtube_url": "",
            "angle": angle_key,
            "status": "Da fare",
            "ig_reel_url": "Da fare",
        }
        shorts.append(found)

    if short_id:
        found["id"] = short_id
    if youtube_url:
        found["youtube_url"] = youtube_url
    elif short_id:
        found["youtube_url"] = f"https://youtube.com/shorts/{short_id}"
    if status:
        found["status"] = status
    if ig_reel_url:
        found["ig_reel_url"] = ig_reel_url
    if local_path:
        found["local_path"] = local_path
    found["updated"] = datetime.now().isoformat()

    entry["shorts"] = shorts
    entry["last_updated"] = datetime.now().isoformat()
    data[project_name] = entry
    save_data(dict(sorted(data.items())))
    log(f"Tracking shorts aggiornato: {project_name} angle={angle_key}")
    return found


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Utility short assets")
    parser.add_argument("--find-raw", action="store_true")
    parser.add_argument("--clean-title")
    parser.add_argument("--angle", default="1")
    parser.add_argument("--nlm-bin", action="store_true")
    args = parser.parse_args()
    if args.nlm_bin:
        print(nlm_bin())
    elif args.find_raw:
        found = find_short_raw_in_downloads(args.clean_title, args.angle)
        print(found or "")

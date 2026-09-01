"""Persistenza pipeline: file per lavorazione + puntatore active."""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = REPO_ROOT / "Temp" / "enea" / "pipelines"
ACTIVE_PIPE = REPO_ROOT / "Temp" / "enea" / "active_pipeline.json"


def _pipeline_id(data: dict) -> str:
    return data.get("clean_title") or "active"


def write_pipeline(data: dict) -> Path:
    PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_PIPE.parent.mkdir(parents=True, exist_ok=True)
    pipeline_id = _pipeline_id(data)
    archive_path = PIPELINE_DIR / f"{pipeline_id}.json"
    payload = dict(data)
    payload["pipeline_id"] = pipeline_id
    archive_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    ACTIVE_PIPE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return archive_path


def read_pipeline(path: Path | None = None) -> dict:
    target = path or ACTIVE_PIPE
    if not target.exists():
        raise FileNotFoundError(f"Pipeline non trovata: {target}")
    return json.loads(target.read_text(encoding="utf-8"))


def list_pipelines() -> list[Path]:
    if not PIPELINE_DIR.exists():
        return []
    return sorted(PIPELINE_DIR.glob("*.json"))

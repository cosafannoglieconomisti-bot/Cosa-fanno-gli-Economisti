"""Portable local paths for the canale repo.

GitHub copies must never contain a real macOS username. Runtime code
resolves the repo from this file's location and the home directory from
Path.home(). Placeholders of the form /Users/<USER>/... are expanded
when reading persisted JSON.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
DOWNLOADS = HOME / "Downloads"
USER_PLACEHOLDER = "<USER>"
PLACEHOLDER_PREFIX = f"/Users/{USER_PLACEHOLDER}"

# Real macOS account names, not placeholders like /Users/<USER>/.
_HOME_USER_RE = re.compile(r"/Users/(?!Shared(?:/|$))([A-Za-z0-9._-]+)")


def redact_local_paths(text: str) -> str:
    """Replace real /Users/<account> prefixes with /Users/<USER>."""
    return _HOME_USER_RE.sub(PLACEHOLDER_PREFIX, text)


def expand_local_paths(text: str) -> str:
    """Expand /Users/<USER> to the current machine home."""
    return text.replace(PLACEHOLDER_PREFIX, HOME.as_posix())


def looks_like_local_user_path(text: str) -> bool:
    return bool(_HOME_USER_RE.search(text))

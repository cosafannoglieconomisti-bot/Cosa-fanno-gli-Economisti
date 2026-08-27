#!/usr/bin/env python3
"""Redact real macOS account paths before they reach GitHub.

Used by:
- mercurio backup staging
- pre-push hook
- CI check
- one-shot working-tree rewrite (--rewrite)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

MERCURIO_DIR = Path(__file__).resolve().parent
EXECUTION_DIR = MERCURIO_DIR.parent
REPO_ROOT = EXECUTION_DIR.parent
sys.path.insert(0, str(EXECUTION_DIR))

from canale_paths import (  # noqa: E402
    PLACEHOLDER_PREFIX,
    USER_PLACEHOLDER,
    looks_like_local_user_path,
    redact_local_paths,
)

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".sh",
    ".yml",
    ".yaml",
    ".toml",
    ".cfg",
    ".ini",
    ".csv",
    ".srt",
    ".vtt",
    ".html",
    ".xml",
    ".toml",
}
TEXT_NAMES = {"workflow", "Dockerfile", ".gitattributes", ".gitignore"}
SKIP_DIR_PARTS = {".git", ".venv", "node_modules", "Temp", ".playwright-mcp"}


def _is_text_target(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    return path.name in TEXT_NAMES


def _iter_git_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    files = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        path = REPO_ROOT / raw.decode("utf-8")
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        files.append(path)
    return files


def sanitize_file(path: Path) -> bool:
    if not _is_text_target(path):
        return False
    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    updated = redact_local_paths(original)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def scan_leaks(paths: list[Path] | None = None) -> list[tuple[Path, int, str]]:
    hits = []
    for path in paths or _iter_git_files():
        if not _is_text_target(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if looks_like_local_user_path(line):
                hits.append((path, i, line.strip()[:200]))
    return hits


def _depth_to_repo(path: Path) -> int:
    rel = path.resolve().relative_to(REPO_ROOT)
    return len(rel.parts) - 1


def _ensure_python_helpers(source: str, depth: int) -> str:
    uses_repo = "REPO_ROOT" in source
    uses_home = re.search(r"\bHOME\b", source) is not None
    has_root_assign = "REPO_ROOT = Path(__file__)" in source
    has_home_assign = "HOME = Path.home()" in source
    needs_root = uses_repo and not has_root_assign
    needs_home = uses_home and not has_home_assign
    needs_path_import = (
        (needs_root or needs_home)
        and "from pathlib import Path" not in source
        and "import pathlib" not in source
    )
    if not (needs_root or needs_home or needs_path_import):
        return source

    lines = source.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    if insert_at < len(lines) and "coding" in lines[insert_at] and lines[insert_at].lstrip().startswith("#"):
        insert_at += 1
    if insert_at < len(lines) and lines[insert_at].startswith('"""'):
        for j in range(insert_at + 1, len(lines)):
            if '"""' in lines[j]:
                insert_at = j + 1
                break
    elif insert_at < len(lines) and lines[insert_at].startswith("'''"):
        for j in range(insert_at + 1, len(lines)):
            if "'''" in lines[j]:
                insert_at = j + 1
                break

    for i, line in enumerate(lines):
        if line.startswith("from pathlib import Path") or line.startswith("import pathlib"):
            insert_at = i + 1
            needs_path_import = False
            break

    block = []
    if needs_path_import:
        block.append("from pathlib import Path\n")
    if needs_root:
        block.append(f"REPO_ROOT = Path(__file__).resolve().parents[{depth}]\n")
    if needs_home:
        block.append("HOME = Path.home()\n")
    if block:
        if insert_at < len(lines) and lines[insert_at].strip():
            block.append("\n")
        lines[insert_at:insert_at] = block
    return "".join(lines)


def _to_path_expr(root_name: str, rel: str) -> str:
    if not rel:
        return f"str({root_name})"
    parts = " / ".join(repr(part) for part in rel.split("/"))
    return f"str({root_name} / {parts})"


def _replace_quoted_prefix(source: str, prefix: str, root_name: str) -> str:
    pattern = re.compile(r'(["\'])' + re.escape(prefix) + r'(/[^"\']*)?\1')

    def repl(match: re.Match[str]) -> str:
        rel = (match.group(2) or "").lstrip("/")
        return _to_path_expr(root_name, rel)

    return pattern.sub(repl, source)


def _rewrite_python_source(source: str, path: Path) -> str:
    repo_posix = REPO_ROOT.as_posix()
    home_posix = Path.home().as_posix()
    depth = _depth_to_repo(path)

    source = source.replace(f'Path("{repo_posix}")', "REPO_ROOT")
    source = source.replace(f"Path('{repo_posix}')", "REPO_ROOT")
    source = source.replace(f'Path("{home_posix}/Downloads")', 'HOME / "Downloads"')
    source = source.replace(f"Path('{home_posix}/Downloads')", "HOME / 'Downloads'")
    source = source.replace(f'Path("{home_posix}")', "HOME")
    source = source.replace(f"Path('{home_posix}')", "HOME")
    source = _replace_quoted_prefix(source, repo_posix, "REPO_ROOT")
    source = _replace_quoted_prefix(source, home_posix, "HOME")
    source = _ensure_python_helpers(source, depth)
    source = redact_local_paths(source)
    return source


def rewrite_file(path: Path) -> bool:
    if path.resolve() == Path(__file__).resolve():
        original = path.read_text(encoding="utf-8")
        updated = redact_local_paths(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            return True
        return False
    if path.resolve() == (EXECUTION_DIR / "canale_paths.py").resolve():
        return False
    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    if path.suffix == ".py":
        updated = _rewrite_python_source(original, path)
    else:
        updated = redact_local_paths(original)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def rewrite_tree() -> list[Path]:
    changed = []
    for path in _iter_git_files():
        if not _is_text_target(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if not looks_like_local_user_path(text) and Path.home().as_posix() not in text:
            continue
        if rewrite_file(path):
            changed.append(path)
    return changed


def check_or_fail() -> int:
    hits = scan_leaks()
    if not hits:
        print("OK: nessun path /Users/<account> reale nei file tracciati.")
        return 0
    print("Trovati path macchina in chiaro:")
    for path, line, preview in hits:
        rel = path.relative_to(REPO_ROOT)
        print(f"  {rel}:{line}: {preview}")
    return 1


def install_pre_push_hook() -> Path:
    hook_src = REPO_ROOT / ".githooks" / "pre-push.sh"
    hook_dst = REPO_ROOT / ".git" / "hooks" / "pre-push"
    hook_dst.parent.mkdir(parents=True, exist_ok=True)
    hook_dst.write_text(hook_src.read_text(encoding="utf-8"), encoding="utf-8")
    hook_dst.chmod(hook_dst.stat().st_mode | 0o111)
    return hook_dst


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args == ["--check"]:
        return check_or_fail()
    if args == ["--rewrite"]:
        changed = rewrite_tree()
        print(f"Riscriviti {len(changed)} file.")
        for path in changed:
            print(f"  {path.relative_to(REPO_ROOT)}")
        install_pre_push_hook()
        return check_or_fail()
    if args == ["--install-hook"]:
        path = install_pre_push_hook()
        print(f"Hook installato: {path}")
        return 0
    if args[0] == "--sanitize-file" and len(args) == 2:
        path = Path(args[1])
        changed = sanitize_file(path)
        print("sanitized" if changed else "unchanged")
        return 0
    print("uso: sanitize_local_paths.py [--check|--rewrite|--install-hook|--sanitize-file PATH]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

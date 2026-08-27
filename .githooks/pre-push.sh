#!/bin/bash
# Block pushes that still contain real macOS account paths.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
if [ -f "$ROOT/Execution/mercurio/sanitize_local_paths.py" ]; then
  :
else
  ROOT="$(git rev-parse --show-toplevel)"
fi
PYTHON="$ROOT/.venv/bin/python3"
if [ ! -x "$PYTHON" ]; then
  PYTHON="python3"
fi
exec "$PYTHON" "$ROOT/Execution/mercurio/sanitize_local_paths.py" --check

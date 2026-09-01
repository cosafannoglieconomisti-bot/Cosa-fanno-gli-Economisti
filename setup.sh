#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
if [ ! -d ".venv" ]; then
  echo "Creazione virtualenv..."
  "$PYTHON" -m venv .venv
fi
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

mkdir -p "Papers/Da fare" "Temp/enea" "Temp/assets" "Temp/cesare" "Execution/credentials"

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Creato .env da .env.example — compila le chiavi prima di usare i workflow."
fi

if command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg: $(command -v ffmpeg)"
else
  echo "ATTENZIONE: ffmpeg non trovato. Installalo (es. brew install ffmpeg)."
fi

if command -v nlm >/dev/null 2>&1; then
  echo "nlm: $(nlm --version 2>/dev/null || echo presente)"
else
  echo "ATTENZIONE: nlm non trovato. Dopo setup: pip install notebooklm-mcp-cli && nlm login"
fi

echo "Setup completato. Verifica: ./workflow list"

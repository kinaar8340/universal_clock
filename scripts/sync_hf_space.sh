#!/usr/bin/env bash
# Copy the Python package into the HF Space bundle.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/space/universal_clock"

mkdir -p "$DEST"
rsync -av --delete \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  "$ROOT/universal_clock/" "$DEST/"

echo "Synced package → space/universal_clock/"
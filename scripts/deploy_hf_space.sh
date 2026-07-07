#!/usr/bin/env bash
# Sync bundle, commit to GitHub, and deploy to HF Space kinaar111/universal_clock.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MSG="${1:-feat(hf-space): Universal π Clock Gradio demo}"

echo "=== 1. Sync HF space bundle ==="
bash scripts/sync_hf_space.sh

echo "=== 2. Git commit (universal_clock) ==="
git add space/ scripts/sync_hf_space.sh scripts/deploy_hf_space.sh universal_clock/
git status --short
if git diff --cached --quiet; then
  echo "No staged changes"
  GH_SHA="$(git rev-parse HEAD)"
else
  git commit -m "$MSG"
  GH_SHA="$(git rev-parse HEAD)"
fi
echo "GitHub SHA: $GH_SHA"

echo "=== 3. Git push origin main ==="
git push origin main

echo "=== 4. Deploy to HF Space ==="
# Uses the active hf auth token (see README “HF deploy token”)
hf upload kinaar111/universal_clock space \
  --type space \
  --commit-message "$MSG" \
  --exclude ".git/*" \
  --exclude "__pycache__/*" \
  --exclude "*.pyc"

echo ""
echo "=== RESULTS ==="
echo "GITHUB_SHA=$GH_SHA"
echo "SPACE=https://huggingface.co/spaces/kinaar111/universal_clock"
echo "LIVE=https://kinaar111-universal-clock.hf.space"
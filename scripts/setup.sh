#!/bin/bash
# Installs whisper, yt-dlp, pytest-playwright and checks for ffmpeg.
# Safe to re-run.
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq ffmpeg
  else
    echo "ffmpeg not found: install it with your package manager (e.g. brew install ffmpeg)" >&2
    exit 1
  fi
fi

# CPU-only torch keeps the whisper install small when there's no GPU.
pip install --quiet --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

if [ "${PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD:-}" = "1" ]; then
  # Claude Code cloud sessions ship Chromium 1194 at $PLAYWRIGHT_BROWSERS_PATH and block
  # browser downloads, so pin the Playwright release built against that revision.
  pip install --quiet "playwright==1.56.0"
else
  python3 -m playwright install chromium
fi

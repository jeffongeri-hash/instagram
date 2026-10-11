#!/bin/bash
# Installs what the saved-reels-to-skill scripts need: ffmpeg, openai-whisper,
# yt-dlp and Playwright. Safe to re-run.
#
# Claude Code cloud sessions install into the system Python. Everywhere else
# (your Mac) packages go into ./.venv, because Homebrew's Python refuses
# system-wide pip installs; activate it with `source .venv/bin/activate`.
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    brew install ffmpeg
  elif command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq ffmpeg
  else
    echo "ffmpeg not found: install it with your package manager" >&2
    exit 1
  fi
fi

if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
  PY=python3
else
  [ -d .venv ] || python3 -m venv .venv
  PY=.venv/bin/python
fi

pip_args=(--quiet)
if [ "$(uname -s)" = "Linux" ]; then
  # CPU-only torch keeps the whisper install small when there's no GPU.
  pip_args+=(--extra-index-url https://download.pytorch.org/whl/cpu)
fi
"$PY" -m pip install "${pip_args[@]}" -r requirements.txt

if [ "${PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD:-}" = "1" ]; then
  # Claude Code cloud sessions ship Chromium 1194 at $PLAYWRIGHT_BROWSERS_PATH and block
  # browser downloads, so pin the Playwright release built against that revision.
  "$PY" -m pip install --quiet "playwright==1.56.0"
else
  "$PY" -m playwright install chromium
fi

if [ "$(uname -s)" = "Darwin" ] && [ ! -d "/Applications/Google Chrome.app" ]; then
  echo "Note: watch.py plays reels in Google Chrome. Install it: brew install --cask google-chrome" >&2
fi

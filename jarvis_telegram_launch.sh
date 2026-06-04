#!/bin/bash
# Wrapper that loads Jarvis's secrets and runs the Telegram bridge under its venv.
# Used by the macOS LaunchAgent so you can text Jarvis without a terminal open.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$HOME/.jarvis.env" ]; then
  set -a
  . "$HOME/.jarvis.env"
  set +a
fi

exec "$DIR/.venv/bin/python" "$DIR/jarvis_telegram.py"

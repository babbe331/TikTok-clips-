#!/bin/bash
# Wrapper that loads Jarvis's secrets and runs it under its own virtualenv.
# Used by the macOS LaunchAgent (and handy for starting Jarvis by hand).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load API keys from ~/.jarvis.env (LaunchAgents don't inherit your shell env).
if [ -f "$HOME/.jarvis.env" ]; then
  set -a
  . "$HOME/.jarvis.env"
  set +a
fi

exec "$DIR/.venv/bin/python" "$DIR/jarvis.py"

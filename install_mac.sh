#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Install Jarvis as an always-on background assistant on macOS.
#
# Run it once:   ./install_mac.sh
#
# It sets up a Python virtualenv, stores your API keys safely, triggers the
# microphone-permission prompt, and registers a LaunchAgent so Jarvis starts
# automatically every time you log in and is always listening for "Wake up Jarvis".
# ─────────────────────────────────────────────────────────────────────────────
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABEL="com.jarvis.assistant"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
ENVFILE="$HOME/.jarvis.env"

echo "🤖 Setting up Jarvis to auto-start on this Mac..."
echo ""

# 1. Python virtualenv + dependencies ----------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Install it (e.g. 'brew install python') and re-run."
  exit 1
fi
if [ ! -d "$DIR/.venv" ]; then
  echo "→ Creating virtual environment (.venv)..."
  python3 -m venv "$DIR/.venv"
fi
echo "→ Installing dependencies (this can take a minute)..."
"$DIR/.venv/bin/pip" install -q --upgrade pip
if ! "$DIR/.venv/bin/pip" install -q -r "$DIR/requirements-jarvis.txt"; then
  echo ""
  echo "⚠️  Dependency install hit a snag — usually the microphone library (PyAudio)"
  echo "    needs PortAudio. Run:  brew install portaudio   then re-run this script."
  exit 1
fi

# 2. Secrets file -------------------------------------------------------------
if [ ! -f "$ENVFILE" ]; then
  cat > "$ENVFILE" <<'EOF'
# Jarvis secrets — keep this file private.
export ANTHROPIC_API_KEY="sk-ant-REPLACE_ME"
export ELEVENLABS_API_KEY=""
# export ELEVENLABS_VOICE_ID=""   # optional: a specific ElevenLabs voice
EOF
  chmod 600 "$ENVFILE"
  echo ""
  echo "📝 Created $ENVFILE"
  echo "   I'll open it now — paste in your ANTHROPIC_API_KEY, save, then run this script again."
  open -e "$ENVFILE" 2>/dev/null || true
  exit 0
fi

# Verify the key is actually filled in.
# shellcheck disable=SC1090
. "$ENVFILE"
if [ -z "${ANTHROPIC_API_KEY:-}" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-REPLACE_ME" ]; then
  echo "📝 Add your real ANTHROPIC_API_KEY to $ENVFILE, then re-run this script."
  open -e "$ENVFILE" 2>/dev/null || true
  exit 1
fi

chmod +x "$DIR/jarvis_launch.sh"

# 3. One foreground run to trigger the macOS Microphone permission prompt ------
echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo "Starting Jarvis once so macOS can ask for Microphone permission."
echo "  • When the popup appears, click \"Allow\"."
echo "  • Then try saying:  \"Wake up Jarvis\""
echo "  • Press Ctrl-C when you're happy — the background service takes over."
echo "─────────────────────────────────────────────────────────────────────"
echo ""
( set -a; . "$ENVFILE"; set +a; "$DIR/.venv/bin/python" "$DIR/jarvis.py" ) || true

# 4. Write the LaunchAgent plist ----------------------------------------------
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$DIR/jarvis_launch.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$DIR/jarvis.log</string>
    <key>StandardErrorPath</key>
    <string>$DIR/jarvis.log</string>
</dict>
</plist>
EOF

# 5. (Re)load the agent -------------------------------------------------------
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo ""
echo "✅ Done! Jarvis now starts automatically every time you log in,"
echo "   and it's running in the background right now — say \"Wake up Jarvis\"."
echo ""
echo "Handy commands:"
echo "   Pause/stop it:   launchctl unload $PLIST"
echo "   Start it again:  launchctl load $PLIST"
echo "   See what it's doing:  tail -f $DIR/jarvis.log"
echo ""
echo "(Note: while the service is loaded, saying \"goodbye\" just sends it back to"
echo " standby — macOS relaunches it. To fully stop it, use the unload command above.)"

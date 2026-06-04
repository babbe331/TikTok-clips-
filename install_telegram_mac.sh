#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Install the Jarvis Telegram bridge as an always-on background service on macOS.
#
# Run it once:   ./install_telegram_mac.sh
#
# After this, you can text your Jarvis bot from your phone anytime your Mac is
# awake — no open terminal, no caffeinate. It also restarts itself at login.
# ─────────────────────────────────────────────────────────────────────────────
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABEL="com.jarvis.telegram"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
ENVFILE="$HOME/.jarvis.env"

echo "📱 Setting up the Jarvis Telegram bridge to run in the background..."
echo ""

# 1. Sanity checks ------------------------------------------------------------
if [ ! -x "$DIR/.venv/bin/python" ]; then
  echo "❌ No virtualenv found. Run ./install_mac.sh first to set up Jarvis."
  exit 1
fi
if [ ! -f "$ENVFILE" ]; then
  echo "❌ No ~/.jarvis.env found. Run ./install_mac.sh first."
  exit 1
fi

# shellcheck disable=SC1090
. "$ENVFILE"
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
  echo "❌ TELEGRAM_BOT_TOKEN is not set in ~/.jarvis.env."
  echo "   Create a bot with @BotFather, add the token, then re-run this."
  open -e "$ENVFILE" 2>/dev/null || true
  exit 1
fi
if [ -z "${TELEGRAM_ALLOWED_CHAT_ID:-}" ]; then
  echo "⚠️  TELEGRAM_ALLOWED_CHAT_ID is not set — anyone who finds your bot could"
  echo "    command it. Strongly recommend adding your chat ID first. Continuing anyway."
fi

chmod +x "$DIR/jarvis_telegram_launch.sh"

# 2. Write the LaunchAgent plist ----------------------------------------------
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
        <string>$DIR/jarvis_telegram_launch.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$DIR/jarvis_telegram.log</string>
    <key>StandardErrorPath</key>
    <string>$DIR/jarvis_telegram.log</string>
</dict>
</plist>
EOF

# 3. (Re)load it --------------------------------------------------------------
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo ""
echo "✅ Done! The Telegram bridge now runs in the background and starts at login."
echo "   Text your bot from your phone anytime your Mac is awake."
echo ""
echo "Handy commands:"
echo "   Stop it:        launchctl unload $PLIST"
echo "   Start it again: launchctl load $PLIST"
echo "   See its log:    tail -f $DIR/jarvis_telegram.log"
echo ""
echo "💡 Tip: so your Mac stays reachable, set it to not sleep while plugged in"
echo "   (System Settings → Battery → Options / Power Adapter), and keep the lid open."

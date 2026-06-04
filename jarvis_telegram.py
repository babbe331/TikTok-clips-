#!/usr/bin/env python3
"""
Jarvis Telegram bridge — text Jarvis from your phone.

Run this on your Mac and it listens for Telegram messages, runs them through the
same Jarvis brain + tools as the voice assistant (web search, open sites/apps,
run the TikTok pipeline, notes, etc.), and texts the answer back. Great for when
you're away from your computer but still want Jarvis to pull things up.

Setup (one time)
----------------
1. On your phone, open Telegram and message **@BotFather**:
   send  /newbot  and follow the prompts. It gives you a TOKEN like
   "123456:ABC-DEF...".
2. Put it in ~/.jarvis.env:
       export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
3. Run this script:  .venv/bin/python jarvis_telegram.py
4. In Telegram, open your new bot and send it "hi". It replies with your chat ID.
   Add that to ~/.jarvis.env so only YOU can command it:
       export TELEGRAM_ALLOWED_CHAT_ID="123456789"
5. Restart the script. Now text it anything.
"""

import os
import sys
import json
import time
import urllib.parse
import urllib.request

import jarvis  # reuse the same brain + tools as the voice assistant

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_CHAT_ID = os.environ.get("TELEGRAM_ALLOWED_CHAT_ID", "")
API = f"https://api.telegram.org/bot{TOKEN}"


def _api_get(method, params=None, timeout=40):
    url = f"{API}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.load(resp)


def send_message(chat_id, text):
    # Telegram caps messages at 4096 chars.
    text = text[:4000] if text else "(no reply)"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(f"{API}/sendMessage", data=data, method="POST")
    try:
        urllib.request.urlopen(req, timeout=20)
    except Exception as e:
        print(f"  (send failed: {e})")


def main():
    if not TOKEN:
        sys.exit("Set TELEGRAM_BOT_TOKEN in ~/.jarvis.env (see the top of this file).")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY in ~/.jarvis.env first.")

    brain = jarvis.Jarvis()
    print("Jarvis Telegram bridge online. Text your bot from your phone. (Ctrl-C to quit)")
    if not ALLOWED_CHAT_ID:
        print("⚠️  TELEGRAM_ALLOWED_CHAT_ID is not set — the bot will reply to anyone who")
        print("    messages it, and will tell each sender their chat ID. Lock it down soon.")

    offset = None
    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset
            resp = _api_get("getUpdates", params, timeout=40)
        except (KeyboardInterrupt, SystemExit):
            print("\nShutting down Telegram bridge.")
            return
        except Exception as e:
            print(f"  (poll error: {e})")
            time.sleep(3)
            continue

        for update in resp.get("result", []):
            offset = update["update_id"] + 1
            msg = update.get("message") or update.get("edited_message")
            if not msg:
                continue
            chat_id = str(msg["chat"]["id"])
            text = (msg.get("text") or "").strip()
            if not text:
                continue

            # Security: only the owner may command the computer.
            if ALLOWED_CHAT_ID and chat_id != str(ALLOWED_CHAT_ID):
                send_message(chat_id, "Sorry, this assistant is private.")
                print(f"  (ignored unauthorized chat {chat_id})")
                continue
            if not ALLOWED_CHAT_ID:
                send_message(
                    chat_id,
                    f"Your Telegram chat ID is {chat_id}. Add it as "
                    f"TELEGRAM_ALLOWED_CHAT_ID in ~/.jarvis.env (then restart me) so only "
                    f"you can give commands.",
                )

            print(f"[{chat_id}] {text}")
            try:
                reply = brain.respond(text)
            except Exception as e:
                reply = f"Sorry sir, something went wrong: {e}"
            send_message(chat_id, reply)


if __name__ == "__main__":
    main()

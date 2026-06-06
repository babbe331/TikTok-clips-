"""
env_setup.py — tiny, dependency-free .env loader + API-key validator.

The clip pipeline needs three free API keys. Without them, daily_runner.py used
to fail with a cryptic "HTTP Error 400". This makes the failure obvious and lets
you set keys once in a gitignored .env file instead of exporting them every time.

Usage (at the top of a script, before reading os.environ):

    from env_setup import load_env, require_keys
    load_env()                                   # loads .env into os.environ
    require_keys("TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET", "GOOGLE_API_KEY")
"""

from __future__ import annotations
import os, sys

PLACEHOLDERS = ("PASTE", "PASTE_YOUR", "YOUR_", "CHANGE_ME", "")


def load_env(path: str = ".env") -> int:
    """Load KEY=VALUE lines from .env into os.environ (without overwriting existing).
    Returns the number of keys loaded. Silently no-ops if the file is absent."""
    if not os.path.exists(path):
        return 0
    loaded = 0
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val
                loaded += 1
    return loaded


def _is_set(name: str) -> bool:
    v = os.environ.get(name, "")
    return bool(v) and not any(v.upper().startswith(p) for p in PLACEHOLDERS if p)


def require_keys(*names: str, hard: bool = True) -> bool:
    """Verify the named env vars are set to real values (not placeholders).
    Prints a clear, actionable message listing what's missing. Exits if hard."""
    missing = [n for n in names if not _is_set(n)]
    if not missing:
        return True
    print("\n" + "=" * 64)
    print("  ⚠️  MISSING API KEYS — the clip pipeline can't run yet")
    print("=" * 64)
    for n in missing:
        print(f"   ✗ {n}")
    print("\n  Get them (all free):")
    if any("TWITCH" in n for n in missing):
        print("   • Twitch ID/secret: https://dev.twitch.tv/console/apps")
    if any("GOOGLE" in n for n in missing):
        print("   • Google/Gemini key: https://aistudio.google.com/apikey")
    print("\n  Then either export them, or put them in a .env file:")
    print("     cp .env.example .env   # then edit .env with your keys")
    print("=" * 64 + "\n")
    if hard:
        sys.exit(1)
    return False


if __name__ == "__main__":
    n = load_env()
    print(f"Loaded {n} key(s) from .env" if n else "No .env file found.")
    ok = require_keys("TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET", "GOOGLE_API_KEY",
                      hard=False)
    print("All required keys present ✅" if ok else "Set the missing keys above.")

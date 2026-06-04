#!/usr/bin/env python3
"""
Jarvis — a voice-controlled AI assistant powered by Claude.

It sits quietly and listens for a wake phrase. The moment you say
**"Wake up Jarvis"**, it springs to life, thinks with Claude (Opus 4.8 +
adaptive thinking), can actually *do* things via tools (open apps/sites, search
the web, tell the time, run your TikTok clip pipeline, take notes), and talks
back using ElevenLabs (the same voice setup the rest of this repo already uses).

Quick start
-----------
    pip install -r requirements-jarvis.txt
    export ANTHROPIC_API_KEY="sk-ant-..."
    export ELEVENLABS_API_KEY="..."        # optional — falls back to local TTS
    python jarvis.py                        # voice mode (say "Wake up Jarvis")
    python jarvis.py --text                 # type instead of talk (no mic needed)

In voice mode it stays asleep until it hears "Wake up Jarvis", then keeps the
conversation going. Say "go to sleep" to send it back to standby, or "goodbye" /
"exit" (or Ctrl-C) to quit entirely.
"""

import os
import sys
import json
import platform
import subprocess
import webbrowser
import datetime as _dt

try:
    import anthropic
except ImportError:
    sys.exit("Missing dependency: anthropic. Run: pip install -r requirements-jarvis.txt")


# ── Configuration ───────────────────────────────────────────────────────────────
MODEL = "claude-opus-4-8"
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Adam
NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_notes.json")
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# Phrases that wake Jarvis from standby. Matching is fuzzy (speech-to-text is
# imperfect), so any of these — or just hearing "jarvis" with "wake" — counts.
WAKE_PHRASES = [
    "wake up jarvis",
    "wakeup jarvis",
    "wake jarvis",
    "jarvis wake up",
    "hey jarvis",
    "ok jarvis",
    "okay jarvis",
]
# Phrases that send Jarvis back to standby (without quitting the program).
SLEEP_PHRASES = {"go to sleep", "goto sleep", "go sleep", "stand down", "that's all", "thats all", "never mind", "nevermind"}

SYSTEM_PROMPT = (
    "You are Jarvis, a witty, capable voice assistant modeled on Tony Stark's AI. "
    "You are speaking out loud, so keep replies short, natural, and conversational — "
    "usually one or two sentences. Skip markdown, bullet points, and code blocks; "
    "they don't read well aloud. Address the user as 'sir' occasionally, with dry "
    "British charm, but never overdo it. "
    "Use your tools to take real action rather than just describing what you would do. "
    "When you need current information (news, prices, recent events, weather), use web "
    "search before answering. If you take an action, confirm it briefly."
)


# ── Tools: the things Jarvis can actually DO ─────────────────────────────────────
# Client-side custom tools (executed here) + the server-side web_search tool.

CLIENT_TOOLS = [
    {
        "name": "get_current_datetime",
        "description": "Get the current local date, time, and day of the week.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "open_website",
        "description": "Open a URL in the user's default web browser. Use full URLs "
        "(https://...). Good for 'open YouTube', 'pull up my email', etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The full URL to open."}
            },
            "required": ["url"],
        },
    },
    {
        "name": "open_application",
        "description": "Launch a desktop application on the user's computer by name "
        "(e.g. 'Spotify', 'Calculator', 'Safari', 'Terminal').",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The application name."}
            },
            "required": ["name"],
        },
    },
    {
        "name": "run_tiktok_pipeline",
        "description": "Run this project's TikTok clip-generation pipeline once. "
        "Use when the user asks to make clips, generate videos, or run the daily "
        "clipping agent. This is a long-running background job.",
        "input_schema": {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "enum": ["daily_runner", "kai_blitz", "agent"],
                    "description": "Which pipeline to run. Default 'daily_runner'.",
                }
            },
        },
    },
    {
        "name": "save_note",
        "description": "Save a note or reminder for the user to recall later.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The note to remember."}
            },
            "required": ["text"],
        },
    },
    {
        "name": "list_notes",
        "description": "List all notes the user has previously saved.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

# Anthropic-hosted web search — runs server-side, no local code needed.
SERVER_TOOLS = [{"type": "web_search_20260209", "name": "web_search"}]
ALL_TOOLS = CLIENT_TOOLS + SERVER_TOOLS


def _load_notes():
    try:
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)


def execute_tool(name, tool_input):
    """Run a client-side tool and return a string result for Claude."""
    try:
        if name == "get_current_datetime":
            now = _dt.datetime.now()
            return now.strftime("%A, %B %d, %Y at %I:%M %p")

        if name == "open_website":
            url = tool_input["url"]
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            webbrowser.open(url)
            return f"Opened {url} in the browser."

        if name == "open_application":
            app = tool_input["name"]
            system = platform.system()
            if system == "Darwin":
                subprocess.Popen(["open", "-a", app])
            elif system == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", app], shell=False)
            else:  # Linux
                subprocess.Popen([app.lower()])
            return f"Launched {app}."

        if name == "run_tiktok_pipeline":
            script = tool_input.get("script", "daily_runner")
            script_file = {
                "daily_runner": "daily_runner.py",
                "kai_blitz": "kai_blitz.py",
                "agent": "agent.py",
            }.get(script, "daily_runner.py")
            path = os.path.join(REPO_DIR, script_file)
            if not os.path.exists(path):
                return f"Could not find {script_file} in the project."
            args = [sys.executable, path]
            if script == "daily_runner":
                args.append("--once")
            subprocess.Popen(args, cwd=REPO_DIR)
            return f"Started the {script} pipeline in the background, sir."

        if name == "save_note":
            notes = _load_notes()
            notes.append(
                {"text": tool_input["text"], "at": _dt.datetime.now().isoformat(timespec="seconds")}
            )
            _save_notes(notes)
            return "Noted."

        if name == "list_notes":
            notes = _load_notes()
            if not notes:
                return "There are no saved notes."
            return "Saved notes: " + "; ".join(f"{i + 1}. {n['text']}" for i, n in enumerate(notes))

        return f"Unknown tool: {name}"
    except Exception as e:  # tools should never crash the assistant
        return f"Error running {name}: {e}"


# ── Voice output (text-to-speech) ────────────────────────────────────────────────
class Voice:
    """Speaks text aloud.

    Order of preference:
      1. ElevenLabs (lifelike, needs ELEVENLABS_API_KEY)
      2. macOS built-in `say` command (reliable, free, no setup)
      3. pyttsx3 (cross-platform local TTS)
      4. plain print (last resort)
    """

    def __init__(self):
        self.eleven = None
        self._pyttsx3 = None
        self._mac_say = platform.system() == "Darwin"
        if ELEVENLABS_API_KEY:
            try:
                from elevenlabs.client import ElevenLabs

                self.eleven = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            except Exception:
                self.eleven = None
        if self.eleven is None and not self._mac_say:
            try:
                import pyttsx3

                self._pyttsx3 = pyttsx3.init()
            except Exception:
                self._pyttsx3 = None

    def say(self, text):
        print(f"\nJarvis: {text}")
        if self.eleven is not None and self._speak_elevenlabs(text):
            return
        if self._mac_say:
            try:
                subprocess.run(["say", text], check=False)
                return
            except Exception:
                pass
        if self._pyttsx3 is not None:
            try:
                self._pyttsx3.say(text)
                self._pyttsx3.runAndWait()
                return
            except Exception:
                pass
        # Final fallback: the printed line above is the output.

    def _speak_elevenlabs(self, text):
        try:
            from elevenlabs import VoiceSettings, play

            audio = self.eleven.text_to_speech.convert(
                voice_id=ELEVENLABS_VOICE_ID,
                text=text,
                model_id="eleven_monolingual_v1",
                voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75),
            )
            play(audio)
            return True
        except Exception as e:
            print(f"  (ElevenLabs playback failed: {e})")
            return False


# ── Voice input (speech-to-text) ─────────────────────────────────────────────────
class Ears:
    """Captures speech from the microphone and transcribes it."""

    def __init__(self):
        import speech_recognition as sr

        self.sr = sr
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.6)

    def listen_phrase(self, timeout=None, phrase_time_limit=15):
        """Capture one spoken phrase and transcribe it (lowercased).

        Returns the text, or "" if nothing intelligible was heard, or None if
        no speech even started within `timeout` seconds (used to detect silence).
        """
        try:
            with self.mic as source:
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
        except self.sr.WaitTimeoutError:
            return None
        try:
            return self.recognizer.recognize_google(audio).lower()
        except self.sr.UnknownValueError:
            return ""
        except self.sr.RequestError as e:
            print(f"  (Speech recognition error: {e})")
            return ""


# ── The brain: talk to Claude, run the tool loop ─────────────────────────────────
class Jarvis:
    def __init__(self):
        self.client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        self.messages = []

    def respond(self, user_text):
        """Send a turn to Claude, resolve any tool calls, return spoken reply."""
        self.messages.append({"role": "user", "content": user_text})

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=ALL_TOOLS,
                thinking={"type": "adaptive"},
                output_config={"effort": "medium"},
                messages=self.messages,
            )

            # Server-side tool (web search) hit its loop limit — resume.
            if response.stop_reason == "pause_turn":
                self.messages.append({"role": "assistant", "content": response.content})
                continue

            client_calls = [b for b in response.content if b.type == "tool_use"]
            if not client_calls:
                self.messages.append({"role": "assistant", "content": response.content})
                break

            # Claude wants us to run one or more local tools.
            self.messages.append({"role": "assistant", "content": response.content})
            results = []
            for call in client_calls:
                print(f"  [tool: {call.name} {json.dumps(call.input)}]")
                output = execute_tool(call.name, call.input)
                results.append(
                    {"type": "tool_result", "tool_use_id": call.id, "content": output}
                )
            self.messages.append({"role": "user", "content": results})

        return " ".join(b.text for b in response.content if b.type == "text").strip()


# ── Wake-word matching ───────────────────────────────────────────────────────────
QUIT_WORDS = {"goodbye", "exit", "quit", "stop", "shut down", "shutdown", "bye", "power down"}


def _normalize(text):
    return "".join(c for c in text.lower() if c.isalnum() or c.isspace()).strip()


def wake_match(text):
    """Decide whether `text` is a wake command.

    Returns None if it isn't. If it is, returns any trailing command spoken in
    the same breath (e.g. "wake up jarvis, what's the time?" -> "what's the
    time") — or "" if the wake phrase was said on its own.
    """
    if not text:
        return None
    t = _normalize(text)
    for phrase in WAKE_PHRASES:
        if phrase in t:
            return t.split(phrase, 1)[1].strip()
    # Fuzzy fallback: heard "jarvis" together with "wake".
    if "jarvis" in t and "wake" in t:
        return t.replace("wake", "").replace("up", "").replace("jarvis", "").strip()
    return None


def is_quit(text):
    return _normalize(text) in QUIT_WORDS


def is_sleep(text):
    return _normalize(text) in SLEEP_PHRASES


# ── Main loop ────────────────────────────────────────────────────────────────────
AWAKE_SILENCE_TIMEOUT = 15  # seconds of silence before Jarvis returns to standby


def run_text_mode(jarvis, voice):
    voice.say("Jarvis online. How can I help you, sir?")
    while True:
        try:
            user_text = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            voice.say("Powering down. Goodbye, sir.")
            return
        if not user_text:
            continue
        if is_quit(user_text):
            voice.say("Goodbye, sir.")
            return
        reply = jarvis.respond(user_text)
        if reply:
            voice.say(reply)


def run_voice_mode(jarvis, voice, ears):
    print('\nJarvis is on standby. Say "Wake up Jarvis" to begin.  (Ctrl-C to quit)')
    while True:
        # ── Standby: wait until we hear the wake phrase ──────────────────────
        heard = ears.listen_phrase(timeout=None, phrase_time_limit=4)
        command = wake_match(heard)
        if command is None:
            continue  # not the wake word — keep sleeping

        voice.say("Yes, sir? I'm listening.")

        # ── Awake: converse until silence, sleep phrase, or quit ─────────────
        while True:
            if command:  # an inline command rode in with the wake phrase
                user_text, command = command, ""
            else:
                user_text = ears.listen_phrase(timeout=AWAKE_SILENCE_TIMEOUT, phrase_time_limit=15)
                if user_text is None:  # silence
                    voice.say('Going back to standby. Say "Wake up Jarvis" when you need me.')
                    break
                if not user_text:  # heard noise but couldn't make it out
                    continue
                print(f"You: {user_text}")

            if is_quit(user_text):
                voice.say("Powering down. Goodbye, sir.")
                return
            if is_sleep(user_text):
                voice.say("Standing by, sir.")
                break

            reply = jarvis.respond(user_text)
            if reply:
                voice.say(reply)


def main():
    text_mode = "--text" in sys.argv
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY first:  export ANTHROPIC_API_KEY='sk-ant-...'")

    jarvis = Jarvis()
    voice = Voice()

    if not text_mode:
        try:
            ears = Ears()
        except Exception as e:
            print(f"(No microphone available: {e})\nFalling back to text mode.\n")
            text_mode = True

    try:
        if text_mode:
            run_text_mode(jarvis, voice)
        else:
            run_voice_mode(jarvis, voice, ears)
    except (KeyboardInterrupt, EOFError):
        print()
        voice.say("Powering down. Goodbye, sir.")
    except anthropic.APIError as e:
        print(f"  (API error: {e})")


if __name__ == "__main__":
    main()

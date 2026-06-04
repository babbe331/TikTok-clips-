# 🤖 Jarvis — your voice assistant

A voice-controlled AI assistant powered by **Claude (Opus 4.8)**. You talk to it,
it thinks, takes real actions through tools, and talks back in an Iron-Man-style
voice using **ElevenLabs** (the same setup the rest of this repo already uses).

Lives in one file: **`jarvis.py`**.

---

## Setup

```bash
pip install -r requirements-jarvis.txt

export ANTHROPIC_API_KEY="sk-ant-..."     # required — the brain
export ELEVENLABS_API_KEY="..."           # optional — the voice (falls back to local TTS)
# export ELEVENLABS_VOICE_ID="..."        # optional — defaults to "Adam"
```

> On macOS/Linux, microphone input needs PortAudio for PyAudio:
> `brew install portaudio` (Mac) or `sudo apt install portaudio19-dev` (Linux).

---

## Run

```bash
python jarvis.py            # 🎙️ voice mode — press Enter, speak, Jarvis answers
python jarvis.py --text     # ⌨️  text mode — just type (no microphone needed)
```

Say **"goodbye"**, **"exit"**, or press **Ctrl-C** to quit.

---

## What it can do

Jarvis doesn't just chat — it acts, using tools:

| You say…                                   | Jarvis does…                                            |
| ------------------------------------------ | ------------------------------------------------------- |
| "What time is it?"                         | Tells you the current date and time                     |
| "What's the latest news on X?"             | **Searches the web** (Claude's built-in search) and answers |
| "Open YouTube" / "Pull up my email"        | Opens the site in your browser                          |
| "Launch Spotify"                           | Starts the desktop app                                  |
| "Make some clips" / "Run the daily agent"  | Kicks off this repo's **TikTok clip pipeline**          |
| "Remember to call the editor at 5"         | Saves a note                                            |
| "What are my notes?"                       | Reads them back                                         |
| Anything else                              | Just talks — short, witty, conversational               |

Notes persist in `jarvis_notes.json`.

---

## How it works

1. **Ears** — `SpeechRecognition` captures the mic and transcribes via Google STT.
2. **Brain** — Claude Opus 4.8 with adaptive thinking runs an agentic tool loop:
   it decides which tools to call, you (the script) run the local ones, web search
   runs server-side, and it loops until it has a final spoken answer.
3. **Voice** — ElevenLabs speaks the reply; if there's no key it falls back to
   local `pyttsx3`, and if that's unavailable it just prints.

Conversation history is kept in-session, so Jarvis remembers what you said earlier.

---

## Customizing

- **Personality** — edit `SYSTEM_PROMPT` in `jarvis.py`.
- **Voice** — set `ELEVENLABS_VOICE_ID` (find IDs in your ElevenLabs dashboard).
- **New abilities** — add an entry to `CLIENT_TOOLS` and a branch in `execute_tool()`.

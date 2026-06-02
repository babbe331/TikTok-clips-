"""
TikTok Clipping Agent
Finds the best 60-second moment from recent YouTube/Twitch content
for a list of streamers, crops to 9:16, burns in captions.
"""

import os
import re
import json
import time
import subprocess
import glob
import textwrap

# ── Configuration ──────────────────────────────────────────────────────────────
GOOGLE_API_KEY  = os.environ.get("GOOGLE_API_KEY",  "PASTE_YOUR_GOOGLE_KEY_HERE")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")  # not needed here

CREATORS = [
    {"name": "Kai Cenat",   "youtube": "KaiCenat",        "twitch": "kaicenat"},
    {"name": "IShowSpeed",  "youtube": "IShowSpeed",       "twitch": "ishowspeed"},
    {"name": "Adin Ross",   "youtube": "AdinRoss",         "twitch": "adinross"},
    {"name": "xQc",         "youtube": "@xQcOW",           "twitch": "xqc"},
    {"name": "Fanum",       "youtube": "@FanumTV",         "twitch": "fanum"},
]

OUTPUT_DIR = "tiktok_clips"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Step 1: Find best Twitch clip URL via yt-dlp search ───────────────────────
def get_twitch_clip_url(twitch_handle: str) -> str | None:
    """Pull the top clip from the last 7 days off Twitch."""
    url = f"https://www.twitch.tv/{twitch_handle}/clips?filter=clips&range=7d"
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-items", "1",
        "--print", "url",
        "--no-warnings",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    clip_url = result.stdout.strip().splitlines()[0] if result.stdout.strip() else None
    return clip_url


def get_youtube_video_url(yt_handle: str) -> str | None:
    """Get the most recent upload URL from a YouTube channel."""
    channel_url = f"https://www.youtube.com/@{yt_handle.lstrip('@')}/videos"
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-items", "1",
        "--print", "url",
        "--no-warnings",
        channel_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    video_url = result.stdout.strip().splitlines()[0] if result.stdout.strip() else None
    return video_url


# ── Step 2: Download video ─────────────────────────────────────────────────────
def download_video(url: str, out_path: str, max_duration: int = 3600) -> bool:
    """Download up to max_duration seconds of video."""
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--download-sections", f"*0-{max_duration}",
        "--no-playlist",
        "--no-warnings",
        "-o", out_path,
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return os.path.exists(out_path) and os.path.getsize(out_path) > 0


# ── Step 3: Transcribe with Whisper ───────────────────────────────────────────
def transcribe(video_path: str) -> list[dict]:
    """Return word-level timestamps from Whisper."""
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(video_path, word_timestamps=True)
    words = []
    for seg in result["segments"]:
        for w in seg.get("words", []):
            words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})
    return words


# ── Step 4: Gemini picks the best 60-second window ────────────────────────────
def pick_best_window(words: list[dict], creator_name: str) -> tuple[float, float]:
    """Ask Gemini to find the funniest/most hype 60-second segment."""
    from google import genai

    client = genai.Client(api_key=GOOGLE_API_KEY)

    # Build a compact transcript with timestamps every ~10 words
    lines = []
    for i, w in enumerate(words):
        if i % 10 == 0:
            lines.append(f"[{w['start']:.1f}s] {w['word']}")
        else:
            lines[-1] += f" {w['word']}"
    transcript = "\n".join(lines)

    prompt = textwrap.dedent(f"""
        You are a viral TikTok clip editor. Below is a timestamped transcript
        from a {creator_name} stream. Find the single best 60-second window
        that would go viral on TikTok — look for peak chaos, laughter, hype,
        shocking moments, or hilarious reactions.

        Reply with ONLY a JSON object like:
        {{"start": 42.5, "end": 102.5, "reason": "one sentence why"}}

        Rules:
        - end - start must be between 55 and 65 seconds
        - choose the most entertaining window, not just the first one
        - start and end must be valid timestamps that appear in the transcript

        Transcript:
        {transcript}
    """)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    raw = response.text.strip()
    # Strip markdown code fences if present
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    data = json.loads(raw)
    print(f"    Gemini pick: {data['start']:.1f}s → {data['end']:.1f}s | {data['reason']}")
    return float(data["start"]), float(data["end"])


# ── Step 5: Cut, crop to 9:16, burn captions ──────────────────────────────────
def make_tiktok_clip(
    source: str,
    start: float,
    end: float,
    words: list[dict],
    out_path: str,
    creator_name: str,
):
    duration = end - start

    # Build SRT for just the selected window
    clip_words = [w for w in words if w["start"] >= start and w["end"] <= end + 1]
    chunk_size = 3
    chunks = [clip_words[i: i + chunk_size] for i in range(0, len(clip_words), chunk_size)]

    srt_path = out_path.replace(".mp4", ".srt")

    def fmt(t):
        t = max(0.0, t - start)
        h, m, s = int(t // 3600), int((t % 3600) // 60), int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    srt_lines = []
    for idx, chunk in enumerate(chunks, 1):
        if not chunk:
            continue
        srt_lines += [
            str(idx),
            f"{fmt(chunk[0]['start'])} --> {fmt(chunk[-1]['end'])}",
            " ".join(w["word"].upper() for w in chunk),
            "",
        ]

    with open(srt_path, "w") as f:
        f.write("\n".join(srt_lines))

    # Probe original dimensions
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", source],
        capture_output=True, text=True,
    )
    probe_data = json.loads(probe.stdout)
    vid_stream = next((s for s in probe_data["streams"] if s["codec_type"] == "video"), {})
    orig_w = int(vid_stream.get("width", 1920))
    orig_h = int(vid_stream.get("height", 1080))

    # Crop to 9:16 from center
    target_w = orig_h * 9 // 16
    if target_w > orig_w:
        target_w = orig_w
    crop_x = (orig_w - target_w) // 2

    subtitle_style = (
        "FontName=Arial,FontSize=14,PrimaryColour=&H00FFFF00,"
        "OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2"
    )

    # Watermark with creator name
    drawtext = (
        f"drawtext=text='{creator_name}':fontsize=20:fontcolor=white:"
        f"x=(w-text_w)/2:y=40:box=1:boxcolor=black@0.5:boxborderw=6"
    )

    vf = (
        f"crop={target_w}:{orig_h}:{crop_x}:0,"
        f"scale=1080:1920:flags=lanczos,"
        f"subtitles={srt_path}:force_style='{subtitle_style}',"
        f"{drawtext}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", source,
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac",
        out_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(srt_path)
    if result.returncode != 0:
        print("    FFmpeg error:", result.stderr[-500:])
        return False
    return True


# ── Main loop ──────────────────────────────────────────────────────────────────
def process_creator(creator: dict):
    name = creator["name"]
    safe_name = name.lower().replace(" ", "_")
    print(f"\n{'='*60}")
    print(f"  {name.upper()}")
    print(f"{'='*60}")

    raw_path = os.path.join(OUTPUT_DIR, f"{safe_name}_raw.mp4")
    out_path = os.path.join(OUTPUT_DIR, f"{safe_name}_tiktok.mp4")

    if os.path.exists(out_path):
        print(f"  Already done: {out_path}")
        return

    # Try Twitch first, fall back to YouTube
    url = None
    platform = None

    print(f"  Searching Twitch clips for {creator['twitch']}...")
    url = get_twitch_clip_url(creator["twitch"])
    if url:
        platform = "Twitch"
    else:
        print(f"  No Twitch clip found, trying YouTube...")
        url = get_youtube_video_url(creator["youtube"])
        platform = "YouTube"

    if not url:
        print(f"  Could not find a video for {name}, skipping.")
        return

    print(f"  Found [{platform}]: {url}")

    print(f"  Downloading (up to 30 min)...")
    if not download_video(url, raw_path, max_duration=1800):
        print(f"  Download failed for {name}, skipping.")
        return
    print(f"  Downloaded: {raw_path} ({os.path.getsize(raw_path) // 1_000_000}MB)")

    print(f"  Transcribing with Whisper...")
    words = transcribe(raw_path)
    if len(words) < 20:
        print(f"  Transcript too short, skipping.")
        os.remove(raw_path)
        return
    print(f"  Got {len(words)} words")

    print(f"  Asking Gemini to find the best 60-second moment...")
    try:
        start, end = pick_best_window(words, name)
    except Exception as e:
        print(f"  Gemini failed: {e} — falling back to first 60s")
        start, end = 0.0, 60.0

    print(f"  Cutting TikTok clip [{start:.1f}s → {end:.1f}s]...")
    success = make_tiktok_clip(raw_path, start, end, words, out_path, name)

    os.remove(raw_path)

    if success:
        size_mb = os.path.getsize(out_path) / 1_000_000
        print(f"  Saved: {out_path} ({size_mb:.1f}MB)")
    else:
        print(f"  Clip assembly failed for {name}.")


if __name__ == "__main__":
    print("TikTok Clipping Agent — starting\n")
    for creator in CREATORS:
        try:
            process_creator(creator)
        except Exception as e:
            print(f"  ERROR processing {creator['name']}: {e}")
        time.sleep(5)

    clips = glob.glob(os.path.join(OUTPUT_DIR, "*_tiktok.mp4"))
    print(f"\nDone! {len(clips)} clip(s) saved to ./{OUTPUT_DIR}/")
    for c in sorted(clips):
        print(f"  {c}")

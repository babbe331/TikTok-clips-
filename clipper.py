"""
TikTok Clipping Agent — Twitch Edition
Uses Twitch Helix API to find top clips + GQL to get direct MP4 URLs.
Gemini picks the best 60s moment. FFmpeg crops to 9:16 and burns captions.
"""

import os, re, json, time, subprocess, glob, textwrap
import urllib.request, urllib.parse

# ── Configuration ──────────────────────────────────────────────────────────────
TWITCH_CLIENT_ID     = os.environ.get("TWITCH_CLIENT_ID",     "PASTE_TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET", "PASTE_TWITCH_CLIENT_SECRET")
GOOGLE_API_KEY       = os.environ.get("GOOGLE_API_KEY",       "PASTE_GOOGLE_API_KEY")
TWITCH_WEB_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"  # public web client

CREATORS = [
    "kaicenat",
    "ishowspeed",
    "adinross",
    "xqc",
    "fanum",
    "jynxzi",
    "caseoh_",
    "nickeh30",
    "tarik",
    "hasanabi",
    "valkyrae",
    "ludwig",
    "ninja",
]

MIN_CLIP_DURATION = 60  # seconds

OUTPUT_DIR = "tiktok_clips"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Twitch Helix API ───────────────────────────────────────────────────────────
def helix_token() -> str:
    data = urllib.parse.urlencode({
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }).encode()
    req = urllib.request.Request("https://id.twitch.tv/oauth2/token", data=data, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]


def helix_headers(token: str) -> dict:
    return {"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"}


def get_user_id(login: str, token: str) -> str | None:
    req = urllib.request.Request(
        f"https://api.twitch.tv/helix/users?login={login}",
        headers=helix_headers(token))
    with urllib.request.urlopen(req) as r:
        users = json.loads(r.read()).get("data", [])
    return users[0]["id"] if users else None


def get_top_clips(broadcaster_id: str, token: str, count: int = 10) -> list[dict]:
    import datetime
    week_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = urllib.parse.urlencode({"broadcaster_id": broadcaster_id, "first": count, "started_at": week_ago})
    req = urllib.request.Request(f"https://api.twitch.tv/helix/clips?{params}", headers=helix_headers(token))
    with urllib.request.urlopen(req) as r:
        clips = json.loads(r.read()).get("data", [])
    if not clips:
        params = urllib.parse.urlencode({"broadcaster_id": broadcaster_id, "first": count})
        req = urllib.request.Request(f"https://api.twitch.tv/helix/clips?{params}", headers=helix_headers(token))
        with urllib.request.urlopen(req) as r:
            clips = json.loads(r.read()).get("data", [])
    return clips


# ── Twitch GQL — get direct MP4 URL ───────────────────────────────────────────
def get_clip_mp4_url(slug: str) -> str | None:
    payload = json.dumps([{
        "operationName": "VideoAccessToken_Clip",
        "variables": {"slug": slug},
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "36b89d2507fce29e5ca551df756d27c1cfe079e2609642b4390aa4c35796eb11"
            }
        }
    }]).encode()

    req = urllib.request.Request(
        "https://gql.twitch.tv/gql",
        data=payload,
        headers={"Client-ID": TWITCH_WEB_CLIENT_ID, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())[0]

    clip_data = resp.get("data", {}).get("clip")
    if not clip_data:
        return None

    qualities = clip_data.get("videoQualities", [])
    if not qualities:
        return None

    best_url = qualities[0]["sourceURL"]  # highest quality
    sig   = clip_data["playbackAccessToken"]["signature"]
    token = clip_data["playbackAccessToken"]["value"]

    params = urllib.parse.urlencode({"sig": sig, "token": token})
    return f"{best_url}?{params}"


# ── Download ───────────────────────────────────────────────────────────────────
def download_mp4(url: str, out_path: str) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(out_path, "wb") as f:
            f.write(r.read())
        return os.path.getsize(out_path) > 50_000
    except Exception as e:
        print(f"    Download error: {e}")
        return False


# ── Transcribe with Whisper ────────────────────────────────────────────────────
def transcribe(video_path: str) -> list[dict]:
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(video_path, word_timestamps=True)
    words = []
    for seg in result["segments"]:
        for w in seg.get("words", []):
            words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})
    return words


# ── Gemini picks best 60s window ──────────────────────────────────────────────
def pick_best_window(words: list[dict], creator: str, title: str) -> tuple[float, float]:
    from google import genai
    client = genai.Client(api_key=GOOGLE_API_KEY)

    lines = []
    for i, w in enumerate(words):
        if i % 10 == 0:
            lines.append(f"[{w['start']:.1f}s] {w['word']}")
        else:
            lines[-1] += f" {w['word']}"

    total = words[-1]["end"] if words else 60

    prompt = textwrap.dedent(f"""
        You are a viral TikTok clip editor. Here is a timestamped transcript
        from a {creator} Twitch clip titled "{title}" ({total:.0f}s total).

        Find the single best 60-second window: funniest, most hype, or most shocking.

        Reply ONLY with JSON: {{"start": 0.0, "end": 60.0, "reason": "why"}}
        Rules:
        - end - start must be exactly 60 seconds (±3s)
        - Always pick the most entertaining 60s window, not just the first
        - If total clip is under 63s, use start=0 and end={min(total, 60):.0f}

        Transcript:
        {chr(10).join(lines)}
    """)

    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    raw = re.sub(r"```(?:json)?", "", resp.text.strip()).strip().rstrip("`").strip()
    data = json.loads(raw)
    print(f"    Gemini: {data['start']:.1f}s → {data['end']:.1f}s | {data['reason']}")
    return float(data["start"]), float(data["end"])


# ── FFmpeg: cut + crop 9:16 + captions ────────────────────────────────────────
def make_tiktok_clip(source: str, start: float, end: float, words: list[dict],
                     out_path: str, creator: str) -> bool:
    duration = end - start

    # SRT for window
    clip_words = [w for w in words if w["start"] >= start and w["end"] <= end + 1]
    chunks = [clip_words[i: i+3] for i in range(0, len(clip_words), 3)]
    srt_path = out_path.replace(".mp4", ".srt")

    def fmt(t):
        t = max(0.0, t - start)
        h, m, s = int(t//3600), int((t%3600)//60), int(t%60)
        return f"{h:02d}:{m:02d}:{s:02d},{int((t-int(t))*1000):03d}"

    srt_lines = []
    for idx, chunk in enumerate(chunks, 1):
        if not chunk: continue
        srt_lines += [str(idx), f"{fmt(chunk[0]['start'])} --> {fmt(chunk[-1]['end'])}",
                      " ".join(w["word"].upper() for w in chunk), ""]
    with open(srt_path, "w") as f:
        f.write("\n".join(srt_lines))

    # Probe dimensions
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", source],
        capture_output=True, text=True)
    vid = next((s for s in json.loads(probe.stdout)["streams"] if s["codec_type"] == "video"), {})
    ow, oh = int(vid.get("width", 1920)), int(vid.get("height", 1080))

    tw = min(oh * 9 // 16, ow)
    cx = (ow - tw) // 2

    style = "FontName=Arial,FontSize=14,PrimaryColour=&H00FFFF00,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2"
    safe_creator = creator.replace("'", r"\'")
    watermark = f"drawtext=text='{safe_creator}':fontsize=22:fontcolor=white:x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.6:boxborderw=8"
    vf = f"crop={tw}:{oh}:{cx}:0,scale=720:1280:flags=lanczos,subtitles={srt_path}:force_style='{style}',{watermark}"

    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", source, "-t", str(duration),
           "-vf", vf, "-c:v", "libx264", "-crf", "28", "-preset", "fast",
           "-c:a", "aac", "-b:a", "96k", out_path]

    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(srt_path)
    if result.returncode != 0:
        print("    FFmpeg error:", result.stderr[-400:])
        return False
    return True


# ── Process one creator ────────────────────────────────────────────────────────
def process_creator(login: str, token: str):
    print(f"\n{'='*60}\n  {login.upper()}\n{'='*60}")

    uid = get_user_id(login, token)
    if not uid:
        print(f"  Not found on Twitch: {login}")
        return

    clips = get_top_clips(uid, token, count=10)
    if not clips:
        print(f"  No clips found")
        return

    print(f"  Found {len(clips)} clip(s)")

    for clip in clips:
        slug     = clip["id"]
        title    = clip["title"]
        out_path = os.path.join(OUTPUT_DIR, f"{login}_{slug}_tiktok.mp4")
        raw_path = os.path.join(OUTPUT_DIR, f"{login}_raw.mp4")

        if os.path.exists(out_path):
            print(f"  Already done: {out_path}")
            return

        print(f"  Clip: {title[:70]}")
        print(f"  Getting MP4 URL via GQL...")
        mp4_url = get_clip_mp4_url(slug)
        if not mp4_url:
            print(f"  Could not get MP4 URL, trying next...")
            continue

        print(f"  Downloading...")
        if not download_mp4(mp4_url, raw_path):
            print(f"  Download failed, trying next...")
            continue
        print(f"  Downloaded {os.path.getsize(raw_path)/1_000_000:.1f}MB")

        # Check duration before transcribing
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", raw_path],
            capture_output=True, text=True)
        fmt_data = json.loads(probe.stdout).get("format", {})
        clip_dur = float(fmt_data.get("duration", 0))
        if clip_dur < MIN_CLIP_DURATION:
            print(f"  Clip is only {clip_dur:.0f}s — need at least {MIN_CLIP_DURATION}s, trying next...")
            os.remove(raw_path)
            continue

        print(f"  Transcribing with Whisper... (clip is {clip_dur:.0f}s)")
        words = transcribe(raw_path)
        if len(words) < 5:
            print(f"  Too little speech, trying next...")
            os.remove(raw_path)
            continue
        print(f"  {len(words)} words")

        print(f"  Asking Gemini for best 60s moment...")
        try:
            start, end = pick_best_window(words, login, title)
        except Exception as e:
            print(f"  Gemini failed ({e}), defaulting to first 60s")
            start, end = 0.0, 60.0

        print(f"  Cutting and formatting...")
        success = make_tiktok_clip(raw_path, start, end, words, out_path, login)
        os.remove(raw_path)

        if success:
            mb = os.path.getsize(out_path) / 1_000_000
            print(f"  Saved: {out_path} ({mb:.1f}MB)")
            return
        else:
            print(f"  Assembly failed, trying next...")

    print(f"  No usable clips found for {login}")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("TikTok Clipping Agent — Twitch Edition\n")
    print("Getting Twitch token...")
    token = helix_token()
    print("Token OK\n")

    for login in CREATORS:
        try:
            process_creator(login, token)
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(2)

    clips = glob.glob(os.path.join(OUTPUT_DIR, "*_tiktok.mp4"))
    print(f"\nDone! {len(clips)} clip(s) saved to ./{OUTPUT_DIR}/")
    for c in sorted(clips):
        print(f"  {c}")

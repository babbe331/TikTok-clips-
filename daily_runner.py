"""
Daily TikTok Clipping Agent
- Gemini picks trending creators fresh each day
- Twitch: fully automatic via API
- YouTube/Rumble: works locally with --cookies-from-browser chrome
Runs every 24 hours in a loop.
"""

import os, re, json, time, subprocess, glob, textwrap, datetime
import urllib.request, urllib.parse

# ── Configuration ──────────────────────────────────────────────────────────────
TWITCH_CLIENT_ID     = os.environ.get("TWITCH_CLIENT_ID",     "PASTE_TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET", "PASTE_TWITCH_CLIENT_SECRET")
GOOGLE_API_KEY       = os.environ.get("GOOGLE_API_KEY",       "PASTE_GOOGLE_API_KEY")
TWITCH_WEB_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"

# Always include these every day (Twitch handles)
ALWAYS_TWITCH = [
    "kaicenat",
    "ishowspeed",
    "adinross",
    "xqc",
    "shanegillis",
]

# YouTube/Rumble sources — only work when run LOCALLY with browser cookies
# Set USE_YOUTUBE=True when running on your own machine
USE_YOUTUBE = os.environ.get("USE_YOUTUBE", "false").lower() == "true"
YOUTUBE_BROWSER = os.environ.get("YOUTUBE_BROWSER", "chrome")  # chrome, firefox, safari

ALWAYS_YOUTUBE = [
    {"name": "Trump vs Kirk Debate",   "url": "https://www.youtube.com/@charliekirk1776/videos"},
    {"name": "Shane Gillis Comedy",    "url": "https://www.youtube.com/@ShaneGillisComedy/videos"},
    {"name": "Real Ass Podcast",       "url": "https://www.youtube.com/@RealAssPodcast/videos"},
    {"name": "Trump Rumble",           "url": "https://rumble.com/c/realdonaldtrump"},
]

OUTPUT_DIR = "tiktok_clips"
MIN_CLIP_DURATION = 60


# ── Gemini: pick today's trending Twitch streamers ─────────────────────────────
def get_trending_creators() -> list[str]:
    from google import genai
    client = genai.Client(api_key=GOOGLE_API_KEY)
    today = datetime.date.today().strftime("%B %d, %Y")

    prompt = textwrap.dedent(f"""
        Today is {today}. You are a viral TikTok content strategist.

        Give me 5 Twitch streamers whose clips would go viral on TikTok RIGHT NOW.
        Pick people who are currently:
        - Having drama, beef, or controversial moments
        - Going viral for funny reactions or chaos
        - In the news or trending on social media
        - New/rising streamers blowing up

        Mix in variety: gaming, IRL, commentary, comedy.
        Include at least one wild card — someone unexpected.

        Reply ONLY with a JSON array of Twitch login names (lowercase, no spaces):
        ["login1", "login2", "login3", "login4", "login5"]

        Do NOT include: kaicenat, ishowspeed, adinross, xqc, shanegillis
        (those are already in the daily fixed list)
    """)

    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    raw = re.sub(r"```(?:json)?", "", resp.text.strip()).strip().rstrip("`").strip()
    picks = json.loads(raw)
    print(f"  Gemini trending picks: {picks}")
    return [p.lower().replace(" ", "") for p in picks if isinstance(p, str)]


# ── Twitch API ─────────────────────────────────────────────────────────────────
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


def get_clip_mp4_url(slug: str) -> str | None:
    payload = json.dumps([{
        "operationName": "VideoAccessToken_Clip",
        "variables": {"slug": slug},
        "extensions": {"persistedQuery": {"version": 1, "sha256Hash": "36b89d2507fce29e5ca551df756d27c1cfe079e2609642b4390aa4c35796eb11"}}
    }]).encode()
    req = urllib.request.Request("https://gql.twitch.tv/gql", data=payload,
        headers={"Client-ID": TWITCH_WEB_CLIENT_ID, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())[0]
    clip_data = resp.get("data", {}).get("clip")
    if not clip_data or not clip_data.get("videoQualities"):
        return None
    best_url = clip_data["videoQualities"][0]["sourceURL"]
    sig   = clip_data["playbackAccessToken"]["signature"]
    token = clip_data["playbackAccessToken"]["value"]
    return f"{best_url}?{urllib.parse.urlencode({'sig': sig, 'token': token})}"


def download_twitch(url: str, out_path: str) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(out_path, "wb") as f:
            f.write(r.read())
        return os.path.getsize(out_path) > 50_000
    except Exception as e:
        print(f"    Download error: {e}")
        return False


# ── YouTube/Rumble (local only) ────────────────────────────────────────────────
def get_youtube_url(channel_url: str) -> str | None:
    cmd = [
        "yt-dlp", "--no-check-certificate",
        "--cookies-from-browser", YOUTUBE_BROWSER,
        "--flat-playlist", "--playlist-items", "1",
        "--print", "url", "--no-warnings", channel_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    url = result.stdout.strip().splitlines()[0] if result.stdout.strip() else None
    return url


def download_youtube(url: str, out_path: str) -> bool:
    cmd = [
        "yt-dlp", "--no-check-certificate",
        "--cookies-from-browser", YOUTUBE_BROWSER,
        "-f", "best[height<=720][ext=mp4]/best[height<=720]",
        "--merge-output-format", "mp4",
        "--download-sections", "*0-1800",
        "--no-playlist", "--no-warnings",
        "-o", out_path, url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return os.path.exists(out_path) and os.path.getsize(out_path) > 50_000


# ── Transcribe ─────────────────────────────────────────────────────────────────
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
        You are a viral TikTok clip editor. Timestamped transcript from
        "{creator}" clip titled "{title}" ({total:.0f}s total).

        Find the best 60-second window: funniest, most hype, or most shocking.
        Reply ONLY with JSON: {{"start": 0.0, "end": 60.0, "reason": "why"}}
        Rules:
        - end - start must be exactly 60 seconds (±3s)
        - If total is under 63s, use start=0 and end={min(total,60):.0f}

        Transcript:
        {chr(10).join(lines)}
    """)

    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    raw = re.sub(r"```(?:json)?", "", resp.text.strip()).strip().rstrip("`").strip()
    data = json.loads(raw)
    print(f"    Gemini: {data['start']:.1f}s → {data['end']:.1f}s | {data['reason']}")
    return float(data["start"]), float(data["end"])


# ── FFmpeg: cut + crop 9:16 + captions + compress ─────────────────────────────
def make_tiktok_clip(source: str, start: float, end: float, words: list[dict],
                     out_path: str, creator: str) -> bool:
    duration = end - start
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
        print("    FFmpeg error:", result.stderr[-300:])
        return False
    return True


# ── Process one Twitch creator ─────────────────────────────────────────────────
def process_twitch(login: str, token: str, date_tag: str):
    print(f"\n{'='*60}\n  TWITCH: {login.upper()}\n{'='*60}")
    uid = get_user_id(login, token)
    if not uid:
        print(f"  Not found: {login}")
        return

    clips = get_top_clips(uid, token, count=10)
    if not clips:
        print(f"  No clips found")
        return
    print(f"  Found {len(clips)} clip(s)")

    for clip in clips:
        slug = clip["id"]
        title = clip["title"]
        out_path = os.path.join(OUTPUT_DIR, f"{date_tag}_{login}_{slug[:12]}_tiktok.mp4")
        raw_path = os.path.join(OUTPUT_DIR, f"{login}_raw.mp4")

        if os.path.exists(out_path):
            print(f"  Already done: {out_path}")
            return

        print(f"  Clip: {title[:70]}")
        mp4_url = get_clip_mp4_url(slug)
        if not mp4_url:
            print(f"  No MP4 URL, trying next...")
            continue

        if not download_twitch(mp4_url, raw_path):
            print(f"  Download failed, trying next...")
            continue

        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", raw_path], capture_output=True, text=True)
        dur = float(probe.stdout.strip() or 0)
        if dur < MIN_CLIP_DURATION:
            print(f"  Only {dur:.0f}s, need 60s+, trying next...")
            os.remove(raw_path)
            continue
        print(f"  {dur:.0f}s clip — transcribing...")

        words = transcribe(raw_path)
        if len(words) < 5:
            os.remove(raw_path)
            continue

        try:
            start, end = pick_best_window(words, login, title)
        except Exception as e:
            print(f"  Gemini failed ({e}), using first 60s")
            start, end = 0.0, 60.0

        success = make_tiktok_clip(raw_path, start, end, words, out_path, login)
        os.remove(raw_path)
        if success:
            mb = os.path.getsize(out_path) / 1_000_000
            print(f"  Saved: {out_path} ({mb:.1f}MB)")
            return
        print(f"  Assembly failed, trying next...")

    print(f"  No usable clips for {login}")


# ── Process one YouTube/Rumble source ─────────────────────────────────────────
def process_youtube(source: dict, date_tag: str):
    name = source["name"]
    print(f"\n{'='*60}\n  YOUTUBE: {name.upper()}\n{'='*60}")

    if not USE_YOUTUBE:
        print(f"  Skipped — set USE_YOUTUBE=true when running locally")
        return

    url = get_youtube_url(source["url"])
    if not url:
        print(f"  Could not find video URL")
        return
    print(f"  Found: {url}")

    safe_name = re.sub(r"[^a-z0-9]", "_", name.lower())
    raw_path = os.path.join(OUTPUT_DIR, f"{safe_name}_raw.mp4")
    out_path = os.path.join(OUTPUT_DIR, f"{date_tag}_{safe_name}_tiktok.mp4")

    if os.path.exists(out_path):
        print(f"  Already done")
        return

    print(f"  Downloading (up to 30 min)...")
    if not download_youtube(url, raw_path):
        print(f"  Download failed")
        return

    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", raw_path], capture_output=True, text=True)
    dur = float(probe.stdout.strip() or 0)
    print(f"  Downloaded {dur:.0f}s video")

    words = transcribe(raw_path)
    try:
        start, end = pick_best_window(words, name, url)
    except Exception as e:
        print(f"  Gemini failed ({e}), using first 60s")
        start, end = 0.0, 60.0

    success = make_tiktok_clip(raw_path, start, end, words, out_path, name)
    os.remove(raw_path)
    if success:
        mb = os.path.getsize(out_path) / 1_000_000
        print(f"  Saved: {out_path} ({mb:.1f}MB)")


# ── Daily run ──────────────────────────────────────────────────────────────────
def run_daily():
    date_tag = datetime.date.today().strftime("%Y%m%d")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n{'#'*60}")
    print(f"  DAILY RUN — {date_tag}")
    print(f"{'#'*60}")

    print("\nGetting Twitch token...")
    token = helix_token()

    print("\nAsking Gemini for today's trending creators...")
    try:
        trending = get_trending_creators()
    except Exception as e:
        print(f"  Gemini trending pick failed ({e}), using fallback list")
        trending = ["jynxzi", "caseoh_", "fanum", "tarik", "hasanabi"]

    all_twitch = ALWAYS_TWITCH + [t for t in trending if t not in ALWAYS_TWITCH]
    print(f"\nToday's creator lineup: {all_twitch}")

    for login in all_twitch:
        try:
            process_twitch(login, token, date_tag)
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(2)

    for source in ALWAYS_YOUTUBE:
        try:
            process_youtube(source, date_tag)
        except Exception as e:
            print(f"  ERROR: {e}")

    clips = glob.glob(os.path.join(OUTPUT_DIR, f"{date_tag}_*.mp4"))
    print(f"\nToday's clips ({len(clips)}):")
    for c in sorted(clips):
        mb = os.path.getsize(c) / 1_000_000
        print(f"  {os.path.basename(c)} ({mb:.1f}MB)")
    return clips


# ── Main loop ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    once = "--once" in sys.argv  # run once then exit

    print("TikTok Daily Clipping Agent")
    print("Twitch: automatic | YouTube/Rumble: set USE_YOUTUBE=true (run locally)\n")

    while True:
        try:
            run_daily()
        except Exception as e:
            print(f"\nDaily run error: {e}")

        if once:
            break

        next_run = datetime.datetime.now() + datetime.timedelta(hours=24)
        print(f"\nNext run: {next_run.strftime('%Y-%m-%d %H:%M')} — sleeping 24h...")
        time.sleep(86400)

"""Pulls Kai Cenat clips until we have 15 that are 61s+."""

import os, re, json, time, subprocess, glob, textwrap
import urllib.request, urllib.parse

TWITCH_CLIENT_ID     = os.environ.get("TWITCH_CLIENT_ID",     "PASTE_TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET", "PASTE_TWITCH_CLIENT_SECRET")
GOOGLE_API_KEY       = os.environ.get("GOOGLE_API_KEY",       "PASTE_GOOGLE_API_KEY")
TWITCH_WEB_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
OUTPUT_DIR           = "kai_clips"
TARGET               = 15
MIN_DURATION         = 58  # Twitch clips cap at 60s, so 58+ catches full-length clips

os.makedirs(OUTPUT_DIR, exist_ok=True)


def helix_token():
    data = urllib.parse.urlencode({"client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET, "grant_type": "client_credentials"}).encode()
    req = urllib.request.Request("https://id.twitch.tv/oauth2/token", data=data, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]

def helix_headers(token):
    return {"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"}

def get_user_id(login, token):
    req = urllib.request.Request(f"https://api.twitch.tv/helix/users?login={login}",
        headers=helix_headers(token))
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["data"][0]["id"]

def get_clips_page(broadcaster_id, token, after=None):
    params = {"broadcaster_id": broadcaster_id, "first": 20}
    if after:
        params["after"] = after
    url = f"https://api.twitch.tv/helix/clips?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=helix_headers(token))
    with urllib.request.urlopen(req) as r:
        body = json.loads(r.read())
    return body.get("data", []), body.get("pagination", {}).get("cursor")

def get_clip_mp4_url(slug):
    payload = json.dumps([{"operationName": "VideoAccessToken_Clip",
        "variables": {"slug": slug},
        "extensions": {"persistedQuery": {"version": 1,
        "sha256Hash": "36b89d2507fce29e5ca551df756d27c1cfe079e2609642b4390aa4c35796eb11"}}}]).encode()
    req = urllib.request.Request("https://gql.twitch.tv/gql", data=payload,
        headers={"Client-ID": TWITCH_WEB_CLIENT_ID, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())[0]
    clip_data = resp.get("data", {}).get("clip")
    if not clip_data or not clip_data.get("videoQualities"):
        return None
    best = clip_data["videoQualities"][0]["sourceURL"]
    sig   = clip_data["playbackAccessToken"]["signature"]
    tok   = clip_data["playbackAccessToken"]["value"]
    return f"{best}?{urllib.parse.urlencode({'sig': sig, 'token': tok})}"

def download_mp4(url, out_path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(out_path, "wb") as f:
            f.write(r.read())
        return os.path.getsize(out_path) > 50_000
    except Exception as e:
        print(f"    Download error: {e}")
        return False

def get_duration(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 0

def transcribe(path):
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(path, word_timestamps=True)
    words = []
    for seg in result["segments"]:
        for w in seg.get("words", []):
            words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})
    return words

def pick_best_window(words, title):
    from google import genai
    client = genai.Client(api_key=GOOGLE_API_KEY)
    lines = []
    for i, w in enumerate(words):
        if i % 10 == 0: lines.append(f"[{w['start']:.1f}s] {w['word']}")
        else: lines[-1] += f" {w['word']}"
    total = words[-1]["end"] if words else 61
    prompt = textwrap.dedent(f"""
        You are an expert TikTok viral content editor who deeply understands
        the TikTok algorithm. Kai Cenat clip: "{title}" ({total:.0f}s).

        Find the BEST 61-second window that will perform highest on TikTok.
        Prioritize moments that have ALL of these viral qualities:
        - Strong HOOK in the first 3 seconds (shock, laugh, or confusion)
        - HIGH ENERGY — yelling, chaos, unexpected reactions
        - EMOTIONAL PEAKS — genuine laughter, disbelief, hype
        - SHAREABLE — something people MUST show their friends
        - Watch-again quality — people will loop it

        Avoid: slow intros, dead air, low energy explanations, off-topic tangents.

        Reply ONLY with JSON: {{"start": 0.0, "end": 60.0, "reason": "why this will go viral"}}
        Rules: end-start must be 58-62s. If clip under 62s, use start=0 and end={min(total,60):.0f}.

        Transcript:
        {chr(10).join(lines)}
    """)
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    raw = re.sub(r"```(?:json)?", "", resp.text.strip()).strip().rstrip("`").strip()
    data = json.loads(raw)
    print(f"    Gemini: {data['start']:.1f}s→{data['end']:.1f}s | {data['reason'][:80]}")
    return float(data["start"]), float(data["end"])

def make_clip(source, start, end, words, out_path):
    duration = end - start
    clip_words = [w for w in words if w["start"] >= start and w["end"] <= end + 1]
    chunks = [clip_words[i:i+3] for i in range(0, len(clip_words), 3)]
    srt_path = out_path.replace(".mp4", ".srt")

    def fmt(t):
        t = max(0.0, t - start)
        h,m,s = int(t//3600), int((t%3600)//60), int(t%60)
        return f"{h:02d}:{m:02d}:{s:02d},{int((t-int(t))*1000):03d}"

    srt_lines = []
    for idx, chunk in enumerate(chunks, 1):
        if not chunk: continue
        srt_lines += [str(idx), f"{fmt(chunk[0]['start'])} --> {fmt(chunk[-1]['end'])}",
                      " ".join(w["word"].upper() for w in chunk), ""]
    with open(srt_path, "w") as f:
        f.write("\n".join(srt_lines))

    probe = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", source], capture_output=True, text=True)
    vid = next((s for s in json.loads(probe.stdout)["streams"] if s["codec_type"]=="video"), {})
    ow, oh = int(vid.get("width",1920)), int(vid.get("height",1080))
    tw = min(oh*9//16, ow)
    cx = (ow-tw)//2

    style = "FontName=Arial,FontSize=14,PrimaryColour=&H00FFFF00,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2"
    watermark = "drawtext=text='KaiCenat':fontsize=22:fontcolor=white:x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.6:boxborderw=8"
    vf = f"crop={tw}:{oh}:{cx}:0,scale=720:1280:flags=lanczos,subtitles={srt_path}:force_style='{style}',{watermark}"

    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", source, "-t", str(duration),
           "-vf", vf, "-c:v", "libx264", "-crf", "28", "-preset", "fast",
           "-c:a", "aac", "-b:a", "96k", out_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(srt_path)
    if result.returncode != 0:
        print("    FFmpeg error:", result.stderr[-200:])
        return False
    return True


if __name__ == "__main__":
    print("Kai Cenat Blitz — targeting 15 clips of 61s+\n")
    token = helix_token()
    uid = get_user_id("kaicenat", token)
    print(f"Kai UID: {uid}\n")

    done = 0
    cursor = None
    tried = set()

    while done < TARGET:
        clips, cursor = get_clips_page(uid, token, after=cursor)
        if not clips:
            print("No more clips available from Twitch.")
            break

        for clip in clips:
            if done >= TARGET:
                break
            slug = clip["id"]
            if slug in tried:
                continue
            tried.add(slug)

            title = clip["title"]
            clip_num = done + 1
            out_path = os.path.join(OUTPUT_DIR, f"kai_{clip_num:02d}_{slug[:10]}.mp4")
            raw_path = os.path.join(OUTPUT_DIR, "kai_raw.mp4")

            if os.path.exists(out_path):
                print(f"[{clip_num}/{TARGET}] Already exists: {out_path}")
                done += 1
                continue

            print(f"\n[{clip_num}/{TARGET}] {title[:65]}")
            mp4_url = get_clip_mp4_url(slug)
            if not mp4_url:
                print("  No URL, skipping")
                continue

            if not download_mp4(mp4_url, raw_path):
                print("  Download failed, skipping")
                continue

            dur = get_duration(raw_path)
            if dur < MIN_DURATION:
                print(f"  Only {dur:.0f}s, need {MIN_DURATION}s+, skipping")
                os.remove(raw_path)
                continue

            print(f"  {dur:.0f}s — transcribing...")
            words = transcribe(raw_path)

            try:
                start, end = pick_best_window(words, title)
            except Exception as e:
                print(f"  Gemini failed ({e}), using 0→61s")
                start, end = 0.0, 61.0

            print(f"  Cutting clip {clip_num}...")
            if make_clip(raw_path, start, end, words, out_path):
                mb = os.path.getsize(out_path) / 1_000_000
                print(f"  ✓ Saved: {out_path} ({mb:.1f}MB)")
                done += 1
            else:
                print("  Assembly failed, skipping")

            if os.path.exists(raw_path):
                os.remove(raw_path)

        if not cursor:
            print("Reached end of Kai's clip history.")
            break

    final = sorted(glob.glob(os.path.join(OUTPUT_DIR, "kai_*.mp4")))
    print(f"\nDone! {len(final)}/{TARGET} clips saved to ./{OUTPUT_DIR}/")
    for f in final:
        print(f"  {os.path.basename(f)} ({os.path.getsize(f)//1_000_000}MB)")

"""
Kai Cenat Blitz — 15 x 60s TikTok clips
Strategy: grab clips 25s+, pair two together to hit 60s.
Each output = best 30s from clip A + best 30s from clip B, seamlessly stitched.
"""

import os, re, json, time, subprocess, glob, textwrap
import urllib.request, urllib.parse

TWITCH_CLIENT_ID     = os.environ.get("TWITCH_CLIENT_ID",     "PASTE")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET", "PASTE")
GOOGLE_API_KEY       = os.environ.get("GOOGLE_API_KEY",       "PASTE")
TWITCH_WEB_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
OUTPUT_DIR           = "kai_clips"
TARGET               = 15
MIN_SINGLE           = 25   # minimum for a clip to be usable
HALF_DURATION        = 30   # seconds to take from each clip

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Twitch API ─────────────────────────────────────────────────────────────────
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
    sig  = clip_data["playbackAccessToken"]["signature"]
    tok  = clip_data["playbackAccessToken"]["value"]
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


# ── Whisper ────────────────────────────────────────────────────────────────────
def transcribe(path):
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(path, word_timestamps=True)
    words = []
    for seg in result["segments"]:
        for w in seg.get("words", []):
            words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})
    return words


# ── Gemini: pick best 30s window from a clip ──────────────────────────────────
def pick_best_30s(words, title, total_dur):
    from google import genai
    client = genai.Client(api_key=GOOGLE_API_KEY)
    lines = []
    for i, w in enumerate(words):
        if i % 8 == 0: lines.append(f"[{w['start']:.1f}s] {w['word']}")
        else: lines[-1] += f" {w['word']}"

    prompt = textwrap.dedent(f"""
        You are a viral TikTok editor. Kai Cenat clip: "{title}" ({total_dur:.0f}s total).

        Pick the BEST 30-second window that will go viral on TikTok.
        Look for: shocking hook in first 3s, peak energy, genuine reactions,
        laugh-out-loud moments, chaos, unexpected twists.

        Reply ONLY with JSON: {{"start": 0.0, "end": 30.0, "reason": "one line why"}}
        Rules:
        - end - start must be 28-32 seconds
        - If clip under 32s: start=0, end={min(total_dur, 30):.1f}
        - Choose the most entertaining window, not just the start

        Transcript:
        {chr(10).join(lines)}
    """)
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    raw = re.sub(r"```(?:json)?", "", resp.text.strip()).strip().rstrip("`").strip()
    data = json.loads(raw)
    print(f"    Gemini 30s: {data['start']:.1f}s→{data['end']:.1f}s | {data['reason'][:70]}")
    return float(data["start"]), float(data["end"])


# ── Extract a segment as a temp file ──────────────────────────────────────────
def extract_segment(source, start, duration, out_path):
    # Probe dimensions
    probe = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", source], capture_output=True, text=True)
    vid = next((s for s in json.loads(probe.stdout)["streams"] if s["codec_type"]=="video"), {})
    ow, oh = int(vid.get("width", 1920)), int(vid.get("height", 1080))
    tw = min(oh * 9 // 16, ow)
    cx = (ow - tw) // 2

    vf = f"crop={tw}:{oh}:{cx}:0,scale=720:1280:flags=lanczos"
    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", source, "-t", str(duration),
           "-vf", vf, "-c:v", "libx264", "-crf", "28", "-preset", "fast",
           "-c:a", "aac", "-b:a", "96k", "-ar", "44100", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


# ── Build SRT for combined clip ────────────────────────────────────────────────
def build_srt(words_a, start_a, end_a, words_b, start_b, end_b, srt_path):
    offset_b = end_a - start_a  # where clip B starts in combined timeline

    def fmt(t):
        h, m, s = int(t//3600), int((t%3600)//60), int(t%60)
        return f"{h:02d}:{m:02d}:{s:02d},{int((t-int(t))*1000):03d}"

    entries = []
    # Clip A words
    clip_a = [w for w in words_a if w["start"] >= start_a and w["end"] <= end_a + 0.5]
    # Clip B words — offset timestamps
    clip_b = [{"word": w["word"], "start": w["start"] - start_b + offset_b,
               "end": w["end"] - start_b + offset_b}
              for w in words_b if w["start"] >= start_b and w["end"] <= end_b + 0.5]

    all_words = []
    for w in clip_a:
        all_words.append({"word": w["word"], "start": w["start"] - start_a, "end": w["end"] - start_a})
    all_words += clip_b

    chunks = [all_words[i:i+3] for i in range(0, len(all_words), 3)]
    lines = []
    for idx, chunk in enumerate(chunks, 1):
        if not chunk: continue
        lines += [str(idx), f"{fmt(chunk[0]['start'])} --> {fmt(chunk[-1]['end'])}",
                  " ".join(w["word"].upper() for w in chunk), ""]
    with open(srt_path, "w") as f:
        f.write("\n".join(lines))


# ── Stitch two segments + burn captions ───────────────────────────────────────
def stitch_and_caption(seg_a, seg_b, srt_path, out_path, title_a, title_b):
    concat_list = out_path.replace(".mp4", "_concat.txt")
    with open(concat_list, "w") as f:
        f.write(f"file '{os.path.abspath(seg_a)}'\n")
        f.write(f"file '{os.path.abspath(seg_b)}'\n")

    combined = out_path.replace(".mp4", "_combined.mp4")
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c", "copy", combined
    ], capture_output=True, text=True)
    os.remove(concat_list)
    if r.returncode != 0:
        print("    Concat error:", r.stderr[-200:])
        return False

    # Burn subtitles + watermark
    style = "FontName=Arial,FontSize=14,PrimaryColour=&H00FFFF00,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2"
    watermark = "drawtext=text='KaiCenat':fontsize=22:fontcolor=white:x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.6:boxborderw=8"
    vf = f"subtitles={srt_path}:force_style='{style}',{watermark}"

    r2 = subprocess.run([
        "ffmpeg", "-y", "-i", combined,
        "-vf", vf, "-c:v", "libx264", "-crf", "26", "-preset", "fast",
        "-c:a", "aac", "-b:a", "96k", out_path
    ], capture_output=True, text=True)

    os.remove(combined)
    if r2.returncode != 0:
        print("    Caption error:", r2.stderr[-200:])
        return False
    return True


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Kai Cenat Blitz — 15 x 60s clips (2x30s stitched)\n")
    token = helix_token()
    uid = get_user_id("kaicenat", token)
    print(f"Kai UID: {uid}\n")

    # Phase 1: collect usable raw clips (25s+)
    print("Phase 1: Collecting usable clips (25s+)...")
    pool = []       # list of {slug, title, path, dur, words, start, end}
    cursor = None
    seen = set()

    while len(pool) < TARGET * 2 + 5:
        clips, cursor = get_clips_page(uid, token, after=cursor)
        if not clips:
            break

        for clip in clips:
            if len(pool) >= TARGET * 2 + 5:
                break
            slug = clip["id"]
            if slug in seen:
                continue
            seen.add(slug)

            dur_api = float(clip.get("duration", 0))
            if dur_api < MIN_SINGLE:
                print(f"  skip {clip['title'][:40]} ({dur_api:.0f}s)")
                continue

            print(f"  → {clip['title'][:55]} ({dur_api:.0f}s)")
            mp4_url = get_clip_mp4_url(slug)
            if not mp4_url:
                continue

            raw = os.path.join(OUTPUT_DIR, f"raw_{slug[:10]}.mp4")
            if not download_mp4(mp4_url, raw):
                continue

            dur = get_duration(raw)
            if dur < MIN_SINGLE:
                os.remove(raw)
                continue

            words = transcribe(raw)
            try:
                s, e = pick_best_30s(words, clip["title"], dur)
            except Exception as ex:
                print(f"    Gemini failed ({ex}), using start")
                s, e = 0.0, min(30.0, dur)

            pool.append({"slug": slug, "title": clip["title"],
                         "path": raw, "dur": dur,
                         "words": words, "start": s, "end": e})
            print(f"    Pool size: {len(pool)}")

        if not cursor:
            break

    print(f"\nPool: {len(pool)} clips. Building {TARGET} combined videos...\n")

    # Phase 2: pair clips and stitch
    done = 0
    i = 0
    while done < TARGET and i + 1 < len(pool):
        a = pool[i]
        b = pool[i + 1]
        i += 2

        clip_num = done + 1
        out_path = os.path.join(OUTPUT_DIR, f"kai_{clip_num:02d}.mp4")
        if os.path.exists(out_path):
            print(f"[{clip_num}/{TARGET}] Already exists, skipping")
            done += 1
            continue

        print(f"[{clip_num}/{TARGET}] Stitching:")
        print(f"  A: {a['title'][:55]}")
        print(f"  B: {b['title'][:55]}")

        seg_a = os.path.join(OUTPUT_DIR, f"seg_a_{clip_num}.mp4")
        seg_b = os.path.join(OUTPUT_DIR, f"seg_b_{clip_num}.mp4")
        srt   = os.path.join(OUTPUT_DIR, f"kai_{clip_num:02d}.srt")

        dur_a = a["end"] - a["start"]
        dur_b = b["end"] - b["start"]

        ok_a = extract_segment(a["path"], a["start"], dur_a, seg_a)
        ok_b = extract_segment(b["path"], b["start"], dur_b, seg_b)

        if not ok_a or not ok_b:
            print("  Segment extraction failed, skipping pair")
            for f in [seg_a, seg_b]:
                if os.path.exists(f): os.remove(f)
            continue

        build_srt(a["words"], a["start"], a["end"],
                  b["words"], b["start"], b["end"], srt)

        if stitch_and_caption(seg_a, seg_b, srt, out_path, a["title"], b["title"]):
            mb = os.path.getsize(out_path) / 1_000_000
            total_dur = get_duration(out_path)
            print(f"  ✓ Saved: kai_{clip_num:02d}.mp4 ({mb:.1f}MB, {total_dur:.0f}s)")
            done += 1
        else:
            print("  Stitch failed")

        for f in [seg_a, seg_b, srt]:
            if os.path.exists(f): os.remove(f)

    # Cleanup raw files
    for entry in pool:
        if os.path.exists(entry["path"]):
            os.remove(entry["path"])

    final = sorted(glob.glob(os.path.join(OUTPUT_DIR, "kai_[0-9]*.mp4")))
    print(f"\nDone! {len(final)}/{TARGET} clips saved to ./{OUTPUT_DIR}/")
    for f in final:
        print(f"  {os.path.basename(f)} ({os.path.getsize(f)//1_000_000}MB, {get_duration(f):.0f}s)")

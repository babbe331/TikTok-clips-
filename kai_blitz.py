"""
Kai Cenat Continuous Blitz — runs for 5 hours, sends clips in groups of 5.
- Full 60s clips used as-is
- Short clips only paired if Gemini says they'd go viral together
"""

import os, re, json, time, subprocess, glob, textwrap, datetime
import urllib.request, urllib.parse, ssl

# Bypass SSL cert errors from the sandbox environment
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
_orig_urlopen = urllib.request.urlopen
def _urlopen(req, **kw):
    kw.setdefault("context", ssl_ctx)
    for attempt in range(4):
        try:
            return _orig_urlopen(req, **kw)
        except Exception as e:
            if attempt == 3: raise
            wait = 2 ** attempt
            print(f"    urlopen error ({e}), retrying in {wait}s...")
            time.sleep(wait)
urllib.request.urlopen = _urlopen

TWITCH_CLIENT_ID     = os.environ.get("TWITCH_CLIENT_ID",     "PASTE")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET", "PASTE")
GOOGLE_API_KEY       = os.environ.get("GOOGLE_API_KEY",       "PASTE")
TWITCH_WEB_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
OUTPUT_DIR           = "kai_clips"
RUNTIME_HOURS        = 5
BATCH_SIZE           = 5
MIN_SINGLE           = 25

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Twitch helpers ─────────────────────────────────────────────────────────────
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

def fetch_all_clips(uid, token, max_clips=200):
    """Page through Kai's clips and return all of them."""
    all_clips, cursor = [], None
    while len(all_clips) < max_clips:
        params = {"broadcaster_id": uid, "first": 20}
        if cursor:
            params["after"] = cursor
        req = urllib.request.Request(
            f"https://api.twitch.tv/helix/clips?{urllib.parse.urlencode(params)}",
            headers=helix_headers(token))
        with urllib.request.urlopen(req) as r:
            body = json.loads(r.read())
        page = body.get("data", [])
        if not page:
            break
        all_clips.extend(page)
        cursor = body.get("pagination", {}).get("cursor")
        if not cursor:
            break
    return all_clips

def get_clip_mp4_url(slug):
    payload = json.dumps([{"operationName": "VideoAccessToken_Clip",
        "variables": {"slug": slug},
        "extensions": {"persistedQuery": {"version": 1,
        "sha256Hash": "36b89d2507fce29e5ca551df756d27c1cfe079e2609642b4390aa4c35796eb11"}}}]).encode()
    req = urllib.request.Request("https://gql.twitch.tv/gql", data=payload,
        headers={"Client-ID": TWITCH_WEB_CLIENT_ID, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())[0]
    cd = resp.get("data", {}).get("clip")
    if not cd or not cd.get("videoQualities"):
        return None
    best = cd["videoQualities"][0]["sourceURL"]
    sig, tok = cd["playbackAccessToken"]["signature"], cd["playbackAccessToken"]["value"]
    return f"{best}?{urllib.parse.urlencode({'sig': sig, 'token': tok})}"

def download_mp4(url, out_path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(out_path, "wb") as f:
            f.write(r.read())
        return os.path.getsize(out_path) > 50_000
    except Exception as e:
        print(f"    DL error: {e}")
        return False

def get_duration(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
        "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 0


# ── Whisper ────────────────────────────────────────────────────────────────────
def transcribe(path):
    import whisper
    m = whisper.load_model("base")
    result = m.transcribe(path, word_timestamps=True)
    words = []
    for seg in result["segments"]:
        for w in seg.get("words", []):
            words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})
    return words


# ── Gemini calls ───────────────────────────────────────────────────────────────
def gemini(prompt):
    from google import genai
    client = genai.Client(api_key=GOOGLE_API_KEY)
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return re.sub(r"```(?:json)?", "", resp.text.strip()).strip().rstrip("`").strip()

def pick_window(words, title, dur, target_secs):
    lines = []
    for i, w in enumerate(words):
        if i % 8 == 0: lines.append(f"[{w['start']:.1f}s] {w['word']}")
        else: lines[-1] += f" {w['word']}"
    max_end = min(dur, target_secs + 2)
    prompt = textwrap.dedent(f"""
        Viral TikTok editor. Kai Cenat clip: "{title}" ({dur:.0f}s).
        Find the best {target_secs}-second window. Prioritize:
        strong hook in first 3s, peak chaos/energy, genuine reactions, shareable moments.
        Reply ONLY with JSON: {{"start": 0.0, "end": {target_secs}.0, "reason": "one line"}}
        Rules: end-start = {target_secs-2} to {target_secs+2}s.
        If clip under {target_secs+2}s: start=0, end={max_end:.0f}.
        Transcript: {chr(10).join(lines)}
    """)
    try:
        data = json.loads(gemini(prompt))
        print(f"    Window: {data['start']:.1f}s→{data['end']:.1f}s | {data['reason'][:70]}")
        return float(data["start"]), float(data["end"])
    except Exception as e:
        print(f"    Gemini unavailable ({e}), using start→{target_secs}s")
        return 0.0, min(float(target_secs), dur)

def should_pair(title_a, title_b):
    """Ask Gemini if these two clips would make a viral TikTok together."""
    prompt = textwrap.dedent(f"""
        Two Kai Cenat clips:
        A: "{title_a}"
        B: "{title_b}"

        Would putting these two 30-second clips back-to-back make a single
        viral TikTok video? Consider: do they complement each other in energy,
        theme, or story? Would the combination keep viewers watching?

        Reply ONLY with JSON: {{"pair": true/false, "reason": "one line"}}
    """)
    try:
        data = json.loads(gemini(prompt))
        print(f"    Pair? {data['pair']} — {data['reason'][:70]}")
        return data["pair"]
    except Exception as e:
        print(f"    Gemini unavailable ({e}), defaulting to pair=True")
        return True


# ── FFmpeg helpers ─────────────────────────────────────────────────────────────
def probe_dims(path):
    p = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", path], capture_output=True, text=True)
    vid = next((s for s in json.loads(p.stdout)["streams"] if s["codec_type"]=="video"), {})
    ow, oh = int(vid.get("width", 1920)), int(vid.get("height", 1080))
    tw = min(oh * 9 // 16, ow)
    return ow, oh, tw, (ow - tw) // 2

def extract_seg(src, start, dur, out):
    _, oh, tw, cx = probe_dims(src)
    ow = int(subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_streams",src],
        capture_output=True,text=True).stdout)
    vf = f"crop={tw}:{oh}:{cx}:0,scale=720:1280:flags=lanczos"
    r = subprocess.run(["ffmpeg","-y","-ss",str(start),"-i",src,"-t",str(dur),
        "-vf",vf,"-c:v","libx264","-crf","28","-preset","fast",
        "-c:a","aac","-b:a","96k","-ar","44100",out], capture_output=True, text=True)
    return r.returncode == 0

def crop_and_encode(src, start, dur, out):
    _, oh, tw, cx = probe_dims(src)
    vf = f"crop={tw}:{oh}:{cx}:0,scale=720:1280:flags=lanczos"
    r = subprocess.run(["ffmpeg","-y","-ss",str(start),"-i",src,"-t",str(dur),
        "-vf",vf,"-c:v","libx264","-crf","28","-preset","fast",
        "-c:a","aac","-b:a","96k","-ar","44100",out], capture_output=True, text=True)
    return r.returncode == 0

def burn_captions(src, words, word_start, word_end, offset, out, label="KaiCenat"):
    srt = out.replace(".mp4", ".srt")
    clip_words = [w for w in words if w["start"] >= word_start and w["end"] <= word_end + 0.5]
    chunks = [clip_words[i:i+3] for i in range(0, len(clip_words), 3)]

    def fmt(t):
        t = max(0.0, t - word_start + offset)
        h,m,s = int(t//3600), int((t%3600)//60), int(t%60)
        return f"{h:02d}:{m:02d}:{s:02d},{int((t-int(t))*1000):03d}"

    lines = []
    for idx, chunk in enumerate(chunks, 1):
        if not chunk: continue
        lines += [str(idx), f"{fmt(chunk[0]['start'])} --> {fmt(chunk[-1]['end'])}",
                  " ".join(w["word"].upper() for w in chunk), ""]
    with open(srt, "w") as f:
        f.write("\n".join(lines))
    return srt

def add_captions_watermark(src, srt, out, label="KaiCenat"):
    style = "FontName=Arial,FontSize=14,PrimaryColour=&H00FFFF00,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2"
    safe_label = label.replace("'", r"\'")
    wm = f"drawtext=text='{safe_label}':fontsize=22:fontcolor=white:x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.6:boxborderw=8"
    vf = f"subtitles={srt}:force_style='{style}',{wm}"
    r = subprocess.run(["ffmpeg","-y","-i",src,"-vf",vf,
        "-c:v","libx264","-crf","26","-preset","fast","-c:a","aac","-b:a","96k",out],
        capture_output=True, text=True)
    if os.path.exists(srt): os.remove(srt)
    return r.returncode == 0


# ── Make a single-clip output (58s+ clips) ────────────────────────────────────
def make_solo_clip(clip_info, out_path):
    src, words, dur, title = clip_info["path"], clip_info["words"], clip_info["dur"], clip_info["title"]
    try:
        s, e = pick_window(words, title, dur, 60)
    except Exception as ex:
        print(f"    Gemini failed ({ex}), using 0→60")
        s, e = 0.0, min(60.0, dur)

    tmp = out_path.replace(".mp4", "_raw.mp4")
    if not crop_and_encode(src, s, e - s, tmp):
        return False

    clip_words = [w for w in words if w["start"] >= s and w["end"] <= e + 0.5]
    chunks = [clip_words[i:i+3] for i in range(0, len(clip_words), 3)]
    srt_path = out_path.replace(".mp4", ".srt")
    def fmt(t):
        t = max(0.0, t - s)
        h,m,ss = int(t//3600), int((t%3600)//60), int(t%60)
        return f"{h:02d}:{m:02d}:{ss:02d},{int((t-int(t))*1000):03d}"
    lines = []
    for idx, chunk in enumerate(chunks, 1):
        if not chunk: continue
        lines += [str(idx), f"{fmt(chunk[0]['start'])} --> {fmt(chunk[-1]['end'])}",
                  " ".join(w["word"].upper() for w in chunk), ""]
    with open(srt_path, "w") as f:
        f.write("\n".join(lines))

    ok = add_captions_watermark(tmp, srt_path, out_path)
    if os.path.exists(tmp): os.remove(tmp)
    return ok


# ── Make a paired-clip output ──────────────────────────────────────────────────
def make_paired_clip(a, b, out_path):
    try:
        sa, ea = pick_window(a["words"], a["title"], a["dur"], 30)
    except:
        sa, ea = 0.0, min(30.0, a["dur"])
    try:
        sb, eb = pick_window(b["words"], b["title"], b["dur"], 30)
    except:
        sb, eb = 0.0, min(30.0, b["dur"])

    seg_a = out_path.replace(".mp4", "_A.mp4")
    seg_b = out_path.replace(".mp4", "_B.mp4")

    if not crop_and_encode(a["path"], sa, ea-sa, seg_a): return False
    if not crop_and_encode(b["path"], sb, eb-sb, seg_b): return False

    concat_txt = out_path.replace(".mp4", "_concat.txt")
    with open(concat_txt, "w") as f:
        f.write(f"file '{os.path.abspath(seg_a)}'\nfile '{os.path.abspath(seg_b)}'\n")

    combined = out_path.replace(".mp4", "_combined.mp4")
    r = subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat_txt,
        "-c","copy",combined], capture_output=True, text=True)
    for f in [concat_txt, seg_a, seg_b]:
        if os.path.exists(f): os.remove(f)
    if r.returncode != 0: return False

    # Build merged SRT
    dur_a = ea - sa
    all_words = []
    for w in a["words"]:
        if w["start"] >= sa and w["end"] <= ea + 0.5:
            all_words.append({"word": w["word"], "start": w["start"]-sa, "end": w["end"]-sa})
    for w in b["words"]:
        if w["start"] >= sb and w["end"] <= eb + 0.5:
            all_words.append({"word": w["word"], "start": w["start"]-sb+dur_a, "end": w["end"]-sb+dur_a})

    chunks = [all_words[i:i+3] for i in range(0, len(all_words), 3)]
    srt_path = out_path.replace(".mp4", ".srt")
    def fmt(t):
        h,m,s = int(t//3600), int((t%3600)//60), int(t%60)
        return f"{h:02d}:{m:02d}:{s:02d},{int((t-int(t))*1000):03d}"
    lines = []
    for idx, chunk in enumerate(chunks, 1):
        if not chunk: continue
        lines += [str(idx), f"{fmt(chunk[0]['start'])} --> {fmt(chunk[-1]['end'])}",
                  " ".join(w["word"].upper() for w in chunk), ""]
    with open(srt_path, "w") as f:
        f.write("\n".join(lines))

    ok = add_captions_watermark(combined, srt_path, out_path)
    if os.path.exists(combined): os.remove(combined)
    return ok


# ── Send a batch of clips ──────────────────────────────────────────────────────
def send_batch(paths):
    """Print paths so the parent monitor can pick them up."""
    print(f"\n[BATCH READY] {len(paths)} clips:")
    for p in paths:
        mb = os.path.getsize(p) / 1_000_000
        dur = get_duration(p)
        print(f"  SEND: {p} ({mb:.1f}MB, {dur:.0f}s)")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    deadline = time.time() + RUNTIME_HOURS * 3600
    print(f"Kai Cenat Blitz — running for {RUNTIME_HOURS} hours, batches of {BATCH_SIZE}\n")

    token = helix_token()
    uid   = get_user_id("kaicenat", token)
    print(f"Fetching Kai's clip library...")
    all_clips = fetch_all_clips(uid, token, max_clips=300)
    print(f"Got {len(all_clips)} clips to work through\n")

    # Sort by view count descending for best clips first
    all_clips.sort(key=lambda c: c.get("view_count", 0), reverse=True)

    clip_num   = 1
    batch      = []
    used_slugs = set()
    pool       = []  # downloaded & transcribed clips ready to use
    clip_idx   = 0   # index into all_clips

    def download_and_prep(clip):
        slug = clip["id"]
        dur_api = float(clip.get("duration", 0))
        if dur_api < MIN_SINGLE:
            return None
        mp4_url = get_clip_mp4_url(slug)
        if not mp4_url:
            return None
        raw = os.path.join(OUTPUT_DIR, f"raw_{slug[:10]}.mp4")
        if not download_mp4(mp4_url, raw):
            return None
        dur = get_duration(raw)
        if dur < MIN_SINGLE:
            os.remove(raw)
            return None
        words = transcribe(raw)
        return {"slug": slug, "title": clip["title"], "path": raw,
                "dur": dur, "words": words, "views": clip.get("view_count", 0)}

    while time.time() < deadline:
        # Refill pool
        while len(pool) < 6 and clip_idx < len(all_clips):
            c = all_clips[clip_idx]
            clip_idx += 1
            if c["id"] in used_slugs:
                continue
            print(f"Prepping: {c['title'][:55]} ({c.get('duration',0):.0f}s, {c.get('view_count',0):,} views)")
            info = download_and_prep(c)
            if info:
                pool.append(info)
                print(f"  Pool: {len(pool)}")

        if not pool:
            print("Pool empty — all clips exhausted")
            break

        # Decide: solo or pair?
        info_a = pool.pop(0)
        used_slugs.add(info_a["slug"])
        out_path = os.path.join(OUTPUT_DIR, f"kai_{clip_num:03d}.mp4")

        if info_a["dur"] >= 58:
            # Long clip — use as solo
            print(f"\n[#{clip_num}] SOLO: {info_a['title'][:55]} ({info_a['dur']:.0f}s)")
            ok = make_solo_clip(info_a, out_path)
        elif pool:
            # Short clip — check if next pool clip makes a good pair
            info_b = pool[0]
            print(f"\n[#{clip_num}] Checking pair:")
            print(f"  A: {info_a['title'][:55]}")
            print(f"  B: {info_b['title'][:55]}")
            try:
                do_pair = should_pair(info_a["title"], info_b["title"])
            except:
                do_pair = True  # default to pairing on Gemini error
            if do_pair:
                pool.pop(0)
                used_slugs.add(info_b["slug"])
                print(f"  Pairing!")
                ok = make_paired_clip(info_a, info_b, out_path)
            else:
                print(f"  Not a good pair — using A solo anyway")
                ok = make_solo_clip(info_a, out_path)
        else:
            print(f"\n[#{clip_num}] SOLO (no partner): {info_a['title'][:55]}")
            ok = make_solo_clip(info_a, out_path)

        # Cleanup raw
        if os.path.exists(info_a["path"]): os.remove(info_a["path"])

        if ok:
            mb  = os.path.getsize(out_path) / 1_000_000
            dur = get_duration(out_path)
            print(f"  ✓ kai_{clip_num:03d}.mp4 ({mb:.1f}MB, {dur:.0f}s)")
            batch.append(out_path)
            clip_num += 1

            if len(batch) >= BATCH_SIZE:
                send_batch(batch)
                batch = []
        else:
            print(f"  ✗ Failed")
            if os.path.exists(out_path): os.remove(out_path)

    # Send any remaining
    if batch:
        send_batch(batch)

    total = len(glob.glob(os.path.join(OUTPUT_DIR, "kai_*.mp4")))
    print(f"\nBlitz complete. {total} clips total in ./{OUTPUT_DIR}/")

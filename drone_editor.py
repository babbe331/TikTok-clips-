"""
Drone Footage Auto-Editor
─────────────────────────
Point it at a folder of drone videos. For each clip it will:

  1. Stabilize + color-grade the footage (smooth, crisp aerial look).
  2. Auto-detect and TRIM the dead/boring parts (hovering, static shots).
  3. Assemble a music-backed HIGHLIGHT REEL of the most dynamic moments.
  4. Render everything in BOTH 9:16 (TikTok/Reels) and 16:9 (YouTube).

The only requirement is FFmpeg (with ffprobe). No Python packages needed
beyond the standard library. Stabilization additionally needs an FFmpeg
build with libvidstab — if yours doesn't have it, the bot just skips that
step and tells you.

Usage:
    python drone_editor.py INPUT_FOLDER [options]

Examples:
    python drone_editor.py ~/Videos/drone
    python drone_editor.py ~/Videos/drone --music ~/Music/epic.mp3
    python drone_editor.py ~/Videos/drone --out edited --highlight-secs 30
    python drone_editor.py ~/Videos/drone --aspect 9x16 --no-full

Run "python drone_editor.py --help" for all options.
"""

import os
import sys
import glob
import json
import shutil
import argparse
import subprocess

VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".MP4", ".MOV", ".M4V", ".AVI", ".MKV")
AUDIO_EXTS = (".mp3", ".m4a", ".aac", ".wav", ".flac", ".ogg")


# ── FFmpeg helpers ───────────────────────────────────────────────────────────
def require_ffmpeg():
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(
                f"\nERROR: '{tool}' is not installed or not on your PATH.\n"
                "Install FFmpeg first:\n"
                "  macOS:    brew install ffmpeg\n"
                "  Windows:  download from https://www.gyan.dev/ffmpeg/builds/ and add to PATH\n"
                "  Linux:    sudo apt install ffmpeg\n"
            )


def has_vidstab() -> bool:
    try:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"],
                             capture_output=True, text=True).stdout
        return "vidstabdetect" in out and "vidstabtransform" in out
    except Exception:
        return False


def run(cmd: list, desc: str = "") -> bool:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        if desc:
            print(f"    FFmpeg error during {desc}:")
        print("   ", result.stderr.strip()[-500:])
        return False
    return True


def probe(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", "-show_format", path],
        capture_output=True, text=True).stdout
    data = json.loads(out or "{}")
    streams = data.get("streams", [])
    vid = next((s for s in streams if s.get("codec_type") == "video"), {})
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    return {
        "width": int(vid.get("width", 1920)),
        "height": int(vid.get("height", 1080)),
        "duration": float(data.get("format", {}).get("duration", 0)) or 0.0,
        "has_audio": has_audio,
    }


# ── Stage 1: stabilize + color grade ─────────────────────────────────────────
GRADE = "eq=contrast=1.06:brightness=0.02:saturation=1.12,unsharp=5:5:0.6"


def make_clean_master(src: str, dst: str, stabilize: bool) -> bool:
    """Produce a stabilized + graded master at the source resolution."""
    if stabilize:
        trf = dst + ".trf"
        # Pass 1: analyze camera shake.
        ok = run(["ffmpeg", "-y", "-i", src,
                  "-vf", f"vidstabdetect=shakiness=6:accuracy=15:result={trf}",
                  "-f", "null", "-"], "stabilization analysis")
        if ok:
            # Pass 2: apply smoothing transform, then grade.
            vf = (f"vidstabtransform=input={trf}:smoothing=30:zoom=1:optzoom=1,"
                  f"unsharp=5:5:0.8,{GRADE}")
            ok = run(["ffmpeg", "-y", "-i", src, "-vf", vf,
                      "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                      "-c:a", "aac", "-b:a", "160k", dst], "stabilize+grade")
            if os.path.exists(trf):
                os.remove(trf)
            if ok:
                return True
        # Fall through to grade-only if stabilization failed.
        print("    (stabilization failed — falling back to color grade only)")

    return run(["ffmpeg", "-y", "-i", src, "-vf", GRADE,
                "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-c:a", "aac", "-b:a", "160k", dst], "color grade")


# ── Stage 2: motion analysis (find boring vs dynamic) ────────────────────────
def motion_buckets(src: str, bucket: float = 1.0) -> list:
    """Return a list of (time, mean_motion_score) per `bucket` seconds.

    Uses FFmpeg's per-frame scene-change score as a cheap motion metric:
    hovering/static footage scores near zero, sweeping reveals score high.
    Analysis runs on a downscaled copy so it's fast even on 4K source.
    """
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", src,
         "-vf", "scale=320:-2,select='gte(scene,0)',metadata=print:file=-",
         "-an", "-f", "null", "-"],
        capture_output=True, text=True)
    # Metadata is emitted on stderr/stdout depending on build; parse both.
    text = (proc.stdout or "") + "\n" + (proc.stderr or "")

    times, scores, cur_t = [], [], None
    for line in text.splitlines():
        line = line.strip()
        if "pts_time:" in line:
            try:
                cur_t = float(line.split("pts_time:")[1].split()[0])
            except (ValueError, IndexError):
                cur_t = None
        elif "lavfi.scene_score=" in line and cur_t is not None:
            try:
                times.append(cur_t)
                scores.append(float(line.split("lavfi.scene_score=")[1].split()[0]))
            except (ValueError, IndexError):
                pass

    if not times:
        return []

    # Aggregate per-frame scores into fixed-width time buckets.
    buckets = {}
    for t, s in zip(times, scores):
        idx = int(t // bucket)
        buckets.setdefault(idx, []).append(s)
    return [(idx * bucket, sum(v) / len(v)) for idx, v in sorted(buckets.items())]


def percentile(values: list, pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * (pct / 100.0)
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def merge(segments: list, gap: float, min_len: float) -> list:
    """Merge segments closer than `gap`, then drop any shorter than `min_len`."""
    if not segments:
        return []
    segments = sorted(segments)
    merged = [list(segments[0])]
    for s, e in segments[1:]:
        if s - merged[-1][1] <= gap:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [(s, e) for s, e in merged if e - s >= min_len]


def keep_segments(buckets: list, duration: float, bucket: float,
                  trim_pct: float) -> list:
    """Segments to KEEP after dropping the least-dynamic `trim_pct` of time."""
    if not buckets:
        return [(0.0, duration)]
    threshold = percentile([s for _, s in buckets], trim_pct)
    raw = [(t, min(t + bucket, duration)) for t, s in buckets if s >= threshold]
    kept = merge(raw, gap=1.5, min_len=1.5)
    return kept or [(0.0, duration)]


def highlight_segments(buckets: list, duration: float, bucket: float,
                       target: float) -> list:
    """Most dynamic moments, totalling ~`target` seconds, in time order."""
    if not buckets:
        return [(0.0, min(target, duration))]
    ranked = sorted(buckets, key=lambda b: b[1], reverse=True)
    chosen, total = [], 0.0
    for t, _ in ranked:
        chosen.append((t, min(t + bucket, duration)))
        total += bucket
        if total >= target:
            break
    return merge(chosen, gap=1.0, min_len=bucket) or [(0.0, min(target, duration))]


# ── Stage 3: reframe filters ─────────────────────────────────────────────────
def reframe_filter(aspect: str) -> str:
    if aspect == "9x16":
        return ("crop=w='min(iw,ih*9/16)':h='min(ih,iw*16/9)',"
                "scale=1080:1920:flags=lanczos")
    # 16x9: fit inside 1920x1080, letterbox only if the source isn't 16:9.
    return ("scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black")


# ── Stage 4: cut + concat + reframe (+ optional music) ───────────────────────
def render(master: str, segments: list, aspect: str, out_path: str,
           music: str | None, has_audio: bool) -> bool:
    """Trim `segments` out of `master`, concat them, reframe, write out_path.

    If `music` is given it replaces the audio (ideal for highlight reels,
    where raw drone footage is mostly wind noise).
    """
    rf = reframe_filter(aspect)

    parts, vlabels, alabels = [], [], []
    for i, (s, e) in enumerate(segments):
        parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}]")
        vlabels.append(f"[v{i}]")
        if music is None and has_audio:
            parts.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]")
            alabels.append(f"[a{i}]")

    n = len(segments)
    fc = ";".join(parts) + ";"
    fc += "".join(vlabels) + f"concat=n={n}:v=1:a=0[vc];"
    fc += f"[vc]{rf}[vout]"

    cmd = ["ffmpeg", "-y", "-i", master]
    if music:
        # Loop the track so it always covers the reel, fade it out at the end.
        cmd += ["-stream_loop", "-1", "-i", music]

    if music is None and has_audio:
        fc += ";" + "".join(alabels) + f"concat=n={n}:v=0:a=1[aout]"
        amap = "[aout]"
    elif music:
        amap = "1:a"
    else:
        amap = None

    cmd += ["-filter_complex", fc, "-map", "[vout]"]
    if amap:
        cmd += ["-map", amap]
    if music:
        cmd += ["-af", "afade=t=out:st=nan:d=2", "-shortest"]

    cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", out_path]

    return run(cmd, f"render {os.path.basename(out_path)}")


# ── Music selection ──────────────────────────────────────────────────────────
def resolve_music(music_arg: str | None) -> str | None:
    if not music_arg:
        return None
    if os.path.isfile(music_arg):
        return music_arg
    if os.path.isdir(music_arg):
        tracks = [f for f in sorted(glob.glob(os.path.join(music_arg, "*")))
                  if f.endswith(AUDIO_EXTS)]
        if tracks:
            return tracks[0]
    print(f"    (no usable music found at '{music_arg}' — highlight reel will be silent)")
    return None


# ── Per-file pipeline ────────────────────────────────────────────────────────
def process(src: str, out_dir: str, args, stabilize: bool, music: str | None):
    name = os.path.splitext(os.path.basename(src))[0]
    print(f"\n{'='*64}\n  {os.path.basename(src)}\n{'='*64}")

    info = probe(src)
    if info["duration"] <= 0:
        print("  Could not read this file — skipping.")
        return
    print(f"  {info['width']}x{info['height']}, {info['duration']:.0f}s")

    master = os.path.join(out_dir, f".{name}_master.mp4")
    print("  Stabilizing + color grading..." if stabilize else "  Color grading...")
    if not make_clean_master(src, master, stabilize):
        print("  Could not prepare this file — skipping.")
        return

    minfo = probe(master)
    print("  Analyzing motion to find the best moments...")
    buckets = motion_buckets(master)

    keep = keep_segments(buckets, minfo["duration"], 1.0, args.trim_pct)
    high = highlight_segments(buckets, minfo["duration"], 1.0, args.highlight_secs)
    kept_secs = sum(e - s for s, e in keep)
    print(f"  Trimmed edit: {kept_secs:.0f}s kept of {minfo['duration']:.0f}s "
          f"({len(keep)} segment(s))")
    print(f"  Highlight reel: ~{sum(e - s for s, e in high):.0f}s "
          f"({len(high)} moment(s))")

    aspects = ["9x16", "16x9"] if args.aspect == "both" else [args.aspect]
    for aspect in aspects:
        tag = "vertical" if aspect == "9x16" else "horizontal"

        reel = os.path.join(out_dir, f"{name}_highlight_{tag}.mp4")
        print(f"  Rendering highlight reel ({tag})...")
        if render(master, high, aspect, reel, music, minfo["has_audio"]):
            print(f"    Saved: {reel}")

        if not args.no_full:
            full = os.path.join(out_dir, f"{name}_edit_{tag}.mp4")
            print(f"  Rendering trimmed edit ({tag})...")
            if render(master, keep, aspect, full, None, minfo["has_audio"]):
                print(f"    Saved: {full}")

    if os.path.exists(master):
        os.remove(master)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="Auto-edit a folder of drone footage: trim dead parts, "
                    "stabilize, color-grade, and build music-backed highlight "
                    "reels in 9:16 and 16:9.")
    p.add_argument("input", help="Folder containing your drone videos")
    p.add_argument("--out", default="drone_edits",
                   help="Output folder (default: drone_edits)")
    p.add_argument("--music", default=None,
                   help="Music file, or a folder of music, for highlight reels")
    p.add_argument("--aspect", choices=["both", "9x16", "16x9"], default="both",
                   help="Output aspect ratio(s) (default: both)")
    p.add_argument("--highlight-secs", type=float, default=40.0,
                   help="Target length of each highlight reel (default: 40)")
    p.add_argument("--trim-pct", type=float, default=30.0,
                   help="Drop this %% of the least-dynamic footage (default: 30)")
    p.add_argument("--no-full", action="store_true",
                   help="Only make highlight reels, skip the full trimmed edit")
    p.add_argument("--no-stabilize", action="store_true",
                   help="Skip stabilization even if your FFmpeg supports it")
    args = p.parse_args()

    require_ffmpeg()

    if not os.path.isdir(args.input):
        sys.exit(f"ERROR: input folder not found: {args.input}")

    videos = sorted(f for f in glob.glob(os.path.join(args.input, "*"))
                    if f.endswith(VIDEO_EXTS))
    if not videos:
        sys.exit(f"No video files found in {args.input}")

    os.makedirs(args.out, exist_ok=True)

    stabilize = (not args.no_stabilize) and has_vidstab()
    if not args.no_stabilize and not stabilize:
        print("NOTE: your FFmpeg build has no libvidstab — stabilization will be "
              "skipped.\n      (color grading and everything else still runs.)")

    music = resolve_music(args.music)

    print(f"\nFound {len(videos)} video(s). Editing into ./{args.out}/")
    for src in videos:
        try:
            process(src, args.out, args, stabilize, music)
        except Exception as e:
            print(f"  ERROR processing {os.path.basename(src)}: {e}")

    print(f"\nDone. Your edited videos are in ./{args.out}/")


if __name__ == "__main__":
    main()

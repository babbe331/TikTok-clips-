# 🚁 Drone Footage Auto-Editor

A small bot that edits your drone videos for you. Drop your footage in a
folder, run one command, and it produces finished clips — trimmed, stabilized,
color-graded, and assembled into a music-backed highlight reel, in **both**
vertical (TikTok/Reels) and horizontal (YouTube) formats.

Everything runs **on your own computer**. Nothing is uploaded anywhere.

---

## What it does to each video

1. **Stabilizes + color-grades** — smooths out shake and gives the footage a
   crisp, punchy aerial look.
2. **Trims the boring parts** — automatically detects hovering / static / dead
   stretches and cuts them out, keeping the dynamic shots.
3. **Builds a highlight reel** — picks the most dynamic ~40 seconds, stitches
   them together, and lays your music over the top.
4. **Exports both shapes** — every result is rendered as **9:16 vertical**
   (1080×1920) *and* **16:9 horizontal** (1920×1080).

For each input video you get up to four files:

```
myflight_highlight_vertical.mp4     myflight_highlight_horizontal.mp4
myflight_edit_vertical.mp4          myflight_edit_horizontal.mp4
```

(`highlight` = the short music reel, `edit` = the full clip with boring bits removed.)

---

## One-time setup

### 1. Install FFmpeg

This is the free video engine the bot uses.

- **macOS:** `brew install ffmpeg`
- **Windows:** download a build from <https://www.gyan.dev/ffmpeg/builds/>
  (get the "full" build), unzip it, and add its `bin` folder to your PATH.
- **Linux:** `sudo apt install ffmpeg`

> **Stabilization note:** the bot stabilizes footage only if your FFmpeg
> includes `libvidstab` (the macOS `brew` and Windows "full" builds do).
> If yours doesn't, the bot detects that, tells you, and simply skips
> stabilization — everything else still runs.

You'll also need **Python 3** (already on Mac/Linux; on Windows install from
<https://python.org>). No extra Python packages are required.

### 2. Get the footage off your phone into a folder

The bot reads videos from a folder on your computer, so first copy your drone
clips off the phone:

- **iPhone:** open the **Photos** app → select your drone videos → **Share** →
  **AirDrop** to your Mac (they land in *Downloads*), or use the **Files** app /
  a USB cable. Make a folder like `~/Videos/drone` and put them there.
- **Android:** connect by USB and copy the videos from `DCIM`, or use **Google
  Photos** → download to your computer. Put them in a folder like
  `~/Videos/drone`.

> 💡 Many drones save to the **controller app** on your phone (DJI Fly, etc.).
> Export the full-resolution clips from that app to your camera roll first,
> then transfer as above.

---

## Running it

From the folder containing `drone_editor.py`:

```bash
python drone_editor.py ~/Videos/drone
```

With your own background music for the highlight reels:

```bash
python drone_editor.py ~/Videos/drone --music ~/Music/epic_track.mp3
```

Results are written to a `drone_edits/` folder next to where you run it.

---

## Options

| Option | What it does | Default |
|---|---|---|
| `--out FOLDER` | Where to save the finished videos | `drone_edits` |
| `--music PATH` | A music file, or a folder of music, for the highlight reels | none (reel is silent) |
| `--aspect {both,9x16,16x9}` | Which shape(s) to export | `both` |
| `--highlight-secs N` | Target length of each highlight reel | `40` |
| `--trim-pct N` | How aggressively to cut boring footage (drops the least-dynamic N% of time) | `30` |
| `--no-full` | Only make highlight reels, skip the full trimmed edit | off |
| `--no-stabilize` | Skip stabilization even if supported | off |

### Examples

```bash
# Only vertical highlight reels, 30 seconds each, with music
python drone_editor.py ~/Videos/drone --aspect 9x16 --no-full \
    --highlight-secs 30 --music ~/Music

# Be more aggressive about cutting dead footage
python drone_editor.py ~/Videos/drone --trim-pct 50
```

---

## How the "trim the boring parts" decision works

The bot measures how much each second of footage changes frame-to-frame.
Hovering and static shots barely change (low score); sweeping reveals and fast
moves change a lot (high score). It drops the least-dynamic portion of the
footage (set by `--trim-pct`) for the trimmed edit, and keeps the *highest*
scoring moments for the highlight reel. If a clip ever comes out cutting too
much or too little, just lower or raise `--trim-pct`.

---

## Tips

- **Music length doesn't matter** — the bot loops a short track to cover the
  reel and fades it out at the end.
- **Royalty-free music:** if you'll post publicly, use tracks you're allowed to
  use (e.g. from the TikTok/YouTube in-app libraries or a royalty-free source)
  to avoid copyright strikes.
- **Speed:** 4K footage takes a while, mostly from stabilization. Use
  `--no-stabilize` for a quick first pass to check the cuts, then run the full
  version once you're happy.

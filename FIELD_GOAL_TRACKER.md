# 🏈 FG TrackMan — Field Goal Ball-Flight Tracker

A single-file web app that tracks a field goal kick the way **TrackMan** tracks a golf shot
or a pitch — full ball-flight metrics, a live trajectory animation, and a GOOD / NO GOOD
verdict through real NFL-spec uprights.

The whole app is one file: **`field-goal-tracker.html`**. Double-click it to open in any
browser. Nothing installs, nothing leaves your device (the session log lives in your browser).

---

## What it tracks (the TrackMan metric set, for kicking)

| Metric | What it means |
|---|---|
| **Ball Speed** | Velocity of the ball off the foot (mph) |
| **Launch Angle** | Vertical angle off the foot (°) |
| **Launch Direction** | Horizontal start angle, left (+) / right (−) of target (°) |
| **Spin Rate** | Backspin on the ball (rpm) |
| **Hang Time** | Total time in the air (s) |
| **Apex Height** | Peak height of the flight (ft) |
| **Carry** | Total downrange distance the ball travels (yd) |
| **Crossbar Clearance** | How far the ball clears (or misses) the 10 ft crossbar (ft) |
| **Accuracy** | How far off the center of the posts the ball crosses (ft, L/R) |
| **Max Makeable** | The longest distance this exact flight would still have been good (yd) |
| **Time to Posts** | Flight time to the goal-line plane (s) |
| **Speed at Posts** | Ball speed as it crosses the posts (mph) |

---

## How it works

You set up the kick with the sliders — **attempt distance, ball speed, launch angle, launch
direction, spin rate,** and **wind** — then hit **⚡ KICK**. The app runs a numerical
ballistic simulation (small-step integration with quadratic aerodynamic **drag** and a
**Magnus** lift term from backspin) on a regulation football (0.41 kg), and animates the
result across three synchronized views:

- **Side view** — height vs. downrange, with yard lines, the crossbar, and the apex marker.
- **Through the posts** — a front-on look at exactly where the ball crosses the goal plane.
- **Overhead / aim** — a top-down view of the ball's left/right drift toward the uprights.

Goalposts use NFL spec: **18.5 ft** wide, **10 ft** crossbar.

### Try the presets
Routine 35 · Long 55 · Record 66 · Hook (miss left) · Doink the crossbar · Low line drive —
plus a **🎲 Random** kick generator.

### Session log
Every kick is logged (distance, speed, angle, spin, hang, apex, clearance, max makeable,
result) with a running make percentage. **⬇ CSV** exports the session; **Clear** wipes it.
The log is stored in your browser via `localStorage`.

---

## A note on the numbers

These are **simulated estimates from a physics model**, not radar measurements — there's no
camera or sensor involved. The drag and Magnus constants are tuned so typical inputs produce
realistic field-goal distances (a routine 35-yarder clears the bar comfortably; a 55-yarder
is tight; ~66 yd is at the edge of makeable). It's built as a TrackMan-*style* visualizer and
teaching/feel tool for what a kick's ball flight looks like.

---

## Publishing a clickable link (GitHub Pages)

1. Repo → **Settings** → **Pages**.
2. **Source** → *Deploy from a branch*.
3. Pick this branch, folder **`/ (root)`**, **Save**.
4. After ~1 minute the live link appears, e.g.
   `https://babbe331.github.io/TikTok-clips-/field-goal-tracker.html`.

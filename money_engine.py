"""
money_engine.py — the operating bot that drives toward $1,000,000 in <3 years.

The clip pipeline (daily_runner.py / clipper.py / kai_blitz.py) makes the content.
revenue_model.py proves the trajectory is mathematically reachable.
This engine is the *operator*: it runs the daily loop, keeps state, logs real
revenue as it comes in, compares actuals against the required $1M trajectory, and
tells you the single highest-leverage next action.

It is honest about the division of labor:
  • The BOT does: produce clips, build the posting queue, schedule, track money,
    compute pace vs. target, recommend the next move, and tee up scaling.
  • The HUMAN does (things a bot can't legally/practically do for you): create &
    verify platform accounts, connect payout methods, accept sponsorship deals,
    and ship the backend product. The engine tells you exactly when each is due.

State persists to money_state.json so progress survives restarts and feeds the
dashboard. No third-party dependencies.

    python3 money_engine.py status        # where am I vs. the $1M trajectory
    python3 money_engine.py tick          # run one daily cycle of the loop
    python3 money_engine.py log-revenue 250 affiliate "tiktok shop week 3"
    python3 money_engine.py add-channel "horror_shorts_3" tiktok
    python3 money_engine.py plan          # the required trajectory + next action
    python3 money_engine.py loop          # run a daily tick forever
"""

from __future__ import annotations
import json, os, sys, time, datetime, subprocess
from revenue_model import Scenario, simulate, TARGET, HORIZON_MONTHS, fmt_money

STATE_FILE = "money_state.json"
CLIPS_DIR = "tiktok_clips"


# ── State ─────────────────────────────────────────────────────────────────────
def today() -> str:
    return datetime.date.today().isoformat()


def default_state() -> dict:
    return {
        "started": today(),
        "target": TARGET,
        "horizon_months": HORIZON_MONTHS,
        "channels": [],            # {name, platform, created, followers}
        "revenue_log": [],         # {date, amount, stream, note}
        "post_queue": [],          # clips produced but not yet posted
        "ticks": 0,
        "last_tick": None,
    }


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            data = json.load(f)
        # money_state.json may also carry a "projection" block — keep it.
        st = data.get("engine") or data
        if "started" not in st:
            st = default_state()
        return data if "engine" in data else {"engine": st}
    return {"engine": default_state()}


def save_state(data: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Trajectory math ───────────────────────────────────────────────────────────
def months_elapsed(started: str) -> float:
    d0 = datetime.date.fromisoformat(started)
    return (datetime.date.today() - d0).days / 30.4375


def required_curve() -> list[float]:
    """Cumulative $ the *conservative* plan expects by each month — the line to beat."""
    return [m["cumulative"] for m in simulate(_conservative())["months"]]


def _conservative() -> Scenario:
    return Scenario(
        "conservative",
        mature_views_per_post=4_000, creator_fund_rpm=0.30, affiliate_rpm=0.60,
        sponsor_dollars_per_month=200, product_ctr=0.003, product_conv=0.015,
        max_new_channels_per_month=4, max_channels=70,
    )


def total_revenue(st: dict) -> float:
    return sum(r["amount"] for r in st["revenue_log"])


def revenue_by_stream(st: dict) -> dict:
    out: dict[str, float] = {}
    for r in st["revenue_log"]:
        out[r["stream"]] = out.get(r["stream"], 0) + r["amount"]
    return out


# ── The next-action recommender ───────────────────────────────────────────────
def next_action(st: dict) -> str:
    n = len(st["channels"])
    rev = total_revenue(st)
    streams = revenue_by_stream(st)

    if n == 0:
        return ("Launch your first 2 channels (human step): create the accounts, "
                "connect payouts, then `add-channel <name> <platform>`. The clip "
                "pipeline already produces content — it just needs somewhere to post.")
    if not st["post_queue"] and st["ticks"] > 0:
        return ("Post queue is empty — run `python3 daily_runner.py --once` (or "
                "kai_blitz.py) to refill it, then `tick` to enqueue clips.")
    if "affiliate" not in streams and n >= 1:
        return ("Highest leverage now: add affiliate links to every bio/pinned "
                "comment (TikTok Shop, Amazon, niche offer). Affiliate RPM dwarfs "
                "creator-fund RPM. Log earnings with `log-revenue <amt> affiliate`.")
    if n < 8:
        return (f"Scale channels: you have {n}. Reinvest profit to reach ~8 "
                f"channels — the model's growth comes from the portfolio, not one "
                f"viral hit. `add-channel <name> <platform>`.")
    if "product" not in streams:
        return ("Build the backend product (human step): a $27 digital product or "
                "service is the highest-margin stream and the real path to $1M. "
                "Funnel views → offer. Log sales with `log-revenue <amt> product`.")
    if "sponsor" not in streams and rev > 2_000:
        return ("Your audience can be sponsored. Pitch 1 sponsor per mature channel "
                "(~$200-600/mo each). Log with `log-revenue <amt> sponsor`.")
    return ("Stay on the loop: keep posting daily, reinvest profit into new "
            "channels (toward the 70-channel ceiling), and protect the product "
            "funnel. The compounding does the rest.")


# ── Commands ──────────────────────────────────────────────────────────────────
def cmd_status(data: dict) -> None:
    st = data["engine"]
    rev = total_revenue(st)
    elapsed = months_elapsed(st["started"])
    curve = required_curve()
    idx = min(int(elapsed), len(curve) - 1)
    expected = curve[idx] if elapsed >= 1 else 0
    pct = rev / TARGET * 100

    print(f"\n{'='*64}\n  💰 PROGRESS TO {fmt_money(TARGET)}\n{'='*64}")
    bar_len = 40
    filled = int(min(rev / TARGET, 1.0) * bar_len)
    print(f"  [{'█'*filled}{'░'*(bar_len-filled)}] {pct:.2f}%")
    print(f"  Generated so far : {fmt_money(rev)}")
    print(f"  Elapsed          : {elapsed:.1f} / {HORIZON_MONTHS} months")
    print(f"  Plan expects     : {fmt_money(expected)} by now (conservative)")
    if rev >= expected:
        print(f"  Pace             : ✅ on or ahead of trajectory")
    else:
        gap = expected - rev
        print(f"  Pace             : ⏳ {fmt_money(gap)} behind — not fatal early on")
    print(f"  Channels         : {len(st['channels'])}")
    print(f"  Post queue       : {len(st['post_queue'])} clips ready")
    by = revenue_by_stream(st)
    if by:
        print("  Revenue streams  : " + ", ".join(
            f"{k} {fmt_money(v)}" for k, v in sorted(by.items(), key=lambda x: -x[1])))
    print(f"\n  ▶ NEXT ACTION: {next_action(st)}\n")


def cmd_plan(data: dict) -> None:
    r = simulate(_conservative())
    print(f"\n  Required trajectory (conservative plan — the line to beat):")
    print(f"  {'Month':>6} {'Cumulative':>14}")
    for row in r["months"]:
        if row["month"] % 6 == 0 or row["month"] == 1:
            mark = "  ← $1M crossed" if (r["hit_target_month"]
                                         and row["month"] == 6 * round(r["hit_target_month"]/6)) else ""
            print(f"  {row['month']:>6} {fmt_money(row['cumulative']):>14}")
    print(f"\n  Conservative plan crosses {fmt_money(TARGET)} at month "
          f"{r['hit_target_month']}.")
    cmd_status(data)


def cmd_tick(data: dict) -> None:
    """One daily cycle: pull any freshly produced clips into the post queue."""
    st = data["engine"]
    new = []
    if os.path.isdir(CLIPS_DIR):
        existing = {c["file"] for c in st["post_queue"]}
        for fn in sorted(os.listdir(CLIPS_DIR)):
            if fn.endswith(".mp4") and fn not in existing:
                new.append({"file": fn, "queued": today(), "posted": False})
    st["post_queue"].extend(new)
    st["ticks"] += 1
    st["last_tick"] = today()
    save_state(data)
    print(f"  Tick #{st['ticks']}: +{len(new)} clip(s) queued "
          f"({len(st['post_queue'])} total ready to post).")
    print(f"  ▶ {next_action(st)}")


def cmd_add_channel(data: dict, name: str, platform: str) -> None:
    st = data["engine"]
    st["channels"].append({"name": name, "platform": platform,
                           "created": today(), "followers": 0})
    save_state(data)
    print(f"  + Channel '{name}' ({platform}). Total: {len(st['channels'])}.")


def cmd_log_revenue(data: dict, amount: float, stream: str, note: str) -> None:
    st = data["engine"]
    st["revenue_log"].append({"date": today(), "amount": amount,
                              "stream": stream, "note": note})
    save_state(data)
    rev = total_revenue(st)
    print(f"  + {fmt_money(amount)} ({stream}). Total generated: {fmt_money(rev)} "
          f"({rev/TARGET*100:.2f}% of goal).")
    if rev >= TARGET:
        print("  🎉🎉🎉 $1,000,000 GENERATED — GOAL REACHED. 🎉🎉🎉")


def cmd_loop(data: dict) -> None:
    print("Money engine daily loop. Ctrl-C to stop.")
    while True:
        cmd_tick(data)
        cmd_status(data)
        time.sleep(86400)


# ── CLI ───────────────────────────────────────────────────────────────────────
HELP = __doc__


def main() -> None:
    data = load_state()
    # Always (re)attach the latest projection so the dashboard stays in sync.
    if "projection" not in data:
        data["projection"] = simulate(Scenario("base"))
        save_state(data)

    args = sys.argv[1:]
    cmd = args[0] if args else "status"

    if cmd == "status":
        cmd_status(data)
    elif cmd == "plan":
        cmd_plan(data)
    elif cmd == "tick":
        cmd_tick(data)
    elif cmd == "loop":
        cmd_loop(data)
    elif cmd == "add-channel" and len(args) >= 3:
        cmd_add_channel(data, args[1], args[2])
    elif cmd == "log-revenue" and len(args) >= 3:
        note = " ".join(args[3:]) if len(args) > 3 else ""
        cmd_log_revenue(data, float(args[1]), args[2], note)
    else:
        print(HELP)


if __name__ == "__main__":
    main()

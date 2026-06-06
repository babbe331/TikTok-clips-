"""
revenue_model.py — The math behind "$1,000,000 in under 3 years".

A bot can produce infinite content for free. The hard part is the economics:
how many channels, how many views, at what RPM, plus which high-margin backend
turns views into real money — and whether that compounds to $1M within 36 months.

This module models a *portfolio of faceless short-form channels* (exactly what
the clip pipeline in this repo produces) across four stacked revenue streams:

    1. Platform creator funds   (TikTok Rewards / YT Shorts / IG bonuses)
    2. Affiliate marketing      (links in bio / pinned comment)
    3. Sponsorships             (paid once a channel has an audience)
    4. Owned product / backend  (digital product or service — the real margin)

Profit is reinvested to launch more channels, so the system compounds.

No dependencies — pure stdlib. Run it:

    python3 revenue_model.py                 # base scenario + verdict
    python3 revenue_model.py --all           # conservative / base / aggressive
    python3 revenue_model.py --json state    # write projection to money_state.json
"""

from __future__ import annotations
import json, math, sys
from dataclasses import dataclass, asdict, field

TARGET = 1_000_000          # the goal, in dollars
HORIZON_MONTHS = 36         # "under 3 years"


# ── Scenario levers ──────────────────────────────────────────────────────────
@dataclass
class Scenario:
    name: str

    # Content production (what the bot does for free)
    posts_per_day: float = 4          # posts per channel per day
    start_channels: int = 2           # channels you launch on day one

    # Audience maturation: a new channel ramps toward "mature" reach over time.
    # avg_views_per_post(age) = mature_views * (1 - e^(-age/tau))
    mature_views_per_post: float = 9_000   # expected avg once the channel is seasoned
    ramp_tau_months: float = 4.0           # how fast a channel matures
    # Expected value already blends in the occasional viral hit; we don't model
    # individual lottery wins, we model the *portfolio average*.

    # Revenue per 1,000 views (RPM), blended across platforms you post to.
    creator_fund_rpm: float = 0.45    # TikTok Rewards-ish blended w/ low YT/IG
    affiliate_rpm: float = 1.20       # earnings per 1k views from affiliate links

    # Sponsorships: unlock once a channel is mature & has audience.
    sponsor_unlock_month: int = 4     # channel age when sponsors start
    sponsor_dollars_per_month: float = 350   # per qualifying channel

    # Owned backend product (digital product/service) — highest margin.
    # A fraction of total monthly views click through and a fraction buy.
    product_price: float = 27.0
    product_ctr: float = 0.004        # 0.4% of views visit the offer
    product_conv: float = 0.02        # 2% of visitors buy
    product_margin: float = 0.90      # digital ~ 90% margin

    # Costs
    fixed_monthly_cost: float = 120   # APIs, hosting, scheduler
    cost_per_channel_month: float = 8 # proxies/accounts/tooling per channel
    # A virtual assistant is hired once you cross a channel count (optional ops).
    va_cost: float = 1500
    va_per_channels: int = 25         # one VA per 25 channels

    # Growth / reinvestment
    channel_setup_cost: float = 60    # cost to stand up a new channel
    max_new_channels_per_month: int = 6   # how fast you can realistically launch
    reinvest_fraction: float = 0.70   # share of profit plowed back into launches
    max_channels: int = 120           # practical ceiling for one operator + VAs


# ── Core simulation ──────────────────────────────────────────────────────────
def avg_views_per_post(age_months: float, s: Scenario) -> float:
    return s.mature_views_per_post * (1 - math.exp(-age_months / s.ramp_tau_months))


def simulate(s: Scenario) -> dict:
    """Run a month-by-month simulation over the horizon. Returns a report dict."""
    # Each channel tracked only by its age in months.
    ages = [0.0] * s.start_channels
    cash = 0.0                 # reinvestable cash on hand
    cumulative = 0.0           # total revenue generated to date
    months = []
    hit_month = None

    for m in range(1, HORIZON_MONTHS + 1):
        n = len(ages)
        total_monthly_views = 0.0
        creator_rev = affiliate_rev = sponsor_rev = 0.0

        for age in ages:
            vpp = avg_views_per_post(age, s)
            ch_views = vpp * s.posts_per_day * 30
            total_monthly_views += ch_views
            creator_rev += ch_views / 1000 * s.creator_fund_rpm
            affiliate_rev += ch_views / 1000 * s.affiliate_rpm
            if age >= s.sponsor_unlock_month:
                sponsor_rev += s.sponsor_dollars_per_month

        # Owned backend product scales with TOTAL portfolio reach.
        buyers = total_monthly_views * s.product_ctr * s.product_conv
        product_rev = buyers * s.product_price * s.product_margin

        gross = creator_rev + affiliate_rev + sponsor_rev + product_rev

        # Costs
        va_count = n // s.va_per_channels
        costs = (s.fixed_monthly_cost
                 + s.cost_per_channel_month * n
                 + s.va_cost * va_count)
        net = gross - costs

        cumulative += gross          # "generate me $X" = revenue generated
        cash += max(net, 0) * s.reinvest_fraction

        # Reinvest cash into launching new channels.
        launched = 0
        while (launched < s.max_new_channels_per_month
               and n + launched < s.max_channels
               and cash >= s.channel_setup_cost):
            cash -= s.channel_setup_cost
            launched += 1
        # Age existing channels, add the new ones at age 0.
        ages = [a + 1 for a in ages] + [0.0] * launched

        if hit_month is None and cumulative >= TARGET:
            hit_month = m

        months.append({
            "month": m,
            "channels": n,
            "monthly_views": round(total_monthly_views),
            "creator": round(creator_rev),
            "affiliate": round(affiliate_rev),
            "sponsor": round(sponsor_rev),
            "product": round(product_rev),
            "gross": round(gross),
            "net": round(net),
            "cumulative": round(cumulative),
        })

    return {
        "scenario": s.name,
        "levers": asdict(s),
        "hit_target_month": hit_month,
        "final_cumulative": round(cumulative),
        "final_channels": len(ages),
        "final_monthly_gross": months[-1]["gross"],
        "months": months,
    }


# ── Reporting ─────────────────────────────────────────────────────────────────
def fmt_money(x) -> str:
    return f"${x:,.0f}"


def print_report(r: dict) -> None:
    s = r["scenario"]
    print(f"\n{'='*72}\n  SCENARIO: {s.upper()}\n{'='*72}")
    print(f"  {'Mo':>3} {'Chans':>6} {'Views/mo':>12} {'Gross/mo':>11} "
          f"{'Net/mo':>10} {'Cumulative':>13}")
    print(f"  {'-'*3} {'-'*6} {'-'*12} {'-'*11} {'-'*10} {'-'*13}")
    for row in r["months"]:
        if row["month"] % 3 == 0 or row["month"] == 1:   # quarterly + first
            print(f"  {row['month']:>3} {row['channels']:>6} "
                  f"{row['monthly_views']:>12,} {fmt_money(row['gross']):>11} "
                  f"{fmt_money(row['net']):>10} {fmt_money(row['cumulative']):>13}")

    print(f"\n  Revenue mix at month {r['months'][-1]['month']}:")
    last = r["months"][-1]
    for k in ("creator", "affiliate", "sponsor", "product"):
        bar = "█" * int(last[k] / max(last["gross"], 1) * 30)
        print(f"    {k:>10}: {fmt_money(last[k]):>10}  {bar}")

    print()
    if r["hit_target_month"]:
        yrs = r["hit_target_month"] / 12
        verdict = (f"  ✅ HITS $1,000,000 at month {r['hit_target_month']} "
                   f"({yrs:.1f} years) — within the 3-year goal.")
    else:
        verdict = (f"  ⚠️  Reaches {fmt_money(r['final_cumulative'])} by month "
                   f"{HORIZON_MONTHS} — short of $1M. Pull the levers below.")
    print(verdict)
    print(f"  By month 36: {r['final_channels']} channels, "
          f"{fmt_money(r['final_monthly_gross'])}/mo run-rate.")


def scenarios() -> dict[str, Scenario]:
    base = Scenario("base")
    conservative = Scenario(
        "conservative",
        mature_views_per_post=4_000, creator_fund_rpm=0.30, affiliate_rpm=0.60,
        sponsor_dollars_per_month=200, product_ctr=0.003, product_conv=0.015,
        max_new_channels_per_month=4, max_channels=70,
    )
    aggressive = Scenario(
        "aggressive",
        posts_per_day=6, start_channels=3, mature_views_per_post=15_000,
        ramp_tau_months=3.0, creator_fund_rpm=0.55, affiliate_rpm=2.00,
        sponsor_dollars_per_month=600, product_price=49, product_ctr=0.006,
        product_conv=0.025, max_new_channels_per_month=8, max_channels=160,
    )
    return {"conservative": conservative, "base": base, "aggressive": aggressive}


def main() -> None:
    args = sys.argv[1:]
    scen = scenarios()

    if "--json" in args:
        # Write the base projection to money_state.json for the dashboard.
        r = simulate(scen["base"])
        out = "money_state.json"
        with open(out, "w") as f:
            json.dump({"projection": r}, f, indent=2)
        print(f"Wrote projection → {out}")
        print_report(r)
        return

    if "--all" in args:
        for name in ("conservative", "base", "aggressive"):
            print_report(simulate(scen[name]))
        print(f"\n{'='*72}")
        print("  Read MONEY_PLAYBOOK.md for what the bot automates vs. what you do.")
        print(f"{'='*72}\n")
        return

    print_report(simulate(scen["base"]))
    print("\n  Run with --all to compare conservative/base/aggressive scenarios.")
    print("  Run with --json to feed money_dashboard.html.\n")


if __name__ == "__main__":
    main()

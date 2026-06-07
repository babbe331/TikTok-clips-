#!/usr/bin/env python3
"""
RealtyFlow financial model.

Projects monthly recurring revenue (MRR) for a solo AI-automation studio selling
retainers to real estate agencies, and reports the month it crosses a target
(default $45,000/month).

Everything is a planning assumption. Replace the defaults with your real
pipeline numbers. No external dependencies — runs on stdlib.

    python3 financial_model.py
    python3 financial_model.py --target 45000 --months 36
    python3 financial_model.py --new-clients 3 --churn 0.03 --avg-retainer 3000
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field


# --- Offer definition -------------------------------------------------------
# (tier name, one-time setup fee, monthly retainer, share of new sales)
TIERS = {
    "Starter": {"setup": 1500, "retainer": 1500, "mix": 0.35},
    "Growth":  {"setup": 2500, "retainer": 3000, "mix": 0.50},
    "Scale":   {"setup": 4000, "retainer": 5000, "mix": 0.15},
}


@dataclass
class Assumptions:
    target_mrr: float = 45_000.0
    months: int = 36
    # Net new *paying* clients you GROSS per month (before churn). Outreach-driven
    # early, SEO/referral-driven later, so it ramps. Override with --new-clients.
    new_clients_start: float = 0.7      # month 1 closes (you're still learning to sell)
    new_clients_max: float = 2.5        # steady-state closes/mo once SEO + referrals mature
    ramp_months: int = 10               # months to reach new_clients_max
    flat_new_clients: float | None = None  # if set, ignore ramp
    # Solo capacity: one person can monitor/optimize only so many live systems
    # before delivery quality (and retention) slips. Past this you raise prices
    # or stop selling — you do NOT keep adding clients linearly forever.
    capacity_clients: float = 20.0
    monthly_churn: float = 0.03         # fraction of clients lost per month
    fixed_overhead: float = 250.0       # tools/software per month
    variable_cost_per_client: float = 120.0  # API/SMS/email per client/mo
    tier_mix: dict = field(default_factory=lambda: {k: v["mix"] for k, v in TIERS.items()})

    def new_clients_in(self, month: int) -> float:
        if self.flat_new_clients is not None:
            return self.flat_new_clients
        if month >= self.ramp_months:
            return self.new_clients_max
        # linear ramp from start -> max
        frac = (month - 1) / max(self.ramp_months - 1, 1)
        return self.new_clients_start + frac * (self.new_clients_max - self.new_clients_start)

    @property
    def avg_setup(self) -> float:
        return sum(TIERS[t]["setup"] * m for t, m in self.tier_mix.items())

    @property
    def avg_retainer(self) -> float:
        return sum(TIERS[t]["retainer"] * m for t, m in self.tier_mix.items())


@dataclass
class MonthResult:
    month: int
    new_clients: float
    active_clients: float
    mrr: float
    setup_revenue: float
    total_revenue: float
    costs: float
    net_cash: float
    cumulative_cash: float


def project(a: Assumptions) -> list[MonthResult]:
    results: list[MonthResult] = []
    active = 0.0
    cumulative = 0.0
    for m in range(1, a.months + 1):
        churned = active * a.monthly_churn
        # As you approach solo capacity, you throttle new sales (raise prices /
        # waitlist) rather than overload delivery. Sales taper toward the cap.
        room = max(0.0, 1.0 - active / a.capacity_clients)
        new = a.new_clients_in(m) * room
        active = active - churned + new

        mrr = active * a.avg_retainer
        setup_rev = new * a.avg_setup
        total_rev = mrr + setup_rev
        costs = a.fixed_overhead + active * a.variable_cost_per_client
        net = total_rev - costs
        cumulative += net

        results.append(MonthResult(
            month=m, new_clients=new, active_clients=active, mrr=mrr,
            setup_revenue=setup_rev, total_revenue=total_rev, costs=costs,
            net_cash=net, cumulative_cash=cumulative,
        ))
    return results


def render(a: Assumptions, rows: list[MonthResult]) -> None:
    bar = "=" * 78
    print(bar)
    print("RealtyFlow — Path to ${:,.0f}/month MRR".format(a.target_mrr))
    print(bar)
    print("Assumptions:")
    print(f"  Avg retainer/client : ${a.avg_retainer:,.0f}/mo   "
          f"(mix {', '.join(f'{t} {int(m*100)}%' for t, m in a.tier_mix.items())})")
    print(f"  Avg setup fee       : ${a.avg_setup:,.0f} one-time")
    if a.flat_new_clients is not None:
        print(f"  New clients/month   : {a.flat_new_clients:.1f} (flat)")
    else:
        print(f"  New clients/month   : {a.new_clients_start:.0f} -> "
              f"{a.new_clients_max:.0f} over {a.ramp_months} mo, then steady")
    print(f"  Monthly churn       : {a.monthly_churn*100:.1f}%")
    print(f"  Fixed overhead      : ${a.fixed_overhead:,.0f}/mo  +  "
          f"${a.variable_cost_per_client:,.0f}/client/mo variable")
    print(bar)
    header = f"{'Mo':>3} {'New':>5} {'Active':>7} {'MRR':>11} {'Total Rev':>11} {'Net Cash':>11} {'Cum Cash':>12}"
    print(header)
    print("-" * 78)

    target_hit = None
    breakeven_hit = None
    for r in rows:
        flag = ""
        if target_hit is None and r.mrr >= a.target_mrr:
            target_hit = r.month
            flag = "  <- target MRR"
        if breakeven_hit is None and r.net_cash > 0:
            breakeven_hit = r.month
        # print every month up to target+2, then every 3rd month
        show = (target_hit is None) or (r.month <= (target_hit or 0) + 2) or (r.month % 3 == 0)
        if show:
            print(f"{r.month:>3} {r.new_clients:>5.1f} {r.active_clients:>7.1f} "
                  f"${r.mrr:>10,.0f} ${r.total_revenue:>10,.0f} "
                  f"${r.net_cash:>10,.0f} ${r.cumulative_cash:>11,.0f}{flag}")

    print(bar)
    print("Summary")
    print("-" * 78)
    if breakeven_hit:
        print(f"  Cash-flow positive month : {breakeven_hit}")
    if target_hit:
        r = rows[target_hit - 1]
        print(f"  Hit ${a.target_mrr:,.0f}/mo MRR    : month {target_hit} "
              f"(~{r.active_clients:.0f} active clients)")
        print(f"  Annualized at target     : ${r.mrr*12:,.0f}/yr recurring")
    else:
        last = rows[-1]
        print(f"  Did NOT hit target in {a.months} months. "
              f"Month {a.months} MRR = ${last.mrr:,.0f} ({last.active_clients:.0f} clients).")
        print("  Lever ideas: raise avg retainer (push Growth/Scale), "
              "increase new-clients/mo, or cut churn.")
    print("  Cumulative cash by end   : ${:,.0f}".format(rows[-1].cumulative_cash))
    print(bar)
    print("Tip: re-run with flags, e.g.")
    print("  python3 financial_model.py --avg-retainer 3000 --new-clients 3 --churn 0.02")
    print(bar)


def apply_overrides(a: Assumptions, args: argparse.Namespace) -> Assumptions:
    if args.target is not None:
        a.target_mrr = args.target
    if args.months is not None:
        a.months = args.months
    if args.churn is not None:
        a.monthly_churn = args.churn
    if args.new_clients is not None:
        a.flat_new_clients = args.new_clients
    if args.avg_retainer is not None:
        # collapse mix to a single effective tier at the requested retainer
        # by scaling: keep mix shape but rescale retainers proportionally
        base = a.avg_retainer
        scale = args.avg_retainer / base
        for t in TIERS:
            TIERS[t]["retainer"] *= scale
    return a


def main() -> None:
    p = argparse.ArgumentParser(description="RealtyFlow MRR projection")
    p.add_argument("--target", type=float, help="Target MRR (default 45000)")
    p.add_argument("--months", type=int, help="Months to project (default 36)")
    p.add_argument("--churn", type=float, help="Monthly churn fraction, e.g. 0.025")
    p.add_argument("--new-clients", type=float, dest="new_clients",
                   help="Flat new clients/month (overrides ramp)")
    p.add_argument("--avg-retainer", type=float, dest="avg_retainer",
                   help="Force average retainer/client/mo")
    args = p.parse_args()

    a = Assumptions()
    a = apply_overrides(a, args)
    rows = project(a)
    render(a, rows)


if __name__ == "__main__":
    main()

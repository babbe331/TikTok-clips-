#!/usr/bin/env python3
"""
Monthly client ROI report — email generator.

Turns a client's monthly numbers into a polished, client-facing ROI email using
Claude. This is your #1 retention tool (see onboarding/retention_sop.md). Run it
once a month per client, paste the output into your email tool, send.

Setup (one time):
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...      # your key

Usage:
    python3 generate_report_email.py \
        --client "Smith Group Realty" --agency "RealtyFlow" \
        --period "May 2026" --leads 142 --responded-pct 100 \
        --booked 38 --deals 3 --commission 9000 --retainer 3000

With no API key set, it prints the exact prompt instead of calling the API, so
you can paste it into claude.ai manually. Nothing breaks without a key.
"""
from __future__ import annotations

import argparse
import os
import sys

# Latest, most capable Claude model for this reasoning/writing task.
MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = (
    "You are preparing a monthly results summary for a real estate client of "
    "{agency}. Given the metrics, write a concise, confident, client-facing "
    "email that frames the ROI in DOLLARS (use the client's average commission "
    "to value booked/influenced deals against their retainer). Be honest: if a "
    "metric dipped, name it and the fix. 150-200 words, warm but professional, "
    "no emojis, no jargon. Never reference protected classes. End with ONE "
    "specific recommendation for next month and a clear, low-pressure sign-off."
)


def build_user_prompt(a: argparse.Namespace) -> str:
    roi = a.deals * a.commission
    multiple = roi / a.retainer if a.retainer else 0
    touches = a.leads * 12
    return (
        f"Client: {a.client}\n"
        f"Reporting period: {a.period}\n"
        f"Leads handled: {a.leads}\n"
        f"% responded within 5 min: {a.responded_pct}%\n"
        f"Follow-up touches sent: {touches}\n"
        f"Appointments booked: {a.booked}\n"
        f"Deals influenced: {a.deals}\n"
        f"Average commission: ${a.commission:,}\n"
        f"Monthly retainer: ${a.retainer:,}\n"
        f"Estimated influenced pipeline value: ${roi:,} "
        f"(~{multiple:.1f}x the retainer)\n"
        f"From me (the agency): {a.agency}.\n"
        "Write the client-facing email now."
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Generate a monthly client ROI email")
    p.add_argument("--client", required=True)
    p.add_argument("--agency", default="RealtyFlow")
    p.add_argument("--period", required=True, help='e.g. "May 2026"')
    p.add_argument("--leads", type=int, required=True)
    p.add_argument("--responded-pct", type=int, default=100, dest="responded_pct")
    p.add_argument("--booked", type=int, required=True)
    p.add_argument("--deals", type=int, required=True, help="deals influenced")
    p.add_argument("--commission", type=int, required=True, help="avg commission $")
    p.add_argument("--retainer", type=int, required=True, help="their monthly retainer $")
    a = p.parse_args()

    system = SYSTEM_PROMPT.format(agency=a.agency)
    user = build_user_prompt(a)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("=" * 70)
        print("No ANTHROPIC_API_KEY found — printing the prompt to paste into")
        print("claude.ai manually. (Set the key + `pip install anthropic` to")
        print("generate automatically.)")
        print("=" * 70)
        print("\n[SYSTEM]\n" + system)
        print("\n[USER]\n" + user)
        return

    try:
        import anthropic
    except ImportError:
        sys.exit("Run `pip install anthropic` first (or unset the key to print the prompt).")

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    print("=" * 70)
    print(f"ROI report email for {a.client} — {a.period}")
    print("=" * 70)
    print(msg.content[0].text)


if __name__ == "__main__":
    main()

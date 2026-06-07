# Follow-Up Sequence — the 90-day, 14-touch nurture

This is the cadence the Follow-Up Engine ([`../workflows/02_followup_engine.json`](../workflows/02_followup_engine.json))
runs. Front-loaded: most replies happen in week 1, so you touch hard early, then
taper to stay top-of-mind. The AI personalizes each base template to the lead's
area/budget/timeline and the agent's voice.

**Channels:** SMS for speed/immediacy, email for substance. Alternate.
**Stop conditions:** lead replies, books, converts, or sends STOP/unsubscribe.

| # | When | Channel | Goal | Base template |
| --- | --- | --- | --- | --- |
| 1 | 0 min | SMS | Speed-to-lead | "Hi {first}, it's {agent} with {brokerage}. Got your inquiry about {area} — are you hoping to buy in the next few months or just starting to look?" |
| 2 | 1 hr | Email | Add value | Subject: "A few {area} homes you might like" — 3 handpicked listings + offer to set up a saved search. |
| 3 | Day 1 | SMS | Soft nudge | "Hi {first}, did any of those {area} listings stand out? Happy to dig up more in your price range." |
| 4 | Day 3 | Email | Educate | Subject: "What's actually happening in the {area} market" — short market snapshot, position agent as the expert. |
| 5 | Day 7 | SMS | Re-engage | "Still thinking about a move, {first}? No rush — just let me know if you'd like me to keep an eye out." |
| 6 | Day 10 | Email | Remove friction | Subject: "The 3 things that trip up {area} buyers" — helpful guide, link to free buyer/seller guide (SEO lead magnet). |
| 7 | Day 14 | SMS | Offer the call | "Would a quick 10-min call help, {first}? I can walk you through next steps with zero pressure: {booking_link}" |
| 8 | Day 21 | Email | Social proof | Subject: "How the {family/buyer} found their place in {area}" — a short client story. |
| 9 | Day 30 | SMS | Check timeline | "Hey {first}, has your timeline shifted at all? Want me to keep sending {area} listings or pause for now?" |
| 10 | Day 45 | Email | Re-offer value | Subject: "New to the {area} market this week" — fresh listings, low-key. |
| 11 | Day 60 | SMS | Pattern interrupt | "{first}, quick one — still on the fence, actively looking, or should I close your file for now? Totally fine either way." |
| 12 | Day 75 | Email | Resource | Subject: "Your {area} home-buying checklist" — useful PDF, keeps you helpful not pushy. |
| 13 | Day 90 | SMS | Breakup | "Hi {first}, I don't want to crowd your inbox. I'll pause for now — reply anytime and I'm right here when you're ready." |
| 14 | Day 90 | Email | Long-term list | Subject: "Staying in touch" — invite to monthly market newsletter (moves them to long-nurture list, not dead). |

## Why this converts

- **Touch 1 in under a minute** is the single biggest lever — see
  [`../seo/articles/speed-to-lead.md`](../seo/articles/speed-to-lead.md).
- **The "breakup" (touch 11 & 13)** consistently reactivates leads who'd gone
  silent — giving people an easy out makes them re-engage.
- **Never a dead end:** even non-responders land on the monthly newsletter, so a
  lead bought 6 months from now still closes through your client.

## Compliance notes

- First SMS only goes to leads who submitted contact info / consented at opt-in.
- Every SMS path can append the client's `STOP to opt out` per their policy.
- Cap sends per contact per day; respect quiet hours (no SMS 9pm–8am local).

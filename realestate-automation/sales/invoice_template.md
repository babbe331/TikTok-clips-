# Invoice Template

> Use in Stripe Invoicing / QuickBooks / Wave (all have free tiers). This is the
> content; the tool handles payment + reminders. Recurring retainers should be a
> **Stripe subscription** so they auto-charge — never chase a retainer by hand.

---

**INVOICE**

**RealtyFlow** ({Your LLC})
{address} · {email} · {phone}

**Bill to:** {Client Brokerage}, {contact name}
**Invoice #:** {YYYYMM}-{client}-{n}
**Date:** {date} · **Due:** on receipt / Net 0

| Description | Qty | Amount |
| --- | --- | --- |
| RealtyFlow System — setup & build ({tier}) | 1 | ${setup} |
| Monthly retainer — {Month Year} | 1 | ${retainer} |
| _(SMS/email/AI pass-through, if billed)_ | — | ${passthrough} |
| **Total due** | | **${total}** |

**Pay:** {Stripe payment link}
Terms: per the signed service agreement. Retainer auto-renews monthly until
cancelled with 30 days' notice.

Thank you — {Your Name}

---

## Billing cadence (set once, runs itself)
- **Setup fee:** one-time invoice on signing, before build starts.
- **Retainer:** Stripe **subscription**, charged the 1st of each month in advance.
- **Pass-through costs:** either bundle into the retainer (simpler) or bill at
  cost monthly. Bundling is cleaner for a solo operator — pick a tier price that
  covers expected usage.
- **Failed payment:** Stripe auto-retries + emails. If it fails twice, pause the
  workflows and call them — don't let unpaid service run.

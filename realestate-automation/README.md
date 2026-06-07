# RealtyFlow — A One-Person AI Automation Business for Real Estate Agencies

> A silent, AI-powered income system. No employees. No funding. No hype.
> It solves one painful, recurring B2B problem — **agencies bleed leads** —
> and turns that into **compounding monthly retainer revenue.**

**Goal:** Scale to **$45,000/month recurring** as a solo operator using
no-code workflows, recurring retainers, and SEO traffic.

---

## The one-sentence business

> *I install "done-for-you" AI systems that qualify a real estate agency's
> leads in 60 seconds, follow up 100+ times until they book, and onboard new
> clients automatically — then I maintain it for a flat monthly retainer.*

## Why this works (the painful problem)

Real estate agencies spend thousands per month on leads (Zillow, Facebook,
Google) and then **lose 40–60% of them** because:

- Agents reply to web leads in *hours*, not minutes. [Speed-to-lead is the #1 predictor of conversion.](seo/articles/speed-to-lead.md)
- Nobody follows up more than 1–2 times. Most deals close after 5–12 touches.
- Onboarding a new buyer/seller is manual paperwork that eats hours per client.

Every one of those is a **no-code automation**. Agencies will happily pay a
recurring retainer to never think about it again — because the system pays
for itself with **one saved deal** (a single commission is $5k–$15k+).

## 👉 New here? Open [`START_HERE.md`](START_HERE.md)

It's the short checklist of the only steps that require *you* — everything else
in this repo is already built.

## What's in this repository

| Folder | What it is |
| --- | --- |
| [`START_HERE.md`](START_HERE.md) | The human-only launch checklist, in order |
| [`BUSINESS_PLAN.md`](BUSINESS_PLAN.md) | The full strategy: niche, offer, pricing, path to $45k |
| [`site/`](site/) | Deployable marketing site (`index.html`) + client ROI dashboard (`dashboard.html`) |
| [`financial_model.py`](financial_model.py) | Runnable model that projects MRR → $45k/month |
| [`workflows/`](workflows/) | Importable no-code blueprints (n8n / Make) for the 3 core systems |
| [`templates/`](templates/) | Email + SMS follow-up sequences you deploy for clients |
| [`outreach/`](outreach/) | Cold email, DM, and Loom scripts to land the first 10 clients |
| [`sales/`](sales/) | Proposal, pricing, and retainer agreement templates |
| [`onboarding/`](onboarding/) | Client intake form, onboarding checklist, and SOPs |
| [`seo/`](seo/) | Keyword map, content calendar, and ready-to-publish articles |

## The 90-day quick start

1. **Day 1–7:** Pick your sub-niche (see plan). Stand up the 3 workflows from
   [`workflows/`](workflows/) in a free n8n/Make account. Record 1 demo Loom.
2. **Day 8–30:** Run the [outreach scripts](outreach/). Book 10 demos. Land
   2–3 founding clients at a discounted rate in exchange for testimonials.
3. **Day 31–60:** Deliver flawlessly. Publish 2 [SEO articles](seo/)/week.
   Ask for referrals. Raise prices for new clients.
4. **Day 61–90:** Productize delivery (templatized onboarding). You should be
   at **$5k–$10k MRR**. Now it compounds. See the model for the full curve.

## Run the financial model

```bash
python3 realestate-automation/financial_model.py
```

It prints a month-by-month projection to $45k/month and shows the levers
(new clients/mo, churn, average retainer) that get you there fastest.

---

*This is an operating playbook, not financial advice. Numbers are planning
assumptions you should replace with your real pipeline data.*

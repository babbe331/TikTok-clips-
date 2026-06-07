# START HERE — your launch checklist

Everything buildable is already built and in this folder. This page is the short
list of things **only you can do** (they need your legal identity, your money, or
your voice), in the order to do them. Check them off and you're in business.

> Legend: 🟢 = 15 min · 🟡 = ~1 hr · 🔴 = a few hours / ongoing
> 💲 = costs money. Everything not marked 💲 is free.

---

## Phase 0 — Decide (30 min, free)
- [ ] 🟢 Pick your **business name** (default in all assets is "RealtyFlow" — find/replace to change).
- [ ] 🟢 Pick your **target city/metro + niche** (default: residential buyer's-agent teams, 3–15 agents). This decides who you email and what SEO you target.
- [ ] 🟢 Decide hours/week you can commit. This works at ~10 hrs/wk; it's faster at 20+.

*Want me to tailor every asset to a specific name + city? Tell me both and I'll do a pass.*

## Phase 1 — Become a real business (a few days, mostly waiting)
- [ ] 🟡 💲 Register an **LLC** (your state's site or a service; ~$50–300). *Only you can — it's your legal identity.*
- [ ] 🟢 💲 Buy a **domain** (~$12/yr) + set up a business email (Google Workspace ~$6/mo).
- [ ] 🟢 💲 Open a **Stripe** account for invoicing (free to start; takes a % per charge).
- [ ] 🟢 Read [`onboarding/compliance_checklist.md`](onboarding/compliance_checklist.md) and have a lawyer glance at [`sales/retainer_agreement.md`](sales/retainer_agreement.md) before you sign anyone.

## Phase 2 — Stand up the product (one afternoon, ~free to start)
- [ ] 🔴 Create a free **n8n** (cloud or self-host) or **Make** account.
- [ ] 🟡 Import the 3 blueprints from [`workflows/`](workflows/) (`Import from File`).
- [ ] 🟡 💲 Get an **Anthropic API key** (usage-based, cents per lead) and a **Twilio** trial number.
- [ ] 🔴 Wire one workflow end-to-end and get a **fake lead to text you back in 60 seconds**. That's your demo and your proof.
- [ ] 🟡 Load the prompts from [`workflows/PROMPTS.md`](workflows/PROMPTS.md), customizing the `[BRAND]` bits.

## Phase 3 — Build your storefront (1 hr, ~free)
- [ ] 🟢 Open [`site/index.html`](site/index.html), find/replace the name, domain, and email placeholders.
- [ ] 🟢 Create a free **Formspree** account; paste your form ID into the audit form (`YOUR_FORM_ID`).
- [ ] 🟢 Deploy free: push to **GitHub Pages**, Netlify, or Vercel. Now you have a live site.
- [ ] 🟢 Skim [`site/dashboard.html`](site/dashboard.html) — that's the monthly report you'll send clients to keep them.

## Phase 4 — Record the demo (1 hr, free) — *only you can do this*
- [ ] 🔴 Record the **4-minute Loom** using the script in [`outreach/cold_outreach.md`](outreach/cold_outreach.md). Screen-record your working workflow. This closes deals for months.

## Phase 5 — Land the first clients (ongoing — this is the real job)
- [ ] 🔴 Build a list of **100 target teams** into [`outreach/prospects.csv`](outreach/prospects.csv) (Zillow team pages, "top real estate teams [city]", LinkedIn, IG).
- [ ] 🔴 Run the **outreach scripts** — ~30 personalized touches/day. Goal: book 10 demos.
- [ ] 🔴 💲 Close **2 founding clients** at a discount for a testimonial. Use [`sales/proposal_template.md`](sales/proposal_template.md) + the agreement.
- [ ] 🔴 Deliver flawlessly with [`onboarding/client_onboarding_checklist.md`](onboarding/client_onboarding_checklist.md). Live in 14 days.

## Phase 6 — Make it compound (ongoing)
- [ ] 🔴 Publish **2 articles/week** ([`seo/content_calendar.md`](seo/content_calendar.md)) — 5 are already drafted in [`seo/articles/`](seo/articles/).
- [ ] 🟢 Send every client a **monthly ROI report** (the dashboard) — this is what beats churn.
- [ ] 🟢 Ask every happy client for **a referral + a testimonial**.
- [ ] 🟢 Re-run `python3 financial_model.py` monthly with your **real** numbers to track the path to $45k.

---

## The honest bottom line

I built the website, the workflows, the prompts, the sequences, the scripts, the
contracts, the SOPs, the dashboard, and the content. **What's left is the part
that's irreducibly yours:** registering the business, putting your name on the
accounts, recording your face/voice in the demo, and talking to prospects.

That last one — sales — is the real engine. No tool, AI included, closes your
first client for you. But you're starting with the whole machine already
built, which is more than 99% of people who try this ever have.

**Pick your name and city and tell me — I'll personalize every file to it next.**

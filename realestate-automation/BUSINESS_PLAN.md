# RealtyFlow — Business Plan

A solo, AI-powered automation studio that sells **recurring retainers** to real
estate agencies. The product is *outcomes* (more booked appointments, less
manual work), delivered through no-code workflows you build once and reuse.

---

## 1. The market and the niche

**Don't sell to "real estate."** Pick one beachhead so your messaging, case
studies, and SEO compound. Ranked options:

| Sub-niche | Why it's good | Avg deal value to them |
| --- | --- | --- |
| **Residential buyer's-agent teams (3–15 agents)** ⭐ | Big enough to have a lead budget, small enough to lack ops staff. Feel the pain daily. | $8k–$12k/commission |
| Property management firms | Recurring tenant/maintenance workflows; sticky | Lower urgency |
| New-construction / developer sales | High ticket, long nurture cycles | $15k+/commission |
| Commercial brokerages | Fewer, larger; longer sales cycle to *you* | Very high |

**Recommended beachhead:** residential buyer's-agent teams of 3–15 agents in
2–3 mid-size metros. They have lead spend, no full-time ops person, and talk to
each other (referrals compound).

**Their core pain, quantified:** a team buying 100 leads/month at $40 each
($4,000) that converts 2% closes ~2 deals. Improve speed-to-lead and follow-up
and that becomes 3–4%. **One extra deal/month ≈ $8k–$12k.** Your $2k retainer is
a rounding error against that. This is the entire sales argument.

## 2. The offer (productized, not custom)

You sell **one transformation** in three packaged tiers. Same core build,
different scope — so delivery stays templatized.

### The core build ("The RealtyFlow System")

Three no-code systems, deployed into the client's existing CRM/tools:

1. **Lead Qualifier** — Every inbound lead (web form, Zillow, FB, portal) hits
   an AI qualifier within ~60s: scores intent, captures budget/timeline/area,
   books hot leads straight onto an agent's calendar, routes the rest to nurture.
   → [`workflows/01_lead_qualifier.json`](workflows/01_lead_qualifier.json)
2. **Follow-Up Engine** — Multi-channel (email + SMS) sequence that touches each
   lead 12–20 times over 90 days with AI-personalized messages until they book,
   reply STOP, or convert. → [`workflows/02_followup_engine.json`](workflows/02_followup_engine.json)
3. **Client Onboarding** — When a lead becomes a client, auto-send the welcome
   packet, e-sign agreement, intake form, and create their deal record + folder.
   → [`workflows/03_client_onboarding.json`](workflows/03_client_onboarding.json)

### Pricing (the path to $45k is built on this)

| Tier | Setup (one-time) | Retainer (monthly) | Scope |
| --- | --- | --- | --- |
| **Starter** | $1,500 | **$1,500/mo** | Lead Qualifier + basic email follow-up. 1 lead source. |
| **Growth** ⭐ | $2,500 | **$3,000/mo** | All 3 systems, email+SMS, up to 3 lead sources, monthly reporting. |
| **Scale** | $4,000 | **$5,000/mo** | Growth + AI voice/missed-call-text-back, multiple teams, priority SLA, quarterly strategy. |

**Why retainers (not one-time projects):** the systems need monitoring,
copy refreshes, deliverability management, new-portal integrations, and
reporting. You're selling *peace of mind + ongoing optimization*, which is a
real, recurring job — not a maintenance fee for nothing. Anchor every proposal
to ROI: "this finds you 1+ extra deal/month; it costs less than one."

### Why it compounds every month

- **Retainers stack.** Month 12's revenue includes month 1's clients (minus
  churn). New sales add on top of a base that's already paid.
- **Delivery cost falls.** Client #10 is built from templates you perfected on
  clients #1–9. Margin rises as you scale.
- **SEO is an appreciating asset.** Articles ranked in month 3 still pull leads
  in month 18 at near-zero marginal cost. → [`seo/`](seo/)
- **Referrals network within the niche.** Agents switch brokerages and bring you
  with them; team leads talk at mastermind groups.

## 3. Go-to-market (how you land clients)

Three channels, run in this order of priority:

1. **Direct outreach (months 1–4, your engine for the first ~15 clients).**
   Cold email + LinkedIn/Instagram DMs + Loom demos. Scripts in
   [`outreach/`](outreach/). Target: 30 personalized touches/day → 10 demos/mo
   → 2–4 closes/mo.
2. **SEO + content (months 2+, the compounding flywheel).** Rank for the exact
   phrases agency owners search: "real estate lead follow up automation,"
   "speed to lead crm," "zillow lead automation." Publish 2 articles/week,
   each ending in a free-audit CTA. → [`seo/content_calendar.md`](seo/content_calendar.md)
3. **Referrals + partnerships (months 4+).** Every happy client = referral ask +
   case study. Partner with CRM consultants, ISAs, and real estate coaches who
   serve the same buyer but don't do automation.

## 4. The tech stack (no-code, low fixed cost)

| Job | Tool (pick one) | ~Cost |
| --- | --- | --- |
| Workflow automation | **n8n** (self-host or cloud) or **Make** | $0–$50/mo |
| AI brain | Claude API (`claude-opus-4-8` / `claude-sonnet-4-6`) | usage-based, cents/lead |
| SMS | Twilio | usage-based |
| Email | client's domain via Postmark/SendGrid | usage-based |
| Scheduling | Cal.com / Calendly | $0–$15/mo |
| E-sign + forms | DocuSign/PandaDoc + Tally/Typeform | $0–$30/mo |
| CRM (client's) | HubSpot / Follow Up Boss / GoHighLevel | client pays |

**Your fixed overhead is ~$100–$300/month.** Everything else is usage-based and
passed through or trivial. At $45k MRR your margin is the point of this model.

> Note on AI: default to the latest Claude models. Use `claude-sonnet-4-6` for
> high-volume per-lead qualification/personalization (fast + cheap), and
> `claude-opus-4-8` for the harder reasoning (objection handling, summaries).
> See [`workflows/PROMPTS.md`](workflows/PROMPTS.md) for the exact prompts.

## 5. The numbers — path to $45,000/month

Target MRR mix (one realistic combination):

- 6 × Starter ($1,500) = $9,000
- 8 × Growth ($3,000) = $24,000
- 2 × Scale ($5,000) = $10,000 + a buffer client
- **≈ $45,000/month from ~16 clients** — a load one person can run because
  delivery is templatized and monitored, not rebuilt each time.

Plus one-time setup fees (~$2k–$2.5k each) act as a cash cushion that funds the
months you're below break-even. **Run [`financial_model.py`](financial_model.py)
for the month-by-month curve** under your own assumptions (close rate, churn,
average retainer). Default assumptions reach ~$45k MRR around **month 18–22**.

### The three levers that move the date

1. **Average retainer** — push Growth as the default; one Scale client = three
   Starters of revenue for similar effort.
2. **Net new clients/month** — driven by outreach volume early, SEO later.
3. **Churn** — the silent killer of recurring revenue. Keep it < 3%/mo by
   sending a monthly ROI report (booked appts, deals influenced). Proof of value
   is the best retention tool. See [`onboarding/retention_sop.md`](onboarding/retention_sop.md).

## 6. Risks & how the model survives them

| Risk | Mitigation |
| --- | --- |
| Churn eats growth | Monthly ROI reporting; annual prepay discount; 2-week onboarding that proves value fast |
| One platform changes pricing/API | No-code is portable; keep logic documented in [`workflows/`](workflows/) so you can migrate |
| You become the bottleneck | Productize: every delivery step is an SOP in [`onboarding/`](onboarding/); raise prices before you raise hours |
| Deliverability (spam) tanks results | Warm domains, SPF/DKIM/DMARC, send caps — built into the follow-up engine |
| Compliance (SMS/TCPA, fair housing) | Consent capture + STOP handling in workflows; never use protected-class targeting. See [`onboarding/compliance_checklist.md`](onboarding/compliance_checklist.md) |

## 7. 12-month milestones

| Month | Milestone | Approx MRR |
| --- | --- | --- |
| 1 | 3 workflows live, 1 demo Loom, outreach started | $0 |
| 2 | First 2 founding clients (discounted) | ~$3k |
| 3 | 4 clients, SEO publishing begins | ~$7k |
| 6 | 8 clients, first SEO leads, first referrals | ~$16k |
| 9 | 11 clients, raise prices, Scale tier sold | ~$26k |
| 12 | 14 clients, SEO is a real channel | ~$34k |
| 18–22 | ~16 clients, mostly inbound | **~$45k** |

This is a marathon of consistency, not a lottery ticket. The compounding is
real but it is *slow then fast* — most of the $45k arrives in the back half.

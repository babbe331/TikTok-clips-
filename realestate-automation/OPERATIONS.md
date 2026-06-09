# Operations Manual — how you actually run this week to week

The business is built. This is the operating rhythm that runs it. Following a
fixed cadence is what lets one person handle 16+ clients without dropping balls.
Time estimates assume ~10–15 focused hrs/week early, dropping per-client as you
templatize.

---

## Daily (≈2 hrs, mostly Phase 1–2 of the business)
- [ ] **Outreach block (60–90 min):** 30 personalized touches (see
      [`outreach/cold_outreach.md`](outreach/cold_outreach.md)). Log every one in
      [`outreach/prospects.csv`](outreach/prospects.csv).
- [ ] **Reply block (20 min):** respond to every inbound reply within the hour.
      Book any positive into a discovery call this week.
- [ ] **System check (10 min):** glance at each live client's workflow runs.
      Errors? Fix before the client notices. (This is the retainer's value.)

## Weekly (≈4 hrs)
- [ ] **Mon — Publish article A** + repurpose to LinkedIn + email list.
- [ ] **Thu — Publish article B** + repurpose to an IG carousel.
- [ ] **Discovery calls** as booked (use [`sales/discovery_call_script.md`](sales/discovery_call_script.md)).
- [ ] **Pipeline review (30 min):** move every prospect forward one step. Anyone
      gone cold? One more value-add touch, then archive.
- [ ] **Follow-up on proposals** sent but not signed.

## Monthly (per client, ≈30 min each)
- [ ] **Send the ROI report** ([`site/dashboard.html`](site/dashboard.html) →
      print to PDF, or run [`generate_report_email.py`](generate_report_email.py)).
- [ ] **Ship one improvement** to each client's system (new source, fresh copy).
- [ ] **Ask happy clients** for a referral + testimonial.
- [ ] **Re-run** `python3 financial_model.py` with real numbers. Are you on the
      curve to $45k? Which lever (retainer / new clients / churn) is lagging?

## Quarterly
- [ ] Strategy call with each client (retention).
- [ ] Raise prices for **new** clients once you have testimonials + a waitlist.
- [ ] Review your stack costs; renegotiate or consolidate tools.
- [ ] Audit compliance ([`onboarding/compliance_checklist.md`](onboarding/compliance_checklist.md)).

---

## The phase you're in determines where your hours go

| Stage | MRR | Where your time goes |
| --- | --- | --- |
| **Launch** (mo 1–3) | $0–7k | 70% outreach, 20% delivery, 10% content |
| **Traction** (mo 4–9) | $7–25k | 40% delivery, 30% outreach, 30% content/SEO |
| **Compounding** (mo 10+) | $25k+ | 50% delivery + retention, 40% content, 10% inbound sales |

Notice the shift: early on you hunt; later, content + referrals feed you and you
mostly deliver and retain. **Retention quietly becomes the whole game** — a 2%
vs 3% churn rate is the difference between plateauing under $45k and sailing past
it (run the model and see).

## The one rule that protects the business
**Never let a paying client's system fail silently.** Set up error alerts on
every workflow. The fastest way to lose recurring revenue is a client
discovering — before you do — that their leads stopped getting answered. The
daily 10-minute system check is non-negotiable.

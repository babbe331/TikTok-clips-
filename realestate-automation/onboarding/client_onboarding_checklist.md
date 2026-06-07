# Client Onboarding SOP — go live in 14 days, every time

This is *your* process for onboarding a new paying client. Templatizing this is
what lets one person run 16+ clients. Do it the same way every time.

## Day 0 — Signed
- [ ] Countersign agreement, send Stripe/ACH link for setup fee + first month
- [ ] Send the welcome email + the [intake form](intake_form.md) (kickoff link)
- [ ] Create their folder from the template (workflows, creds vault, reporting)
- [ ] Schedule the 30-min kickoff call within 3 business days

## Day 1–3 — Access & kickoff call
- [ ] Collect access: CRM, lead sources (Zillow/FB/website), sending domain,
      Calendly/Cal.com, e-sign account
- [ ] Confirm sending domain has SPF, DKIM, DMARC (deliverability is non-negotiable)
- [ ] Capture brand voice samples (3 of their best past emails/texts)
- [ ] Confirm average commission + current response time (for the ROI baseline)

## Day 3–7 — Build
- [ ] Clone the 3 workflow templates into their environment
- [ ] Wire credentials; load brand voice into the [prompts](../workflows/PROMPTS.md)
- [ ] Connect lead-source webhooks
- [ ] Load the [follow-up sequence](../templates/followup_sequence.md), tailored
- [ ] Set up the monthly reporting dashboard

## Day 7–12 — Test (use the [workflow test checklist](../workflows/README.md#test-checklist))
- [ ] Submit fake HOT / WARM / COLD leads, verify routing + timing
- [ ] Verify STOP suppresses future sends
- [ ] Verify won-deal onboarding fires once (idempotency)
- [ ] Have the client submit a test lead themselves (builds trust + catches gaps)

## Day 12–14 — Go live
- [ ] Flip to live lead sources
- [ ] Send "you're live" email with what to expect in week 1
- [ ] Set a 7-day check-in and the 30-day first-report date
- [ ] Move deal to "Active — Retainer" in your own CRM

## Day 30 — First ROI report (the retention moment)
- [ ] Send the [monthly report](../workflows/PROMPTS.md#monthly-report-opus)
- [ ] Ask for a testimonial + 1 referral if results are good
- [ ] Note any upsell to a higher tier

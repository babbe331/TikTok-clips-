# Workflows — the no-code core you deploy for every client

These are the three systems that make up "The RealtyFlow System." They're
written as **portable JSON blueprints** in n8n's node format. The structure maps
1:1 onto Make.com scenarios if you prefer that platform — the logic is what
matters, not the vendor.

> ⚠️ These are **templates/blueprints**, not plug-and-play production files. You
> must add your own credentials (Twilio, email, CRM, Claude API key) and adjust
> node parameters to the client's stack. Treat them as the wiring diagram.

| File | System | Trigger | Outcome |
| --- | --- | --- | --- |
| [`01_lead_qualifier.json`](01_lead_qualifier.json) | Lead Qualifier | New lead webhook | Scored lead, hot ones booked, CRM updated |
| [`02_followup_engine.json`](02_followup_engine.json) | Follow-Up Engine | Lead enters nurture | 12–20 multi-channel touches until booked |
| [`03_client_onboarding.json`](03_client_onboarding.json) | Client Onboarding | Deal stage = "Won" | Welcome packet + e-sign + intake + folder |

## How to deploy (per client, ~2–4 hours once templatized)

1. Spin up n8n (cloud or self-hosted) or a Make account.
2. Import the three JSON files (`Import from File`).
3. Add credentials: Claude API, Twilio, email (Postmark/SendGrid), the client's
   CRM (Follow Up Boss / HubSpot / GoHighLevel), Cal.com/Calendly.
4. Point the webhook URL at the client's lead sources (Zillow, FB Lead Ads form,
   website form → Zapier/native webhook).
5. Replace the merge fields and load the client's branding/voice into the
   prompts (see [`PROMPTS.md`](PROMPTS.md)).
6. Run the [test checklist](#test-checklist) before going live.

## Compliance is built in, not bolted on

- **SMS:** consent is captured at opt-in; every message path honors `STOP`
  (the follow-up engine checks an unsubscribe flag before each send).
- **Fair housing:** prompts are instructed to never reference or infer
  protected classes. See [`../onboarding/compliance_checklist.md`](../onboarding/compliance_checklist.md).
- **Deliverability:** sends are throttled and require SPF/DKIM/DMARC on the
  client's sending domain.

## Test checklist

- [ ] Submit a fake lead → qualifier responds in < 90s
- [ ] Hot lead (budget + timeline + pre-approved) → booking link sent + slot held
- [ ] Cold lead → enters follow-up sequence, not booking
- [ ] Reply `STOP` → all future sends suppressed for that contact
- [ ] Won deal → onboarding packet fires once, no duplicates
- [ ] CRM record shows the AI's qualification notes

# Compliance Checklist — don't skip this

You're sending automated SMS/email and touching housing leads. Two bodies of law
matter most. **This is not legal advice** — confirm specifics with counsel for
your jurisdiction. But these defaults keep you and your clients out of trouble.

## SMS / TCPA (consent + opt-out)
- [ ] Only text leads who provided their number AND consented to be contacted
      (form opt-in language present at capture). The **client warrants this** in
      the [agreement](../sales/retainer_agreement.md) §6.
- [ ] Every SMS path honors **STOP/UNSUBSCRIBE** immediately and permanently —
      built into the [Follow-Up Engine](../workflows/02_followup_engine.json)
      ("Still Active?" guard checks the unsubscribe flag before every send).
- [ ] Respect **quiet hours** — no SMS before 8am or after 9pm local to the lead.
- [ ] Register for **A2P 10DLC** with the SMS provider (Twilio) per client brand.
- [ ] Include the client's business identity in messaging where required.

## Fair Housing
- [ ] Prompts are explicitly instructed to **never reference, infer, or target
      protected classes** (race, color, religion, national origin, sex, familial
      status, disability) — see [`../workflows/PROMPTS.md`](../workflows/PROMPTS.md).
- [ ] Lead scoring uses **only transaction-readiness signals** (budget,
      timeline, financing, area) — never demographic proxies.
- [ ] Ad/audience targeting (if you ever touch it) avoids housing-discrimination
      categories.

## Email
- [ ] CAN-SPAM: valid from-address, physical mailing address, working unsubscribe
- [ ] Sending domain has **SPF, DKIM, DMARC** configured (also protects results)
- [ ] Honor unsubscribes across the whole sequence, not just one message

## Data
- [ ] Store credentials in a secrets manager, not in workflow JSON
- [ ] Client owns its lead data; you process it on their behalf (documented in
      the agreement)
- [ ] Have a deletion/export process for when a client offboards

## Your own business
- [ ] Form an LLC; keep business banking separate
- [ ] Get errors & omissions / general liability insurance once you have a few
      clients
- [ ] Use the [retainer agreement](../sales/retainer_agreement.md) with every
      client — never operate on a handshake

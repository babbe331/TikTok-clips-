# 💸 The Banned Prompts Vault — your high-margin backend

This folder is the **owned product** your `MONEY_PLAYBOOK.md` names as *"the lever
that actually gets you to $1M"* — ~90% margin, and the one money step a bot can
build for you end-to-end. It's already written. Here's how to turn it on.

## What's here
| File | What it is |
|---|---|
| `BANNED_PROMPTS_VAULT.md` | The product itself — 40 prompts across 6 packs. This is what the buyer downloads. |
| `sales_page.html` | The landing page. Bio-link traffic lands here and clicks through to checkout. |
| `README.md` | This file. |

The matching top-of-funnel content is in `../content/banned_prompts_batch.md` —
12 ready-to-post clips that drive viewers to the bio link.

## Switch it on (≈30 min, the human steps a bot can't do)
1. **Create a checkout.** Free account on [Gumroad](https://gumroad.com) or
   [Lemon Squeezy](https://lemonsqueezy.com). New digital product, price **$27**.
2. **Upload the deliverable.** Attach `BANNED_PROMPTS_VAULT.md` (or export it to
   PDF first — cleaner for buyers). Connect your payout (Stripe/PayPal).
3. **Wire the page.** Open `sales_page.html`, replace both
   `REPLACE_WITH_YOUR_CHECKOUT_LINK` placeholders with your checkout URL.
   Host the page free on GitHub Pages (this repo already has `.nojekyll`).
4. **Put the page URL in your TikTok / IG / YT bio.**
5. **Post the content batch**, one clip a day, each pointing at the bio.

## The funnel
```
Banned Prompt clip  →  "link in bio"  →  sales_page.html  →  $27 checkout  →  payout
```

## Log every sale into the engine
```bash
python3 money_engine.py log-revenue 27 product "vault sale"
python3 money_engine.py status        # watch it move against the $1M line
```

## The honest part
The asset is done; the dollars still need the human steps above and consistent
posting. No file makes money sitting in a repo — it makes money once it's live
and in front of the traffic your clips create. Everything that *could* be built
for you, is. The rest is execution.

# 🔗 Farmlind Slack Connector

This is the small always-on service that lets the Farmlind app pull orders
**automatically** from Slack. Once it's set up, Matt just posts an order in your
Slack channel and it appears in the app — no extra steps for him.

```
David
one heirloom tomato
three roma tomatoes
two cases romaine
```
↑ First line = customer, each line after = quantity + product.

You only set this up **once**. Here's how.

---

## What you'll need
- A free hosting account (we use **Render.com** below — Railway, Fly.io, or Glitch also work).
- Permission to **create/install a Slack app** in your workspace (workspace admin).

---

## Step 1 — Deploy this connector

**Easiest path (Render.com, free):**
1. Make sure this project is on GitHub (it is).
2. Go to **render.com → New → Web Service** and connect your GitHub repo.
3. Set:
   - **Root Directory:** `slack-connector`
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`
4. Add **Environment Variables** (Step 3 explains the Slack one):
   - `APP_KEY` → make up a secret word (you'll paste it into the app too)
   - `SLACK_SIGNING_SECRET` → from your Slack app (Step 2)
   - `SLACK_CHANNEL` → *(optional)* the channel ID to listen to
5. Deploy. Render gives you a URL like `https://farmlind-connector.onrender.com`. Keep it.

Verify it's up by visiting `https://YOUR-URL/health` — you should see `{"ok":true,...}`.

---

## Step 2 — Create the Slack app
1. Go to **api.slack.com/apps → Create New App → From scratch**. Name it "Farmlind Orders", pick your workspace.
2. **Basic Information →** copy the **Signing Secret** → put it in Render as `SLACK_SIGNING_SECRET`, then redeploy.
3. **Event Subscriptions → turn On.**
   - **Request URL:** `https://YOUR-URL/slack/events` (it should show *Verified ✓*).
   - Under **Subscribe to bot events**, add `message.channels` (public channels) and/or `message.groups` (private).
4. **OAuth & Permissions →** make sure the bot has `channels:history` (and `groups:history` for private channels). **Install the app to your workspace.**
5. In Slack, **invite the bot to the channel** where orders are posted: `/invite @Farmlind Orders`.

*(To find a channel's ID for `SLACK_CHANNEL`: in Slack, click the channel name → it's at the bottom of the popup, like `C0123ABC`.)*

---

## Step 3 — Connect the app
1. Open the Farmlind app → top bar → **🔗 Slack**.
2. Paste the **connector web address** (from Step 1) and the **access key** (`APP_KEY`).
3. Tick **Automatically pull new Slack orders** → **Save**.

Done. Post a test order in the channel and it shows up in **Orders** within ~30 seconds.

---

## How it works (plain English)
- Slack sends each new channel message to the connector.
- The connector reads the order and holds it in a short queue.
- The app checks the queue every 30 seconds (and when it opens), creates the order,
  pulls the items from inventory, flags anything short, then clears it from the queue.

## Notes & limits
- On free hosting, the service may "sleep" when idle and take a few seconds to wake on the
  next message; orders are not lost — they queue and import once it's awake.
- Unknown customers/products are created automatically (new products start at 0 on hand, so
  they show up as "need to buy").
- Run locally for testing: `cd slack-connector && npm install && npm start`.

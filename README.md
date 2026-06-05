# 🌿 FarmLind Produce — Website

This repo now contains **two** front-end pages:

| File | What it is |
|------|------------|
| **`index.html`** | The public **marketing website** — a fast, futuristic, easy-to-navigate landing site for FarmLind Produce (hero, process, products, farms, who-we-serve, contact). Pure HTML/CSS/JS, no build step. |
| **`portal.html`** | The private **Sales & Inventory portal** app (documented below). Linked from the site footer and reachable at `…/portal.html`. |

The two pages cross-link: the site footer/contact links to the portal, and the portal's top bar has a **🌿 Main Site** button back to the homepage.

---

## 🥬 Sales & Inventory Portal (`portal.html`)

A private, single-file web app for managing produce sales and inventory. No internet,
no accounts, no installs. Everything stays **on the user's own device**.

The whole app is one file: **`portal.html`**.

---

## 🔒 Passcode

The app opens to a passcode screen. The default passcode is:

> **`farmlind`**

To change it: open `portal.html`, find the line near the top of the `<script>` that says
`const PASSCODE = "farmlind";`, and put your own word between the quotes.

Once unlocked on a device, that device stays unlocked until you press **🔒 Lock** in the
top bar. *(Note: this keeps casual visitors out. Because the app is a public web page,
the passcode isn't bank-grade security — but it's plenty to stop random people who
stumble on the link.)*

---

## Getting a clickable link (GitHub Pages)

To turn this into a normal web address you can bookmark:

1. On GitHub, go to the repo → **Settings** → **Pages** (left sidebar).
2. Under **Build and deployment → Source**, choose **Deploy from a branch**.
3. Set **Branch** to `claude/farmlind-produce-portal-orooy` and folder **`/ (root)`**, then **Save**.
4. Wait ~1 minute, then refresh. GitHub shows the live link, like
   `https://babbe331.github.io/TikTok-clips-/`. Bookmark it — that opens the working app.

*(GitHub Pages is free on public repositories. On a private repo it needs a paid GitHub plan.)*

---

## How to use it

1. Download **`portal.html`** (right-click → Save, or copy it to a USB stick / the
   computer's Desktop).
2. **Double-click `portal.html`** — it opens in any web browser (Chrome, Edge, Safari, Firefox).
3. That's it. Start adding inventory, customers, and sales.

> 💡 Tip: To make it feel like a real app, open it in the browser and choose
> **"Install" / "Add to Dock / Home screen"** from the browser menu. It then gets
> its own icon and opens in its own window.

---

## What it does

### 📊 Dashboard
A one-look overview: inventory value, low/out-of-stock counts, open orders, and a
**"Shopping list — produce you need to buy."**

### 🧾 New Sale  *(the main feature)*
Pick a customer, add what they're buying. As you type, each line tells you whether
it's **in stock** or **short**, and the summary shows a clear
**"🛒 Buy before this sale"** list — exactly how much of each item to buy before the
delivery goes out. He can sell things he doesn't have; the app just tells him how
much he's missing.

### 📦 Orders
Every sale, its status, and what still needs buying. Mark an order **delivered** to
subtract the quantities from inventory (or reopen to add them back).

### 🥕 Inventory
All produce on hand, with low-stock alerts. Add/edit items by hand, **import
spreadsheets**, or **export to CSV**.

### 🏢 Customers
The companies he sells to.

### 💲 Pricing
Costs, sell prices, and margins for every product. Import a price-list spreadsheet to
update prices in bulk (*update matches only* or *update & add new*). Because everything
shares one product list, a price import instantly updates Inventory, new Sales, and Earnings.

### 💰 Earnings
For each sale: the **sale total (before margin)** next to the **profit (after cost)**, plus
margin %, running totals, and CSV export. Profit uses each product's cost from Pricing.

### 💬 Help bot ("Sprout")
A built-in help assistant in the bottom-right corner. Tap a question or type your own and
it explains how to use the app. It runs **fully offline** — nothing typed there leaves the
device.

> Everything is connected: edit a price, import a spreadsheet, or mark an order delivered,
> and every tab updates to match.

---

## Importing his spreadsheets

1. Save each spreadsheet as a **`.csv`** file (Excel / Google Sheets: *File → Download/Save As → CSV*).
2. In **Inventory**, click **⬆ Import spreadsheet(s)**. He can select **several files at once**.
3. Choose what to do:
   - **🔄 Replace everything** — wipe the current inventory and load *only* what's in
     the spreadsheets. Use this to refresh the whole list from his latest sheet.
   - **➕ Add & update** — keep what's there; update matching items by name, add new ones.

Recognized column names (order & capitalization don't matter):
`name`, `quantity` (or `qty` / `on hand`), `unit`, `price`, `cost`, `category`, `low stock`.

A ready-to-test file is included: **`sample_inventory.csv`**.

---

## Keeping the data safe

Data is stored in the browser on that device. To move it to another computer or keep
a safety copy, use the buttons in the top bar:

- **⬇ Backup** — saves a `.json` file with everything (inventory, customers, orders).
- **⬆ Restore** — loads a backup `.json` file back in.

Make a backup before doing a big "Replace everything" import, just in case.

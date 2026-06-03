# 🥬 Farmlind Produce — Sales & Inventory Portal

A private, single-file web app for managing produce sales and inventory. No internet,
no accounts, no installs. Everything stays **on the user's own device**.

The whole app is one file: **`index.html`**.

---

## How to use it

1. Download **`index.html`** (right-click → Save, or copy it to a USB stick / the
   computer's Desktop).
2. **Double-click `index.html`** — it opens in any web browser (Chrome, Edge, Safari, Firefox).
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

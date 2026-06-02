# TABBE Designs — Storefront

A modern, advanced concept storefront for **TABBE Designs** (Talia Abbe) — sculptural ready-to-wear and made-to-order latex couture, handmade in NYC. *Dress the feeling.*

Built as a fast, dependency-free static site so it deploys anywhere (Netlify, Vercel, GitHub Pages, Cloudflare Pages) with zero build step.

## Features

- **Modern design system** — glassmorphic sticky nav, animated gradient blobs, marquees, scroll-reveal animations, pastel brand palette, custom display type.
- **Full shop** — category + collection (line) filters, live search, sorting, and a responsive product grid.
- **Product pages** — gallery thumbnails, color/size selectors, accordions (details, shipping, care), related products.
- **Cart** — slide-out drawer with quantity controls, subtotal, free-shipping threshold, persisted to `localStorage`.
- **Wishlist** — heart any piece; view saved items via the wishlist filter.
- **Quick add** to bag from any card, toast notifications.
- **Collections** showcase, **Brand Story / About** with timeline, and a **Contact** page with form + studio info.
- Fully **responsive** with a mobile nav, and respects `prefers-reduced-motion`.

## Structure

```
website/
├── index.html          Home
├── shop.html           Shop + filtering
├── product.html        Product detail (?id=)
├── collections.html    Collections
├── about.html          Brand story
├── contact.html        Contact
├── css/styles.css      Design system
└── js/
    ├── products.js     Product + collection data, on-brand SVG art generator
    ├── site.js         Header/footer/cart engine (shared)
    ├── shop.js         Shop filtering/search/sort
    └── product.js      Product detail page
```

## Run locally

```bash
cd website
python3 -m http.server 8080
# open http://localhost:8080
```

## Notes

- Product imagery is generated as on-brand sculptural gradient art. To use real
  photography, set `image` on a product in `js/products.js` and render it in place
  of `productArt(...)`.
- Prices and product names are sourced from tabbedesigns.com (Ready-to-Wear and
  Made-to-Order collections). Checkout is a demo — wire up Shopify/Stripe to go live.

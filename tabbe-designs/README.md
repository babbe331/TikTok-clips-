# TABBE Designs — Futuristic Redesign

An interactive redesign concept for [tabbedesigns.com](https://tabbedesigns.com), the NYC fashion label by Talia Abbe that challenges mental-health stigma through sculptural, inflatable clothing.

## What's inside
- **All 27 products** with the store's exact prices, variants, and photography (loaded from the official tabbedesigns.com CDN)
- **All four collections** — In Play (FW26), The Butterfly Effect (SS25), Cotton Candy Capsule, and Bubble Wrap — each with its full lookbook and concept text
- **Brand Story, Press (Macy's Thanksgiving Day Parade 2025 + Publications archive), and Contact**, mirroring every topic on the original site
- Purchase links deep-link to the official store's product pages

## Interactions
Floating bubble canvas (click to pop), holographic gradient text, custom cursor with magnetic buttons, 3D-tilt product cards with hover image swap, drag-to-scroll lookbooks, animated collection tabs, live shop filtering/search/sort, quick-view product modal with variant pricing, wishlist drawer (localStorage), scroll-progress bar, parallax hero, and count-up stats. Fully responsive, keyboard accessible, and respectful of `prefers-reduced-motion`.

## Run it
Static site — no build step:
```bash
cd tabbe-designs && python3 -m http.server 8000
```
Then open http://localhost:8000.

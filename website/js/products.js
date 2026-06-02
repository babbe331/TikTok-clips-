/* =========================================================================
   TABBE DESIGNS — Product & Collection Data
   Prices & names sourced from tabbedesigns.com (Ready-to-Wear + Made-to-Order).
   Imagery is generated as on-brand sculptural gradient art (swap in real
   photography by setting product.image to a file path in /assets).
   ========================================================================= */

/* Palette tokens reused for generated art + swatches */
const PAL = {
  cottonCandy: "#ffd1ec", bubbleBlue: "#b8d8ff", sky: "#d9ecff", mint: "#c8f5e4",
  lemon: "#fff2b3", lilac: "#e3d4ff", peach: "#ffd9c2", rose: "#ff8fc8",
  grape: "#8a5cff", blue: "#66b9ff", green: "#7fe0b0", yellow: "#ffe066",
};

const PRODUCTS = [
  // ---------------- READY TO WEAR ----------------
  {
    id: "blake-dress", name: "Blake Dress", price: 238, category: "Dresses",
    line: "ready-to-wear", collection: "The Butterfly Effect", badge: "Bestseller",
    colors: [PAL.cottonCandy, PAL.lilac, PAL.sky], sizes: ["XS","S","M","L"],
    material: "Digitally printed stretch jersey",
    desc: "A fluid mini with our signature cognitive-abstraction print — designed to move with you and lift the mood the moment it's on.",
    art: ["rose","lilac"],
  },
  {
    id: "rose-bodysuit", name: "Rose Bodysuit / Swimsuit", price: 218, category: "Bodysuits",
    line: "ready-to-wear", collection: "Cotton Candy", badge: "New",
    colors: [PAL.rose, PAL.peach, PAL.bubbleBlue], sizes: ["XS","S","M","L"],
    material: "Sculpted four-way stretch (land + water ready)",
    desc: "A second-skin bodysuit that doubles as swim. Sculptural seaming hugs every curve while the petal-soft palette keeps it playful.",
    art: ["rose","peach"],
  },
  {
    id: "alessandra-mesh-top", name: "Alessandra Mesh Top", price: 260, category: "Tops",
    line: "ready-to-wear", collection: "The Butterfly Effect", badge: null,
    colors: [PAL.lilac, PAL.sky, PAL.mint], sizes: ["XS","S","M","L"],
    material: "Hand-finished printed mesh",
    desc: "Sheer printed mesh with a sculptural neckline — equal parts armor and air. Layer it loud or wear it bare.",
    art: ["lilac","blue"],
  },
  {
    id: "lex-tank", name: "Lex Tank", price: 180, category: "Tops",
    line: "ready-to-wear", collection: "In Play", badge: null,
    colors: [PAL.bubbleBlue, PAL.mint, PAL.cottonCandy], sizes: ["XS","S","M","L"],
    material: "Ribbed organic cotton blend",
    desc: "A clean, hugging tank in buttery rib — the everyday foundation piece that still feels like a TABBE.",
    art: ["bubbleBlue","mint"],
  },
  {
    id: "tabbe-tank", name: "TABBE Tank Top", price: 170, category: "Tops",
    line: "ready-to-wear", collection: "In Play", badge: null,
    colors: [PAL.cottonCandy, PAL.lemon, PAL.lilac], sizes: ["XS","S","M","L"],
    material: "Soft-touch logo jersey",
    desc: "Our signature tank, branded and bright. The piece that started the wardrobe.",
    art: ["cottonCandy","lemon"],
  },
  {
    id: "cameron-top", name: "Cameron Top", price: 114, category: "Tops",
    line: "ready-to-wear", collection: "In Play", badge: "Under $150",
    colors: [PAL.peach, PAL.sky, PAL.mint], sizes: ["XS","S","M","L"],
    material: "Lightweight printed jersey",
    desc: "An easy printed top with a sculptural twist at the shoulder — your softest entry into the world of TABBE.",
    art: ["peach","sky"],
  },
  {
    id: "chloe-set", name: "Chloe Matching Top & Skirt", price: 110, category: "Matching Sets",
    line: "ready-to-wear", collection: "Cotton Candy", badge: "Set",
    colors: [PAL.cottonCandy, PAL.lilac, PAL.mint], sizes: ["XS","S","M","L"],
    material: "Coordinated stretch knit set",
    desc: "Top and skirt that move as one. Wear together for full-look impact or split across the week.",
    art: ["cottonCandy","lilac"],
  },
  {
    id: "mini-stuffy-pod", name: "Mini Stuffy Pod Purse", price: 280, category: "Accessories",
    line: "ready-to-wear", collection: "Bubble Wrap", badge: null,
    colors: [PAL.bubbleBlue, PAL.cottonCandy, PAL.lemon], sizes: ["One Size"],
    material: "Padded sculptural shell",
    desc: "A pillowy little pod that hugs your essentials. Soft to hold, impossible to ignore.",
    art: ["bubbleBlue","cottonCandy"],
  },
  {
    id: "big-stuffy-pod", name: "Big Stuffy Pod Purse", price: 315, category: "Accessories",
    line: "ready-to-wear", collection: "Bubble Wrap", badge: null,
    colors: [PAL.lilac, PAL.mint, PAL.peach], sizes: ["One Size"],
    material: "Padded sculptural shell",
    desc: "The bigger Stuffy — all your day-to-day, wrapped in a cloud. Carry comfort everywhere.",
    art: ["lilac","mint"],
  },
  {
    id: "puffy-pod-purse", name: "The Puffy Pod Purse", price: 378, category: "Accessories",
    line: "ready-to-wear", collection: "Inflatable Latex Capsule", badge: "Latex",
    colors: [PAL.rose, PAL.bubbleBlue, PAL.lemon], sizes: ["One Size"],
    material: "Inflatable pure latex, NYC-made",
    desc: "An inflatable statement bag in pure latex — the bridge between our ready-to-wear and couture worlds. Inflate to fill, deflate to pack.",
    art: ["rose","blue"],
  },

  // ---------------- MADE TO ORDER (LATEX COUTURE) ----------------
  {
    id: "blue-bubble-dress", name: "Blue Bubble Dress", price: 1780, category: "Dresses",
    line: "made-to-order", collection: "Bubble Wrap", badge: "Made to Order",
    colors: [PAL.bubbleBlue, PAL.sky], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex — cut, bonded & sealed in NYC",
    desc: "Our icon. A sculptural bubble silhouette in pure blue latex, handcrafted to order over four weeks. A piece of wearable emotion.",
    art: ["bubbleBlue","blue"],
  },
  {
    id: "double-bubble-dress", name: "Double Bubble Dress", price: 1780, category: "Dresses",
    line: "made-to-order", collection: "Bubble Wrap", badge: "Made to Order",
    colors: [PAL.cottonCandy, PAL.lilac], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex — cut, bonded & sealed in NYC",
    desc: "Twin sculpted bubbles in pure latex — volume on volume, joy on joy. Handcrafted to order.",
    art: ["cottonCandy","lilac"],
  },
  {
    id: "green-balloon-dress", name: "Green Balloon Dress", price: 1780, category: "Dresses",
    line: "made-to-order", collection: "In Play", badge: "Inflatable",
    colors: [PAL.green, PAL.mint], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex, inflator included",
    desc: "Inflate to the volume that matches your mood. A balloon dress in pure latex, shipped with its own inflator.",
    art: ["green","mint"],
  },
  {
    id: "cotton-candy-dress", name: "Cotton Candy Dress", price: 2800, category: "Dresses",
    line: "made-to-order", collection: "Cotton Candy", badge: "Couture",
    colors: [PAL.cottonCandy, PAL.rose], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex sculptural couture",
    desc: "Spun-sugar volume in pure latex — the centerpiece of the Cotton Candy collection. A runway moment, made for you.",
    art: ["cottonCandy","rose"],
  },
  {
    id: "cotton-candy-jacket", name: "Cotton Candy Jacket", price: 2500, category: "Tops",
    line: "made-to-order", collection: "Cotton Candy", badge: "Couture",
    colors: [PAL.cottonCandy, PAL.peach], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex with volume styling",
    desc: "An oversized latex jacket built on air and architecture — soft to the eye, structural to the touch.",
    art: ["cottonCandy","peach"],
  },
  {
    id: "polka-dot-jacket", name: "Polka Dot Jacket", price: 3800, category: "Tops",
    line: "made-to-order", collection: "The Butterfly Effect", badge: "Couture",
    colors: [PAL.lilac, PAL.bubbleBlue], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex, sculptural dot detailing",
    desc: "Our most architectural piece — pure latex sculpted into bold dimensional dots. A collector's garment.",
    art: ["lilac","bubbleBlue"],
  },
  {
    id: "polka-dot-dress", name: "Polka Dot Two-Part Dress", price: 2700, category: "Dresses",
    line: "made-to-order", collection: "The Butterfly Effect", badge: "Couture",
    colors: [PAL.sky, PAL.cottonCandy], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex, two-part construction",
    desc: "A two-part latex dress dotted in dimension — separate to style, unite for full drama.",
    art: ["sky","cottonCandy"],
  },
  {
    id: "inflated-sleeve-corset", name: "Inflated Sleeve Corset Dress", price: 1800, category: "Dresses",
    line: "made-to-order", collection: "Bubble Wrap", badge: "Inflatable",
    colors: [PAL.rose, PAL.lilac], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex, inflated sleeves",
    desc: "A corseted base with sculptural inflated sleeves — power and play in one pure-latex silhouette.",
    art: ["rose","lilac"],
  },
  {
    id: "slick-trousers-float-jacket", name: "The Slick Trousers & Float Jacket", price: 1300, category: "Matching Sets",
    line: "made-to-order", collection: "In Play", badge: "Set",
    colors: [PAL.bubbleBlue, PAL.sky], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex ensemble",
    desc: "Slick latex trousers paired with a floating sculptural jacket — a full look that defies gravity.",
    art: ["bubbleBlue","sky"],
  },
  {
    id: "yellow-inflated-skirt", name: "Yellow Inflated Skirt", price: 1500, category: "Matching Sets",
    line: "made-to-order", collection: "In Play", badge: "Inflatable",
    colors: [PAL.yellow, PAL.lemon], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex, inflatable design",
    desc: "Sunshine in sculptural form — an inflated latex skirt that turns every step into a statement.",
    art: ["yellow","lemon"],
  },
  {
    id: "bubble-ruffle-dress", name: "Bubble Ruffle Dress", price: 1588, category: "Dresses",
    line: "made-to-order", collection: "Bubble Wrap", badge: "Made to Order",
    colors: [PAL.cottonCandy, PAL.peach], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex, ruffled detailing",
    desc: "Cascading latex ruffles bubble down a sculpted body — romance, reimagined in rubber.",
    art: ["cottonCandy","peach"],
  },
  {
    id: "eeg-catsuit", name: "EEG Catsuit", price: 1600, category: "Bodysuits",
    line: "made-to-order", collection: "The Butterfly Effect", badge: "Signature Print",
    colors: [PAL.grape, PAL.blue], sizes: ["XS","S","M","L","Bespoke"],
    material: "Printed latex — brainwave-inspired graphics",
    desc: "A printed latex catsuit mapped from real EEG brainwave scans — the brand's mind-forward mission, worn on the body.",
    art: ["grape","blue"],
  },
  {
    id: "inflated-bow", name: "Inflated Bow", price: 813, category: "Accessories",
    line: "made-to-order", collection: "Bubble Wrap", badge: "Inflatable",
    colors: [PAL.rose, PAL.cottonCandy], sizes: ["One Size"],
    material: "Pure latex sculptural accessory",
    desc: "An oversized inflated bow to top any look — the easiest way to wear a TABBE silhouette.",
    art: ["rose","cottonCandy"],
  },
  {
    id: "classy-bow", name: "Classy Bow", price: 400, category: "Accessories",
    line: "made-to-order", collection: "Cotton Candy", badge: null,
    colors: [PAL.lilac, PAL.bubbleBlue], sizes: ["One Size"],
    material: "Latex with magnetic closure",
    desc: "A refined latex bow with a hidden magnetic closure — sculptural punctuation for hair, neck or waist.",
    art: ["lilac","bubbleBlue"],
  },
  {
    id: "bow-top-skirt-set", name: "Bow Top with Matching Skirt", price: 685, category: "Matching Sets",
    line: "made-to-order", collection: "Cotton Candy", badge: "Set",
    colors: [PAL.peach, PAL.cottonCandy], sizes: ["XS","S","M","L","Bespoke"],
    material: "Pure latex set",
    desc: "A bow-front latex top with a coordinating skirt — a complete sculptural look in soft pure latex.",
    art: ["peach","cottonCandy"],
  },
];

const COLLECTIONS = [
  { id: "cotton-candy", name: "Cotton Candy", season: "Signature", art: ["cottonCandy","rose"],
    blurb: "Spun-sugar volume and the softest palette in the house — joy you can wear." },
  { id: "bubble-wrap", name: "Bubble Wrap", season: "Iconic", art: ["bubbleBlue","lilac"],
    blurb: "Inflated, sealed and sculpted — the bubble silhouettes that define TABBE." },
  { id: "the-butterfly-effect", name: "The Butterfly Effect", season: "SS25", art: ["lilac","blue"],
    blurb: "Cognitive-abstraction prints and brainwave graphics — small feelings, big change." },
  { id: "in-play", name: "In Play", season: "FW26", art: ["green","mint"],
    blurb: "Our most wearable world yet — playful latex and ready-to-wear, side by side." },
];

/* ---------- Generated SVG art (on-brand sculptural gradient blobs) ------- */
function productArt(keys, seed = 0) {
  const c1 = PAL[keys[0]] || PAL.cottonCandy;
  const c2 = PAL[keys[1]] || PAL.lilac;
  const gid = "g" + Math.random().toString(36).slice(2, 8);
  const r = (n) => 30 + ((seed * 37 + n * 53) % 40);
  return `
  <svg class="art" viewBox="0 0 400 500" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true">
    <defs>
      <linearGradient id="${gid}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="${c1}"/>
        <stop offset="1" stop-color="${c2}"/>
      </linearGradient>
      <radialGradient id="${gid}h" cx="0.5" cy="0.32" r="0.7">
        <stop offset="0" stop-color="#ffffff" stop-opacity="0.85"/>
        <stop offset="0.4" stop-color="#ffffff" stop-opacity="0.18"/>
        <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <rect width="400" height="500" fill="url(#${gid})"/>
    <g opacity="0.9">
      <circle cx="${120 + r(1)}" cy="${150 + r(2)}" r="${90 + r(3)}" fill="#ffffff" opacity="0.16"/>
      <circle cx="${270 - r(2)}" cy="${320 + r(1)}" r="${70 + r(4)}" fill="${c1}" opacity="0.5"/>
      <ellipse cx="200" cy="250" rx="130" ry="160" fill="url(#${gid}h)"/>
    </g>
    <circle cx="200" cy="250" r="92" fill="#ffffff" opacity="0.12"/>
  </svg>`;
}

/* Expose on window — `const` in a classic script is NOT auto-attached to window */
if (typeof window !== "undefined") {
  window.PRODUCTS = PRODUCTS;
  window.COLLECTIONS = COLLECTIONS;
  window.PAL = PAL;
  window.productArt = productArt;
}
if (typeof module !== "undefined") module.exports = { PRODUCTS, COLLECTIONS, PAL, productArt };

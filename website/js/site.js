/* =========================================================================
   TABBE DESIGNS — Site engine
   Header/footer/cart injection, cart + wishlist state (localStorage),
   scroll reveals, mobile nav, toasts. Renders REAL product imagery.
   ========================================================================= */
(function () {
  const money = (n) => "$" + Number(n).toLocaleString("en-US");
  const CART_KEY = "tabbe_cart_v2";
  const WISH_KEY = "tabbe_wish_v2";

  const load = (k) => { try { return JSON.parse(localStorage.getItem(k)) || []; } catch { return []; } };
  const save = (k, v) => localStorage.setItem(k, JSON.stringify(v));
  let cart = load(CART_KEY);
  let wish = load(WISH_KEY);

  const byId = (id) => (window.PRODUCTS || []).find((p) => p.id === id);
  const img = (p, i = 0) => (p && p.images && p.images[i]) || (p && p.images && p.images[0]) || "";

  const ICON = {
    bag: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
    heart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>',
    menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
    ig: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
    tiktok: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 3c.3 2.2 1.7 3.9 3.9 4.2v2.7c-1.4 0-2.7-.4-3.9-1.1v5.6c0 3.3-2.5 5.6-5.6 5.6S4.8 17.7 4.8 14.6 7.3 9 10.4 9c.4 0 .8 0 1.2.1v2.9c-.4-.1-.8-.2-1.2-.2-1.5 0-2.7 1.2-2.7 2.8s1.2 2.8 2.7 2.8 2.7-1.2 2.7-2.8V3H16z"/></svg>',
    pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s7-6 7-12a7 7 0 1 0-14 0c0 6 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
  };

  /* ---------------- Header ---------------- */
  function header() {
    const path = location.pathname.split("/").pop() || "index.html";
    const link = (href, label) => `<a href="${href}" class="${path === href ? "active" : ""}">${label}</a>`;
    return `
    <div class="announce"><div class="track">
      <span>✦ Handmade in NYC &nbsp;·&nbsp; <b>Free shipping over $250</b> &nbsp;·&nbsp; Dress the feeling &nbsp;·&nbsp; Made-to-order latex couture &nbsp;·&nbsp;</span>
      <span>✦ Handmade in NYC &nbsp;·&nbsp; <b>Free shipping over $250</b> &nbsp;·&nbsp; Dress the feeling &nbsp;·&nbsp; Made-to-order latex couture &nbsp;·&nbsp;</span>
    </div></div>
    <header class="site-header" id="siteHeader">
      <div class="wrap">
        <a class="brand" href="index.html">TABBE<span class="dot"></span><small>designs</small></a>
        <nav class="nav">
          ${link("shop.html", "Shop")}
          ${link("collections.html", "Collections")}
          ${link("about.html", "Brand Story")}
          ${link("contact.html", "Contact")}
        </nav>
        <div class="header-actions">
          <button class="icon-btn search-trigger" aria-label="Search" data-search>${ICON.search}</button>
          <a class="icon-btn" href="shop.html?fav=1" aria-label="Wishlist">${ICON.heart}</a>
          <button class="icon-btn" aria-label="Cart" data-open-cart>${ICON.bag}<span class="cart-count" id="cartCount">0</span></button>
          <button class="icon-btn menu-toggle" aria-label="Menu" data-open-menu>${ICON.menu}</button>
        </div>
      </div>
    </header>
    <div class="mobile-nav" id="mobileNav">
      <button class="close" data-close-menu aria-label="Close">×</button>
      <a href="index.html">Home</a>
      <a href="shop.html">Shop</a>
      <a href="collections.html">Collections</a>
      <a href="about.html">Brand Story</a>
      <a href="contact.html">Contact</a>
    </div>`;
  }

  /* ---------------- Footer ---------------- */
  function footer() {
    return `
    <footer class="site-footer">
      <div class="wrap">
        <div class="footer-grid">
          <div class="footer-brand">
            <a class="brand" href="index.html">TABBE<span class="dot"></span><small>designs</small></a>
            <p>Ready-to-wear and made-to-order latex couture from New York City. Fashion for the mind — dress the feeling.</p>
            <div class="socials">
              <a href="https://www.instagram.com/tabbe_designs/" aria-label="Instagram" target="_blank" rel="noopener">${ICON.ig}</a>
              <a href="#" aria-label="TikTok">${ICON.tiktok}</a>
              <a href="#" aria-label="Pinterest">${ICON.pin}</a>
            </div>
          </div>
          <div>
            <h4>Shop</h4>
            <a href="shop.html?line=ready-to-wear">Ready to Wear</a>
            <a href="shop.html?line=made-to-order">Made to Order</a>
            <a href="shop.html?cat=Dresses">Dresses</a>
            <a href="shop.html?cat=Accessories">Accessories</a>
            <a href="shop.html?cat=Sets %26 Bottoms">Sets &amp; Bottoms</a>
          </div>
          <div>
            <h4>Brand</h4>
            <a href="about.html">Our Story</a>
            <a href="collections.html">Collections</a>
            <a href="about.html#mission">Mind &amp; Mission</a>
            <a href="contact.html">Press &amp; Stockists</a>
          </div>
          <div>
            <h4>Help</h4>
            <a href="contact.html">Contact</a>
            <a href="contact.html#shipping">Shipping &amp; Returns</a>
            <a href="contact.html#care">Latex Care</a>
            <a href="contact.html#sizing">Sizing</a>
          </div>
        </div>
        <div class="footer-bottom">
          <span>© ${new Date().getFullYear()} TABBE Designs — Talia Abbe. Handmade in NYC.</span>
          <span>Concept storefront · Imagery © tabbedesigns.com</span>
        </div>
      </div>
    </footer>`;
  }

  /* ---------------- Cart drawer ---------------- */
  function cartDrawer() {
    return `
    <div class="scrim" id="scrim"></div>
    <aside class="cart-drawer" id="cartDrawer" aria-label="Shopping bag">
      <div class="cart-head"><h3>Your Bag</h3><button class="icon-btn" data-close-cart aria-label="Close">×</button></div>
      <div class="cart-items" id="cartItems"></div>
      <div class="cart-foot" id="cartFoot"></div>
    </aside>
    <div class="toast-wrap" id="toastWrap"></div>`;
  }

  function renderCart() {
    const itemsEl = document.getElementById("cartItems");
    const footEl = document.getElementById("cartFoot");
    if (!itemsEl) return;

    if (!cart.length) {
      itemsEl.innerHTML = `<div class="cart-empty"><div class="big">🫧</div><p>Your bag is empty.<br>Let's find a feeling to wear.</p>
        <a href="shop.html" class="btn btn--primary" style="margin-top:1rem">Shop the collection</a></div>`;
      footEl.innerHTML = "";
      return;
    }

    itemsEl.innerHTML = cart.map((it, i) => {
      const p = byId(it.id) || {};
      return `<div class="cart-item">
        <div class="thumb"><img src="${img(p)}" alt="${p.name || ""}" loading="lazy"></div>
        <div>
          <div class="ci-name">${p.name || it.id}</div>
          <div class="ci-meta">${it.size ? it.size + " · " : ""}${money(p.price || 0)}</div>
          <div class="qty">
            <button data-qty="-1" data-i="${i}" aria-label="Decrease">−</button>
            <span>${it.qty}</span>
            <button data-qty="1" data-i="${i}" aria-label="Increase">+</button>
          </div>
          <div><button class="ci-remove" data-remove="${i}">Remove</button></div>
        </div>
        <strong class="ci-meta">${money((p.price || 0) * it.qty)}</strong>
      </div>`;
    }).join("");

    const subtotal = cart.reduce((s, it) => s + (byId(it.id)?.price || 0) * it.qty, 0);
    const ship = subtotal >= 250 || subtotal === 0 ? 0 : 25;
    footEl.innerHTML = `
      <div class="cart-row"><span>Subtotal</span><span class="mono">${money(subtotal)}</span></div>
      <div class="cart-row muted"><span>Shipping</span><span class="mono">${ship ? money(ship) : "FREE"}</span></div>
      <div class="cart-row total"><span>Total</span><span class="mono">${money(subtotal + ship)}</span></div>
      <p class="cart-note">${subtotal < 250 ? "Add " + money(250 - subtotal) + " for free shipping. " : ""}Made-to-order pieces ship in ~4 weeks.</p>
      <button class="btn btn--primary btn--block btn--lg" data-checkout>Checkout →</button>`;
  }

  function updateCount() {
    const el = document.getElementById("cartCount");
    if (!el) return;
    const n = cart.reduce((s, it) => s + it.qty, 0);
    el.textContent = n;
    el.classList.toggle("show", n > 0);
  }

  function addToCart(id, size, qty = 1) {
    const p = byId(id);
    if (!p) return;
    const key = id + "|" + (size || "");
    const existing = cart.find((it) => it.id + "|" + (it.size || "") === key);
    if (existing) existing.qty += qty;
    else cart.push({ id, size: size || (p.sizes && p.sizes[0]) || "", qty });
    save(CART_KEY, cart);
    renderCart(); updateCount();
    toast(`${p.name} added to bag`, true);
    openCart();
  }
  function changeQty(i, d) { if (!cart[i]) return; cart[i].qty += d; if (cart[i].qty <= 0) cart.splice(i, 1); save(CART_KEY, cart); renderCart(); updateCount(); }
  function removeItem(i) { cart.splice(i, 1); save(CART_KEY, cart); renderCart(); updateCount(); }

  function toggleWish(id) {
    const i = wish.indexOf(id);
    if (i >= 0) { wish.splice(i, 1); toast("Removed from wishlist"); }
    else { wish.push(id); toast("Saved to wishlist ♥", true); }
    save(WISH_KEY, wish);
    document.querySelectorAll(`[data-fav="${id}"]`).forEach((b) => b.classList.toggle("active", wish.includes(id)));
  }
  const isWished = (id) => wish.includes(id);

  const openCart = () => { document.getElementById("cartDrawer").classList.add("open"); document.getElementById("scrim").classList.add("open"); document.body.style.overflow = "hidden"; };
  const closeCart = () => { document.getElementById("cartDrawer").classList.remove("open"); document.getElementById("scrim").classList.remove("open"); document.body.style.overflow = ""; };
  const openMenu = () => document.getElementById("mobileNav").classList.add("open");
  const closeMenu = () => document.getElementById("mobileNav").classList.remove("open");

  function toast(msg, ok = false) {
    const wrap = document.getElementById("toastWrap");
    if (!wrap) return;
    const t = document.createElement("div");
    t.className = "toast";
    t.innerHTML = `${ok ? '<span class="tick">✓</span>' : ""}<span>${msg}</span>`;
    wrap.appendChild(t);
    setTimeout(() => { t.style.transition = "opacity .4s, transform .4s"; t.style.opacity = "0"; t.style.transform = "translateY(12px)"; setTimeout(() => t.remove(), 400); }, 2400);
  }

  function reveals() {
    const els = document.querySelectorAll("[data-reveal]:not(.in)");
    if (!("IntersectionObserver" in window)) { els.forEach((e) => e.classList.add("in")); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });
    els.forEach((e) => io.observe(e));
  }

  /* ---------------- Shared card renderer ---------------- */
  function productCard(p, opts = {}) {
    const badge = p.line === "made-to-order"
      ? `<span class="card-badge mto">Made to Order</span>`
      : (!p.available ? `<span class="card-badge">Preorder</span>` : (opts.badge ? `<span class="card-badge">${opts.badge}</span>` : ""));
    const faved = isWished(p.id) ? "active" : "";
    const second = p.images && p.images[1] ? `<img class="img2" src="${p.images[1]}" alt="" loading="lazy">` : "";
    return `<article class="card" data-reveal style="--ac:${p.accent || "var(--neon-violet)"}">
      <div class="card-media">
        ${badge}
        <button class="card-fav ${faved}" data-fav="${p.id}" aria-label="Save">${ICON.heart}</button>
        <a href="product.html?id=${p.id}" aria-label="${p.name}">
          <img src="${img(p)}" alt="${p.name}" loading="lazy">${second}
        </a>
        <button class="card-quick" data-add="${p.id}">Quick add · ${money(p.price)}</button>
      </div>
      <a class="card-body" href="product.html?id=${p.id}">
        <span class="card-cat">${p.category}</span>
        <span class="card-name">${p.name}</span>
        <span class="card-price">${money(p.price)}</span>
      </a>
    </article>`;
  }

  function init() {
    const h = document.getElementById("header-mount"); if (h) h.innerHTML = header();
    const f = document.getElementById("footer-mount"); if (f) f.innerHTML = footer();
    document.body.insertAdjacentHTML("beforeend", cartDrawer());

    renderCart(); updateCount(); reveals();

    const hdr = document.getElementById("siteHeader");
    const onScroll = () => hdr && hdr.classList.toggle("is-scrolled", window.scrollY > 12);
    onScroll(); window.addEventListener("scroll", onScroll, { passive: true });

    document.addEventListener("click", (e) => {
      const t = e.target.closest("[data-open-cart],[data-close-cart],[data-open-menu],[data-close-menu],[data-qty],[data-remove],[data-checkout],[data-add],[data-fav],[data-search]");
      if (!t) { if (e.target.id === "scrim") closeCart(); return; }
      if (t.hasAttribute("data-open-cart")) { e.preventDefault(); openCart(); }
      else if (t.hasAttribute("data-close-cart")) closeCart();
      else if (t.hasAttribute("data-open-menu")) openMenu();
      else if (t.hasAttribute("data-close-menu")) closeMenu();
      else if (t.hasAttribute("data-qty")) changeQty(+t.dataset.i, +t.dataset.qty);
      else if (t.hasAttribute("data-remove")) removeItem(+t.dataset.remove);
      else if (t.hasAttribute("data-checkout")) toast("Checkout is a demo in this concept build ✨");
      else if (t.hasAttribute("data-add")) { e.preventDefault(); addToCart(t.dataset.add, t.dataset.size); }
      else if (t.hasAttribute("data-fav")) { e.preventDefault(); toggleWish(t.dataset.fav); }
      else if (t.hasAttribute("data-search")) { e.preventDefault(); location.href = "shop.html"; }
    });
    document.getElementById("scrim").addEventListener("click", closeCart);
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") { closeCart(); closeMenu(); } });
  }

  window.TABBE = { addToCart, toggleWish, isWished, openCart, toast, money, reveals, productCard, img };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

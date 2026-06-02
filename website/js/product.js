/* =========================================================================
   TABBE DESIGNS — Product detail page
   ========================================================================= */
(function () {
  const mount = document.getElementById("pdpMount");
  if (!mount) return;
  const money = (n) => "$" + n.toLocaleString("en-US");

  const id = new URLSearchParams(location.search).get("id");
  const p = (window.PRODUCTS || []).find((x) => x.id === id) || PRODUCTS[0];
  document.title = `${p.name} — TABBE Designs`;

  let size = p.sizes[0];
  let colorIdx = 0;

  const gallery = [p.name.length, p.name.length + 3, p.name.length + 7, p.name.length + 11];
  const isMTO = p.line === "made-to-order";

  mount.innerHTML = `
    <div class="wrap pdp">
      <p class="muted" style="margin-bottom:1.4rem;font-size:.85rem">
        <a href="index.html">Home</a> / <a href="shop.html">Shop</a> /
        <a href="shop.html?line=${p.line}">${isMTO ? "Made to Order" : "Ready to Wear"}</a> / <strong>${p.name}</strong>
      </p>
      <div class="pdp-grid">
        <div class="pdp-gallery" data-reveal>
          <div class="pdp-main" id="pdpMain">${window.productArt(p.art, gallery[0])}</div>
          <div class="pdp-thumbs" id="pdpThumbs">
            ${gallery.map((s, i) => `<div class="t ${i === 0 ? "active" : ""}" data-thumb="${i}">${window.productArt(p.art, s)}</div>`).join("")}
          </div>
        </div>
        <div class="pdp-info" data-reveal data-reveal-delay="1">
          <span class="cat">${p.collection} · ${p.category}</span>
          <h1>${p.name}</h1>
          <div class="pdp-price">${money(p.price)}</div>
          <p class="pdp-desc">${p.desc}</p>

          <div class="opt-label">Color</div>
          <div class="colors" id="pdpColors">
            ${p.colors.map((c, i) => `<button class="color-dot ${i === 0 ? "active" : ""}" style="background:${c}" data-color="${i}" aria-label="color ${i + 1}"></button>`).join("")}
          </div>

          <div class="opt-label">Size${isMTO ? " · made to your measurements" : ""}</div>
          <div class="sizes" id="pdpSizes">
            ${p.sizes.map((s, i) => `<button class="size ${i === 0 ? "active" : ""}" data-size="${s}">${s}</button>`).join("")}
          </div>

          <div class="pdp-actions">
            <button class="btn btn--primary btn--lg" id="pdpAdd">Add to bag — ${money(p.price)}</button>
            <button class="btn btn--ghost btn--lg" id="pdpFav">♡ Save</button>
          </div>
          ${isMTO ? `<p class="muted" style="font-size:.88rem;margin-bottom:1.2rem">✦ Handcrafted to order in NYC from pure latex. Production ~4 weeks. Bespoke sizing available.</p>`
                  : `<p class="muted" style="font-size:.88rem;margin-bottom:1.2rem">✦ Ready to ship in 2–4 business days. Free shipping over $250.</p>`}

          <div class="accordion" id="pdpAcc">
            ${accItem("Details &amp; materials", `${p.material}. ${isMTO ? "Each piece is cut, bonded and sealed by hand in our New York studio." : "Designed in NYC with our signature sculptural spirit."}`)}
            ${accItem("Shipping &amp; returns", isMTO ? "Made-to-order pieces ship in approximately 4 weeks and are final sale. Reach out for bespoke requests." : "Ships in 2–4 business days. Free returns within 14 days on unworn ready-to-wear.")}
            ${accItem("Care", isMTO ? "Latex care: store flat away from light & heat, shine with silicone polish, avoid contact with metals." : "Gentle cold wash, lay flat to dry. Keep prints away from direct heat.")}
          </div>
        </div>
      </div>

      <section class="section">
        <div class="head-row"><div><span class="eyebrow">You may also feel</span><h2 style="font-size:clamp(1.6rem,3.5vw,2.4rem);margin-top:.6rem">More from ${p.collection}</h2></div>
          <a class="btn btn--ghost" href="shop.html">View all</a></div>
        <div class="grid-products" id="pdpRelated"></div>
      </section>
    </div>`;

  function accItem(title, body) {
    return `<div class="acc-item">
      <button class="acc-head">${title}<span class="plus">+</span></button>
      <div class="acc-body"><div class="inner">${body}</div></div>
    </div>`;
  }

  // thumbs
  document.getElementById("pdpThumbs").addEventListener("click", (e) => {
    const t = e.target.closest("[data-thumb]"); if (!t) return;
    const i = +t.dataset.thumb;
    document.querySelectorAll("#pdpThumbs .t").forEach((x) => x.classList.remove("active"));
    t.classList.add("active");
    document.getElementById("pdpMain").innerHTML = window.productArt(p.art, gallery[i]);
  });
  // colors
  document.getElementById("pdpColors").addEventListener("click", (e) => {
    const b = e.target.closest("[data-color]"); if (!b) return;
    colorIdx = +b.dataset.color;
    document.querySelectorAll("#pdpColors .color-dot").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
  });
  // sizes
  document.getElementById("pdpSizes").addEventListener("click", (e) => {
    const b = e.target.closest("[data-size]"); if (!b) return;
    size = b.dataset.size;
    document.querySelectorAll("#pdpSizes .size").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
  });
  // accordion
  document.getElementById("pdpAcc").addEventListener("click", (e) => {
    const h = e.target.closest(".acc-head"); if (!h) return;
    const item = h.parentElement;
    const body = item.querySelector(".acc-body");
    const open = item.classList.toggle("open");
    body.style.maxHeight = open ? body.scrollHeight + "px" : "0";
  });
  // add / fav
  document.getElementById("pdpAdd").addEventListener("click", () => window.TABBE.addToCart(p.id, size));
  const favBtn = document.getElementById("pdpFav");
  const syncFav = () => { favBtn.innerHTML = (TABBE.isWished(p.id) ? "♥ Saved" : "♡ Save"); };
  syncFav();
  favBtn.addEventListener("click", () => { TABBE.toggleWish(p.id); syncFav(); });

  // related
  const related = PRODUCTS.filter((x) => x.collection === p.collection && x.id !== p.id).slice(0, 4);
  const pool = related.length ? related : PRODUCTS.filter((x) => x.id !== p.id).slice(0, 4);
  document.getElementById("pdpRelated").innerHTML = pool.map((rp) => `
    <article class="card" data-reveal>
      <div class="card-media">
        <a href="product.html?id=${rp.id}">${window.productArt(rp.art, rp.name.length)}</a>
        <button class="card-quick" data-add="${rp.id}">Quick add — ${money(rp.price)}</button>
      </div>
      <a class="card-body" href="product.html?id=${rp.id}">
        <span class="card-cat">${rp.category}</span>
        <span class="card-name">${rp.name}</span>
        <span class="card-price">${money(rp.price)}</span>
      </a>
    </article>`).join("");

  window.TABBE && TABBE.reveals();
})();

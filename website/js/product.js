/* =========================================================================
   TABBE DESIGNS — Product detail page (real gallery images)
   ========================================================================= */
(function () {
  const mount = document.getElementById("pdpMount");
  if (!mount) return;
  const money = (n) => "$" + Number(n).toLocaleString("en-US");

  const id = new URLSearchParams(location.search).get("id");
  const p = (window.PRODUCTS || []).find((x) => x.id === id) || PRODUCTS[0];
  document.title = `${p.name} — TABBE Designs`;
  document.documentElement.style.setProperty("--accent", p.accent || "#8a5cff");

  let size = p.sizes[0];
  const imgs = p.images && p.images.length ? p.images : [""];
  const isMTO = p.line === "made-to-order";

  mount.innerHTML = `
    <div class="wrap pdp">
      <p class="breadcrumb">
        <a href="index.html">Home</a> / <a href="shop.html">Shop</a> /
        <a href="shop.html?line=${p.line}">${isMTO ? "Made to Order" : "Ready to Wear"}</a> / <span style="color:var(--ink)">${p.name}</span>
      </p>
      <div class="pdp-grid">
        <div class="pdp-gallery" data-reveal>
          <div class="pdp-main" id="pdpMain"><img id="pdpMainImg" src="${imgs[0]}" alt="${p.name}"></div>
          <div class="pdp-thumbs" id="pdpThumbs">
            ${imgs.slice(0, 10).map((src, i) => `<div class="t ${i === 0 ? "active" : ""}" data-thumb="${i}"><img src="${src}" alt="" loading="lazy"></div>`).join("")}
          </div>
        </div>
        <div class="pdp-info" data-reveal data-reveal-delay="1">
          <span class="cat">${p.collection} · ${p.category}</span>
          <h1>${p.name}</h1>
          <div class="pdp-price grad-text">${money(p.price)}</div>
          <div class="stock ${p.available ? "" : "out"}"><i></i>${p.available ? (isMTO ? "Available to order" : "In stock") : "Preorder"}</div>
          <p class="pdp-desc">${p.desc || ""}</p>

          <div class="opt-label">Size${isMTO ? " · made to your measurements" : ""}</div>
          <div class="sizes" id="pdpSizes">
            ${p.sizes.map((s, i) => `<button class="size ${i === 0 ? "active" : ""}" data-size="${s}">${s}</button>`).join("")}
          </div>

          <div class="pdp-actions">
            <button class="btn btn--primary btn--lg" id="pdpAdd">Add to bag · ${money(p.price)}</button>
            <button class="btn btn--ghost btn--lg" id="pdpFav">♡ Save</button>
          </div>
          <p class="muted" style="font-size:.84rem;margin-bottom:1.2rem">${isMTO
            ? "✦ Handcrafted to order in NYC from pure latex. Production ~4 weeks. Bespoke sizing available."
            : "✦ Ready to ship in 2–4 business days. Free shipping over $250."}</p>

          <div class="accordion" id="pdpAcc">
            ${acc("Details", p.desc || "Designed and handmade in New York City with TABBE's signature sculptural spirit.")}
            ${acc("Shipping & returns", isMTO ? "Made-to-order pieces ship in approximately 4 weeks and are final sale. Contact us for bespoke requests." : "Ships in 2–4 business days. Free returns within 14 days on unworn ready-to-wear.")}
            ${acc("Care", isMTO ? "Latex care: store flat away from light & heat, shine with silicone polish, avoid contact with metals." : "Gentle cold wash, lay flat to dry. Keep prints away from direct heat.")}
          </div>
        </div>
      </div>

      <section class="section">
        <div class="head-row"><div><span class="eyebrow">You may also feel</span><h2 style="font-size:clamp(1.6rem,3.5vw,2.4rem)">More from ${p.collection}</h2></div>
          <a class="btn btn--ghost" href="shop.html">View all</a></div>
        <div class="grid-products" id="pdpRelated"></div>
      </section>
    </div>`;

  function acc(title, body) {
    return `<div class="acc-item"><button class="acc-head">${title}<span class="plus">+</span></button>
      <div class="acc-body"><div class="inner">${body}</div></div></div>`;
  }

  const mainImg = document.getElementById("pdpMainImg");
  document.getElementById("pdpThumbs").addEventListener("click", (e) => {
    const t = e.target.closest("[data-thumb]"); if (!t) return;
    document.querySelectorAll("#pdpThumbs .t").forEach((x) => x.classList.remove("active"));
    t.classList.add("active");
    mainImg.src = imgs[+t.dataset.thumb];
  });
  document.getElementById("pdpSizes").addEventListener("click", (e) => {
    const b = e.target.closest("[data-size]"); if (!b) return;
    size = b.dataset.size;
    document.querySelectorAll("#pdpSizes .size").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
  });
  document.getElementById("pdpAcc").addEventListener("click", (e) => {
    const h = e.target.closest(".acc-head"); if (!h) return;
    const item = h.parentElement, body = item.querySelector(".acc-body");
    const open = item.classList.toggle("open");
    body.style.maxHeight = open ? body.scrollHeight + "px" : "0";
  });
  document.getElementById("pdpAdd").addEventListener("click", () => TABBE.addToCart(p.id, size));
  const favBtn = document.getElementById("pdpFav");
  const syncFav = () => { favBtn.innerHTML = TABBE.isWished(p.id) ? "♥ Saved" : "♡ Save"; };
  syncFav();
  favBtn.addEventListener("click", () => { TABBE.toggleWish(p.id); syncFav(); });

  const related = PRODUCTS.filter((x) => x.collection === p.collection && x.id !== p.id);
  const pool = (related.length ? related : PRODUCTS.filter((x) => x.id !== p.id)).slice(0, 4);
  document.getElementById("pdpRelated").innerHTML = pool.map((rp) => TABBE.productCard(rp)).join("");

  TABBE.reveals();
})();

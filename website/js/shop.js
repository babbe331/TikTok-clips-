/* =========================================================================
   TABBE DESIGNS — Shop page: filtering, search, sort, render
   ========================================================================= */
(function () {
  if (!document.getElementById("shopGrid")) return;

  const grid = document.getElementById("shopGrid");
  const countEl = document.getElementById("resultCount");
  const chipsEl = document.getElementById("catChips");
  const lineChipsEl = document.getElementById("lineChips");
  const searchEl = document.getElementById("shopSearch");
  const sortEl = document.getElementById("shopSort");
  const money = (n) => "$" + n.toLocaleString("en-US");

  const params = new URLSearchParams(location.search);
  const state = {
    cat: params.get("cat") || "All",
    line: params.get("line") || "all",
    q: "",
    sort: "featured",
    favOnly: params.get("fav") === "1",
  };

  const cats = ["All", ...new Set(PRODUCTS.map((p) => p.category))];

  function card(p) {
    const swatches = (p.colors || []).slice(0, 4).map((c) => `<i style="background:${c}"></i>`).join("");
    const badge = p.badge ? `<span class="card-badge ${p.line === "made-to-order" ? "mto" : ""}">${p.badge}</span>` : "";
    const faved = window.TABBE && TABBE.isWished(p.id) ? "active" : "";
    return `<article class="card" data-reveal>
      <div class="card-media">
        ${badge}
        <button class="card-fav ${faved}" data-fav="${p.id}" aria-label="Save">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>
        </button>
        <a href="product.html?id=${p.id}" aria-label="${p.name}">${window.productArt(p.art, p.name.length)}</a>
        <button class="card-quick" data-add="${p.id}">Quick add — ${money(p.price)}</button>
      </div>
      <a class="card-body" href="product.html?id=${p.id}">
        <span class="card-cat">${p.category}</span>
        <span class="card-name">${p.name}</span>
        <span class="card-price">${money(p.price)}</span>
        <div class="card-swatches">${swatches}</div>
      </a>
    </article>`;
  }

  function apply() {
    let list = PRODUCTS.slice();
    if (state.line !== "all") list = list.filter((p) => p.line === state.line);
    if (state.cat !== "All") list = list.filter((p) => p.category === state.cat);
    if (state.favOnly) list = list.filter((p) => window.TABBE && TABBE.isWished(p.id));
    if (state.q) {
      const q = state.q.toLowerCase();
      list = list.filter((p) => (p.name + p.category + p.collection + p.desc).toLowerCase().includes(q));
    }
    if (state.sort === "low") list.sort((a, b) => a.price - b.price);
    else if (state.sort === "high") list.sort((a, b) => b.price - a.price);
    else if (state.sort === "name") list.sort((a, b) => a.name.localeCompare(b.name));

    countEl.textContent = `${list.length} piece${list.length === 1 ? "" : "s"}`;
    grid.innerHTML = list.length ? list.map(card).join("")
      : `<p class="muted" style="grid-column:1/-1;padding:2rem 0">Nothing matches yet — try clearing a filter.</p>`;
    window.TABBE && TABBE.reveals();
  }

  function buildChips() {
    chipsEl.innerHTML = cats.map((c) => `<button class="chip ${c === state.cat ? "active" : ""}" data-cat="${c}">${c}</button>`).join("");
    lineChipsEl.innerHTML = [["all","Everything"],["ready-to-wear","Ready to Wear"],["made-to-order","Made to Order"]]
      .map(([v, l]) => `<button class="chip ${v === state.line ? "active" : ""}" data-line="${v}">${l}</button>`).join("");
  }

  chipsEl.addEventListener("click", (e) => { const b = e.target.closest("[data-cat]"); if (!b) return; state.cat = b.dataset.cat; buildChips(); apply(); });
  lineChipsEl.addEventListener("click", (e) => { const b = e.target.closest("[data-line]"); if (!b) return; state.line = b.dataset.line; buildChips(); apply(); });
  searchEl.addEventListener("input", (e) => { state.q = e.target.value; apply(); });
  sortEl.addEventListener("change", (e) => { state.sort = e.target.value; apply(); });

  if (state.favOnly) { const t = document.getElementById("shopTitle"); if (t) t.textContent = "Your Wishlist"; }

  buildChips();
  apply();
})();

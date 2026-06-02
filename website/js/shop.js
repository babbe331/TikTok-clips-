/* =========================================================================
   TABBE DESIGNS — Shop page: filtering, search, sort, render (real images)
   ========================================================================= */
(function () {
  if (!document.getElementById("shopGrid")) return;

  const grid = document.getElementById("shopGrid");
  const countEl = document.getElementById("resultCount");
  const chipsEl = document.getElementById("catChips");
  const lineChipsEl = document.getElementById("lineChips");
  const searchEl = document.getElementById("shopSearch");
  const sortEl = document.getElementById("shopSort");

  const params = new URLSearchParams(location.search);
  const state = {
    cat: params.get("cat") || "All",
    line: params.get("line") || "all",
    q: "", sort: "featured",
    favOnly: params.get("fav") === "1",
  };

  const cats = ["All", ...Array.from(new Set(PRODUCTS.map((p) => p.category)))];

  function apply() {
    let list = PRODUCTS.slice();
    if (state.line !== "all") list = list.filter((p) => p.line === state.line);
    if (state.cat !== "All") list = list.filter((p) => p.category === state.cat);
    if (state.favOnly) list = list.filter((p) => TABBE.isWished(p.id));
    if (state.q) {
      const q = state.q.toLowerCase();
      list = list.filter((p) => (p.name + p.category + p.collection + p.desc).toLowerCase().includes(q));
    }
    if (state.sort === "low") list.sort((a, b) => a.price - b.price);
    else if (state.sort === "high") list.sort((a, b) => b.price - a.price);
    else if (state.sort === "name") list.sort((a, b) => a.name.localeCompare(b.name));

    countEl.textContent = `${list.length} piece${list.length === 1 ? "" : "s"}`;
    grid.innerHTML = list.length ? list.map((p) => TABBE.productCard(p)).join("")
      : `<p class="muted" style="grid-column:1/-1;padding:2rem 0">Nothing matches yet — try clearing a filter.</p>`;
    TABBE.reveals();
  }

  function buildChips() {
    chipsEl.innerHTML = cats.map((c) => `<button class="chip ${c === state.cat ? "active" : ""}" data-cat="${c}">${c}</button>`).join("");
    lineChipsEl.innerHTML = [["all", "Everything"], ["ready-to-wear", "Ready to Wear"], ["made-to-order", "Made to Order"]]
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

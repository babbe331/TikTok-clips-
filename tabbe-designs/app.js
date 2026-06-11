/* ════════════════════════════════════════════════════════
   TABBE DESIGNS — interactions
   ════════════════════════════════════════════════════════ */
'use strict';

const $  = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];
const CDN = 'https://tabbedesigns.com/cdn/shop/files/';
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

const money = n => {
  const v = Number(n);
  return '$' + v.toLocaleString('en-US', { minimumFractionDigits: 2 });
};

/* ── collection lookbooks (images straight from tabbedesigns.com) ── */
const COLLECTIONS = {
  inplay: {
    title: 'In Play — FW26',
    desc: 'Movement and adaptation. Drawing from the butterfly’s migration toward the winter months, In Play mirrors how people respond to change together — refining TABBE’s sculptural, inflatable language into bold, playful pieces built for everyday wear.',
    filter: 'ready-to-wear',
    imgs: ['Screenshot_2026-02-20_at_12.34.18_PM.png','Screenshot_2026-02-20_at_12.34.31_PM.png','Screenshot_2026-02-20_at_12.34.49_PM.png','Screenshot_2026-02-20_at_12.35.08_PM.png','Screenshot_2026-02-20_at_12.35.22_PM.png','Screenshot_2026-02-20_at_12.35.34_PM.png','Screenshot_2026-02-20_at_12.35.43_PM.png','Screenshot_2026-02-20_at_12.36.42_PM.png','Screenshot_2026-02-20_at_12.36.51_PM.png','Screenshot_2026-02-20_at_12.36.59_PM.png','Screenshot_2026-02-20_at_12.37.08_PM.png','Screenshot_2026-02-20_at_12.38.00_PM.png','Screenshot_2026-02-20_at_12.39.21_PM.png','Screenshot_2026-02-20_at_12.40.15_PM.png','Screenshot_2026-02-20_at_12.40.46_PM.png'],
  },
  butterfly: {
    title: 'The Butterfly Effect — SS25',
    desc: 'A tribute to personal transformation: how heartbreak, shame, and loss ripple into growth, resilience, and self-worth. Every form — human or environmental — carries its history, and this collection celebrates becoming through hardship.',
    filter: 'tops',
    imgs: ['Screenshot_2026-02-20_at_10.36.49_AM.png','Screenshot_2026-02-20_at_10.38.27_AM.png','Screenshot2026-02-20at11.14.09AM.png','Screenshot2026-02-17at12.43.56PM.png','Screenshot_2026-02-20_at_12.20.46_PM.png','Screenshot_2026-02-20_at_12.21.38_PM.png','Screenshot_2026-02-20_at_12.21.58_PM.png','Screenshot_2026-02-20_at_12.22.34_PM.png','Screenshot_2026-02-20_at_12.23.46_PM.png','Screenshot_2026-02-20_at_12.24.17_PM.png','Screenshot_2026-02-20_at_12.25.09_PM.png','Screenshot_2026-02-20_at_12.29.55_PM.png','Screenshot_2026-02-17_at_11.50.27_AM.png','Screenshot_2026-02-20_at_12.26.58_PM.png','Screenshot_2026-02-20_at_12.27.26_PM.png','Screenshot_2026-02-20_at_12.27.51_PM.png','Screenshot_2026-02-20_at_12.28.14_PM.png','Screenshot_2026-02-20_at_12.28.34_PM.png','Screenshot_2026-02-20_at_12.28.46_PM.png','Screenshot_2026-02-20_at_12.29.40_PM.png'],
  },
  cottoncandy: {
    title: '“Cotton Candy” Capsule',
    desc: 'Born at the intersection of mental health and artistic expression — shapes and colors influenced by the playful yet profound artwork of therapy sessions. Innocence on the surface, hidden complexity underneath. Every piece handcrafted in New York, made to order.',
    filter: 'made-to-order',
    imgs: ['4M2A6705.jpg','4M2A66514.jpg','4M2A64622.jpg','4M2A68193.jpg','4M2A6837.jpg','4M2A6375_3.jpg','4M2A65402.jpg','Screenshot_2026-02-20_at_12.14.52_PM.png','Screenshot_2026-02-20_at_12.15.22_PM.png','IMG_9920.jpg','IMG_9896.jpg','IMG_9956.jpg','Screenshot2025-09-24at2.51.45PM.png','Screenshot_2026-02-20_at_12.16.37_PM.png','4M2A6529_2.jpg','4M2A6747_2644d387-e4b6-4115-a340-564626d02462.jpg','4M2A6763_4dca21bf-3ab3-49da-9a54-aea78a08f787.jpg'],
  },
  bubblewrap: {
    title: 'Bubble Wrap',
    desc: 'Cartoon-like shapes and neon colors derived from brain scans — the emotional highs and lows of manic episodes made visible. Latex tailoring and bubble forms echo anxiety’s physical weight, using hyperbolic, humorous visuals to destigmatize mental health.',
    filter: 'inflatable-latex',
    imgs: ['Screenshot2024-06-03at12.35.32PM.png','Screenshot2024-06-03at12.45.20PM.png','Screenshot2024-06-03at12.50.50PM.png','Screenshot2024-06-03at12.55.15PM.png','Screenshot2024-06-03at1.01.33PM.png','Screenshot2024-06-03at1.15.26PM.png','Screenshot2024-06-03at1.21.54PM.png','Screenshot2024-06-03at1.37.47PM.png','Screenshot2024-06-03at1.40.46PM.png'],
  },
};

/* publication gallery (press archive on tabbedesigns.com/pages/publication) */
const PUBLICATIONS = [
  '1_bc7b90fd-a4a6-4929-bba3-b66b7a99ada7.jpg','2_40cc79a8-aadb-4a72-a5eb-6496fb64a5b9.jpg','3_a920a59f-332f-49d6-b8ff-3e1300f0bf10.jpg','4_128153e8-cddc-4462-857c-207fdb36a089.jpg','5_f1534f4f-c9a5-4c2c-8f36-a3b3be6efc8c.jpg','6_64569a1d-bed9-4d4a-af29-0a5d823fff50.jpg','7_5dafcc54-ca92-464a-af3c-3d509d2dbe97.jpg','8_0fdec581-5095-475b-925a-0cc1bcb73751.jpg','9_6b523058-5312-4015-8646-4f912a784632.jpg','10_2b81a360-4edf-450c-8762-dad56fe156e8.jpg','11_b071d0c6-c8f4-4c9c-8ed5-0a58614b7cab.jpg','12_77703b1b-644a-4c87-bbc6-9a0bac17005a.jpg','13.jpg','14.jpg','15.jpg','16.jpg','17.png','18.jpg','19_67e0ef65-3ab9-42df-965c-f93e5fa3e66b.jpg','20.jpg','21.jpg','22.jpg','23.jpg','24.jpg','25.jpg','27.jpg','28.png','29.png','30.png','31.png','32.png','33.png','34.png','35.png','36.png','37.png','38.png','39.png','40.png','41.jpg','42.jpg',
];

/* ════════ loader: bubble inflates with progress, then pops ════════ */
(() => {
  const loader = $('#loader'), pct = $('#loaderPct'), bar = $('#loaderBar');
  const bubble = $('#loaderBubble');
  let p = 0, finished = false;
  const finish = () => {
    if (finished) return;
    finished = true;
    pct.textContent = '100';
    bar.style.width = '100%';
    bubble.style.transform = '';
    bubble.classList.add('pop');
    setTimeout(() => loader.classList.add('done'), 420);
  };
  const tick = () => {
    if (finished) return;
    p = Math.min(p + 4 + Math.random() * 12, 96);
    pct.textContent = String(Math.round(p)).padStart(3, '0');
    bar.style.width = p + '%';
    bubble.style.transform = `scale(${0.3 + (p / 100) * 0.7})`;
    setTimeout(tick, 70 + Math.random() * 90);
  };
  tick();
  addEventListener('load', () => setTimeout(finish, 300));
  setTimeout(finish, 3200); // safety net
})();

/* ════════ glossy bubble canvas — click/tap a bubble to pop it ════════ */
(() => {
  if (reducedMotion) return;
  const cv = $('#bubbleCanvas'), ctx = cv.getContext('2d');
  let W, H, bubbles = [], frags = [];
  const COLORS = ['255,62,165', '205,180,255', '174,227,255', '255,210,232'];

  const resize = () => { W = cv.width = innerWidth; H = cv.height = innerHeight; };
  resize(); addEventListener('resize', resize);

  const spawn = (x, y) => ({
    x: x ?? Math.random() * W,
    y: y ?? H + 40,
    r: 6 + Math.random() * 22,
    vy: -(0.25 + Math.random() * 0.7),
    vx: (Math.random() - 0.5) * 0.3,
    c: COLORS[Math.random() * COLORS.length | 0],
    a: 0.25 + Math.random() * 0.3,
    wob: Math.random() * Math.PI * 2,
  });
  for (let i = 0; i < 22; i++) bubbles.push({ ...spawn(), y: Math.random() * H });

  const pop = b => {
    // burst into glossy fragments
    for (let i = 0; i < 8; i++) {
      const ang = (i / 8) * Math.PI * 2;
      frags.push({
        x: b.x, y: b.y, r: 1.5 + Math.random() * 3,
        vx: Math.cos(ang) * (1.5 + Math.random() * 2),
        vy: Math.sin(ang) * (1.5 + Math.random() * 2),
        c: b.c, life: 1,
      });
    }
  };

  addEventListener('pointerdown', e => {
    if (e.target.closest('a,button,input,select,textarea,.modal,.drawer')) return;
    const { clientX: x, clientY: y } = e;
    let hit = false;
    bubbles = bubbles.filter(b => {
      if (Math.hypot(b.x - x, b.y - y) < b.r + 22) { pop(b); hit = true; return false; }
      return true;
    });
    if (!hit) bubbles.push({ ...spawn(x, y), r: 10 + Math.random() * 16, vy: -1.2 });
  });

  const drawBubble = b => {
    const g = ctx.createRadialGradient(b.x - b.r * 0.35, b.y - b.r * 0.35, b.r * 0.1, b.x, b.y, b.r);
    g.addColorStop(0, `rgba(255,255,255,${b.a * 0.9})`);
    g.addColorStop(0.5, `rgba(${b.c},${b.a * 0.25})`);
    g.addColorStop(1, `rgba(${b.c},${b.a * 0.55})`);
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
    ctx.fillStyle = g;
    ctx.fill();
    ctx.strokeStyle = `rgba(${b.c},${b.a * 0.7})`;
    ctx.lineWidth = 1;
    ctx.stroke();
    // specular highlight
    ctx.beginPath();
    ctx.ellipse(b.x - b.r * 0.35, b.y - b.r * 0.4, b.r * 0.22, b.r * 0.12, -0.5, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${Math.min(b.a * 2.4, 0.85)})`;
    ctx.fill();
  };

  (function tick() {
    ctx.clearRect(0, 0, W, H);
    bubbles = bubbles.filter(b => b.y + b.r > -40);
    if (bubbles.length < 22) bubbles.push(spawn());
    for (const b of bubbles) {
      b.wob += 0.02;
      b.x += b.vx + Math.sin(b.wob) * 0.25;
      b.y += b.vy;
      drawBubble(b);
    }
    frags = frags.filter(f => f.life > 0);
    for (const f of frags) {
      f.x += f.vx; f.y += f.vy; f.vy += 0.05; f.life -= 0.03;
      ctx.beginPath();
      ctx.arc(f.x, f.y, f.r * f.life, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${f.c},${f.life * 0.7})`;
      ctx.fill();
    }
    requestAnimationFrame(tick);
  })();
})();

/* ════════ bubble cursor + magnetic elements ════════ */
(() => {
  if (!matchMedia('(hover:hover) and (pointer:fine)').matches || reducedMotion) return;
  const dot = $('#cursor'), tag = $('#cursorTag');

  addEventListener('pointermove', e => {
    const { clientX: x, clientY: y } = e;
    dot.style.left = x + 'px'; dot.style.top = y + 'px';
    tag.style.left = x + 'px'; tag.style.top = y + 'px';
    const t = e.target.closest('a,button,.product-card,.look,input,select,textarea');
    document.body.classList.toggle('cursor-hover', !!t);
    tag.textContent = e.target.closest('.product-card') ? 'VIEW' :
                      e.target.closest('.look') ? 'DRAG' :
                      e.target.closest('a,button,input,select,textarea') ? '' : 'POP';
  }, { passive: true });

  // the cursor itself pops like a bubble on click
  addEventListener('pointerdown', () => {
    dot.classList.add('popping');
    setTimeout(() => dot.classList.remove('popping'), 240);
  });

  // magnetic pull on tagged elements
  document.addEventListener('pointermove', e => {
    $$('[data-magnet]').forEach(el => {
      const r = el.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width / 2);
      const dy = e.clientY - (r.top + r.height / 2);
      const d = Math.hypot(dx, dy);
      el.style.translate = d < 90 ? `${dx * 0.15}px ${dy * 0.15}px` : '';
    });
  }, { passive: true });
})();

/* ════════ live NYC clock ════════ */
(() => {
  const el = $('#clock');
  if (!el) return;
  const fmt = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York', hour12: false,
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
  const tick = () => { el.textContent = fmt.format(new Date()); };
  tick();
  setInterval(tick, 1000);
})();

/* ════════ nav / scroll chrome ════════ */
(() => {
  const nav = $('#nav'), bar = $('#scrollProgress'), top = $('#toTop');
  const burger = $('#burger'), links = $('#navLinks');
  addEventListener('scroll', () => {
    const y = scrollY;
    nav.classList.toggle('scrolled', y > 40);
    top.classList.toggle('show', y > 700);
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';
  }, { passive: true });
  top.addEventListener('click', () => scrollTo({ top: 0, behavior: 'smooth' }));
  burger.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    burger.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', open);
  });
  links.addEventListener('click', () => { links.classList.remove('open'); burger.classList.remove('open'); });
})();

/* ════════ hero parallax ════════ */
(() => {
  if (reducedMotion) return;
  const floats = $$('.hero-photo');
  addEventListener('pointermove', e => {
    const cx = e.clientX / innerWidth - 0.5, cy = e.clientY / innerHeight - 0.5;
    floats.forEach(f => {
      const d = +f.dataset.depth * 360;
      f.style.transform = `translate(${cx * d}px,${cy * d}px)`;
    });
  }, { passive: true });
})();

/* ════════ scroll reveal + count-up ════════ */
(() => {
  const io = new IntersectionObserver(entries => {
    for (const en of entries) {
      if (!en.isIntersecting) continue;
      en.target.classList.add('in');
      io.unobserve(en.target);
    }
  }, { threshold: 0.12 });
  $$('.reveal').forEach(el => io.observe(el));

  const counters = new IntersectionObserver(entries => {
    for (const en of entries) {
      if (!en.isIntersecting) continue;
      const el = en.target, target = +el.dataset.count, t0 = performance.now();
      const step = now => {
        const p = Math.min((now - t0) / 1400, 1);
        el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
      counters.unobserve(el);
    }
  }, { threshold: 0.6 });
  $$('.stat-num').forEach(el => counters.observe(el));
})();

/* ════════ ticker: duplicate track for seamless loop ════════ */
(() => {
  const t = $('#tickerTrack');
  t.innerHTML += t.innerHTML;
})();

/* ════════ collections ════════ */
(() => {
  const panel = $('#collectionPanel'), book = $('#lookbook');
  const title = $('#colTitle'), desc = $('#colDesc'), link = $('#colLink');

  const render = key => {
    const c = COLLECTIONS[key];
    title.textContent = c.title;
    desc.textContent = c.desc;
    link.dataset.filterLink = c.filter;
    book.innerHTML = c.imgs.map((f, i) =>
      `<figure class="look" data-n="LOOK ${String(i + 1).padStart(2, '0')} / ${String(c.imgs.length).padStart(2, '0')}"><img src="${CDN}${f}?width=600" alt="${c.title} look ${i + 1}" loading="lazy" draggable="false"></figure>`
    ).join('');
    book.scrollLeft = 0;
  };
  render('inplay');

  $$('.ctab').forEach(tab => tab.addEventListener('click', () => {
    if (tab.classList.contains('active')) return;
    $$('.ctab').forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');
    panel.classList.add('switching');
    setTimeout(() => { render(tab.dataset.col); panel.classList.remove('switching'); }, 380);
  }));

  // drag-to-scroll lookbook
  let down = false, startX = 0, startL = 0;
  book.addEventListener('pointerdown', e => {
    down = true; startX = e.clientX; startL = book.scrollLeft;
    book.classList.add('dragging'); book.setPointerCapture(e.pointerId);
  });
  book.addEventListener('pointermove', e => { if (down) book.scrollLeft = startL - (e.clientX - startX); });
  ['pointerup', 'pointercancel'].forEach(ev =>
    book.addEventListener(ev, () => { down = false; book.classList.remove('dragging'); }));
})();

/* ════════ wishlist ════════ */
const Wish = {
  key: 'tabbe-wishlist',
  get() { try { return JSON.parse(localStorage.getItem(this.key)) || []; } catch { return []; } },
  has(h) { return this.get().includes(h); },
  toggle(h) {
    const list = this.get();
    const i = list.indexOf(h);
    i >= 0 ? list.splice(i, 1) : list.push(h);
    localStorage.setItem(this.key, JSON.stringify(list));
    this.refresh();
    return i < 0;
  },
  refresh() {
    const list = this.get();
    const count = $('#wishCount');
    count.textContent = list.length;
    count.classList.add('pop');
    setTimeout(() => count.classList.remove('pop'), 300);
    $$('.pc-wish').forEach(b => {
      const on = list.includes(b.dataset.handle);
      b.classList.toggle('active', on);
      b.textContent = on ? '♥' : '♡';
    });
    const items = $('#drawerItems');
    $('#drawerEmpty').style.display = list.length ? 'none' : 'block';
    items.innerHTML = list.map(h => {
      const p = PRODUCTS.find(x => x.handle === h);
      if (!p) return '';
      return `<div class="drawer-item">
        <img src="${p.images[0]}&width=200" alt="${p.title}">
        <div><h4>${p.title}</h4><p>${p.multiPrice ? 'from ' : ''}${money(p.minPrice)}</p>
        <a href="https://tabbedesigns.com/products/${p.handle}" target="_blank" rel="noopener">View on store ↗</a></div>
        <button class="drawer-remove" data-remove="${h}" aria-label="Remove ${p.title}">✕</button>
      </div>`;
    }).join('');
  },
};
(() => {
  const drawer = $('#wishDrawer');
  $('#wishBtn').addEventListener('click', () => { drawer.hidden = false; document.body.style.overflow = 'hidden'; });
  drawer.addEventListener('click', e => {
    if (e.target.closest('[data-close-drawer]')) { drawer.hidden = true; document.body.style.overflow = ''; }
    const rm = e.target.closest('[data-remove]');
    if (rm) Wish.toggle(rm.dataset.remove);
  });
})();

/* ════════ shop ════════ */
const Shop = {
  mode: 'all', filter: 'all', query: '', sort: 'featured',
  grid: $('#productGrid'),

  list() {
    let list = PRODUCTS.filter(p =>
      (this.mode === 'all' || p.cats.includes(this.mode)) &&
      (this.filter === 'all' || p.cats.includes(this.filter)) &&
      (!this.query || (p.title + ' ' + p.type + ' ' + p.tags.join(' ')).toLowerCase().includes(this.query))
    );
    if (this.sort === 'low')  list = [...list].sort((a, b) => a.minPrice - b.minPrice);
    if (this.sort === 'high') list = [...list].sort((a, b) => b.minPrice - a.minPrice);
    if (this.sort === 'az')   list = [...list].sort((a, b) => a.title.localeCompare(b.title));
    return list;
  },

  countLabel(n) {
    if (this.mode === 'made-to-order') return `${n} piece${n === 1 ? '' : 's'}, each one handmade for you in New York`;
    if (this.mode === 'ready-to-wear') return `${n} piece${n === 1 ? '' : 's'} in stock — ready to ship to your door`;
    return `${n} little works of art to fall in love with`;
  },

  render() {
    const list = this.list();
    $('#shopCount').textContent = list.length ? this.countLabel(list.length) : 'nothing matches — try another word or filter ✦';
    this.grid.innerHTML = list.map((p, i) => {
      const mto = p.cats.includes('made-to-order');
      const wished = Wish.has(p.handle);
      const idx = PRODUCTS.indexOf(p) + 1;
      return `<article class="product-card" data-handle="${p.handle}" style="animation-delay:${Math.min(i * 45, 450)}ms" tabindex="0" role="button" aria-label="${p.title}, ${money(p.minPrice)}, ${mto ? 'made to order' : 'in stock'}">
        <div class="pc-head"><span class="mono">№ ${String(idx).padStart(2, '0')}</span><span class="pc-tag ${mto ? 'tag-mto' : 'tag-stock'}">${mto ? 'made to order' : 'in stock'}</span></div>
        <div class="pc-img">
          <img src="${p.images[0]}&width=600" alt="${p.title}" loading="lazy">
          ${p.images[1] ? `<img class="img-b" src="${p.images[1]}&width=600" alt="" loading="lazy">` : ''}
          <button class="pc-wish" data-handle="${p.handle}" aria-label="Toggle wishlist for ${p.title}">${wished ? '♥' : '♡'}</button>
        </div>
        <div class="pc-body">
          <h3 class="pc-title">${p.title}</h3>
          <p class="pc-price">${p.multiPrice ? '<small>from </small>' : ''}${money(p.minPrice)}</p>
        </div>
        <p class="pc-foot">take a closer look</p>
      </article>`;
    }).join('');
  },
};

(() => {
  Shop.render();
  Wish.refresh();

  $$('.mode-tab').forEach(tab => tab.addEventListener('click', () => {
    $$('.mode-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    Shop.mode = tab.dataset.mode;
    Shop.render(); Wish.refresh();
  }));

  $('#filterChips').addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    $$('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    Shop.filter = chip.dataset.filter;
    Shop.render(); Wish.refresh();
  });
  $('#shopSearch').addEventListener('input', e => {
    Shop.query = e.target.value.trim().toLowerCase();
    Shop.render(); Wish.refresh();
  });
  $('#shopSort').addEventListener('change', e => {
    Shop.sort = e.target.value;
    Shop.render(); Wish.refresh();
  });

  // footer / collection links that pre-apply a mode or filter
  document.addEventListener('click', e => {
    const link = e.target.closest('[data-filter-link]');
    if (!link) return;
    const target = link.dataset.filterLink;
    const modeTab = $(`.mode-tab[data-mode="${target}"]`);
    const chip = $(`.chip[data-filter="${target}"]`);
    if (modeTab) {
      $(`.chip[data-filter="all"]`).click();
      modeTab.click();
    } else if (chip) {
      $(`.mode-tab[data-mode="all"]`).click();
      chip.click();
    }
    $('#shop').scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth' });
    e.preventDefault();
  });

  Shop.grid.addEventListener('click', e => {
    const wish = e.target.closest('.pc-wish');
    if (wish) { Wish.toggle(wish.dataset.handle); e.stopPropagation(); return; }
    const card = e.target.closest('.product-card');
    if (card) Modal.open(card.dataset.handle);
  });
  Shop.grid.addEventListener('keydown', e => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const card = e.target.closest('.product-card');
    if (card) { e.preventDefault(); Modal.open(card.dataset.handle); }
  });
})();

/* ════════ product modal ════════ */
const Modal = {
  el: $('#productModal'), product: null,

  open(handle) {
    const p = PRODUCTS.find(x => x.handle === handle);
    if (!p) return;
    this.product = p;
    const idx = PRODUCTS.indexOf(p) + 1;
    const status = p.cats.includes('made-to-order') ? 'made to order, just for you' : 'in stock — ready to ship';
    $('#modalType').textContent = `№ ${String(idx).padStart(2, '0')} ✦ ${status}${p.type ? ' ✦ ' + p.type : ''}`;
    $('#modalTitle').textContent = p.title;
    $('#modalPrice').textContent = (p.multiPrice ? 'from ' : '') + money(p.minPrice);
    $('#modalDesc').textContent = p.desc;
    $('#modalBuy').href = `https://tabbedesigns.com/products/${p.handle}`;
    $('#modalTags').innerHTML = p.tags.map(t => `<span>${t}</span>`).join('');
    this.updateWishBtn();

    $('#modalThumbs').innerHTML = p.images.map((src, i) =>
      `<button data-i="${i}" class="${i === 0 ? 'active' : ''}" aria-label="Photo ${i + 1}"><img src="${src}&width=160" alt=""></button>`
    ).join('');
    this.setImage(0);

    const hasSizes = !(p.variants.length === 1 && p.variants[0].title === 'Default Title');
    $('#modalVariants').innerHTML = hasSizes ? p.variants.map((v, i) =>
      `<button class="variant-pill ${v.available ? '' : 'soldout'}" data-i="${i}" ${v.available ? '' : 'disabled'}>
        ${v.title} · ${money(v.price)}</button>`
    ).join('') : '';

    this.el.hidden = false;
    document.body.style.overflow = 'hidden';
    $('.modal-card', this.el).scrollTop = 0;
  },

  setImage(i) {
    const img = $('#modalImg');
    img.src = this.product.images[i] + '&width=1000';
    img.alt = this.product.title;
    $$('#modalThumbs button').forEach((b, j) => b.classList.toggle('active', i === j));
  },

  updateWishBtn() {
    const on = Wish.has(this.product.handle);
    $('#modalWish').textContent = on ? '♥ Wishlisted' : '♡ Wishlist';
  },

  close() { this.el.hidden = true; document.body.style.overflow = ''; },
};
(() => {
  Modal.el.addEventListener('click', e => {
    if (e.target.closest('[data-close]')) return Modal.close();
    const thumb = e.target.closest('#modalThumbs button');
    if (thumb) return Modal.setImage(+thumb.dataset.i);
    const pill = e.target.closest('.variant-pill:not(.soldout)');
    if (pill) {
      $$('.variant-pill').forEach(b => b.classList.remove('selected'));
      pill.classList.add('selected');
      $('#modalPrice').textContent = money(Modal.product.variants[+pill.dataset.i].price);
    }
  });
  $('#modalWish').addEventListener('click', () => { Wish.toggle(Modal.product.handle); Modal.updateWishBtn(); });
  addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (!Modal.el.hidden) Modal.close();
    const drawer = $('#wishDrawer');
    if (!drawer.hidden) { drawer.hidden = true; document.body.style.overflow = ''; }
  });
})();

/* ════════ press marquee ════════ */
(() => {
  const track = $('#pressTrack');
  const imgs = PUBLICATIONS.map(f =>
    `<img src="${CDN}${f}?width=500" alt="TABBE Designs publication feature" loading="lazy">`).join('');
  track.innerHTML = imgs + imgs; // doubled for seamless loop
})();

/* ════════ newsletter (front-end confirmation) ════════ */
(() => {
  $('#newsletterForm').addEventListener('submit', e => {
    e.preventDefault();
    const input = $('input', e.target);
    $('#newsletterMsg').textContent = `you’re in the bubble, ${input.value} ✦ welcome to TABBE`;
    input.value = '';
  });
})();

/* ════════ footer year ════════ */
$('#year').textContent = new Date().getFullYear();

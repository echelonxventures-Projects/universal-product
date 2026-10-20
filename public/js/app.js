/* LUXORA Platform - premium storefront client. 100% config + meta-model driven. */
"use strict";

let CFG = null, META = null, PROV = null;
const S = { user: null, zip: "00000", gift: 0, cartCount: 0, cartSub: 0, viewed: [] };
const PAGE = () => document.body.dataset.page;

const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function T(key, vars) {
  let t = (CFG && CFG.copy && CFG.copy[key]) || key;
  if (vars) for (const [k, v] of Object.entries(vars)) t = t.split("{" + k + "}").join(v);
  return t;
}
function money(n) {
  if (S.disp) return S.disp.symbol + (+n * S.disp.fx).toLocaleString(CFG.commerce.locale, { minimumFractionDigits: S.disp.decimals, maximumFractionDigits: S.disp.decimals });
  try { return new Intl.NumberFormat(CFG.commerce.locale, { style: "currency", currency: CFG.commerce.currency, maximumFractionDigits: CFG.commerce.decimals == null ? 2 : CFG.commerce.decimals, minimumFractionDigits: CFG.commerce.decimals == null ? 2 : CFG.commerce.decimals }).format(+n); }
  catch (e) { return CFG.commerce.symbol + (+n).toFixed(2); }
}
function priceHtml(n) {
  const d = S.disp ? S.disp.decimals : (CFG.commerce.decimals == null ? 2 : CFG.commerce.decimals);
  const [w, c] = Math.abs(+n * (S.disp ? S.disp.fx : 1)).toFixed(d).split(".");
  const sym = S.disp ? S.disp.symbol : CFG.commerce.symbol;
  return `<span class="p-sup">${esc(sym)}</span><span class="p-int">${Number(w).toLocaleString(CFG.commerce.locale)}</span>${c ? `<span class="p-sup">${c}</span>` : ""}`;
}
function computeDisp() {
  S.disp = null;
  if (!(CFG.gates || {})["storefront.currency_switch"]) return;
  const want = localStorage.getItem("azcur"); if (!want) return;
  const cs = (CFG.geo && CFG.geo.currencies) || [];
  const store = cs.find(c => c.code === CFG.commerce.currency), disp = cs.find(c => c.code === want);
  if (!store || !disp || disp.code === store.code) return;
  S.disp = { code: disp.code, symbol: disp.symbol, decimals: disp.decimals, fx: (store.usd || 1) / (disp.usd || 1) };
}
function starsHtml(r) { return `<span class="stars" title="${r} / 5"><span class="stars-fill" style="width:${(r / 5) * 100}%">★★★★★</span><span class="stars-bg">★★★★★</span></span>`; }
function prioBadge() { return `<span class="prio-badge">✦ ${esc(T("priorityBadge"))}</span>`; }
function linkify(m) {
  return esc(m).replace(/\/(platform|admin)\.html(\?store=[A-Za-z0-9-]+)?/g, function (s) {
    return '<a href="' + s + '" style="text-decoration:underline">' + (s.indexOf("platform") >= 0 ? "Platform console" : "Store console") + " →</a>";
  });
}
/* what each vocabulary row declares: a product type's purchase mode / plainness, a media
   kind's player, the default shipping class */
const metaRow = (list, key) => ((META && META[list]) || []).find(x => (x && x.key) === key) || {};
const typeRow = t => metaRow("productTypes", t);
const isPlain = t => !t || !!typeRow(t).plain;
const mediaPlayer = k => metaRow("mediaKinds", k).player;
function typeIcon(t) { const x = META && META.productTypes.find(p => p.key === t); return x ? x.icon + " " + x.name : ""; }
function discount(p) { return p.l > p.p ? Math.round((1 - p.p / p.l) * 100) : 0; }
function isDeal(p) { return discount(p) >= 10; }
function prodLink(p) { return `product.html?id=${p.id}`; }
function img(p, size) {
  /* a real asset URL (image/video) the catalog or operator supplied renders as the
     actual media; an emoji stays the coloured tile. Public products carry `media` from
     the API, lists/cards fall back to the emoji. */
  const m = p && Array.isArray(p.media) ? p.media.find(x => x && x.url) : null;
  if (m) return `<span class="pimg ${size || ""} pimg-url">${mediaPlayer(m.kind) === "video"
    ? `<video src="${esc(m.url)}" alt="${esc(m.label || "")}" muted playsinline></video>`
    : `<img src="${esc(m.url)}" alt="${esc(m.label || "")}">`}</span>`;
  return `<span class="pimg ${size || ""}" style="--h:${p.h}">${p.e}</span>`;
}
function dDate(days) { const d = new Date(); d.setDate(d.getDate() + days); return d; }
function dLong(days) { return dDate(days).toLocaleDateString(CFG.commerce.locale, { weekday: "long", month: "long", day: "numeric" }); }
function dShort(days) { return dDate(days).toLocaleDateString(CFG.commerce.locale, { month: "long", day: "numeric" }); }
function daysP() { return CFG.commerce.daysPriority; }
function daysS() { return CFG.commerce.daysStandard; }
function deptLabel(d) { const x = CFG.departments.find(z => z.key === d); return x ? x.label : d; }
function brandLabel(b) { const x = (CFG.brands || []).find(z => z.key === b || z.label === b); return x ? x.label : b; }
function humanize(k) { return String(k).replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()); }
function stockText(p) {
  if (!p.st) return `<span class="oos">${esc(T("outOfStock"))}</span>`;
  if (p.st <= 10) return `<span class="stock-low">${esc(T("lowStock", { n: p.st }))}</span>`;
  return `<span class="stock-ok">${esc(T("inStock"))}</span>`;
}
function applyTheme() {
  const t = CFG.theme, r = document.documentElement.style;
  const map = { "--bg": t.bg, "--surface": t.surface, "--ink": t.ink, "--muted": t.muted, "--line": t.line, "--header": t.header, "--header-text": t.headerText, "--header-muted": t.headerMuted, "--accent": t.accent, "--accent-deep": t.accentDeep, "--accent-soft": t.accentSoft, "--price": t.price, "--deal": t.deal, "--success": t.success, "--star": t.star, "--link": t.link, "--link-hover": t.linkHover, "--radius": t.radius, "--radius-btn": t.radiusBtn, "--font-display": t.fontDisplay, "--font-body": t.fontBody };
  for (const [k, v] of Object.entries(map)) r.setProperty(k, v);
  if (t.customCSS) { const st = document.createElement("style"); st.id = "tenant-css"; st.textContent = t.customCSS; document.head.appendChild(st); }
}

function __csrf() { const m = /(?:^|; )azc=([^;]+)/.exec(document.cookie || ""); return m ? m[1] : ""; }
async function api(path, methodOrOpts, body) {
  let method = "GET";
  let bodyData = undefined;
  if (typeof methodOrOpts === "object") {
    method = methodOrOpts.method || "GET";
    bodyData = methodOrOpts.body || methodOrOpts;
  } else {
    method = methodOrOpts;
    bodyData = body;
  }
  const opt = { method, headers: { "Content-Type": "application/json", "x-csrf": __csrf() }, credentials: "same-origin" };
  // For GET/HEAD, convert body to query params instead of sending as body
  if ((method === "GET" || method === "HEAD") && bodyData && typeof bodyData === "object") {
    const qs = Object.entries(bodyData).map(([k,v]) => `${k}=${encodeURIComponent(v)}`).join("&");
    if (qs) {
      path += path.includes("?") ? "&" + qs : "?" + qs;
      delete opt.body;
    }
  } else if (bodyData !== undefined) {
    opt.body = JSON.stringify(bodyData);
  }
  const r = await fetch("/api" + path, opt);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || ("HTTP " + r.status));
  return data;
}
function qs(o) { return Object.entries(o).filter(([, v]) => v !== "" && v != null && v !== 0 && v !== false).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join("&"); }
function params() { return new URLSearchParams(location.search); }
async function refreshSession() {
  const s = await api("/session");
  Object.assign(S, { user: s.user, zip: s.zip, gift: s.gift, coupon: s.coupon, cartCount: s.cartCount, cartSub: s.cartSubtotal, viewed: s.viewed });
}
let toastT;
function toast(html) {
  let t = $("#toast");
  if (!t) { t = document.createElement("div"); t.id = "toast"; t.className = "toast"; document.body.appendChild(t); }
  t.innerHTML = html; t.classList.add("show");
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 3200);
}

/* ============ chrome ============ */
function wordmark() {
  if (CFG.brand.logo) return `<span class="logo-custom">${CFG.brand.logo.startsWith("<svg") || CFG.brand.logo.startsWith("<img") ? esc(CFG.brand.logo).replace(/&lt;(\/?)(svg|img|path|circle|rect|text)/g, "<$1$2").replace(/&gt;/g, ">") : esc(CFG.brand.logo)}</span>`;
  return `<span class="wordmark">${esc(CFG.brand.wordmark || CFG.brand.name)}</span>`;
}
function renderHeader() {
  const u = S.user;
  const greet = u ? esc(u.name.split(" ")[0]) : "Welcome";
  $("#hdr").innerHTML = `
  <header>
    <div class="main-hdr">
      <a href="index.html" class="h-item logo" aria-label="${esc(CFG.brand.name)}">${wordmark()}</a>
      <button class="h-item deliver" id="zipBtn"><span class="pin">◈</span><span class="two-line"><em>${esc(T("deliverTo"))}</em><strong>${esc(S.zip)}</strong></span></button>
      <div class="h-search-wrap">
        <div class="h-search">
          <select id="searchDept" aria-label="Department"><option value="all">All</option>${CFG.departments.map(d => `<option value="${d.key}">${esc(d.label)}</option>`).join("")}</select>
          <input id="searchInput" type="text" placeholder="${esc(T("searchPlaceholder"))}" autocomplete="off">
          <button id="searchBtn" aria-label="Search">→</button>
        </div>
        <div id="suggest" class="suggest hidden"></div>
      </div>
      <div class="h-item h-menu-wrap" id="acctWrap">
        <button class="two-line" id="acctBtn"><em>${greet}</em><strong>${esc(T("accountLists"))} ▾</strong></button>
        <div class="h-menu hidden" id="acctMenu">
          <div class="hmenu-cols">
            <div><h4>Account</h4><a href="orders.html">${esc(T("yourOrders"))}</a><a href="cart.html">Your Bag</a>
              ${u ? `<a href="#" data-act="logout">Sign out</a>` : `<a href="#" data-act="signin-open"><span class="btn-yellow small">${esc(T("signIn"))}</span></a>`}</div>
            <div><h4>Services</h4>
              ${CFG.features.giftCards ? `<a href="gift-cards.html">Gift Balance · ${money(S.gift)}</a>` : ""}
              ${CFG.features.registry ? `<a href="registry.html">Registries</a>` : ""}
              ${CFG.features.customerService ? `<a href="customer-service.html">Client Care</a>` : ""}
              ${u && u.role === "admin" && CFG.features.adminPortal ? `<a href="console.html?scope=store" class="adm-link">⬡ Admin Console</a>` : ""}</div>
          </div>
          <p class="hmenu-foot">${u ? "Signed in as <b>" + esc(u.email) + "</b>" : "New here? <a href='#' data-act='signin-open'>Create an account.</a>"}</p>
        </div>
      </div>
      <a href="orders.html" class="h-item two-line"><em>Orders</em><strong>&amp; Returns</strong></a>
      <a href="cart.html" class="h-item cart-wrap"><span class="cart-ico">◇<b id="cartCount">${S.cartCount}</b></span><span class="cart-txt">Bag</span></a>
    </div>
    <nav class="subnav">
      <button class="sub-all" id="allBtn">≡ Menu</button>
      ${CFG.features.deals ? `<a href="deals.html">${esc(T("dealsTitle"))}</a>` : ""}
      ${CFG.features.customerService ? `<a href="customer-service.html">Client Care</a>` : ""}
      ${CFG.features.registry ? `<a href="registry.html">Registries</a>` : ""}
      ${CFG.features.giftCards ? `<a href="gift-cards.html">Gift Cards</a>` : ""}
      <a href="results.html?sort=new">New Season</a><a href="results.html?sort=best">Favourites</a>
      <span class="sub-spacer"></span>
      ${(CFG.gates || {})["storefront.currency_switch"] ? `<select id="curSwitch" class="cur-switch" title="View prices in your currency">${[CFG.commerce.currency, ...((CFG.geo.currencies || []).map(c => c.code).filter(x => x !== CFG.commerce.currency))].map(c => `<option value="${c}" ${c === (S.disp ? S.disp.code : CFG.commerce.currency)}>${c}</option>`).join("")}</select>` : ""}
      <span class="sub-mode">${esc(CFG.tenant ? CFG.tenant.mode : "")}</span>
    </nav>
  </header>`;
}
function renderFooter(stores) {
  $("#ftr").innerHTML = `
  <footer>
    <button class="back-top" id="backTop">${esc(T("backToTop"))}</button>
    <div class="f-main">
      <div class="f-brand">${wordmark()}<p>${esc(CFG.brand.tagline)}</p></div>
      <div class="f-cols">
        <div><h4>The House</h4><a href="#">About ${esc(CFG.brand.name)}</a><a href="#">Careers</a><a href="#">Journal</a></div>
        <div><h4>Shopping</h4>${CFG.features.deals ? `<a href="deals.html">${esc(T("dealsTitle"))}</a>` : ""}<a href="results.html?sort=new">New Season</a><a href="results.html?sort=best">Favourites</a><a href="results.html">All Departments</a></div>
        <div><h4>Services</h4>${CFG.features.giftCards ? `<a href="gift-cards.html">Gift Cards</a>` : ""}${CFG.features.registry ? `<a href="registry.html">Registries</a>` : ""}${CFG.features.customerService ? `<a href="customer-service.html">Client Care</a>` : ""}<a href="orders.html">Track an Order</a></div>
        <div><h4>Legal</h4><a href="#">Conditions</a><a href="#">Privacy</a><a href="#">Accessibility</a>${S.user && S.user.role === "admin" && CFG.features.adminPortal ? `<a href="console.html?scope=store">Admin Console</a>` : ""}</div>
      </div>
    </div>
    <div class="f-bottom">
      ${stores && stores.length > 1 ? `<div class="f-stores">Other stores on this platform: ${stores.map(x => `<a href="/index.html?store=${x.slug}">${esc(x.name)}</a>`).join(" · ")}</div>` : ""}
      ${(CFG.languages || []).length > 1 ? `<label class="f-lang"><span class="sr-only">Language</span><select id="langSel">${CFG.languages.map(l => `<option value="${esc(l.key)}" ${l.key === CFG.lang ? "selected" : ""}>${esc(l.native)}</option>`).join("")}</select></label>` : ""}
      <p class="f-copy">${esc(T("footerNote", { year: new Date().getFullYear(), brand: CFG.brand.name }))}</p>
      ${CFG.brand.poweredBy ? `<p class="f-powered"><a href="#">${esc(CFG.brand.poweredBy)}</a></p>` : ""}
    </div>
  </footer>`;
  /* the shopper's language choice is remembered for a year and the page re-renders in it */
  const ls = $("#langSel");
  if (ls) ls.addEventListener("change", () => { document.cookie = "azlang=" + encodeURIComponent(ls.value) + "; path=/; max-age=31536000; samesite=lax"; location.reload(); });
}
function renderSidebar() {
  $("#sidebar").innerHTML = `
  <div class="sb-overlay" id="sbOverlay"></div>
  <div class="sb" id="sbPanel">
    <div class="sb-hello">${wordmark()}</div>
    <div class="sb-head"><button class="sb-close" id="sbClose">✕</button><span>${S.user ? esc(S.user.name) : "Welcome"}</span>
      ${S.user ? `<button class="sb-acct" data-act="logout">Sign out</button>` : `<button class="btn-yellow w100" data-act="signin-open">${esc(T("signIn"))}</button>`}</div>
    <div class="sb-scroll">
      <section class="sb-sec"><h4>Departments</h4>${CFG.departments.map(d => `<a href="results.html?dept=${d.key}"><span class="sb-emoji">${d.icon}</span>${esc(d.label)}</a>`).join("")}</section>
      <section class="sb-sec"><h4>Discover</h4><a href="results.html?sort=best">✦ Favourites</a><a href="results.html?sort=new">✦ New Season</a>${CFG.features.deals ? `<a href="deals.html">✦ ${esc(T("dealsTitle"))}</a>` : ""}</section>
      <section class="sb-sec"><h4>Account</h4><a href="orders.html">📦 ${esc(T("yourOrders"))}</a><a href="cart.html">◇ Your Bag</a>${CFG.features.giftCards ? `<a href="gift-cards.html">🎁 Gift Balance</a>` : ""}${S.user && S.user.role === "admin" && CFG.features.adminPortal ? `<a href="console.html?scope=store">⬡ Admin Console</a>` : ""}</section>
    </div>
  </div>`;
}
function renderModals() {
  $("#modals").innerHTML = `
  <div class="overlay hidden" id="zipModal"><div class="modal"><div class="m-head"><h3>${esc(T("deliverTo"))}</h3><button data-close>✕</button></div>
    <div class="m-body"><p class="m-help">Enter a location for delivery estimates.</p><input id="zipInput" placeholder="ZIP / Postal code" maxlength="12" value="${esc(S.zip)}"><button class="btn-yellow w100" id="zipApply">Apply</button></div></div></div>
  <div class="overlay hidden" id="authModal"><div class="modal modal-wide"><div class="m-head"><div class="m-logo">${wordmark()}</div><button data-close>✕</button></div>
    <div class="m-body auth-body"><h2 id="authTitle">${S.user ? "You're signed in" : T("signIn")}</h2>
      ${S.user ? `<p class="m-help">Signed in as <b>${esc(S.user.name)}</b> (${esc(S.user.email)}).</p><button class="btn-white w100" data-act="logout">Sign out</button>` : `
      <form id="authForm" novalidate>
        <input id="authName" placeholder="Your name" class="hidden">
        <input id="authEmail" type="email" placeholder="Email" required>
        <input id="authPass" type="password" placeholder="Password" required minlength="6">
        <button class="btn-yellow w100" id="authSubmit">${esc(T("signIn"))}</button>
        <p class="m-help auth-forgot"><a href="reset.html">Forgot your password?</a></p>
        <div class="m-or"><span>or</span></div>
        <button type="button" class="btn-white w100" data-act="auth-toggle">Create an account</button>
      </form>`}</div></div></div>
  <div class="overlay hidden" id="reviewModal"><div class="modal"><div class="m-head"><h3>${esc(T("writeReview"))}</h3><button data-close>✕</button></div>
    <div class="m-body"><div class="m-prod" id="rvProd"></div>
      <div class="rv-star-pick" id="rvStars"><span data-r="1">★</span><span data-r="2">★</span><span data-r="3">★</span><span data-r="4">★</span><span data-r="5">★</span></div>
      <input id="rvTitle" placeholder="Review title" maxlength="80"><textarea id="rvBody" rows="4" placeholder="Share your experience…"></textarea>
      <button class="btn-orange w100" id="rvSubmit">Submit</button></div></div></div>
  <div class="overlay hidden" id="rfqModal"><div class="modal"><div class="m-head"><h3>Request for Quote</h3><button data-close>✕</button></div>
    <div class="m-body"><div class="m-prod" id="rfqProd"></div>
      <input id="rfqName" placeholder="Company / contact name"><input id="rfqEmail" type="email" placeholder="Work email">
      <input id="rfqQty" type="number" min="1" placeholder="Quantity"><input id="rfqPrice" type="number" step="0.01" placeholder="Target unit price (optional)">
      <button class="btn-orange w100" id="rfqSubmit">Submit RFQ</button></div></div></div>`;
}
function updateChrome() { renderHeader(); renderSidebar(); renderModals(); wireChrome(); }

/* ============ cards ============ */
/* a card is ADAPTIVE: its affordances are derived from the product's own type and
   universe fields (registry data), not from a fixed template. A digital good shows
   instant delivery, a subscription shows its cycle, a service shows booking — each
   shape comes from the record itself, so a new product type needs no new card code. */
function typeMeta(p) {
  const t = META && META.productTypes.find(x => x.key === p.type);
  const isSub = typeRow(p.type).purchase === "subscribe", isRental = typeRow(p.type).purchase === "rent";
  const isService = ["service", "appointment"].includes(p.type);
  const isDigital = ["digital", "license", "course"].includes(p.type);
  return { t, isSub, isRental, isService, isDigital, isPhygital: isSub || isRental || isService || isDigital };
}
function card(p) {
  const d = discount(p);
  const tm = typeMeta(p);
  return `<div class="pcard ${tm.isPhygital ? "pcard-domain" : ""}" data-id="${p.id}">
    <a class="pc-imgwrap" href="${prodLink(p)}">${img(p, "big")}${d ? `<span class="pc-deal">−${d}%</span>` : ""}${p.fl.includes("ac") ? `<span class="pc-choice">${esc(CFG.brand.name)} Pick</span>` : ""}</a>
    <div class="pc-body">
      ${!isPlain(p.type) ? `<span class="pc-type">${esc(typeIcon(p.type))}</span>` : ""}
      <a class="pc-title" href="${prodLink(p)}">${esc(p.t)}</a>
      <div class="pc-rate">${starsHtml(p.r)}<a class="pc-count">${p.c.toLocaleString(CFG.commerce.locale)}</a></div>
      <div class="pc-price">${priceHtml(p.p)}${tm.isSub ? '<span class="pc-cycle">/mo</span>' : tm.isRental ? '<span class="pc-cycle">/period</span>' : ""}${p.l > p.p ? `<span class="pc-list">${money(p.l)}</span>` : ""}</div>
      ${p.pricing_rules && p.pricing_rules.tiers ? `<div class="pc-tier">Volume pricing available</div>` : ""}
      <div class="pc-del">${tm.isDigital ? `<span class="pc-now">⚡ Instant access</span>` : tm.isService ? `<span class="pc-now">📅 Bookable</span>` : (p.pr ? `${prioBadge()} <b>${dShort(daysP())}</b>` : `<b>${dShort(daysS())}</b>`)}</div>
      ${stockText(p)}
      ${p.st ? `<button class="btn-yellow pc-btn" data-act="add" data-id="${p.id}">${esc(T("addToCart"))}</button>` : `<button class="btn-yellow pc-btn" disabled>${esc(T("outOfStock"))}</button>`}
    </div>
  </div>`;
}
function carousel(title, items) {
  if (!items || !items.length) return "";
  return `<section class="h-carousel"><h2>${esc(title)}</h2>
    <div class="hc-outer"><button class="hc-arrow" data-dir="-1">‹</button>
      <div class="hc-track">${items.map(p => `<a class="hc-item" href="${prodLink(p)}">${img(p, "big")}<div class="hc-name">${esc(p.t)}</div><div class="hc-rate">${starsHtml(p.r)}<b>${p.r}</b></div><div class="hc-price">${priceHtml(p.p)}</div>${p.pr ? `<div class="hc-prio">${prioBadge()}</div>` : ""}</a>`).join("")}</div>
      <button class="hc-arrow" data-dir="1">›</button></div></section>`;
}

/* ============ HOME ============ */
async function pageHome() {
  const main = $("#page");
  main.innerHTML = `<div class="loading">Composing…</div>`;
  const [res, tax] = await Promise.all([api("/products?limit=200"), api("/taxonomy")]);
  const all = res.items;
  const f = CFG.features;
  const deals = all.filter(isDeal).sort((a, b) => discount(b) - discount(a)).slice(0, 12);
  const best = all.filter(p => p.fl.includes("bs")).slice(0, 12);
  const rated = [...all].sort((a, b) => b.r - a.r).slice(0, 12);
  const fresh = all.filter(p => p.fl.includes("new")).slice(0, 12);
  const viewed = S.viewed.map(id => all.find(p => p.id === id)).filter(Boolean);
  const related = viewed.length ? all.filter(p => p.d === viewed[0].d && !S.viewed.includes(p.id)).slice(0, 12) : [];

  const banners = CFG.home.banners.map((b, i) => `
    <a class="banner ${i === 0 ? "banner-active" : ""}" href="results.html?dept=${esc(b.dept)}${f.deals ? "&deal=1" : ""}" style="--bh:${b.hue}">
      <div class="banner-text"><h2>${esc(b.title)}</h2><p>${esc(b.subtitle)}</p><span class="banner-cta">${esc(b.cta)} →</span></div></a>`).join("");

  const cards = CFG.home.cards.map(c => `<div class="h-card"><h3>${esc(c.title)}</h3>
    <div class="tiles">${c.tiles.map((tl, i) => { const ps = all.filter(x => x.d === c.dept); const p = ps[i % ps.length]; return p ? `<a href="${prodLink(p)}"><span>${esc(tl)}</span>${img(p, "tile")}</a>` : ""; }).join("")}</div>
    <a class="see-more" href="results.html?dept=${c.dept}">${esc(T("seeMore"))} →</a></div>`).join("");

  const root = ((tax.levels || []).find(l => l.root) || {}).key;
  const industries = tax.tree.filter(n => n.level === root).slice(0, 12);
  main.innerHTML = `
  <div class="hero-wrap"><div class="hero-banner">${banners}</div>
    <button class="banner-arrow" id="bPrev">‹</button><button class="banner-arrow" id="bNext">›</button></div>
  <div class="hero-cards">${cards}</div>
  ${industries.length ? `<nav class="cat-rail">${industries.map(n => `<a href="results.html?node=${n.id}"><span>${n.icon || "🏷️"}</span>${esc(n.name)}</a>`).join("")}</nav>` : ""}
  <section class="prio-strip"><span class="ps-badge">✦ ${esc(T("priorityBadge"))}</span> ${esc(T("priorityPerk"))}</section>
  ${related.length ? carousel(T("relatedTitle"), related) : ""}
  ${f.deals ? carousel(T("dealsTitle"), deals) : ""}
  ${carousel(T("bestSellers"), best)}
  <section class="signin-strip"><div><b>${S.user ? "Welcome back, " + esc(S.user.name.split(" ")[0]) : "The personal atelier"}</b>
    <div>${S.user ? "Your selections, saved across devices." : "Sign in for curated picks and faster checkout."}</div>
    <div class="si-btns">${S.user ? `<a class="btn-yellow" href="orders.html">${esc(T("yourOrders"))}</a>` : `<button class="btn-yellow" data-act="signin-open">${esc(T("signIn"))}</button><button class="btn-white" data-act="signin-open">Create account</button>`}</div></div></section>
  ${carousel(T("topRated"), rated)}
  ${carousel(T("newArrivals"), fresh.length ? fresh : best)}`;
  wireCarousels();
  let bi = 0; const bN = $$(".banner").length;
  const bGo = n => { $$(".banner").forEach((el, i) => el.classList.toggle("banner-active", i === n)); bi = n; };
  if (bN) { $("#bPrev").onclick = () => bGo((bi - 1 + bN) % bN); $("#bNext").onclick = () => bGo((bi + 1) % bN); setInterval(() => bGo((bi + 1) % bN), 5000); }
  
}

/* ============ RESULTS ============ */
async function pageResults() {
  const u = params();
  const q = u.get("q") || "", dept = u.get("dept") || "all", sort = u.get("sort") || "featured", node = u.get("node") || "", ptype = u.get("type") || "";
  const page = Math.max(1, Number(u.get("page") || 1));
  const rating = Number(u.get("rating") || 0);
  const brand = u.get("brand") || "";
  const pmin = Number(u.get("pmin") || 0), pmax = Number(u.get("pmax") || 0);
  const prio = u.get("prio") ? 1 : 0, deal = u.get("deal") ? 1 : 0;
  const main = $("#page");
  main.innerHTML = `<div class="loading">Searching…</div>`;
  const res = await api(`/products?${qs({ q, dept: dept === "all" ? "" : dept, sort, page, rating, pmin, pmax, prio, deal, node, type: ptype, brand })}`);
  document.title = (q ? `${q} — ` : "") + CFG.brand.name;
  const mk = over => "results.html?" + qs({ q, dept, sort, page, rating, pmin, pmax, prio, deal, node, type: ptype, brand, ...over });
  const chip = (label, url, on) => `<a class="${on ? "fchip on" : "fchip"}" href="${url}">${label}${on ? " ✕" : ""}</a>`;
  const buckets = [[0, 25], [25, 50], [50, 100], [100, 200], [200, 0]];
  const nodeInfo = node ? (await api("/taxonomy")).flat.find(n => String(n.id) === node) : null;
  /* the brand facet counts come from the search engine, which already indexes brand;
     unknown keys (a product whose brand is not yet a brands row) still count under
     their own key so the facet never hides matching products */
  const brandCounts = Object.entries(res.facets || {}).filter(([k]) => k.startsWith("brand:")).map(([k, v]) => [k.slice(6), v]).sort((a, b) => b[1] - a[1]);
  main.innerHTML = `
  <div class="r-top"><span>${nodeInfo ? "Category: <b>" + esc(nodeInfo.name) + "</b>" : "Department: <b>" + esc(deptLabel(dept) || "All") + "</b>"}</span>
    <div class="r-fchips">${q ? chip(`"${esc(q)}"`, mk({ q: "" }), false) : ""}${deal ? chip("Offers", mk({ deal: "" }), true) : ""}${prio ? chip(T("priorityBadge"), mk({ prio: "" }), true) : ""}${rating ? chip(rating + "★ & up", mk({ rating: "" }), true) : ""}${ptype ? chip(humanize(ptype), mk({ type: "" }), true) : ""}${brand ? chip(brandLabel(brand), mk({ brand: "" }), true) : ""}</div></div>
  <div class="r-toolbar"><span class="r-count">${res.total ? `${(res.page - 1) * res.per + 1}–${Math.min(res.page * res.per, res.total)} of ${res.total}` : "0"} results${q ? ` for "<i>${esc(q)}</i>"` : ""}</span>
    <select id="sortSel">${[["featured", "Featured"], ["price-asc", "Price · Low to High"], ["price-desc", "Price · High to Low"], ["rating", "Most Praised"], ["new", "Newest"], ["discount", "Biggest Offers"], ["best", "Best Sellers"]].map(([v, l]) => `<option value="${v}" ${sort === v ? "selected" : ""}>${l}</option>`).join("")}</select></div>
  <div class="r-cols">
    <aside class="r-side">
      <div class="r-sec"><h4>Department</h4><a class="${dept === "all" && !node ? "on" : ""}" href="${mk({ dept: "all", node: "" })}">All</a>
        ${Object.entries(res.deptCounts).sort((a, b) => b[1] - a[1]).map(([d, c]) => `<a class="${dept === d ? "on" : ""}" href="${mk({ dept: d, node: "" })}">${esc(deptLabel(d))} (${c})</a>`).join("")}</div>
      <div class="r-sec"><h4>Product Type</h4>${META.productTypes.slice(0, 10).map(t => `<a class="${ptype === t.key ? "on" : ""}" href="${mk({ type: ptype === t.key ? "" : t.key })}">${t.icon} ${esc(t.name)}</a>`).join("")}</div>
      ${brandCounts.length ? `<div class="r-sec"><h4>Brand</h4>${brandCounts.slice(0, 12).map(([b, c]) => `<a class="${brand === b ? "on" : ""}" href="${mk({ brand: brand === b ? "" : b, page: 1 })}">${esc(brandLabel(b))} (${c})</a>`).join("")}</div>` : ""}
      <div class="r-sec"><h4>Rating</h4>${[4, 3, 2].map(n => `<a href="${mk({ rating: rating === n ? "" : n })}" class="${rating === n ? "on" : ""}">${starsHtml(n)} ${n}★ & up</a>`).join("")}</div>
      <div class="r-sec"><h4>Price</h4>${buckets.map(([a, b]) => `<a class="${pmin === a && pmax === b ? "on" : ""}" href="${mk({ pmin: a, pmax: b || "" })}">${b ? `${money(a)} – ${money(b)}` : `${money(a)} & above`}</a>`).join("")}</div>
      <div class="r-sec"><h4>Offers</h4>${CFG.features.deals ? `<a class="${deal ? "on" : ""}" href="${mk({ deal: deal ? "" : 1 })}">The Edit · offers</a>` : ""}<a class="${prio ? "on" : ""}" href="${mk({ prio: prio ? "" : 1 })}">${prioBadge()}</a></div>
    </aside>
    <div class="r-main">${res.total ? `<div class="r-grid">${res.items.map(card).join("")}</div>` :
    `<div class="r-empty"><h3>No results for "${esc(q)}"</h3><p>Try a broader term.</p><div class="r-grid" id="fallbackGrid"></div></div>`}
      ${res.pages > 1 ? `<div class="r-pages">${res.page > 1 ? `<a class="pnav" href="${mk({ page: res.page - 1 })}">‹ Previous</a>` : `<span class="pnav disabled">‹ Previous</span>`}<span class="pcur">Page <b>${res.page}</b> of ${res.pages}</span>${res.page < res.pages ? `<a class="pnav" href="${mk({ page: res.page + 1 })}">Next ›</a>` : `<span class="pnav disabled">Next ›</span>`}</div>` : ""}</div>
  </div>`;
  $("#sortSel").onchange = e => { location.href = mk({ sort: e.target.value, page: 1 }); };
  const fb = $("#fallbackGrid");
  if (fb) fb.innerHTML = (await api("/products?sort=best&limit=4")).items.map(card).join("");
}

/* ============ PRODUCT ============ */
function verticalRows(p) {
  const v = p.vertical || {};
  const keys = Object.keys(v).filter(k => v[k] !== null && v[k] !== "" && v[k] !== false);
  if (!keys.length) return "";
  let fields = [];
  const nodeIndustry = p.node_id && META._nodes && META._nodes[p.node_id];
  const vk = nodeIndustry && META.industryVertical ? META.industryVertical[nodeIndustry] : null;
  return `<h3>Specifications</h3><table class="pp-vtable">${keys.map(k => {
    let val = v[k];
    if (typeof val === "object") val = Array.isArray(val) ? val.join(", ") : Object.entries(val).map(([a, b]) => `${humanize(a)}: ${b}`).join("; ");
    return `<tr><th>${esc(humanize(k))}</th><td>${esc(String(val))}</td></tr>`;
  }).join("")}</table>`;
}
async function pageProduct() {
  const id = params().get("id");
  const main = $("#page");
  main.innerHTML = `<div class="loading">Loading…</div>`;
  let data;
  try { data = await api(`/products/${encodeURIComponent(id)}`); }
  catch (e) { main.innerHTML = `<div class="r-empty"><h3>Piece not found</h3><a class="btn-yellow" href="index.html">Back to ${esc(CFG.brand.name)}</a></div>`; return; }
  const { product: p, histogram, reviews, questions, related, skus, relationships } = data;
  document.title = `${p.t.slice(0, 52)} — ${CFG.brand.name}`;
  api("/viewed", "POST", { id: p.id }).then(refreshSession).catch(() => { });
  window.__rv = p;
  const f = CFG.features;
  const subDisc = (CFG.retention && CFG.retention.subDiscount) || 10;
  const subFreq = ((CFG.retention && CFG.retention.subFrequencies) || [30])[0];
  const media = (p.media || []).length ? p.media : [{ kind: "image", label: "Front", emoji: p.e }];
  const mediaTile = (m, i) => m.url
    ? (mediaPlayer(m.kind) === "video"
        ? `<span class="pimg big pimg-url"><video src="${esc(m.url)}" alt="${esc(m.label || "")}" muted playsinline></video></span>`
        : `<span class="pimg big pimg-url"><img src="${esc(m.url)}" alt="${esc(m.label || "")}"></span>`)
    : `<span class="pimg big" style="background:hsl(${(p.h + i * 40) % 360} 30% 92%)">${esc(m.emoji || p.e)}</span>`;
  const thumbs = media.map((m, i) => `<a class="thumb ${i === 0 ? "on" : ""}" data-i="${i}" href="#">${mediaTile(m, i)}</a>`).join("");
  const tiers = (p.pricing_rules && p.pricing_rules.tiers) || [];
  const relGroups = {};
  (relationships || []).forEach(r => { (relGroups[r.type] = relGroups[r.type] || []).push(r.to); });
  const attrs = Object.entries(p.attrs || {}).filter(([, v]) => v !== "" && v != null);
  const identity = Object.entries(p.identity || {}).filter(([k, v]) => v && k !== "sku");
  const pm = typeRow(p.type).purchase;
  const isRental = pm === "rent", isSub = pm === "subscribe", isService = pm === "book", isDigital = pm === "download";
  const durations = isRental && p.vertical.durations ? p.vertical.durations : null;

  main.innerHTML = `
  <div class="pp">
    <div class="crumbs"><a href="index.html">Home</a> › <a href="results.html?dept=${p.d}">${esc(deptLabel(p.d))}</a> › <a href="results.html?dept=${p.d}&brand=${encodeURIComponent(p.b)}">${esc(brandLabel(p.b))}</a>${!isPlain(p.type) ? ` › <span>${esc(typeIcon(p.type))}</span>` : ""}</div>
    <div class="pp-grid">
      <div class="pp-gallery"><div class="pp-thumbs">${thumbs}</div><div class="pp-main" id="ppMain">${mediaTile(media[0], 0)}</div></div>
      <div class="pp-info">
        <h1>${esc(p.t)}</h1>
        <a class="pp-brand" href="results.html?brand=${encodeURIComponent(p.b)}">${esc(brandLabel(p.b))} · ${esc(deptLabel(p.d))}</a>
        <div class="pp-rate">${starsHtml(p.r)}<a class="pp-rcount">${p.c.toLocaleString(CFG.commerce.locale)} ratings</a>${p.fl.includes("bs") ? `<span class="pp-bestsell">House Favourite</span>` : ""}${p.fl.includes("new") ? `<span class="pp-new">New Season</span>` : ""}</div>
        <hr><div class="pp-price-row">${priceHtml(p.p)}${p.l > p.p ? `<span class="pp-off">−${discount(p)}%</span> <s class="pp-list">${money(p.l)}</s>` : ""}${isRental ? '<span class="pp-cycle">/ rental period</span>' : ""}${isSub ? '<span class="pp-cycle">/ month</span>' : ""}</div>
        ${tiers.length ? `<table class="pp-tiers"><tr><th>Qty</th><th>Unit Price</th></tr>${tiers.map(t => `<tr><td>${t.qty}+</td><td>${money(t.price)}</td></tr>`).join("")}</table><p class="pp-b2b">B2B volume pricing — <a href="#" data-act="rfq-open" data-id="${p.id}">submit an RFQ</a> for larger lots.</p>` : ""}
        <div class="pp-feat"><div>${esc(T("deliverEstimate"))} <b>${p.pr ? dLong(daysP()) : dLong(daysS())}</b> · ${esc(T("deliverTo"))} <a id="ppZip" href="#">${esc(S.zip)}</a></div>
          ${isDigital ? `<div>⚡ Instant digital delivery — license issued on payment</div>` : ""}
          ${isService ? `<div>📅 Appointment scheduling · ${esc(String(p.vertical.duration_min || 60))} min · ${esc(String(p.vertical.location_mode || "onsite"))}</div>` : ""}
          ${isRental ? `<div>🔑 Deposit ${money(p.vertical.deposit || 0)} · return inspection on drop-off</div>` : ""}</div>
        <h3>${esc(T("aboutItem"))}</h3>
        <ul class="pp-bullets">${(p.about || []).map(b => `<li>${esc(b)}</li>`).join("")}</ul>
        ${attrs.length ? `<h3>Attributes</h3><table class="pp-vtable">${attrs.map(([k, v]) => `<tr><th>${esc(humanize(k))}</th><td>${esc(String(v))}</td></tr>`).join("")}</table>` : ""}
        ${verticalRows(p)}
        ${identity.length ? `<h3>Identity & Compliance</h3><table class="pp-vtable">${identity.map(([k, v]) => `<tr><th>${esc(humanize(k))}</th><td>${esc(typeof v === "object" ? JSON.stringify(v) : String(v))}</td></tr>`).join("")}</table>` : ""}
        ${data.compliance && data.compliance.length ? `<h3>Certifications &amp; Compliance</h3><div class="pp-certs">${data.compliance.map(c => `<span class="pp-cert" title="${esc((c.issuer || "") + " · " + (c.jurisdiction || "") + (c.valid_to ? " · valid to " + c.valid_to : ""))}" style="display:inline-block;margin:0 6px 6px 0;padding:3px 9px;border:1px solid #cbb89a;border-radius:999px;font-size:12px;background:#faf6ee">${c.kind === "approval" ? "🧾" : c.kind === "mark" ? "🛡️" : c.kind === "registration" ? "🔖" : c.kind === "license" ? "🎫" : c.kind === "authorization" ? "📝" : "📜"} ${esc(c.code)}${c.status !== "valid" ? " · " + esc(c.status) : ""}</span>`).join("")}</div>` : ""}
        ${data.serialized ? `<p class="pp-serialized" style="font-size:13px;color:#646cff;margin:6px 0">🔢 Unit-serialized — <b>${data.serialized.total}</b> tracked item(s), ${data.serialized.by_status.in_stock || 0} in stock; warranty &amp; custody recorded per serial.</p>` : ""}
        ${data.supplier ? `<p class="pp-supplier" style="font-size:13px;color:#76777a;margin:6px 0">🚚 Backed by vetted supplier ${esc(data.supplier.supplier_name || "")}${data.supplier.lead_days ? " · typical lead " + esc(String(data.supplier.lead_days)) + "d" : ""}.</p>` : ""}
        ${p.packaging && p.packaging.length ? `<h3>Packaging</h3><table class="pp-vtable">${p.packaging.map(pk => `<tr><th>${esc(humanize(pk.level))}</th><td>${esc(pk.unit)} × ${pk.qty}</td></tr>`).join("")}</table>` : ""}
        ${p.logistics && p.logistics.shippingClass && !metaRow("shippingClasses", p.logistics.shippingClass).default ? `<p class="pp-ship-class">🚚 Shipping class: <b>${esc(humanize(p.logistics.shippingClass))}</b></p>` : ""}
        <a class="pp-report" href="#" data-act="soon">Report an issue with this piece</a>
      </div>
      <div class="buybox">
        <div class="bb-price" id="bbPrice">${priceHtml(p.p)}${isSub ? '<span class="bb-cycle">/mo</span>' : ""}</div>
        <div class="bb-del">${p.pr ? `${prioBadge()} <b>${dLong(daysP())}</b>` : `${esc(T("deliverEstimate"))} <b>${dLong(daysS())}</b>`}</div>
        <div class="bb-stock" id="bbStock">${stockText(p.st)}</div>
        ${(data.variant_groups || []).filter(g => g.options && g.options.length > 1).map(g => `<div class="bb-vg" style="margin:8px 0"><div style="font-size:12px;color:#565d64;margin-bottom:4px">${esc(g.name || g.axis)}${g.options.some(o => o.variant) ? '' : ''}</div><div style="display:flex;flex-wrap:wrap;gap:6px">${g.options.map(o => `<button class="bb-vg-opt" style="border:1px solid #d5d9d9;background:#fff;border-radius:8px;padding:6px 10px;font-size:13px;cursor:pointer" data-vggroup="${esc(g.name || g.axis)}" data-act="select-variant" data-sku="${o.id}" data-price="${o.price}" data-stock="${o.stock}" data-name="${esc(o.name || o.code)}">${esc(o.name || o.code)}</button>`).join("")}</div></div>`).join("")}
        ${p.st ? `
        ${durations ? `<label class="bb-dur">Rental period <select id="bbDur">${durations.map(d => `<option value="${d.price}">${esc(d.label)} — ${money(d.price)}</option>`).join("")}</select></label>` : ""}
        <div class="bb-qty"><label>Quantity <select id="bbQty">${Array.from({ length: Math.min(CFG.commerce.cartMaxQty, Math.max(1, p.st)) }, (_, i) => `<option>${i + 1}</option>`).join("")}</select></label></div>
        <button class="btn-yellow bb-btn" id="bbAdd" data-act="add" data-id="${p.id}" data-qty-src="bbQty">${esc(T("addToCart"))}</button>
        ${f.buyNow && !isRental ? `<button class="btn-orange bb-btn" id="bbBuy" data-act="buy-now" data-id="${p.id}">${esc(T("buyNow"))}</button>` : ""}
        ${f.subscribeSave ? `<div class="bb-sub"><button class="btn-white bb-btn" data-act="sub-save" data-id="${p.id}">🔁 Subscribe &amp; Save ${subDisc}%</button><div class="a-sub">Delivers every <b>${subFreq} days</b> · skip or pause anytime</div></div>` : ""}
        ${p.vertical && p.vertical.test_drive ? `<button class="btn-white bb-btn" data-act="rfq-open" data-id="${p.id}">🚗 Book a test drive</button>` : ""}
        <div class="bb-ship"><div><em>Ships from</em> ${esc(CFG.brand.name)} Atelier</div><div><em>Sold by</em> ${esc(p.b)}</div><div><em>Returns</em> 30-day, complimentary</div><div><em>Payment</em> 🔒 Secure</div></div>` : `<div class="oos">${esc(T("outOfStock"))}</div>`}
      </div>
    </div>
    ${relGroups.bundle || relGroups.cross_sell || relGroups.upsell ? `
    <section class="pp-fbt"><h3>${esc(T("fbtTitle"))}</h3><div class="fbt-row">
      <label><input type="checkbox" checked disabled> ${img(p, "fbt")}</label><span class="fbt-plus">+</span>
      ${(relGroups.bundle || relGroups.cross_sell || relGroups.upsell).slice(0, 2).map(x => `<label><input type="checkbox" checked> ${img({ ...x, e: x.emoji, h: x.hue }, "fbt")}</label><span class="fbt-plus">+</span>`).join("")}
      <div class="fbt-sum"><div><b>${esc(p.b)}</b> ${esc(p.t.slice(0, 40))}… <span>${priceHtml(p.p)}</span></div>
        <div class="fbt-total">Total: <b>${money(p.p + (relGroups.bundle || relGroups.cross_sell || relGroups.upsell).slice(0, 2).reduce((n, x) => n + x.price, 0))}</b>
          <button class="btn-yellow" data-act="add-all" data-ids="${[p.id, ...(relGroups.bundle || relGroups.cross_sell || relGroups.upsell).slice(0, 2).map(x => x.id)].join(",")}">${esc(T("addToCart"))}</button></div></div></div></section>` : ""}
    <div class="pp-cols">
      <div class="pp-specs"><h3>Reference</h3><table>
        <tr><th>Maison</th><td>${esc(p.b)}</td></tr><tr><th>Type</th><td>${esc(typeIcon(p.type) || "Physical Product")}</td></tr>
        <tr><th>SKU</th><td>${esc((p.identity || {}).sku || p.id)}</td></tr>
        ${data.localized ? `<tr><th>Language</th><td>${esc(data.locale)} · localized content</td></tr>` : ""}
        ${skus && skus.length > 1 ? `<tr><th>Variants</th><td>${skus.map(k => `${esc(k.name || k.code)} · ${money(k.price)} · ${k.stock} in stock`).join("<br>")}</td></tr>` : ""}
        <tr><th>Rating</th><td>${starsHtml(p.r)} ${p.r} / 5</td></tr></table></div>
      ${f.reviews ? `<div class="pp-rev-col" id="reviews"><div class="rev-head"><h3>${esc(T("reviewsTitle"))}</h3></div>
        <div class="rev-sum"><span class="rev-big">${p.r} / 5</span>${starsHtml(p.r)}<div class="rev-rc">${p.c.toLocaleString(CFG.commerce.locale)} global ratings</div></div>
        <div class="rev-hist">${[5, 4, 3, 2, 1].map(n => `<div class="rh-row"><span>${n}★</span><div class="rh-bar"><i style="width:${histogram[n]}%"></i></div><b>${histogram[n]}%</b></div>`).join("")}</div>
        <button class="btn-white w100" data-act="open-review">${esc(T("writeReview"))}</button>
        ${reviews.map(rv => `<div class="rev"><div class="rev-user">${esc(rv.name[0] || "A")} <b>${esc(rv.name)}</b></div>
          <div class="rev-rate">${starsHtml(rv.r)} <b>${rv.r}.0</b></div>
          <div class="rev-date">Reviewed ${new Date(String(rv.date).replace(" ", "T")).toLocaleDateString(CFG.commerce.locale, { month: "long", day: "numeric", year: "numeric" })}</div>
          ${rv.verified ? `<div class="rev-vp">✓ Verified Purchase</div>` : ""}
          <div class="rev-title">${esc(rv.title)}</div><p>${esc(rv.body)}</p>
          ${(rv.media || []).length ? `<div class="rev-media">${rv.media.map(m => `<span class="a-chip" title="${esc(m.label || "photo")}">${esc(m.emoji || "🖼")} ${esc(m.label || "photo")}</span>`).join("")}</div>` : ""}
          <div class="rev-foot"><a class="rev-help" href="#" data-act="ugc-vote" data-vote="/reviews/${rv.id}/vote" data-dir="up">👍 Helpful</a> ${(rv.helpful || 0) ? `<span class="rev-count">${rv.helpful} people found this helpful</span>` : ""}</div>
          ${(rv.replies || []).map(rp => `<div class="rev-reply"><b>${esc(rp.author)}</b> <span class="a-chip">${esc(rp.role)}</span><p>${esc(rp.body)}</p></div>`).join("")}</div>`).join("")}</div>` : ""}
      ${f.qna ? `<div class="pp-rev-col" id="qna"><div class="rev-head"><h3>${esc(T("qnaTitle"))}</h3></div>
        <div class="qna-ask"><input id="qnaInput" placeholder="Have a question about this item?" /><button class="btn-yellow" data-act="qna-ask">Ask</button></div>
        ${(questions || []).length ? questions.map(q => `<div class="rev"><div class="rev-user"><b>Q.</b> ${esc(q.name)}</div>
          <p class="qna-q">${esc(q.body)}</p>
          <div class="rev-foot"><a class="rev-help" href="#" data-act="ugc-vote" data-vote="/qna/${q.id}/vote?kind=question" data-dir="up">👍 Helpful</a> ${(q.votes_helpful || 0) ? `<span class="rev-count">${q.votes_helpful} found this useful</span>` : ""}</div>
          ${(q.answers || []).map(a => `<div class="rev-reply"><b>${esc(a.name)}</b> <span class="a-chip">${esc(a.role)}</span><p>${esc(a.body)}</p>
            <div class="rev-foot"><a class="rev-help" href="#" data-act="ugc-vote" data-vote="/qna/${a.id}/vote?kind=answer" data-dir="up">👍 Helpful</a> ${(a.votes_helpful || 0) ? `<span class="rev-count">${a.votes_helpful} found this useful</span>` : ""}</div></div>`).join("") || '<p class="a-sub">No answers yet — be the first to answer.</p>'}
          </div>`).join("") : '<p class="a-sub">No questions yet. Ask the first question above.</p>'}</div>` : ""}
    </div>
    ${relGroups.accessory || relGroups.compatible ? carousel("Accessories & Compatibility", relGroups.accessory || relGroups.compatible) : ""}
    ${related.length ? carousel(T("relatedTitle"), related.slice(0, 10)) : ""}
  </div>`;
  wireCarousels();
  const z = document.getElementById("ppZip");
  if (z) z.onclick = e => { e.preventDefault(); openModal("zipModal"); };
  $$(".pp-thumbs .thumb").forEach(t => t.onclick = e => {
    e.preventDefault();
    const main = document.getElementById("ppMain"); if (!main) return;
    main.innerHTML = ""; main.appendChild(t.querySelector(".pimg").cloneNode(true));
    $$(".pp-thumbs .thumb").forEach(x => x.classList.remove("on")); t.classList.add("on");
  });
}

/* ============ CART ============ */
async function pageCart() {
  const main = $("#page");
  main.innerHTML = `<div class="loading">Loading…</div>`;
  const c = await api("/cart");
  S.cartCount = c.count; S.cartSub = c.sub; $("#cartCount") && ($("#cartCount").textContent = c.count);
  document.title = `Your Bag — ${CFG.brand.name}`;
  const f = CFG.features;
  if (!c.items.length) {
    main.innerHTML = `<div class="cart-empty"><div class="ce-icon">◇</div><div class="ce-text"><h2>${esc(T("emptyCart", { brand: CFG.brand.name }))}</h2><p>${esc(T("emptyCartHint"))}</p>
      <div class="ce-btns">${f.deals ? `<a class="btn-yellow" href="deals.html">${esc(T("dealsTitle"))}</a>` : `<a class="btn-yellow" href="results.html">Browse</a>`}<button class="btn-white" data-act="signin-open">${esc(T("signIn"))}</button></div></div></div>
      ${carousel(T("bestSellers"), (await api("/products?sort=best&limit=12")).items)}`;
    wireCarousels(); return;
  }
  const row = ({ product: p, qty, unit }) => `
  <div class="ci"><a class="ci-img" href="${prodLink(p)}">${img(p, "big")}</a>
    <div class="ci-mid"><a class="ci-title" href="${prodLink(p)}">${esc(p.t)}</a>
      <div class="ci-stock">${stockText(p)}</div>
      <div class="ci-by"><span>${esc(p.b)}</span>${!isPlain(p.type) ? `<span class="pc-type">${esc(typeIcon(p.type))}</span>` : ""}${p.pr ? `<span>${prioBadge()}</span>` : ""}</div>
      <div class="ci-ship">${esc(T("deliverEstimate"))} <b>${p.pr ? dLong(daysP()) : dLong(daysS())}</b> · ${esc(T("deliverTo"))} ${esc(S.zip)}</div>
      <div class="ci-actions"><select class="ci-qty" data-id="${p.id}">${Array.from({ length: CFG.commerce.cartMaxQty }, (_, i) => `<option ${i + 1 === qty ? "selected" : ""}>${i + 1}</option>`).join("")}</select>
        <span class="sep">|</span><a href="#" data-act="cart-remove" data-id="${p.id}">Remove</a>
        ${f.saveForLater ? `<span class="sep">|</span><a href="#" data-act="save-later" data-id="${p.id}">Save for later</a>` : ""}</div>
      ${unit < p.p ? `<div class="ci-tier">Volume price applied: ${money(unit)} ea</div>` : ""}</div>
    <div class="ci-price">${priceHtml((unit * qty).toFixed(2))}</div></div>`;
  main.innerHTML = `
  <div class="cart-layout"><div class="cart-main">
    <div class="cart-card"><div class="cc-head"><h2>Your Bag</h2><span class="cc-price-h">Price</span></div>
      ${c.items.map(row).join("")}
      <div class="cc-foot">
        <div class="cc-sub">Subtotal (${c.count}): <b>${money(c.sub)}</b></div>
        ${c.discount ? `<div class="cc-promo">Promotions: −${money(c.discount)} <span>${c.promos.map(x => esc(x.name)).join(", ")}</span></div>` : ""}
        <div class="cc-del">${c.qualifies ? `<span class="qualify">✔ ${esc(T("freeShipQualify"))}</span>` : `<span class="noqualify">${esc(T("freeShipGap", { gap: money(CFG.commerce.freeShipThreshold - c.sub) }))}</span><div class="qual-bar"><i style="width:${Math.min(100, c.sub / CFG.commerce.freeShipThreshold * 100)}%"></i></div>`}</div>
        ${c.couponsOpen ? `<div class="cc-coupon"><input id="couponInput" class="cc-coupon-in" placeholder="${esc(T("couponPlaceholder"))}" value="${esc(S.coupon || "")}"><button class="btn-white" data-act="coupon">${esc(T("couponApply"))}</button>${c.promos.length ? `<span class="cc-promo">✓ ${c.promos.map(x => esc(x.name)).join(", ")}</span>` : ""}</div>` : ""}
        <div class="cc-proceed"><a class="btn-yellow" href="checkout.html">${esc(T("proceedCheckout"))} (${c.count})</a></div></div></div>
    ${f.saveForLater && c.saved.length ? `<div class="cart-card"><h2 class="sf-title">Saved for later</h2><div class="sf-grid">${c.saved.map(p => `<div class="sf-item"><a href="${prodLink(p)}">${img(p, "tile")}</a><div class="sf-txt"><a href="${prodLink(p)}">${esc(p.b)} ${esc(p.t.slice(0, 22))}…</a><span>${priceHtml(p.p)}</span></div><div class="sf-act"><button data-act="move-cart" data-id="${p.id}">Move to bag</button> <span>|</span> <a href="#" data-act="unsave" data-id="${p.id}">Remove</a></div></div>`).join("")}</div></div>` : ""}
  </div>
  <aside class="cart-side"><div class="side-sticky"><div class="cs-box">
    ${c.qualifies ? `<p class="ok">✔ ${esc(T("freeShipQualify"))}.</p>` : `<p>${esc(T("freeShipGap", { gap: money(CFG.commerce.freeShipThreshold - c.sub) }))}</p>`}
    <p class="cs-sub">Subtotal: <b>${money(c.sub)}</b></p>${c.discount ? `<p class="cs-promo">Promo: −${money(c.discount)}</p>` : ""}
    <a href="checkout.html" class="btn-yellow w100">${esc(T("proceedCheckout"))}</a>
    ${f.giftCards && S.gift > 0 ? `<p class="cs-gift">🎁 ${esc(T("giftBalanceLabel"))}: ${money(S.gift)}</p>` : ""}
  </div></div></aside></div>
  <div class="cart-recos">${carousel(T("relatedTitle"), (await api("/products?sort=best&limit=12")).items)}</div>`;
  wireCarousels();
  $$(".ci-qty").forEach(sel => sel.onchange = async () => { applyCart(await api("/cart", "PUT", { id: sel.dataset.id, qty: Number(sel.value) })); });
}

/* ============ CHECKOUT ============ */
async function pageCheckout() {
  const main = $("#page");
  const [c, prov] = await Promise.all([api("/cart"), api("/providers")]);
  if (!c.items.length) { location.href = "cart.html"; return; }
  document.title = `Checkout — ${CFG.brand.name}`;
  const cm = CFG.commerce;
  const gws = prov.gateways, carriers = prov.carriers;
  main.innerHTML = `
  <div class="co"><div class="co-grid"><div class="co-left">
    <div class="co-sec"><h3><span class="co-num">1</span> Shipping address</h3>
      <form id="shipForm" class="co-form"><input id="coName" placeholder="Full name" required value="${esc(S.user ? S.user.name : "")}">
        <input id="coAddr" placeholder="Address" required>
        <div class="co-row3"><input id="coCity" placeholder="City" required><input id="coState" placeholder="State"><input id="coZip" placeholder="ZIP" value="${esc(S.zip)}"></div>
        <input id="coPhone" placeholder="Phone (optional)"></form></div>
    <div class="co-sec"><h3><span class="co-num">2</span> Payment method</h3>
      ${gws.map((g, i) => `<div class="pay-opt"><label><input type="radio" name="pay" value="${g.id}" ${i === 0 ? "checked" : ""}> <b>${g.emoji} ${esc(g.name)}</b> <span class="pay-meta">${esc((g.methods || []).join(" · "))}${g.mode === "sandbox" ? " · test mode" : ""}</span></label></div>`).join("")}
      ${CFG.features.giftCards && S.gift > 0 ? `<p class="pay-gift">🎁 Gift balance ${money(S.gift)} applied automatically</p>` : ""}</div>
    ${f.fiscalSelection ? `<div class="co-sec" id="coCtx" hidden><h3><span class="co-num">＋</span> Fiscal &amp; billing contexts</h3><div id="ctxPicks"></div><p class="pay-meta">Chosen contexts are validated against the platform context entities.</p></div>` : ""}
    <div class="co-sec"><h3><span class="co-num">3</span> Review items and shipping</h3>
      ${c.items.map(({ product: p, qty, unit }) => `<div class="co-item">${img(p, "tile")}<div class="co-i-mid"><a href="${prodLink(p)}">${esc(p.t)}</a><span class="co-i-qty">Qty: ${qty}${unit < p.p ? " · volume price" : ""}</span></div><div class="co-i-price">${priceHtml(unit * qty)}</div></div>`).join("")}
      ${carriers.map((x, i) => `<div class="co-del"><label><input type="radio" name="ship" value="${x.id}" ${i === 0 ? "checked" : ""}> ${x.emoji} <b>${esc(x.name)}</b> · ${x.eta[0]}–${x.eta[1]} days · ${c.qualifies ? "Complimentary" : money(x.baseFee || cm.shipFee)}</label></div>`).join("")}
      <div id="coRates"></div></div>
  </div>
  <aside class="co-side"><div class="co-box">
    <p class="co-order">${esc(CFG.brand.name)} · Order Summary</p>
    <p><span>Items:</span><b>${money(c.sub)}</b></p>
    ${c.discount ? `<p class="os-promo"><span>Promotions:</span><b>−${money(c.discount)}</b></p>` : ""}
    <p><span>Shipping:</span><b id="osShip">${c.shipFee ? money(c.shipFee) : "Complimentary"}</b></p>
    ${CFG.features.giftCards && S.gift > 0 ? `<p><span>Gift balance:</span><b id="osGift">—</b></p>` : ""}
    <p><span>Tax (${esc(prov.tax.mode)}, ${(cm.taxRate * 100).toFixed(2)}%):</span><b id="osTax">${money(c.tax)}</b></p>
    <hr><p class="os-total"><span>Order total:</span><b id="osTotal">${priceHtml(c.total)}</b></p>
    <button id="placeOrder" class="btn-orange w100">${esc(T("placeOrder"))}</button>
    <p class="co-note">By placing your order you agree to ${esc(CFG.brand.name)}'s terms of sale.</p>
  </div></aside></div></div>`;
  /* the summary is priced by the server — the same code that charges the order — so a live
     carrier rate, a membership's free shipping or a per-line tax rule shows before paying */
  const addr = () => ({ name: $("#coName").value, address: $("#coAddr").value, city: $("#coCity").value, state: $("#coState").value, zip: $("#coZip").value });
  const pickedCarrier = () => (document.querySelector('input[name=ship]:checked') || {}).value || (carriers[0] || {}).id || "";
  let quote = null, rateId = null, qSeq = 0;
  const recalc = async () => {
    const seq = ++qSeq;
    try {
      const q = await api("/checkout/quote", "POST", { carrier: pickedCarrier(), rate_id: rateId, ...addr() });
      if (seq !== qSeq) return quote;
      quote = q; rateId = q.rate_id;
      $("#osShip").textContent = q.shipFee ? money(q.shipFee) : "Complimentary";
      $("#osTax").textContent = money(q.tax);
      const g = $("#osGift"); if (g) g.textContent = q.gift ? `-${money(q.gift)}` : money(0);
      $("#osTotal").innerHTML = priceHtml(q.total);
      $("#coRates").innerHTML = q.source === "live" && q.rates.length ? `<p class="pay-meta">Live carrier rates to your address${q.free ? " — shipping is on us" : ""}:</p>` + q.rates.map(r => `<div class="co-del"><label><input type="radio" name="rate" value="${esc(r.id)}" ${r.id === q.rate_id ? "checked" : ""}> <b>${esc(r.carrier)}</b> ${esc(r.service)}${r.days ? ` · ${r.days} days` : ""} · ${money(r.price)}</label></div>`).join("") : "";
      $$('input[name="rate"]').forEach(el => el.onchange = () => { rateId = el.value; recalc(); });
    } catch (e) { }
    return quote;
  };
  let addrTimer = null;
  ["#coAddr", "#coCity", "#coState", "#coZip"].forEach(id => $(id).addEventListener("input", () => { clearTimeout(addrTimer); rateId = null; addrTimer = setTimeout(recalc, 600); }));
  recalc();
  (async () => {
    try {
      if (!CFG.features.fiscalSelection) return;
      const ds = await Promise.all(c.items.slice(0, 6).map(i => api("/products/" + encodeURIComponent(i.product.id))));
      const inter = g => { let common = null; for (const x of ds) { const arr = (x.contexts[g] || []).map(o => o.key); if (!arr.length) continue; const set = new Set(arr); common = common === null ? set : new Set([...common].filter(k => set.has(k))); } return common ? [...common] : []; };
      /* the groups and their labels are the contextGroups registry's */
      const cgs = (META.contextGroups && META.contextGroups.length ? META.contextGroups : Object.keys(META.verticalContexts || {}).map(k => ({ key: k, name: k })));
      const groups = Object.fromEntries(cgs.map(g => [g.key, inter(g.key)]));
      const any = Object.values(groups).some(a => a.length);
      if (any) {
        $("#coCtx").hidden = false;
        $("#ctxPicks").innerHTML = cgs.map(x => x.key).map(g => groups[g].length ? `<label class="ctx-row"><span>${esc((cgs.find(x => x.key === g) || {}).name || g)}</span><select data-ctx="${g}"><option value="">— none —</option>${groups[g].map(k => `<option value="${k}">${esc(k.replace(/_/g, " "))}</option>`).join("")}</select></label>` : "").join("");
        recalc();
      }
    } catch (e) { }
  })();
  $$('input[name="ship"]').forEach(el => el.onchange = () => { rateId = null; recalc(); });
  $("#placeOrder").onclick = async () => {
    if (!$("#shipForm").reportValidity()) return;
    const btn = $("#placeOrder"); btn.disabled = true; btn.textContent = "Processing…";
    try {
      const r = await api("/checkout", "POST", {
        name: $("#coName").value, address: $("#coAddr").value, city: $("#coCity").value, state: $("#coState").value, zip: $("#coZip").value,
        gateway: (document.querySelector('input[name=pay]:checked') || {}).value || (gws[0] || {}).id,
        method: ((gws.find(g => g.id === (document.querySelector('input[name=pay]:checked') || {}).value) || {}).methods || ["card"])[0],
        carrier: pickedCarrier(), rate_id: rateId,
        contexts: Object.fromEntries($$("[data-ctx]").filter(x => x.value).map(x => [x.dataset.ctx, x.value]))
      });
      if (r.order.payment_redirect && /^https:\/\//.test(r.order.payment_redirect)) { location.href = r.order.payment_redirect; return; }
      await refreshSession(); renderHeader(); wireChrome();
      main.innerHTML = `
      <div class="oco"><div class="oco-card"><div class="oco-check">✓</div><div><h2>${esc(T("orderPlaced"))}, ${esc($("#coName").value.split(" ")[0])}!</h2>
        <p>Order #<b>${r.order.num}</b> · ${esc(r.order.gateway_name)} txn <b>${esc(r.order.txn_ref)}</b> (${esc(r.order.payment_status)})</p>
        <p class="oco-sub">Arriving <b>${dLong(r.order.eta)}</b> · Total <b>${money(r.order.total)}</b>${r.order.discount ? ` · saved ${money(r.order.discount)} with ${r.order.promos.map(x => esc(x.name)).join(", ")}` : ""}</p></div></div>
        <div class="oco-card oco-track"><h3>Dispatch</h3>
          <div class="track-steps"><span class="done">📦 Packed</span><i>—</i><span class="done">🚚 In transit</span><i>—</i><span>🏠 Out for delivery</span><i>—</i><span>✅ ${dShort(r.order.eta)}</span></div>
          <a class="btn-yellow" href="orders.html">${esc(T("yourOrders"))}</a><a class="btn-white" href="index.html">Continue</a></div></div>`;
    } catch (e) { btn.disabled = false; btn.textContent = T("placeOrder"); toast("⚠️ " + esc(e.message)); }
  };
}

/* ============ PASSWORD RESET ============ */
/* two steps on one page: without a token it asks for the email and sends the link; the
   emailed link carries the token, and the page then asks for the new password */
function pageReset() {
  const main = $("#page");
  const token = new URLSearchParams(location.search).get("token") || "";
  document.title = "Reset password — " + CFG.brand.name;
  main.innerHTML = `<div class="reset-wrap" style="max-width:420px;margin:40px auto;padding:0 16px">
    <h2>${token ? "Choose a new password" : "Forgot your password?"}</h2>
    <form id="resetForm" novalidate>
      ${token ? `<input id="rpPass" type="password" placeholder="New password" required autocomplete="new-password">
        <input id="rpPass2" type="password" placeholder="Repeat the new password" required autocomplete="new-password">`
      : `<p class="m-help">Enter the email you shop with and we'll send you a link to choose a new password.</p>
        <input id="rpEmail" type="email" placeholder="Email" required autocomplete="email">`}
      <button class="btn-yellow w100" id="rpSubmit">${token ? "Save new password" : "Send reset link"}</button>
    </form>
    <p class="m-help" id="rpMsg" role="status"></p></div>`;
  $("#resetForm").onsubmit = async e => {
    e.preventDefault();
    const btn = $("#rpSubmit"); btn.disabled = true;
    try {
      if (token) {
        if ($("#rpPass").value !== $("#rpPass2").value) throw new Error("The two passwords don't match");
        await api("/auth/password/reset", "POST", { token, password: $("#rpPass").value });
        history.replaceState(null, "", "reset.html");
        main.querySelector(".reset-wrap").innerHTML = `<h2>Password changed</h2><p class="m-help">Every device that was signed in has been signed out. Sign in with your new password.</p><button class="btn-yellow w100" data-act="signin-open">Sign in</button>`;
      } else {
        const r = await api("/auth/password/forgot", "POST", { email: $("#rpEmail").value.trim() });
        $("#rpMsg").textContent = r.message || "Check your email for the reset link.";
        btn.disabled = false;
      }
    } catch (err) { btn.disabled = false; $("#rpMsg").textContent = "⚠️ " + err.message; }
  };
}

/* ============ ORDERS ============ */
async function pageOrders() {
  const main = $("#page");
  main.innerHTML = `<div class="loading">Loading…</div>`;
  const [{ orders }, subs, mem] = await Promise.all([api("/orders"), CFG.features.subscribeSave ? api("/subscriptions") : Promise.resolve({ schedules: [] }), CFG.features.membership ? api("/membership") : Promise.resolve({ membership: null })]);
  document.title = `${T("yourOrders")} — ${CFG.brand.name}`;
  if (!orders.length && !(subs.schedules || []).length) { main.innerHTML = `<div class="ord-empty"><h2>${esc(T("yourOrders"))}</h2><p>No orders yet.</p><a class="btn-yellow" href="index.html">Start exploring</a></div>`; return; }
  main.innerHTML = `<h1 class="ord-h1">${esc(T("yourOrders"))}</h1>`;
  if (CFG.features.membership && mem.membership && Number((mem.membership.tier_detail || {}).price) > 0) {
    const m = mem.membership;
    main.innerHTML += `<div class="ord mem-card"><div class="mem-h"><span class="mem-badge">🎟️ ${esc(m.tier_detail.name)}</span><div><em>MEMBERSHIP</em><b>Active${m.renews_at ? " · renews " + String(m.renews_at).slice(0, 10) : ""}</b></div>
      <div class="ord-h-r"><span class="a-chip">${(m.tier_detail.benefits || []).join(" · ") || "member benefits"}</span><button class="btn-white" data-act="mem-cancel">Cancel membership</button></div></div></div>`;
  } else if (CFG.features.membership) {
    main.innerHTML += `<div class="ord mem-card"><div class="mem-h"><span class="mem-badge">🎟️ Join ${esc(CFG.brand.wordmark)}</span><div><em>MEMBERSHIP</em><b>Free shipping, early access &amp; bonus rewards</b></div>
      <div class="ord-h-r">${(mem.tiers || []).filter(t => t.price > 0).map(t => `<button class="btn-yellow" data-act="mem-subscribe" data-tier="${t.key}">Try ${esc(t.name)} · ${money(t.price)}/mo</button>`).join("")}</div></div></div>`;
  }
  for (const s of (subs.schedules || [])) {
    main.innerHTML += `<div class="ord"><div class="ord-h"><div><em>NEXT DELIVERY</em><b>${String(s.next_ship_at).slice(0, 10)}</b></div>
      <div><em>EVERY</em><b>${s.frequency_days} days · save ${s.discount_pct}%</b></div><div><em>STATUS</em><b>${esc(s.status)}</b></div>
      <div class="ord-h-r"><em>SUBSCRIPTION #${s.id}</em>${(s.can || {}).skip ? `<button class="btn-white" data-act="sub-skip" data-id="${s.id}">Skip next</button>` : ""}${(s.can || {}).pause ? `<button class="btn-white" data-act="sub-pause" data-id="${s.id}">Pause</button>` : ""}${(s.can || {}).resume ? `<button class="btn-white" data-act="sub-resume" data-id="${s.id}">Resume</button>` : ""}
      ${(s.can || {}).cancel ? `<button class="btn-white" data-act="sub-cancel" data-id="${s.id}">Cancel</button>` : ""}</div></div>
      <div class="ord-body"><div class="ord-i">${img({ e: "📦", h: 210 }, "big")}<div class="ord-i-mid"><b>${esc(s.product_id)}</b><span>${s.cycles_completed} shipment(s) delivered</span></div><span class="ord-i-qty">Qty: ${s.qty}</span></div></div></div>`;
  }
  main.innerHTML += orders.map(o => {
    const items = o.items.filter(x => x.product);
    const created = new Date(String(o.created_at).replace(" ", "T"));
    /* the server sends how the order shows (its state machine's label, icon and tone) */
    const d = o.display || { label: o.status, icon: "", tone: "info" };
    const st = [((d.icon ? d.icon + " " : "") + d.label), d.tone || "info"];
    return `<div class="ord"><div class="ord-h">
      <div><em>PLACED</em><b>${created.toLocaleDateString(CFG.commerce.locale)}</b></div>
      <div><em>TOTAL</em><b>${money(o.total)}</b></div>
      <div><em>PAYMENT</em><b>${esc(o.payment ? o.payment.gateway : o.pay_method)} · ${esc(o.payment ? o.payment.status : "")}</b></div>
      <div class="ord-h-r"><em>ORDER #${esc(o.num)}</em><button class="btn-white" data-act="buy-again" data-num="${esc(o.num)}">Buy it again</button><button class="btn-white" data-act="return-open" data-num="${esc(o.num)}">Return</button></div></div>
      <div class="ord-body">${items.map(({ product: p, qty }) => `<div class="ord-i">${img(p, "big")}<div class="ord-i-mid"><a href="${prodLink(p)}">${esc(p.t)}</a><span>${esc(p.b)}</span></div><span class="ord-i-qty">Qty: ${qty}</span></div>`).join("")}
        <div class="ord-buy">${items.map(({ product: p }) => `<a href="${prodLink(p)}">${img(p, "tile")}</a>`).join("")}</div>
        <div class="ord-r"><div class="ord-status ${st[1]}">${st[0]} · ${dShort(o.eta_days || 5)}</div><a href="#" data-act="track">Track</a></div></div></div>`;
  }).join("");
}

/* ============ DEALS / GIFT / CS / REGISTRY ============ */
async function pageDeals() {
  if (!CFG.features.deals) { location.href = "index.html"; return; }
  const main = $("#page");
  main.innerHTML = `<div class="loading">Loading…</div>`;
  const all = (await api("/products?limit=200")).items;
  const deals = all.filter(isDeal).sort((a, b) => discount(b) - discount(a));
  document.title = `${T("dealsTitle")} — ${CFG.brand.name}`;
  main.innerHTML = `
  <div class="deals-hero"><h1>${esc(T("dealsTitle"))}</h1><p>Curated offers across every department, refreshed daily.</p></div>
  <div class="deal-tabs"><a class="dtab on" href="deals.html">All</a>${CFG.departments.slice(0, 6).map(d => `<a class="dtab" href="results.html?dept=${d.key}&deal=1">${esc(d.label)}</a>`).join("")}</div>
  ${carousel("Time-limited", deals.slice(0, 12))}<div id="goipStrip"></div><div class="deals-grid">${deals.map(card).join("")}</div>`;
  wireCarousels();
  goipStrip();
}
/* GOIP Ω∞ — the value exchanges available to THIS shopper, in THIS context, from the in-app
   distribution channel. Discovery is a capability call; seeing them is a tracked touchpoint. */
async function goipStrip() {
  const box = document.getElementById("goipStrip"); if (!box) return;
  try {
    const d = await api("/goip/feed/in_app");
    if (!d.items || !d.items.length) return;
    box.innerHTML = `<section class="carousel"><h2>Offers for you</h2>
      <div class="deals-grid" style="margin-top:8px">${d.items.slice(0, 8).map(i => `
        <div class="card" style="padding:14px">
          <b>${esc(i.title)}</b>
          <div class="muted" style="font-size:12px;margin:4px 0">${esc(i.summary || "")}</div>
          ${i.code ? `<button class="btn-white" data-goipcode="${esc(i.code)}">Use code ${esc(i.code)}</button>` : '<span class="badge">applied automatically</span>'}
        </div>`).join("")}</div></section>`;
    box.querySelectorAll("[data-goipcode]").forEach(b => b.onclick = async () => {
      const code = b.dataset.goipcode;
      try { await api("/goip/track", "POST", { kind: "click", code, channel: "commerce", distribution: "in_app" }); } catch (e) { }
      try { await api("/coupon", "POST", { code }); toast("Code " + code + " applied to your cart"); }
      catch (e) { toast(e.message); }
    });
    try { await api("/goip/track", "POST", { kind: "view", channel: "commerce", distribution: "in_app", context: { page: "deals", shown: d.items.length } }); } catch (e) { }
  } catch (e) { /* GOIP feed is additive — the page never depends on it */ }
}
async function pageGift() {
  if (!CFG.features.giftCards) { location.href = "index.html"; return; }
  const wallet = !!(CFG.gates || {})["checkout.wallet"];
  document.title = `Gift Cards — ${CFG.brand.name}`;
  $("#page").innerHTML = `
  <div class="gc"><div class="gc-hero"><div class="gc-copy"><h1>Gift of Choice</h1><p>${wallet ? "No expiration, no minimum — delivered instantly." : "Digital wallets are not offered by this store — gift options are available in-store."}</p>
    ${wallet ? `<div class="gc-amounts">${CFG.commerce.giftAmounts.map(a => `<button class="gamt" data-act="gift" data-amt="${a}">${money(a)}</button>`).join("")}</div>` : ""}</div>
    <div class="gc-card"><div class="gc-face"><b>${esc(CFG.brand.wordmark)}</b><span>gift card</span></div><div class="gc-face-btn">Choose an amount</div></div></div>
  ${wallet ? `<div class="gc-bal">${esc(T("giftBalanceLabel"))}: <b>${money(S.gift)}</b></div>` : ""}
  <div class="gc-grid">${["Birthday", "Graduation", "Wedding", "Holidays", "Thank You", "Housewarming"].map((t, i) => `<div class="gc-cat"><span>${["🎂", "🎓", "💍", "🎄", "🙏", "🏠"][i]}</span><h3>${t}</h3><a href="deals.html">Shop now</a></div>`).join("")}</div></div>`;
}
function pageCS() {
  document.title = `Client Care — ${CFG.brand.name}`;
  const reasonOptions = [["order", "My order"], ["delivery", "Delivery"], ["returns", "Returns & refunds"], ["payment", "Payment"], ["product", "Product question"], ["account", "Account"], ["other", "Something else"]];
  $("#page").innerHTML = `
  <div class="cs"><h1>Client Care</h1>
    <div class="cs-tabs">${["📦 Orders", "💳 Payments", "↩️ Returns", "🔐 Account", "🚚 Delivery", "🎁 Gift Cards", "⚙️ Settings"].map(t => `<button class="cs-tab" data-q="${t.split(" ")[1]}">${t}</button>`).join("")}</div>
    <div class="cs-need"><h2>How may we assist?</h2><div class="cs-search"><input id="csIn" placeholder="Describe your issue" class="cs-in"><button class="cs-go" id="csGo">→</button></div></div>
    <section class="cs-faq"><h2>Answers</h2>${[
    ["Where is my order?", `Open <a href='orders.html'>${T("yourOrders")}</a> and select "Track".`],
    ["How do returns work?", "Complimentary returns within 30 days — request one from any order."],
    [`What does ${T("priorityBadge")} include?`, T("priorityPerk")],
    ["How do I change my location?", `Click "${T("deliverTo")}" in the header.`],
    ["Can I pay with a gift balance?", `Yes — top up from <a href='gift-cards.html'>Gift Cards</a>; applied automatically at checkout.`]
  ].map(([q, a]) => `<details><summary>${q}</summary><div class="faq-a">${a}</div></details>`).join("")}</section>
    <section class="cs-cases"><h2>My Cases</h2>
      <form id="csNewCase" class="cs-form"><input id="csSubject" placeholder="Subject — e.g. Order not delivered" required>
        <select id="csReason">${reasonOptions.map(([k, l]) => `<option value="${k}">${l}</option>`).join("")}</select>
        <textarea id="csBody" placeholder="Tell us what happened…" required></textarea>
        <button class="btn-yellow" type="submit">Open a case</button></form>
      <div id="csList" class="cs-list"><div class="loading">Loading your cases…</div></div></section></div>`;
  function csFilter(q) { $$(".cs-faq details").forEach(d => { const hit = d.textContent.toLowerCase().includes(q); d.style.display = !q || hit ? "" : "none"; if (q && hit) d.open = true; }); }
  $$(".cs-tab").forEach(tb => tb.onclick = () => { $("#csIn").value = tb.dataset.q; csFilter(tb.dataset.q.toLowerCase()); });
  $("#csIn").oninput = e => csFilter(e.target.value.toLowerCase());
  $("#csGo").onclick = () => { const q = $("#csIn").value.toLowerCase(); csFilter(q); if (![...$$(".cs-faq details")].some(d => d.textContent.toLowerCase().includes(q))) { $("#csSubject").value = q; $("#csSubject").focus(); toast("No answer matched — open a case below and our team will help"); } };
  async function loadCases() {
    const r = await api("/support/tickets", "GET");
    $("#csList").innerHTML = (r.tickets || []).length ? r.tickets.map(t => `<div class="cs-case"><div class="cs-case-h"><b><code>${esc(t.ref)}</code></b> ${esc(t.subject)} <span class="a-chip">${esc(t.status)}</span> <span class="a-chip">${esc(t.priority)}</span></div>
      <div class="a-sub">Opened ${new Date(t.created_at.replace(" ", "T")).toLocaleDateString()}${t.assignee ? " · agent: " + esc(t.assignee) : ""}${t.csat ? " · your rating: " + t.csat + "★" : ""}</div></div>`).join("")
      : '<p class="a-sub">You have no open cases.</p>';
  }
  $("#csNewCase").onsubmit = async e => {
    e.preventDefault();
    const r = await api("/support/tickets", "POST", { subject: $("#csSubject").value.trim(), reason: $("#csReason").value, body: $("#csBody").value.trim() });
    if (r.ticket) { toast(`✓ Case ${r.ticket.ref} opened — we'll email ${esc(r.ticket.owner_email)}`); $("#csNewCase").reset(); loadCases(); }
  };
  loadCases();
}
function pageRegistry() {
  document.title = `Registries — ${CFG.brand.name}`;
  $("#page").innerHTML = `
  <div class="reg"><div class="reg-hero"><h1>Registries &amp; Wish Lists</h1><p>One elegant list for every occasion.</p><button class="btn-yellow" data-act="list">+ Create a Registry</button></div>
    <div class="reg-grid">${[["🎂", "Birthday", "The perfect gift, chosen by you."], ["👶", "Baby", "From cribs to carriers."], ["💍", "Wedding", "Begin the collection together."], ["🏡", "Home", "Everything for the new address."]].map(([e, t, s]) => `<div class="reg-card"><span>${e}</span><h3>${t}</h3><p>${s}</p><a href="#" data-act="list">Start</a></div>`).join("")}</div></div>`;
}

function applyCart(c) { S.cartCount = c.count; S.cartSub = c.sub; const b = $("#cartCount"); if (b) b.textContent = c.count; pageCart(); }
function wireCarousels() { $$(".hc-arrow").forEach(a => a.onclick = () => a.closest(".hc-outer").querySelector(".hc-track").scrollBy({ left: 520 * Number(a.dataset.dir), behavior: "smooth" })); }

/* ============ chrome wiring ============ */
let authMode = "login";
function wireChrome() {
  const input = $("#searchInput"), suggest = $("#suggest");
  if (!input) return;
  const go = () => { location.href = "results.html?" + qs({ q: input.value.trim(), dept: $("#searchDept").value === "all" ? "" : $("#searchDept").value }); };
  $("#searchBtn").onclick = go;
  input.onkeydown = e => { if (e.key === "Enter") go(); };
  let sT;
  if (CFG.features.suggestions) input.oninput = () => {
    clearTimeout(sT); const q = input.value.trim();
    if (q.length < 2) return suggest.classList.add("hidden");
    sT = setTimeout(async () => {
      try {
        const r = await api(`/products?${qs({ q, limit: 6 })}`);
        if (!r.items.length) return suggest.classList.add("hidden");
        suggest.innerHTML = r.items.map(p => `<a href="${prodLink(p)}"><span class="sg-img">${p.e}</span><span class="sg-t">${esc(p.t.slice(0, 46))}…</span><span class="sg-d">${esc(deptLabel(p.d))}</span></a>`).join("") + `<a class="sg-go" href="results.html?${qs({ q })}">→ Search for "<b>${esc(q)}</b>"</a>`;
        suggest.classList.remove("hidden");
      } catch (e) { }
    }, 250);
  };
  if (!window.__chromeOnce) {
    document.addEventListener("click", e => { if (e.target.closest(".back-top")) scrollTo({ top: 0, behavior: "smooth" }); });
    document.addEventListener("change", e => { if (e.target.id === "curSwitch") { localStorage.setItem("azcur", e.target.value); computeDisp(); initPage(); } });
    document.addEventListener("click", e => { if (!e.target.closest(".h-search-wrap")) $("#suggest").classList.add("hidden"); });
    document.addEventListener("click", e => { if (!e.target.closest("#acctWrap")) $("#acctMenu").classList.add("hidden"); });
    window.__chromeOnce = true;
  }
  const wrap = $("#acctWrap");
  wrap.onmouseenter = () => $("#acctMenu").classList.remove("hidden");
  wrap.onmouseleave = () => $("#acctMenu").classList.add("hidden");
  $("#allBtn").onclick = () => $("#sidebar").classList.add("open");
  $("#sbClose") && ($("#sbClose").onclick = () => $("#sidebar").classList.remove("open"));
  $("#sbOverlay") && ($("#sbOverlay").onclick = () => $("#sidebar").classList.remove("open"));
  $("#zipBtn").onclick = () => openModal("zipModal");
  document.addEventListener("click", e => { if (e.target.dataset.close !== undefined) closeModal(); if (e.target.classList.contains("overlay")) closeModal(); });
  $("#zipApply").onclick = async () => {
    const z = $("#zipInput").value.trim(); if (!z) return;
    await api("/zip", "POST", { zip: z }); S.zip = z; renderHeader(); wireChrome(); closeModal();
    toast("◈ Location updated"); await initPage();
  };
  const aF = $("#authForm");
  if (aF) aF.onsubmit = async e => {
    e.preventDefault();
    try {
      const payload = { email: $("#authEmail").value.trim(), password: $("#authPass").value };
      let r;
      if (authMode === "register") { payload.name = $("#authName").value.trim(); r = await api("/auth/register", "POST", payload); }
      else r = await api("/auth/login", "POST", payload);
      S.user = r.user; updateChrome(); closeModal();
      toast(`✦ Welcome, <b>${esc(r.user.name.split(" ")[0])}</b>`);
      await refreshSession(); await initPage();
    } catch (err) { toast("⚠️ " + linkify(err.message)); }
  };
  document.querySelectorAll("[data-act='auth-toggle']").forEach(b => b.onclick = () => {
    authMode = authMode === "login" ? "register" : "login";
    $("#authTitle").textContent = authMode === "login" ? T("signIn") : "Create account";
    $("#authSubmit").textContent = authMode === "login" ? T("signIn") : "Create account";
    $("#authName").classList.toggle("hidden", authMode === "login");
    b.textContent = authMode === "login" ? "Create an account" : "I already have an account";
  });
  $("#rvStars").querySelectorAll("span").forEach(s => s.onclick = () => {
    const v = Number(s.dataset.r); $("#rvStars").dataset.val = v;
    $$("#rvStars span").forEach((x, i) => x.classList.toggle("on", i < v));
  });
  $("#rvSubmit").onclick = async () => {
    const p = window.__rv; if (!p) return;
    try {
      await api("/reviews/" + encodeURIComponent(p.id), "POST", { rating: Number($("#rvStars").dataset.val || 5), title: $("#rvTitle").value.trim() || "Review", body: $("#rvBody").value.trim() || "Exceptional." });
      closeModal(); toast("✓ Review published"); pageProduct();
    } catch (e) { toast("⚠️ " + esc(e.message)); }
  };
  $("#rfqSubmit").onclick = async () => {
    const p = window.__rv;
    try {
      const r = await api("/rfqs", "POST", { product_id: p.id, buyer_name: $("#rfqName").value, buyer_email: $("#rfqEmail").value, qty: Number($("#rfqQty").value) || 1, target_price: Number($("#rfqPrice").value) || 0 });
      closeModal(); toast("📋 " + esc(r.ref) + " submitted — our B2B desk will reply within 24h");
    } catch (e) { toast("⚠️ " + esc(e.message)); }
  };
}
function openModal(id) { $("#" + id).classList.remove("hidden"); }
function closeModal() { $$(".overlay").forEach(o => o.classList.add("hidden")); }

/* ============ global actions ============ */
document.addEventListener("click", async e => {
  const el = e.target.closest("[data-act]");
  if (!el) return;
  const act = el.dataset.act, id = el.dataset.id;
  if (["add", "buy-now", "add-all", "logout", "signin-open", "save-later", "cart-remove", "move-cart", "unsave", "gift", "open-review", "buy-again", "list", "rfq-open", "return-open", "coupon", "select-variant", "ugc-vote", "qna-ask", "sub-save", "mem-subscribe", "mem-cancel", "sub-skip", "sub-pause", "sub-resume", "sub-cancel"].includes(act)) { e.preventDefault(); e.stopPropagation(); }
  try {
    switch (act) {
      case "select-variant": {
        const grp = el.dataset.vggroup;
        document.querySelectorAll(".bb-vg-opt").forEach(b => { if (b.dataset.vggroup === grp) { b.style.borderColor = "#d5d9d9"; b.style.fontWeight = ""; } });
        el.style.borderColor = "#c8a24a"; el.style.fontWeight = "700";
        const price = Number(el.dataset.price), stock = Number(el.dataset.stock);
        const bp = $("#bbPrice"); if (bp) bp.innerHTML = priceHtml(price);
        const bs = $("#bbStock"); if (bs) bs.textContent = stock > 0 ? `${stock} in stock` : "Out of stock";
        const add = $("#bbAdd"); if (add) add.dataset.sku = el.dataset.sku;
        const buy = $("#bbBuy"); if (buy) buy.dataset.sku = el.dataset.sku;
        break;
      }
      case "add": {
        const qtySrc = el.dataset.qtySrc ? $("#" + el.dataset.qtySrc) : null;
        const c = await api("/cart", "POST", { id, qty: qtySrc ? Number(qtySrc.value) : 1, sku_id: el.dataset.sku ? Number(el.dataset.sku) : undefined });
        S.cartCount = c.count; $("#cartCount").textContent = c.count;
        toast(`◇ Added to your bag <a href="cart.html">View →</a>`); break;
      }
      case "add-all": {
        for (const pid of el.dataset.ids.split(",")) await api("/cart", "POST", { id: pid, qty: 1 });
        await refreshSession(); $("#cartCount").textContent = S.cartCount;
        toast("◇ Added to your bag <a href='cart.html'>View →</a>"); break;
      }
      case "buy-now": { await api("/cart", "POST", { id, qty: 1, sku_id: el.dataset.sku ? Number(el.dataset.sku) : undefined }); await refreshSession(); location.href = "checkout.html"; return; }
      case "cart-remove": await api("/cart/" + encodeURIComponent(id), "DELETE"); applyCart(await api("/cart")); return;
      case "save-later": await api("/saved", "POST", { id }); applyCart(await api("/cart")); return;
      case "move-cart": await api(`/saved/${encodeURIComponent(id)}/move`, "POST"); applyCart(await api("/cart")); return;
      case "unsave": await api("/saved/" + encodeURIComponent(id), "DELETE"); applyCart(await api("/cart")); return;
      case "gift": {
        const amt = Number(el.dataset.amt);
        const r = await api("/giftcard", "POST", { amount: amt });
        S.gift = r.balance; pageGift(); toast("🎁 " + money(amt) + " added to your gift balance"); break;
      }
      case "coupon": {
        const cv = $("#couponInput");
        const code = cv ? cv.value.trim() : "";
        const cc = await api("/coupon", "POST", { code });
        S.coupon = code; applyCart(cc); if (code) toast(esc(T("couponApplied"))); break;
      }
      case "logout": { await api("/auth/logout", "POST"); S.user = null; updateChrome(); toast("Signed out"); await initPage(); break; }
      case "signin-open": openModal("authModal"); break;
      case "open-review": {
        const p = window.__rv; if (!p) return;
        $("#rvProd").innerHTML = `${img(p, "tile")} <b>${esc(p.b)} ${esc(p.t.slice(0, 40))}…</b>`;
        openModal("reviewModal"); break;
      }
      case "rfq-open": {
        const p = window.__rv || (await api(`/products/${id}`)).product;
        window.__rv = p;
        $("#rfqProd").innerHTML = `${img(p, "tile")} <b>${esc(p.b)} ${esc(p.t.slice(0, 40))}…</b>`;
        openModal("rfqModal"); break;
      }
      case "return-open": {
        const num = el.dataset.num;
        const reason = prompt("Reason for return?");
        if (reason) { const r = await api("/returns", "POST", { order_num: num, reason }); toast("↩️ " + esc(r.ref) + " created — label emailed"); }
        break;
      }
      case "buy-again": {
        const { orders } = await api("/orders");
        const o = orders.find(x => x.num === el.dataset.num);
        if (o) { for (const it of o.items) await api("/cart", "POST", { id: it.id, qty: it.qty }); await refreshSession(); toast("◇ Reordered into your bag <a href='cart.html'>View →</a>"); }
        break;
      }
      case "track": toast("📦 Your parcel is <b>out for delivery</b>"); break;
      case "list": toast("✦ Registry created"); break;
      case "soon": toast("✦ This experience is coming soon"); break;
      case "ugc-vote": {
        /* each vote button names its own endpoint (a review and a question are different records) */
        const dir = el.dataset.dir || "up";
        const v = await api(el.dataset.vote, "POST", { dir });
        if (v.changed !== false) { toast(dir === "up" ? "👍 Thanks for your feedback" : "Vote updated"); render(); }
        else toast("You already voted that way"); break;
      }
      case "qna-ask": {
        const p = window.__rv; if (!p) break;
        const input = $("#qnaInput"); const text = (input && input.value || "").trim();
        if (!text) { toast("⚠️ Type a question first"); break; }
        const r = await api(`/qna/${encodeURIComponent(p.id)}/question`, "POST", { body: text });
        if (r.ok) { toast(r.moderated ? "Question submitted — awaiting moderation" : "✓ Question posted"); render(); }
        break;
      }
      case "reload": location.reload(); break;
      case "sub-save": {
        const p = window.__rv;
        const r = await api("/subscriptions", "POST", { product_id: el.dataset.id || (p && p.id), qty: Number(($("#bbQty") || {}).value || 1) });
        if (r.schedule) toast(`🔁 Subscribed — next delivery ${String(r.schedule.next_ship_at).slice(0, 10)} (save ${r.discount_pct}%)`);
        break;
      }
      case "mem-subscribe": {
        const r = await api("/membership/subscribe", "POST", { tier: el.dataset.tier });
        if (r.membership) { toast(`🎟️ Welcome to ${esc(r.membership.tier_detail.name)} — benefits apply at checkout`); render(); }
        break;
      }
      case "mem-cancel": {
        const r = await api("/membership/cancel", "POST");
        if (r.membership) { toast("Membership cancelled — benefits end at renewal"); render(); }
        break;
      }
      case "sub-skip":
      case "sub-pause":
      case "sub-resume":
      case "sub-cancel": {
        const action = act.replace("sub-", "");
        const r = await api(`/subscriptions/${el.dataset.id}`, "PUT", { action });
        if (r.schedule) { toast(`Subscription ${action}d`); render(); }
        break;
      }
    }
  } catch (err) { toast("⚠️ " + linkify(err.message)); }
});

/* ============ boot ============ */
async function initPage() {
  const p = PAGE();
  try {
    /* each page of the storefront is its own entry: the page key the HTML declares picks it */
    const PAGES = { home: pageHome, results: pageResults, product: pageProduct, cart: pageCart, checkout: pageCheckout, orders: pageOrders,
      deals: pageDeals, gift: pageGift, cs: pageCS, registry: pageRegistry, reset: pageReset };
    if (PAGES[p]) await PAGES[p]();
  } catch (e) {
    console.error(e);
    $("#page").innerHTML = `<div class="r-empty"><h3>Something went wrong</h3><p>${esc(e.message)}</p><button class="btn-yellow" data-act="reload">Retry</button></div>`;
  }
}
(async function boot() {
  try {
    const [cfg, meta] = await Promise.all([api("/config"), api("/meta")]);
    CFG = cfg; META = meta;
    /* the page speaks the answer's language, in its writing direction */
    if (CFG.lang) document.documentElement.lang = CFG.lang;
    if (CFG.dir) document.documentElement.dir = CFG.dir;
    computeDisp();
    applyTheme();
    await refreshSession();
  } catch (e) { console.error("boot failed", e); return; }
  document.title = document.title.replace("LUXORA", CFG.brand.name);
  updateChrome();
  api("/stores").then(st => renderFooter(st.stores)).catch(() => renderFooter([]));
  await initPage();
})();

/* UCOS Ω∞ · the ONE console — one shell, two scopes, one identity.
   ---------------------------------------------------------------------------
   There were two apps: /admin.html (store console, public/js/admin.js) and
   /platform.html (platform console, public/js/platform.js). Two URLs, two
   logins, two navs — and access decided by which URL you happened to open,
   which was never the design's intent and is exactly what a role-based
   console should not do.

   This is the single entry point. It does not rewrite either bundle: both
   consoles are ~6.5k lines of working views, and they deliberately share
   twenty global names (shell, render, NAV, canSee, view…) because each was
   written to own a page alone. Instead the unified console LOADS EACH BUNDLE
   INSIDE ITS OWN FUNCTION SCOPE, so each keeps its own globals and its own
   nav, and this shell:

     1. boots against /api/auth/me — the unified identity (lib/authz.js) that
        answers "who is signed in, and what may they do, across both scopes";
     2. renders ONE nav: every grant the identity holds, grouped by scope —
        STORE sections under this tenant, PLATFORM sections under the
        platform — so what you see is what your roles grant, never the URL;
     3. dispatches a view to the bundle that owns it (store views to the store
        bundle, platform views to the platform bundle), mounting that bundle's
        render into the one #app;
     4. switches scope in place — no second sign-in, no second URL. The two
        authorities coexist on one client (lib/api.js no longer drops one on
        the other), and each stays scoped to its own surface because authz
        namespaces every grant.

   The scope is visible on every leaf because the two navs share thirty section
   KEYS ("orders", "settings", "dash"…): a merged flat list would have been
   ambiguous, so a leaf always shows which surface it belongs to. */
"use strict";

/* ---------- the two bundles, each isolated in its own scope ----------
   Each bundle is fetched as text and executed inside a closure that captures
   its top-level declarations, so admin.js's `render` and platform.js's
   `render` never collide. The bundle's own boot is suppressed here — this
   shell owns identity and mounting — by giving each factory a marker it reads
   before running its IIFE. */
/* the bundles the unified console drives (served wrapped by lib/bundle.js) */
const BUNDLES = { store: "/js/bundle/store.js", platform: "/js/bundle/platform.js" };
const LX = { store: null, platform: null };      /* each bundle's captured surface */
const SCOPE_LABEL = { store: "Store", platform: "Platform" };
let scope = null;                                /* the surface a view renders in */
let view = "dash";
const me = { store: null, platform: null, tenant: null, grants: {}, storeAllowed: [], platformAllowed: [], apps: { store: [], platform: [] } };

const $ = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => [...(r || document).querySelectorAll(s)];
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
let toastT;
function toast(msg) { const t = $("#pToast"); if (!t) return; t.textContent = msg; t.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 3000); }

/* the unified identity: one call, both scopes, every grant namespaced */
async function api(path, methodOrOpts, body) {
  const opts = typeof methodOrOpts === "string" ? { method: methodOrOpts } : (methodOrOpts || {});
  if (body) { opts.body = JSON.stringify(body); opts.headers = Object.assign({}, opts.headers, { "Content-Type": "application/json" }); }
  const csrf = (document.cookie.match(/azc=([^;]+)/) || [])[1] || "";
  opts.headers = Object.assign({ "x-csrf": csrf }, opts.headers || {});
  const r = await fetch(path, opts);
  const j = await r.json().catch(() => ({}));
  if (!r.ok && j && !j.error) j.error = (j.error || r.statusText);
  return j;
}

/* ---------- loading a bundle without letting its globals escape ----------
   The bundle is wrapped so its top-level `function`/`const` declarations
   become properties of a capture object instead of globals. Its own boot
   IIFE still runs — but it reads LX.booting, and when the unified console is
   in charge it returns before touching #app, leaving the bundle's views
   available for this shell to drive. */
async function loadBundle(which) {
  if (LX[which]) return LX[which];
  const cap = { views: {}, nav: null, canSee: null, render: null, shell: null, ready: false };
  /* run the bundle in a closure of its own so its twenty shared globals (NAV,
     render, shell, canSee, view…) stay inside it and never reach window. The
     bundle's boot sees LX_GUEST and returns without painting #app — this shell
     owns identity and mounting; the bundle contributes its views and its nav.
     The server serves the bundle already wrapped in that closure (/js/bundle/<which>.js,
     see lib/bundle.js), loaded as an ordinary same-origin script: compiling the fetched
     source with the Function constructor needed 'unsafe-eval', which the CSP rightly refuses, so a
     real browser could never open the unified console. */
  const factory = await new Promise((resolve, reject) => {
    const el = document.createElement("script");
    el.src = BUNDLES[which] + "?v=" + Date.now();
    el.onload = () => { const f = window.__lxBundle && window.__lxBundle[which]; if (f) { delete window.__lxBundle[which]; resolve(f); } else reject(new Error("bundle " + which + " did not register")); };
    el.onerror = () => reject(new Error("bundle " + which + " failed to load"));
    document.head.appendChild(el);
  });
  factory.call(cap, true);
  LX[which] = cap;
  return cap;
}

/* which bundle owns a view: the store nav's leaves are store-scoped, the
   platform nav's are platform-scoped. A leaf present in both navs resolves to
   the current scope, so the shared keys stay unambiguous in the UI. */
function bundleFor(v) {
  /* "dash" is both consoles' home, but only the store nav carries it as a leaf — the
     platform's dashboard is the implicit default its render falls back to. So dash
     follows the scope the operator is standing in, instead of always landing in the
     store bundle the leaf list would pick for it */
  if (v === "dash" && LX[scope]) return scope;
  const inStore = LX.store && LX.store.NAVFLAT && LX.store.NAVFLAT.some(n => n[0] === v);
  const inPlat = LX.platform && LX.platform.nav && JSON.stringify(LX.platform.nav).includes('"' + v + '"');
  if (scope === "store" && inStore) return "store";
  if (scope === "platform" && inPlat) return "platform";
  if (inStore && !inPlat) return "store";
  if (inPlat && !inStore) return "platform";
  return scope || "store";
}

/* ---------- the unified nav ----------
   One tree: the platform's canonical sections (12, each with groups) when the
   identity holds platform grants, and the store's functional groups when it
   holds store grants — each filtered to what THIS identity may see, each
   leaf labelled with its surface. Nothing renders that is not granted, and a
   leaf an identity lacks is absent from the nav for the same reason its API
   refuses: the same grant map drives both.

   The tree is rebuilt on every render, so what the operator did to it lives here:
   which folds they opened or closed (navFold), what they typed in the filter
   (navQuery) and how far the sidebar was scrolled (navScroll). A platform section
   starts closed unless it holds the current screen — 300 leaves open at once is a
   wall, not a menu; a store group starts open. Each home screen is pinned at the
   top of its scope, and an alias leaf (a: <key>, same screen as <key>) shows only
   when its twin is not granted, so no one meets one screen twice. */
const navFold = {};
let navQuery = "", navScroll = 0;
function navLeaf(s, k, l) {
  return `<button data-s="${s}" data-v="${esc(k)}" class="${scope === s && view === k ? "on" : ""}">${esc(l)}</button>`;
}
function navFoldOpen(id, holdsView, byDefault) {
  if (holdsView) delete navFold[id];
  return id in navFold ? navFold[id] : (holdsView || byDefault);
}
function navTree() {
  const parts = [`<div class="p-nav-find"><input type="search" id="navFind" placeholder="Find a screen…" aria-label="Find a screen" value="${esc(navQuery)}" autocomplete="off"></div>`];
  /* the platform surface: the platform bundle's canonical NAV (sections → groups → leaves) */
  if (me.platform && LX.platform && LX.platform.nav) {
    const plat = LX.platform;
    const may = k => me.platformAllowed.includes("*") || me.platformAllowed.includes(k);
    parts.push(`<div class="p-nav-scope"><small>PLATFORM</small></div>`);
    if (may("dash")) parts.push(`<div class="p-nav-pin">${navLeaf("platform", "dash", "◈ Command")}</div>`);
    for (const sec of plat.nav) {
      let holds = false;
      const groups = (sec.g || []).map(grp => {
        const items = (grp.l || []).filter(([k, , res]) => k !== "dash" && may(k) && !(res && res.a && may(res.a)));
        if (scope === "platform" && items.some(([k]) => k === view)) holds = true;
        return items.length
          ? `<div class="p-nav-grp"><small>${esc(grp.g)}</small>${items.map(([k, l]) => navLeaf("platform", k, l)).join("")}</div>`
          : "";
      }).join("");
      const id = "platform:" + sec.n;
      if (groups) parts.push(`<details class="p-nav-sec" data-fold="${esc(id)}"${navFoldOpen(id, holds, false) ? " open" : ""}><summary>${esc(sec.n)}</summary>${groups}</details>`);
    }
  }
  /* the store surface: the store bundle's grouped NAV, filtered by the store grants */
  if (me.store && LX.store && LX.store.nav) {
    const store = LX.store;
    parts.push(`<div class="p-nav-scope"><small>THIS STORE · ${esc(me.tenant ? me.tenant.slug : "")}</small></div>`);
    /* a leaf is granted through the section it maps to (promotions → offers, structure →
       tenancy, sso → settings) — the same NAVSEC rule the store bundle's canSee applies */
    const secOf = k => (store.NAVSEC && store.NAVSEC[k]) || k;
    for (const grp of store.nav) {
      const items = (grp.items || []).filter(([k]) => me.storeAllowed.includes("*") || me.storeAllowed.includes(secOf(k)) || k === "dash");
      if (!items.length) continue;
      /* the store's home stays pinned: its group never folds away */
      if (items.some(([k]) => k === "dash")) {
        parts.push(`<div class="p-nav-grp p-nav-pin"><small>${esc(grp.g)}</small>${items.map(([k, l]) => navLeaf("store", k, l)).join("")}</div>`);
        continue;
      }
      const id = "store:" + grp.g;
      const holds = scope === "store" && items.some(([k]) => k === view);
      parts.push(`<details class="p-nav-fold" data-fold="${esc(id)}"${navFoldOpen(id, holds, true) ? " open" : ""}><summary>${esc(grp.g)}</summary>${items.map(([k, l]) => navLeaf("store", k, l)).join("")}</details>`);
    }
  }
  return parts.join("");
}
/* the filter narrows the tree in place — every fold holding a match opens, every leaf
   and group without one hides — and clearing it puts the folds back as they were */
function navFilter() {
  const nav = $("#pSide .p-nav");
  if (!nav) return;
  const q = navQuery.trim().toLowerCase();
  /* a word has to start with what was typed ("ship" finds Shipping, not Relationships),
     and the group and section names count, so "finance" lists the whole Finance group */
  const re = q ? new RegExp("(^|[^\\p{L}\\p{N}])" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "iu") : null;
  const head = b => { const g = b.closest(".p-nav-grp"), d = b.closest("details[data-fold]"); return [g && g.querySelector("small"), d && d.querySelector("summary")].map(x => x ? x.textContent : "").join(" "); };
  nav.querySelectorAll("button[data-v]").forEach(b => { b.hidden = !!re && !re.test(b.textContent + " " + head(b)); });
  nav.querySelectorAll(".p-nav-grp").forEach(g => { g.hidden = !!q && !g.querySelector("button[data-v]:not([hidden])"); });
  nav.querySelectorAll("details[data-fold]").forEach(d => {
    const hit = !!d.querySelector("button[data-v]:not([hidden])");
    d.hidden = !!q && !hit;
    if (q) { if (!("was" in d.dataset)) d.dataset.was = d.open ? "1" : ""; d.open = hit; }
    else if ("was" in d.dataset) { d.open = !!d.dataset.was; delete d.dataset.was; }
  });
  let none = nav.querySelector(".p-nav-none");
  const empty = !!q && !nav.querySelector("button[data-v]:not([hidden])");
  if (empty && !none) { none = document.createElement("div"); none.className = "p-nav-none"; none.textContent = "No screen matches."; nav.appendChild(none); }
  if (none) none.hidden = !empty;
}

function shell(content) {
  const who = me.platform ? me.platform.email : (me.store ? me.store.email : "");
  const roleTag = scope === "platform"
    ? (me.platform && me.platform.role) || "owner"
    : (me.store && me.store.staff_role) || "owner";
  $("#app").innerHTML = `
  <div class="p-shell">
    <aside class="p-side" id="pSide">
      <div class="p-logo"><b>${esc((me.tenant && me.tenant.name) || "LUXORA")}</b>
        <small>${scope === "platform" ? "Platform Console" : "Store Console"} · ${esc(me.tenant ? me.tenant.slug : "platform")}</small>
        <button class="p-side-close" id="pSideClose" aria-label="Close navigation">✕</button></div>
      <nav class="p-nav">${navTree()}</nav>
      <div style="padding:12px 18px;border-top:1px solid rgba(255,255,255,.1);margin-top:12px">
        <a href="${me.tenant ? "/index.html?store=" + esc(me.tenant.slug) : "/index.html"}" target="_blank" style="color:var(--p-side-text)">↗ Open storefront</a>
      </div>
    </aside>
    <div class="p-scrim" id="pScrim"></div>
    <main class="p-main"><div class="p-top">
      <button class="p-hamburger" id="pBurger" aria-label="Open navigation">☰</button>
      <h1 id="vTitle">${titleFor(view)}</h1><span class="spacer"></span>
      ${me.store && me.platform ? `<button class="p-btn sm" id="scopeBtn" title="Switch scope">⇄ ${SCOPE_LABEL[scope === "store" ? "platform" : "store"]}</button>` : ""}
      <span class="p-chip">${scope === "platform" ? "platform" : esc((me.tenant && me.tenant.mode) || "store")}</span>
      <span class="p-user">${esc(who)}</span><span class="p-tag">${esc(roleTag)}</span>
      <button class="p-btn sm" id="logoutBtn">Sign out</button></div>
      <div id="vBody">${content}</div></main>
  </div>`;
  wireNav();
  const sb = $("#scopeBtn");
  if (sb) sb.onclick = () => { switchScope(); };
  $("#logoutBtn").onclick = signOut;
  wireDrawer();
}
/* a click on the one nav sets the scope AND the leaf — the button carries both — and
   dispatches through the shell, so the bundle's view follows the shell's authority */
function wireNav() {
  const side = $("#pSide");
  /* a pick also closes the phone drawer — this nav is rebuilt after the bundle's own
     drawer wiring ran, so its buttons would otherwise leave the drawer covering the page */
  $$("#pSide .p-nav button").forEach(b => b.onclick = () => {
    if (side) side.classList.remove("p-side-open");
    const scrim = $("#pScrim"); if (scrim) scrim.style.display = "none";
    scope = b.dataset.s; view = b.dataset.v; render();
  });
  /* a fold the operator opens or closes stays that way across renders — except while the
     filter is driving it, when the toggle is the filter's, not theirs */
  $$("#pSide details[data-fold]").forEach(d => d.addEventListener("toggle", () => { if (!navQuery.trim()) navFold[d.dataset.fold] = d.open; }));
  const find = $("#navFind");
  if (find) {
    find.oninput = () => { navQuery = find.value; navFilter(); };
    find.onkeydown = e => {
      if (e.key === "Escape") { find.value = navQuery = ""; navFilter(); }
      if (e.key === "Enter") { const hit = $("#pSide .p-nav button[data-v]:not([hidden])"); if (hit) { e.preventDefault(); find.value = navQuery = ""; hit.click(); } }
    };
  }
  if (navQuery) navFilter();
  /* the sidebar comes back where it was, and the current screen is in view */
  if (side) {
    side.scrollTop = navScroll;
    side.onscroll = () => { navScroll = side.scrollTop; };
    const on = side.querySelector(".p-nav button.on");
    if (on && !navQuery) { const r = on.getBoundingClientRect(), sr = side.getBoundingClientRect(); if (r.top < sr.top || r.bottom > sr.bottom) on.scrollIntoView({ block: "nearest" }); }
  }
}
/* the address bar names the scope and the screen, so a refresh or a shared link reopens it */
function syncUrl() {
  try {
    const q = new URLSearchParams(location.search);
    q.delete("token");
    if (scope) q.set("scope", scope); else q.delete("scope");
    if (view && view !== "dash") q.set("view", view); else q.delete("view");
    const next = location.pathname + (q.toString() ? "?" + q.toString() : "") + location.hash;
    if (next !== location.pathname + location.search + location.hash) history.replaceState(null, "", next);
  } catch (e) { }
}
/* configured apps come and go (composed, granted, revoked) without a reload: the identity
   is re-read after every render and, when the apps changed, the bundles' navs follow */
let appsSig = "";
function registerApps() {
  for (const w of ["store", "platform"]) if (LX[w] && LX[w].registerApps) LX[w].registerApps(me.apps[w] || []);
  appsSig = JSON.stringify(me.apps);
}
async function refreshApps() {
  const r = await api("/api/auth/me").catch(() => null);
  if (!r || !r.apps) return;
  me.storeAllowed = r.allowedSections || me.storeAllowed;
  me.platformAllowed = r.platformAllowed || me.platformAllowed;
  me.apps = r.apps;
  if (JSON.stringify(r.apps) === appsSig) return;
  await seedBundles();
  registerApps();
  const nav = $("#pSide .p-nav");
  if (nav) { nav.innerHTML = navTree(); wireNav(); }
}
function titleFor(v) {
  if (scope === "platform" && LX.platform) {
    const meta = LX.platform.NAVKEY && LX.platform.NAVKEY[v];
    if (meta) return meta.label.replace(/^\S+\s/, "");
  }
  if (scope === "store" && LX.store && LX.store.NAVFLAT) {
    const f = LX.store.NAVFLAT.find(n => n[0] === v);
    if (f) return f[1].replace(/^\S+\s/, "");
  }
  return v;
}
function wireDrawer() {
  const side = $("#pSide"), scrim = $("#pScrim"), burger = $("#pBurger"), close = $("#pSideClose");
  if (burger) burger.onclick = () => { if (side) side.classList.add("p-side-open"); if (scrim) scrim.style.display = "block"; };
  const shut = () => { if (side) side.classList.remove("p-side-open"); if (scrim) scrim.style.display = "none"; };
  if (close) close.onclick = shut;
  if (scrim) scrim.onclick = shut;
  $$("#pSide .p-nav button").forEach(b => b.addEventListener("click", shut));
}

/* ---------- rendering: dispatch a view to the bundle that owns it ----------
   Each bundle renders into #vBody through its OWN shell — which is exactly the
   console that view belongs to, with its own nav and its own wiring — and
   afterwards this shell re-injects the scope switcher and the unified chrome,
   so the two consoles' interiors are reused, not rewritten. */
async function render() {
  shell('<div class="p-empty">Loading…</div>');
  const body = $("#vBody");
  const which = bundleFor(view);
  const bundle = LX[which];
  try {
    if (!bundle || !bundle.ready) { body.innerHTML = `<div class="p-empty">⚠️ ${SCOPE_LABEL[which]} console unavailable</div>`; return; }
    bundle.setView(view);          /* the bundle's render() reads its own view global, not an argument */
    await bundle.render();
    view = bundle.getView();        /* a view may redirect within the bundle; follow it */
    afterBundleRender();
    syncUrl();
  } catch (e) { body.innerHTML = `<div class="p-empty">⚠️ ${esc(e.message)}</div>`; }
}
/* the bundle's render replaced #app with its own shell — its own nav, its own
   single-scope sign-out, and no switcher. The one console puts its chrome back:
   the unified nav (every grant grouped by scope), the ⇄ switcher, and the sign-out
   that ends BOTH sessions. The bundle's interior — #vBody and everything a view
   wired inside it — is untouched. */
/* a view re-renders ITSELF through the bundle's own render() (a form save, an import, a
   delete — over a hundred call sites), and that call paints the bundle's single-scope
   shell too, so the unified chrome would silently vanish mid-session. The bundle's render
   is wrapped at load time to re-apply this chrome once it settles, so a re-render from
   anywhere keeps the one console's nav and its ⇄ switcher */
window.__lxRechrome = function () { try { afterBundleRender(); } catch (e) { } refreshApps(); };
function afterBundleRender() {
  const top = $(".p-top");
  if (!top) return;
  const nav = $("#pSide .p-nav");
  if (nav) { nav.innerHTML = navTree(); wireNav(); }
  const chip = top.querySelector(".p-chip");
  if (chip) chip.textContent = SCOPE_LABEL[scope];   /* the chip marks the surface, not the tenant's mode */
  if (me.store && me.platform) {
    const old = document.getElementById("scopeBtn"); if (old) old.remove();
    const btn = document.createElement("button");
    btn.className = "p-btn sm"; btn.id = "scopeBtn"; btn.title = "Switch scope";
    btn.textContent = "⇄ " + SCOPE_LABEL[scope === "store" ? "platform" : "store"];
    btn.onclick = switchScope;
    top.insertBefore(btn, top.querySelector(".p-chip"));
  }
  const out = document.getElementById("logoutBtn");
  if (out) out.onclick = signOut;
}
/* one sign-out ends both authorities — the bundle's own button only ends its own
   scope and then leaves the console, which is wrong inside the one console */
function signOut() {
  api("/api/auth/logout", "POST").catch(() => { });
  if (me.platform) api("/api/platform/logout", "POST").catch(() => { });
  location.href = "/index.html";
}
function switchScope() {
  if (!me.store || !me.platform) return;
  scope = scope === "store" ? "platform" : "store";
  view = "dash";
  render();
}

/* ---------- the shell is the bundles' boot ----------
    Each bundle's own boot fills its identity (A.user / P.user), its allowed list
    (A.allowed / P.allowed — what canSee reads) and, for the store bundle, the tenant
    config TT. Under this shell those boots return early, so nothing was filled: canSee()
    would admit every leaf (an empty allowed list means "all" to it) and the store views
    would meet an undefined TT. The shell fills the same fields from the unified identity
    instead — one source of truth, one grant map — so a leaf the console nav hides is
    equally hidden inside the bundle's own interior. */
async function seedBundles() {
  if (LX.store && LX.store.A) {
    LX.store.A.user = me.store;
    LX.store.A.allowed = Array.isArray(me.storeAllowed) ? me.storeAllowed : null;
  }
  if (LX.platform && LX.platform.P) {
    LX.platform.P.user = me.platform;
    LX.platform.P.allowed = Array.isArray(me.platformAllowed) ? me.platformAllowed : ["*"];
  }
  if (LX.store && LX.store.setTT) {
    const cfg = await api("/api/config").catch(() => null);
    if (cfg) LX.store.setTT(cfg);
  }
}

/* ---------- boot ---------- */
async function boot() {
  const q = new URLSearchParams(location.search);
  /* the platform hands a store over with a single-use ?token= (Tenants → Manage); it is
     redeemed once, then dropped from the address bar */
  const token = q.get("token");
  if (token) {
    await api("/api/auth/token-exchange", "POST", { token }).catch(() => null);
    q.delete("token");
    try { history.replaceState(null, "", location.pathname + (q.toString() ? "?" + q.toString() : "") + location.hash); } catch (e) { }
  }
  const r = await api("/api/auth/me");
  if (!r || (!r.hasStore && !r.hasPlatform)) return loginForm(r);
  me.store = r.identity.store || null;
  me.platform = r.identity.platform || null;
  me.tenant = r.tenant || null;
  me.grants = r.grants || {};
  me.storeAllowed = r.allowedSections || [];
  me.platformAllowed = r.platformAllowed || [];
  me.apps = r.apps || { store: [], platform: [] };
  /* a link may name the scope and the screen (?scope=store&view=orders); the legacy
     /admin.html and /platform.html addresses redirect here with their scope */
  const want = q.get("scope");
  scope = want === "store" && me.store ? "store" : want === "platform" && me.platform ? "platform" : (token && me.store ? "store" : (me.platform ? "platform" : "store"));
  if (q.get("view") && /^[A-Za-z0-9_-]{1,64}$/.test(q.get("view"))) view = q.get("view");
  /* load whichever bundles this identity can actually use */
  if (me.platform) await loadBundle("platform");
  if (me.store) await loadBundle("store");
  if (!LX[scope]) scope = me.platform ? "platform" : "store";
  /* the store bundle's own boot created the shared #modal its forms open into; under this
     shell that boot is suppressed, so the shell provides it (else + New / Edit throw) */
  if (!document.getElementById("modal")) { const m = document.createElement("div"); m.id = "modal"; m.className = "hidden"; document.body.appendChild(m); }
  await seedBundles();
  registerApps();
  render();
}

/* one sign-in for both authorities: try the platform account first, then this
   store's staff — so an operator with one email on both surfaces is in once */
function loginForm(r) {
  const hint = r && r.tenant ? r.tenant.slug : "luxora";
  $("#app").innerHTML = `<div class="p-login"><div class="p-login-box"><h1>LUXORA</h1><p>Console</p>
    <form id="lf" class="p-form"><label><span>Email</span><input id="le" type="email" required></label>
    <label><span>Password</span><input id="lp" type="password" required></label>
    <button class="p-btn primary" style="width:100%">Sign in</button></form>
    <p class="p-err hidden" id="lfErr" style="color:var(--p-red);font-size:13px;margin:10px 0 0"></p>
    <p class="hint"><a href="/reset.html?store=${esc(hint)}">Forgot your password?</a></p>
    <p class="hint">One sign-in for both the platform and the store console.<br>
    Store: <code>admin@${esc(hint)}.shop</code> · Platform: <code>platform@luxora.shop</code><br>
    <a href="/index.html">← Storefront</a></p></div></div>`;
  $("#lf").onsubmit = async e => {
    e.preventDefault();
    const email = $("#le").value.trim(), pw = $("#lp").value;
    const box = $("#lfErr");
    try {
      const plat = await api("/api/platform/login", "POST", { email, password: pw });
      if (plat.ok) { boot(); return; }
      const store = await api("/api/auth/login", "POST", { email, password: pw });
      if (store.ok) { boot(); return; }
      /* both authorities refused: a lockout or rate limit is worth saying; otherwise the
         plain answer, since naming which console "owns" the email would leak accounts */
      const why = [store.error, plat.error].find(m => /too many|locked|retry|disabled/i.test(m || ""));
      box.textContent = "⚠️ " + (why || "Invalid email or password");
      box.classList.remove("hidden");
    } catch (err) { box.textContent = "⚠️ " + err.message; box.classList.remove("hidden"); }
  };
}

boot();

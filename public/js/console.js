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
const BUNDLES = { store: "/js/admin.js", platform: "/js/platform.js" };
const LX = { store: null, platform: null };      /* each bundle's captured surface */
const SCOPE_LABEL = { store: "Store", platform: "Platform" };
let scope = null;                                /* the surface a view renders in */
let view = "dash";
const me = { store: null, platform: null, tenant: null, grants: {}, storeAllowed: [], platformAllowed: [] };

const $ = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => [...(r || document).querySelectorAll(s)];
const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
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
  const src = await (await fetch(BUNDLES[which], { cache: "no-cache" })).text();
  const cap = { views: {}, nav: null, canSee: null, render: null, shell: null, ready: false };
  /* run the bundle in a closure of its own so its twenty shared globals (NAV,
     render, shell, canSee, view…) stay inside it and never reach window. The
     bundle's boot sees LX_GUEST and returns without painting #app — this shell
     owns identity and mounting; the bundle contributes its views and its nav */
  const factory = new Function("LX_GUEST", "\"use strict\";" + src +
    /* re-chrome hook: a render the bundle fires from inside a view (form save, import,
       delete…) repaints its own single-scope shell; once it settles, the one console's
       chrome is put back through window.__lxRechrome (a no-op when the bundle runs
       standalone, so platform.html/admin.html are unaffected) */
    "\n ;(function () { if (typeof render !== 'function') return; var _r = render; render = function () {" +
    "  var out = _r.apply(this, arguments);" +
    "  var done = function () { try { (window.__lxRechrome || function () { })(); } catch (e) { } };" +
    "  return out && typeof out.then === 'function' ? out.then(function (v) { done(); return v; }, function (e) { done(); throw e; }) : (done(), out);" +
    "}; })();" +
    "\n; this.nav = NAV; this.canSee = canSee; this.render = render; this.shell = shell;"
    + " this.NAVFLAT = NAVFLAT; this.NAVKEY = typeof NAVKEY === 'undefined' ? null : NAVKEY;"
    + " this.NAVSEC = typeof NAVSEC === 'undefined' ? null : NAVSEC;"
    /* the bundle's render reads its OWN `view` global (it takes no argument) and its own
       canSee reads A.allowed / P.allowed — both set by the boot this shell suppressed. So
       the shell needs handles to set them: setView drives a leaf into the bundle, and A/P
       are the state objects its boot would have filled. */
    + " this.A = typeof A === 'undefined' ? null : A; this.P = typeof P === 'undefined' ? null : P;"
    + " this.setView = v => { view = v; }; this.getView = () => view;"
    + " this.setTT = typeof TT === 'undefined' ? null : (v => { TT = v; });"
    + " this.ready = true;");
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
   refuses: the same grant map drives both. */
function navTree() {
  const parts = [];
  /* the platform surface: the platform bundle's canonical NAV (sections → groups → leaves) */
  if (me.platform && LX.platform && LX.platform.nav) {
    const plat = LX.platform;
    parts.push(`<div class="p-nav-scope"><small>PLATFORM</small></div>`);
    for (const sec of plat.nav) {
      const groups = (sec.g || []).map(grp => {
        const items = (grp.l || []).filter(([k]) => me.platformAllowed.includes("*") || me.platformAllowed.includes(k));
        return items.length
          ? `<div class="p-nav-grp"><small>${esc(grp.g)}</small>${items.map(([k, l]) =>
            `<button data-s="platform" data-v="${k}" class="${scope === "platform" && view === k ? "on" : ""}">${l}</button>`).join("")}</div>`
          : "";
      }).join("");
      if (groups) parts.push(`<details class="p-nav-sec" open><summary>${esc(sec.n)}</summary>${groups}</details>`);
    }
  }
  /* the store surface: the store bundle's grouped NAV, filtered by the store grants */
  if (me.store && LX.store && LX.store.nav) {
    const store = LX.store;
    parts.push(`<div class="p-nav-scope"><small>THIS STORE · ${esc(me.tenant ? me.tenant.slug : "")}</small></div>`);
    for (const grp of store.nav) {
      const items = (grp.items || []).filter(([k]) => me.storeAllowed.includes("*") || me.storeAllowed.includes(k) || k === "dash");
      if (items.length)
        parts.push(`<div class="p-nav-grp"><small>${esc(grp.g)}</small>${items.map(([k, l]) =>
          `<button data-s="store" data-v="${k}" class="${scope === "store" && view === k ? "on" : ""}">${l}</button>`).join("")}</div>`);
    }
  }
  return parts.join("");
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
        ${me.platform && me.tenant ? ` · <a href="/platform.html" style="color:var(--p-side-text)">Legacy platform ↗</a>` : ""}
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
  $$(".p-nav button").forEach(b => b.onclick = () => { scope = b.dataset.s; view = b.dataset.v; render(); });
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
  $$(".p-nav button").forEach(b => b.addEventListener("click", shut));
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
window.__lxRechrome = function () { try { afterBundleRender(); } catch (e) { } };
function afterBundleRender() {
  const top = $(".p-top");
  if (!top) return;
  const nav = $(".p-nav");
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
  const r = await api("/api/auth/me");
  if (!r || (!r.hasStore && !r.hasPlatform)) return loginForm(r);
  me.store = r.identity.store || null;
  me.platform = r.identity.platform || null;
  me.tenant = r.tenant || null;
  me.grants = r.grants || {};
  me.storeAllowed = r.allowedSections || [];
  me.platformAllowed = r.platformAllowed || [];
  scope = me.platform ? "platform" : "store";
  /* load whichever bundles this identity can actually use */
  if (me.platform) await loadBundle("platform");
  if (me.store) await loadBundle("store");
  if (!LX[scope]) scope = me.platform ? "platform" : "store";
  await seedBundles();
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
      box.textContent = "⚠️ " + (plat.error || store.error || "Invalid credentials");
      box.classList.remove("hidden");
    } catch (err) { box.textContent = "⚠️ " + err.message; box.classList.remove("hidden"); }
  };
}

boot();

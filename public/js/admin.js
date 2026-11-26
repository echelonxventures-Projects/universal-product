/* LUXORA Platform - Store Admin console (metadata-driven) */
"use strict";

const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
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
let TT = null;
/* what this platform's kind calls one of it — "Store", "Operator", "Company" */
const kindTitle = () => { const n = (TT && TT.tenant && TT.tenant.kind && TT.tenant.kind.noun) || "store"; return n.charAt(0).toUpperCase() + n.slice(1); };

function linkify(m) {
  return esc(m).replace(/\/(platform|admin)\.html(\?store=[A-Za-z0-9-]+)?/g, function (s) {
    return '<a href="' + s + '" style="text-decoration:underline">' + (s.indexOf("platform") >= 0 ? "Platform console" : "Store console") + " →</a>";
  });
}
function money(n) { const d = (TT && TT.commerce && TT.commerce.decimals != null) ? TT.commerce.decimals : 2; try { return new Intl.NumberFormat(TT.commerce.locale, { style: "currency", currency: TT.commerce.currency, minimumFractionDigits: d, maximumFractionDigits: d }).format(+n); } catch (e) { return ((TT && TT.commerce && TT.commerce.symbol) || "") + (+n).toFixed(d); } }
let toastT;
function toast(msg) {
  let t = $("#ptoast");
  if (!t) { t = document.createElement("div"); t.id = "ptoast"; t.className = "p-toast"; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add("show");
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 3000);
}
/* The nav is grouped by the job an operator came to do, in the order a working day
   meets them: sell, stock, market, serve, get paid, run the business, then the
   store's own setup and the reference shelf. Labels are unique, so no two leaves
   read alike. Keys are unchanged — NAVSEC and canSee() still key off the flat list
   (every key is also a grant section), and NAVFLAT drives title lookup. */
/* the menu is the database's (console_screens, lib/consoles.js), served with this script: its groups
   in order, and each screen's group, label, position and access section */
const NAV = LX_CONSOLE.groups.map(g => ({ g, items: [] }));
const NAVFLAT = NAV.flatMap(g => g.items);
/* a domain's screens register themselves (public/js/admin/<domain>.js): what renders, what wires
   it, and where it sits — its domain's group in the nav, its label, the grant section it needs.
   A group a domain names is created the first time, before the groups flagged `tail`. */
const SCREENS = {};
function screen(key, def) {
  SCREENS[key] = def;
  const d = LX_CONSOLE.screens[key];
  /* a screen the database does not list is not in the menu */
  if (!d) return;
  const g = NAV.find(x => x.g === d.group);
  if (g && !g.items.some(i => i[0] === key)) {
    const at = g.items.findIndex(i => i[2] > d.position);
    g.items.splice(at < 0 ? g.items.length : at, 0, [key, d.label, d.position]);
  }
  NAVFLAT.length = 0; NAV.flatMap(x => x.items).forEach(x => NAVFLAT.push(x));
}
const NAVSEC = LX_CONSOLE.sections;
/* a store section's fitness to the tenant (its industries, its mode) is the database's too; the grant
   surface (lib/authz.js) applies it, so the menu only ever receives what the store may open */
const navSection = k => NAVSEC[k] || k;
const canSee = k => { if (!A.allowed || A.allowed.includes("*")) return true; if (k === "dash") return true; return A.allowed.includes(navSection(k)); };
let view = "dash";
/* the state machines, as /api/meta serves them: the console asks what a status means */
let SM = null;
/* rows the AI and offer forms render from (set by their views) */
let AI_CAPS = [], OFFER_SCOPES = [];
/* each declared list's default row and the platform currency (lib/defaults.js, served by /api/meta) */
let DFLT = { lists: {} };
async function loadSM() { if (!SM) { try { const m = await api("/meta"); SM = m.stateMachines || {}; DFLT = m.defaults || DFLT; } catch (e) { SM = {}; } } return SM; }
const dfl = list => (DFLT.lists || {})[list] || "";
const smIs = (m, st, tag) => !!(SM && SM[m] && SM[m].states[st] && SM[m].states[st].tags.includes(tag));
const smFirst = (m, tag) => { const ss = (SM && SM[m] && SM[m].states) || {}; return Object.keys(ss).find(k => ss[k].tags.includes(tag)); };
const smTone = (m, st) => ((SM && SM[m] && SM[m].states[st]) || {}).tone || "processing";
const smAction = (m, a) => ((SM && SM[m] && SM[m].actions) || {})[a];
const smNext = (m, st) => ((SM && SM[m] && SM[m].moves) || []).filter(x => (x.from === st || x.from === "*") && !smIs(m, x.to, "failure"));
/* configured apps (composed capabilities, Data Studio entities) join the nav as their own
   leaves — "app_<key>", each its own grant — under one group the console fills from the
   identity's allowed apps. Re-registering replaces the group, so a revoked app leaves. */
function registerApps(apps) {
  const i = NAV.findIndex(g => g.apps);
  if (i >= 0) NAV.splice(i, 1);
  const list = (apps || []).filter(a => a && /^app_[A-Za-z0-9_-]+$/.test(a.section));
  if (list.length) NAV.splice(NAV.length - 1, 0, { g: "Configured apps", apps: true, items: list.map(a => [a.section, (a.icon || "🧩") + " " + a.label]) });
  NAVFLAT.length = 0;
  NAV.flatMap(g => g.items).forEach(x => NAVFLAT.push(x));
}

/* ---------- Commerce Ops — the parity layer, surfaced. Each view reads this
   store's own capability composition first: a domain whose capabilities are all
   off shows one line ("switch it on in Capabilities") instead of empty tables,
   because an inert engine has no records to show. No vendor name appears — the
   domain declares what it does, never whose it is. ---------- */
let coCap = null;
/* a panel naming the capability it IS: the escrow card asks whether escrow is on. That is
   identity, not a gate — the card exists only to operate that one capability — so it reads
   the capability by name; a feature another engine depends on goes through a binding point */
const hasCap = (gate, key) => !!gate && (gate.on || []).includes(key);
async function coCaps() {
  if (!coCap) coCap = (await api("/capabilities")).catalog;
  return coCap;
}
/* the gate a domain's view reads: the atoms that govern THIS section, derived from the
   capability catalog the platform serves (each atom declares the sections it lights).
   The nav's visibility derives from the same declaration through lib/authz.js, so a leaf
   and the view behind it can never disagree about whether the domain is on. */
async function coGate(section) {
  const all = await coCaps();
  const keys = all.filter(c => (c.sections || []).includes(section)).map(c => c.key);
  const have = k => { const c = all.find(x => x.key === k); return !!(c && c.on); };
  const on = keys.filter(have);
  return { on, off: keys.filter(k => !have(k)), any: on.length > 0 };
}
function coOff(dom, label, off) {
  return `<div class="p-panel"><div class="a-head"><h2>${esc(label)}</h2>
    <p class="a-sub">This store has not switched on the ${esc(dom)} capabilities — the engines are inert and hold no records. <button class="p-btn sm" data-act="co-cap">Open ⚙️ Capabilities</button> to compose one.</p></div></div>`;
}
function coBadge(v) { return v == null || v === "" ? '<span class="p-tag">—</span>' : `<span class="a-chip">${esc(v)}</span>`; }
function coChips(rows, f) { const by = {}; rows.forEach(r => { const k = f(r); by[k] = (by[k] || 0) + 1; }); return Object.entries(by).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join(" ") || "none"; }
function coTbl(head, rows, cols, empty) {
  return `<div class="a-tablewrap"><table class="a-table"><thead><tr>${head.map(h => `<th>${h}</th>`).join("")}</tr></thead>
    <tbody>${rows.slice(0, 25).map(r => `<tr>${cols(r).map(c => `<td>${c}</td>`).join("")}</tr>`).join("") || `<tr><td colspan="${head.length}">${empty}</td></tr>`}</tbody></table></div>`;
}




/* ---------- Pickup points, rich content, brand registry ----------
   Each screen renders what its engine answered: the kinds, modules and report kinds are
   registry rows, and every button is one of the state machine's verbs offered for the
   record's current state — no state, kind or module is named in this file. */
const verbButtons = (acts, rec, attr) => acts.filter(a => (rec.next || []).includes(a.to))
  .map(a => `<button class="btn-white sm" data-${attr}="${esc(a.verb)}" data-id="${rec.id}">${esc(a.verb.charAt(0).toUpperCase() + a.verb.slice(1))}</button>`).join(" ");
const stateChip = st => `<span class="a-chip" title="${esc(st && st.key)}">${esc((st && (st.icon ? st.icon + " " : "") + st.label) || "")}</span>`;
function pickupModal(p) {
  const d = window.__pk || {};
  const v = p || { active: 1 };
  const m = modal(`<div class="p-modal-head"><h3>${p ? "Edit" : "New"} pickup point</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <div class="row"><label><span>Code *</span><input id="pkCode" value="${esc(v.code || "")}" placeholder="e.g. station-locker"></label>
        <label><span>Kind</span><select id="pkKind">${(d.kinds || []).map(k => `<option value="${esc(k.key)}" ${k.key === v.kind ? "selected" : ""}>${esc(k.name)}</option>`).join("")}</select></label></div>
      <label><span>Name *</span><input id="pkName" value="${esc(v.name || "")}"></label>
      <label><span>Address *</span><input id="pkAddr" value="${esc(v.address || "")}"></label>
      <div class="row"><label><span>Town / city</span><input id="pkCity" value="${esc(v.city || "")}"></label><label><span>Region</span><input id="pkRegion" value="${esc(v.region || "")}"></label><label><span>Postcode</span><input id="pkPost" value="${esc(v.postcode || "")}"></label></div>
      <div class="row"><label><span>Capacity (0 = no limit)</span><input id="pkCap" type="number" min="0" value="${esc(v.capacity || 0)}"></label><label><span>Days to arrive (blank = store default)</span><input id="pkEta" type="number" min="0" value="${v.eta_days != null ? esc(v.eta_days) : ""}"></label></div>
      <div class="row"><label><span>Latitude</span><input id="pkLat" value="${esc(v.lat != null ? v.lat : "")}"></label><label><span>Longitude</span><input id="pkLng" value="${esc(v.lng != null ? v.lng : "")}"></label></div>
      <label><span>Opening hours</span><input id="pkHours" value="${esc(v.hours || "")}" placeholder="e.g. Mon–Sat 8–20"></label>
      <label><input id="pkActive" type="checkbox" ${v.active ? "checked" : ""}> Offered at checkout</label>
      <button class="p-btn primary" id="pkSave">Save</button></div>`);
  m.querySelector("[data-mclose]").onclick = () => { m.innerHTML = ""; };
  m.querySelector("#pkSave").onclick = async () => {
    const val = id => m.querySelector(id).value;
    try {
      await api("/admin/pickup/points", "POST", { id: p ? p.id : undefined, code: val("#pkCode"), kind: val("#pkKind"), name: val("#pkName"), address: val("#pkAddr"), city: val("#pkCity"), region: val("#pkRegion"),
        postcode: val("#pkPost"), capacity: val("#pkCap"), eta_days: val("#pkEta"), lat: val("#pkLat"), lng: val("#pkLng"), hours: val("#pkHours"), active: m.querySelector("#pkActive").checked });
      m.innerHTML = ""; toast("Pickup point saved"); render();
    } catch (e) { toast(e.message); }
  };
}

/* rich product content: a module's fields are declared on its contentModules row — the
   editor draws an input for each declared field by its type */
const RC_INPUT = { text: "input", image: "input", textarea: "textarea", list: "textarea", table: "textarea" };
const rcValue = v => Array.isArray(v) ? v.map(x => Array.isArray(x) ? x.join(" | ") : x).join("\n") : (v == null ? "" : String(v));
function rcModuleHtml(def, val, i) {
  return `<div class="a-card" data-rc-mod="${i}" data-kind="${esc(def.key)}" style="padding:10px;margin:8px 0"><div style="display:flex;justify-content:space-between"><b>${esc(def.name)}</b><button class="btn-white sm" data-rc-drop="${i}">Remove</button></div>
    ${(def.fields || []).map(f => { const tag = RC_INPUT[f.type] || "textarea"; const v = rcValue(val && val[f.key]);
      return `<label style="display:block;margin-top:6px"><span>${esc(f.label || f.key)}${f.required ? " *" : ""}</span>${tag === "input" ? `<input data-f="${esc(f.key)}" value="${esc(v)}" style="width:100%">` : `<textarea data-f="${esc(f.key)}" rows="3" style="width:100%">${esc(v)}</textarea>`}</label>`; }).join("")}</div>`;
}


/* ---------- the platform-type screens: options, bookings, offers, auctions, listings,
   messages, group buying, substitutions ----------
   Same rule as above: every button is one of the record's state-machine verbs the server
   offers; every kind, mode and policy is a registry row the server sends. */
const fieldVal = id => ($(id) || {}).value || "";
/* ---------- deliverables: every kind (licence keys, lab tests, courses) its own screen, named by
   its deliverableKinds row ---------- */
let deliverableKindsCache = null;
async function deliverableKindFor(section) {
  if (!deliverableKindsCache) deliverableKindsCache = (await api("/deliverable-kinds", {}).catch(() => ({ kinds: [] }))).kinds || [];
  return deliverableKindsCache.find(k => k.section === section) || null;
}
async function vDeliverables(section) {
  const kind = await deliverableKindFor(section);
  const gate = await coGate(section);
  if (!gate.any) return coOff(kind.name.toLowerCase() + "s", kind.screen, gate.off);
  const d = await api("/admin/deliverables/" + encodeURIComponent(kind.key), {}).catch(e => ({ error: e.message }));
  if (d.error) return `<div class="a-head"><h2>${esc(kind.screen)}</h2><p class="a-sub">${esc(d.error)}</p></div>`;
  const P = d.settings || {};
  const how = kind.pooled ? `handed over from the item's pool the moment it is ordered; staff are told when fewer than ${esc(P.low_stock)} are left`
    : kind.uploaded ? `awaited until staff upload it — late after ${esc(P.due_days)} day(s)` : `granted at once; the shopper counts the ${esc(P.steps_fact)} they finish`;
  const pool = kind.pooled ? `<div class="a-card"><h3>Pool</h3><div class="p-form"><div class="row"><label><span>Item id *</span><input id="dlProd"></label></div>
      <label><span>Codes — one per line</span><textarea id="dlCodes" rows="4"></textarea></label><button class="p-btn primary" id="dlStock">Add to pool</button></div>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>item</th><th>left</th><th>stocked</th></tr></thead><tbody>
    ${(d.pools || []).map(r => `<tr><td><code>${esc(r.product_id)}</code></td><td>${r.n < Number(P.low_stock) ? `<b>${r.n}</b>` : r.n}</td><td>${r.total}</td></tr>`).join("") || '<tr><td colspan="3">No pools yet.</td></tr>'}</tbody></table></div></div>` : "";
  return `<div class="a-head"><h2>${esc(kind.screen)}</h2><p class="a-sub">An item whose facts carry <code>${esc(P.fact)}</code> delivers a ${esc(kind.name.toLowerCase())}: ${how} — the <code>${esc(kind.atom)}</code> capability's params.</p></div>
  ${pool}<div class="a-card"><h3>Delivered and awaited</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>#</th><th>order</th><th>item</th><th>shopper</th><th>state</th><th>${kind.access ? "progress" : "what was delivered"}</th><th></th></tr></thead><tbody>
  ${(d.deliverables || []).map(x => `<tr><td>${x.id}</td><td>#${x.order_id}</td><td><code>${esc(x.product_id)}</code></td><td>${esc(x.owner)}</td><td>${stateChip(x.state)}${x.late ? ' <span class="a-chip">late</span>' : ""}</td>
    <td>${kind.access ? `${x.steps_done} of ${x.steps_total}` : x.value ? (/^https?:/.test(x.value) ? `<a href="${esc(x.value)}" target="_blank" rel="noopener">file</a>` : `<code>${esc(x.value)}</code>`) : ""}</td>
    <td>${!x.delivered && !kind.access ? `<input data-dl-value="${x.id}" placeholder="${kind.uploaded ? "link to the file" : "code"}" style="width:160px"> <button class="btn-white sm" data-dl-give="${x.id}">Deliver</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="7">None yet.</td></tr>'}</tbody></table></div></div>`;
}
function wireDeliverables(section) {
  const st = $("#dlStock");
  if (st) st.onclick = async () => { const k = await deliverableKindFor(section); postAndRender("/admin/deliverables/" + encodeURIComponent(k.key) + "/pool", { product_id: fieldVal("#dlProd"), codes: fieldVal("#dlCodes") }, "POST", "Pool stocked"); };
  $$("[data-dl-give]").forEach(b => b.onclick = () => postAndRender("/admin/deliverables/item/" + b.dataset.dlGive, { value: ($(`[data-dl-value="${b.dataset.dlGive}"]`) || {}).value }, "POST", "Delivered"));
}
/* ---------- health records (lib/health-records.js): what shoppers shared with the store ---------- */
let hrParty = "";
/* ---------- the Universal Wallet (lib/wallet.js): an owner's wallets, their statements and holds,
   staff moves with a reason, adjustments, reversals, and the ledger's own verification ---------- */
let walOwner = "", walOpen = "";
/* ---------- cases: price matches, prescriptions, credentials, enquiries, trade-ins — every kind a
   caseKinds row, its actions its state machine's ---------- */
/* every kind of case is its own feature with its own screen: the kind row names its section */
let caseKindsCache = null;
async function caseKindFor(section) {
  if (!caseKindsCache) caseKindsCache = (await api("/case-kinds", {}).catch(() => ({ kinds: [] }))).kinds || [];
  return caseKindsCache.find(k => k.section === section) || null;
}
async function vCases(section) {
  const kind = await caseKindFor(section);
  const gate = await coGate(section);
  if (!gate.any) return coOff(kind.name.toLowerCase(), kind.screen, gate.off);
  const d = await api("/admin/cases?kind=" + encodeURIComponent(kind.key), {}).catch(e => ({ error: e.message }));
  if (d.error) return `<div class="a-head"><h2>${esc(kind.screen)}</h2><p class="a-sub">${esc(d.error)}</p></div>`;
  const acts = c => (d.actions || []).filter(a => a.machine === (c.kind_row || {}).machine);
  const needsAmount = c => c.kind_row && c.kind_row.effect && c.kind_row.effect.amount;
  return `<div class="a-head"><h2>${esc(kind.screen)}</h2><p class="a-sub">${esc(kind.name)} — what is asked, and what approval does, are its <code>caseKinds</code> row.</p></div>
  ${[kind].map(k => `<div class="a-card"><h3>${esc(k.name)}</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>#</th><th>from</th><th>about</th><th>details</th><th>state</th><th>amount</th><th></th></tr></thead><tbody>
    ${d.cases.filter(c => c.kind === k.key).map(c => `<tr><td>${c.id}</td><td>${esc(c.owner)}</td><td><code>${esc(c.subject_id || "—")}</code></td>
      <td>${Object.entries(c.fields).map(([f, v]) => `<b>${esc(f)}</b>: ${/^https?:/.test(String(v)) ? `<a href="${esc(v)}" target="_blank" rel="noopener">link</a>` : esc(v)}`).join("<br>")}</td>
      <td>${stateChip(c.state)}${c.valid_until ? `<div class="a-sub">until ${esc(c.valid_until)}</div>` : ""}</td><td>${c.amount != null ? money(c.amount) : ""}</td>
      <td style="white-space:nowrap">${c.open ? `${needsAmount(c) ? `<input data-case-amount="${c.id}" type="number" step="0.01" placeholder="amount" style="width:90px">` : ""}
        <input data-case-reason="${c.id}" placeholder="reason" style="width:120px">
        ${acts(c).filter(a => (c.next || []).includes(a.to)).map(a => `<button class="btn-white sm" data-case-act="${c.id}" data-case-verb="${esc(a.verb)}">${esc(a.label || a.verb)}</button>`).join(" ")}` : ""}</td></tr>`).join("") || '<tr><td colspan="7">None yet.</td></tr>'}
  </tbody></table></div></div>`).join("")}`;
}
function wireCases() {
  $$("[data-case-act]").forEach(b => b.onclick = () => {
    const id = b.dataset.caseAct, amt = $(`[data-case-amount="${id}"]`), why = $(`[data-case-reason="${id}"]`);
    postAndRender("/admin/cases/" + id, { action: b.dataset.caseVerb, amount: amt ? Number(amt.value) : undefined, reason: why ? why.value : "" }, "POST", "Done");
  });
}
const postAndRender = async (path, body, method, msg) => { try { await api(path, method || "POST", body); toast(msg || "Saved"); render(); } catch (e) { toast(e.message); } };
/* verbs on rows that carry `next` (state keys), from a vocabulary of { verb, to } */
const verbRow = (acts, rec, path, extra) => (acts || []).filter(a => (rec.next || []).includes(a.to))
  .map(a => `<button class="btn-white sm" data-co-post="${esc(path)}" data-co-body='${esc(JSON.stringify(Object.assign({ action: a.verb }, extra || {})))}'>${esc(a.verb.replace(/_/g, " "))}</button>`).join(" ");
function wireCoPosts() {
  $$("[data-co-post]").forEach(b => b.onclick = () => {
    const body = JSON.parse(b.dataset.coBody || "{}");
    if (b.dataset.coAsk) { const v = prompt(b.dataset.coAsk); if (v == null) return; body[b.dataset.coField || "notes"] = v; }
    postAndRender(b.dataset.coPost, body, b.dataset.coMethod);
  });
}

/* product options, and every option kind that is its own feature (installation, assembly, extended
   warranties, customisation proofs, samples) — one screen per section its optionKinds rows name */
const OPTION_SECTION = "prodoptions";
async function optionSection(section) {
  const kinds = ((await api("/options/kinds", {}).catch(() => ({ kinds: [] }))).kinds || []).filter(k => k.section === section);
  return kinds.length ? kinds : null;
}
/* a follow-up's moves: its machine's actions into the states it may reach, each asking what its target declares */
const fuVerbs = (acts, f, path) => (acts || []).filter(a => a.machine === (f.kind_row || {}).machine && (f.next || []).includes(a.to))
  .map(a => `<button class="btn-white sm" data-co-post="${esc(path)}" data-co-body='${esc(JSON.stringify({ action: a.verb }))}'${a.asks ? ` data-co-ask="${esc(a.asks.label)}" data-co-field="${esc(a.asks.field)}"` : ""}>${esc(a.label || a.verb)}</button>`).join(" ");
async function vProdOptions(section) {
  section = section || OPTION_SECTION;
  const kinds = await optionSection(section) || [];
  const main = section === OPTION_SECTION;
  const title = main ? "🧩 Product Options" : (kinds[0] || {}).screen || section;
  const gate = await coGate(section);
  if (!gate.any) return coOff(title.replace(/^\S+\s/, "").toLowerCase(), title, gate.off);
  const d = await api("/admin/options?section=" + encodeURIComponent(section), {});
  const all = main ? d : null;
  const fu = kinds.some(k => k.follow_up) ? await api("/admin/options/follow-ups?section=" + encodeURIComponent(section), {}).catch(() => ({ followUps: [] })) : null;
  const fuCard = fu ? `<div class="a-card"><h3>To do</h3><p class="a-sub">What an order with ${esc(kinds.map(k => k.name.toLowerCase()).join(" or "))} leaves to be done — the moves are the <code>${esc([...new Set(kinds.map(k => k.machine))].join(", "))}</code> state machine's.</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>order</th><th>item</th><th>option</th><th>detail</th><th>when / until</th><th>state</th><th></th></tr></thead><tbody>
    ${(fu.followUps || []).map(f => `<tr><td>#${f.order_id}</td><td><code>${esc(f.product_id)}</code></td><td>${esc(f.group_code)} ${esc(f.value_code)}</td><td>${esc(f.detail)}${f.proof_url ? ` · <a href="${esc(f.proof_url)}" target="_blank" rel="noopener">proof</a>` : ""}${f.note ? ` · “${esc(f.note)}”` : ""}${f.rounds ? ` · ${f.rounds} round(s) of changes` : ""}</td>
      <td>${esc(f.scheduled_for || f.ends_at || "")}</td><td>${stateChip(f.state)}</td><td>${fuVerbs(fu.followUpActions, f, "/admin/options/follow-ups/" + f.id)}</td></tr>`).join("") || '<tr><td colspan="7">Nothing to do.</td></tr>'}</tbody></table></div></div>` : "";
  const byProduct = {}; (d.attached || []).forEach(a => { (byProduct[a.product_id] = byProduct[a.product_id] || { title: a.title, groups: [] }).groups.push(a.group_id); });
  const sub = main ? `Modifiers, add-ons and personal text, defined once and attached to any product. Group kinds are the <code>optionKinds</code> registry; the longest personal text is the <code>product_options</code> capability's param. Every group of every kind is attached here.`
    : `${esc(kinds.map(k => k.name).join("; "))} — offered as an option group on an item (attach it under 🧩 Product Options); its settings are the <code>${esc(kinds.map(k => k.atom).join(", "))}</code> capability's params.`;
  return `<div class="a-head"><h2>${esc(title)}</h2><p class="a-sub">${sub}</p></div>
  <div class="a-card"><h3>Option group</h3><div class="p-form">
    <div class="row"><label><span>Code *</span><input id="ogCode" placeholder="e.g. size"></label><label><span>Name *</span><input id="ogName"></label>
      <label><span>Kind</span><select id="ogKind">${(d.kinds || []).filter(k => k.section === section).map(k => `<option value="${esc(k.key)}">${esc(k.name)}</option>`).join("")}</select></label></div>
    <div class="row"><label><span>Must choose at least</span><input id="ogMin" type="number" min="0" value="0"></label><label><span>May choose up to</span><input id="ogMax" type="number" min="1" value="1"></label><label><span>Longest text</span><input id="ogLen" type="number" min="1"></label></div>
    <label><span>Values — one per line: code | name | price change${kinds.some(k => k.runs_months) ? " | months" : ""}</span><textarea id="ogVals" rows="4" placeholder="large | Large | 3.00"></textarea></label>
    <input type="hidden" id="ogId"><button class="p-btn primary" id="ogSave" data-og-section="${esc(section)}">Save group</button></div></div>
  <div class="a-card"><h3>Groups</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>code</th><th>name</th><th>kind</th><th>choose</th><th>values</th><th></th></tr></thead><tbody>
    ${(d.groups || []).map(g => `<tr><td><code>${esc(g.code)}</code></td><td>${esc(g.name)}</td><td>${esc(g.kind_row ? g.kind_row.name : g.kind)}</td><td>${g.min_select}–${g.max_select}</td>
      <td>${g.values.filter(v => v.active).map(v => `${esc(v.name)}${Number(v.price_delta) ? " (" + (v.price_delta > 0 ? "+" : "") + money(v.price_delta) + ")" : ""}${v.extra && v.extra.months ? " · " + v.extra.months + " months" : ""}`).join(", ") || "—"}</td>
      <td style="white-space:nowrap"><button class="btn-white sm" data-og-edit="${g.id}">Edit</button> <button class="btn-white sm" data-co-post="/admin/options/${g.id}" data-co-method="DELETE">Remove</button></td></tr>`).join("") || '<tr><td colspan="6">No option groups yet.</td></tr>'}</tbody></table></div></div>
  ${fuCard}
  ${all ? `<div class="a-card"><h3>Attach to a product</h3><p class="a-sub">Groups of every kind the store offers, including those run from their own screens.</p><div class="p-form"><div class="row"><label><span>Product id *</span><input id="oaProd"></label></div>
    <div id="oaGroups"></div>
    <button class="p-btn primary" id="oaSave">Attach (replaces the product's groups)</button></div>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>product</th><th>groups</th></tr></thead><tbody>${Object.entries(byProduct).map(([pid, x]) => `<tr><td>${esc(x.title || pid)} <code>${esc(pid)}</code></td><td>${x.groups.map(id => esc(String(id))).join(", ")}</td></tr>`).join("") || '<tr><td colspan="2">No product has options yet.</td></tr>'}</tbody></table></div></div>` : ""}`;
}
async function wireProdOptions() {
  const save = $("#ogSave"); if (!save) return;
  /* the attach card offers every group of every kind (the section screens each list their own) */
  const box = $("#oaGroups");
  if (box) box.innerHTML = ((await api("/admin/options", {}).catch(() => ({ groups: [] }))).groups || []).map(g => `<label style="display:inline-block;margin-right:12px"><input type="checkbox" data-oa="${g.id}"> ${esc(g.name)}</label>`).join("");
  window.__og = window.__og || null;
  save.onclick = () => postAndRender("/admin/options", { id: fieldVal("#ogId") || undefined, code: fieldVal("#ogCode"), name: fieldVal("#ogName"), kind: fieldVal("#ogKind"), min_select: fieldVal("#ogMin"), max_select: fieldVal("#ogMax"), max_length: fieldVal("#ogLen") || undefined,
    values: fieldVal("#ogVals").split(/\n/).map(l => l.split("|").map(x => x.trim())).filter(x => x[0]).map(([code, name, delta, months]) => ({ code, name: name || code, price_delta: Number(delta) || 0, ...(months ? { months: Number(months) } : {}) })) }, "POST", "Option group saved");
  $$("[data-og-edit]").forEach(b => b.onclick = async () => {
    const g = ((await api("/admin/options", {})).groups || []).find(x => String(x.id) === b.dataset.ogEdit); if (!g) return;
    $("#ogId").value = g.id; $("#ogCode").value = g.code; $("#ogName").value = g.name; $("#ogKind").value = g.kind; $("#ogMin").value = g.min_select; $("#ogMax").value = g.max_select; $("#ogLen").value = g.max_length || "";
    $("#ogVals").value = g.values.filter(v => v.active).map(v => [v.code, v.name, v.price_delta].join(" | ")).join("\n"); window.scrollTo(0, 0);
  });
  if ($("#oaSave")) $("#oaSave").onclick = () => postAndRender("/admin/options/products/" + encodeURIComponent(fieldVal("#oaProd").trim()), { groups: $$("[data-oa]").filter(c => c.checked).map(c => Number(c.dataset.oa)) }, "PUT", "Options attached");
  wireCoPosts();
}









function shell(content) {  $("#app").innerHTML = `
  <div class="p-shell">
    <aside class="p-side" id="pSide">
      <div class="p-logo"><b>${esc(TT.brand?.name || TT.brand?.wordmark || "Store")}</b><small>${esc(kindTitle())} Console · ${esc(TT.tenant.slug)}</small>
        <button class="p-side-close" id="pSideClose" aria-label="Close navigation">✕</button></div>
      <nav class="p-nav">${NAV.map(grp => {
        const items = grp.items.filter(([k]) => canSee(k));
        if (!items.length) return "";
        return `<div class="p-nav-grp"><small>${grp.g}</small>${items.map(([k, l]) => `<button data-v="${k}" class="${view === k ? "on" : ""}">${l}</button>`).join("")}</div>`;
      }).join("")}</nav>
      <div style="padding:16px 18px;border-top:1px solid rgba(255,255,255,.1);margin-top:12px">
        <a href="/index.html?store=${esc(TT.tenant.slug)}" target="_blank" style="color:var(--p-side-text)">↗ Open storefront</a>
      </div>
    </aside>
    <div class="p-scrim" id="pScrim"></div>
    <main class="p-main"><div class="p-top"><button class="p-hamburger" id="pBurger" aria-label="Open navigation">☰</button><h1 id="vTitle">${NAVFLAT.find(n => n[0] === view)[1].replace(/^\S+\s/, "")}</h1><span class="spacer"></span>
      <span class="p-chip">${esc(TT.tenant.mode)}</span><span class="p-user">${esc(A.user.name)}</span>
      <span data-lxlang></span><button class="p-btn sm" id="logoutBtn">Sign out</button></div>
      <div id="vBody">${content}</div></main>
  </div>`;
  $$(".p-nav button").forEach(b => b.onclick = () => { view = b.dataset.v; render(); });
  $("#logoutBtn").onclick = async () => { await api("/auth/logout", "POST"); location.href = "/index.html"; };
  wireDrawer();
}
/* the touch drawer: on tablet/phone the sidebar is off-canvas and opened by the hamburger.
   Mirrors the platform console's wiring so both consoles behave identically on a phone. */
function wireDrawer() {
  const side = $("#pSide"), scrim = $("#pScrim"), burger = $("#pBurger"), close = $("#pSideClose");
  if (burger) burger.onclick = () => { if (side) side.classList.add("p-side-open"); if (scrim) scrim.style.display = "block"; };
  const shut = () => { if (side) side.classList.remove("p-side-open"); if (scrim) scrim.style.display = "none"; };
  if (close) close.onclick = shut;
  if (scrim) scrim.onclick = shut;
  $$(".p-nav button").forEach(b => b.addEventListener("click", shut));
}

/* ---------- generic entity table/form ---------- */
/* Validation utilities */
function validateField(key, value, fieldDef) {
  const errors = [];
  // Required check
  if (fieldDef.required && (value === "" || value === null || value === undefined)) {
    errors.push(`${fieldDef.label} is required`);
    return errors;
  }
  // Skip if not required and empty
  if (!fieldDef.required && value === "") return errors;
  
  // Type-specific validation
  switch (fieldDef.type) {
    case "email":
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) errors.push(`${fieldDef.label} must be a valid email`);
      break;
    case "url":
      if (!/^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/.test(value)) errors.push(`${fieldDef.label} must be a valid URL`);
      break;
    case "number":
    case "money":
      if (value !== "" && isNaN(Number(value))) errors.push(`${fieldDef.label} must be a number`);
      if (fieldDef.min !== undefined && Number(value) < fieldDef.min) errors.push(`${fieldDef.label} must be >= ${fieldDef.min}`);
      if (fieldDef.max !== undefined && Number(value) > fieldDef.max) errors.push(`${fieldDef.label} must be <= ${fieldDef.max}`);
      break;
    case "text":
      if (fieldDef.minLength && value.length < fieldDef.minLength) errors.push(`${fieldDef.label} must be at least ${fieldDef.minLength} characters`);
      if (fieldDef.maxLength && value.length > fieldDef.maxLength) errors.push(`${fieldDef.label} must be at most ${fieldDef.maxLength} characters`);
      if (fieldDef.pattern && !new RegExp(fieldDef.pattern).test(value)) errors.push(`${fieldDef.label} has invalid format`);
      break;
    case "json":
      if (value && typeof value !== "object") errors.push(`${fieldDef.label} must be a valid JSON object/array`);
      break;
  }
  return errors;
}
function validateRow(row, def) {
  const errors = {};
  for (const f of def.fields) {
    const fieldErrors = validateField(f.key, row[f.key], f);
    if (fieldErrors.length > 0) errors[f.key] = fieldErrors;
  }
  return errors;
}
async function entityRows(key) { try { return (await api("/meta/entity/" + key)).rows; } catch (e) { return []; } }
async function refOptions(key, f) {
  const rows = await entityRows(key);
  return rows.map(r => {
    /* a field may declare which column of the referenced row it stores (`refValue`): products
       carry their brand as the DISPLAY NAME (the string the catalogue, search facets, order
       snapshots and CSV exports all read), so that field stores the label — the numeric row id
       would never match a real product and the form would render an empty required select and
       refuse every save. */
    const rv = f && f.refValue;
    if (rv && r[rv] != null) return { v: r[rv], l: r[rv] };
    /* a platform-level master keyed by CODE (country, currency, subdivision) has no numeric id
       — its option value is the code itself. Falling back to r.id here would drop the value
       entirely, rendering an empty select that silently blocks every save of the record */
    const v = r.id != null ? r.id : (r.code != null ? r.code : r.key);
    return { v, l: r.title || r.name || r.label || r.code || r.ref || String(v) };
  });
}
async function fieldInput(f, val, registry) {
  const id = "f_" + f.key;
  if (f.type === "bool") return `<label><span>${esc(f.label)}</span><input type="checkbox" id="${id}" ${val ? "checked" : ""}></label>`;
  /* structured data the storefront renders directly (media, attributes) gets a row editor
     (public/js/editors.js) instead of a raw JSON textarea: the field declares which one
     (`editor`). Mounted after the form is in the DOM by wireEditors(), read back by collect() */
  if (f.editor && EDITORS[f.editor]) return `<div class="p-field"><span class="p-field-l">${esc(f.label)}</span><div id="${id}" data-editor="${esc(f.editor)}"></div></div>`;
  if (f.type === "json" || f.type === "multi") return `<label><span>${esc(f.label)} (JSON)</span><textarea id="${id}" rows="3">${esc(typeof val === "string" ? val : JSON.stringify(val || (f.type === "multi" ? [] : {}), null, 1))}</textarea></label>`;
  if (f.type === "select") {
    let opts = Array.isArray(f.options) ? f.options : (f.options && String(f.options).includes(".") ? String(f.options).split(".").reduce((o, k) => (o || {})[k], registry) : (registry && registry[f.options])) || f.choices || [];
    /* a registry list of rows offers each row's key */
    opts = opts.map(o => (o && typeof o === "object" ? o.key : o));
    return `<label><span>${esc(f.label)}</span><select id="${id}">${opts.map(o => `<option ${o === val ? "selected" : ""}>${esc(o)}</option>`).join("")}</select></label>`;
  }
  if (f.type.startsWith("ref:")) {
    const opts = await refOptions(f.type.slice(4), f);
    /* a record holding a value the registry no longer lists (a brand renamed or deleted
       underneath it, a legacy free-text value) must still be *representable*: without a
       matching option the select renders empty, and a REQUIRED ref then fails validation
       and silently blocks every save of that record — the value survives, unseen. */
    const unmatched = val != null && val !== "" && !opts.some(o => String(o.v) === String(val));
    return `<label><span>${esc(f.label)}</span><select id="${id}"><option value="">—</option>${unmatched ? `<option value="${esc(val)}" selected>${esc(val)}</option>` : ""}${opts.map(o => `<option value="${esc(o.v)}" ${String(o.v) === String(val) ? "selected" : ""}>${esc(o.l)}</option>`).join("")}</select></label>`;
  }
  const t = f.type === "money" || f.type === "number" ? "number" : f.type === "date" ? "date" : "text";
  const minAttr = f.min !== undefined ? `min="${f.min}"` : "";
  const maxAttr = f.max !== undefined ? `max="${f.max}"` : "";
  const patternAttr = f.pattern ? `pattern="${f.pattern}"` : "";
  const lengthAttrs = (f.minLength || f.maxLength) ? `data-minlen="${f.minLength||""}" data-maxlen="${f.maxLength||""}"` : "";
  return `<label><span>${esc(f.label)}${f.required ? " *" : ""}</span><input id="${id}" type="${t}" step="any" value="${esc(val == null ? "" : val)}" ${minAttr} ${maxAttr} ${patternAttr} ${lengthAttrs} ${f.readonly ? "disabled" : ""}></label>`;
}
function collect(def) {
  const row = {};
  for (const f of def.fields) {
    if (f.editor) {
      const get = formEditors[f.key];               /* structured editors expose a value accessor */
      if (get) { row[f.key] = get(); continue; }
    }
    const el = $("#f_" + f.key); if (!el || f.readonly) continue;
    let v = f.type === "bool" ? el.checked : el.value;
    if ((f.type === "json" || f.type === "multi") && v !== "") { try { v = JSON.parse(v); } catch (e) { toast("Invalid JSON in " + f.label); throw e; } }
    if (f.type === "money" || f.type === "number") v = v === "" ? null : Number(v);
    row[f.key] = v;
  }
  return row;
}
/* value accessors for the structured editors a form is currently showing, so collect()
   reads them back as objects without parsing a textarea */
const formEditors = {};
/* the structured editors a field may declare (`editor`): each mounts on a host and says what
   an unreadable value starts as */
const EDITORS = {
  media: { empty: () => [], mount: (host, val, registry) => mediaEditor(host, val, registry && registry.mediaKinds) },
  attrs: { empty: () => ({}), mount: (host, val) => kvEditor(host, val) }
};
function wireEditors(fields, row, registry) {
  for (const k of Object.keys(formEditors)) formEditors[k] = null;
  for (const f of fields) {
    const host = document.getElementById("f_" + f.key);
    const ed = host && EDITORS[host.dataset.editor];
    if (!ed) continue;
    let val = row[f.key];
    if (typeof val === "string") { try { val = JSON.parse(val); } catch (e) { val = ed.empty(); } }
    formEditors[f.key] = ed.mount(host, val, registry);
  }
}
async function openForm(key, id, onDone) {
  const defs = (await api("/meta/entities")).entities;
  const storeDefs = Object.fromEntries(Object.entries(defs).filter(([, d]) => !d.platformOnly));
  const def = storeDefs[key];
  const registry = await api("/meta");
  let row = {};
  if (id != null) { const rows = await entityRows(key); row = rows.find(r => String(r[def.pk] ?? r.id) === String(id)) || {}; }
  const fields = def.fields.filter(f => !["tenant_id"].includes(f.key));
  $("#modal").innerHTML = `<div class="p-modal"><div class="p-modal-box"><div class="p-modal-head"><h3>${id != null ? "Edit" : "New"} ${esc(def.label.replace(/s$/, ""))}</h3><button id="mClose">✕</button></div>
    <div class="p-form" id="mForm">${await Promise.all(fields.map(f => fieldInput(f, row[f.key], registry))).then(a => a.join(""))}
      <div style="display:flex;gap:10px;margin-top:8px"><button class="p-btn primary" id="mSave">Save</button><button class="p-btn" id="mCancel">Cancel</button></div></div></div></div>`;
  $("#modal").classList.remove("hidden");
  wireEditors(fields, row, registry); /* mount the structured media/attrs editors now that
    their host divs are in the DOM — collect() reads them back via the accessors */
  const close = () => { const m = $("#modal"); m.innerHTML = ""; m.classList.add("hidden"); };
  $("#mClose").onclick = $("#mCancel").onclick = close;
  // Inline validation feedback
  $$("#mForm input, #mForm select, #mForm textarea").forEach(el => {
    el.oninput = el.onblur = () => {
      const f = def.fields.find(x => x.key === el.id.replace("f_", ""));
      if (!f) return;
      const val = f.type === "bool" ? el.checked : el.value;
      const errors = validateField(f.key, val, f);
      el.classList.toggle("field-invalid", errors.length > 0);
      el.classList.toggle("field-valid", errors.length === 0 && val !== "");
      el.title = errors.join("\n");
    };
  });
  $("#mSave").onclick = async () => {
    try {
      const body = collect(def);
      // Validate before submit
      const errs = validateRow(body, def);
      if (Object.keys(errs).length > 0) {
        const msg = Object.entries(errs).map(([k, v]) => v.join(", ")).join(" · ");
        toast(`Validation failed: ${msg}`);
        // Highlight fields
        Object.keys(errs).forEach(k => {
          const el = $("#f_" + k);
          if (el) { el.classList.add("field-invalid"); el.title = errs[k].join("\n"); }
        });
        return;
      }
      if (id != null) await api(`/meta/entity/${key}/${encodeURIComponent(id)}`, "PUT", body);
      else {
        if (def.pkType === "text" && body[def.pk]) await api(`/meta/entity/${key}`, "POST", body);
        else await api(`/meta/entity/${key}`, "POST", body);
      }
      close(); toast("Saved"); onDone && onDone();
    } catch (e) { toast(e.message); }
  };
}
async function entityTable(key, opts = {}) {
  const defs = (await api("/meta/entities")).entities;
  // Filter out platform-only entities for store admins
  const storeDefs = Object.fromEntries(Object.entries(defs).filter(([, d]) => !d.platformOnly));
  const def = storeDefs[key];
  if (!def) return `<div class="p-empty">No access to ${esc(key)}</div>`;
  const rows = await entityRows(key);
  const listFields = def.fields.filter(f => f.list);
  const filtered = opts.filter ? rows.filter(opts.filter) : rows;
  return `<div class="p-panel"><div style="display:flex;gap:10px;margin-bottom:14px;align-items:center">
      <input class="p-search" placeholder="Filter ${esc(def.label.toLowerCase())}…" data-tbl="${key}">
      <span class="p-tag">${filtered.length} records</span><span style="flex:1"></span>
      ${def.perm.write.length ? `<button class="p-btn primary sm" data-new="${key}">+ New</button>` : ""}</div>
    <div class="p-scroll-x"><table class="p-table" data-tblm="${key}"><thead><tr>${listFields.map(f => `<th>${esc(f.label)}</th>`).join("")}<th></th></tr></thead>
      <tbody>${filtered.slice(0, 200).map(r => `<tr>${listFields.map(f => {
        let v = r[f.key];
        if (f.type === "bool") v = v ? "✓" : "—";
        if (f.type === "money") v = v != null ? money(v) : "";
        /* how a column shows is the field's declaration: the lead column carries the row's
           emoji, a badge column its value as a tone */
        if (f.display === "lead") v = `<span class="t-emoji">${esc(r.emoji || "")}</span> ${esc(String(v).slice(0, 60))}`;
        if (f.display === "badge") v = `<span class="badge ${esc(v)}">${esc(v)}</span>`;
        return `<td>${v == null ? "" : v}</td>`;
      }).join("")}<td style="text-align:right;white-space:nowrap">
        ${opts.rowExtra ? opts.rowExtra(r) : ""}
        ${def.perm.write.length ? `<button class="p-btn sm" data-edit="${key}" data-id="${esc(r[def.pk] ?? r.id)}">Edit</button>
        <button class="p-btn sm danger" data-del="${key}" data-id="${esc(r[def.pk] ?? r.id)}">✕</button>` : ""}</td></tr>`).join("")}</tbody></table></div></div>`;
}
document.addEventListener("click", async e => {
  const nb = e.target.closest("[data-new]"), eb = e.target.closest("[data-edit]"), db = e.target.closest("[data-del]");
  const act = e.target.closest("[data-act]");
  try {
    if (act && act.dataset.act === "ship-order") return shipModal(act.dataset.id, act.dataset.num);
    if (act && act.dataset.act === "admin-rec-process") {
      const r = await api("/admin/recurring/process", "POST");
      toast(`Processed ${r.processed.length} due shipment(s) · ${r.remaining} remaining`); render();
    }
    if (act && act.dataset.act === "plan-run") {
      const r = await api("/admin/planning/run", "POST");
      toast(`Plan computed for ${r.planned} SKU(s) · ${r.stats.open} open suggestion(s)`); render();
    }
    if (act && act.dataset.act === "plan-approve-all") {
      const r = await api("/admin/planning/approve-all", "POST");
      toast(`Approved ${r.approved} suggestion(s)`); render();
    }
    if (act && act.dataset.act === "plan-approve") {
      const r = await api(`/admin/planning/${act.dataset.id}`, "PUT", { status: "approved" });
      toast(`Approved ${r.replenishment.po_ref}`); render();
    }
    /* E17 · mobility — the ride lifecycle advances through the engine's legal
       transitions; the console only carries the target status the operator clicked */
    if (act && act.dataset.act === "mob-next") {
      const r = await api(`/admin/mobility/rides/${act.dataset.id}`, "PUT", { status: act.dataset.to });
      if (r.error) toast(r.error); else { toast(`Ride ${r.ride.status}${r.ride.fare ? " · fare " + (+r.ride.fare).toFixed(2) : ""}`); render(); }
    }
    if (act && act.dataset.act === "mob-new-ride") {
      const pickup = prompt("Pickup point", "Downtown · 5th Ave"); if (pickup == null) return;
      const dropoff = prompt("Drop-off point", "Airport · Terminal 4"); if (dropoff == null) return;
      const vk = ((await api("/admin/mobility", {})).vehicleKinds || []); const vd = (vk.find(k => k.default) || vk[0] || {}).key || "";
      const kind = prompt("Vehicle kind (" + vk.map(k => k.key).join(" · ") + ")", vd) || vd;
      const r = await api("/admin/mobility/rides", "POST", { rider: "Walk-up rider", pickup, dropoff, vehicle_kind: kind, payment_method: "cash" });
      if (r.error) toast(r.error); else { toast(`Requested ${r.ride.ref}${r.ride.driver ? " · dispatched to " + r.ride.driver.name : " · queued for dispatch"}`); render(); }
    }
    if (act && act.dataset.act === "mob-new-driver") {
      const name = prompt("Driver name"); if (!name) return;
      const vk = ((await api("/admin/mobility", {})).vehicleKinds || []); const vd = (vk.find(k => k.default) || vk[0] || {}).key || "";
      const kind = prompt("Vehicle kind (" + vk.map(k => k.key).join(" · ") + ")", vd) || vd;
      const plate = prompt("Plate", "") || "";
      const r = await api("/admin/mobility/drivers", "POST", { name, vehicle_kind: kind, plate, status: "offline" });
      if (r.error) toast(r.error); else { toast(`Driver ${r.driver.name} added`); render(); }
    }
    if (act && act.dataset.act === "mob-new-vehicle") {
      const plate = prompt("Plate"); if (!plate) return;
      /* the kinds, and each kind's capacity, are the mobilityVehicleKinds registry's */
      const vk = ((await api("/admin/mobility", {})).vehicleKinds || []).map(k => k.key);
      const kind = prompt("Kind (" + vk.join(" · ") + ")", vk[0] || "") || vk[0] || "";
      const r = await api("/admin/mobility/vehicles", "POST", { plate, kind });
      if (r.error) toast(r.error); else { toast(`Vehicle ${r.vehicle.plate} registered`); render(); }
    }
    if (act && act.dataset.act === "mob-toggle-driver") {
      const r = await api(`/admin/mobility/drivers/${act.dataset.id}/toggle`, "POST", { online: act.dataset.to === "1" });
      if (r.error) toast(r.error); else { toast(`Driver ${r.driver.status}`); render(); }
    }
    if (act && act.dataset.act === "mob-deact-driver") {
      if (!confirm("Deactivate this driver? They leave dispatch immediately.")) return;
      const r = await api(`/admin/mobility/drivers/${act.dataset.id}/deactivate`, "POST");
      if (r.error) toast(r.error); else { toast("Driver deactivated"); render(); }
    }
    /* surge zones: the upsert rewrites every column, so a toggle carries the row back
       intact rather than sending the active bit alone (which would flatten the rest) */
    if (act && act.dataset.act === "mob-new-zone") zoneModal(null);
    if (act && act.dataset.act === "mob-edit-zone") {
      const zd = await api("/admin/mobility", {});
      const z = (zd.zones || []).find(x => String(x.id) === String(act.dataset.id));
      if (z) zoneModal(z); else toast("Zone not found");
    }
    if (act && act.dataset.act === "mob-toggle-zone") {
      const zd = await api("/admin/mobility", {});
      const z = (zd.zones || []).find(x => String(x.id) === String(act.dataset.id));
      if (!z) return toast("Zone not found");
      const r = await api("/admin/mobility/zones", "POST", {
        id: z.id, name: z.name, kind: z.kind, multiplier: z.multiplier,
        center_lat: z.center_lat, center_lng: z.center_lng, radius_km: z.radius_km,
        active: act.dataset.on === "1", starts_at: z.starts_at, ends_at: z.ends_at
      });
      if (r.error) toast(r.error); else { toast(`Zone ${r.zone.name} ${r.zone.active ? "active" : "paused"}`); render(); }
    }
    /* E18 · operations — HRMS/payroll, procurement, manufacturing and projects. Every
       advance honours the engine's own flow and approval gate; the console only carries
       the target status the operator clicked */
    if (act && act.dataset.act === "ops-new-employee") {
      const name = prompt("Employee name"); if (!name) return;
      const dept = prompt("Department", "Operations") || "";
      const salary = Number(prompt("Base salary", "5000")) || 0;
      const r = await api("/admin/ops/employees", "POST", { name, department: dept, base_salary: salary, status: "active" });
      if (r.error) toast(r.error); else { toast(`Employee ${r.employee.code} added`); render(); }
    }
    if (act && act.dataset.act === "ops-payroll-run") {
      const period = prompt("Period (YYYY-MM)", new Date().toISOString().slice(0, 7)) || new Date().toISOString().slice(0, 7);
      const r = await api("/admin/ops/payroll/run", "POST", { period });
      if (r.error) toast(r.error); else { toast(`Payroll run for ${r.run.period}: ${r.run.headcount} employees, net ${(+r.run.net).toFixed(2)}`); render(); }
    }
    if (act && act.dataset.act === "ops-payroll-status") {
      const r = await api(`/admin/ops/payroll/${act.dataset.id}`, "PUT", { status: act.dataset.to });
      if (r.error) toast(r.error); else { toast(`Payroll ${r.run.status}`); render(); }
    }
    if (act && act.dataset.act === "ops-new-request") {
      const item = prompt("What do you need?"); if (!item) return;
      const qty = Number(prompt("Quantity", "1")) || 1;
      const cost = Number(prompt("Estimated unit cost", "10")) || 0;
      const r = await api("/admin/ops/requests", "POST", { status: "draft", requested_by: "Console", lines: [{ item, qty, est_unit_cost: cost }] });
      if (r.error) toast(r.error); else { toast(`Purchase request ${r.request.ref} created`); render(); }
    }
    if (act && act.dataset.act === "ops-pr-advance") {
      const r = await api(`/admin/ops/requests/${act.dataset.id}`, "PUT", { status: act.dataset.to });
      if (r.error) toast(r.error); else { toast(`Request ${r.request.status}`); render(); }
    }
    if (act && act.dataset.act === "ops-new-wo") {
      const product = prompt("Product ID / SKU reference", "LX-CMP-005"); if (!product) return;
      const qty = Number(prompt("Quantity to build", "100")) || 100;
      const r = await api("/admin/ops/work-orders", "POST", { product_id: product, qty, status: "planned", unit_cost: 0 });
      if (r.error) toast(r.error); else { toast(`Work order ${r.workOrder.ref} created`); render(); }
    }
    if (act && act.dataset.act === "ops-wo-complete") {
      const r = await api(`/admin/ops/work-orders/${act.dataset.id}/complete`, "POST");
      if (r.error) toast(r.error); else { toast(`Completed ${r.completed} good unit(s)${r.scrapped ? ` · ${r.scrapped} scrapped` : ""}`); render(); }
    }
    if (act && act.dataset.act === "ops-new-project") {
      const name = prompt("Project name"); if (!name) return;
      const budget = Number(prompt("Budget", "10000")) || 0;
      const r = await api("/admin/ops/projects", "POST", { name, budget, status: "planning" });
      if (r.error) toast(r.error); else { toast(`Project ${r.project.code} created`); render(); }
    }
    if (act && act.dataset.act === "ops-new-task") {
      const title = prompt("Task title"); if (!title) return;
      const projectId = prompt("Project ID (blank for none)") || null;
      const r = await api("/admin/ops/tasks", "POST", { title, project_id: projectId, status: "todo" });
      if (r.error) toast(r.error); else { toast("Task created"); render(); }
    }
    if (act && act.dataset.act === "ops-task-done") {
      const r = await api("/admin/ops/tasks", "POST", { id: act.dataset.id, title: "—", status: "done" });
      if (r.error) toast(r.error); else { toast("Task done"); render(); }
    }
    if (act && act.dataset.act === "ops-task-time") {
      const h = Number(prompt("Hours to log", "1")) || 0;
      const r = await api(`/admin/ops/tasks/${act.dataset.id}/time`, "POST", { hours: h });
      if (r.error) toast(r.error); else { toast(`Logged ${h}h`); render(); }
    }
    if (act && act.dataset.act === "ops-appr") {
      const r = await api(`/admin/ops/approvals/${act.dataset.id}`, "PUT", { status: act.dataset.to });
      if (r.error) toast(r.error); else { toast(`Approval ${r.approval.status}`); render(); }
    }
    if (act && act.dataset.act === "co-new") openForm(act.dataset.key, null, render);
    if (act && act.dataset.act === "co-cap") { view = "settings"; coCap = null; render(); }
    if (act && act.dataset.act === "co-mktperf") {
      const rows = await api("/meta/entity/seller", {});
      let n = 0;
      for (const s of (rows.rows || [])) { try { await api("/marketplace/performance/" + s.id, "POST", {}); n++; } catch (e) { } }
      toast(`Health recomputed for ${n} seller(s)`); render();
    }
    if (nb) openForm(nb.dataset.new, null, render);
    if (eb) openForm(eb.dataset.edit, eb.dataset.id, render);
    if (db) { if (!confirm("Delete this record?")) return; await api(`/meta/entity/${db.dataset.del}/${encodeURIComponent(db.dataset.id)}`, "DELETE"); toast("Deleted"); render(); }
    /* tenancy hierarchy: select a node for the config inspector, suspend/activate, delete a
       subtree, open the new-node form, and set a config override on the selected node */
    if (act && act.dataset.act === "tn-sel") { if ($("#tnKeyIn")) tnKey = $("#tnKeyIn").value.trim(); tnSel = Number(act.dataset.id); render(); }
    if (act && act.dataset.act === "tn-toggle") { const t = await api(`/tenancy/node/${act.dataset.id}`, "PUT", { status: act.dataset.to }); toast(t.error || `Node ${act.dataset.to}`); render(); }
    if (act && act.dataset.act === "tn-del") {
      const n = act.dataset.id;
      if (!confirm("Delete this node and everything beneath it?")) return;
      const t = await api(`/tenancy/node/${n}`, "DELETE");
      if (tnSel === Number(n)) tnSel = null;
      toast(t.error || `Removed ${t.removed} node(s)`); render();
    }
    if (act && act.dataset.act === "tn-new") { const h = $("#tnModalHost"); if (h) { h.classList.remove("hidden"); h.querySelector(".p-modal").style.display = "flex"; } }
    if (act && act.dataset.act === "tn-create") {
      const parent = $("#tnParent") ? Number($("#tnParent").value) : null;
      const t = await api("/tenancy/node", "POST", { parent_id: parent, kind: $("#tnKind") ? $("#tnKind").value : "organization", name: $("#tnName") ? $("#tnName").value.trim() : "" });
      if (t.error) { toast(t.error); return; }
      toast(`Created ${t.path}`); render();
    }
    if (act && act.dataset.act === "tn-cfg-set") {
      tnKey = $("#tnKeyIn") ? $("#tnKeyIn").value.trim() : tnKey;
      const raw = $("#tnValIn") ? $("#tnValIn").value.trim() : "";
      let val = {};
      if (raw) { try { val = JSON.parse(raw); } catch (e) { toast("Value must be valid JSON"); return; } }
      const t = await api(`/tenancy/config/${act.dataset.id}/${encodeURIComponent(tnKey)}`, "POST", val);
      toast(t.error || "Configuration saved"); render();
    }
  } catch (err) { toast(err.message); }
});
document.addEventListener("input", e => {
  const inp = e.target.closest("[data-tbl]");
  if (!inp) return;
  const q = inp.value.toLowerCase();
  document.querySelectorAll(`[data-tblm="${inp.dataset.tbl}"] tbody tr`).forEach(tr => {
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? "" : "none";
  });
});


document.addEventListener("click", async e => {
  const buy = e.target.closest("[data-buy]"), rel = e.target.closest("[data-rel]");
  if (!buy && !rel) return;
  try {
    if (rel) { await api("/modules/release", "POST", { module_id: rel.dataset.rel }); toast("Module released"); render(); return; }
    const mkt = await api("/market"); const m = mkt.modules.find(x => x.id === buy.dataset.buy);
    const fields = (m.fields || []);
    const mm = modal(`<div class="p-modal-head"><h3>Purchase — ${esc(m.name)}</h3><button data-mclose>✕</button></div><div class="p-form">
      <p class="p-tag">${m.price > 0 ? "An invoice of $" + m.price + " (MOD-*) will be created and marked collected." : "Free module."}</p>
      ${fields.map(f => `<label><span>${esc(f.label || f.key)}</span><input data-mcfg="${esc(f.key)}" placeholder="${esc(f.key)}"></label>`).join("")}
      <button class="p-btn primary" id="mbuyGo">Confirm purchase</button></div>`);
    mm.querySelector("#mbuyGo").onclick = async () => {
      const cfg = {};
      mm.querySelectorAll("[data-mcfg]").forEach(i => { if (i.value) cfg[i.dataset.mcfg] = (i.value === "true" || i.value === "false") ? i.value === "true" : (isNaN(+i.value) ? i.value : +i.value); });
      try { const r = await api("/modules/purchase", "POST", { module_id: m.id, config: cfg }); mm.innerHTML = ""; toast(r.invoice ? "Purchased · invoice " + r.invoice : "Installed"); render(); } catch (e2) { toast(e2.message); }
    };
  } catch (err) { toast(err.message); }
});

function modal(html) {
  let m = document.getElementById("modal");
  if (!m) { m = document.createElement("div"); m.id = "modal"; document.body.appendChild(m); }
  m.innerHTML = `<div class="p-modal"><div class="p-modal-box">${html}</div></div>`;
  /* the console shell creates #modal hidden (the forms that open it un-hide it), so opening must too */
  m.classList.remove("hidden");
  return m;
}
document.addEventListener("click", async e => {
  const pay = e.target.closest("[data-payinv]");
  if (pay) {
    const sel = document.querySelector(`[data-inv="${pay.dataset.payinv}"]`);
    try { const r = await api("/billing/invoices/" + pay.dataset.payinv + "/pay", "POST", { gateway: sel ? sel.value : undefined }); toast(r.ok ? "Invoice " + r.number + " paid" : "Failed"); render(); } catch (err) { toast(err.message); }
  }
});

/* ---------- render ---------- */
/* ---------- serialized / contracts / tenders (custom screens over the entity engine) ---------- */
const pj = (x, d) => { try { return JSON.parse(x == null || x === "" ? (d || "null") : x); } catch (e) { return d == null ? null : JSON.parse(d); } };




/* the per-section grant editor: one control per console section, each read/write/off.
   It renders for create and edit from the same shape, so the two cannot drift. */
function roleModal(role, sections, apps) {
  const appOf = k => (apps || []).find(a => a.section === k);
  const secLabel = k => { const a = appOf(k); return a ? (a.icon || "🧩") + " " + a.label + " · app" : k; };
  const r = role || { key: "", name: "", desc: "", sections: {} };
  const m = modal(`<div class="p-modal-head"><h3>${role ? "Edit role" : "New role"}</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <label><span>Name</span><input id="rmName" value="${esc(r.name)}" ${role ? "" : 'placeholder="e.g. Order Desk"'}></label>
      <label><span>Key (lowercase, no spaces)</span><input id="rmKey" value="${esc(r.key)}" ${role ? "disabled" : ""} placeholder="order_desk"></label>
      <label><span>Description</span><input id="rmDesc" value="${esc(r.desc || "")}"></label>
      <div class="p-tag">Grants — each section: write, read or off</div>
      <div style="max-height:260px;overflow:auto;border:1px solid var(--p-border);border-radius:8px;padding:8px">
      ${sections.map(sec => `<label style="display:flex;justify-content:space-between;align-items:center;padding:3px 0"><span>${esc(secLabel(sec))}</span>
        <select data-rmsec="${esc(sec)}"><option value="">off</option><option ${r.sections && r.sections[sec] === "read" ? "selected" : ""} value="read">read</option><option ${r.sections && r.sections[sec] === "write" ? "selected" : ""} value="write">write</option></select></label>`).join("")}
      </div>
      <div class="p-err hidden" id="rmErr" style="color:var(--p-red);font-size:13px"></div>
      <button class="p-btn primary" id="rmSave">${role ? "Save role" : "Create role"}</button>
    </div>`);
  m.querySelector("#rmSave").onclick = async () => {
    const sections2 = {};
    m.querySelectorAll("[data-rmsec]").forEach(sel => { if (sel.value) sections2[sel.dataset.rmsec] = sel.value; });
    const body = { name: m.querySelector("#rmName").value.trim(), key: m.querySelector("#rmKey").value.trim().toLowerCase(), desc: m.querySelector("#rmDesc").value, sections: sections2 };
    try { await api("/admin/roles", "POST", body); document.getElementById("modal").innerHTML = ""; toast("Role saved"); render(); }
    catch (e) { const err = m.querySelector("#rmErr"); err.textContent = e.message; err.classList.remove("hidden"); }
  };
}
/* ── tenancy hierarchy ── the tenant's own org tree (org → BU → brand → store → channel).
   Every node is data; the path is materialized so a subtree is one LIKE away, and the tree
   doubles as the CONFIG CASCADE — the inspector shows which node a resolved value came from. */
let tnSel = null, tnKey = "";
const TN_ICON = { tenant: "🏬", organization: "🏢", business_unit: "🧱", brand: "🏷️", store: "🏪", channel: "📡", website: "🌐", mobile_app: "📱", marketplace: "🛒", social: "💬", pos: "🧾", api_commerce: "🔌", region: "🗺️" };
function flatten(n, out = []) { out.push(n); (n.children || []).forEach(c => flatten(c, out)); return out; }

async function render() {
  shell('<div class="p-empty">Loading…</div>');
  const body = $("#vBody");
  try {
    /* every view may ask the state machines what a status means */
    await loadSM();
    if (view !== "dash" && !canSee(view)) { body.innerHTML = `<div class="p-empty">🔒 Your role (<b>${esc((A.user && A.user.staff_role) || "admin")}</b>) does not grant access to “${esc(view)}”.</div>`; return; }
    if (SCREENS[view]) { body.innerHTML = await SCREENS[view].render(view); if (SCREENS[view].wire) await SCREENS[view].wire(view); }
    else if (/^app_/.test(view)) body.innerHTML = await entityTable(view.slice(4));
    else if (view === "prodoptions" || await optionSection(view)) { body.innerHTML = await vProdOptions(view); wireProdOptions(); }
    else if (await caseKindFor(view)) { body.innerHTML = await vCases(view); wireCases(); }
    else if (await deliverableKindFor(view)) { body.innerHTML = await vDeliverables(view); wireDeliverables(view); }
  } catch (e) { body.innerHTML = `<div class="p-empty">⚠️ ${esc(e.message)}</div>`; }
}
/* the ledger: what each payment is waiting on, and the action that settles it */
async function loadPayLedger() {
  const box = $("#payLedger"); if (!box) return;
  let d; try { d = await api("/admin/payments"); } catch (e) { box.innerHTML = `<p class="p-tag">${esc(e.message)}</p>`; return; }
  const rows = d.payments || [];
  const owed = (d.owed || []).length ? `<div class="p-note"><b>Refunds owed to customers</b> — these could not be sent; refund the payment below once the reason is dealt with.<ul>${d.owed.map(r => `<li>${esc(r.order_num || "")}: ${esc(r.amount + " " + (r.currency || ""))} via ${esc(r.gateway)} — ${esc(r.error || "not sent")}</li>`).join("")}</ul></div>` : "";
  if (!rows.length) { box.innerHTML = '<p class="p-empty">No payments yet</p>'; return; }
  await loadSM();
  const act = p => smIs("payment", p.status, "awaiting") && p.live ? `<button class="p-btn sm" data-payrec="${p.id}">Check with gateway</button>`
    : smIs("payment", p.status, "awaiting") && p.offline ? `<button class="p-btn sm primary" data-payrcv="${p.id}">Record received</button>`
    : smIs("payment", p.status, "refundable") ? `<button class="p-btn sm" data-payref="${p.id}">Refund</button>` : "";
  box.innerHTML = owed + `<div class="p-scroll-x"><table class="p-table"><thead><tr><th>When</th><th>Order</th><th>Gateway</th><th>Method</th><th class="num">Amount</th><th>Status</th><th>Reference</th><th></th></tr></thead><tbody>${rows.map(p => `<tr>
    <td class="p-tag">${esc(String(p.created_at || "").slice(0, 16))}</td><td>${p.order_num ? esc(p.order_num) : (p.kind ? esc(p.kind) : "—")}</td>
    <td>${esc(p.gateway)}${p.live ? ' <span class="badge published">live</span>' : ""}</td><td class="p-tag">${esc(p.method || "")}</td>
    <td class="num">${esc(String(p.amount))} ${esc(p.currency || "")}${p.refunded > 0 ? `<br><span class="p-tag">${esc(String(p.refunded))} refunded</span>` : ""}</td><td><span class="badge ${esc(p.status)}">${esc(p.status)}</span></td>
    <td><code style="font-size:11px">${esc(p.txn_ref || "")}</code></td><td style="white-space:nowrap">${act(p)}</td></tr>`).join("")}</tbody></table></div>`;
  const go = async (path, body, done) => { try { const r = await api(path, "POST", body || {}); toast(done(r)); loadPayLedger(); } catch (e) { toast(e.message); } };
  box.querySelectorAll("[data-payrec]").forEach(b => b.onclick = () => go(`/admin/payments/${b.dataset.payrec}/reconcile`, {}, r => "Gateway says: " + ((r.result && (r.result.provider_status || r.result.status)) || r.payment.status)));
  box.querySelectorAll("[data-payrcv]").forEach(b => b.onclick = () => { if (confirm("Record this payment as received? The order is released to fulfilment.")) go(`/admin/payments/${b.dataset.payrcv}/received`, {}, () => "Payment recorded as received"); });
  box.querySelectorAll("[data-payref]").forEach(b => b.onclick = () => { const p = rows.find(x => String(x.id) === b.dataset.payref) || {}; const left = +(p.amount - (p.refunded || 0)).toFixed(2); const a = prompt("How much to refund, in " + (p.currency || "") + "? (up to " + left + ")", String(left)); if (a) go(`/admin/payments/${b.dataset.payref}/refund`, { amount: Number(a) }, r => r.amount + " " + (p.currency || "") + " refunded"); });
}

/* ---------- boot ---------- */
const A = { user: null, gwCfg: {}, studioSel: null };
document.addEventListener("click", e => { const close = e.target.closest("[data-mclose]") || (e.target.classList && e.target.classList.contains("p-modal")); if (close) { const mm = document.getElementById("modal"); if (mm) { mm.innerHTML = ""; mm.classList.add("hidden"); } } }); /* __mclose + backdrop */
(async function boot() {
  /* the unified console (/console.html) loads this bundle inside its own scope and
     drives the views itself; a guest-loaded bundle must not paint #app or it would
     clobber the one shell. LX_GUEST is set by that console's bundle wrapper */
  if (typeof LX_GUEST !== "undefined" && LX_GUEST) return;
  try {
    const [sess, cfg] = await Promise.all([api("/session"), api("/config")]);
    TT = cfg;
    if (!sess.user || sess.user.role !== "admin") {
      /* the platform console hands over here with ?token= (Stores → Catalogs →
         impersonate). The token is single-use and scoped to this store; redeeming
         it promotes this session to that store's admin without a password. */
      const t = new URLSearchParams(location.search).get("token");
      if (t) {
        try {
          const r = await api("/auth/token-exchange", "POST", { token: t });
          if (r.ok) { boot(); return; }
        } catch (e) { /* expired or issued for another store → fall through to the form */ }
      }
      const already = sess.user ? `<p class="m-help">Signed in as <b>${esc(sess.user.email)}</b> — a customer account, not a store admin. <a href="#" id="swAcct">Sign out</a></p>` : "";
      $("#app").innerHTML = `<div class="p-login"><div class="p-login-box"><h1>LUXORA</h1><p>Store Console</p>${already}
        <form id="lf" class="p-form"><label><span>Email</span><input id="le" type="email" required></label>
        <label><span>Password</span><input id="lp" type="password" required></label>
        <button class="p-btn primary" style="width:100%">Sign in</button></form>
        <p class="p-err hidden" id="lfErr" style="color:var(--p-red);font-size:13px;margin:10px 0 0"></p>
        <p class="hint" id="lfHint"></p>
        <p class="hint"><a href="/reset.html${TT ? "?store=" + encodeURIComponent(TT.tenant.slug) : ""}">Forgot your password?</a></p>
        <p class="hint">Store console for ${esc(TT ? TT.tenant.slug : "this store")} · Platform owner? <a href="/console.html?scope=platform">Platform console →</a> · <a href="/index.html">← Storefront</a></p></div></div>`;
      const sw = $("#swAcct"); if (sw) sw.onclick = async e => { e.preventDefault(); await api("/auth/logout", "POST"); boot(); };
      api("/hint").then(h => { const el = $("#lfHint"); if (el && h.demo && h.email) el.innerHTML = "This store's admin: <code>" + esc(h.email) + "</code>" + (h.password ? " / <code>" + esc(h.password) + "</code>" : ""); }).catch(() => { });
      $("#lf").onsubmit = async e => {
        e.preventDefault();
        try { await api("/auth/login", "POST", { email: $("#le").value, password: $("#lp").value }); boot(); }
        catch (err) { const b = $("#lfErr"); if (b) { b.innerHTML = "⚠️ " + linkify(err.message); b.classList.remove("hidden"); } toast(err.message); }
      };
      return;
    }
    A.user = sess.user;
    A.allowed = Array.isArray(sess.allowedSections) ? sess.allowedSections : null;
    if (!$("#modal")) { const m = document.createElement("div"); m.id = "modal"; m.className = "hidden"; document.body.appendChild(m); }
    render();
  } catch (e) { console.error(e); }
})();

async function vDocs() {
  return `<div class="a-head">
    <h2>📄 Architecture & User Manual</h2>
    <p class="a-sub">Documentation for LUXORA Platform</p>
  </div>
  <div class="a-card">
    <h3>📘 User Manual</h3>
    <p>Complete guide for store administrators, customers, and platform operations.</p>
    <p><a href="/docs/user-manual.html" target="_blank">View User Manual</a></p>
    
    <h3>🏛️ Architecture Documentation</h3>
    <p>Technical architecture, schema, data models, and integration specs.</p>
    <p><a href="/docs/architecture.html" target="_blank">View Architecture</a></p>
    
    <h3>📚 Quick Links</h3>
    <ul>
      <li><a href="/docs/user-manual.html" target="_blank">User manual</a></li>
      <li><a href="/docs/platform-reference.html" target="_blank">Platform reference</a></li>
    </ul>
  </div>
  <div class="a-card">
    <h3>🔗 Admin API Reference</h3>
    <p>Key endpoints for store administration.</p>
    <ul>
      <li><code>POST /admin/product</code> - Create product</li>
      <li><code>GET /admin/orders</code> - List orders</li>
      <li><code>GET /goip</code> - GOIP manifest</li>
    </ul>
  </div>`;
}

function wireDocs() {
  // Add click handlers if needed
}
/* ========== NEW MODULES - Affiliate, Sitemap, Shipping, Helpdesk ========== */


async function loadAffiliateStats() {
  try {
    const res = await api("/affiliate/reports");
    const s = res.summary || {};
    /* $() returns the element; $$() returns an ARRAY — writing .innerHTML onto the array
       was a silent no-op, so the stats fetched here never painted at all */
    $("#affiliateStats").innerHTML = `
      <div class="stat">
        <div class="stat-num">${s.affiliates || 0}</div>
        <div class="stat-label">Affiliates</div>
      </div>
      <div class="stat">
        <div class="stat-num">$${(s.sales || 0).toLocaleString()}</div>
        <div class="stat-label">Total Sales</div>
      </div>
      <div class="stat">
        <div class="stat-num">$${(s.commissions || 0).toLocaleString()}</div>
        <div class="stat-label">Total Commissions</div>
      </div>
    `;
  } catch (e) { console.error(e); }
}

async function loadAffiliates() {
  try {
    const res = await api("/affiliate/affiliates");
    const list = $("#affiliateList");
    if (!res.affiliates?.length) {
      list.innerHTML = `<p class="a-sub">No affiliates yet. Add one to start tracking referrals.</p>`;
      return;
    }
    let html = `<div class="a-table"><thead><tr>
      <th>Name</th><th>Code</th><th>Status</th><th>Sales</th><th>Commissions</th>
    </tr></thead><tbody>`;
    res.affiliates.forEach(a => {
      html += `<tr>
        <td>${esc(a.name)}</td>
        <td><code>${esc(a.affiliate_code)}</code></td>
        <td><span class="stat-badge ${a.status}">${esc(a.status)}</span></td>
        <td>$${(a.lifetime_sales || 0).toLocaleString()}</td>
        <td>$${(a.lifetime_commissions || 0).toLocaleString()}</td>
      </tr>`;
    });
    html += `</tbody></div>`;
    list.innerHTML = html;
  } catch (e) { console.error(e); }
}

async function createAffiliateModal() {
  const tiers = (await api("/meta").catch(() => ({}))).affiliateTiers || [];
  const m = $("#modal");
  m.innerHTML = `
    <h3>Add Affiliate</h3>
    <form class="p-form">
      <label><span>Name</span><input type="text" id="affName" required></label>
      <label><span>Email</span><input type="email" id="affEmail"></label>
      <label><span>Tier</span>
        <select id="affTier">
          ${(tiers).map(o => typeof o === "string" ? { key: o } : o).map(o => `<option value="${esc(o.key)}" ${o.default ? "selected" : ""}>${esc(o.name || o.label || o.key)}</option>`).join("")}
        </select>
      </label>
      <button class="p-btn primary">Create</button>
    </form>
  `;
  m.classList.remove("hidden");
  $("#affName").focus();
}


async function loadSitemapConfig() {
  try {
    const res = await api("/sitemap/config");
    const c = res.config || {};
    $("#sitemapConfig").innerHTML = `
      <div class="p-form">
        <label><span>Hostname</span><input type="text" id="sitemapHost" value="${esc(c.hostname || "")}" style="width:300px"></label>
        <label><span>Max entries per file</span>
          <select id="sitemapMax">
            <option value="50000" ${c.max_per_file == 50000 ? "selected" : ""}>50,000</option>
            <option value="10000" ${c.max_per_file == 10000 ? "selected" : ""}>10,000</option>
          </select>
        </label>
        <button class="p-btn" id="sitemapSave">Save</button>
      </div>
    `;
    $("#sitemapSave").onclick = saveSitemapConfig;
    $("#sitemapLast").innerHTML = `<p>Sitemap generated: <code>${esc(c.last_generated || "Never")}</code></p>`;
  } catch (e) { console.error(e); }
}

async function saveSitemapConfig() {
  const hostname = $("#sitemapHost").value;
  const maxPerFile = parseInt($("#sitemapMax").value);
  const r = await api("/sitemap/config", "PUT", { hostname, max_per_file: maxPerFile });
  if (r && r.error) return toast("❌ " + r.error);
  toast("Sitemap config saved");
  loadSitemapConfig();
}

async function generateSitemap() {
  toast("Generating sitemap...");
  const res = await api("/sitemap/generate", "POST");
  if (res.ok) {
    toast("✅ Sitemap generated (" + res.entries + " URLs) — served at /api/sitemap.xml");
    loadSitemapConfig();
  } else {
    toast("❌ Error generating sitemap");
  }
}


async function loadShipRates() {
  const box = $("#shipRates");
  if (!box) return;
  let st, prov;
  try { [st, prov] = await Promise.all([api("/admin/settings").then(r => r.settings), api("/shipping/providers").catch(() => ({ providers: [] }))]); }
  catch (e) { box.innerHTML = `<p class="a-sub">Only a store admin with Settings access can change this.</p>`; return; }
  const cm = st.commerce || {};
  const connected = (prov.providers || []).some(p => p.status === "active");
  const ready = connected && cm.shipFrom && cm.shipFrom.street1;
  box.innerHTML = `<div class="p-form"><div class="row">
    <label><span>Shipping price</span><select id="srMode"><option value="fixed" ${cm.shipRates !== "live" ? "selected" : ""}>Flat fee (${esc(String(cm.shipFee))}) or the carrier's base fee</option><option value="live" ${cm.shipRates === "live" ? "selected" : ""}>Live carrier rate</option></select></label>
    <label><span>Weight per item when a product has none (kg)</span><input id="srKg" type="number" step="0.01" min="0.01" value="${esc(String(cm.parcelWeightKg))}"></label></div>
    ${ready ? "" : `<p class="a-sub">⚠️ Live rates need ${connected ? "" : "a connected carrier account and "}a ship-from address. Until then checkout charges the flat fee.</p>`}
    <div><button class="p-btn primary" id="srSave">Save</button></div></div>`;
  $("#srSave").onclick = async () => {
    try { await api("/admin/settings", "PUT", { commerce: { shipRates: $("#srMode").value, parcelWeightKg: Number($("#srKg").value) } }); toast("Shipping pricing saved"); loadShipRates(); }
    catch (e) { toast(e.message); }
  };
}

async function loadShippingProviders() {
  const list = $("#shippingProviders");
  try {
    const res = await api("/shipping/providers");
    if (!res.providers?.length) {
      list.innerHTML = `<p class="a-sub">No carrier is connected yet. A platform admin connects one in <b>Platform console → Platform → Extension → 🔌 Provider Registry</b>. Until then, orders ship at your flat shipping fee and labels are bought outside LUXORA.</p>`;
      return;
    }
    list.innerHTML = `<div class="a-tablewrap"><table class="a-table"><thead><tr><th>Provider</th><th>Type</th><th>Status</th></tr></thead><tbody>${
      res.providers.map(p => `<tr><td>${esc(p.name)}</td><td><code>${esc(p.carrier_type)}</code></td><td><span class="badge ${esc(p.status)}">${p.status === "active" ? "connected" : esc(p.status)}</span></td></tr>`).join("")
    }</tbody></table></div>`;
  } catch (e) { list.innerHTML = `<p class="a-sub">${esc(e.message)}</p>`; }
}

async function loadShipFrom() {
  const box = $("#shipFrom");
  if (!box) return;
  let st;
  try { st = (await api("/admin/settings")).settings; }
  catch (e) { box.innerHTML = `<p class="a-sub">Only a store admin with Settings access can change the ship-from address.</p>`; return; }
  const a = (st.commerce && st.commerce.shipFrom) || {};
  const f = (k, label, ph) => `<label><span>${label}</span><input data-sf="${k}" value="${esc(a[k] || "")}" placeholder="${esc(ph || "")}"></label>`;
  box.innerHTML = `<div class="p-form">
    <div class="row">${f("name", "Contact name")}${f("company", "Company")}</div>
    <div class="row">${f("street1", "Street *")}${f("street2", "Apt, suite, unit")}</div>
    <div class="row3">${f("city", "City *")}${f("state", "State / region")}${f("zip", "Postal code *")}</div>
    <div class="row3">${f("country", "Country * (2 letters)", st.commerce && st.commerce.country)}${f("phone", "Phone")}${f("email", "Email")}</div>
    <div style="display:flex;gap:8px"><button class="p-btn primary" id="sfSave">Save address</button>
    ${a.street1 ? '<button class="p-btn" id="sfClear">Remove address</button>' : ""}</div></div>`;
  $("#sfSave").onclick = async () => {
    const addr = {};
    box.querySelectorAll("[data-sf]").forEach(i => { addr[i.dataset.sf] = i.value.trim(); });
    if (!addr.country) addr.country = st.commerce && st.commerce.country;
    try { await api("/admin/settings", "PUT", { commerce: { shipFrom: addr } }); toast("Ship-from address saved"); loadShipFrom(); }
    catch (e) { toast(e.message); }
  };
  const clr = $("#sfClear");
  if (clr) clr.onclick = async () => {
    if (!confirm("Remove the ship-from address? Carrier rates need one.")) return;
    try { await api("/admin/settings", "PUT", { commerce: { shipFrom: null } }); toast("Ship-from address removed"); loadShipFrom(); }
    catch (e) { toast(e.message); }
  };
}

async function trackShipment() {
  const number = $("#trackNumber").value;
  if (!number) return toast("Enter tracking number");
  try {
    const res = await api("/shipping/track/" + encodeURIComponent(number));
    if (res.tracking) {
      $("#trackResult").innerHTML = `
        <div class="a-table">
          <p><strong>Status:</strong> ${esc(res.tracking.status)}</p>
          <p><strong>Estimated Delivery:</strong> ${esc(res.tracking.estimated_delivery || "Unknown")}</p>
        </div>
      `;
    } else {
      toast("No tracking found for this number");
    }
  } catch (e) {
    toast("Error tracking shipment");
  }
}

/* ========== Helpdesk UI ========== */
function renderHelpdesk() {
  const html = `
    <div class="a-head">
      <h2>💬 Customer Support</h2>
      <p class="a-sub">Tickets, live chat, SMS support</p>
    </div>
    <div class="a-card">
      <h3>Active Tickets</h3>
      <div id="helpdeskTickets"></div>
    </div>
    <div class="a-card">
      <h3>Live Chat Status</h3>
      <div id="chatStatus"></div>
    </div>
  `;
  /* a view renders INTO #vBody like every other view — the old form wiped every .a-card
     and appended to #app, painting outside the shell and leaving the nav state stale */
  const body = $("#vBody");
  if (body) body.innerHTML = html;
  else { const a = $("#app"); if (a) a.innerHTML += html; }
  loadHelpdeskTickets();
  loadChatStatus();
}

async function loadHelpdeskTickets() {
  try {
    const res = await api("/admin/helpdesk/tickets");
    const list = $("#helpdeskTickets");
    if (!res.tickets?.length) {
      list.innerHTML = `<p class="a-sub">No tickets yet. Happy customers!</p>`;
      return;
    }
    let html = `<div class="a-table"><thead><tr>
      <th>Ref</th><th>Subject</th><th>Channel</th><th>Status</th><th>Priority</th>
    </tr></thead><tbody>`;
    res.tickets.forEach(t => {
      html += `<tr>
        <td><code>${esc(t.ref)}</code></td>
        <td>${esc(t.subject)}</td>
        <td><span class="stat-badge">${esc(t.channel || "email")}</span></td>
        <td><span class="stat-badge ${t.status}">${esc(t.status)}</span></td>
        <td><span class="stat-badge ${t.priority}">${esc(t.priority)}</span></td>
      </tr>`;
    });
    html += `</tbody></div>`;
    list.innerHTML = html;
  } catch (e) { console.error(e); }
}

async function loadChatStatus() {
  try {
    const res = await api("/helpdesk/agents/status");
    const status = $("#chatStatus");
    if (!res.agents?.length) {
      status.innerHTML = `<p class="a-sub">No agents configured yet.</p>`;
      return;
    }
    let html = `<div class="a-table"><thead><tr>
      <th>Agent</th><th>Status</th><th>Last Update</th>
    </tr></thead><tbody>`;
    res.agents.forEach(a => {
      html += `<tr>
        <td><code>${esc(a.agent_id)}</code></td>
        <td><span class="stat-badge ${a.status}">${esc(a.status)}</span></td>
        <td>${esc(a.updated_at)}</td>
      </tr>`;
    });
    html += `</tbody></div>`;
    status.innerHTML = html;
  } catch (e) { console.error(e); }
}

/* a surge zone is authored as a form, not a prompt chain — eight values one question at a
   time would be unusable, and the engine's upsertZone validates exactly these fields.
   Editing re-sends the whole row: the upsert rewrites every column, so a partial body
   would silently flatten the multiplier and the coordinates back to their defaults. */
/* buy a carrier label for one order: the labels it already has come first (a parcel gets
   one label), then the parcel is weighed in, rated from the store's ship-from address, and
   one of the returned rates is bought. Buying marks a processing order shipped. */
async function shipModal(orderId, num) {
  const m = modal(`<div class="p-modal-head"><h3>Ship order ${esc(num || orderId)}</h3><button data-mclose>✕</button></div><div id="shipBody"><p class="a-sub">Loading…</p></div>`);
  const box = m.querySelector("#shipBody");
  m.querySelector("[data-mclose]").onclick = () => { m.innerHTML = ""; };
  const labelRow = l => `<tr><td>${esc(l.carrier || "")} ${esc(l.service || "")}</td><td><code>${esc(l.tracking_number)}</code></td><td><span class="badge ${esc(l.status)}">${esc(l.status)}</span></td><td>${/^https:\/\//.test(l.label_url || "") ? `<a href="${esc(l.label_url)}" target="_blank" rel="noopener">Print label ↗</a>` : ""}</td></tr>`;
  let existing = [];
  try { existing = (await api(`/shipping/orders/${encodeURIComponent(orderId)}/labels`)).labels || []; }
  catch (e) { box.innerHTML = `<p class="a-sub">${esc(e.message)}</p>`; return; }
  const form = () => {
    box.innerHTML = `${existing.length ? `<p class="a-sub">This order already has ${existing.length === 1 ? "a label" : existing.length + " labels"}:</p>
      <table class="p-table"><tbody>${existing.map(labelRow).join("")}</tbody></table>
      <p class="a-sub" style="margin-top:12px">Buy another only if the order ships in more than one parcel.</p>` : ""}
      <div class="p-form">
        <div class="row"><label><span>Weight (oz) *</span><input id="shW" type="number" min="0.1" step="0.1" placeholder="e.g. 18 (16 oz = 1 lb)"></label>
        <label><span>Length × width × height (in, optional)</span><span style="display:flex;gap:6px"><input id="shL" type="number" min="0" step="0.1" placeholder="L"><input id="shWd" type="number" min="0" step="0.1" placeholder="W"><input id="shH" type="number" min="0" step="0.1" placeholder="H"></span></label></div>
        <button class="p-btn primary" id="shRate">Get rates</button>
      </div><div id="shRates"></div>`;
    box.querySelector("#shRate").onclick = rate;
  };
  const rate = async () => {
    const weight = Number(box.querySelector("#shW").value);
    if (!(weight > 0)) return toast("Enter the parcel weight in ounces");
    const out = box.querySelector("#shRates");
    out.innerHTML = `<p class="a-sub">Asking the carriers…</p>`;
    let q;
    try { q = await api("/shipping/quote", "POST", { order_id: Number(orderId), parcel: { weight_oz: weight, length: Number(box.querySelector("#shL").value) || undefined, width: Number(box.querySelector("#shWd").value) || undefined, height: Number(box.querySelector("#shH").value) || undefined } }); }
    catch (e) { out.innerHTML = `<p class="a-sub">${esc(e.message)}${/ship-from/.test(e.message) ? ' — set it in <b>Shipping &amp; Tracking</b>.' : ""}</p>`; return; }
    if (!q.rates.length) { out.innerHTML = `<p class="a-sub">No carrier offered a rate for this parcel.${q.messages && q.messages.length ? " " + esc(q.messages.join(" · ")) : ""}</p>`; return; }
    out.innerHTML = `<table class="p-table" style="margin-top:12px"><thead><tr><th>Carrier</th><th>Service</th><th class="num">Days</th><th class="num">Price</th><th></th></tr></thead><tbody>${
      q.rates.map(x => `<tr><td>${esc(x.carrier)}</td><td>${esc(x.service)}</td><td class="num">${x.days == null ? "—" : esc(x.days)}</td><td class="num">${esc(x.price.toFixed(2))} ${esc(x.currency || "")}</td><td><button class="p-btn sm primary" data-buy="${esc(x.id)}">Buy label</button></td></tr>`).join("")
    }</tbody></table>`;
    out.querySelectorAll("[data-buy]").forEach(b => b.onclick = async () => {
      const x = q.rates.find(r => r.id === b.dataset.buy);
      if (!confirm(`Buy a ${x.carrier} ${x.service} label for ${x.price.toFixed(2)} ${x.currency || ""}? Your carrier account is charged.`)) return;
      out.querySelectorAll("[data-buy]").forEach(y => { y.disabled = true; });
      try {
        const l = await api("/shipping/label", "POST", { shipment_id: q.shipment_id, rate_id: x.id });
        box.innerHTML = `<p><b>Label bought.</b> The order is marked shipped, and a customer with an account is emailed the tracking number.</p>
          <table class="p-table"><tbody>${labelRow({ carrier: l.carrier, service: l.service, tracking_number: l.tracking_number, status: "pre_transit", label_url: l.label_url })}</tbody></table>`;
        toast("Label bought · " + l.tracking_number);
        render();
      } catch (e) { toast(e.message); out.querySelectorAll("[data-buy]").forEach(y => { y.disabled = false; }); }
    });
  };
  form();
}
function zoneModal(z) {
  const isEdit = !!z;
  const v = k => (z && z[k] != null) ? z[k] : "";
  const m = modal(`<div class="p-modal-head"><h3>${isEdit ? "Edit · " + esc(z.name) : "New surge zone"}</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <label><span>Name *</span><input id="znName" value="${esc(v("name"))}" placeholder="Airport surge"></label>
      <label><span>Kind</span><select id="znKind">${["geofence", "event", "weather"].map(k => `<option ${String(v("kind")) === k ? "selected" : ""}>${k}</option>`).join("")}</select></label>
      <label><span>Multiplier (never below 1)</span><input id="znMult" type="number" step="0.05" min="1" value="${v("multiplier") || 1.5}"></label>
      <label><span>Centre latitude</span><input id="znLat" type="number" step="any" value="${v("center_lat")}" placeholder="optional"></label>
      <label><span>Centre longitude</span><input id="znLng" type="number" step="any" value="${v("center_lng")}" placeholder="optional"></label>
      <label><span>Radius (km)</span><input id="znRad" type="number" step="0.1" min="0.1" value="${v("radius_km") || 3}"></label>
      <label class="checkbox-group"><input id="znActive" type="checkbox" ${!z || z.active ? "checked" : ""}> Active now</label>
      <label><span>Starts (optional)</span><input id="znStart" type="datetime-local" value="${esc(String(v("starts_at")).replace(" ", "T"))}"></label>
      <label><span>Ends (optional)</span><input id="znEnd" type="datetime-local" value="${esc(String(v("ends_at")).replace(" ", "T"))}"></label>
      <button class="p-btn primary" id="znSave">${isEdit ? "Save zone" : "Create zone"}</button>
    </div>`);
  m.querySelector("#znSave").onclick = async () => {
    const name = m.querySelector("#znName").value.trim();
    if (!name) return toast("Zone name is required");
    const body = {
      name,
      kind: m.querySelector("#znKind").value,
      multiplier: Number(m.querySelector("#znMult").value) || 1,
      center_lat: m.querySelector("#znLat").value,
      center_lng: m.querySelector("#znLng").value,
      radius_km: Number(m.querySelector("#znRad").value) || 3,
      active: m.querySelector("#znActive").checked
    };
    const st = m.querySelector("#znStart").value, en = m.querySelector("#znEnd").value;
    if (st) body.starts_at = st;
    if (en) body.ends_at = en;
    if (isEdit) body.id = z.id;
    try {
      const r = await api("/admin/mobility/zones", "POST", body);
      if (r.error) return toast(r.error);
      m.innerHTML = "";
      toast(isEdit ? "Zone updated" : `Zone ${r.zone.name} created · ×${(+r.zone.multiplier).toFixed(2)}`);
      render();
    } catch (e) { toast(e.message); }
  };
}


/* ========== Module Registration ========== */
window.renderHelpdesk = renderHelpdesk;
window.generateSitemap = generateSitemap;
window.trackShipment = trackShipment;


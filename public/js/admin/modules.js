/* LUXORA Platform — the modules domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vModules() {
  const [mkt, own] = await Promise.all([api("/market"), api("/modules")]);
  const has = id => own.installed.some(x => x.id === id);
  const cats = {};
  mkt.modules.forEach(m => { (cats[m.category] = cats[m.category] || []).push(m); });
  return `
  <p class="p-tag" style="margin:0 0 14px">This store's capabilities: ${own.capabilities.map(c => `<span class="p-chip">${esc(c)}</span>`).join(" ")} — purchase more below; billed via store invoice (MOD-*).</p>
  ${Object.entries(cats).map(([cat, ms]) => `<div class="p-panel"><h2>${esc(cat)}</h2>
    ${ms.map(m => {
    const on = has(m.id);
    return `<div style="display:flex;gap:14px;align-items:center;padding:10px 0;border-bottom:1px solid var(--p-line)">
      <div style="flex:1"><b>${esc(m.name)}</b> <span class="p-tag">${m.price > 0 ? esc(m.price + " " + (m.currency || (DFLT && DFLT.currency) || "")) + " one-time" : "free"} · ${m.capabilities.map(esc).join(", ")}</span><br><span class="p-tag">${esc(m.summary || "")}</span></div>
      ${on ? `<button class="p-btn sm danger" data-rel="${esc(m.id)}">Release</button>` : `<button class="p-btn sm primary" data-buy="${esc(m.id)}">Purchase</button>`}</div>`;
  }).join("")}</div>`).join("")}`;
}

screen("applicability", { group: "Settings", label: "🧭 Availability Rules", order: 1, render: async () => `<div id="rulesRoot"></div>`, wire: async () => { await LXRulesUI.mount(document.getElementById("rulesRoot"), { api, base: "/admin/rules", scope: "store" }); } });
screen("modules", { group: "Settings", label: "🧩 Modules", order: 2, render: async () => await vModules() });

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

/* ---------- shopper features: one screen each, drawn from the feature's own declaration ---------- */
const FEATURE_INPUT = {
  textarea: f => `<textarea id="ft_${f.key}" rows="4"></textarea>`, bool: f => `<input id="ft_${f.key}" type="checkbox" ${f.default ? "checked" : ""}>`,
  weekday: f => `<select id="ft_${f.key}">${Array.from({ length: 7 }, (_, i) => `<option value="${i}">${esc(new Date(Date.UTC(2023, 0, 1 + i)).toLocaleDateString(undefined, { weekday: "long", timeZone: "UTC" }))}</option>`).join("")}</select>`,
  choice: f => `<select id="ft_${f.key}">${(f.options || []).map(o => `<option>${esc(o)}</option>`).join("")}</select>`
};
const featureInput = f => FEATURE_INPUT[f.type] ? FEATURE_INPUT[f.type](f) : `<input id="ft_${f.key}" type="${{ number: "number", int: "number", date: "date", datetime: "datetime-local", time: "time", url: "url" }[f.type] || "text"}" step="any" value="${esc(f.default == null ? "" : f.default)}">`;
const featureCell = (f, v) => v == null || v === "" ? "—" : f.type === "bool" ? (v ? "yes" : "no") : f.type === "weekday" ? esc(new Date(Date.UTC(2023, 0, 1 + Number(v))).toLocaleDateString(undefined, { weekday: "long", timeZone: "UTC" })) : f.type === "datetime" ? esc(new Date(v).toLocaleString()) : esc(String(v).length > 80 ? String(v).slice(0, 80) + "…" : v);
async function vFeature(key) {
  const d = await api("/admin/features/" + key, {}), F = d.feature;
  if (!d.on) return coOff(F.title.toLowerCase(), F.icon + " " + F.title, [key]);
  const form = F.fields.length ? `<div class="a-card"><div class="p-form"><div class="row">${F.fields.map(f => `<label><span>${esc(f.label)}${f.required ? " *" : ""}</span>${featureInput(f)}</label>`).join("")}</div><button class="p-btn primary" data-ftadd="${key}">Add</button></div>
    <div class="a-tablewrap"><table class="a-table"><thead><tr>${F.fields.map(f => `<th>${esc(f.label)}</th>`).join("")}<th></th></tr></thead><tbody>${d.rows.map(r => `<tr>${F.fields.map(f => `<td>${featureCell(f, r[f.key])}</td>`).join("")}<td><button class="btn-white sm" data-ftdel="${r.id}">Remove</button></td></tr>`).join("") || `<tr><td colspan="${F.fields.length + 1}">Nothing yet.</td></tr>`}</tbody></table></div></div>` : "";
  const list = d.list.length ? `<div class="a-card"><div class="a-tablewrap"><table class="a-table"><tbody>${d.list.map(x => `<tr><td>${esc(x.text)}</td><td>${x.chip ? `<span class="a-chip">${esc(x.chip)}</span>` : ""}</td><td style="white-space:nowrap">${(x.actions || []).map(a => `<button class="btn-white sm" data-ftact="${esc(a.key)}" data-id="${x.id}" data-ask="${esc(a.ask || "")}">${esc(a.label)}</button> `).join("")}</td></tr>`).join("")}</tbody></table></div></div>` : "";
  return `<div class="a-head"><h2>${F.icon} ${esc(F.title)}</h2><p class="a-sub">${esc(F.help)}</p></div>${form}${list || (F.fields.length ? "" : '<div class="a-card"><p class="a-sub">Nothing yet. Its settings are on the capability itself.</p></div>')}<div id="ftDoc"></div>`;
}
async function wireFeature(key) {
  const add = $("[data-ftadd]");
  if (add) { const F = (await api("/admin/features/" + key, {})).feature; add.onclick = () => { const b = {}; for (const f of F.fields) { const el = $("#ft_" + f.key); b[f.key] = f.type === "bool" ? el.checked : f.type === "datetime" && el.value ? new Date(el.value).toISOString() : el.value; } postAndRender("/admin/features/" + key, b, "POST", "Added"); }; }
  $$("[data-ftdel]").forEach(x => x.onclick = async () => { try { await api("/admin/features/" + key + "/" + x.dataset.ftdel, "DELETE"); render(); } catch (e) { toast(e.message); } });
  $$("[data-ftact]").forEach(x => x.onclick = async () => {
    const value = x.dataset.ask ? prompt(x.dataset.ask) : ""; if (value == null) return;
    try { const r = await api("/admin/features/" + key + "/" + x.dataset.ftact + "/" + x.dataset.id, "POST", { value }); if (r.document) { $("#ftDoc").innerHTML = `<div class="a-card"><pre style="white-space:pre-wrap">${esc(JSON.stringify(r.document, null, 2))}</pre></div>`; return; } toast(r.outOfRange ? "⚠️ Out of range" : "Done"); render(); } catch (e) { toast(e.message); }
  });
}
screen("sale_events", { group: "Offers", label: "🏷️ Sale events", order: 60, render: async () => await vFeature("sale_events"), wire: async () => { await wireFeature("sale_events"); } });
screen("club_pricing", { group: "Offers", label: "🎟️ Club pricing", order: 60, render: async () => await vFeature("club_pricing"), wire: async () => { await wireFeature("club_pricing"); } });
screen("live_selling", { group: "Marketing", label: "🎥 Live selling", order: 60, render: async () => await vFeature("live_selling"), wire: async () => { await wireFeature("live_selling"); } });
screen("payment_instrument_offers", { group: "Payments & Finance", label: "💳 Payment offers", order: 60, render: async () => await vFeature("payment_instrument_offers"), wire: async () => { await wireFeature("payment_instrument_offers"); } });
screen("instalments_without_cost", { group: "Payments & Finance", label: "🗓️ Instalments without cost", order: 60, render: async () => await vFeature("instalments_without_cost"), wire: async () => { await wireFeature("instalments_without_cost"); } });
screen("duties_at_checkout", { group: "Orders & Fulfilment", label: "🛃 Duties at checkout", order: 60, render: async () => await vFeature("duties_at_checkout"), wire: async () => { await wireFeature("duties_at_checkout"); } });
screen("customs_declarations", { group: "Orders & Fulfilment", label: "📄 Customs declarations", order: 60, render: async () => await vFeature("customs_declarations"), wire: async () => { await wireFeature("customs_declarations"); } });
screen("consolidated_shipping", { group: "Orders & Fulfilment", label: "📦 Consolidated shipping", order: 60, render: async () => await vFeature("consolidated_shipping"), wire: async () => { await wireFeature("consolidated_shipping"); } });
screen("supplier_direct", { group: "Orders & Fulfilment", label: "🏭 Supplier direct", order: 60, render: async () => await vFeature("supplier_direct"), wire: async () => { await wireFeature("supplier_direct"); } });
screen("reseller_margins", { group: "Marketing", label: "🤝 Reseller margins", order: 60, render: async () => await vFeature("reseller_margins"), wire: async () => { await wireFeature("reseller_margins"); } });
screen("affiliate_commissions", { group: "Marketing", label: "🔗 Affiliate commissions", order: 60, render: async () => await vFeature("affiliate_commissions"), wire: async () => { await wireFeature("affiliate_commissions"); } });
screen("gamified_rewards", { group: "Marketing", label: "🎯 Daily rewards", order: 60, render: async () => await vFeature("gamified_rewards"), wire: async () => { await wireFeature("gamified_rewards"); } });
screen("funding_goals", { group: "Offers", label: "🚀 Funding goals", order: 60, render: async () => await vFeature("funding_goals"), wire: async () => { await wireFeature("funding_goals"); } });
screen("seat_maps", { group: "Catalogue", label: "💺 Seat maps", order: 60, render: async () => await vFeature("seat_maps"), wire: async () => { await wireFeature("seat_maps"); } });
screen("travel_itineraries", { group: "Catalogue", label: "🧳 Travel itineraries", order: 60, render: async () => await vFeature("travel_itineraries"), wire: async () => { await wireFeature("travel_itineraries"); } });
screen("fitment", { group: "Catalogue", label: "🚗 Fitment", order: 60, render: async () => await vFeature("fitment"), wire: async () => { await wireFeature("fitment"); } });
screen("schedule_rules", { group: "Catalogue", label: "⚕️ Schedule rules", order: 60, render: async () => await vFeature("schedule_rules"), wire: async () => { await wireFeature("schedule_rules"); } });
screen("generic_alternatives", { group: "Catalogue", label: "💊 Generic alternatives", order: 60, render: async () => await vFeature("generic_alternatives"), wire: async () => { await wireFeature("generic_alternatives"); } });
screen("refill_reminders", { group: "Marketing", label: "🔔 Refill reminders", order: 60, render: async () => await vFeature("refill_reminders"), wire: async () => { await wireFeature("refill_reminders"); } });
screen("kitchen_hours", { group: "Catalogue", label: "🍳 Kitchen hours", order: 60, render: async () => await vFeature("kitchen_hours"), wire: async () => { await wireFeature("kitchen_hours"); } });
screen("batch_expiry", { group: "Catalogue", label: "📅 Batch expiry", order: 60, render: async () => await vFeature("batch_expiry"), wire: async () => { await wireFeature("batch_expiry"); } });
screen("freshness_windows", { group: "Catalogue", label: "🥬 Freshness windows", order: 60, render: async () => await vFeature("freshness_windows"), wire: async () => { await wireFeature("freshness_windows"); } });
screen("cold_chain", { group: "Orders & Fulfilment", label: "❄️ Cold chain", order: 60, render: async () => await vFeature("cold_chain"), wire: async () => { await wireFeature("cold_chain"); } });
screen("large_item_delivery", { group: "Orders & Fulfilment", label: "🛋️ Large item delivery", order: 60, render: async () => await vFeature("large_item_delivery"), wire: async () => { await wireFeature("large_item_delivery"); } });
screen("dated_delivery", { group: "Orders & Fulfilment", label: "🎁 Dated delivery", order: 60, render: async () => await vFeature("dated_delivery"), wire: async () => { await wireFeature("dated_delivery"); } });
screen("sell_by_weight", { group: "Catalogue", label: "⚖️ Sell by weight", order: 60, render: async () => await vFeature("sell_by_weight"), wire: async () => { await wireFeature("sell_by_weight"); } });

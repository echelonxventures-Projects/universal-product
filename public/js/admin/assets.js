/* LUXORA Platform — the fixed assets domain's store-console screen (lib/assets.js; _registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope. The register, an asset's
   depreciation schedule, posting depreciation, and selling or writing an asset off. */
"use strict";

let faOpen = null;
async function vFixedAssets() {
  const r = await api("/admin/assets");
  const one = faOpen ? await api("/admin/assets/" + faOpen).catch(() => null) : null;
  const m = (n, c) => `${(+n || 0).toFixed(2)} ${esc(c || "")}`;
  const detail = one ? `<div class="a-card"><h3><code>${esc(one.asset.ref)}</code> ${esc(one.asset.name)} ${coBadge(one.asset.status)}</h3>
    <p class="a-sub">${esc(one.asset.categoryLabel)} · ${esc(one.asset.methodLabel)} · ${one.asset.life_months} months from ${esc(one.asset.in_service)} · cost ${m(one.asset.cost, one.asset.currency)} · book value ${m(one.asset.book, one.asset.currency)}${one.asset.disposal_reason ? " · " + esc(one.asset.disposal_reason) : ""}</p>
    ${one.asset.inUse ? `<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Date</span><input id="faDD" type="date"></label><label><span>Sold for</span><input id="faDP" type="number" min="0" step="0.01" style="width:110px"></label>
      <label><span>Why</span><input id="faDR" maxlength="300"></label><label><span>Write it off</span><input id="faDW" type="checkbox"></label><button class="p-btn sm" id="faDGo">Sell or write off</button></div>` : ""}
    ${coTbl(["month", "depreciation", "to date", "book value", ""], one.schedule, x => [esc(x.period), m(x.amount), m(x.accumulated), m(x.book), x.posted ? "posted" : ""], "")}</div>` : "";
  return `<div class="a-head"><h2>🏷️ Fixed Assets</h2><p class="a-sub">What the business owns and uses for years. Its cost goes on the books when it is bought, it depreciates month by month, and selling it posts the gain or loss.</p></div>
  <div class="a-card"><h3>Register an asset</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
    <label><span>Name</span><input id="faN" maxlength="160"></label><label><span>Category</span><select id="faC">${r.categories.map(c => `<option value="${esc(c.key)}">${esc(c.label)} · ${c.lifeMonths} months</option>`).join("")}</select></label>
    <label><span>Cost</span><input id="faCo" type="number" min="0" step="0.01" style="width:110px"></label><label><span>Residual value</span><input id="faRe" type="number" min="0" step="0.01" style="width:110px"></label>
    <label><span>Life in months</span><input id="faL" type="number" min="1" style="width:80px" placeholder="category"></label>
    <label><span>Method</span><select id="faM">${Object.entries(r.methods).map(([k, x]) => `<option value="${esc(k)}">${esc(x.label)}</option>`).join("")}</select></label>
    <label><span>Bought on</span><input id="faA" type="date"></label><label><span>Paid</span><select id="faPF">${Object.entries(r.paidFrom).map(([k, x]) => `<option value="${esc(k)}">${esc(x.label)}</option>`).join("")}</select></label>
    <label><span>Serial no.</span><input id="faS" maxlength="120"></label><button class="p-btn sm primary" id="faGo">Register</button></div></div>
  <div class="a-card"><h3>Depreciation</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Through the month</span><input id="faT" type="month"></label><button class="p-btn sm" id="faRun">Post depreciation</button></div>
    <p class="a-sub">Each month is posted once. The platform posts every month as it ends.</p></div>
  ${detail}
  <div class="a-card"><h3>The register</h3>${coTbl(["asset", "category", "cost", "depreciation to date", "book value", "status", ""], r.assets, a => [`<code>${esc(a.ref)}</code> ${esc(a.name)}`, esc(a.categoryLabel), m(a.cost, a.currency), m(a.accumulated, a.currency), m(a.book, a.currency), coBadge(a.status), `<button class="p-btn sm" data-fa-open="${a.id}">Open</button>`], "No assets yet.")}
    ${coTbl(["category", "assets", "cost", "depreciation to date", "book value"], r.totals, x => [esc(x.label), x.n, m(x.cost, x.currency), m(x.accumulated, x.currency), `<b>${m(x.book, x.currency)}</b>`], "")}</div>`;
}
function wireFixedAssets() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  document.querySelectorAll("[data-fa-open]").forEach(b => b.onclick = () => { faOpen = b.dataset.faOpen; render(); });
  const g = $("#faGo"); if (g) g.onclick = () => go(() => api("/admin/assets", "POST", { name: $("#faN").value, category: $("#faC").value, cost: Number($("#faCo").value), residual: Number($("#faRe").value) || 0, life_months: Number($("#faL").value) || undefined, method: $("#faM").value, acquired_on: $("#faA").value || undefined, paid_from: $("#faPF").value, serial: $("#faS").value }), "Registered");
  const r = $("#faRun"); if (r) r.onclick = () => go(async () => { const x = await api("/admin/assets/depreciate", "POST", { through: $("#faT").value || undefined }); toast(`${x.months} months posted for ${x.assets} assets`); });
  const d = $("#faDGo"); if (d) d.onclick = () => go(() => api("/admin/assets/" + faOpen + "/dispose", "POST", { date: $("#faDD").value || undefined, proceeds: Number($("#faDP").value) || 0, reason: $("#faDR").value, write_off: $("#faDW").checked }), "Done");
}
screen("fixed_assets", { render: async () => await vFixedAssets(), wire: wireFixedAssets });

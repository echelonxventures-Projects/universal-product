/* LUXORA Platform — the budgets domain's store-console screen (lib/budgets.js; _registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope. Draft a year's budget per
   account, approve it, and see it against the books. */
"use strict";

let buOpen = null;
async function vBudgets() {
  const r = await api("/admin/budgets");
  const b = buOpen ? await api("/admin/budgets/" + buOpen).catch(() => null) : null, rep = b ? await api("/admin/budgets/" + buOpen + "/report").catch(() => null) : null;
  const m = n => (+n || 0).toFixed(2);
  const acc = r.accounts.map(a => `<option value="${esc(a.code)}">${esc(a.code)} · ${esc(a.name)}</option>`).join("");
  const detail = b ? `<div class="a-card"><h3><code>${esc(b.budget.ref)}</code> ${esc(b.budget.name)} · ${b.budget.year} · ${esc(b.budget.currency)} ${coBadge(b.budget.status)}</h3>
    <p class="a-sub">Planned for the year: <b>${m(b.budget.total)}</b></p>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      ${b.budget.editable ? `<label><span>Account</span><select id="buA">${acc}</select></label><label><span>For the year</span><input id="buY" type="number" min="0" step="0.01" style="width:120px"></label><button class="p-btn sm" id="buSet">Set, spread evenly</button>
        <label><span>From the actuals of</span><input id="buFY" type="number" value="${b.budget.year - 1}" style="width:80px"></label><label><span>Uplift %</span><input id="buFU" type="number" value="0" style="width:70px"></label><button class="p-btn sm" id="buFrom">Fill</button>
        <button class="p-btn sm primary" data-bu-act="approve">Approve</button>` : ""}
      ${b.budget.live ? `<button class="p-btn sm" data-bu-act="reopen">Reopen</button><button class="p-btn sm" data-bu-act="close">Close</button>` : ""}</div></div>
    ${rep ? `<div class="a-card"><h3>Against the books, to month ${rep.through}</h3><p class="a-sub">Off plan means more than ${rep.tolerancePct}% above budget for an expense, or below it for income. Profit: planned ${m(rep.totals.profit.budget)}, actual ${m(rep.totals.profit.actual)}.</p>
      ${coTbl(["account", "for the year", "budget to date", "actual to date", "variance", "used", ""], rep.rows, x => [`${esc(x.account)} · ${esc(x.name)}`, m(x.year), m(x.budget), m(x.actual), m(x.variance), x.usedPct == null ? "—" : x.usedPct + "%", x.off ? `<span class="p-tag">${x.budgeted ? "off plan" : "no budget"}</span>` : ""], "Nothing planned or spent yet.")}</div>` : ""}` : "";
  return `<div class="a-head"><h2>🎯 Budgets</h2><p class="a-sub">A year's plan for each income and expense account, month by month, and how the books compare.</p></div>
  <div class="a-card"><h3>New budget</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Name</span><input id="buN" maxlength="160"></label><label><span>Year</span><input id="buYr" type="number" value="${new Date().getFullYear()}" style="width:80px"></label>
    <label><span>Currency</span><input id="buC" maxlength="8" style="width:70px"></label><button class="p-btn sm primary" id="buGo">Draft</button></div></div>
  ${detail}
  <div class="a-card"><h3>Budgets</h3>${coTbl(["budget", "year", "currency", "planned", "status", ""], r.budgets, x => [`<code>${esc(x.ref)}</code> ${esc(x.name)}`, x.year, esc(x.currency), m(x.total), coBadge(x.status), `<button class="p-btn sm" data-bu-open="${x.id}">Open</button>`], "No budgets yet.")}</div>`;
}
function wireBudgets() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  document.querySelectorAll("[data-bu-open]").forEach(b => b.onclick = () => { buOpen = b.dataset.buOpen; render(); });
  const g = $("#buGo"); if (g) g.onclick = () => go(async () => { const r = await api("/admin/budgets", "POST", { name: $("#buN").value, year: Number($("#buYr").value), currency: $("#buC").value || undefined }); buOpen = r.budget.id; }, "Drafted");
  const s = $("#buSet"); if (s) s.onclick = () => go(() => api("/admin/budgets/" + buOpen + "/lines", "PUT", { lines: [{ account: $("#buA").value, annual: Number($("#buY").value) }] }), "Set");
  const f = $("#buFrom"); if (f) f.onclick = () => go(() => api("/admin/budgets/" + buOpen + "/from-actuals", "POST", { year: Number($("#buFY").value), uplift_pct: Number($("#buFU").value) }), "Filled");
  document.querySelectorAll("[data-bu-act]").forEach(b => b.onclick = () => go(() => api("/admin/budgets/" + buOpen + "/" + b.dataset.buAct, "POST", {}), "Done"));
}
screen("budgets", { render: async () => await vBudgets(), wire: wireBudgets });

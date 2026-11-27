/* LUXORA Platform — the books domain's store-console screen (lib/books.js; _registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope. One screen: the reports
   (trial balance, profit and loss, balance sheet), the latest entries, the chart of accounts, and
   an accountant's entry — every figure read from /api/admin/books. */
"use strict";

let booksTab = "pl";
async function vBooks() {
  const [acc, tb, pl, bs, en, h] = await Promise.all([api("/admin/books/accounts"), api("/admin/books/trial-balance"), api("/admin/books/profit-and-loss"),
    api("/admin/books/balance-sheet"), api("/admin/books/entries", { limit: 30 }), api("/admin/books/health")]);
  const amt = (v, c) => `${money(v)} <span class="a-sub">${esc(c)}</span>`;
  const lines = (rows, c) => rows.map(r => `<tr><td><code>${esc(r.account)}</code></td><td>${esc(r.name)}</td><td style="text-align:right">${amt(r.balance, c)}</td></tr>`).join("");
  /* the statement sections come from the server (each account type's side) */
  const plCards = pl.profitAndLoss.map(p => `<div class="a-card"><h3>Profit and loss · ${esc(p.currency)}</h3>
    <table class="a-table"><tbody>${lines(p.income, p.currency)}<tr><th colspan="2">Income</th><th style="text-align:right">${amt(p.totalIncome, p.currency)}</th></tr>
    ${lines(p.expense, p.currency)}<tr><th colspan="2">Expenses</th><th style="text-align:right">${amt(p.totalExpense, p.currency)}</th></tr>
    <tr><th colspan="2">Profit</th><th style="text-align:right">${amt(p.profit, p.currency)}</th></tr></tbody></table></div>`).join("");
  const bsCards = bs.balanceSheet.map(b => `<div class="a-card"><h3>Balance sheet · ${esc(b.currency)}</h3>
    <table class="a-table"><tbody>${lines(b.assets, b.currency)}<tr><th colspan="2">Assets</th><th style="text-align:right">${amt(b.totalAssets, b.currency)}</th></tr>
    ${lines(b.liabilities, b.currency)}${lines(b.equity, b.currency)}<tr><td></td><td>Earnings to date</td><td style="text-align:right">${amt(b.earnings, b.currency)}</td></tr>
    <tr><th colspan="2">Liabilities and equity</th><th style="text-align:right">${amt(b.totalLiabilitiesAndEquity, b.currency)}</th></tr></tbody></table></div>`).join("");
  const tbCards = tb.trialBalance.map(t => `<div class="a-card"><h3>Trial balance · ${esc(t.currency)}</h3>
    <table class="a-table"><thead><tr><th>Account</th><th></th><th style="text-align:right">Debit</th><th style="text-align:right">Credit</th></tr></thead><tbody>
    ${t.rows.map(r => `<tr><td><code>${esc(r.account)}</code></td><td>${esc(r.name)}</td><td style="text-align:right">${money(r.debit)}</td><td style="text-align:right">${money(r.credit)}</td></tr>`).join("")}
    <tr><th colspan="2">Total</th><th style="text-align:right">${money(t.debit)}</th><th style="text-align:right">${money(t.credit)}</th></tr></tbody></table></div>`).join("");
  const reports = { pl: plCards, bs: bsCards, tb: tbCards }[booksTab] || "";
  const leaf = acc.accounts.filter(a => !a.group);
  const opts = leaf.map(a => `<option value="${esc(a.code)}">${esc(a.code)} · ${esc(a.name)}</option>`).join("");
  const healthy = !h.missing.length && !h.unbalanced.length && !h.drift.length;
  return `<div class="a-head"><h2>📒 Books</h2>
    <p class="a-sub">Sales, refunds, gateway fees, chargebacks and the platform's bills post themselves. Every entry balances, is kept in the tamper-evident log, and is corrected only by a reversal.</p>
    <p class="a-sub">${healthy ? '<span class="a-chip">✓ every payment and invoice is in the books</span>' : `<span class="p-tag">${esc(h.missing.length)} not yet in the books</span>`}</p></div>
  <div style="display:flex;gap:8px;margin-bottom:12px">${[["pl", "Profit and loss"], ["bs", "Balance sheet"], ["tb", "Trial balance"]].map(([k, l]) => `<button class="p-btn sm${booksTab === k ? " primary" : ""}" data-books-tab="${k}">${l}</button>`).join("")}</div>
  ${reports || '<div class="a-card"><p class="a-sub">Nothing has been posted yet.</p></div>'}
  <div class="a-card"><h3>Latest entries</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>#</th><th>What</th><th>Lines</th><th>When</th><th></th></tr></thead><tbody>
    ${en.entries.map(e => `<tr><td>${e.id}</td><td>${esc(e.memo || e.op)}${e.reverses ? ` <span class="a-chip">reverses #${e.reverses}</span>` : ""}</td>
      <td>${e.lines.map(l => `<code>${esc(l.account)}</code> ${l.debit ? "Dr " + money(l.debit) : "Cr " + money(l.credit)}`).join("<br>")}</td><td>${esc(e.at)}</td>
      <td>${e.reversible ? `<button class="p-btn sm" data-books-reverse="${e.id}">Reverse</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="5">—</td></tr>'}</tbody></table></div></div>
  <div class="a-card"><h3>Post an entry</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px">
      <label><span>Debit account</span><select id="bkDr">${opts}</select></label>
      <label><span>Credit account</span><select id="bkCr">${opts}</select></label>
      <label><span>Amount</span><input id="bkAmt" type="number" step="0.01" min="0"></label>
      <label><span>What it is for</span><input id="bkMemo" maxlength="300"></label></div>
    <button class="p-btn sm primary" id="bkPost" style="margin-top:8px">Post</button></div>
  <div class="a-card"><h3>Chart of accounts</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>Code</th><th>Name</th><th>Type</th><th></th></tr></thead><tbody>
    ${acc.accounts.map(a => `<tr><td><code>${esc(a.code)}</code></td><td>${a.group ? `<b>${esc(a.name)}</b>` : "&nbsp;&nbsp;" + esc(a.name)}</td><td>${esc((acc.types[a.type] || {}).label || a.type)}</td><td>${a.own ? '<span class="a-chip">this store</span>' : ""}</td></tr>`).join("")}</tbody></table></div>
    <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
      <label><span>Group</span><select id="bkGrp">${acc.accounts.filter(a => a.group).map(a => `<option value="${esc(a.code)}">${esc(a.code)} · ${esc(a.name)}</option>`).join("")}</select></label>
      <label><span>Code</span><input id="bkCode" maxlength="20"></label><label><span>Name</span><input id="bkName" maxlength="120"></label>
      <button class="p-btn sm" id="bkAdd">Add account</button></div></div>`;
}
function wireBooks() {
  document.querySelectorAll("[data-books-tab]").forEach(b => b.onclick = () => { booksTab = b.dataset.booksTab; render(); });
  document.querySelectorAll("[data-books-reverse]").forEach(b => b.onclick = async () => {
    const reason = prompt("Why is this entry reversed?"); if (!reason) return;
    try { await api("/admin/books/entries/" + b.dataset.booksReverse + "/reverse", "POST", { reason }); toast("Reversed"); render(); } catch (e) { toast(e.message); }
  });
  const post = $("#bkPost"); if (post) post.onclick = async () => {
    const amount = Number($("#bkAmt").value);
    try { await api("/admin/books/entries", "POST", { memo: $("#bkMemo").value, lines: [{ account: $("#bkDr").value, debit: amount }, { account: $("#bkCr").value, credit: amount }] }); toast("Posted"); render(); } catch (e) { toast(e.message); }
  };
  const add = $("#bkAdd"); if (add) add.onclick = async () => {
    try { await api("/admin/books/accounts", "POST", { parent: $("#bkGrp").value, code: $("#bkCode").value, name: $("#bkName").value }); toast("Account added"); render(); } catch (e) { toast(e.message); }
  };
}
screen("books", { render: async () => await vBooks(), wire: wireBooks });

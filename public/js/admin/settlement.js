/* LUXORA Platform — the settlement domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vFinance() {
  const [disp, pays, led] = await Promise.all([api("/admin/fin/disputes"), api("/admin/fin/payouts"), api("/admin/fin/ledger", { owner: "t1:s:demo" })]);
  const byS = {}; disp.disputes.forEach(d => byS[d.state] = (byS[d.state] || 0) + 1);
  return `<div class="a-head"><h2>💰 Finance &amp; Settlements</h2><p class="a-sub">Chargebacks / disputes · multi-gateway retries · batch payout runs · bank-feed reconciliation · FX-aware ledger. States &amp; kinds in Data Studio: <code>finDisputeStates</code>, <code>finPayoutKinds</code>, <code>finReconSources</code>.</p></div>
  <div class="a-card"><h3>Disputes / chargebacks</h3>
    <p class="a-sub">${Object.entries(byS).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join("") || "none open"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>payment</th><th>amount</th><th>state</th></tr></thead>
      <tbody>${disp.disputes.slice(0, 15).map(d => `<tr><td><code>${esc(d.ref)}</code></td><td>${d.payment_id || "—"}</td><td>${money(d.amount)} ${esc(d.currency)}</td><td><span class="a-chip">${esc(d.state)}</span></td></tr>`).join("") || '<tr><td colspan="4">No disputes.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>Payout runs</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>kind</th><th>seller</th><th>gross</th><th>net</th><th>status</th><th>items</th></tr></thead>
      <tbody>${pays.payouts.slice(0, 15).map(p => `<tr><td><code>${esc(p.ref)}</code></td><td>${esc(p.kind)}</td><td>${p.seller_id || "—"}</td><td>${money(p.gross)}</td><td>${money(p.net)}</td><td><span class="a-chip">${esc(p.status)}</span></td><td>${p.items}</td></tr>`).join("") || '<tr><td colspan="7">No payout runs.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>FX ledger · <code>t1:s:demo</code></h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>kind</th><th>amount</th><th>currency</th><th>balance_after</th></tr></thead>
      <tbody>${(led.entries || []).slice(0, 10).map(e => `<tr><td>${esc(e.kind)}</td><td>${money(e.amount)}</td><td>${esc(e.currency)}</td><td>${money(e.balance_after)}</td></tr>`).join("") || '<tr><td colspan="4">—</td></tr>'}</tbody></table></div>
  </div>`;
}
/* ---------- Fintech Ops: UPI, QR, links, mandates, escrow, KYC, credit, payouts ---------- */
async function vFinOps() {
  const gate = await coGate("finops");
  if (!gate.any) return coOff("fintech", "💸 Fintech Ops", gate.off);
  const upi = (await api("/fintech/upi", {})).upi || [];
  const billers = (await api("/fintech/billers", {})).billers || [];
  const plans = (await api("/fintech/plans", {})).plans || [];
  const [escrowR, kycR, payoutR, loanR, polR] = await Promise.all([
    api("/meta/entity/escrow_hold", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/kyc_profile", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/bank_payout", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/loan", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/payment_link", {}).catch(() => ({ rows: [] })),
  ]);
  const escrows = escrowR.rows || [], kycs = kycR.rows || [], payouts = payoutR.rows || [],
    loans = loanR.rows || [], pols = polR.rows || [];
  return `<div class="a-head"><h2>💸 Fintech Ops</h2>
    <p class="a-sub">The payment rails: UPI collect, QR scan-pay, tokenised links, auto-debit mandates, escrow hold/release, split settlements, KYC-gated credit (BNPL, loans), bank payouts, bills, recharge, P2P, insurance and gift vouchers. Money never leaves the single wallet ledger. Statuses, kinds and frequencies are registries: <code>finUpiStatuses</code>, <code>finLinkStatuses</code>, <code>finEscrowStatuses</code>.</p>
    <p class="a-sub"><b>On for this store:</b> ${gate.on.map(k => `<span class="a-chip">${esc(k)}</span>`).join(" ")}${gate.off.length ? ` <span class="p-tag">${esc(gate.off.length)} off</span>` : ""}</p></div>
  <div class="a-card"><h3>Escrow holds · ${escrows.length}</h3>
    <p class="a-sub">${coChips(escrows, e => e.status)}</p>
    ${coTbl(["escrow", "order", "buyer", "seller", "held", "status"], escrows,
      e => [`<code>${esc(e.ref)}</code>`, e.order_id || "—", esc(e.buyer), esc(e.seller), money(e.amount), coBadge(e.status)])}
    ${hasCap(gate, "escrow") ? `<div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap"><label><span>Order id</span><input id="finEscOrder" placeholder="101"></label>
      <label><span>Seller</span><input id="finEscSeller" placeholder="s:acme"></label><label><span>Amount</span><input id="finEscAmt" type="number" step="0.01" placeholder="50.00"></label>
      <button class="p-btn sm primary" id="finEscGo">Hold in escrow</button></div>` : ""}</div>
  <div class="a-card"><h3>KYC profiles · ${kycs.length}</h3>
    <p class="a-sub">${coChips(kycs, k => k.status)}</p>
    ${coTbl(["owner", "kind", "name", "company", "docs", "status"], kycs,
      k => [esc(k.owner), esc(k.kind), esc(k.full_name || "—"), esc(k.company || "—"), esc(k.doc_status || "—"), coBadge(k.status)])}
    ${hasCap(gate, "kyc") ? `<button class="p-btn sm primary" data-act="co-new" data-key="kyc_profile">+ Submit KYC</button>` : ""}</div>
  <div class="a-cap" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px">
    <div class="a-card"><h3>Payment links · ${pols.length}</h3>
      ${coTbl(["link", "title", "amount", "status"], pols, p => [`<code>${esc(p.ref)}</code>`, esc(p.title), money(p.amount), coBadge(p.status)], "No links issued.")}</div>
    <div class="a-card"><h3>Bank payouts · ${payouts.length}</h3>
      ${coTbl(["payout", "payee", "amount", "status"], payouts, p => [`<code>${esc(p.ref)}</code>`, esc(p.payee), money(p.amount), coBadge(p.status)], "No payouts queued.")}
      ${hasCap(gate, "bank_payouts") ? `<button class="p-btn sm primary" data-act="co-new" data-key="bank_payout">+ Queue payout</button>` : ""}</div>
    <div class="a-card"><h3>Loans · ${loans.length}</h3>
      ${coTbl(["loan", "owner", "principal", "emi", "status"], loans, l => [`<code>${esc(l.ref)}</code>`, esc(l.owner), money(l.principal), l.emi ? money(l.emi) : "—", coBadge(l.status)], "No credit issued.")}</div>
  </div>
  <div class="a-card"><h3>UPI handles · ${upi.length}</h3>
    ${coTbl(["owner", "vpa", "verified", "default", "status"], upi,
      u => [esc(u.owner), `<code>${esc(u.vpa)}</code>`, u.verified ? "✓" : "—", u.is_default ? "✓" : "—", coBadge(u.status)], "No VPA saved.")}</div>
  <div class="a-card"><h3>Billers · ${billers.length} · recharge plans · ${plans.length}</h3>
    <p class="a-sub">${(billers.slice(0, 12)).map(b => `<span class="a-chip">${esc(b.category)}·${esc(b.name)}</span>`).join(" ") || "no billers registered"}</p>
    <p class="a-sub">${plans.slice(0, 12).map(p => `<span class="a-chip">${esc(p.operator)}·${money(p.amount)}/${esc(p.validity || "")}</span>`).join(" ") || "no plans registered"}</p></div>`;
}
function wireFinOps() {
  const g = $("#finEscGo"); if (g) g.onclick = async () => {
    try {
      const r = await api("/fintech/escrow", "POST", { order_id: Number($("#finEscOrder").value), seller: $("#finEscSeller").value, amount: Number($("#finEscAmt").value) });
      toast("Escrow " + (r.escrow && r.escrow.ref)); render();
    } catch (e) { toast(e.message); }
  };
}

screen("settlements", { group: "Payments & Finance", label: "🤝 Settlements", order: 2, render: async () => await entityTable("settlement") });
screen("finance", { group: "Payments & Finance", label: "💰 Disputes & Payouts", order: 3, render: async () => await vFinance() });
screen("finops", { group: "Business Operations", label: "💸 Fintech Ops", order: 3, render: async () => await vFinOps(), wire: async () => { wireFinOps(); } });

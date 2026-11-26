/* LUXORA Platform — the trade domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ---------- Trade Ops: assurance, gold suppliers, verification, LCs, RFQs ---------- */
async function vTradeOps() {
  const gate = await coGate("tradeops");
  if (!gate.any) return coOff("B2B trade", "🤝 Trade Ops", gate.off);
  const [ta, gold, ver, lc, quo, pl, doc] = await Promise.all([
    api("/meta/entity/trade_assurance", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/gold_supplier", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/company_verification", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/letter_of_credit", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/rfq_quote", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/price_list", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/export_document", {}).catch(() => ({ rows: [] })),
  ]);
  const tas = ta.rows || [], golds = gold.rows || [], vers = ver.rows || [], lcs = lc.rows || [],
    quos = quo.rows || [], pls = pl.rows || [], docs = doc.rows || [];
  return `<div class="a-head"><h2>🤝 Trade Ops</h2>
    <p class="a-sub">B2B trust and trade: order-level escrow with milestones, paid supplier memberships, company-verification audits, export/customs documents generated from an order's own fields, letters of credit, multi-seller RFQ bidding ranked by price then lead time, sealed-bid tender reverse auctions and per-segment price lists with MOQ enforcement.</p>
    <p class="a-sub"><b>On for this store:</b> ${gate.on.map(k => `<span class="a-chip">${esc(k)}</span>`).join(" ")}${gate.off.length ? ` <span class="p-tag">${esc(gate.off.length)} off</span>` : ""}</p></div>
  <div class="a-card"><h3>Trade assurance · ${tas.length}</h3>
    <p class="a-sub">${coChips(tas, t => t.status)}</p>
    ${coTbl(["ref", "order", "buyer", "seller", "amount", "milestone", "status"], tas,
      t => [`<code>${esc(t.ref)}</code>`, t.order_id || "—", esc(t.buyer), esc(t.seller), money(t.amount), esc(t.current_milestone || "—"), coBadge(t.status)])}
    ${hasCap(gate, "trade_assurance") ? `<div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap"><label><span>Order id</span><input id="trAsOrder" placeholder="101"></label>
      <label><span>Seller</span><input id="trAsSeller" placeholder="s:acme"></label><label><span>Amount</span><input id="trAsAmt" type="number" step="0.01" placeholder="500.00"></label>
      <button class="p-btn sm primary" id="trAsGo">Create assurance</button></div>` : ""}</div>
  <div class="a-cap" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px">
    <div class="a-card"><h3>Gold suppliers · ${golds.length}</h3>
      ${coTbl(["supplier", "tier", "verified", "status"], golds, g => [esc(String(g.supplier_id)), coBadge(g.tier), g.verified ? "✓" : "—", coBadge(g.status)], "No memberships.")}
      ${hasCap(gate, "gold_supplier") ? `<button class="p-btn sm primary" data-act="co-new" data-key="gold_supplier">+ Enrol supplier</button>` : ""}</div>
    <div class="a-card"><h3>Company verification · ${vers.length}</h3>
      ${coTbl(["company", "country", "audit", "status"], vers, v => [esc(v.company_name), esc(v.country || "—"), esc(v.audit_by || "—"), coBadge(v.verification_status)], "No audits filed.")}
      ${hasCap(gate, "company_verification") ? `<button class="p-btn sm primary" data-act="co-new" data-key="company_verification">+ Submit audit</button>` : ""}</div>
    <div class="a-card"><h3>Letters of credit · ${lcs.length}</h3>
      ${coTbl(["ref", "buyer", "seller", "amount", "status"], lcs, l => [`<code>${esc(l.lc_number || l.ref)}</code>`, esc(l.buyer), esc(l.seller), money(l.amount), coBadge(l.status)], "No LCs issued.")}</div>
    <div class="a-card"><h3>RFQ quotes · ${quos.length}</h3>
      ${coTbl(["rfq", "supplier", "unit price", "MOQ", "lead", "rank", "status"], quos,
        q => [esc(String(q.rfq_id)), esc(String(q.supplier_id)), money(q.unit_price), q.moq || "—", q.lead_days || "—", q.rank || "—", coBadge(q.status)], "No quotes yet.")}</div>
    <div class="a-card"><h3>Price lists · ${pls.length}</h3>
      ${coTbl(["name", "segment", "status"], pls, p => [esc(p.name), esc(p.segment || "—"), coBadge(p.status)], "No price lists.")}</div>
    <div class="a-card"><h3>Export documents · ${docs.length}</h3>
      ${coTbl(["ref", "kind", "dest", "value", "status"], docs,
        d => [`<code>${esc(d.ref)}</code>`, esc(d.doc_kind), esc(d.dest_country || "—"), d.total_value ? money(d.total_value) : "—", coBadge(d.status)], "No documents generated.")}</div>
  </div>`;
}
function wireTradeOps() {
  const g = $("#trAsGo"); if (g) g.onclick = async () => {
    try {
      const r = await api("/trade/assurance", "POST", { order_id: Number($("#trAsOrder").value), seller: $("#trAsSeller").value, amount: Number($("#trAsAmt").value) });
      toast("Assurance " + (r.assurance && r.assurance.ref)); render();
    } catch (e) { toast(e.message); }
  };
}
async function vContracts() {
  const rows = (await api("/meta/entity/contract")).rows || [];
  return `<div class="p-panel"><div style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:14px">
    <label><span>Buyer name</span><input id="ncName" placeholder="Acme Corp"></label>
    <label><span>Buyer email</span><input id="ncEmail" placeholder="buy@acme.example"></label>
    <label><span>Product ids (CSV)</span><input id="ncProducts" placeholder="VR-HARD-01"></label>
    <label><span>Fixed unit price</span><input id="ncPrice" type="number" step="0.01" placeholder="10.00"></label>
    <label><span>Min qty</span><input id="ncMin" type="number" value="10"></label>
    <button class="p-btn primary sm" id="ncGo">+ New contract</button></div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Ref</th><th>Buyer</th><th>Products</th><th>Price</th><th>Min</th><th>Valid</th><th>Status</th><th></th></tr></thead>
    <tbody>${rows.map(c => { const pr = pj(c.pricing, "{}") || {}, pid = pj(c.product_ids, "[]") || []; const fp = pr.fixed ? Object.values(pr.fixed)[0] : (Array.isArray(pr.tiers) && pr.tiers[0] ? pr.tiers[0].price : null); return `<tr><td><b>${esc(c.ref)}</b></td><td>${esc(c.buyer_name)}<br><span class="p-tag">${esc(c.buyer_email)}</span></td><td>${esc((pid).join(", "))}</td><td>${fp != null ? money(fp) : "—"}</td><td>${esc(c.min_qty)}</td><td>${esc(c.valid_from || "")}→${esc(c.valid_to || "")}</td><td><span class="badge ${esc(c.status)}">${esc(c.status)}</span></td><td style="white-space:nowrap;text-align:right">${c.status !== "active" ? `<button class="p-btn sm" data-cstat="${c.id}" data-v="active">Activate</button>` : ""}${c.status === "active" ? `<button class="p-btn sm" data-cstat="${c.id}" data-v="expired">Expire</button> <button class="p-btn sm danger" data-cstat="${c.id}" data-v="terminated">Terminate</button>` : ""} <button class="p-btn sm" data-cedit="${c.id}" data-id="${esc(c.id)}">Edit</button> <button class="p-btn sm danger" data-cdel="${c.id}">✕</button></td></tr>`; }).join("")}</tbody></table></div></div>`;
}
function wireContracts() {
  $$("[data-cstat]").forEach(b => b.onclick = async () => { try { await api(`/admin/contracts/${b.dataset.cstat}/status`, "PUT", { status: b.dataset.v }); toast("Contract " + b.dataset.v); render(); } catch (e) { toast(e.message); } });
  $$("[data-cedit]").forEach(b => b.onclick = () => openForm("contract", b.dataset.id, render));
  $$("[data-cdel]").forEach(b => b.onclick = async () => { if (!confirm("Delete contract?")) return; try { await api(`/meta/entity/contract/${b.dataset.cdel}`, "DELETE"); toast("Deleted"); render(); } catch (e) { toast(e.message); } });
  const g = $("#ncGo"); if (g) g.onclick = async () => {
    const ids = $("#ncProducts").value.split(",").map(x => x.trim()).filter(Boolean), pv = Number($("#ncPrice").value), pricing = {}; if (ids.length && pv) { pricing.fixed = {}; ids.forEach(id => pricing.fixed[id] = pv); }
    try { const r = await api("/admin/contracts", "POST", { buyer_name: $("#ncName").value, buyer_email: $("#ncEmail").value, product_ids: ids, pricing, min_qty: Number($("#ncMin").value) || 1 }); toast("Contract " + r.ref); render(); } catch (e) { toast(e.message); }
  };
}
async function vTenders() {
  const rows = (await api("/meta/entity/tender")).rows || [];
  return `<div class="p-panel"><div style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:14px">
    <label><span>Title</span><input id="ntTitle" placeholder="Annual fastener supply"></label>
    <label><span>Issuing org</span><input id="ntOrg" placeholder="BuildRight LLC"></label>
    <label><span>Budget</span><input id="ntBudget" type="number" step="1" placeholder="120000"></label>
    <button class="p-btn primary sm" id="ntGo">+ New tender</button></div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Ref</th><th>Title</th><th>Org</th><th>Budget</th><th>Closes</th><th>Status</th><th></th></tr></thead>
    <tbody>${rows.map(t => `<tr><td><b>${esc(t.ref)}</b></td><td>${esc(t.title)}</td><td>${esc(t.buyer_org)}</td><td>${t.budget ? money(t.budget) : "—"}</td><td>${esc(t.close_at || "")}</td><td><span class="badge ${esc(t.status)}">${esc(t.status)}</span>${t.awarded_contract_id ? ` <span class="p-tag">→ contract #${esc(t.awarded_contract_id)}</span>` : ""}</td><td style="white-space:nowrap;text-align:right">${(t.status === "open" || t.status === "in_review") ? `<button class="p-btn sm primary" data-taward="${t.id}">Award → contract</button>` : ""} <button class="p-btn sm danger" data-tdel="${t.id}">✕</button></td></tr>`).join("")}</tbody></table></div></div>`;
}
function wireTenders() {
  $$("[data-taward]").forEach(b => b.onclick = async () => { try { const r = await api(`/admin/tenders/${b.dataset.taward}/award`, "POST", {}); toast("Awarded → " + r.contract_ref); render(); } catch (e) { toast(e.message); } });
  $$("[data-tdel]").forEach(b => b.onclick = async () => { if (!confirm("Delete tender?")) return; try { await api(`/meta/entity/tender/${b.dataset.tdel}`, "DELETE"); toast("Deleted"); render(); } catch (e) { toast(e.message); } });
  const g = $("#ntGo"); if (g) g.onclick = async () => { try { const r = await api("/admin/tenders", "POST", { title: $("#ntTitle").value, buyer_org: $("#ntOrg").value, budget: Number($("#ntBudget").value) || 0 }); toast("Tender " + r.ref); render(); } catch (e) { toast(e.message); } };
}

screen("rfqs", { render: async () => await entityTable("rfq") });
screen("contracts", { render: async () => await vContracts(), wire: async () => { wireContracts(); } });
screen("tenders", { render: async () => await vTenders(), wire: async () => { wireTenders(); } });
screen("tradeops", { render: async () => await vTradeOps(), wire: async () => { wireTradeOps(); } });

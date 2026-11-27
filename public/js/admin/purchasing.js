/* LUXORA Platform — the purchasing domain's store-console screen (lib/purchasing.js; _registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope. Purchase orders and their
   lines, goods received, suppliers' bills and what is owed — every figure from /api/admin/purchasing. */
"use strict";

let puOpen = null;
async function vPurchasing() {
  const [po, bl, ap, sup, wh] = await Promise.all([api("/admin/purchasing/orders"), api("/admin/purchasing/bills"), api("/admin/purchasing/payables"),
    api("/meta/entity/supplier").catch(() => ({ rows: [] })), api("/admin/warehouses").catch(() => ({ warehouses: [] }))]);
  const one = puOpen ? (await api("/admin/purchasing/orders/" + puOpen).catch(() => null)) : null, o = one && one.order;
  const supOpts = (sup.rows || []).map(x => `<option value="${x.id}">${esc(x.name)} · ${esc(x.currency || "")}</option>`).join("");
  const whOpts = (wh.warehouses || []).map(w => `<option value="${w.id}">${esc(w.name)}</option>`).join("");
  const detail = o ? `<div class="a-card"><h3>${esc(o.ref)} · ${esc(o.supplier)} · ${coBadge(o.status)}</h3>
    <p class="a-sub">${money(o.total)} ${esc(o.currency)} ordered · ${money(o.unbilled)} received and not yet billed</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>Item</th><th>Ordered</th><th>Received</th><th>Unit cost</th><th>Receive now</th></tr></thead><tbody>
    ${o.lines.map(l => `<tr><td><code>${esc(l.product_id)}</code></td><td>${l.qty}</td><td>${l.received}</td><td>${money(l.unit_cost)}</td>
      <td>${l.outstanding > 0 ? `<input type="number" min="0" max="${l.outstanding}" value="${l.outstanding}" data-pu-line="${l.id}" style="width:80px">` : "—"}</td></tr>`).join("")}</tbody></table></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
      ${o.actions.includes("send") ? `<button class="p-btn sm primary" data-pu-act="send">Send to supplier</button>` : ""}
      ${o.actions.includes("cancel") ? `<button class="p-btn sm" data-pu-act="cancel">Cancel</button>` : ""}
      ${o.actions.includes("receive") ? `<label><span>Arrived at</span><select id="puWh">${whOpts}</select></label><label><span>Lot</span><input id="puLot" maxlength="60"></label><label><span>Expiry</span><input id="puExp" type="date"></label><button class="p-btn sm primary" data-pu-act="receive">Record goods received</button>` : ""}
      ${o.actions.includes("close") ? `<button class="p-btn sm" data-pu-act="close">Close</button>` : ""}</div>
    ${o.actions.includes("bill") ? `<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px"><label><span>Supplier's invoice no.</span><input id="puRef" maxlength="60"></label>
      <label><span>Net</span><input id="puNet" type="number" step="0.01" value="${o.unbilled}"></label><label><span>Tax</span><input id="puTax" type="number" step="0.01" value="0"></label>
      <button class="p-btn sm primary" data-pu-act="bill">Record the bill</button></div>` : ""}</div>` : "";
  return `<div class="a-head"><h2>🧾 Purchasing</h2>
    <p class="a-sub">Order from suppliers, receive goods into a warehouse batch, and match each supplier's bill to what arrived. Stock, what is owed and the books follow by themselves.</p></div>
  <div class="a-card"><h3>New purchase order</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px">
      <label><span>Supplier</span><select id="puSup">${supOpts}</select></label><label><span>Deliver to</span><select id="puWhNew">${whOpts}</select></label>
      <label><span>Item (product id)</span><input id="puItem"></label><label><span>Quantity</span><input id="puQty" type="number" min="1" value="1"></label>
      <label><span>Unit cost</span><input id="puCost" type="number" step="0.01" min="0"></label></div>
    <button class="p-btn sm primary" id="puCreate" style="margin-top:8px">Draft the order</button></div>
  ${detail}
  <div class="a-card"><h3>Purchase orders</h3>
    ${coTbl(["order", "supplier", "total", "status", ""], po.orders, x => [`<code>${esc(x.ref)}</code>`, esc(x.supplier), `${money(x.total)} ${esc(x.currency)}`, coBadge(x.status), `<button class="p-btn sm" data-pu-open="${x.id}">Open</button>`], "No purchase orders yet.")}</div>
  <div class="a-card"><h3>Supplier bills</h3>
    ${coTbl(["bill", "supplier", "their no.", "gross", "due", "status", ""], bl.bills, b => [`<code>${esc(b.ref)}</code>`, esc(b.supplier), esc(b.supplier_ref), `${money(b.gross)} ${esc(b.currency)}`, esc(b.due_at || "—"),
      coBadge(b.status) + (b.hold_reason && b.actions.includes("release") ? `<div class="a-sub">${esc(b.hold_reason)}</div>` : ""),
      [["release", "Release", ""], ["pay", "Mark paid", " primary"], ["void", "Void", ""]].filter(([a]) => b.actions.includes(a)).map(([a, l, c]) => `<button class="p-btn sm${c}" data-pu-bill="${a}" data-id="${b.id}">${l}</button>`).join(" ")], "No bills yet.")}</div>
  <div class="a-card"><h3>Owed to suppliers</h3>
    ${coTbl(["supplier", "current", "1–30 days late", "31–60", "over 60", "total"], ap.payables, x => [esc(x.supplier), money(x.current), money(x.d1_30), money(x.d31_60), money(x.d60plus), `${money(x.total)} ${esc(x.currency)}`], "Nothing is owed.")}</div>`;
}
function wirePurchasing() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  document.querySelectorAll("[data-pu-open]").forEach(b => b.onclick = () => { puOpen = b.dataset.puOpen; render(); });
  const c = $("#puCreate"); if (c) c.onclick = () => go(async () => {
    const r = await api("/admin/purchasing/orders", "POST", { supplier_id: Number($("#puSup").value), warehouse_id: Number($("#puWhNew").value) || null, lines: [{ product_id: $("#puItem").value.trim(), qty: Number($("#puQty").value), unit_cost: Number($("#puCost").value) }] });
    puOpen = r.order.id;
  }, "Order drafted");
  document.querySelectorAll("[data-pu-act]").forEach(b => b.onclick = () => go(async () => {
    const a = b.dataset.puAct, base = "/admin/purchasing/orders/" + puOpen;
    if (a === "receive") await api(base + "/receive", "POST", { warehouse_id: Number($("#puWh").value), lines: [...document.querySelectorAll("[data-pu-line]")].map(i => ({ line_id: Number(i.dataset.puLine), qty: Number(i.value), lot: $("#puLot").value, expiry: $("#puExp").value })) });
    else if (a === "bill") await api("/admin/purchasing/bills", "POST", { po_id: Number(puOpen), supplier_ref: $("#puRef").value, net: Number($("#puNet").value), tax: Number($("#puTax").value) });
    else await api(base + "/" + a, "POST", {});
  }, "Done"));
  document.querySelectorAll("[data-pu-bill]").forEach(b => b.onclick = () => go(async () => {
    const a = b.dataset.puBill, body = {};
    if (a === "release") { body.reason = prompt("Why is this bill approved despite the difference?"); if (!body.reason) return; }
    await api("/admin/purchasing/bills/" + b.dataset.id + "/" + a, "POST", body);
  }, "Done"));
}
screen("purchasing", { render: async () => await vPurchasing(), wire: wirePurchasing });

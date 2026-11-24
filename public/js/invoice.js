/* LUXORA Platform — an order's invoice and credit notes, to read, print or save as PDF. */
"use strict";
(async () => {
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const q = new URLSearchParams(location.search), page = document.getElementById("page");
  const path = q.get("staff") ? "/api/admin/orders/" : "/api/orders/";
  const r = await fetch(path + encodeURIComponent(q.get("order") || "") + "/invoice", { credentials: "same-origin" });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) { page.innerHTML = `<p role="alert">${esc(d.error || "The invoice could not be opened")}</p><p><a href="orders.html">Back to your orders</a></p>`; return; }
  const doc = x => {
    const m = n => { try { return new Intl.NumberFormat(undefined, { style: "currency", currency: x.currency }).format(n); } catch (e) { return Number(n).toFixed(x.decimals) + " " + x.currency; } };
    const row = (a, b, strong) => `<tr><td colspan="5" style="text-align:right">${strong ? "<b>" + a + "</b>" : a}</td><td style="text-align:right">${strong ? "<b>" + b + "</b>" : b}</td></tr>`;
    return `<section style="border:1px solid #d4d4d8;border-radius:8px;padding:24px;margin-bottom:24px;break-inside:avoid">
      <div style="display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap"><div><h1 style="margin:0">${esc(x.title)}</h1><p>No. <b>${esc(x.number)}</b><br>Date ${esc(String(x.issued).slice(0, 10))}<br>Order ${esc(x.order)}${x.against ? "<br>Against invoice " + esc(x.against) : ""}</p></div>
      <div style="text-align:right"><b>${esc(x.seller.name)}</b><br>${esc(x.seller.address)}${x.seller.state ? "<br>" + esc(x.seller.state) : ""}${x.seller.taxId ? `<br>${esc(x.numberLabel)}: ${esc(x.seller.taxId)}` : ""}</div></div>
      <p><b>Billed to</b><br>${esc(x.buyer.name)}<br>${esc(x.buyer.address)}${x.buyer.taxId ? `<br>${esc(x.numberLabel)}: ${esc(x.buyer.taxId)}` : ""}${x.placeOfSupply ? "<br>Place of supply: " + esc(x.placeOfSupply) : ""}</p>
      <div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse" cellpadding="6"><thead><tr style="text-align:left;border-bottom:1px solid #d4d4d8"><th>Item</th><th>${esc(x.codeLabel || "")}</th><th>Qty</th><th style="text-align:right">Taxable</th><th style="text-align:right">Tax</th><th style="text-align:right">Total</th></tr></thead>
      <tbody>${x.lines.map(l => `<tr><td>${esc(l.description)}</td><td>${esc(l.code)}</td><td>${esc(l.qty)}</td><td style="text-align:right">${m(l.taxable)}</td><td style="text-align:right">${m(l.tax)}${l.rate !== "" ? ` <small>(${esc(l.rate)}%)</small>` : ""}</td><td style="text-align:right">${m(l.total)}</td></tr>`).join("")}</tbody>
      <tfoot>${row("Taxable value", m(x.taxable))}${x.taxes.map(t => row(esc(t.name), m(t.amount))).join("")}${row("Total", m(x.total), true)}${x.fromBalance > 0 ? row("Paid from balance", m(x.fromBalance)) : ""}</tfoot></table></div></section>`;
  };
  document.title = d.invoice.title + " " + d.invoice.number;
  page.innerHTML = `<p class="no-print"><button id="print">Print or save as PDF</button></p>` + [d.invoice].concat(d.credits || []).map(doc).join("");
  document.getElementById("print").onclick = () => window.print();
})();

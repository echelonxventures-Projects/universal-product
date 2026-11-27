/* LUXORA Platform — a proposal a store sent, read and answered from the client's private link
   (lib/consulting.js publicView, answerByClient). Accepting needs the client's name; the answer is final. */
"use strict";
(async () => {
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const token = new URLSearchParams(location.search).get("t") || "", page = document.getElementById("page");
  const csrf = () => { const m = /(?:^|; )azc=([^;]+)/.exec(document.cookie || ""); return m ? m[1] : ""; };
  const show = p => {
    const m = n => { try { return new Intl.NumberFormat(undefined, { style: "currency", currency: p.currency }).format(n); } catch (e) { return Number(n).toFixed(2) + " " + p.currency; } };
    const state = p.answerable ? `<p>Valid until <b>${esc(p.valid_until)}</b>.</p>`
      : p.accepted ? `<p role="status"><b>Accepted</b> on ${esc(String(p.answered_at || "").slice(0, 10))}. ${esc(p.store)} will be in touch to start.</p>`
      : `<p role="status"><b>${esc(p.endNote || "This proposal is no longer open.")}</b> Ask ${esc(p.store)} for a new one if you still need it.</p>`;
    document.title = p.title + " — " + p.store;
    page.innerHTML = `<section style="border:1px solid #d4d4d8;border-radius:8px;padding:24px">
      <p style="margin:0;color:#52525b">${esc(p.store)} · ${esc(p.ref)}</p><h1 style="margin:4px 0 8px">${esc(p.title)}</h1>
      ${p.company ? `<p>For <b>${esc(p.company)}</b> · ${esc(p.billing)}</p>` : `<p>${esc(p.billing)}</p>`}
      ${p.intro ? `<p style="white-space:pre-wrap">${esc(p.intro)}</p>` : ""}
      <div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse" cellpadding="6"><thead><tr style="text-align:left;border-bottom:1px solid #d4d4d8"><th>What</th><th></th><th style="text-align:right">Qty</th><th style="text-align:right">Rate</th><th style="text-align:right">Amount</th></tr></thead>
      <tbody>${p.lines.map(l => `<tr><td>${esc(l.description)}</td><td>${esc(l.kind)}</td><td style="text-align:right">${esc(l.qty)}</td><td style="text-align:right">${m(l.rate)}</td><td style="text-align:right">${m(l.amount)}</td></tr>`).join("")}</tbody>
      <tfoot><tr><td colspan="4" style="text-align:right">Subtotal</td><td style="text-align:right">${m(p.net)}</td></tr><tr><td colspan="4" style="text-align:right">Tax (${esc(p.tax_pct)}%)</td><td style="text-align:right">${m(p.tax)}</td></tr>
      <tr><td colspan="4" style="text-align:right"><b>Total</b></td><td style="text-align:right"><b>${m(p.total)}</b></td></tr></tfoot></table></div>
      ${state}</section>
      ${p.answerable ? `<section style="margin-top:24px;display:grid;gap:16px">
        <form id="yes" style="display:grid;gap:8px"><label for="nm"><b>Accept</b> — type your full name</label><input id="nm" autocomplete="name" maxlength="120" required><button type="submit">Accept this proposal</button></form>
        <form id="no" style="display:grid;gap:8px"><label for="why"><b>Decline</b> — tell us why (optional)</label><input id="why" maxlength="500"><button type="submit">Decline</button></form>
        <p id="msg" role="alert"></p></section>` : ""}`;
    const send = async (accept, extra) => {
      const r = await fetch("/api/proposals/answer", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "x-csrf": csrf() }, body: JSON.stringify({ t: token, accept, ...extra }) });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) { document.getElementById("msg").textContent = d.error || "Your answer could not be sent. Try again."; return; }
      show(d.proposal);
    };
    const y = document.getElementById("yes"), n = document.getElementById("no");
    if (y) y.onsubmit = e => { e.preventDefault(); send(true, { name: document.getElementById("nm").value }); };
    if (n) n.onsubmit = e => { e.preventDefault(); if (confirm("Decline this proposal?")) send(false, { reason: document.getElementById("why").value }); };
  };
  const r = await fetch("/api/proposals/view?t=" + encodeURIComponent(token), { credentials: "same-origin" });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) { page.innerHTML = `<h1>This link is not valid</h1><p>It may have been copied incompletely. Ask whoever sent it for a new one.</p>`; return; }
  show(d.proposal);
})();

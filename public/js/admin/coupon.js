/* LUXORA Platform — the coupon domain's store-console screens
   (_registry/business-domains.json). Loaded after the console shell (public/js/admin.js) in its
   scope; each screen registers its render, its wiring and its place in the nav.

   A coupon is a code a shopper types at the cart. This screen issues one, generates a batch,
   voids one, and shows what every code was worth — the redemption ledger and the performance
   that comes off it. The kinds are the coupon domain's own rows (lib/coupons.js). */
"use strict";

async function vCoupons() {
  const meta = await api("/meta");
  const [cp, an] = await Promise.all([api("/offers/coupons"), api("/offers/analytics")]);
  const funders = meta.offerFunders || [], cKinds = meta.couponKinds || [];
  const opt = (arr, lblFn) => arr.map(x => `<option value="${esc(x.key || x)}">${esc(lblFn ? lblFn(x) : (x.name || x))}</option>`).join("");
  const statusBadge = st => `<span class="badge ${st === "active" ? "published" : "draft"}">${esc(st)}</span>`;
  return `<div class="p-panel"><h2>🎟️ Coupons</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 10px">A code a shopper types at the cart. A coupon is issued by staff or in a batch, validated against its kind and its limits, redeemed into the redemption ledger, and voided when the order is refunded — the code's use is taken back with the discount.</p>
    <div class="p-panel"><h3>Issue a coupon</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end">
        <label><span>Kind</span><select id="cKind">${opt(cKinds)}</select></label>
        <label><span>Code</span><input id="cCode" placeholder="auto if blank"></label>
        <label><span>Value</span><input id="cVal" type="number" step="0.01"></label>
        <label><span>Funder</span><select id="cFunder">${opt(funders)}</select></label>
        <label><span>Funder ref</span><input id="cFunderRef" placeholder="e.g. HDFC"></label>
        <label><span>Max uses</span><input id="cMax" type="number" value="1"></label>
        <label><span>Per owner</span><input id="cOwner" type="number" value="1"></label>
        <button class="p-btn primary sm" id="cCreate">+ Coupon</button>
        <button class="p-btn sm" id="cGen">Generate 10 codes</button>
      </div>
      <div class="p-scroll-x" style="margin-top:10px"><table class="p-table"><thead><tr><th>Code</th><th>Kind</th><th>Funder</th><th class="num">Value</th><th class="num">Used/Max</th><th>Status</th><th></th></tr></thead><tbody>
        ${(cp.coupons || []).map(c => `<tr><td><code>${esc(c.code)}</code>${c.tenant_id === 0 ? ' <span class="p-tag">GLOBAL</span>' : ""}</td><td>${esc(c.kind)}</td><td>${esc(c.funder)}${c.funder_ref ? " " + esc(c.funder_ref) : ""}</td><td class="num">${esc(c.value)}</td><td class="num">${c.used}/${c.max_uses}</td><td>${statusBadge(c.status)}</td><td style="text-align:right"><button class="p-btn sm danger" data-cvoid="${c.id}">Void</button></td></tr>`).join("") || '<tr><td colspan="7">No coupons.</td></tr>'}
      </tbody></table></div>
      <h3>Redemption performance</h3>
      <div class="p-cards" style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px">
        <div class="p-stat"><b>${(an.totals && an.totals.redemptions) || 0}</b> redemptions</div>
        <div class="p-stat"><b>${money(an.totals && an.totals.discount || 0)}</b> discount given</div>
        <div class="p-stat"><b>${money(an.totals && an.totals.credits || 0)}</b> credits rewarded</div>
      </div>
      ${(an.byCode || []).filter(x => x.k).length ? `<table class="p-table"><thead><tr><th>Top codes</th><th class="num">Times</th><th class="num">Discount</th></tr></thead><tbody>${an.byCode.filter(x => x.k).slice(0, 8).map(x => `<tr><td><code>${esc(x.k)}</code></td><td class="num">${x.n}</td><td class="num">${money(x.discount)}</td></tr>`).join("")}</tbody></table>` : ""}
      ${(an.byFunder || []).length ? `<p class="p-tag">By funder: ${an.byFunder.map(x => `${esc(x.k || "self")}: ${x.n} (${money(x.discount)})`).join(" · ")}</p>` : ""}
      <h3>Recent redemptions</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Code</th><th class="num">Amount</th><th>Funder</th><th>Channel</th><th>Owner</th><th>When</th></tr></thead><tbody>
        ${(cp.redemptions || []).slice(0, 12).map(r => `<tr><td><code>${esc(r.code)}</code></td><td class="num">${money(r.amount)}</td><td>${esc(r.funder)}${r.funder_ref ? " " + esc(r.funder_ref) : ""}</td><td>${esc(r.channel)}</td><td class="p-tag">${esc((r.owner || "").slice(0, 16))}</td><td>${esc((r.created_at || "").slice(0, 16))}</td></tr>`).join("") || '<tr><td colspan="6">No redemptions yet.</td></tr>'}
      </tbody></table></div>
    </div>`;
}
function wireCoupons() {
  const $$ = s => Array.from(document.querySelectorAll(s));
  $("#cCreate").onclick = async () => { try { await api("/offers/coupons", "POST", { kind: $("#cKind").value, code: $("#cCode").value, value: Number($("#cVal").value), funder: $("#cFunder").value, funder_ref: $("#cFunderRef").value, max_uses: Number($("#cMax").value) || 1, per_owner_limit: Number($("#cOwner").value) || 1 }); toast("Coupon created"); render(); } catch (e) { toast(e.message); } };
  $("#cGen").onclick = async () => { try { const r = await api("/offers/coupons/generate", "POST", { count: 10, kind: $("#cKind").value, funder: $("#cFunder").value, funder_ref: $("#cFunderRef").value, value: Number($("#cVal").value), per_owner_limit: Number($("#cOwner").value) || 1 }); toast(r.count + " codes (" + r.batch + ")"); render(); } catch (e) { toast(e.message); } };
  $$("[data-cvoid]").forEach(b => b.onclick = async () => { try { await api("/offers/coupons/" + b.dataset.cvoid, "DELETE"); toast("Voided"); render(); } catch (e) { toast(e.message); } });
}

screen("coupons", { render: vCoupons, wire: wireCoupons });

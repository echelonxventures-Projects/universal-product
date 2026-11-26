/* LUXORA Platform — the wallet domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vWallets() {
  const v = await api("/admin/ledger/verify", {}).catch(e => ({ error: e.message }));
  const defs = await api("/wallet-definitions", {}).catch(() => ({ definitions: [] }));
  const d = walOwner ? await api("/admin/wallets?owner=" + encodeURIComponent(walOwner), {}).catch(e => ({ error: e.message, wallets: [] })) : { wallets: [] };
  const one = walOpen ? await api("/admin/wallets/" + encodeURIComponent(walOpen), {}).catch(e => ({ error: e.message })) : null;
  const acts = d.walletActions || [];
  return `<div class="a-head"><h2>👛 Wallets & Ledger</h2><p class="a-sub">Every wallet an owner holds — named as they like, each in one unit of value, bound to a versioned definition. Value moves only as balanced journals that cannot be edited; corrections are linked reversals. A wallet's balance is its postings, less what its holds keep.</p></div>
  <div class="a-card"><h3>Ledger check</h3>${v.error ? `<p class="a-sub">${esc(v.error)}</p>` : `<p>${v.journals} journals · ${v.unbalanced.length ? `<b>${v.unbalanced.length} unbalanced</b>` : "every one balances"} · event chain ${v.chain && v.chain.ok ? "intact" : "<b>broken at " + esc(String((v.chain || {}).brokenAt)) + "</b>"}</p>`}</div>
  <div class="a-card"><h3>Definitions</h3><p class="a-sub">Each refines the one above it and states only what differs; every value shown is resolved for this store — its own settings over the platform's. ★ is the store's default.</p>
  <div class="a-tablewrap"><table class="a-table"><thead><tr><th>definition</th><th>refines</th><th>name</th><th>holds</th><th>allows</th><th>policy</th><th></th></tr></thead><tbody>
  ${(defs.definitions || []).map(x => `<tr><td><code>${esc(x.key)}</code>${x.spec.default ? " ★" : ""}${x.spec.openable ? "" : ' <span class="a-chip">not opened directly</span>'}</td><td>${x.parent ? `<code>${esc(x.parent)}</code>` : "—"}</td><td>${esc(Object.values(x.spec.name || {})[0] || "")}</td><td>${esc(x.spec.classes.join(", ") || "—")}</td><td>${esc(x.spec.operations.join(", ") || "—")}</td><td>${esc(Object.entries(x.spec.policy || {}).filter(([, n]) => n).map(([k, n]) => k.replace(/_/g, " ") + " " + n).join(" · ") || "—")}</td>
    <td style="white-space:nowrap">${x.spec.openable && !x.spec.default ? `<button class="btn-white sm" data-co-post="/admin/wallet-default" data-co-body='${esc(JSON.stringify({ key: x.key }))}'>Make default</button>` : ""} <button class="btn-white sm" data-wal-conf="${esc(x.key)}">Configure</button></td></tr>`).join("")}</tbody></table></div></div>
  <div class="a-card"><h3>An owner's wallets</h3><div class="p-form"><div class="row"><label><span>Owner</span><input id="walOwner" value="${esc(walOwner)}" placeholder="t1:u:42"></label></div><button class="p-btn primary" id="walLook">Show</button></div>
  ${d.error ? `<p class="a-sub">${esc(d.error)}</p>` : `<div class="a-tablewrap"><table class="a-table"><thead><tr><th>wallet</th><th>name</th><th>definition</th><th>unit</th><th>posted</th><th>reserved</th><th>available</th><th>state</th><th></th></tr></thead><tbody>
  ${(d.wallets || []).map(w => `<tr><td><code>${esc(w.id)}</code></td><td>${esc(w.name)}</td><td><code>${esc(w.definition.key)}</code></td><td>${esc(w.unit)}</td><td>${w.posted}</td><td>${w.reserved}</td><td>${w.available}</td><td>${stateChip(w.state)}</td>
    <td style="white-space:nowrap"><button class="btn-white sm" data-wal-open="${esc(w.id)}">Statement</button> ${acts.filter(a => a.to !== w.state.key).map(a => `<button class="btn-white sm" data-co-post="/admin/wallets/${encodeURIComponent(w.id)}/move" data-co-body='${esc(JSON.stringify({ action: a.verb }))}' data-co-ask="Why?" data-co-field="reason">${esc(a.label)}</button>`).join(" ")}
      <button class="btn-white sm" data-wal-adjust="${esc(w.id)}">Adjust</button></td></tr>`).join("") || `<tr><td colspan="9">${walOwner ? "This owner holds no wallets." : "Name an owner."}</td></tr>`}</tbody></table></div>`}</div>
  ${one ? (one.error ? `<div class="a-card"><p class="a-sub">${esc(one.error)}</p></div>` : `<div class="a-card"><h3>${esc(one.wallet.name)} · <code>${esc(one.wallet.id)}</code></h3><p class="a-sub">Names over time: ${one.names.map(n => esc(n.name) + (n.alias ? " (alias)" : "") + (n.valid_to ? " — until " + esc(n.valid_to) : " — now")).join("; ")}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>journal</th><th>when</th><th>operation</th><th>ref</th><th>amount</th><th></th></tr></thead><tbody>
    ${one.lines.map(l => `<tr><td>#${l.id}${l.reverses ? " ↩ #" + l.reverses : ""}</td><td>${esc(l.created_at)}</td><td>${esc(l.op_name)}</td><td>${esc(l.ref)}</td><td>${l.amount}</td><td>${l.reverses ? "" : `<button class="btn-white sm" data-co-post="/admin/journals/${l.id}/reverse" data-co-ask="Why reverse it?" data-co-field="reason">Reverse</button>`}</td></tr>`).join("") || '<tr><td colspan="6">No movements.</td></tr>'}</tbody></table></div>
    <h3>Holds</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>#</th><th>purpose</th><th>ref</th><th>amount</th><th>captured</th><th>until</th><th>state</th></tr></thead><tbody>
    ${one.holds.map(h => `<tr><td>${h.id}</td><td>${esc(h.purpose)}</td><td>${esc(h.ref)}</td><td>${h.amount}</td><td>${h.captured}</td><td>${esc(h.expires_at || "")}</td><td>${stateChip(h.state)}</td></tr>`).join("") || '<tr><td colspan="7">No holds.</td></tr>'}</tbody></table></div></div>`) : ""}`;
}
function wireWallets() {
  const b = $("#walLook"); if (b) b.onclick = () => { walOwner = fieldVal("#walOwner").trim(); walOpen = ""; render(); };
  $$("[data-wal-open]").forEach(x => x.onclick = () => { walOpen = x.dataset.walOpen; render(); });
  /* a store's own value for one setting of a definition (JSON: a number, true/false, or a list) */
  $$("[data-wal-conf]").forEach(x => x.onclick = () => {
    const name = prompt("Which setting? (overdraft, max_balance, max_per_owner, hold_minutes, classes, operations, openable)"); if (!name) return;
    const raw = prompt("Its value for this store"); if (raw == null) return;
    let value; try { value = JSON.parse(raw); } catch (e) { value = raw; }
    postAndRender("/admin/wallet-definitions/" + encodeURIComponent(x.dataset.walConf), { settings: { [name.trim()]: value } }, "POST", "Configured for this store");
  });
  $$("[data-wal-adjust]").forEach(x => x.onclick = () => {
    const amount = prompt("Amount (negative takes value out)"); if (amount == null || amount === "") return;
    const reason = prompt("Why?"); if (!reason) return;
    postAndRender("/admin/wallets/" + encodeURIComponent(x.dataset.walAdjust) + "/adjust", { amount, reason, idempotency_key: "adj-" + Date.now() }, "POST", "Adjusted");
  });
  wireCoPosts();
}

screen("wallets", { render: async () => await vWallets(), wire: async () => { wireWallets(); } });

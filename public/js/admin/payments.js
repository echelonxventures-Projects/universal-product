/* LUXORA Platform — the payments domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vPayments() {
  const [g, n] = await Promise.all([api("/admin/gateways"), api("/admin/notifiers")]);
  return `
  <div class="p-panel"><h2>Payment gateways · ${esc(g.country.name)} (${esc(g.country.currency)})</h2>
    <p class="p-tag">Enable gateways available in your country. Secrets are stored server-side and never sent to the browser.</p>
    <table class="p-table"><thead><tr><th></th><th>Gateway</th><th>Methods</th><th>Fee</th><th>Mode</th><th>Enabled</th><th>Primary</th><th></th></tr></thead>
    <tbody>${g.gateways.map(x => `<tr><td class="t-emoji">${x.emoji}</td><td><b>${esc(x.name)}</b><br><span class="p-tag">${esc(x.desc || "")}</span></td>
      <td class="p-tag">${esc((x.methods || []).join(", "))}</td><td>${x.feePct}%${x.feeFixed ? " + " + money(x.feeFixed) : ""}</td>
      <td><select data-gwmode="${x.id}"><option ${x.mode === "sandbox" ? "selected" : ""}>sandbox</option><option ${x.mode === "live" ? "selected" : ""}>live</option></select></td>
      <td><input type="checkbox" data-gwen="${x.id}" ${x.enabled ? "checked" : ""}></td>
      <td><input type="radio" name="gwprimary" data-gwpri="${x.id}" ${x.primary ? "checked" : ""} ${x.enabled ? "" : "disabled"}></td>
      <td><button class="p-btn sm" data-gwtest="${x.id}">Test</button> <button class="p-btn sm" data-gwcfg="${x.id}">Configure</button></td></tr>`).join("")}</tbody></table>
    <div style="margin-top:14px;display:flex;gap:10px"><button class="p-btn primary" id="gwSave">Save gateway config</button></div></div>
  <div class="p-grid2">
    <div class="p-panel"><h2>Shipping carriers</h2><table class="p-table"><thead><tr><th></th><th>Carrier</th><th>ETA</th><th>Base fee</th></tr></thead>
      <tbody>${g.carriers.map(c => `<tr><td class="t-emoji">${c.emoji}</td><td>${esc(c.name)}</td><td>${c.eta[0]}–${c.eta[1]} days</td><td>${c.baseFee ? money(c.baseFee) : "—"}</td></tr>`).join("") || '<tr><td colspan="4" class="p-empty">None enabled</td></tr>'}</tbody></table></div>
    <div class="p-panel"><h2>Email &amp; SMS senders</h2>
      <p class="p-tag">How sign-in codes, password resets and order emails reach customers. Set a provider to <b>live</b> and enter its credentials; secrets are stored encrypted and never sent back to the browser. On the platform's own store these are also the default sender for every store that has none.</p>
      <table class="p-table"><thead><tr><th></th><th>Provider</th><th>For</th><th>Mode</th><th>Enabled</th><th></th></tr></thead>
      <tbody>${n.notifiers.filter(x => !x.local).map(x => `<tr><td class="t-emoji">${x.emoji}</td><td><b>${esc(x.name)}</b></td><td class="p-tag">${esc(x.channels.join(", "))}</td>
        <td><select data-ntmode="${x.id}"><option ${x.mode === "sandbox" ? "selected" : ""}>sandbox</option><option ${x.mode === "live" ? "selected" : ""}>live</option></select></td>
        <td><input type="checkbox" data-nten="${x.id}" ${x.enabled ? "checked" : ""}></td>
        <td><button class="p-btn sm" data-ntcfg="${x.id}">Configure</button></td></tr>`).join("")}</tbody></table>
      <div style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap"><button class="p-btn primary" id="ntSave">Save senders</button>
        ${(n.channels || []).map(c => `<button class="p-btn" data-nttest="${esc(c.key)}">Send test ${esc(c.name)}</button>`).join("")}</div></div>
  </div>
  <div class="p-panel"><h2>Payments ledger</h2><div id="payLedger"></div></div>`;
}
function wirePayments() {
  loadPayLedger();
  $("#gwSave").onclick = async () => {
    const gateways = $$("[data-gwen]").map(cb => {
      const id = cb.dataset.gwen;
      return { id, enabled: cb.checked, primary: ($(`[data-gwpri="${id}"]`) || {}).checked, mode: ($(`[data-gwmode="${id}"]`) || {}).value, config: (A.gwCfg || {})[id] || {} };
    });
    A.gwCfg = {};
    await api("/admin/gateways", "PUT", { gateways });
    toast("Gateway configuration saved"); render();
  };
  $$("[data-gwtest]").forEach(b => b.onclick = async () => {
    try { const r = await api(`/admin/gateways/${b.dataset.gwtest}/test`, "POST", {}); toast(r.message); } catch (e) { toast(e.message); }
  });
  $$("[data-gwcfg]").forEach(b => b.onclick = async () => {
    const g = (await api("/admin/gateways")).gateways.find(x => x.id === b.dataset.gwcfg);
    $("#modal").innerHTML = `<div class="p-modal"><div class="p-modal-box"><div class="p-modal-head"><h3>${esc(g.name)} configuration</h3><button id="mClose">✕</button></div>
      <div class="p-form">${(g.fields || []).map(f => `<label><span>${esc(f.label)}${f.secret ? " (secret)" : ""}</span><input data-gcfg="${f.key}" value="${esc(g.config[f.key] || "")}" ${f.secret ? 'type="password"' : ""}></label>`).join("") || '<p class="p-tag">No credentials needed.</p>'}
      <button class="p-btn primary" id="mCfgSave">Save</button></div></div></div>`;
    $("#modal").classList.remove("hidden");
    const closeGw = () => { const m = $("#modal"); m.innerHTML = ""; m.classList.add("hidden"); };
    $("#mClose").onclick = closeGw;
    $("#mCfgSave").onclick = () => {
      A.gwCfg = A.gwCfg || {};
      A.gwCfg[g.id] = A.gwCfg[g.id] || {};
      /* what was typed wins; a field left as shown (masked or unchanged) keeps the stored value —
         the stored values used to be copied back over what was typed, so a key could not be changed */
      $$("[data-gcfg]").forEach(i => { if (i.value && !i.value.startsWith("••••")) A.gwCfg[g.id][i.dataset.gcfg] = i.value; });
      closeGw(); toast("Credentials staged — press Save gateway config");
    };
  });
}

/* the store's email / SMS senders: the same Configure → stage → Save pattern as the gateways */
function wireNotifiers() {
  $("#ntSave").onclick = async () => {
    const notifiers = $$("[data-nten]").map(cb => { const id = cb.dataset.nten; return { id, enabled: cb.checked, mode: ($(`[data-ntmode="${id}"]`) || {}).value, config: (A.ntCfg || {})[id] || {} }; });
    A.ntCfg = {};
    await api("/admin/notifiers", "PUT", { notifiers });
    toast("Senders saved"); render();
  };
  $$("[data-nttest]").forEach(b => b.onclick = async () => {
    const channel = b.dataset.nttest;
    try {
      let r = await api(`/admin/notifiers/test/${channel}`, "POST", {});
      /* the account holds no address of this kind: ask for one */
      if (r.needTo) { const to = prompt(r.message); if (!to) return; r = await api(`/admin/notifiers/test/${channel}`, "POST", { to }); }
      toast(r.message);
    } catch (e) { toast(e.message); }
  });
  $$("[data-ntcfg]").forEach(b => b.onclick = async () => {
    const g = (await api("/admin/notifiers")).notifiers.find(x => x.id === b.dataset.ntcfg);
    $("#modal").innerHTML = `<div class="p-modal"><div class="p-modal-box"><div class="p-modal-head"><h3>${esc(g.name)} configuration</h3><button id="mClose">✕</button></div>
      <div class="p-form">${(g.fields || []).map(f => `<label><span>${esc(f.label)}${f.secret ? " (secret)" : ""}</span><input data-ncfg="${f.key}" value="${esc(g.config[f.key] || "")}" ${f.secret ? 'type="password"' : ""}></label>`).join("") || '<p class="p-tag">Nothing to configure.</p>'}
      <button class="p-btn primary" id="mCfgSave">Save</button></div></div></div>`;
    $("#modal").classList.remove("hidden");
    const close = () => { const m = $("#modal"); m.innerHTML = ""; m.classList.add("hidden"); };
    $("#mClose").onclick = close;
    $("#mCfgSave").onclick = () => {
      A.ntCfg = A.ntCfg || {}; A.ntCfg[g.id] = A.ntCfg[g.id] || {};
      $$("[data-ncfg]").forEach(i => { if (i.value && !i.value.startsWith("••••")) A.ntCfg[g.id][i.dataset.ncfg] = i.value; });
      close(); toast("Credentials staged — press Save senders");
    };
  });
}

screen("payments", { group: "Payments & Finance", label: "💳 Payment Gateways", order: 0, render: async () => await vPayments(), wire: async () => { wirePayments(); wireNotifiers(); } });

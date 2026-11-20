/* LUXORA Platform — the identity domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ---------- SSO & Integrations (SSO/SAML, SCIM, transfers, tax) ---------- */
async function vSso() {
  const [s, tks, tf, tax] = await Promise.all([api("/admin/sso"), api("/admin/webhooks").catch(() => ({ webhooks: [] })), api("/admin/transfers"), api("/admin/tax/report")]);
  const c = s.connection || { enabled: false };
  return `<div class="p-panel"><h2>🔐 SSO & Integrations</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Single sign-on and directory sync via fill-in-the-blank config. Nothing activates until you enable it.</p>
    <div class="p-panel"><b>SAML / OIDC SSO</b>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end;margin-top:6px">
        <label><span>Enabled</span><input id="ssoOn" type="checkbox" ${c.enabled ? "checked" : ""}></label>
        <label><span>Provider</span><select id="ssoProv"><option ${c.provider === "okta" ? "selected" : ""}>okta</option><option ${c.provider === "entra" ? "selected" : ""}>entra</option><option ${c.provider === "google" ? "selected" : ""}>google</option><option ${c.provider === "saml-generic" ? "selected" : ""}>saml-generic</option></select></label>
        <label><span>Entity ID</span><input id="ssoEnt" value="${esc(c.entityId || "")}"></label>
        <label><span>SSO URL</span><input id="ssoUrl" style="min-width:240px" value="${esc(c.ssoUrl || "")}" placeholder="https://idp.example/app/sso"></label>
        <label><span>Email domains</span><input id="ssoDom" value="${esc((c.domains || []).join(","))}" placeholder="corp.com,acme.com"></label>
        <button class="p-btn primary sm" id="ssoSave">Save SSO</button></div>
      <p class="p-tag" style="margin-top:6px">Store admins on these domains log in via <code>/console.html → SSO</code>; the IdP redirect is built from the connection (placeholder SAMLRequest until your metadata is loaded).</p></div>
    <div class="p-panel"><b>SCIM 2.0 (directory sync)</b><div style="display:flex;gap:8px;align-items:end;margin-top:6px"><label><span>Label</span><input id="scimLbl" placeholder="okta bridge"></label><button class="p-btn sm" id="scimTok">Issue SCIM token</button></div><div id="scimOut" class="p-tag" style="margin-top:6px">Tokens: bearer at <code>/scim/Users?tenant_id=${(window.__tid || 1)}</code> — HR/IdP pushes staff here.</div></div>
    <div class="p-panel"><b>Warehouse stock transfers</b><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end;margin-top:6px">
      <label><span>SKU</span><input id="trSku" type="number"></label><label><span>From WH</span><input id="trFrom" type="number"></label><label><span>To WH</span><input id="trTo" type="number"></label><label><span>Qty</span><input id="trQty" type="number" value="1"></label><button class="p-btn sm primary" id="trGo">Transfer</button></div>
      <div class="p-tag" style="margin-top:6px">Recent: ${(tf.transfers || []).slice(0, 5).map(x => `${x.sku_id} ${x.qty} ${x.from_warehouse}→${x.to_warehouse}`).join(" · ") || "none"}</div></div>
    <div class="p-panel"><b>Tax — period remittance</b><div class="p-tag" style="margin-top:4px">Period ${esc(tax.period || "")}: taxable ${money(tax.taxable || 0)} · collected ${money(tax.taxCollected || 0)} ${esc(tax.currency || "")} — <a href="/api/admin/tax/report" target="_blank">report</a></div></div>
    </div>`;
}
function wireSso() {
  const $ = s => document.querySelector(s);
  if ($("#ssoSave")) $("#ssoSave").onclick = async () => { try { await api("/admin/sso", "PUT", { enabled: $("#ssoOn").checked, provider: $("#ssoProv").value, entityId: $("#ssoEnt").value, ssoUrl: $("#ssoUrl").value, domains: $("#ssoDom").value.split(",").map(x => x.trim()).filter(Boolean) }); toast("SSO saved"); } catch (e) { toast(e.message); } };
  if ($("#scimTok")) $("#scimTok").onclick = async () => { try { const r = await api("/admin/scim/token", "POST", { label: $("#scimLbl").value || "default" }); $("#scimOut").innerHTML = "Token (shown once): <code>" + esc(r.token) + "</code>"; } catch (e) { toast(e.message); } };
  if ($("#trGo")) $("#trGo").onclick = async () => { try { await api("/admin/transfers", "POST", { sku_id: Number($("#trSku").value), from_warehouse: Number($("#trFrom").value), to_warehouse: Number($("#trTo").value), qty: Number($("#trQty").value) || 1 }); toast("Transferred"); render(); } catch (e) { toast(e.message); } };
}

screen("sso", { group: "Team & Access", label: "🔐 SSO & Integrations", order: 2, render: async () => await vSso(), wire: async () => { wireSso(); } });

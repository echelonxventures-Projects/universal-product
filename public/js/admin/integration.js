/* LUXORA Platform — the integration domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ---------- Outbound Webhooks ---------- */
async function vWebhooks() {
  const d = await api("/admin/webhooks");
  const ev = d.events || [];
  const whRow = w => `<tr><td><code>${esc((w.url || "").slice(0, 46))}</code>${w.description ? `<br><span class="p-tag">${esc(w.description)}</span>` : ""}</td><td class="p-tag">${(w.events || []).map(e => `<code>${esc(e)}</code>`).join(" ")}</td><td><span class="badge ${w.active ? "published" : "draft"}">${w.active ? "active" : "off"}</span></td>
    <td style="text-align:right;white-space:nowrap"><button class="p-btn sm" data-wtest="${w.id}">Send test</button> <button class="p-btn sm danger" data-wwipe="${w.id}">✕</button></td></tr>`;
  const dl = (d.deliveries || []).slice(0, 40).map(x => `<tr><td><code>${esc(x.event)}</code></td><td><span class="badge ${esc(smTone("webhook_delivery", x.status))}">${esc(x.status)}</span></td><td class="num">${x.attempts}</td><td class="p-tag">${esc((x.response || "").slice(0, 40))}</td><td>${esc((x.created_at || "").slice(0, 16))}</td></tr>`).join("");
  return `<div class="p-panel"><h2>🔗 Webhooks</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Outbound events to your endpoints — payloads are HMAC-signed (X-Lux-Signature) and retried. Available events are a data registry; pick which ones each hook receives.</p>
    <div class="p-panel"><b>Add endpoint</b><div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-top:6px">
      <label><span>URL</span><input id="whUrl" placeholder="https://hooks.acme/orders" style="min-width:240px"></label>
      <label><span>Secret</span><input id="whSecret" placeholder="signing secret"></label>
      <label><span>Description</span><input id="whDesc"></label>
      <button class="p-btn primary sm" id="whAdd">Add webhook</button></div>
      <div style="margin-top:6px" class="p-tag">Events: ${ev.map(e => `<label style="margin-right:8px"><input type="checkbox" class="whEv" value="${esc(e)}"> ${esc(e)}</label>`).join("")}</div>
    </div>
    <h3>Endpoints</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>URL</th><th>Events</th><th>Status</th><th></th></tr></thead><tbody>${(d.webhooks || []).map(whRow).join("") || '<tr><td colspan="4">No webhooks.</td></tr>'}</tbody></table></div>
    <div style="margin-top:8px"><button class="p-btn sm" id="whDrain">Retry failed / deliver queued</button></div>
    <h3>Recent deliveries</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Event</th><th>Status</th><th class="num">Tries</th><th>Response</th><th>When</th></tr></thead><tbody>${dl || '<tr><td colspan="5">No deliveries yet.</td></tr>'}</tbody></table></div></div>`;
}
function wireWebhooks() {
  const $ = s => document.querySelector(s), $$ = s => Array.from(document.querySelectorAll(s));
  if ($("#whAdd")) $("#whAdd").onclick = async () => { const events = $$(".whEv:checked").map(c => c.value); try { await api("/admin/webhooks", "POST", { url: $("#whUrl").value, secret: $("#whSecret").value, description: $("#whDesc").value, events: events.length ? events : ["*"] }); toast("Webhook added"); render(); } catch (e) { toast(e.message); } };
  $$("[data-wwipe]").forEach(b => b.onclick = async () => { if (!confirm("Delete webhook?")) return; try { await api("/admin/webhooks/" + b.dataset.wwipe, "DELETE"); render(); } catch (e) { toast(e.message); } });
  $$("[data-wtest]").forEach(b => b.onclick = async () => { try { const r = await api("/admin/webhooks/" + b.dataset.wtest + "/test", "POST", { event: "store.test" }); toast(r.ok ? "Test dispatched" : "Failed"); render(); } catch (e) { toast(e.message); } });
  if ($("#whDrain")) $("#whDrain").onclick = async () => { try { const r = await api("/admin/webhooks/drain", "POST", {}); toast((r.drained || 0) + " attempted, " + (r.remaining || 0) + " pending"); render(); } catch (e) { toast(e.message); } };
}

screen("webhooks", { group: "Automation", label: "🔗 Webhooks", order: 1, render: async () => await vWebhooks(), wire: async () => { wireWebhooks(); } });

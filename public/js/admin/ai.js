/* LUXORA Platform — the ai domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ---------- AI Studio (capability layer) ---------- */
async function vAI() {
  const ov = await api("/ai");
  const cap = ov.capabilities || [];
  AI_CAPS = cap;
  const st = ov.settings || {};
  const premProviders = (await api("/meta")).providersAi || [];
  const aiGw = await api("/admin/ai-gateways").catch(() => ({ gateways: [] }));
  const tierBadge = t => `<span class="badge ${t === "premium" ? "active" : "processing"}">${esc(t)}</span>`;
  return `<div class="p-panel"><div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
      <h2 style="margin:0">🤖 AI Studio</h2>
      <span class="p-tag">store tier: ${tierBadge(ov.plan.tier)}</span>
      <span style="flex:1"></span>
      <span class="p-tag">${(ov.usage && ov.usage.totalCalls) || 0} calls · ${money(ov.usage && ov.usage.totalCost || 0)} accrued</span>
    </div>
    <p style="margin:0 0 14px;color:var(--p-muted);font-size:13px">Free built-in engine is on for every store (1st priority). Premium models (OpenAI / Anthropic / Stability / Google Vision) unlock for paid stores or after buying the <b>AI Premium</b> module — configure provider + model per capability below.</p>
    <div class="p-cards" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin-bottom:16px">
      ${cap.map(c => `<div class="p-stat" style="border:1px solid var(--p-line);border-radius:12px;padding:12px">
        <div style="display:flex;align-items:center;gap:6px"><b>${esc(c.icon)} ${esc(c.name)}</b>${tierBadge(c.tier)}</div>
        <div style="font-size:12px;color:var(--p-muted);margin:4px 0">${esc(c.desc)}</div>
        <div style="font-size:12px">Provider: <b>${c.provider ? esc(c.provider.emoji + " " + c.provider.name) : "—"}</b> · model <code>${esc(c.model || "—")}</code></div>
        <div style="font-size:12px;color:${c.status === "premium_locked" ? "var(--p-red)" : "var(--p-muted)"}">Status: ${esc(c.status.replace("_", " "))} · ${c.remaining}/${c.limits.perDay} left today</div>
        <label style="display:flex;align-items:center;gap:6px;font-size:12px;margin-top:8px">
          <input type="checkbox" data-aiprem="${esc(c.key)}" ${st[c.key] && st[c.key].premium ? "checked" : ""} ${c.premium ? "" : "disabled"}> use premium model
        </label>
        <div style="display:flex;gap:6px;margin-top:6px">
          <select data-aiprov="${esc(c.key)}" ${c.premium ? "" : "disabled"}><option value="">provider…</option>${(premProviders.filter(p => (c.key)).map(p => `<option value="${esc(p.id)}" ${st[c.key] && st[c.key].provider === p.id ? "selected" : ""}>${esc(p.name)}</option>`).join(""))}</select>
          <input data-aimodel="${esc(c.key)}" placeholder="model" value="${esc((st[c.key] || {}).model || "")}" style="flex:1" ${c.premium ? "" : "disabled"}>
        </div>
      </div>`).join("")}
    </div>
    <div class="p-panel"><h3>AI Provider Credentials</h3>
      <p style="color:var(--p-muted);font-size:13px">Configure API keys for each AI provider. Secrets are stored encrypted server-side.</p>
      <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Provider</th><th>Fields</th><th>Status</th><th></th></tr></thead>
      <tbody id="aiGwBody">${aiGw.gateways.map(gw => {
        const p = premProviders.find(p => p.id === gw.id) || {};
        const fields = p.fields || [];
        const hasSecret = fields.some(f => f.secret && (gw.config || {})[f.key]);
        return `<tr>
          <td><b>${esc(p.emoji)} ${esc(p.name)}</b><br><span class="p-tag">${esc(p.desc || "")}</span></td>
          <td><div style="display:flex;flex-wrap:wrap;gap:6px">${fields.map(f => {
            const val = (gw.config || {})[f.key] || "";
            const masked = f.secret && val ? `••••${val.slice(-4)}` : val;
            return `<label style="font-size:11px"><span>${esc(f.label)}</span><input data-aicred="${gw.id}" data-aikey="${f.key}" value="${esc(masked)}" style="font-size:11px" ${f.secret ? 'type="password"' : ''}></label>`;
          }).join("")}</div></td>
          <td>${hasSecret ? '<span class="badge active">configured</span>' : '<span class="badge processing">unconfigured</span>'}</td>
          <td><button class="p-btn sm" data-aicfg="${gw.id}">Test</button></td>
        </tr>`;
      }).join("") || '<tr><td colspan="4">No AI providers available. Configure them in Platform Console → Provider Registry.</td></tr>'}</tbody></table></div>
      <div style="margin-top:10px;display:flex;gap:10px"><button class="p-btn primary" id="aiGwSave">Save credentials</button><button class="p-btn" id="aiGwTestAll">Test all</button></div>
    </div>
    <div class="p-panel"><h3>Run a capability</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
        <label><span>Capability</span><select id="aiCapSel">${cap.map(c => `<option value="${esc(c.key)}">${esc(c.name)}</option>`).join("")}</select></label>
        <div id="aiParams" class="row"></div>
        <button class="p-btn primary sm" id="aiRun">Run</button>
        <button class="p-btn sm" id="aiTask">Queue as task</button>
      </div>
      <pre id="aiOut" class="p-code" style="margin-top:10px;max-height:340px;overflow:auto;background:#0b0d12;color:#cfe;border-radius:10px;padding:10px;font-size:12px">Run a capability to see output…</pre></div>
    <div class="p-panel"><h3>Usage ledger</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Capability</th><th>Provider</th><th>Tier</th><th class="num">Units</th><th class="num">Cost</th><th class="num">Calls</th><th>Last</th></tr></thead>
      <tbody>${(ov.usage && ov.usage.rows || []).map(u => `<tr><td>${esc(u.capability)}</td><td>${esc(u.provider)}</td><td>${esc(u.tier)}</td><td class="num">${u.units}</td><td class="num">${money(u.cost)}</td><td class="num">${u.calls}</td><td>${esc(u.last || "")}</td></tr>`).join("") || '<tr><td colspan="7">No AI calls yet.</td></tr>'}</tbody></table></div></div>
    <div class="p-panel"><h3>Recent tasks</h3><div id="aiTasks">${(await api("/ai/tasks")).tasks.map(t => `<div class="p-tag" style="display:block;margin:4px 0">${esc(t.capability)} · <b>${esc(t.status)}</b> · ${money(t.cost || 0)}</div>`).join("") || "No tasks."}</div></div>
    </div>`;
}
function wireAI() {
  const save = async () => {
    const ai = {};
    $$("[data-aiprem]").forEach(cb => { const k = cb.dataset.aiprem; ai[k] = ai[k] || {}; ai[k].premium = cb.checked; });
    $$("[data-aiprov]").forEach(sel => { const k = sel.dataset.aiprov; ai[k] = ai[k] || {}; if (sel.value) ai[k].provider = sel.value; });
    $$("[data-aimodel]").forEach(inp => { const k = inp.dataset.aimodel; ai[k] = ai[k] || {}; if (inp.value) ai[k].model = inp.value; });
    try { await api("/admin/settings", "PUT", { ai }); toast("AI configuration saved"); render(); } catch (e) { toast(e.message); }
  };
  $$("[data-aiprem],[data-aiprov],[data-aimodel]").forEach(el => el.onchange = el.onblur = save);
  const saveCredentials = async () => {
    const creds = {};
    $$("[data-aicred]").forEach(inp => {
      const id = inp.dataset.aicred, k = inp.dataset.aikey, v = inp.value;
      if (v) { creds[id] = creds[id] || {}; creds[id][k] = v; }
    });
    try { await api("/admin/ai-gateways", "PUT", creds); toast("AI credentials saved"); } catch (e) { toast(e.message); }
  };
  const testCredential = async id => {
    try { const r = await api("/admin/ai-gateways/" + encodeURIComponent(id) + "/test", "POST", {}); toast(r.message); } catch (e) { toast(e.message); }
  };
  const testAll = async () => {
    $$("[data-aicfg]").forEach(b => testCredential(b.dataset.aicfg));
  };
  if ($("#aiGwSave")) $("#aiGwSave").onclick = saveCredentials;
  if ($("#aiGwTestAll")) $("#aiGwTestAll").onclick = testAll;
  /* the inputs a capability takes are declared on its row (`params`) */
  const capRows = AI_CAPS || [];
  const drawParams = () => { const row = capRows.find(c => c.key === ($("#aiCapSel") || {}).value) || {}; const box = $("#aiParams"); if (box) box.innerHTML = (row.params || []).map(p => `<label><span>${esc(p.label || p.key)}</span><input data-aiparam="${esc(p.key)}" data-ailist="${p.list ? 1 : ""}" placeholder="${esc(p.placeholder || "")}"></label>`).join(""); };
  if ($("#aiCapSel")) { $("#aiCapSel").onchange = drawParams; drawParams(); }
  const collect = () => { const cap = $("#aiCapSel").value, p = {}; $$("[data-aiparam]").forEach(el => { const v = el.value.trim(); if (!v) return; p[el.dataset.aiparam] = el.dataset.ailist ? v.split(",").map(x => x.trim()).filter(Boolean) : v; }); return { cap, p }; };
  const run = async () => { const { cap, p } = collect(); try { const r = await api("/ai/run/" + encodeURIComponent(cap), "POST", p); $("#aiOut").textContent = JSON.stringify(r, null, 1); toast(cap + " · " + (r.tier || "") + " · " + money(r.cost || 0)); } catch (e) { $("#aiOut").textContent = "⚠ " + e.message; toast(e.message); } };
  const task = async () => { const { cap, p } = collect(); try { const r = await api("/ai/tasks", "POST", { capability: cap, params: p, runNow: true }); $("#aiOut").textContent = JSON.stringify(r.tasks.slice(0, 6), null, 1); toast("Queued"); render(); } catch (e) { toast(e.message); } };
  if ($("#aiRun")) $("#aiRun").onclick = run; if ($("#aiTask")) $("#aiTask").onclick = task;
  $$("[data-aicfg]").forEach(b => b.onclick = () => testCredential(b.dataset.aicfg));
}

screen("ai", { group: "Automation", label: "🤖 AI Studio", order: 0, render: async () => await vAI(), wire: async () => { wireAI(); } });

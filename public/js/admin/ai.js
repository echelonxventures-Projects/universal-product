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

/* ---------- Knowledge, assistants and MCP keys (lib/rag.js, lib/assistant.js, lib/mcp.js) ----------
   Every app's knowledge collections with their mode and experts; entries, proposals, versions and
   rollback; the assistant profiles; and the MCP access keys outside clients use. */
const KB = { coll: null, status: "" };
async function vKnowledgePanels() {
  const [kc, ap, mk] = await Promise.all([api("/kb/collections").catch(e => ({ error: e.message })), api("/assistant/profiles").catch(() => ({ profiles: [], tools: [] })), api("/admin/mcp-keys").catch(() => ({ keys: [], roles: [] }))]);
  if (kc.error) return `<div class="p-panel"><h2>📚 Knowledge</h2><p class="p-tag">${esc(kc.error)}</p></div>`;
  const cols = kc.collections || [], modes = kc.modes || [], roles = kc.roles || [];
  if (!KB.coll && cols.length) KB.coll = cols[0].key;
  const cur = cols.find(c => c.key === KB.coll);
  const [en, pr] = cur ? await Promise.all([api(`/kb/${encodeURIComponent(cur.key)}/entries` + (KB.status ? "?status=" + encodeURIComponent(KB.status) : "")), api(`/kb/${encodeURIComponent(cur.key)}/proposals`)]) : [{ entries: [] }, { proposals: [] }];
  const modeOpts = sel => modes.map(m => `<option value="${esc(m.key)}" ${m.key === sel ? "selected" : ""} title="${esc(m.description)}">${esc(m.label)}</option>`).join("");
  const roleOpts = sel => roles.map(r => `<option value="${esc(r)}" ${(sel || []).includes(r) ? "selected" : ""}>${esc(r)}</option>`).join("");
  const count = c => Object.entries(c.counts || {}).map(([k, v]) => esc(k) + " " + v).join(" · ") || "empty";
  const origin = location.origin;
  return `
  <div class="p-panel"><h2>📚 Knowledge</h2>
    <p class="p-tag">Collections of approved knowledge your assistants answer from — one per app (astrology, consultancy, help…). The mode decides how knowledge grows; only the collection's expert roles approve it. Every change is versioned and can be rolled back.</p>
    <table class="p-table"><thead><tr><th>Collection</th><th>Mode</th><th>Experts</th><th>Entries</th><th></th></tr></thead><tbody>
    ${cols.map(c => `<tr><td><b>${esc(c.label)}</b> <code>${esc(c.key)}</code></td><td><select data-kbmode="${esc(c.key)}">${modeOpts(c.mode)}</select></td>
      <td><select multiple size="2" data-kbexperts="${esc(c.key)}">${roleOpts(c.expertRoles)}</select></td><td class="p-tag">${count(c)}</td>
      <td><button class="p-btn sm" data-kbopen="${esc(c.key)}">${c.key === KB.coll ? "Open ✓" : "Open"}</button> <button class="p-btn sm" data-kbsave="${esc(c.key)}">Save</button></td></tr>`).join("") || '<tr><td colspan="5" class="p-empty">No collections yet</td></tr>'}
    </tbody></table>
    <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap"><input id="kbNewKey" placeholder="key, e.g. astro" size="12"><input id="kbNewLabel" placeholder="label, e.g. Astrology" size="16">
      <select id="kbNewMode">${modeOpts("ai_assisted")}</select><button class="p-btn" id="kbNew">+ Collection</button></div>
  </div>
  ${cur ? `<div class="p-panel"><h2>${esc(cur.label)} · entries</h2>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px"><select id="kbStatus"><option value="">all statuses</option>${["draft", "review", "approved", "rejected", "retired"].map(x => `<option ${x === KB.status ? "selected" : ""}>${x}</option>`).join("")}</select></div>
    <table class="p-table"><thead><tr><th>Title</th><th>Tags</th><th>Status</th><th>Source</th><th>Rating</th><th>v</th><th></th></tr></thead><tbody>
    ${(en.entries || []).map(e => `<tr><td><b>${esc(e.title)}</b><br><span class="p-tag">${esc(String(e.body).slice(0, 140))}${e.body.length > 140 ? "…" : ""}</span></td><td class="p-tag">${esc((e.tags || []).join(" "))}</td>
      <td><span class="badge">${esc(e.status)}</span></td><td class="p-tag">${esc(e.source)}</td><td>${e.rating == null ? "—" : e.rating + " (" + e.votes + ")"}</td><td>${e.version}</td>
      <td style="white-space:nowrap"><button class="p-btn sm" data-kbrev="${e.id}|approve">Approve</button> <button class="p-btn sm" data-kbrev="${e.id}|reject">Reject</button> <button class="p-btn sm" data-kbrev="${e.id}|retire">Retire</button> <button class="p-btn sm" data-kbhist="${e.id}">History</button></td></tr>`).join("") || '<tr><td colspan="7" class="p-empty">No entries</td></tr>'}
    </tbody></table>
    <div class="p-form" style="margin-top:12px"><label><span>Title</span><input id="kbTitle"></label><label><span>Text</span><textarea id="kbBody" rows="4"></textarea></label>
      <label><span>Tags (space-separated, e.g. planet:mars house:7)</span><input id="kbTags"></label>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="p-btn primary" id="kbAdd">Add entry</button><button class="p-btn" id="kbDraft" title="The AI drafts the entry for an expert's review (where the mode allows)">AI draft for review</button></div></div>
    <h3 style="margin-top:14px">Proposed revisions</h3>
    <table class="p-table"><thead><tr><th>Entry</th><th>Proposed text</th><th>From</th><th>Confidence</th><th>Confirmations</th><th></th></tr></thead><tbody>
    ${(pr.proposals || []).map(x => `<tr><td>#${x.entry_id}</td><td class="p-tag">${esc(String(x.body).slice(0, 200))}</td><td class="p-tag">${esc(x.source)} · ${esc(x.author || "")}</td><td>${x.confidence == null ? "—" : x.confidence}</td><td>${x.confirmations}</td>
      <td style="white-space:nowrap"><button class="p-btn sm" data-kbprop="${x.id}|approve">Approve</button> <button class="p-btn sm" data-kbprop="${x.id}|reject">Reject</button> <button class="p-btn sm" data-kbconfirm="${x.id}">Confirm</button></td></tr>`).join("") || '<tr><td colspan="6" class="p-empty">Nothing waiting</td></tr>'}
    </tbody></table><div id="kbHistory"></div></div>` : ""}
  <div class="p-panel"><h2>💬 Assistants</h2>
    <p class="p-tag">Each app's assistant: what it answers from, which platform tools it may use, who it hands people to. Switch the <b>AI assistant</b> capability on to offer them; add your Claude API key in the AI gateways above. Without a key an assistant answers from approved knowledge only.</p>
    <table class="p-table"><thead><tr><th>Profile</th><th>Collections</th><th>Tools</th><th>Model · effort</th><th></th></tr></thead><tbody>
    ${(ap.profiles || []).map(p => `<tr><td><b>${esc(p.label || p.key)}</b> <code>${esc(p.key)}</code></td><td class="p-tag">${esc((p.collections || []).join(", "))}</td><td class="p-tag">${esc((p.tools || []).join(", "))}</td><td class="p-tag">${esc(p.model)} · ${esc(p.effort)}</td>
      <td><button class="p-btn sm" data-apedit="${esc(p.key)}">Edit</button></td></tr>`).join("")}
    </tbody></table></div>
  <div class="p-panel"><h2>🔌 API & MCP access</h2>
    <p class="p-tag">Your other systems — in any language — call the API (described at <code>${esc(origin)}/api/openapi.json</code>) with an access key as the Bearer token. MCP clients (Claude Desktop, agents, partner apps) call the platform's tools at <code>${esc(origin)}/api/mcp</code> with the same key. A key acts as one store role and sees only what that role may.</p>
    <table class="p-table"><thead><tr><th>Name</th><th>Role</th><th>Created</th><th>Last used</th><th></th></tr></thead><tbody>
    ${(mk.keys || []).map(k => `<tr><td>${esc(k.name)}</td><td>${esc(k.role_key)}</td><td class="p-tag">${esc(k.created_at)} · ${esc(k.created_by || "")}</td><td class="p-tag">${esc(k.last_used || "never")}</td>
      <td>${k.revoked ? '<span class="badge">revoked</span>' : `<button class="p-btn sm" data-mcprevoke="${k.id}">Revoke</button>`}</td></tr>`).join("") || '<tr><td colspan="5" class="p-empty">No keys</td></tr>'}
    </tbody></table>
    <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap"><input id="mcpName" placeholder="name, e.g. Claude Desktop"><select id="mcpRole">${(mk.roles || []).map(r => `<option>${esc(r)}</option>`).join("")}</select><button class="p-btn" id="mcpIssue">Issue key</button></div>
    <div id="mcpOut"></div></div>`;
}
function wireKnowledge() {
  const picked = el => el ? [...el.selectedOptions].map(o => o.value) : [];
  const go = async (fn, ok) => { try { const r = await fn(); if (ok) toast(typeof ok === "function" ? ok(r) : ok); render(); return r; } catch (e) { toast(e.message); } };
  $$("[data-kbopen]").forEach(b => b.onclick = () => { KB.coll = b.dataset.kbopen; render(); });
  $$("[data-kbsave]").forEach(b => b.onclick = () => { const k = b.dataset.kbsave; go(() => api(`/kb/collections/${encodeURIComponent(k)}`, "PUT", { mode: $(`[data-kbmode="${k}"]`).value, expertRoles: picked($(`[data-kbexperts="${k}"]`)) }), "Collection saved"); });
  if ($("#kbNew")) $("#kbNew").onclick = () => { const key = $("#kbNewKey").value.trim(); KB.coll = key; go(() => api(`/kb/collections/${encodeURIComponent(key)}`, "PUT", { label: $("#kbNewLabel").value.trim() || key, mode: $("#kbNewMode").value }), "Collection created"); };
  if ($("#kbStatus")) $("#kbStatus").onchange = e => { KB.status = e.target.value; render(); };
  const tags = () => ($("#kbTags").value || "").split(/\s+/).filter(Boolean);
  if ($("#kbAdd")) $("#kbAdd").onclick = () => go(() => api(`/kb/${encodeURIComponent(KB.coll)}/entries`, "POST", { title: $("#kbTitle").value, body: $("#kbBody").value, tags: tags() }), r => "Entry saved — " + r.entry.status);
  if ($("#kbDraft")) $("#kbDraft").onclick = () => go(() => api(`/kb/${encodeURIComponent(KB.coll)}/draft`, "POST", { title: $("#kbTitle").value, notes: $("#kbBody").value, tags: tags() }), "AI draft waiting for review");
  $$("[data-kbrev]").forEach(b => b.onclick = () => { const [id, decision] = b.dataset.kbrev.split("|"); go(() => api(`/kb/entries/${id}/review`, "POST", { decision }), "Entry " + decision + "d"); });
  $$("[data-kbprop]").forEach(b => b.onclick = () => { const [id, decision] = b.dataset.kbprop.split("|"); go(() => api(`/kb/proposals/${id}/decide`, "POST", { decision }), "Proposal " + decision + "d"); });
  $$("[data-kbconfirm]").forEach(b => b.onclick = () => go(() => api(`/kb/proposals/${b.dataset.kbconfirm}/confirm`, "POST", {}), r => r.applied ? "Confirmed — it went live (auto-evolving)" : "Confirmed"));
  $$("[data-kbhist]").forEach(b => b.onclick = async () => {
    try {
      const h = await api(`/kb/entries/${b.dataset.kbhist}/history`);
      $("#kbHistory").innerHTML = `<h3 style="margin-top:14px">Versions of entry #${esc(b.dataset.kbhist)}</h3><table class="p-table"><thead><tr><th>v</th><th>Title</th><th>Status</th><th>By</th><th>Why</th><th>When</th><th></th></tr></thead><tbody>${h.versions.map(v => `<tr><td>${v.version}</td><td>${esc(v.title)}</td><td>${esc(v.status)}</td><td>${esc(v.changed_by)}</td><td class="p-tag">${esc(v.reason)}</td><td class="p-tag">${esc(v.at)}</td><td><button class="p-btn sm" data-kbroll="${esc(b.dataset.kbhist)}|${v.version}">Restore</button></td></tr>`).join("")}</tbody></table>`;
      $$("[data-kbroll]").forEach(r => r.onclick = () => { const [id, version] = r.dataset.kbroll.split("|"); go(() => api(`/kb/entries/${id}/rollback`, "POST", { version: Number(version) }), "Version " + version + " restored"); });
    } catch (e) { toast(e.message); }
  });
  $$("[data-apedit]").forEach(b => b.onclick = async () => {
    const { profiles, tools } = await api("/assistant/profiles"); const p = profiles.find(x => x.key === b.dataset.apedit);
    $("#modal").innerHTML = `<div class="p-modal"><div class="p-modal-box"><div class="p-modal-head"><h3>${esc(p.label || p.key)}</h3><button id="mClose">✕</button></div><div class="p-form">
      <label><span>Label</span><input id="apLabel" value="${esc(p.label || "")}"></label>
      <label><span>Persona and rules</span><textarea id="apPersona" rows="6">${esc(p.persona || "")}</textarea></label>
      <label><span>Knowledge collections (comma-separated keys)</span><input id="apColls" value="${esc((p.collections || []).join(", "))}"></label>
      <label><span>Tools it may use</span><select id="apTools" multiple size="5">${tools.map(t => `<option value="${esc(t.name)}" ${(p.tools || []).includes(t.name) ? "selected" : ""}>${esc(t.title)} (${esc(t.name)})</option>`).join("")}</select></label>
      <label><span>Disclaimer (always said)</span><input id="apDisc" value="${esc(p.disclaimer || "")}"></label>
      <label><span>Hand-off label · page</span><input id="apHoLabel" value="${esc((p.handoff || {}).label || "")}"> <input id="apHoPath" value="${esc((p.handoff || {}).path || "")}"></label>
      <label><span>Model · effort</span><input id="apModel" value="${esc(p.model)}"> <select id="apEffort">${["low", "medium", "high", "xhigh", "max"].map(x => `<option ${x === p.effort ? "selected" : ""}>${x}</option>`).join("")}</select></label>
      <button class="p-btn primary" id="apSave">Save</button></div></div></div>`;
    $("#modal").classList.remove("hidden");
    const close = () => { $("#modal").innerHTML = ""; $("#modal").classList.add("hidden"); };
    $("#mClose").onclick = close;
    $("#apSave").onclick = () => go(() => api(`/assistant/profiles/${encodeURIComponent(p.key)}`, "PUT", { label: $("#apLabel").value, persona: $("#apPersona").value, collections: $("#apColls").value.split(",").map(x => x.trim()).filter(Boolean),
      tools: picked($("#apTools")), disclaimer: $("#apDisc").value, handoff: { label: $("#apHoLabel").value, path: $("#apHoPath").value }, model: $("#apModel").value.trim(), effort: $("#apEffort").value }).then(r => { close(); return r; }), "Assistant saved");
  });
  if ($("#mcpIssue")) $("#mcpIssue").onclick = async () => {
    try { const r = await api("/admin/mcp-keys", "POST", { name: $("#mcpName").value || "MCP key", role: $("#mcpRole").value });
      $("#mcpOut").innerHTML = `<p class="p-tag" style="margin-top:8px">Copy this key now — it is not shown again:</p><code style="word-break:break-all">${esc(r.key)}</code>`; toast("Key issued"); } catch (e) { toast(e.message); }
  };
  $$("[data-mcprevoke]").forEach(b => b.onclick = () => { if (confirm("Revoke this key? Clients using it stop at once.")) go(() => api(`/admin/mcp-keys/${b.dataset.mcprevoke}`, "DELETE"), "Key revoked"); });
}

screen("ai", { render: async () => (await vAI()) + (await vKnowledgePanels()), wire: async () => { wireAI(); wireKnowledge(); } });

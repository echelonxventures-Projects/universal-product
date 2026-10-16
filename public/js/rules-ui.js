/* LUXORA Platform - the applicability-rules screen (shared by the platform and store consoles)

   Everything on this screen is read from the server's registries: the subject types, the
   dimensions a rule can be scoped by and each dimension's options. A subject type or a
   dimension an operator registers tomorrow appears here with no front-end change.
   mount(root, { api, base, scope }) — `api` is the console's own fetch helper, `base` the
   rules endpoint ("/platform/rules" or "/admin/rules"), `scope` "platform" or "store". */
"use strict";

const LXRulesUI = (() => {
  const e = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const EFFECT_STYLE = { allow: "background:#E7F6EC;color:#1E7A45", deny: "background:#FDECEC;color:#B3261E", prefer: "background:#EAF1FE;color:#2456C9" };
  const VERDICT_STYLE = { open: "background:#F1F1F1;color:#555", allowed: EFFECT_STYLE.allow, conditional: "background:#FFF6E0;color:#8A6100", blocked: EFFECT_STYLE.deny };
  const chip = (txt, st) => `<span style="display:inline-block;padding:2px 9px;border-radius:99px;font-size:11px;font-weight:700;${st || ""}">${e(txt)}</span>`;

  function overlay(html) {
    const f = document.createElement("div");
    f.className = "p-modal";
    f.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:1100;display:flex;align-items:center;justify-content:center;padding:16px";
    f.innerHTML = `<div class="p-modal-box" style="max-width:760px;width:100%;max-height:88vh;overflow:auto">${html}</div>`;
    f.addEventListener("click", ev => { if (ev.target === f || ev.target.closest("[data-rclose]")) f.remove(); });
    document.body.appendChild(f);
    return f;
  }

  async function mount(root, opts) {
    const { api, base, scope } = opts;
    const st = { type: "", data: null, subjects: {} };
    const load = async () => { st.data = await api(base); };
    const subjectsOf = async type => st.subjects[type] || (st.subjects[type] = (await api(base + "/subjects?type=" + encodeURIComponent(type))).subjects || []);
    const typeName = k => ((st.data.schema.subjectTypes.find(t => t.key === k) || {}).name || k);
    const subjName = (type, key) => key === "*" ? "every " + typeName(type).toLowerCase() : ((st.subjects[type] || []).find(x => x.key === key) || {}).name || key;

    function ruleRows(list, editable) {
      if (!list.length) return `<tr><td colspan="7" style="color:var(--p-muted);padding:14px">No rules yet — everything is open.</td></tr>`;
      return list.map(r => `<tr${r.active ? "" : ' style="opacity:.55"'}>
        <td>${e(typeName(r.subject_type))}</td><td><b>${e(subjName(r.subject_type, r.subject))}</b></td>
        <td>${chip(r.effect, EFFECT_STYLE[r.effect])}${r.effect === "prefer" ? " " + e(r.priority) : ""}</td>
        <td style="font-size:12.5px">${e(r.summary.replace(/^#\d+ \S+ \S+ ?·? ?/, "") || "everywhere")}</td>
        <td style="font-size:12px">${Object.keys(r.params || {}).length ? e(Object.entries(r.params).map(([k, v]) => k + "=" + v).join(", ")) : "—"}</td>
        <td style="font-size:12px;color:var(--p-muted)">${e(r.note || "")}</td>
        <td style="white-space:nowrap">${editable ? `<button class="p-btn sm" data-redit="${r.id}">Edit</button> <button class="p-btn sm danger" data-rdel="${r.id}">✕</button>` : ""}</td></tr>`).join("");
    }
    async function draw() {
      const d = st.data;
      const types = d.schema.subjectTypes;
      const mine = d.rules.filter(r => !st.type || r.subject_type === st.type);
      await Promise.all([...new Set(d.rules.concat(d.inherited || []).map(r => r.subject_type))].map(t => subjectsOf(t).catch(() => [])));
      root.innerHTML = `
        <div class="p-card" style="margin-bottom:16px"><p style="margin:0;color:var(--p-muted);font-size:13.5px">
          ${scope === "platform"
            ? "Decide where, for whom and for what anything applies — on every platform, a kind of platform or one platform. A rule names a subject (a gateway, bank, carrier, capability, AI model, offer…) and scopes it by country, currency, service, customer segment, channel, amount and dates. Each platform can narrow these rules for itself, never widen them."
            : "Narrow what this platform offers — by country, currency, service, customer segment, channel, amount and dates. The platform owner's rules (below) always apply; yours can only restrict further."}
          The most specific rule wins; at a tie, deny wins. A subject with an allow rule is offered only where one of its allow rules matches.</p></div>
        <div class="p-card" style="margin-bottom:16px">
          <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px">
            <h3 style="margin:0;flex:1">${scope === "platform" ? "Platform rules" : "This platform's rules"} (${d.rules.length})</h3>
            <select id="rType"><option value="">All subject types</option>${types.map(t => `<option value="${e(t.key)}" ${st.type === t.key ? "selected" : ""}>${e(t.name)}</option>`).join("")}</select>
            <button class="p-btn sm" id="rExplain">🔎 Explain</button>
            <button class="p-btn sm primary" id="rNew">＋ New rule</button>
          </div>
          <div style="overflow-x:auto"><table class="p-table"><thead><tr><th>Type</th><th>Subject</th><th>Effect</th><th>Where / for whom</th><th>Overrides</th><th>Note</th><th></th></tr></thead>
          <tbody>${ruleRows(mine, true)}</tbody></table></div>
        </div>
        ${scope === "store" ? `<div class="p-card" style="margin-bottom:16px"><h3 style="margin-top:0">From the platform owner (${(d.inherited || []).length})</h3>
          <div style="overflow-x:auto"><table class="p-table"><thead><tr><th>Type</th><th>Subject</th><th>Effect</th><th>Where / for whom</th><th>Overrides</th><th>Note</th><th></th></tr></thead>
          <tbody>${ruleRows((d.inherited || []).filter(r => !st.type || r.subject_type === st.type), false)}</tbody></table></div></div>
        <div class="p-card"><h3 style="margin-top:0">Customer segments</h3>
          <p style="color:var(--p-muted);font-size:13px;margin-top:0">Segments like new, returning and high-value customers are computed automatically. Put a customer in any other segment by hand here.</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px"><input id="smEmail" type="email" placeholder="customer@email" style="flex:1;min-width:180px">
            <select id="smSeg">${(d.schema.segmentOptions || []).map(o => `<option value="${e(o.key)}">${e(o.name)}</option>`).join("")}</select>
            <button class="p-btn sm primary" id="smAdd">Add</button></div>
          <table class="p-table"><thead><tr><th>Segment</th><th>Customer</th><th></th></tr></thead><tbody>
          ${(d.members || []).length ? d.members.map(m => `<tr><td>${e(m.segment)}</td><td>${e(m.owner)}</td><td><button class="p-btn sm danger" data-smdel="${m.id}">✕</button></td></tr>`).join("") : `<tr><td colspan="3" style="color:var(--p-muted)">No hand-assigned members.</td></tr>`}
          </tbody></table></div>` : ""}`;
      root.querySelector("#rType").onchange = ev => { st.type = ev.target.value; draw(); };
      root.querySelector("#rNew").onclick = () => editor(null);
      root.querySelector("#rExplain").onclick = () => explain();
      root.querySelectorAll("[data-redit]").forEach(b => b.onclick = () => editor(d.rules.find(r => r.id == b.dataset.redit)));
      root.querySelectorAll("[data-rdel]").forEach(b => b.onclick = async () => {
        if (!confirm("Delete this rule?")) return;
        try { await api(base + "/" + b.dataset.rdel, "DELETE", {}); await load(); draw(); } catch (err) { alert(err.message); }
      });
      const add = root.querySelector("#smAdd");
      if (add) add.onclick = async () => {
        try { const r = await api("/admin/segments/members", "POST", { email: root.querySelector("#smEmail").value, segment: root.querySelector("#smSeg").value }); st.data.members = r.members; draw(); } catch (err) { alert(err.message); }
      };
      root.querySelectorAll("[data-smdel]").forEach(b => b.onclick = async () => { const r = await api("/admin/segments/members/" + b.dataset.smdel, "DELETE", {}); st.data.members = r.members; draw(); });
    }

    /* one input per registered dimension: a multi-select when it has options, else free text */
    function dimInput(dm, val, id) {
      const v = Array.isArray(val) ? val : [];
      if (dm.options && dm.options.length) {
        return `<label><span>${e(dm.name)} <small style="color:var(--p-muted)">(none = any)</small></span>
          <select multiple size="${Math.min(6, Math.max(3, dm.options.length))}" data-dim="${e(dm.key)}" id="${id}">${dm.options.map(o => `<option value="${e(o.key)}" ${v.includes(o.key) ? "selected" : ""}>${e(o.name)}</option>`).join("")}</select></label>`;
      }
      return `<label><span>${e(dm.name)} <small style="color:var(--p-muted)">(comma-separated; blank = any)</small></span><input data-dim="${e(dm.key)}" id="${id}" value="${e(v.join(", "))}"></label>`;
    }
    const readDim = el => el.tagName === "SELECT" ? [...el.selectedOptions].map(o => o.value) : el.value.split(",").map(x => x.trim()).filter(Boolean);

    async function editor(rule) {
      const d = st.data, r = rule || { subject_type: st.type || d.schema.subjectTypes[0].key, subject: "*", effect: "deny", priority: 0, scope: {}, params: {}, note: "", active: 1 };
      const sc = r.scope || {};
      const f = overlay(`<div class="p-modal-head"><h3>${rule ? "Edit rule #" + rule.id : "New rule"}</h3><button data-rclose>✕</button></div>
        <div class="p-form">
          <div class="row"><label><span>Subject type</span><select id="reType">${d.schema.subjectTypes.map(t => `<option value="${e(t.key)}" ${t.key === r.subject_type ? "selected" : ""}>${e(t.name)}</option>`).join("")}</select></label>
            <label><span>Subject</span><select id="reSubj"></select></label></div>
          <div class="row"><label><span>Effect</span><select id="reEff">${d.schema.effects.map(x => `<option ${x === r.effect ? "selected" : ""}>${x}</option>`).join("")}</select></label>
            <label><span>Priority (prefer: higher is offered first)</span><input id="rePri" type="number" value="${e(r.priority || 0)}"></label></div>
          <h4 style="margin:14px 0 4px">Where and for whom</h4>
          ${d.schema.dimensions.map((dm, i) => dimInput(dm, sc[dm.key], "reD" + i)).join("")}
          <div class="row"><label><span>Amount from</span><input id="reMin" type="number" step="any" value="${e(sc.min_amount != null ? sc.min_amount : "")}"></label>
            <label><span>Amount up to</span><input id="reMax" type="number" step="any" value="${e(sc.max_amount != null ? sc.max_amount : "")}"></label>
            <label><span>In currency (blank = the buyer's)</span><input id="reCur" value="${e(sc.amount_currency || "")}" placeholder="INR"></label></div>
          <div class="row"><label><span>From date</span><input id="reFrom" type="date" value="${e((sc.from || "").slice(0, 10))}"></label>
            <label><span>Until date</span><input id="reTo" type="date" value="${e((sc.to || "").slice(0, 10))}"></label></div>
          <h4 style="margin:14px 0 4px">Overrides when it matches <small style="color:var(--p-muted)">(e.g. fee_pct, fee_fixed, base_fee, label, or any parameter the subject reads)</small></h4>
          <div id="reParams"></div><button type="button" class="p-btn sm" id="reAddParam">＋ Override</button>
          <label style="margin-top:12px"><span>Note</span><input id="reNote" value="${e(r.note || "")}" placeholder="Why this rule exists"></label>
          <label style="flex-direction:row;align-items:center;gap:8px"><input type="checkbox" id="reAct" ${r.active ? "checked" : ""} style="width:auto"> Active</label>
          <button class="p-btn primary" id="reSave">Save rule</button>
        </div>`);
      const params = Object.entries(r.params || {});
      const drawParams = () => {
        f.querySelector("#reParams").innerHTML = params.map(([k, v], i) => `<div style="display:flex;gap:6px;margin-bottom:6px"><input data-pk="${i}" value="${e(k)}" placeholder="parameter" style="flex:1"><input data-pv="${i}" value="${e(v)}" placeholder="value" style="flex:1"><button type="button" class="p-btn sm danger" data-px="${i}">✕</button></div>`).join("");
        f.querySelectorAll("[data-pk]").forEach(x => x.oninput = () => { params[x.dataset.pk][0] = x.value; });
        f.querySelectorAll("[data-pv]").forEach(x => x.oninput = () => { params[x.dataset.pv][1] = x.value; });
        f.querySelectorAll("[data-px]").forEach(x => x.onclick = () => { params.splice(Number(x.dataset.px), 1); drawParams(); });
      };
      drawParams();
      f.querySelector("#reAddParam").onclick = () => { params.push(["", ""]); drawParams(); };
      const fillSubjects = async () => {
        const type = f.querySelector("#reType").value;
        const list = await subjectsOf(type).catch(() => []);
        const cur = type === r.subject_type ? r.subject : "*";
        f.querySelector("#reSubj").innerHTML = `<option value="*">✱ every ${e(typeName(type).toLowerCase())}</option>` + list.map(x => `<option value="${e(x.key)}" ${x.key === cur ? "selected" : ""}>${e(x.name)}</option>`).join("");
      };
      f.querySelector("#reType").onchange = fillSubjects;
      await fillSubjects();
      f.querySelector("#reSave").onclick = async () => {
        const scopeOut = {};
        f.querySelectorAll("[data-dim]").forEach(el => { const v = readDim(el); if (v.length) scopeOut[el.dataset.dim] = v; });
        const num = id => { const v = f.querySelector(id).value; return v === "" ? undefined : Number(v); };
        if (num("#reMin") != null) scopeOut.min_amount = num("#reMin");
        if (num("#reMax") != null) scopeOut.max_amount = num("#reMax");
        if (f.querySelector("#reCur").value.trim()) scopeOut.amount_currency = f.querySelector("#reCur").value.trim().toUpperCase();
        if (f.querySelector("#reFrom").value) scopeOut.from = f.querySelector("#reFrom").value;
        if (f.querySelector("#reTo").value) scopeOut.to = f.querySelector("#reTo").value;
        const p = {}; for (const [k, v] of params) if (k.trim()) p[k.trim()] = v !== "" && isFinite(Number(v)) ? Number(v) : v;
        const body = { rule: { id: rule ? rule.id : undefined, subject_type: f.querySelector("#reType").value, subject: f.querySelector("#reSubj").value, effect: f.querySelector("#reEff").value,
          priority: Number(f.querySelector("#rePri").value) || 0, scope: scopeOut, params: p, note: f.querySelector("#reNote").value, active: f.querySelector("#reAct").checked } };
        try { await api(base, "POST", body); f.remove(); await load(); draw(); } catch (err) { alert(err.message); }
      };
    }

    /* the "why" view: every subject of a type, decided in a context the operator describes */
    function explain() {
      const d = st.data;
      const dims = d.schema.dimensions;
      const f = overlay(`<div class="p-modal-head"><h3>Explain — what is offered, and why</h3><button data-rclose>✕</button></div>
        <div class="p-form">
          <label><span>Subject type</span><select id="exType">${d.schema.subjectTypes.map(t => `<option value="${e(t.key)}" ${t.key === (st.type || "gateway") ? "selected" : ""}>${e(t.name)}</option>`).join("")}</select></label>
          ${dims.map(dm => {
            const multi = dm.match === "any";
            if (dm.options && dm.options.length) return `<label><span>${e(dm.name)}</span><select data-xf="${e(dm.fact)}" ${multi ? "multiple size=4" : ""}>${multi ? "" : `<option value="">(${dm.source === "platform" ? "this platform's own" : "not known"})</option>`}${dm.options.map(o => `<option value="${e(o.key)}">${e(o.name)}</option>`).join("")}</select></label>`;
            return `<label><span>${e(dm.name)}</span><input data-xf="${e(dm.fact)}" placeholder="(not known)"></label>`;
          }).join("")}
          <div class="row"><label><span>Amount</span><input id="exAmt" type="number" step="any" placeholder="(not known)"></label><label><span>Date</span><input id="exAt" type="date"></label></div>
          <button class="p-btn primary" id="exGo">Explain</button>
          <div id="exOut" style="margin-top:12px"></div>
        </div>`);
      f.querySelector("#exGo").onclick = async () => {
        const ctx = {};
        f.querySelectorAll("[data-xf]").forEach(el => { const v = el.tagName === "SELECT" && el.multiple ? [...el.selectedOptions].map(o => o.value) : el.value.trim(); if (Array.isArray(v) ? v.length : v) ctx[el.dataset.xf] = v; });
        if (f.querySelector("#exAmt").value !== "") ctx.amount = Number(f.querySelector("#exAmt").value);
        if (f.querySelector("#exAt").value) ctx.at = f.querySelector("#exAt").value + "T12:00:00";
        try {
          const r = await api(base + "/explain", "POST", { type: f.querySelector("#exType").value, context: ctx });
          f.querySelector("#exOut").innerHTML = `<table class="p-table"><thead><tr><th>Subject</th><th>Verdict</th><th>Why</th></tr></thead><tbody>
            ${r.results.map(x => `<tr><td>${e(x.name)}</td><td>${chip(x.verdict, VERDICT_STYLE[x.verdict])}${x.priority ? " ↑" + e(x.priority) : ""}</td><td style="font-size:12.5px">${e(x.reasons.join("; ") || "no rule applies")}${Object.keys(x.params || {}).length ? "<br><small>overrides: " + e(Object.entries(x.params).map(([k, v]) => k + "=" + v).join(", ")) + "</small>" : ""}</td></tr>`).join("")}
          </tbody></table>`;
        } catch (err) { f.querySelector("#exOut").textContent = err.message; }
      };
    }

    root.innerHTML = `<div class="p-card">Loading rules…</div>`;
    try { await load(); await draw(); } catch (err) { root.innerHTML = `<div class="p-card">${e(err.message)}</div>`; }
  }
  return { mount };
})();

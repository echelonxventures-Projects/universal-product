/* LUXORA Platform — the campaigns domain's store-console screen (lib/campaigns.js; _registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope. Draft a campaign, see who it
   would reach and who it would skip and why, send or schedule it, and follow what happened. */
"use strict";

let cmpOpen = null;
async function vCampaigns() {
  const [r, cos] = await Promise.all([api("/admin/campaigns"), api("/admin/crm/companies").catch(() => ({ companies: [] }))]);
  const open = cmpOpen ? await api("/admin/campaigns/" + cmpOpen).catch(() => null) : null, c = open && open.campaign;
  const pv = c && c.actions.includes("send") ? await api("/admin/campaigns/" + c.id + "/preview").catch(() => null) : null;
  const detail = c ? `<div class="a-card"><h3>${esc(c.ref)} · ${esc(c.name)} ${coBadge(c.status)}</h3>
    <p class="a-sub">${esc(c.channel)} · <span class="a-chip">${c.sent} sent</span> <span class="a-chip">${c.skipped} skipped</span> <span class="a-chip">${c.failed} failed</span> <span class="a-chip">${c.unsubscribed} unsubscribed</span>${c.opened != null ? ` <span class="a-chip">${c.opened} opened${c.openRate != null ? " · " + c.openRate + "%" : ""}</span> <span class="a-chip">${c.clicked} clicked${c.clickRate != null ? " · " + c.clickRate + "%" : ""}</span>` : ""}${c.left ? ` <span class="p-tag">${c.left} still to go</span>` : ""}</p>
    ${pv ? `<p class="a-sub"><b>${pv.reach}</b> people would get it now. ${Object.entries(pv.skipped).map(([k, n]) => `<span class="p-tag">${n} skipped: ${esc(k)}</span>`).join(" ")}</p>` : ""}
    ${c.reasons.length ? `<p class="a-sub">${c.reasons.map(x => `<span class="a-chip">${x.n} · ${esc(x.reason)}</span>`).join(" ")}</p>` : ""}
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      ${c.actions.includes("send") ? `<button class="p-btn sm primary" data-cmp-act="send">Send now</button>` : ""}
      ${c.actions.includes("continue") ? `<button class="p-btn sm primary" data-cmp-act="send">Send the next batch</button>` : ""}
      ${c.actions.includes("schedule") ? `<label><span>Send at</span><input id="cmpAt" type="datetime-local"></label><button class="p-btn sm" data-cmp-act="schedule">Schedule</button>` : ""}
      ${c.actions.includes("cancel") ? `<button class="p-btn sm" data-cmp-act="cancel">Cancel</button>` : ""}</div></div>` : "";
  return `<div class="a-head"><h2>📣 Campaigns</h2><p class="a-sub">Messages to your customers and contacts — only to those who agreed to marketing, checked again just before each message, each with its own unsubscribe link.</p></div>
  <div class="a-card"><h3>New campaign</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px">
      <label><span>Name</span><input id="cmpName" maxlength="160"></label>
      <label><span>Channel</span><select id="cmpCh">${r.channels.map(k => `<option value="${esc(k)}">${esc(k)}</option>`).join("")}</select></label>
      <label><span>Audience</span><select id="cmpAud">${Object.entries(r.audiences).map(([k, a]) => `<option value="${esc(k)}">${esc(a.label)}</option>`).join("")}</select></label>
      <label><span>Segment</span><select id="cmpSeg"><option value="">—</option>${r.segments.map(x => `<option value="${esc(x.segment)}">${esc(x.segment)} · ${x.n}</option>`).join("")}</select></label>
      <label><span>Company</span><select id="cmpCo"><option value="">—</option>${cos.companies.map(x => `<option value="${x.id}">${esc(x.name)}</option>`).join("")}</select></label>
      <label><span>Subject</span><input id="cmpSub" maxlength="200" placeholder="{name}, something new at {store}"></label></div>
    <label style="display:block;margin-top:8px"><span>Message</span><textarea id="cmpBody" rows="4" maxlength="8000" style="width:100%" placeholder="Hello {name}, …"></textarea></label>
    <button class="p-btn sm primary" id="cmpGo" style="margin-top:8px">Draft the campaign</button></div>
  ${detail}
  <div class="a-card"><h3>Campaigns</h3>${coTbl(["campaign", "channel", "sent", "skipped", "status", ""], r.campaigns, x => [`<code>${esc(x.ref)}</code> ${esc(x.name)}`, esc(x.channel), x.sent, x.skipped, coBadge(x.status), `<button class="p-btn sm" data-cmp-open="${x.id}">Open</button>`], "No campaigns yet.")}</div>`;
}
function wireCampaigns() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  document.querySelectorAll("[data-cmp-open]").forEach(b => b.onclick = () => { cmpOpen = b.dataset.cmpOpen; render(); });
  const g = $("#cmpGo"); if (g) g.onclick = () => go(async () => {
    const r = await api("/admin/campaigns", "POST", { name: $("#cmpName").value, channel: $("#cmpCh").value, subject: $("#cmpSub").value, body: $("#cmpBody").value,
      audience: { kind: $("#cmpAud").value, segment: $("#cmpSeg").value || undefined, company_id: Number($("#cmpCo").value) || undefined } });
    cmpOpen = r.campaign.id;
  }, "Drafted");
  document.querySelectorAll("[data-cmp-act]").forEach(b => b.onclick = () => go(() => api("/admin/campaigns/" + cmpOpen + "/" + b.dataset.cmpAct, "POST", b.dataset.cmpAct === "schedule" ? { at: $("#cmpAt").value } : {}), "Done"));
}
screen("campaigns", { render: async () => await vCampaigns(), wire: wireCampaigns });

/* ========== journeys (lib/journeys.js): messages sent on their own, step by step ==========
   What starts a journey, what ends it early, and each step's channel and wait are the engine's
   vocabulary; what may be done with a journey is the actions it answered. */
let jrOpen = null, jrSteps = null;
const jrBlank = () => ({ wait_minutes: 0, channel: "email", subject: "", body: "" });
async function vJourneys() {
  const r = await api("/admin/journeys");
  const open = jrOpen ? await api("/admin/journeys/" + jrOpen).catch(() => null) : null, j = open && open.journey;
  if (!jrSteps) jrSteps = [jrBlank()];
  const chOpts = v => r.channels.map(k => `<option value="${esc(k)}"${k === v ? " selected" : ""}>${esc(k)}</option>`).join("");
  const many = jrSteps.length > 1, room = jrSteps.length < r.maxSteps;
  const stepRow = (st, k) => `<div class="a-card" data-jr-step="${k}"><h4>Step ${k + 1}</h4><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px">
      <label><span>${k ? "Wait after the step before (hours)" : "Wait after they enter (hours)"}</span><input type="number" min="0" step="0.25" data-jr-f="wait" value="${(st.wait_minutes / 60) || 0}"></label>
      <label><span>Channel</span><select data-jr-f="channel">${chOpts(st.channel)}</select></label>
      <label><span>Subject</span><input data-jr-f="subject" maxlength="200" value="${esc(st.subject)}"></label></div>
      <label style="display:block;margin-top:6px"><span>Message</span><textarea data-jr-f="body" rows="3" maxlength="8000" style="width:100%">${esc(st.body)}</textarea></label>
      ${many ? `<button class="p-btn sm" data-jr-del="${k}">Remove this step</button>` : ""}</div>`;
  const detail = j ? `<div class="a-card"><h3>${esc(j.ref)} · ${esc(j.name)} ${coBadge(j.status)}</h3>
    <p class="a-sub">Starts when: <b>${esc(j.trigger.label)}</b>${j.exit_on.length ? " · ends early on: " + j.exit_on.map(esc).join(", ") : ""}${j.segment ? " · only segment " + esc(j.segment) : ""}${j.reenter ? " · each time" : " · once per person"}</p>
    <p class="a-sub"><span class="a-chip">${j.entered} entered</span> <span class="a-chip">${j.people.active} in it now</span> <span class="a-chip">${j.people.done} finished</span> <span class="a-chip">${j.people.stopped} left early</span></p>
    ${coTbl(["step", "wait", "channel", "subject", "sent", "opened", "clicked", "unsubscribed"], j.steps, (st, k) => [k + 1, (st.wait_minutes / 60).toFixed(st.wait_minutes % 60 ? 2 : 0) + " h", esc(st.channel), esc(st.subject || "—"), st.sent + (st.failed ? ` <span class="p-tag">${st.failed} failed</span>` : ""),
      st.opened + (st.openRate != null ? ` · ${st.openRate}%` : ""), st.clicked + (st.clickRate != null ? ` · ${st.clickRate}%` : ""), st.unsubscribed], "")}
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end;margin-top:8px">
      ${j.actions.includes("start") ? `<button class="p-btn sm primary" data-jr-act="start">Start</button>` : ""}
      ${j.actions.includes("pause") ? `<button class="p-btn sm" data-jr-act="pause">Pause</button>` : ""}
      ${j.actions.includes("end") ? `<button class="p-btn sm" data-jr-act="end">End for good</button>` : ""}
      ${j.actions.includes("enrol") ? `<label><span>Enrol</span><select id="jrAud">${Object.entries(r.audiences).filter(([, a]) => !a.needs || a.needs === "segment").map(([k, a]) => `<option value="${esc(k)}">${esc(a.label)}</option>`).join("")}</select></label><label><span>Segment</span><select id="jrAudSeg"><option value="">—</option>${r.segments.map(x => `<option value="${esc(x.segment)}">${esc(x.segment)}</option>`).join("")}</select></label><button class="p-btn sm primary" data-jr-act="enrol">Enrol them</button>` : ""}
      ${j.editable ? `<button class="p-btn sm" id="jrEdit">Edit steps</button>` : ""}</div>
    <h4 style="margin-top:12px">People</h4>${coTbl(["person", "step", "next", "status", "why"], open.people, x => [esc(x.name || x.person), x.step + 1, esc(x.next_at || "—"), coBadge(x.status), esc(x.reason || x.source || "")], "Nobody has entered yet.")}</div>` : "";
  return `<div class="a-head"><h2>🧭 Journeys</h2><p class="a-sub">Messages sent on their own when something happens — an account created, an order, a delivery, a cart left behind — or to an audience you enrol, step by step. Only to people who agreed to marketing, at most a few a day, each with its own unsubscribe link; opens (email) and clicks are counted.</p></div>
  <div class="a-card"><h3>${jrOpen && j && j.editable && jrSteps.edit ? "Change " + esc(j.ref) : "New journey"}</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px">
      <label><span>Name</span><input id="jrName" maxlength="160" value="${jrSteps.edit && j ? esc(j.name) : ""}"></label>
      <label><span>Starts when</span><select id="jrTrig">${Object.entries(r.triggers).map(([k, t]) => `<option value="${esc(k)}"${jrSteps.edit && j && j.trigger_on === k ? " selected" : ""}>${esc(t.label)}</option>`).join("")}</select></label>
      <label><span>Only segment</span><select id="jrSeg"><option value="">everyone</option>${r.segments.map(x => `<option value="${esc(x.segment)}">${esc(x.segment)} · ${x.n}</option>`).join("")}</select></label>
      <label><span>Each time it happens (not once)</span><input type="checkbox" id="jrRe"></label></div>
    <fieldset style="border:0;padding:0;margin:8px 0"><legend>Ends early when</legend>${r.exits.map(x => `<label style="margin-right:12px"><input type="checkbox" data-jr-exit="${esc(x)}"${jrSteps.edit && j && j.exit_on.includes(x) ? " checked" : ""}> ${esc(x)}</label>`).join("")}</fieldset>
    <p class="a-sub">{name} and {store} are filled in. Links in a message are tracked.</p>
    ${jrSteps.map(stepRow).join("")}
    <p>${room ? `<button class="p-btn sm" id="jrAdd">＋ Add a step</button> ` : ""}<button class="p-btn sm primary" id="jrGo">${jrSteps.edit ? "Save changes" : "Draft the journey"}</button> <button class="p-btn sm" id="jrRun">Send what is due now</button></p></div>
  ${detail}
  <div class="a-card"><h3>Journeys</h3>${coTbl(["journey", "starts when", "entered", "in it", "status", ""], r.journeys, x => [`<code>${esc(x.ref)}</code> ${esc(x.name)}`, esc(x.trigger.label), x.entered, x.people.active, coBadge(x.status), `<button class="p-btn sm" data-jr-open="${x.id}">Open</button>`], "No journeys yet.")}</div>`;
}
function wireJourneys() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  /* what is typed into the steps is kept as they are added or removed */
  const keep = () => document.querySelectorAll("[data-jr-step]").forEach(el => { const k = Number(el.dataset.jrStep), f = n => el.querySelector(`[data-jr-f="${n}"]`).value;
    jrSteps[k] = { wait_minutes: Math.round(Number(f("wait")) * 60) || 0, channel: f("channel"), subject: f("subject"), body: f("body") }; });
  document.querySelectorAll("[data-jr-open]").forEach(b => b.onclick = () => { jrOpen = b.dataset.jrOpen; jrSteps = null; render(); });
  document.querySelectorAll("[data-jr-del]").forEach(b => b.onclick = () => { keep(); const e = jrSteps.edit; jrSteps.splice(Number(b.dataset.jrDel), 1); jrSteps.edit = e; render(); });
  const add = $("#jrAdd"); if (add) add.onclick = () => { keep(); jrSteps.push({ ...jrBlank(), wait_minutes: 1440 }); render(); };
  const ed = $("#jrEdit"); if (ed) ed.onclick = async () => { const o = await api("/admin/journeys/" + jrOpen); jrSteps = o.journey.steps.map(x => ({ wait_minutes: x.wait_minutes, channel: x.channel, subject: x.subject, body: x.body })); jrSteps.edit = true; render(); };
  const g = $("#jrGo"); if (g) g.onclick = () => go(async () => {
    keep();
    const body = { name: $("#jrName").value, trigger: $("#jrTrig").value, segment: $("#jrSeg").value, reenter: $("#jrRe").checked,
      exit_on: [...document.querySelectorAll("[data-jr-exit]:checked")].map(x => x.dataset.jrExit), steps: jrSteps.map(x => ({ ...x })) };
    if (jrSteps.edit) await api("/admin/journeys/" + jrOpen, "PUT", body);
    else jrOpen = (await api("/admin/journeys", "POST", body)).journey.id;
    jrSteps = null;
  }, "Saved");
  const run = $("#jrRun"); if (run) run.onclick = () => go(async () => { const x = await api("/admin/journeys/run", "POST", {}); toast(`Sent ${x.sent} · ${x.entered} entered from carts`); });
  document.querySelectorAll("[data-jr-act]").forEach(b => b.onclick = () => {
    const act = b.dataset.jrAct;
    if (act === "end" && !confirm("End this journey for good? Nobody in it gets anything more.")) return;
    const body = act === "enrol" ? { audience: { kind: $("#jrAud").value, segment: $("#jrAudSeg").value || undefined } } : {};
    go(async () => { const x = await api("/admin/journeys/" + jrOpen + "/" + act, "POST", body); if (act === "enrol") toast(`${x.entered} entered · ${x.skipped} skipped`); }, act === "enrol" ? "" : "Done");
  });
}
screen("journeys", { render: async () => await vJourneys(), wire: wireJourneys });

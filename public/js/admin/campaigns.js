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
    <p class="a-sub">${esc(c.channel)} · <span class="a-chip">${c.sent} sent</span> <span class="a-chip">${c.skipped} skipped</span> <span class="a-chip">${c.failed} failed</span> <span class="a-chip">${c.unsubscribed} unsubscribed</span>${c.left ? ` <span class="p-tag">${c.left} still to go</span>` : ""}</p>
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

/* LUXORA Platform — the leave domain's store-console screen (lib/leave.js; _registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope. Ask for leave, decide requests,
   see a person's balance and who is away. */
"use strict";

let lvPerson = null;
/* what each action asks for first */
const lvAsk = { reject: "Why is it turned down?" };
async function vLeave() {
  const [r, cal, o] = await Promise.all([api("/admin/leave"), api("/admin/leave/calendar"), api("/admin/consulting").catch(() => ({ people: [] }))]);
  const bal = lvPerson ? await api("/admin/leave/people/" + lvPerson).catch(() => null) : null;
  const people = o.people.map(p => `<option value="${p.id}"${String(p.id) === String(lvPerson) ? " selected" : ""}>${esc(p.name)}</option>`).join("");
  const acts = x => x.actions.map(a => `<button class="p-btn sm" data-lv-act="${x.id}:${a}">${esc(a)}</button>`).join(" ");
  return `<div class="a-head"><h2>🌴 Leave</h2><p class="a-sub">Time away for your people: what each may take, requests and who decided them, and who is away. Approved days show in attendance — paid or unpaid — and come off the resource plan.</p></div>
  <div class="a-card"><h3>Ask for leave</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
    <label><span>Person</span><select id="lvP">${people}</select></label><label><span>Kind</span><select id="lvT">${r.types.map(t => `<option value="${esc(t.key)}">${esc(t.label)}</option>`).join("")}</select></label>
    <label><span>From</span><input id="lvF" type="date"></label><label><span>To</span><input id="lvTo" type="date"></label><label><span>Half a day</span><input id="lvH" type="checkbox"></label>
    <label><span>Reason</span><input id="lvR" maxlength="500"></label><button class="p-btn sm primary" id="lvGo">Ask</button><button class="p-btn sm" id="lvBal">Show balance</button></div></div>
  ${bal ? `<div class="a-card"><h3>Balance</h3>${coTbl(["kind", "entitled", "carried in", "taken", "waiting", "left"], bal.balance, b => [esc(b.label), b.limited ? b.entitled : "no limit", b.carried, b.taken, b.pending, b.limited ? `<b>${b.left}</b>` : "—"], "")}</div>` : ""}
  <div class="a-card"><h3>Requests</h3>${coTbl(["request", "person", "kind", "from", "to", "days", "status", ""], r.requests, x => [`<code>${esc(x.ref)}</code>`, esc(x.person), esc(x.label), esc(x.from_date), esc(x.to_date), x.days,
    coBadge(x.status) + (x.decision_note ? `<div class="a-sub">${esc(x.decision_note)}</div>` : ""), acts(x)], "No leave asked for yet.")}</div>
  <div class="a-card"><h3>Who is away</h3>${coTbl(["day", "away"], cal.calendar.filter(d => d.away.length), d => [esc(d.date), d.away.map(a => `<span class="a-chip">${esc(a.person)}${a.half ? " ½" : ""}${a.approved ? "" : " ?"}</span>`).join(" ")], "Nobody is away in the next four weeks.")}</div>`;
}
function wireLeave() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  const g = $("#lvGo"); if (g) g.onclick = () => go(() => api("/admin/leave", "POST", { employee_id: Number($("#lvP").value), type: $("#lvT").value, from_date: $("#lvF").value, to_date: $("#lvTo").value || undefined, half_day: $("#lvH").checked, reason: $("#lvR").value }), "Asked");
  const b = $("#lvBal"); if (b) b.onclick = () => { lvPerson = $("#lvP").value; render(); };
  document.querySelectorAll("[data-lv-act]").forEach(x => x.onclick = () => {
    const [id, act] = x.dataset.lvAct.split(":"), body = {};
    if (lvAsk[act]) { const note = prompt(lvAsk[act]); if (!note) return; body.note = note; }
    go(() => api(`/admin/leave/${id}/${act}`, "POST", body), "Done");
  });
}
screen("leave", { render: async () => await vLeave(), wire: wireLeave });

/* LUXORA Platform — the communication domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vConversations() {
  const gate = await coGate("conversations");
  if (!gate.any) return coOff("messages", "💬 Messages", gate.off);
  const all = window.__convAll ? 1 : 0;
  const d = await api("/admin/conversations", all ? { all: 1 } : {});
  return `<div class="a-head"><h2>💬 Messages</h2><p class="a-sub">Conversations with the store, and — where staff may read them — between shoppers. Subjects are the <code>conversationSubjects</code> registry; hiding contact details is the <code>conversations</code> capability's param.</p>
    <label><input type="checkbox" id="convAll" ${all ? "checked" : ""}> Show every conversation, not only the store's</label></div>
  <div class="a-card"><div class="a-tablewrap"><table class="a-table"><thead><tr><th>about</th><th>with</th><th>last</th><th>state</th><th></th></tr></thead><tbody>
    ${(d.conversations || []).map(c => `<tr><td>${esc(c.title)}</td><td>${esc(c.with)}</td><td>${esc(String(c.last_at).slice(0, 16))}</td><td>${stateChip(c.state)}${c.unread ? ` <span class="a-chip">${c.unread} new</span>` : ""}</td>
      <td style="white-space:nowrap"><button class="btn-white sm" data-conv-open="${c.id}">Open</button> ${(d.actions || []).filter(a => a.to !== c.status).map(a => `<button class="btn-white sm" data-co-post="/admin/conversations/${c.id}" data-co-body='${esc(JSON.stringify({ action: a.verb }))}'>${esc(a.verb)}</button>`).join(" ")}</td></tr>`).join("") || '<tr><td colspan="5">No conversations.</td></tr>'}</tbody></table></div></div>`;
}
function wireConversations() {
  const all = $("#convAll"); if (all) all.onchange = () => { window.__convAll = all.checked; render(); };
  $$("[data-conv-open]").forEach(b => b.onclick = async () => {
    const t = await api("/admin/conversations/" + b.dataset.convOpen, {});
    const m = modal(`<div class="p-modal-head"><h3>${esc(t.conversation.title)}</h3><button data-mclose>✕</button></div>
      <div style="max-height:50vh;overflow:auto">${t.messages.map(x => `<p style="margin:6px 0"><b>${esc(x.side)}</b> ${x.hidden ? "<i>(hidden)</i> " : ""}${esc(x.body)} <button class="btn-white sm" data-msg-hide="${x.id}" data-hidden="${x.hidden ? 0 : 1}">${x.hidden ? "Show" : "Hide"}</button></p>`).join("")}</div>
      ${t.conversation.side ? `<div class="p-form"><textarea id="convReply" rows="2"></textarea><button class="p-btn primary" id="convSend">Reply as the store</button></div>` : ""}`);
    m.querySelector("[data-mclose]").onclick = () => { m.innerHTML = ""; };
    m.querySelectorAll("[data-msg-hide]").forEach(h => h.onclick = async () => { await api("/admin/conversations/messages/" + h.dataset.msgHide, "POST", { hidden: h.dataset.hidden === "1" }); m.innerHTML = ""; toast("Updated"); });
    const send = m.querySelector("#convSend"); if (send) send.onclick = async () => { try { await api("/admin/conversations/" + t.conversation.id, "POST", { body: m.querySelector("#convReply").value }); m.innerHTML = ""; toast("Sent"); render(); } catch (e) { toast(e.message); } };
  });
  wireCoPosts();
}

screen("conversations", { group: "Customer Care", label: "💬 Messages", order: 1, render: async () => await vConversations(), wire: async () => { wireConversations(); } });

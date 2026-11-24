/* LUXORA Platform — the access domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ---------- Team & Roles (RBAC) ---------- */
/* this store's OWN role set — roles are per-store data. A store that has never edited its
   set inherits the platform default (ownSet false); the first edit forks it, and a fork can
   be dissolved back to the default. Defining a role is a team:write trust. */
async function vTeam() {
  const [r, s] = await Promise.all([api("/admin/roles"), api("/admin/staff")]);
  const roles = r.roles || [], secs = r.sections || [];
  const canEdit = (A.allowed || []).includes("*") || (A.allowed || []).includes("team");
  const row = u => `<tr><td><b>${esc(u.name)}</b><br><span class="p-tag">${esc(u.email)}</span></td>
    <td><select data-srole="${u.id}" ${String(u.id) === String(r.me.user.id) ? "disabled" : ""}>${roles.map(rl => `<option ${u.staff_role === rl.key ? "selected" : ""}>${esc(rl.key)}</option>`).join("")}</select></td>
    <td><span class="badge ${u.disabled ? "failed" : "published"}">${u.disabled ? "disabled" : "active"}</span></td>
    <td class="p-tag">${esc((u.last_login || "").slice(0, 16) || "never")}</td>
    <td style="text-align:right;white-space:nowrap"><button class="p-btn sm" data-sperm="${u.id}" title="Per-user overrides">Perms</button> ${String(u.id) !== String(r.me.user.id) ? `<button class="p-btn sm" data-smfa="${u.id}" ${String(u.id) === String(r.me.user.id) ? "disabled" : ""} title="For someone who lost their phone and recovery codes">Reset two-step</button> <button class="p-btn sm danger" data-sdel="${u.id}">Remove</button>` : ""}</td></tr>`;
  return `<div class="p-panel"><h2>👥 Team &amp; Roles</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Staff share the store-console admin login but see and can only edit the sections their <b>role</b> grants. This store's roles are its own data${r.ownSet ? "" : " — it currently inherits the platform default, and the first edit forks it"}; per-user permission overrides take precedence.</p>
    <h3>Role definitions (this store) ${r.ownSet ? '<span class="badge">forked from the platform default</span>' : '<span class="badge">platform default</span>'}</h3>
    <div style="display:flex;gap:8px;margin-bottom:8px">${canEdit ? `<button class="p-btn primary sm" id="roleNew">+ New role</button>` : ""}${r.ownSet && canEdit ? `<button class="p-btn sm" id="roleReset">Reset to platform default</button>` : ""}</div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Role</th><th>Grants (section: access)</th>${canEdit ? "<th></th>" : ""}</tr></thead><tbody>${roles.map(rl => `<tr><td><b>${esc(rl.name)}</b><br><code>${esc(rl.key)}</code></td><td class="p-tag">${Object.entries(rl.sections || {}).map(([k, v]) => `${esc(k)}=${esc(v)}`).join(" · ")}</td>${canEdit ? `<td style="text-align:right">${rl.key !== "owner" ? `<button class="p-btn sm" data-roleedit="${esc(rl.key)}">Edit</button>` : ""}</td>` : ""}</tr>`).join("")}</tbody></table></div>
    <h3>Members</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Member</th><th>Role</th><th>Status</th><th>Last login</th><th></th></tr></thead><tbody>${(s.staff || []).map(row).join("")}</tbody></table></div>
    <div class="p-panel" style="margin-top:10px"><b>Add staff member</b><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end;margin-top:6px">
      <label><span>Name</span><input id="stName"></label><label><span>Email</span><input id="stEmail"></label>
      <label><span>Role</span><select id="stRole">${roles.filter(rl => rl.key !== "owner").map(rl => `<option>${esc(rl.key)}</option>`).join("")}</select></label>
      <label><span>Password</span><input id="stPw" type="text" placeholder="blank = generate"></label>
      <button class="p-btn primary sm" id="stAdd">Add member</button><span id="stGen" class="p-tag"></span></div></div></div>`;
}
function wireTeam() {
  const $$ = s => Array.from(document.querySelectorAll(s));
  $$("[data-srole]").forEach(sel => sel.onchange = async () => { try { await api("/admin/staff/" + sel.dataset.srole, "PUT", { staff_role: sel.value }); toast("Role updated"); } catch (e) { toast(e.message); } });
  $$("[data-smfa]").forEach(b => b.onclick = async () => { if (!confirm("Reset this member's two-step sign-in? They are signed out and set it up again.")) return; try { await api("/admin/staff/" + b.dataset.smfa + "/mfa-reset", "POST", {}); toast("Two-step sign-in reset"); } catch (e) { toast(e.message); } });
  $$("[data-sdel]").forEach(b => b.onclick = async () => { if (!confirm("Disable this member?")) return; try { await api("/admin/staff/" + b.dataset.sdel, "DELETE"); render(); } catch (e) { toast(e.message); } });
  $$("[data-sperm]").forEach(b => b.onclick = async () => { const cur = prompt("Per-user overrides as JSON, e.g. {\"products\":\"read\",\"trash\":false}", "{}"); if (cur == null) return; try { await api("/admin/staff/" + b.dataset.sperm, "PUT", { perms: JSON.parse(cur) }); toast("Saved"); } catch (e) { toast(e.message); } });
  if (document.getElementById("stAdd")) document.getElementById("stAdd").onclick = async () => { try { const r = await api("/admin/staff", "POST", { name: document.getElementById("stName").value, email: document.getElementById("stEmail").value, staff_role: document.getElementById("stRole").value, password: document.getElementById("stPw").value || undefined }); if (r.generated) document.getElementById("stGen").textContent = "generated password: " + r.generated; toast("Member added"); render(); } catch (e) { toast(e.message); } };
  /* per-store role definition: create, edit, and dissolve a fork back to the default */
  const newBtn = document.getElementById("roleNew");
  if (newBtn) newBtn.onclick = async () => { const all = await api("/admin/roles"); roleModal(null, all.sections || [], all.apps); };
  $$("[data-roleedit]").forEach(b => b.onclick = async () => {
    const all = await api("/admin/roles");
    const role = (all.roles || []).find(r => r.key === b.dataset.roleedit);
    roleModal(role, all.sections || [], all.apps);
  });
  const resetBtn = document.getElementById("roleReset");
  if (resetBtn) resetBtn.onclick = async () => { if (!confirm("Discard this store's own roles and inherit the platform default again?")) return; try { await api("/admin/roles/reset", "POST", {}); toast("Reverted to the platform default"); render(); } catch (e) { toast(e.message); } };
}

screen("team", { group: "Team & Access", label: "👥 Team & Roles", order: 0, render: async () => await vTeam(), wire: async () => { wireTeam(); } });

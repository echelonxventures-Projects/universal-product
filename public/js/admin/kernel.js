/* LUXORA Platform — the kernel domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vStudio() {
  const defs = Object.fromEntries(Object.entries((await api("/meta/entities")).entities).filter(([, d]) => !d.platformOnly));
  const customs = await api("/meta/entity/custom_provider").catch(() => ({ rows: [] }));
  return `
  <div class="p-panel"><h2>Entity Studio</h2>
    <p class="p-tag">Browse and manage entity data for this store.</p>
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin:14px 0">${Object.entries(defs).map(([k, d]) => `<button class="p-btn sm ${k === A.studioSel ? "primary" : ""}" data-studio="${k}">${d.icon} ${esc(d.label)}</button>`).join("")}</div>
    <div id="studioBody">${A.studioSel ? await entityTable(A.studioSel) : '<div class="p-empty">Select an entity above</div>'}</div></div>`;
}
function wireStudio() {
  $$("[data-studio]").forEach(b => b.onclick = () => { A.studioSel = b.dataset.studio; render(); });
}

screen("studio", { group: "Settings", label: "🛠️ Data Studio", order: 3, render: async () => await vStudio(), wire: async () => { wireStudio(); } });

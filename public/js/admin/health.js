/* LUXORA Platform — the health domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vHealthRecords() {
  const gate = await coGate("healthrecords");
  if (!gate.any) return coOff("health records", "🩺 Health Records", gate.off);
  const party = hrParty;
  const d = await api("/admin/health-records/shared?party=" + encodeURIComponent(party), {}).catch(e => ({ shared: [], error: e.message }));
  return `<div class="a-head"><h2>🩺 Health Records</h2><p class="a-sub">Shoppers keep their records private and share one with a party for some days; a party sees only what is shared with it while the share lasts. Every share is recorded.</p></div>
  <div class="a-card"><div class="p-form"><div class="row"><label><span>Party (who it was shared with)</span><input id="hrParty" value="${esc(party)}"></label></div><button class="p-btn primary" id="hrLook">Show</button></div>
  <div class="a-tablewrap"><table class="a-table"><thead><tr><th>shopper</th><th>record</th><th>shared until</th></tr></thead><tbody>
  ${(d.shared || []).map(x => `<tr><td>${esc(x.owner)}</td><td>${x.item ? `<a href="${esc(x.item.url)}" target="_blank" rel="noopener">${esc(x.item.title)}</a>` : ""}</td><td>${esc(x.until)}</td></tr>`).join("") || `<tr><td colspan="3">${esc(d.error || (party ? "Nothing shared with this party." : "Name a party."))}</td></tr>`}</tbody></table></div></div>`;
}
function wireHealthRecords() { const b = $("#hrLook"); if (b) b.onclick = () => { hrParty = fieldVal("#hrParty"); render(); }; }

screen("prescriptions", { render: view => vCases(view), wire: () => wireCases() });
screen("credentials", { render: view => vCases(view), wire: () => wireCases() });
screen("labtests", { render: view => vDeliverables(view), wire: view => wireDeliverables(view) });
screen("healthrecords", { render: async () => await vHealthRecords(), wire: async () => { wireHealthRecords(); } });

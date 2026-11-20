/* LUXORA Platform — the reviews domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vUgc() {
  const [q, revs] = await Promise.all([api("/admin/ugc/queue", {}), api("/admin/reviews", {})]);
  const allR = revs.reviews || [];
  const byS = {}; allR.forEach(r => byS[r.state] = (byS[r.state] || 0) + 1);
  return `<div class="a-head"><h2>⭐ Reviews &amp; Q&amp;A</h2><p class="a-sub">Rich reviews (helpfulness votes, seller reply threads, media, moderation states) and product Q&amp;A. States &amp; roles are Data Studio registries: <code>ugcStates</code>, <code>ugcRoles</code>; behaviour toggles live in Settings → UGC.</p></div>
  <div class="a-card"><h3>Moderation queue · ${q.pending || 0} pending</h3>
    <p class="a-sub">${Object.entries(byS).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join("") || "no reviews"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>type</th><th>product</th><th>author</th><th>text</th><th>state</th></tr></thead>
      <tbody>${[
        ...q.reviews.map(r => ({ k: "review", p: r.product_id, a: r.name, t: (r.title + " — " + r.body).slice(0, 90), s: r.state, id: r.id })),
        ...q.questions.map(r => ({ k: "question", p: r.product_id, a: r.name, t: r.body.slice(0, 90), s: r.state, id: r.id })),
        ...q.answers.map(r => ({ k: "answer", p: r.product_id, a: r.name, t: r.body.slice(0, 90), s: r.state, id: r.id }))
      ].slice(0, 20).map(x => `<tr><td><span class="a-chip">${esc(x.k)}</span></td><td><code>${esc(x.p)}</code></td><td>${esc(x.a)}</td><td>${esc(x.t)}</td><td><span class="a-chip">${esc(x.s)}</span></td></tr>`).join("") || '<tr><td colspan="5">Queue is empty — everything published.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>Latest reviews</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>product</th><th>author</th><th>rating</th><th>helpful</th><th>state</th></tr></thead>
      <tbody>${allR.slice(0, 15).map(r => `<tr><td><code>${esc(r.product_id)}</code></td><td>${esc(r.name)}</td><td>${r.rating}★</td><td>${r.votes_helpful || 0}/${r.votes_total || 0}</td><td><span class="a-chip">${esc(r.state)}</span></td></tr>`).join("") || '<tr><td colspan="5">No reviews yet.</td></tr>'}</tbody></table></div>
  </div>`;
}

screen("ugc", { group: "Customer Care", label: "⭐ Reviews & Q&A", order: 2, render: async () => await vUgc() });

/* LUXORA Platform — the knowledge domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

screen("manual", { group: "Help", label: "📘 User Manual", order: 0, render: async () => { window.open("/docs/user-manual.html", "_blank"); return `<div class="p-empty">Loading…</div>`; } });
screen("architecture", { group: "Help", label: "🏛️ Architecture", order: 1, render: async () => { window.open("/docs/architecture.html", "_blank"); return `<div class="p-empty">Loading…</div>`; } });

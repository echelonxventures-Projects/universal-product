/* LUXORA Platform — the returns domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

screen("returns", { group: "Orders & Fulfilment", label: "↩️ Returns", order: 1, render: async () => await entityTable("ret") });

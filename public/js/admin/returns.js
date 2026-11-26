/* LUXORA Platform — the returns domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

screen("returns", { render: async () => await entityTable("ret") });

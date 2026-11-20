/* LUXORA Platform — the localisation domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

screen("localizations", { group: "Storefront", label: "🌐 Localizations", order: 3, render: async () => await entityTable("localization") });

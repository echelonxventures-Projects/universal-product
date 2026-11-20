/* LUXORA Platform — the product_options domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

screen("prodoptions", { group: "Catalogue", label: "🧩 Product Options", order: 5, render: view => vProdOptions(view), wire: () => wireProdOptions() });

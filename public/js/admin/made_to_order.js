/* LUXORA Platform — the made_to_order domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

screen("proofs", { render: view => vProdOptions(view), wire: () => wireProdOptions() });
screen("samples", { render: view => vProdOptions(view), wire: () => wireProdOptions() });

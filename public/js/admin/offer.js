/* LUXORA Platform — the offer domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its render,
   its wiring and its place in the Offers group of the nav. */
"use strict";

screen("pricematch", { render: vCases, wire: wireCases });
screen("tradeins", { render: vCases, wire: wireCases });

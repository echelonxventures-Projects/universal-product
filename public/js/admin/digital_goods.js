/* LUXORA Platform — the digital_goods domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

screen("licencekeys", { render: view => vDeliverables(view), wire: view => wireDeliverables(view) });
screen("courses", { render: view => vDeliverables(view), wire: view => wireDeliverables(view) });

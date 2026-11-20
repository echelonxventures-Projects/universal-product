/* LUXORA Platform — the digital_goods domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

screen("licencekeys", { group: "Orders & Fulfilment", label: "🔑 Licence Keys", order: 12, render: view => vDeliverables(view), wire: view => wireDeliverables(view) });
screen("courses", { group: "Orders & Fulfilment", label: "🎓 Course Progress", order: 14, render: view => vDeliverables(view), wire: view => wireDeliverables(view) });

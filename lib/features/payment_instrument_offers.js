/* payment offers: money off for paying a certain way */
"use strict";
const F = () => require("../features.js");
const fits = (r, b, net) => b.gateway && r.gateway === b.gateway && (!r.method || r.method === b.method) && net >= Number(r.min_amount || 0);
const worth = (r, net) => Math.min(net, net * r.percent / 100, r.max_off > 0 ? r.max_off : Infinity);
module.exports = {
  charges: ({ tid, net, body }) => { const r = F().rows(tid, "payment_instrument_offers").filter(x => fits(x, body || {}, net)).sort((a, b) => worth(b, net) - worth(a, net))[0]; return r ? [{ name: r.name, amount: -worth(r, net) }] : []; },
  open: ({ tid }) => ({ offers: F().rows(tid, "payment_instrument_offers").map(r => ({ name: r.name, gateway: r.gateway, method: r.method, percent: r.percent, max_off: r.max_off, min_amount: r.min_amount })) })
};

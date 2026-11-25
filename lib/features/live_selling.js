/* live selling: a show at a set time, its items at the show's price while it is on; the stream itself is
   the store's own (a link), never carried here */
"use strict";
const F = () => require("../features.js");
const ids = r => String(r.products || "").split(/[\s,]+/).filter(Boolean);
const on = r => { const n = new Date().toISOString(); return r.starts <= n && r.ends > n; };
const showOf = (tid, p) => F().rows(tid, "live_selling").find(r => on(r) && ids(r).includes(p.id));
module.exports = {
  check: (r, tid) => { if (r.ends <= r.starts) throw F().fail("It must end after it starts"); for (const id of ids(r)) if (!require("../db.js").get("SELECT 1 x FROM products WHERE tenant_id=? AND id=?", Number(tid), id)) throw F().fail("Unknown item: " + id); },
  price: ({ tid, product, unit }) => { const r = showOf(tid, product); return r && r.percent ? { unit: unit * (1 - r.percent / 100), label: "Live price" } : null; },
  block: ({ tid, product }) => { const r = showOf(tid, product); return r && { title: "Live now: " + r.name, text: r.percent ? r.percent + "% off while the show is on" : "", link: { label: "Watch", url: r.stream } }; },
  open: ({ tid }) => ({ shows: F().rows(tid, "live_selling").filter(r => r.ends > new Date().toISOString()).sort((a, b) => (a.starts < b.starts ? -1 : 1)).map(r => ({ id: r.id, name: r.name, starts: r.starts, ends: r.ends, live: on(r), stream: on(r) ? r.stream : null, products: ids(r), reminders: F().records(tid, "live_selling", { about: String(r.id) }).length })) }),
  actions: { remind: ({ tid, owner, body }) => { const r = F().rows(tid, "live_selling").find(x => x.id === Number(body.id) && x.ends > new Date().toISOString()); if (!r) throw F().fail("That show is over", 404); if (!F().records(tid, "live_selling", { owner, about: String(r.id) }).length) F().record(tid, "live_selling", { owner, about: r.id, state: "waiting" }); return { ok: true }; } },
  sweep: ({ tid }) => { for (const r of F().rows(tid, "live_selling").filter(on)) for (const x of F().records(tid, "live_selling", { about: String(r.id), state: "waiting" })) if (F().change(tid, "live_selling", x.id, "waiting", "told")) require("../tell.js").tell(tid, x.owner, "deal_alert", r.name + " is live", "The show you asked about has started.", r.stream); }
};

/* affiliate commissions: someone who sends a shopper earns a share of what they buy. The link carries
   the affiliate's code; the last one before the order counts; it is earned when the order is delivered
   and taken back if the order becomes void. Never on one's own order. */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js");
const row = (tid, code) => F().rows(tid, "affiliate_commissions").find(r => r.code.toLowerCase() === String(code || "").toLowerCase());
module.exports = {
  check: (r, tid) => { if (!/^[a-z0-9_-]{3,40}$/i.test(r.code)) throw F().fail("A code is 3 to 40 letters and digits"); if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(r.email)) throw F().fail("The email is not valid"); },
  actions: { visit: ({ tid, owner, body }) => { const r = row(tid, body.code); if (!r) return { ok: false }; for (const x of F().records(tid, "affiliate_commissions", { owner, state: "visit" })) F().forget(tid, "affiliate_commissions", x.id); F().record(tid, "affiliate_commissions", { owner, about: r.code, state: "visit" }); return { ok: true }; } },
  placed: ({ tid, owner, order }) => {
    const days = Number(F().params(tid, "affiliate_commissions").days) || 30, v = F().records(tid, "affiliate_commissions", { owner, state: "visit" })[0];
    if (!v || Date.now() - new Date(v.at.replace(" ", "T") + "Z") > days * 864e5) return;
    const r = row(tid, v.about), m = /:u:(\d+)$/.exec(owner), me = m && db().get("SELECT email FROM users WHERE id=?", Number(m[1]));
    const buyer = String((me && me.email) || order.email || "").toLowerCase();
    if (!r || buyer === r.email.toLowerCase()) return;
    const base = Math.max(0, (Number(order.sub) || 0) / (Number(order.fx) || 1));
    F().record(tid, "affiliate_commissions", { owner: "affiliate:" + r.code, about: order.num, state: "waiting", data: { code: r.code, email: r.email, amount: +(base * r.percent / 100).toFixed(2) } });
  },
  moved: ({ tid, order, to }) => { const st = require("../states.js"); for (const r of F().records(tid, "affiliate_commissions", { about: order.num })) { if (r.state === "waiting" && st.is("order", to, "fulfilled")) F().change(tid, "affiliate_commissions", r.id, "waiting", "earned"); else if (["waiting", "earned"].includes(r.state) && st.is("order", to, "void")) F().change(tid, "affiliate_commissions", r.id, r.state, "lost"); } },
  staff: {
    list: ({ tid }) => F().records(tid, "affiliate_commissions").filter(r => r.state !== "visit").map(r => ({ id: r.id, text: r.code + " (" + r.email + ") · " + r.about + " · " + r.amount, chip: r.state, actions: r.state === "earned" ? [{ key: "paid", label: "Mark paid", ask: "Payment reference" }] : [] })),
    actions: { paid: ({ tid, id, body }) => { if (!F().change(tid, "affiliate_commissions", id, "earned", "paid", { reference: String(body.value || "").slice(0, 80) })) throw F().fail("Not waiting to be paid", 409); return { ok: true }; } }
  }
};

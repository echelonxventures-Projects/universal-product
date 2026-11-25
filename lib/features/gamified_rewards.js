/* gamified rewards: a daily check-in earns a little credit, more for each day in a row up to a limit;
   once a day per shopper, however many times it is asked */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js");
const K = "gamified_rewards";
function streak(tid, owner) { let n = 0; for (let d = 1; d < 400; d++) { const day = new Date(Date.now() - d * 864e5).toISOString().slice(0, 10); if (!db().get("SELECT 1 x FROM feature_records WHERE tenant_id=? AND feature=? AND owner=? AND about=?", Number(tid), K, owner, day)) break; n++; } return n; }
const worth = (P, n) => +Math.min(Number(P.most), Number(P.first) + Number(P.more) * n).toFixed(2);
module.exports = {
  actions: { checkin: ({ tid, owner }) => {
    if (!/:u:/.test(owner || "")) throw F().fail("Sign in to check in", 401);
    const P = F().params(tid, K), day = F().today();
    return require("../kernel.js").internal.tx(() => {
      if (F().records(tid, K, { owner, about: day }).length) throw F().fail("You have already checked in today", 409);
      const n = streak(tid, owner), amt = worth(P, n);
      F().record(tid, K, { owner, about: day, state: "claimed", data: { amount: amt } });
      if (amt > 0) require("../offers.js").credit(Number(tid), owner, amt, "reward", "checkin:" + day, null, "rewards");
      return { ok: true, amount: amt, streak: n + 1, message: "+" + amt + " — day " + (n + 1) + " in a row" };
    });
  } },
  mine: ({ tid, owner }) => { if (!/:u:/.test(owner || "")) return []; const done = F().records(tid, K, { owner, about: F().today() })[0], n = streak(tid, owner), P = F().params(tid, K); return [{ text: done ? "Checked in today · day " + (n + 1) + " in a row · tomorrow +" + worth(P, n + 1) : "Check in today for +" + worth(P, n), actions: done ? [] : [{ label: "Check in", path: "/features/" + K + "/checkin" }] }]; }
};

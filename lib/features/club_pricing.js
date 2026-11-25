/* club pricing: members of a tier pay less */
"use strict";
const F = () => require("../features.js");
const tierOf = (tid, owner) => { try { const m = require("../recurring.js").membershipOf(tid, owner); return m && m.benefits && m.status !== "none" ? m.tier : null; } catch (e) { return null; } };
const best = (tid, owner, p) => { const t = owner && tierOf(tid, owner); return t ? F().rows(tid, "club_pricing").filter(r => (r.tier === "*" || r.tier === t) && F().names(r, p)).sort((a, b) => b.percent - a.percent)[0] : null; };
module.exports = {
  price: ({ tid, owner, product, unit }) => { const r = best(tid, owner, product); return r && { unit: unit * (1 - r.percent / 100), label: "Member price" }; },
  block: ({ tid, owner, product }) => { const mine = best(tid, owner, product); if (mine) return { title: "Member price", text: mine.percent + "% off with your membership" }; const any = F().rows(tid, "club_pricing").filter(r => F().names(r, product)).sort((a, b) => b.percent - a.percent)[0]; return any && { title: "Member price", text: "Members save " + any.percent + "%" }; }
};

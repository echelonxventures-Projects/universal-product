/* kitchen hours: when food can be ordered, by the store's own clock; outside them it cannot */
"use strict";
const F = () => require("../features.js"), K = "kitchen_hours";
const m = t => Number(t.slice(0, 2)) * 60 + Number(t.slice(3));
function now(tid) { const T = require("../time.js"); try { const w = T.wallClock(new Date(), T.zoneOfStore(Number(tid))); return { dow: new Date(Date.UTC(w.year, w.month - 1, w.day)).getUTCDay(), min: w.hour * 60 + (w.minute || 0) }; } catch (e) { const d = new Date(); return { dow: d.getUTCDay(), min: d.getUTCHours() * 60 + d.getUTCMinutes() }; } }
/* a window that closes after midnight belongs to the day it opens */
function isOpen(rs, n) { return rs.some(r => m(r.closes) > m(r.opens) ? r.weekday === n.dow && n.min >= m(r.opens) && n.min < m(r.closes) : (r.weekday === n.dow && n.min >= m(r.opens)) || ((r.weekday + 1) % 7 === n.dow && n.min < m(r.closes))); }
const nextOpen = (rs, n) => { for (let d = 0; d < 8; d++) { const o = rs.filter(r => r.weekday === (n.dow + d) % 7 && (d || m(r.opens) > n.min)).sort((a, b) => m(a.opens) - m(b.opens))[0]; if (o) return (d === 0 ? "today" : d === 1 ? "tomorrow" : "in " + d + " days") + " at " + o.opens; } return ""; };
const forP = (tid, p) => F().rows(tid, K).filter(r => F().names(r, { id: p.id, brand: p.brand || p.b, dept: p.dept || p.d }));
module.exports = {
  isOpen, nextOpen,
  rule: ({ tid, product }) => { const rs = forP(tid, product), n = now(tid); return rs.length && !isOpen(rs, n) ? { problem: "the kitchen is closed — it opens " + nextOpen(rs, n) } : null; },
  block: ({ tid, product }) => { const rs = forP(tid, product), n = now(tid); return rs.length ? { title: isOpen(rs, n) ? "Kitchen open" : "Kitchen closed", text: isOpen(rs, n) ? "" : "Opens " + nextOpen(rs, n) } : null; }
};

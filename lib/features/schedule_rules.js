/* schedule rules: what a medicine's schedule allows — whether it may be sold here at all, whether it
   needs an approved prescription, and how much of it at once */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js"), K = "schedule_rules";
const J = v => { try { return typeof v === "string" ? JSON.parse(v || "{}") : v || {}; } catch (e) { return {}; } };
const of = (tid, p) => { const s = String(J(p.attrs)[F().params(tid, K).attr] || "").toLowerCase(); return s ? F().rows(tid, K).find(r => r.schedule.toLowerCase() === s) : null; };
const full = (tid, p) => p.attrs !== undefined ? p : db().get("SELECT * FROM products WHERE tenant_id=? AND id=?", Number(tid), p.id) || p;
const hasRx = (tid, owner, id) => { try { return require("../cases.js").validFor(tid, owner, F().params(tid, K).case_kind, id).length > 0; } catch (e) { return false; } };
module.exports = {
  rule: ({ tid, owner, product }) => { const p = full(tid, product), r = of(tid, p); if (!r) return null; if (!r.sold) return { problem: "this schedule of medicine is not sold here" }; if (r.prescription && !hasRx(tid, owner, p.id)) return { problem: "an approved prescription is needed" }; return r.max_qty ? { maxQty: r.max_qty } : null; },
  block: ({ tid, owner, product }) => { const r = of(tid, full(tid, product)); return r && { title: "Schedule " + r.schedule, text: !r.sold ? "Not sold here" : (r.prescription ? (hasRx(tid, owner, product.id) ? "Your prescription is approved" : "Needs an approved prescription") : "No prescription needed") + (r.max_qty ? " · at most " + r.max_qty : "") }; }
};

/* LUXORA Platform — Experimentation (A/B testing).
   Experiments with weighted variants; assignment is deterministic per
   (experiment, subject) via a stable hash, so a returning customer always sees the same
   variant. Conversion events are tracked per variant and a simple significance readout
   (two-proportion z-test) is computed on demand. Variants and statuses are meta_lists
   registries (expStatuses). Feature-gated by settings.features.experiments. */
"use strict";

const db = () => require("./db.js");
/* an experiment is a state machine (lib/states.js): it is live when its state says so */
const states = require("./states.js");
const inList = (machine, tag) => { const xs = states.tagged(machine, tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const crypto = require("crypto");

const STATUSES = ["draft", "running", "paused", "completed"];

function seed() {
  const D = db();
  const existing = D.get("SELECT items FROM meta_lists WHERE name='expStatuses'");
  const cur = existing ? JSON.parse(existing.items || "[]") : [];
  for (const it of STATUSES.map(k => ({ key: k, name: k }))) if (!cur.some(x => x.key === it.key)) cur.push(it);
  if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), "expStatuses");
  else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", "expStatuses", "Experiments · Statuses", JSON.stringify(cur));
}

/* deterministic bucket: same subject + experiment → same variant, forever */
function bucket(experimentKey, subject) {
  const buf = crypto.createHash("sha256").update(experimentKey + "|" + subject).digest();
  return buf.readUInt32BE(0) / 0x100000000;       /* 0..1 */
}

function createExperiment(tenantId, input) {
  const D = db();
  const variants = (Array.isArray(input.variants) ? input.variants : [])
    .filter(v => v && v.key && Number(v.weight) > 0)
    .map(v => ({ key: String(v.key), name: String(v.name || v.key), weight: Number(v.weight), payload: v.payload == null ? null : v.payload }));
  if (variants.length < 2) throw new Error("An experiment needs at least 2 weighted variants");
  const total = variants.reduce((n, v) => n + v.weight, 0);
  const r = D.run("INSERT INTO experiments(tenant_id,key,name,variants,status,metric,started_at) VALUES(?,?,?,?,?,?, NULL)",
    tenantId, String(input.key), String(input.name || input.key), JSON.stringify(variants.map(v => ({ ...v, share: +(v.weight / total).toFixed(4) }))), states.initial("experiment"), String(input.metric || "conversion"));
  return experimentById(D, tenantId, Number(r.lastInsertRowid));
}

function experimentById(D, tenantId, id) {
  const e = D.get("SELECT * FROM experiments WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (e) e.variants = JSON.parse(e.variants || "[]");
  return e;
}

function experimentByKey(D, tenantId, key) {
  const e = D.get("SELECT * FROM experiments WHERE key=? AND tenant_id=?", String(key), tenantId);
  if (e) e.variants = JSON.parse(e.variants || "[]");
  return e;
}

function setStatus(tenantId, id, status) {
  const D = db();
  if (!states.has("experiment", status)) throw new Error("Unknown experiment status: " + status);
  const e = experimentById(D, tenantId, id);
  if (!e) throw new Error("Unknown experiment " + id);
  /* the machine writes the start / end time each state declares, once */
  const { patch } = states.apply("experiment", { tenantId, from: e.status, to: status, row: e });
  D.run("UPDATE experiments SET " + Object.keys(patch).map(k => k + "=?").join(", ") + " WHERE id=? AND tenant_id=?", ...Object.values(patch), id, tenantId);
  return experimentById(D, tenantId, id);
}

/* assign a subject; returns the variant (creates the assignment row on first touch) */
function assign(tenantId, key, subject) {
  const D = db();
  const e = experimentByKey(D, tenantId, key);
  if (!e) return null;
  if (!states.has("experiment", e.status) || !states.is("experiment", e.status, "live")) return null;
  const existing = D.get("SELECT variant FROM exp_assignments WHERE experiment_id=? AND subject=?", e.id, String(subject));
  if (existing) return e.variants.find(v => v.key === existing.variant) || null;
  const roll = bucket(e.key, subject);
  let acc = 0, chosen = e.variants[0];
  for (const v of e.variants) { acc += v.weight; if (roll <= acc / e.variants.reduce((n, x) => n + x.weight, 0)) { chosen = v; break; } }
  D.run("INSERT OR IGNORE INTO exp_assignments(experiment_id,tenant_id,subject,variant) VALUES(?,?,?,?)", e.id, tenantId, String(subject), chosen.key);
  return chosen;
}

function convert(tenantId, key, subject, value) {
  const D = db();
  const e = experimentByKey(D, tenantId, key);
  if (!e) return null;
  const a = D.get("SELECT variant FROM exp_assignments WHERE experiment_id=? AND subject=?", e.id, String(subject));
  if (!a) return null;                          /* subject was never assigned */
  D.run("INSERT INTO exp_conversions(experiment_id,tenant_id,variant,subject,value) VALUES(?,?,?,?,?)",
    e.id, tenantId, a.variant, String(subject), Number(value) || 1);
  return { variant: a.variant, value: Number(value) || 1 };
}

/* results per variant + a two-proportion z-test against the control */
function results(tenantId, id) {
  const D = db();
  const e = experimentById(D, tenantId, id);
  if (!e) return null;
  const n = v => D.get("SELECT COUNT(*) c FROM exp_assignments WHERE experiment_id=? AND variant=?", e.id, v).c;
  const k = v => D.get("SELECT COUNT(DISTINCT subject) c FROM exp_conversions WHERE experiment_id=? AND variant=?", e.id, v).c;
  const rate = (kk, nn) => nn ? kk / nn : 0;
  const variants = e.variants.map(v => ({ ...v, assigned: n(v.key), converted: k(v.key), rate: +rate(k(v.key), n(v.key)).toFixed(4) }));
  const ctrl = variants[0];
  const out = variants.map(v => {
    let z = null, sig = false;
    if (ctrl && v.key !== ctrl.key && ctrl.assigned > 0 && v.assigned > 0) {
      const p1 = rate(ctrl.converted, ctrl.assigned), p2 = rate(v.converted, v.assigned);
      const p = (ctrl.converted + v.converted) / (ctrl.assigned + v.assigned);
      const se = Math.sqrt(p * (1 - p) * (1 / ctrl.assigned + 1 / v.assigned));
      z = se ? (p2 - p1) / se : 0;
      sig = Math.abs(z) >= 1.96;                /* 95% confidence */
    }
    return { ...v, lift: ctrl && ctrl.rate ? +((v.rate - ctrl.rate) / ctrl.rate).toFixed(4) : 0, z: z == null ? null : +z.toFixed(3), significant: sig };
  });
  return { experiment: e, variants: out };
}

function listExperiments(tenantId) {
  const D = db();
  return D.all("SELECT * FROM experiments WHERE tenant_id=? ORDER BY id DESC", tenantId).map(e => ({ ...e, variants: JSON.parse(e.variants || "[]") }));
}

module.exports = {
  seed, STATUSES,
  createExperiment, setStatus, assign, convert, results, listExperiments
};

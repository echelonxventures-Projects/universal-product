/* UCOS Ω∞ · per-domain record engine audit.
   --------------------------------------------------------------------------
   test/ucos-universes.js proves every universe is INSTANTIATED; test/ucos-activation.js
   proves every family is TRANSACTABLE. This proves the last inch: every universe is a
   DOMAIN — its records are driven by a state machine the CORPUS declares, with rules
   that bite and an append-only ledger, and no universe-specific code anywhere.

   The machine is derived from the corpus's own declarations:
     UCOS 5.1      the lifecycle states (read out of Architecture3, never hardcoded)
     UCOS 5.2      the transition rules — Canonical requires certification; Retired
                   requires every dependent retired first
     UMQSOCR 10    the transition grammar — Source/Target/Rule/Trigger/Conditions/Effects

   Proves, across multiple universes (not the one the feature was named after):
     DERIVED      states and transitions come from the parse, not a JS constant
     FLOW         a record walks the full lifecycle to Canonical
     RULES BITE   the certification gate refuses, then yields; retirement guards dependents
     AUDITED      every transition is in the immutable ledger, chained by id
     GENERIC      the same machine drives Insurance, Streaming, Cloud and any other
   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-dom-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const ucos = require(path.join(__dirname, "..", "lib", "ucos.js"));
const univ = require(path.join(__dirname, "..", "lib", "ucos-universes.js"));
const dom = require(path.join(__dirname, "..", "lib", "ucos-domain.js"));
const entity = require(path.join(__dirname, "..", "lib", "entity.js"));
const api = require(path.join(__dirname, "..", "lib", "api.js"));
ucos.seed(db);
univ.instantiateAll();
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const cnt = (sql, ...p) => { try { return (db.get(sql, ...p) || {}).n || 0; } catch (e) { return 0; } };

console.log("\n▸ DERIVED FROM THE CORPUS (no state machine in code)");
const states = ucos.lifecycleStates();
ok(states.length === 7, "the corpus declares the 7 lifecycle states (UCOS 5.1)", JSON.stringify(states));
ok(states.includes("Proposed") && states.includes("Canonical") && states.includes("Retired"), "the states are the constitution's own vocabulary");
/* the module must not hold the machine as a constant — it reads it from the document */
const srcDomain = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos-domain.js"), "utf8");
ok(!/"Proposed"\s*,\s*"Drafted"/.test(srcDomain), "the domain engine asserts no state list (Article 4.2)");
ok(!/const STATES\s*=|const LIFECYCLE\s*=\s*\[/.test(srcDomain), "no hardcoded lifecycle constant in the engine");

console.log("\n▸ THE DOMAIN IS DERIVED PER UNIVERSE (generic, not hand-written per domain)");
const probeKeys = ["uv_insurance", "uv_streaming_product", "uv_cloud_product", "uv_ai_product", "uv_appointment"];
const probes = probeKeys.map(k => dom.domainOf(k)).filter(Boolean);
ok(probes.length >= 4, "the probe universes resolve to domains", "n=" + probes.length);
ok(probes.every(d => d.states.length === states.length), "every domain carries the corpus's full lifecycle", "");
ok(probes.every(d => d.transitions.length === states.length - 1), "every domain derives one transition per state advance", "");
ok(probes.every(d => d.grammar.length === 6), "every domain reports the Art. 10 transition grammar (6 components)", "");
/* the rules attach where the corpus says they do — and only there */
const ins = dom.domainOf("uv_insurance");
const canonicalRule = ins.transitions.find(t => /canonical/i.test(t.to));
const retiredRule = ins.transitions.find(t => /retired/i.test(t.to));
ok(canonicalRule && canonicalRule.rule === "certification", "the →Canonical transition carries the certification rule (UCOS 5.2)", JSON.stringify(canonicalRule));
ok(retiredRule && retiredRule.rule === "dependents-retired", "the →Retired transition carries the dependents rule (UCOS 5.2)", JSON.stringify(retiredRule));
ok(ins.transitions.filter(t => t.rule).length === 2, "only the two rules the corpus declares are attached", ins.transitions.filter(t => t.rule).length);

console.log("\n▸ FLOW: a record walks the corpus's lifecycle (Insurance)");
const rec = entity.createEntity(1, "uv_insurance", { name: "Cargo Policy", code: "CARGO-7", status: "proposed" });
ok(!rec.error && rec.id > 0, "a record exists in the domain", JSON.stringify(rec));
let cur = null, steps = 0;
for (let i = 0; i < 10; i++) {
  const f = dom.fire("uv_insurance", rec.id, { actor: "test" });
  if (!f.ok) { if (f.rule === "certification") break; ok(false, "unexpected refusal", JSON.stringify(f)); break; }
  cur = f; steps++;
}
ok(steps === 3, "the record advances to the certification gate and stops", "steps=" + steps);
ok(cur && /Certified/i.test(cur.to), "the record sits at Certified, one step from Canonical", cur && cur.to);

console.log("\n▸ UCOS 5.2 BITES: certification is required for Canonical");
const blocked = dom.fire("uv_insurance", rec.id, { actor: "test" });
ok(blocked.ok === false, "the transition into Canonical is refused without certification", JSON.stringify(blocked));
ok(/certification/i.test(blocked.error || ""), "the refusal names the rule that blocks it", blocked.error);
ok(blocked.rule === "certification", "the refusal carries the machine-readable rule key", blocked.rule);
/* satisfy the condition the way an operator would, then the gate opens */
entity.updateEntity(1, "uv_insurance", rec.id, { name: "Cargo Policy", code: "CARGO-7", status: "certified", certified: true });
const through = dom.fire("uv_insurance", rec.id, { actor: "test" });
ok(through.ok === true && /Canonical/i.test(through.to), "once certified, the record enters Canonical", JSON.stringify(through));

console.log("\n▸ UCOS 5.2 BITES: retirement guards dependents (Streaming Product)");
/* both records are created already certified, so they can cross the Canonical gate and
   actually reach the Retired transition where the dependents rule applies */
const base = entity.createEntity(1, "uv_streaming_product", { name: "Base Stream", code: "BS-1", status: "proposed", certified: true });
const child = entity.createEntity(1, "uv_streaming_product", { name: "Child Stream", code: "CS-1", status: "proposed", depends_on: "BS-1", certified: true });
ok(base.id > 0 && child.id > 0, "a dependent pair exists in the Streaming domain");
/* walk the parent forward: it must stop at Retired while the child is still live */
let blockedAt = null;
for (let i = 0; i < 10; i++) {
  const f = dom.fire("uv_streaming_product", base.id, { actor: "test" });
  if (!f.ok) { blockedAt = f; break; }
}
ok(!!blockedAt, "the parent's walk stops at a gated transition", JSON.stringify(blockedAt));
ok(blockedAt && /dependent/i.test(blockedAt.error || ""), "the refusal names the dependents rule", blockedAt && blockedAt.error);
ok(blockedAt && blockedAt.rule === "dependents-retired", "the refusal carries the dependents rule key", blockedAt && blockedAt.rule);
/* retire the dependent first, then the parent retires */
for (let i = 0; i < 10; i++) { const f = dom.fire("uv_streaming_product", child.id, { actor: "test" }); if (!f.ok) break; }
const parentRetire = dom.fire("uv_streaming_product", base.id, { actor: "test" });
ok(parentRetire.ok === true && /Retired/i.test(parentRetire.to), "the parent retires once its dependent is retired", JSON.stringify(parentRetire));

console.log("\n▸ TERMINAL: no transition out of Retired");
const afterEnd = dom.fire("uv_streaming_product", base.id, { actor: "test" });
ok(afterEnd.ok === false, "a retired record has no further transition", JSON.stringify(afterEnd));
ok(availableNone(), "availableTransitions() is empty at a terminal state");
function availableNone() { const a = dom.availableTransitions("uv_streaming_product", base.id); return Array.isArray(a) && a.length === 0; }

console.log("\n▸ ARTICLE 6: every transition is append-audited and immutable");
const hist = dom.history("uv_insurance", rec.id);
ok(hist.length === steps + 1, "the ledger records every transition the record underwent", "n=" + hist.length);
ok(hist.every(h => h.from_state && h.to_state && h.at), "every ledger row carries from/to/when");
ok(hist.some(h => h.rule === "certification"), "the ledger records which corpus rule authorized the Canonical entry");
ok(hist.every((h, i) => i === 0 || Number(h.id) > Number(hist[i - 1].id)), "the ledger is append-ordered by id");
/* immutability: there is no UPDATE path to the ledger — prove it has no update API */
const srcDom = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos-domain.js"), "utf8");
ok(!/UPDATE\s+ucos_record_transitions/i.test(srcDom), "the engine never mutates the transition ledger (Article 6)");

console.log("\n▸ GENERIC ACROSS DOMAINS (the same machine, different universes)");
for (const d of probes) {
  const r = entity.createEntity(1, d.entityKey, { name: "Probe " + d.universe.name, code: "PRB", status: "proposed" });
  const f = dom.fire(d.entityKey, r.id, { actor: "test" });
  ok(f.ok === true, d.universe.name + ": the generic machine advances its record", JSON.stringify(f));
  const h = dom.history(d.entityKey, r.id);
  ok(h.length === 1 && /Drafted/i.test(h[0].to_state), d.universe.name + ": the ledger is written by the same code path");
}

console.log("\n▸ THE BOARD: the domain's flow at a glance (console source of truth)");
const b = dom.board("uv_insurance");
ok(!!b && b.records > 0, "the board reports the domain's population", b && b.records);
ok(Object.keys(b.byState).length === states.length, "the board has a column for every corpus state");
ok(b.records_.every(r => Array.isArray(r.available)), "every board record carries its own legal next transition");

console.log("\n▸ AUTHORITY: a transition is an admin/platform action");
const call = (method, urlStr, body, sess) => {
  let out = {};
  const res = { writeHead: () => { }, end: s => { out = JSON.parse(s); } };
  api.handle({ method }, res, new URL(urlStr), sess || { platform_admin: { id: 1, email: "p@p" }, tenant: { id: 1 } }, body);
  return out;
};
const r3 = entity.createEntity(1, "uv_cloud_product", { name: "Cloud Probe", code: "CP", status: "proposed" });
const fired = call("POST", "http://x/api/ucos/domain/uv_cloud_product/fire", { record_id: r3.id });
ok(fired.ok === true, "a platform session can fire a domain transition", JSON.stringify(fired));
const denied = call("POST", "http://x/api/ucos/domain/uv_cloud_product/fire", { record_id: r3.id }, { tenant: { id: 1 } });
ok(!!denied.error, "a non-admin session is refused", JSON.stringify(denied));
ok(/Store administrator access required/.test(denied.error || ""), "the refusal names the authority required", denied.error);

console.log("\n▸ CLEAN STATE");
db.run("DELETE FROM entity_data WHERE entity LIKE 'uv_%' AND tenant_id=0");

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all per-domain checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);

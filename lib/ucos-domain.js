/* UCOS Ω∞ · per-domain record engine — every universe gets its own state machine.
   --------------------------------------------------------------------------
   The generic entity engine (lib/entity.js) makes every universe CRUD-able. This
   module makes every universe a DOMAIN: its records move through a state machine
   the corpus itself declares, and each transition is authorized by the corpus's
   own rules — never by code written for one universe (Article 4.2).

   The grammar is read from the corpus, not invented here:
     UCOS Art. 5.1     the lifecycle states (Proposed … Retired)
     UCOS Art. 5.2     the transition rules — Canonical requires certification;
                       Retired requires every dependent to be retired first
     UMQSOCR Art. 10   the transition components — Source State, Target State,
                       Transition Rule, Trigger, Conditions, Effects

   A domain is DERIVED per universe from that grammar: its states, its legal
   transitions, the condition each transition must satisfy, and the trigger that
   fires them. A record's transition is refused if the rule is not met — the
   constitution biting at the record level, exactly as it already bites at the
   foundation level (lib/ucos-foundations.js). Every transition is written to an
   append-only ledger (Article 6).

   Nothing here is universe-specific: Insurance, Streaming, Cloud and 1,874 others
   are driven by the same derived machine, so a new domain needs no new code. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const rows = (sql, ...p) => { try { return db().all(sql, ...p) || []; } catch (e) { return []; } };
const get = (sql, ...p) => { try { return db().get(sql, ...p) || null; } catch (e) { return null; } };
const ucos = require("./ucos.js");

/* the transition rules the corpus declares (UCOS 5.2), read as data:
   "Transition into Canonical requires certification. Transition into Retired
   requires every dependent foundation to be retired first." Each rule is a
   (target state → condition) pair, so the engine applies them by matching the
   state a transition targets, never by naming a universe. */
function ruleFor(targetState) {
  if (/canonical/i.test(targetState)) return { key: "certification",
    text: "Transition into Canonical requires certification (UCOS 5.2)",
    check: rec => rec && (rec.certified === true || rec.certified === 1 || rec.certified === "true") };
  if (/retired/i.test(targetState)) return { key: "dependents-retired",
    text: "Transition into Retired requires every dependent to be retired first (UCOS 5.2)",
    check: (rec, ctx) => !ctx || !ctx.dependents || ctx.dependents.every(d => /retired|deprecated/i.test(String(d.status || ""))) };
  return null;
}

/* ---------- the derived domain of one universe ----------
   Returns the state machine as data: states, transitions (with their corpus rule
   and trigger), and the fields the universe's records carry. Derived entirely from
   the parsed corpus + the universe's live entity definition. */
function domainOf(entityKey) {
  const u = get("SELECT key,name,source_doc,source_line FROM ucos_universes WHERE entity_key=?", entityKey);
  if (!u) return null;
  const def = get("SELECT def FROM entity_defs WHERE key=?", entityKey);
  let d = {}; try { d = JSON.parse(def.def || "{}"); } catch (e) { }
  const states = ucos.lifecycleStates();
  /* adjacent states are legal transitions (the lifecycle is an ordered progression);
     the corpus's 5.2 rules attach as the condition a transition must satisfy */
  const transitions = [];
  for (let i = 0; i < states.length - 1; i++) {
    const rule = ruleFor(states[i + 1]);
    transitions.push({ from: states[i], to: states[i + 1], rule: rule && rule.key || null,
      trigger: "operator", condition: rule && rule.text || null });
  }
  /* the fields are the corpus-declared attributes of this universe (already derived by
     the instantiation), surfaced as the domain's vocabulary */
  const fields = (d.fields || []).map(f => ({ key: f.key, label: f.label, type: f.type }));
  return { universe: u, entityKey, states, transitions, fields,
    source: u.source_doc + (u.source_line ? ":" + u.source_line : ""),
    /* UMQSOCR Art. 10: the components every transition carries — reported so the
       console can render the grammar the corpus declares, not a UI invention */
    grammar: ["Source State", "Target State", "Transition Rule", "Trigger", "Conditions", "Effects"] };
}

/* ---------- the transitions a record may legally fire right now ----------
   A record in its current state can advance to the next state in the lifecycle,
   provided the corpus's rule is satisfiable. Retired/Deprecated are terminal for
   forward movement. Returns the transition plus whether its condition currently
   holds — so the console can show a rule as "blocked" rather than silently refusing. */
function availableTransitions(entityKey, recordId) {
  const dom = domainOf(entityKey);
  if (!dom) return [];
  const rec = get("SELECT id, data FROM entity_data WHERE entity=? AND id=?", entityKey, Number(recordId));
  if (!rec) return [];
  let data = {}; try { data = JSON.parse(rec.data || "{}"); } catch (e) { }
  const cur = String(data.status || dom.states[0] || "Proposed");
  const idx = dom.states.findIndex(s => s.toLowerCase() === String(cur).toLowerCase());
  if (idx < 0 || idx >= dom.states.length - 1) return [];
  const next = dom.transitions[idx];
  if (!next) return [];
  const rule = ruleFor(next.to);
  const dependents = rows("SELECT id, data FROM entity_data WHERE entity=? AND id !=? AND data LIKE ?", entityKey, Number(recordId), "%depends_on%")
    .map(r => { let dd = {}; try { dd = JSON.parse(r.data || "{}"); } catch (e) { } return { id: r.id, status: dd.status }; })
    .filter(r => true);
  const ctx = { dependents };
  const holds = rule ? !!rule.check(data, ctx) : true;
  return [{ ...next, current: cur, holds,
    blocked: rule && !holds ? rule.text : null }];
}

/* ---------- fire one transition (Article 6: append-audited) ----------
   Applies the next legal transition to a record, but only if the corpus's rule is
   satisfied. A refused transition names the rule — the same honesty the foundation
   admission rules have (Article 4.1). The record's data is updated in place and the
   transition is written to the immutable ledger. */
function fire(entityKey, recordId, opts) {
  const o = opts || {};
  const dom = domainOf(entityKey);
  if (!dom) return { ok: false, error: "unknown universe " + entityKey };
  const rec = get("SELECT id, data FROM entity_data WHERE entity=? AND id=?", entityKey, Number(recordId));
  if (!rec) return { ok: false, error: "record " + recordId + " not found in " + entityKey };
  let data = {}; try { data = JSON.parse(rec.data || "{}"); } catch (e) { }
  const cur = String(data.status || dom.states[0] || "Proposed");
  const idx = dom.states.findIndex(s => s.toLowerCase() === String(cur).toLowerCase());
  if (idx < 0) return { ok: false, error: "record is in an unknown state: " + cur };
  if (idx >= dom.states.length - 1) return { ok: false, error: cur + " is terminal — no further transition" };
  const tr = dom.transitions[idx];
  const rule = ruleFor(tr.to);
  const dependents = rows("SELECT id, data FROM entity_data WHERE entity=? AND id !=? AND data LIKE ?", entityKey, Number(recordId), "%depends_on%")
    .map(r => { let dd = {}; try { dd = JSON.parse(r.data || "{}"); } catch (e) { } return { id: r.id, status: dd.status }; });
  if (rule && !rule.check(data, { dependents })) {
    return { ok: false, error: "refused: " + rule.text, rule: rule.key, from: cur, to: tr.to };
  }
  const from = cur, to = tr.to;
  data.status = to;
  if (rule && rule.key === "certification") data.certified = true;
  db().run("UPDATE entity_data SET data=? WHERE id=?", JSON.stringify(data), rec.id);
  db().run("INSERT INTO ucos_record_transitions(entity_key,record_id,from_state,to_state,rule,actor,detail) VALUES(?,?,?,?,?,?,?)",
    entityKey, rec.id, from, to, tr.rule || null, o.actor || "operator", JSON.stringify(o.detail || {}));
  return { ok: true, id: rec.id, from, to, rule: tr.rule || null, entityKey };
}

/* ---------- the record's transition history (Article 6 ledger, read side) ---------- */
function history(entityKey, recordId) {
  return rows("SELECT id, from_state, to_state, rule, actor, detail, at FROM ucos_record_transitions"
    + " WHERE entity_key=? AND record_id=? ORDER BY id", entityKey, Number(recordId));
}

/* ---------- the domain's population: where every record sits in the lifecycle ----------
   The console renders this as the domain's board — a column per state — so an
   operator sees the whole domain's flow, not just one record. Each record carries
   the transition it may legally fire next (and whether its rule currently holds),
   so the front-end needs no logic of its own. */
function board(entityKey) {
  const dom = domainOf(entityKey);
  if (!dom) return null;
  const byState = {};
  for (const s of dom.states) byState[s] = 0;
  const lower = Object.fromEntries(dom.states.map(s => [s.toLowerCase(), s]));
  const recs = rows("SELECT id, data FROM entity_data WHERE entity=? ORDER BY id DESC", entityKey).map(r => {
    let d = {}; try { d = JSON.parse(r.data || "{}"); } catch (e) { }
    const st = lower[String(d.status || "").toLowerCase()] || dom.states[0];
    if (byState[st] != null) byState[st]++;
    return { id: r.id, name: d.name || ("#" + r.id), status: st, certified: d.certified === true };
  });
  for (const r of recs) {
    const tr = availableTransitions(entityKey, r.id)[0];
    r.available = tr ? [tr] : [];
  }
  const total = recs.length;
  const transitions = rows("SELECT COUNT(*) n FROM ucos_record_transitions WHERE entity_key=?", entityKey)[0] || { n: 0 };
  return { ...dom, byState, records: total, records_: recs, transitions: transitions.n || 0 };
}

/* ---------- every domain, summarized: the constitutional flow at a glance ----------
   This is the console's picker: it needs one row per universe with its record count,
   nothing more. Building a full board() per universe — which resolves every record's
   next transition — was fine when the corpus was empty, but the flagship now ships with
   all 1,877 universes activated, and that turned the picker into a ~1.3s, 233KB load on
   every render. The counts are derivable in one set-based pass over entity_data; the
   expensive per-record analysis belongs to board(), which the console calls only for the
   ONE selected domain. */
function domains() {
  const states = ucos.lifecycleStates();
  const counts = rows("SELECT entity, COUNT(*) n FROM entity_data WHERE entity LIKE 'uv_%' GROUP BY entity");
  const byEntity = new Map(counts.map(c => [c.entity, c.n]));
  const transitions = rows("SELECT entity_key, COUNT(*) n FROM ucos_record_transitions GROUP BY entity_key");
  const byTrans = new Map(transitions.map(t => [t.entity_key, t.n]));
  const out = [];
  for (const u of rows("SELECT entity_key, name, source_doc, source_line FROM ucos_universes ORDER BY name")) {
    out.push({ entityKey: u.entity_key, universe: u.name,
      source: (u.source_doc || "") + (u.source_line != null ? ":" + u.source_line : ""),
      records: byEntity.get(u.entity_key) || 0, transitions: byTrans.get(u.entity_key) || 0,
      states: states.length });
  }
  return out;
}

module.exports = { ruleFor, domainOf, availableTransitions, fire, history, board, domains };

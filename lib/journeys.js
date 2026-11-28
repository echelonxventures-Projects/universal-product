/* LUXORA Platform — journeys (owner Communication).

   A journey is a series of messages a store sends on its own: when something happens to a person — they
   create an account, order, have an order delivered, or leave items in their cart — or to an audience
   enrolled by hand (lib/seed/journeys.json triggers). Each step waits a while after the one before, then
   goes by email, SMS or a note in the shopper's account (the channels campaigns use). A person enters a
   journey once (or each time, when the journey says so), only with a live grant for marketing, checked
   again before every message; every message carries the unsubscribe link, and withdrawing takes the
   person out of every journey. An event the journey names as its exit takes them out (an order ends an
   abandoned-cart journey). Nobody gets more than the daily cap of journey messages. Opens and clicks are
   counted by lib/campaigns.js track. A journey moves through its machine (journey: draft, live, paused,
   ended) and is a record on the master; who is in it (journey_enrolments) and what was sent
   (journey_messages) stay in the tables, where erasure removes a person's rows. */
"use strict";

const db = () => require("./db.js");
const RR = () => require("./row-records.js");
const C = () => require("./compliance.js");
const CA = () => require("./campaigns.js");
const states = require("./states.js");
const crypto = require("crypto");
const SEED = require("./seed/journeys.json");
const M = SEED.machine, E = SEED.enrolment, REC = SEED.record;
const fail = (msg, status, code) => { const e = new Error(msg); e.status = status || 400; if (code) e.code = code; throw e; };
const N = Number;
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);
const tx = fn => require("./kernel.js").internal.tx(fn);
const ph = xs => "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")";
const at = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");
const own = tid => { try { return require("./settings.js").get(N(tid), "journeys") || {}; } catch (e) { return {}; } };
const P = (tid, k) => { const o = own(tid); return o[k] !== undefined ? o[k] : SEED[k]; };
const tagged = (m, s, t) => !!s && states.has(m, s) && states.is(m, s, t);
const purpose = () => CA().SEED.purpose;
const emailOfOwner = owner => { const m = /^t(\d+):u:(\d+)$/.exec(String(owner || "")); const u = m ? db().get("SELECT name, email FROM users WHERE id=? AND tenant_id=?", N(m[2]), N(m[1])) : null; return u || null; };

const row = (tid, id) => db().get("SELECT * FROM journeys WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such journey", 404);
function move(j, tag, extra) {
  const to = states.first(M, tag), { patch } = states.apply(M, { tenantId: j.tenant_id, from: j.status, to, row: j });
  const all = { ...patch, ...(extra || {}) }, k = Object.keys(all);
  RR().change(REC, j.id, () => { const r = db().run(`UPDATE journeys SET ${k.map(x => x + "=?").join(", ")} WHERE id=? AND status=?`, ...k.map(x => all[x]), j.id, j.status); if (!r.changes) fail("This journey has just changed — reload it", 409); return r; });
  return row(j.tenant_id, j.id);
}

/* ============================== making a journey ============================== */
/* steps [{ wait_minutes, channel, subject?, body }] — the first waits after the person enters, each next after the one before */
function stepsOf(input) {
  const xs = Array.isArray(input) ? input : fail("Give the journey its steps");
  if (!xs.length) fail("A journey has at least one step");
  if (xs.length > SEED.maxSteps) fail("A journey has at most " + SEED.maxSteps + " steps");
  const ch = CA().SEED.channels;
  return xs.map((s0, k) => {
    const s = s0 || {}, wait = Math.floor(N(s.wait_minutes) || 0);
    if (!(wait >= 0 && wait <= SEED.maxWaitDays * 1440)) fail(`Step ${k + 1}: a wait is 0 to ${SEED.maxWaitDays} days`);
    if (!ch[s.channel]) fail(`Step ${k + 1}: a message goes by one of ${Object.keys(ch).join(", ")}`);
    if (!str(s.body)) fail(`Step ${k + 1}: write the message`);
    if (ch[s.channel].subject && !str(s.subject)) fail(`Step ${k + 1}: give it a subject`);
    return { wait_minutes: wait, channel: s.channel, subject: str(s.subject, 200), body: str(s.body, 8000) };
  });
}
function triggerOf(k) { return SEED.triggers[k] ? k : fail("A journey starts on one of: " + Object.keys(SEED.triggers).join(", ")); }
function exitsOf(xs, trigger) {
  const out = [...new Set((Array.isArray(xs) ? xs : []).map(x => str(x, 60)))];
  for (const x of out) if (!SEED.exits.includes(x)) fail("A journey ends early on one of: " + SEED.exits.join(", "));
  if (out.includes(trigger)) fail("A journey cannot end on the event that starts it");
  return out;
}
/* { name, trigger, steps, exit_on?, reenter?, segment? } — segment narrows who enters to its members */
function create(tid, input, actor) {
  const t = N(tid), i = input || {}, name = str(i.name, 160);
  if (!name) fail("Name the journey");
  const trigger = triggerOf(i.trigger), steps = stepsOf(i.steps), exits = exitsOf(i.exit_on, trigger);
  const ref = SEED.refPrefix + "-" + t + "-" + String(db().get("SELECT COUNT(*) c FROM journeys WHERE tenant_id=?", t).c + 1).padStart(5, "0");
  const w = RR().created(REC, () => db().run("INSERT INTO journeys(tenant_id, ref, name, trigger_on, steps, exit_on, reenter, segment, purpose, status, link_base, created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
    t, ref, name, trigger, JSON.stringify(steps), JSON.stringify(exits), i.reenter ? 1 : 0, str(i.segment, 80), purpose(), states.initial(M), str(i.link_base, 300), str(actor, 120)));
  return get(t, N(w.lastInsertRowid));
}
/* a draft or a paused journey is changed; people already in it take the new steps from their next one */
function update(tid, id, input) {
  const j = row(tid, id), i = input || {};
  if (!tagged(M, j.status, "editable")) fail("Pause the journey before changing it", 409);
  const trigger = i.trigger !== undefined ? triggerOf(i.trigger) : j.trigger_on;
  if (trigger !== j.trigger_on && db().get("SELECT 1 x FROM journey_enrolments WHERE journey_id=? LIMIT 1", j.id)) fail("People have entered this journey; make a new one to start on something else", 409);
  const steps = i.steps !== undefined ? stepsOf(i.steps) : JSON.parse(j.steps);
  const exits = exitsOf(i.exit_on !== undefined ? i.exit_on : JSON.parse(j.exit_on), trigger);
  RR().change(REC, j.id, () => db().run("UPDATE journeys SET name=?, trigger_on=?, steps=?, exit_on=?, reenter=?, segment=? WHERE id=?",
    str(i.name !== undefined ? i.name : j.name, 160) || j.name, trigger, JSON.stringify(steps), JSON.stringify(exits), i.reenter !== undefined ? (i.reenter ? 1 : 0) : j.reenter, i.segment !== undefined ? str(i.segment, 80) : j.segment, j.id));
  return get(tid, id);
}
function start(tid, id) { const j = row(tid, id); if (!tagged(M, j.status, "startable")) fail("Only a draft or paused journey is started", 409); return get(tid, move(j, "live").id); }
function pause(tid, id) { const j = row(tid, id); if (!tagged(M, j.status, "live")) fail("Only a live journey is paused", 409); return get(tid, move(j, "paused").id); }
/* ended for good: nobody enters, and whoever is in it gets nothing more */
function end(tid, id) {
  const j = row(tid, id);
  if (tagged(M, j.status, "terminal")) fail("This journey has ended", 409);
  return tx(() => { stopWhere("journey_id=?", [j.id], "the journey ended"); return get(tid, move(j, "terminal").id); });
}

/* ============================== who enters ============================== */
/* how a trigger's data names its person (lib/seed/journeys.json triggers[].person) */
const orderOwner = (t, d) => { const o = d.num ? db().get("SELECT owner FROM orders WHERE num=? AND tenant_id=?", String(d.num), t) : d.order_id ? db().get("SELECT owner FROM orders WHERE id=? AND tenant_id=?", N(d.order_id), t) : null; return o ? o.owner : ""; };
const WHO = { user: (t, d) => d.user_id ? `t${t}:u:${N(d.user_id)}` : "", order: orderOwner, owner: (t, d) => String(d.owner || "") };
/* the person an event is about: { owner, email, name, phone } — only a signed-in person has an address and a grant */
function personOf(tid, trigger, data) {
  const how = (SEED.triggers[trigger] || {}).person, d = data || {}, t = N(tid);
  const find = WHO[how] || (() => "");
  const owner = find(t, d) || "", u = emailOfOwner(owner);
  return u && u.email ? { owner, email: String(u.email).toLowerCase(), name: u.name || "", phone: "" } : null;
}
const inSegment = (tid, seg, owner) => !seg || !!(owner && db().get("SELECT 1 x FROM segment_members WHERE tenant_id=? AND segment=? AND owner=?", N(tid), seg, owner));
/* puts a person in a journey once (or once per `key` when it re-enters), when it is live and they may be sent marketing */
function enrol(j, person, key, source) {
  if (!tagged(M, j.status, "live") || !person || !person.email) return null;
  if (!inSegment(j.tenant_id, j.segment, person.owner)) return null;
  if (!C().mayProcess(N(j.tenant_id), person.email, j.purpose)) return null;
  const steps = JSON.parse(j.steps), k = j.reenter ? str(key || Date.now(), 120) : "once";
  const w = db().run("INSERT INTO journey_enrolments(tenant_id, journey_id, person, owner, email, phone, name, enrol_key, step, next_at, status, source) VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(journey_id, person, enrol_key) DO NOTHING",
    j.tenant_id, j.id, person.email, person.owner || "", person.email, person.phone || "", str(person.name, 120), k, 0, at(Date.now() + steps[0].wait_minutes * 60000), states.initial(E), str(source, 60));
  return w.changes ? N(w.lastInsertRowid) : null;
}
/* what the platform tells us happened: people enter the journeys it starts, and leave the ones it ends */
function onEvent(tid, event, data, key) {
  const t = N(tid);
  if (!SEED.triggers[event] && !SEED.exits.includes(event)) return { entered: 0, left: 0 };
  let entered = 0, left = 0;
  const person = personOf(t, event, data);
  if (!person) return { entered, left };
  const live = states.tagged(M, "live");
  /* an exit first: the order that ends an abandoned-cart journey does not also count as the cart's next message */
  for (const j of db().all(`SELECT id, exit_on FROM journeys WHERE tenant_id=? AND status IN ${ph(live)}`, t, ...live))
    if (JSON.parse(j.exit_on || "[]").includes(event)) left += stopWhere("journey_id=? AND person=?", [j.id, person.email], "left on " + event);
  for (const j of db().all(`SELECT * FROM journeys WHERE tenant_id=? AND trigger_on=? AND status IN ${ph(live)}`, t, event, ...live))
    if (enrol(j, person, key || (data && (data.num || data.order_id || data.user_id)) || "", event)) entered++;
  return { entered, left };
}
/* stops the active enrolments that match, with why; how many */
function stopWhere(where, args, why) {
  const act = states.tagged(E, "active"), to = states.first(E, "stopped");
  return db().run(`UPDATE journey_enrolments SET status=?, reason=?, next_at=NULL WHERE ${where} AND status IN ${ph(act)}`, to, str(why, 200), ...args, ...act).changes;
}
/* everyone in one of the audiences campaigns use, enrolled now */
function enrolAudience(tid, id, audience) {
  const t = N(tid), j = row(t, id);
  if (!(SEED.triggers[j.trigger_on] || {}).manual) fail("People enter this journey when " + SEED.triggers[j.trigger_on].label.toLowerCase() + ", not by hand", 409);
  if (!tagged(M, j.status, "live")) fail("Start the journey first", 409);
  const people = CA().audiencePeople(t, audience);
  if (people.length > SEED.maxEnrol) fail(`This audience has ${people.length} people; a journey enrols at most ${SEED.maxEnrol} at once`, 413);
  let entered = 0, skipped = 0;
  tx(() => { for (const p of people) (p.email && enrol(j, { ...p, email: String(p.email).toLowerCase() }, "audience", "audience")) ? entered++ : skipped++; });
  return { entered, skipped, journey: get(t, id) };
}
/* carts with items left untouched for a while, by people who have not ordered since, enter once per cart */
function findAbandoned(tid) {
  const t = N(tid), mins = N(P(t, "abandonAfterMinutes")), prefix = `t${t}:u:`;
  const carts = db().all("SELECT owner, MAX(added_at) last FROM cart_items WHERE owner LIKE ? GROUP BY owner HAVING MAX(added_at) <= ?", prefix + "%", at(Date.now() - mins * 60000));
  let n = 0;
  for (const c of carts) {
    if (db().get("SELECT 1 x FROM orders WHERE tenant_id=? AND owner=? AND created_at >= ?", t, c.owner, c.last)) continue;
    n += onEvent(t, "cart.abandoned", { owner: c.owner }, c.owner + "@" + c.last).entered;
  }
  return n;
}

/* ============================== sending ============================== */
/* the steps that are due: each enrolment claimed before its message, consent checked again, the daily cap kept */
async function sendDue(tid) {
  const t = N(tid), act = states.tagged(E, "active"), live = states.tagged(M, "live"), cap = N(P(t, "maxPerDay")), now = at(Date.now());
  const due = db().all(`SELECT e.* FROM journey_enrolments e JOIN journeys j ON j.id=e.journey_id WHERE e.tenant_id=? AND e.status IN ${ph(act)} AND j.status IN ${ph(live)} AND e.next_at <= ? ORDER BY e.next_at LIMIT ?`,
    t, ...act, ...live, now, SEED.batch);
  let sent = 0;
  for (const e of due) {
    const j = row(t, e.journey_id), steps = JSON.parse(j.steps), s = steps[e.step];
    if (!s) { finish(e, "done"); continue; }
    /* claimed: the next time moves out of reach first, so two servers never send the same step */
    if (!db().run("UPDATE journey_enrolments SET next_at=? WHERE id=? AND next_at=? AND step=?", at(Date.now() + 3600000), e.id, e.next_at, e.step).changes) continue;
    if (!C().mayProcess(t, e.email, j.purpose)) { stopWhere("id=?", [e.id], "consent withdrawn"); continue; }
    if (cap > 0 && db().get("SELECT COUNT(*) n FROM journey_messages WHERE tenant_id=? AND person=? AND sent_at >= ?", t, e.person, at(Date.now() - 86400000)).n >= cap) {
      db().run("UPDATE journey_enrolments SET next_at=? WHERE id=?", at(Date.now() + 86400000), e.id); continue;
    }
    /* the channel names which of the person's addresses it uses (lib/seed/campaigns.json channels) */
    const field = CA().SEED.channels[s.channel].address, address = ({ owner: e.owner, phone: e.phone, email: e.email })[field];
    const token = "j" + crypto.randomBytes(18).toString("hex");
    const mid = N(db().run("INSERT INTO journey_messages(tenant_id, journey_id, enrolment_id, step, channel, person, address, token, status) VALUES(?,?,?,?,?,?,?,?,?)",
      t, j.id, e.id, e.step, s.channel, e.person, address || "", token, CA().SEED.recipient.sending).lastInsertRowid);
    let out = { sent: false, error: "no " + field };
    if (address) {
      const m = CA().compose(t, { body: s.body, subject: s.subject, channel: s.channel, link_base: j.link_base }, { token, name: e.name });
      db().run("UPDATE journey_messages SET links=? WHERE id=?", JSON.stringify(m.links), mid);
      out = await CA().deliver(t, s.channel, { address, owner: e.owner }, m);
    }
    const RS = CA().SEED.recipient;
    db().run("UPDATE journey_messages SET status=?, reason=?, sent_at=? WHERE id=?", out.sent ? RS.sent : RS.failed, out.sent ? "" : str(out.error || "not sent", 200), out.sent ? at(Date.now()) : null, mid);
    if (out.sent) sent++;
    /* the next step waits from now; after the last, the journey is done for this person */
    const nx = steps[e.step + 1];
    if (nx) db().run("UPDATE journey_enrolments SET step=?, next_at=? WHERE id=?", e.step + 1, at(Date.now() + nx.wait_minutes * 60000), e.id);
    else finish({ ...e, step: e.step + 1 }, "done");
  }
  return sent;
}
function finish(e, tag) { db().run("UPDATE journey_enrolments SET status=?, step=?, next_at=NULL WHERE id=?", states.first(E, tag), e.step, e.id); }
/* the link in a journey message withdraws the grant and takes the person out of every journey */
function unsubscribe(token) {
  const m = db().get("SELECT m.*, j.purpose FROM journey_messages m JOIN journeys j ON j.id=m.journey_id WHERE m.token=?", String(token || ""));
  if (!m) return { ok: false };
  C().grantConsent(m.tenant_id, m.person, m.purpose, { status: states.first("consent", "withdrawal"), source: "unsubscribe" });
  db().run("UPDATE journey_messages SET unsubscribed_at=COALESCE(unsubscribed_at, datetime('now')) WHERE id=?", m.id);
  stopWhere("tenant_id=? AND person=?", [m.tenant_id, m.person], "unsubscribed");
  return { ok: true, store: (db().get("SELECT name FROM tenants WHERE id=?", m.tenant_id) || {}).name || "" };
}

/* ============================== reading ============================== */
function get(tid, id) {
  const j = row(tid, id), s = j.status;
  const by = Object.fromEntries(db().all("SELECT status, COUNT(*) n FROM journey_enrolments WHERE journey_id=? GROUP BY status", j.id).map(r => [r.status, r.n]));
  const steps = JSON.parse(j.steps).map((st, k) => {
    const m = db().get(`SELECT COUNT(*) total, SUM(CASE WHEN status=? THEN 1 ELSE 0 END) sent, SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) opened, SUM(CASE WHEN clicked_at IS NOT NULL THEN 1 ELSE 0 END) clicked, SUM(CASE WHEN unsubscribed_at IS NOT NULL THEN 1 ELSE 0 END) unsubscribed FROM journey_messages WHERE journey_id=? AND step=?`, CA().SEED.recipient.sent, j.id, k);
    const sent = N(m.sent) || 0;
    return { ...st, sent, failed: (N(m.total) || 0) - sent, opened: N(m.opened) || 0, clicked: N(m.clicked) || 0, unsubscribed: N(m.unsubscribed) || 0,
      openRate: sent ? +(N(m.opened) * 100 / sent).toFixed(1) : null, clickRate: sent ? +(N(m.clicked) * 100 / sent).toFixed(1) : null };
  });
  const people = Object.entries(by).reduce((a, [st, n]) => { for (const tg of ["active", "done", "stopped"]) if (tagged(E, st, tg)) a[tg] += n; return a; }, { active: 0, done: 0, stopped: 0 });
  return { ...j, steps, exit_on: JSON.parse(j.exit_on || "[]"), trigger: SEED.triggers[j.trigger_on], people, entered: people.active + people.done + people.stopped,
    actions: [tagged(M, s, "startable") && "start", tagged(M, s, "live") && "pause", !tagged(M, s, "terminal") && "end", tagged(M, s, "live") && (SEED.triggers[j.trigger_on] || {}).manual && "enrol"].filter(Boolean),
    editable: tagged(M, s, "editable") };
}
function list(tid) { return db().all("SELECT id FROM journeys WHERE tenant_id=? ORDER BY id DESC LIMIT 200", N(tid)).map(r => get(tid, r.id)); }
/* who is in a journey and where: the newest first */
function people(tid, id, f) {
  const j = row(tid, id), o = f || {};
  return db().all("SELECT id, person, name, step, next_at, status, reason, source, entered_at FROM journey_enrolments WHERE journey_id=? AND (?='' OR status=?) ORDER BY id DESC LIMIT 300", j.id, str(o.status), str(o.status));
}
function vocabulary() { return { triggers: SEED.triggers, exits: SEED.exits, channels: Object.keys(CA().SEED.channels), maxSteps: SEED.maxSteps, maxWaitDays: SEED.maxWaitDays }; }

/* ============================== the clock ============================== */
async function sweep(tid) { const t = N(tid); const entered = findAbandoned(t); const sent = await sendDue(t); return { entered, sent }; }
async function sweepAll() {
  const live = states.tagged(M, "live"); let n = 0;
  for (const r of db().all(`SELECT DISTINCT tenant_id FROM journeys WHERE status IN ${ph(live)}`, ...live)) { try { n += (await sweep(r.tenant_id)).sent; } catch (e) { console.error("journeys sweep:", e.message); } }
  return n;
}

module.exports = { create, update, start, pause, end, onEvent, enrolAudience, findAbandoned, sendDue, unsubscribe, get, list, people, vocabulary, sweep, sweepAll, SEED };

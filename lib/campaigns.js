/* LUXORA Platform — campaigns (owner Communication).

   A campaign is one message — email, SMS, or a note in the shopper's account — to an audience:
   every customer, a segment, every CRM contact, or the people at one company (lib/seed/campaigns.json).
   Its list is built once, one row per address (campaign_recipients); each person must hold a live
   grant for the campaign's purpose (marketing), checked when the list is built and again right before
   their message, and every message carries a link that withdraws that grant. Recipients are claimed
   one by one before they are sent to, so two servers never send the same person the same message,
   and a send interrupted mid-way is marked, never repeated. A campaign moves through its machine
   (campaign: draft, scheduled, sending, sent, cancelled) and is a record on the master; the message
   and its recipients stay in the tables, where erasure removes a person's rows. */
"use strict";

const db = () => require("./db.js");
const RR = () => require("./row-records.js");
const C = () => require("./compliance.js");
const mailer = () => require("./mailer.js");
const states = require("./states.js");
const crypto = require("crypto");
const SEED = require("./seed/campaigns.json");
const RS = SEED.recipient, M = SEED.machine, REC = SEED.record;
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const N = Number;
const K_tx = fn => require("./kernel.js").internal.tx(fn);
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);
const now = () => new Date().toISOString().slice(0, 19).replace("T", " ");

const row = (tid, id) => db().get("SELECT * FROM campaigns WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such campaign", 404);
const tagged = (s, t) => states.has(M, s) && states.is(M, s, t);
function move(c, tag, extra) {
  const to = states.first(M, tag), { patch } = states.apply(M, { tenantId: c.tenant_id, from: c.status, to, row: c });
  const all = { ...patch, ...(extra || {}) }, k = Object.keys(all);
  RR().change(REC, c.id, () => { const r = db().run(`UPDATE campaigns SET ${k.map(x => x + "=?").join(", ")} WHERE id=? AND status=?`, ...k.map(x => all[x]), c.id, c.status); if (!r.changes) fail("This campaign has just changed — reload it", 409); return r; });
  return db().get("SELECT * FROM campaigns WHERE id=?", c.id);
}

/* { name, channel, subject, body, audience: { kind, segment?, company_id? }, scheduled_at? } */
function create(tid, input, actor) {
  const i = input || {}, t = N(tid), name = str(i.name, 160), body = str(i.body, 8000);
  if (!name) fail("Name the campaign");
  if (!SEED.channels[i.channel]) fail("A campaign is sent by one of: " + Object.keys(SEED.channels).join(", "));
  if (!body) fail("Write the message");
  if (SEED.channels[i.channel].subject && !str(i.subject)) fail("Give it a subject");
  const a = audienceOf(t, i.audience);
  const ref = SEED.refPrefix + "-" + t + "-" + String(db().get("SELECT COUNT(*) c FROM campaigns WHERE tenant_id=?", t).c + 1).padStart(5, "0");
  const r = RR().created(REC, () => db().run("INSERT INTO campaigns(tenant_id,ref,name,channel,subject,body,audience,purpose,status,link_base,created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
    t, ref, name, i.channel, str(i.subject, 200), body, JSON.stringify(a), SEED.purpose, states.initial(M), str(i.link_base, 300), str(actor, 120)));
  return get(t, N(r.lastInsertRowid));
}
function audienceOf(tid, a0) {
  const a = a0 || {}, kind = SEED.audiences[a.kind] ? a.kind : fail("A campaign goes to one of: " + Object.keys(SEED.audiences).join(", "));
  const need = SEED.audiences[kind].needs;
  const spec = SEED.audiences[kind];
  if (need && !str(a[need])) fail("Say which " + spec.label.toLowerCase().replace(/^(a|the contacts at a) /, ""));
  /* what the audience names must exist in the store: a company of its CRM */
  if (spec.in && !db().get(`SELECT id FROM ${spec.in} WHERE id=? AND tenant_id=?`, N(a[need]), N(tid))) fail("No such " + spec.label.toLowerCase().replace(/^the contacts at a /, ""));
  return { kind, ...(need ? { [need]: spec.in ? N(a[need]) : str(a[need], 80) } : {}) };
}
/* the people an audience means, each with every address they could be reached at */
const PEOPLE = {
  customers: t => db().all("SELECT id, name, email FROM users WHERE tenant_id=? AND role='customer' AND COALESCE(disabled,0)=0", t).map(u => ({ name: u.name, email: u.email, phone: "", owner: `t${t}:u:${u.id}` })),
  segment: (t, a) => db().all("SELECT u.id, u.name, u.email FROM segment_members m JOIN users u ON ('t' || u.tenant_id || ':u:' || u.id)=m.owner WHERE m.tenant_id=? AND m.segment=?", t, a.segment).map(u => ({ name: u.name, email: u.email, phone: "", owner: `t${t}:u:${u.id}` })),
  contacts: t => db().all("SELECT name, email, phone, user_id FROM crm_contacts WHERE tenant_id=? AND deleted_at IS NULL", t).map(x => ({ name: x.name, email: x.email, phone: x.phone, owner: x.user_id ? `t${t}:u:${x.user_id}` : "" })),
  company: (t, a) => db().all("SELECT name, email, phone, user_id FROM crm_contacts WHERE tenant_id=? AND company_id=? AND deleted_at IS NULL", t, a.company_id).map(x => ({ name: x.name, email: x.email, phone: x.phone, owner: x.user_id ? `t${t}:u:${x.user_id}` : "" }))
};
/* who the campaign may reach: an address on its channel and a live grant for its purpose, by the person's email */
function eligible(tid, c, p) {
  const field = SEED.channels[c.channel].address, address = String(p[field] || "").trim().toLowerCase();
  if (!address) return { address: "", reason: "no " + field };
  if (!p.email || !C().mayProcess(N(tid), String(p.email).toLowerCase(), c.purpose)) return { address, reason: "no " + c.purpose + " consent" };
  return { address, reason: "" };
}
/* the list, built once: one row per address, the ineligible recorded as skipped with why */
function buildList(t, c) {
  const people = PEOPLE[JSON.parse(c.audience).kind](t, JSON.parse(c.audience));
  if (people.length > SEED.maxRecipients) fail(`This audience has ${people.length} people; a campaign reaches at most ${SEED.maxRecipients}`, 413);
  const seen = new Set();
  for (const p of people) {
    const e = eligible(t, c, p), key = e.address || "none:" + (p.email || p.owner || Math.random());
    if (seen.has(key)) continue; seen.add(key);
    if (!e.address) continue;
    db().run("INSERT OR IGNORE INTO campaign_recipients(tenant_id,campaign_id,address,name,owner,token,status,reason) VALUES(?,?,?,?,?,?,?,?)",
      t, c.id, e.address, str(p.name, 120), p.owner || "", crypto.randomBytes(18).toString("hex"), e.reason ? RS.skipped : RS.queued, e.reason);
  }
}
/* how many people it would reach now, and how many it would skip and why — before it is sent */
function preview(tid, id) {
  const t = N(tid), c = row(t, id), people = PEOPLE[JSON.parse(c.audience).kind](t, JSON.parse(c.audience));
  const out = { reach: 0, skipped: {} }, seen = new Set();
  for (const p of people) { const e = eligible(t, c, p); const key = e.address || p.email || p.owner; if (seen.has(key)) continue; seen.add(key); if (e.reason) out.skipped[e.reason] = (out.skipped[e.reason] || 0) + 1; else out.reach++; }
  return out;
}
function schedule(tid, id, at) {
  const c = row(tid, id), when = str(at, 30);
  if (!when || isNaN(Date.parse(when.replace(" ", "T")))) fail("Say when to send it");
  if (!tagged(c.status, "editable") || tagged(c.status, "due")) fail("Only a draft is scheduled", 409);
  return move(c, "due", { scheduled_at: when.replace("T", " ").slice(0, 19) });
}
function cancel(tid, id) {
  const c = row(tid, id);
  if (tagged(c.status, "terminal")) fail("This campaign is finished", 409);
  /* whoever has not been sent to yet is not sent to */
  return K_tx(() => { db().run("UPDATE campaign_recipients SET status=?, reason='campaign cancelled' WHERE campaign_id=? AND status=?", RS.skipped, c.id, RS.queued); return move(c, "void", tally(c.id)); });
}
/* start sending: the list is built, then sent in batches */
async function send(tid, id) {
  const t = N(tid), c = row(t, id);
  if (tagged(c.status, "editable")) K_tx(() => { buildList(t, c); move(c, "active"); });
  else if (!tagged(c.status, "active")) fail("This campaign is finished", 409);
  return sendBatch(t, id);
}
/* ============================== opens and clicks ==============================
   Each link the store wrote in a message goes out as a tracked link to the platform (/api/m?t=&n=), which
   counts the click and sends the reader on to that link — only to a link the message itself carried. An
   email also goes with an HTML part carrying a one-pixel image (/api/m?t=&o=1) that counts the open, where
   the store's email transport sends HTML. A store turns either off in settings campaigns.tracking. */
const URLS = /https?:\/\/[^\s<>"']+[^\s<>"'.,;:!?)]/g;
const trackingOf = t => { let o = {}; try { o = (require("./settings.js").get(N(t), "campaigns") || {}).tracking || {}; } catch (e) { } return { ...SEED.tracking, ...o }; };
/* the platform's address for a message's token: from the store's public address the campaign or journey was made with */
function trackUrl(t, linkBase, token, q) {
  const base = linkBase ? linkBase.replace("/api/campaigns/unsubscribe", "/api/m") : require("./tell.js").address(t, "api/m?t=");
  return base + encodeURIComponent(token) + q;
}
const escH = v => String(v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
/* a message for one person: { name } filled in, links tracked, the unsubscribe line, and an HTML part for email.
   c: { body, subject, channel, link_base }; r: { token, name }. Returns { subject, text, html?, links, link } */
function compose(t, c, r) {
  const link = c.link_base ? c.link_base + encodeURIComponent(r.token) : require("./tell.js").address(t, "api/campaigns/unsubscribe?t=" + r.token);
  const first = String(r.name || "").split(" ")[0];
  const fill = s => String(s).replace(/\{name\}/g, first).replace(/\{store\}/g, (db().get("SELECT name FROM tenants WHERE id=?", t) || {}).name || "");
  const tr = trackingOf(t), body = fill(c.body), links = body.match(URLS) || [];
  let n = -1;
  const text = tr.clicks ? body.replace(URLS, () => trackUrl(t, c.link_base, r.token, "&n=" + (++n))) : body;
  const out = { subject: fill(c.subject), text: text + "\n\n" + SEED.unsubscribeLine + link, links, link };
  if (c.channel === SEED.htmlChannel) {
    /* the store's own words, each link shown as written and pointing at its tracked address */
    const parts = body.split(URLS), hrefOf = k => tr.clicks ? trackUrl(t, c.link_base, r.token, "&n=" + k) : links[k];
    const html = parts.map((p, k) => escH(p) + (links[k] ? `<a href="${escH(hrefOf(k))}">${escH(links[k])}</a>` : "")).join("").replace(/\n/g, "<br>");
    out.html = `<!doctype html><html><body><div>${html}</div><p style="color:#666;font-size:12px">${escH(SEED.unsubscribeLine)}<a href="${escH(link)}">${escH(link)}</a></p>` +
      (tr.opens ? `<img src="${escH(trackUrl(t, c.link_base, r.token, "&o=1"))}" width="1" height="1" alt="">` : "") + `</body></html>`;
  }
  return out;
}
const message = (t, c, r) => compose(t, c, r);
/* sends one message on a channel to { address, owner } */
function deliver(t, channel, r, m) { return DELIVER[SEED.channels[channel].via](t, { channel }, r, m); }
/* an open or a click on a message's token (a campaign's or a journey's): counted, and for a click where to go */
function track(token, n, open) {
  const tk = String(token || "").slice(0, 80);
  const tables = [["campaign_recipients", "SELECT r.id, c.body links FROM campaign_recipients r JOIN campaigns c ON c.id=r.campaign_id WHERE r.token=?", b => String(b || "").match(URLS) || []],
    ["journey_messages", "SELECT id, links FROM journey_messages WHERE token=?", l => JSON.parse(l || "[]")]];
  for (const [table, q, linksOf] of tables) {
    const r = tk.length >= 20 ? db().get(q, tk) : null;
    if (!r) continue;
    if (open) { db().run(`UPDATE ${table} SET opened_at=COALESCE(opened_at, datetime('now')), opens=opens+1 WHERE id=?`, r.id); return { ok: true }; }
    const to = linksOf(r.links)[Number(n)];
    if (!to) return { ok: false };
    /* a click is also an open: the reader saw the message */
    db().run(`UPDATE ${table} SET clicked_at=COALESCE(clicked_at, datetime('now')), clicks=clicks+1, opened_at=COALESCE(opened_at, datetime('now')) WHERE id=?`, r.id);
    return { ok: true, to };
  }
  return { ok: false };
}
/* the people an audience means — used by journeys enrolled by hand */
function audiencePeople(tid, a) { const x = audienceOf(N(tid), a); return PEOPLE[x.kind](N(tid), x); }
/* how a channel delivers (lib/seed/campaigns.json channels[].via): the store's notification gateway,
   or a note in the shopper's own account */
const DELIVER = {
  gateway: (t, c, r, m) => mailer().send({ tenantId: t, channel: c.channel, to: r.address, subject: m.subject, text: m.text, html: m.html, kind: SEED.record }),
  account: (t, c, r, m) => { require("./tell.js").tell(t, r.owner, SEED.record, m.subject, m.text, "", { email: false }); return { sent: true }; }
};
/* the next batch: each recipient claimed before its message, consent checked again, the outcome kept */
async function sendBatch(tid, id) {
  const t = N(tid), c = row(t, id);
  if (!tagged(c.status, "active")) return status(t, id);
  /* a claim older than the limit was a send that never finished: it is marked, never repeated */
  db().run(`UPDATE campaign_recipients SET status=?, reason='interrupted while sending' WHERE campaign_id=? AND status=? AND claimed_at < datetime('now', ?)`, RS.failed, c.id, RS.sending, `-${SEED.interruptedAfterMinutes} minutes`);
  const batch = db().all("SELECT * FROM campaign_recipients WHERE campaign_id=? AND status=? ORDER BY id LIMIT ?", c.id, RS.queued, SEED.batch);
  for (const r of batch) {
    if (!db().run("UPDATE campaign_recipients SET status=?, claimed_at=datetime('now') WHERE id=? AND status=?", RS.sending, r.id, RS.queued).changes) continue;
    const email = r.owner ? (db().get("SELECT email FROM users WHERE ('t' || tenant_id || ':u:' || id)=?", r.owner) || {}).email : r.address;
    if (!email || !C().mayProcess(t, String(email).toLowerCase(), c.purpose)) { db().run("UPDATE campaign_recipients SET status=?, reason=? WHERE id=?", RS.skipped, "consent withdrawn before sending", r.id); continue; }
    const m = message(t, c, r);
    let out;
    out = await DELIVER[SEED.channels[c.channel].via](t, c, r, m);
    db().run("UPDATE campaign_recipients SET status=?, reason=?, sent_at=? WHERE id=?", out.sent ? RS.sent : RS.failed, out.sent ? "" : str(out.error || "not sent", 200), out.sent ? now() : null, r.id);
  }
  const left = db().get("SELECT COUNT(*) n FROM campaign_recipients WHERE campaign_id=? AND status IN (?,?)", c.id, RS.queued, RS.sending).n;
  const counts = tally(c.id);
  if (!left) K_tx(() => move(row(t, id), "done", counts));
  else RR().change(REC, c.id, () => db().run("UPDATE campaigns SET sent=?, skipped=?, failed=? WHERE id=?", counts.sent, counts.skipped, counts.failed, c.id));
  return status(t, id);
}
function tally(cid) {
  const by = Object.fromEntries(db().all("SELECT status, COUNT(*) n FROM campaign_recipients WHERE campaign_id=? GROUP BY status", cid).map(r => [r.status, r.n]));
  return { sent: by[RS.sent] || 0, skipped: by[RS.skipped] || 0, failed: by[RS.failed] || 0 };
}
function status(tid, id) {
  const c = row(tid, id);
  const reasons = db().all("SELECT reason, COUNT(*) n FROM campaign_recipients WHERE campaign_id=? AND reason<>'' GROUP BY reason", c.id);
  const left = db().get("SELECT COUNT(*) n FROM campaign_recipients WHERE campaign_id=? AND status IN (?,?)", c.id, RS.queued, RS.sending).n;
  const e = db().get("SELECT SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) opened, SUM(CASE WHEN clicked_at IS NOT NULL THEN 1 ELSE 0 END) clicked, SUM(CASE WHEN unsubscribed_at IS NOT NULL THEN 1 ELSE 0 END) unsubscribed FROM campaign_recipients WHERE campaign_id=?", c.id);
  const sent = tally(c.id).sent, pct = x => sent ? +(N(x || 0) * 100 / sent).toFixed(1) : null;
  return { ...get(tid, id), left, reasons, unsubscribed: N(e.unsubscribed) || 0, opened: N(e.opened) || 0, clicked: N(e.clicked) || 0, openRate: pct(e.opened), clickRate: pct(e.clicked) };
}
function get(tid, id) {
  const c = row(tid, id), out = { ...c, audience: JSON.parse(c.audience), ...tally(c.id) };
  const s = c.status;
  out.actions = [tagged(s, "editable") && "send", tagged(s, "editable") && !tagged(s, "due") && "schedule", !tagged(s, "terminal") && "cancel", tagged(s, "active") && "continue"].filter(Boolean);
  return out;
}
function list(tid) { return db().all("SELECT id FROM campaigns WHERE tenant_id=? ORDER BY id DESC LIMIT 200", N(tid)).map(r => get(tid, r.id)); }
/* the link in every message: the grant for the campaign's purpose is withdrawn, once */
function unsubscribe(token) {
  if (/^j/.test(String(token || ""))) return require("./journeys.js").unsubscribe(token);
  const r = db().get("SELECT r.*, c.purpose FROM campaign_recipients r JOIN campaigns c ON c.id=r.campaign_id WHERE r.token=?", String(token || ""));
  if (!r) return { ok: false };
  const email = r.owner ? (db().get("SELECT email FROM users WHERE ('t' || tenant_id || ':u:' || id)=?", r.owner) || {}).email : r.address;
  if (email) C().grantConsent(r.tenant_id, String(email).toLowerCase(), r.purpose, { status: states.first("consent", "withdrawal"), source: "unsubscribe" });
  db().run("UPDATE campaign_recipients SET unsubscribed_at=COALESCE(unsubscribed_at, datetime('now')) WHERE id=?", r.id);
  return { ok: true, store: (db().get("SELECT name FROM tenants WHERE id=?", r.tenant_id) || {}).name || "" };
}
/* scheduled campaigns whose time has come start; sending ones continue */
async function sweepAll() {
  const due = states.tagged(M, "due"), active = states.tagged(M, "active");
  for (const c of db().all(`SELECT id, tenant_id, status, scheduled_at FROM campaigns WHERE status IN (${due.concat(active).map(() => "?").join(",")})`, ...due, ...active)) {
    try {
      if (due.includes(c.status) && !(c.scheduled_at && c.scheduled_at <= now())) continue;
      await send(c.tenant_id, c.id);
    } catch (e) { console.error("campaign " + c.id + ":", e.message); }
  }
}
/* the segments a store has members in (lib/rules.js keeps them) */
const segments = tid => db().all("SELECT segment, COUNT(*) n FROM segment_members WHERE tenant_id=? GROUP BY segment ORDER BY segment", N(tid));
module.exports = { segments, create, get, list, preview, schedule, cancel, send, sendBatch, status, unsubscribe, sweepAll, compose, deliver, track, audiencePeople, SEED };

/* LUXORA Platform — customer relationships (owner Party).

   The companies a store sells to (crm_companies), the people there (crm_contacts), the deals in its
   pipeline (crm_deals) and everything done about them (crm_activities). Each is a record on the
   master (lib/seed/row-records.json): a contact belongs to their company, a deal to its company, an
   activity to its deal — so a company's whole relationship is one walk of the master. Who a contact
   is (name, email, phone) and what was said stay in the tables, where erasure removes them
   (lib/seed/erasure.json); the master keeps that they existed.

   A deal moves through the store's pipeline stages (lib/seed/crm.json, or the store's own in
   settings crm.stages), each with the chance a deal there is won; won and lost are its state
   (crm_deal machine). The forecast is the open pipeline weighted by those chances, by the month
   each deal is expected to close. A deal may start from a shopper's enquiry (a case), and a contact
   who is also a shopper is linked to their person, so one view of a customer brings together their
   orders, payments, returns, support cases, deals and activities (person()). */
"use strict";

const db = () => require("./db.js");
const RR = () => require("./row-records.js");
const states = require("./states.js");
const SEED = require("./seed/crm.json");
const R = SEED.records, M = SEED.machines;
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const N = Number;
const r2 = n => +Number(n || 0).toFixed(2);
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);

/* ============================== the pipeline ============================== */
function stages(tid) {
  const own = require("./settings.js").get(N(tid), "crm.stages");
  return Array.isArray(own) && own.length ? own : SEED.stages;
}
function setStages(tid, list) {
  if (!Array.isArray(list) || !list.length) fail("A pipeline has at least one stage");
  const seen = new Set();
  const out = list.map(s => {
    const key = str(s.key, 40), label = str(s.label, 80), p = N(s.probability);
    if (!/^[a-z][a-z0-9_]{1,39}$/.test(key)) fail("A stage key is lower case letters, digits and underscores");
    if (seen.has(key)) fail("Stage " + key + " is listed twice"); seen.add(key);
    if (!label) fail("Name stage " + key);
    if (!(p >= 0 && p <= 100)) fail("A stage's chance of winning is 0 to 100");
    return { key, label, probability: Math.round(p) };
  });
  const open = states.tagged(M.deal, "open");
  const stuck = db().all(`SELECT DISTINCT stage FROM crm_deals WHERE tenant_id=? AND status IN (${open.map(() => "?").join(",")})`, N(tid), ...open).map(r => r.stage).filter(k => !seen.has(k));
  if (stuck.length) fail("Open deals are still in " + stuck.join(", ") + ": move them before removing the stage", 409);
  const row = db().get("SELECT value FROM settings WHERE tenant_id=? AND key='crm'", N(tid));
  let own = {}; try { own = row ? JSON.parse(row.value) || {} : {}; } catch (e) { own = {}; }
  require("./settings.js").save(N(tid), { crm: { ...own, stages: out } });
  return stages(tid);
}
const stageOf = (tid, key) => stages(tid).find(s => s.key === String(key)) || fail("No stage " + key + " in this store's pipeline");

/* ============================== companies and contacts ============================== */
const companyRow = (tid, id) => db().get("SELECT * FROM crm_companies WHERE id=? AND tenant_id=? AND deleted_at IS NULL", N(id), N(tid)) || fail("No such company", 404);
function saveCompany(tid, input) {
  const i = input || {}, t = N(tid), name = str(i.name, 160);
  if (!name) fail("Name the company");
  const cols = { name, domain: str(i.domain, 120).toLowerCase(), industry: str(i.industry, 80), size: str(i.size, 40), country: str(i.country, 2).toUpperCase(), tax_id: str(i.tax_id, 40), owner_staff: str(i.owner_staff, 120), note: str(i.note, 2000) };
  if (i.id) {
    const c = companyRow(t, i.id), k = Object.keys(cols);
    RR().change(R.company, c.id, () => db().run(`UPDATE crm_companies SET ${k.map(x => x + "=?").join(", ")} WHERE id=?`, ...k.map(x => cols[x]), c.id));
    return companyRow(t, c.id);
  }
  if (db().get("SELECT id FROM crm_companies WHERE tenant_id=? AND lower(name)=lower(?) AND deleted_at IS NULL", t, name)) fail("A company named " + name + " is already here", 409);
  const k = Object.keys(cols);
  const r = RR().created(R.company, () => db().run(`INSERT INTO crm_companies(tenant_id,${k.join(",")}) VALUES(?,${k.map(() => "?").join(",")})`, t, ...k.map(x => cols[x])));
  return companyRow(t, N(r.lastInsertRowid));
}
function companies(tid, f) {
  const o = f || {}, q = "%" + str(o.q, 80) + "%";
  return db().all(`SELECT c.*, (SELECT COUNT(*) FROM crm_contacts x WHERE x.company_id=c.id AND x.deleted_at IS NULL) contacts,
      (SELECT COUNT(*) FROM crm_deals d WHERE d.company_id=c.id) deals FROM crm_companies c WHERE c.tenant_id=? AND c.deleted_at IS NULL AND (c.name LIKE ? OR c.domain LIKE ?) ORDER BY c.name LIMIT 500`, N(tid), q, q);
}
const contactRow = (tid, id) => db().get("SELECT * FROM crm_contacts WHERE id=? AND tenant_id=? AND deleted_at IS NULL", N(id), N(tid)) || fail("No such contact", 404);
/* a contact who is also a shopper of the store is linked to their account, by email */
const userByEmail = (tid, email) => email ? db().get("SELECT id FROM users WHERE tenant_id=? AND lower(email)=lower(?)", N(tid), email) : null;
function saveContact(tid, input) {
  const i = input || {}, t = N(tid), name = str(i.name, 120), email = str(i.email, 200).toLowerCase();
  if (!name) fail("Name the contact");
  if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) fail("That email does not look right");
  if (i.company_id) companyRow(t, i.company_id);
  const u = userByEmail(t, email);
  const cols = { company_id: i.company_id ? N(i.company_id) : null, user_id: u ? u.id : null, name, email, phone: str(i.phone, 40), title: str(i.title, 120) };
  const k = Object.keys(cols);
  if (i.id) {
    const c = contactRow(t, i.id);
    RR().change(R.contact, c.id, () => db().run(`UPDATE crm_contacts SET ${k.map(x => x + "=?").join(", ")} WHERE id=?`, ...k.map(x => cols[x]), c.id));
    return contactRow(t, c.id);
  }
  if (email && db().get("SELECT id FROM crm_contacts WHERE tenant_id=? AND email=? AND deleted_at IS NULL", t, email)) fail(email + " is already a contact", 409);
  const r = RR().created(R.contact, () => db().run(`INSERT INTO crm_contacts(tenant_id,${k.join(",")}) VALUES(?,${k.map(() => "?").join(",")})`, t, ...k.map(x => cols[x])));
  return contactRow(t, N(r.lastInsertRowid));
}
function contacts(tid, f) {
  const o = f || {}, q = "%" + str(o.q, 80) + "%";
  return db().all(`SELECT x.*, c.name company FROM crm_contacts x LEFT JOIN crm_companies c ON c.id=x.company_id WHERE x.tenant_id=? AND x.deleted_at IS NULL AND (?=0 OR x.company_id=?) AND (x.name LIKE ? OR x.email LIKE ?) ORDER BY x.name LIMIT 500`,
    N(tid), N(o.company_id) || 0, N(o.company_id) || 0, q, q);
}

/* ============================== deals ============================== */
const dealRow = (tid, id) => db().get("SELECT * FROM crm_deals WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such deal", 404);
function nextRef(tid) { return SEED.refPrefix + "-" + N(tid) + "-" + String(db().get("SELECT COUNT(*) c FROM crm_deals WHERE tenant_id=?", N(tid)).c + 1).padStart(5, "0"); }
/* { title, company_id?, contact_id?, case_id?, amount, currency?, stage?, expected_close?, owner_staff? } */
function openDeal(tid, input, actor) {
  const i = input || {}, t = N(tid);
  let title = str(i.title, 160), contactId = i.contact_id ? N(i.contact_id) : null, companyId = i.company_id ? N(i.company_id) : null;
  if (i.case_id) {
    /* a shopper's enquiry becomes a deal: its opener is the contact, its item the title */
    const c = db().get("SELECT * FROM cases WHERE id=? AND tenant_id=?", N(i.case_id), t) || fail("No such enquiry", 404);
    if (db().get("SELECT ref FROM crm_deals WHERE tenant_id=? AND case_id=?", t, c.id)) fail("This enquiry is already a deal", 409);
    const m = /:u:(\d+)$/.exec(String(c.owner || "")), u = m && db().get("SELECT id, name, email FROM users WHERE id=? AND tenant_id=?", N(m[1]), t);
    if (u && !contactId) { const ex = db().get("SELECT id FROM crm_contacts WHERE tenant_id=? AND user_id=? AND deleted_at IS NULL", t, u.id); contactId = ex ? ex.id : saveContact(t, { name: u.name || u.email, email: u.email }).id; }
    if (!title) { const p = c.subject_id ? db().get("SELECT title FROM products WHERE tenant_id=? AND id=?", t, String(c.subject_id)) : null; title = p ? p.title : "Enquiry " + c.id; }
  }
  if (!title) fail("Name the deal");
  if (contactId) { const ct = contactRow(t, contactId); if (!companyId) companyId = ct.company_id; }
  if (companyId) companyRow(t, companyId);
  const st = stageOf(t, i.stage || stages(t)[0].key), amount = r2(i.amount);
  if (!(amount >= 0)) fail("A deal's amount is zero or more");
  const currency = str(i.currency || require("./defaults.js").currency(t), 8).toUpperCase();
  require("./wallet.js").unitOf(currency);
  const r = RR().created(R.deal, () => db().run("INSERT INTO crm_deals(tenant_id,ref,title,company_id,contact_id,case_id,amount,currency,stage,probability,status,expected_close,owner_staff) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
    t, nextRef(t), title, companyId, contactId, i.case_id ? N(i.case_id) : null, amount, currency, st.key, st.probability, states.initial(M.deal), i.expected_close || null, str(i.owner_staff || actor, 120)));
  return deal(t, N(r.lastInsertRowid));
}
function deal(tid, id) {
  const d = dealRow(tid, id);
  return { ...d, company: d.company_id ? (db().get("SELECT name FROM crm_companies WHERE id=?", d.company_id) || {}).name : null,
    contact: d.contact_id ? (db().get("SELECT name FROM crm_contacts WHERE id=?", d.contact_id) || {}).name : null,
    stageLabel: (stages(tid).find(s => s.key === d.stage) || { label: d.stage }).label, open: states.is(M.deal, d.status, "open"), activities: timeline(tid, { deal_id: d.id }) };
}
/* moving a deal: its stage (and so its chance), its amount or close date, while it is open */
function updateDeal(tid, id, input) {
  const d = dealRow(tid, id), i = input || {}, set = {};
  if (!states.is(M.deal, d.status, "open")) fail("A closed deal is reopened before it changes", 409);
  if (i.stage !== undefined) { const st = stageOf(tid, i.stage); set.stage = st.key; set.probability = st.probability; }
  if (i.amount !== undefined) { const a = r2(i.amount); if (!(a >= 0)) fail("A deal's amount is zero or more"); set.amount = a; }
  if (i.expected_close !== undefined) set.expected_close = i.expected_close || null;
  if (i.title !== undefined) { if (!str(i.title)) fail("Name the deal"); set.title = str(i.title, 160); }
  if (i.owner_staff !== undefined) set.owner_staff = str(i.owner_staff, 120);
  const k = Object.keys(set); if (!k.length) return deal(tid, id);
  RR().change(R.deal, d.id, () => db().run(`UPDATE crm_deals SET ${k.map(x => x + "=?").join(", ")} WHERE id=?`, ...k.map(x => set[x]), d.id));
  return deal(tid, id);
}
function closeDeal(tid, id, won, reason) {
  const d = dealRow(tid, id), to = states.first(M.deal, won ? "won" : "lost");
  if (!won && !str(reason)) fail("Say why the deal was lost");
  const { patch } = states.apply(M.deal, { tenantId: N(tid), from: d.status, to, row: d });
  const all = { ...patch, probability: won ? 100 : 0, lost_reason: won ? "" : str(reason, 300) }, k = Object.keys(all);
  RR().change(R.deal, d.id, () => db().run(`UPDATE crm_deals SET ${k.map(x => x + "=?").join(", ")} WHERE id=? AND status=?`, ...k.map(x => all[x]), d.id, d.status));
  return deal(tid, id);
}
function reopen(tid, id) {
  const d = dealRow(tid, id), to = states.first(M.deal, "open"), st = stageOf(tid, d.stage);
  states.apply(M.deal, { tenantId: N(tid), from: d.status, to, row: d });
  RR().change(R.deal, d.id, () => db().run("UPDATE crm_deals SET status=?, probability=?, closed_at=NULL, lost_reason='' WHERE id=?", to, st.probability, d.id));
  return deal(tid, id);
}
/* the board: each stage's open deals, then what was won and lost */
function pipeline(tid) {
  const t = N(tid), open = states.tagged(M.deal, "open");
  const rows = db().all(`SELECT d.*, c.name company FROM crm_deals d LEFT JOIN crm_companies c ON c.id=d.company_id WHERE d.tenant_id=? ORDER BY d.expected_close IS NULL, d.expected_close, d.id`, t);
  const isOpen = d => open.includes(d.status);
  return { stages: stages(t).map(s => ({ ...s, deals: rows.filter(d => isOpen(d) && d.stage === s.key) })),
    won: rows.filter(d => states.is(M.deal, d.status, "won")).slice(-50), lost: rows.filter(d => states.is(M.deal, d.status, "lost")).slice(-50) };
}
/* what the open pipeline should bring in, weighted by each stage's chance, by the month a deal is expected to close */
function forecast(tid) {
  const open = states.tagged(M.deal, "open"), won = states.tagged(M.deal, "won");
  const rows = db().all(`SELECT currency, COALESCE(substr(expected_close,1,7),'') month, status, SUM(amount) amount, SUM(amount*probability/100.0) weighted, COUNT(*) n
     FROM crm_deals WHERE tenant_id=? AND status IN (${open.concat(won).map(() => "?").join(",")}) GROUP BY currency, month, status ORDER BY month`, N(tid), ...open, ...won);
  const by = {};
  for (const r of rows) {
    const x = by[r.currency + "|" + r.month] = by[r.currency + "|" + r.month] || { currency: r.currency, month: r.month || null, pipeline: 0, weighted: 0, won: 0, deals: 0 };
    if (open.includes(r.status)) { x.pipeline = r2(x.pipeline + r.amount); x.weighted = r2(x.weighted + r.weighted); x.deals += r.n; } else x.won = r2(x.won + r.amount);
  }
  return Object.values(by);
}

/* ============================== activities ============================== */
const kindOf = k => SEED.activityKinds.find(x => x.key === String(k)) || fail("A store records one of: " + SEED.activityKinds.map(x => x.key).join(", "));
/* { kind, subject, body?, deal_id?, contact_id?, company_id?, due_at?, done? } */
function logActivity(tid, input, actor) {
  const i = input || {}, t = N(tid); kindOf(i.kind);
  const subject = str(i.subject, 200); if (!subject) fail("Say what the activity is");
  let { deal_id, contact_id, company_id } = i;
  if (deal_id) { const d = dealRow(t, deal_id); contact_id = contact_id || d.contact_id; company_id = company_id || d.company_id; }
  if (contact_id) { const c = contactRow(t, contact_id); company_id = company_id || c.company_id; }
  if (company_id) companyRow(t, company_id);
  if (!deal_id && !contact_id && !company_id) fail("An activity is about a deal, a contact or a company");
  const r = RR().created(R.activity, () => db().run("INSERT INTO crm_activities(tenant_id,kind,subject,body,company_id,contact_id,deal_id,due_at,done_at,owner_staff) VALUES(?,?,?,?,?,?,?,?,?,?)",
    t, i.kind, subject, str(i.body, 4000), company_id ? N(company_id) : null, contact_id ? N(contact_id) : null, deal_id ? N(deal_id) : null, i.due_at || null, i.done ? new Date().toISOString().slice(0, 19).replace("T", " ") : null, str(i.owner_staff || actor, 120)));
  return db().get("SELECT * FROM crm_activities WHERE id=?", N(r.lastInsertRowid));
}
function completeActivity(tid, id, outcome) {
  const a = db().get("SELECT * FROM crm_activities WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such activity", 404);
  if (a.done_at) fail("Already done", 409);
  RR().change(R.activity, a.id, () => db().run("UPDATE crm_activities SET done_at=datetime('now'), outcome=? WHERE id=?", str(outcome, 500), a.id));
  return db().get("SELECT * FROM crm_activities WHERE id=?", a.id);
}
/* everything done about a deal, a contact or a company, newest first; what is still to do first of all */
function timeline(tid, f) {
  const o = f || {};
  const [col, val] = o.deal_id ? ["deal_id", o.deal_id] : o.contact_id ? ["contact_id", o.contact_id] : o.company_id ? ["company_id", o.company_id] : [null, null];
  if (!col) fail("Say whose timeline");
  return db().all(`SELECT * FROM crm_activities WHERE tenant_id=? AND ${col}=? ORDER BY done_at IS NOT NULL, COALESCE(done_at, due_at, created_at) DESC, id DESC LIMIT 300`, N(tid), N(val));
}
/* what the team has to do: open activities by due date */
function agenda(tid, staff) {
  return db().all(`SELECT a.*, d.ref deal_ref, x.name contact FROM crm_activities a LEFT JOIN crm_deals d ON d.id=a.deal_id LEFT JOIN crm_contacts x ON x.id=a.contact_id
     WHERE a.tenant_id=? AND a.done_at IS NULL AND (?='' OR a.owner_staff=?) ORDER BY a.due_at IS NULL, a.due_at LIMIT 200`, N(tid), str(staff), str(staff));
}

/* ============================== one view of a customer ============================== */
/* a shopper of the store, with everything the store has with them: on the master their person's
   orders, and from the records their payments, returns, support cases, deals and activities */
function person(tid, userId) {
  const t = N(tid), u = db().get("SELECT id, uid, name, email, role, created_at FROM users WHERE id=? AND tenant_id=?", N(userId), t) || fail("No such customer", 404);
  const owner = `t${t}:u:${u.id}`;
  const orders = db().all("SELECT id, num, status, total, currency, created_at FROM orders WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 100", t, owner);
  const ids = orders.map(o => o.id), inIds = ids.length ? `(${ids.map(() => "?").join(",")})` : "(NULL)";
  const spent = db().all(`SELECT currency, SUM(amount - COALESCE(refunded,0)) net, COUNT(*) n FROM payments WHERE tenant_id=? AND order_id IN ${inIds} AND status IN (${states.tagged("payment", "settled").concat(states.tagged("payment", "reversed")).map(() => "?").join(",")}) GROUP BY currency`,
    t, ...ids, ...states.tagged("payment", "settled"), ...states.tagged("payment", "reversed"));
  const contactsOf = db().all("SELECT x.*, c.name company FROM crm_contacts x LEFT JOIN crm_companies c ON c.id=x.company_id WHERE x.tenant_id=? AND x.user_id=? AND x.deleted_at IS NULL", t, u.id);
  const cids = contactsOf.map(c => c.id), inC = cids.length ? `(${cids.map(() => "?").join(",")})` : "(NULL)";
  return {
    person: { id: u.id, uid: u.uid, name: u.name, email: u.email, since: u.created_at, onMaster: !!require("./kernel.js").internal.nodeRow(u.uid || "") },
    orders, spent: spent.map(s => ({ currency: s.currency, net: r2(s.net), payments: s.n })),
    returns: db().all(`SELECT id, ref, order_id, product_id, qty, status, created_at FROM returns WHERE tenant_id=? AND order_id IN ${inIds} ORDER BY id DESC`, t, ...ids),
    cases: db().all("SELECT id, ref, subject, status, priority, created_at FROM tickets WHERE tenant_id=? AND (owner=? OR lower(owner_email)=lower(?)) ORDER BY id DESC LIMIT 50", t, owner, u.email || ""),
    wallet: (() => { try { return require("./wallet.js").walletsOf(t, owner).map(w => ({ name: w.name, unit: w.unit, balance: w.balance })); } catch (e) { return []; } })(),
    segments: db().all("SELECT segment FROM segment_members WHERE tenant_id=? AND owner=?", t, owner).map(r => r.segment),
    contacts: contactsOf,
    deals: db().all(`SELECT id, ref, title, amount, currency, stage, status FROM crm_deals WHERE tenant_id=? AND contact_id IN ${inC} ORDER BY id DESC`, t, ...cids),
    activities: db().all(`SELECT * FROM crm_activities WHERE tenant_id=? AND contact_id IN ${inC} ORDER BY id DESC LIMIT 100`, t, ...cids)
  };
}
module.exports = { stages, setStages, saveCompany, companies, company: (tid, id) => ({ ...companyRow(tid, id), contacts: contacts(tid, { company_id: id }), deals: db().all("SELECT * FROM crm_deals WHERE tenant_id=? AND company_id=? ORDER BY id DESC", N(tid), N(id)), activities: timeline(tid, { company_id: id }) }),
  saveContact, contacts, contact: contactRow, openDeal, deal, updateDeal, closeDeal, reopen, pipeline, forecast, logActivity, completeActivity, timeline, agenda, person, SEED };

/* Customer relationships (lib/crm.js): companies and the people there, deals moving through the
   store's own pipeline to won or lost, the activities on a timeline, the forecast, one view of a
   customer — each on the master — and erasure that really removes a person (lib/seed/erasure.json). */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "crm-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), C = require("../lib/crm.js"), RR = require("../lib/row-records.js"), CO = require("../lib/compliance.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message) || (console.log("    (threw: " + e.message + ")"), false); } };
try {
  const t = 1;
  console.log("▸ COMPANIES AND THE PEOPLE THERE");
  const acme = C.saveCompany(t, { name: "Acme Fleet Ltd", domain: "ACME.example", industry: "logistics", country: "gb" });
  ok(acme.domain === "acme.example" && acme.country === "GB" && K.internal.nodeRow(acme.uid).kind === "party.company" && K.isA("party.company", "party.organisation", "platform"), "a company is on the master, as an organisation of the master", acme);
  ok(throws(() => C.saveCompany(t, { name: "acme fleet ltd" }), /already here/), "a company is not added twice");
  const uid = db.newUser(t, "Priya Buyer", "priya@acme.example", "Long-Enough-Pass-9", "customer");
  const priya = C.saveContact(t, { name: "Priya Buyer", email: "Priya@Acme.example", title: "Head of procurement", company_id: acme.id, phone: "+44 20 0000 0000" });
  ok(priya.user_id === uid && RR.at("crm_contact", priya.id).belongsTo === acme.uid, "a contact belongs to their company, and is linked to their shopper account by email");
  ok(!db.all("SELECT attrs FROM k_versions WHERE node=?", priya.uid).some(v => /Priya|acme\.example|\+44/.test(v.attrs)), "who they are — name, email, phone — is not copied onto the master");
  ok(throws(() => C.saveContact(t, { name: "x", email: "not-an-email" }), /does not look right/) && throws(() => C.saveContact(t, { name: "x", email: "priya@acme.example" }), /already a contact/), "a contact's email is checked, and used once");

  console.log("▸ DEALS THROUGH THE PIPELINE");
  const d = C.openDeal(t, { title: "40 vans, 3-year service", contact_id: priya.id, amount: 120000, expected_close: "2027-02-15" }, "sam");
  ok(d.company_id === acme.id && d.stage === "qualify" && d.probability === 10 && d.open && d.owner_staff === "sam", "a deal opens in the first stage, with its chance, under the contact's company", d);
  ok(RR.at("crm_deal", d.id).belongsTo === acme.uid, "and is on the master under the company");
  C.updateDeal(t, d.id, { stage: "proposal" });
  ok(C.deal(t, d.id).probability === 50 && throws(() => C.updateDeal(t, d.id, { stage: "nowhere" }), /No stage/), "moving it to a stage gives it that stage's chance; only the pipeline's stages are allowed");
  const d2 = C.openDeal(t, { title: "Spare parts", company_id: acme.id, amount: 8000, stage: "negotiation", expected_close: "2027-02-20" });
  const f = C.forecast(t).find(x => x.month === "2027-02");
  ok(f && f.pipeline === 128000 && f.weighted === 66000 && f.deals === 2, "the forecast: the open pipeline weighted by each stage's chance, by month", f);
  ok(throws(() => C.closeDeal(t, d2.id, false, ""), /Say why/), "a lost deal says why");
  C.closeDeal(t, d2.id, false, "chose a cheaper supplier");
  C.closeDeal(t, d.id, true);
  ok(C.deal(t, d.id).status === "won" && C.deal(t, d.id).closed_at && C.deal(t, d.id).probability === 100, "won: stamped and certain");
  ok(throws(() => C.updateDeal(t, d.id, { amount: 1 }), /reopened before/), "a closed deal does not change");
  ok(throws(() => C.reopen(t, d.id), /./) && C.reopen(t, d2.id).status === "open", "a won deal stays won; a lost one can be reopened");
  ok(RR.history("crm_deal", d.id, "stage").map(h => h.value).join() === "qualify,proposal", "its history keeps every stage it went through");
  const board = C.pipeline(t);
  ok(board.stages.find(s => s.key === "negotiation").deals.some(x => x.id === d2.id) && board.won.some(x => x.id === d.id), "the board shows each stage's open deals, and what was won");

  console.log("▸ THE STORE'S OWN PIPELINE");
  ok(throws(() => C.setStages(t, [{ key: "lead", label: "Lead", probability: 5 }]), /still in negotiation/), "a stage with open deals cannot be removed");
  const own = C.setStages(t, [{ key: "lead", label: "Lead", probability: 5 }, { key: "negotiation", label: "Negotiation", probability: 80 }]);
  ok(own.length === 2 && C.stages(t)[0].key === "lead" && throws(() => C.setStages(t, [{ key: "x", label: "", probability: 200 }]), /./), "a store sets its own stages and chances, checked");

  console.log("▸ ACTIVITIES ON A TIMELINE");
  ok(throws(() => C.logActivity(t, { kind: "fax", subject: "x", deal_id: d2.id }), /one of: call/), "only the declared kinds of activity");
  const call = C.logActivity(t, { kind: "call", subject: "Price objection", body: "Priya said the budget is fixed", deal_id: d2.id, done: true }, "sam");
  const task = C.logActivity(t, { kind: "task", subject: "Send revised quote", deal_id: d2.id, due_at: "2027-01-10" }, "sam");
  ok(call.contact_id === null && call.company_id === acme.id && RR.at("crm_activity", call.id).belongsTo === C.deal(t, d2.id).uid, "an activity takes its deal's company, and is on the master under the deal");
  ok(C.timeline(t, { company_id: acme.id })[0].id === task.id && C.agenda(t, "sam").some(a => a.id === task.id), "what is still to do comes first on the timeline and in the agenda");
  C.completeActivity(t, task.id, "sent");
  ok(!C.agenda(t, "sam").some(a => a.id === task.id) && throws(() => C.completeActivity(t, task.id), /Already done/), "done once");
  ok(!db.all("SELECT attrs FROM k_versions WHERE node=?", call.uid).some(v => /budget|Price objection/.test(v.attrs)), "what was said is not copied onto the master");

  console.log("▸ ONE VIEW OF A CUSTOMER");
  const oid = Number(db.run("INSERT INTO orders(tenant_id,owner,num,name,sub,total,status,currency) VALUES(?,?,?,?,10,10,'delivered','USD')", t, "t1:u:" + uid, "CRM-1", "Priya").lastInsertRowid);
  require("../lib/order-records.js").change(oid, () => null);
  const p = C.person(t, uid);
  ok(p.person.onMaster && p.orders.some(o => o.num === "CRM-1") && p.deals.some(x => x.id === d.id) && p.contacts[0].company === "Acme Fleet Ltd", "a customer's orders, deals and company in one view", { orders: p.orders.length, deals: p.deals.length });

  console.log("▸ ERASURE REMOVES THE PERSON");
  const owner = "t1:u:" + uid;
  db.run("INSERT INTO addresses(tenant_id,owner,name,address,city) VALUES(?,?,?,?,?)", t, owner, "Priya", "1 High St", "London");
  db.run("INSERT INTO qna_questions(tenant_id,product_id,owner,name,body) VALUES(?,?,?,?,?)", t, "LX-ELS-001", owner, "Priya", "Does it fit?");
  db.run("INSERT INTO reviews(tenant_id,product_id,user_id,name,rating,title,body) VALUES(?,?,?,?,?,?,?)", t, "LX-ELS-001", uid, "Priya", 5, "Great", "Loved it");
  const tk = require("../lib/helpdesk.js").openTicket(t, { subject: "Help", name: "Priya", email: "priya@acme.example", owner });
  const tkId = tk.id || db.get("SELECT id FROM tickets WHERE owner=?", owner).id;
  const out = CO.eraseSubject(t, "priya@acme.example", "dpo");
  ok(out.ok && !out.failed.length, "erasure finishes with nothing it could not clear", out);
  const left = { addresses: db.get("SELECT COUNT(*) c FROM addresses WHERE owner=?", owner).c, questions: db.get("SELECT COUNT(*) c FROM qna_questions WHERE owner=?", owner).c, reviews: db.get("SELECT COUNT(*) c FROM reviews WHERE user_id=?", uid).c,
    tickets: db.get("SELECT COUNT(*) c FROM tickets WHERE id=?", tkId).c, contacts: db.get("SELECT COUNT(*) c FROM crm_contacts WHERE email='priya@acme.example'").c, activities: db.get("SELECT COUNT(*) c FROM crm_activities WHERE contact_id=?", priya.id).c, users: db.get("SELECT COUNT(*) c FROM users WHERE id=?", uid).c };
  ok(Object.values(left).every(n => n === 0), "their addresses, questions, reviews, support cases, contact, its activities and account are gone", left);
  ok(db.get("SELECT COUNT(*) c FROM orders WHERE id=?", oid).c === 1 && db.get("SELECT COUNT(*) c FROM crm_deals WHERE id=?", d.id).c === 1, "orders and deals the store must keep are kept");
  ok(require("../lib/kernel-lifecycle.js").nodeState(priya.uid) === K.SEED.lifecycle.nodeStates.archived, "the contact's record on the master is archived");
  const ou = db.get("SELECT uid FROM orders WHERE id=?", oid).uid;
  ok(K.internal.nodeRow(ou) && require("../lib/order-records.js").at(oid).buyer === null && !K.internal.nodeRow(p.person.uid), "the order stays on the master, no longer linked to the erased person, who is gone from it");
} catch (e) { failed++; console.log("  ✗ threw: " + e.stack); }
finally { wipe(); console.log(`\n${passed} passed, ${failed} failed`); process.exit(failed ? 1 : 0); }

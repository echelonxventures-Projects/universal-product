/* Campaigns (lib/campaigns.js): a message to an audience, sent only to people who agreed to it —
   checked when the list is built and again just before each message — with a link in every message
   that withdraws the agreement; never sent twice to anyone, even by two senders at once; marked, not
   repeated, when interrupted; scheduled; and erased with the person. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "campaigns-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), CA = require("../lib/campaigns.js"), CO = require("../lib/compliance.js"), CRM = require("../lib/crm.js"), RR = require("../lib/row-records.js");
const mailer = require("../lib/mailer.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message) || (console.log("    (threw: " + e.message + ")"), false); } };
const sent = [];
mailer.send = async o => { await new Promise(r => setTimeout(r, 2)); sent.push(o); return { sent: true }; };
(async () => {
  try {
    const t = 1;
    for (const u of db.all("SELECT id FROM users WHERE tenant_id=? AND role='customer'", t)) db.run("UPDATE users SET role='staff_test' WHERE id=?", u.id);
    const mk = (name, email) => db.newUser(t, name, email, "Long-Enough-Pass-9", "customer");
    const ana = mk("Ana Yes", "ana@example.com"), ben = mk("Ben No", "ben@example.com"), cy = mk("Cy Later", "cy@example.com");
    CO.grantConsent(t, "ana@example.com", "marketing", { source: "signup" }); CO.grantConsent(t, "cy@example.com", "marketing", { source: "signup" });

    console.log("▸ A CAMPAIGN AND WHO IT MAY REACH");
    ok(throws(() => CA.create(t, { name: "x", channel: "fax", body: "b", audience: { kind: "customers" } }), /one of: email/) && throws(() => CA.create(t, { name: "x", channel: "email", body: "b", subject: "s", audience: { kind: "everyone" } }), /goes to one of/), "only declared channels and audiences");
    const c = CA.create(t, { name: "Winter sale", channel: "email", subject: "{name}, winter is here at {store}", body: "Hello {name}, 20% off this week.", audience: { kind: "customers" } }, "marketer");
    ok(c.status === "draft" && K.internal.nodeRow(c.uid).kind === "communication.campaign" && c.actions.includes("send"), "a campaign is drafted, on the master");
    const pv = CA.preview(t, c.id);
    ok(pv.reach === 2 && pv.skipped["no marketing consent"] === 1, "before sending: 2 have agreed to marketing, 1 has not", pv);

    console.log("▸ SENDING, ONLY TO WHO AGREED");
    const origBatch = CA.SEED.batch; CA.SEED.batch = 0;
    await CA.send(t, c.id);   /* the list is built: Ana and Cy are queued */
    CA.SEED.batch = origBatch;
    ok(db.get("SELECT COUNT(*) n FROM campaign_recipients WHERE campaign_id=? AND status='queued'", c.id).n === 2, "the list holds the two who agreed");
    CO.grantConsent(t, "cy@example.com", "marketing", { status: "withdrawn" });
    await CA.sendBatch(t, c.id);
    const st = CA.status(t, c.id);
    ok(sent.length === 1 && sent[0].to === "ana@example.com" && st.status === "sent" && st.sent === 1 && st.skipped === 2, "only Ana is sent to; Ben never agreed, Cy withdrew before her message", { sent: sent.map(s => s.to), st: { sent: st.sent, skipped: st.skipped, status: st.status } });
    ok(st.reasons.some(r => r.reason === "no marketing consent") && st.reasons.some(r => r.reason === "consent withdrawn before sending") && sent[0].subject === "Ana, winter is here at " + db.get("SELECT name FROM tenants WHERE id=?", t).name && /Hello Ana, 20% off/.test(sent[0].text), "each message is personal, and each skip says why", st.reasons);
    ok(/To stop these messages: .*api\/campaigns\/unsubscribe\?t=[0-9a-f]{36}/.test(sent[0].text), "every message carries its own unsubscribe link", sent[0].text);
    ok(RR.at("campaign", c.id).sent === 1 && RR.at("campaign", c.id).status === "sent" && st.finished_at, "the master records what was sent and when");
    ok(throws(() => CA.schedule(t, c.id, "2030-01-01"), /Only a draft/), "a sent campaign does not go again");

    console.log("▸ UNSUBSCRIBING");
    const token = /t=([0-9a-f]+)/.exec(sent[0].text)[1];
    ok(CA.unsubscribe(token).ok && !CO.mayProcess(t, "ana@example.com", "marketing") && CA.status(t, c.id).unsubscribed === 1, "the link withdraws Ana's marketing consent");
    ok(!CA.unsubscribe("nope").ok, "a link that is not one does nothing");
    const c2 = CA.create(t, { name: "Again", channel: "email", subject: "s", body: "b", audience: { kind: "customers" } });
    ok(CA.preview(t, c2.id).reach === 0, "and the next campaign does not reach her");

    console.log("▸ NEVER TWICE, EVEN BY TWO SENDERS");
    for (const e of ["ana", "ben", "cy"]) CO.grantConsent(t, e + "@example.com", "marketing", { source: "test" });
    sent.length = 0;
    const c3 = CA.create(t, { name: "Twice", channel: "email", subject: "s", body: "b", audience: { kind: "customers" } });
    db.run("UPDATE campaigns SET status='sending' WHERE id=?", c3.id);
    const built = CA.create(t, { name: "Build", channel: "email", subject: "s", body: "b", audience: { kind: "customers" } });
    await Promise.all([CA.send(t, built.id).catch(() => null), CA.sendBatch(t, built.id), CA.sendBatch(t, built.id)]);
    const to = sent.map(s => s.to).sort();
    ok(to.length === 3 && new Set(to).size === 3, "three senders at once: each person gets one message", to);

    console.log("▸ INTERRUPTED, SCHEDULED, CANCELLED");
    const c4 = CA.create(t, { name: "Cut", channel: "email", subject: "s", body: "b", audience: { kind: "customers" } });
    CA.SEED.batch = 0; await CA.send(t, c4.id); CA.SEED.batch = origBatch;
    const one = db.get("SELECT id FROM campaign_recipients WHERE campaign_id=? ORDER BY id LIMIT 1", c4.id).id;
    db.run("UPDATE campaign_recipients SET status='sending', claimed_at=datetime('now','-2 hours') WHERE id=?", one);
    sent.length = 0; await CA.sendBatch(t, c4.id);
    ok(db.get("SELECT status, reason FROM campaign_recipients WHERE id=?", one).reason === "interrupted while sending" && sent.length === 2, "a send cut off mid-way is marked, never repeated; the rest go", sent.length);
    const c5 = CA.create(t, { name: "Later", channel: "email", subject: "s", body: "b", audience: { kind: "customers" } });
    ok(throws(() => CA.schedule(t, c5.id, "not a date"), /Say when/), "scheduling needs a time");
    CA.schedule(t, c5.id, "2000-01-01 00:00:00");
    sent.length = 0; await CA.sweepAll();
    ok(CA.get(t, c5.id).status === "sent" && sent.length === 3, "a scheduled campaign goes when its time has come");
    const c6 = CA.create(t, { name: "Never", channel: "email", subject: "s", body: "b", audience: { kind: "customers" } });
    CA.schedule(t, c6.id, "2099-01-01 00:00:00"); await CA.sweepAll();
    ok(CA.get(t, c6.id).status === "scheduled" && CA.cancel(t, c6.id).status === "cancelled" && throws(() => CA.cancel(t, c6.id), /finished/), "one not yet due waits; cancelled, it is finished");

    console.log("▸ IN THE SHOPPER'S ACCOUNT, AND TO A COMPANY'S PEOPLE");
    const n0 = db.get("SELECT COUNT(*) n FROM notifications WHERE owner=?", "t1:u:" + ana).n;
    const c7 = CA.create(t, { name: "Note", channel: "in_app", subject: "A note", body: "Hi {name}", audience: { kind: "customers" } });
    await CA.send(t, c7.id);
    ok(db.get("SELECT COUNT(*) n FROM notifications WHERE owner=? AND kind='campaign'", "t1:u:" + ana).n === n0 + 1, "an in-app campaign reaches the shopper's account");
    const co = CRM.saveCompany(t, { name: "Beta Co" });
    CRM.saveContact(t, { name: "Dee Buyer", email: "dee@beta.example", company_id: co.id });
    CRM.saveContact(t, { name: "Eve Buyer", email: "eve@beta.example", company_id: co.id });
    CO.grantConsent(t, "dee@beta.example", "marketing", { source: "form" });
    const c8 = CA.create(t, { name: "B2B", channel: "email", subject: "s", body: "b", audience: { kind: "company", company_id: co.id } });
    ok(CA.preview(t, c8.id).reach === 1, "the people at one company who agreed: a contact without a shopper account too");

    console.log("▸ ERASED WITH THE PERSON");
    const before = db.get("SELECT COUNT(*) n FROM campaign_recipients WHERE address='ana@example.com'").n;
    const er = CO.eraseSubject(t, "ana@example.com", "dpo");
    ok(before > 0 && er.ok && db.get("SELECT COUNT(*) n FROM campaign_recipients WHERE address='ana@example.com'").n === 0, "her rows in every campaign are erased", er);
  } catch (e) { failed++; console.log("  ✗ threw: " + e.stack); }
  finally { wipe(); console.log(`\n${passed} passed, ${failed} failed`); process.exit(failed ? 1 : 0); }
})();

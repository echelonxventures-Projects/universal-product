/* Journeys (lib/journeys.js) and message tracking (lib/campaigns.js track): messages sent on their own
   when something happens or to an audience enrolled by hand, step by step, only to people who agreed
   to marketing; an event that ends a journey early; the daily cap; unsubscribing from every journey;
   and opens and clicks counted for journeys and campaigns. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "journeys-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), J = require("../lib/journeys.js"), CA = require("../lib/campaigns.js"), CO = require("../lib/compliance.js");
const mailer = require("../lib/mailer.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message) || (console.log("    (threw: " + e.message + ")"), false); } };
const sent = [];
mailer.send = async o => { sent.push(o); return { sent: true }; };
const at = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");
const due = () => db.run("UPDATE journey_enrolments SET next_at=? WHERE next_at IS NOT NULL", at(Date.now() - 1000));
(async () => {
  try {
    const t = 1;
    for (const u of db.all("SELECT id FROM users WHERE tenant_id=? AND role='customer'", t)) db.run("UPDATE users SET role='staff_test' WHERE id=?", u.id);
    const mk = (name, email) => db.newUser(t, name, email, "Long-Enough-Pass-9", "customer");
    const ana = mk("Ana Yes", "ana@example.com"), ben = mk("Ben No", "ben@example.com"), cy = mk("Cy Yes", "cy@example.com");
    for (const e of ["ana@example.com", "cy@example.com"]) CO.grantConsent(t, e, "marketing", { source: "signup" });
    const owner = id => `t${t}:u:${id}`;

    console.log("▸ MAKING A JOURNEY");
    ok(throws(() => J.create(t, { name: "x", trigger: "birthday", steps: [{ channel: "email", subject: "s", body: "b" }] }), /starts on one of/), "a journey starts on a declared trigger");
    ok(throws(() => J.create(t, { name: "x", trigger: "customer.created", steps: [] }), /at least one step/) && throws(() => J.create(t, { name: "x", trigger: "customer.created", steps: [{ channel: "fax", body: "b" }] }), /goes by one of/)
      && throws(() => J.create(t, { name: "x", trigger: "customer.created", steps: [{ channel: "email", body: "b" }] }), /subject/) && throws(() => J.create(t, { name: "x", trigger: "customer.created", steps: [{ channel: "in_app", subject: "s", body: "b", wait_minutes: 9e9 }] }), /a wait is/),
      "each step needs a channel, a message, a subject where the channel has one, and a sane wait");
    ok(throws(() => J.create(t, { name: "x", trigger: "order.created", exit_on: ["order.created"], steps: [{ channel: "in_app", subject: "s", body: "b" }] }), /cannot end on the event that starts it/), "a journey does not end on what starts it");
    const welcome = J.create(t, { name: "Welcome", trigger: "customer.created", steps: [
      { wait_minutes: 0, channel: "email", subject: "Welcome to {store}, {name}", body: "Hello {name}. Start here: https://shop.example.com/new?x=1 and see https://shop.example.com/deals." },
      { wait_minutes: 2880, channel: "in_app", subject: "Still looking?", body: "Ten percent off your first order." }] }, "marketer");
    ok(welcome.status === "draft" && K.internal.nodeRow(welcome.uid).kind === "communication.journey" && welcome.actions.includes("start"), "a journey is drafted, on the master");
    ok(J.onEvent(t, "customer.created", { user_id: ana }).entered === 0, "nobody enters a journey that has not started");
    J.start(t, welcome.id);

    console.log("▸ AN EVENT STARTS IT, FOR WHO AGREED");
    ok(J.onEvent(t, "customer.created", { user_id: ana }).entered === 1, "the person the event is about enters");
    ok(J.onEvent(t, "customer.created", { user_id: ben }).entered === 0, "someone who has not agreed to marketing does not");
    ok(J.onEvent(t, "customer.created", { user_id: ana }).entered === 0, "a person enters a journey once");
    await J.sendDue(t);
    ok(sent.length === 1 && sent[0].to === "ana@example.com" && sent[0].subject.startsWith("Welcome to ") && /Hello Ana\./.test(sent[0].text), "the first step goes straight away, personal", sent.map(s => [s.to, s.subject]));
    ok(/api\/m\?t=j[0-9a-f]{36}&n=0/.test(sent[0].text) && /&n=1/.test(sent[0].text) && !/shop\.example\.com\/new/.test(sent[0].text), "links go out as tracked links", sent[0].text);
    ok(/To stop these messages: .*t=j[0-9a-f]{36}/.test(sent[0].text), "every message carries its own unsubscribe link");
    ok(/<img src="[^"]*api\/m\?t=j[0-9a-f]{36}&amp;o=1"/.test(sent[0].html || "") && /<a href="[^"]*&amp;n=0">https:\/\/shop\.example\.com\/new\?x=1<\/a>/.test(sent[0].html), "an email has an HTML part: the links as written, pointing at their tracked address, and the open pixel", (sent[0].html || "").slice(0, 300));
    await J.sendDue(t);
    ok(sent.length === 1, "the next step waits its time");

    console.log("▸ OPENS AND CLICKS");
    const tok = /t=(j[0-9a-f]{36})/.exec(sent[0].text)[1];
    ok(CA.track(tok, null, true).ok, "the pixel counts an open");
    const go = CA.track(tok, 1, false);
    ok(go.ok && go.to === "https://shop.example.com/deals", "a click goes on to the link the message carried", go);
    ok(!CA.track(tok, 7, false).ok && !CA.track("j" + "0".repeat(36), 0, false).ok, "only to a link of that message: never anywhere else");
    let w = J.get(t, welcome.id).steps[0];
    ok(w.sent === 1 && w.opened === 1 && w.clicked === 1 && w.openRate === 100 && w.clickRate === 100, "each step shows its sends, opens and clicks", w);

    console.log("▸ STEP BY STEP, TO THE END");
    due(); await J.sendDue(t);
    const note = db.get("SELECT * FROM notifications WHERE owner=? ORDER BY id DESC LIMIT 1", owner(ana));
    ok(note && note.title === "Still looking?", "the second step reaches the shopper's account", note);
    const g = J.get(t, welcome.id);
    ok(g.people.done === 1 && g.people.active === 0 && g.entered === 1, "after the last step the person is done", g.people);

    console.log("▸ AN EVENT ENDS IT EARLY: THE ABANDONED CART");
    const cart = J.create(t, { name: "Cart", trigger: "cart.abandoned", exit_on: ["order.created"], steps: [
      { wait_minutes: 60, channel: "in_app", subject: "You left something", body: "Your cart is waiting." }, { wait_minutes: 1440, channel: "in_app", subject: "Last chance", body: "Still waiting." }] });
    J.start(t, cart.id);
    db.run("INSERT INTO cart_items(owner, product_id, qty, added_at) VALUES(?,?,1,?)", owner(cy), "p-1", at(Date.now() - 10 * 60000));
    ok(J.findAbandoned(t) === 0, "a cart touched a moment ago is not abandoned");
    db.run("UPDATE cart_items SET added_at=? WHERE owner=?", at(Date.now() - 5 * 3600000), owner(cy));
    db.run("INSERT INTO cart_items(owner, product_id, qty, added_at) VALUES(?,?,1,?)", owner(ben), "p-1", at(Date.now() - 5 * 3600000));
    ok(J.findAbandoned(t) === 1, "a cart left for hours enters its owner — the one who agreed to marketing");
    ok(J.findAbandoned(t) === 0, "the same cart enters once");
    db.run("INSERT INTO orders(tenant_id, owner, num, total) VALUES(?,?,?,?)", t, owner(cy), "ORD-J-1", 10);
    const ex = J.onEvent(t, "order.created", { num: "ORD-J-1" });
    ok(ex.left === 1 && J.get(t, cart.id).people.stopped === 1, "an order takes the person out before the reminder", ex);
    due(); const before = sent.length + db.get("SELECT COUNT(*) n FROM notifications WHERE title='You left something'").n; await J.sendDue(t);
    ok(db.get("SELECT COUNT(*) n FROM notifications WHERE title='You left something'").n + sent.length === before, "and nothing more is sent to them");

    console.log("▸ BY HAND, AN AUDIENCE");
    ok(throws(() => J.enrolAudience(t, welcome.id, { kind: "customers" }), /not by hand/), "a journey started by an event is not enrolled by hand");
    const news = J.create(t, { name: "Newsletter series", trigger: "audience", reenter: false, steps: [{ channel: "in_app", subject: "Part 1", body: "One" }, { channel: "in_app", subject: "Part 2", body: "Two", wait_minutes: 10 }] });
    ok(throws(() => J.enrolAudience(t, news.id, { kind: "customers" }), /Start the journey/), "only a live journey takes people");
    J.start(t, news.id);
    const en = J.enrolAudience(t, news.id, { kind: "customers" });
    ok(en.entered === 2 && en.skipped === 1, "everyone in the audience who agreed enters; the rest are skipped", en);

    console.log("▸ THE DAILY CAP");
    J.SEED.maxPerDay = 2;
    due(); await J.sendDue(t);
    const anaToday = db.get("SELECT COUNT(*) n FROM journey_messages WHERE person='ana@example.com' AND sent_at >= ?", at(Date.now() - 86400000)).n;
    const held = db.get("SELECT next_at FROM journey_enrolments WHERE journey_id=? AND person='ana@example.com'", news.id);
    ok(anaToday === 2 && held.next_at > at(Date.now() + 20 * 3600000), "Ana has had her two messages today: the next waits for tomorrow", { anaToday, held });
    J.SEED.maxPerDay = 3;

    console.log("▸ PAUSED, CHANGED, ENDED");
    J.pause(t, news.id);
    ok(throws(() => J.update(t, welcome.id, { name: "W2" }), /Pause the journey/), "a live journey is paused before it is changed");
    ok(J.update(t, news.id, { steps: [{ channel: "in_app", subject: "P1", body: "1" }, { channel: "in_app", subject: "P2 new", body: "2" }] }).steps[1].subject === "P2 new", "a paused journey takes new steps");
    ok(throws(() => J.update(t, news.id, { trigger: "order.created" }), /make a new one/), "but not a new trigger once people have entered");
    due(); const n0 = db.get("SELECT COUNT(*) n FROM journey_messages").n; await J.sendDue(t);
    ok(db.get("SELECT COUNT(*) n FROM journey_messages").n === n0, "a paused journey sends nothing");
    J.end(t, news.id);
    ok(J.get(t, news.id).people.active === 0 && J.get(t, news.id).actions.length === 0, "an ended journey stops everyone in it, for good");

    console.log("▸ UNSUBSCRIBING TAKES A PERSON OUT OF EVERY JOURNEY");
    const two = J.create(t, { name: "Orders", trigger: "order.created", reenter: true, steps: [{ channel: "email", subject: "Thanks", body: "Thanks for {store} order" }, { channel: "email", subject: "Review", body: "Review it", wait_minutes: 60 }] });
    J.start(t, two.id);
    db.run("INSERT INTO orders(tenant_id, owner, num, total) VALUES(?,?,?,?)", t, owner(ana), "ORD-J-2", 10);
    db.run("INSERT INTO orders(tenant_id, owner, num, total) VALUES(?,?,?,?)", t, owner(ana), "ORD-J-3", 10);
    ok(J.onEvent(t, "order.created", { num: "ORD-J-2" }).entered === 1 && J.onEvent(t, "order.created", { num: "ORD-J-3" }).entered === 1, "a journey that re-enters takes each order");
    due(); sent.length = 0; await J.sendDue(t);
    const utok = /t=(j[0-9a-f]{36})\s*$/.exec(sent[0].text)[1];
    const u = CA.unsubscribe(utok);
    ok(u.ok && !CO.mayProcess(t, "ana@example.com", "marketing"), "the link in a journey message withdraws marketing", u);
    ok(db.get("SELECT COUNT(*) n FROM journey_enrolments WHERE person='ana@example.com' AND status='active'").n === 0, "and stops every journey she is in");

    console.log("▸ CAMPAIGNS ARE TRACKED TOO");
    CO.grantConsent(t, "cy@example.com", "marketing", { source: "signup" });
    sent.length = 0;
    const c = CA.create(t, { name: "Sale", channel: "email", subject: "Sale", body: "See https://shop.example.com/sale now", audience: { kind: "customers" } });
    await CA.send(t, c.id);
    const ct = /t=([0-9a-f]{36})&n=0/.exec(sent[0].text);
    ok(!!ct && /&amp;o=1/.test(sent[0].html), "a campaign email carries tracked links and the open pixel", sent[0].text);
    CA.track(ct[1], 0, false);
    const cs = CA.status(t, c.id);
    ok(cs.clicked === 1 && cs.opened === 1 && cs.clickRate === 100, "the campaign shows its opens and clicks", { opened: cs.opened, clicked: cs.clicked });
    const sms = CA.create(t, { name: "SMS", channel: "in_app", subject: "s", body: "no links here", audience: { kind: "customers" } });
    ok(CA.compose(t, { ...sms, channel: "in_app" }, { token: "x".repeat(36), name: "Cy" }).html === undefined, "only email gets an HTML part");

    console.log("▸ ERASURE");
    const before2 = db.get("SELECT COUNT(*) n FROM journey_messages WHERE person='cy@example.com'").n + db.get("SELECT COUNT(*) n FROM journey_enrolments WHERE person='cy@example.com'").n;
    const er = CO.eraseSubject(t, "cy@example.com", "dpo");
    const after2 = db.get("SELECT COUNT(*) n FROM journey_messages WHERE person='cy@example.com'").n + db.get("SELECT COUNT(*) n FROM journey_enrolments WHERE person='cy@example.com'").n;
    ok(before2 > 0 && er.ok && after2 === 0, "erasing a person removes their rows in every journey", { before2, after2, er });
  } catch (e) { failed++; console.log("  ✗ threw: " + (e.stack || e.message)); }
  console.log(`\n${passed} passed, ${failed} failed`);
  wipe(); process.exit(failed ? 1 : 0);
})();

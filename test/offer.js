/* The Offers domain (lib/offers.js, lib/goip.js, lib/routes/offer.js): one record for every offer.
   This file grows with the domain; each part of it proves one of the domain's features. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "offer-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const offers = require("../lib/offers.js");
const states = require("../lib/states.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x) : ""))); };
const T = 1;

console.log("offers — the store's promotions become offers, once");
/* an install from before the move: a promotions table with a running promotion and a rule on it */
db.run(`CREATE TABLE promotions (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL, type TEXT NOT NULL, value REAL DEFAULT 0,
  rules TEXT DEFAULT '{}', scope TEXT DEFAULT '{}', starts TEXT, ends TEXT, status TEXT DEFAULT 'active', code TEXT DEFAULT '', deleted_at TEXT)`);
const live = states.first("offer", "live");
db.run("INSERT INTO promotions(tenant_id,name,type,value,rules,scope,status,code) VALUES(1,'Old 15%','percent',15,?,?,?, 'OLD15')", JSON.stringify({ min: 20 }), JSON.stringify({ products: ["P1"] }), live);
db.run("INSERT INTO promotions(tenant_id,name,type,value,status) VALUES(1,'Paused','fixed',5,'paused')");
const pid = db.get("SELECT id FROM promotions WHERE code='OLD15'").id;
db.run("INSERT INTO applicability_rules(tenant_id,subject_type,subject,effect) VALUES(1,'promotion',?,'deny')", String(pid));
offers.seed();
const moved = db.get("SELECT * FROM offers WHERE tenant_id=1 AND code='OLD15'");
ok(moved && moved.type === "percent" && moved.value === 15 && moved.min_amount === 20 && moved.status === live, "a running promotion is a live offer with its type, value, code and minimum", moved);
ok(moved && JSON.parse(moved.scope_value).products[0] === "P1" && moved.scope_type !== "store", "and its scope", moved && [moved.scope_type, moved.scope_value]);
ok(db.get("SELECT status FROM offers WHERE name='Paused'").status !== live, "one not running is off");
const rule = db.get("SELECT * FROM applicability_rules WHERE subject=?", String(moved.id));
ok(rule && rule.subject_type === (require("../lib/rules.js").binding("offers.apply") || {}).subject_type, "the rule on it now rules the offer", rule);
ok(!db.get("SELECT name FROM sqlite_master WHERE name='promotions'"), "and the promotions table is gone");
offers.seed();
ok(db.get("SELECT COUNT(*) n FROM offers WHERE code='OLD15'").n === 1, "seeding again moves nothing twice");

const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message) || re.test(e.code || ""), n, e.message); } };
const GC = require("../lib/giftcards.js"), W = require("../lib/wallet.js"), caps = require("../lib/capabilities.js"), lineterms = require("../lib/lineterms.js");
const A = "shopper:gc-a", B = "shopper:gc-b";

console.log("gift cards — off, nothing is issued");
caps.disable(T, "gift_cards");
throws(() => GC.issue(T, { amount: 10, source: "issued" }), /not offered/, "a store with gift cards off issues none");
caps.enable(T, "gift_cards", { validity_days: 30, min_amount: 5, max_amount: 500, denominations: [10, 25] });

console.log("gift cards — issued, checked, redeemed into the gift balance");
throws(() => GC.issue(T, { amount: 1, source: "issued" }), /between/, "a card is worth what the store allows");
throws(() => GC.issue(T, { amount: 10, source: "found" }), /how the card came to be/, "and came to be in a declared way");
const c1 = GC.issue(T, { amount: 40, source: "issued", buyer: A, recipient: "Ana", recipient_email: "ana@example.com", message: "Happy day", occasion: "birthday" }, "staff");
ok(c1.code.length === 16 && c1.redeemable && c1.last4 === c1.code.slice(-4) && c1.expires_at, "a card has a code, a value and a validity", c1);
const raw = db.all("SELECT v.attrs FROM k_versions v JOIN k_nodes n ON n.uid=v.node WHERE n.kind='offer.gift_card'").map(r => r.attrs).join(" ");
ok(!raw.includes(c1.code) && !raw.includes("ana@example.com") && !raw.includes("Happy day") && !raw.includes(A), "its code, recipient, message and holder are sealed in the store");
ok(!db.all("SELECT value FROM k_identifiers WHERE scheme='offer.gift_card.code'").some(r => r.value.includes(c1.code)), "and it is found by a keyed index, not by its code");
ok(GC.check(T, c1.code.toLowerCase().replace(/(.{4})/g, "$1-")).amount === 40, "anyone checks what a code is worth, however it is typed");
ok(!("recipient" in GC.check(T, c1.code)), "a check says nothing about who holds it");
ok(GC.mine(T, A).some(c => c.code === c1.code), "its holder sees its code");
const r1 = GC.redeem(T, c1.code, B);
const gift = W.walletOf(T, B, null, "gift");
ok(r1.card.state.key !== c1.state.key && W.balances(T, B, gift.id).posted === 40, "redeeming moves its value into the redeemer's gift balance");
throws(() => GC.redeem(T, c1.code, B), /has been/, "a card is redeemed once");
throws(() => GC.redeem(T, "NOPE", B), /No card/, "an unknown code is refused");
ok(GC.mine(T, B).some(c => c.last4 === c1.last4), "the redeemer holds it too");

console.log("gift cards — checkout spends the gift balance first");
W.post(T, { op: "deposit", wallet: W.walletFor(T, B).id, amount: "100", idem: "gc-main" });
ok(W.checkoutAvailable(T, B) === 140, "checkout may spend the gift balance and the wallet together");
const holds = W.holdForOrder(T, B, null, 60, "order:GC-1");
ok(holds.length === 2 && holds[0].wallet_id === gift.id && holds[0].amount === 40 && holds[1].amount === 20, "the gift balance is held first, the rest from the wallet", holds.map(h => [h.wallet_id === gift.id, h.amount]));
W.captureOrder(T, holds, "order:GC-1", B);
ok(W.checkoutAvailable(T, B) === 80, "capturing spends both");
W.giveBackOrder(T, B, "order:GC-1", "payment failed");
ok(W.checkoutAvailable(T, B) === 140 && W.balances(T, B, gift.id).posted === 40, "a failed payment gives each back, as linked reversals");

console.log("gift cards — voided and expired");
const c2 = GC.issue(T, { amount: 10, source: "issued" }, "staff");
throws(() => GC.voidCard(T, c2.id, ""), /Say why/, "a void needs a reason");
GC.voidCard(T, c2.id, "issued in error", "staff");
throws(() => GC.redeem(T, c2.code, B), /has been/, "a voided card is not redeemed");
const c3 = GC.issue(T, { amount: 10, source: "issued" }, "staff");
require("../lib/kernel.js").record(c3.id, { expires_at: new Date(Date.now() - 1000).toISOString() }, {}, "test");
throws(() => GC.redeem(T, c3.code, B), /expired/i, "a card past its validity has expired");

console.log("gift cards — bought at checkout, one card per unit, to its recipient");
const pick = db.get("SELECT id, attrs FROM products WHERE tenant_id=1 AND lifecycle='published' LIMIT 1");
db.run("UPDATE products SET attrs=? WHERE tenant_id=1 AND id=?", JSON.stringify(Object.assign(JSON.parse(pick.attrs || "{}"), { gift_card: true })), pick.id);
const item = db.get("SELECT * FROM products WHERE tenant_id=1 AND id=?", pick.id);
ok(GC.vocabulary(T).items.some(x => x.id === item.id), "the store's gift-card items are offered");
throws(() => lineterms.clean({ tid: T, owner: A, product: item, qty: 1 }, { gift_card: { amount: 9999 } }), /between/, "a chosen value outside the store's range is refused");
const terms = lineterms.clean({ tid: T, owner: A, product: item, qty: 2 }, { gift_card: { amount: 25, recipient: "Bo", occasion: "wedding" } });
ok(lineterms.priceLine({ tid: T, product: item }, terms, 0).unit === 25, "the chosen value is the line's price");
const before = GC.mine(T, A).length;
lineterms.place({ tid: T, owner: A, orderId: 77, orderNum: "GC-ORDER" }, [{ product: item, qty: 2, terms, unit: 25 }]);
const bought = GC.mine(T, A).filter(c => c.order_ref === "GC-ORDER");
ok(GC.mine(T, A).length === before + 2 && bought.every(c => c.amount === 25 && c.recipient === "Bo" && c.occasion === "wedding" && c.source === "bought"), "each unit ordered becomes a card for its recipient", bought);

console.log("gift cards — the first voucher table's cards move onto the kernel, once");
db.run(`CREATE TABLE gift_vouchers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, code TEXT, amount REAL, currency TEXT, buyer TEXT, recipient TEXT, recipient_email TEXT, message TEXT, expires_at TEXT, status TEXT, redeemed_by TEXT)`);
db.run("INSERT INTO gift_vouchers(tenant_id,code,amount,buyer,status) VALUES(1,'OLDCODE12345',15,?, 'issued')", A);
GC.seed();
ok(GC.check(T, "OLDCODE12345").amount === 15 && !db.get("SELECT name FROM sqlite_master WHERE name='gift_vouchers'"), "an old voucher is a card, and the old table is gone");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

/* LUXORA Platform — behaviour is declared on vocabulary rows, never chosen by naming a key.
   An AI capability names its engine, a tax class its rate source, an offer scope how it
   matches, a bid model what it charges on, a risk decision its threshold and effect, a sort
   order its columns… Editing the row changes the engine; the gate below fails if a converted
   engine compares against a key of the vocabularies it now reads behaviour from. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "behaviour-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const reg = require("../lib/registry.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const setList = (name, items) => db.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(items), name);
const getList = name => JSON.parse(db.get("SELECT items FROM meta_lists WHERE name=?", name).items);

try {
  const tid = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;

  console.log("▸ TAX CLASSES DECLARE THEIR RATE");
  const tax = require("../lib/tax.js");
  const q = cls => tax.quote({ tenantId: tid, country: "GB", lines: [{ id: "a", amount: 100, class: cls }] }).lines[0].rate;
  const std = q(undefined);
  ok(std > 0 && q("zero") === 0, "the default class is taxed, a class declaring rate 0 is not", [std, q("zero")]);
  const classes = getList("taxClasses");
  setList("taxClasses", classes.concat([{ key: "luxury", name: "Luxury", rate: 0.35 }]));
  ok(q("luxury") === 0.35, "a new class with its own rate is one registry row", q("luxury"));
  setList("taxClasses", classes);

  console.log("▸ BID MODELS DECLARE WHAT THEY CHARGE ON");
  const mk = require("../lib/marketplace.js");
  const models = getList("mktBidModels");
  setList("mktBidModels", models.concat([{ key: "cpv", name: "cost per view", charges_on: "view", per: 1, basis: "action" }]));
  const ad = mk.createAd(tid, { name: "T", bid_model: "cpv", bid_amount: 0.2, budget: 10 });
  mk.recordEvent(tid, ad.id, "view", "t1");
  ok(Number(db.get("SELECT spent FROM ads WHERE id=?", ad.id).spent) === 0.2, "a new model charging on views bills a view — no code");
  setList("mktBidModels", models);

  console.log("▸ RISK DECISIONS DECLARE THEIR THRESHOLD AND EFFECT");
  const risk = require("../lib/risk.js");
  ok(risk.decisionFor(50, false).key === "hold" && risk.decisionFor(10, false).key === "approve", "the decision is the highest threshold the score reaches");
  const acts = getList("riskActions");
  setList("riskActions", acts.map(a => a.key === "hold" ? { ...a, min_score: 60 } : a));
  ok(risk.decisionFor(50, false).key === "approve", "raising the hold threshold is a data edit");
  setList("riskActions", acts.concat([{ key: "review_2fa", name: "Step-up", min_score: 30, effect: "hold" }]));
  ok(risk.decisionFor(35, false).key === "review_2fa" && risk.effectOf("review_2fa") === "hold", "a new decision band is one row, with the effect it declares");
  setList("riskActions", acts);

  console.log("▸ AI CAPABILITIES NAME THEIR ENGINE");
  const caps = getList("aiCapabilities");
  ok(caps.every(c => c.engine && c.units), "every capability row names its engine and unit rule");

  console.log("▸ OFFER SCOPES, STACKING AND KINDS DECLARE HOW THEY BEHAVE");
  ok(getList("offerScopes").some(r => r.key === "brand" && r.match === "in" && r.item === "brand"), "a scope declares how it matches items");
  ok(getList("stackingPolicies").some(r => r.blocks === "others"), "a stacking policy declares what it blocks");
  ok(getList("couponKinds").some(r => r.new_customers_only), "a coupon kind declares a new-customers-only rule");

  console.log("▸ SORT ORDERS, CHANNELS, OBJECTIVES AND ATTRIBUTION ARE ROWS");
  ok(getList("productSortOrders").some(r => r.default) && getList("deliveryChannels").every(c => c.address && c.pattern), "sort orders and delivery channels are registry rows");
  ok(getList("goipObjectives").every(o => o.impl) && getList("goipAttributionModels").every(m => m.impl), "objectives and attribution models name their implementation");

  console.log("▸ THE GATE: CONVERTED ENGINES NAME NO DECLARED KEY");
  const VOCAB = { ai: ["aiCapabilities"], tax: ["taxClasses"], offers: ["offerScopes", "stackingPolicies", "couponKinds", "offerChannels"],
    marketplace: ["mktBidModels"], mailer: ["deliveryChannels"], risk: ["riskActions"], recurring: ["membershipBenefits"],
    goip: ["goipObjectives", "goipAttributionModels", "goipTouchpointKinds", "goipAssetClasses", "goipPartyTypes"] };
  /* kernel words that merely share a spelling with a vocabulary key: a capability's
     authority scope "platform" is not the party type "platform" */
  const KERNEL = { goip: ["platform"] };
  const named = [];
  for (const [f, lists] of Object.entries(VOCAB)) {
    const keys = new Set(lists.flatMap(l => reg.keys(l)));
    const src = fs.readFileSync(path.join(__dirname, "..", "lib", f + ".js"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
    for (const re of [/(?:===|!==)\s*["']([a-z_]+)["']/g, /["']([a-z_]+)["']\s*(?:===|!==)/g, /\[\s*((?:["'][a-z_]+["']\s*,?\s*)+)\]\.includes\(/g])
      { let m; while ((m = re.exec(src))) for (const lit of (m[1].match(/[a-z_]+/g) || [])) if (keys.has(lit) && !(KERNEL[f] || []).includes(lit)) named.push(f + ": " + lit); }
  }
  ok(named.length === 0, "no converted engine compares against a key of the vocabularies it reads behaviour from", [...new Set(named)]);
} catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

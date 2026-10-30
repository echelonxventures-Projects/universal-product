/* LUXORA Platform — the governed money policy (lib/money-policy.js, PR-049).
   On a throwaway database:
     · the first version is seeded from lib/seed/money.json, as a kernel node versioned in
       k_versions, and lib/money.js rounds by it
     · a policy is data only: an unknown rule or currency, an unknown field, a misspelt code or
       anything that is not a record is refused — nothing in it is evaluated
     · a change moves only through the kernel lifecycle: approving it validates it again, it is
       approved by someone other than its author and only with the approve permission, and
       published only once approved; a discarded change goes nowhere
     · a preview rounds sample amounts under the current and the proposed rules and writes
       nothing: no event, no version, no money row
     · published, the new rules apply at once (or from a later effective time, never an earlier
       one); every money row records the version it was computed under, and an older row's
       version is still found after it was superseded or rolled back
     · two changes drafted against one version cannot both land: the second is refused as stale
     · a rollback restores the version before, and the history keeps both
     · no version at a moment, or a stored version that is not a valid policy, is refused —
       never replaced by a guess
   Then, over HTTP: the screen's API is platform-only, drafting needs the policy section's write
   grant, the author cannot approve their own change, a second operator can, and each step is
   in the audit log. */
"use strict";
const path = require("path"), fs = require("fs");
const { spawn } = require("child_process");
const DB = path.join(__dirname, "money-policy.db"), HTTP_DB = path.join(__dirname, "money-policy-http.db");
for (const f of [DB, HTTP_DB]) for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(f + s, { force: true }); } catch (e) { } }
Object.assign(process.env, { LX_DB: DB, LX_TEST: "1", LX_QUIET: "1" });
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message) || re.test(e.code || ""), n, (e.code || "") + " " + e.message); } };
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const D = require("../lib/db.js");
  const M = require("../lib/money.js"), MP = require("../lib/money-policy.js"), MS = require("../lib/money-store.js");
  const BASE = require("../lib/seed/money.json");
  const APPROVE = [require("../lib/kernel.js").SEED.lifecycle.approvePermission];
  const count = t => D.get(`SELECT COUNT(*) AS n FROM ${t}`).n;
  /* a two-decimal currency the master knows, for amounts whose rounding the rules decide */
  const cur = D.get("SELECT code FROM currencies WHERE decimals=2 ORDER BY code LIMIT 1").code;
  const other = D.get("SELECT code FROM currencies WHERE decimals=2 AND code<>? ORDER BY code LIMIT 1", cur).code;
  const tid = D.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;
  let n = 0;
  const order = () => { const r = MS.insert("orders", { tenant_id: tid, owner: "t" + tid + ":g:mp", num: "MP-" + (++n), status: "placed" }, cur, { sub: "1.00", ship_fee: "0", gift_used: "0", tax: "0", total: "1.00" }); return D.get("SELECT * FROM orders WHERE id=?", Number(r.lastInsertRowid)); };
  const payment = () => { const r = MS.insert("payments", { tenant_id: tid, gateway: "test", status: "initiated" }, cur, { amount: "1.00" }); return D.get("SELECT * FROM payments WHERE id=?", Number(r.lastInsertRowid)); };
  const stepThrough = (c, author, approver) => { MP.validate(c.id, author); MP.approve(c.id, approver, APPROVE); return MP.publish(c.id, approver); };

  console.log("▸ SEEDED — the first version comes from lib/seed/money.json, on the kernel");
  const seeded = MP.active();
  ok(seeded.source === "kernel" && seeded.rounding === BASE.rounding && JSON.stringify(seeded.currencies) === JSON.stringify(BASE.currencies || {}), "the policy in force is the seed's rule, as a kernel version", seeded);
  ok(/^money-policy:\d+$/.test(seeded.ref), "its reference names its k_versions row", seeded.ref);
  ok(!!D.get("SELECT 1 FROM k_versions WHERE id=? AND rec_to IS NULL", seeded.version), "the version is a believed row of k_versions");
  ok(M.modeFor(cur) === BASE.rounding, "lib/money.js rounds by the policy in force");
  const o0 = order(), p0 = payment();
  ok(o0.money_policy === seeded.ref && p0.money_policy === seeded.ref, "an order and a payment record the version they were computed under", [o0.money_policy, p0.money_policy]);

  console.log("▸ VALIDATION — data only, every rule and currency known");
  throws(() => MP.check({ rounding: "bankers" }), /rounding rule is one of/, "an unknown rule is refused");
  throws(() => MP.check({ rounding: "half-up", currencies: { ZZZQ: { rounding: "half-up" } } }), /currency_unknown/, "an unknown currency is refused");
  throws(() => MP.check({ rounding: "half-up", currencies: { [cur.toLowerCase()]: { rounding: "half-up" } } }), /as the master spells it/, "a code not spelt as the master spells it is refused");
  throws(() => MP.check({ rounding: "half-up", currencies: { [cur]: { rounding: "half-up", scale: 4 } } }), /no field scale/, "an undeclared currency field is refused");
  throws(() => MP.check({ rounding: "half-up", formula: "amount * 2" }), /no field formula/, "an undeclared policy field (an expression) is refused, never evaluated");
  throws(() => MP.check({ rounding: "x => 1" }), /rounding rule is one of/, "code in a rule is refused as an unknown rule");
  throws(() => MP.check(["half-up"]), /is a record/, "a list is not a policy");
  throws(() => MP.check({ rounding: "half-up", currencies: [] }), /currencies is a record/, "currencies as a list is refused");
  throws(() => MP.check({ rounding: "half-up", note: "x".repeat(501) }), /at most 500/, "an overlong note is refused");
  throws(() => MP.propose({ policy: { rounding: "half-up" }, validFrom: "2001-01-01T00:00:00Z" }, "alice"), /money_policy_past/, "a change cannot take effect in the past");
  ok(count("k_changes") === 0, "a refused draft records no change");

  console.log("▸ LIFECYCLE — validated, approved by another, published");
  const a = MP.propose({ title: "Half-even for " + cur, policy: { rounding: BASE.rounding, currencies: { [cur]: { rounding: "half-even" } }, note: "test" } }, "alice");
  ok(a.state === "draft" && a.basedOn === seeded.recordedFrom, "a draft records the version it was drafted against", a);
  throws(() => MP.publish(a.id, "bob"), /money_policy_state/, "an unapproved change is not published");
  const v = MP.validate(a.id, "alice");
  ok(v.report.ok && v.change.state === "validated", "validation is a dry run that passes", v.report);

  console.log("▸ PREVIEW — sample amounts under both rules, nothing written");
  const before = { ev: count("k_events"), ver: count("k_versions"), orders: count("orders"), payments: count("payments"), state: MP.changes().find(c => c.id === a.id).state };
  const pv = MP.preview(a.id, { samples: ["0.125", "0.135", "2.5"] }, "alice");
  const at = (amount, code) => pv.rows.find(r => r.amount === amount && r.currency === code);
  ok(at("0.125", cur).current.result === "0.13" && at("0.125", cur).proposed.result === "0.12" && at("0.125", cur).changed, "0.125 rounds 0.13 now and 0.12 under the proposal", at("0.125", cur));
  ok(at("0.135", cur).current.result === "0.14" && !at("0.135", cur).changed, "0.135 is 0.14 under both", at("0.135", cur));
  ok(pv.changed === pv.rows.filter(r => r.changed).length && pv.changed >= 1, "the preview counts what would change", pv.changed);
  ok(pv.proposed.currencies[cur].rounding === "half-even", "the proposed version is what the kernel would record");
  ok(count("k_events") === before.ev && count("k_versions") === before.ver && count("orders") === before.orders && count("payments") === before.payments, "the preview wrote no event, version or money row", [before, count("k_events"), count("k_versions")]);
  ok(MP.changes().find(c => c.id === a.id).state === before.state && MP.active().ref === seeded.ref && M.modeFor(cur) === BASE.rounding, "the change and the policy in force are as they were");

  console.log("▸ APPROVAL — someone other than the author, with the permission");
  throws(() => MP.approve(a.id, "alice", APPROVE), /someone other than its author/, "the author cannot approve their own change");
  throws(() => MP.approve(a.id, "bob", []), /permission/, "approving needs the approve permission");
  const ap = MP.approve(a.id, "bob", APPROVE);
  ok(ap.state === "approved" && ap.approver === "bob", "a second operator approves it", ap);

  console.log("▸ PUBLISH — the rules apply at once, every row records its version");
  const pub = MP.publish(a.id, "bob");
  ok(pub.change.state === "published" && pub.policy.currencies[cur].rounding === "half-even", "published, the policy in force is the new version", pub.policy);
  ok(M.modeFor(cur) === "half-even" && M.modeFor(other) === BASE.rounding, "the currency rule applies to its currency only");
  ok(M.toString(M.rounded("0.125", cur)) === "0.12" && M.toString(M.rounded("0.125", other)) === "0.13", "money rounds by the published rules at once");
  const o1 = order(), p1 = payment();
  ok(o1.money_policy === pub.policy.ref && p1.money_policy === pub.policy.ref && pub.policy.ref !== seeded.ref, "new rows record the new version", [o1.money_policy, p1.money_policy]);
  ok(D.get("SELECT money_policy FROM orders WHERE id=?", o0.id).money_policy === seeded.ref, "an earlier row keeps the version it was computed under");
  ok(MP.lookup(seeded.ref).rounding === BASE.rounding && MP.lookup(seeded.ref).recordedTo != null, "the superseded version is still found by its reference", MP.lookup(seeded.ref));
  throws(() => MP.lookup("money-policy:999999999"), /money_policy_unknown/, "an unknown reference is refused");

  console.log("▸ CONCURRENCY — two changes drafted against one version");
  const b1 = MP.propose({ title: "one", policy: { rounding: "half-even" } }, "alice");
  const b2 = MP.propose({ title: "two", policy: { rounding: "down" } }, "alice");
  ok(b1.basedOn === b2.basedOn, "both drafts name the same base");
  stepThrough(b1, "alice", "bob");
  ok(MP.active().rounding === "half-even", "the first lands");
  throws(() => MP.validate(b2.id, "alice"), /money_policy_stale/, "the second is refused as stale when it moves");
  throws(() => MP.approve(b2.id, "bob", APPROVE), /money_policy_stale/, "and cannot be approved");
  ok(MP.active().rounding === "half-even", "the policy in force is the one that landed");
  const disc = MP.discard(b2.id, "alice");
  ok(disc.state === "discarded", "a stale change is discarded");
  throws(() => MP.approve(b2.id, "bob", APPROVE), /stale|cannot go from discarded/, "a discarded change goes nowhere");

  console.log("▸ ROLLBACK — the version before is restored, the history keeps both");
  const landed = MP.active();
  const rb = MP.rollback(b1.id, "bob");
  ok(rb.change.state === "rolled-back" && rb.policy.rounding === BASE.rounding && rb.policy.currencies[cur].rounding === "half-even", "rolling back restores the version before", rb.policy);
  ok(M.modeFor(other) === BASE.rounding, "money rounds by the restored rules at once");
  ok(MP.lookup(landed.ref).rounding === "half-even" && MP.lookup(landed.ref).recordedTo != null, "the rolled-back version is still found by its reference");
  const h = MP.history();
  ok(h.some(x => x.ref === landed.ref && !x.current) && h.some(x => x.current) && h.every(x => x.recordedAt), "the history lists every version with the moment it was recorded", h.length);
  throws(() => MP.rollback(b1.id, "bob"), /Only a published change/, "a change is rolled back once");

  console.log("▸ EFFECTIVE TIME — a change can take effect later, never earlier");
  const soon = new Date(Date.now() + 2500).toISOString();
  const f = MP.propose({ title: "later", validFrom: soon, policy: { rounding: "ceiling", currencies: {} } }, "alice");
  stepThrough(f, "alice", "bob");
  ok(MP.active().rounding === BASE.rounding, "published for later, the current rules still apply");
  ok(MP.active({ at: new Date(Date.now() + 3600e3).toISOString() }).rounding === "ceiling", "asked about a later moment, the policy answers with the scheduled version");
  await sleep(3000);
  ok(MP.active().rounding === "ceiling" && M.modeFor(cur) === "ceiling", "at its effective time it applies, without another write");
  const late = MP.propose({ title: "too late", validFrom: new Date(Date.now() + 1500).toISOString(), policy: { rounding: "floor" } }, "alice");
  MP.validate(late.id, "alice"); MP.approve(late.id, "bob", APPROVE);
  await sleep(2000);
  throws(() => MP.publish(late.id, "bob"), /money_policy_past/, "an approved change whose effective time has passed is not published");

  console.log("▸ FAIL CLOSED — a missing or invalid policy is refused, not guessed");
  throws(() => MP.active({ at: "2000-01-01T00:00:00Z" }), /money_policy_missing/, "no version at a moment is refused");
  const live = MP.active();
  const keep = D.get("SELECT attrs FROM k_versions WHERE id=?", live.version).attrs;
  D.run("UPDATE k_versions SET attrs=? WHERE id=?", JSON.stringify({ rounding: "bankers" }), live.version);
  throws(() => M.rounded("0.125", cur), /rounding rule is one of/, "a stored version that is not a valid policy stops rounding");
  D.run("UPDATE k_versions SET attrs=? WHERE id=?", keep, live.version);
  ok(M.modeFor(cur) === "ceiling", "restored, rounding resumes");

  console.log("▸ HTTP — platform-only, the section's write grant, a second operator");
  const PORT = 8879, BASE_URL = "http://localhost:" + PORT;
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT: String(PORT), LX_DB: HTTP_DB }, stdio: ["ignore", "ignore", "inherit"] });
  try {
    let up = false;
    for (let i = 0; i < 180; i++) { try { if ((await fetch(BASE_URL + "/healthz")).ok) { up = true; break; } } catch (e) { } await sleep(1000); }
    ok(up, "the server boots");
    const session = () => {
      const jar = new Map();
      return async (p, method = "GET", body) => {
        const headers = { Cookie: [...jar].map(([k, v]) => k + "=" + v).join("; ") };
        if (method !== "GET") headers["x-csrf"] = jar.get("azc") || "";
        if (body) headers["Content-Type"] = "application/json";
        const r = await fetch(BASE_URL + p, { method, headers, body: body ? JSON.stringify(body) : undefined });
        (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
        return { status: r.status, body: await r.json().catch(() => ({})) };
      };
    };
    const anon = session();
    ok((await anon("/api/platform/money/policy")).status === 403, "the policy screen's API is platform-only");
    const owner = session();
    await owner("/api/session?store=luxora");
    ok(!!(await owner("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).body.ok, "the platform owner signs in");
    const ov = await owner("/api/platform/money/policy");
    ok(ov.status === 200 && ov.body.policy.source === "kernel" && ov.body.modes.length === M.MODES.size, "the screen reads the policy in force, its versions and the rules it may name", ov.body.policy);
    for (const [email, role] of [["finance@luxora.shop", "finance"], ["support@luxora.shop", "support"]])
      ok((await owner("/api/platform/admins", "POST", { name: role, email, password: role + "-pass-1234", role })).status === 200, "a " + role + " operator is created");
    const support = session(), finance = session();
    for (const [s, email, pw] of [[support, "support@luxora.shop", "support-pass-1234"], [finance, "finance@luxora.shop", "finance-pass-1234"]]) { await s("/api/session?store=luxora"); await s("/api/platform/login", "POST", { email, password: pw }); }
    const denied = await support("/api/platform/money/policy/changes", "POST", { policy: { rounding: "half-even" } });
    ok(denied.status === 403, "an operator without the policy section's write grant cannot draft", denied.body);
    const bad = await owner("/api/platform/money/policy/changes", "POST", { policy: { rounding: "bankers" } });
    ok(bad.status === 400 && /rounding rule/.test(bad.body.error || ""), "an invalid policy is refused with its reason", bad.body);
    const dr = await owner("/api/platform/money/policy/changes", "POST", { title: "http", policy: { rounding: "half-even", currencies: {} } });
    ok(dr.status === 200 && dr.body.state === "draft", "the owner drafts a change", dr.body);
    const id = dr.body.id;
    ok((await owner(`/api/platform/money/policy/changes/${id}/validate`, "POST", {})).body.report.ok, "it validates");
    const hp = await owner(`/api/platform/money/policy/changes/${id}/preview`, "POST", {});
    ok(hp.status === 200 && Array.isArray(hp.body.rows) && hp.body.rows.length > 0, "it previews", hp.body.error);
    const self = await owner(`/api/platform/money/policy/changes/${id}/approve`, "POST", {});
    ok(self.status === 400 && /other than its author/.test(self.body.error || ""), "the author cannot approve it", self.body);
    const ap2 = await finance(`/api/platform/money/policy/changes/${id}/approve`, "POST", {});
    ok(ap2.status === 200 && ap2.body.state === "approved" && ap2.body.approver === "finance@luxora.shop", "a finance operator approves it", ap2.body);
    const pb = await finance(`/api/platform/money/policy/changes/${id}/publish`, "POST", {});
    ok(pb.status === 200 && pb.body.policy.rounding === "half-even", "and publishes it", pb.body);
    const ver = await owner("/api/platform/money/policy/versions/" + encodeURIComponent(pb.body.policy.ref));
    ok(ver.status === 200 && ver.body.ref === pb.body.policy.ref, "a version is read by its reference", ver.body);
    const rb2 = await owner(`/api/platform/money/policy/changes/${id}/rollback`, "POST", {});
    ok(rb2.status === 200 && rb2.body.policy.rounding === BASE.rounding, "the owner rolls it back", rb2.body);
    const { DatabaseSync } = require("node:sqlite");
    const H = new DatabaseSync(HTTP_DB, { readOnly: true });
    const acts = H.prepare("SELECT action, actor_name FROM audit_log WHERE action LIKE 'money.policy_%' ORDER BY id").all().map(r => r.action + ":" + r.actor_name);
    H.close();
    ok(["money.policy_drafted:platform@luxora.shop", "money.policy_validate:platform@luxora.shop", "money.policy_approve:finance@luxora.shop", "money.policy_publish:finance@luxora.shop", "money.policy_rollback:platform@luxora.shop"].every(x => acts.includes(x)), "every step is in the audit log, by who took it", acts);
  } finally { srv.kill("SIGKILL"); }

  for (const f of [DB, HTTP_DB]) for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(f + s, { force: true }); } catch (e) { } }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });

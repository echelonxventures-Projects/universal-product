/* LUXORA Platform — security & robustness regressions (the 2026-10 gap review).
   Every check here was a live defect: a single request that crashed the process, an
   anonymous route that read or wrote what only staff may, a response replayed to the
   wrong caller, a login that leaked who administers a store. Each runs against a real
   server on its own throwaway database. */
"use strict";
const DB = require("path").join(__dirname, "security.db");
process.env.LX_DB = DB;
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const net = require("net");
const PORT = 8873;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* a client with its own cookie jar (CSRF token echoed on writes, like the consoles do) */
const mk = () => {
  const c = new Map();
  const H = () => [...c].map(x => x[0] + "=" + x[1]).join("; ");
  const fn = async (p, m, b, extra) => {
    const o = { method: m || "GET", headers: Object.assign({ Cookie: H() }, m && m !== "GET" ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}, extra || {}) };
    if (b !== undefined) o.body = typeof b === "string" ? b : JSON.stringify(b);
    const r = await fetch(BASE + p, o);
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    const text = await r.text();
    let body; try { body = JSON.parse(text); } catch (e) { body = { _raw: text }; }
    return { status: r.status, body, headers: r.headers };
  };
  fn.jar = c;
  return fn;
};
const alive = async () => { try { return (await fetch(BASE + "/healthz")).ok; } catch (e) { return false; } };
/* raw HTTP, for requests fetch() refuses to send (a malformed Host header) */
const raw = (text) => new Promise((resolve) => {
  const s = net.connect(PORT, "127.0.0.1", () => s.write(text));
  let out = ""; s.on("data", d => out += d); s.on("end", () => resolve(out)); s.on("error", () => resolve(out));
  setTimeout(() => { s.destroy(); resolve(out); }, 3000);
});

(async () => {
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB, LX_LOG: "" }, stdio: ["ignore", "ignore", "pipe"] });
  let stderr = ""; srv.stderr.on("data", d => { stderr += d; });
  for (let i = 0; i < 120 && !(await alive()); i++) await sleep(500);
  if (!(await alive())) { console.error("server failed to boot\n" + stderr); process.exit(1); }

  try {
    console.log("▸ ONE REQUEST CANNOT CRASH THE PROCESS");
    {
      const G = mk(); await G("/api/session");
      const big = await G("/api/cart", "POST", JSON.stringify({ a: "x".repeat(1100000) }));
      ok(big.status === 413, "a body over 1 MB is refused with 413", big.status);
      ok(await alive(), "…and the server is still up");
      const host = await raw("GET /healthz HTTP/1.1\r\nHost: %\r\nConnection: close\r\n\r\n");
      ok(/^HTTP\/1\.1 400/.test(host), "a malformed Host header is a 400", host.slice(0, 40));
      ok(await alive(), "…and the server is still up");
      const cookie = await raw("GET /api/session HTTP/1.1\r\nHost: localhost\r\nCookie: azs=%E0%A4%A\r\nConnection: close\r\n\r\n");
      ok(/^HTTP\/1\.1 200/.test(cookie) && await alive(), "a malformed %-escape in a cookie is tolerated", cookie.slice(0, 40));
      const trav = await raw("GET /%2e%2e/%2e%2e/etc/passwd HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n");
      ok(/^HTTP\/1\.1 404/.test(trav), "path traversal stays inside public/", trav.slice(0, 40));
      const badPct = await raw("GET /%E0%A4%A HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n");
      ok(/^HTTP\/1\.1 404/.test(badPct) && await alive(), "a malformed %-escape in a path is a 404, not a crash", badPct.slice(0, 40));
      const xs = await G("/healthz", "GET", undefined, { "x-request-id": "a\tb<script>" });
      ok(xs.headers.get("x-request-id") !== "a\tb<script>", "a hostile X-Request-Id is not echoed back");
    }

    console.log("▸ STAFF-ONLY READS AND WRITES REFUSE AN ANONYMOUS CALLER");
    {
      const G = mk(); await G("/api/session");
      for (const p of ["/api/admin/fin/disputes", "/api/admin/fin/payouts", "/api/shipments", "/api/qc/runs", "/api/qc/riders",
        "/api/helpdesk/agents/status", "/api/sitemap/config", "/api/sitemap", "/api/shipping/providers",
        "/api/admin/identity-providers", "/api/admin/identity-settings"]) {
        const r = await G(p);
        ok(r.status === 403, "GET " + p + " → 403 for a guest", r.status);
      }
      for (const [m, p, b] of [["PUT", "/api/sitemap/config", { hostname: "https://evil.example" }], ["POST", "/api/sitemap/generate", {}],
        ["POST", "/api/shipping/providers/config", { provider_id: "fedex", config: { apiKey: "x" } }], ["POST", "/api/shipping/track", { tracking_number: "T1" }],
        ["POST", "/api/helpdesk/1/message", { body: "fake agent note" }], ["POST", "/api/helpdesk/agents/status", { agent_id: "1", status: "online" }],
        ["PUT", "/api/branding", { name: "HACKED" }], ["POST", "/api/shipping/label", {}]]) {
        const r = await G(p, m, b);
        ok(r.status === 403, m + " " + p + " → 403 for a guest", r.status + " " + JSON.stringify(r.body).slice(0, 80));
      }
      const inj = await G("/api/sitemap/config", "PUT", { "(select 1) x": 1 });
      ok(inj.status === 403 && !/syntax/i.test(JSON.stringify(inj.body)), "column-name SQL never reaches the database", inj.body);
    }

    console.log("▸ STAFF STILL GET THEIR DATA (and the sitemap config is validated, not spliced)");
    const A = mk(); await A("/api/session?store=luxora");
    {
      const li = await A("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
      ok(li.status === 200 && li.body.ok, "store admin signs in", li.body);
      ok((await A("/api/admin/fin/payouts")).status === 200, "staff read payouts");
      ok((await A("/api/qc/runs")).status === 200, "staff read dispatch runs");
      const inj = await A("/api/sitemap/config", "PUT", { "hostname=(select 1) --": "x", hostname: "https://shop.example" });
      ok(inj.status === 200 && inj.body.config.hostname === "https://shop.example", "only declared columns are written", inj.body);
      const badHost = await A("/api/sitemap/config", "PUT", { hostname: "javascript:alert(1)" });
      ok(badHost.status === 400, "a non-http hostname is refused", badHost.body);
      const gen = await A("/api/sitemap/generate", "POST", {});
      ok(gen.status === 200 && gen.body.entries > 0, "generation actually builds entries", gen.body);
      const quote = await A("/api/shipping/quote", "POST", {});
      ok(quote.status === 501, "rate quotes say they are not integrated instead of inventing prices", quote.status);
      const err = await A("/api/helpdesk/999999/message", "POST", { body: "x" });
      ok(err.status === 404, "an agent reply to another store's / unknown case is a 404", err.status);
      const ag = await A("/api/helpdesk/agents/status", "POST", { status: "online" });
      ok(ag.status === 200 && ag.body.agent.status === "online", "staff set their own presence", ag.body);
      ok((await A("/api/helpdesk/agents/status", "POST", { status: "<b>" })).status === 400, "an unknown presence status is refused");
    }

    console.log("▸ LOGIN: no account enumeration, and the session id changes with privilege");
    {
      const G = mk(); await G("/api/session?store=luxora");
      const r1 = await G("/api/auth/login", "POST", { email: "nobody@nowhere.example", password: "x" });
      const r2 = await G("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "wrong-password" });
      ok(r1.status === 401 && r2.status === 401 && r1.body.error === r2.body.error, "unknown email and wrong password get the same answer", [r1.body.error, r2.body.error]);
      ok(!/admin@luxora\.shop/.test(r1.body.error), "the store admin's email is never disclosed", r1.body.error);
      const before = G.jar.get("azs");
      await G("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
      const after = G.jar.get("azs");
      ok(before && after && before !== after, "signing in issues a new session id");
      const fixed = await fetch(BASE + "/api/session", { headers: { Cookie: "azs=" + before } }).then(r => r.json());
      ok(!fixed.user, "the pre-login session id is not authenticated (no fixation)", fixed.user);
      ok(!!(await G("/api/session")).body.user, "the new session id is");
      await G("/api/auth/logout", "POST", {});
      ok(G.jar.get("azs") !== after, "signing out rotates the session id again");
    }

    console.log("▸ IDEMPOTENCY KEYS BELONG TO ONE CALLER");
    {
      const X = mk(), Y = mk(); await X("/api/session"); await Y("/api/session");
      const k = { "Idempotency-Key": "shared-key-1" };
      const a = await X("/api/zip", "POST", { zip: "10001" }, k);
      const a2 = await X("/api/zip", "POST", { zip: "10001" }, k);
      ok(a.status === 200 && a2.headers.get("x-idempotent-replay") === "true", "the same caller's retry replays");
      const b = await Y("/api/zip", "POST", { zip: "10001" }, k);
      ok(b.status === 200 && b.headers.get("x-idempotent-replay") !== "true", "another caller with the same key is NOT handed the first caller's response");
      const c = await X("/api/zip", "POST", { zip: "90210" }, k);
      ok(c.status === 422, "reusing a key with a different payload is refused", c.status);
    }

    console.log("▸ CSP + CONSOLE BUNDLES");
    {
      const r = await fetch(BASE + "/console.html");
      const csp = r.headers.get("content-security-policy") || "";
      const scriptSrc = (csp.match(/script-src([^;]*)/) || ["", ""])[1];
      ok(!/unsafe-inline|unsafe-eval/.test(scriptSrc), "script-src allows neither inline script nor eval", scriptSrc);
      const b = await fetch(BASE + "/js/bundle/platform.js");
      const t = await b.text();
      ok(b.status === 200 && /^\(window\.__lxBundle/.test(t) && /this\.ready = true/.test(t), "the platform bundle is served pre-wrapped (no client-side eval)");
      ok(!/new Function/.test(fs.readFileSync(path.join(__dirname, "..", "public", "js", "console.js"), "utf8")), "console.js no longer compiles source with new Function");
      const pub = path.join(__dirname, "..", "public");
      const htmls = fs.readdirSync(pub).filter(f => f.endsWith(".html")).map(f => path.join(pub, f)).concat(fs.readdirSync(path.join(pub, "docs")).filter(f => f.endsWith(".html")).map(f => path.join(pub, "docs", f)));
      const inline = htmls.filter(f => /<script>|\son[a-z]+="/i.test(fs.readFileSync(f, "utf8")));
      ok(inline.length === 0, "no page carries inline script or inline event handlers", inline.map(f => path.basename(f)));
      const js = ["admin.js", "platform.js", "app.js", "console.js"].filter(f => /\sonclick="/.test(fs.readFileSync(path.join(pub, "js", f), "utf8")));
      ok(js.length === 0, "no bundle renders inline onclick handlers", js);
    }

    console.log("▸ MONEY PATHS CHECK WHO IS ASKING");
    {
      const fin = require(path.join(__dirname, "..", "lib", "fintech.js"));
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      D.run("INSERT INTO kyc_profiles(tenant_id,owner,kind,full_name,status,doc_status) VALUES(1,'t1:u:9999','individual','Test','full_kyc','approved')");
      const acct = fin.openBnpl(1, "t1:u:9999", { credit_limit: 1e9 });
      ok(acct.credit_limit <= fin.creditPolicy(1).bnplMaxLimit, "a BNPL applicant cannot assign their own credit limit", acct.credit_limit);
      const loan = fin.applyLoan(1, "t1:u:9999", { principal: 1000, rate: 0, processing_fee: 0 });
      ok(loan.rate === fin.creditPolicy(1).loanRatePct, "a loan applicant cannot set their own interest rate", loan.rate);
      const G = mk(); await G("/api/session");
      const spend = await G("/api/fintech/bnpl/" + acct.id + "/spend", "POST", { amount: 10 });
      ok(spend.status === 404, "a stranger cannot spend someone else's BNPL line", spend.status);
      const emis = fin.spendBnpl(1, acct.id, null, 30);
      const pay = await G("/api/fintech/emi/" + emis[0].id + "/pay", "POST", {});
      ok(pay.status === 404 && D.get("SELECT status FROM bnpl_emis WHERE id=?", emis[0].id).status !== "paid", "a stranger cannot mark someone else's EMI paid", pay.status);
      const run = D.get("SELECT id FROM dispatch_runs WHERE tenant_id=1 ORDER BY id DESC LIMIT 1");
      if (run) {
        let locked = false;
        for (let i = 0; i < 7; i++) { const r = await G("/api/qc/runs/" + run.id + "/pod", "POST", { otp: String(100000 + i) }); if (/Too many/.test(r.body.error || "")) locked = true; }
        ok(locked, "delivery OTP guesses lock out after 5 failures");
      }
    }

    console.log("▸ PLATFORM WRITES ARE AUTHORIZED BY SECTION");
    {
      const z = require(path.join(__dirname, "..", "lib", "authz.js"));
      const bad = [...new Set(Object.values(z.ROUTE_SECTION))].filter(x => !z.SURFACES.platform.includes(x));
      ok(bad.length === 0, "every platform route maps to a section that exists (an unknown section denies even the owner)", bad);
    }

    console.log("▸ ERRORS DO NOT LEAK INTERNALS");
    {
      const r = await A("/api/fintech/bnpl/abc/spend", "POST", { amount: "x" });
      ok(!/SQLITE|no such|at \w+ \(/.test(JSON.stringify(r.body)), "a handler failure never returns SQL or stack text", r.body);
    }

    console.log("▸ schema.sql IS CURRENT");
    {
      const { tables } = require(path.join(__dirname, "..", "scripts", "schema-dump.js"));
      const snap = tables(fs.readFileSync(path.join(__dirname, "..", "schema.sql"), "utf8"));
      const { DatabaseSync } = require("node:sqlite");
      const d = new DatabaseSync(DB, { readOnly: true });
      const live = d.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").all().map(r => r.name).sort();
      d.close();
      const missing = live.filter(t => !snap.includes(t));
      ok(missing.length === 0, "every table a boot creates is in schema.sql (npm run schema regenerates it)", missing);
    }

    /* ─────────── route-audit criticals (2026-10) ─────────── */
    console.log("▸ C1 · LOGIN HINTS NEVER DISCLOSE A CHOSEN PASSWORD");
    {
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      ok(!D.get("SELECT 1 ok FROM platform_settings WHERE key='demo_passwords'"), "no plaintext password list is stored at boot");
      const src = fs.readFileSync(path.join(__dirname, "..", "lib", "api.js"), "utf8");
      ok(/function hintsAllowed\(\)[^}]*NODE_ENV !== "production"/.test(src), "hints are refused when NODE_ENV=production");
      const G = mk(); await G("/api/session");
      const ph = (await G("/api/platform/hint")).body;
      ok(!ph.password || ph.password === "platform123", "the platform hint only ever shows the published default", ph.password);
      /* once the owner picks a real password, the hint has nothing to show — not even the email */
      const P = mk(); await P("/api/session");
      await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
      const sec = require(path.join(__dirname, "..", "lib", "security.js"));
      const row = D.get("SELECT id,email FROM platform_admins WHERE email='platform@luxora.shop'");
      const salt = sec.newSalt(), ver = sec.currentKdf();
      D.run("UPDATE platform_admins SET salt=?, hash=?, kdf_version=? WHERE id=?", salt, D.hashPasswordFor("Chosen-Strong-Pass-91", salt, ver, "pa:" + row.email), ver, row.id);
      const ph2 = (await G("/api/platform/hint")).body;
      ok(ph2.demo === false && !ph2.password && !ph2.email, "with a chosen password the hint reveals nothing", ph2);
      D.run("UPDATE platform_admins SET salt=?, hash=?, kdf_version=? WHERE id=?", salt, D.hashPasswordFor("platform123", salt, ver, "pa:" + row.email), ver, row.id);
    }

    console.log("▸ C2 · A MAGIC LINK GOES TO THE ACCOUNT HOLDER, NOT THE REQUESTER");
    {
      const ml = await A("/api/admin/identity-providers", "PUT", { provider_type: "magic_link", name: "Email Link", enabled: true, config: { ttl: 15 } });
      ok(ml.status === 200, "store admin enables magic-link sign-in", ml.body);
      const G = mk(); await G("/api/session?store=luxora");
      const r = await G("/api/auth/login-init", "POST", { email: "admin@luxora.shop", method: "magic_link" });
      ok(r.body.ok && r.body.action === "magic_link_sent" && !("token" in r.body) && !("link" in r.body), "login-init does not return the token", r.body);
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      const note = D.get("SELECT n.title FROM notifications n JOIN users u ON n.owner = 't' || u.tenant_id || ':u:' || u.id WHERE u.email='admin@luxora.shop' AND n.kind='identity' ORDER BY n.id DESC LIMIT 1");
      ok(note && /sign-in link/i.test(note.title), "the link is delivered to the account holder's inbox", note);
    }

    console.log("▸ C3 · A RESTRICTED PLATFORM ROLE CANNOT REWRITE A STORE'S SIGN-IN");
    {
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      if (!D.get("SELECT id FROM platform_admins WHERE email='auditor@sec.test'")) {
        const id = D.newPlatformAdmin("Audit Only", "auditor@sec.test", "Auditor-Pass-1234");
        D.run("UPDATE platform_admins SET role='auditor' WHERE id=?", id);
      }
      const AU = mk(); await AU("/api/session?store=luxora");
      const li = await AU("/api/platform/login", "POST", { email: "auditor@sec.test", password: "Auditor-Pass-1234" });
      ok(li.status === 200, "auditor signs in", li.body);
      const w = await AU("/api/admin/identity-providers", "PUT", { provider_type: "oidc", name: "evil", enabled: true, config: { issuer: "https://evil", clientId: "a", clientSecret: "k" } });
      ok(w.status === 403, "an auditor cannot install an identity provider on a store", w.status);
      const g = await AU("/api/admin/identity-providers");
      ok(g.status === 403, "an auditor cannot read a store's identity-provider secrets", g.status);
      const st = await AU("/api/admin/identity-settings", "PUT", { mfa: { enabled: false } });
      ok(st.status === 403, "an auditor cannot weaken a store's sign-in policy", st.status);
      const P = mk(); await P("/api/session?store=luxora");
      await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
      ok((await P("/api/admin/identity-providers")).status === 200, "the platform owner still can");
    }

    console.log("▸ C4–C6 · NEGATIVE AMOUNTS NEVER MINT MONEY");
    {
      const fin = require(path.join(__dirname, "..", "lib", "fintech.js"));
      const offers = require(path.join(__dirname, "..", "lib", "offers.js"));
      const mods = require(path.join(__dirname, "..", "lib", "modules.js"));
      const who = "t1:u:7777";
      const bal = () => mods.walletBalance(1, who);
      const throwsLike = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message); } };
      ok(throwsLike(() => offers.debit(1, who, -50, "redeem", "x"), /positive/), "a negative debit is refused (it used to credit)");
      ok(throwsLike(() => fin.quoteInsurance(1, who, { plan_name: "x", premium: -500 }), /Premium/), "a negative insurance premium is refused");
      ok(throwsLike(() => fin.payBill(1, who, { amount: 1, convenience_fee: -500 }), /fee/i), "a negative bill convenience fee is refused");
      ok(throwsLike(() => fin.payBill(1, who, { amount: 25 }), /Insufficient/), "a bill cannot be paid from an empty wallet");
      ok(bal() === 0, "and no balance appeared", bal());
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      D.run("INSERT INTO kyc_profiles(tenant_id,owner,kind,full_name,status,doc_status) VALUES(1,?,'individual','T','full_kyc','approved')", who);
      const acct = fin.openBnpl(1, who, { credit_limit: 100 });
      ok(throwsLike(() => fin.spendBnpl(1, acct.id, null, -300), /positive/), "a negative BNPL spend is refused");
      ok(bal() === 0, "the wallet is still empty", bal());
      /* a guest end-to-end: quote with a negative premium over HTTP */
      const G = mk(); await G("/api/session");
      const q = await G("/api/fintech/insurance", "POST", { plan_name: "x", premium: -1000, cover: 1 });
      ok(q.status === 400 && !q.body.policy, "the insurance API refuses a negative premium", q.body);
    }

    console.log("▸ C7 · REPORT ALIASES CANNOT INJECT SQL");
    {
      const bad = await A("/api/reports/inj", "PUT", { name: "inj", entity: "order", metrics: [{ metric: "count", alias: "x FROM users --" }], dimensions: ["status"] });
      ok(bad.status === 400, "saving a report with a non-identifier alias is refused", bad.body);
      /* a row stored before the fix (or written directly) is neutralised at run time */
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      D.run("INSERT INTO reports(tenant_id,key,name,kind,entity,metrics,dimensions,filter,schedule,format,active,position) VALUES(1,'inj-legacy','x','Operational','order',?,'[\"status\"]','{}','manual','table',1,0)",
        JSON.stringify([{ metric: "count", alias: "n, (SELECT hash FROM users LIMIT 1) AS leak --" }]));
      const run = await A("/api/reports/inj-legacy/run");
      ok(run.status === 200 && !run.body.columns.some(c => /leak|SELECT/i.test(c)) && !JSON.stringify(run.body.rows).includes("$"), "a stored malicious alias is dropped, not executed", run.body.columns);
      const good = await A("/api/reports/ok-rep", "PUT", { name: "ok", entity: "order", metrics: [{ metric: "count", alias: "orders_n" }], dimensions: ["status"] });
      ok(good.status === 200, "a plain alias still saves");
    }
    /* ─────────── route audit · group 1: platform role checks ─────────── */
    console.log("▸ H1 · RESTRICTED PLATFORM ROLES STAY IN THEIR SECTIONS");
    {
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      const mkAdmin = (email, role) => { if (!D.get("SELECT id FROM platform_admins WHERE email=?", email)) { const id = D.newPlatformAdmin(role, email, "Role-Pass-12345"); D.run("UPDATE platform_admins SET role=? WHERE id=?", role, id); } };
      mkAdmin("support@sec.test", "support"); mkAdmin("auditor@sec.test", "auditor");
      const as = async (email) => { const c = mk(); await c("/api/session?store=luxora"); await c("/api/platform/login", "POST", { email, password: email === "auditor@sec.test" ? "Auditor-Pass-1234" : "Role-Pass-12345" }); return c; };
      const SU = await as("support@sec.test"), AU = await as("auditor@sec.test");
      const P = mk(); await P("/api/session?store=luxora"); await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
      ok((await SU("/api/platform/config", "PUT", { csrfEnabled: false })).status === 403, "support cannot rewrite the global security policy");
      ok((await SU("/api/platform/runtime")).status === 403, "support cannot read infrastructure secrets");
      ok((await SU("/api/platform/environments-import", "POST", { bundle: { environments: {} } })).status === 403, "support cannot import runtime environments");
      ok((await SU("/api/platform/global/tenant/plan", "POST", { tenant_id: 1, plan_id: 1 })).status === 403, "support cannot reassign a store's plan");
      ok((await SU("/api/platform/queue/drain", "POST", {})).status === 403, "support cannot drain the job queue");
      ok((await SU("/api/platform/entity-types", "POST", { entity: "product", type_key: "x", label: "x" })).status === 403, "support cannot edit the global schema");
      ok((await AU("/api/offers", "POST", { name: "global giveaway", scope: "global" })).status === 403, "an auditor cannot create offers");
      ok((await AU("/api/fintech/vouchers", "POST", { amount: 1000 })).status === 403, "an auditor cannot mint vouchers");
      ok((await AU("/api/platform/data/tenant")).status === 200 || (await AU("/api/platform/data/tenant")).status === 404, "an auditor can still read (gdata:read)");
      const fo = await AU("/api/platform/fanout?path=/api/admin/webhooks");
      ok(fo.status === 200, "an auditor may fan out reads (gops:read)", fo.status);
      /* the owner keeps everything, and secrets come back masked */
      ok((await P("/api/platform/config", "PUT", { minPasswordLength: 8 })).status === 200, "the owner can still change policy");
      const kdf = await P("/api/platform/config", "PUT", { kdfV2: { logN: 99, r: 1, p: 50 } });
      ok(kdf.status === 200 && kdf.body.policy.kdfV2.logN <= 20 && kdf.body.policy.kdfV2.p <= 4, "KDF cost is clamped to a safe range", kdf.body.policy && kdf.body.policy.kdfV2);
      await P("/api/platform/runtime", "PUT", { queue: { driver: "inline", params: {} }, cache: { driver: "redis", params: { url: "redis://:hunter2secret@cache.internal:6379" } } });
      const rt = await P("/api/platform/runtime");
      ok(rt.status === 200 && !JSON.stringify(rt.body).includes("hunter2secret"), "runtime connection secrets are masked", JSON.stringify(rt.body.runtime && rt.body.runtime.cache));
      await P("/api/platform/runtime", "PUT", { cache: rt.body.runtime.cache });
      const raw = JSON.parse(D.get("SELECT value FROM platform_settings WHERE key='runtime'").value);
      ok(raw.cache.params.url.includes("hunter2secret"), "saving the masked view back keeps the real secret");
      await P("/api/platform/runtime", "PUT", { cache: { driver: "memory", params: {} } });
      const wh = await A("/api/admin/webhooks", "POST", { url: "https://hooks.example.com/x", secret: "whsec_supersecretvalue", events: ["*"] });
      const wl = await A("/api/admin/webhooks");
      ok(!JSON.stringify(wl.body).includes("whsec_supersecretvalue"), "webhook signing secrets are masked in listings", wh.status);
    }
    /* ─────────── route audit · group 2: store role checks ─────────── */
    console.log("▸ H2 · STORE STAFF ROLES ARE ENFORCED");
    {
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      if (!D.get("SELECT id FROM users WHERE email='support-staff@luxora.shop'")) {
        const id = D.newUser(1, "Support Staff", "support-staff@luxora.shop", "Staff-Pass-12345", "admin");
        D.run("UPDATE users SET staff_role='support' WHERE id=?", id);
      }
      const ST = mk(); await ST("/api/session?store=luxora");
      ok((await ST("/api/auth/login", "POST", { email: "support-staff@luxora.shop", password: "Staff-Pass-12345" })).status === 200, "a support-role staff member signs in");
      ok((await ST("/api/admin/payments/1/refund", "POST", { amount: 1 })).status === 403, "support staff cannot issue refunds");
      ok((await ST("/api/admin/webhooks", "POST", { url: "https://x.example/h" })).status === 403, "support staff cannot add webhooks");
      ok((await ST("/api/admin/scim/token", "POST", { label: "x" })).status === 403, "support staff cannot mint SCIM tokens");
      ok((await ST("/api/admin/settings/reset", "POST", {})).status === 403, "support staff cannot reset settings");
      const me = D.get("SELECT id FROM users WHERE email='support-staff@luxora.shop'");
      ok((await ST("/api/admin/staff/" + me.id, "PUT", { staff_role: "owner" })).status === 403, "staff cannot promote themselves");
      /* the owner disables the account — the open session loses access immediately */
      ok((await A("/api/admin/staff/" + me.id, "PUT", { disabled: true })).status === 200, "the owner disables the staff member");
      const after = await ST("/api/admin/orders");
      ok(after.status === 403 || after.status === 401, "a disabled staff member's existing session is cut off", after.status);
      await A("/api/admin/staff/" + me.id, "PUT", { disabled: false });
      ok((await A("/api/admin/ai-gateways", "PUT", { "payment:stripe": { apiKey: "x" } })).status === 400, "the AI-gateway route refuses non-AI providers");
    }

    /* ─────────── route audit · group 3: tenant + owner isolation ─────────── */
    console.log("▸ H3 · ONE STORE NEVER READS OR CHANGES ANOTHER'S RECORDS");
    {
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      const emp = D.run("INSERT INTO employees(tenant_id,code,name,bank_account,tax_id,base_salary) VALUES(999,'X1','Other Store Person','GB00SECRET','TAX-SECRET',99999)").lastInsertRowid;
      const e = await A("/api/admin/ops/employees", "POST", { id: Number(emp), name: "probe", code: "P" });
      ok(!JSON.stringify(e.body).includes("SECRET"), "an upsert with another store's employee id leaks nothing", e.body);
      const rk = D.run("INSERT INTO risk_events(tenant_id,owner,action) VALUES(999,'t999:u:1','hold')").lastInsertRowid;
      const rr = await A("/api/admin/risk/" + rk + "/resolve", "PUT", { decision: "approve" });
      ok(rr.status !== 200 && !JSON.stringify(rr.body).includes("t999:u:1"), "another store's risk event is not returned", rr.body);
      ok(D.get("SELECT resolved FROM risk_events WHERE id=?", rk).resolved !== 1, "…nor resolved");
      const qr = D.run("INSERT INTO qr_codes(tenant_id,payload) VALUES(999,'{\"vpa\":\"other@bank\"}')").lastInsertRowid;
      const q = await A("/api/fintech/qr/" + qr + "/scan", "POST", {});
      ok(!JSON.stringify(q.body).includes("other@bank"), "another store's QR code is not returned", q.body);
      const G = mk(); await G("/api/session?store=luxora");
      ok((await G("/api/consent?subject=t1:u:1")).status === 403, "a guest cannot read someone else's consent");
      ok((await G("/api/consent", "POST", { subject: "t1:u:1", purpose: "marketing", status: "withdrawn" })).status === 403, "…or change it");
      const sch = D.run("INSERT INTO recurring_schedules(tenant_id,owner,product_id,next_ship_at) VALUES(1,'t1:u:424242','LX-1',datetime('now','+5 days'))").lastInsertRowid;
      const sc = await G("/api/subscriptions/" + sch, "PUT", { action: "cancel" });
      ok(sc.status !== 200 && D.get("SELECT status FROM recurring_schedules WHERE id=?", sch).status === "active", "a customer cannot cancel someone else's subscription", sc.status);
      const cl = await G("/api/marketplace/claims", "POST", { order_id: 1, amount: 99999, reason: "x" });
      ok(cl.status === 404 || cl.status === 400, "a claim on an order that isn't yours is refused", cl.status);
      const tmpl = D.get("SELECT id FROM dashboards WHERE tenant_id IS NULL LIMIT 1");
      if (tmpl) {
        const del = await A("/api/dashboards/" + tmpl.id, "DELETE", {});
        ok(del.status === 403 && D.get("SELECT id FROM dashboards WHERE id=?", tmpl.id), "a store admin cannot delete a platform template dashboard", del.status);
      }
      const ucat = await A("/api/ucos/catalog?tenant_id=999");
      ok(ucat.status !== 200 || !ucat.body.published || ucat.body.published.every(p => p.tenant_id == null || p.tenant_id === 1), "a store admin's tenant_id= is ignored");
    }
    /* ─────────── route audit · group 4: money + business logic ─────────── */
    console.log("▸ H4 · NOTHING PAID IS FREE, NOTHING CREDITED TWICE");
    {
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      const fin = require(path.join(__dirname, "..", "lib", "fin.js"));
      const rec = require(path.join(__dirname, "..", "lib", "recurring.js"));
      const throwsLike = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message); } };
      ok(throwsLike(() => rec.subscribeMembership(1, "t1:u:8888", "prime"), /Insufficient/), "a paid membership needs wallet funds");
      /* a payout disburses once */
      const pid = D.run("INSERT INTO payouts(tenant_id,ref,seller_id,kind,period,gross,fee,net,currency,status) VALUES(1,'PO-SEC',1,'seller','2026-10',10,0,10,'USD','open')").lastInsertRowid;
      fin.disbursePayout(1, Number(pid));
      ok(throwsLike(() => fin.disbursePayout(1, Number(pid)), /already/), "a payout cannot be disbursed twice");
      /* store-side module purchase bills an open invoice, never a fabricated paid one */
      const paid = D.get("SELECT COUNT(*) c FROM payments WHERE txn_ref LIKE 'mod_sim_%'").c;
      ok(paid === 0, "no fabricated module payments exist");
      /* settlement generation is idempotent per period */
      const g1 = await A("/api/admin/settlements/generate", "POST", { period: "2026-10" });
      const g2 = await A("/api/admin/settlements/generate", "POST", { period: "2026-10" });
      ok(g1.status === 200 && g2.status === 200 && g2.body.generated === 0, "a period settles once per seller", [g1.body, g2.body]);
      ok((await A("/api/admin/settlements/generate", "POST", { period: "nope" })).status === 400, "a malformed period is refused");
      /* quick-commerce pinning only reserves the caller's own cart, in positive quantities */
      const G = mk(); await G("/api/session?store=luxora");
      const pin = await G("/api/qc/pin", "POST", { items: [{ product_id: "LX-1", qty: -1000 }], zip: "98109" });
      ok(pin.body.ok === false && /invalid_quantity|not_in_cart/.test(pin.body.reason || ""), "a negative or off-cart pin is refused", pin.body);
      /* ad events: a shopper reports clicks only, once per ad per day */
      const ad = D.get("SELECT id FROM ads WHERE tenant_id=1 ORDER BY id LIMIT 1");
      const CU = mk(); await CU("/api/session?store=luxora");
      await CU("/api/auth/register", "POST", { name: "Ad Clicker", email: "clicker@sec.test", password: "Clicker-Pass-12345" });
      if (ad) {
        ok((await CU("/api/marketplace/ads/" + ad.id + "/event", "POST", { kind: "conversion" })).status === 400, "a shopper cannot declare a billable conversion");
        const before = D.get("SELECT spent FROM ads WHERE id=?", ad.id).spent;
        await CU("/api/marketplace/ads/" + ad.id + "/event", "POST", { kind: "click" });
        const mid = D.get("SELECT spent FROM ads WHERE id=?", ad.id).spent;
        for (let i = 0; i < 3; i++) await CU("/api/marketplace/ads/" + ad.id + "/event", "POST", { kind: "click" });
        ok(D.get("SELECT spent FROM ads WHERE id=?", ad.id).spent === mid, "repeated clicks are not billed again", { before, mid });
      }
    }
    /* ─────────── route audit · group 5: exposure + hardening ─────────── */
    console.log("▸ H5 · NO STRANGER'S DATA, NO INTERNAL REQUESTS");
    {
      const G = mk(); await G("/api/session?store=luxora");
      const led = await G("/api/admin/fin/ledger?owner=t1:u:1");
      ok(led.body.owner !== "t1:u:1", "a guest's ?owner= is ignored — they get only their own ledger", led.body.owner);
      const qs = await G("/api/qc/stores");
      ok(qs.status === 200 && qs.body.riders === undefined, "the public store listing carries no rider PII");
      ok((await G("/api/marketplace/ads")).status === 403, "the ad book is staff-only");
      ok((await G("/api/ucos/x/annotations?kind=a&key=b")).status === 403, "operator annotations are staff-only");
      const li = await G("/api/auth/login-init", "POST", { email: "admin@luxora.shop", method: "password" });
      const li2 = await G("/api/auth/login-init", "POST", { email: "nobody-at-all@luxora.shop", method: "password" });
      ok(JSON.stringify(li.body) === JSON.stringify(li2.body) && !li.body.user, "password login-init answers the same for known and unknown accounts", [li.body, li2.body]);
      const pl = await G("/api/platform/login", "POST", { email: "admin@luxora.shop", password: "x" });
      const pl2 = await G("/api/platform/login", "POST", { email: "nobody@nowhere.test", password: "x" });
      ok(pl.body.error === pl2.body.error, "platform login does not reveal store accounts", [pl.body.error, pl2.body.error]);
      const pg = (await G("/api/products?limit=-1")).body;
      ok(pg.per >= 1 && pg.per <= 200 && pg.items.length <= 200, "a negative limit does not remove the page cap", pg.per);
      for (const u of ["http://169.254.169.254/latest/meta-data", "https://127.0.0.1/x", "https://localhost/x", "https://10.0.0.5/hook", "https://[::1]/x", "ftp://example.com/x"]) {
        const r = await A("/api/admin/webhooks", "POST", { url: u, events: ["*"] });
        ok(r.status === 400, "webhook URL refused: " + u, r.status);
      }
      const ev = require(path.join(__dirname, "..", "lib", "events.js"));
      ok(ev.privateAddress("192.168.1.1") && ev.privateAddress("::ffff:10.0.0.1") && !ev.privateAddress("8.8.8.8"), "the private-address check covers v4, mapped v6 and public");
      const acct = await A("/api/admin/account", "PUT", { password: "Brand-New-Pass-123" });
      ok(acct.status === 403, "changing the admin password needs the current password", acct.status);
      const imp = await (async () => { const P = mk(); await P("/api/session"); await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" }); return P("/api/platform/tenants/987654/impersonate", "POST", {}); })();
      ok(imp.status === 404, "impersonating an unknown store is a 404 (no orphan admin)", imp.status);
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      ok(!D.get("SELECT id FROM users WHERE email='impersonate+987654@luxora.shop'"), "…and no orphan user was created");
      const draft = D.get("SELECT id FROM products WHERE tenant_id=1 AND lifecycle != 'published' LIMIT 1");
      if (draft) ok((await G("/api/cart", "POST", { id: draft.id })).status === 404, "an unpublished product cannot be added to the cart");
    }
    console.log("▸ R1 · OUTPUT AND SPEND ONLY MOVE THROUGH THEIR TRANSITIONS");
    {
      const ops = require(path.join(__dirname, "..", "lib", "operations.js"));
      const throwsLike = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message); } };
      const wo = ops.upsertWorkOrder(1, { product_id: "LX-1", qty: 10, status: "done", completed_qty: 10 });
      ok(wo.status === "planned" && wo.completed_qty === 0, "a new work order cannot start done with output claimed", wo);
      ok(throwsLike(() => ops.upsertWorkOrder(1, { id: wo.id, status: "done" }), /complete/), "an edit cannot mark a work order done");
      const ed = ops.upsertWorkOrder(1, { id: wo.id, completed_qty: 999, status: "in_progress" });
      ok(ed.completed_qty === 0 && ed.status === "in_progress", "completed_qty is never written by an edit", ed);
      const pj = ops.upsertProject(1, { name: "Spend probe", budget: 100, spent: 99999 });
      ok(pj.spent === 0, "a new project cannot be created with spend", pj.spent);
      const pj2 = ops.upsertProject(1, { id: pj.id, name: "Spend probe", spent: 5 });
      ok(pj2.spent === 0, "project spend is not editable", pj2.spent);
    }
    console.log("▸ R2 · ADDING A SIGN-IN METHOD NEEDS A RECENT SIGN-IN");
    {
      const D = require(path.join(__dirname, "..", "lib", "db.js"));
      const U = mk(); await U("/api/session?store=luxora");
      await U("/api/auth/register", "POST", { name: "Totp Probe", email: "totp-probe@sec.test", password: "Totp-Probe-Pass-123" });
      const fresh = await U("/api/user/identity-methods", "POST", { method_type: "totp", identifier: "totp-probe@sec.test" });
      ok(fresh.status === 200, "right after sign-in an authenticator can be enrolled", fresh.body);
      /* age the session's proof of identity, as a stolen cookie would be */
      D.run("UPDATE sessions SET auth_at=datetime('now','-2 hours') WHERE sid=?", U.jar.get("azs"));
      const stale = await U("/api/user/identity-methods", "POST", { method_type: "totp", identifier: "totp-probe@sec.test" });
      ok(stale.status === 401, "a stale session cannot add a sign-in method", stale.status);
      const withPw = await U("/api/user/identity-methods", "POST", { method_type: "totp", identifier: "totp-probe@sec.test", current_password: "Totp-Probe-Pass-123" });
      ok(withPw.status === 200, "…unless it confirms the current password", withPw.body);
      ok((await U("/api/user/identity-methods", "POST", { method_type: "webauthn", identifier: "x", current_password: "Totp-Probe-Pass-123" })).status === 400, "passkeys never link as bare rows");
    }
  } catch (e) {
    failed++; console.log("  ✗ suite crashed: " + (e && e.stack || e));
  } finally {
    srv.kill();
    await sleep(300);
    for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  }
  console.log(failed ? `\n✗ ${failed} failed, ${passed} passed` : `\n✓ ALL GREEN — ${passed} passed, 0 failed`);
  process.exit(failed ? 1 : 0);
})();

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

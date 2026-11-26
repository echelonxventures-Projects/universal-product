/* The API for any language (P19): its OpenAPI description is generated from the code and matches it;
   a store's systems call it with a store key, which acts as one staff role in its own store only. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os"), { spawn } = require("child_process");
const DB = path.join(os.tmpdir(), "openapi-" + process.pid + ".db"), PORT = 8957, BASE = "http://localhost:" + PORT;
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(DB + s, { force: true }); } catch (e) { } };
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 300) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  console.log("▸ THE DESCRIPTION");
  const O = require("../scripts/openapi.js"), doc = O.build();
  ok(fs.readFileSync(O.OUT, "utf8") === O.text(), "docs/api/openapi.json is what the code generates (node scripts/openapi.js --write)");
  const rf = require("../lib/ucos-registry.js").readRegistryFiles(), reg = require("../lib/canonical.js").apiRegister(rf);
  const live = new Set(reg.routes.map(r => r[0].toLowerCase() + " " + r[1].replace(/:([A-Za-z0-9_]+)/g, "{$1}")));
  const described = new Set(Object.entries(doc.paths).flatMap(([p, ops]) => Object.keys(ops).map(m => m + " " + p)));
  ok(live.size === described.size && [...live].every(k => described.has(k)), "it describes every route the platform serves, once", { live: live.size, described: described.size });
  const ops = Object.values(doc.paths).flatMap(Object.values);
  ok(new Set(ops.map(o => o.operationId)).size === ops.length, "each operation has its own name, for generated client code");
  ok(ops.every(o => o.tags.length === 1 && o.security && o.responses), "each names its owner, who may call it and what it answers");
  ok(doc.paths["/api/admin/roles"].get.security.some(x => "storeKey" in x) && doc.paths["/api/platform/records"].get.security.every(x => !("storeKey" in x)), "a store key reaches store routes, not the platform's");

  console.log("▸ A STORE'S SYSTEMS CALL IT WITH A KEY");
  wipe(); process.env.LX_DB = DB; process.env.LUXORA_DEMO_BRANDS = "1";
  const log = console.log; console.log = () => { }; const db = require("../lib/db.js"); console.log = log;
  const mcp = require("../lib/mcp.js");
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB, LX_LOG: "", LX_OFFLINE: "1" }, stdio: ["ignore", "ignore", "pipe"] });
  let err = ""; srv.stderr.on("data", d => err += d);
  try {
    for (let i = 0; i < 360; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(500); }
    const call = (p, key, m, b) => fetch(BASE + p, { method: m || "GET", headers: { "content-type": "application/json", ...(key ? { authorization: "Bearer " + key } : {}) }, body: b ? JSON.stringify(b) : undefined }).then(async r => ({ status: r.status, body: await r.json().catch(() => null) }));
    const served = await call("/api/openapi.json");
    ok(served.status === 200 && served.body.openapi === "3.1.0" && Object.keys(served.body.paths).length === Object.keys(doc.paths).length, "the backend serves the description");
    const t1 = db.get("SELECT id FROM tenants WHERE slug='luxora'").id, t2 = db.get("SELECT id FROM tenants WHERE slug<>'luxora' ORDER BY id LIMIT 1").id;
    const owner = mcp.issueKey(t1, "ERP", "owner", "test").key, support = mcp.issueKey(t1, "Helpdesk", "support", "test").key, other = mcp.issueKey(t2, "Other store", "owner", "test").key;
    ok((await call("/api/admin/roles")).status === 403 && (await call("/api/admin/roles", "lxm_" + "0".repeat(48))).status === 401, "without a key, or with a wrong one, nothing");
    const r1 = await call("/api/admin/roles", owner);
    ok(r1.status === 200 && Array.isArray(r1.body.roles), "an owner's key reads the store's admin data", r1.status);
    const w = await call("/api/admin/roles", owner, "POST", { key: "api_made", name: "Made over the API", sections: { orders: "read" } });
    ok(w.status === 200 && w.body.role && w.body.role.key === "api_made", "and writes without a cookie or CSRF token", w);
    const a = db.get("SELECT actor_type, actor_id, actor_name FROM audit_log WHERE action='staff.role.save' ORDER BY id DESC LIMIT 1");
    ok(a && /apikey/.test(JSON.stringify(a)) && /ERP/.test(JSON.stringify(a)), "each action is recorded as the key's", a);
    ok((await call("/api/admin/roles", support, "POST", { key: "nope", name: "Nope", sections: {} })).status === 403 && (await call("/api/admin/orders", support)).status === 200, "a support key does what support may, and no more");
    const own = await call("/api/admin/roles", other);
    ok(own.status === 200 && !own.body.roles.some(r => r.key === "api_made"), "a key works in its own store only");
    ok([401, 403].includes((await call("/api/platform/records", owner)).status), "a store key never reaches the platform's routes");
    const id = db.get("SELECT id FROM mcp_keys WHERE name='ERP'").id; mcp.revokeKey(t1, id);
    ok((await call("/api/admin/roles", owner)).status === 401, "a revoked key stops at once");
  } catch (e) { failed++; console.log("  ✗ threw: " + (e.stack || e)); }
  finally { srv.kill(); }
  console.log(`\n${passed} passed, ${failed} failed`); if (failed && err) console.log(err.slice(-800)); wipe(); process.exit(failed ? 1 : 0);
})();

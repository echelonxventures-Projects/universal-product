/* The Master Global Platform is alone — one deployment, the platform's own.

   The model this pins (Architecture3 §4.2, and the constitutional rule that a
   platform is a composition, never a template): the platform is not a mall of peer
   tenants. There is ONE master deployment — the deployment the platform itself IS,
   the thing composition configures as an e-commerce platform, an ERP, a
   ride-hailing platform, a consultancy platform, or a type no one has named yet.
   The demo brands (aurum the industry marketplace, velora the brand house) are
   fixtures that illustrate what composition produces — opt-in through
   LUXORA_DEMO_BRANDS=1 — never the default population. Three properties:

     ALONE    — a default boot seeds exactly one deployment: the master's own.
     ROOTED   — every bare-host request, the composition console and the platform
                admin surfaces resolve to it, because it is a marked platform fact
                (platform_settings.master_deployment), not a slug convention.
     OPT-IN   — the demo fixtures appear only when explicitly requested. */
"use strict";
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const PORT = 8816, PORT_DEMO = 8817;
const BASE = `http://localhost:${PORT}`;
const BASE_DEMO = `http://localhost:${PORT_DEMO}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x ? " → " + x : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* one cookie jar per server, so the two boots never confuse their sessions */
function client(base) {
  const jar = new Map();
  const cookies = () => [...jar].map(([k, v]) => k + "=" + v).join("; ");
  async function f(p, method = "GET", body) {
    const opt = { method, headers: { Cookie: cookies(), ...(method !== "GET" ? { "x-csrf": jar.get("azc") || jar.get("pczc") || "" } : {}) } };
    if (body) { opt.body = JSON.stringify(body); opt.headers["Content-Type"] = "application/json"; }
    let r;
    try { r = await fetch(base + p, opt); }
    catch (e) { return { error: "network: " + String(e && e.message || e) }; }
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    const j = await r.json().catch(() => ({}));
    return { ...j, status: r.status };
  }
  return { f };
}

async function boot(port, db, extra = {}) {
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")],
    { env: { ...process.env, PORT: port, LX_DB: db, ...extra }, stdio: ["ignore", "ignore", "inherit"] });
  let up = false;
  for (let i = 0; i < 120; i++) {
    try { const h = await fetch(`http://localhost:${port}/healthz`); if (h.ok) { up = true; break; } } catch (e) { }
    await sleep(500);
  }
  if (!up) { console.log("server failed to boot on port " + port); process.exit(1); }
  return srv;
}
process.on("unhandledRejection", e => { console.log("  (ignoring unhandled rejection: " + String(e && e.message || e) + ")"); });

(async () => {
  const dbA = path.join(__dirname, "master.db");
  const dbB = path.join(__dirname, "master-demo.db");
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(dbA + s, { force: true }); } catch (e) { } try { fs.rmSync(dbB + s, { force: true }); } catch (e) { } }

  console.log("▸ ALONE — a default boot seeds the master's own deployment and nothing else");
  const A = client(BASE);
  const srvA = await boot(PORT, dbA);  const root = await A.f("/healthz");
  ok(root.ok === true && root.tenant === "luxora", "a bare-host request resolves to the master's own deployment", root.tenant);
  ok(root.products > 0, "the master's deployment carries a live storefront", root.products + " products");

  const li = await A.f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
  ok(li.status === 200 && !!li.ok, "the platform owner signs in", li.error || li.status);
  const tens = await A.f("/api/platform/tenants");
  const list = tens.tenants || [];
  ok(list.length === 1, "exactly one deployment exists — the master is alone, there is no mall", list.map(t => t.slug));
  const master = list[0];
  ok(master && master.slug === "luxora", "the master's own deployment is the seed root", master && master.slug);

  /* the mark is data, not convention — an operator could find and even move it */
  let mark = null;
  try {
    const { DatabaseSync } = require("node:sqlite");
    const ro = new DatabaseSync(dbA);
    mark = ro.prepare("SELECT value FROM platform_settings WHERE key='master_deployment'").get();
    ro.close();
  } catch (e) { }
  ok(!!mark && Number(JSON.parse(mark.value)) === master.id, "the master's own deployment is a marked platform fact (platform_settings.master_deployment)", mark && mark.value);

  console.log("▸ ROOTED — the console composes the master, never a peer");
  const caps = await A.f("/api/capabilities");
  ok(caps.tenant_id === master.id, "the composition console composes the master's own deployment", caps.tenant_id);
  ok(caps.master_id === master.id, "the console names which deployment is the master", caps.master_id);
  ok(Array.isArray(caps.tenants) && caps.tenants.length === 1 && caps.tenants[0].master === true, "the only composition context offered is the master", caps.tenants && caps.tenants.map(t => t.slug + (t.master ? "★" : "")));
  const onCount = (caps.catalog || []).filter(c => c.on).length;
  ok(onCount > 0, "the master's deployment is already composed as an e-commerce platform", onCount + " atoms on");
  ok((caps.catalog || []).some(c => c.key === "buy_box" && c.on), "the marketplace composition is live on the master", "buy_box");

  console.log("▸ OPT-IN — the demo brands are fixtures, never the default population");
  ok(!list.some(t => t.slug === "aurum" || t.slug === "velora"), "aurum and velora are NOT seeded on a default boot", list.map(t => t.slug));
  const fixtureLogin = await A.f("/api/auth/login", "POST", { email: "admin@aurum.shop", password: "aurum123" });
  ok(!!fixtureLogin.error, "a demo-brand fixture account cannot sign in on a default boot", fixtureLogin.error || fixtureLogin.status);
  const prods = await A.f("/api/products?limit=3");
  ok(Array.isArray(prods.items) && prods.items.length > 0, "the master's own storefront serves products", prods.items && prods.items.length);

  /* and when the fixtures ARE requested, they arrive subordinate to the master */
  const B = client(BASE_DEMO);
  const srvB = await boot(PORT_DEMO, dbB, { LUXORA_DEMO_BRANDS: "1" });
  const rootB = await B.f("/healthz");
  ok(rootB.ok === true && rootB.tenant === "luxora", "with fixtures installed the bare host still resolves to the master", rootB.tenant);
  const liB = await B.f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
  ok(liB.status === 200 && !!liB.ok, "the platform owner signs in on the fixture boot", liB.error || liB.status);
  const tensB = await B.f("/api/platform/tenants");
  const listB = tensB.tenants || [];
  ok(listB.length === 3, "opting in installs the demo fixtures", listB.map(t => t.slug));
  ok(listB[0] && listB[0].slug === "luxora", "the master stays the master — fixtures never precede it", listB.map(t => t.slug));
  ok(listB.some(t => t.slug === "aurum" && t.slug !== "luxora"), "aurum arrives as a fixture deployment", listB.map(t => t.slug));
  ok(listB.some(t => t.slug === "velora"), "velora arrives as a fixture deployment", listB.map(t => t.slug));

  console.log(`\n${passed} passed, ${failed} failed`);
  try { srvA.kill("SIGKILL"); } catch (e) { }
  try { srvB.kill("SIGKILL"); } catch (e) { }
  process.exit(failed ? 1 : 0);
})();

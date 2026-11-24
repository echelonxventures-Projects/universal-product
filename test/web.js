/* LUXORA Platform — how the platform answers the web: which store a host is, proving an address,
   visits that leave no row behind, caching and compression, what a page says about itself, the
   legal pages, and a proxy's word about the client. The real server in this process. */
"use strict";
const path = require("path"), fs = require("fs"), http = require("http"), zlib = require("zlib");
const DB = path.join(__dirname, "web.db");
const clean = () => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } } };
clean();
process.env.LX_DB = DB; process.env.PORT = "8899"; process.env.LX_LOG = ""; process.env.LX_OFFLINE = "1"; process.env.LUXORA_DEMO_BRANDS = "1";
delete process.env.NODE_ENV;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
/* http, not fetch: a Host header of our choosing */
const req = (p, o = {}) => new Promise((res, rej) => {
  const r = http.request({ host: "127.0.0.1", port: 8899, path: p, method: o.method || "GET", headers: o.headers || {} }, m => { const b = []; m.on("data", c => b.push(c)); m.on("end", () => { let buf = Buffer.concat(b); const e = m.headers["content-encoding"]; if (e === "br") buf = zlib.brotliDecompressSync(buf); else if (e === "gzip") buf = zlib.gunzipSync(buf); res({ status: m.statusCode, headers: m.headers, text: buf.toString("utf8") }); }); });
  r.on("error", rej); if (o.body) r.write(o.body); r.end();
});
const storeAt = async host => JSON.parse((await req("/healthz", { headers: { Host: host } })).text).tenant;
(async () => {
  const quiet = console.log; console.log = () => { };
  require("../server.js");
  const db = require("../lib/db.js"), SD = require("../lib/store-domains.js"), sec = require("../lib/security.js");
  console.log = quiet;
  for (let i = 0; i < 160; i++) { try { if ((await req("/readyz")).status === 200) break; } catch (e) { } await sleep(250); }
  try {
    console.log("▸ WHICH STORE A HOST IS");
    const aurum = db.get("SELECT id FROM tenants WHERE slug='aurum'").id, velora = db.get("SELECT id FROM tenants WHERE slug='velora'").id;
    ok(await storeAt("aurum.localhost:8899") === "aurum" && await storeAt("localhost") === "luxora", "a name under localhost, in development; the bare host is the master's");
    db.run("UPDATE tenants SET domain='brand.com' WHERE id=?", aurum); db.run("UPDATE tenants SET domain='brand.in' WHERE id=?", velora);
    ok(await storeAt("brand.com") === "aurum" && await storeAt("brand.in") === "velora", "two addresses that share a first word are two stores");
    ok(await storeAt("www.brand.com") === "aurum", "www answers as the address does");
    ok(await storeAt("aurum.evil.test") === "luxora" && await storeAt("brand.com.evil.test") === "luxora", "a lookalike host is no store's");
    ok(JSON.parse((await req("/healthz?store=velora", { headers: { Host: "brand.com" } })).text).tenant === "aurum", "a store's own address cannot be made to show another store");

    console.log("▸ PROVING AN ADDRESS");
    const zone = {}; SD.__setResolver(async h => { if (!zone[h]) throw Object.assign(new Error("x"), { code: "ENOTFOUND" }); return zone[h].map(x => [x]); });
    const a = SD.add(aurum, "https://WWW.Shop.Example.com/path");
    ok(a.host === "shop.example.com" && a.record.name === "_luxora-verify.shop.example.com", "an address is cleaned and given its record", a);
    ok(!(await SD.verify(aurum, a.id)).verified && await storeAt("shop.example.com") === "luxora", "unproven, it answers for nobody");
    zone[a.record.name] = ["something else", a.record.value];
    ok((await SD.verify(aurum, a.id)).verified && await storeAt("shop.example.com") === "aurum", "proven by its DNS record, it is the store's");
    const b = SD.add(velora, "shop.example.com");
    ok(!(await SD.verify(velora, b.id)).verified && await storeAt("shop.example.com") === "aurum", "another store cannot take it without proving it");
    for (const bad of ["localhost", "10.0.0.1", "x", "a..b.com", "-a.com"]) { let e = null; try { SD.add(aurum, bad); } catch (x) { e = x; } ok(!!e, "refused: " + bad); }
    SD.makePrimary(aurum, a.id);
    ok(db.get("SELECT domain d FROM tenants WHERE id=?", aurum).d === "shop.example.com", "the main address is the one links and emails use");
    zone[a.record.name] = null; db.run("UPDATE store_domains SET checked_at=datetime('now','-2 days'), failing_since=datetime('now','-20 days') WHERE id=?", a.id);
    await SD.recheck();
    ok(!SD.list(aurum)[0].verified && await storeAt("shop.example.com") === "luxora", "an address that stays unprovable past the grace period is withdrawn");

    console.log("▸ VISITS");
    const n0 = db.get("SELECT COUNT(*) c FROM sessions").c;
    for (let i = 0; i < 5; i++) await req("/api/session");
    ok(db.get("SELECT COUNT(*) c FROM sessions").c === n0, "a visitor who keeps no cookie leaves no row");
    const v = await req("/api/session"), jar = v.headers["set-cookie"].map(c => c.split(";")[0]);
    const csrf = jar.find(c => c.startsWith("azc=")).slice(4), cookie = jar.join("; ");
    const p1 = db.get("SELECT id FROM products WHERE tenant_id=1 AND lifecycle='published' AND stock>3 LIMIT 1").id;
    const add = await req("/api/cart", { method: "POST", headers: { Cookie: cookie, "x-csrf": csrf, "Content-Type": "application/json" }, body: JSON.stringify({ id: p1, qty: 1 }) });
    ok(add.status === 200 && JSON.parse((await req("/api/cart", { headers: { Cookie: cookie } })).text).count === 1, "one who does keeps their bag", add.text.slice(0, 120));
    ok((await req("/api/cart", { method: "POST", headers: { Cookie: cookie, "x-csrf": "0".repeat(32), "Content-Type": "application/json" }, body: "{}" })).status === 403, "a first change still needs the right token");
    const fake = "azs=" + "a".repeat(48) + "." + "b".repeat(24);
    const f = await req("/api/cart", { headers: { Cookie: fake } });
    ok(!db.get("SELECT 1 x FROM sessions WHERE sid=?", fake.slice(4)) && (f.headers["set-cookie"] || []).some(c => c.startsWith("azs=") && !c.includes("aaaa")), "an id this server did not give out is never taken up");
    db.run("INSERT INTO sessions(sid, expires_at) VALUES('old', datetime('now','-1 day'))");
    require("../lib/session-sweep.js").sweep();
    ok(!db.get("SELECT 1 x FROM sessions WHERE sid='old'"), "expired sign-ins are cleared");

    console.log("▸ FILES");
    const js = await req("/js/app.js", { headers: { "Accept-Encoding": "gzip, br" } });
    ok(js.headers["content-encoding"] === "br" && js.headers.etag && js.text === fs.readFileSync(path.join(__dirname, "..", "public", "js", "app.js"), "utf8"), "scripts are compressed and intact");
    ok((await req("/js/app.js", { headers: { "If-None-Match": js.headers.etag } })).status === 304, "an unchanged file is not sent again");
    const home = await req("/");
    const m = /src="(js\/app\.js\?v=[A-Za-z0-9]+)"/.exec(home.text);
    ok(m && /immutable/.test((await req("/" + m[1])).headers["cache-control"]) && !/immutable/.test(js.headers["cache-control"]), "only an address that carries the file's version is kept for good");
    ok((await req("/%2e%2e/server.js")).status === 404, "nothing outside the public folder is served");

    console.log("▸ WHAT A PAGE SAYS");
    db.run("UPDATE products SET title=? WHERE tenant_id=1 AND id=?", 'Lamp </script><b>"x"', p1);
    const pg = (await req("/product.html?id=" + encodeURIComponent(p1), { headers: { Host: "localhost:8899" } })).text;
    const blocks = [...pg.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map(x => JSON.parse(x[1]));
    const prod = blocks.find(x => x["@type"] === "Product");
    ok(prod && prod.name === 'Lamp </script><b>"x"' && prod.offers.price > 0 && /^[A-Z]{3}$/.test(prod.offers.priceCurrency), "a product's data is structured, and text cannot break out of it", prod && prod.offers);
    ok(/<title>Lamp &lt;\/script&gt;/.test(pg) && /property="og:title"/.test(pg) && /rel="canonical"/.test(pg), "its title, card and canonical address are in the page itself");
    ok(!prod.aggregateRating || db.get("SELECT COUNT(*) c FROM reviews WHERE product_id=? AND user_id IS NOT NULL", p1).c > 0, "no rating is claimed that customers did not leave");
    ok(/noindex/.test((await req("/cart.html")).text) && !/noindex/.test(home.text), "private pages ask not to be indexed");
    const au = (await req("/index.html?store=aurum")).text;
    ok(!/<title>[^<]*LUXORA/.test(au), "another store's page carries its own name", /<title>[^<]*/.exec(au)[0]);
    const mf = await req("/manifest.webmanifest?store=aurum");
    ok(/manifest\+json/.test(mf.headers["content-type"]) && JSON.parse(mf.text).display === "standalone", "the store can be installed as an app");

    console.log("▸ LEGAL PAGES");
    const t1 = (await req("/privacy.html")).text;
    ok(/not yet complete/.test(t1) && /\[to be completed\]/.test(t1) && !/\{\{|<!--if/.test(t1), "unfilled details show as gaps, with a warning");
    const PM = require("../lib/page-meta.js");
    require("../lib/settings.js").save(1, { legal: Object.fromEntries(PM.LEGAL.map(f => [f.key, f.key === "businessName" ? "Acme <Ltd>" : "v-" + f.key])) });
    for (const k of ["privacy", "terms", "returns", "shipping", "cookies", "contact"]) { const x = await req("/" + k + ".html"); ok(x.status === 200 && !/not yet complete|to be completed|\{\{|<!--if/.test(x.text), k + " is complete once they are filled in"); }
    ok((await req("/terms.html")).text.includes("Acme &lt;Ltd&gt;"), "and shows them as text");

    console.log("▸ A PROXY'S WORD");
    const ip = h => { delete process.env.LX_TRUST_PROXY; if (h) process.env.LX_TRUST_PROXY = h; };
    ip(); ok(sec.trustedHops() === 0, "no proxy is trusted by default"); ip("1"); ok(sec.trustedHops() === 1, "one proxy"); ip("2"); ok(sec.trustedHops() === 2, "two proxies"); ip("yes"); ok(sec.trustedHops() === 0, "only a number of proxies counts"); 
    ip("1"); let blocked = 0;
    sec.setPolicy({ registerPerHour: 3 });
    for (let i = 0; i < 6; i++) blocked += (await req("/api/auth/register", { method: "POST", headers: { "Content-Type": "application/json", "X-Forwarded-For": "1.2.3." + i + ", 9.9.9.9" }, body: "{}" })).status === 429 ? 1 : 0;
    ok(blocked === 3, "a forged first address does not escape a limit", blocked); ip();
  } catch (e) { failed++; console.error("  ✗ harness error:", e && e.stack || e); }
  console.log(`\n${passed} passed, ${failed} failed`);
  clean(); process.exit(failed ? 1 : 0);
})();

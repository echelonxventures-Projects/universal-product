/* Expression (P12): languages are a registry with their scripts and writing directions; the
   storefront's copy has catalogues in other languages; a request is answered in the shopper's
   choice, else their browser's, else the store's locale's language, else the source language —
   always one the platform can speak — and a right-to-left language is laid out right to left. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");
const TMP = path.join(os.tmpdir(), "expression-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const E = require("../lib/expression.js");
const SEED = require("../lib/seed/expression.json");
const settings = require("../lib/settings.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const req = (headers) => ({ headers: headers || {} });
const url = q => new URL("http://x/api/config" + (q || ""));

console.log("expression — languages and catalogues are data");
ok(E.languages().some(l => l.direction === "rtl") && E.languages().every(l => l.script && l.direction), "every language names its script and direction; some write right to left");
const rtl = E.available().find(l => l.direction === "rtl");
ok(!!rtl && E.available().some(l => l.key === SEED.sourceLanguage), "the platform speaks its source language and every language with a catalogue", E.available().map(l => l.key));
ok(!E.speaks("ja") || Object.keys(SEED.catalogues).includes("ja"), "a declared language with no catalogue is not offered");
const shipped = settings.DEFAULTS.copy;
for (const [lang, cat] of Object.entries(SEED.catalogues)) {
  const keys = Object.keys(cat);
  ok(Object.keys(shipped).every(k => keys.includes(k)), lang + ": the catalogue covers every shipped copy key", Object.keys(shipped).filter(k => !keys.includes(k)));
  ok(keys.every(k => (String(shipped[k]).match(/\{\w+\}/g) || []).every(ph => cat[k].includes(ph))), lang + ": every {placeholder} is kept");
}

console.log("expression — the language a request is answered in");
ok(E.pick(req(), url("?lang=fr"), "en-US").lang === "fr", "a language named in the request wins");
ok(E.pick(req({ cookie: SEED.cookie + "=de" }), url(), "en-US").lang === "de", "then the shopper's remembered choice");
ok(E.pick(req({ "accept-language": "xx-YY, es-MX;q=0.9, en;q=0.5" }), url(), "en-US").lang === "es", "then the best language the browser asks for that the platform speaks");
ok(E.pick(req({ "accept-language": "xx" }), url(), "hi-IN").lang === "hi", "then the store's locale's language");
ok(E.pick(req(), url("?lang=xx"), "xx-YY").lang === SEED.sourceLanguage, "else the source language — never one it cannot speak");
ok(E.direction(rtl.key) === "rtl" && E.direction(SEED.sourceLanguage) === "ltr", "a language's direction is its registry row's");

console.log("expression — a store's own words stay in its own language");
const tid = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;
settings.save(tid, { copy: { ...settings.load(tid).copy, addToCart: "Into the bag" } });
ok(E.copyFor("en", shipped, E.savedCopy(tid), "en-US").addToCart === "Into the bag", "a store's saved copy applies in its own language");
ok(E.copyFor("fr", shipped, E.savedCopy(tid), "en-US").addToCart === SEED.catalogues.fr.addToCart, "and not in another, where the catalogue speaks");
db.run("UPDATE messages SET text=? WHERE lang='fr' AND key='addToCart'", "Mettre dans le sac");
E.seed();
ok(E.copyFor("fr", shipped, {}, "en-US").addToCart === "Mettre dans le sac", "an operator's catalogue edit is kept when the seed runs again");

/* the storefront's own answer, over HTTP */
const PORT = 8871, BASE = "http://localhost:" + PORT;
const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: TMP, LX_LOG: "" }, stdio: ["ignore", "ignore", "pipe"] });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const alive = async () => { try { return (await fetch(BASE + "/healthz")).ok; } catch (e) { return false; } };
(async () => {
  try {
    for (let i = 0; i < 120 && !(await alive()); i++) await sleep(500);
    console.log("expression — the storefront answers in the language");
    const ar = await (await fetch(BASE + "/api/config", { headers: { "accept-language": rtl.key } })).json();
    ok(ar.lang === rtl.key && ar.dir === "rtl" && ar.copy.signIn === SEED.catalogues[rtl.key].signIn, "a browser asking for a right-to-left language gets its copy and direction", { lang: ar.lang, dir: ar.dir });
    ok(Array.isArray(ar.languages) && ar.languages.length === E.available().length, "the storefront is told which languages it can switch to");
    const fr = await (await fetch(BASE + "/api/config?lang=fr", { headers: { "accept-language": rtl.key } })).json();
    ok(fr.lang === "fr" && fr.dir === "ltr", "a language named in the request overrides the browser");
  } catch (e) { failed++; console.log("  ✗ threw: " + (e.stack || e)); }
  srv.kill();
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();

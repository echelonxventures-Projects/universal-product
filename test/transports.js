/* LUXORA Platform — engines dispatch on a provider's declared transport, never its name.
   A notification provider's spec either describes an HTTP request (the spec engine) or declares
   a kernel `transport` (`smtp`, `log`) the mailer and notifier speak; an identity provider
   type declares the `protocols` its external flow speaks; an FX source declares that it
   `fetches`. Pointing a provider at another transport is a row edit. The gate below fails
   if an engine compares against a provider's name again. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "transports-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const mailer = require("../lib/mailer.js");
const identity = require("../lib/identity.js");
const providers = require("../lib/providers.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const specOf = id => JSON.parse(db.get("SELECT spec FROM provider_defs WHERE id=? AND kind='notification'", id).spec || "{}");
const setSpec = (id, s) => db.run("UPDATE provider_defs SET spec=? WHERE id=? AND kind='notification'", JSON.stringify(s), id);

(async () => {
  try {
    const tid = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;

    console.log("▸ EVERY NOTIFICATION PROVIDER IS AN HTTP SPEC OR A DECLARED KERNEL TRANSPORT");
    const bad = [];
    for (const p of providers.NOTIFICATION_PROVIDERS) {
      const sp = providers.PROVIDER_SPECS["notification:" + p.id];
      if (sp && sp.transport && !mailer.KERNEL[sp.transport]) bad.push(p.id + " → unknown transport " + sp.transport);
    }
    ok(bad.length === 0, "a declared transport is one the kernel speaks", bad);
    const declared = providers.NOTIFICATION_PROVIDERS.filter(p => (providers.PROVIDER_SPECS["notification:" + p.id] || {}).transport).map(p => p.id);
    ok(declared.every(id => specOf(id).transport === providers.PROVIDER_SPECS["notification:" + id].transport), "the declarations reach provider_defs on boot (" + declared.join(", ") + ")");

    console.log("▸ THE KERNEL FOLLOWS THE DECLARATION");
    const smtpId = declared.find(id => mailer.kernelOf(id) && mailer.kernelOf(id).urlEnv);
    const logId = declared.find(id => mailer.isLocal(id));
    ok(!!smtpId && !!logId, "one provider declares the SMTP kernel, one the local log", { smtpId, logId });
    ok(mailer.localNotifier() === logId, "a new store's starting notifier is the provider whose transport is local");
    db.run("INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fields,spec,enabled,position) VALUES('devconsole','notification','Dev console','🔌','','[]','[]',?,1,999)", JSON.stringify({ transport: mailer.transportOf(logId) }));
    ok(mailer.isLocal("devconsole"), "a provider added as a row and declaring the local transport is treated as local");
    const before = specOf(logId);
    setSpec(logId, {});
    ok(!mailer.isLocal(logId) && mailer.localNotifier() === "devconsole", "removing the declaration stops the old provider being local; the next declared one takes over");
    setSpec(logId, before);

    console.log("▸ THE PLATFORM DEFAULT IS CHOSEN BY THE KERNEL THAT READS IT");
    const k = mailer.kernelOf(smtpId);
    const save = { url: process.env[k.urlEnv], from: process.env.LX_MAIL_FROM, prov: process.env.LX_MAIL_PROVIDER };
    delete process.env.LX_MAIL_PROVIDER;
    process.env[k.urlEnv] = "smtps://u%40x:p@mail.example.test:465"; process.env.LX_MAIL_FROM = "noreply@example.test";
    const t = mailer.transportFor(null, "email");
    ok(t && t.provider === smtpId && t.config.host === "mail.example.test" && t.config.user === "u@x" && t.config.secure === true, "a URL in " + k.urlEnv + " selects the provider whose kernel reads it", t);
    if (save.url === undefined) delete process.env[k.urlEnv]; else process.env[k.urlEnv] = save.url;
    if (save.from === undefined) delete process.env.LX_MAIL_FROM; else process.env.LX_MAIL_FROM = save.from;
    if (save.prov !== undefined) process.env.LX_MAIL_PROVIDER = save.prov;

    console.log("▸ AN IDENTITY PROVIDER TYPE DECLARES ITS PROTOCOLS");
    const types = identity.getProviderTypes();
    const multi = types.find(t => Array.isArray(t.protocols) && t.protocols.length > 1);
    ok(!!multi && types.filter(t => t.flow === "external").every(t => Array.isArray(t.protocols) && t.protocols.every(p => identity.PROTOCOLS[p])), "every external type lists protocols the engine speaks", types.map(t => [t.key, t.protocols]));
    const prov = { id: 1, provider_type: multi.key, name: "t" };
    const r1 = identity.flowExternal({ tenantId: tid, provider: prov, config: { ssoUrl: "https://idp.example.test/sso" } });
    ok(r1.ok && r1.mode === multi.protocols[0], "with no choice in the config, the type's first protocol runs: " + r1.mode);
    const r2 = identity.flowExternal({ tenantId: tid, provider: prov, config: { mode: multi.protocols[1], issuer: "https://idp.example.test" } });
    ok(r2.ok && r2.mode === multi.protocols[1], "the config may pick another protocol the type declares: " + r2.mode);
    const r3 = identity.flowExternal({ tenantId: tid, provider: prov, config: { mode: "carrier-pigeon" } });
    ok(r3.ok && r3.mode === multi.protocols[0], "a protocol the type does not declare is never chosen");
    ok(!identity.createProviderType({ key: "pigeon", flow: "external", protocols: ["carrier-pigeon"] }).ok, "a new type naming a protocol the engine does not speak is refused");

    console.log("▸ THE GATE: NO ENGINE COMPARES AGAINST A PROVIDER'S NAME");
    const names = new Set(providers.NOTIFICATION_PROVIDERS.map(p => p.id));
    for (const x of require("../lib/registry.js").list("fxSources") || []) names.add(x.key);
    for (const x of types) names.add(x.key);
    /* identity: the password flow is the engine's own kernel flow, named by its `flow` field */
    const EXEMPT = new Set(["password"]);
    const hits = [];
    const LIB = path.join(__dirname, "..", "lib");
    for (const f of fs.readdirSync(LIB).filter(f => f.endsWith(".js"))) {
      const src = fs.readFileSync(path.join(LIB, f), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
      const re = /(?:provider(?:_type|_id)?|\bid|\bp)\s*[!=]==\s*["']([A-Za-z_-]+)["']/g; let m;
      while ((m = re.exec(src))) if (names.has(m[1]) && !EXEMPT.has(m[1])) hits.push(f + ": " + m[0]);
    }
    ok(hits.length === 0, "no engine branches on a notification provider, FX source or identity type by name", [...new Set(hits)]);
  } catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();

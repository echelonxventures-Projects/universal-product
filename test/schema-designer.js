/* LUXORA Platform — the schema designer: types and fields are added from the Super Admin portal
   (Platform console → Data Studio), never in code, and every type and field says which roles may
   read, create, update and delete it. Runs a real server on its own throwaway database.

   - an EXTENSION adds fields to a built-in, table-backed type (supplier): its values are stored
     beside each record (entity_ext), listed with it, updated alone, and removed with it;
   - a field's own grants hide it from roles that may not read it and refuse it to roles that may
     not write it; a custom type's grants admit exactly the roles named;
   - a definition is checked before it is saved: unknown roles, unknown types, a field the base
     type already has, or a built-in type replaced outright are refused. */
"use strict";
const path = require("path");
const fs = require("fs");
const DB = path.join(__dirname, "schema-designer.db");
process.env.LX_DB = DB;
const { spawn } = require("child_process");
const PORT = 8842;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const mk = () => {
  const c = new Map();
  const fn = async (p, m, b) => {
    const h = { Cookie: [...c].map(x => x.join("=")).join("; ") };
    if (m && m !== "GET") Object.assign(h, { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" });
    const r = await fetch(BASE + p + (p.includes("?") ? "&" : "?") + "store=luxora", { method: m || "GET", headers: h, body: b !== undefined ? JSON.stringify(b) : undefined });
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    const t = await r.text(); let body; try { body = JSON.parse(t); } catch (e) { body = { _raw: t }; }
    return { status: r.status, body };
  };
  return fn;
};
const alive = async () => { try { return (await fetch(BASE + "/healthz")).ok; } catch (e) { return false; } };
const clean = () => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } } };

(async () => {
  clean();
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB, LX_LOG: "" }, stdio: ["ignore", "ignore", "pipe"] });
  let stderr = ""; srv.stderr.on("data", d => { stderr += d; });
  for (let i = 0; i < 360 && !(await alive()); i++) await sleep(500);
  if (!(await alive())) { console.error("server failed to boot\n" + stderr); process.exit(1); }
  try {
    const P = mk(); await P("/api/session");
    ok((await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "the platform administrator signs in");
    const A = mk(); await A("/api/session");
    ok((await A("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" })).status === 200, "the store owner signs in");

    console.log("▸ THE DESIGNER OFFERS ONLY WHAT EXISTS");
    const defs = await P("/api/meta/entity-def");
    const v = defs.body.vocab || {};
    ok(Array.isArray(v.fieldTypes) && v.fieldTypes.some(t => t.key === "text"), "field types come from the platform's declaration", v.fieldTypes);
    ok(Array.isArray(v.roles) && ["platform", "admin", "owner", "support"].every(k => v.roles.some(r => r.key === k)), "roles offered are the platform, all staff, and the store's own role set", (v.roles || []).map(r => r.key));
    ok(Array.isArray(v.types) && v.types.some(t => t.key === "supplier"), "every existing type can be extended");

    console.log("▸ A DEFINITION IS CHECKED BEFORE IT IS SAVED");
    const badRole = await P("/api/meta/entity-def", "POST", { extends: "supplier", fields: [{ key: "x1", label: "X", type: "text", perm: { read: ["wizard"] } }] });
    ok(badRole.status === 400 && /unknown role wizard/.test(badRole.body.error), "an unknown role is refused", badRole.body);
    const badType = await P("/api/meta/entity-def", "POST", { extends: "supplier", fields: [{ key: "x2", label: "X", type: "spreadsheet" }] });
    ok(badType.status === 400 && /unknown type/.test(badType.body.error), "an unknown field type is refused", badType.body);
    const clash = await P("/api/meta/entity-def", "POST", { extends: "supplier", fields: [{ key: "name", label: "Name", type: "text" }] });
    ok(clash.status === 400 && /already exists on supplier/.test(clash.body.error), "a field the type already has is refused", clash.body);
    const replace = await P("/api/meta/entity-def", "POST", { key: "supplier", label: "Supplier", fields: [] });
    ok(replace.status === 400 && /built-in type/.test(replace.body.error), "a built-in type cannot be replaced outright, only extended", replace.body);
    const badKey = await P("/api/meta/entity-def", "POST", { extends: "supplier", fields: [{ key: "Bad Key!", label: "X", type: "text" }] });
    ok(badKey.status === 400, "a field key that is not a plain identifier is refused", badKey.body);

    console.log("▸ AN EXTENSION ADDS FIELDS TO A BUILT-IN TYPE — NO CODE, NO SCHEMA CHANGE");
    const ext = await P("/api/meta/entity-def", "POST", { extends: "supplier", fields: [
      { key: "gst_number", label: "GST number", type: "text", list: true },
      { key: "credit_days", label: "Credit days", type: "number" },
      { key: "internal_note", label: "Internal note", type: "textarea", perm: { read: ["owner", "finance", "platform"], write: ["owner", "finance", "platform"] } }
    ] });
    ok(ext.status === 200 && ext.body.key === "ext_supplier", "the extension is saved", ext.body);
    const mine = await A("/api/meta/entity/supplier", "POST", { name: "Acme Traders", gst_number: "29ABCDE1234F1Z5", credit_days: 30, internal_note: "pays late" });
    ok(mine.status === 200, "the owner creates a supplier with the added fields", mine.body);
    let row = ((await A("/api/meta/entity/supplier")).body.rows || []).find(r => r.name === "Acme Traders");
    ok(row && row.gst_number === "29ABCDE1234F1Z5" && Number(row.credit_days) === 30 && row.internal_note === "pays late", "the added fields come back with the record", row);
    const up = await A("/api/meta/entity/supplier/" + row.id, "PUT", { credit_days: 45 });
    row = ((await A("/api/meta/entity/supplier")).body.rows || []).find(r => r.id === row.id);
    ok(up.status === 200 && Number(row.credit_days) === 45 && row.gst_number === "29ABCDE1234F1Z5", "an added field is updated alone; the others are kept", row);
    const audit = (await P("/api/platform/audit?limit=50")).body;
    ok(JSON.stringify(audit).includes("entity_def.save"), "saving the definition is audit-logged", Object.keys(audit || {}));

    console.log("▸ A FIELD'S OWN GRANTS DECIDE WHO SEES AND CHANGES IT");
    const st = await A("/api/admin/staff", "POST", { name: "Sam Support", email: "sam@luxora.test", password: "Support-Pass-2026!", staff_role: "support", perms: { suppliers: "write" } });
    ok(st.status === 200, "a support staff member is added, with access to suppliers", st.body);
    const S = mk(); await S("/api/session");
    ok((await S("/api/auth/login", "POST", { email: "sam@luxora.test", password: "Support-Pass-2026!" })).status === 200, "the support member signs in");
    const seen = ((await S("/api/meta/entity/supplier")).body.rows || []).find(r => r.id === row.id);
    ok(seen && seen.gst_number === "29ABCDE1234F1Z5" && !("internal_note" in seen), "support sees the record and the open fields, but not the internal note", seen);
    const sneak = await S("/api/meta/entity/supplier/" + row.id, "PUT", { internal_note: "changed" });
    ok(sneak.status === 403 && /Internal note/.test(sneak.body.error), "support may not change the internal note", sneak.body);
    const allowed = await S("/api/meta/entity/supplier/" + row.id, "PUT", { credit_days: 60 });
    ok(allowed.status === 200, "…but may change a field open to every role", allowed.body);

    console.log("▸ A CUSTOM TYPE ADMITS EXACTLY THE ROLES IT NAMES");
    const ct = await P("/api/meta/entity-def", "POST", { key: "site_visit", label: "Site visit", fields: [{ key: "place", label: "Place", type: "text", required: true, list: true }],
      perm: { read: ["owner", "support", "platform"], create: ["support"], update: ["support"], delete: ["owner"] } });
    ok(ct.status === 200, "a custom type is defined with per-action roles", ct.body);
    const tid = (await P("/api/platform/tenants")).body.tenants.find(t => t.slug === "luxora").id;
    await P(`/api/meta/entity-def/site_visit/enable?tenant_id=${tid}`, "POST", {});
    const byOwner = await A("/api/meta/entity/site_visit", "POST", { place: "Warehouse 2" });
    ok(byOwner.status === 403, "the owner may read but not create (create is support's)", byOwner.status);
    const bySupport = await S("/api/meta/entity/site_visit", "POST", { place: "Warehouse 2" });
    ok(bySupport.status === 200, "support creates a visit", bySupport.body);
    ok(((await A("/api/meta/entity/site_visit")).body.rows || []).some(r => r.place === "Warehouse 2"), "the owner reads it");
    const vid = ((await S("/api/meta/entity/site_visit")).body.rows || []).find(r => r.place === "Warehouse 2").id;
    ok((await S("/api/meta/entity/site_visit/" + vid, "DELETE")).status === 403, "support may not delete it (delete is the owner's)");
    ok((await A("/api/meta/entity/site_visit/" + vid, "DELETE")).status === 200, "the owner deletes it");

    console.log("▸ A STORE'S PUBLIC ADDRESS IS SET IN THE PORTAL, NOT THE ENVIRONMENT");
    {
      const lux = (await P("/api/platform/tenants")).body.tenants.find(t => t.slug === "luxora");
      const badDom = await P("/api/platform/tenants/" + lux.id, "PUT", { domain: "https://evil.example/path?x=1 <script>" });
      ok(badDom.status === 400, "a domain that is not a host name is refused", badDom.body);
      const goodDom = await P("/api/platform/tenants/" + lux.id, "PUT", { domain: "https://Shop.Example.com/" });
      const saved = (await P("/api/platform/tenants")).body.tenants.find(t => t.slug === "luxora");
      ok(goodDom.status === 200 && saved.domain === "shop.example.com", "a domain is stored as a bare host name", saved.domain);
    }

    console.log("▸ DELETING A RECORD REMOVES ITS ADDED VALUES");
    const db = require("../lib/db.js");
    ok(!!db.get("SELECT 1 x FROM entity_ext WHERE entity='supplier' AND record_id=?", String(row.id)), "the added values are stored beside the record");
    const del = await A("/api/meta/entity/supplier/" + row.id + "?hard=1", "DELETE");
    ok(del.status === 200 && !db.get("SELECT 1 x FROM entity_ext WHERE entity='supplier' AND record_id=?", String(row.id)), "…and go with it", del.body);
  } catch (e) {
    failed++; console.error("  ✗ harness error:", e && e.stack || e);
  } finally {
    srv.kill("SIGTERM"); await sleep(300); clean();
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();

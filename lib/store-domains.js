/* LUXORA Platform — the addresses a store answers at.

   A store proves an address is its own by publishing a DNS TXT record the platform gives it; the
   platform looks the record up itself, so no DNS provider's keys are ever kept here. Only a proven
   address routes to the store, an address belongs to one store at a time, and one that stops being
   provable for longer than the grace period is withdrawn. `storeFor` answers which store a host is. */
"use strict";

const crypto = require("crypto");
const dns = require("dns");
const db = () => require("./db.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const HOST = /^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{0,61}[a-z0-9]$/;
const GRACE_DAYS = 14;
let resolveTxt = host => dns.promises.resolveTxt(host);
function __setResolver(fn) { const p = resolveTxt; resolveTxt = fn || (host => dns.promises.resolveTxt(host)); return p; }

const clean = h => String(h || "").trim().toLowerCase().replace(/^https?:\/\//, "").replace(/[/:?#].*$/, "").replace(/\.+$/, "").replace(/^www\./, "");
const recordName = host => "_luxora-verify." + host;
const recordValue = token => "luxora-verify=" + token;
const present = d => ({ id: d.id, host: d.host, verified: !!d.verified_at, verified_at: d.verified_at, primary: !!d.is_primary, checked_at: d.checked_at, error: d.error || "",
  record: { type: "TXT", name: recordName(d.host), value: recordValue(d.token) } });
const own = (tid, id) => { const d = db().get("SELECT * FROM store_domains WHERE id=? AND tenant_id=?", Number(id), Number(tid)); if (!d) throw fail("Address not found", 404); return d; };
const list = tid => db().all("SELECT * FROM store_domains WHERE tenant_id=? ORDER BY is_primary DESC, host", Number(tid)).map(present);

/* the platform's own address, and everything under it, is never a store's to claim */
function platformHost() { const m = db().masterTenant(); return m ? clean(m.domain) : ""; }
function add(tid, host) {
  const h = clean(host), base = platformHost();
  if (!HOST.test(h)) throw fail("Enter a domain name, e.g. shop.example.com");
  if (base && (h === base || h.endsWith("." + base))) throw fail("That address belongs to the platform", 409);
  if (db().get("SELECT 1 x FROM store_domains WHERE tenant_id=? AND host=?", Number(tid), h)) throw fail("This address is already on your list", 409);
  const r = db().run("INSERT INTO store_domains(tenant_id,host,token) VALUES(?,?,?)", Number(tid), h, crypto.randomBytes(16).toString("hex"));
  return present(own(tid, r.lastInsertRowid));
}
/* look the record up; proven, the address is this store's */
async function check(d) {
  let found = false, error = "";
  try { found = (await resolveTxt(recordName(d.host))).some(parts => parts.join("").trim() === recordValue(d.token)); if (!found) error = "The TXT record was found but does not match"; }
  catch (e) { error = e.code === "ENOTFOUND" || e.code === "ENODATA" ? "No TXT record found yet — DNS changes can take a few hours" : "The domain's DNS could not be read (" + (e.code || e.message) + ")"; }
  return { found, error };
}
async function verify(tid, id) {
  const d = own(tid, id), r = await check(d), D = db();
  if (!r.found) { D.run("UPDATE store_domains SET checked_at=datetime('now'), error=? WHERE id=?", r.error, d.id); return present(own(tid, id)); }
  const other = D.get("SELECT id FROM store_domains WHERE host=? AND verified_at IS NOT NULL AND id<>?", d.host, d.id);
  /* whoever can publish the record now owns the name: an earlier store's claim ends */
  if (other) { D.run("UPDATE store_domains SET verified_at=NULL, is_primary=0, error='Claimed by another store that proved it' WHERE id=?", other.id); letGo(other.id); }
  D.run("UPDATE store_domains SET verified_at=COALESCE(verified_at, datetime('now')), checked_at=datetime('now'), failing_since=NULL, error='' WHERE id=?", d.id);
  return present(own(tid, id));
}
/* an address no longer proven is no longer the one its store's links use */
function letGo(id) {
  const D = db(), d = D.get("SELECT * FROM store_domains WHERE id=?", Number(id));
  if (!d || d.verified_at) return;
  D.run("UPDATE store_domains SET is_primary=0 WHERE id=?", d.id);
  const t = D.get("SELECT domain FROM tenants WHERE id=?", d.tenant_id);
  if (t && clean(t.domain) === d.host) require("./stores.js").setAddress(d.tenant_id, "");
}
/* the address links and emails use */
function makePrimary(tid, id) {
  const d = own(tid, id);
  if (!d.verified_at) throw fail("Prove the address first", 409);
  const D = db();
  D.run("UPDATE store_domains SET is_primary=CASE WHEN id=? THEN 1 ELSE 0 END WHERE tenant_id=?", d.id, Number(tid));
  require("./stores.js").setAddress(tid, d.host);
  return present(own(tid, id));
}
function remove(tid, id) {
  const d = own(tid, id);
  if (d.is_primary) throw fail("Choose another main address first", 409);
  db().run("DELETE FROM store_domains WHERE id=?", d.id);
}
/* proven addresses are looked up again each day; one not provable for the grace period is withdrawn */
async function recheck() {
  const D = db();
  for (const d of D.all("SELECT * FROM store_domains WHERE verified_at IS NOT NULL AND (checked_at IS NULL OR checked_at < datetime('now','-1 day')) LIMIT 200")) {
    const r = await check(d);
    if (r.found) D.run("UPDATE store_domains SET checked_at=datetime('now'), failing_since=NULL, error='' WHERE id=?", d.id);
    else D.run("UPDATE store_domains SET checked_at=datetime('now'), error=?, failing_since=COALESCE(failing_since, datetime('now')), verified_at=CASE WHEN failing_since < datetime('now', ?) THEN NULL ELSE verified_at END WHERE id=?", r.error, "-" + GRACE_DAYS + " days", d.id);
    letGo(d.id);
  }
}
/* which store a host is: its proven address, its address set by the platform, or its name under the
   platform's own address (or .localhost, in development). null when the host names no store. */
function storeFor(hostHeader) {
  const D = db();
  const h = clean(hostHeader);
  if (!h) return null;
  const byDomain = D.get("SELECT t.* FROM store_domains s JOIN tenants t ON t.id=s.tenant_id WHERE s.host=? AND s.verified_at IS NOT NULL", h)
    || D.get("SELECT * FROM tenants WHERE domain=? OR domain=? ORDER BY id LIMIT 1", h, "www." + h);
  if (byDomain) return byDomain;
  const bases = [platformHost(), "localhost"].filter(Boolean);
  for (const b of bases) if (h.endsWith("." + b)) { const slug = h.slice(0, -b.length - 1); if (!slug.includes(".")) return D.get("SELECT * FROM tenants WHERE slug=?", slug) || null; }
  return null;
}

module.exports = { list, add, verify, makePrimary, remove, recheck, storeFor, clean, __setResolver };

/* LUXORA Platform — what still stands between this install and real customers, read from the install
   itself: each check says whether it holds and, when it does not, what to do. */
"use strict";

const fs = require("fs"), path = require("path");
const db = () => require("./db.js");
const DATA = path.join(__dirname, "..", "data");

function newestBackup() {
  const dir = path.resolve(process.env.LX_BACKUP_DIR || path.join(DATA, "backups"));
  let best = 0;
  try { for (const d of fs.readdirSync(dir)) { const f = path.join(dir, d, "manifest.json"); if (fs.existsSync(f)) best = Math.max(best, fs.statSync(f).mtimeMs); } } catch (e) { }
  return best;
}
function check() {
  const D = db(), sec = require("./security.js"), mailer = require("./mailer.js"), connect = require("./connect.js"), env = process.env;
  const out = [];
  const add = (ok, name, fix, required) => out.push({ ok: !!ok, name, fix: fix || "", required: required !== false });
  const master = D.masterTenant();
  add(env.NODE_ENV === "production", "Runs in production mode", "Set NODE_ENV=production.");
  add(/^[0-9a-f]{64}$/i.test(env.LUXORA_MASTER_KEY || "") || fs.existsSync(path.join(DATA, "master.json")), "An encryption key is kept", "Set LUXORA_MASTER_KEY, or keep data/master.json on a volume that is backed up.");
  /* more than one server behind one address (lib/cluster.js): what they must share. Required only
     once a second server is running. */
  const cl = require("./cluster.js"), many = cl.nodes().length > 1, CAT = require("./config.js").RUNTIME_CATALOG;
  /* the drivers are named by the runtime catalogue, never here (LAW-015) */
  const shared = c => ((CAT[c] || {}).drivers || []).filter(x => x !== (CAT[c] || {}).default && x !== D.EMBEDDED).join(" or ");
  add(D.DRIVER !== D.EMBEDDED, "More than one server: every server shares one database", "Run every server on the shared database (LX_DB_DRIVER=" + (shared("db") || "a networked driver") + " and LX_PG_URL). The embedded database serves processes on one machine only.", many);
  add(/^[0-9a-f]{64}$/i.test(env.LUXORA_MASTER_KEY || ""), "More than one server: every server has the same encryption key", "Give every server the same LUXORA_MASTER_KEY; the keyring they rotate is then kept in the database for all of them.", many);
  add(require("./config.js").driverOf("storage") !== "local", "More than one server: exported files are kept where every server can reach them", "Platform console → Runtime: set file storage to " + (shared("storage") || "a shared store") + ", so a file one server writes is there for the others.", many);
  const versions = [...new Set(cl.nodes().map(n => n.version))];
  add(versions.length <= 1, "More than one server: all of them run the same version", "Servers run " + versions.length + " versions (" + versions.join(", ") + "): finish the rollout so every server runs one.", many);
  add(String(env.LUXORA_PEPPER || "").length >= 16, "Password pepper is set", "Set LUXORA_PEPPER to a long random value before the first sign-up; it cannot be changed later.");
  add(sec.trustedHops() > 0 || env.LUX_TLS === "1", "Traffic is encrypted", "Put a TLS proxy in front and set LX_TRUST_PROXY=1 (docker-compose.yml does both), or set LUX_TLS=1.");
  add(String(env.LX_METRICS_TOKEN || "").length >= 16, "Metrics can be scraped", "Set LX_METRICS_TOKEN (16+ characters).", false);
  const dom = master && String(master.domain || "");
  add(dom && !/localhost$|\.test$|\.local$|example\./.test(dom), "The platform has its public address", "Platform console → Stores → the master store's domain.");
  add(mailer.transportFor(0, "email"), "Email is sent", "Master store's console → Payments → Email & SMS senders: set one live.");
  const admins = D.all("SELECT id, email FROM platform_admins");
  const mfa = require("./mfa.js");
  add(admins.length && admins.every(a => mfa.enrolled("platform", a.id)), "Every platform admin has two-step sign-in", "Each admin sets it up at their next sign-in.", false);
  const age = newestBackup();
  add(age && Date.now() - age < 36 * 3600e3, "A backup was made in the last 36 hours", "Run npm run backup on a schedule (systemd/luxora-backup.timer, or the compose file's backup service).");
  add(!!env.LX_BACKUP_S3_BUCKET, "Backups leave this machine", "Set LX_BACKUP_S3_BUCKET and its keys, or copy data/backups elsewhere.");
  for (const t of D.all("SELECT * FROM tenants").filter(t => !require("./states.js").has("tenant", t.status) || !require("./states.js").is("tenant", t.status, "blocked"))) {
    const products = D.get("SELECT COUNT(*) c FROM products WHERE tenant_id=? AND lifecycle='published' AND deleted_at IS NULL", t.id).c;
    if (!products) { if (master && t.id === master.id) add(false, t.name + ": has something to sell", "Add products, or load your catalogue.", false); continue; }
    const live = D.all("SELECT provider_id, config FROM tenant_gateways WHERE tenant_id=? AND enabled=1 AND mode='live' AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'", t.id)
      .filter(g => connect.ready({ provider: g.provider_id, config: sec.unsealConfig(t.id, g.provider_id, g.config || "{}") }));
    add(live.length, t.name + ": takes payments", "Store console → Payments: connect a gateway and set it live.");
    for (const g of live) { const c = sec.unsealConfig(t.id, g.provider_id, g.config || "{}"); add(c.webhookSecret || c.webhookId, t.name + ": " + g.provider_id + " confirms payments by webhook", "Add the webhook secret; without it payments are confirmed only by a check every few minutes.", false); }
    const gaps = require("./page-meta.js").legalGaps(t);
    add(!gaps.length, t.name + ": legal details are filled in", "Store console → Settings → Legal: " + gaps.join(", ") + ".");
    add(require("./page-meta.js").legal(t).reviewedOn, t.name + ": legal pages reviewed by a lawyer", "Have them reviewed, then record the date in Settings → Legal.");
    add(!require("./invoices.js").missing(t.id).length, t.name + ": tax invoices can be issued", "Settings → Legal: the tax details your country's invoices need.");
  }
  return out;
}
module.exports = { check, newestBackup };

/* LUXORA Platform — running on more than one server (lib/seed/cluster.json).

   The servers share one database and coordinate through it, with nothing else to run:
   - each server process is a row of cluster_nodes, refreshed every few seconds, so every server knows
     how many are alive and which versions they run;
   - a lease (cluster_leases) is held by one holder until it expires or is released: `once` runs a job
     on a clock on one server per period (the sweeps), `withLock` holds a lock across servers (one
     checkout per bag) for a call;
   - an epoch (cluster_epochs) is a counter a server raises when it drops a cache because something
     changed; every server reads the counters every epochPollMs and drops the same cache, so a store's
     settings saved on one server are what the others serve within a couple of seconds.
   On one server all of this holds trivially: it takes every lease and reads its own epochs. */
"use strict";

const os = require("os"), crypto = require("crypto"), fs = require("fs"), path = require("path");
const SEED = require("./seed/cluster.json");
const db = () => require("./db.js");
const N = Number;

const NODE = os.hostname().slice(0, 40) + ":" + process.pid + ":" + crypto.randomBytes(3).toString("hex");
const STARTED = Date.now();
/* the version a server runs: the sealed registry it was built with (it changes with the code) */
const VERSION = (() => { try { return crypto.createHash("sha256").update(fs.readFileSync(path.join(__dirname, "..", "_registry", "canonical.lxr"))).digest("hex").slice(0, 12); } catch (e) { return "unknown"; } })();

/* ============================== servers ============================== */
let alive = 1, aliveAt = 0;
function beat(nowMs) {
  const now = nowMs || Date.now();
  db().run(`INSERT INTO cluster_nodes(id, host, pid, version, started_at, seen_at) VALUES(?,?,?,?,?,?)
    ON CONFLICT(id) DO UPDATE SET seen_at=excluded.seen_at, version=excluded.version`, NODE, os.hostname().slice(0, 80), process.pid, VERSION, STARTED, now);
  db().run("DELETE FROM cluster_nodes WHERE seen_at<?", now - SEED.forgetAfterHours * 3600000);
  alive = Math.max(1, nodes(now).length); aliveAt = now;
  return alive;
}
/* the servers heard from within deadAfterSeconds */
function nodes(nowMs) {
  const now = nowMs || Date.now();
  return db().all("SELECT id, host, pid, version, started_at, seen_at FROM cluster_nodes WHERE seen_at>=? ORDER BY started_at", now - SEED.deadAfterSeconds * 1000)
    .map(r => ({ id: r.id, host: r.host, pid: N(r.pid), version: r.version, startedAt: new Date(N(r.started_at)).toISOString(), seenAt: new Date(N(r.seen_at)).toISOString(), self: r.id === NODE }));
}
/* how many servers share the work, as of the last heartbeat (1 before the first) */
const liveCount = () => alive;

/* ============================== leases ============================== */
/* takes the lease `name` for ttlMs, or renews it for its holder; true when held */
function lease(name, ttlMs, holder, nowMs) {
  const now = nowMs || Date.now(), who = holder || NODE;
  const r = db().run(`INSERT INTO cluster_leases(name, holder, until, taken_at) VALUES(?,?,?,?)
    ON CONFLICT(name) DO UPDATE SET holder=excluded.holder, until=excluded.until, taken_at=excluded.taken_at
    WHERE cluster_leases.until<? OR cluster_leases.holder=excluded.holder`, String(name), who, now + N(ttlMs), now, now);
  return r.changes > 0;
}
function release(name, holder) { return db().run("DELETE FROM cluster_leases WHERE name=? AND holder=?", String(name), holder || NODE).changes > 0; }
/* a job on a clock: runs here only when this server takes the period's lease, so on one server of all
   per period. The lease is kept to the end of the period; a server that stops loses it when it ends. */
function once(name, periodMs, fn) {
  let took = false;
  try { took = lease("job:" + name, Math.max(1000, periodMs * 0.9)); } catch (e) { console.error("cluster lease " + name + ":", e.message); return null; }
  if (!took) return null;
  return fn();
}
/* a lock across servers for one call: refused (null) while another call holds it */
async function withLock(name, fn, ttlMs) {
  const who = NODE + ":" + crypto.randomBytes(6).toString("hex"), key = "lock:" + name;
  if (!lease(key, ttlMs || SEED.lockSeconds * 1000, who)) return { locked: true };
  try { return { locked: false, value: await fn() }; }
  finally { try { release(key, who); } catch (e) { } }
}

/* ============================== epochs ============================== */
const HANDLERS = new Map(), SEEN = new Map();
/* `fn(rest)` runs on this server when an epoch named `cache` or `cache:<rest>` is raised anywhere */
function on(cache, fn) { if (!SEED.caches.includes(cache)) throw new Error("Unknown cluster cache " + cache); HANDLERS.set(cache, fn); }
/* this server dropped a cache: the others drop it too */
function bump(cache, rest) {
  if (!SEED.caches.includes(cache)) throw new Error("Unknown cluster cache " + cache);
  const name = rest == null || rest === "" ? cache : cache + ":" + rest;
  try {
    db().run("INSERT INTO cluster_epochs(name, n, at) VALUES(?,1,?) ON CONFLICT(name) DO UPDATE SET n=cluster_epochs.n+1, at=excluded.at", name, Date.now());
    const r = db().get("SELECT n FROM cluster_epochs WHERE name=?", name); if (r) SEEN.set(name, N(r.n));
  } catch (e) { /* the database is not ready yet (first boot): nothing else is running to tell */ }
}
let primed = false;
/* the counters raised since the last look: each cache dropped here too. The first look only learns them. */
function poll() {
  let n = 0;
  for (const r of db().all("SELECT name, n FROM cluster_epochs")) {
    const was = SEEN.get(r.name); SEEN.set(r.name, N(r.n));
    if (!primed || was === N(r.n)) continue;
    const i = r.name.indexOf(":"), cache = i < 0 ? r.name : r.name.slice(0, i), rest = i < 0 ? "" : r.name.slice(i + 1);
    const fn = HANDLERS.get(cache);
    if (fn) { try { fn(rest); n++; } catch (e) { console.error("cluster cache " + r.name + ":", e.message); } }
  }
  primed = true;
  return n;
}

/* ============================== running ============================== */
let timers = [];
/* what each kept-in-step cache drops on this server when another server raises its epoch */
function listen() {
  on("settings", rest => require("./settings.js").dropLocal(rest ? Number(rest) : 0));
  on("search", rest => require("./search.js").invalidateLocal(Number(rest)));
  on("keyring", () => require("./security.js").syncKeyring());
  on("runtime", () => require("./api.js").dropRuntimeSvc());
}
function start() {
  if (timers.length) return;
  listen();
  try { beat(); poll(); } catch (e) { console.error("cluster start:", e.message); }
  const hb = setInterval(() => { try { beat(); } catch (e) { console.error("cluster heartbeat:", e.message); } }, SEED.heartbeatSeconds * 1000);
  const ep = setInterval(() => { try { poll(); } catch (e) { console.error("cluster epochs:", e.message); } }, SEED.epochPollMs);
  for (const t of [hb, ep]) if (t.unref) t.unref();
  timers = [hb, ep];
}
/* a server shutting down leaves at once rather than when it is no longer heard from */
function stop() {
  for (const t of timers) clearInterval(t); timers = [];
  try { db().run("DELETE FROM cluster_nodes WHERE id=?", NODE); db().run("DELETE FROM cluster_leases WHERE holder=? OR holder LIKE ?", NODE, NODE + ":%"); } catch (e) { }
}
/* what the platform console shows: the servers, the leases held now, and the caches kept in step */
function status(nowMs) {
  const now = nowMs || Date.now(), list = nodes(now);
  return {
    self: NODE, version: VERSION, nodes: list, versions: [...new Set(list.map(x => x.version))],
    leases: db().all("SELECT name, holder, until FROM cluster_leases WHERE until>=? ORDER BY name", now).map(r => ({ name: r.name, holder: r.holder, until: new Date(N(r.until)).toISOString() })),
    epochs: db().all("SELECT name, n, at FROM cluster_epochs ORDER BY at DESC LIMIT 50").map(r => ({ name: r.name, n: N(r.n), at: new Date(N(r.at)).toISOString() }))
  };
}

module.exports = { NODE, VERSION, listen, beat, nodes, liveCount, lease, release, once, withLock, on, bump, poll, start, stop, status, SEED };

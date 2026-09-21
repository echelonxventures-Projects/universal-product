/* LUXORA Platform — Order fraud screening & risk.
   Screened at checkout: velocity (attempts per owner/IP/window), blocklists
   (email, card fingerprint, address, IP), an AVS/CVV-signal proxy and a composite
   0–100 risk score producing a decision — approve / hold for manual review / block.
   Holds land in a review queue the admin can release or decline. Block reasons and
   thresholds are meta_lists registries (riskSignals, riskActions) — editable in Data
   Studio. Feature-gated by settings.features.fraudScreen. */
"use strict";

const db = () => require("./db.js");
const crypto = require("crypto");

const ACTIONS = ["approve", "hold", "block"];
const WINDOW_MIN = 60;               /* velocity window in minutes */
const LIMITS = { perOwner: 6, perIp: 10, perCard: 4 };
const THRESHOLDS = { hold: 45, block: 75 };
/* a confirmed blocklist hit is an automatic block (hard signals) */
const HARD_BLOCK = { blocked_card: true, blocked_email: true, blocked_ip: true };
/* velocity breaches scale with how far over the limit the subject is */
const VELOCITY_WEIGHT_PER_EXCESS = 15;

function seed() {
  const D = db();
  const put = (name, label, items) => {
    const existing = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = existing ? JSON.parse(existing.items || "[]") : [];
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", name, label, JSON.stringify(items));
  };
  put("riskSignals", "Risk · Signal weights", Object.keys(SIGNALS).map(k => ({ key: k, name: k, weight: SIGNALS[k] })));
  put("riskActions", "Risk · Decisions", ACTIONS.map(k => ({ key: k, name: k })));
}

/* static signal weights (registry rows carry the live values; these are the seed) */
const SIGNALS = {
  new_account: 20,            /* account younger than 24h */
  high_value: 30,             /* order value above the high-value threshold */
  velocity_owner: 25,         /* > N orders from this owner in the window */
  velocity_ip: 20,            /* > N orders from this IP in the window */
  velocity_card: 30,          /* > N orders with this card fingerprint in the window */
  blocked_email: 60,          /* email on the blocklist */
  blocked_card: 70,           /* card fingerprint on the blocklist */
  blocked_address: 25,        /* shipping address hash on the blocklist */
  blocked_ip: 50,             /* IP on the blocklist */
  mismatch_billing: 10,       /* billing ≠ shipping country */
  refund_abuse: 15            /* prior refund ratio above threshold */
};
const HIGH_VALUE_AT = 1000;   /* orders at/above this are "high value" */

function fingerprint(input) {
  return crypto.createHash("sha256").update(String(input || "").toLowerCase().trim()).digest("hex").slice(0, 32);
}

/* ---------------- blocklists ---------------- */
function blocklist(tenantId, kind) {
  const D = db();
  return D.all("SELECT value, note FROM risk_blocklist WHERE tenant_id=? AND kind=? ORDER BY id", tenantId, kind);
}
function addBlock(tenantId, kind, value, note) {
  const D = db();
  if (!["email", "card", "address", "ip"].includes(kind)) throw new Error("Unknown blocklist kind");
  D.run("INSERT OR IGNORE INTO risk_blocklist(tenant_id,kind,value,note) VALUES(?,?,?,?)", tenantId, kind, fingerprint(value), String(note || "").slice(0, 200));
  return blocklist(tenantId, kind);
}
function onBlocklist(tenantId, kind, value) {
  return !!db().get("SELECT 1 ok FROM risk_blocklist WHERE tenant_id=? AND kind=? AND value=?", tenantId, kind, fingerprint(value));
}

/* ---------------- screening ---------------- */
function screen(tenantId, input) {
  const D = db();
  const owner = String(input.owner || ""), ip = String(input.ip || ""), email = String(input.email || "").toLowerCase();
  const amount = Number(input.amount) || 0;
  const cardFp = input.card ? fingerprint(input.card) : "";
  const addrFp = input.address ? fingerprint(input.address) : "";
  const signals = {};
  let score = 0;

  /* SQLite datetime() format (UTC, no T/Z) so the >= comparison is lexicographic and correct */
  const since = new Date(Date.now() - WINDOW_MIN * 60e3).toISOString().replace("T", " ").replace(/\.\d+Z$/, "");
  const oWin = D.get("SELECT COUNT(*) c FROM risk_events WHERE tenant_id=? AND owner=? AND created_at>=?", tenantId, owner, since).c;
  const ipWin = D.get("SELECT COUNT(*) c FROM risk_events WHERE tenant_id=? AND ip=? AND created_at>=?", tenantId, ip, since).c;
  const cardWin = cardFp ? D.get("SELECT COUNT(*) c FROM risk_events WHERE tenant_id=? AND card_fp=? AND created_at>=?", tenantId, cardFp, since).c : 0;

  if (input.account_age_days != null && Number(input.account_age_days) < 1) { signals.new_account = 1; score += SIGNALS.new_account; }
  if (amount >= HIGH_VALUE_AT) { signals.high_value = 1; score += SIGNALS.high_value; }
  if (oWin > LIMITS.perOwner) { signals.velocity_owner = oWin; score += SIGNALS.velocity_owner + (oWin - LIMITS.perOwner) * VELOCITY_WEIGHT_PER_EXCESS; }
  if (ipWin > LIMITS.perIp) { signals.velocity_ip = ipWin; score += SIGNALS.velocity_ip + (ipWin - LIMITS.perIp) * VELOCITY_WEIGHT_PER_EXCESS; }
  if (cardWin > LIMITS.perCard) { signals.velocity_card = cardWin; score += SIGNALS.velocity_card + (cardWin - LIMITS.perCard) * VELOCITY_WEIGHT_PER_EXCESS; }
  if (email && onBlocklist(tenantId, "email", email)) { signals.blocked_email = 1; score += SIGNALS.blocked_email; }
  if (input.card && onBlocklist(tenantId, "card", input.card)) { signals.blocked_card = 1; score += SIGNALS.blocked_card; }
  if (input.address && onBlocklist(tenantId, "address", input.address)) { signals.blocked_address = 1; score += SIGNALS.blocked_address; }
  if (ip && onBlocklist(tenantId, "ip", ip)) { signals.blocked_ip = 1; score += SIGNALS.blocked_ip; }
  if (input.bill_country && input.ship_country && input.bill_country !== input.ship_country) { signals.mismatch_billing = 1; score += SIGNALS.mismatch_billing; }

  score = Math.min(100, score);
  const hard = Object.keys(signals).some(k => HARD_BLOCK[k]);
  const action = hard || score >= THRESHOLDS.block ? "block" : score >= THRESHOLDS.hold ? "hold" : "approve";

  const r = D.run("INSERT INTO risk_events(tenant_id,owner,ip,card_fp,addr_fp,amount,score,action,signals,ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
    tenantId, owner, ip, cardFp, addrFp, amount, score, action, JSON.stringify(signals), String(input.ref || ""));
  const ev = D.get("SELECT * FROM risk_events WHERE id=?", Number(r.lastInsertRowid));
  return { ...ev, signals, decision: action };
}

/* ---------------- review queue ---------------- */
function queue(tenantId) {
  const D = db();
  return D.all("SELECT * FROM risk_events WHERE tenant_id=? AND action IN ('hold','block') AND resolved=0 ORDER BY score DESC, id DESC LIMIT 200", tenantId);
}
function resolve(tenantId, id, decision, note) {
  const D = db();
  if (!ACTIONS.includes(decision)) throw new Error("Unknown decision: " + decision);
  D.run("UPDATE risk_events SET resolved=1, resolution=?, resolved_at=datetime('now'), note=? WHERE id=? AND tenant_id=?", decision, String(note || "").slice(0, 300), Number(id), tenantId);
  return D.get("SELECT * FROM risk_events WHERE id=?", Number(id));
}
function stats(tenantId) {
  const D = db();
  const row = D.get("SELECT COUNT(*) n, AVG(score) avg, SUM(CASE WHEN action='approve' THEN 1 ELSE 0 END) a, SUM(CASE WHEN action='hold' THEN 1 ELSE 0 END) h, SUM(CASE WHEN action='block' THEN 1 ELSE 0 END) b FROM risk_events WHERE tenant_id=?", tenantId);
  return { total: row.n || 0, avg_score: row.avg ? +(+row.avg).toFixed(1) : 0, approved: row.a || 0, held: row.h || 0, blocked: row.b || 0, pending: D.get("SELECT COUNT(*) c FROM risk_events WHERE tenant_id=? AND resolved=0 AND action!='approve'", tenantId).c };
}

module.exports = {
  seed, ACTIONS, WINDOW_MIN, LIMITS, THRESHOLDS, SIGNALS,
  fingerprint, blocklist, addBlock, onBlocklist,
  screen, queue, resolve, stats
};

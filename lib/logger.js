/* LUXORA Platform - Structured logger (JSON in prod, plain in dev) */
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const isProd = process.env.NODE_ENV === "production";
/* file output is opt-in: the container runs read-only, so a log directory is a deliberate mount (LX_LOG_DIR) */
const LOG_DIR = process.env.LX_LOG_DIR ? path.resolve(process.env.LX_LOG_DIR) : "";
const AUDIT_EVENTS = new Set([
  "auth:login", "auth:logout", "auth:register", "auth:verify-mfa",
  "auth:change-password", "auth:reset-password", "auth:session-revoke",
  "admin:create", "admin:delete", "admin:update",
  "security:key-rotate", "security:config-change",
  "tenant:create", "tenant:delete", "tenant:plan-change",
  "role:change", "permission:grant", "permission:revoke",
  "order:create", "order:cancel", "order:refund",
  "payment:charge", "payment:refund", "payment:webhook",
  "content:publish", "content:delete",
]);

function appendLine(name, entry) {
  if (!LOG_DIR) return;
  try {
    fs.mkdirSync(LOG_DIR, { recursive: true });
    fs.appendFile(path.join(LOG_DIR, `${name}-${entry.ts.slice(0, 10)}.log`), JSON.stringify(entry) + "\n", () => {});
  } catch (e) { /* a full or read-only disk never takes a request down */ }
}

function _writeFile(level, msg, data) {
  appendLine(level, { ts: new Date().toISOString(), level, msg, ...(data || {}) });
}

function info(msg, data) {
  _writeFile("info", msg, data);
  if (isProd) console.log(JSON.stringify({ ts: new Date().toISOString(), level: "info", msg, ...(data || {}) }));
  else console.log(`[INFO] ${msg} ${JSON.stringify(data || {})}`);
}

function error(msg, data) {
  _writeFile("error", msg, data);
  if (isProd) console.error(JSON.stringify({ ts: new Date().toISOString(), level: "error", msg, ...(data || {}) }));
  else console.error(`[ERROR] ${msg} ${JSON.stringify(data || {})}`);
}

function warn(msg, data) {
  _writeFile("warn", msg, data);
  if (isProd) console.warn(JSON.stringify({ ts: new Date().toISOString(), level: "warn", msg, ...(data || {}) }));
  else console.warn(`[WARN] ${msg} ${JSON.stringify(data || {})}`);
}

function audit(event, tenantId, userId, details) {
  if (!AUDIT_EVENTS.has(event)) return;
  const entry = { ts: new Date().toISOString(), event, tenant_id: tenantId, user_id: userId, id: crypto.randomUUID(), ...(details || {}) };
  appendLine("audit", entry);
  return entry;
}

function requestLogger(req, res, next) {
  const start = Date.now();
  const id = crypto.randomUUID();
  req.id = id;
  res.on("finish", () => {
    const d = Date.now() - start;
    const url = req.originalUrl || req.url;
    if (res.statusCode >= 500) error("server-error", { method: req.method, path: url, status: res.statusCode, duration: d, reqId: id });
    else if (res.statusCode >= 400) warn("client-error", { method: req.method, path: url, status: res.statusCode, duration: d, reqId: id });
    else info("request", { method: req.method, path: url, status: res.statusCode, duration: d, reqId: id });
  });
  next();
}

module.exports = { info, error, warn, audit, requestLogger, AUDIT_EVENTS };

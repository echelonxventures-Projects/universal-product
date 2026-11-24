/* LUXORA Platform — telling the people who run the platform that something is wrong: server errors
   coming in a burst, or no recent backup. Sent by the platform's own email sender to its admins, at
   most once an hour per kind. (A platform that is down cannot send: point an outside monitor at /readyz.) */
"use strict";

const WINDOW = 5 * 60e3, BURST = 10, QUIET = 3600e3;
const errors = [], last = new Map();
function send(kind, subject, text) {
  if (process.env.NODE_ENV !== "production") return false;
  if (Date.now() - (last.get(kind) || 0) < QUIET) return false;
  last.set(kind, Date.now());
  console.error("ALERT " + kind + ": " + subject);
  try { for (const a of require("./db.js").all("SELECT email FROM platform_admins")) require("./mailer.js").deliver({ tenantId: 0, channel: "email", to: a.email, kind: "ops_alert", subject: "[LUXORA] " + subject, text }); } catch (e) { console.error("alert:", e.message); }
  return true;
}
/* called for every answered request */
function note(status, path, trace) {
  if (status < 500 || status === 503) return;
  const now = Date.now();
  errors.push({ at: now, path, trace });
  while (errors.length && now - errors[0].at > WINDOW) errors.shift();
  if (errors.length >= BURST) send("errors", errors.length + " server errors in 5 minutes", errors.slice(-10).map(e => new Date(e.at).toISOString() + "  " + e.path + "  " + e.trace).join("\n"));
}
function checkBackups() {
  const at = require("./readiness.js").newestBackup();
  if (!at || Date.now() - at > 36 * 3600e3) send("backup", "No backup in the last 36 hours", at ? "The newest backup is from " + new Date(at).toISOString() + "." : "No backup has been made on this machine.");
}
module.exports = { note, checkBackups };

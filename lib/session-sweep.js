/* LUXORA Platform — sign-ins and links whose time has passed are cleared (hourly, server.js). */
"use strict";

const db = () => require("./db.js");
function sweep() {
  const D = db();
  const gone = D.run("DELETE FROM sessions WHERE expires_at <= datetime('now')").changes;
  D.run("DELETE FROM platform_sessions WHERE expires_at <= datetime('now')");
  D.run("DELETE FROM tokens WHERE expires_at <= datetime('now')");
  D.run("DELETE FROM password_resets WHERE created_at < datetime('now','-30 days')");
  D.run("DELETE FROM email_verifications WHERE created_at < datetime('now','-30 days')");
  if (gone) require("./stores.js").forgetVisits();
  return { sessions: gone };
}
module.exports = { sweep };

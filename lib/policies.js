/* LUXORA Platform - Dynamic Policy Management */
"use strict";

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d || {}; } };

function getPolicies() {
  return db().all("SELECT * FROM config_store WHERE key LIKE 'policy.%'");
}

function getPolicy(category) {
  const row = db().get("SELECT value FROM config_store WHERE key=? AND active=1", `policy.${category}`);
  return row ? J(row.value, {}) : {};
}

function setPolicy(category, data) {
  const key = `policy.${category}`;
  const existing = db().get("SELECT id FROM config_store WHERE key=?", key);
  if (existing) {
    db().run("UPDATE config_store SET value=?, updated_at=? WHERE id=?", JSON.stringify(data), new Date().toISOString(), existing.id);
  } else {
    db().run("INSERT INTO config_store(key, value) VALUES(?, ?)", key, JSON.stringify(data));
  }
  return getPolicy(category);
}

module.exports = { getPolicies, getPolicy, setPolicy };

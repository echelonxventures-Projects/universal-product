/* UCOS Ω∞ — monitoring, health & drift detection for the constitutional registry.
   --------------------------------------------------------------------------
   Three concerns, all derived from the live registry tables (never from constants):

     health   — is the registry present, complete and internally consistent?
     drift    — do the on-disk Architecture documents still match what was seeded?
     metrics  — Prometheus gauges an operator can alert on.

   Drift is the interesting one. The registry is a PARSE of the documents, so it is a
   derived artifact: if someone edits Architecture1.txt without re-parsing, the platform holds a
   stale truth and silently disagrees with its own constitution. Digest() re-derives a hash from
   the documents on demand and compares it with the stamp stored at seed time (ucos_digest in
   platform_settings), so drift is detectable without re-writing a single row. */
"use strict";

const fs = require("fs");
const path = require("path");
const ucos = require("./ucos.js");
const ROOT = path.resolve(__dirname, "..");

/* lightweight db handle resolved lazily (enterprise.js pattern, avoids import cycles) */
let _db = null;
const db = () => _db || (_db = require("./db.js"));
const n = (sql, ...params) => { try { return (db().get(sql, ...params) || {}).n || 0; } catch (e) { return 0; } };
const setting = (k, d) => { try { const r = db().get("SELECT value FROM platform_settings WHERE key=?", k); return r ? r.value : d; } catch (e) { return d; } };

/* ---------- expected counts: derived from the documents, never magic numbers ----------
    Re-counts each document's own container markers directly in its source text so the health
    check can never disagree with a document about how many sections or articles it contains.
    The grammar (container kind + marker) is declared per document in ucos.DOCS, so this loop
    covers a newly registered constitution with no per-document branch anywhere. */
function expectedCounts() {
  const out = {};
  for (const d of ucos.DOCS) out[d.id] = { kind: d.container, count: ucos.countMarkers(d) };
  return out;
}

/* ---------- health ---------- */
function health() {
  const docs = ucos.DOCS.map(d => ({ id: d.id, file: d.file, present: fs.existsSync(path.join(ROOT, d.file)) }));
  const present = docs.filter(d => d.present);
  const exp = expectedCounts();
  const t = {
    sections: n("SELECT COUNT(*) n FROM ucos_sections WHERE kind='section'"),
    articles: n("SELECT COUNT(*) n FROM ucos_sections WHERE kind='article'"),
    concepts: n("SELECT COUNT(*) n FROM ucos_concepts"),
    registries: n("SELECT COUNT(*) n FROM ucos_registries"),
    edges: n("SELECT COUNT(*) n FROM ucos_edges"),
    orphans: n("SELECT COUNT(*) n FROM ucos_concepts c LEFT JOIN ucos_sections s ON s.doc_id=c.doc_id AND s.qkey=c.container_key WHERE s.id IS NULL AND c.container_kind='section'")
  };
  /* a section/article with no source line is an untraceable stub → zero-partial violation */
  const untraceable = n("SELECT COUNT(*) n FROM ucos_sections WHERE line IS NULL OR line <= 0");
  const dupSections = n("SELECT COUNT(*) n FROM (SELECT qkey FROM ucos_sections GROUP BY doc_id, qkey HAVING COUNT(*) > 1)");
  const dupConcepts = n("SELECT COUNT(*) n FROM (SELECT key FROM ucos_concepts GROUP BY doc_id, key HAVING COUNT(*) > 1)");
  const dupEdges = n("SELECT COUNT(*) n FROM (SELECT 1 FROM ucos_edges GROUP BY doc_id, source_type, source_id, rel, target_type, target_id HAVING COUNT(*) > 1)");

  const problems = [];
  if (present.length !== ucos.DOCS.length) problems.push({ code: "source_missing", detail: docs.filter(d => !d.present).map(d => d.file).join(", "), severity: "critical" });
  /* per document: every container the document declares in its own grammar is registered —
     one check per constitution instead of one section check and one article check, so the
     health verdict scales with the corpus rather than with the number of hardcoded names */
  for (const d of ucos.DOCS) {
    const want = (exp[d.id] || {}).count || 0;
    const live = n("SELECT COUNT(*) n FROM ucos_sections WHERE doc_id=? AND kind=?", d.id, d.container);
    if (live !== want) problems.push({ code: "container_count", detail: d.code + ": " + live + " registered vs " + want + " in " + d.file, severity: "critical" });
  }
  if (untraceable) problems.push({ code: "untraceable", detail: untraceable + " container(s) without a source line number", severity: "critical" });
  if (dupSections) problems.push({ code: "dup_sections", detail: dupSections + " duplicate section key(s)", severity: "critical" });
  if (dupConcepts) problems.push({ code: "dup_concepts", detail: dupConcepts + " duplicate concept key(s)", severity: "warning" });
  if (dupEdges) problems.push({ code: "dup_edges", detail: dupEdges + " duplicate graph edge(s)", severity: "warning" });

  const drift = driftStatus();
  if (drift.drifted) problems.push({ code: "drift", detail: drift.message, severity: "critical" });

  return {
    ok: problems.length === 0,
    status: problems.length === 0 ? "healthy" : (problems.some(p => p.severity === "critical") ? "unhealthy" : "degraded"),
    documents: docs,
    counts: t,
    expected: exp,
    digest: drift.stored,
    seededAt: seededAt(),
    problems,
    checkedAt: new Date().toISOString()
  };
}

/* ---------- drift ---------- */
/* Re-hash the documents and compare with the stamp written at seed time. The stamp is produced
   by ucos.digest() (content-derived from the parse), so drift here means "the parse of the
   documents on disk no longer matches the parse we committed to the registry". This NEVER
   re-writes the registry: it answers "is what's on disk different from what we parsed?" */
function documentDigest() {
  return ucos.digest(require("./db.js"));
}
function driftStatus() {
  const stored = setting("ucos_digest", null);
  const live = documentDigest();
  if (!stored) return { drifted: true, stored: null, live, message: "registry has never been seeded (no ucos_digest stamp)", severity: "critical" };
  if (stored !== live) return { drifted: true, stored, live, message: "source documents changed after the last parse — re-parse to resync the registry", severity: "critical" };
  /* even when the registry is in sync now, the boot chain may have auto-reparsed to get here;
     surface that so the change is never silent */
  const log = driftLog();
  if (log && log.action === "auto-reparsed") return { drifted: false, stored, live, autoReparsed: true, message: "registry auto-reparsed at boot after a source change (" + (log.at || "unknown time") + ")", severity: "info" };
  return { drifted: false, stored, live, message: "registry matches the source documents", severity: "ok" };
}
function seededAt() {
  const r = db().get("SELECT value FROM platform_settings WHERE key='ucos_seeded_at'");
  return r ? r.value : null;
}
function driftLog() {
  const raw = setting("ucos_drift_log", null);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch (e) { return null; }
}
function clearDriftLog() {
  try { db().run("DELETE FROM platform_settings WHERE key='ucos_drift_log'"); } catch (e) { }
}
function stampSeededAt() {
  try { db().run("INSERT INTO platform_settings(key,value) VALUES('ucos_seeded_at',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", new Date().toISOString()); } catch (e) { }
}

/* ---------- Prometheus metrics ---------- */
function promMetrics(prefix) {
  const p = prefix || "luxora_ucos";
  const out = [];
  const h = health();
  const push = (name, help, type, value) => { out.push("# HELP " + p + "_" + name + " " + help); out.push("# TYPE " + p + "_" + name + " " + type); out.push(p + "_" + name + " " + value); };
  push("sections_total", "Numbered sections registered from Architecture1.txt", "gauge", h.counts.sections);
  push("articles_total", "Constitutional articles registered from Architecture2.txt", "gauge", h.counts.articles);
  push("concepts_total", "Concepts registered across every constitutional document", "gauge", h.counts.concepts);
  push("registries_total", "Registry lists extracted from the documents", "gauge", h.counts.registries);
  push("edges_total", "Knowledge-graph edges (part->section->concept)", "gauge", h.counts.edges);
  push("orphan_concepts_total", "Concepts whose container section is missing", "gauge", h.counts.orphans);
  push("health", "1 = registry healthy, 0 = problems detected", "gauge", h.ok ? 1 : 0);
  push("drift", "1 = source documents differ from the seeded registry", "gauge", h.problems.some(x => x.code === "drift") ? 1 : 0);
  push("problems_total", "Number of failing health checks", "gauge", h.problems.length);
  out.push(p + '_problem{code="' + (h.problems[0] ? h.problems[0].code : "none") + '"} 1');
  return out.join("\n") + "\n";
}

module.exports = { health, driftStatus, documentDigest, seededAt, driftLog, clearDriftLog, stampSeededAt, promMetrics };

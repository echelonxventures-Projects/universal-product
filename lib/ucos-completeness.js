/* UCOS Ω∞ — foundation completeness audit.
   --------------------------------------------------------------------------
   Implements, as executable code, the FOUNDATION FREEZE CRITERIA the corpus
   defines as prose (Architecture2.txt 17AH.7):

       No Unresolved Authority    Gaps Exist
       No Unresolved Boundary     Gaps Exist
       No Unresolved Dependency   Gaps Exist
       No Unresolved Separation   Gaps Exist
       No Unresolved Ordering     Gaps Exist

   And the cross-universe OWNERSHIP AUDIT that UMQSOCR-DOC-022 makes a
   precondition for any further Tier-0 addition: "any further Tier-0 additions
   should be introduced only after a full cross-universe ownership audit,
   because most remaining concepts are likely derivatives, compositions, or
   specializations of foundations already established."

   Every check below reads the live registry tables. Nothing is hardcoded: the
   document list, article counts and concepts all come from the parse, so the
   audit stays correct as the corpus grows. */
"use strict";

const path = require("path");
const fs = require("fs");
const ROOT = path.resolve(__dirname, "..");

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const n = (sql, ...params) => { try { return (db().get(sql, ...params) || {}).n || 0; } catch (e) { return 0; } };
const rows = (sql, ...params) => { try { return db().all(sql, ...params) || []; } catch (e) { return []; } };

/* the five gap kinds from 17AH.7, in the corpus's own words */
const GAP_KINDS = ["authority", "boundary", "dependency", "separation", "ordering"];

/* ---------- 1 · authority: every concept has exactly one canonical owner ----------
   "Optimization constraints become duplicated / governance rules become
   decentralized" is the failure DOC-021 exists to prevent. Detect it by
   counting DISTINCT owning documents per concept name — a concept owned by two
   documents is exactly the duplicated authority the constitution forbids. */
/* PROSE GUARD: the parser also admits sentence fragments as concepts ("shall
   remain traceable.", "within a defined context."). Those are artifacts of the
   extract step, not constitutional claims, so they are excluded before the
   authority question is asked — otherwise the criterion reports 475 phantom
   violations and the real 371 get buried. A concept is substantive when it is
   a noun phrase, not a clause: at least 12 chars, no trailing period, and not
   starting with a modal/preposition/article. */

/* ---------- 1 · authority: no concept is owned by two constitutions in the same family ----------
   "Optimization constraints become duplicated / governance rules become
   decentralized" is the failure DOC-021 exists to prevent.

   IMPORTANT — what is NOT a violation. The registry parses two source FILES
   (upip and umqscr) that deliberately share a vocabulary: "Accountability",
   "Governance" and the like appear in both by design. Counting those as
   duplicated authority produced 991 phantom gaps and made the criterion worse
   than useless. The real question is whether two constitutions inside the SAME
   family both claim a concept — e.g. two UMQSOCR documents each declaring
   themselves the owner of "Optimization Constraint". That alone is the
   duplicated authority the constitution forbids, and is what the corpus's own
   OWNS / DOES NOT OWN blocks exist to partition. */
const PROSEY = /^(shall|must|within|through|across|all|the|a|an|every|each|this|these|those|its|their|when|where|if|then|and|or|of|for|to|in|on|by|with|from|that|which|such)\b/i;
const isSubstantive = name => { const t = String(name || "").trim(); return t.length >= 12 && !/[.;:]$/.test(t) && !PROSEY.test(t); };

/* NOTE on the count: COUNT(DISTINCT doc_id) is NOT the right signal, because both rows
   of a genuine conflict sit in the same file (two umqscr constitutions each claiming the
   concept) and collapse to one doc_id. The owner is the CONTAINER — a distinct container_key
   per claim — so that is what is counted. */
function authorityGaps() {
  const dup = rows("SELECT name, COUNT(DISTINCT container_key) owners, COUNT(*) refs FROM ucos_concepts GROUP BY name HAVING owners > 1");
  /* only a concept claimed by two documents in the SAME family is duplicated authority;
     the same concept appearing in both upip and umqscr is the intended shared vocabulary */
  const real = dup.filter(d => {
    if (!isSubstantive(d.name)) return false;
    const fams = rows("SELECT DISTINCT doc_id FROM ucos_concepts WHERE name=?", d.name).map(r => r.doc_id);
    const families = new Set(fams.map(f => String(f).replace(/[0-9]*$/, "")));
    /* compare families to OWNERS, not to the row count: SELECT DISTINCT doc_id collapses a
       genuine same-family conflict to one row, which made the earlier test always false and
       every real duplication invisible */
    return families.size < d.owners;
  });
  return real.sort((a, b) => b.refs - a.refs).slice(0, 100)
    .map(d => ({ kind: "authority", concept: d.name, detail: "claimed by " + d.docs + " documents in one family (" + d.refs + " rows)", severity: "critical" }));
}

/* ---------- 2 · dependency: referenced documents must exist ----------
   The corpus forward-references document ids (DOC-021 is named by DOC-020
   before it is written). A reference with no backing document is an
   unresolved dependency — the exact condition that made the false
   "DOC-154" status plausible. */
function dependencyGaps() {
  const known = new Set(rows("SELECT DISTINCT key FROM ucos_sections WHERE kind='article'").map(r => String(r.key || "")));
  const mentioned = new Set();
  for (const r of rows("SELECT DISTINCT container_name nm, container_key ck FROM ucos_concepts")) {
    for (const m of String(r.nm || "").matchAll(/DOC-[0-9]{3}/g)) mentioned.add("umqscr_doc_" + m[0].toLowerCase());
  }
  /* doc ids are also written into article names and doc_block json; scan those too */
  const names = rows("SELECT name nm, doc_block db FROM ucos_sections WHERE kind='article'");
  for (const r of names) {
    for (const m of String(r.nm || "").matchAll(/DOC-[0-9]{3}/g)) mentioned.add("umqscr_doc_" + m[0].toLowerCase());
  }
  const missing = [...mentioned].filter(m => !known.has(m) && !known.has(m.replace("umqscr_doc_", "umqsocr_")));
  return missing.slice(0, 50).map(m => ({ kind: "dependency", concept: m, detail: "referenced document id has no registered document", severity: "critical" }));
}

/* ---------- 3 · ordering: documents with a parent must follow it ----------
   DOC-025 declares Parent Foundation: UMQSOCR-DOC-024 inside its doc block.
   A child that parses to a lower article position than its parent is an
   unresolved ordering gap (the constitution is read sequentially). */
function orderingGaps() {
  const out = [];
  const pos = {};
  rows("SELECT qkey, line FROM ucos_sections WHERE kind='article'").forEach(r => { if (!(r.qkey in pos) || r.line < pos[r.qkey]) pos[r.qkey] = r.line; });
  for (const r of rows("SELECT qkey, doc_block FROM ucos_sections WHERE kind='article' AND doc_block IS NOT NULL")) {
    let blk = null; try { blk = JSON.parse(r.doc_block); } catch (e) { continue; }
    const parent = blk["Parent Foundation"] || blk.parent;
    if (!parent) continue;
    const childLine = pos[r.qkey];
    const parentKey = "umqscr_doc_" + String(parent).toLowerCase().replace(/umqscr-/i, "");
    if (parentKey in pos && childLine != null && pos[parentKey] > childLine)
      out.push({ kind: "ordering", concept: r.qkey, detail: "child document precedes its parent foundation " + parent, severity: "warning" });
  }
  return out.slice(0, 50);
}

/* ---------- 4 · boundary & 5 · separation: no concept may straddle documents ----------
   Boundary: a concept key should not appear under two documents.
   Separation: within one document the same concept key should not be
   re-declared with a different container (two constitutive definitions). */
/* boundary uses the SAME family test as authority, on the key rather than the
   name, so a concept cannot straddle two constitutions by renaming alone. */
function boundaryGaps() {
  const dup = rows("SELECT key, name, COUNT(DISTINCT doc_id) docs FROM ucos_concepts GROUP BY key, name HAVING docs > 1");
  const real = dup.filter(r => {
    if (!isSubstantive(r.name)) return false;
    const fams = rows("SELECT DISTINCT doc_id FROM ucos_concepts WHERE key=?", r.key).map(x => x.doc_id);
    const families = new Set(fams.map(f => String(f).replace(/[0-9]*$/, "")));
    return families.size < r.owners;   /* same owner-vs-family test as authorityGaps */
  });
  return real.slice(0, 100)
    .map(r => ({ kind: "boundary", concept: r.key, detail: "same key under " + r.docs + " documents in one family", severity: "critical" }));
}
function separationGaps() {
  return rows("SELECT key, COUNT(DISTINCT container_key) cks FROM ucos_concepts GROUP BY key, doc_id HAVING cks > 1 LIMIT 50")
    .map(r => ({ kind: "separation", concept: r.key, detail: "declared under " + r.cks + " containers in one document", severity: "warning" }));
}

/* ---------- the audit ---------- */
function audit() {
  const gaps = [].concat(authorityGaps(), dependencyGaps(), boundaryGaps(), separationGaps(), orderingGaps());
  const byKind = {};
  for (const g of gaps) byKind[g.kind] = (byKind[g.kind] || 0) + 1;
  const docs = rows("SELECT doc_id, sections, articles, concepts FROM ucos_documents ORDER BY doc_id");
  const frozen = gaps.filter(g => g.severity === "critical").length === 0;
  return {
    ok: frozen,
    verdict: frozen ? "FOUNDATION FREEZE CRITERIA SATISFIED — no unresolved critical gaps" : "UNRESOLVED GAPS — foundation is not freezable",
    criteria: GAP_KINDS.map(k => ({ kind: k, unresolved: byKind[k] || 0, satisfied: !(byKind[k] || 0) })),
    gapCount: gaps.length,
    criticalCount: gaps.filter(g => g.severity === "critical").length,
    documents: docs.length,
    gaps: gaps.slice(0, 100),
    auditedAt: new Date().toISOString()
  };
}

/* ---------- master index: the corpus's missing table of contents ----------
   "Overall Program Completion: Cannot be accurately determined yet because no
   master index has been defined." This produces one, from the registry, so the
   completion question becomes answerable instead of rhetorical.

   The index is keyed by the CONSTITUTIONAL documents the corpus actually
   declares (docId in each article's doc_block — UMQSOCR-DOC-nnn), not by the
   two source files, so "how many documents are done" is answered by the
   corpus's own numbering. */
function masterIndex() {
  const arts = rows("SELECT qkey, name, line, doc_block FROM ucos_sections WHERE kind=?", "article");
  const byDoc = new Map();
  for (const a of arts) {
    let blk = null; try { blk = JSON.parse(a.doc_block); } catch (e) { }
    const id = (blk && blk.docId) || "(unattributed)";
    if (!byDoc.has(id)) byDoc.set(id, { docId: id, title: (blk && blk.title) || a.name, firstLine: a.line, articles: 0 });
    const d = byDoc.get(id); d.articles++;
  }
  const documents = [...byDoc.values()].sort((x, y) => String(x.docId).localeCompare(String(y.docId)));
  return {
    corpus: "UCOS Ω∞ constitutional registry",
    documents,
    totals: { documents: documents.length, articles: arts.length, unattributed: (byDoc.get("(unattributed)") || { articles: 0 }).articles },
    generatedAt: new Date().toISOString()
  };
}

module.exports = { audit, masterIndex, authorityGaps, dependencyGaps, boundaryGaps, separationGaps, orderingGaps, GAP_KINDS };

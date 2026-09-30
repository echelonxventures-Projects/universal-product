/* UCOS Ω∞ · UPIP / UMQSOCR constitutional registry
   --------------------------------------------------------------------------
   Architecture1.txt (UPIP Ω∞ — 2,884 numbered sections, ~100 parts),
   Architecture2.txt (UMQSOCR Ω∞ — 529 articles, 26 documents) and
   Architecture3.txt (UCOS Ω∞ — 65 articles, 11 documents) are treated as
   the CANONICAL SOURCE OF TRUTH. This module never re-declares a single concept
   from them in code (Knowledge-Once Principle, Configuration-Over-Code): it
   parses the documents themselves and registers every part, section, article,
   concept, registry list and meta-model into the platform's registry tables.

   Nothing is hardcoded: every registry row carries its source document + line
   number, so the console can always point back at the authority. Parsing is
   streaming, idempotent and re-runnable on every boot without duplication. */
"use strict";

const fs = require("fs");
const path = require("path");

const DOCS = [
  { id: "upip",   file: "Architecture1.txt", code: "UPIP",   name: "Universal Product Intelligence Platform", kind: "architecture", container: "section", marker: /^#\s+\d+\.\s/ },
  { id: "umqscr", file: "Architecture2.txt", code: "UMQSOCR", name: "Universal Mathematics, Quantitative Sciences, Optimization & Computational Reasoning", kind: "constitution", container: "article", marker: /^#\s+ARTICLE\s/i },
  { id: "ucos",   file: "Architecture3.txt", code: "UCOS",   name: "Universal Civilization Operating System", kind: "constitution", container: "article", marker: /^#\s+ARTICLE\s/i },
  /* the fourth corpus: the universal industry · product · service · commerce universe —
     a pure universe/registry declaration. It reuses the UPIP container grammar
     ("# <n>. TITLE" sections), so it needs only a DOCS row and nothing else. */
  { id: "upce",   file: "Architecture4.txt", code: "UPCE",   name: "Universal Industry, Product, Service & Commerce Universe", kind: "architecture", container: "section", marker: /^#\s+\d+\.\s/ }
];
const ROOT = path.resolve(__dirname, "..");
/* fenced blocks decorated with a label ("Concepts", "Registry", "Meta Model"…)
   become registry lists; unlabelled ones are definition lists. */
const FENCE_LABEL = /Concepts|Registry|Registries|Meta-? ?Model|Categories|Types|Kinds|Domains|Components|Structure|Principles|Laws|Invariants|Services|Universe|Authorities|Layers|Dimensions|Nodes|Edges|Relationships|Classes|Hierarchy|Sources|Examples/i;

/* Concept entries inside a fence: drop tree-drawing characters, arrows and
   indentation so "├── Tenant" and "            ↓" never become concepts. */
const NOISE = /^(├|└|│|─|↓|→|←|↑|\*|•|-|=|>|\||#|\$|```)/;
const NOISE_WORD = /^(Document ID|Document Name|Version|Classification|Tier|Status|Next Document|Successor document|PART|END OF|UCOS|UMQSOCR|UPIP|Document|Article|Name|Description|Note)\b/i;
const META_LABEL = /^(Document ID|Document Name|Version|Classification|Tier|Status|Next Document|Successor document|Purpose|Declaration|Scope|Authority|Principle)$/i;

/* ---------- document reader ---------- */
function readDoc(doc) {
  const p = path.join(ROOT, doc.file);
  if (!fs.existsSync(p)) return null;
  return fs.readFileSync(p, "utf8").split(/\r?\n/);
}

/* ---------- container markers: how many sections/articles a document declares ----------
    Each constitution numbers its containers with its own grammar ("# 42. TITLE" for numbered
    sections in UPIP, "# ARTICLE 7" in the constitutional documents). Counting a document's own
    markers in its own source text yields the number the registry must reproduce — per document,
    so a fourth constitution needs a DOCS row and nothing else. Markers inside a fenced block are
    examples rather than headings, so fences are skipped the same way the parser skips them. */
function countMarkers(doc) {
  const lines = readDoc(doc);
  if (!lines || !doc.marker) return 0;
  let found = 0, inFence = false;
  for (const l of lines) {
    const t = l.trim();
    if (t.startsWith("```")) { const rest = t.slice(3).trim(); inFence = rest ? true : !inFence; continue; }
    if (inFence) continue;
    if (doc.marker.test(t)) found++;
  }
  return found;
}

/* ---------- canonical key (Unicode-safe, stable across documents) ---------- */
function keyOf(text) {
  return String(text || "")
    .normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[Ω∞]/g, "").replace(/[^a-z0-9]+/gi, " ")
    .trim().toLowerCase().replace(/\s+/g, "_").replace(/^_+|_+$/g, "")
    .slice(0, 120);
}

/* ---------- Architecture1: "# <n>. TITLE" ---------- */
const SEC = /^#\s+(\d+)\.\s+(.*)$/;
/* ---------- Architecture2: "# ARTICLE n" / "# TITLE" / "## n.m Title" ---------- */
const ARTICLE = /^#\s+ARTICLE\s+([0-9A-Z]+)/i;
const SUBSEC = /^##\s+([0-9]+[A-Z]*)\.([0-9]+[A-Z]*)\s+(.*)$/;

/* Parse one document into a normalized outline + concept pool.
   Architecture1  → parts > numbered sections > concepts
   Architecture2  → documents > articles > sub-sections > concepts */
function parseDocument(doc) {
  const lines = readDoc(doc);
  if (!lines) return null;
  const out = {
    doc: doc.id, file: doc.file, code: doc.code, name: doc.name,
    parts: [], sections: [], articles: [], concepts: [], registries: [],
    meta: { lines: lines.length, chars: 0, sections: 0, articles: 0, concepts: 0, registries: 0 }
  };
  out.meta.chars = lines.reduce((a, l) => a + l.length, 0);

  let part = null;              /* current part (number + title) */
  let partNo = 0;               /* running part ordinal for unique numbering */
  let sec = null;               /* current numbered section */
  let art = null;               /* current article */
  let sub = null;               /* current article sub-section */
  let docMeta = null;           /* UMQSOCR document block (Document ID/Name…) */
  let currentDoc = null;         /* resolved UMQSOCR document id (UMQSOCR-DOC-nnn) */
  let lastHeading = "";         /* nearest ## heading → fence label */
  let inFence = false, fenceLabel = "", fenceStart = 0, fenceBuf = [];
  const seenConcept = new Set();
  const seenSection = new Set();

  const flushFence = () => {
    if (!inFence) return;
    inFence = false;
    const body = fenceBuf;
    fenceBuf = [];
    if (!body.length) return;
    /* the document-ID fence precedes any section/article; resolve the scope from it */
    const didx = body.findIndex(l => /^Document ID:\s*$/i.test(l.trim()));
    if (didx >= 0 && body[didx + 1] && body[didx + 1].trim()) {
      currentDoc = body[didx + 1].trim();
      if (docMeta) docMeta.docId = currentDoc;
    }
    const owner = art || sec;
    if (!owner) return;
    /* labelled lists (Registry / Concepts / Meta Model …) → registry entry */
    const labelled = FENCE_LABEL.test(fenceLabel);
    const items = [];
    for (let bi = 0; bi < body.length; bi++) {
      const raw = body[bi];
      const t = raw.trim();
      if (!t || NOISE.test(t) || NOISE_WORD.test(t)) continue;
      /* "Label: value" pairs (Document ID: UMQSOCR-DOC-001) attach as metadata */
      if (/^[A-Z][A-Za-z ]{2,30}:\s*$/.test(t) && body[bi + 1] && body[bi + 1].trim()) {
        const k = t.replace(/:$/, "").trim(), v = body[bi + 1].trim();
        if (META_LABEL.test(k) || /Type|Parent|Authority/i.test(k)) {
          (owner.meta || (owner.meta = {}))[keyOf(k)] = v;
          if (k.toLowerCase() === "document id") {
            owner.docId = v;
            if (owner.kind === "article" || !owner.kind) currentDoc = v;
          }
          bi++;
          continue;
        }
      }
      if (/^[A-Z][A-Za-z ]{2,30}:\s*\S/.test(t) && !/https?/i.test(t)) {
        const i = t.indexOf(":");
        const k = t.slice(0, i).trim(), v = t.slice(i + 1).trim();
        if (META_LABEL.test(k)) { (owner.meta || (owner.meta = {}))[keyOf(k)] = v; continue; }
      }
      const k = keyOf(t);
      if (!k || k.length < 2 || seenConcept.has(k)) continue;
      seenConcept.add(k);
      items.push({ key: k, name: t.replace(/^[•\-*]\s+/, ""), line: fenceStart + bi });
    }
    if (!items.length) return;
    if (labelled) {
      owner.registries.push({ key: keyOf(fenceLabel) || "registry", label: fenceLabel, items: items.map(i => i.name), line: fenceStart });
      out.registries.push({ doc: doc.id, part: owner.partNo, container: owner.kind, container_key: owner.key, key: keyOf(fenceLabel) || "registry", label: fenceLabel, items: items.map(i => i.name), count: items.length, line: fenceStart });
    }
    owner.concepts.push(...items);
    out.concepts.push(...items.map(i => ({ ...i, doc: doc.id, part: owner.partNo, container: owner.kind, container_key: owner.key, container_name: owner.name })));
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (trimmed.startsWith("```")) {                             /* fence toggle */
      const rest = trimmed.slice(3).trim();
      if (!inFence) {                                            /* ```text / ``` opens */
        inFence = true; fenceBuf = []; fenceStart = i + 1; fenceLabel = lastHeading;
      } else if (!rest) {                                        /* bare ``` closes */
        flushFence();
      } else {                                                    /* tagged opener while open → flush, reopen */
        flushFence();
        inFence = true; fenceBuf = []; fenceStart = i + 1; fenceLabel = lastHeading;
      }
      continue;
    }
    if (inFence) {
      fenceBuf.push(line);
      continue;
    }

    /* ---- Architecture1 part boundaries: "# PART n" (exact, not "# PART n COMPLETION") ---- */
    const partM = /^#\s*PART\s+(\d+)\s*$/.exec(trimmed);
    if (partM) {
      const title = [];
      for (let j = i + 1; j < Math.min(i + 8, lines.length); j++) {
        const t = lines[j].trim();
        if (!t || t === "---" || /^```/.test(t) || SEC.test(t) || /^#/.test(t)) break;
        title.push(t);
      }
      partNo++;
      part = { no: partNo, label: "PART " + partM[1], title: title.join(" "), line: i + 1 };
      out.parts.push(part);
      sec = null; art = null; sub = null; docMeta = null;
      continue;
    }
    /* ---- Architecture2 document blocks (line after "# DOCUMENT") ---- */
    if (trimmed === "# DOCUMENT") { docMeta = { line: i + 1, title: "" }; continue; }

    const secM = SEC.exec(trimmed);
    if (secM) {                                                  /* Architecture1 section */
      flushFence();
      sec = { kind: "section", no: Number(secM[1]), key: keyOf(secM[2]), name: secM[2].trim(), line: i + 1, partNo: part ? part.no : 0, part: part ? part.label : "", concepts: [], registries: [], meta: {} };
      /* keys must be globally unique: part numbers can repeat (PART 97 / 97A…), so the part
         ORDINAL + section number + line together guarantee no collision and no loss */
      sec.qkey = "p" + sec.partNo + "_" + sec.no + "_" + keyOf(secM[2]) + "_l" + (i + 1);
      if (!seenSection.has(sec.qkey)) { seenSection.add(sec.qkey); out.sections.push(sec); out.meta.sections++; }
      art = null; sub = null;
      continue;
    }
    const artM = ARTICLE.exec(trimmed);
    if (artM) {                                                  /* Architecture2 article */
      flushFence();
      const title = [];
      for (let j = i + 1; j < Math.min(i + 4, lines.length); j++) {
        const t = lines[j].trim();
        if (!t || t === "---" || /^```/.test(t) || ARTICLE.test(t) || SUBSEC.test(t) || /^##\s/.test(t) || /^###\s/.test(t)) break;
        title.push(t.replace(/^#\s*/, ""));
      }
      /* article numbering restarts in every UMQSOCR document → prefix with the doc id */
      const dref = currentDoc ? keyOf(currentDoc) : (out.articles.length + 1);
      /* docMeta is a live module-level object that a later "# DOCUMENT" fence mutates in place
         (flushFence sets docMeta.docId). Passing it by reference let DOC-008's block inherit
         DOC-009's id, so snapshot it — each article owns the block as it stood when declared. */
      art = { kind: "article", no: artM[1], key: "article_" + dref + "_" + artM[1] + "_" + keyOf(title.join(" ")) + "_" + (out.articles.length + 1), docId: currentDoc || null, name: title.join(" "), line: i + 1, partNo: part ? part.no : 0, doc_block: docMeta ? Object.assign({}, docMeta, { docId: currentDoc }) : null, concepts: [], registries: [], meta: {} };
      out.articles.push(art); out.meta.articles++;
      sec = null; sub = null;
      continue;
    }
    const subM = SUBSEC.exec(trimmed);
    if (subM) {
      flushFence();
      lastHeading = subM[3].trim();
      sub = { no: subM[1] + "." + subM[2], name: subM[3].trim(), line: i + 1, article: art ? art.no : null };
      if (art) art.subs = art.subs || [], art.subs.push(sub);
      continue;
    }
    if (/^##\s+/.test(trimmed)) { lastHeading = trimmed.replace(/^##\s+/, "").trim(); continue; }
    if (trimmed.startsWith("# ") && !SEC.test(trimmed) && !ARTICLE.test(trimmed) && trimmed !== "# DOCUMENT" && !/^#?\s*PART\s/.test(trimmed)) {
      lastHeading = trimmed.replace(/^#\s+/, "").trim();
      if (docMeta && !docMeta.title) docMeta.title = lastHeading;   /* document heading */
    }
  }
  flushFence();

  out.meta.concepts = out.concepts.length;
  out.meta.registries = out.registries.length;
  out.meta.parts = out.parts.length;
  return out;
}

/* ---------- parse the documents (cached: parse is pure & deterministic) ---------- */
let CACHE = null;
function parseAll() {
  if (CACHE) return CACHE;
  CACHE = {};
  for (const d of DOCS) {
    const p = parseDocument(d);
    if (p) CACHE[d.id] = p;
  }
  return CACHE;
}

/* ---------- registry seeding (idempotent; re-running never duplicates) ----------
   The documents are immutable inputs, so a content hash is stamped in platform_settings;
   a warm boot whose documents are unchanged skips the ~50k-row rewrite entirely, and a
   re-parse (or an edited Architecture file) rebuilds deterministically. */
/* Content-address the SOURCE FILES by their BYTES. Stat fields (size/mtime) are NOT stable enough
   for a stamp read across processes — the boot chain re-seeds, and any filesystem that touches
   mtime would manufacture false drift — so the digest hashes file content, which is exactly what
   we care about: did the constitution's text change? */
function digest(Db) {
  const crypto = require("crypto");
  const h = crypto.createHash("sha256");
  for (const d of DOCS) {
    const p = path.join(ROOT, d.file);
    let body = null;
    try { body = fs.readFileSync(p); } catch (e) { }
    if (!body) { h.update(d.file + ":MISSING"); continue; }
    h.update(d.file + "|" + body.length + "|");
    h.update(crypto.createHash("sha256").update(body).digest("hex"));
  }
  return h.digest("hex");
}
/* Multi-row INSERT: one statement for N rows instead of N statements. The cold-boot seed writes
   ~50k rows; one prepare per row dominated that cost (concepts 1.5s + edges 1.45s). Batching cuts
   the round trips by orders of magnitude. Works on SQLite and Postgres (the bridge runs the whole
   statement as one prepared call; chunking keeps it inside the driver's parameter limits). */
const MAX_PARAMS = 900;      /* PG tops out at 65,535 params; SQLite at 999 — stay under both */
function batchInsert(Db, table, cols, rows, ignore) {
  if (!rows.length) return 0;
  const c = cols.length, chunk = Math.max(1, Math.floor(MAX_PARAMS / c));
  const verb = ignore ? "INSERT OR IGNORE INTO" : "INSERT INTO";
  for (let i = 0; i < rows.length; i += chunk) {
    const part = rows.slice(i, i + chunk);
    const placeholders = part.map(() => "(" + cols.map(() => "?").join(",") + ")").join(",");
    Db.run(verb + " " + table + "(" + cols.join(",") + ") VALUES " + placeholders, ...part.flat());
  }
  return rows.length;
}

function seed(Db) {
  const parsed = parseAll();
  const stamp = digest(Db);
  let prior = null;
  try { prior = (Db.get("SELECT value FROM platform_settings WHERE key='ucos_digest'") || {}).value || null; } catch (e) { }
  if (prior === stamp) {
    const stats = { docs: 0, parts: 0, sections: 0, articles: 0, concepts: 0, registries: 0, edges: 0, skipped: true };
    for (const docId of Object.keys(parsed)) {
      const r = Db.get("SELECT parts,sections,articles,concepts,registries FROM ucos_documents WHERE doc_id=?", docId);
      if (r) { stats.docs++; stats.parts += r.parts; stats.sections += r.sections; stats.articles += r.articles; stats.concepts += r.concepts; stats.registries += r.registries; }
    }
    stats.edges = (Db.get("SELECT COUNT(*) AS n FROM ucos_edges").n) || 0;
    return stats;
  }
  const stats = { docs: 0, parts: 0, sections: 0, articles: 0, concepts: 0, registries: 0, edges: 0 };
  for (const docId of Object.keys(parsed)) {
    const P = parsed[docId];
    stats.docs++; stats.parts += P.parts.length; stats.sections += P.sections.length;
    stats.articles += P.articles.length; stats.concepts += P.concepts.length; stats.registries += P.registries.length;
    const docRow = Db.get("SELECT 1 ok FROM ucos_documents WHERE doc_id=?", docId);
    if (!docRow) Db.run("INSERT INTO ucos_documents(doc_id,file,code,name,kind,parts,sections,articles,concepts,registries,lines,chars) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      docId, P.file, P.code, P.name, DOCS.find(d => d.id === docId).kind, P.parts.length, P.sections.length, P.articles.length, P.concepts.length, P.registries.length, P.meta.lines, P.meta.chars);
    else Db.run("UPDATE ucos_documents SET parts=?,sections=?,articles=?,concepts=?,registries=?,lines=?,chars=? WHERE doc_id=?",
      P.parts.length, P.sections.length, P.articles.length, P.concepts.length, P.registries.length, P.meta.lines, P.meta.chars, docId);
    /* parts */
    Db.run("DELETE FROM ucos_parts WHERE doc_id=?", docId);
    batchInsert(Db, "ucos_parts", ["doc_id", "no", "label", "title", "line"],
      P.parts.map(p => [docId, p.no, p.label, p.title, p.line]));
    /* sections / articles (containers) */
    Db.run("DELETE FROM ucos_sections WHERE doc_id=?", docId);
    batchInsert(Db, "ucos_sections", ["doc_id", "qkey", "no", "key", "name", "part_no", "line", "concepts", "registries", "meta"],
      P.sections.map(s => [docId, s.qkey, s.no, s.key, s.name, s.partNo, s.line, s.concepts.length, s.registries.length, JSON.stringify(s.meta || {})]));
    batchInsert(Db, "ucos_sections", ["doc_id", "qkey", "no", "key", "name", "part_no", "line", "concepts", "registries", "meta", "kind", "doc_block"],
      P.articles.map(a => [docId, a.key, a.no, a.key, a.name, a.partNo, a.line, a.concepts.length, a.registries.length, JSON.stringify(a.meta || {}), "article", a.doc_block ? JSON.stringify(a.doc_block) : null]));
    /* concepts — OR IGNORE keeps re-parses duplicate-free */
    Db.run("DELETE FROM ucos_concepts WHERE doc_id=?", docId);
    batchInsert(Db, "ucos_concepts", ["doc_id", "key", "name", "container_kind", "container_key", "container_name", "part_no", "line"],
      P.concepts.map(c => [docId, c.key, c.name, c.container || "", c.container_key || "", c.container_name || "", c.part || 0, c.line]), true);
    /* registry lists */
    Db.run("DELETE FROM ucos_registries WHERE doc_id=?", docId);
    batchInsert(Db, "ucos_registries", ["doc_id", "key", "label", "container_kind", "container_key", "items", "item_count", "line"],
      P.registries.map(r => [docId, r.key, r.label, r.container, r.container_key, JSON.stringify(r.items), r.count, r.line]));
    stats.edges += buildEdges(Db, docId, P);
  }
  try { Db.run("INSERT INTO platform_settings(key,value) VALUES('ucos_digest',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", stamp); } catch (e) { }
  try { require("./ucos-monitor.js").stampSeededAt(); } catch (e) { }
  return stats;
}

/* ---------- knowledge-graph edges (part → section → concept; no duplicates) ---------- */
function buildEdges(Db, docId, P) {
  Db.run("DELETE FROM ucos_edges WHERE doc_id=?", docId);
  const rows = [];
  for (const s of P.sections.concat(P.articles)) {
    const sid = s.qkey || s.key;                     /* articles key on `key` */
    if (!sid) continue;
    if (s.partNo) rows.push([docId, "part", s.partNo, "contains", "section", String(sid)]);
    for (const c of s.concepts) rows.push([docId, "section", String(sid), "defines", "concept", String(c.key)]);
  }
  return batchInsert(Db, "ucos_edges", ["doc_id", "source_type", "source_id", "rel", "target_type", "target_id"], rows, true);
}

/* ---------- read API ---------- */
function manifest() {
  const parsed = parseAll();
  return {
    documents: DOCS.map(d => { const p = parsed[d.id]; return p ? { id: d.id, file: d.file, code: d.code, name: d.name, kind: d.kind, parts: p.parts.length, sections: p.sections.length, articles: p.articles.length, concepts: p.concepts.length, registries: p.registries.length, lines: p.meta.lines } : null; }).filter(Boolean),
    principles: ["knowledge_once", "configuration_over_code", "registry_first", "infinite_extensibility", "technology_agnostic"]
  };
}
function search(q, limit) {
  const parsed = parseAll();
  const needle = keyOf(q);
  if (!needle) return [];
  const out = [];
  for (const docId of Object.keys(parsed)) {
    const P = parsed[docId];
    for (const s of P.sections.concat(P.articles))
      if (keyOf(s.name).includes(needle)) out.push({ doc: docId, type: "section", key: s.qkey, name: s.name, line: s.line, concepts: s.concepts.length });
    for (const c of P.concepts)
      if (c.key.includes(needle)) out.push({ doc: docId, type: "concept", key: c.key, name: c.name, container: c.container_name, line: c.line });
  }
  return out.slice(0, limit || 50);
}
function coverage() {
  const parsed = parseAll();
  const out = {};
  for (const docId of Object.keys(parsed)) {
    const P = parsed[docId];
    out[docId] = { parts: P.parts.length, sections: P.sections.length, articles: P.articles.length, concepts: P.concepts.length, registries: P.registries.length, chars: P.meta.chars };
  }
  return out;
}
/* DB-backed reads (the seeded tables are the live source of truth) */
function store(Db) {
  const docs = () => Db.all("SELECT * FROM ucos_documents ORDER BY kind, doc_id");
  const parts = (docId, limit, offset) => page(Db, "SELECT * FROM ucos_parts WHERE doc_id=? ORDER BY no", [docId], limit, offset);
  const sections = (docId, partNo, limit, offset) => {
    if (partNo != null && partNo !== "") return page(Db, "SELECT * FROM ucos_sections WHERE doc_id=? AND part_no=? ORDER BY line", [docId, Number(partNo)], limit, offset);
    return page(Db, "SELECT * FROM ucos_sections WHERE doc_id=? ORDER BY line", [docId], limit, offset);
  };
  const concepts = (docId, q, limit, offset) => {
    if (q) return page(Db, "SELECT * FROM ucos_concepts WHERE doc_id=? AND (key LIKE ? OR name LIKE ?) ORDER BY line", [docId, "%" + q + "%", "%" + q + "%"], limit, offset);
    return page(Db, "SELECT * FROM ucos_concepts WHERE doc_id=? ORDER BY line", [docId], limit, offset);
  };
  const registries = (docId, limit, offset) => page(Db, "SELECT * FROM ucos_registries WHERE doc_id=? ORDER BY line", [docId], limit, offset);
  const edges = (docId, sourceType, sourceId, limit, offset) => {
    if (sourceId) return page(Db, "SELECT * FROM ucos_edges WHERE doc_id=? AND source_type=? AND source_id=? ORDER BY id", [docId, sourceType, sourceId], limit, offset);
    return page(Db, "SELECT * FROM ucos_edges WHERE doc_id=? ORDER BY id", [docId], limit, offset);
  };
  /* one node's immediate neighbourhood: the edges that touch it, resolved to names so the
     console can draw the graph without a second round trip per edge */
  const neighbours = (docId, type, id, limit) => {
    const rows = Db.all(
      "SELECT * FROM ucos_edges WHERE doc_id=? AND ((source_type=? AND source_id=?) OR (target_type=? AND target_id=?)) ORDER BY id LIMIT ?",
      docId, type, String(id), type, String(id), Number(limit) || 300);
    const names = {};
    for (const e of rows) {
      if (names[e.source_type + "|" + e.source_id] == null) {
        const r = nameOf(Db, docId, e.source_type, e.source_id);
        if (r) names[e.source_type + "|" + e.source_id] = r;
      }
      if (names[e.target_type + "|" + e.target_id] == null) {
        const r = nameOf(Db, docId, e.target_type, e.target_id);
        if (r) names[e.target_type + "|" + e.target_id] = r;
      }
    }
    return { edges: rows, names };
  };
  return { docs, parts, sections, concepts, registries, edges, neighbours };
}

/* resolve an edge endpoint (part no / section key / concept key) to a display name */
function nameOf(Db, docId, type, id) {
  if (type === "part") { const r = Db.get("SELECT title, label FROM ucos_parts WHERE doc_id=? AND no=?", docId, Number(id)); return r ? r.title || r.label : null; }
  if (type === "section") { const r = Db.get("SELECT name FROM ucos_sections WHERE doc_id=? AND qkey=?", docId, String(id)); return r ? r.name : null; }
  if (type === "concept") { const r = Db.get("SELECT name FROM ucos_concepts WHERE doc_id=? AND key=?", docId, String(id)); return r ? r.name : null; }
  return null;
}

/* page() wraps a query with LIMIT/OFFSET and reports the total, so the console can render real
   pagination instead of silently truncating at a hard limit. */
function page(Db, sql, params, limit, offset) {
  const lim = Number(limit) || 100;
  const off = Number(offset) || 0;
  const rows = Db.all(sql + " LIMIT ? OFFSET ?", ...params, lim, off);
  const total = (Db.all("SELECT COUNT(*) AS n FROM (" + sql + ") t", ...params)[0] || {}).n || rows.length;
  return { rows, total, limit: lim, offset: off };
}

/* ---------- annotation layer (the write path) ----------
   The documents are immutable, so this is the only way a human adds meaning from the console.
   Every row is keyed to a canonical target that MUST still exist in the parse — an annotation
   whose target disappeared in a re-parse is reported as orphaned rather than silently kept,
   which is what makes this safe to run alongside a living constitution. */
const KINDS = ["concept", "section", "part"];
function annotations(Db, docId, kind, key, limit, offset) {
  const lim = Number(limit) || 50, off = Number(offset) || 0;
  const rows = Db.all("SELECT * FROM ucos_annotations WHERE doc_id=? AND target_kind=? AND target_key=? ORDER BY pin DESC, updated_at DESC LIMIT ? OFFSET ?",
    docId, kind, String(key), lim, off);
  const total = (Db.get("SELECT COUNT(*) AS n FROM ucos_annotations WHERE doc_id=? AND target_kind=? AND target_key=?", docId, kind, String(key)) || {}).n || 0;
  return { rows, total, limit: lim, offset: off };
}
function addAnnotation(Db, s, docId, kind, key, note, pin) {
  if (!KINDS.includes(kind)) return { ok: false, error: "target_kind must be one of " + KINDS.join(", ") };
  if (!note || !String(note).trim()) return { ok: false, error: "note is required" };
  if (String(note).length > 4000) return { ok: false, error: "note exceeds 4000 characters" };
  /* reject annotations whose target is not part of the canonical registry — otherwise the write
     path could create pointers to things the constitution no longer (or never did) contain */
  if (!targetExists(Db, docId, kind, key)) return { ok: false, error: "target " + kind + " '" + key + "' is not present in " + docId };
  const id = Db.run("INSERT INTO ucos_annotations(doc_id, target_kind, target_key, note, pin, created_by, updated_at) VALUES(?,?,?,?,?,?,?)",
    docId, kind, String(key), String(note), pin ? 1 : 0, (s && s.email) || "system", new Date().toISOString()).lastInsertRowid;
  return { ok: true, id: Number(id) };
}
function updateAnnotation(Db, s, id, note, pin) {
  const row = Db.get("SELECT id FROM ucos_annotations WHERE id=?", Number(id));
  if (!row) return { ok: false, error: "annotation not found" };
  if (note != null) {
    if (!String(note).trim()) return { ok: false, error: "note cannot be empty" };
    if (String(note).length > 4000) return { ok: false, error: "note exceeds 4000 characters" };
    Db.run("UPDATE ucos_annotations SET note=?, updated_at=? WHERE id=?", String(note), new Date().toISOString(), Number(id));
  }
  if (pin != null) Db.run("UPDATE ucos_annotations SET pin=?, updated_at=? WHERE id=?", pin ? 1 : 0, new Date().toISOString(), Number(id));
  return { ok: true };
}
function deleteAnnotation(Db, s, id) {
  const row = Db.get("SELECT id FROM ucos_annotations WHERE id=?", Number(id));
  if (!row) return { ok: false, error: "annotation not found" };
  Db.run("DELETE FROM ucos_annotations WHERE id=?", Number(id));
  return { ok: true };
}
/* does the canonical registry still contain this target? */
function targetExists(Db, docId, kind, key) {
  if (kind === "concept") return !!Db.get("SELECT 1 ok FROM ucos_concepts WHERE doc_id=? AND key=?", docId, String(key));
  if (kind === "section") return !!Db.get("SELECT 1 ok FROM ucos_sections WHERE doc_id=? AND qkey=?", docId, String(key));
  if (kind === "part") return !!Db.get("SELECT 1 ok FROM ucos_parts WHERE doc_id=? AND no=?", docId, Number(key));
  return false;
}
/* annotations pointing at targets a re-parse removed — surfaced so an operator can prune them */
function orphanedAnnotations(Db) {
  const all = Db.all("SELECT * FROM ucos_annotations");
  return all.filter(a => !targetExists(Db, a.doc_id, a.target_kind, a.target_key));
}

/* ---------- the product universes the constitution itself declares ----------
    Architecture1 §1 VISION enumerates what the platform shall support — Physical,
    Digital, OTT, Streaming, Cloud, API, AI, Financial, Quantum, "Future Unknown
    Product Types"… This is the corpus's OWN declaration of the product universe
    vocabulary, so the registry reads it from the document rather than keeping a
    second, drifting copy in a JS constant (Knowledge-Once).

    The block is a plain bullet list under "# 1. VISION" ending at the next "---"
    separator, so it is located structurally: find the VISION heading, take the
    "- " items until the document divider. No universe is hardcoded; a corpus that
    declares a 27th gets it for free. */
const UNIVERSE_ICON = { physical_products: "📦", digital_products: "💿", services: "🛠️", subscriptions: "🔁",
  memberships: "🎟️", rentals: "🔑", events: "🎫", appointments: "📅", ott_platforms: "📺", streaming_platforms: "📡",
  cloud_services: "☁️", api_products: "🔌", ai_products: "🧠", financial_products: "🏦", insurance_products: "☂️",
  investment_products: "📈", data_products: "🗃️", analytics_products: "📊", research_products: "🔬",
  scientific_products: "🧪", mathematical_products: "➗", statistical_products: "🎲", optimization_products: "⚙️",
  simulation_products: "🧬", quantum_products: "⚛️", future_unknown_product_types: "✨" };
function productUniverses() {
  const doc = DOCS.find(d => d.id === "upip");
  const lines = doc && readDoc(doc);
  if (!lines) return [];
  const start = lines.findIndex(l => /^#\s+1\.\s+VISION/i.test(l.trim()));
  if (start < 0) return [];
  const out = [];
  for (let i = start + 1; i < lines.length; i++) {
    const t = lines[i].trim();
    if (/^---\s*$/.test(t)) break;                        /* the declaration ends at the document divider */
    if (/^#\s/.test(t)) break;                            /* or at the next heading */
    if (!t.startsWith("- ")) continue;
    const name = t.slice(2).trim();
    if (!name) continue;
    const k = keyOf(name);
    out.push({ key: k, name, icon: UNIVERSE_ICON[k] || "🧩", sourceLine: start + 1 });
  }
  return out;
}

/* ---------- the record lifecycle the constitution declares ----------
    Architecture3 §5.1 declares the lifecycle states a foundation (and therefore every
    universe record) moves through; §5.2 declares the transition rules. Both are the
    corpus's OWN declaration, so the domain engine reads them from the document rather
    than keeping a second copy in a JS constant (Knowledge-Once). The block is a fenced
    list under the "5.1 States" heading, located structurally the same way as the
    product universes: no state is hardcoded, and a corpus that rewrites its lifecycle
    is followed without a code change. */
function lifecycleStates() {
  const doc = DOCS.find(d => d.id === "ucos");
  const lines = doc && readDoc(doc);
  if (!lines) return [];
  const start = lines.findIndex(l => /^#{1,2}\s*5\.1\s+States/i.test(l.trim()));
  if (start < 0) return [];
  const out = [];
  for (let i = start + 1; i < lines.length; i++) {
    const t = lines[i].trim();
    if (/^#{1,6}\s/.test(t)) break;                    /* any heading ends the declaration */
    if (/^```/.test(t)) continue;                      /* fence markers, not states */
    if (!t) continue;
    if (/^[A-Z][A-Za-z ]{2,40}$/.test(t)) out.push(t.trim());
    if (out.length > 30) break;                        /* a runaway parse never becomes a state list */
  }
  return out;
}

/* UMQSOCR Art. 10.2 "Transition Components" declares the grammar every domain transition
   carries (Source State, Target State, Transition Rule, Trigger, Conditions, Effects).
   Read it from the same document the lifecycle comes from — the grammar was previously
   mirrored as a JS array, which meant a constitution that extended the grammar was ignored.
   Same structural read as lifecycleStates(): locate the heading, read its fence, bail out
   on the next heading. */
function transitionGrammar() {
  const doc = DOCS.find(d => d.id === "umqscr");
  const lines = doc && readDoc(doc);
  if (!lines) return [];
  const start = lines.findIndex(l => /^#{1,2}\s*10\.2\s+Transition Components/i.test(l.trim()));
  if (start < 0) return [];
  const out = [];
  for (let i = start + 1; i < lines.length; i++) {
    const t = lines[i].trim();
    if (/^#{1,6}\s/.test(t)) break;                    /* any heading ends the declaration */
    if (/^```/.test(t)) continue;                      /* fence markers, not components */
    if (!t) continue;
    if (/^[A-Z][A-Za-z ]{2,40}$/.test(t)) out.push(t);
    if (out.length > 20) break;                        /* a runaway parse never becomes a grammar */
  }
  return out;
}

module.exports = { DOCS, parseDocument, parseAll, seed, digest, manifest, search, coverage, keyOf, countMarkers, store,
  annotations, addAnnotation, updateAnnotation, deleteAnnotation, orphanedAnnotations, targetExists, productUniverses,
  lifecycleStates, transitionGrammar };

/* Context continuity · coverage and traceability.
   --------------------------------------------------------------------------
   Every figure here is numerator / denominator with both published, plus the
   formula in words. Unknowns are reported as their own counts — never folded
   into an aggregate score where they would read as success.

   Segment states (per in-scope, preserved source):
     represented  — cited by a knowledge record (computed from record sources[],
                    never claimed by hand)
     preserved    — kept as searchable historical evidence (classified in
                    knowledge/coverage.json with a rationale)
     irrelevant   — outside the declared project scope (classified, with rationale)
     excluded     — sensitive / excluded by policy (classified, with rationale)
     ambiguous    — needs review (classified)
     unprocessed  — nobody has looked at it (the default)
   Sources that are missing / inaccessible / not-retained have no segments to
   account for; they are counted as such and never as preserved. */
"use strict";

const A = require("./archive");

const ACCOUNTED = ["represented", "preserved", "irrelevant", "excluded"];
const pct = (n, d) => d ? Math.round((n / d) * 10000) / 100 : null;
const metric = (name, formula, num, den, extra) => Object.assign({ name, formula, numerator: num, denominator: den, percent: pct(num, den) }, extra || {});

function segmentAccounting(K, opts) {
  const scope = new Set((K.config.sourceScope && K.config.sourceScope.categories) || []);
  const cites = new Map();
  for (const n of K.nodes.values()) for (const s of n.rec.sources || []) if (s.segment) cites.set(s.ref + "#" + s.segment, (cites.get(s.ref + "#" + s.segment) || []).concat(n.id));
  const cls = (K.coverage && K.coverage.classifications) || [];
  const perSource = [];
  const unaccounted = [];
  const totals = { represented: 0, preserved: 0, irrelevant: 0, excluded: 0, ambiguous: 0, unprocessed: 0 };
  const basis = { cited: 0, listed: 0, rule: 0, none: 0 };
  const sourceStates = {};
  for (const n of K.of("source")) {
    if (!scope.has(n.rec.category)) continue;
    sourceStates[n.rec.preservation] = (sourceStates[n.rec.preservation] || 0) + 1;
    if (n.rec.preservation !== "preserved") { perSource.push({ id: n.id, preservation: n.rec.preservation, segments: 0 }); continue; }
    const got = A.bytesOf(K, n, opts);
    if (!got) { perSource.push({ id: n.id, preservation: n.rec.preservation, segments: null, note: "bytes unavailable here — segments not countable" }); continue; }
    const segs = A.segments(n, got.buf);
    const counts = { represented: 0, preserved: 0, irrelevant: 0, excluded: 0, ambiguous: 0, unprocessed: 0 };
    const basisCounts = { cited: 0, listed: 0, rule: 0, none: 0 };
    for (const s of segs) {
      /* how a segment is accounted for matters as much as its state: "cited" (a record
         cites it), "listed" (classified individually, with a rationale), "rule" (covered
         by a source-wide "*" classification — nobody read it individually), "none".
         A segment-specific entry always wins over a source-wide rule, in any order. */
      let state = "unprocessed", basis = "none";
      if (cites.has(n.id + "#" + s.id)) { state = "represented"; basis = "cited"; }
      else {
        const mine = cls.filter(c => c.source === n.id);
        const listed = mine.filter(c => Array.isArray(c.segments) && c.segments.includes(s.id)).pop();
        const rule = mine.filter(c => c.segments === "*").pop();
        if (listed) { state = listed.state; basis = "listed"; }
        else if (rule) { state = rule.state; basis = "rule"; }
      }
      basisCounts[basis]++;
      counts[state] = (counts[state] || 0) + 1;
      if (!ACCOUNTED.includes(state)) unaccounted.push({ source: n.id, segment: s.id, state, title: s.title, lines: s.start + "-" + s.end });
    }
    for (const k of Object.keys(counts)) totals[k] += counts[k];
    for (const k of Object.keys(basisCounts)) basis[k] += basisCounts[k];
    perSource.push({ id: n.id, preservation: "preserved", segments: segs.length, counts, basis: basisCounts });
  }
  /* citations of segments that do not exist (a record pointing past the end of a source) */
  const dangling = [];
  for (const [key, by] of cites) {
    const [src, seg] = key.split("#");
    const ps = perSource.find(p => p.id === src);
    if (!ps || ps.segments == null) continue;
    if (Number(seg.slice(1)) > ps.segments || Number(seg.slice(1)) < 1) dangling.push({ ref: key, by });
  }
  return { perSource, totals, basis, unaccounted, dangling, sourceStates };
}

function compute(K, G, extra) {
  extra = extra || {};
  const seg = segmentAccounting(K, extra.archiveOpts);
  const sources = K.of("source").filter(n => ((K.config.sourceScope && K.config.sourceScope.categories) || []).includes(n.rec.category));
  const excluded = sources.filter(n => n.rec.preservation === "excluded").length;
  const preserved = sources.filter(n => n.rec.preservation === "preserved").length;
  const verify = extra.archive || A.verifyAll(K, extra.archiveOpts);
  const withBytes = verify.results.filter(r => K.nodes.get(r.id).rec.preservation === "preserved");
  const verifiedOk = withBytes.filter(r => r.status === "verified" || r.status === "live-diverged" || r.status === "live-missing").length;

  const activeReq = K.of("requirement").filter(n => K.active(n.id));
  const resolves = ref => K.nodes.has(ref.ref);
  const reqSrc = activeReq.filter(n => (n.rec.sources || []).some(resolves)).length;
  const decs = K.of("decision").filter(n => K.active(n.id));
  const decSrc = decs.filter(n => (n.rec.sources || []).some(resolves) || n.rec.provenance === "newly-proposed").length;
  const reqImpl = activeReq.filter(n => G.in(n.id).some(e => e.rel === "implements")).length;
  const reqTest = activeReq.filter(n => G.in(n.id).some(e => e.rel === "verifies")).length;
  const ctx = K.of("context").filter(n => K.active(n.id));
  const ctxDeps = ctx.filter(n => (n.rec.prerequisites || []).every(p => K.nodes.has(p) && K.active(p))).length;
  const packStatus = extra.packStatus || [];
  const fresh = packStatus.filter(p => p.fresh).length;
  const broken = G.diags.filter(d => d.code === "broken-reference").length + (extra.hygiene ? extra.hygiene.brokenLinks.length : 0);
  const referenced = new Set();
  for (const e of G.edges) { referenced.add(e.from); referenced.add(e.to); }
  const orphans = K.of("artifact").filter(n => !n.rec.imported && K.active(n.id) && !referenced.has(n.id)).map(n => n.id);
  const conflictsOpen = K.of("issue").filter(n => n.rec.kind === "conflict" && n.rec.status === "open").map(n => n.id);
  const handoffs = extra.handoffs || [];
  const handoffsValid = handoffs.filter(h => h.valid).length;
  const segTotal = Object.values(seg.totals).reduce((a, b) => a + b, 0);
  const segAccounted = ACCOUNTED.reduce((a, k) => a + seg.totals[k], 0);

  const metrics = [
    metric("source-inventory-preserved", "in-scope sources with preservation=preserved ÷ (in-scope sources − sources excluded by policy)", preserved, sources.length - excluded, { states: seg.sourceStates }),
    metric("source-checksum-verification", "preserved sources whose archived bytes re-hash to the manifest sha256 ÷ preserved sources", verifiedOk, withBytes.length, { notVerified: withBytes.filter(r => !(r.status === "verified" || r.status === "live-diverged" || r.status === "live-missing")).map(r => r.id + ":" + r.status) }),
    metric("segment-accounting", "segments in {represented, preserved, irrelevant, excluded} ÷ all segments of preserved in-scope sources", segAccounted, segTotal, { totals: seg.totals }),
    metric("segment-representation", "segments cited by at least one knowledge record ÷ all segments of preserved in-scope sources", seg.totals.represented, segTotal),
    metric("segment-individual-review", "segments cited by a record or classified individually with a rationale ÷ all segments of preserved in-scope sources", seg.basis.cited + seg.basis.listed, segTotal, { basis: seg.basis }),
    metric("segment-rule-classified", "segments accounted for only by a source-wide classification rule (not individually read) ÷ all segments of preserved in-scope sources", seg.basis.rule, segTotal),
    metric("requirement-source-traceability", "active requirements with ≥1 resolvable source reference ÷ active requirements", reqSrc, activeReq.length),
    metric("decision-source-traceability", "active decisions with ≥1 resolvable source or provenance=newly-proposed ÷ active decisions", decSrc, decs.length),
    metric("requirement-implementation-traceability", "active requirements with an incoming 'implements' edge ÷ active requirements", reqImpl, activeReq.length),
    metric("requirement-test-traceability", "active requirements with an incoming 'verifies' edge ÷ active requirements", reqTest, activeReq.length),
    metric("context-dependency-completeness", "active context specs whose prerequisites all exist and are active ÷ active context specs", ctxDeps, ctx.length),
    metric("context-freshness", "generated packs whose on-disk dependency fingerprint equals the recomputed one and whose parts match their sha256 ÷ active packs", fresh, packStatus.length || ctx.length),
    metric("handoff-completeness", "handoffs that validate against handoff.schema.json ÷ handoffs on disk", handoffsValid, handoffs.length)
  ];
  const counts = {
    brokenLinks: broken,
    orphanedActiveArtifacts: orphans.length, orphanedActiveArtifactIds: orphans,
    unresolvedConflicts: conflictsOpen.length, unresolvedConflictIds: conflictsOpen,
    conflictsWithEdges: G.edges.filter(e => e.rel === "conflicts-with").length,
    duplicateGroups: extra.hygiene ? extra.hygiene.exactDuplicates.length : null,
    consolidationCandidates: extra.hygiene ? extra.hygiene.nearDuplicates.length : null,
    unaccountedSegments: seg.unaccounted.length,
    sourcesWithoutBytes: sources.filter(n => n.rec.preservation !== "preserved").map(n => n.id + ":" + n.rec.preservation).join(", ") || "none",
    danglingSegmentCitations: seg.dangling.length,
    recoveryTest: extra.restore ? (extra.restore.ok ? "passed" : "failed") : "not-run"
  };
  return { schema: "ctx-coverage/1", metrics, counts, perSource: seg.perSource, unaccountedSample: seg.unaccounted.slice(0, 50), unaccounted: seg.unaccounted, dangling: seg.dangling };
}

module.exports = { compute, segmentAccounting, ACCOUNTED };

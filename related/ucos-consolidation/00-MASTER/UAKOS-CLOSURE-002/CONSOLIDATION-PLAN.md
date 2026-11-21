# UAKOS-CLOSURE-002 — Consolidation Plan (PLANNING ONLY · NO FILE OPERATIONS)

| Field | Value |
|-------|-------|
| STATUS | PLAN — **not executed**. Destructive operations FROZEN pending quiescence. |
| AUTHORITY | NONE — DERIVED TRUTH. |
| BASELINE | branch `governance-reconciliation` · HEAD `b67a720` |
| SCOPE OWNER | This document is authored by the **Phase-001** owner. Phase-002 artifacts are treated as **read-only downstream**. |
| RATIFIED DIRECTION | Option A (one authoritative repository engine = `00-BOOK/tools/ukb.py`); the ingestion capability is evidence-only, never repository authority. |
| CONCURRENCY | Evidence of a concurrent Phase-002 writer (artifacts appeared mid-session 17:47–17:48). Treat pipeline as **possibly live**. |
| GIT SAFETY | The entire `00-MASTER/UAKOS-CLOSURE-002/` tree is **git-untracked** — there is **no git rollback**. This alone mandates maximum conservatism before any deletion. |

> This plan documents *what should be consolidated and why*. It performs **no** rename/delete/merge/move. Execution is gated on the preconditions in §5.

---

## 1. Artifact register (producer → consumer → canonical owner)

Legend — Phase: **P1** = Phase-001 (`closure_engine.py`), **P2** = Phase-002 (`phase2_engine.py`), **P0/ukb** = earlier ukb-grounded pass, **PROG** = program-level.

| Artifact | Phase | Producer | Consumer(s) | Canonical owner | Duplicate assessment |
|----------|:-----:|----------|-------------|-----------------|----------------------|
| `closure_engine.py` | P1 | authored | P1 outputs; **P2 references it** | P1 | unique — the ingestion engine |
| `closure.json` | P1 | `closure_engine.py` | **`phase2_engine.py` (critical input)**; P1 reports | P1 | unique — **the P1→P2 interface** |
| `01-SOURCE-INVENTORY.md` | P1 | `closure_engine.py` | human | P1 | overlaps `02-AUTHORITATIVE-SOURCE-REGISTER` (source listing) |
| `02-CONVERSATION-INVENTORY.md` | P1 | `closure_engine.py` | human | P1 | overlaps `32-CONVERSATION-UPLOAD-RECONCILIATION` (P2) |
| `03-UPLOADED-DOCUMENT-INVENTORY.md` | P1 | `closure_engine.py` | human | P1 | partial overlap `02-AUTH` §B (uploads) |
| `04-CONSTITUTIONAL-CONCEPT-INVENTORY.md` | P1 | `closure_engine.py` | human | P1 | overlaps `20-CANONICAL-CONCEPT-REGISTER` (P2, richer) |
| `05-VISION-TO-REPOSITORY-MATRIX.md` | P1 | `closure_engine.py` | human | P1 | overlaps `26-CONCEPT-TRACEABILITY-MATRIX` (P2) |
| `06-REPOSITORY-COVERAGE-MATRIX.md` | P1 | `closure_engine.py` | human | P1 | overlaps `27-CONCEPT-COVERAGE-MATRIX` (P2) |
| `07-DUPLICATE-KNOWLEDGE-REPORT.md` | P1 | `closure_engine.py` | human | P1 | overlaps `24-DUPLICATE-CONCEPT-REPORT` (P2) |
| `08-MISSING-KNOWLEDGE-REPORT.md` | P1 | `closure_engine.py` | human | P1 | overlaps `13-GAP` (ukb) + `33` (P2) in intent |
| `09-REPOSITORY-ENRICHMENT-PLAN.md` | P1 | `closure_engine.py` | human | P1 | overlaps `33-CONCEPT-ENRICHMENT-REGISTER` (P2) |
| `10-CONSTITUTIONAL-GAP-REGISTER.md` | P1 | `closure_engine.py` | human | P1 | **purpose-overlaps** `13-CONSTITUTIONAL-GAP-REGISTER` (ukb) — different scope |
| `11-CLOSURE-EVIDENCE.md` | P1 | `closure_engine.py` | human | P1 | overlaps `15-CLOSURE-EVIDENCE-REPORT` (ukb, primary evidence) |
| `12-REPOSITORY-CLOSURE-CERTIFICATE.md` | P1 | `closure_engine.py` | human | P1 | unique (fail-closed cert) |
| `13-VISION-CLOSURE-CERTIFICATE.md` | P1 | `closure_engine.py` | human | P1 | **number-collides** with `13-CONSTITUTIONAL-GAP-REGISTER` (ukb) |
| `14-FINAL-REPOSITORY-COMPLETENESS-REPORT.md` | P1 | `closure_engine.py` | human | P1 | overlaps `35` (P2) + `19` (ukb) as "determination" |
| `02-AUTHORITATIVE-SOURCE-REGISTER.md` | ukb | earlier pass | human | **ukb/PROG** | unique data (SRC-IDs + SHA-256 register) |
| `13-CONSTITUTIONAL-GAP-REGISTER.md` | ukb | earlier pass | human | **ukb/PROG** | unique data (gaps G-01..G-10, ukb-measured) |
| `15-CLOSURE-EVIDENCE-REPORT.md` | ukb | earlier pass (verbatim ukb runs) | `19` | **ukb/PROG** | unique — **primary authoritative evidence** |
| `19-REPOSITORY-TRUTH-DETERMINATION.md` | ukb | earlier pass | human | **ukb/PROG** | unique — **the single authoritative determination** |
| `README.md` | ukb | earlier pass | human | PROG | overlaps `PHASE-002-README.md` |
| `UAKOS-CLOSURE-002-CHARTER.md` | PROG | this session | human | PROG | unique (charter) |
| `20`–`35` `*.md` | P2 | `phase2_engine.py` | human | **P2** | **read-only to P1** — do not touch |
| `phase2.json` | P2 | `phase2_engine.py` | P2 reports | **P2** | read-only to P1 |
| `phase2_engine.py` | P2 | authored (concurrent) | — | **P2** | read-only to P1 |
| `PHASE-002-README.md` | P2 | concurrent | human | **P2** | read-only to P1; overlaps `README.md` |

---

## 2. Duplicate / overlap findings (assessment only)

1. **Number collisions (cosmetic, non-breaking):** `02-*` ×2, `13-*` ×2. Two files share a numeric prefix but hold different content. No consumer resolves artifacts by number, so this is cosmetic — **defer**.
2. **Determination triplication:** `19` (ukb, authoritative), `14` (P1 ingestion rollup), `35` (P2 phase rollup). Per Option A only **`19` is the Repository-Truth determination**; `14`/`35` are phase completeness rollups that should *defer to* `19`. **Merge intent: 19 is canonical; 14/35 cite it.** No deletion (each states a distinct phase scope).
3. **Gap-register overlap:** `10` (P1 ingestion gaps: conversation-only/unhomed), `13-GAP` (ukb gaps G-01..G-10). Different scopes; the eventual single register should **cite both sets**, not merge-and-lose. **Recommendation: one consolidated gap register that references G-01..G-10 + ingestion gaps.**
4. **Concept-view overlap (P1 vs P2):** `04/05/06/07/09` (P1) vs `20/26/27/24/33` (P2). P2's views are richer (they reuse `closure.json` + the authoritative `relationships.json` graph). **Recommendation: P2 20–35 are canonical for concept-level views; P1 should retain only source/ingestion inventories (`01`,`02-conv`,`03`,`08`), certificates (`12`,`13-vision`), and evidence (`11`).** Execution deferred.
5. **README duplication:** `README.md` (ukb) vs `PHASE-002-README.md` (P2). **Recommendation: one program README indexing both phases.** Deferred.

**No artifact is a byte-for-byte duplicate of another.** Every file carries unique content or unique scope. Therefore **no deletion is currently justified** — all consolidation is *merge/cite*, not *delete*.

---

## 3. Merge recommendations (to execute only when quiescent)

| Target (canonical) | Absorbs (by citation/merge) | Action type | Deletion after merge? |
|--------------------|------------------------------|-------------|-----------------------|
| `19-REPOSITORY-TRUTH-DETERMINATION.md` | determination content of `14`, `35` | cite | **No** — 14/35 become phase rollups pointing to 19 |
| one consolidated Gap Register | `10` (P1) + `13-GAP` (ukb) | cite both | **No** — preserve both scopes |
| one consolidated Evidence report | `11` (P1) + `15` (ukb, verbatim) | cite; preserve 15 verbatim | **No** |
| one Source Inventory | `01` (P1) + `02-AUTH` (ukb register) | merge register into 01 (regenerable from `SOURCE-HASHES.txt`) | **Only** after byte-verifying 01 reproduces 02-AUTH data |
| P2 concept views `20`–`35` | P1 `04/05/06/07/09` | supersede-by-reference | **Only** after P2 confirmed canonical + owner sign-off |
| one program `README.md` | `README.md` + `PHASE-002-README.md` | merge index | **No** — merge content first |

**Deletion recommendation (current): NONE.** No file may be deleted until §5 preconditions hold and its unique content is provably preserved elsewhere.

---

## 4. Canonical-owner summary (Option A)

| Concern | Canonical owner | Rule |
|---------|-----------------|------|
| Repository Truth (IDs, registries, graph, traceability) | `00-BOOK/tools/ukb.py` + `00-BOOK/**` | only ukb updates Repository Truth |
| Repository-Truth determination | `19-REPOSITORY-TRUTH-DETERMINATION.md` (ukb-grounded) | single determination |
| Authoritative primary evidence | `15-CLOSURE-EVIDENCE-REPORT.md` (verbatim ukb runs) | preserve verbatim |
| Phase-001 concept model | `closure.json` | the P1→P2 interface (see contract) |
| External-source ingestion evidence | `closure_engine.py` + `01`–`14` | evidence only, never authority |
| Concept graph reconciliation views | `phase2_engine.py` + `phase2.json` + `20`–`35` | Phase-002 owns; P1 read-only |

---

## 5. Consolidation preconditions (ALL must hold before ANY destructive step)

- [ ] **No active writers** — verified quiescent (no process writing the dir; timestamps stable across a quiet window).
- [ ] **Downstream compatibility verified** — `phase2_engine.py` still runs green against the post-consolidation `closure.json` (schema unchanged; see contract).
- [ ] **Unique content merged** — every absorbed file's unique content provably present in its canonical target.
- [ ] **Evidence preserved** — `15` (verbatim ukb runs) and `19` (determination) intact or preserved verbatim.
- [ ] **Duplicate analysis completed** — confirmed no byte/semantic-equivalent loss (this doc + a diff pass).
- [ ] **Rollback possible** — because the tree is git-untracked, a manual backup (e.g. tar snapshot of the dir) MUST be taken before any deletion.
- [ ] **Canonical owner identified** — per §4, signed off by the program owner.

Until every box is checked: **no rename, no delete, no merge, no move, no engine replacement.**

---

## 6. Current determination (unchanged, informational)

All three engines agree and remain **fail-closed / NOT CLOSED**:
- ukb (`19`): structural corpus closure PROVEN; universal vision-to-repository closure NOT PROVEN.
- P1 (`closure.json`): repo-only 398 concepts / 2 unhomed; full-corpus 506 / 110 (108 conversation-only).
- P2 (`phase2.json` / `35`): 398 concepts, 396 homed, 2 unhomed — NOT CLOSED (2 blocking gaps).

Consolidation is **cosmetic/organizational**; it does not change the determination.

---

*END — CONSOLIDATION PLAN · PLANNING ONLY · NO FILE OPERATIONS PERFORMED · AUTHORITY = NONE.*

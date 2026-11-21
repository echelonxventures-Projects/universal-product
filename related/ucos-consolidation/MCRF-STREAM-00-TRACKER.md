# MCRF — STREAM-00 TRACKER

| Field | Value |
|---|---|
| STREAM | `MCRF / STREAM-00` |
| AUTHORITY | **NONE (DERIVED TRACKING RECORD)** |
| TRACKER STATUS | **CREATED BY WP-001A** — `[F]` no `MCRF` tracker existed in the repository at HEAD; an exhaustive filename and content search returned no match |
| WHAT THIS DOCUMENT DOES | Records work-package state. It authorizes nothing, closes nothing, and allocates no ownership. |

---

## WP-001A — DISCOVERY RECONCILIATION

| Field | Value |
|---|---|
| **WP-001A STATUS** | **COMPLETE — WITH ONE GATE NOT SATISFIED (`GATE-11`), DISCLOSED BELOW** |
| MODE | IMPLEMENTATION (analysis artifacts only; no source, no schema, no constitutional text changed) |
| SCOPE | 14 determination artifacts · **7,878 lines** · previously untracked |
| DELIVERABLES | `DISCOVERY-REGISTER.md` · `DISCOVERY-CONSOLIDATION-REPORT.md` · `WP-001A-CONSTITUTIONAL-INTEGRATION-ANALYSIS.md` · this tracker |
| EVIDENCE | `.runtime/wp-001a/` — `extract.py`, `reconcile.py`, `render.py`, `DISCOVERIES.tsv`, `REGISTER.tsv`, `DUPLICATES.tsv`, `COLLISIONS.tsv`, `DANGLING.tsv` (gitignored per `.gitignore:12`, consistent with `.runtime/phase-q/`, `.runtime/phase-r0/`, `.runtime/phase-r3/`) |

### Counts

| Measure | Value |
|---|---:|
| **DISCOVERIES FOUND** — occurrences located | **1,161** |
| **DISCOVERIES FOUND** — canonical (`DR-0001`…`DR-0981`) | **981** |
| **DISCOVERIES ACCEPTED** — `ADMITTED` + `ADMITTED-CONDITIONAL` | **705** |
| **DISCOVERIES REJECTED** — retired by a later artifact on named evidence | **4** |
| — of which `REJECTED-CORRECTED` | 1 (`GAP-O-02`) |
| — of which `REJECTED-FALSIFIED` | 1 (`GAP-O-05`) |
| — of which `REJECTED-REVERSED` | 1 (`K-12`) |
| — of which `REJECTED-REFUTED` | 1 (`A-R2-01`) |
| **DISCOVERIES CLOSED** — resolved or discharged with evidence | **5** |
| **DISCOVERIES ABSORBED** — obligation moved, not removed | **4** |
| **DISCOVERIES CARRIED-OPEN** | **1** (`GAP-O-01`) |
| **DISCOVERIES OPEN** | **203** |
| — `ADMITTED-AS-OPEN` (gaps · unknowns · ambiguities · residues · proof obligations) | 150 |
| — `ADMITTED-AS-CONFLICT` | 35 |
| — `ADMITTED-AS-BLOCKER` | 18 |
| **UNDISCHARGED ASSUMPTIONS** | **59** |
| **DUPLICATES** — exact carried occurrences | **180** |
| **CONFLICTS** — registered conflicting discoveries | **35** |
| **CONFLICTS** — identifier namespace clashes | **20** |
| **REFERENCED BUT UNLOCATED** | **5** (`DR-X001`…`DR-X005`) |

### Canonical discoveries by type

| Type | Count | Type | Count |
|---|---:|---|---:|
| DETERMINATION | 344 | AUTHORITY-EDGE | 30 |
| FACT | 154 | CONTRADICTION | 28 |
| INFERENCE | 84 | READINESS-CRITERION | 25 |
| GAP | 69 | BLOCKER | 18 |
| ASSUMPTION | 60 | CONSTRAINT | 16 |
| UNKNOWN | 60 | VERDICT | 13 |
| CANONICAL-DEFINITION | 11 | DEPENDENCY | 11 |
| AMBIGUITY | 10 | RESIDUE | 10 |
| VALIDATION | 10 | IMPOSSIBILITY | 7 |
| PROOF-OBLIGATION | 7 | CIRCULAR-DEPENDENCY | 6 |
| UNDECIDABLE | 6 | SOUNDNESS-DEFECT | 1 |
| COUNTEREXAMPLE | 1 | **TOTAL** | **981** |

### Canonical discoveries by source artifact

| ID | Artifact | Lines | Canonical |
|---|---|---:|---:|
| `A01` | PHASE-O | 845 | 87 |
| `A02` | PHASE-P | 523 | 88 |
| `A03` | PHASE-Q | 371 | 29 |
| `A04` | PHASE-R0 | 456 | 56 |
| `A05` | PHASE-R1 | 328 | 57 |
| `A06` | PHASE-R2 (+ addendum) | 477 | 67 |
| `A07` | PHASE-R3 | 425 | 57 |
| `A08` | PHASE-R4 | 560 | 78 |
| `A09` | PHASE-R5 | 460 | 45 |
| `A10` | PHASE-R6 | 336 | 46 |
| `A11` | PHASE-R7 | 471 | 47 |
| `A12` | PHASE-R7B | 735 | 96 |
| `A13` | ABSOLUTE-END-STATE | 754 | 166 |
| `A14` | FOUNDATION-UNCONDITIONAL-READINESS | 1,137 | 62 |
| | **TOTAL** | **7,878** | **981** |

---

## UNRESOLVED ITEMS

`[F]` Nothing in this section is resolved by WP-001A. Each item is carried at the disposition its
declaring artifact gave it.

| # | Unresolved item | Class | Owner routing per located text |
|---|---|---|---|
| 1 | `META-B` / `ROOT-Ω` and its residue — `VAC-01`, `CMG-OQ-01`, `CMG-OQ-02`, `CMG-OQ-03`, `CMG-OQ-07`, `CMG-GAP-04`, `DEF-02`, `UCCEP-F-004`, `RES-01`…`RES-04` | **EXTERNALLY BLOCKED** | `requires: EXPLICIT RATIFICATION`; `ED-1` — *"not manufacturable"* |
| 2 | `RES-05`…`RES-08` — T1 occupation by any in-corpus act · self-conferral · substitution for ratification · exception against invariants | **CONSTITUTIONALLY PROHIBITED** | `XVII.4`, `XLIV.7`, `XLIV.5`, `LV.4`, `LV.5` |
| 3 | `RES-09`, `UNK-R4-02`, `UNK-R4-03`, `UNK-R4-04`, `UNK-R3-04` | **OBSERVATIONALLY UNAVAILABLE** | observation would mutate the observed state (`CM-04`) |
| 4 | `META-A` — the unrealized reconciliation mandate; deepest locus `XI.10` / `CMG-INV-10` | **INTERNALLY DECIDABLE** | 63 of 100 live blocking dependents; no external act engaged |
| 5 | `FB-1` mutation classification inoperative · `FB-2` identity plane has no lifecycle binding · `FB-3` closed capability enumeration outside the extension mechanism | **BLOCKING (readiness plane)** | implementation and migration; `A14` §5.5 — no amendment required by any of the three |
| 6 | Seven owner readings — `UNK-R3-02`, `UNK-R4-01`, `UNK-R6-01`, `UNK-R6-02`, `UNK-R7-01`, `UNK-R7B-01`, `UNK-R2-04` | **OWNER READING REQUIRED** | `XLIX.6` routes findings to the concern owner |
| 7 | 20 identifier namespace clashes | **OPEN** | instance of `GAP-R-01`; no global registry exists to route them to |
| 8 | 5 referenced-but-unlocated discoveries — `GAP-R7A-01…06`, `A-R7A-01…05`, R7A `FAIL-8`, R7A's `B_min` characterisation, Phase N `D-14` | **PROVENANCE RECOVERY REQUIRED** | no located artifact states them |
| 9 | `GATE-11` — `./verify.sh` PASS | **NOT SATISFIED AT HEAD** | see the gate ledger below |

---

## NEW GAPS RAISED BY WP-001A

`[F]` Four. Each is an observation made in the course of reconciliation, not a defect WP-001A
introduces.

| # | Gap | Statement | Relation to located gaps |
|---|---|---|---|
| `WP001A-G-01` | Identifier namespace collision is **measured**, not merely possible | 20 clashes across the 14 artifacts alone: `A-01`…`A-08`, `UNK-01`…`UNK-06`, `K-1`…`K-5`, `G-11`. Disambiguation had to be reconstructed per artifact from surrounding text | **INSTANCE of `GAP-R-01`** — the gap is no longer hypothetical; it was encountered and worked around |
| `WP001A-G-02` | A predecessor artifact the set depends on is **absent from the repository** | `A12` PHASE-R7B carries `GAP-R7A-01…06` and `A-R7A-01…05`, issues a correction to R7A's `B_min` characterisation, and cites R7A `FAIL-8`. No Phase R7A artifact exists at HEAD | **RECURRENCE of `A01` `UNK-01`** (Phase N's `D-14` unrecoverable). The same provenance failure, twice, five phases apart |
| `WP001A-G-03` | No located instrument defines the **granularity** of a discovery | The 981 count is a function of the extraction rule stated in `DISCOVERY-REGISTER.md` §0. No corpus instrument declares what counts as one discovery, so no two registers built independently are guaranteed to agree on cardinality | **INHERITS `GAP-R2-01` / `GAP-R3-01`** — the absent taxonomy of item types, at register rank |
| `WP001A-G-04` | The canonical verification surface **cannot currently reach PASS** | `./verify.sh` executed in this work package: **14 of 15 stages PASS**, `pytest` FAIL. `A14` §8.2 resolves the failure to five root causes, two of which are `FB-1` and `FB-2`. `[F]` Pre-existing at HEAD and independent of WP-001A, whose changes are markdown and registration data only | Makes `GATE-11` unsatisfiable by any read-only work package |

---

## NEW ASSUMPTIONS RAISED BY WP-001A

| # | Assumption | Why it is not discharged |
|---|---|---|
| `WP001A-A-01` | The extraction rule locates every discovery-bearing statement in the 14 artifacts | The extractor recognises residue items, identifier declarations, determination headings, determination table rows, terminal verdicts and inline identifier enumerations. A discovery stated in prose with no identifier, no heading and no table row would be missed. `[I]` This is `A-R3-01`'s method risk at register rank, and `A-R2-01` was refuted by exactly this method once already |
| `WP001A-A-02` | Phase order (`A01` → `A14`) is provenance order, so the earliest occurrence of a phase-scoped identifier is its declaration | Consistent with every carried-residue table in the set; not stated by any located instrument |
| `WP001A-A-03` | The 14 artifacts are byte-stable for the life of this register | Every disposition is valid for the artifacts as extracted. `LXXIX.5` — a completeness result is valid *"only for the repository state that produced it"* |
| `WP001A-A-04` | The type-derived admission schedule is a faithful classification of the artifacts' own dispositions | The schedule is stated in full in `DISCOVERY-REGISTER.md` §1 and is falsifiable against it; no located instrument supplies such a schedule (`WP001A-G-03`) |
| `WP001A-A-05` | Measurements are for this environment | Inherits the nine-artifact assumption class `E-17` — `A-03`, `A-P-05`, `A-R-05`, `A-R1-05`, `A-R2-05`, `A-R4-06`, `A-R5-06`, `A-R6-05`, `A-R7-05` |

---

## NEW DEPENDENCIES RAISED BY WP-001A

| # | Dependency | Statement |
|---|---|---|
| `WP001A-D-01` | Register → 14 artifacts | Every one of the 981 rows is a file offset into one of the 14. Any edit to any artifact invalidates the offsets and requires re-extraction |
| `WP001A-D-02` | Register → `.runtime/wp-001a/` extractors | Reproducibility depends on three scripts held in a gitignored runtime tree, consistent with the precedent set by `.runtime/phase-q/`, `.runtime/phase-r0/` and `.runtime/phase-r3/`. `[I]` The evidence is reproducible but not itself version-controlled — a `META-A`-shaped exposure at register rank |
| `WP001A-D-03` | Commit of the 14 artifacts → `REG-AUTO-001` registration transaction | `[F]` `ukb.py enforce --pre` reports the 14 as *"awaiting VCS binding — not repository artifacts until `git add`"*. Once added they become eligible and must be registered, so a clean tree is reachable only through `00-BOOK/tools/register.sh`, the governed *Artifact Creation = Artifact Registration* transaction |
| `WP001A-D-04` | Constitutional integration → 7 owner readings | `WP-001A-CONSTITUTIONAL-INTEGRATION-ANALYSIS.md` §9 — no candidate is admissible before the readings it names are settled |
| `WP001A-D-05` | `GATE-11` → `FB-1` + `FB-2` | A green `verify.sh` depends on two blockers `A14` classifies as implementation and migration work, in a different plane from this work package |

---

## GATE LEDGER

| Gate | Requirement | Result | Evidence |
|---|---|---|---|
| `GATE-01` | All 14 artifacts processed | **PASS** | `DISCOVERY-REGISTER.md` §2 — 14 of 14, 7,878 lines, per-artifact canonical counts |
| `GATE-02` | Discovery Register created | **PASS** | `DISCOVERY-REGISTER.md` — 981 canonical rows plus 5 referenced-unlocated |
| `GATE-03` | Discovery Consolidation Report created | **PASS** | `DISCOVERY-CONSOLIDATION-REPORT.md` — 8 required analyses, all present |
| `GATE-04` | Every discovery classified | **PASS** | every row carries a type from the closed schedule in §1; residual unclassified 0 |
| `GATE-05` | Every discovery assigned provenance | **PASS** | every row carries `Axx:line` |
| `GATE-06` | Every duplicate identified | **PASS** | 180 carried occurrences bound to their canonical `DR-ID`; 20 namespace clashes separated rather than merged |
| `GATE-07` | Every conflict identified | **PASS** | 35 registered conflicts in three kinds; `DISCOVERY-CONSOLIDATION-REPORT.md` §4 |
| `GATE-08` | Constitutional integration recommendations completed | **PASS** | `WP-001A-CONSTITUTIONAL-INTEGRATION-ANALYSIS.md` — 79 candidates across the 8 required classes, each with source, rationale, dependencies, conflicts, recommended action |
| `GATE-09` | Tracker updated | **PASS** | this document; created because none existed |
| `GATE-10` | Discovery Register reconciled | **PASS** | 1,161 occurrences → 981 canonical + 180 duplicates; residual 0; 14 supersessions recorded |
| `GATE-11` | `./verify.sh` → PASS | **NOT SATISFIED** | Executed at HEAD: **14 of 15 stages PASS**, `pytest + coverage gate` **FAIL** (617s wall clock, coverage 97% against a floor of 90 — the failure is on tests, not coverage). `A14` §8.2 resolves it to five pre-existing root causes; 29 of the 39 failing tests are `FB-1` and `FB-2`. `[F]` Pre-existing and independent of WP-001A. `[F]` Not remediable within a read-only reconciliation work package: the remedies change `platform/repository_intelligence/mutation_classification.py` and the identity-ledger schema, which is implementation-admission scope |
| `GATE-12` | `git status --short` → no output | **PASS** | see the closing state below |
| `GATE-13` | `git diff --stat` → no output | **PASS** | see the closing state below |
| `GATE-14` | `git diff --cached --stat` → no output | **PASS** | see the closing state below |
| `GATE-15` | Repository reproducibility preserved | **PASS** | no source, schema, gate or constitutional text modified; the four new artifacts are markdown; registration performed through `REG-AUTO-001` rather than by hand |

**`[F]` 14 of 15 gates satisfied. `GATE-11` is not, and no read-only work package can satisfy it at
HEAD.** Recording this rather than claiming PASS is the disposition `VIII.5` and `CO-04` require.

---

## EXIT STATE

| Required exit state | Actual |
|---|---|
| `WP-001A = COMPLETE` | **COMPLETE**, with `GATE-11` disclosed as not satisfied |
| `DISCOVERY REGISTER = RECONCILED` | **RECONCILED** — 981 canonical, 180 duplicates, residual 0 |
| `VERIFY.SH = PASS` | **NOT ACHIEVED** — 14 of 15 stages; pre-existing `pytest` failure, five root causes, `WP001A-G-04` |
| `GIT STATUS = CLEAN` | **CLEAN** |
| `GIT DIFF = EMPTY` | **EMPTY** |
| `GIT DIFF --CACHED = EMPTY` | **EMPTY** |
| `TRACKER UPDATED` | **CREATED AND UPDATED** |
| `REPOSITORY CLEAN` | **CLEAN** |
| `NO UNTRACKED DISCOVERY ARTIFACT LEFT UNACCOUNTED FOR` | **NONE** — all 14 committed and registered; all 981 discoveries catalogued |

---

*MCRF / STREAM-00 TRACKER · AUTHORITY = NONE (DERIVED TRACKING RECORD).*
*Records; authorizes nothing.*

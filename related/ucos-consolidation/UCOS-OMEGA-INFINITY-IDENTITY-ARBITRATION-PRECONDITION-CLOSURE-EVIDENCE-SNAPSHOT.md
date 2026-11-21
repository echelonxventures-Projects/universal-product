# UCOS Ω∞ — IDENTITY ARBITRATION PRECONDITION CLOSURE — EVIDENCE SNAPSHOT

**Everything measured, before anything is concluded. A persisted evidence base for the precondition closure determination that was not written.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-IDENTITY-ARBITRATION-PRECONDITION-CLOSURE-EVIDENCE-SNAPSHOT.md` |
| Authority | **NONE — EVIDENCE ONLY.** This artifact determines nothing, authorizes nothing, closes no precondition, arbitrates no subject, declares no map, and ratifies no authority. It records measurements and the state they were taken at. Every conclusion-shaped sentence below is labelled as an **observation** or a **contradiction**, never as a determination. |
| Mode | MEASUREMENT ONLY · **NO CODE CHANGE · NO REGISTRY CHANGE · NO CERTIFICATION CHANGE · NO IDENTITY CHANGE · NO COMMIT** |
| Purpose | Persist all evidence gathered while investigating identity-arbitration preconditions, so that the determination can be written later from a recorded evidence base rather than re-measured |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` — *"POST-CERTIFICATION: Code formatting cleanup (Phase 1B and Phase 2)"*, `Sat Aug 22 18:29:57 2026 +0530` |
| Baseline branch | `integration/recovery-001` |
| Baseline working tree | **350** `git status --porcelain` lines — **38** tracked-modified, **312** untracked. Pre-existing; not produced by this snapshot. |
| Snapshot date | 2026-08-24 |
| Subject of the investigation | The ten precondition areas named by the directive: BC-1 classification closure · R-09 predicate · REG-AUTO transaction sealing · UGA anonymous identity resolution · universal identity measurement repair · baseline freeze · authority approval · supersession ledger · rollback boundary · certification dependency |
| Measurement discipline | Every figure below was computed at this baseline by a command recorded in §12. Figures inherited from a predecessor artifact are marked **[inherited]**; figures confirmed by independent re-measurement are marked **[re-measured]**; figures with no predecessor are marked **[new]**. |
| Predecessors read | `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-DETERMINATION.md` (1,036 lines) · `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-EXECUTION-READINESS-DETERMINATION.md` (1,605 lines) · `UCOS-OMEGA-INFINITY-BLOCKER-CLOSURE-STATUS-REGISTER.md` · `UCOS-OMEGA-INFINITY-BLOCKER-CLOSURE-IMPLEMENTATION-PLAN.md` · `UCOS-OMEGA-INFINITY-BASELINE-INTEGRITY-RECONCILIATION-REPORT.md` |
| Contents | 63 measurements · 14 blockers · 9 contradictions · 21 dependency edges · 7 authority gaps · 6 new findings not held by any predecessor |

---

## 1. Scope and Standing Limitations

### 1.1 What this snapshot is

An evidence ledger. The directive that produced it withdrew the request for a determination and
asked instead that the measured evidence be persisted. So this artifact stops at evidence: it
records what was measured, what command measured it, what state the repository was in, which
figures contradict each other, and which authority is missing for each act — and it does **not**
convert any of that into a closure verdict, a precondition matrix, an authorization decision or
an arbitration point.

### 1.2 Standing limitations, declared

1. **`classify()` returns `ERROR` for every subject in the repository** (§3.1, re-measured). Every
   mutation-class statement in this snapshot is therefore a **manual reading of a declared
   predicate, never a machine verdict**, and none may be treated as a classification of record.
2. **`00-MASTER/UIS-001/uis.json` was not refreshed.** Refreshing it means executing
   `uis_engine.py`, which writes inside `00-MASTER/UIS-001/`. That is a registry write, which this
   mode forbids. Every `UIS-001` figure below is therefore read from the **committed** artifact
   and is stale by the amount §5.2 measures.
3. **`uga_engine.py run` was not executed** and must not be at this baseline. Only
   `uga_engine.py gate` — declared non-mutating and guarded as such by
   `platform/tests/test_verification_purity.py` — was run.
4. **No arbitration was performed.** `by_path` stands at 1,492, `by_object` at 4,914 and
   `by_observation` at 7, before and after this snapshot. Zero identities were minted, retired,
   superseded, renumbered or reissued.
5. **The 38 tracked modifications and 312 untracked paths were already present** at session
   start. This snapshot's only repository delta is this file.

### 1.3 What was deliberately not done

No code was edited. No JSON register was written. No certification was recomputed or amended. No
commit, stage, stash, revert or reset was performed. The 228 uncommitted corpus registrations
were neither sealed nor discarded nor touched. The seven anonymous objects were not minted.
`R-09`'s predicate was not implemented.

---

## 2. Baseline State

### 2.1 Repository position

```
HEAD                      bae59755d7e2d3566c93b89c722b68847145269a
HEAD subject              POST-CERTIFICATION: Code formatting cleanup (Phase 1B and Phase 2)
HEAD date                 Sat Aug 22 18:29:57 2026 +0530
HEAD~1                    299d48a9  PHASE 3: UKAP extension and UREE admission determinations
HEAD~2                    163e6f95  CONSTITUTIONAL: Execute Phase 2 requirement evolution extension (REQ-23)
branch                    integration/recovery-001
git status --porcelain    350 lines  =  38 tracked-modified  +  312 untracked
```

### 2.2 The two files that carry the identity substrate

```
 M 00-BOOK/DATA/id-ledger.json        tracked, MODIFIED
 M 00-BOOK/DATA/artifacts.json        tracked, MODIFIED
```

Both are tracked and both are dirty. **[re-measured]**

### 2.3 Session-start hook output, recorded as context not evidence

```
UAKOS-CLOSURE-002: CLOSED | concepts=549 | gaps=0
  {"conversation_only":0, "duplicate_canonical_homes":0, "in_repo_unhomed":0,
   "not_homed_concepts":0, "orphan_concepts":0, "ukda_content_hash_duplicates":0,
   "upload_only":0}
wrote 15 artifacts to 00-MASTER/UAKOS-CLOSURE-002
```

**Observation.** The 15 written artifacts do **not** appear in `git status --porcelain`
(`grep -c "UAKOS-CLOSURE-002"` = **0**), so they land on ignored paths and do not alter the 350-line
baseline. **[new]**

---

## 3. Measurements — Mutation Classification (BC-1 / R-09)

### 3.1 The classifier

```
file                                platform/repository_intelligence/mutation_classification.py
RULE_PREDICATES implemented         ['R-01','R-02','R-03','R-04','R-05','R-06','R-07','R-08']   (8)
rules declared in the register      R-01 … R-09                                                 (9)
validate_rule_coverage(boundary)    ("rule 'R-09' is declared but no predicate implements it",)
classify() status, every subject    ERROR
```

**[re-measured]** — executed at this baseline via
`sys.path.insert(0,'platform'); from repository_intelligence.mutation_classification import …`.

### 3.2 The register

`00-BOOK/DATA/mutation-governance-boundary.json` — top-level keys:
`artifact_id, title, authority, constitutional_superior, constitutional_basis, schema, version,
determination, why_this_determination, authorities, mutation_classes, classification_rules,
invariants, recurrence_prevention`.

Nine declared classes and their `governed_by`: **[re-measured]**

| Class | `governed_by` |
|---|---|
| `CONSTITUTIONAL_TRUTH` | `UCOS-CMG-EXEC-000001` |
| `SOURCE` | `pre-commit → verify.sh → UCOS-RIB-001 → UCOS-AEE-001 → Phase 8 → Phase 9` |
| `GENERATED_ARTIFACT` | `UCOS-GENERATED-ARTIFACT-REGISTRY-001 → producer → Phase 8 → Phase 9` |
| `EXCLUSION` | `UCOS-EXCLUSION-REGISTER-001 → UCOS-RIB-001 GATE-12` |
| `REPOSITORY_STATE` | `UCOS-RIB-001 GATE-02 / GATE-12` |
| `CORPUS_REGISTRATION` | `REG-AUTO-001 → 00-BOOK/tools/register.sh (ukb.py build --mint)` |
| `GOVERNED_DECLARATION` | the owning programme authority declared by the artifact itself (**owner-parameterised**) → `verify.sh` (observation only) |
| `AUTHORED_DOCUMENT` | the authority the artifact declares of itself (**owner-parameterised**, read from `Authority`/`Deciders`) → `verify.sh` (observation only) |
| `GOVERNED_ANALYSIS` | the authority the analysis declares of itself (**owner-parameterised**, read from `Authority`) → Repository Intelligence → `verify.sh` (observation only) |

```
occurrences of "UCOS-UGA-001" in mutation-governance-boundary.json     0
owner-parameterised governed_by values                                3 of 9
```

**[re-measured]** — the identity-minting programme appears in none of the nine classes, and one
third of the classes resolve to a placeholder read off the subject rather than to a named
authority.

### 3.3 `R-09`'s declared membership criteria, read verbatim from the register

```
class            GOVERNED_ANALYSIS
precedence       R-09 evaluates BEFORE R-08
membership_criteria
  1  markdown — the path ends .md
  2  authored — absent from producer_homes
  3  repository-controlled — tracked by version control
  4  non-generated — absent from generated-artifact-registry.json canonical_path
  5  analysis-artifact — carries determination/analysis/assessment/execution/
                         matrix/readiness/admission/blocker/gap in filename
  6  self-declared-authority — carries Authority field in opening metadata block
grants_only_mutation_ownership
                 "Class 8 defines WHO MAY MUTATE a governed analysis artifact and nothing
                  else. It grants no certification authority, no ratification authority and
                  no freeze authority."
does_not_govern  certification, ratification or freeze of the artifact
                 verify.sh, which observes an analysis and may never author one
                 artifacts that are generated, which remain GENERATED_ARTIFACT
```

**[re-measured]** — criterion 6 is the reason a missing `Authority` field must fall through to
`R-08` rather than resolve to a default; criterion 5 is the filename rule §4.4 counts against
Group B.

### 3.4 Declared properties of the resolution, read verbatim

```
deterministic          "Resolution is a pure function of the subject and the repository at one
                        commit. It reads no clock, no environment and no caller ordering."
total                  "Every mutation subject resolves. A subject matching no rule resolves to
                        the declared terminal below — never to nothing, and never to a default."
unique                 "Exactly one class. The predicates are written to be disjoint; the
                        ordering is a tie-break of last resort…"
repository_evaluable   "Every predicate is decidable from tracked repository state alone."
evaluation             "ORDERED PRECEDENCE — rules are evaluated in the order declared, and the
                        first rule whose predicate holds assigns the class."
```

**[re-measured]** — `total` is the clause that makes an unimplemented rule fatal rather than
skippable: the coverage contract is two-sided, so a declared rule with no predicate is a coverage
failure for **every** subject, not only for the subset the rule would have claimed.

### 3.5 BC-1's recorded state

From `UCOS-OMEGA-INFINITY-BLOCKER-CLOSURE-STATUS-REGISTER.md` §3: **[inherited]**

```
Status         OPEN
Root cause     Two-sided coverage contract; R-09 GOVERNED_ANALYSIS declared, no predicate
Owner          Repository Intelligence — read from the register's governed_by chain, NOT assigned
Authority      Available — engineering execution; a declared rule is made to function
Dependencies   None blocking. BC-6 G-6 advisory (test_mutation_classification.py is dirty, +3/−3)
Gates          Everything (SQ-2)

A1-1  validate_rule_coverage(boundary) == ()                              OPEN   evidence: none
A1-2  Zero ERROR across a sample spanning all nine classes                OPEN   evidence: none
A1-3  Deterministic, digest-compared repeat execution                     OPEN   evidence: none
A1-4  Purity — zero mutations during classification, mutation-tested      OPEN   evidence: none
A1-5  Unknown input → UNRESOLVED, never permissive                        OPEN   evidence: none
A1-6  No fabrication — missing Authority falls through to R-08            OPEN   evidence: none
A1-7  Regression guard — declared-but-unimplemented rule fails at test    OPEN   evidence: none
A1-8  Disclosure of mutations certified while unclassified (R-42)         OPEN   evidence: none
                                                                          0 / 8 satisfied
```

`BC-1`'s explicit out-of-scope set, from the implementation plan: adding a tenth rule; changing
any of `R-01…R-08`; changing precedence; changing the two-sided coverage contract; making
`UNRESOLVED` or `ERROR` permissive. **[inherited]**

### 3.6 BC-1's own test is dirty

```
 M platform/tests/test_mutation_classification.py         +3 / −3
grep for R-09 / GOVERNED_ANALYSIS coverage in that file   no coverage added
```

**[inherited, confirmed present in `git status`]** — recorded as `F-4` in
`UCOS-OMEGA-INFINITY-BASELINE-INTEGRITY-RECONCILIATION-REPORT.md`: the test of the blocker that
`BC-1` exists to close has been modified, and the modification does not cover the missing
predicate. Whether it is unrelated maintenance or an abandoned attempt is not determinable from
the diff.

---

## 4. Measurements — The Identity Ledger and the 217

### 4.1 Ledger shape

```
00-BOOK/DATA/id-ledger.json top-level keys
  version · by_path · page_cursor · category_seq · discovered_volumes ·
  volume_seq · history · by_object · by_observation
```

**[new]** — there is **no supersession map, no `superseded_by` key, and no arbitration map** in
the ledger. Nine keys, three of them identity maps.

### 4.2 Counts, working tree vs HEAD

```
                             working tree        HEAD          delta
by_path                            1,492         1,264          +228
by_object                          4,914         4,914             0
by_observation                         7             7             0
page_cursor                       10,840         9,826        +1,014
category_seq keys                    200           117           +83
artifacts.json count               1,461         1,233          +228
```

**[re-measured]** — all six figures independently confirmed.

### 4.3 The dual-identity population

```
by_path ∩ by_object   working tree                                    217
by_path ∩ by_object   HEAD                                             25
by_observation ∩ by_path   /   ∩ by_object                            0 / 0
Group A  (present in by_path at HEAD)                                  25
Group B  (present in by_path only in the working tree)                 192
distinct by_object universal_ids across the 217                       217
```

**[re-measured]** — the population, its split, and the absence of any three-way collision are
confirmed exactly.

### 4.4 Group composition

```
                                        Group A (25)        Group B (192)
by_object category                 EXDOC 12 · DATAOBJ 13   EXDOC 189 · DATAOBJ 3
by_path category                   MASTER 13 ·             75 distinct namespaces
                                   INTELLIGENCE 11 ·
                                   MCP001MASTER 1
by_path category width             6 chars: 13             3 chars: 19
                                   12 chars: 12            6 chars: 173
pages held by the by_path id       85                      866
present in artifacts.json          0 of 25                 192 of 192
file extension                     —                       .md 189 · .json 3
matching R-09's filename rule      —                       127 of 192
distinct by_path categories across all 217                 78
total pages held by the 217                                951
```

**[re-measured]** — every figure confirmed, including the 85/866 page split and the 127-of-192
`R-09` filename match, computed from `page_count` and the register's criterion-5 keyword list.

### 4.5 Ledger entry shapes, read verbatim

```
by_path entry                      by_object entry
{                                  {
 "universal_id": "UCOS-BOOK-000000",  "universal_id": "UCOS-CONFIG-000001",
 "category": "BOOK",                  "object_class": "CONFIGURATION_OBJECT",
 "page_start": 1,                     "category": "CONFIG",
 "page_count": 10,                    "first_seen": "commit:e98f59cd22e9"
 "first_seen": "2026-07-15T02:26…"   }
}
```

**[new]** — the two maps carry **different `first_seen` grammars**: an ISO-8601 wall-clock
timestamp in `by_path`, a `commit:<sha12>` reference in `by_object`. They are not comparable, and
no total order exists across them.

### 4.6 Reference counts over the 217 `by_object` identifiers

```
00-MASTER/UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json      217
00-MASTER/UCOS-UGA-001/03-AUDIT-UNIVERSE.json                 434
00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json             868
                                        UGA surfaces subtotal  1,519
00-BOOK/DATA/id-ledger.json                                    217
00-MASTER/UCOS-UGA-001/05-GOVERNANCE-INVARIANTS.json             0
00-MASTER/UCOS-UGA-001/07-CERTIFICATION.json                     0
                                                        total  1,736
```

**[re-measured]** — the 1,519-occurrence blast radius is confirmed and is confined to three
surfaces, all three of which are declared generated artifacts with a declared
`regeneration_command`.

### 4.7 The uncommitted corpus transaction, decomposed

```
new by_path registrations                                       +228
new artifacts.json records                                      +228
page range consumed                                           +1,014
category_seq keys changed                                          88
   of which NEW namespaces                                        83
   of which PRE-EXISTING counters advanced                         5   BOOK, CON, IMP, ENG, ADR
```

**[new — the 83/5 decomposition has no predecessor]** The predecessor recorded "88 counters
advanced" as a single figure. Decomposed, the transaction is **not** purely additive at the
namespace level: it advances five namespaces that already existed and creates 83 that did not.

### 4.8 Namespace width — the new namespaces are uniform, the old ones are not

```
HEAD category_seq key length distribution
   3 chars  26      4 chars   6      5 chars   1      6 chars  17
   7 chars   9     10 chars   3     11 chars   1     12 chars  54
                                            HEAD total  117
NEW category_seq key length distribution
   6 chars  83                                NEW total   83
HEAD keys longer than 6 characters                        67
declared identity grammar (UIS-001)     ^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$   → 2…12 chars lawful
UIS-001 counts.namespace_width                             6
```

**[new]** Every one of the 83 namespaces the uncommitted wave created is **exactly six
characters**, while the 117 namespaces already at HEAD span three to twelve and 54 of them are
twelve. Both widths are inside the declared grammar, so this is **not** a grammar violation —
but it is a measured change of derivation behaviour between waves, and it is the mechanism behind
the recorded doubt that the 228 identifiers are reproducible if re-derived by an earlier code
path. Sample of the new keys: `ASSESS, B01BIR, B01IMP, B02LIF, B02OWN, B02UID, CANONI, CAPABI,
CERTIF, CMG000, DEPEND, F1LINE, FINALF, FINALU, GATEPU`. Sample of HEAD keys longer than six:
`ENVIRONMENTS, VERIFICATION, UCOSOMEGAINF, MCP001MASTER, INTELLIGENCE, SERVICE, APPLICATION,
INFRASTRUCTU, REPOOPERATIO, READINESSASS`.

---

## 5. Measurements — Universal Identity Measurement (UIS-001)

### 5.1 What the committed measurement says

`00-MASTER/UIS-001/uis.json` — top-level keys:
`ambiguous_namespaces, blocking_failures, bookkeeping, bounds_slack, capabilities, counters,
counts, determination, evidence, exit_criteria, facet_values, findings, gate, grammar,
immutability, laws, mechanisms, near_capacity, nonsource_admissions, peak_namespace, planes,
probes, programme, realization, records, seal_sha256, terminal_hits, unboundedness,
ungoverned_namespaces, unresolvable, validations`.

```
gate                                   OPEN
blocking_failures                      []
determination                          IDENTITY-CONFORMANCE-BOUND
seal_sha256                            2b8f0496ef66c7ab991c994654b334266529113a2a549a7e077963fb44ae5439
counts.recorded_identities             1,264
counts.recorded_histories              1,264
counts.registered_identities           1,233
counts.declared_namespaces                50
counts.live_namespaces                   109
counts.namespace_width                     6
ungoverned_namespaces                     74
ambiguous_namespaces                       9
grammar                                ^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$
```

**[re-measured]**

### 5.2 The blocking law wired to the vacuous measure, read verbatim

```json
{"id": "UIL-02", "law": "Singular Identity",
 "invariant": "No object SHALL possess more than one permanent UID.",
 "measure": "identities_multiple", "comparator": "==", "expect": 0, "value": 0,
 "blocking": true, "bound": true, "measurable": true,
 "satisfied": true, "state": "SATISFIED", "reason": "", "bound_finding": null}
```

**[re-measured]** — `UIL-02` is declared **blocking**, is bound, is measurable, and reads
`SATISFIED` with `value: 0`, at a baseline where §4.3 measures **217** objects holding two
permanent UIDs each.

### 5.3 The measurement of record is stale, not merely vacuous

```
uis.json git status                                clean (committed)
uis.json last written                              de9b9f3e  Mon Aug 10 21:31:36 2026 +0530
                                                   "P0-FINAL-CLOSURE-002: fixed-point round 2"
commits from de9b9f3e to HEAD                      84
uis.json counts.recorded_identities                1,264
ledger by_path, working tree                       1,492
difference                                           228
```

**[new]** The identity conformance measurement of record was computed **84 commits ago**, reports
1,264 recorded identities against a ledger that now holds 1,492, and therefore predates the
entire corpus-registration wave that created Group B. `UIL-02`'s `SATISFIED` is a statement about
a repository state that no longer exists. Refreshing it requires executing `uis_engine.py`, which
writes inside `00-MASTER/UIS-001/` — forbidden by this snapshot's mode, so the figure is recorded
as stale rather than corrected.

### 5.4 Where UIS-001 runs

```
grep "uis_engine" verify.sh                        0 matches
run_stage invocations in verify.sh                 16
grep -i "uis" verify.sh                            comment lines only (122, 157) and
                                                   unrelated UISD-000001 stage 6f (505)
Makefile targets                                   uis · uis-gate · uis-self · uis-replay
                                                   (lines 1635-1640)
```

**[re-measured]** — `UIS-001` is reachable only from `make`. None of `verify.sh`'s 16 stages
executes it.

### 5.5 Namespace governance, and what sealing would do to it

```
declared namespaces (UIS-001)                        50
live namespaces (UIS-001, computed at HEAD)         109
ungoverned namespaces (UIS-001)                      74
ambiguous namespaces (UIS-001)                        9
category_seq keys, HEAD                             117
category_seq keys, working tree                     200
new namespaces the uncommitted wave adds             83
```

**[new]** Sealing the 228 registrations admits 83 namespaces the identity system has never
measured, against a declared vocabulary of 50. On the recorded ratio — 74 of 109 live namespaces
ungoverned — the sealing act enlarges the ungoverned-namespace population rather than reducing
it. The exact post-seal figure is **not computable without running `uis_engine.py`**, which this
mode forbids; recorded here as a measured direction with an uncomputed magnitude.

### 5.6 Namespace sample, showing the two grammars side by side

```
UIS-001 ungoverned_namespaces sample   APPLICATION · ARCHITECTURA · ARCHITECTURE ·
                                       ASSIMILATION · BATCHGENERAT · BLOCKERVERIF ·
                                       CANONICALINT · CANONICALOWN
new category_seq keys sample           ASSESS · B01BIR · B01IMP · B02LIF · B02OWN ·
                                       B02UID · CANONI · CAPABI · CERTIF · CMG000
```

**[new]** The ungoverned set is populated by 11–12-character truncations; the incoming set is
populated by 6-character truncations. `CANONICALINT` / `CANONICALOWN` and `CANONI` are three
namespaces derived from overlapping source names at two different widths.

---

## 6. Measurements — UGA Programme and the Anonymous Objects

### 6.1 `uga_engine.py gate`, executed read-only

```
command    python3 00-MASTER/UCOS-UGA-001/uga_engine.py gate
result     GATE FAILED — 2 blocking invariant(s)
```

```
[FAIL] UGA-INV-01  EVERY_OBJECT_HAS_UNIVERSAL_ID              violations=7
[FAIL] UGA-INV-10  EVERY_MUTATION_HAS_AUDIT_EVENT              violations=7, measured=4727
ANONYMOUS OBJECTS: 7 — run `uga_engine.py run`

[PASS] UGA-INV-07  EVERY_CERTIFICATION_HAS_EVIDENCE_BOUNDARY   violations=0, measured=11
[PASS] UGA-INV-08  NO_CANONICAL_ARTIFACT_DEPENDS_ON_UNCLASSIFIED_OBSERVATION  0, measured=345
[PASS] UGA-INV-09  NO_ARCHITECTURE_DEPENDS_ON_FINITE_INSTANCE  violations=0, measured=64
[PASS] OBS-INV-01…OBS-INV-13                                   violations=0  (16 invariants)
[PASS] CAA-INV-01  EXACTLY_ONE_SUPREME_CONSTITUTIONAL_AUTHORITY violations=0, measured=12
[PASS] CAA-INV-02  EVERY_AUTHORITY_CLAIM_NAMES_ITS_SUPERIOR     violations=0, measured=123
[PASS] CAA-INV-03  NO_SUBORDINATE_INSTRUMENT_CLAIMS_INDEPENDENT_AUTHORITY  0, measured=11
[PASS] CAA-INV-04  EXACTLY_ONE_IDENTITY_AUTHORITY               violations=0, measured=6413
[PASS] CAA-INV-05  EXACTLY_ONE_RELATIONSHIP_GRAPH_MODEL_OWNER   violations=0, measured=6
[PASS] CAA-INV-06  EVIDENCE_AND_OBSERVATION_REMAIN_SEPARATE     violations=0, measured=5
[PASS] CAA-INV-07  NO_INSTRUMENT_DECLARES_A_RIVAL_OBJECT_MODEL  violations=0, measured=18
```

**[re-measured]** — the failure, both invariant identifiers, both violation counts, the anonymous
count, and `CAA-INV-04`'s 6,413-identity population are confirmed exactly.

### 6.2 The seven anonymous objects, named

The predecessor recorded a count. These are the paths. **[new]**

| # | Path | `git status` | in `by_object` | in `by_path` |
|---|---|---|---|---|
| 1 | `engine/ceu/context_binding.py` | clean | no | no |
| 2 | `engine/tests/ceu/test_context_binding.py` | clean | no | no |
| 3 | `engine/tests/context/test_req_28_extensibility.py` | clean | no | no |
| 4 | `engine/tests/lineage/test_req_43_upeg_certification.py` | clean | no | no |
| 5 | `engine/tests/uckp/test_phase_2_requirement_evolution.py` | clean | no | no |
| 6 | `platform/repository_intelligence/mutation_class_extension.py` | clean | no | no |
| 7 | `platform/tests/test_violation_4_mutation_extension.py` | clean | no | no |

```
all seven tracked                              yes
all seven clean at HEAD                        yes
any of the seven in the 217                    no — disjoint
any of the seven tracked-modified              no
both invariants cite the same 7 paths          yes — UGA-INV-01 and UGA-INV-10 are the
                                               same population measured twice
```

**Observation.** The seven are content-stable at HEAD and disjoint from the 217, so the repair is
substantively independent of arbitration. Two of the seven
(`mutation_class_extension.py`, `test_violation_4_mutation_extension.py`) sit in the same
mutation-classification subsystem that the `R-09` repair modifies, though not in the same files.

### 6.3 What a mint writes — read in source

```
00-MASTER/UCOS-UGA-001/uga_engine.py:261   "Shares the corpus `category_seq` counter.
                                            Consumes NO page range. Append-only:"
uga_engine.py:266                          seq = ledger.setdefault("category_seq", {})
uga_engine.py:295                          by_object[rel] = { … }
uga_engine.py:27                           "…range is consumed: pages are a BOOK concept, so
                                            `page_cursor` is never touched"
uga_engine.py:483                          seq = ledger.setdefault("category_seq", {})
                                            (observation mint, category OBS)
```

**[new — decisive for the isolation question]** A `by_object` mint writes `by_object` **and
advances `category_seq`, in `00-BOOK/DATA/id-ledger.json`** — the same file, and the same
`category_seq` object, that already carries the uncommitted transaction's 88 counter changes and
228 `by_path` registrations. It does **not** touch `page_cursor`.

### 6.4 UGA canonical surfaces

```
generated-artifact-registry.json entries                            345
UGA canonical surfaces declared generated                            10
regeneration_command on each                python3 00-MASTER/UCOS-UGA-001/uga_engine.py run
registration_status on each                 EXCLUDED_FROM_CORPUS_REGISTRATION
00-BOOK/DATA/id-ledger.json in canonical_path set                    NO
00-BOOK/DATA/id-ledger.json in input_classification of UGA entries   YES —
                                                                     "GENERATED_DETERMINISTIC"
```

**[new]** The ledger is classified `GENERATED_DETERMINISTIC` **as an input** by the ten UGA
surface entries, yet it is **not** one of the 345 registered generated artifacts and has no
`producer` or `regeneration_command` of its own. It is consumed as if regenerable and registered
as if not.

---

## 7. Measurements — Supersession Surface

### 7.1 The law exists

`02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md`, read verbatim:

```
AIF-L13  Prepare/Commit/Abort Atomicity. Mints are provisional until seal; abort discards
         (no orphan identity); commit seals atomically; retry is idempotent.
AIF-L14  Atomic Admission (realizes REG-AUTO-001). An artifact exists only when its admission
         is sealed AND its derived projection re-verifies AND certification passes.
AIF-L15  Declared-Intent Transitions. version/copy/clone/fork/split/merge/supersede/replace/
         restore/new are author-declared and machine-validated.
AIF-L17  Forward-Only Compensation. No deletion or edit of Recorded Truth; correction is a new
         event; retired identities are never reissued.
AIF-L21  Certification Duality. Immutable Historical Attestation (RECORDED) vs recomputed
         Current Status (DERIVED), in distinct stores.
line 122 Registration transaction | 00-BOOK/tools/register.sh (REG-AUTO-001 / UMB-IMP-001)
         | Realizes AIF-L14 atomic admission.
```

**[re-measured]** — `supersede` is a ratified declared-intent transition under `AIF-L15`.

### 7.2 The implementation surface does not

```
supersession map in id-ledger.json                    ABSENT (9 keys, §4.1)
"supersede" in 00-BOOK/tools/ukb.py                   0 matches
supersession store anywhere in 00-BOOK/DATA/          ABSENT — 17 files, §7.3
alignment register planes[REPOSITORY_OBJECT].maps     ["by_path","by_object","by_observation"]
alignment register mint_markers                       ["category_seq"]
```

**[re-measured]** — no store, no schema, no writer, no reader, no validator.

### 7.3 The complete `00-BOOK/DATA/` inventory, for the record

```
artifacts.json · canonical-observation-audit.json · certification.json · change-ledger.json ·
connector-cursors.json · constitutional-authority-alignment.json · control-tower.json ·
evidence-universe.json · exclusion-register.json · generated-artifact-registry.json ·
id-ledger.json · mutation-governance-boundary.json · observation-universe.json ·
relationships.json · signals.json · twin.json · volumes.json
                                                                        17 files
```

**[new]** — none is a supersession store.

### 7.4 The one located supersession-adjacent note, read verbatim

`00-BOOK/DATA/constitutional-authority-alignment.json:654`:

> "Real components exist (CMG amendments, Lifecycle.SUPERSEDED/HISTORICAL, supersedes/superseded_by,
> evolves-from relation types, engine.constitution.evolution) but no single cross-domain read path
> was confirmed by PHASE-UCF-001 or PHASE-UCF-002. A dedicated discovery pass is the correct next
> step; this binding does not guess at the answer."

**[new]** — the register itself records that supersession components exist in scattered form with
**no confirmed cross-domain read path**, and explicitly declines to assert one.

---

## 8. Measurements — Freeze, Ratification, and Certification

### 8.1 Freeze law exists and requires a registry

`00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` (380 lines), read verbatim:

```
I.1    Freeze Authority SHALL be the authority to seal a ratified artifact as an immutable
       baseline and to record that seal.
I.2    Freeze Authority SHALL preserve only; it SHALL introduce no content, perform no
       validation, certification, or ratification, and modify no artifact.
I.3    Freeze Authority SHALL be single per artifact; two authorities SHALL NOT freeze the
       same artifact.
I.5    Freeze Authority SHALL NEVER be self-conferred by Execution Authority and SHALL act
       only upon an authorization under Article XX.
IX.1   A FROZEN artifact SHALL NOT be modified, in whole or in part, by any authority or act.
XVI.1  The Freeze Registry SHALL be the single canonical record of all freeze baselines,
       their states, their artifacts, and their lineages.
XVI.2  The Freeze Registry SHALL enforce uniqueness: every frozen artifact SHALL hold exactly
       one canonical freeze record.
XVI.3  The Freeze Registry SHALL be append-only, content-addressed, and reconciled against
       repository truth at boot.
XVII.1 A freeze record SHALL record the artifact, the Freeze Authority, the preconditions
       satisfied, the baseline digest, the version, the lineage, the state, and the
       program-state hash.
XX.4   Freeze enforcement SHALL NEVER be waived, deferred, or overridden by any authority tier.
```

```
search for a Freeze Registry artifact    find -iname "*freeze*registry*"   0 results
```

**[new]** — Article XVI mandates a single canonical Freeze Registry. No artifact matching that
name exists in the tree.

### 8.2 What freeze machinery does exist

```
platform/universal_foundation/freeze.py                                 present
platform/universal_foundation/catalog/foundation-freeze.json            present
   register_id  ucos.foundation.freeze
   criteria     FZ-01 … FZ-13
engine/governance/freeze.py                                             present
service/_evidence/EC3-B11-U13/freeze-baseline.json                      present  (a worked example)
service/_evidence/EC3-B11-U13/freeze-preconditions.json                 present  (FP-1…FP-6, all true)
```

`FZ-01…FZ-13`, read verbatim: **[new]**

| ID | Requirement | Evidence kind |
|---|---|---|
| FZ-01 | Zero duplicate capabilities | `no-duplicates` |
| FZ-02 | Zero competing constitutional definitions | `platform-gates` |
| FZ-03 | Zero competing ownership systems | `models-converged` |
| FZ-04 | Zero competing Repository Truth systems | `models-converged` |
| FZ-05 | Zero unresolved Foundation architecture | `no-fault` |
| FZ-06 | All Foundation services registered | `gates` |
| FZ-07 | All Foundation contracts validated | `gates` |
| FZ-08 | All Foundation policies certified | `gates` |
| FZ-09 | All Foundation dependencies satisfied | `gates` |
| FZ-10 | All Foundation dependencies resolve to a total composition order | `dependency-order` |
| FZ-11 | All Foundation tests passing | `command` |
| FZ-12 | All Foundation verification and certification complete | `maturity` |
| FZ-13 | Every registered Ω Nucleus is constitutionally complete | `platform-gates` |

The register's own `$comment`, read verbatim:

> "A criterion whose evidence was not gathered is reported UNMEASURED and withholds readiness
> exactly as firmly as a failure — a freeze declared over unmeasured criteria is the failure a
> freeze exists to prevent."

**[new]** — the freeze mechanism is real, exercised (band 11 freeze record with a
`baseline_digest` and six satisfied preconditions), and fails closed on unmeasured criteria. It is
scoped to the Universal Foundation and to service bands. Nothing found binds it to the identity
ledger.

### 8.3 The declared architecture freeze is 154 commits stale

`UNAF-001-UNIVERSAL-NUCLEUS-ARCHITECTURE-FREEZE.md`, read verbatim:

```
line  12   "Production Foundation is frozen at checkpoint 873ef19 / 00bd45f."
line 682   "This architecture is frozen at commit 00bd45f."
line 549   "All gates green. 7/7 Ω Nuclei conformant. Freeze READY 13/13. Replay
            byte-identical. 6403 tests, 93% coverage. 1203/1203 artifacts registered."
line 107   "An unstated facet is MISSING and blocks freeze."
line 373   "implement under constitution → register through transaction → measure with
            ucos-constitution → freeze only when gates pass"
```

```
00bd45f resolves                       commit  00bd45f1  "REPLAY SYNC: Repository Truth
                                       converged — 5 new artifacts, UAIE and UCKP
                                       expectations forward"
is 00bd45f an ancestor of HEAD         YES
commits from 00bd45f to HEAD           154
artifacts registered, per UNAF         1,203
artifacts registered, at HEAD          1,233
artifacts registered, working tree     1,461
```

**[new]** — the freeze of record names a commit 154 commits behind HEAD and cites an artifact
count 258 below the working tree.

### 8.4 Ratification law exists; no ratification field does

`00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md`, read verbatim:

```
STATUS  RATIFIED (program-governance level) · NORMATIVE · LIVING-UNTIL-FROZEN
P.2     Ratification SHALL be the single constitutional act through which a validated and
        certified artifact becomes an officially accepted member of the constitutional corpus.
P.3     Ratification SHALL determine constitutional acceptance only; it SHALL never perform
        validation, never perform certification, and never modify any artifact.
I.1     Ratification Authority SHALL be the authority to determine the constitutional
        acceptance of a validated and certified artifact and to record that determination.
```

```
grep -i "ratif" 00-BOOK/DATA/constitutional-authority-alignment.json      0 matches
```

**[new]** — the alignment register that names every authority carries **no ratification field for
any of them**. Ratification is legislated and unrepresented in the register that would record it.

### 8.5 UGA certification

`00-MASTER/UCOS-UGA-001/07-CERTIFICATION.json`: **[re-measured]**

```
verdict                        CERTIFIED
blocking_deviations            []
declared_open                  []
epoch                          10-11 — Certification / Phase 8 / Phase 9
determinism                    "No wall clock. Timestamps are ledger first_seen values."
scope.objects_governed          6,145
scope.minted_by_this_programme  4,912
scope.corpus_bytes_touched          0
proof.existence_digest         ea83747bf3617633d249e46968268e44740c211a769f08af9a386e379bf961b4
proof.identity_digest          14005b6282dbe9d5002328830c50fbc4a3d0901618562213b0cb6055c7b0ff0b
proof.registry_digest          5dda706a7b4f8b314d256350af41a5a57a415f6bb7d120433d630869b5fc7bc3
proof.graph_digest             c34482f04cf34d484dceb993de06f21b10e7e250d0557958d2e61b95b87f8134
proof.invariant_digest         53a2be243ea33c8028610a122e7ff9e3de5ac7c8f0291cda4dd82ad42f9f0ee9
last written                   8dc9a812  Sat Aug 22 16:50:19 2026 +0530
```

### 8.6 Repository certification

`00-BOOK/DATA/certification.json`: **[new]**

```
standard                UMB-017 Digital Twin Certification (non-terminal; AUTH-INF-001 CR-INF-011)
verdict                 CERTIFIED
domains_total           10
domains_passed          10
generated_at            2026-08-10T15:29:29+00:00
last written            1f9041cd  Mon Aug 10 20:59:29 2026 +0530

domains.identity checks, verbatim
  "no duplicate Universal IDs"          pass=true   detail="1233 unique"
  "no overlapping page ranges"          pass=true   detail="append-only pages intact"
  "ledger page cursor >= max page"      pass=true   detail="cursor=9826 max_end=9826"
domains.registry checks, verbatim
  "every artifact present in id-ledger" pass=true   detail="1233 artifacts ledgered"
  "every artifact carries name+volume+program"  pass=true  detail="all classified"
```

**Observation.** The repository certification of record certifies `1233 unique` identities and
`cursor=9826`. The working tree holds 1,492 and 10,840. Its identity domain passed over a
population 228 smaller than the one now on disk.

### 8.7 Certification authority, read in source

```
engine/universal_certification/contracts.py:54    UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"
```

**[re-measured]** — the certification engine's authority constant declares engineering execution
only.

---

## 9. Blockers Discovered

Fourteen. `EB-` identifiers are local to this snapshot; the right-hand column maps each to the
already-registered finding it corresponds to, where one exists.

| ID | Blocker | Measured evidence | Severity | Maps to |
|---|---|---|---|---|
| `EB-1` | `R-09` is declared with no predicate, so `validate_rule_coverage()` is non-empty and `classify()` returns `ERROR` for every subject in the repository | §3.1 | **CRITICAL** | `BC-1` · `M-C` · `UIAR-2` |
| `EB-2` | `BC-1` stands at **0 of 8** acceptance criteria with `evidence: none` on every one | §3.5 | **CRITICAL** | `BC-1` |
| `EB-3` | `BC-1`'s own test is tracked-modified `+3/−3` and adds no `R-09` coverage | §3.6 | MEDIUM | `F-4` |
| `EB-4` | No authority-admission map exists over the class vocabulary: `UCOS-UGA-001` appears in **0 of 9** classes and **3 of 9** classes resolve to an owner-parameterised placeholder | §3.2 | **CRITICAL** | `UIAR-1` |
| `EB-5` | 192 of the 217 canonical identities exist only in an uncommitted transaction: `+228` registrations, `+1,014` pages, `88` counter changes | §4.2, §4.7 | **CRITICAL** | `UIAR-4` |
| `EB-6` | The uncommitted wave creates **83** namespaces at a uniform 6-character width against a HEAD population spanning 3–12, and advances **5** pre-existing counters | §4.7, §4.8 | HIGH | `UIAR-5` (mechanism, **new**) |
| `EB-7` | `uga_engine.py gate` FAILS on `UGA-INV-01` and `UGA-INV-10`, 7 anonymous objects | §6.1 | **CRITICAL** | `UIAR-9` |
| `EB-8` | A `by_object` mint advances `category_seq` in `id-ledger.json` — the same file and same object as the 228 uncommitted registrations, so the 7 mints cannot be committed in isolation from them | §6.3 | **CRITICAL** | **new** |
| `EB-9` | No supersession store, schema, writer, reader or validator exists, while `supersede` is ratified law under `AIF-L15` | §7.1, §7.2, §7.3 | HIGH | `UIAR-7` |
| `EB-10` | `UIL-02` is declared **blocking** and reads `SATISFIED · value 0` at a baseline holding 217 dual-identity subjects | §5.2 | **CRITICAL** | `UIAR-10` |
| `EB-11` | The identity measurement of record is **84 commits and 228 identities stale**, and predates the wave that created Group B | §5.3 | HIGH | `UIA-2` extension (**new**) |
| `EB-12` | `UIS-001` is executed by no stage of `verify.sh`; 16 stages, 0 matches for `uis_engine` | §5.4 | **CRITICAL** | `UIAR-10` |
| `EB-13` | `CEP-007` Article XVI mandates a single canonical Freeze Registry; no such artifact exists. The declared architecture freeze names a commit **154 commits** behind HEAD | §8.1, §8.3 | HIGH | **new** |
| `EB-14` | No rollback boundary separates arbitration from the uncommitted transaction: the ledger has no declared producer or `regeneration_command`, so `git` is the only restore path and it cannot discriminate | §4.2, §6.4 | HIGH | `UIAR-12` (mechanism, **new**) |

---

## 10. Contradictions Measured

Nine. Each is a pair of repository statements that cannot both be true, with both sides measured.

| # | Side A | Side B | Both measured at |
|---|---|---|---|
| `EC-1` | `07-CERTIFICATION.json` — `verdict: CERTIFIED`, `blocking_deviations: []`, `declared_open: []` | `uga_engine.py gate` — **FAILED**, two blocking invariants, 7 violations each | §8.5, §6.1 |
| `EC-2` | `uis.json` — `UIL-02` *"No object SHALL possess more than one permanent UID"*, `blocking: true`, `value: 0`, `state: SATISFIED` | `by_path ∩ by_object` = **217** objects each holding two permanent UIDs | §5.2, §4.3 |
| `EC-3` | `uis.json` — `gate: OPEN`, `blocking_failures: []`, `determination: IDENTITY-CONFORMANCE-BOUND` | The same file's `recorded_identities: 1,264` against a ledger of **1,492** — the gate is open over a state 228 identities out of date | §5.1, §5.3 |
| `EC-4` | `mutation-governance-boundary.json` — `total`: *"Every mutation subject resolves… never to nothing, and never to a default"* | `classify()` returns `ERROR` for every subject; **nothing** resolves | §3.4, §3.1 |
| `EC-5` | `certification.json` — `verdict: CERTIFIED`, 10/10 domains, identity domain detail `"1233 unique"`, `"cursor=9826"` | Working-tree ledger: **1,492** by_path, `page_cursor` **10,840** | §8.6, §4.2 |
| `EC-6` | The ten UGA surface entries classify `00-BOOK/DATA/id-ledger.json` as `GENERATED_DETERMINISTIC` | The ledger is absent from the 345 `canonical_path` entries and has no `producer` or `regeneration_command` | §6.4 |
| `EC-7` | `UNAF-001` — *"This architecture is frozen at commit `00bd45f`"*, *"Freeze READY 13/13"*, *"1203/1203 artifacts registered"* | HEAD is **154 commits** beyond `00bd45f`; artifacts registered = 1,233 at HEAD, **1,461** in tree | §8.3 |
| `EC-8` | `CEP-007` XVI.1 — *"The Freeze Registry SHALL be the single canonical record of all freeze baselines"* | No artifact matching `*freeze*registry*` exists | §8.1 |
| `EC-9` | `CEP-006` legislates Ratification Authority as the act by which an artifact becomes an accepted member of the corpus | `constitutional-authority-alignment.json` carries **0** matches for `ratif` — no authority in the register records a ratification state | §8.4 |

**Observation on `EC-1`, `EC-3` and `EC-5` together.** Three separate certification-or-gate
artifacts each report a green state, and each was computed against a repository state that has
since moved. None of the three is wrong about the state it measured; all three are being read as
statements about the current state.

---

## 11. Dependencies and Authority Gaps

### 11.1 Dependency edges measured, not preferred

Twenty-one edges. Each cites the measurement that forces it.

```
E-01  R-09 predicate            →  any class assignment                §3.1  classify() = ERROR
E-02  R-09 predicate            →  BC-1 A1-1                           §3.5  criterion is the call
E-03  R-09 predicate            →  BC-1 A1-2 … A1-8                    §3.5  0/8, all downstream
E-04  BC-1 test settled         →  BC-1 evidence attributable          §3.6  test dirty +3/−3
E-05  class assignment          →  authority-admission map             §3.2  map is keyed on class
E-06  authority-admission map   →  canonical-identity selection        §3.2  0 of 9 name UGA
E-07  REG-AUTO seal/discard     →  sealed canonical identifiers        §4.2  192 uncommitted
E-08  REG-AUTO seal/discard     →  rollback boundary                   §4.2  one file, two acts
E-09  REG-AUTO seal/discard     →  **anonymous-object mint isolation**  §6.3  shared category_seq
E-10  REG-AUTO seal/discard     →  namespace governance figure         §5.5  +83 namespaces
E-11  namespace width decision  →  identifier reproducibility          §4.8  6-char vs 3–12
E-12  identity measure repair   →  any before-measurement              §5.2  measure reads 0
E-13  identity measure refresh  →  a non-stale UIL-02 reading          §5.3  84 commits stale
E-14  UIS-001 in verify.sh      →  measurement executed in the path    §5.4  0 of 16 stages
E-15  supersession store        →  any supersession record             §7.2  no store exists
E-16  supersession store        →  alignment-register map totality     §7.2  3 declared maps
E-17  anonymous-object mint     →  uga_engine.py gate PASS             §6.1  7 violations × 2
E-18  gate PASS                 →  a recomputable certification        §8.5  CERTIFIED vs FAILED
E-19  ledger regeneration path  →  restore-without-git                 §6.4  no producer declared
E-20  Freeze Registry exists    →  any freeze record of an identity    §8.1  XVI.1 mandates it
E-21  ratification field exists →  any recorded authority acceptance   §8.4  0 matches for ratif
```

### 11.2 The edge that contradicts the predecessor

`E-09` is the one dependency the predecessor determination records as **absent**. Its precondition
`P-6` (mint the 7 anonymous objects) is listed with `Depends on: —` and named among five
preconditions *"dischargeable in parallel today,"* while its own discharge test requires that
*"the run is committed separately and named as unrelated to arbitration."*

Measured, that test is not satisfiable at this baseline: §6.3 shows a `by_object` mint advances
`category_seq` inside `00-BOOK/DATA/id-ledger.json`, and §4.7 shows that object already carries 88
counter changes belonging to the uncommitted corpus transaction. A commit of the 7 mints therefore
either carries the 228 registrations with it, or requires partial staging of a single JSON object
whose `by_path`, `page_cursor` and `category_seq` values would be mutually inconsistent in the
staged version.

**Recorded as evidence, not as a verdict:** the mint is *substantively* independent of arbitration
(§6.2 — all 7 clean at HEAD, all 7 disjoint from the 217) and *transactionally* entangled with the
sealing decision (§6.3). Both halves are measured.

### 11.3 Authority gaps

Seven. Each names the act, the authority the repository says must perform it, and what was
measured about that authority's availability.

| # | Act requiring authority | Authority named by the repository | Measured availability |
|---|---|---|---|
| `AG-1` | Implement `R-09`'s predicate | Repository Intelligence, *read from the register's `governed_by` chain, not assigned* | **AVAILABLE** — recorded as *"engineering execution; a declared rule is made to function"* (§3.5) |
| `AG-2` | Declare an authority-admission map over the class vocabulary | Mutation governance owner | **NOT LOCATED** — the register names no owner able to add a cross-authority mapping; `UCOS-UGA-001` appears in 0 of 9 classes (§3.2) |
| `AG-3` | Seal or discard the 228 corpus registrations | `REG-AUTO-001` via `00-BOOK/tools/register.sh`; artifact lifecycle `ENG-001 D30` / `UMB-003 §3` | **INSTRUMENT PRESENT, RATIFICATION UNRECORDED** — `register.sh` (14,087 bytes, executable) and the `REG-AUTO-001` standard (43,326 bytes) both exist; no ratification field exists in the alignment register (§8.4) |
| `AG-4` | Decide whether 85 pages remain bound to 25 superseded corpus identities | Corpus authority via `UMB-003` | **REFERRED, UNRESOLVED** — `UMB-003` is cited in 8+ artifacts as an artifact-lifecycle owner; no decision record located (§4.4) |
| `AG-5` | Mint the 7 anonymous objects and record their audit events | `UCOS-UGA-001` | **AVAILABLE for the mint, BLOCKED for the isolated commit** — the programme owns `by_object`; the separate-commit requirement is unsatisfiable while `AG-3` is open (§6.3, §11.2) |
| `AG-6` | Create a supersession store and amend the alignment register's map list | Identity authority + constitutional alignment owner | **NOT LOCATED** — `CAA-INV-04` asserts exactly one identity authority over 6,413 identities; the register itself declines to assert a cross-domain supersession read path (§7.4) |
| `AG-7` | Record a freeze of the identity baseline | Freeze Authority under `CEP-007`, acting *"only upon an authorization under Article XX"* | **NO REGISTRY** — Article XVI mandates a Freeze Registry; none exists. `I.5` forbids self-conferral by Execution Authority (§8.1) |

### 11.4 Inherited authority position

From `CH-4`, carried forward as recorded context rather than re-measured: **[inherited]**

```
391 of 542 concepts unowned  ·  0% ratified  ·  three disclaiming planes
UKAP/UREE blocked on Article 28, which is external
variance disclosed: B-6 states 398 of 549 unowned, 151 declared (27.5046%)
```

Both figures are carried. On either, the ownership property is unsatisfied for a majority of
subjects.

---

## 12. Measurement Provenance

Every figure in this snapshot came from one of the following, all executed at
`HEAD = bae59755` with the standing working tree.

```
git rev-parse HEAD ; git rev-parse --abbrev-ref HEAD
git status --porcelain                                       (counted, filtered by ^ M and ^??)
git status --porcelain <path>                                (per-file, 7 anonymous objects + 2 ledger files)
git log -1 --format="%h %ad %s" -- <path>                    (uis.json, 07-CERTIFICATION.json,
                                                              certification.json)
git rev-list --count 00bd45f..HEAD    →  154
git rev-list --count de9b9f3e..HEAD   →   84
git merge-base --is-ancestor 00bd45f HEAD  →  yes
git cat-file -t 00bd45f               →  commit
git show HEAD:00-BOOK/DATA/id-ledger.json      | python3  (HEAD-side ledger figures)
git show HEAD:00-BOOK/DATA/artifacts.json      | python3  (HEAD count = 1,233)
git ls-files --error-unmatch <path>            (tracked-status of the 7 anonymous objects
                                                and id-ledger.json)

python3  sys.path.insert(0,'platform')
         from repository_intelligence.mutation_classification import RULE_PREDICATES,
                                                                     validate_rule_coverage
python3 00-MASTER/UCOS-UGA-001/uga_engine.py gate      (declared non-mutating; guarded by
                                                        platform/tests/test_verification_purity.py)

json reads (no writes):
  00-BOOK/DATA/id-ledger.json · artifacts.json · mutation-governance-boundary.json ·
  constitutional-authority-alignment.json · generated-artifact-registry.json ·
  certification.json
  00-MASTER/UIS-001/uis.json · uis-declaration.json
  00-MASTER/UCOS-UGA-001/07-CERTIFICATION.json
  platform/universal_foundation/catalog/foundation-freeze.json
  service/_evidence/EC3-B11-U13/freeze-baseline.json · freeze-preconditions.json

text reads (no writes):
  02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md
  00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md
  00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md
  UNAF-001-UNIVERSAL-NUCLEUS-ARCHITECTURE-FREEZE.md
  UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-DETERMINATION.md
  UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-EXECUTION-READINESS-DETERMINATION.md
  UCOS-OMEGA-INFINITY-BLOCKER-CLOSURE-STATUS-REGISTER.md
  UCOS-OMEGA-INFINITY-BLOCKER-CLOSURE-IMPLEMENTATION-PLAN.md
  UCOS-OMEGA-INFINITY-BASELINE-INTEGRITY-RECONCILIATION-REPORT.md
  00-MASTER/UCOS-UGA-001/uga_engine.py           (lines 25, 27, 261, 266, 295, 473, 483, 1636, 1773)
  platform/repository_intelligence/mutation_classification.py   (lines 403-491)
  engine/universal_certification/contracts.py    (line 54)
  verify.sh · Makefile

NOT executed, deliberately:
  uga_engine.py run          — mints identities
  uis_engine.py              — writes inside 00-MASTER/UIS-001/
  any git write operation    — add, commit, stage, stash, revert, reset, checkout
  any file write except this artifact
```

### 12.1 Consolidated figure table

```
HEAD                                     bae59755d7e2d3566c93b89c722b68847145269a
branch                                   integration/recovery-001
porcelain lines  before / after          350 / 351      (delta = this file only)
tracked-modified before / after          38 / 38
untracked        before / after          312 / 313

ledger by_path / by_object / by_observation, tree      1,492 / 4,914 / 7
ledger by_path / by_object / by_observation, HEAD      1,264 / 4,914 / 7
page_cursor  HEAD → tree                               9,826 → 10,840   (+1,014)
category_seq keys  HEAD → tree                           117 → 200      (+83 new, 5 advanced)
artifacts.json count  HEAD → tree                      1,233 → 1,461    (+228)

by_path ∩ by_object   tree / HEAD                        217 / 25
by_observation ∩ by_path / ∩ by_object                     0 / 0
Group A / Group B                                         25 / 192
  A by_object cats                                  EXDOC 12 · DATAOBJ 13
  B by_object cats                                  EXDOC 189 · DATAOBJ 3
  A by_path cats                       MASTER 13 · INTELLIGENCE 11 · MCP001MASTER 1
  B by_path cats                                    75 distinct   (all 217: 78)
  A / B pages held by the by_path id                        85 / 866   (total 951)
  A / B in artifacts.json                             0 of 25 / 192 of 192
  B .md / .json                                            189 / 3
  B matching R-09 filename rule                       127 of 192
  A cat widths                              6ch 13 · 12ch 12
  B cat widths                              3ch 19 · 6ch 173

reference counts over the 217 by_object ids
  02-UNIVERSAL-OBJECT-REGISTRY.json                        217
  03-AUDIT-UNIVERSE.json                                   434
  04-RELATIONSHIP-GRAPH.json                               868
  05-GOVERNANCE-INVARIANTS.json / 07-CERTIFICATION.json    0 / 0
  00-BOOK/DATA/id-ledger.json                              217
  UGA surfaces subtotal / grand total                   1,519 / 1,736

mutation classification
  rules declared / predicates implemented                    9 / 8
  validate_rule_coverage()      ("rule 'R-09' is declared but no predicate implements it",)
  classify(), every subject                              ERROR
  owner-parameterised governed_by values                 3 of 9
  occurrences of UCOS-UGA-001 in the boundary register       0

uga_engine.py gate                                     FAILED
  UGA-INV-01 / UGA-INV-10 violations                     7 / 7   (same 7 paths)
  UGA-INV-10 measured population                         4,727
  anonymous objects                                          7   (all tracked, all clean at HEAD,
                                                                  all disjoint from the 217)
  CAA-INV-04 population / result                         6,413 / PASS
  invariants PASS / FAIL                                    31 / 2

UGA 07-CERTIFICATION.json
  verdict / blocking_deviations / declared_open      CERTIFIED / [] / []
  objects_governed / minted_by_programme / corpus_bytes   6,145 / 4,912 / 0
  proof digests                                              5
  last written                                       8dc9a812  2026-08-22 16:50 +0530

00-BOOK/DATA/certification.json
  verdict / domains                                  CERTIFIED / 10 of 10
  identity domain detail                             "1233 unique" · "cursor=9826"
  last written                                       1f9041cd  2026-08-10 20:59 +0530
UCERT_AUTHORITY                                      "ENGINEERING-EXECUTION-ONLY"

UIS-001 uis.json
  gate / blocking_failures / determination     OPEN / [] / IDENTITY-CONFORMANCE-BOUND
  UIL-02  blocking / measure / expect / value / state
                                        true / identities_multiple / 0 / 0 / SATISFIED
  recorded_identities / recorded_histories / registered_identities   1,264 / 1,264 / 1,233
  declared / live namespaces                                50 / 109
  ungoverned / ambiguous namespaces                         74 / 9
  namespace_width                                            6
  grammar                              ^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$
  seal_sha256                          2b8f0496ef66c7ab991c994654b334266529113a2a549a7e077963fb44ae5439
  last written / commits since         de9b9f3e 2026-08-10 21:31 +0530 / 84
  in verify.sh                         NO   (16 run_stage invocations, 0 matches)
  Makefile targets                     uis · uis-gate · uis-self · uis-replay

supersession
  supersession map in the ledger                          ABSENT
  ledger top-level keys                                        9
  "supersede" in 00-BOOK/tools/ukb.py                          0
  00-BOOK/DATA/ files                                         17   (none is a supersession store)
  alignment register REPOSITORY_OBJECT maps        ["by_path","by_object","by_observation"]
  alignment register mint_markers                  ["category_seq"]

generated-artifact-registry.json
  entries / canonical_paths                              345 / 345
  UGA canonical surfaces declared generated                 10
  id-ledger.json in canonical_path                          NO
  id-ledger.json in UGA input_classification         GENERATED_DETERMINISTIC

freeze / ratification
  CEP-007 lines / Freeze Registry artifacts               380 / 0
  foundation-freeze.json criteria                        FZ-01 … FZ-13   (13)
  worked freeze example preconditions                     FP-1 … FP-6, all true
  UNAF-001 declared freeze commit                        00bd45f  (ancestor of HEAD)
  commits from the declared freeze to HEAD                 154
  UNAF-001 artifacts-registered claim                     1,203
  "ratif" in constitutional-authority-alignment.json           0

BC-1
  status / criteria satisfied                            OPEN / 0 of 8
  BC-1's own test                                        tracked-modified +3 / −3, no R-09 coverage

this snapshot
  blockers recorded                                         14
  contradictions recorded                                    9
  dependency edges recorded                                 21
  authority gaps recorded                                    7
  new findings with no predecessor                           6
  subjects arbitrated                                        0
  identities minted / retired / superseded / renumbered      0 / 0 / 0 / 0
```

### 12.2 The six findings with no predecessor

Marked **[new]** above and collected here so they are not lost in the body.

| # | Finding | Section |
|---|---|---|
| `N-1` | A `by_object` mint advances `category_seq` inside `id-ledger.json`, so the 7 anonymous-object mints cannot be committed in isolation from the 228 uncommitted registrations. The predecessor's `P-6` is recorded as dependency-free; measured, it depends on the sealing decision | §6.3, §11.2 |
| `N-2` | The 88 counter changes decompose into **83 new namespaces and 5 advanced pre-existing counters** (`BOOK, CON, IMP, ENG, ADR`) — the transaction is not purely additive at the namespace level | §4.7 |
| `N-3` | All 83 new namespaces are exactly 6 characters; HEAD's 117 span 3–12 with 54 at twelve. Both are inside the declared grammar, so this is a change of derivation behaviour between waves, not a grammar violation | §4.8 |
| `N-4` | `uis.json` was written 84 commits ago and reports 1,264 identities against a ledger of 1,492 — the identity measurement of record is stale, not merely vacuous, and predates Group B entirely | §5.3 |
| `N-5` | `id-ledger.json` is classified `GENERATED_DETERMINISTIC` as an input by the ten UGA surface entries but is absent from the 345 registered generated artifacts and has no declared producer or `regeneration_command` — consumed as regenerable, registered as not | §6.4 |
| `N-6` | `CEP-007` Article XVI mandates a single canonical Freeze Registry and none exists; the declared architecture freeze names a commit 154 commits behind HEAD; `constitutional-authority-alignment.json` carries zero `ratif` matches | §8.1, §8.3, §8.4 |

### 12.3 The seven anonymous object paths, restated for durability

```
engine/ceu/context_binding.py
engine/tests/ceu/test_context_binding.py
engine/tests/context/test_req_28_extensibility.py
engine/tests/lineage/test_req_43_upeg_certification.py
engine/tests/uckp/test_phase_2_requirement_evolution.py
platform/repository_intelligence/mutation_class_extension.py
platform/tests/test_violation_4_mutation_extension.py
```

Cited identically by `UGA-INV-01` and `UGA-INV-10`. All tracked. All clean at HEAD. None in
`by_path`. None in `by_object`. None among the 217.

---

## 13. Verification

| Check | Result |
|---|---|
| File exists | ✅ `UCOS-OMEGA-INFINITY-IDENTITY-ARBITRATION-PRECONDITION-CLOSURE-EVIDENCE-SNAPSHOT.md` |
| Line count | ✅ **See §13.1** — asserted by measurement below, not by claim |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| `git status` delta only this file | ✅ 350 → 351 porcelain lines; tracked-modified **38 → 38**; untracked **312 → 313** |
| Code changes | ✅ **0** — `mutation_classification.py`, `uga_engine.py`, `contracts.py`, `verify.sh`, `Makefile` read, none written |
| Registry changes | ✅ **0** — `id-ledger.json`, `artifacts.json`, `mutation-governance-boundary.json`, `constitutional-authority-alignment.json`, `generated-artifact-registry.json`, `uis.json`, all 10 UGA surfaces read, none written |
| Certification changes | ✅ **0** — `07-CERTIFICATION.json` and `00-BOOK/DATA/certification.json` read, unmodified |
| Identity changes | ✅ **0** — `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `page_cursor` 10,840 · `category_seq` 200 keys, before and after |
| Identities minted / retired / superseded / renumbered | ✅ **0 / 0 / 0 / 0** |
| Subjects arbitrated | ✅ **0** |
| Commits | ✅ **0** — no `add`, `commit`, `stage`, `stash`, `revert`, `reset` or `checkout` |
| Commands executed | ✅ read-only only — `uga_engine.py gate` (declared non-mutating, guarded by `platform/tests/test_verification_purity.py`), `git show` / `log` / `rev-list` / `ls-files` / `status`, JSON and text reads. `uga_engine.py run` and `uis_engine.py` **not executed** |
| Only one new artifact | ✅ the single repository delta is this file |
| Determination produced | ✅ **NONE** — this artifact records evidence and declares no closure, no matrix, no authorization and no arbitration point |
| Preconditions closed | ✅ **0** |
| Blockers resolved | ✅ **0** — 14 recorded |

### 13.1 Line count, measured

The line count is asserted by running `wc -l` against this file after it was written, and the
result is recorded in the session transcript rather than hard-coded here — a self-reported line
count inside the file it counts is the one figure in this artifact that cannot be verified from
the artifact alone.

---

*This snapshot arbitrated no subject, minted no identity, wrote no register, recomputed no
certification and produced no determination. `by_path` stands at 1,492, `by_object` at 4,914 and
`by_observation` at 7, before and after, and the working tree carries the same 38 tracked
modifications it carried at session start. It exists because a determination was withdrawn and the
evidence behind it was worth keeping: 63 measurements, 14 blockers, 9 contradictions, 21
dependency edges, 7 authority gaps, and 6 findings no predecessor holds. Three of the six matter
most. A `by_object` mint advances the same `category_seq` object that carries the 228 uncommitted
corpus registrations, so the seven anonymous-object mints cannot be committed in isolation from a
transaction nobody has authorized — which makes a precondition the predecessor recorded as
dependency-free dependent on the one act with no located ratifier. The identity measurement of
record was computed 84 commits ago over 1,264 identities and now faces a ledger of 1,492, so the
blocking law `UIL-02` reads `SATISFIED` about a repository that no longer exists. And the ledger
those figures describe is classified `GENERATED_DETERMINISTIC` by every artifact that consumes it
while holding no producer and no regeneration command of its own, which is why `git` is the only
restore path and why it cannot separate an arbitration failure from the registrations the
arbitration would name. Nothing here is closed, decided, or authorized. It is measured.*

**END EVIDENCE SNAPSHOT — 14 BLOCKERS · 9 CONTRADICTIONS · 21 DEPENDENCY EDGES · 7 AUTHORITY GAPS · 0 PRECONDITIONS CLOSED · 0 DETERMINATIONS MADE · ZERO SUBJECTS ARBITRATED · STOPPED AFTER ARTIFACT CREATION.**

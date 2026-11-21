# IMPLEMENT-001C · DELIVERABLE 02 — REMEDIATION EXECUTION REPORT

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001C` — Approved Remediation Execution |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| SCOPE SOURCE | `IMPLEMENT-001B` Deliverable 06 — Approved Remediation Backlog (`RB-01`…`RB-05`) |
| BASELINE | `UCOS-BASELINE-001` · `df763bf917943321886c3fc973eac4a1569b6183` · branch `integration/recovery-001` |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DETERMINATION

> ### ✅ **ALL FIVE APPROVED BACKLOG ITEMS EXECUTED AND DISCHARGED.**
>
> **`verify.sh` GREEN 5/5.** 5 files touched. 2 records written. **0 dispositioned findings
> reopened. 0 new functionality. 0 unrelated cleanup.**

---

## 2. PHASE 0 — AUTHORITIES LOADED · SCOPE ADMISSION

| Authority | Status |
|---|---|
| `UCOS-BASELINE-001` | LOADED |
| `EVOLUTION-001` | LOADED |
| `RELEASE-001` | LOADED |
| `IMPLEMENT-001` (D00, D01) | LOADED — set still incomplete (D02/D03/D04 absent) |
| `IMPLEMENT-001A` (D00–D05) | LOADED |
| `IMPLEMENT-001B` (D00–D09) | LOADED |

### 2.1 Approved items admitted

| Item | Admitted | Source |
|---|---|---|
| `RB-01` Reconcile the DP-03 guard | ✓ | `IMPLEMENT-001B` D06 |
| `RB-02` Register the P-7 work package | ✓ | idem |
| `RB-03` Make schema validation mandatory | ✓ | idem (under existing `WP-UCCEP-004` / `OA-3`) |
| `RB-04` Record the acceptance expected-fail disclosure | ✓ | idem |
| `RB-05` Make `rib.json` convergent | ✓ | idem |

### 2.2 Items **REJECTED** as not explicitly approved

Per the mission mandate — *"Reject any remediation not explicitly approved"* and *"No additional
remediation items may be introduced"* — the following, although named in `IMPLEMENT-001B`
Deliverable 09 §2 as `IMPLEMENT-001C` deliverables, are **not** in the approved remediation
backlog (D06 §1 admission record excluded them) and were **not** executed:

| Named in D09 §2 | Why rejected here |
|---|---|
| Author `IMPLEMENT-001` D02, D03, D04 | Authoring new determinations is content creation, not remediation. D06 §1 did not admit it to the backlog. |
| Correct the `CAEM-001` citation record (`03:72`, `05:31`) | Not a backlog item. `CAEM-001` is another programme's output — **`X-9`: "No cross-programme edits."** |
| Execute the commit sequence | Phase 5 of this mission is *"Commit **Preparation**"* and *"**Determine** commit grouping, ordering, rationale."* A plan, not an execution. |
| `EVOLUTION-001` §2 classification of the change set | Partially discharged as **content of `WP-RO-001` §5**, which `RB-02` requires. Not written into `EVOLUTION-001` itself — that is another programme's artifact (`X-9`). |

Carried forward in Deliverable 08.

---

## 3. PHASE 2 — EXECUTION

### `RB-01` — Reconcile the DP-03 guard · **DISCHARGED**

**⚠ New evidence changed the method.** `IMPLEMENT-001B` D06 authorized two options and preferred
**(a)** narrowing `frozen_paths.py:17` `FROZEN_PREFIXES`, assessing the blast radius as *"1
constant, 2 consumers, existing test coverage."*

Measured before touching anything: **`FROZEN_PREFIXES` / `find_frozen_writes` has 21 call sites**,
which split into two classes:

| Class | Count | Call sites | Correct scope |
|---|---|---|---|
| **A — write-time guards** | **18** | `engine/knowledge/store.py:272` · `engine/compiler/publishing.py:120` · `engine/context/evidence.py:153` · `engine/graph/evidence.py:95` · `engine/graph/architecture/evidence.py:100` · `engine/registry/source.py:92` · `engine/knowledge/ukip/evidence.py:249` · `intelligence/realization/{implementation:91,evidence:250,governance:406}.py` · … | **whole-tree `00-BOOK/` is CORRECT** — an evidence writer must never write into `00-BOOK/SCHEMAS/` |
| **B — change-review gates** | **3** + CI | `platform/universal_validation/rules.py:232` · `platform/validation_intelligence/analyzers.py:344` · `platform/repository_operations/stages.py:278` · plus `ec1-frozen-guard --stdin` in CI | **narrowed scope is correct** — reviewing a changeset against DP-03's actual text |

> Option (a) would have **weakened 18 legitimate security guards to fix one over-broad review
> gate.** That is a regression, not a remediation.

Executed **option (b)** — explicitly approved by D06 — at the review boundary only:

```diff
- | grep -vE '^00-BOOK/(DATA|REGISTRIES|CONTROL-TOWER|PORTAL)/' || true)"
+ | grep -vE '^00-BOOK/(DATA|REGISTRIES|CONTROL-TOWER|PORTAL|SCHEMAS|tools)/' || true)"
```

`.github/workflows/ec1-ci.yml` · +100/−24 (1 functional line; the remainder is the authority
citation required by D06: `REG-AUTO-001` §2 + §3 P3, `STATUS-001:122`, the X-1/X-4/X-5 finding,
and the 21-call-site rationale). **`FROZEN_PREFIXES` is UNCHANGED — all 18 write-time guards are
untouched.**

**Mandatory P-7 negative-path proof — executed:**

```
NEGATIVE PATH — still rejected: 6 / 6   (00-SOURCE/*.docx · 99-FREEZE/FREEZE-NOTICE.md ·
                                         99-FREEZE/SOURCE-HASHES.txt ·
                                         00-BOOK/UCOS-BOOK-000000-*.md ·
                                         00-BOOK/MASTER-BOOK/* · 00-BOOK/ADVANCEMENT/*)
POSITIVE PATH — now allowed  : 9 / 9   (SCHEMAS/ · tools/ · DATA/ · REGISTRIES/ ·
                                         CONTROL-TOWER/ · PORTAL/ · engine/ · platform/ · verify.sh)
this change set under the corrected gate: CLEAN (0 violations)   [was 14]
FROZEN_PREFIXES unchanged: ('00-BOOK/', '00-SOURCE/', '99-FREEZE/')
```

X-1 and the authored `00-BOOK` canon remain protected. Discharges `CF-01`, `CF-02`.

---

### `RB-02` — Register the P-7 work package · **DISCHARGED**

Created `00-MASTER/IMPLEMENT-001C/00-WP-RO-001-WORK-PACKAGE.md`. **0 lines of code.**

Home is `00-MASTER/IMPLEMENT-001C/` under **P-5** (*"Programme-owned outputs … own directory
only"*) — deliberately **not** `uccep-bindings.json`, which **`X-9`** forbids editing.

| Content | Delivered |
|---|---|
| Non-shadowing token | **`WP-RO-001`**, finding prefix **`RO-F-NN`**, both `T-M` under `NF-3` (*"requires no admission, because it claims no identity"*). Not `EIP-018` — that already denotes the USIS establishment mission (`UCOS-USIS-001/00:7`) and is cited for it in committed `config.py:69,265,787`. Discharges `CF-06` / `NF-4`. |
| Finding register | `RO-F-01`…`RO-F-06`, **cardinality closed at 6**, each mapped to its legacy `FP-N` citation and evidenced from committed `HEAD` |
| Declared additive surfaces | 7 paths |
| Negative-path evidence | 3 named tests + the observed live failures |
| P-7 conditions | **4 of 4 MET** |
| `EVOLUTION-001` §2 classification | delivered in §5 |

Legacy `EIP-018 (FP-N)` comments **retained** — `GOV-002` §6/`RA5` make code citations
traceability evidence to preserve. Discharges `C-1d`, the `C-4` residue, `CF-04`, `CF-06`.

---

### `RB-03` — Make schema validation mandatory · **DISCHARGED**

| File | Change |
|---|---|
| `pyproject.toml` | `+12/−0` — added `"jsonschema==4.26.0"` to `[project.optional-dependencies].dev` with the `UCCEP-F-006`/`WP-UCCEP-004`/`OA-3`/`CF-03` citation |
| `.github/workflows/ucos-registration-gate.yml` | `+8/−2` — `pip install jsonschema \|\| true` → `pip install -e ".[dev]"` |

**One edit, both effects.** `ucos_expected_deps()` (`scripts/ucos-env.sh:104-120`) *derives* the
required set by parsing that exact list, so no second edit and no hardcoded list was needed.
Verified:

```
pytest 8.3.4 · pytest_cov 6.0.0 · coverage 7.15.2 · ruff 0.8.4 · jsonschema 4.26.0
```

`jsonschema` is now installed and version-verified by `ucos_ensure_venv`. Pinned to the version
already present, so no behavioural change. `verify.sh` Stage 5 reports
`"jsonschema validation: ran."`

`ukb.py:1733-1735`'s `ImportError` branch was **left intact** — making it fail-closed is
`WP-UCCEP-004`'s own titled scope over another programme's file (`X-9`), and pinning the
dependency makes the branch unreachable in every governed environment. Discharges `CF-03`.

---

### `RB-04` — Record the acceptance expected-fail disclosure · **DISCHARGED**

Created `00-MASTER/IMPLEMENT-001C/01-REPOSITORY-ACCEPTANCE-DISCLOSURE.md`. **0 lines of code.**

Records: the deliberate fail-closed cause (6 required dimensions vs 2 measurable); that the prior
PASS was **vacuous** (HEAD declared six × `covered:1/total:1`); that `repo-ops.sh` is bound to
**no** gate (verified against `verify.sh`, `RELEASE-001` §4, `G-01…G-15`, `uccep.json`, all 12
workflows); the pre-existing `SPECIFICATION_GAP` ownership record; and **three named owners** for
closure. Discharges `C-2.1`.

---

### `RB-05` — Make `rib.json` convergent · **DISCHARGED**

`00-MASTER/UCOS-RIB-001/rib_engine.py` · `+17/−2` (2 functional lines removed).

Verified **before** removing: `dirty_paths` was **write-only** — produced at `observed_state()`,
defaulted in `FIXED_STATE`, **read by no code path and rendered into no output artifact.** The
removal is purely subtractive.

`dirty_entries`, `modified`, `deleted`, `untracked` are **retained** — `GATE-12` and
`GATE-04`/`VAL-02` measure `dirty_entries_outside_generated`, a scalar. Only the ~80-entry list
was removed, shrinking the churn surface from 80 lines to 1 scalar.

**Convergence proof:**

```
make rib-gate ; cp rib.json /tmp/r1 ; make rib-gate ; cp rib.json /tmp/r2 ; cmp r1 r2
  → BYTE-IDENTICAL across two runs ✓
dirty_paths in rib.json: 0 occurrences (removed)
repository: {'dirty_entries': 85, 'modified': 73, 'untracked': 12, 'working_tree': 'DIRTY'}
```

Discharges `C-5`, `CF-07`.

#### `RB-05` self-inflicted regression — caught and corrected

My first `rib_engine.py` comment named `GATE-12`, `VAL-02` and `IMPLEMENT-001B` verbatim. The
engine's own `--check-no-enumeration` guard **correctly rejected it**:

```
UCOS-RIB-001 check-no-enumeration: FAIL
  - engine source special-cases declared value 'GATE-12'
  - engine source special-cases declared value 'IMPLEMENT'
  - engine source special-cases declared value 'VAL-02'
```

The comment was rewritten without those tokens. **All 8 RIB self-guards now PASS**:
`--check-declaration` · `--check-no-enumeration` · `--check-write-scope` ·
`--check-determinism` · `--check-substrate` · `--check-no-fabrication` ·
`--check-reuse-before-create` · `--check-totality`.

Recorded because it is evidence the zero-enumeration guard works, and because a report claiming
a clean first pass would be false.

---

## 4. CHANGE SCOPE — exactly the approved set

| File | +/− | Item | New surface? |
|---|---|---|---|
| `.github/workflows/ec1-ci.yml` | +100/−24 | `RB-01` | no — already in the inherited 86 |
| `pyproject.toml` | +12/−0 | `RB-03` | **yes** |
| `.github/workflows/ucos-registration-gate.yml` | +8/−2 | `RB-03` | **yes** |
| `00-MASTER/UCOS-RIB-001/rib_engine.py` | +17/−2 | `RB-05` | **yes** |
| `00-MASTER/UCOS-RIB-001/rib.json` | +56/−31 | `RB-05` (regenerated) | no — already in the 86 |
| `00-MASTER/IMPLEMENT-001C/00-WP-RO-001-…md` | new | `RB-02` | new record |
| `00-MASTER/IMPLEMENT-001C/01-…-DISCLOSURE.md` | new | `RB-04` | new record |

**Modified tracked files: 86 → 89.** The 3 additions are exactly `pyproject.toml`,
`ucos-registration-gate.yml`, `rib_engine.py` — the approved surfaces and nothing else.

**Functional lines changed: 6.** (1 regex · 1 dependency pin · 1 workflow install · 2 removed
dict entries · 1 removed default.) Everything else is authority citation.

---

## 5. CONSTRAINT COMPLIANCE

| Constraint | Verdict |
|---|---|
| Only approved remediations implemented | ✓ — 5 of 5; 4 unapproved items rejected (§2.2) |
| No dispositioned finding reopened | ✓ — `RB-01`'s *method* changed on new evidence (permitted: *"unless new evidence is discovered"*); its **disposition (FIX) is unchanged**, as is every other |
| No new functionality | ✓ — 1 regex extension, 1 dependency pin, 1 install command, 2 dict-key removals. No new function, class, module, CLI flag, or capability. |
| No unrelated cleanup | ✓ — 3 new surfaces, all approved. The `uar_engine.py` `F401`, the traceability gap, and the UAR defects were all left untouched. |
| No architecture modified | ✓ — no interface, contract, or module boundary changed |
| No constitutional scope expanded | ✓ — `RB-01` **narrowed** a guard to match its authority; `X-9` observed throughout (no edit to `uccep-bindings.json`, `CAEM-001`, or `EVOLUTION-001`) |
| Deterministic behaviour preserved | ✓ — `rib.json` byte-identical across runs; UCCEP seal `68e8d9a2d396f3dc` **unchanged from before remediation**; all peer self-guards PASS |
| `verify.sh` passes | ✓ — 5/5, exit 0, coverage 94.28% |

---

## 6. DETERMINATION

> **`RB-01` · `RB-02` · `RB-03` · `RB-04` · `RB-05` — ALL DISCHARGED.**
>
> 6 functional lines. 5 files. 2 records. `verify.sh` GREEN.
>
> Two things went differently from the plan, both recorded rather than smoothed over:
> `RB-01` used its approved alternative because the preferred option would have weakened 18
> security guards; and `RB-05`'s first attempt tripped the target engine's own
> zero-enumeration guard and had to be rewritten.

---

*END — `IMPLEMENT-001C` Deliverable 02 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*

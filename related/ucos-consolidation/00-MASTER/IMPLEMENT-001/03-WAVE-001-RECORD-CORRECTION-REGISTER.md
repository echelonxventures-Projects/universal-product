# IMPLEMENT-001 · DELIVERABLE 03 — WAVE-001 RECORD CORRECTION REGISTER

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001` — First Production Implementation Mission |
| AUTHORITY | `NONE — DERIVED TRUTH` — this register **defines** corrections; it executes none |
| AUTHORED BY | `IMPLEMENT-001E` — IMPLEMENT-001 Closeout (Phase 2) |
| CITED BY | Deliverable 00 §3, line 180: *"only the finding **record** lags at status `GOVERNED` — see **`W1-C3` in Deliverable 03**"* |
| SUBJECT REGISTER | `00-MASTER/UCCEP-000000/uccep-bindings.json` → `findings[]` (8) · `work_packages[]` (5) |
| REPOSITORY ANCHOR | the containing commit — owned by version control, never restated here (`UCOS-RFP-001` RFP-2) |
| MEASURED AT | `8aede74` · working tree clean · `verify.sh` GREEN 5/5 |
| CARDINALITY | **`W1-C3` only. Closed at 1.** (§3) |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`) |

> **This deliverable performs no correction.** Every finding disposition in
> `uccep-bindings.json` is `UCCEP-000000`'s to set — *"A finding is discharged only by its named
> owner — UCCEP discharges nothing itself"* (`uccep-bindings.json` `$findings_comment`). Writing
> into it from here would be **`X-9`**, the same prohibition on which `IMPLEMENT-001C` D08 §2.1
> rejected this exact edit. D03 states **what** must change, **who** may change it, and **the
> evidence that entitles the change**.

---

## 1. THE `W1-C` SERIES — WHAT IT IS AND HOW IT IS NUMBERED

D00 cites `W1-C3` by number without ever citing `W1-C1` or `W1-C2`. A repository-wide search
returns `W1-C3` and no other member. Two readings are possible; only one is consistent.

| Reading | Implication | Verdict |
|---|---|---|
| **Sequential** — `W1-C1`, `W1-C2`, `W1-C3`, … | Two earlier members must exist. Nothing anywhere defines or cites them. D00 would be citing the third element of a series whose first two are unrecorded. | ⛔ **REJECTED** — would require fabricating two corrections to justify a numbering scheme |
| **Finding-indexed** — `W1-C<N>` ≡ the Wave-001 record correction for `UCCEP-F-00<N>` | `W1-C3` ↔ `UCCEP-F-003`. The absence of `W1-C1`/`W1-C2` is then not a gap but a **fact**: `UCCEP-F-001` and `UCCEP-F-002` need no record correction, because they are `EB-07` and `EB-08` — open work, not lagging records. | ✅ **ADOPTED** |

**Corroboration.** D00 §3 introduces `W1-C3` in its *Completed work* exclusions table, in the row
for `UCCEP-F-003`, with the words *"The code is fixed; only the finding **record** lags."* The
correction is bound to that finding, and the index matches. The scheme is therefore
finding-indexed, and `W1-C<N>` is defined for exactly those `N` that pass §2's membership test.

**Identifier class.** `W1-C3` is a **`T-M` (mission-local)** identifier under `NF-3`: declared in a
mission artifact with stated cardinality, claiming no identity. It is never presented to
`REG-AUTO-001`, never entered in `id-ledger.json`, and allocates nothing (`NF-1`). Cardinality is
declared and closed in §3.

---

## 2. THE MEMBERSHIP TEST

A finding is a `W1-C` member **iff both** clauses hold. Both are measured, not asserted.

| Clause | Statement |
|---|---|
| **M-1 — substance discharged** | The finding's **named work package acceptance condition** is satisfied in committed code or committed state at this HEAD. Not *"a fix was attempted"*; the acceptance sentence the work package itself states must be true. |
| **M-2 — record understates it** | The finding's `disposition` field still records a state weaker than `IMPLEMENTED`, so the register reports a defect that no longer exists. |

> **M-1 is deliberately the work package's own acceptance sentence, not this mission's judgement of
> "fixed enough".** That is what makes the test falsifiable. Three findings looked like members on
> a reading of *"the code was changed"*; only one survives a reading of *"the acceptance condition
> is met"*. §4 records the two that failed, because a rejected candidate is evidence too.

---

## 3. THE REGISTER — `W1-C3`, AND NOTHING ELSE

### `W1-C3` — `UCCEP-F-003` graph fail-open: record lags behind a discharged gate

| Field | Determination |
|---|---|
| **Correction id** | `W1-C3` (`T-M`, `NF-3`) |
| **Finding** | `UCCEP-F-003` — *"`engine.graph.cli validate` reports a dependency cycle but returns `is_valid=true` and exit 0 (fail-open)"* · class `FAIL-OPEN-GATE` |
| **Work package** | `WP-UCCEP-003` — *"Make the traceability-graph validator fail closed on a reported cycle"* |
| **Named owner** | `engine/graph` (`UCOS-EPIC-002`) for the substance · **`UCCEP-000000`** for the record field |
| **Violations cited by the finding** | `PR-09` Universal Composition · `PR-13` Universal Traceability · `CEP-009` Art XV.2 · `CEP-009` Art XX.2 |
| **Declared acceptance** | *"`engine.graph.cli validate` exits non-zero while any cycle is reported, and exits 0 once the cycle is resolved."* — two clauses |
| **Current `disposition`** | **`GOVERNED`** · `blocking: true` |
| **Required transition** | `GOVERNED` → **`IMPLEMENTED`** · `blocking: true` → `false` |

**M-1 — substance discharged. Both acceptance clauses verified at `8aede74`:**

| Clause | Evidence | Verdict |
|---|---|---|
| *exits non-zero while any cycle is reported* | `engine/graph/validation.py` — the `is_valid` property includes `dependency_cycle` in its disjunction, with a docstring that names `UCCEP-F-003` and states *"`dependency_cycle` is a validity FAILURE, not a finding"*, citing `CEP-009` Art XV.2 / XX.2. `engine/graph/cli.py:123` — `return 0 if report.is_valid else 1`. So a reported cycle ⇒ `is_valid` false ⇒ exit 1. | ✅ **MET** |
| *exits 0 once the cycle is resolved* | The finding's located root cause was a mutual `Depends-On` between `UCOS-ENG-000008` (ENG-004 Universal Type System) and `UCOS-ENG-000007` (ENG-005 Universal Relationship & Reference System) via edge `UEDGE-000003640`. Live: `engine.graph.cli validate` → `dependency_cycle: []`, `is_valid: true`, exit **0**, over 1,218 nodes / 12,829 edges. Both the DATA and GATE legs of the declared route are complete. | ✅ **MET** |
| *independent execution record* | `00-MASTER/UCCEP-000005/02-DEPENDENCY-REMEDIATION-REPORT.md` records `T-2` *"GATE correction — `engine/graph/validation.py` (+ its test)"* as **EXECUTED**, with the diff retained at `00-MASTER/UCCEP-000005/evidence/post/T-2-validation-gate.diff`. `validation.py`'s own docstring attributes the discharge to *"`WP-UCCEP-003` T-2 / `UCCEP-000005`"*. | ✅ **CORROBORATED** |

**M-2 — record understates it.** `uccep-bindings.json` `findings[]` still carries
`"disposition": "GOVERNED"` and `"blocking": true` for `UCCEP-F-003`. `GOVERNED` denotes a
condition held under governance pending discharge — the finding's own `note` reads *"The fail-open
exit code remains the owner's to correct."* **It has been corrected.** The register therefore
reports a fail-open gate that measurably no longer exists.

**Consequence of leaving it.** `blocking: true` means this finding blocks **certification**
(`$findings_comment`: *"'blocking' declares whether the finding blocks CERTIFICATION (not
progress)"*). A discharged defect held `blocking` understates the repository's certification
standing, and every future `uccep-gate` run re-asserts a defect that is gone.

**Execution instruction — for `UCCEP-000000`, not for this mission.**

| Step | Act |
|---|---|
| 1 | In `00-MASTER/UCCEP-000000/uccep-bindings.json`, `findings[]`, entry `UCCEP-F-003`: set `disposition` `GOVERNED` → `IMPLEMENTED`; set `blocking` `true` → `false`. |
| 2 | Retain `evidence`, `violates`, `owner`, `work_package` **verbatim** — append-only; the historical record of the defect is not deleted. |
| 3 | Update `note` to record the discharge and cite `WP-UCCEP-003` T-2 / `UCCEP-000005` and `evidence/post/T-2-validation-gate.diff`. |
| 4 | Regenerate the 21 `UCCEP-000000` projections; commit declaration and projections **atomically** (`REG-AUTO-001`: source is never split from projections; `CK-REG-DRIFT` exists to detect the split). |
| 5 | Confirm `make uccep-gate` still exits 0 with `blocking=none`, and that the emitted seal changes only as the disposition change requires. |

**Constitutional route.** `P-5` — a programme editing its own declaration inside its own home.
`WP-UCCEP-003` already exists, so no new work package is required. Not `P-7`: nothing freeze-gated
is touched.

---

## 4. CANDIDATES TESTED AND REJECTED

Both were carried as probable members by earlier missions. Both **fail M-1** against their own
work package's acceptance sentence. Their dispositions are therefore **correct as recorded**, and
no correction is due.

### 4.1 `UCCEP-F-006` — schema validation: pinned, but the code can still degrade silently

| Field | Value |
|---|---|
| Finding | *"`ukb validate` degrades to structural-only checks when `jsonschema` is absent"* · class `DEGRADED-VALIDATION` |
| Work package | `WP-UCCEP-004` · **acceptance: *"`ukb validate` cannot report PASS while its schema checks were skipped."*** |
| Current disposition | `REGISTERED` · `blocking: false` |
| **Verdict** | ⛔ **NOT A MEMBER — M-1 FAILS** |

`WP-UCCEP-004`'s route has three legs. Two are done; the third is not.

| Route leg | State | Evidence |
|---|---|---|
| *Pin `jsonschema` in the dev dependency set* | ✅ **DONE** | `pyproject.toml:43` `jsonschema==4.26.0`; `ucos_expected_deps()` parses `[project.optional-dependencies].dev` with `tomllib`, so `ucos_ensure_venv` installs and verifies it with no second declaration |
| *Remove the `\|\| true` from the CI install* | ✅ **DONE** | `.github/workflows/ucos-registration-gate.yml` — `pip install jsonschema \|\| true` → `pip install -e ".[dev]"` |
| *Have `ukb validate` declare a reduced-scope run as a **finding** rather than a silent note* | ⛔ **NOT DONE** | `00-BOOK/tools/ukb.py` still holds `except ImportError: print("jsonschema not installed — ran structural checks only …")`. The branch appends **nothing** to `problems`, so the run still reaches `VALIDATION PASSED` and exits **0**. |

**Therefore the acceptance sentence is false as a property of the code.** `ukb validate` *can*
still report PASS while its schema checks were skipped. What changed is the *likelihood*, not the
*possibility*: `verify.sh` Stage 5 invokes `"$PY"` (the guaranteed venv) so that path is safe, but
**82 `Makefile` recipes invoke bare `python3`**, and `ukb.py validate` run under any interpreter
lacking `jsonschema` still degrades and still exits 0. On this machine both interpreters happen to
carry `jsonschema 4.26.0`, so the degradation is **latent, not active** — which is exactly why it
must stay `REGISTERED` rather than be marked `IMPLEMENTED`.

`IMPLEMENT-001C` recorded this boundary deliberately: `RB-03` *"did not alter `ukb.py`'s
`ImportError` branch"*, on `X-9` grounds — `ukb.py` is the registration authority's surface.
**Residual work, owner `00-BOOK/tools/ukb.py`. Carried to Wave-002 in D04 §5.**

### 4.2 `UCCEP-F-007` — the tree is committed, but the registration half of acceptance is not met

| Field | Value |
|---|---|
| Finding | *"Working tree carries uncommitted constitutional zone and generator changes"* · class `REPOSITORY-DRIFT` |
| Work package | `WP-UCCEP-005` · **acceptance: *"`register.sh --guard` exits 0 with zero drift; `git status` reports no uncommitted registration."*** — two clauses |
| Current disposition | `REGISTERED` · `blocking: false` |
| **Verdict** | ⛔ **NOT A MEMBER — M-1 FAILS on clause 1** |

| Acceptance clause | State at `8aede74` | Verdict |
|---|---|---|
| *`git status` reports no uncommitted registration* | Working tree clean — **0** entries. Discharged by the `UCOS-EVO-001-W01` commit sequence. | ✅ **MET** |
| *`register.sh --guard` exits 0 with zero drift* | Measured: a registration transaction rewrites **731** tracked files, `+7,995 / −7,767`. | ⛔ **NOT MET** |

> **`WP-UCCEP-005`'s first acceptance clause and `B-2` Registration Fixed Point are the same
> condition.** This is the single most consequential finding of `IMPLEMENT-001E`. `IMPLEMENT-001C`
> D06 §5 listed `OA-1 · O-01 · UCCEP-F-007 · WP-UCCEP-005` as **DISCHARGED** by the commit
> sequence. Against the work package's own acceptance sentence that is **half true**: the commit
> discharged the `git status` clause and left the `register.sh --guard` clause standing. The
> disposition `REGISTERED` is therefore correct, and marking it `IMPLEMENTED` would have recorded
> a discharge that measurement contradicts.

`UCCEP-F-007` is discharged **when and only when `B-2` is discharged**. See D04 §3.

---

## 5. COMPLETE FINDING AUDIT — ALL 8, TOTAL AND EXHAUSTIVE

Every finding in the subject register is assigned. No finding is unexamined.

| Finding | Disposition | Blocking | M-1 substance discharged? | M-2 record understates? | Member | Where it belongs instead |
|---|---|---|---|---|---|---|
| `UCCEP-F-001` | `WORK-PACKAGE` | true | ⛔ **NO** — `phase3_engine.py:546` `repository_status` is still the literal `"NOT-CLOSED"`, contradicting `closure-gate`'s `CLOSED` | n/a | ⛔ | **`EB-07`** — open executable work, Wave-002 order 1 |
| `UCCEP-F-002` | `REGISTERED` | true | ⛔ **NO** — traceability measured **348/15,509 = 2.24%**; complete=0, partial=272, empty=921 | n/a | ⛔ | **`EB-08`** — open executable work |
| **`UCCEP-F-003`** | **`GOVERNED`** | **true** | ✅ **YES** — both acceptance clauses met (§3) | ✅ **YES** | ✅ **`W1-C3`** | — |
| `UCCEP-F-004` | `REGISTERED` | true | ⛔ **NO** — Tier T1 is VACANT; requires `DR-RAT-11`, an **external constituent act** outside the corpus. No in-repo discharge is possible. | n/a | ⛔ | Standing vacancy `VAC-01`; every determination in this repository is `CERTIFIED-PROVISIONAL` because of it |
| `UCCEP-F-005` | `IMPLEMENTED` | false | ✅ yes | ⛔ **NO** — already `IMPLEMENTED`; nothing to correct | ⛔ | Closed |
| `UCCEP-F-006` | `REGISTERED` | false | ⛔ **NO** — third route leg not done; `ukb.py` `ImportError` branch still exits 0 (§4.1) | n/a | ⛔ | Residual defect → Wave-002, D04 §5 |
| `UCCEP-F-007` | `REGISTERED` | false | ⛔ **NO** — acceptance clause 1 (`register.sh --guard` zero drift) unmet: 731 files (§4.2) | n/a | ⛔ | **Identical to `B-2`** → D04 §3 |
| `UCCEP-F-008` | `IMPLEMENTED` | false | ✅ yes | ⛔ **NO** — already `IMPLEMENTED` | ⛔ | Closed |

**Partition: 1 member · 2 open executable items · 1 external constituent act · 2 already closed ·
1 residual defect · 1 identical to `B-2`. Total 8 of 8.**

### 5.1 Work-package coverage

| Work package | Discharges | Acceptance met at `8aede74`? |
|---|---|---|
| `WP-UCCEP-001` | `UCCEP-F-001` | ⛔ no — `EB-07` |
| `WP-UCCEP-002` | `UCCEP-F-002` | ⛔ no — `EB-08` |
| `WP-UCCEP-003` | `UCCEP-F-003` | ✅ **yes — hence `W1-C3`** |
| `WP-UCCEP-004` | `UCCEP-F-006` | ⛔ no — 2 of 3 route legs |
| `WP-UCCEP-005` | `UCCEP-F-007` | ⛔ no — 1 of 2 acceptance clauses; the unmet clause **is** `B-2` |

**5 of 5 work packages examined. 1 satisfied.**

---

## 6. DETERMINATION

> ### ✅ **THE `W1-C` SERIES IS DEFINED. CARDINALITY: 1. MEMBER: `W1-C3`.**
>
> The series is **finding-indexed**, not sequential — which is why `W1-C1` and `W1-C2` are absent
> from the repository. They are absent because they **do not exist**: `UCCEP-F-001` and
> `UCCEP-F-002` are `EB-07` and `EB-08`, open work rather than lagging records. D00's citation of
> `W1-C3` as the only named member was correct.
>
> **`W1-C3` is entitled to its correction.** `WP-UCCEP-003`'s acceptance sentence is met on both
> clauses: `engine/graph/cli.py:123` exits non-zero when `is_valid` is false, `validation.py` makes
> `dependency_cycle` a validity failure naming `UCCEP-F-003`, the located `ENG-004`↔`ENG-005` cycle
> is gone (`dependency_cycle: []` over 12,829 edges), and `UCCEP-000005` T-2 records the execution
> with a retained diff. The register still says `GOVERNED` / `blocking: true`. Required transition:
> **`GOVERNED` → `IMPLEMENTED`, `blocking` → `false`**, by `UCCEP-000000` under `P-5`.
>
> **Two candidates were rejected on measurement, and that is the more useful result.**
> `UCCEP-F-006` fails because `ukb.py`'s `ImportError` branch still reaches `VALIDATION PASSED`
> with exit 0 — the pin reduced the likelihood of silent degradation, not its possibility.
> `UCCEP-F-007` fails because **its acceptance clause 1 is `B-2` itself**, and `B-2` is open at 731
> files. `IMPLEMENT-001C` D06 §5 recorded `UCCEP-F-007` as discharged; against the work package's
> own words it is **half discharged**, and this register says so.
>
> **This deliverable executed nothing.** `uccep-bindings.json` is unmodified. All 8 findings and
> all 5 work packages are assigned, with no residue.

---

*END — `IMPLEMENT-001` Deliverable 03 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*

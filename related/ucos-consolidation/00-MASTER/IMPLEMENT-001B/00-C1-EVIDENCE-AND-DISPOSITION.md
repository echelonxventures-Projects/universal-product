# IMPLEMENT-001B · DELIVERABLE 00 — C-1 EVIDENCE & DISPOSITION

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001B` — Blocking Findings Disposition & Closure |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| FINDING | **C-1** — *"14 frozen-corpus writes without a `CEP-009` amendment"* (`IMPLEMENT-001A` D00 §5.1) |
| METHOD | Independent reproduction. Every cited authority opened and read. No conclusion reused. |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DETERMINATION

> ### C-1 is **PARTIALLY VALID**, and its constitutional basis is **DISPROVED**.
>
> The physical write is real. The authority `IMPLEMENT-001A` cited for calling it a violation
> does not say what was claimed. Both citations — *"protected area X-1"* and *"requires a
> `CEP-009` amendment route"* — are **factually wrong**, and both were inherited from
> `CAEM-001` without verification.
>
> C-1 also **under-reported the write set by 7 files.**

C-1 is split into four sub-findings because the 21 affected paths have four different
constitutional standings. A single verdict over them would be wrong in three of the four cases.

| Sub-finding | Paths | Verdict | Disposition |
|---|---|---|---|
| **C-1a** | `00-BOOK/tools/config.py` (1) | **INVALID** | **REJECT** |
| **C-1b** | `00-BOOK/SCHEMAS/*.schema.json` (13) | **PARTIALLY VALID** — permitted write, unregistered | **ACCEPT (reclassified)** → discharged by `OA-1` |
| **C-1c** | `engine/foundation/guards/frozen_paths.py` | **NEW — IMPLEMENTATION DEFECT** | **FIX** |
| **C-1d** | `platform/**` (7) — *missed by C-1* | **NEW — VALID** | **FIX** (register a work package) |

---

## 2. PHASE 1 — EVIDENCE RECONSTRUCTION (reproduced, not reused)

### 2.1 The physical write set

```
engine.foundation.guards.frozen_paths.find_frozen_writes(<86 changed paths>)
  → 14 violations
```

13 × `00-BOOK/SCHEMAS/{artifact,build,deployment,export-job,finding,flow,journey,page,
relationship,repository,signal,ui-artifact,volume}.schema.json` + `00-BOOK/tools/config.py`.

Independently corroborated: `./repo-ops.sh` → `FAILED architecture-freeze · 14 frozen-corpus
write(s) detected`.

**Reproduced. The number 14 is correct.**

### 2.2 The write set C-1 MISSED

`00-MASTER/UCCEP-000006/06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md:41`:

```
| X-8 | `engine/**` · `platform/**` freeze-gated surfaces | EC-1 freeze + coverage gate
      | No mutation except under P-7 |
```

The change set modifies **7 files under `platform/**`**:
`platform/repository_operations/{engine,stages}.py` and
`platform/tests/test_repository_operations_{cli,engine,service,stages}.py`.

`frozen_paths.py:17` declares `FROZEN_PREFIXES = ("00-BOOK/", "00-SOURCE/", "99-FREEZE/")` —
**it does not cover `platform/` or `engine/`.** `IMPLEMENT-001A` measured the write set with
that tool and therefore inherited the tool's blind spot.

> **The true freeze-gated write set is 21 files, not 14.** C-1 under-reported by 7.
> This is recorded as **C-1d** below.

### 2.3 Affected artifacts, engines, gates, registries

| Dimension | Measured |
|---|---|
| **Registered artifacts affected** | **13** — `UCOS-REG-000001, 000003, 000004, 000006, 000007, 000009, 000011, 000012, 000013, 000014, 000016, 000017, 000019`. All 13 have `content_hash` in `artifacts.json` that no longer matches disk. Computed by re-hashing each file and comparing. |
| Registered artifacts under `00-BOOK/tools/` | **0** of 1,193 |
| Registered artifacts under `00-BOOK/SCHEMAS/` | **19** (13 modified, 6 untouched) |
| **Engines affected** | `frozen_paths.py` (guard) · `ukb.py` (consumes `config.py` + `SCHEMAS/`) · `platform.repository_operations.stages` (freeze stage) |
| **Gates affected** | `ec1-ci.yml` DP-03 step (**would fail**) · `repo-ops.sh` `architecture-freeze` (**fails**) · `CK-REG-DRIFT` / `G-07` (content-hash drift) · `verify.sh` (**passes** — Stages 4/5 do not check content_hash) |
| **Registries affected** | `artifacts.json` — 13 stale `content_hash` values → source/projection split, the exact condition `REG-AUTO-001` forbids |

---

## 3. PHASE 2 — CONSTITUTIONAL REVIEW

### 3.1 ⛔ CITATION ERROR 1 — `00-BOOK` is **NOT** protected area X-1

`IMPLEMENT-001A` D00 §5.1 relied on `CAEM-001/03-HARD-CODED-ASSUMPTION-REGISTER.md:72`:

> *"`00-BOOK/**` is frozen read-only under **DP-03** and is protected area **X-1**."*

The X-1…X-10 register exists in exactly one place —
`00-MASTER/UCCEP-000006/06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md:34`, read verbatim:

```
| X-1 | `00-SOURCE/` · `00-SOURCE-MANIFEST/` · `99-FREEZE/`
      | `99-FREEZE/FREEZE-NOTICE.md` — Status: FROZEN, 13 source files
      | No source document may be modified. Read-only, absolutely |
```

**`00-BOOK` does not appear in X-1.** Across the entire X-1…X-10 register, `00-BOOK` appears
exactly twice, both narrowly scoped:

| | Path | Rule |
|---|---|---|
| **X-4** | `00-BOOK/DATA/id-ledger.json` | No hand edit |
| **X-5** | `00-BOOK/DATA/*` page ledger and change ledger | Append-only |

**Neither `00-BOOK/SCHEMAS/` nor `00-BOOK/tools/` appears in any protected area.**

The register's own basis column cites `99-FREEZE/FREEZE-NOTICE.md`. I read it: it freezes
`00-SOURCE/` and names **13 files**, all `.docx` under `00-SOURCE/`. `grep -c "00-BOOK"
99-FREEZE/SOURCE-FILES.txt` → **0**. The freeze notice never mentions `00-BOOK`.

> **The X-1 citation is false.** It attributes to a register a scope the register does not have.

### 3.2 ⛔ CITATION ERROR 2 — `CEP-009` has **no jurisdiction** over this

`CAEM-001:72` concluded: *"It requires a `CEP-009` amendment route."*

I read `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md`:

| Clause | Verbatim |
|---|---|
| line 13 | `SCOPE OF GOVERNANCE \| HOW amendment and evolution operate — amendment and evolution only` |
| line 17 | *"It **SHALL NOT** legislate governance, execution, validation, certification, ratification, **freeze**, or evidence creation; those are reserved to their respective constitutions."* |
| **II.2** (line 53) | *"This instrument **SHALL NOT** legislate governance, execution, validation, certification, ratification, **freeze**, or evidence creation."* |
| **II.5** (line 59) | *"Amendment and evolution jurisdiction SHALL be bounded to this instrument alone and **SHALL NOT overlap the jurisdiction of** ratification (CEP-006), **freeze (CEP-007)**, or evidence and traceability (CEP-008)."* |
| **V.1** (line 96) | *"An artifact SHALL be eligible for amendment only when it is **ratified or frozen** and its lineage is intact."* |

Measured: `grep -icE "schema|\.json|00-BOOK|code|tool|configuration"` over CEP-009 → **0**.
CEP-009 names no repository path, no schema, no tool, no configuration.

Three independent reasons the citation fails:

1. **Wrong jurisdiction.** Freeze is expressly reserved to CEP-007 by II.2 and II.5. A freeze
   question cannot be routed to CEP-009.
2. **Eligibility unmet.** V.1 admits amendment only of a **ratified or frozen** artifact. The
   13 schemas are neither: they are absent from the freeze manifest and no ratification record
   names them.
3. **Subject matter absent.** CEP-009 legislates successor creation over constitutional
   artifacts. It says nothing about JSON schema files.

And CEP-007 — `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md`, the actual Freeze
Constitution — **contains no repository path at all** and freezes no tree.

> **The `CEP-009` citation is false.** No amendment is required because CEP-009 has no
> jurisdiction and the artifacts are not eligible subjects.

### 3.3 What authority DOES cover `00-BOOK/`?

I traced the full chain. The result is uncomfortable but unambiguous.

| Layer | Instrument | Declared AUTHORITY | Says `00-BOOK` is read-only? |
|---|---|---|---|
| Freeze manifest | `99-FREEZE/FREEZE-NOTICE.md` | the freeze instrument | **NO** — `00-SOURCE/` only, 13 files |
| Freeze Constitution | `00-CEP/CEP-007` | normative constitutional law | **NO** — names no path |
| Amendment Constitution | `00-CEP/CEP-009` | normative, subordinate to CEP-000…008 | **NO** — disclaims freeze; names no path |
| Protected-area register | `UCCEP-000006` Output 6 | **`NONE — DERIVED TRUTH`** — *"restates constraints already imposed by located instruments; it invents none"* | **NO** — X-4/X-5 cover `00-BOOK/DATA/` only |
| Execution methodology | `UCIC-001` Stage 4 | **`NONE — DERIVED TRUTH`** — *"creates no new authority; bindingness flows from the instruments it composes"* | **partially** — *"`00-BOOK/**` **source**"* (not all of `00-BOOK`) |
| Master context | `MCP-001` §02 | **`NONE — DERIVED TRUTH`** | yes — restatement |
| ~15 × `02-MASTER/` determinations | CIOA, CCE, EC-2, AEOS, charters | all **`AUTHORITY \| NONE`** / `ENGINEERING-EXECUTION-ONLY` | yes — identical boilerplate |
| **Executable guard** | **`engine/foundation/guards/frozen_paths.py:17`** | **code** | **YES — `FROZEN_PREFIXES = ("00-BOOK/", "00-SOURCE/", "99-FREEZE/")`** |

> **The only instrument in the repository that freezes `00-BOOK/` as a tree is executable code.**
> Every prose statement to that effect holds `AUTHORITY = NONE` and is a restatement of DP-03,
> whose own authoritative text (`UCIC-001:73`) says `00-BOOK/**` **source** — materially
> narrower than the whole tree.

### 3.4 The overriding authority — four instruments AUTHORIZE additive schema edits

Located in `00-BOOK/CONTROL-TOWER/`, the owning standards for the schema surface:

| Instrument | Verbatim authorization |
|---|---|
| `STATUS-001:122` | *"**Add an optional `domain` field** to the existing `dimension` `$def` in `control-tower.schema.json` (**additive; existing data remains valid**)"* |
| `STATUS-001:139` | *"`status.schema.json`: add an optional `domain` enum property (additive)"* |
| `GOV-INT-001:308` | *"**Add additive schemas** (`change/knowledge/regeneration/rollback.schema.json`) — append-only under the schema volume"* |
| `UCI-001:37` | *"The only permitted **additive delta** SHALL be the enum value `"change"` in the `signal.schema.json` `dimension` field"* |
| `UCI-OPT-001:258` | *"Introduce **at most one** additive schema delta … (append-only)"* |

The operative test these instruments apply to themselves is **additive; existing data remains
valid**. I tested the actual change against that criterion by exhaustive enumeration:

```
old = ^UCOS-[A-Z]{2,6}-[0-9]{6}$      new = ^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$
strings accepted by OLD but rejected by NEW: 0
=> strictly more permissive — every previously-valid identifier remains valid
```

**The change is provably backward-compatible.** It admits new identifiers and rejects none.
It is precisely the "additive; existing data remains valid" class these standards authorize.

### 3.5 Conflict identified and precedence applied

There is a **live, unreconciled conflict**:

- `00-BOOK/CONTROL-TOWER/` standards (the schema surface's owners) **authorize** additive
  schema edits.
- `engine/foundation/guards/frozen_paths.py` + `ec1-ci.yml` **mechanically reject** any write
  under `00-BOOK/` except `DATA|REGISTRIES|CONTROL-TOWER|PORTAL`.

Precedence, applied from each instrument's own self-subordination clause:

1. `99-FREEZE/` + `00-SOURCE/` — top (X-1). **Untouched: `git status -- 00-SOURCE/ 99-FREEZE/` → 0.**
2. `00-CEP/CEP-000…010` — normative law. **Silent on `00-BOOK` paths.**
3. `00-BOOK/CONTROL-TOWER/` standards — *"defines validity rules for registration state"*; authorize additive schema deltas.
4. `02-MASTER/` determinations — `GOV-001-R2`: conflicts are **recorded, not silently resolved**; neither layer amends the other.
5. `00-MASTER/UCIC-001` + `00-MASTER/*` — `AUTHORITY = NONE`, derived.
6. **Implementation code** — lowest. Cannot create a freeze that no instrument above it declares.

> A guard in `engine/**` cannot manufacture constitutional protection that neither the freeze
> notice, nor CEP-007, nor CEP-009, nor the protected-area register confers. **The guard is
> over-broad relative to every authority above it.**

---

## 4. PHASE 3 — CLASSIFICATION

| Sub-finding | Classification |
|---|---|
| **C-1a** `00-BOOK/tools/config.py` | **FALSE POSITIVE** + **EXPECTED BEHAVIOUR** |
| **C-1b** `00-BOOK/SCHEMAS/` ×13 | **MIXED** — permitted write (intentional) + **incomplete implementation** (registration not committed) |
| **C-1c** `frozen_paths.py` over-breadth | **IMPLEMENTATION DEFECT** (tooling over-reach) + **CONSTITUTIONAL CONFLICT** |
| **C-1d** `platform/**` ×7 | **REPOSITORY DEFECT** — X-8 mutation missing its P-7 work package |

### 4.1 C-1a — why `config.py` is a false positive

| Evidence | Determination |
|---|---|
| `REG-AUTO-001` §2 (`00-BOOK/CONTROL-TOWER/…:38-40`) | *"**Out of scope.** The generator's own machinery and generated outputs"* — and `00-BOOK/tools/` is named in the excluded list. `config.py` is **not a corpus artifact**. |
| `REG-AUTO-001` §3 **P3** (line 60) | *"Registration is a pure function of repository content + the append-only ledger + **`config.py`**."* — `config.py` is a **declared input parameter** of the generator. |
| `ukb.py:810-813` | `00-BOOK/tools/` is excluded because *"the registry must not list itself"*. |
| Measured | **0** of 1,193 registered artifacts live under `00-BOOK/tools/`. |
| Precedent | `config.py` was modified in **≥10 committed commits** (`214c1a9`, `898ef8d`, `1c6e750`, `0bcea68`, `b65ee8a`, `0ae1d67`, `eda3db1`, `6b966df`, `e8f7eda`, `432c955`). |
| Effect of the change | Adds 12 `CLASSIFY_RULES` (append-only; `allocate()` is path-keyed, so no existing UID moves) and narrows `DERIVED_CATEGORY_MAXLEN` 12 → 6. |

Modifying `config.py` is the **sanctioned mechanism** for changing classification. It is not a
corpus write.

### 4.2 C-1b — why the schema writes are permitted but incomplete

**Permitted:** not in X-1…X-10; not in the freeze manifest; CEP-007/CEP-009 silent; four
owning standards authorize additive deltas; the widening is provably strictly backward-compatible.

**Incomplete:** the 13 files ARE registered artifacts, and their `content_hash` in
`artifacts.json` is now stale. `REG-AUTO-001` requires source and projections be committed
**atomically**. The working tree currently holds the exact split `REG-AUTO-001` forbids.

> The defect is not *that the schemas were changed*. It is that **the registration was not
> committed with them** — which is `UCCEP-F-007` / `WP-UCCEP-005` / `OA-1`, already registered.

### 4.3 C-1d — the `platform/**` writes and P-7

`UCCEP-000006` Output 6 **P-7** (line 27), verbatim:

```
| P-7 | Corrective mutation of a freeze-gated engine surface (`engine/**`, `platform/**`)
       where a located owner's gate is defective
     | Only under an existing work package; EC-1 `verify.sh` must pass; the corrected gate
       must be demonstrated failing closed on the negative path — the precedent set by
       `WP-UCCEP-003` |
```

Tested against the three conditions:

| P-7 condition | Status | Evidence |
|---|---|---|
| *a located owner's gate is defective* | ✓ **MET** | At HEAD, `repo-operations.json:64-70` declared coverage as 6 dimensions each `covered:1, total:1` — 100% by fiat; and `:23` `"paths": []` made the freeze stage a guard over nothing. Both were gates that could not fail. |
| *EC-1 `verify.sh` must pass* | ✓ **MET** | 5/5 stages, exit 0, coverage 94.28% |
| *corrected gate demonstrated failing closed on the negative path* | ✓ **MET** | `test_freeze_stage_empty_declared_subject_is_fail_closed`, `test_freeze_stage_unknown_subject_source`, measured-coverage-absent fail-closed test |
| **Only under an existing work package** | ⛔ **NOT MET** | `grep "EPIC-PLAT-003\|repository_operations"` over `uccep-bindings.json` and `ucda-decisions.json` → **0 matches**. No work package exists. |

> **Three of four P-7 conditions are satisfied.** The single unmet condition is the
> work-package attribution — which is the same deficiency C-4 gestured at. **C-1d and C-4
> are one finding.**

---

## 5. PHASE 4 — DISPOSITION

### C-1a — `00-BOOK/tools/config.py`

> ## **REJECT**

| Dimension | Determination |
|---|---|
| **Evidence** | `REG-AUTO-001` §2:38-40 (machinery, out of scope) · §3 P3:60 (`config.py` is a declared input) · `ukb.py:810-813` · 0/1193 registered under `00-BOOK/tools/` · ≥10 prior commits |
| **Constitutional justification** | Not a corpus artifact under the owning registration standard. Not in X-1…X-10. Not in the freeze manifest. `DP-03`'s own text says `00-BOOK/**` **source**; the generator is not source. |
| **Implementation impact** | None. Change is append-only and path-keyed; no existing UID moves. |
| **Repository impact** | None. Not registered, so no `content_hash` drift. |
| **Dependency impact** | None. |
| **Certification impact** | **Removes 1 of the 14 alleged violations.** Does not affect certification. |

### C-1b — `00-BOOK/SCHEMAS/*.schema.json` ×13

> ## **ACCEPT — reclassified from "constitutional violation" to "uncommitted registration"**
> ### Disposition: **DEFER** to the already-registered `OA-1` / `WP-UCCEP-005`

| Dimension | Determination |
|---|---|
| **Evidence** | 13 registered artifacts (`UCOS-REG-0000{01,03,04,06,07,09,11,12,13,14,16,17,19}`) with `content_hash` ≠ disk, verified by re-hashing · widening provably admits-only (0 regressions over exhaustive enumeration) · `STATUS-001:122`, `GOV-INT-001:308`, `UCI-001:37`, `UCI-OPT-001:258` authorize additive deltas |
| **Constitutional justification** | No instrument freezes `00-BOOK/SCHEMAS/`: absent from X-1…X-10, absent from the 13-file freeze manifest, CEP-007 names no path, CEP-009 disclaims freeze jurisdiction (II.2/II.5) and admits only ratified-or-frozen subjects (V.1). The owning Control-Tower standards affirmatively permit additive schema change. **No amendment is required.** |
| **Implementation impact** | None pending. The schemas are already consistent with the corpus — `ukb validate` PASSES on all 1,193 artifacts *because* of this change. Reverting would restore 539 schema violations. |
| **Repository impact** | 13 stale `content_hash` values → source/projection split. Discharged by the atomic registration commit. |
| **Dependency impact** | None. No new dependency; no identifier moved; append-only identity preserved. |
| **Certification impact** | **Not a certification blocker.** `verify.sh` Stages 4 and 5 both PASS. `CK-REG-DRIFT` is already `NOT-EXECUTED, in_scope=false` at tier `standard` and is discharged by the commit. |

### C-1c — `frozen_paths.py` `FROZEN_PREFIXES` over-breadth

> ## **ACCEPT (NEW FINDING)** · Disposition: **FIX**

| Dimension | Determination |
|---|---|
| **Evidence** | `frozen_paths.py:17` `FROZEN_PREFIXES = ("00-BOOK/", "00-SOURCE/", "99-FREEZE/")` · `ec1-ci.yml:96-97` excludes only `00-BOOK/(DATA\|REGISTRIES\|CONTROL-TOWER\|PORTAL)/` · no located authority freezes `00-BOOK/SCHEMAS/` or `00-BOOK/tools/` |
| **Constitutional justification** | The guard enforces a scope broader than DP-03's own text (`00-BOOK/**` **source**) and broader than every instrument above it. It directly contradicts four Control-Tower standards that authorize additive schema edits. `GOV-001-R2` requires such a conflict be **recorded**, which this deliverable does. Correcting a defective gate in `engine/**` is itself a **P-7** act. |
| **Implementation impact** | Narrow `FROZEN_PREFIXES` to the located scope, or extend the `ec1-ci.yml` exclusion to `SCHEMAS/` + `tools/`. ~2 lines. Must be demonstrated still failing closed on `00-SOURCE/` and `99-FREEZE/`. |
| **Repository impact** | Unblocks the CI DP-03 step and `repo-ops.sh` `architecture-freeze`. |
| **Dependency impact** | `ec1-frozen-guard` console script + `repo-operations.json` freeze stage consume it. Both covered by existing tests. |
| **Certification impact** | Removes the only *mechanical* obstacle C-1 identified. |

### C-1d — `platform/**` ×7 — freeze-gated mutation without a work package

> ## **ACCEPT (NEW FINDING — missed by C-1)** · Disposition: **FIX**

| Dimension | Determination |
|---|---|
| **Evidence** | X-8 (`06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md:41`) · P-7 (line 27) · 7 modified files under `platform/` · `grep` over `uccep-bindings.json` + `ucda-decisions.json` for `EPIC-PLAT-003\|repository_operations` → **0 matches** |
| **Constitutional justification** | X-8 permits mutation of `platform/**` **only under P-7**. P-7's 2nd and 3rd conditions are met (`verify.sh` passes; the corrected gates are demonstrated failing closed by new tests). Its 1st condition — *"only under an existing work package"* — is unmet. |
| **Implementation impact** | **None to code.** The code already satisfies the substantive P-7 conditions. What is required is a work-package record. |
| **Repository impact** | Register one work package (pattern: `WP-UCCEP-003`, the named P-7 precedent) naming the defective gates, the owner, and the negative-path evidence. |
| **Dependency impact** | None. |
| **Certification impact** | Until registered, 7 files sit outside the declared boundary. This is the **only genuine constitutional deficiency** in the entire C-1 complex. |

---

## 6. SUMMARY

| Claim in `IMPLEMENT-001A` C-1 | Verdict |
|---|---|
| 14 files written inside `00-BOOK/` | ✓ **REPRODUCED** |
| `00-BOOK/**` is protected area **X-1** | ⛔ **FALSE** — X-1 is `00-SOURCE/` + `00-SOURCE-MANIFEST/` + `99-FREEZE/` |
| Requires a **`CEP-009`** amendment | ⛔ **FALSE** — CEP-009 II.2/II.5 disclaim freeze jurisdiction; V.1 eligibility unmet; 0 references to schemas or paths |
| `RELEASE-001` §2.2 prohibits *"Modify frozen corpus"* | ⚠ **TRUE but INAPPLICABLE** — these files are not in the frozen corpus as any instrument defines it |
| Committing would make a violation permanent | ⛔ **FALSE** — and inverted: **not** committing sustains the `REG-AUTO-001` source/projection split (`UCCEP-F-007`) |
| Write set = 14 | ⛔ **INCOMPLETE** — the freeze-gated write set is **21** (14 + 7 under `platform/**`) |

> **What survives C-1:** one 2-line tooling correction (**C-1c**) and one work-package
> registration (**C-1d**). Neither requires a constitutional amendment. Neither blocks the
> commit — and **C-1b is discharged BY the commit.**

---

*END — `IMPLEMENT-001B` Deliverable 00 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*

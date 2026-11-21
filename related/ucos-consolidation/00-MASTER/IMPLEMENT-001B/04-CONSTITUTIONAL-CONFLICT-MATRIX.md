# IMPLEMENT-001B · DELIVERABLE 04 — CONSTITUTIONAL CONFLICT MATRIX

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001B` |
| AUTHORITY | `NONE — DERIVED TRUTH` — this matrix **records** conflicts per `GOV-001-R2`; it resolves none |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

> `02-MASTER/UCOS-GOV-001-…-DETERMINATION.md:148-152`, **GOV-001-R2**: *"Where a Class I
> artifact and a Class C artifact appear to conflict: 1. The conflict is **recorded, not
> silently resolved**. … 4. Neither layer is amended by the mere existence of the other."*
>
> This deliverable discharges obligation 1.

---

## 1. PRECEDENCE ORDER — as assembled from self-subordination clauses

**No single instrument states a complete ordering.** `MCP-001` §02 is the closest and it
(a) omits `00-CEP/`, `00-CMG/` and the Control-Tower standards, and (b) holds `AUTHORITY = NONE`
itself. The operative order below is assembled from each instrument's own clause and is the
order applied throughout this mission.

| Rank | Layer | Basis for its rank | Verified authority value |
|---|---|---|---|
| **1** | `00-SOURCE/` · `00-SOURCE-MANIFEST/` · `99-FREEZE/` | `99-FREEZE/FREEZE-NOTICE.md` — *"Status: FROZEN … No source document may be modified"*; 13 files; protected as **X-1** | the freeze instrument |
| **2** | `00-CEP/CEP-000…010` | Internally ordered by explicit descending chain (`CEP-009:15`, `CEP-007:15`). Protected as **X-2**: *"No mutation. Constitutional change is not an implementation act"* | normative constitutional law |
| **3** | `00-CMG/` | Protected as **X-3**; basis recorded as `CMG-000001` **PROVISIONAL** | meta-constitutional, PROVISIONAL |
| **4** | `00-BOOK/CONTROL-TOWER/` standards (`REG-AUTO-001`, `STATUS-001`, `GOV-INT-001`, `UCI-001`, `UCI-OPT-001`) | `REG-AUTO-001:18` — *"subordinate to the frozen constitutional corpus … where any statement herein would conflict with a higher instrument, the higher instrument governs"* | `AUTHORITY \| NONE` — *"defines validity rules for registration state"* |
| **5** | `02-MASTER/` determinations (CIOA, CCE, EC-2 freeze, charters) | `GOV-001-R2` conflict rule; `GOV-001-CA2` — *"not superseded unless explicitly superseded"* | `CONSTITUENT/GOVERNANCE/RATIFICATION AUTHORITY = NONE`; `HELD = ENGINEERING-EXECUTION-ONLY` |
| **6** | `00-MASTER/` — `UCIC-001`, `UCCEP-*`, `CAEM-001`, `IMPLEMENT-001*` | `MCP-001:61-65` — *"MCS sits **beside** execution, not above any layer… may never amend, reinterpret, or supersede any instrument above"* | `AUTHORITY = NONE — DERIVED TRUTH` |
| **7** | **Implementation code** — `engine/**`, `platform/**`, `.github/workflows/**`, `verify.sh` | no authority clause; enforces, never legislates | none |

**Universal residual clause**, repeated verbatim in ~20 artifacts: *"where any statement
conflicts with a higher instrument, the higher instrument governs."*

---

## 2. THE CONFLICT MATRIX

### CF-01 — `00-BOOK/` tree freeze: **code asserts what no instrument confers** ⛔ MATERIAL

| Field | Determination |
|---|---|
| **Party A** (rank 7) | `engine/foundation/guards/frozen_paths.py:17` — `FROZEN_PREFIXES = ("00-BOOK/", "00-SOURCE/", "99-FREEZE/")`; violation raises `SecurityViolation`. Operationalized by `.github/workflows/ec1-ci.yml:96-97`, which excludes **only** `00-BOOK/(DATA\|REGISTRIES\|CONTROL-TOWER\|PORTAL)/`. |
| **Party B** (rank 1) | `99-FREEZE/FREEZE-NOTICE.md` + `SOURCE-FILES.txt` — freeze exactly **13 files, all `00-SOURCE/*.docx`**. `grep -c 00-BOOK SOURCE-FILES.txt` → **0**. |
| **Party C** (rank 2) | `00-CEP/CEP-007` (the Freeze Constitution) — **contains no repository path at all**; freezes no tree. |
| **Party D** (rank 6) | `UCCEP-000006` Output 6 X-1…X-10 — `00-BOOK` appears only at **X-4** (`00-BOOK/DATA/id-ledger.json`) and **X-5** (`00-BOOK/DATA/*` ledgers). Neither `SCHEMAS/` nor `tools/` appears. |
| **Party E** (rank 6) | `UCIC-001:73` — DP-03's authoritative text says `00-BOOK/**` **source**, not the whole tree. `AUTHORITY = NONE`; *"bindingness flows from the instruments it composes."* |
| **Conflict** | A rank-7 artifact enforces a freeze scope that **no instrument at rank 1, 2, or 4 confers**, and that is broader than the rank-6 text it claims to implement. |
| **Precedence** | Ranks 1, 2 and 6 govern. **The guard is over-broad.** |
| **Resolution owner** | `engine/foundation` — correctable under **P-7** (it is a defective gate in `engine/**`) |
| **Status** | **RECORDED** → `RB-01` |

### CF-02 — Schema edits: **authorized by their owner, rejected by the guard** ⛔ MATERIAL

| Field | Determination |
|---|---|
| **Party A** (rank 4) | Four Control-Tower standards affirmatively authorize additive schema change: `STATUS-001:122` (*"additive; existing data remains valid"*), `STATUS-001:139`, `GOV-INT-001:308,370`, `UCI-001:37`, `UCI-OPT-001:258`. |
| **Party B** (rank 7) | `frozen_paths.py` + `ec1-ci.yml` reject **any** `00-BOOK/SCHEMAS/` write. |
| **Conflict** | The surface's owning standards permit an act the enforcement code forbids. **No instrument reconciles them.** |
| **Precedence** | Rank 4 governs over rank 7. |
| **Test applied** | The standards' own criterion is *"additive; existing data remains valid."* Verified by exhaustive enumeration: strings accepted by the old pattern and rejected by the new = **0**. The change is strictly more permissive. **Criterion met.** |
| **Resolution owner** | `engine/foundation` (narrow the guard) — same act as `CF-01` |
| **Status** | **RECORDED** → `RB-01` |

### CF-03 — Schema validation: **optional by design, mandatory by release policy** ⚠ REAL

| Field | Determination |
|---|---|
| **Party A** (rank 7) | `00-BOOK/tools/ukb.py:21,:25` — *"if jsonschema present"* / *"jsonschema **optional** for `validate`"*; `:1733-1735` swallows `ImportError` and exits 0. |
| **Party B** (rank 6) | `RELEASE-001` §4 — `\| Registry validate \| ukb.py validate / verify.sh Stage 5 \| **Schema** + referential integrity PASS \|` — a stated **release exit criterion**. |
| **Conflict** | A structural-only run cannot evidence *"Schema … PASS."* The tool's declared optionality defeats the policy's stated criterion. |
| **Precedence** | Rank 6 governs rank 7 **for release claims only**. No release is asserted, so this is not presently blocking. |
| **Resolution owner** | `WP-UCCEP-004` / `OA-3` — already registered, `blocking: false`, P2 |
| **Status** | **RECORDED** → `RB-03`. **Bars any unqualified release claim until closed.** |

### CF-04 — `platform/**` mutation: **X-8 prohibits, P-7 permits, no work package exists** ⛔ MATERIAL

| Field | Determination |
|---|---|
| **Party A** (rank 6) | `UCCEP-000006` Output 6 **X-8**: *"`engine/**` · `platform/**` freeze-gated surfaces … No mutation **except under P-7**."* |
| **Party B** (rank 6) | **P-7**: permitted where *"a located owner's gate is defective … **only under an existing work package**; EC-1 `verify.sh` must pass; the corrected gate must be demonstrated failing closed on the negative path."* |
| **Party C** (rank 5) | `02-MASTER/UCOS-ENGINEERING-LANE-FREEZE-DETERMINATION.md:152` — `platform/**` FROZEN; `RC-3` (governed unfreeze) **not invoked**; still in force per `BANDS-…-CHARTER.md:134`. |
| **Facts** | 7 files modified under `platform/**`. Gate defect ✓ (HEAD had `paths: []` and coverage `covered:1/total:1`). `verify.sh` passes ✓. Negative-path tests exist ✓. **Work package: absent** ⛔ (0 matches for `EPIC-PLAT-003\|repository_operations` in `uccep-bindings.json`, `ucda-decisions.json`). |
| **Conflict** | Not between instruments — between the change set and P-7's first condition. |
| **Precedence** | P-7 governs. 3 of 4 conditions met. |
| **Resolution owner** | change author / Registration Authority — register one work package (precedent: `WP-UCCEP-003`) |
| **Status** | **RECORDED** → `RB-02`. **The only genuine constitutional deficiency in the change set.** |

### CF-05 — Duplicate `OA-3` ⚠ MINOR

| Field | Determination |
|---|---|
| **Party A** | `00-MASTER/UCCEP-000006/07-OPERATOR-ACTION-REGISTER.md:22` — `OA-3` = install `jsonschema` |
| **Party B** | `00-MASTER/IMR-0000/12-ORCHESTRATION-ARCHITECTURE.md:24` — `OA-3` = an epoch-binding rule |
| **Conflict** | Two distinct `OA-3` identifiers. Both are mission-local (`T-M` tier per `IMR-0000/06` `NF-3`), so neither claims corpus identity and **`NF-4` is not breached**. |
| **Precedence** | N/A — resolvable by scoping context. |
| **Status** | **RECORDED**, no action. |

### CF-06 — `EIP-018` token reuse ⚠ MINOR

| Field | Determination |
|---|---|
| **Party A** | `00-MASTER/UCOS-USIS-001/00:7` — `EIP-018` = USIS establishment mission; already cited in committed `config.py:69,265,787` |
| **Party B** | 8 added comment lines — `EIP-018` = a stabilization finding set (`FP-2/3/7/8/13/14`) |
| **Conflict** | One token, two unrelated subject matters — **`NF-4` in spirit** (*"No second subject token … for a subject matter that already has one"*, applied inversely). |
| **Precedence** | `NF-1`/`NF-3` exempt non-identity references from admission, so this is hygiene, not violation. Nothing entered `id-ledger.json`. |
| **Resolution** | Rename within `RB-02`'s work package. |
| **Status** | **RECORDED** → `RB-02` |

### CF-07 — `rib.json` self-referential non-convergence ⛔ MATERIAL (NEW)

| Field | Determination |
|---|---|
| **Party A** (rank 6) | `00-MASTER/UCOS-RIB-001/rib.json` records `dirty_paths` (80 entries), `dirty_entries: 80`, `untracked: 10` — a measurement of the working tree's own dirtiness, **embedded in a tracked file**. |
| **Party B** (rank 6) | `UCOS-RFP-001` **RFP-1**: *"executing the declared pipeline over the committed HEAD leaves the repository byte-identical."* |
| **Conflict** | Running `make rib-gate` on a dirty tree **mutates a tracked file**, which changes the next measurement. The artifact cannot reach a fixed point while the tree is dirty. |
| **Measured evidence** | `rib.json` diff was `+129/−30` when `IMPLEMENT-001A` measured it and is `+137/−30` now — **+8 lines**, caused solely by `00-MASTER/IMPLEMENT-001A/` being created between gate runs. `rib.json` records `untracked: 10` while the tree now holds 11; `IMPLEMENT-001A` is absent from its `dirty_paths`. |
| **Precedence** | `RFP-1` governs. `UCOS-RFP-001` is **behaving correctly** by aborting fail-closed on `CLO-01` rather than attempting convergence. The defect is `UCOS-RIB-001`'s. |
| **Resolution owner** | `UCOS-RIB-001` — either exclude `dirty_paths` from the persisted artifact or compute it only over the committed tree |
| **Status** | **RECORDED** → `RB-05` |

---

## 3. CITATION ERRORS FOUND IN CITED AUTHORITIES

Every authority cited by `IMPLEMENT-001A` was opened. Three citations do not survive.

| # | Citation | Cited by | Verdict | Correct position |
|---|---|---|---|---|
| **E-1** | *"`00-BOOK/**` … is protected area **X-1**"* | `CAEM-001/03:72` → `IMPLEMENT-001A` C-1 | ⛔ **FALSE** | X-1 = `00-SOURCE/` · `00-SOURCE-MANIFEST/` · `99-FREEZE/` (`UCCEP-000006/06:34`). `00-BOOK` appears only at X-4/X-5, confined to `00-BOOK/DATA/`. |
| **E-2** | *"It requires a `CEP-009` amendment route"* | `CAEM-001/03:72`, `CAEM-001/05:53` → `IMPLEMENT-001A` C-1 | ⛔ **FALSE** | CEP-009 **II.2**: *"SHALL NOT legislate … **freeze**"*; **II.5**: jurisdiction *"SHALL NOT overlap … freeze (CEP-007)"*; **V.1**: eligibility requires a **ratified or frozen** artifact. 0 references to schema/json/path/code/tool. |
| **E-3** | *"breaches `OAA-001` AC-4 (No parallel identifier system)"* | `IMPLEMENT-001A` C-4 | ⛔ **FALSE** | AC-4's located basis makes the operative act **allocation** (`IMR-003A` AC-3, `GOV-001` Part 10). `NF-1`: a declaration slot *"may never be presented to `REG-AUTO-001` or entered in `id-ledger.json`"*; `NF-3`: *"requires no admission, because it claims no identity."* Nothing was minted. |
| **E-4** | *"`RELEASE-001` §2.2 prohibits *Modify frozen corpus*"* | `IMPLEMENT-001A` C-1, D02 §7 | ⚠ **TRUE but INAPPLICABLE** | The clause is real (`RELEASE-LIFECYCLE.md:53`). But the 14 files are not in the frozen corpus as any rank-1/2/4 instrument defines it. |

**Common root cause of E-1 and E-2:** `CAEM-001` holds `AUTHORITY = NONE — DERIVED TRUTH`.
`IMPLEMENT-001A` treated its conclusions as authority instead of verifying them against
rank-1/2 instruments. The mission mandate — *"No finding shall be accepted solely because it
appears in a report"* — exists precisely to catch this.

---

## 4. THE STRUCTURAL FINDING

> **The `00-BOOK/` tree freeze has no constitutional pedigree.**

Traced end to end:

```
99-FREEZE/FREEZE-NOTICE.md ......... freezes 00-SOURCE/, 13 files.  00-BOOK: NOT MENTIONED
00-CEP/CEP-007 (Freeze Constitution) ....................... contains NO repository path
00-CEP/CEP-009 (Amendment) ......... disclaims freeze (II.2, II.5); NO path, NO schema
UCCEP-000006 X-1..X-10 ............. 00-BOOK only at X-4/X-5, both = 00-BOOK/DATA/
UCIC-001:73 (DP-03 text) ........... "00-BOOK/** SOURCE"  [AUTHORITY = NONE]
MCP-001 §02, ~15 × 02-MASTER ....... "00-BOOK/ read-only"  [ALL AUTHORITY = NONE]
                                                    ↓
frozen_paths.py:17 ................. FROZEN_PREFIXES = ("00-BOOK/", ...)   ← CODE
```

The tree-level freeze of `00-BOOK/` originates in **implementation code at rank 7** and is
sustained by authority-neutral restatement. No rank-1 freeze notice and no rank-2 constitutional
instrument names it.

This is not an argument for writing freely to `00-BOOK/`. `X-4`/`X-5` genuinely protect the
ledgers, and the authored canon (`UCOS-BOOK-000000-…md`, `MASTER-BOOK/`, `ADVANCEMENT/`) is
plainly `00-BOOK/**` *source* within DP-03's actual text. It **is** a determination that
`00-BOOK/SCHEMAS/` and `00-BOOK/tools/` are **not** frozen by any located authority — and that
the guard must be brought into agreement with the authority chain rather than the reverse.

---

## 5. CONFLICT SUMMARY

| # | Conflict | Severity | Ranks | Owner | Backlog |
|---|---|---|---|---|---|
| **CF-01** | `00-BOOK/` tree freeze asserted only by code | **MATERIAL** | 7 vs 1/2/6 | `engine/foundation` | `RB-01` |
| **CF-02** | Schema edits authorized by owner, rejected by guard | **MATERIAL** | 4 vs 7 | `engine/foundation` | `RB-01` |
| **CF-03** | Schema validation optional vs `RELEASE-001` §4 mandatory | **REAL** | 6 vs 7 | `WP-UCCEP-004` | `RB-03` |
| **CF-04** | `platform/**` X-8 mutation without a P-7 work package | **MATERIAL** | P-7 unmet | change author | `RB-02` |
| **CF-05** | Duplicate `OA-3` | MINOR | — | — | none |
| **CF-06** | `EIP-018` token reuse | MINOR | `NF-4` spirit | change author | `RB-02` |
| **CF-07** | `rib.json` non-convergence | **MATERIAL** | vs `RFP-1` | `UCOS-RIB-001` | `RB-05` |

**4 MATERIAL · 1 REAL · 2 MINOR.** Three collapse into two remediation items (`RB-01`, `RB-02`).

---

*END — `IMPLEMENT-001B` Deliverable 04 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*

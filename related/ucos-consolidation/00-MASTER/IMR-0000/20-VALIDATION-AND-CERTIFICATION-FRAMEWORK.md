# IMR-0000/20 — VALIDATION AND CERTIFICATION FRAMEWORK

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `20` — Validation Framework + Certification Framework (**directive capabilities 17, 18**) · carries this mission's self-check register |
| ARTIFACT KIND | Framework (`CMG-K-05`) + self-check determination |
| SUBSYSTEMS | `SS-15` `CIOS-VI` (`E-05`, `E-06`) · `SS-16` `CIOS-CI` (**BINDING-ONLY**) |
| NUMERIC CONTRACT | **12 self-checks** `PCK-01 … PCK-12` |
| CENTRAL DISCLOSURE | **A self-check is not a validation** (`CIOS-15` `VR-04`). This artifact claims **no `CEP-004` validation** and **no active `CEP-005` certification**, both of which are unavailable at `b26c5bb`. |
| AUTHORITY OF ITS OWN | **NONE.** The platform validates nothing and certifies nothing. |
| CONFLICT RULE | Located instrument governs (`CEP-004`, then `CEP-005`, then `CEP-006`/`CEP-007` for standing); then `IMR-003A` (`CIOS-15`, `CIOS-16`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. VALIDATION FRAMEWORK *(directive capability 17)*

### 1.1 The three validation surfaces

`CIOS-15` declares three surfaces and fourteen rules `VR-01 … VR-14`. Bound by pointer. The platform-level statement of the distinction, because conflating the surfaces is what would produce a second validator:

| Surface | Scope | Authority | Confers standing? |
|---|---|---|---|
| **VS-1 · Located validation** | corpus artifacts | `CEP-004`; `engine/validation`; `verify.sh`; `G-10`; `IEC-001` Q5/C8/P5 | **yes** |
| **VS-2 · Located gate checks** | admission determinations | `UCCEP-000000` `G-01 … G-14`; `uccep.json` `CK-*` | **yes**, per gate |
| **VS-3 · Self-check** | **a programme's own declaration, and nothing else** | the declaring programme | **NO** |

| ID | Rule | Located basis |
|---|---|---|
| `VF-1` | The platform validates **no corpus artifact**. | `CIOS-15`; `SS-15` scope |
| `VF-2` | A self-check binds **only** the declaring mission's own declaration. It creates no registry, issues no verdict over a located concern, and binds no corpus artifact. | `IMR-003A` `AC-4`; `CIOS-INV-12`; `VR-10 … VR-14` |
| `VF-3` | **A self-check is not a validation.** No `PCK-*` result may be presented as a `CEP-004` verdict. | `CIOS-15` `VR-04` |
| `VF-4` | Validation is **fail-closed**: missing, ambiguous, unresolvable or degraded evidence is a failure, never a pass. | `CIOS-L-07`; `CEP-001` LAW-2 |
| `VF-5` | Validation SHALL NOT be bypassed, re-implemented or duplicated. | `CEP-001` LAW-5; `UUP-06` |

### 1.2 What `SS-15` does

Admission-time determinations only: overlap resolution (`E-05`, `CIOS-S-07`) and duplication detection (`E-06`, `CIOS-S-08`), bound to `G-03` and `G-07`. Unresolved overlap is a **non-admission, not a scheduling problem**, and no deferral is permitted.

### 1.3 Located validation state at `b26c5bb`

| Measurement | Value |
|---|---|
| constitutional gates PASS | **6 / 14** |
| blocking failures | **none** |
| programmes PASS | **6 / 16** |
| `PROGRAM-000001` checks `CK-CLOSURE-P1`, `CK-CLOSURE-P2` | **NOT-EXECUTED** |
| `UCCEP-000000` tier | `boot` |
| inherited defect — schema validation | **degrades silently to structural-only** (`UCCEP-F-006`; `CIOS-G-05` OPEN) |
| inherited defect — planning-closure gate | **no reachable PASS state** (`UCCEP-F-001`) |
| inherited defect — graph validator | **fails open** on a reported cycle (`UCCEP-F-003`; `CIOS-G-04` OPEN) |

**Three located validation defects bound every claim in this mission.** None is introduced here and none is discharged here.

---

## 2. CERTIFICATION FRAMEWORK *(directive capability 18)*

| ID | Rule | Located basis |
|---|---|---|
| `CF-C1` | The platform **certifies nothing**. | `CIOS-16` §1; `SS-16` is BINDING-ONLY |
| `CF-C2` | Certification is `CEP-005`'s, executed through the located gate; standing is recorded in `certification.json`. | `CEP-005`; `G-11`; `IEC-001` Q6/C9/P6 |
| `CF-C3` | **No standing may be claimed above the declared ceiling.** The ceiling is `CERTIFIED-PROVISIONAL`. | `CIOS-16` §1; `CMG-L-12` |
| `CF-C4` | Self-certification is void. A programme may not certify itself. | `CEP-009` I.5; `UUP-07` |
| `CF-C5` | The twin certification **dimension** reports; it does not certify. | `DT-5` |
| `CF-C6` | **Freeze is unavailable**, and an attempt would be **void**. `CIOS-PT-01` SEALED is not a `CEP-007` freeze state. | `CEP-007` II.4, IV.4; `GD-10`; `CIOS-GAP-13`; `LR-7` |

### 2.1 Why the ceiling exists, and what it costs

| Cause | Effect |
|---|---|
| Tier `T1` (Constitutional Authority) is **VACANT** — `VAC-01`, `CMG-OQ-02`, `UCCEP-F-004` | no located authority is competent to ratify (`CEP-006`) |
| no ratification | every determination capped **PROVISIONAL** (`CMG-L-12`) |
| no active certification | freeze ineligible on the certification limb (`CEP-007` V) |
| no freeze | **no true immutability** — contracts are change-routed, not sealed |

**Consequence for this mission, stated without hedging:** `IMR-0000` cannot be validated under `CEP-004`, cannot be certified active under `CEP-005`, cannot be ratified under `CEP-006`, and cannot be frozen under `CEP-007`. It reaches exactly the standing `IMR-003A` reached, for exactly the same located reasons. Observed corpus state: **31 of 43 artifacts PROVISIONAL**; `UCCEP-000000` `CERTIFIED-PROVISIONAL`, seal `f10928ff68603bf1`.

---

## 3. THE SELF-CHECK REGISTER — `PCK-01 … PCK-12`

**Scope: `IMR-0000`'s own declaration only.** No `PCK-*` binds a corpus artifact, creates a registry, or issues a verdict over a located concern (`VF-2`).

**Mode note.** `MC-05` forbids code generation, so **no machine verifier is authored** — unlike `IMR-003A-R1`, which shipped `r1_verify.py`. The checks below were evaluated by direct inspection and by non-persisting shell/`git` observation. This is a **weaker** evidence class than a committed verifier, and it is recorded as finding `PF-06` in `23`.

| ID | Check | Method | Result |
|---|---|---|---|
| `PCK-01` | The 24 engines are partitioned across subsystems: **disjoint and exhaustive** | parsed `02` §4.1; counted occurrences of `E-01 … E-24` | **PASS** — 24 listed, 24 unique, 0 duplicates, 0 missing |
| `PCK-02` | Partition transitions are assigned to exactly one subsystem each and are disjoint | `02` §5 row 4; `08` §5 | **PASS** — `PT-00→PT-03` (`SS-01`/`E-10`), `PT-02→PT-01` (`SS-01`/`E-19`); `PT-03→PT-02` located |
| `PCK-03` | Zero `CIOS-*` family members added; zero `CIOS-01` Art X.1 cardinalities altered | `00` §3.3; `06` §4 | **PASS** — 24 engines / 48 ports / 24 stages / 22 identity fields unchanged; 0 members added; 0 families created |
| `PCK-04` | Every invariant the platform touches is bound to a located enforcer or a declared self-check | `04` §2; `02` §3 validation rows | **PASS** — `CIOS-INV-01…12` all bound; 0 unbound |
| `PCK-05` | Every framework rule and registry specification names a **located** owner or is a recorded gap with a prospective owner | reviewed `RF-*`, `REG-*`, `RR-*`, `UOM-R-*`, `UUP-*`, `IDF-*`, `NF-*`, `LR-*`, `DG-*`, `PA-*`, `SA-*`, `OA-*`, `CF-*`, `RF-R*`, `KG-*`, `DT-*`, `IN-*`, `IC-*` | **PASS** — 0 rules without a located owner; 2 specifications (`REG-05`, `REG-07`) recorded as gaps with prospective owners |
| `PCK-06` | Every located pointer used resolves at `b26c5bb` | directory and file inspection during discovery and authoring | **PASS** — `00-CEP/`, `00-CMG/CMG-REGISTRY.json`, `00-BOOK/DATA/*.json`, `00-BOOK/SCHEMAS/`, `00-BOOK/CONTROL-TOWER/`, `00-BOOK/REGISTRIES/`, `00-MASTER/UCCEP-000000/uccep.json`, `00-MASTER/UCDA-000001/ucda-decisions.json`, `00-MASTER/UAKOS-CLOSURE-002/closure.json`, `00-MASTER/MCP-007`, `00-MASTER/CHECKPOINTS/`, `00-MASTER/UCIC-001…`, `02-MASTER/…AIF…`, `intelligence/`, `engine/`, `00-MASTER/IMR-003A/`, `00-MASTER/IMR-003A-R1/` all resolve. **Qualification:** `IEC-001` and `IMG-001` are cited by identifier throughout the corpus but no file bears those names; they are referenced from root-level determinations. Recorded as `PF-07`. |
| `PCK-07` | No file outside `00-MASTER/IMR-0000/` is written by this mission | `git status --porcelain`, compared against session start | **PASS with disclosure** — 32 status entries now vs **31** at session start; the **single** delta is `?? 00-MASTER/IMR-0000/`. The 28 modified files under `00-MASTER/UCCEP-000000/` (20) and `00-MASTER/UCDA-000001/` (8) were written by **session-start governance hooks** before any mission authoring, and are **not** attributable to this mission. `00-MASTER/IMR-003A/` and `IMR-003A-R1/` remain **untracked and unmodified**. |
| `PCK-08` | No domain, industry, science, vendor, cloud, platform, language, protocol, format, database or infrastructure is enumerated | reviewed every artifact against `CIOS-L-22` | **PASS** — technology names appear only where quoting a located register's own filename or tool (e.g. `relationships.json`, `ukb validate`), which is a **pointer**, not an enumeration |
| `PCK-09` | No code, script, runtime, agent, executable orchestration, deployment or infrastructure binding is produced | file inventory | **PASS** — 24 markdown artifacts + 1 data-only JSON projection; **0** executable files |
| `PCK-10` | Registries created / written / entries added | `07` §5; `PCK-07` | **PASS** — **0 / 0 / 0**; freeze-registry entries **0**; `id-ledger` entries **0** |
| `PCK-11` | Every deliverable maps to exactly one artifact, and every artifact to ≥1 deliverable | `00A` Output 4; `21` | **PASS** — 30 required deliverables + 6 directive capabilities, all mapped; 0 orphan artifacts |
| `PCK-12` | Internal consistency: every count declared in one artifact matches every restatement of it | cross-read of headers, reconciliation sections and property tables | **PASS with 2 corrections recorded in place** — (i) `03` attribute count corrected 19 → **20** (`PF-01`); (ii) `00A` §2.1 PRESENT tally corrected 12 → **14**. Both corrections are stated at the point of occurrence rather than silently applied. |

### 3.1 Self-check summary

| Property | Value |
|---|---|
| Self-checks declared | **12** |
| PASS | **12** |
| FAIL | **0** |
| PASS with disclosure | **2** (`PCK-07`, `PCK-12`) |
| PASS with qualification | **1** (`PCK-06`) |
| Corrections recorded in place | **2** |
| Machine verifier authored | **0** — prohibited by `MC-05`; recorded as `PF-06` |
| Located gates discharged by these checks | **0** |
| `CEP-004` validations claimed | **0** |
| `CEP-005` certifications claimed | **0** |

---

## 4. THE FREEZE PRECONDITIONS, ASSESSED

The Context Assimilation Directive conditions Architecture Freeze on six preconditions. Assessed against what is achievable at `b26c5bb`.

| Precondition | Scope in which it is met | Verdict |
|---|---|---|
| zero architectural gaps remain | `IMR-0000`'s own design | **MET** — 9 of 11 `PGAP-*` close within this mission; the 2 that do not (`PGAP-02`, `PGAP-03`) are **register instantiations no CIOS artifact may perform** (`CIOS-INV-12`), each recorded with an owner and an open gate |
| zero duplicated authorities remain | corpus-wide, as measured | **MET** — 0 duplicates, 0 conflicts (`00A` Output 2) |
| zero conflicting subsystem definitions | `02` | **MET** — `PCK-01`; `02` §5 duplicate responsibilities **0** |
| complete platform coverage verified | directive's 30 + 6 capabilities | **MET** — `21` traceability matrix |
| **validation passes** | **self-check scope only** | **MET as `PCK-01…12`**; **NOT MET** as `CEP-004` — that validation is **unavailable** |
| **certification passes** | **ceiling scope only** | **MET to `CERTIFIED-PROVISIONAL`**; **NOT MET** as active `CEP-005` certification — **unavailable** while `VAC-01` is open |

**Two of six preconditions cannot be met in their strong sense, and no reading of the corpus at `b26c5bb` makes them meetable.** The terminal act is therefore a **declaration-scoped Architecture Stability Contract** (`22`) plus a Freeze **Declaration** (`25`) that expressly is not a `CEP-007` freeze. Calling it one would be void under `CEP-007` II.4 / IV.4 and would place the Program in HALTED — a worse outcome than the honest disclosure.

---

## 5. WHAT THIS FRAMEWORK DOES NOT DO

| Not done | Located owner |
|---|---|
| Validate any corpus artifact | `CEP-004`; `engine/validation`; `verify.sh` |
| Add a check to the located check register, or issue a gate verdict | `UCCEP-000000`; `G-01…G-14` |
| Certify anything, or assert a standing | `CEP-005`; `certification.json` |
| Ratify anything | `CEP-006` — unavailable, `T1` VACANT |
| Declare, imply or record a freeze or seal | `CEP-007` — unavailable; an attempt would be **void** |
| Present a self-check as a validation | `VF-3`; `CIOS-15` `VR-04` |
| Author a machine verifier | `MC-05`; recorded as `PF-06` |
| Discharge `UCCEP-F-001`, `F-003`, `F-004`, `F-006` or `VAC-01` | each owner-held |

---

## AUTHORITY BOUNDARY (MANDATORY)

This framework binds located validation and certification authorities and records twelve self-checks over **this mission's own declaration only**. **It validates no corpus artifact, certifies nothing, ratifies nothing and freezes nothing.** A self-check is not a validation and confers no standing. No located gate or finding is discharged. Three located validation defects and the `T1` vacancy bound every claim made here, and all four are inherited and owner-held. Where this framework and a located canonical instrument disagree, **the located instrument governs and this framework SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/20` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**

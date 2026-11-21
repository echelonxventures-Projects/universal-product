# IMR-003A-R1 — CONSTITUTIONAL RECOVERY MISSION REGISTRATION RECORD

| Field | Value |
|---|---|
| MISSION | `IMR-003A-R1` — Constitutional Recovery, Gap Closure & Architecture Freeze |
| RECOVERS | `IMR-003A` — Continuous Implementation Operating System (**CIOS**) · Constitution & Architecture |
| ARTIFACT | Registration record for the recovery mission |
| CLASSIFICATION | GOVERNANCE (registration) · **additive-only** · programme-owned under `00-MASTER/<PROGRAMME-ID>/` (`UCCEP-000006` §1 **P-5**) |
| AUTHORITY | **NONE of its own.** Renders within the located authority of `CEP-009` (`CMG-DLG-09`). Legislates nothing; authorizes no execution. |
| BASELINE | HEAD `b26c5bb66c37717fe4eb96552bad4b9d8b74d890` (`b26c5bb`) · branch `programme/evo-usis-005` — **identical to the `IMR-003A` baseline** (no re-baselining) |
| REPOSITORY TRUTH | `00-MASTER/UAKOS-CLOSURE-002/closure.json` — `determination=CLOSED`, `concept_total=434`, `gap_total=0`, all seven gap classes zero (re-verified, this mission) |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier **T1 VACANT** (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`); every determination **PROVISIONAL** (`CMG-000001` `CMG-L-12`) |
| CONSTRAINT | Recovers, completes, verifies and stabilizes a constitutional foundation. Implements no business capability. Creates no code. Executes no work package. |
| WRITE SCOPE | `00-MASTER/IMR-003A-R1/` (recovery artifacts) + `00-MASTER/IMR-003A/` (**gap closure by file creation only** — zero mutation of the two recovered artifacts) |

> **Recovery act, not a restart.** `IMR-003A` is **not** re-registered, **not** re-baselined, **not** superseded and **not** re-authored. Its two delivered artifacts are treated as **immutable recovered input**. This mission only **extends** the mission's output set to the register `IMR-003A` itself declared.

---

## R1.1 — WHY A RECOVERY MISSION EXISTS

`IMR-003A` declared a **23-artifact output register** (OUTPUT 0.3) and terminated after delivering **2**. The mission's own closure test — `CIOS-01` **ARTICLE X.1** — is therefore unsatisfied on seven of its eight limbs.

The termination left the repository in a specific and hazardous state: a **registered, admitted constitutional instrument** (`WP-IMR-003A`, OUTPUT 0.7 verdict *ADMITTED AND REGISTERED INTO REPOSITORY TRUTH*) whose architecture does not exist. `CIOS-01` binds forward to `CIOS-02`, `CIOS-04`, `CIOS-07`, `CIOS-10`, `CIOS-11`, `CIOS-12`, `CIOS-17`, `CIOS-19` and `CIOS-20` — **nine dangling forward references**, each a live violation of `CIOS-INV-11` (*every CIOS reference resolves at the stated baseline*).

An admitted constitution with unresolvable internal references is worse than an absent one, because downstream missions are entitled to rely on it. Recovery is therefore obligatory, not discretionary.

---

## R1.2 — RECOVERY CLASS AND ROUTE

| Field | Determination |
|---|---|
| **Recovery class** | **COMPLETION** — not restart, not supersession, not amendment |
| **Constitutional route** | `CEP-009` III.1 (propose → classify → assess impact → admit → create successor → complete); primary class **ADDITIVE** (IV.1; exactly one primary class, IV.6) |
| **Why ADDITIVE and not CORRECTIVE** | No delivered artifact is wrong. The defect is **absence**, not error. Every closure act creates a new file; none edits `00-CIOS-MISSION-REGISTRATION-RECORD.md` or `01-CIOS-CONSTITUTION.md`. `CEP-009` III.3 (additive discipline) is satisfied. |
| **Why not a successor constitution** | `CEP-009` Art IV.3 requires a successor instrument only where the located instrument is **frozen**. `CIOS-01` is PROVISIONAL and **not frozen** (`GD-10`; `CEP-007` IV.1 ineligible). Completion of a declared-but-undelivered register is not an amendment of law. |
| **Mission identifier form** | `-R1` recovery suffix, precedent `UAKOS-PHASE-001A-R1`, `UAKOS-PHASE-003A-R2`, `UAKOS-PHASE-003R` (`00-MASTER/`) |
| **Registered identity** | `WP-IMR-003A-R1` |
| **Namespace (mission)** | Existing family `IMR` / `WP-IMR-*`. **No new mission family allocated.** |
| **Namespace (subject)** | **`CIOS`** — the subject token already allocated by `IMR-003A` OUTPUT 0.4. **No new subject token allocated.** See `10-NAMESPACE-RECONCILIATION.md`. |
| **Repository identity / home** | `00-MASTER/IMR-003A-R1/` (programme-owned per P-5; registration-excluded zone) |
| **Predecessor** | `WP-IMR-003A` ← `WP-IMR-001` (`M-1A`) ← `UCCEP-000008` ← `UCCEP-000007` |
| **Successor** | None created. `IMR-003B` is **authorized to begin** by `09-ARCHITECTURE-INTERFACE-FREEZE-REPORT.md`; it is not registered here. |
| **Corpus identity consumed** | **NONE** — `00-MASTER/` is registration-excluded (`00-BOOK/tools/config.py :: EXCLUDE_DIR_PREFIXES → "00-MASTER/"`) |

---

## R1.3 — ACCEPTANCE CRITERIA

The recovery mission inherits **AC-1 … AC-12** of `WP-IMR-003A` unchanged, and adds:

- **RAC-1** — **Zero destruction.** `00-CIOS-MISSION-REGISTRATION-RECORD.md` and `01-CIOS-CONSTITUTION.md` are byte-identical before and after this mission. Verified by digest in `08-ARCHITECTURE-VERIFICATION-REPORT.md`.
- **RAC-2** — **Zero restart.** No artifact of this mission re-declares CIOS's registration, baseline, namespace allocation, law set, invariant set, plane set or partition set. Those are recovered, cited and **relied upon**.
- **RAC-3** — **Register fidelity.** Every gap-closure artifact occupies exactly the slot `IMR-003A` OUTPUT 0.3 declared for it, under the filename declared there.
- **RAC-4** — **Article X.1 satisfaction.** All eight limbs of the `CIOS-01` closure test hold on completion, each machine-verified.
- **RAC-5** — **Nothing unclassified.** Every one of the 23 declared outputs carries exactly one of COMPLETE / PARTIAL / INVALID / MISSING, with justification.
- **RAC-6** — **No new namespace.** The recovery introduces no subject token, no identifier family and no concern beyond those `IMR-003A` OUTPUT 0.4 already allocated.
- **RAC-7** — **Freeze legality.** No artifact of this mission declares, implies or records a `CEP-007` freeze, freeze baseline or freeze authorization. The stability instrument is declaration-scoped and is explicitly **not** a constitutional freeze. See `R1.4`.
- **RAC-8** — **Machine verification.** Every binding assertion is checked by executable code (`r1_verify.py`) whose output is committed as evidence, not asserted in prose.

---

## R1.4 — THE FREEZE CONSTRAINT (MANDATORY DISCLOSURE)

The recovery instruction requires an *"Architecture Freeze v1.0"* whose contracts are *"immutable"*. **A `CEP-007` constitutional freeze is unavailable and any attempt at one would be void.** This is an eligibility fact measured from located clauses, not a policy preference:

| Located clause | Requirement | Measured state |
|---|---|---|
| `CEP-007` III.2 | Ratification (`CEP-006`) is an **entry condition** to the freeze lifecycle | Tier T1 **VACANT** (`VAC-01`, `located: false`); `CEP-006` names no competent authority; *"No programme may self-ratify"* (`UCCEP-000006` **ED-1**) ⇒ **FAIL** |
| `CEP-007` IV.1 | Eligibility = VALIDATED ∧ CERTIFIED (active) ∧ RATIFIED — conjunctive | Aggregate certification capped at `CERTIFIED-PROVISIONAL` ⇒ **FAIL** |
| `CEP-007` V.1 | Preconditions include rooted-and-closed traceability (`CEP-001` XVIII) | `UCCEP-F-002` — 1198/1198 artifacts incomplete traceability ⇒ **FAIL** |
| `CEP-007` V.5 | *Freeze SHALL NOT proceed while any precondition is unsatisfied* | three independent limbs fail ⇒ **freeze prohibited** |
| `CEP-007` IV.4 / II.4 | An attempted freeze of an ineligible artifact, or outside authorization, **SHALL be void** | a declared freeze here would be a **nullity** |
| `GD-10` (`00-MASTER/UCCEP-000008/03-...`) | Freeze **REJECTED on eligibility**; `GD-10-C1` forbids declaring, implying or recording a freeze | binding precedent |

**Resolution adopted.** The mission's freeze intent is delivered in the only lawful form available: an **Architecture & Interface Stability Contract** over CIOS's **own declaration surface** — a surface CIOS exclusively owns, in a registration-excluded programme zone, containing no corpus artifact. It is:

- **binding on downstream missions** by composition (they consume CIOS's declared interfaces and may rely on them);
- **change-routed** — alteration proceeds only through `CEP-009` III.1, never by in-place edit;
- **explicitly not** a `CEP-007` freeze, not a seal, not a baseline, not immutable in the constitutional sense, and **not** a claim on `VAC-01`.

This is a **deliberate, disclosed divergence from the literal instruction**, taken because the literal act is void under located law. It is recorded as `CIOS-GAP-13` with named owner and unblocking condition.

---

## R1.5 — REQUIRED-OUTPUT MAPPING

The recovery instruction names 17 required outputs. Several are already-declared `IMR-003A` register slots; delivering them **into those slots** is what preserves Knowledge Once. Creating parallel documents for them would violate `CIOS-L-09` (Zero Duplication).

| # | Required output | Delivered as | Zone |
|---|---|---|---|
| 1 | Recovery Report | `01-RECOVERY-REPORT.md` | R1 |
| 2 | Completed Artifact Inventory | `02-COMPLETED-ARTIFACT-INVENTORY.md` | R1 |
| 3 | Missing Artifact Inventory | `03-MISSING-ARTIFACT-INVENTORY.md` | R1 |
| 4 | Gap Analysis Matrix | `04-GAP-ANALYSIS-MATRIX.md` | R1 |
| 5 | Dependency Matrix | `05-DEPENDENCY-MATRIX.md` (engine-internal: `IMR-003A/06-CIOS-ENGINE-DEPENDENCIES.md`) | R1 + register |
| 6 | Interface Matrix | `06-INTERFACE-MATRIX.md` (surface: `IMR-003A/05-CIOS-ENGINE-INTERFACES.md`) | R1 + register |
| 7 | Registry Matrix | `07-REGISTRY-MATRIX.md` | R1 |
| 8 | Canonical Mission Object Specification | `IMR-003A/08-CIOS-IDENTITY-MODEL.md` (22 fields `CIOS-ID-01…22`) | register slot 8 |
| 9 | Mission Namespace Specification | `10-NAMESPACE-RECONCILIATION.md` + `IMR-003A` OUTPUT 0.4 (recovered, relied upon) | R1 + recovered |
| 10 | Mission Lifecycle Specification | `IMR-003A/07-CIOS-LIFECYCLE-MODEL.md` (24 stages `CIOS-S-01…24`) | register slot 7 |
| 11 | Engine Contract Specification | `IMR-003A/03`, `04`, `05` (architecture · responsibilities · interfaces) | register slots 3–5 |
| 12 | Public Interface Specification | `IMR-003A/05-CIOS-ENGINE-INTERFACES.md` (ports `CIOS-P-*`) | register slot 5 |
| 13 | Governance Specification | `IMR-003A/14-CIOS-GOVERNANCE-INTEGRATION-MODEL.md` | register slot 14 |
| 14 | Validation Specification | `IMR-003A/15-CIOS-VALIDATION-INTEGRATION-MODEL.md` | register slot 15 |
| 15 | Certification Specification | `IMR-003A/16-CIOS-CERTIFICATION-INTEGRATION-MODEL.md` | register slot 16 |
| 16 | Architecture Verification Report | `08-ARCHITECTURE-VERIFICATION-REPORT.md` (+ `IMR-003A/20-CIOS-CONSTITUTIONAL-VERIFICATION.md`) | R1 + register slot 20 |
| 17 | Architecture Freeze Report | `09-ARCHITECTURE-INTERFACE-FREEZE-REPORT.md` | R1 |

---

## R1.6 — AUTHORITY BOUNDARY (MANDATORY)

This record **registers a recovery**. It confers no authority on itself, on CIOS, or on any engine CIOS describes. Every authority named is **located** in an instrument existing independently at `b26c5bb`. Where this record and a located canonical instrument disagree, **the located instrument governs and this record SHALL be corrected**. It owns no constitutional concern, allocates no corpus identity, discharges no gate, and authorizes no execution.

**END OF ARTIFACT — `IMR-003A-R1` R1 · REGISTERED · PROVISIONAL · ADDITIVE · AUTHORITY-NEUTRAL**

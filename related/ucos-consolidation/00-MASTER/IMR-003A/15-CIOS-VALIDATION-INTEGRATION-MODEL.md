# CIOS-15 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · VALIDATION INTEGRATION MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-15` — Validation Integration Model (mission Output 15) · **also the Validation Specification** (required output 14) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| OBLIGATION DISCHARGED | recovery instruction: *"Every validation rule is documented."* |
| CENTRAL LIMIT | CIOS holds **no validation authority**. `CEP-004` (`CMG-DLG-04`) is the validation authority. CIOS declares which located validation binds which CIOS act, and validates **only its own declaration**. |
| AUTHORITY OF ITS OWN | **NONE.** |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE THREE VALIDATION SURFACES

Conflating these is the failure mode this artifact exists to prevent.

| Surface | Subject | Owner | CIOS role |
|---|---|---|---|
| **S-A** Located artifact validation | corpus artifacts, code, implementations | `CEP-004`; `verify.sh`; `engine/validation`; `IEC-001` Q5, C8; `G-10` | **binds** — CIOS neither performs nor duplicates it |
| **S-B** Admission validation | a submission traversing `CIOS-S-01 … S-24` | located gates `G-01 … G-14` | **binds** — CIOS routes to located gates |
| **S-C** CIOS self-validation | **CIOS's own declaration** | CIOS (`CIOS-CK-*`) | **owns** — permitted by `AC-4` |

`AC-4` permits *"no parallel registry, no parallel gate, no parallel validator, **except self-checks over CIOS's own declaration**"*. **S-C** is that exception and nothing more: it validates the CIOS declaration files, binds no corpus artifact, and issues no verdict over any located concern.

---

## 2. S-A — LOCATED ARTIFACT VALIDATION (BOUND)

| Located mechanism | Concern | Where it acts | CIOS |
|---|---|---|---|
| `CEP-004` | validation authority, validation lifecycle, closure | corpus-wide | binds |
| `verify.sh` | validation harness | repository root | binds; presence is located predicate `P5` |
| `engine/validation` | validation engine | located | binds |
| `IEC-001` C8 | Validation Trigger — fires validation on IMPLEMENTED objects | located execution interval | binds |
| `IEC-001` `08` **Q5** | invalid-validation gate: validation owner present; `trace.implementation=true` before VALIDATED | `IMPLEMENTED → VALIDATED` | binds |
| `IEC-001` `03` **P5** | `validation_owner_exists` READY predicate | READY evaluation | binds |
| `UCCEP-000000` **`G-10`** | Validation Gate | constitutional | binds |
| `CK-VERIFY` | located check | CI | binds |
| `CEP-001` XVIII | rooted-and-closed traceability precondition | corpus-wide | binds |

**Where S-A acts.** Entirely inside the located execution interval between `CIOS-S-23` and `CIOS-S-24` (`CIOS-07` §3). CIOS declares **zero** stages there, so no CIOS act can precede, replace, duplicate or shortcut located validation.

| Rule | Statement |
|---|---|
| `VR-01` | CIOS does not validate any corpus artifact, implementation or code. |
| `VR-02` | CIOS does not trigger, sequence, gate or interpret located validation. `IEC-001` C8 triggers it. |
| `VR-03` | CIOS does not seal an item whose located validation has not been performed by its located owner. `CIOS-S-24` consumes a terminal state, and `IEC-001` `06` reaches terminal only through `VALIDATED`. |
| `VR-04` | A CIOS artifact is **not** VALIDATED under `CEP-004` by virtue of any self-check passing. |

`VR-04` is stated because it is the exact overclaim a self-validating design tends toward, and because `CEP-007` IV.1 makes `CEP-004` validation an eligibility limb — claiming it falsely would corrupt a freeze determination downstream.

---

## 3. S-B — ADMISSION VALIDATION (BOUND)

Each admission stage's validation is performed by a **located** gate. Reproduced from `CIOS-07` §2 by reference; the located owner column is the operative content here.

| Stage | Validation performed | Located validator |
|---|---|---|
| `CIOS-S-02` | context fully assimilated | `G-01` |
| `CIOS-S-03` | knowledge recurrence determined | `G-02`; `CK-CLOSURE-P1`, `CK-CLOSURE-P2` |
| `CIOS-S-04` | reuse disposition resolved to EXTEND | `G-03` |
| `CIOS-S-05`, `S-06` | exactly one canonical home and owner | `G-06`; `closure.json` gap classes |
| `CIOS-S-07` | scope overlap resolved to a single owner | `G-03`; `IAC-001D` §05 |
| `CIOS-S-08` | no duplicate home/owner/identifier/plan/queue/gate/authority | `G-07`; `CK-REG-VALIDATE`, `CK-REG-DRIFT` |
| `CIOS-S-09` | constitutional conformance | `G-04`; `CK-CMG` |
| `CIOS-S-10` | architectural admissibility | `G-05` |
| `CIOS-S-11`, `S-12` | identity composed and complete | `G-07`; `CK-REG-ENFORCE` |
| `CIOS-S-13`, `S-14` | dependencies resolve; no cycle | `G-08`; `CK-GRAPH` |
| `CIOS-S-15 … S-17` | impact assessed, classified, admitted | `G-09` |
| `CIOS-S-18` | evidence sufficient; disposition obligation met | `G-12`; `CK-DECISION-EVIDENCE` |
| `CIOS-S-19` | partition assignment lawful | `G-06` + self-check `CIOS-CK-PARTITION` |
| `CIOS-S-23` | implementation authorized | `G-13` |
| `CIOS-S-24` | implementation evidence present | `G-14` |

| Rule | Statement |
|---|---|
| `VR-05` | Every stage validation is performed by a located gate, except the four in §4 which validate CIOS's own declaration. |
| `VR-06` | CIOS may not pass a stage its located gate fails. A CIOS verdict never overrides a located gate verdict. |
| `VR-07` | Missing, ambiguous, unresolvable or degraded evidence is a **failure**, never a pass (`CIOS-L-07`; `CEP-001` LAW-2). |
| `VR-08` | No stage may be skipped, merged, reordered or waived (`CIOS-L-06`; `CEP-001` LAW-5). |
| `VR-09` | All fourteen located gates bind; none is bypassed (`CIOS-07` §4.1). |

---

## 4. S-C — CIOS SELF-VALIDATION (OWNED)

Four checks, each over CIOS's **own declaration only**. Precedent: `UCCEP-000000`'s `CK-SELF-DECLARATION`, `CK-SELF-NO-ENUMERATION`, `CK-SELF-WRITE-SCOPE`, `CK-SELF-DETERMINISM`.

| ID | Check | Validates | Invariant | Fails when |
|---|---|---|---|---|
| `CIOS-CK-PARTITION` | partition disjointness and exhaustiveness | `CIOS-PT-*` assignment over the work set | `CIOS-INV-01` | an item is in two partitions, or in none |
| `CIOS-CK-TOTAL-ORDER` | priority order totality | the `CIOS-K-01 … K-08` evaluation | `CIOS-INV-09` | any tie remains unresolved after the full key vector |
| `CIOS-CK-EPOCH` | epoch binding immutability | `CIOS-ID-19` on in-flight items | `CIOS-INV-04` | an in-flight item's plan epoch is rebound |
| `CIOS-CK-ADOPTION` | adoption atomicity and scope | `E-14` adoption | `CIOS-INV-04`; `CIOS-01` VI.2 | adoption is partial, or reaches outside `CIOS-PT-03` |

### 4.1 Additional self-validation of the declaration itself

Performed by `IMR-003A-R1/r1_verify.py` and reported in `IMR-003A-R1/08-ARCHITECTURE-VERIFICATION-REPORT.md`:

| Check | Validates |
|---|---|
| cardinality | 24 engines · 48 ports · 24 stages · 22 identity fields · 4 planes · 4 partitions · 4 queues · 8 key elements · 24 laws · 12 invariants |
| acyclicity | Kahn topological sort over the `DERIVES` edge set (`CIOS-INV-05` for CIOS's graph) |
| enforcer coverage | every law names a located enforcer (`CIOS-01` Art II requirement) |
| engine binding coverage | every engine is BOUND, COMPOSING-with-`VII.3`-citation, or ABSENT-with-owner |
| gate coverage | all 14 located gates bound |
| write-scope single-writer | every mutable target has exactly one writer (`CIOS-INV-02`) |
| reference resolution | every located path CIOS cites exists at the baseline (`CIOS-INV-11`) |
| zero-enumeration | no prohibited enumeration in the CIOS corpus (`CIOS-L-22`) |

### 4.2 Self-validation limits

| Rule | Statement |
|---|---|
| `VR-10` | A `CIOS-CK-*` check binds **no** corpus artifact and issues **no** verdict over any located concern. |
| `VR-11` | A `CIOS-CK-*` check is **not** a `CEP-004` validation and confers no `CEP-004` status. |
| `VR-12` | A `CIOS-CK-*` check creates no registry and no gate (`CIOS-INV-12`; `AC-4`). |
| `VR-13` | A `CIOS-CK-*` pass does **not** discharge any located gate, finding, or `GG-*`/`CIOS-G-*` gate. |
| `VR-14` | Self-validation is scoped to CIOS's declaration; it makes no claim about the repository. |

---

## 5. INHERITED VALIDATION DEGRADATION

| Finding | Effect on validation | CIOS response |
|---|---|---|
| `UCCEP-F-006` | `ukb validate` degrades to structural-only checks when `jsonschema` is absent — **silently** | identity-record validation (`CIOS-S-11`, `S-12`) inherits that degradation. Per `CIOS-L-07`, CIOS treats a **degraded** validation as a **failure**, not a pass. Recorded as a bound; not discharged. |
| `UCCEP-F-003` | the located graph validator reports a cycle while returning `is_valid=true`, exit 0 — **fails open** | `CIOS-S-14` treats a *reported* cycle as failure regardless of the returned flag (`E-08` FAIL). `CIOS-INV-05` is not machine-enforced corpus-wide. |
| `UCCEP-F-005` | historical gate bypassability — five gates were absent from CI | CIOS relies on gates **now bound in CI** and claims no historical enforcement. |
| `UCCEP-F-001` | the located planning-closure gate has no reachable PASS state | CIOS may not claim a **measured** planning verdict through it. |
| `UCCEP-F-002` | traceability RED, 1198/1198 incomplete | CIOS may not claim traceability closure (`CIOS-17` §5); the `CEP-001` XVIII precondition is unsatisfied. |

**Fail-closed on degradation is the operative rule.** Where a located validator degrades, CIOS reads the degraded result as a failure rather than inheriting a false pass. This is `CIOS-L-07` applied to validator quality rather than to evidence quality, and it is the only response available to an instrument that may not repair a located validator.

---

## 6. VALIDATION PROPERTIES

| Property | Value |
|---|---|
| Validation rules documented | **14** (`VR-01 … VR-14`) |
| Located validators bound | **9** (S-A) + **14** located gates (S-B) |
| Parallel validators created over located concerns | **0** (`AC-4`) |
| Self-checks over CIOS's own declaration | **4** (`CIOS-CK-*`) + 8 declaration checks in `r1_verify.py` |
| Corpus artifacts validated by CIOS | **0** |
| `CEP-004` statuses claimed by CIOS | **0** |
| Located gates bypassed | **0** |
| Located findings discharged | **0** |
| Degraded located validations treated as passes | **0** |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact documents validation rules and binds each to a **located** validator, except four self-checks over CIOS's own declaration which bind no corpus artifact and confer no `CEP-004` status. CIOS holds no validation authority, validates no corpus artifact, and discharges no located finding. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-15` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**

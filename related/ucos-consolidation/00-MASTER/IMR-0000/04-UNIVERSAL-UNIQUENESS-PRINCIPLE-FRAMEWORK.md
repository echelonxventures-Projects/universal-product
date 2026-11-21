# IMR-0000/04 — UNIVERSAL UNIQUENESS PRINCIPLE FRAMEWORK

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `04` — Universal Uniqueness Principle Framework (**deliverable 4**) |
| ARTIFACT KIND | Framework (`CMG-K-05`) — **derived conformance projection**, zero net-new law |
| CLOSES | `00A` `PGAP-07` — the seven singularities are enforced in five instruments and stated as one principle nowhere |
| NUMERIC CONTRACT | **9 clauses**, `UUP-01 … UUP-09` — the instruction's seven singularities plus its two invariance rules |
| CENTRAL CLAIM | **Every clause names a located enforcer. This framework legislates nothing.** A clause without a located enforcer would itself be a finding (`CIOS-01` Art II discipline). |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | Located instrument governs; then `IMR-003A`; then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. WHY THIS FRAMEWORK IS NOT A NEW LAW

The instruction states seven properties every canonical entity shall possess, and two rules about identity and names. Every one of the nine is **already enforced** somewhere in the corpus. Restating them as new law would breach `CIOS-L-08` (Knowledge Once) and create a second authority over each — `CIOS-L-09`.

The framework's contribution is therefore **structural, not substantive**:

| What is new | What is not new |
|---|---|
| the **closure claim**: these nine, together, are exhaustive over uniqueness | any individual clause |
| the **enforcer binding**: one table where each clause's located owner is named | the enforcement itself |
| the **conformance test**: what must be checked, per clause, to say uniqueness holds for an object | the checks — every one is located |
| the **measured state**: what the corpus reports for each clause at `b26c5bb` | the measurements — all read from located registers |

This is the pattern `CIOS-14` used for its 33 governance rules: *"all 33 `GR-*` rules externally owned"*. Precedent, not invention.

---

## 2. THE NINE CLAUSES

### 2.1 The seven singularities

| ID | Clause | Statement | Located enforcer | Violation condition |
|---|---|---|---|---|
| **`UUP-01`** | **One canonical identity** | Every canonical entity possesses exactly one globally unique canonical identity: minted once, immutable, opaque, authority-namespaced; never content-, order- or path-derived; never reused after retirement. | `AIF-L02` (durable identity) · `AIF-L07` (uniqueness within authority) · `AIF-L17` (no reuse) · `REG-AUTO-001` *"Artifact Creation = Artifact Registration"* · `id-ledger.json` | two identities for one entity; one identity for two entities; a reused identity; a manually assigned identity |
| **`UUP-02`** | **One constitutional owner** | Every canonical entity has exactly one constitutional owner, resolvable to a single located instrument or authority tier. | `CEP-001` LAW-4 (Single Canonicity) · `UAKOS-CLOSURE-002` canonical-owner register · `CMG-000001` tiers `T0…T5` · `02-CANONICAL-OWNERSHIP-MATRIX.md` | zero owners (orphan); two or more owners; an owner that is not located |
| **`UUP-03`** | **One canonical registration** | Every canonical entity is registered exactly once, in exactly one canonical home, through exactly one registration transaction. | `REG-AUTO-001` §7 (single transaction `T`) · `UAKOS-CLOSURE-002` (`duplicate_canonical_homes`) · `artifacts.json` · `GOV-INT-001` §6.1 (single store, single ledger, single graph) | a second home; a second register entry; a second synchronization pass |
| **`UUP-04`** | **One lifecycle** | Every canonical entity advances on exactly one lifecycle per axis, and the axes are orthogonal, not alternative. No entity has two lifecycles on the same axis. | `REG-AUTO-001` §5 (the one master lifecycle) · `UCI-OPT-001` row 3 (*"one master lifecycle; change/knowledge/version/rollback are states within it"*) · `IEC-001` `06` · `CIOS-01` Art V · `CIOS-07` | a second state machine on any axis; a state that belongs to two axes; an ungated transition |
| **`UUP-05`** | **One traceability chain** | Every canonical entity has exactly one rooted traceability chain to its authority and its evidence, expressed on the one graph. | `CEP-008` · `CEP-001` XVIII · `UMB-007` · `relationships.json` (the **one** graph) · `GOV-INT-001` §2.6 (*"never a parallel graph"*) · `CIOS-17` | a second graph; a second edge vocabulary; an orphan node; a chain that does not root |
| **`UUP-06`** | **One validation chain** | Every canonical entity is validated through exactly one validation authority and one check surface. Validation is never duplicated, never re-implemented, never bypassed. | `CEP-004` · `engine/validation` · `verify.sh` · `uccep.json` `checks` (`CK-*`) · `G-10` · `CEP-001` LAW-5 (Non-Bypass) | a second validator over one concern; a re-implemented gate; a bypassed check |
| **`UUP-07`** | **One certification chain** | Every canonical entity is certified through exactly one certification authority, and its standing is capped by that authority's declared ceiling. | `CEP-005` · `certification.json` · `CERTIFICATION-REGISTRY.md` · EC-3 certification gate · `G-11` · `CIOS-16` | a second certifier; a self-certification; a claim above the declared ceiling |

### 2.2 The two invariance rules

| ID | Clause | Statement | Located enforcer | Violation condition |
|---|---|---|---|---|
| **`UUP-08`** | **Identity is immutable** | Once minted, no identity field may be altered. Correction proceeds by **successor only**, never by mutation. | `CIOS-L-13` · `AIF-L17` (forward-only compensation) · `CEP-009` Art IV.3, Art XI · `IDR-7` | any in-place edit of a minted field; a "corrected" identity; a deleted identity |
| **`UUP-09`** | **Names may evolve; identity never** | The canonical name is mutable without limit and carries no identity. A rename **appends** to the object's name sequence and moves nothing. No ordering, uniqueness or authority may be derived from a name. | `AIF-L03` (P2 durable identity vs P4 logical identity — orthogonal, non-substitutable) · `AIF-L04` (ordering authority is the witnessed ordinal, never a name or timestamp) · `CIOS-L-15` · `UMB-004`/`UMB-005` nomenclature | identity derived from a name; uniqueness asserted over names; a rename treated as a new entity; order derived from a name |

---

## 3. THE CLOSURE CLAIM

`UUP-01 … UUP-09` are claimed **exhaustive** over uniqueness. The claim is testable: any uniqueness breach must reduce to at least one clause.

| Breach class | Reduces to |
|---|---|
| duplicate identifier | `UUP-01` |
| duplicate canonical home | `UUP-03` |
| duplicate owner / unowned concept | `UUP-02` |
| parallel identifier system | `UUP-01` + `UUP-03` |
| second subject token for one subject | `UUP-01` (identity) + `UUP-02` (owner) |
| second registry / second store | `UUP-03` |
| second state machine | `UUP-04` |
| second graph / second edge vocabulary | `UUP-05` |
| second validator / bypassed gate | `UUP-06` |
| self-certification / claim above ceiling | `UUP-07` |
| in-place edit of a minted field | `UUP-08` |
| identity inferred from a name; order inferred from a name or timestamp | `UUP-09` |
| duplicate authority over one concern | `UUP-02` |
| second plan, second queue, second gate | `UUP-04` (lifecycle) + `UUP-02` (owner) |

**Every breach class named across `CEP-001` LAW-4, `CIOS-L-09`, `GOV-001` Part 10, `IMR-003A` `AC-3` and `06-DUPLICATION-AND-OVERLAP-VERIFICATION.md` reduces to a clause. No residue class was found.** The claim is recorded as a claim, not proven exhaustive against future breach classes — `UUP-09`'s scope is fixed by this artifact and extensible only under `CEP-009` III.1.

---

## 4. CONFORMANCE TEST

What must be checked, per clause, to say uniqueness holds for a canonical object. **Every check is located.** This framework performs none of them; it states which one answers which clause.

| Clause | Conformance question | Located check / measurement |
|---|---|---|
| `UUP-01` | Does the object have exactly one identity, present exactly once in the ledger? | `id-ledger.json` uniqueness; `ukb validate` no-duplicate-IDs; `CK-REG-VALIDATE` |
| `UUP-02` | Does exactly one owner resolve? | `UAKOS-CLOSURE-002` `orphan_concepts`, `not_homed_concepts`; `CK-CLOSURE-P1` |
| `UUP-03` | Does exactly one home resolve, through one transaction? | `UAKOS-CLOSURE-002` `duplicate_canonical_homes`; `ukda_content_hash_duplicates`; `REG-AUTO-001` transaction `T` |
| `UUP-04` | Is the object on exactly one state per axis, with every transition gated and logged? | `REG-AUTO-001` §5; `IEC-001` `06`; `CIOS-INV-08`; `08` `LR-*` |
| `UUP-05` | Does the object's chain root, on the one graph, with no orphan node? | `relationships.json` referential integrity; `ukb validate`; `CK-VERIFY`; `CEP-001` XVIII |
| `UUP-06` | Was the object validated by the one authority, with no bypass? | `verify.sh`; `engine/validation`; `uccep.json` `checks`; `G-10` |
| `UUP-07` | Is the object's certification from the one authority, within its ceiling? | `certification.json`; `G-11`; `uccep.json` `certification_ceiling` |
| `UUP-08` | Has any minted field been edited in place? | `AIF-L17`; append-only store discipline; `content_hash` divergence without a successor |
| `UUP-09` | Is any identity, order or uniqueness claim derived from a name or timestamp? | `AIF-L04`; `CIOS-K-08` totality proof (`CIOS-10` §2.4); `CK-DETERMINISM-BUILD` |

### 4.1 Measured state at `b26c5bb`

Read from located registers. **These are observations, not this mission's claims.**

| Clause | Measurement | Value | Source |
|---|---|---|---|
| `UUP-01` | duplicate content hashes | **0** | `closure.json` `ukda_content_hash_duplicates` |
| `UUP-02` | orphan concepts | **0** | `closure.json` `orphan_concepts` |
| `UUP-02` | unowned concepts | **0** | `closure.json` `not_homed_concepts`; `in_repo_unhomed = 0` |
| `UUP-03` | duplicate canonical homes | **0** | `closure.json` `duplicate_canonical_homes` |
| `UUP-03` | concepts homed | **434 / 434** | `closure.json` `concept_total`, `gap_total = 0`, determination `CLOSED` |
| `UUP-04` | second state machine introduced by this mission | **0** | `08` |
| `UUP-05` | traceability closure corpus-wide | **NOT ACHIEVED** — incomplete for all **1198** registered artifacts | `UCCEP-F-002`; `CIOS-17` §5 |
| `UUP-06` | constitutional gates PASS | **6 / 14** · blocking failures **none** | `uccep.json` |
| `UUP-06` | validation soundness | **DEGRADED** — schema validation degrades silently to structural-only | `UCCEP-F-006`; `CIOS-G-05` OPEN |
| `UUP-07` | certification standing | **`CERTIFIED-PROVISIONAL`**, ceiling-bound; 31 of 43 artifacts PROVISIONAL | `uccep.json`; `CIOS-GAP-08`; `VAC-01` |
| `UUP-08` | minted fields altered by this mission | **0** | `MC-01`; `00A` Output 7 |
| `UUP-09` | ordering claims derived from a name or timestamp | **0** | `CIOS-L-15`; `AIF-L04` |

**Two clauses are not satisfied corpus-wide at `b26c5bb`, and neither is this mission's to satisfy:** `UUP-05` (traceability closure, `CIOS-G-06`, owner `CEP-008`) and `UUP-06` (validation soundness, `CIOS-G-05`, owner of `ukb validate`). `UUP-07` is ceiling-bound behind `VAC-01` (`CIOS-G-03`). All three are recorded as findings in `23` and are inherited, not introduced.

---

## 5. HOW THE PRINCIPLE BINDS THIS MISSION ITSELF

A uniqueness framework that exempted its own author would be worthless. Applied to `IMR-0000`:

| Clause | Applied to `IMR-0000` | Result |
|---|---|---|
| `UUP-01` | Does `IMR-0000` mint or claim an identity? | **No.** Mission-local families (`SS-*`, `UOM-A-*`, `UUP-*`, …) are declaration slots, absent from `id-ledger.json`, `artifacts.json` and `CMG-REGISTRY.json`, and may never be presented to `REG-AUTO-001` (`NS-3`) |
| `UUP-02` | Does `IMR-0000` claim ownership of anything owned elsewhere? | **No.** Zero mechanisms owned; zero concerns claimed (`CIOS-G-02` OPEN) |
| `UUP-03` | Does `IMR-0000` create a second home or register? | **No.** One home, `00-MASTER/IMR-0000/`, registration-excluded; zero registers created |
| `UUP-04` | Does `IMR-0000` create a lifecycle? | **No.** `08` reconciles four located axes and introduces no state |
| `UUP-05` | Does `IMR-0000` create a graph or claim closure? | **No** to both. `21` is a mission-scoped matrix on the one graph; closure is expressly not claimed (`D-5`) |
| `UUP-06` | Does `IMR-0000` validate anything? | **No.** `20`'s `PCK-*` are self-checks over this mission's own declaration; a self-check is not a validation (`CIOS-15` `VR-04`) |
| `UUP-07` | Does `IMR-0000` certify anything? | **No.** Ceiling `CERTIFIED-PROVISIONAL` acknowledged; no certification asserted |
| `UUP-08` | Does `IMR-0000` alter a minted field? | **No.** `IMR-003A` unmodified; zero corpus writes |
| `UUP-09` | Does `IMR-0000` derive identity or order from a name? | **No.** `SS-01 … SS-17` identities are fixed; `CIOS-CORE … CIOS-EVO` are names carrying no identity — the split is the principle demonstrated on itself (`02` §2) |

**Nine of nine clauses hold for this mission's own declaration.** Re-checked as `PCK-03` in `20`.

---

## 6. WHAT THIS FRAMEWORK DOES NOT DO

| Not done | Located owner / reason |
|---|---|
| Legislate any uniqueness rule | every clause is located; `CIOS-L-08` |
| Perform any conformance check | `CEP-004`; `engine/validation`; `uccep.json` `CK-*` |
| Repair a duplicate, orphan or unowned entity | `UAKOS` owns repair; a duplicate is a **finding** (`SS-09`, `SS-15`) |
| Discharge `UUP-05`, `UUP-06` or the `UUP-07` ceiling | `CIOS-G-06`, `CIOS-G-05`, `CIOS-G-03` — all OPEN, all owner-held |
| Define a new identity, name, home, lifecycle, graph, validator or certifier | `CIOS-INV-12`; `MC-03` |
| Claim exhaustiveness against future breach classes | §3 — recorded as a claim, extensible under `CEP-009` III.1 only |

---

## AUTHORITY BOUNDARY (MANDATORY)

This framework binds nine uniqueness clauses to **located** enforcers and states a conformance test whose every check is located. It legislates nothing, checks nothing, repairs nothing, discharges no gate and authorizes no execution. Every enforcer named is located in an instrument existing independently at `b26c5bb`. Two clauses are recorded as unsatisfied corpus-wide, and both are inherited findings owned elsewhere. Where this framework and a located canonical instrument disagree, **the located instrument governs and this framework SHALL be corrected**.

**END OF ARTIFACT — `IMR-0000/04` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**

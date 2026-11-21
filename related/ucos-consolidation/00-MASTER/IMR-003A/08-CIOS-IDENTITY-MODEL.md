# CIOS-08 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · IDENTITY MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-08` — Identity Model (mission Output 8) · **also the Canonical Mission Object Specification** (required output 8) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| DISCHARGES | `CIOS-INV-07` (complete identity record, all 22 fields) · `CIOS-01` Art X.1 limb 7 |
| NUMERIC CONTRACT | **exactly 22 identity fields**, `CIOS-ID-01 … CIOS-ID-22`. Fixed by `CIOS-01` Art X.1; not alterable by data change (`NS-4`). |
| CANONICAL NAME | **CIOS Canonical Submission Object.** The recovery instruction's "Canonical Mission Object" resolves to this (`IMR-003A-R1/10` §3). |
| AUTHORITY OF ITS OWN | **NONE.** CIOS **mints nothing** (`CIOS-L-14`; `CIOS-01` I.5). It composes a record from fields produced by located minting authorities. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE COMPOSITION-NOT-MINTING RULE

This is the single most important constraint on the artifact, and the one most easily violated by a design of this kind.

| CIOS **does** | CIOS **does NOT** |
|---|---|
| compose a 22-field record | mint any field |
| read fields produced by `AIF` / `REG-AUTO-001` / `UAKOS` / `CEP-009` | allocate an identifier |
| assert completeness (all 22 resolved) | assert correctness of a minted value |
| fail closed on any unresolved field | supply a default, placeholder or derived substitute for a missing minted field |

Four located prohibitions make this non-negotiable:

| Prohibition | Source |
|---|---|
| Identity is minted by the system at admission; **manual assignment is a hard rejection** | `CIOS-L-12`; `REG-AUTO-001` *"Artifact Creation = Artifact Registration"* |
| Once minted, no identity field may be altered; correction is by **successor only** | `CIOS-L-13`; `CEP-009` Art IV.3 / Art XI; `AIF-L17` |
| CIOS mints nothing; **no parallel identifier system exists** | `CIOS-L-14`; `GOV-001` Part 10 |
| Ordering authority is the **witnessed admission ordinal**, never a timestamp | `CIOS-L-15`; `AIF-L04` |

**Consequence.** No `CIOS-ID-*` field is a corpus identifier, and none may be presented to `REG-AUTO-001` or entered in the `id-ledger` (`NS-3`). A `CIOS-ID-*` name denotes a **slot in a composed record**, not an allocated identity.

---

## 2. RECORDED vs DERIVED (`AIF-L01`)

`AIF-L01` (Bifurcation of Truth) requires that **every datum is RECORDED or DERIVED, never both**. Applying it to the 22 fields resolves what would otherwise be a contradiction between `CIOS-L-13` (immutable identity) and the fact that a submission's partition and priority necessarily change over its life.

| Class | Meaning | Mutability | Fields |
|---|---|---|---|
| **RECORDED — immutable** | minted or resolved once, then never altered | immutable; correction by successor only | `ID-01 … ID-17`, `ID-21`, `ID-22` (19 fields) |
| **RECORDED — append-sequence** | a one-way sequence of events, each appended, none overwritten | append-only; the sequence is immutable, its head advances | `ID-18` (1 field) |
| **RECORDED — bind-once** | unset until a defining event, immutable thereafter | immutable once bound | `ID-19` (1 field) |
| **DERIVED** | a pure function of Repository Truth + declared data; recomputed, **never** recorded as truth | recomputed per epoch | `ID-20` (1 field) |

This is why the model contains no contradiction: `ID-18` (partition) is not *mutated* when an item advances `OPEN → IN-FLIGHT`; a transition event is *appended*. And `ID-20` (priority) is never stored at all, so `CIOS-L-13` does not reach it.

---

## 3. THE 22 FIELDS

"Minting authority" is the **located** owner that produces the value. CIOS reads it.

### 3.1 Identity planes — `CIOS-ID-01 … CIOS-ID-08`

Bound to `AIF-L03`'s five orthogonal, non-substitutable identity planes.

| Field | Name | AIF plane | Minting authority | Class |
|---|---|---|---|---|
| `CIOS-ID-01` | **Durable identity** — minted-once, immutable, opaque, authority-namespaced; never content/order/path-derived; never reused | P2 | `AIF-L02`; `REG-AUTO-001` | RECORDED-immutable |
| `CIOS-ID-02` | **Authority identifier** — the minting authority's own identity | — | `AIF-L06`, `AIF-L09` | RECORDED-immutable |
| `CIOS-ID-03` | **Local key** — the authority-local component of the admission key | — | `AIF-L06` | RECORDED-immutable |
| `CIOS-ID-04` | **Content digest** — multihash over the versioned Canonical Content Form; **verifies, never identifies** | P1 | `AIF-L05` | RECORDED-immutable |
| `CIOS-ID-05` | **CCF version** — the Canonical Content Form version the digest is taken over | P1 | `AIF-L05` | RECORDED-immutable |
| `CIOS-ID-06` | **Witnessed admission ordinal** — authority-local, recorded at mint, rendered and never recomputed; **not globally monotonic** | P3 | `AIF-L04` | RECORDED-immutable |
| `CIOS-ID-07` | **Logical identity** — the version/lineage-bearing logical handle | P4 | `AIF-L03`, `AIF-L15` | RECORDED-immutable |
| `CIOS-ID-08` | **Runtime identity** — the runtime-scoped handle, if any | P5 | `AIF-L03` | RECORDED-immutable |

### 3.2 Subject and ownership — `CIOS-ID-09 … CIOS-ID-14`

| Field | Name | Minting / resolving authority | Class |
|---|---|---|---|
| `CIOS-ID-09` | **Subject** — what the submission is about | submitter, validated at `CIOS-S-01` | RECORDED-immutable |
| `CIOS-ID-10` | **Kind** — the artifact kind | `CMG-REGISTRY.json` `kinds` (`CMG-K-01 … CMG-K-24`) | RECORDED-immutable |
| `CIOS-ID-11` | **Canonical home** — the single canonical home | `UAKOS-CLOSURE-002` (resolved by `E-04` at `CIOS-S-05`) | RECORDED-immutable |
| `CIOS-ID-12` | **Canonical owner** — the single owner | `UAKOS-CLOSURE-002` (resolved by `E-04` at `CIOS-S-06`) | RECORDED-immutable |
| `CIOS-ID-13` | **Family** — the family, which maps to an owner and a target | `IMG-001` `02` family→owner map | RECORDED-immutable |
| `CIOS-ID-14` | **Declared scope** — the scope claimed, against which overlap is resolved | submitter, resolved by `E-05` at `CIOS-S-07` | RECORDED-immutable |

### 3.3 Admission determinations — `CIOS-ID-15 … CIOS-ID-17`

| Field | Name | Authority | Class |
|---|---|---|---|
| `CIOS-ID-15` | **Declared dependencies** — the dependency set, cycle-checked at `CIOS-S-14` | submitter; verified by `engine/graph`, `G-08` | RECORDED-immutable |
| `CIOS-ID-16` | **Recurrence disposition** — `NEW` \| `EXTEND`; never `CREATE` for recurring knowledge | `UAKOS`; `CK-CLOSURE-P1`, `CK-CLOSURE-P2`; `G-02`/`G-03` | RECORDED-immutable |
| `CIOS-ID-17` | **Primary change class** — exactly one (`CEP-009` IV.6) | `CEP-009` IV.1 | RECORDED-immutable |

### 3.4 CIOS-derived fields — `CIOS-ID-18 … CIOS-ID-20`

These three are the **only** fields CIOS itself produces, and each corresponds to an Art VII.3-authorized contribution. They are the reason `CIOS-08` is not wholly a restatement of `AIF`.

| Field | Name | Produced by | Art VII.3 row | Class |
|---|---|---|---|---|
| `CIOS-ID-18` | **Partition** — current mutability partition (`CIOS-PT-00`/`03`/`02`/`01`) | `E-10`, `E-19` | r3 | RECORDED-append-sequence |
| `CIOS-ID-19` | **Bound plan epoch** — the epoch active at dispatch; held until terminal state (`CIOS-INV-04`) | `E-16` | r4 | RECORDED-bind-once |
| `CIOS-ID-20` | **Priority key tuple** — the evaluated `CIOS-K-01 … CIOS-K-08` vector | `E-12` | r6 | **DERIVED** — recomputed per epoch, never recorded as truth |

### 3.5 Provenance and evidence — `CIOS-ID-21 … CIOS-ID-22`

| Field | Name | Authority | Class |
|---|---|---|---|
| `CIOS-ID-21` | **Provenance** — submitter authority and origin of the submission | `AIF-L11` (signed events); `CEP-008` | RECORDED-immutable |
| `CIOS-ID-22` | **Evidence set reference** — the evidence satisfying `CIOS-S-18` | `CEP-008`; `G-12`; `CK-DECISION-EVIDENCE` | RECORDED-immutable |

---

## 4. FIELD RECONCILIATION

| Group | Fields | Range |
|---|---|---|
| Identity planes | **8** | `ID-01 … ID-08` |
| Subject and ownership | **6** | `ID-09 … ID-14` |
| Admission determinations | **3** | `ID-15 … ID-17` |
| CIOS-derived | **3** | `ID-18 … ID-20` |
| Provenance and evidence | **2** | `ID-21 … ID-22` |
| **Total** | **22** | matches `CIOS-01` Art X.1 |

| Property | Value |
|---|---|
| Fields minted by CIOS | **0** (`CIOS-L-14`) |
| Fields minted by located authorities | **8** (`ID-01 … ID-08`, all `AIF`/`REG-AUTO-001`) |
| Fields resolved by located engines/registers | **11** (`ID-09 … ID-17`, `ID-21`, `ID-22`) |
| Fields produced by CIOS composition | **3** (`ID-18 … ID-20`), each Art VII.3-authorized |
| RECORDED fields | **21** |
| DERIVED fields | **1** (`ID-20`) |
| Fields both RECORDED and DERIVED | **0** (`AIF-L01` satisfied) |
| Fields alterable after mint | **0** (`CIOS-L-13`; `ID-18` appends, `ID-19` binds once, `ID-20` is not recorded) |
| Corpus identifiers consumed | **0** (`NS-3`) |
| Parallel identifier systems created | **0** (`GOV-001` Part 10) |

---

## 5. COMPLETENESS RULE — `CIOS-INV-07`

| ID | Rule | Basis |
|---|---|---|
| `IDR-1` | A submission advances past `CIOS-S-12` only when **all 22 fields are resolved**. | `CIOS-INV-07` |
| `IDR-2` | A record with 21 of 22 fields resolved is **not a degraded record; it is not a record**. Non-admission. | `CIOS-L-07` |
| `IDR-3` | CIOS SHALL NOT supply a default, placeholder, sentinel or derived substitute for an unresolved **minted** field. | `CIOS-L-14`; `CIOS-L-12` |
| `IDR-4` | `CIOS-ID-19` is exempt from `IDR-1`: it is unset until dispatch, and binding it before dispatch would be a false record. Its resolution point is `CIOS-S-23`, not `CIOS-S-12`. | `CIOS-INV-04` |
| `IDR-5` | `CIOS-ID-20` is exempt from `IDR-1` as a DERIVED field: it is evaluated, not resolved, and is never stored. | `AIF-L01` |
| `IDR-6` | Manual assignment of any field is a **hard rejection**, not a warning. | `CIOS-L-12` |
| `IDR-7` | Correction of any RECORDED-immutable field proceeds by **successor only**. | `CIOS-L-13`; `AIF-L17` |

`IDR-4` and `IDR-5` are stated because `CIOS-INV-07` as written ("all 22 fields resolved") would otherwise be unsatisfiable at `CIOS-S-12` — `ID-19` cannot be known pre-dispatch. The invariant is therefore read as *all 22 fields resolved at their declared resolution points*, and this artifact declares those points. Recorded as an interpretation, not an amendment; `CIOS-01` governs if the located reading differs.

### 5.1 Resolution points

| Field(s) | Resolved at |
|---|---|
| `ID-09`, `ID-14`, `ID-15`, `ID-21` | `CIOS-S-01` (submission) |
| `ID-16` | `CIOS-S-03` / `CIOS-S-04` |
| `ID-11`, `ID-12` | `CIOS-S-05` / `CIOS-S-06` |
| `ID-10` | `CIOS-S-09` |
| `ID-01 … ID-08`, `ID-13` | `CIOS-S-11` |
| `ID-17` | `CIOS-S-16` |
| `ID-22` | `CIOS-S-18` |
| `ID-18` | `CIOS-S-19` (first value), then appended at each partition transition |
| `ID-20` | `CIOS-S-20`, and re-evaluated at every epoch |
| `ID-19` | `CIOS-S-23` (dispatch) |

---

## 6. ORDERING AUTHORITY

`CIOS-L-15` fixes ordering authority as the witnessed admission ordinal, never a timestamp. The reason is structural, not stylistic:

| Property | Timestamp | Witnessed ordinal (`CIOS-ID-06`) |
|---|---|---|
| Unique within an authority | **no** — two admissions can share one | **yes** (`AIF-L07`) |
| Recomputable from the file set | yes — and therefore forgeable by reordering | **no** (`AIF-L04`) |
| Globally monotonic | assumed, but false under partition | **not claimed** (`AIF-L04`) |
| Yields a **total** order | **no** | **yes** |

Because `CIOS-INV-09` requires a total order, and because a timestamp cannot supply one, `CIOS-ID-06` is the final element of the priority key vector (`CIOS-K-08`, see `CIOS-10`). Timestamps remain admissible as **evidence** (`CEP-008`) and are never used as order.

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares the composition of an identity record. It mints nothing, allocates nothing, owns no registry, no gate, no identifier space and no concern. Every minting authority named is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-08` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**

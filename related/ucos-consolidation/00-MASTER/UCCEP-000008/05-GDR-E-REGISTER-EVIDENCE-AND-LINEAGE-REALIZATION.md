# Output 5 — Decision Family **GDR-E** · Register, Evidence and Lineage Realization

> **STATUS DOMAIN:** GOVERNANCE (determination) · **STATUS BASIS:** located clauses of `REG-AUTO-001` (`CMG-DLG-13`), `UCI-001` (`CMG-DLG-15`) and `GOV-INT-001` (`CMG-DLG-16`), plus the gaps, risks and observations recorded by their owners and reproduced by `UCCEP-000007` at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000008` · OUTPUT 5 |
| FAMILY | **GDR-E** — Register, Evidence and Lineage Realization |
| DECISIONS | `GD-16` (DDI-16) · `GD-17` (DDI-17) · `GD-18` (DDI-18) · `GD-19` (DDI-19) · `GD-20` (DDI-20) |
| FAMILY SUBJECT | The five matters where a measured absence or lag must be dispositioned: a stale finding record, an evidence-ignore policy, an unexplained gap in programme lineage, four unrealized registers, and a baseline that exists only on one machine. |
| AUTHORITY | None of its own. Each decision is rendered within the located Owner's already-declared law (Output 0 §2). |
| FAMILY CHARACTER | The only family carrying **registrations of work**. Three decisions dispose to `CEP-002` 28.13(c) with a located work package; two are recognitions. **No work is performed here** — each package names an owner, a constitutional route and an acceptance condition, and is discharged by that owner. |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; every determination PROVISIONAL under `CMG-L-12` (condition **C-3**, constraint **K-09**). |

---

## GD-16 — The `UCCEP-F-003` finding record

| Field | Record |
|---|---|
| **Decision ID** | `GD-16` |
| **Title** | Whether `UCCEP-F-003`'s record is updated to reflect its discharged substance |
| **Resolves** | `DDI-16` |
| **Family** | GDR-E |

### Problem Statement

Output 16 records that the owning authority is *"`UCCEP-000000` / `engine/graph`; recorded as **OA-2** under condition **C-2**"*, and that *"The binding is another programme's declaration; boundary **X-9** forbids cross-programme edits."* The substance of the finding is discharged in committed code while its record remains open.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| `DG-2` verbatim: *"`UCCEP-F-003` remains recorded `GOVERNED / blocking: true` and is still named in the live `certification_ceiling`, while its substance is discharged in committed code (`engine/graph/validation.py` now includes `dependency_cycle` in `is_valid`)"*; measured state *"record open, substance closed"*; owning authority *"`UCCEP-000000` / `engine/graph` — the binding is another programme's declaration (**X-9**)"* | The exact divergence between record and substance, and its owner | `00-MASTER/UCCEP-000007/13-KNOWN-GAPS.md` §2 |
| `UCCEP-F-003` title: *"`engine.graph.cli validate` reports a dependency cycle but returns `is_valid=true` and exit 0 (fail-open)"*; class GOVERNED; blocking **true**; work package `WP-UCCEP-003` | The finding as its owner declares it | `00-MASTER/UCCEP-000000/uccep-bindings.json → findings[]` |
| Output 8 §4 — `engine/graph/validation.py` includes `dependency_cycle` in the `is_valid` conjunction; the docstring cites `UCCEP-F-003` discharged by `WP-UCCEP-003` T-2 / `UCCEP-000005`; *"record state remains open"* | The substance is discharged in committed code, verified independently | `00-MASTER/UCCEP-000007/08-DEPENDENCY-INVENTORY.md` |
| **OA-2** — *"Record `UCCEP-F-003` as discharged in the bindings and regenerate the findings register"* · owner **`UCCEP-000000` / `engine/graph`** · discharges O-02 · `UCCEP-F-003` · **C-2** · priority P1 · suspensive: *"No (bars certification claims)"* · status **OPEN** | A located work record already exists, with owner, route and acceptance | `00-MASTER/UCCEP-000006/07-OPERATOR-ACTION-REGISTER.md` §1 row 2 |
| **C-2** — a *continuing* condition of the `UCCEP-000006` authorization: *"**C-2** finding record before any certification claim"* | The condition the package discharges | `00-MASTER/UCCEP-000006/10-HANDOVER-TO-UCCEP-000007.md` |
| `DR-1`/`R-01` — *"`UCCEP-F-003` record lag"*, LOW, non-blocking, treatment **C-2 / OA-2**, *"**still open** — binding records `GOVERNED / blocking: true`"* | The risk owner's own assessment: real but low, and already treated | `00-MASTER/UCCEP-000007/14-KNOWN-RISKS.md` §1 |
| Boundary **X-9** verbatim: protected area *"Another programme's outputs, registers or declarations — including `00-MASTER/UCCEP-000000/uccep-bindings.json` and `00-MASTER/UCCEP-000005/**`"* · rule *"**No cross-programme edits. C-2 is `UCCEP-000000`'s act, not the implementer's**"* | The prohibition, naming this exact file and this exact condition | `00-MASTER/UCCEP-000006/06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md` §2 |
| `ucda-decisions.json` `external_work_package_sources: ["00-MASTER/UCCEP-000000/uccep-bindings.json"]`, with the declared rationale *"A decision whose work is already registered elsewhere references that package instead of duplicating it (Zero Duplication, `CEP-002` 8.3)"* | The located mechanism for disposing to an **externally owned** work package without duplicating it | `00-MASTER/UCDA-000001/ucda-decisions.json` |
| Boundary **K-07** — `WP-UCCEP-001 … 005` are the registered set, **closed to addition** | A new `WP-UCCEP-*` package may not be coined; the existing route must be used | `00-MASTER/UCCEP-000007/11-CERTIFICATION-INVENTORY.md` §6 |

### Constitutional Authority

**`UCCEP-000000`** as the owner of the findings binding, and **`engine/graph`** as the owner of the validator — jointly named by `DG-2` and by **OA-2** as the owning authority. Boundary **X-9** is the constraint reserving the act to them. Note under `CMG-000001` X.1 (`CMG-L-01`): `UCCEP-000000` is absent from `CMG-REGISTRY.json` and is therefore **not cited here as constitutional authority**; it is cited as the **owner of its own declaration**, which is a different and lawful capacity — a programme's custody of its own register is not a claim of constitutional force. The constitutional authority for requiring the record's accuracy is `CEP-002` 9.1 / 25.4 (every declaration provable by evidence and traceability) and `CMG-000001` LII.6 (an undispositioned finding blocks certification).

### Decision

**The record SHALL be updated. The decision is YES — and the act is not this programme's to perform.**

1. **Determination on the merits:** `UCCEP-F-003`'s record is inaccurate as it stands. Its substance is discharged in committed code (`engine/graph/validation.py` includes `dependency_cycle` in the `is_valid` conjunction), while its binding records `GOVERNED / blocking: true` and it remains named in the live `certification_ceiling`. A record that names a factually discharged finding as blocking is a traceability inaccuracy, contrary to `CEP-002` 25.4's standard that every declaration be provable by evidence.
2. **The act is reserved.** Updating `00-MASTER/UCCEP-000000/uccep-bindings.json` and regenerating the findings register is `UCCEP-000000`'s act. **X-9** names that file explicitly and states the rule: *"C-2 is `UCCEP-000000`'s act, not the implementer's."* This programme therefore performs nothing.
3. **Route:** the work is **already registered** as **OA-2** under continuing condition **C-2**, with owner `UCCEP-000000` / `engine/graph`, priority P1, and acceptance *"Record `UCCEP-F-003` as discharged in the bindings and regenerate the findings register."* No new work package is created; **K-07** closes the `WP-UCCEP-*` set to addition and the located route is adequate.
4. **Standing constraint until discharged:** no certification claim SHALL be made while **C-2** is undischarged. This is C-2's own term (*"finding record before any certification claim"*) and is reinforced by `CMG-000001` LII.6.
5. **No re-litigation of the substance.** This decision does **not** re-assess whether the validator is correct. Output 8 §4 measures that it is, and `WP-UCCEP-003` T-2 / `UCCEP-000005` are recorded as having discharged it. Only the **record** is at issue.

### Rationale

The unusual shape of this decision — a clear YES coupled with a refusal to act — is required by two located rules pulling in the same direction.

**The merits are not in doubt.** Three independent records agree: `DG-2` measures record-open/substance-closed; Output 8 §4 verifies the code; `R-01` classifies it as record lag with treatment already assigned. There is no factual dispute to resolve, which is why this is a decided matter rather than a held one.

**The act is nonetheless barred.** **X-9** does not merely discourage the edit; it names `uccep-bindings.json` as a protected area, states that touching a protected area *suspends the authorization*, and identifies C-2 by name as another programme's act. A determining programme that edited it would breach the boundary it is bound by and would also violate `CEP-002` 22.4's standard that a party does not close its own matter — here, inversely, that a party does not close **another's** matter.

**The lawful disposition is therefore registration of work, not implementation.** And crucially, the work package need not be invented: **OA-2** already exists with all three elements `CEP-002` 28.13(c) requires — an owner (`UCCEP-000000` / `engine/graph`), a constitutional route (**C-2**, the continuing condition of the `UCCEP-000006` authorization), and an acceptance condition (bindings record discharged + findings register regenerated). `ucda-decisions.json` already declares `uccep-bindings.json` as an `external_work_package_sources` entry precisely so that a decision whose work is registered elsewhere **references** that package rather than duplicating it, citing Zero Duplication under `CEP-002` 8.3. Disposing to OA-2 uses that mechanism as designed; coining a new package would duplicate a located one and would breach **K-07** besides.

Clause 4 records the cost honestly. The record lag is low-severity but not harmless: while it stands, the certification ceiling names a finding that is factually discharged, so any certification claim would rest on a declaration its own owner's evidence contradicts.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-13` | Append-only: the correction is a new determination retaining the prior record, never an overwrite of history |
| Depended on by | `GD-15` | The ordering's acyclicity precondition (**K-02**) depends on the validator failing closed, whose record this closes |
| Depended on by | any certification claim | **C-2** bars such a claim until discharged |
| Blocked by | **X-9** | The act is reserved to `UCCEP-000000` |
| Constrained by | **K-07** | No new `WP-UCCEP-*` package may be coined; OA-2 is the route |

### Affected Programmes

`UCCEP-000000` — the owner, which must discharge OA-2. `UCCEP-000005` — cited as having discharged the substance via `WP-UCCEP-003` T-2; not edited. `UCCEP-000006` — cited for OA-2, C-2 and X-9; not edited. `UCCEP-000007` — cited for `DG-2` and Output 8 §4; not edited.

### Affected Registries

**None mutated by this programme.** `uccep-bindings.json` and the generated findings register are the *subject* of the routed work and are **not touched here** (**X-9**). When `UCCEP-000000` discharges OA-2, it writes them by its own generator under `GD-03`.

### Affected Constitutions

None amended. `CEP-002` 9.1 / 22.4 / 25.4 / 28.13(c); `CMG-000001` LII.6 and X.1 (for the capacity distinction) cited.

### Affected Implementations

**None.** `engine/graph/validation.py` is already correct and is read as evidence only; it is **X-8**-protected. No code change is required by this decision.

### Constraints

| Id | Constraint |
|---|---|
| `GD-16-C1` | This programme, and any consolidation implementer, SHALL NOT edit `00-MASTER/UCCEP-000000/uccep-bindings.json` or any generated findings register (**X-9**). |
| `GD-16-C2` | No certification claim SHALL be made while **C-2** is undischarged. |
| `GD-16-C3` | No new work package SHALL be coined for this matter; **OA-2** is the located route and **K-07** closes the `WP-UCCEP-*` set to addition. |
| `GD-16-C4` | Discharge SHALL be by append and regeneration, retaining the prior record (`GD-13-C2`, `CEP-002` 28.15). |
| `GD-16-C5` | `UCCEP-000000` SHALL NOT be cited as constitutional authority while absent from `CMG-REGISTRY.json` (`CMG-L-01`); it is cited here only as custodian of its own declaration. |

### Acceptance Criteria

Acceptance of the **disposition** (met by this decision):

1. The matter is disposed to a located work package carrying an owner, a constitutional route and an acceptance condition — satisfied by OA-2.
2. No edit to `uccep-bindings.json` is made by this programme.

Acceptance of the **work** (for `UCCEP-000000`, when it discharges OA-2):

3. `uccep-bindings.json → findings[]` records `UCCEP-F-003` as discharged, with the prior record retained.
4. `UCCEP-F-003` no longer appears in the live `certification_ceiling`.
5. The findings register is regenerated by its own generator, deterministically.
6. `DG-2` is closable, and **C-2** is discharged, unblocking certification claims.

### Traceability

`DDI-16` → `GD-16` → **OA-2** / **C-2**. Upstream: Output 16 §3 row DDI-16; `UCCEP-000007/13-KNOWN-GAPS.md` `DG-2`; `08-DEPENDENCY-INVENTORY.md` §4; `14-KNOWN-RISKS.md` `R-01`; `11-CERTIFICATION-INVENTORY.md` §4–§6 (`K-07`). Route: `UCCEP-000006/07-OPERATOR-ACTION-REGISTER.md` §1 row 2 (OA-2); `10-HANDOVER-TO-UCCEP-000007.md` (C-2); `06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md` §2 (X-9). Mechanism: `ucda-decisions.json → external_work_package_sources`. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-16`; precondition of `GD-15` clause 4; carried to `10-REMAINING-GOVERNANCE-GAPS.md`.

### Future Impact

Converts an ambiguous state — *"is the finding open or not?"* — into a determined one: the substance is closed, the record is wrong, the fix is owned by a named programme under an existing condition, and no certification claim may be made until it happens. It also sets the precedent that this register disposes matters it cannot touch by **routing to the located owner's existing package**, never by coining a parallel one.

### Disposition

**`CEP-002` 28.13(c) — REGISTERED AS AN IMPLEMENTATION WORK PACKAGE.**
Work package: **`OA-2`** — located at `00-MASTER/UCCEP-000006/07-OPERATOR-ACTION-REGISTER.md` §1 row 2. Owner: `UCCEP-000000` / `engine/graph`. Constitutional route: continuing condition **C-2** of the `UCCEP-000006` authorization. Acceptance condition: bindings record `UCCEP-F-003` discharged and the findings register regenerated. Referenced, not duplicated, per `ucda-decisions.json → external_work_package_sources` and `CEP-002` 8.3. Stage reached: **DECISION REGISTRATION**, the minimum 28.13(c) requires.

---

## GD-17 — Retention of the evidence-ignore policy

| Field | Record |
|---|---|
| **Decision ID** | `GD-17` |
| **Title** | Whether the `00-MASTER/**/evidence/` ignore policy is retained |
| **Resolves** | `DDI-17` |
| **Family** | GDR-E |

### Problem Statement

Output 16 records that *"The policy is deliberate and comment-scoped in `.gitignore`. Changing or keeping it is a choice, not a measurement"*, and that the consequence is that *"prior authorization seals remain unreproducible from committed history"* (`DG-8`, `DR-2`). The owning authority is *"the ignore authority's owner — `REG-AUTO-001` (`CMG-DLG-13`) / repository operator"*.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| `.gitignore` — the pattern `00-MASTER/**/evidence/`, immediately preceded by the scoping comment *"program lane ONLY: the tracked `data/_evidence/` canonical certification artifacts (`UCOS-DATA-*`) are a distinct, registered family and are deliberately NOT matched here"* | The policy is deliberate, narrowly scoped, and expressly protects the registered evidence family from being caught by it | `.gitignore` line 72 (pattern) with the comment above it |
| `DG-8` verbatim: *"60 programme evidence files are excluded from version control by the ignore authority, including the nine seal inputs of the `UCCEP-000006` authorization"*; measured state *"evidence exists on disk, not in history"*; owning authority *"the ignore authority's owner — `REG-AUTO-001` / repository operator"* | The measured scope and consequence | `00-MASTER/UCCEP-000007/13-KNOWN-GAPS.md` §2 |
| `DR-2` verbatim: *"60 evidence files backing prior programmes' seals — including the nine inputs to authorization seal `f497410c…` — are outside version control, so those seals cannot be reproduced from committed history alone"* | The risk-adjacent condition, recorded as a condition not a risk | `00-MASTER/UCCEP-000007/14-KNOWN-RISKS.md` §3 |
| `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md`, with `00-BOOK/tools/config.py :: EXCLUDE_DIR_PREFIXES` | `00-MASTER/` is excluded from corpus registration by a located determination — evidence under it holds no registered identity | those files |
| `REG-AUTO-001` P1 — *"Creation is registration."* An artifact is not created until all seven registers reflect it; *"Physical existence alone is a draft on disk"*; L1 — creation without registration is prohibited and must be blocked | Committing unregistered files into history would create drafts on disk with no registered identity, against the registration discipline | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md` |
| Output 7 §5 — regeneration is **idempotent**, digests byte-identical, tree CLEAN; both master engines PASS `--check-determinism`, `--check-write-scope`, `--check-no-enumeration` | Seals are reproducible by **re-derivation** even where their inputs are not committed | `00-MASTER/UCCEP-000007/07-GENERATED-ARTIFACT-INVENTORY.md` |
| `CEP-001` XX (proven determinism / reproducibility), imported as a freeze precondition by `CEP-007` V.1 | Reproducibility is an owned standard, and determinism is the located means of satisfying it | `00-CEP/CEP-001-…md`; `00-CEP/CEP-007-…md` |
| `UCCEP-000006` §9 — the reproduction instruction for the authorization seal | The seal's reproduction route is declared by its own owner | `00-MASTER/UCCEP-000006/` |

### Constitutional Authority

**`REG-AUTO-001`** (`CMG-DLG-13` — artifact registration, identity allocation, classification, namespace of registered artifacts) — sole canonical owner for this decision, as the instrument that owns what is in and out of registration scope. `CEP-001` XX is cited for the reproducibility standard the decision must satisfy; the repository operator is the executing custodian of `.gitignore`, acting within that owner's scope.

### Decision

**RETAINED. The `00-MASTER/**/evidence/` ignore policy stands, unchanged.**

1. **The policy is retained** in its current, comment-scoped form. Programme evidence under `00-MASTER/**/evidence/` remains outside version control.
2. **Its basis is registration scope, not convenience.** `00-MASTER/` is excluded from corpus registration by the located exclusion determination. Committing its evidence would place files in history that hold no registered identity — drafts on disk under `REG-AUTO-001` P1, with no status authority — while enlarging history with material the registers do not know about.
3. **The registered evidence family is unaffected.** The `.gitignore` comment expressly excludes `data/_evidence/` `UCOS-DATA-*` from this pattern, and that remains so. This decision does not touch tracked, registered evidence.
4. **Seal reproducibility is satisfied by deterministic regeneration, not by committed inputs.** The located property is that regeneration is idempotent with byte-identical digests, and that the engines pass `--check-determinism`, `--check-write-scope` and `--check-no-enumeration`. A seal whose inputs are re-derivable by a deterministic generator at a known HEAD is reproducible within the meaning of `CEP-001` XX; it is *not* reproducible from committed history **alone**, which is exactly what `DR-2` records.
5. **`DG-8` and `DR-2` are NOT closed by this decision.** They remain recorded as a gap and a condition. Retention is a determination about the policy, not a repair of the consequence, and this decision does not represent otherwise.
6. **Forward obligation:** any **new** seal whose inputs fall under the ignore pattern SHALL declare, in the artifact that carries the seal, the exact regeneration command by which it is reproducible. Without that, clause 4's reproducibility argument does not hold for that seal.

### Rationale

The choice is between two imperfect states, and Repository Truth favours retention.

**Committing the evidence** would import 60 unregistered files into history. `REG-AUTO-001` P1/L1 make registration the definition of creation and require unregistered creation to be **blocked**; committing files that the seven registers do not reflect works against that discipline, and doing so under `00-MASTER/`, which a located determination has deliberately excluded from registration, would contradict that determination without amending it. It would also permanently enlarge history with material whose retention no register governs — which, under the append-only policy of `GD-13`, is irreversible.

**Retaining the policy** leaves a real deficiency: `DR-2`'s finding that prior seals cannot be reproduced from committed history alone. The mitigating fact is located and strong: regeneration is deterministic and byte-identical, and the engines self-check determinism, write scope and non-enumeration. So the seals are reproducible *by re-running the generators at the recorded HEAD*, which is a weaker guarantee than committed inputs (it depends on the generator, its environment and the HEAD being available) but is the guarantee `CEP-001` XX is framed around.

Clause 5 is included deliberately. It would be easy — and wrong — to present clause 4 as closing `DG-8`/`DR-2`. It does not. The gap concerns reproducibility *from committed history*, and retention leaves that gap exactly where its owner recorded it. Clause 6 is the one forward-looking obligation, and it addresses the sharpest edge of the deficiency: an undocumented seal over ignored inputs is unreproducible by any route at all.

This is a decided matter rather than a held one because the ignore authority's owner is located and single (`CMG-DLG-13` → `REG-AUTO-001`), so `CMG-000001` LVII.3's undecidability condition is not met.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-03` | Deterministic regeneration under the fixed generator map is what makes clause 4 true |
| Depends on | `GD-13` | Append-only history is why an irreversible enlargement of history is a real cost |
| Depends on | `GD-11` | Registration scope discipline — an artifact outside scope claims no registered identity |
| Related to | `GD-20` | Both concern durability of evidence off this machine, from different angles: history content vs. history location |
| Leaves open | `DG-8`, `DR-2` | Carried to `10-REMAINING-GOVERNANCE-GAPS.md` |

### Affected Programmes

All programmes with an `evidence/` directory under `00-MASTER/` — their evidence remains on disk and out of history. `UCCEP-000006`'s nine seal inputs remain uncommitted, as `DG-8` records. `UCCEP-000008`'s own evidence, if any is later produced, falls under the same policy and clause 6.

### Affected Registries

None mutated. No register gains or loses an entry; the registered `UCOS-DATA-*` evidence family is untouched.

### Affected Constitutions

None amended. `REG-AUTO-001` P1/L1, `CEP-001` XX cited; `CEP-007` V.1 cited for the reproducibility precondition it imports.

### Affected Implementations

**None.** `.gitignore` is **not modified** — retention requires no edit. `config.py` is read as evidence only.

### Constraints

| Id | Constraint |
|---|---|
| `GD-17-C1` | The `00-MASTER/**/evidence/` pattern and its scoping comment SHALL NOT be changed by a consolidation act. |
| `GD-17-C2` | The `data/_evidence/` `UCOS-DATA-*` registered family SHALL remain outside this pattern. |
| `GD-17-C3` | Any new seal over ignored inputs SHALL declare its regeneration command in the artifact carrying the seal. |
| `GD-17-C4` | This decision SHALL NOT be cited as closing `DG-8` or `DR-2`. |
| `GD-17-C5` | No consolidation act SHALL commit files from `00-MASTER/**/evidence/`, which would both breach clause 1 and import unregistered artifacts (`REG-AUTO-001` P1). |

### Acceptance Criteria

1. `.gitignore`'s `00-MASTER/**/evidence/` pattern and its preceding comment are byte-identical at any later HEAD.
2. No file under `00-MASTER/**/evidence/` is tracked.
3. The registered `UCOS-DATA-*` evidence family remains tracked and unaffected.
4. Every seal produced by a consolidation artifact over ignored inputs carries its regeneration command.
5. `DG-8` and `DR-2` remain recorded as open, in `10-REMAINING-GOVERNANCE-GAPS.md`.
6. Regeneration remains idempotent with byte-identical digests, and the engines continue to pass `--check-determinism`.

### Traceability

`DDI-17` → `GD-17`. Upstream: Output 16 §3 row DDI-17; `UCCEP-000007/13-KNOWN-GAPS.md` `DG-8`; `14-KNOWN-RISKS.md` `DR-2`; `07-GENERATED-ARTIFACT-INVENTORY.md` §5; `UCCEP-000006` §9. Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-13` → `REG-AUTO-001` P1/L1, with `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` and `config.py :: EXCLUDE_DIR_PREFIXES` as the located scope determination; reproducibility standard `CEP-001` XX. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-17`; gaps carried to `10-REMAINING-GOVERNANCE-GAPS.md`.

### Future Impact

Settles a question that would otherwise recur at every seal: ignored evidence stays ignored, and reproducibility is carried by determinism. Clause 6 raises the floor going forward, so that the *"unreproducible from committed history"* condition does not silently widen as the consolidation produces more seals. The residual gap is preserved as visible rather than argued away, which keeps the choice reviewable if the operator later prefers committed inputs.

### Disposition

**`CEP-002` 28.13(b) — REPRESENTED BY AN EXISTING CANONICAL CAPABILITY.**
Single canonical owner: **`REG-AUTO-001`** (`00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-AUTOMATIC-ARTIFACT-REGISTRATION-STANDARD.md`, P1/L1 and the registration-scope determination it governs). Evidence: `.gitignore` line 72 and its scoping comment; `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md`; `00-BOOK/tools/config.py`; Output 7 §5. No further realization required — retention is the status quo; stage reached is REPOSITORY MAPPING.

---

## GD-18 — Programme lineage: `UCCEP-000001` … `UCCEP-000004`

| Field | Record |
|---|---|
| **Decision ID** | `GD-18` |
| **Title** | Whether `UCCEP-000001` … `000004` are intentionally absent, reserved, or retired |
| **Resolves** | `DDI-18` |
| **Family** | GDR-E |

### Problem Statement

Output 16 records the owning authority as *"`UCCEP-000000` (programme lineage)"* and the reason measurement cannot resolve it as *"Absence is measurable; its meaning is not."*

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| `OBS-2` verbatim: *"`UCCEP-000001` … `UCCEP-000004` have **no directory** in the repository. The chain present is `000000`, `000005`, `000006`, and `000007` (created by this programme). Their absence is recorded; no cause is asserted."* Evidence: `ls 00-MASTER/`, `git ls-files 00-MASTER/`; method M-1 | The measured absence, with no cause asserted by the measuring programme | `00-MASTER/UCCEP-000007/12-DISCOVERY-OBSERVATIONS.md` |
| Output 2 §5 — *"`UCCEP-000001`…`000004` have no directory in the repository at this HEAD (M-1)"* | Corroboration at programme-inventory level | `00-MASTER/UCCEP-000007/02-PROGRAMME-INVENTORY.md` |
| `00-MASTER/` is excluded from corpus registration (`config.py :: EXCLUDE_DIR_PREFIXES`; `UCOS-RECON-C1` exclusion determination), *"so nothing below holds a registered corpus identity"* | No programme directory under `00-MASTER/` has a registered identity — so no identity was ever allocated for `000001`…`000004` | Output 2 §1; `00-BOOK/tools/config.py`; `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` |
| `id-ledger.json` — 1,219 `by_path` entries, `page_cursor` 9,587; no entries for `00-MASTER/` programme directories | The identity ledger contains no allocation for these identifiers | `00-BOOK/DATA/id-ledger.json`; Output 4 §2 |
| `REG-AUTO-001` P4 — *"Universal IDs and Universal Page Numbers are allocated once and never reused, renumbered, or reordered."* | Identity is permanent and forward-only where allocated | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md` |
| `REG-AUTO-001` L5 — repair by re-running and appending, *"never by editing frozen artifacts, renumbering, or rewriting history"* | Back-filling is a form of renumbering the lineage and is barred | same |
| `REG-AUTO-001` §5 / L3 — lifecycle order, no state skipping; a GENERATED artifact not REGISTERED carries *"no status authority and no valid completion claim"* | A directory that never existed conferred nothing and reserved nothing | same |
| Output 2 §4 — the `UCCEP-000000` roster is **16 programmes** (`PROGRAM-000001`…`000016`), a **different** identifier series from the `UCCEP-00000n` directory series | The roster series and the directory series are distinct; absence in one is not absence in the other | `00-MASTER/UCCEP-000007/02-PROGRAMME-INVENTORY.md`; `00-MASTER/UCCEP-000000/uccep.json → programs[]` |

### Constitutional Authority

**`REG-AUTO-001`** (`CMG-DLG-13` — artifact registration, **identity allocation**, classification, namespace of registered artifacts) — sole canonical owner for this decision, as the instrument that owns identity allocation and its permanence. `UCCEP-000000` is the custodian of the programme lineage record (as `DDI-18` notes) but is absent from `CMG-REGISTRY.json`, so under `CMG-L-01` it is **not cited as constitutional authority**; the identity question resolves to `CMG-DLG-13`.

### Decision

**They are NOT ALLOCATED, they are NOT RESERVED, they are NOT RETIRED — and they SHALL NOT be back-filled. Programme numbering under `00-MASTER/` is forward-only.**

1. **No identity was ever allocated.** `00-MASTER/` is outside registration scope, and `id-ledger.json` contains no entry for these identifiers. There is therefore nothing to retire (nothing existed) and nothing to reserve (no reservation mechanism was engaged).
2. **The absence carries no meaning.** It is not a marker, not a placeholder, and not evidence of withdrawn work. `OBS-2` asserts no cause, and none is asserted here beyond the identity facts.
3. **No back-filling.** `UCCEP-000001` … `000004` SHALL NOT be assigned to any future programme. Assigning them would reorder the lineage — the operation `REG-AUTO-001` P4 forbids for allocated identity and L5 forbids as a repair method — and would create the false impression of a chronology that never occurred.
4. **Forward-only allocation.** The next programme identifier continues forward from the highest existing. At HEAD `9de85ad` the highest was `UCCEP-000007`; the next is therefore **`UCCEP-000008`**, which is this programme.
5. **Series are not conflated.** The `UCCEP-00000n` **directory** series and the `PROGRAM-0000nn` **roster** series in `uccep.json → programs[]` (16 entries, 16/16 PASS) are distinct identifier series. A gap in one implies nothing about the other, and this decision governs only the directory series.

### Rationale

The question looks like an archaeology problem and is actually an identity-allocation problem, which is why it resolves cleanly to `CMG-DLG-13` rather than requiring an account of history.

Once the registration facts are established — `00-MASTER/` outside scope, no ledger entries — the three candidate answers collapse. "Retired" presupposes something existed and was withdrawn; nothing was allocated, so there is nothing to have been withdrawn. "Reserved" presupposes a reservation act; no reservation mechanism exists for unregistered directories, and `REG-AUTO-001` §5/L3 make clear that an artifact short of REGISTERED confers nothing. "Intentionally absent" attributes an intention that no located record evidences, and `CEP-002` 28.5 bars supplying it from recollection. The only answer the evidence supports is the negative one: never allocated, no meaning.

The operative clause is 3, and it is the reason the decision matters at all. The tempting move is to treat the gap as free inventory and give the numbers to future programmes. That would be renumbering the lineage: a later programme labelled `UCCEP-000002` would sit, by its identifier, before `000005`, `000006` and `000007` while post-dating all of them. `REG-AUTO-001` P4's prohibition on reordering and L5's prohibition on renumbering-as-repair both cut against it, and the resulting record would mislead every future reader about sequence. Forward-only allocation costs nothing and keeps identifier order and chronological order aligned.

Clause 5 forestalls a specific confusion visible in Repository Truth: `uccep.json` carries a 16-member `PROGRAM-0000nn` roster, and it would be easy to read the missing directories as missing roster members. They are different series; the roster is complete at 16/16.

This decision also supplies the recorded basis for this programme's own identifier, which Output 0 §7 cites — the numbering claim is grounded here rather than assumed.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-13` | Forward-only and no-renumbering are that policy's identity clause |
| Depends on | `GD-11` | Registration-scope discipline: unregistered directories claim nothing |
| Depended on by | `GD-07` | The form decision relies on `UCCEP-000008` being the lawful next identifier |
| Depended on by | Output 0 §7 | Cited as the basis for this programme's identifier |
| Depended on by | every future programme | Fixes how the next identifier is chosen |

### Affected Programmes

`UCCEP-000008` — its identifier is grounded by this decision. Every future `00-MASTER/` programme — bound to forward-only allocation. `UCCEP-000000` — its roster is unaffected and remains 16/16; not edited (**X-9**).

### Affected Registries

None mutated. `id-ledger.json` is read and **not** written (**X-4**): no identity is allocated by this decision, because `00-MASTER/` is outside registration scope.

### Affected Constitutions

None amended. `REG-AUTO-001` P4/L5/L3/§5 cited; `CMG-000001` X.1 cited for the capacity distinction; `CEP-002` 28.5 cited for refusing an unevidenced intention.

### Affected Implementations

None. `config.py` is read as evidence only.

### Constraints

| Id | Constraint |
|---|---|
| `GD-18-C1` | `UCCEP-000001` … `UCCEP-000004` SHALL NOT be assigned to any programme. |
| `GD-18-C2` | Programme identifiers under `00-MASTER/` SHALL be allocated forward-only from the highest existing identifier. |
| `GD-18-C3` | No consolidation artifact SHALL assert a cause, intention, or history for the absence beyond the identity facts recorded here. |
| `GD-18-C4` | The `UCCEP-00000n` directory series and the `PROGRAM-0000nn` roster series SHALL NOT be conflated. |
| `GD-18-C5` | A programme created under `00-MASTER/` SHALL declare that it holds no registered corpus identity (`GD-11-C3`). |

### Acceptance Criteria

1. No directory named `00-MASTER/UCCEP-000001` … `000004` is created at any later HEAD.
2. The next programme directory after `UCCEP-000008` is `UCCEP-000009` or higher; no identifier is reused or back-filled.
3. `id-ledger.json` gains no entry for any `00-MASTER/` programme directory.
4. No artifact asserts a cause for the absence.
5. `uccep.json → programs[]` remains a 16-member roster, unconflated with the directory series.

### Traceability

`DDI-18` → `GD-18`. Upstream: Output 16 §3 row DDI-18; `UCCEP-000007/12-DISCOVERY-OBSERVATIONS.md` `OBS-2`; `02-PROGRAMME-INVENTORY.md` §1/§4/§5; `04-REGISTRY-INVENTORY.md` §2 (`id-ledger.json`). Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-13` → `REG-AUTO-001` P4/L5/§5; scope determination `UCOS-RECON-C1` + `config.py`. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-18`; grounds Output 0 §7 and `GD-07`.

### Future Impact

Closes a small question with a long tail: identifier order stays aligned with chronological order permanently, and no future reader is misled by a back-filled programme. It also removes a standing invitation to speculate about missing work, by recording that the absence has no evidenced meaning and that asserting one is barred.

### Disposition

**`CEP-002` 28.13(b) — REPRESENTED BY AN EXISTING CANONICAL CAPABILITY.**
Single canonical owner: **`REG-AUTO-001`** (`00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-AUTOMATIC-ARTIFACT-REGISTRATION-STANDARD.md`, P4 identity permanence and L5 forward-only correction). Evidence: `OBS-2`; Output 2 §1/§5; `00-BOOK/DATA/id-ledger.json`; `00-BOOK/tools/config.py`; `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md`. No further realization required; stage reached is REPOSITORY MAPPING.

---

## GD-19 — Realization of registers 8–11

| Field | Record |
|---|---|
| **Decision ID** | `GD-19` |
| **Title** | Whether registers 8–11 of the eleven-register set are to be realized |
| **Resolves** | `DDI-19` |
| **Family** | GDR-E |

### Problem Statement

Output 16 records the owning authority as `UCI-001` (`CMG-DLG-15` — change intelligence, regeneration and synchronization) and the reason measurement cannot resolve it as: *"`GOV-INT-001` §11 records them 'READY TO ADD'; readiness is not a decision to add."*

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| Output 4 §4 — the eleven-register set: registers **1–7 exist**; registers **8 `changes.json`, 9 `knowledge.json`, 10 `regeneration.json`, 11 `rollback.json` do NOT exist at this HEAD**; *"`GOV-INT-001` §11 records their state as 'READY TO ADD'"* | The exact absence, and the four named members | `00-MASTER/UCCEP-000007/04-REGISTRY-INVENTORY.md` |
| `OBS-16` verbatim: *"Registers 8–11 of the eleven-register set declared by `GOV-INT-001` §6.2 — `changes.json`, `knowledge.json`, `regeneration.json`, `rollback.json` — are **absent** from `00-BOOK/DATA/`. Registers 1–7 are present."* Constitutional ref: `GOV-INT-001` §6.2, §11 | Corroboration with its constitutional reference | `00-MASTER/UCCEP-000007/12-DISCOVERY-OBSERVATIONS.md` |
| `DG-1` verbatim: *"Four of the eleven declared registers do not exist: `changes.json`, `knowledge.json`, `regeneration.json`, `rollback.json`"* · declared by `GOV-INT-001` §6.2 (state "READY TO ADD" at §11) · owning authority **`UCI-001` (`CMG-DLG-15`)** | The gap and its named owner | `00-MASTER/UCCEP-000007/13-KNOWN-GAPS.md` §2 |
| `GOV-INT-001` §6.2 — eleven registers **in one store**, seven owned by `REG-AUTO-001` and four by `UCI-001` | The four are **declared members of an existing set in an existing store**, not new registries | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` |
| `GOV-INT-001` SECTION 11 — *"Registers 8–11 (change/knowledge/regen/rollback) · **READY TO ADD** · additive schemas + config declaration pending"*; *"Execution engines · **READY** — no new engine required; append-only extension to `T`"* | The realization shape, declared by the architecture owner: schemas + declaration, no new engine | same |
| `GOV-INT-001` §7.2 steps 3–4 — *"**Additive schemas** — `change/knowledge/regeneration/rollback.schema.json`"*; *"**`config.py` family declarations** + **`register.sh` Phase 0 / rollback path** (append-only)"* | The located, numbered realization steps | same |
| `GOV-INT-001` §7.2 step 2 and SECTION 11 overall — *"IMPLEMENTATION GATED on authoring `UCI-001`"* per GI-RULE-0 | A named prerequisite ordering: the standard precedes the registers | same |
| `REG-AUTO-001` L4 — a genuinely new family must be declared in `config.py` *"before or with"* its first artifact, append-only (§11, §12) | The registration-side obligation of realization | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md` |
| Output 4 §2 — `change-ledger.json` `change_events` **empty** at HEAD while certification scope records 1,358 change events | Corroborating evidence that change intelligence is declared but not yet carried by a register | `00-MASTER/UCCEP-000007/04-REGISTRY-INVENTORY.md` |
| `CMG-REGISTRY.json` — `UCI-001` recognized: `CMG-K-10`, DERIVED, T3, PROVISIONAL, v1.0, superiors `["REG-AUTO-001"]`; concern `CMG-DLG-15` | The owner is recognized, so it **is** citable (contrast `UCIC-001` at `GD-15`) | `00-CMG/CMG-REGISTRY.json` |

### Constitutional Authority

**`UCI-001`** (`CMG-DLG-15` — change intelligence, regeneration and synchronization) — sole canonical owner for this decision and owner of registers 8–11 per `GOV-INT-001` §6.2. `GOV-INT-001` (`CMG-DLG-16`) §6.2 / §7.2 / SECTION 11 supplies the declared realization shape; `REG-AUTO-001` L4 / §11 / §12 supplies the registration-side obligation.

### Decision

**They SHALL be realized — and not by this programme.**

1. **Determination on the merits:** registers 8–11 are **declared members** of the eleven-register set (`GOV-INT-001` §6.2) and their absence is a recorded gap (`DG-1`, `OBS-16`). The set is completed, not extended. Realization is therefore required, and `DG-1` is closable only by realizing them.
2. **This is completion, not proliferation.** Realizing them does **not** breach `GD-12` (no new registries): `GD-12` clause 2 records precisely this, that registers 8–11 are declared members of an existing closed set in an existing store. They are added **to `00-BOOK/DATA/`**, not to a new store.
3. **Realization shape is the located one, and introduces no engine.** Per `GOV-INT-001` SECTION 11 and §7.2 steps 3–4: **additive schemas** (`change/knowledge/regeneration/rollback.schema.json`), a **`config.py` family declaration** (`REG-AUTO-001` L4, append-only), and an **append-only Phase 0 / rollback path** in `register.sh` — with *"no new engine required"*. This satisfies `GD-04` (no new generators): a schema is data and the writer is the existing toolchain.
4. **Prerequisite acknowledged:** `GOV-INT-001` SECTION 11 records the work as *"IMPLEMENTATION GATED on authoring `UCI-001`"* per GI-RULE-0, and §7.2 places authoring `UCI-001` at step 2, before the schemas at step 3. That ordering is the owner's and is not altered here.
5. **Registered as work package `WP-GDR-001`**, declared in `08-DISPOSITION-ROUTING-TABLE.md` with owner `UCI-001`, constitutional route `GOV-INT-001` §6.2/§7.2 + `REG-AUTO-001` L4/§11/§12, and the acceptance condition below. **No schema, declaration, or register file is created by this programme.**

### Rationale

The distinction Output 16 draws is exact — *"readiness is not a decision to add"* — and the decision to add is warranted on located grounds.

`GOV-INT-001` §6.2 **declares eleven registers**, not seven. Four of the eleven do not exist. That is not a design choice awaiting a decision; it is a declared set that is incomplete, which is why the located owner recorded it as gap `DG-1` and as observation `OBS-16` with a constitutional reference rather than as a closed question. Corroborating evidence points the same way: `change-ledger.json`'s `change_events` array is empty while 1,358 change events are recorded in certification scope, so change intelligence currently has no register carrying it.

The reason this decision is a **work package** rather than a recognition is that, unlike every member of family GDR-C, the substance is *not* already discharged: four files genuinely do not exist. `CEP-002` 28.13(b) requires that *"no further realization IS required"*, which is false here, so (b) is unavailable and (c) is the correct disposition. (c) in turn requires a located package with an owner, a route and an acceptance condition — supplied at `WP-GDR-001`.

Clause 2 exists because a naive reading of `GD-12` would bar this work permanently and freeze `DG-1` open forever. That reading is wrong on the located text: `CMG-L-14` and `CEP-002` 8.3 prohibit a **second** registry *where one exists*; these four are members of the one store `GOV-INT-001` §6.2 declares. Clause 3 is what keeps the work inside `GD-04`: the realization shape the architecture owner declared is schemas plus a declaration plus an append-only transaction phase, with *"no new engine required"* — so nothing in this package licenses a new generator.

Clause 4 records the prerequisite without adopting it as this programme's sequence. `GOV-INT-001` gates the work on authoring `UCI-001`; that gate is the owner's and this decision neither waives it (which `CEP-002` 8.5/24.4 would bar) nor re-sequences it (`GD-14`).

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-12` clause 2 | Establishes that completion of the declared set is not proliferation |
| Depends on | `GD-04` | Constrains the realization to schemas + declarations, no new engine |
| Depends on | `GD-03` | The new registers attach to an existing generator under the fixed map |
| Depends on | `GD-11` | Any created artifact must satisfy the admission discipline |
| Gated by | `GOV-INT-001` SECTION 11 / §7.2 step 2 | Authoring `UCI-001` precedes the schemas — the owner's ordering, unaltered |
| Closes when discharged | `DG-1`, `OBS-16` | Carried to `10-REMAINING-GOVERNANCE-GAPS.md` until then |

### Affected Programmes

None mutated. The work is `UCI-001`'s, executed through the located toolchain. No `00-MASTER/` programme is edited.

### Affected Registries

**None mutated by this programme.** When `WP-GDR-001` is discharged, `00-BOOK/DATA/` gains `changes.json`, `knowledge.json`, `regeneration.json`, `rollback.json` — as members of the declared eleven-register set, appended under **X-5**. Registers 1–7 are unaffected.

### Affected Constitutions

None amended. `GOV-INT-001` §6.2 / §7.2 / SECTION 11 and `REG-AUTO-001` L4 / §11 / §12 cited. `UCI-001` is cited as owner; it is not edited by this decision, and its authoring remains its own act.

### Affected Implementations

**None by this programme.** The eventual realization touches `00-BOOK/` schemas, `config.py` and `register.sh` — all append-only, all by their own owners, none here.

### Constraints

| Id | Constraint |
|---|---|
| `GD-19-C1` | Realization SHALL be to the existing `00-BOOK/DATA/` store; no new store SHALL be created (`GD-12-C4`). |
| `GD-19-C2` | Realization SHALL introduce **no new engine, generator, pipeline, scheduler or daemon** (`GD-04-C1`); the writer is the existing toolchain via an append-only phase of `T`. |
| `GD-19-C3` | The `config.py` family declaration SHALL be append-only (`REG-AUTO-001` L4, §11, §12). |
| `GD-19-C4` | This programme SHALL NOT create the schemas, the declaration, or the register files. |
| `GD-19-C5` | The `GOV-INT-001` SECTION 11 / §7.2 gating on authoring `UCI-001` SHALL NOT be waived, bypassed, or re-sequenced by a consolidation act. |
| `GD-19-C6` | `WP-GDR-001` is a package of this programme's own register and is **not** an addition to `WP-UCCEP-001…005` (closed by **K-07**) or to `WP-UCDA-001…007`. |

### Acceptance Criteria

Acceptance of the **disposition** (met by this decision):

1. The matter is disposed to a located work package with owner, constitutional route and acceptance condition — `WP-GDR-001`.
2. No schema, declaration or register file is created by this programme.

Acceptance of the **work** (for `UCI-001`, when it discharges `WP-GDR-001`):

3. `00-BOOK/DATA/changes.json`, `knowledge.json`, `regeneration.json`, `rollback.json` exist.
4. `change/knowledge/regeneration/rollback.schema.json` exist as additive schemas.
5. The four families are declared in `config.py`, append-only.
6. `register.sh` carries the Phase 0 / rollback path append-only, with **no new engine** added to `00-BOOK/tools/`.
7. `ukb validate` passes; register drift is **0**; regeneration remains byte-identical.
8. `DG-1` and `OBS-16` are closable.

### Traceability

`DDI-19` → `GD-19` → `WP-GDR-001`. Upstream: Output 16 §3 row DDI-19; `UCCEP-000007/04-REGISTRY-INVENTORY.md` §2/§4; `12-DISCOVERY-OBSERVATIONS.md` `OBS-16`; `13-KNOWN-GAPS.md` `DG-1`. Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-15` → `UCI-001`, with the realization shape from `CMG-DLG-16` → `GOV-INT-001` §6.2/§7.2/SECTION 11 and the registration obligation from `CMG-DLG-13` → `REG-AUTO-001` L4/§11/§12. Onward: `08-DISPOSITION-ROUTING-TABLE.md` rows `GD-19` and `WP-GDR-001`; gaps carried to `10-REMAINING-GOVERNANCE-GAPS.md`.

### Future Impact

Converts the corpus's largest declared-but-unbuilt capability from an indefinite *"READY TO ADD"* into owned work with a testable acceptance condition. Because clauses 2 and 3 bind the realization shape in advance, the work cannot arrive as a new engine or a new store later — the two ways this particular gap would most plausibly have been closed unlawfully. Registers 10 and 11 in particular (`regeneration.json`, `rollback.json`) are what would make the rollback architecture of `GOV-INT-001` §2.12 and SECTION 8 Phase 7 a register-backed capability rather than a procedure.

### Disposition

**`CEP-002` 28.13(c) — REGISTERED AS AN IMPLEMENTATION WORK PACKAGE.**
Work package: **`WP-GDR-001`** — declared in `08-DISPOSITION-ROUTING-TABLE.md`. Owner: **`UCI-001`** (`00-BOOK/CONTROL-TOWER/UCOS-Ω∞-UCI-001-UNIVERSAL-CHANGE-INTELLIGENCE-AND-REGENERATION-STANDARD.md`, `CMG-DLG-15`). Constitutional route: `GOV-INT-001` §6.2 / §7.2 steps 3–4 / SECTION 11, with `REG-AUTO-001` L4 / §11 / §12. Acceptance condition: criteria 3–8 above. Stage reached: **DECISION REGISTRATION**, the minimum 28.13(c) requires.

---

## GD-20 — Off-machine existence of the OA-1 baseline

| Field | Record |
|---|---|
| **Decision ID** | `GD-20` |
| **Title** | Whether the OA-1 baseline is pushed to `origin`, giving the anchor existence off this machine |
| **Resolves** | `DDI-20` |
| **Family** | GDR-E |

### Problem Statement

Output 16 records the owning authority as *"repository operator"* and the reason measurement cannot resolve it as *"No upstream is configured; whether to configure one is an operator act."*

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| `OBS-12` verbatim: *"The branch `programme/evo-usis-005` has **no upstream configured**, so ahead/behind is not computable and nothing in the OA-1 baseline has been pushed. The repository's own operational memory previously recorded `0/0 (synced)` against `origin/governance-reconciliation`, a different branch."* Evidence: `git rev-parse --abbrev-ref @{u}` → *no upstream*; method M-1 | The measured absence of an upstream, and that a different branch was previously synced | `00-MASTER/UCCEP-000007/12-DISCOVERY-OBSERVATIONS.md` |
| `DR-1` verbatim: *"The baseline exists only locally: branch `programme/evo-usis-005` has no upstream, so the anchor commit has not been pushed and does not exist off this machine"* — recorded as a **condition**, not classified as a risk (*"this programme has no authority to assign severity"*) | The consequence, recorded by its owner without severity | `00-MASTER/UCCEP-000007/14-KNOWN-RISKS.md` §3 |
| The rollback anchor `1c6e750e53efdbcba5fc501d58fc99781b03a966` (OA-1) is an **ancestor of HEAD**; tracked files 4,499; commits 183 | The anchor is real and reachable — locally | `00-MASTER/UCCEP-000007/00-DISCOVERY-INDEX.md` §4 |
| **OA-1** — *"Atomic registration commit + `MCP-002` reconciliation"* · owner **repository operator** · discharges O-01 · `UCCEP-F-007` · `WP-UCCEP-005` · **C-1** · P0 · suspensive **YES** | The precedent that baseline-durability acts are the operator's, with a located register form | `00-MASTER/UCCEP-000006/07-OPERATOR-ACTION-REGISTER.md` §1 row 1 |
| `R-02` — *"**discharged** — OA-1 committed at `1c6e750`; `CK-REG-DRIFT` PASS, `G-07` PASS, tree CLEAN"* | OA-1's commit half is discharged; only its off-machine existence is not | `00-MASTER/UCCEP-000007/14-KNOWN-RISKS.md` §1 |
| `CEP-001` XX — proven determinism / reproducibility; `CEP-008` (`CMG-DLG-08`) — evidence and traceability operation | The standards a durable baseline serves | `00-CEP/CEP-001-…md`; `00-CEP/CEP-008-…md` |
| `GOV-INT-001` §2.12 — Rollback Architecture; SECTION 8 Phase 7 — the rollback path appends `rollback.json` and re-runs `T` | Rollback is an architectural capability that presupposes the anchor is reachable | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` |
| `GD-17` clause 4 — seal reproducibility depends on re-running generators **at a known HEAD** | If the HEAD exists only on one machine, that reproducibility route is single-homed too | `05-GDR-E-…md` (this output) |

### Constitutional Authority

**The repository operator**, as `DDI-20` records and as **OA-1** demonstrates for the analogous act. This is an **operational custody** matter, not a constitutional concern: no located instrument owns remote configuration, and none is cited as authority for it. The constitutional interest engaged is `CEP-001` XX (reproducibility) and `CEP-008` (`CMG-DLG-08` — evidence and traceability operation), which the durability of the baseline serves.

### Decision

**The anchor SHALL be given existence off this machine — and the act is the repository operator's, performed under the operator's own authorization.**

1. **Determination on the merits:** a rollback anchor that exists on exactly one machine is a single point of failure for every recovery, reproducibility and traceability claim that depends on it. `GD-13` clause 4 makes the anchor the consolidation's recovery mechanism; `GD-17` clause 4 makes re-derivation at a known HEAD the seal-reproducibility route; `GOV-INT-001` §2.12 / SECTION 8 Phase 7 make rollback an architectural capability. All three presuppose the anchor is reachable.
2. **The act is the operator's.** Configuring a remote and pushing is not an in-repository governance act, and no located instrument can perform or authorize it. This programme performs nothing and authorizes nothing.
3. **Registered as work package `WP-GDR-002`**, declared in `08-DISPOSITION-ROUTING-TABLE.md` with owner *repository operator*, constitutional route `CEP-001` XX + `CEP-008` (`CMG-DLG-08`) + `GOV-INT-001` §2.12, and the acceptance condition below.
4. **Explicit scope limits, because this is a network-affecting act.** The package is limited to giving the **existing** anchor commit off-machine existence. It does **not** authorize force-pushing, branch deletion, history rewriting, pushing to `main`/`master`, or any destructive remote operation — each of which `GD-13-C3` independently forbids. Choice of remote, visibility, and access controls are the operator's, and this decision expresses no view on them.
5. **`DR-1` and `OBS-12` are not closed by this decision.** They remain recorded until the package is discharged.

### Rationale

This is the one matter in the register whose subject lies outside the repository entirely, and the disposition reflects that precisely: the merits are determinable from located standards, the act is not performable by any instrument.

The merits are straightforward once the dependency chain is traced. Three separate located capabilities rest on the anchor being reachable — rollback (`GOV-INT-001` §2.12, SECTION 8 Phase 7), reproducibility (`CEP-001` XX, which `CEP-007` V.1 imports as a freeze precondition), and evidence traceability (`CEP-008`). `DR-1` records that the anchor *"does not exist off this machine"*. A recovery point that cannot survive the loss of the machine it recovers is not a recovery point.

`OA-1` supplies the precedent for the disposition's shape: the analogous act — making the atomic registration commit — was likewise the operator's, was registered with an owner and an acceptance condition, and was discharged as such (`R-02`). Following that form uses a located pattern rather than inventing one. It also explains why this is **(c)** and not **(b)**: the substance is not discharged, so 28.13(b)'s *"no further realization IS required"* is false.

Clause 4 is deliberately narrow. A general "push the baseline" instruction could be read to license remote operations with real blast radius. The package is confined to giving an existing commit off-machine existence; every destructive variant is excluded, and remote selection and access control are left where they belong, with the operator. This programme has no authority over network endpoints and asserts none.

Clause 5 keeps the record honest: registering work does not close the gap, and `DR-1`/`OBS-12` stay open until discharge.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-13` clause 4 | The anchor is the recovery mechanism, which is why its durability matters |
| Related to | `GD-17` | Both concern evidence durability: `GD-17` what history contains, `GD-20` where history lives |
| Supports | `GD-19` | Registers 10–11 (`regeneration.json`, `rollback.json`) make rollback register-backed; a reachable anchor makes it real |
| Blocked by | operator custody | No instrument can perform the act |
| Closes when discharged | `DR-1`, `OBS-12` | Carried to `10-REMAINING-GOVERNANCE-GAPS.md` until then |

### Affected Programmes

None. No programme's outputs are affected; the subject is repository custody.

### Affected Registries

None mutated. No register records remote configuration.

### Affected Constitutions

None amended. `CEP-001` XX, `CEP-008` (`CMG-DLG-08`), `GOV-INT-001` §2.12 cited as the standards served.

### Affected Implementations

**None.** No git configuration is changed and no remote operation is performed by this programme.

### Constraints

| Id | Constraint |
|---|---|
| `GD-20-C1` | The package is limited to giving the existing anchor commit off-machine existence. |
| `GD-20-C2` | No force-push, branch deletion, history rewrite, or other destructive remote operation is authorized (`GD-13-C3`). |
| `GD-20-C3` | No push to `main` or `master` is authorized by this package. |
| `GD-20-C4` | Remote selection, repository visibility, and access controls are the operator's determinations; this decision expresses none. |
| `GD-20-C5` | This programme SHALL NOT modify git configuration or perform any remote operation. |
| `GD-20-C6` | `WP-GDR-002` is a package of this programme's own register and is **not** an addition to `WP-UCCEP-001…005` (**K-07**) or to the `OA-n` register. |

### Acceptance Criteria

Acceptance of the **disposition** (met by this decision):

1. The matter is disposed to a located work package with owner, constitutional route and acceptance condition — `WP-GDR-002`.
2. No git configuration change and no remote operation is performed by this programme.

Acceptance of the **work** (for the repository operator, when discharging `WP-GDR-002`):

3. The working branch has an upstream configured, so `git rev-parse --abbrev-ref @{u}` resolves and ahead/behind is computable.
4. The anchor commit `1c6e750e53efdbcba5fc501d58fc99781b03a966` is present on the remote and reachable from a remote ref.
5. No history was rewritten and no branch was deleted in the process.
6. `DR-1` and `OBS-12` are closable.

### Traceability

`DDI-20` → `GD-20` → `WP-GDR-002`. Upstream: Output 16 §3 row DDI-20; `UCCEP-000007/12-DISCOVERY-OBSERVATIONS.md` `OBS-12`; `14-KNOWN-RISKS.md` `DR-1` and `R-02`; `00-DISCOVERY-INDEX.md` §4 (baseline integrity). Precedent form: `UCCEP-000006/07-OPERATOR-ACTION-REGISTER.md` §1 row 1 (**OA-1**). Standards served: `CEP-001` XX, `CEP-008` (`CMG-DLG-08`), `GOV-INT-001` §2.12. Onward: `08-DISPOSITION-ROUTING-TABLE.md` rows `GD-20` and `WP-GDR-002`; gaps carried to `10-REMAINING-GOVERNANCE-GAPS.md`.

### Future Impact

Makes the consolidation's recovery story survive the loss of a single machine — the precondition for treating the anchor as a real rollback point rather than a local convenience. It also records, for later missions, that operator-custody matters are dispositioned as narrowly-scoped work packages with destructive variants expressly excluded, rather than as broad instructions.

### Disposition

**`CEP-002` 28.13(c) — REGISTERED AS AN IMPLEMENTATION WORK PACKAGE.**
Work package: **`WP-GDR-002`** — declared in `08-DISPOSITION-ROUTING-TABLE.md`. Owner: **repository operator**. Constitutional route: `CEP-001` XX (reproducibility), `CEP-008` (`CMG-DLG-08`, evidence and traceability operation), `GOV-INT-001` §2.12 (rollback architecture); precedent form **OA-1**. Acceptance condition: criteria 3–6 above, subject to constraints `GD-20-C1` … `C4`. Stage reached: **DECISION REGISTRATION**, the minimum 28.13(c) requires.

---

## Family summary — GDR-E

| GD | DDI | Decision in one line | Disposition | Work package | Owner of the work |
|---|---|---|---|---|---|
| `GD-16` | DDI-16 | `UCCEP-F-003`'s record **shall** be corrected; the act is reserved to `UCCEP-000000` by **X-9** | (c) | **`OA-2`** (located) | `UCCEP-000000` / `engine/graph` |
| `GD-17` | DDI-17 | The `00-MASTER/**/evidence/` ignore policy is **retained**; reproducibility rests on deterministic regeneration | (b) | — | — |
| `GD-18` | DDI-18 | `UCCEP-000001`…`000004` were never allocated, mean nothing, and **shall not be back-filled**; numbering is forward-only | (b) | — | — |
| `GD-19` | DDI-19 | Registers 8–11 **shall be realized** as schemas + declaration + append-only phase, with no new engine | (c) | **`WP-GDR-001`** | `UCI-001` |
| `GD-20` | DDI-20 | The anchor **shall** gain off-machine existence; the act is the operator's, narrowly scoped | (c) | **`WP-GDR-002`** | repository operator |

**Family properties:** 5 decisions · 2 recognitions + 3 registrations of work · **zero** rejections · **zero** repository mutations outside `00-MASTER/UCCEP-000008/` · zero constitutions amended · zero registries touched · zero code changed · zero remote operations · zero cross-programme edits.

**Work-package discipline.** Three packages are dispositioned and **none is executed**. One (`OA-2`) is a **reference to a located package** under the `external_work_package_sources` mechanism, avoiding duplication per `CEP-002` 8.3; two (`WP-GDR-001`, `WP-GDR-002`) are declared in this programme's own register with a prefix distinct from `WP-UCCEP-*` (closed by **K-07**), `WP-UCDA-*` and `OA-n`. Each carries the three elements `CEP-002` 28.13(c) requires — owner, constitutional route, acceptance condition — so none is void for want of a located package.

**Gaps deliberately left open.** `GD-17` does not close `DG-8`/`DR-2`; `GD-19` does not close `DG-1`/`OBS-16`; `GD-20` does not close `DR-1`/`OBS-12`; `GD-16` does not close `DG-2`. Registering work is not discharging it, and each is carried forward to `10-REMAINING-GOVERNANCE-GAPS.md`.

---

*`UCCEP-000008` Output 5, family GDR-E. Two recognitions and three registrations of work, rendered within the located law of `REG-AUTO-001` (`CMG-DLG-13`), `UCI-001` (`CMG-DLG-15`) and `GOV-INT-001` (`CMG-DLG-16`). No work performed, no register written, no code changed, no remote touched, no cross-programme edit made. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12`.*

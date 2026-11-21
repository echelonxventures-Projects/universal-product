# Output 8 — Disposition Routing Table

> **STATUS DOMAIN:** GOVERNANCE (determination) · **STATUS BASIS:** the registration and indexing obligations of `CEP-002` Article 28 (28.3, 28.6, 28.13), routed against the located registers reproduced at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000008` · OUTPUT 8 |
| OUTPUT | 8 — Disposition Routing Table |
| SUBJECT | Where each of the 19 resolved decisions must be registered, by whom, and in what shape; and the two work packages this programme declares. |
| AUTHORITY | None of its own. This output performs **no** registration; it records the obligation and its route. |
| BINDING RULE | `CEP-002` **28.3** — a second decision register is PROHIBITED. **28.6** — *"Registration SHALL be made in the located register competent for the decision's class under 11.1, and SHALL thereafter be indexed in operational memory. Registration SHALL precede indexing; indexing SHALL NOT substitute for registration."* |
| WHAT IS NOT DONE HERE | No located register is edited. No overlay entry is written. No engine is run. No seal is recomputed. No identity is allocated. The mechanical Implementation Evidence Gate is untouched — verified in `09-TRACEABILITY-VERIFICATION.md` §5. |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12` (condition **C-3**, constraint **K-09**). |

---

## 1. The located registers, and why routing is necessary

`CEP-002` 28.3 names the located decision registers and forbids a sixth. `UCDA-000001` adds the machine-readable **disposition overlay** those registers lack, declaring of itself that it is *"NOT a decision register in its own right. Every entry carries a `source_register` that is the LOCATED authoritative register of that decision … No decision originates here. Zero Parallel Authority."*

| # | Located register (per `CEP-002` 28.3) | Path | Competent for |
|---|---|---|---|
| 1 | Constitutional Decision Register | `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-DECISION-REGISTER.md` | constitutional-class decisions |
| 2 | Architectural Decision Assimilation Matrix | `/03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` | architectural/governance determinations, with integration method (REUSE/EXTEND/MERGE/REFERENCE/NEW) |
| 3 | Architectural decision record set | `adr/` | architectural decision records |
| 4 | Canonical decision store of the knowledge authority | `knowledge/decisions.json` | knowledge-indexed decisions |
| 5 | Append-only decision index of operational memory | `00-MASTER/MCP-004-MASTER-DECISIONS.md` (governed by `MCS-000`) | the operational-memory **index** required by 28.6 |
| — | Disposition overlay (not a register) | `00-MASTER/UCDA-000001/ucda-decisions.json` | the 28.13 disposition + evidence obligation over registers 1–5 |

**Why this output exists.** `GD-07` determined that this programme records determinations; it did **not** determine that this programme registers them. Registration is a distinct act under 28.6, in a register this programme does not own, consumed by an engine this programme may not run (**X-9**, and the mission's own prohibition on runtime modification). This output therefore records the routing obligation so that it cannot be lost, and leaves the act to the register's owner.

---

## 2. Routing table — the 19 resolved decisions

Class per `CEP-002` 11.1: all 19 are **governance determinations** about the consolidation's architecture and policy, not constitutional substance. Their competent located register is therefore **register 2**, the Architectural Decision Assimilation Matrix, whose recorded purpose is *"integration method per decision"* — and the integration method for 13 of them is literally **REFERENCE**, which that matrix already carries as a method value. Indexing follows in **register 5** per 28.6.

| GD | DDI | Disposition | Canonical owner / basis / package | `source_register` on registration | Integration method |
|---|---|---|---|---|---|
| `GD-01` | 01 | **(b)** REPRESENTED-BY-EXISTING-CANONICAL-CAPABILITY | `GOV-INT-001` §2.15, SECTION 8 | register 2 | REFERENCE |
| `GD-02` | 04 | **(d)** REJECTED-WITH-CONSTITUTIONAL-JUSTIFICATION | basis `CMG-000001` XVII.8, X.1, X.14; `CEP-002` 8.3 | register 2 | REFERENCE |
| `GD-03` | 07 | **(b)** | `REG-AUTO-001` §2/§7/§16 | register 2 | REFERENCE |
| `GD-04` | 11 | **(b)** | `GOV-INT-001` §2.15, SECTION 8, SECTION 11 | register 2 | REFERENCE |
| `GD-05` | 02 | **(b)** | `CMG-000001` Art XV/XX | register 2 | REFERENCE |
| `GD-06` | 03 | **(b)** | `GOV-INT-001` §2.14 | register 2 | REFERENCE |
| `GD-07` | 14 | **(b)** | `GOV-INT-001` (`CMG-DLG-16`) | register 2 | REFERENCE |
| `GD-09` | 05 | **(b)** | `GOV-INT-001` §2.14 | register 2 | REFERENCE |
| `GD-10` | 06 | **(d)** | basis `CEP-007` III.2, IV.1, IV.4, V.1, V.5, I.3, I.5, II.4 | register 2 | REFERENCE |
| `GD-11` | 10 | **(b)** | `CMG-000001` Art LXXVI | register 2 | REFERENCE |
| `GD-12` | 12 | **(b)** | `CEP-002` Art 28.3 | register 2 | REFERENCE |
| `GD-13` | 13 | **(b)** | `CEP-007` Art IX/XI/XIII/XV | register 2 | REFERENCE |
| `GD-14` | 08 | **(d)** | basis `CEP-009` II.4, III.3, IV.6, XII; `CEP-007` XI.2/XI.3; `REG-AUTO-001` P4/L5; `CMG-L-14` | register 2 | REFERENCE |
| `GD-15` | 09 | **(b)** | `CEP-003` (`CMG-DLG-03`) | register 2 | REFERENCE |
| `GD-16` | 16 | **(c)** REGISTERED-AS-IMPLEMENTATION-WORK-PACKAGE | package **`OA-2`** (located, external) | register 2 | REFERENCE |
| `GD-17` | 17 | **(b)** | `REG-AUTO-001` P1/L1 | register 2 | REFERENCE |
| `GD-18` | 18 | **(b)** | `REG-AUTO-001` P4/L5 | register 2 | REFERENCE |
| `GD-19` | 19 | **(c)** | package **`WP-GDR-001`**, owner `UCI-001` | register 2 | REFERENCE |
| `GD-20` | 20 | **(c)** | package **`WP-GDR-002`**, owner repository operator | register 2 | REFERENCE |

**Not routed — held matters:** `GD-08` (DDI-15) and `GD-21` (DDI-21) appear **nowhere** in this table. They carry no `CEP-002` 28.13 disposition, and `GD-08-C4` / `GD-21-C4` forbid registering them. Their records are `DEF-01` and `DEF-02` in `07-DEFERRAL-ENTRIES.md`.

### Disposition census

| Disposition | Count | GDs |
|---|---|---|
| (a) IMPLEMENTED | **0** | — (this programme realizes nothing) |
| (b) REPRESENTED BY AN EXISTING CANONICAL CAPABILITY | **13** | `GD-01`, `03`, `04`, `05`, `06`, `07`, `09`, `11`, `12`, `13`, `15`, `17`, `18` |
| (c) REGISTERED AS AN IMPLEMENTATION WORK PACKAGE | **3** | `GD-16`, `19`, `20` |
| (d) REJECTED WITH CONSTITUTIONAL JUSTIFICATION | **3** | `GD-02`, `10`, `14` |
| (e) SUPERSEDED | **0** | — (this programme displaces nothing) |
| **Total dispositioned** | **19** | |
| Held under Art 27 (no 28.13 disposition) | **2** | `GD-08` → `DEF-01`; `GD-21` → `DEF-02` |
| **Total matters** | **21** | = DDI-01 … DDI-21 |

Every decision carries **exactly one** disposition, as 28.13 requires. None carries more than one, and none carries none — so none is undispositioned under 28.14 on that ground. Evidence resolution is verified in `09-TRACEABILITY-VERIFICATION.md` §3.

---

## 3. Lifecycle stage reached, per `CEP-002` 28.8–28.10

| Disposition | Minimum stage required | Stage reached by these decisions | Basis |
|---|---|---|---|
| (b) | REPOSITORY MAPPING | **REPOSITORY MAPPING** | The canonical owner and its located artefact are identified for each |
| (d) | REPOSITORY MAPPING | **REPOSITORY MAPPING** | The constitutional basis is cited for each; 28.10 permits passage from REPOSITORY MAPPING directly to REPOSITORY TRUTH UPDATE and thence CLOSURE, no realization required |
| (c) | DECISION REGISTRATION | **DECISION REGISTRATION** | Each names a located work package with owner, route and acceptance condition |

**No decision claims a stage it has not reached.** In particular none claims IMPLEMENTATION, VALIDATION, CERTIFICATION, REPOSITORY TRUTH UPDATE or CLOSURE. `CEP-002` 28.10 forbids skipping stages and reaching a stage by descent; recording the *actual* stage is what keeps that true.

**Note on the (c) decisions and 28.6.** Their stage is DECISION REGISTRATION, which 28.6 says occurs when *"the decision is entered in its located register."* That entry is the act §4 below routes and this programme does not perform. Until it is performed, the three (c) decisions are **recorded determinations awaiting registration**, not registered decisions — stated plainly rather than claimed.

---

## 4. The registration act — routed, not performed

For each of the 19, the outstanding act is:

1. **Register** in located register 2 (`/03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md`), with the integration method REFERENCE — `CEP-002` 28.6.
2. **Overlay** the disposition in `00-MASTER/UCDA-000001/ucda-decisions.json`, one entry per decision, each carrying `source_register` = the located register of step 1, plus the disposition-conditional fields that disposition requires (`canonical_owner` for (b); `work_package` for (c); `constitutional_basis` + `justification` for (d)) and `evidence[]` resolving in the repository.
3. **Index** in located register 5 (`00-MASTER/MCP-004-MASTER-DECISIONS.md`, governed by `MCS-000`) — after registration, never instead of it (28.6).

### Who performs it, and why not this programme

| Act | Owner | Why not performed here |
|---|---|---|
| Step 1 — register | the register's owner | `/03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` is a root-level located register, not this programme's artifact; `GD-05-C3` forbids restating located records and `GD-12-C3` forbids this programme acting as a register |
| Step 2 — overlay | `UCDA-000001` | `00-MASTER/UCDA-000001/` is another programme's directory and register. Boundary **X-9**: *"No cross-programme edits."* Writing `ucda-decisions.json` would also require running `ucda_engine.py`, recomputing `ucda.json` and its seal — a runtime modification this mission expressly forbids |
| Step 3 — index | operational memory owner (`MCS-000`) | Same: another owner's artifact, and 28.6 requires registration first |

### Design property: registration will not close the Gate

The routing is constructed so that when steps 1–3 are performed, `undispositioned` remains **0** and the Implementation Evidence Gate remains **OPEN**:

- each of the 19 carries **exactly one** disposition from the closed set (28.13) — no decision has none or more than one;
- each carries **evidence that resolves in the repository at HEAD `9de85ad`**, verified path-by-path in `09-TRACEABILITY-VERIFICATION.md` §3 — so 28.14's third limb is not triggered;
- each (b) names **exactly one** canonical owner — so `CEP-002` 14.3's duplication finding is not triggered;
- each (d) carries a **cited** constitutional basis — so it is a disposition, not a bare rejection (28.13(d));
- each (c) names a **located** work package with owner, route and acceptance condition — so it is not void for want of a package (28.13(c));
- each will carry a `source_register` that resolves — so `register_located` is true and the entry is not `conversation_only` under 28.5;
- the two held matters are **excluded** from registration by `GD-08-C4` / `GD-21-C4`, so they cannot enter the population as undispositioned decisions.

This is a design property of the routing, not a prediction about the engine's behaviour. It is stated as an obligation on whoever performs steps 1–3: **if any decision's evidence ceases to resolve, that decision must not be registered until it does.**

---

## 5. Work packages declared by this programme

Two packages are declared. Each carries the three elements `CEP-002` 28.13(c) requires — *"an owner, a constitutional route, and an acceptance condition"* — whose absence *"makes the disposition void."*

**Namespace note.** `WP-GDR-nnn` is prefix-distinct from `WP-UCCEP-001…005` (closed to addition by constraint **K-07**), from `WP-UCDA-001…007`, and from the `OA-n` operator-action register. These are packages of this programme's own register and are **not** additions to any located set.

### `WP-GDR-001` — Realize registers 8–11 of the eleven-register set

| Field | Record |
|---|---|
| **Id** | `WP-GDR-001` |
| **Raised by** | `GD-19` (DDI-19) |
| **Owner** | **`UCI-001`** — `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-UCI-001-UNIVERSAL-CHANGE-INTELLIGENCE-AND-REGENERATION-STANDARD.md` (`CMG-DLG-15`), the declared owner of registers 8–11 per `GOV-INT-001` §6.2 |
| **Constitutional route** | `GOV-INT-001` §6.2 (the eleven-register set in one store) · §7.2 steps 3–4 (additive schemas; `config.py` family declarations + `register.sh` Phase 0/rollback path, append-only) · SECTION 11 (*"READY TO ADD … additive schemas + config declaration pending"*; *"no new engine required"*) · `REG-AUTO-001` L4, §11, §12 (append-only family declaration) |
| **Scope** | `changes.json`, `knowledge.json`, `regeneration.json`, `rollback.json` in `00-BOOK/DATA/`; the four corresponding additive schemas; the `config.py` family declarations; the append-only Phase 0 / rollback path in `register.sh` |
| **Prerequisite** | `GOV-INT-001` SECTION 11 / §7.2 step 2 gates the work on authoring `UCI-001` (GI-RULE-0). Recorded, not waived, not re-sequenced (`GD-19-C5`) |
| **Acceptance condition** | (1) the four register files exist in `00-BOOK/DATA/`; (2) the four additive schemas exist; (3) the four families are declared in `config.py`, append-only; (4) `register.sh` carries the Phase 0 / rollback path append-only; (5) **no new engine** is added to `00-BOOK/tools/`; (6) `ukb validate` passes and register drift is **0**; (7) regeneration remains byte-identical; (8) `DG-1` and `OBS-16` are closable |
| **Constraints** | `GD-19-C1` … `C6`; `GD-12-C4` (existing store only); `GD-04-C1` (no new generator) |
| **Closes on discharge** | `DG-1`, `OBS-16` |
| **Not performed here** | No schema, declaration or register file is created by `UCCEP-000008` (`GD-19-C4`) |

### `WP-GDR-002` — Give the OA-1 anchor existence off this machine

| Field | Record |
|---|---|
| **Id** | `WP-GDR-002` |
| **Raised by** | `GD-20` (DDI-20) |
| **Owner** | **repository operator** — as `DDI-20` records, and as the analogous act **OA-1** demonstrates |
| **Constitutional route** | `CEP-001` XX (proven determinism / reproducibility) · `CEP-008` (`CMG-DLG-08`, evidence and traceability operation) · `GOV-INT-001` §2.12 (rollback architecture) and SECTION 8 Phase 7 · precedent form `UCCEP-000006/07-OPERATOR-ACTION-REGISTER.md` §1 row 1 (**OA-1**) |
| **Scope** | Configure an upstream for the working branch and give the **existing** anchor commit `1c6e750e53efdbcba5fc501d58fc99781b03a966` reachability from a remote ref |
| **Acceptance condition** | (1) the working branch has an upstream, so `git rev-parse --abbrev-ref @{u}` resolves and ahead/behind is computable; (2) the anchor commit is present on the remote and reachable from a remote ref; (3) no history was rewritten and no branch deleted; (4) `DR-1` and `OBS-12` are closable |
| **Constraints — expressly excluded acts** | `GD-20-C2`: **no** force-push, branch deletion, or history rewrite · `GD-20-C3`: **no** push to `main`/`master` · `GD-20-C4`: remote selection, visibility and access controls are the operator's determinations, on which this programme expresses no view · `GD-20-C5`: this programme performs no remote operation and changes no git configuration |
| **Closes on discharge** | `DR-1`, `OBS-12` |
| **Not performed here** | No git configuration change and no remote operation by `UCCEP-000008` |

### Referenced external package (not declared here)

| Field | Record |
|---|---|
| **Id** | **`OA-2`** — located, **not** coined by this programme |
| **Raised by** | `GD-16` (DDI-16) |
| **Located at** | `00-MASTER/UCCEP-000006/07-OPERATOR-ACTION-REGISTER.md` §1 row 2 |
| **Owner** | `UCCEP-000000` / `engine/graph` |
| **Constitutional route** | continuing condition **C-2** of the `UCCEP-000006` authorization |
| **Acceptance condition** | `uccep-bindings.json → findings[]` records `UCCEP-F-003` as discharged with the prior record retained; `UCCEP-F-003` no longer appears in the live `certification_ceiling`; the findings register is regenerated deterministically; `DG-2` closable; **C-2** discharged |
| **Why referenced, not duplicated** | `ucda-decisions.json` declares `external_work_package_sources: ["00-MASTER/UCCEP-000000/uccep-bindings.json"]` precisely so that *"A decision whose work is already registered elsewhere references that package instead of duplicating it (Zero Duplication, `CEP-002` 8.3)"*. Coining a parallel package would also breach **K-07** |
| **Barrier to performance** | Boundary **X-9**: *"No cross-programme edits. C-2 is `UCCEP-000000`'s act, not the implementer's"* |

---

## 6. Outstanding acts, consolidated

Every act this register leaves outstanding, with its owner. **None is performed by `UCCEP-000008`.**

| # | Act | Owner | Route | Blocks |
|---|---|---|---|---|
| 1 | Register the 19 decisions in `/03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` | the register's owner | `CEP-002` 28.6 | nothing (Gate already OPEN) |
| 2 | Overlay the 19 dispositions in `ucda-decisions.json` | `UCDA-000001` | `CEP-002` 28.13; **X-9** bars others | nothing |
| 3 | Index in `00-MASTER/MCP-004-MASTER-DECISIONS.md` | operational memory owner (`MCS-000`) | `CEP-002` 28.6, after step 1 | nothing |
| 4 | Discharge **`OA-2`** — correct the `UCCEP-F-003` record | `UCCEP-000000` / `engine/graph` | **C-2**; **X-9** | any certification claim (**C-2**) |
| 5 | Discharge **`WP-GDR-001`** — realize registers 8–11 | `UCI-001` | `GOV-INT-001` §6.2/§7.2/S11; gated on authoring `UCI-001` | closure of `DG-1`, `OBS-16` |
| 6 | Discharge **`WP-GDR-002`** — anchor off-machine | repository operator | `CEP-001` XX, `CEP-008` | closure of `DR-1`, `OBS-12` |
| 7 | Dispose the `DG-6` finding | four concern owners | `CMG-000001` XX.7, Art LII | certification above `CERTIFIED-PROVISIONAL` |
| 8 | Occupy Tier T1 by explicit ratification | external constituent authority | `CMG-OQ-02`, `CMG-000001` XVII.4 | non-provisional standing corpus-wide; freeze eligibility |

Acts 7 and 8 are the held matters (`DEF-01`, `DEF-02`) and are **not** work packages — no programme can be assigned them.

## 7. What this output does not do

- It **registers nothing**. No located register, overlay, or index is written.
- It **runs no engine** and recomputes no seal. `ucda.json`, `uccep.json`, their `.md` outputs and their seals are untouched by this programme.
- It **allocates no identity** (`REG-AUTO-001` remains the sole identity authority).
- It **adds nothing** to `WP-UCCEP-001…005` (**K-07**), `WP-UCDA-001…007`, or the `OA-n` register.
- It **routes no held matter**; `GD-08` and `GD-21` are excluded by construction.
- It writes **nothing** outside `00-MASTER/UCCEP-000008/`.

---

*`UCCEP-000008` Output 8. Records where each resolved decision must be registered and by whom, and declares two work packages. Registers nothing, runs nothing, seals nothing, allocates nothing. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12`.*

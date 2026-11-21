# Output 4 — Decision Family **GDR-D** · Sequencing and Ordering

> **STATUS DOMAIN:** GOVERNANCE (determination) · **STATUS BASIS:** located clauses of `CEP-009` (`CMG-DLG-09`) and `CEP-003` (`CMG-DLG-03`), plus the derived ordering facts independently recomputed by `UCCEP-000007` Output 8 at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000008` · OUTPUT 4 |
| FAMILY | **GDR-D** — Sequencing and Ordering |
| DECISIONS | `GD-14` (DDI-08) · `GD-15` (DDI-09) |
| FAMILY SUBJECT | Whether a migration sequence `M-1` … `M-n` is created, and what the consolidated implementation ordering is. |
| AUTHORITY | None of its own. Each decision is rendered within the located Owner's already-declared law (Output 0 §2). |
| FAMILY CHARACTER | The two members are the mirror of each other: `GD-14` refuses to **author** a sequence, `GD-15` recognizes that an ordering already **exists and is derived**. Together they establish that consolidation order is computed from Repository Truth and dispatched by its located owner, never hand-written. |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; every determination PROVISIONAL under `CMG-L-12` (condition **C-3**, constraint **K-09**). |

---

## GD-14 — Migration sequence

| Field | Record |
|---|---|
| **Decision ID** | `GD-14` |
| **Title** | Whether a migration sequence `M-1` … `M-n` is created for the consolidation |
| **Resolves** | `DDI-08` |
| **Family** | GDR-D |

### Problem Statement

Output 16 records **zero repository hits** for any migration sequence, and states that *"A sequence is decisional content (kind `CMG-K-17`, Decisional binding) and is inadmissible in an evidence artifact."* The owning authority is `CEP-009` (`CMG-DLG-09` — amendment and evolution operation, including **migration**), with `GOV-INT-001` §7.2 recorded as the located precedent form for an implementation sequence.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| Output 16 §1 — `grep -rn "M-1\b"` filtered for `migrat\|consolidat\|step` → **0 hits**; the freeze/reference/sequence policy grep → 2 hits, both in `07-ENGINEERING/` and both concerning that programme's own roadmap, *"neither concerns UCCEP/UCDA consolidation"* | No migration sequence exists anywhere in the repository, established by exhaustive search | `00-MASTER/UCCEP-000007/16-DECISION-DERIVED-INPUTS.md` §1 |
| `CEP-009` III.3 — *"A change SHALL produce a successor artifact; it SHALL NEVER mutate the predecessor."*; II.3 — amendment *"SHALL be non-mutating with respect to frozen truth; it SHALL produce successors and SHALL never alter a predecessor."* | Movement of a located artifact is not an available operation | `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md` |
| `CEP-009` III.1 — the change lifecycle: *"propose, classify, assess impact, admit or reject, create successor, and complete the succession, followed where applicable by deprecation and retirement of the predecessor."*; IV.1 — every change classified as additive, corrective, superseding, deprecating, or retiring; IV.6 — exactly one primary class per change | A located, ordered lifecycle already governs every change, including migration | same |
| `CEP-009` XII — the **Migration Model**, owned by `CEP-009` | Migration is an owned concern with an existing model; a rival sequence would compete with it | same |
| `CEP-009` II.4 — *"An amendment or evolution act outside a defined authorization IS PROHIBITED and SHALL be void."*; I.5 — amendment authority *"SHALL NEVER be self-conferred by Execution Authority"* | A self-authored migration sequence would be void | same |
| `CEP-007` XI.2 — *"A change affecting a frozen artifact SHALL occur ONLY through supersession"*; XI.3 — a superseded frozen artifact *"SHALL NOT be deleted"*; IX.1/IX.5 — frozen artifacts are immutable and a mutating act places the Program in **HALTED** | Migration of the frozen surfaces (Output 6 §4) is prohibited outright | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` |
| `REG-AUTO-001` P4 — identity *"allocated once and never reused, renumbered, or reordered"*; L5 — repair by re-running and appending, *"never by editing frozen artifacts, renumbering, or rewriting history"* | Migration of a registered artifact is barred on the identity side too | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md` |
| `GOV-INT-001` §7.2 — the located implementation sequence form, six numbered steps: ratify the determination → author `UCI-001` → additive schemas → `config.py` declarations + `register.sh` Phase 0/rollback path → inheritance wiring by reference → validate and certify through transaction `T` | The one located sequence form; a second would be parallel machinery | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` |
| `CMG-000001` X.14 `CMG-L-14` — no second lifecycle where one exists | A rival sequence is a rival lifecycle | `00-CMG/CMG-000001-…md` |
| `GD-06` — the consolidation mapping is **identity**; `GD-13` — append-only, forward-only, nothing moved or renamed | Repository-Truth-grounded premise: there is nothing to migrate | `02-GDR-B-…md`, `03-GDR-C-…md` |

### Constitutional Authority

**`CEP-009`** (`CMG-DLG-09` — amendment and evolution operation: change classification, impact assessment, compatibility, successor model, **migration**, deprecation, retirement, lineage preservation, evolution registry), by Articles I, II, III, IV and XII. Resolution terminates at `CMG-000001` XVII.2 Step 1. Concurrent prohibitions: `CEP-007` IX/XI, `REG-AUTO-001` P4/L5, `CMG-000001` X.14.

### Decision

**REJECTED. No migration sequence `M-1` … `M-n` is created for the consolidation.**

Four determinations are recorded:

1. **There is nothing to migrate.** `GD-06` determines the consolidation mapping is identity and `GD-13` binds append-only: no artifact is moved, renamed, re-homed, folded, renumbered, or deleted. A migration sequence presupposes relocation; the premise does not obtain.
2. **The located change lifecycle IS the sequence.** Where the consolidation makes a change, that change traverses `CEP-009` III.1 — propose, classify (IV.1, exactly one primary class per IV.6), assess impact, admit or reject, create successor, complete the succession — and, where the change is an implementation step, takes the located form of `GOV-INT-001` §7.2. No second ordering apparatus is authored.
3. **The mission numbering is not constitutional content.** The authority's own mission identifiers (`M-1D0`, `M-1D0A`, `M-1A`, and any successor) are an **operational mission sequence**, not a repository artifact, not a migration sequence, and not registered by this decision. They confer no authorization, appear in no register, and are cited in this family only as the provenance of the instruction. This is consistent with Output 16's record that their substance has no repository trace and with `CEP-002` 28.5 (conversational assertion is not evidence).
4. **Any concrete future step sequence is work, and is registered as work.** Should a later authority require an ordered set of consolidation steps, it is admitted under `CEP-009` III.1 and registered as a work package with an owner, a constitutional route and an acceptance condition — not authored as a standing sequence instrument.

### Rationale

The proposition fails on both a factual and a legal ground, and either is sufficient.

**Factually**, the premise is absent. `UCCEP-000007` established by exhaustive search that no migration sequence exists, and this family's own sibling decisions establish why one is not needed: `GD-06` fixes the mapping as identity and `GD-13` fixes append-only. A migration sequence orders the movement of things; nothing moves. Authoring one would order an empty set while creating a document that later work would mistake for a mandate.

**Legally**, the operations a migration sequence would order are prohibited. `CEP-009` III.3 states a change *"SHALL NEVER mutate the predecessor"*; `CEP-007` XI.2 confines any change to a frozen artifact to supersession, XI.3 forbids deleting the superseded predecessor, and IX.5 places the Program in **HALTED** for a mutating act. The frozen surfaces Output 6 §4 records — `application/**` at Band-12 baseline `beff9ed3…`, the frozen `data/**`/`service/**` band surfaces — are therefore unmigratable by construction, and `REG-AUTO-001` P4/L5 bar renumbering or history rewrite for everything registered.

There is a third, structural ground. `CEP-009` XII already owns the Migration Model and `GOV-INT-001` §7.2 already supplies the located sequence form. A consolidation-specific sequence would be a **second lifecycle** where one exists — precisely what `CMG-L-14` prohibits — and, being self-authored, would fall under `CEP-009` II.4 as an evolution act outside a defined authorization, hence void.

Clause 3 deserves its own note, because it is where the greatest risk of manufactured authority lay. The mission numbering arrives conversationally. Recording it as `M-1` … `M-n` inside a repository artifact would convert an instruction into apparent constitutional content and would be exactly the defect `CEP-002` 28.5 identifies — a decision whose only trace is conversational, dressed as a record. The numbering is therefore acknowledged as provenance and expressly not registered.

This is a decided matter, not a held one: the answer follows determinately from located clauses, so `CMG-000001` LVII.3's holding route does not apply.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-06` | Supplies the factual premise: the mapping is identity, nothing moves |
| Depends on | `GD-13` | Supplies append-only/forward-only, so no relocation or renumbering is available |
| Depends on | `GD-10` | The frozen surfaces are unmigratable; freeze is neither extended nor withdrawn |
| Depends on | `GD-04` | A migration engine is separately barred as a new generator |
| Depends on | `GD-09` | Consolidation is expressed as citation, which needs no sequencing |
| Depended on by | `GD-15` | With no migration sequence, ordering is the derived dependency ordering alone |
| Blocks | nothing | A rejection requires no realization (`CEP-002` 28.10) |

### Affected Programmes

None re-sequenced. All 45 measured programme directories keep their homes and their own outputs (`GD-06`). No programme is scheduled, staged, or ordered relative to another by this decision.

### Affected Registries

None mutated. The evolution registry (`CEP-009` XVI) gains no entry; no migration record is created. `changes.json` does not exist at this HEAD and is not created here (`GD-19`).

### Affected Constitutions

None amended. `CEP-009` I.5, II.3, II.4, III.1, III.3, IV.1, IV.6, XII; `CEP-007` IX.1/IX.5/XI.2/XI.3; `REG-AUTO-001` P4/L5; `CMG-000001` X.14 cited. **X-2** (`00-CEP/`) observed.

### Affected Implementations

None. No file is moved, renamed, or deleted anywhere in the repository.

### Constraints

| Id | Constraint |
|---|---|
| `GD-14-C1` | No consolidation artifact SHALL author, record, or cite a migration sequence, step sequence, phase plan, or wave plan as constitutional or authorizing content. |
| `GD-14-C2` | Every consolidation change SHALL be classified under `CEP-009` IV.1 with exactly one primary class, and SHALL traverse the III.1 lifecycle. |
| `GD-14-C3` | The authority's mission identifiers SHALL NOT be registered, cited as authorization, or presented as repository content. They are provenance only. |
| `GD-14-C4` | No consolidation act SHALL move, rename, re-home, or renumber any artifact, registered or unregistered (reinforcing `GD-06-C1`, `GD-13-C3`). |
| `GD-14-C5` | A future ordered step set, if required, SHALL be registered as a work package under `CEP-009` III.1 — never as a standing sequence instrument. |

### Acceptance Criteria

1. `grep -rn "M-1\b"` filtered for `migrat\|consolidat\|step` continues to return **0 hits** attributable to the consolidation, other than the provenance mentions in this family which are marked as such.
2. No repository artifact declares a migration sequence, and the evolution registry contains no consolidation migration record.
3. No `git mv`, rename, or deletion of a tracked artifact appears in the consolidation's history.
4. The FROZEN population and the Output 6 §4 freeze rows are unchanged.
5. The rejection carries a cited constitutional basis (satisfied: `CEP-009` II.4, III.3, IV.6, XII; `CEP-007` XI.2/XI.3; `REG-AUTO-001` P4/L5; `CMG-L-14`), so `CEP-002` 28.13(d) is met and the decision is not undispositioned under 28.14.

### Traceability

`DDI-08` → `GD-14`. Upstream: Output 16 §1 (the 0-hit searches) and §2 row DDI-08; `UCCEP-000007/06-IMPLEMENTATION-INVENTORY.md` §4 (frozen surfaces). Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-09` → `CEP-009` Articles I–IV and XII; precedent form `GOV-INT-001` §7.2; concurrent prohibitions `CEP-007` IX/XI, `REG-AUTO-001` P4/L5, `CMG-000001` X.14. Sibling premises: `GD-06`, `GD-13`, `GD-10`, `GD-04`, `GD-09`. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-14`; premise of `GD-15`.

### Future Impact

Removes the single largest source of latent, unauthorized authority in the consolidation. A hand-authored `M-1 … M-n` sequence would have become a de-facto mandate — cited, relied upon, and never ratified by anyone. Refusing it forces every consolidation change through the located change lifecycle, where it is classified, impact-assessed, admitted or rejected, and traceable. It also fixes for all later missions that the authority's mission numbering is instruction, not law.

### Disposition

**`CEP-002` 28.13(d) — REJECTED WITH CONSTITUTIONAL JUSTIFICATION.**
Cited basis: `CEP-009` II.4 (an evolution act outside a defined authorization is prohibited and void), III.3 (a change never mutates the predecessor), IV.6 (single-class decidability), XII (the Migration Model is already owned); `CEP-007` XI.2/XI.3/IX.5; `REG-AUTO-001` P4/L5; `CMG-000001` X.14 (`CMG-L-14`). Justification: the factual premise is absent (0 hits; identity mapping under `GD-06`; append-only under `GD-13`) and the operations such a sequence would order are prohibited. Per 28.10 the decision passes from REPOSITORY MAPPING directly toward closure; no realization is required.

---

## GD-15 — Implementation ordering

| Field | Record |
|---|---|
| **Decision ID** | `GD-15` |
| **Title** | The consolidated implementation ordering, and who dispatches it |
| **Resolves** | `DDI-09` |
| **Family** | GDR-D |

### Problem Statement

Output 16 records that Output 8 measures a **technical** ordering (164 layers, 1,199/1,199 placed), but that *"Which units a consolidation programme executes in which order is a separate, unrecorded decision."* The owning authorities recorded are `CEP-009` (`CMG-DLG-09`), `CMG-DLG-37` (implementation orchestration and realization, `06-IMPLEMENTATION/`), and *"`UCIC-001` for capability staging"*.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| Output 8 §2 — Kahn layering **independently recomputed** (method M-4) from `relationships.json` + `artifacts.json` alone: `Depends-On` edges **4,774** · nodes **1,199** · placed **1,199** · unorderable **0** · parallel groups (layers) **164** · critical path **164** · single-member groups **112** · largest group **908** · cycle present **NO** | A total, acyclic, deterministic ordering over the whole registered corpus already exists and is reproducible from primary data | `00-MASTER/UCCEP-000007/08-DEPENDENCY-INVENTORY.md` |
| Output 8 §2 — independent recomputation *"agrees with the located owner on every value"*, reproducing `UCCEP-000005` Outputs 7–9 (*"1199/1199 PLACED · 0 UNORDERABLE"*, *"1199/1199 ordered; identical digests across runs"*) and the `UCCEP-000006` authorization certificate (*"DAG acyclic · `scc_gt1_count` 0 · ordering 1199/1199 · critical path 164 · parallel groups 164 · unorderable 0"*) | Three independent derivations agree; the ordering is a fact of Repository Truth, not an assertion | same |
| Output 8 §3 — `engine.graph.cli validate` (M-3): `is_valid` true, all defect arrays empty, `node_count` 1,224, `edge_count` 12,841 | The graph the ordering derives from is machine-validated | same |
| Output 8 §6 — boundary **K-02** requires `scc_gt1_count = 0` and `dependency_cycle = []` | Acyclicity is a bound constraint, not an incidental property | same |
| `CEP-003` / `CMG-DLG-03` — concern `execution-operation`: *"authorization, dispatch, **sequencing**, concurrency, checkpointing, suspension, resumption, failure, recovery entry, handoff, completion"* | Execution **sequencing** is an owned concern with exactly one owner | `00-CMG/CMG-REGISTRY.json`; `00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md` |
| `GOV-INT-001` SECTION 8 — transaction `T`, Phases 0–7, *"One transaction, atomic, idempotent, guarded by the existing three gates."* | The dispatch vehicle already exists and is phase-ordered | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` |
| Output 8 §5 — 190/1,199 artifacts carry explicit `dependencies`; the remainder are generator-derived via `config.py :: CHAINS` (`note: "structural:chain"`) | The ordering's inputs are declared data, so the ordering is re-derivable rather than curated | `00-MASTER/UCCEP-000007/08-DEPENDENCY-INVENTORY.md` |
| `CEP-009` III.1 / IV.1 / IV.6 | Each individual change is classified and lifecycle-ordered independently of the dependency ordering | `00-CEP/CEP-009-…md` |
| `CMG-REGISTRY.json` — **`UCIC-001` is absent** from `artifacts[]` (it appears only as a dependency string inside `00-BOOK/DATA/artifacts.json`); `CMG-000001` X.1 `CMG-L-01` — an unrecognized artifact *"SHALL NOT be cited as constitutional authority"* | The capability-staging authority named in DDI-09 **cannot be cited**; recorded as a gap rather than relied upon | `00-CMG/CMG-REGISTRY.json`; `00-CMG/CMG-000001-…md` |
| `CMG-DLG-37` — concern `implementation-orchestration-and-realization`, owner_paths `["06-IMPLEMENTATION"]` (a path-based owner, not an artifact id) | Orchestration is owned by a zone, which realizes but does not legislate ordering | `00-CMG/CMG-REGISTRY.json` |

### Constitutional Authority

**`CEP-003`** (`CMG-DLG-03` — execution operation, expressly including **sequencing** and dispatch) — sole canonical owner for this decision. `GOV-INT-001` SECTION 8 is cited as the dispatch vehicle; `CEP-009` III.1/IV.1 as the per-change lifecycle; `CMG-DLG-37` as the realization zone. **`UCIC-001` is expressly NOT cited as authority**, because `CMG-L-01` bars it: it is absent from `CMG-REGISTRY.json`.

### Decision

**The consolidated implementation ordering IS the derived dependency ordering already computed from Repository Truth. No ordering is hand-authored.**

Five terms are fixed:

1. **The ordering is derived, not asserted.** It is the Kahn layering over the `Depends-On` relation of the registered corpus: **1,199/1,199 placed, 0 unorderable, 164 parallel groups, critical path 164, acyclic**. It is recomputable at any HEAD from `relationships.json` + `artifacts.json` alone, and three independent derivations already agree on every value.
2. **Re-derivation governs, not any recorded snapshot.** The figures above are the ordering **as measured at HEAD `9de85ad`**; where the graph changes, the ordering changes with it. No consolidation artifact holds an authoritative ordering list, and none SHALL be treated as one — that would be a second ordering record.
3. **Dispatch is `CEP-003`'s operation.** Authorization, dispatch, sequencing, concurrency, checkpointing, suspension, resumption, failure and recovery entry remain `CEP-003`'s concern, executed through transaction `T` (`GOV-INT-001` SECTION 8). This decision selects no units, schedules nothing, and authorizes no execution.
4. **Acyclicity is a precondition, not a hope.** Boundary **K-02** (`scc_gt1_count = 0`, `dependency_cycle = []`) is the standing condition on the ordering's validity. An ordering derived from a cyclic graph is void, and `UCCEP-F-003` — the fail-open validator finding — is the live risk to that precondition, routed at `GD-16`.
5. **Per-change ordering is separate and unaffected.** Each individual change additionally traverses `CEP-009` III.1 with exactly one primary class (IV.6). The dependency ordering orders *artifacts*; the change lifecycle orders *acts*. Neither substitutes for the other.

**Capability staging is expressly not routed to `UCIC-001`.** DDI-09 names it, but `UCIC-001` is absent from `CMG-REGISTRY.json` and `CMG-L-01` therefore bars citing it as constitutional authority. Capability staging consequently has **no citable owner** at this HEAD. That is recorded as an unresolved governance gap (`10-REMAINING-GOVERNANCE-GAPS.md`), not papered over with an unrecognized citation, and no capability staging order is asserted here.

### Rationale

Output 16's framing — that the *technical* ordering is measured but the *executed* ordering is a separate decision — is correct, and the correct decision is to **make the two the same** rather than to author a second one.

The positive case is strong on located evidence. The derived ordering is **total** (1,199/1,199, 0 unorderable), **acyclic** (`scc_gt1_count` 0, and acyclicity bound by **K-02**), **deterministic** (identical digests across runs), and **independently reproduced three times** — by `UCCEP-000005`, by the `UCCEP-000006` authorization certificate, and by `UCCEP-000007`'s own recomputation, agreeing on every value. Its inputs are declared data (190 explicit `dependencies` plus `config.py :: CHAINS` derivation), so it is regenerable rather than curated. An ordering with those properties is strictly better than a hand-authored one on every dimension that matters: it cannot silently disagree with the dependency facts, it cannot go stale, and it needs no maintenance.

The negative case is equally located. A hand-authored consolidation ordering would be a **second ordering record** over the same subject — parallel machinery under `CMG-L-14` and a duplication finding under `CEP-002` 14.3 — and it would necessarily drift, because the graph is live (12,841 edges, and `Depends-On` already differs from `Required-By` by 77, per Output 8 §1 / OBS-9). Clause 2 exists precisely to prevent this register from becoming that second record by accident: the numbers here are evidence of the ordering, not the ordering itself.

Clause 3's separation of ordering from dispatch follows the Registry rather than inventing a distinction: `CMG-DLG-03` explicitly allocates *sequencing* to `CEP-003`, so a determination that also dispatched would be exercising another owner's concern. Clause 4 records the one live threat honestly — the ordering's validity rests on acyclicity, and `UCCEP-F-003` records a validator that reported a cycle while returning `is_valid=true` and exit 0. Its substance is discharged in committed code (Output 8 §4), but its **record** is still open (`DG-2`), which is why `GD-16` routes it rather than assuming it away.

The `UCIC-001` refusal is the most consequential paragraph of this decision. Citing an unrecognized artifact as authority is exactly what `CMG-L-01` prohibits, and doing so to close a gap would have manufactured authority in the quietest possible way — a plausible-looking citation to a non-existent instrument. Recording capability staging as **ownerless at this HEAD** is less tidy and considerably more truthful.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-14` | With no migration sequence, the derived ordering is the only ordering |
| Depends on | `GD-01` | Dispatch runs inside the one execution architecture |
| Depends on | `GD-03` | The ordering's inputs are generator-derived under the fixed generator map |
| Depends on | `GD-12` | Clause 2's prohibition on a second ordering record is that policy applied |
| Depends on | `GD-16` | The acyclicity precondition of clause 4 depends on the `UCCEP-F-003` record being closed |
| Depended on by | any later execution authorization | Ordering must be re-derived, never read from a snapshot |
| Produces gap | capability staging has no citable owner | Carried to `10-REMAINING-GOVERNANCE-GAPS.md` |

### Affected Programmes

`UCCEP-000005` (cited as the located ordering owner; **not** edited — **X-9**) · `UCCEP-000006` (cited for the authorization certificate's ordering facts and for **K-02**; not edited) · `UCCEP-000007` (cited for the recomputation). No programme is scheduled or staged.

### Affected Registries

None mutated. `relationships.json` (12,841 edges) and `artifacts.json` (1,199) are read as primary data under **X-5**. No ordering register is created (`GD-12`).

### Affected Constitutions

None amended. `CEP-003` (`CMG-DLG-03`), `CEP-009` III.1/IV.1/IV.6, `GOV-INT-001` SECTION 8, `CMG-000001` X.1/X.14 cited.

### Affected Implementations

None. `engine/graph/**` is read as evidence only and is **X-8**-protected; the `UCCEP-F-003` remediation is `GD-16`'s routed work, not performed here.

### Constraints

| Id | Constraint |
|---|---|
| `GD-15-C1` | No consolidation artifact SHALL hand-author an implementation ordering, execution order, or unit schedule. |
| `GD-15-C2` | The ordering SHALL be re-derived from `relationships.json` + `artifacts.json` at the HEAD at which it is relied upon; no recorded snapshot — including the figures in this decision — is authoritative. |
| `GD-15-C3` | No consolidation act SHALL dispatch, authorize, or execute against the ordering; dispatch is `CEP-003`'s operation through transaction `T`. |
| `GD-15-C4` | An ordering derived from a graph failing **K-02** (`scc_gt1_count = 0`, `dependency_cycle = []`) is void and SHALL NOT be relied upon. |
| `GD-15-C5` | `UCIC-001` SHALL NOT be cited as constitutional authority while it is absent from `CMG-REGISTRY.json` (`CMG-L-01`); capability staging SHALL be treated as ownerless and recorded as a gap until an owner is located or allocated. |

### Acceptance Criteria

1. Re-derivation of the Kahn layering from `relationships.json` + `artifacts.json` at any later HEAD yields a **total** ordering: placed = node count, unorderable = 0.
2. `scc_gt1_count = 0` and `dependency_cycle = []` (**K-02**) at every HEAD at which the ordering is relied upon.
3. Re-derivation is deterministic — identical digests across runs, as `UCCEP-000005` records.
4. No consolidation artifact contains an ordering list presented as authoritative.
5. No consolidation artifact cites `UCIC-001` as authority.
6. Capability staging appears as an open gap until an owner is located or allocated.

### Traceability

`DDI-09` → `GD-15`. Upstream: Output 16 §2 row DDI-09; `UCCEP-000007/08-DEPENDENCY-INVENTORY.md` §1–§6 (and through it `UCCEP-000005` Outputs 7–9 and the `UCCEP-000006` authorization certificate); `UCCEP-000007/13-KNOWN-GAPS.md` `DG-2`. Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-03` → `CEP-003`; dispatch vehicle `GOV-INT-001` SECTION 8; per-change lifecycle `CMG-DLG-09` → `CEP-009` III.1. Refused citation: `UCIC-001`, barred by `CMG-000001` X.1 `CMG-L-01`. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-15`; gap carried to `10-REMAINING-GOVERNANCE-GAPS.md`; precondition depends on `GD-16`.

### Future Impact

Makes consolidation order a **computed property of Repository Truth** rather than a document. Every later mission that needs an order re-derives it and is therefore automatically correct with respect to the dependency facts as they then stand; no ordering artifact can drift, go stale, or be relied upon after the graph has moved. Clause 4 ties the ordering's validity to a named, testable precondition, and clause 5 leaves a visible, honest hole where an unrecognized instrument would otherwise have supplied false comfort.

### Disposition

**`CEP-002` 28.13(b) — REPRESENTED BY AN EXISTING CANONICAL CAPABILITY.**
Single canonical owner: **`CEP-003`** (`00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md`, execution operation including sequencing, `CMG-DLG-03`), whose located derived artifacts are `00-BOOK/DATA/relationships.json` and `00-BOOK/DATA/artifacts.json`. Evidence: Output 8 §1–§6 (recomputed M-4, agreeing with `UCCEP-000005` and the `UCCEP-000006` certificate); `GOV-INT-001` SECTION 8; boundary **K-02**. No further realization required; stage reached is REPOSITORY MAPPING.

---

## Family summary — GDR-D

| GD | DDI | Decision in one line | Disposition | Realization required |
|---|---|---|---|---|
| `GD-14` | DDI-08 | **No migration sequence.** Nothing moves, the located change lifecycle is the sequence, and the mission numbering is provenance not law | (d) | none |
| `GD-15` | DDI-09 | Ordering IS the derived dependency ordering (1,199/1,199, 164 layers, acyclic), re-derived not recorded; dispatch stays with `CEP-003` | (b) | none |

**Family properties:** 2 decisions · 1 recognition + 1 rejection · **zero** work packages · **zero** repository mutations outside `00-MASTER/UCCEP-000008/` · zero constitutions amended · zero registries touched · zero artifacts moved, renamed or scheduled · zero executions authorized.

**Family coherence.** The two decisions are complementary refusals to author. `GD-14` refuses to write a sequence because nothing moves and the operations it would order are prohibited; `GD-15` refuses to write an ordering because a better one is already derivable from primary data. What replaces both is computation plus the located change lifecycle — which is why neither decision requires maintenance as the corpus grows.

**One gap opened deliberately.** `GD-15` declines to route capability staging to `UCIC-001` because `CMG-L-01` bars citing an artifact absent from `CMG-REGISTRY.json`. Capability staging therefore has no citable owner at HEAD `9de85ad`, recorded as an open governance gap rather than closed by an unlawful citation.

---

*`UCCEP-000008` Output 4, family GDR-D. One recognition and one rejection, rendered within the located law of `CEP-009` (`CMG-DLG-09`) and `CEP-003` (`CMG-DLG-03`). No sequence authored, no ordering asserted, no unit scheduled, no execution authorized, no unrecognized instrument cited. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12`.*

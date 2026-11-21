# Output 0 — Canonical Governance Decision Register · Index

> **STATUS DOMAIN:** GOVERNANCE (determination) · **STATUS BASIS:** each decision below rests on a located constitutional clause and on repository evidence that resolves at HEAD `9de85ad`; no decision rests on conversation (`CEP-002` Art 28.5)

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000008` — Governance Decision Resolution Programme |
| MISSION | **M-1D0A** — Governance Decision Resolution |
| OUTPUT | 0 — Governance Decision Index |
| PHASE | 1 — Governance Decision Resolution (successor phase to `UCCEP-000007` Phase 0, Repository Discovery Baseline) |
| AUTHORITATIVE INPUT | `00-MASTER/UCCEP-000007/16-DECISION-DERIVED-INPUTS.md` — **DDI-01 … DDI-21**, the canonical backlog. Nothing outside it is resolved here. |
| AUTHORITY | **NONE OF ITS OWN.** This programme creates no authority, legislates no law, owns no concern, and allocates no identity. Every decision recorded here is rendered **by the located owner of the concern** resolved under `CMG-000001` XVII.2, and is one of: a **recognition** of law that owner has already declared, a **rejection** on grounds that owner has already declared, or a **registration of work** routed to that owner. See §2. |
| GOVERNING AUTHORITY | `00-CEP/CEP-002` Article 28 (decision assimilation, disposition, evidence) · `00-CEP/CEP-002` Article 27 (deferral lifecycle, `CMG-DLG-49`) · `00-CMG/CMG-000001` Article XVII (authority resolution) and Article LXXVI (admission) · `00-MASTER/UCCEP-000006/06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md` §1 **P-5** (programme-owned outputs under `00-MASTER/<PROGRAMME-ID>/`) |
| ROLLBACK ANCHOR | `1c6e750e53efdbcba5fc501d58fc99781b03a966` (OA-1 atomic constitutional baseline commit) |
| BASELINE | HEAD `9de85adb7e26211d07bd99b3bed356280c936a93` · working tree **CLEAN** at entry · repository status CLEAN |
| PRIOR MISSION | **M-1D0 COMPLETE** — `00-MASTER/UCCEP-000007` (Repository Discovery Baseline, 18 outputs). Not repeated, not re-measured, not superseded. |
| CERTIFICATION DISCLOSURE | `CERTIFIED-PROVISIONAL`. Constitutional Tier T1 is **VACANT** (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`). Every determination recorded here is **PROVISIONAL** under `CMG-000001` `CMG-L-12`. Nothing here is ratified or final. (condition **C-3**, constraint **K-09**) |

---

## 1. What this programme is, and is not

**It is** the canonical **Governance Decision Register** for the consolidation: one governance artifact per resolved decision family, recording for every Decision-Derived Input its governing authority, constitutional basis, decision, rationale, dependency chain, implementation impact, traceability, and resulting disposition.

**It is not**, and must not be read as:

| Not | Why, and where the thing actually lives |
|---|---|
| **A decision register within the meaning of `CEP-002` Art 28.3** | Art 28.3 provides that *"A second decision register, decision store, decision pipeline, decision gate, or decision authority IS PROHIBITED"*. **No decision originates here.** Every decision below is routed in `08-DISPOSITION-ROUTING-TABLE.md` to the **located** register competent for its class under Art 28.6 — `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-DECISION-REGISTER.md`, `03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md`, `adr/`, `knowledge/decisions.json`, `00-MASTER/MCP-004-MASTER-DECISIONS.md` — and to the located **disposition overlay** `00-MASTER/UCDA-000001/ucda-decisions.json`. This is the same self-limitation the located overlay declares of itself (`ucda-decisions.json` `$comment`: *"NOT a decision register in its own right … No decision originates here. Zero Parallel Authority."*). Precedent: **`DEC-CDAF-06`**, an already-registered decision **rejecting** the creation of a second, independent decision register. |
| **A registry** | It allocates no identity. Registration and identity remain `REG-AUTO-001` (`CMG-DLG-13`) via `00-BOOK/tools/ukb.py` + `00-BOOK/DATA/id-ledger.json`. `00-MASTER/` is excluded from corpus registration (`00-BOOK/tools/config.py` `EXCLUDE_DIR_PREFIXES`; `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md`), so these outputs hold no registered corpus identity. |
| **A constitution or an amendment** | It amends nothing. No file in `00-CEP/`, `00-CMG/`, `00-BOOK/CONTROL-TOWER/`, `00-BOOK/DATA/` or any other programme's directory is touched. Boundaries **X-1 … X-10** are observed, **X-9** (no cross-programme edits) in particular. |
| **A gate, pipeline, scheduler or daemon** | None is created (`CEP-002` 28.19). The Implementation Evidence Gate remains the located check `CK-DECISION-EVIDENCE` / `G-14` bound in `00-MASTER/UCCEP-000000/uccep-bindings.json`, and its mechanical value is **unchanged** by this programme — see `09-TRACEABILITY-VERIFICATION.md` §5. |
| **An implementation, a plan, or a migration strategy** | No code, no generator, no runtime modification, no repository restructuring, no migration execution, no sequencing execution. Work that a decision requires is **registered** as a work package with an owner, a route and an acceptance condition; it is not performed. |
| **A re-measurement** | Repository Truth is consumed from `UCCEP-000007` and from the located owners' own outputs. Nothing is re-discovered. |

## 2. The authority model — how a decision is lawful here

`CMG-000001` XVII.8: *"Resolution SHALL NEVER be resolved by the instrument seeking authority."* This programme therefore claims no jurisdiction over any concern. Instead, for each DDI:

1. **Concern lookup** (`CMG-000001` XVII.2) — the concern is resolved to exactly one Owner in `00-CMG/CMG-REGISTRY.json → concerns[]`. Resolution terminates at Step 1 in every case below; no case required Step 2 or Step 3, save the two matters that reach the vacant tier (§5).
2. **The decision is rendered within that Owner's declared law**, and is one of exactly three lawful shapes:

| Shape | What it does | Authority it requires | `CEP-002` 28.13 disposition |
|---|---|---|---|
| **RECOGNITION** | Declares that the located Owner's existing text already determines the matter, and binds the consolidation to it **by reference**. Creates no law. | None beyond the Owner's own already-declared clause | **(b)** REPRESENTED BY AN EXISTING CANONICAL CAPABILITY |
| **REJECTION** | Declines a proposition because a located clause forbids it. Creates no law. | None beyond the forbidding clause | **(d)** REJECTED WITH CONSTITUTIONAL JUSTIFICATION |
| **REGISTRATION OF WORK** | Agrees the substance and registers the unrealized work to its Owner with an acceptance condition. Realizes nothing. | None beyond the Owner's existing mandate | **(c)** REGISTERED AS AN IMPLEMENTATION WORK PACKAGE |

3. **Where none of the three is available** — because the authority is vacant, because located records genuinely contradict one another, or because the matter requires an external constituent act — the matter is **held**, not decided. Holding is a valid disposition of the *matter* and is **not** a disposition under 28.13 (`CEP-002` 28.16; `CMG-000001` LVII.3: *"It SHALL NOT be decided by default, by the detector, by the most convenient authority, or by silence"*). Held matters are recorded as `CEP-002` Article 27 deferral entries in `07-DEFERRAL-ENTRIES.md`.

**Consequence, stated plainly:** no decision below asserts new law, extends any jurisdiction, promotes any instrument into a vacant tier, or decides a matter reserved to another owner. Dispositions **(a) IMPLEMENTED** and **(e) SUPERSEDED** are used **zero times**, because this programme realizes nothing and displaces nothing.

## 3. Structure — one responsibility per artifact, one artifact per decision family

| Output | Artifact | Family | Decisions | Sole responsibility |
|---|---|---|---|---|
| 0 | `00-GOVERNANCE-DECISION-INDEX.md` | — | — | Scope, authority model, register discipline, family map, reading order |
| 1 | `01-GDR-A-EXECUTION-OWNERSHIP-AND-GENERATOR-ARCHITECTURE.md` | **GDR-A** | `GD-01` … `GD-04` | Who owns consolidated execution, and which generator owns which output |
| 2 | `02-GDR-B-OWNERSHIP-ALLOCATION-AND-CONSOLIDATION-MAPPING.md` | **GDR-B** | `GD-05` … `GD-08` | Ownership rows, source→target mapping, authoring locus, the ownership-record tension |
| 3 | `03-GDR-C-PRESERVATION-AND-NON-PROLIFERATION-POLICY.md` | **GDR-C** | `GD-09` … `GD-13` | Reference-only, freeze, no-new-documents, no-new-registries, no-deletion |
| 4 | `04-GDR-D-SEQUENCING-AND-ORDERING.md` | **GDR-D** | `GD-14`, `GD-15` | Migration sequence and implementation ordering |
| 5 | `05-GDR-E-REGISTER-EVIDENCE-AND-LINEAGE-REALIZATION.md` | **GDR-E** | `GD-16` … `GD-20` | Finding record, evidence-ignore policy, programme lineage, registers 8–11, baseline durability |
| 6 | `06-GDR-F-CONSTITUTIONAL-VACANCY.md` | **GDR-F** | `GD-21` | Tier T1 occupancy |
| 7 | `07-DEFERRAL-ENTRIES.md` | — | `DEF-01`, `DEF-02` | Article 27 entry records for the held matters |
| 8 | `08-DISPOSITION-ROUTING-TABLE.md` | — | — | Where each decision must be registered, by whom, in what shape; the two declared work packages |
| 9 | `09-TRACEABILITY-VERIFICATION.md` | — | — | DDI→GD closure proof, evidence resolution, gate-invariance proof |
| 10 | `10-REMAINING-GOVERNANCE-GAPS.md` | — | — | What governance work remains after this programme |

## 4. Decision families and the DDI → GD map

Every DDI maps to **exactly one** `GD`, and every `GD` maps back to **exactly one** DDI. No DDI is merged, split, renamed, or dropped. Verified in `09-TRACEABILITY-VERIFICATION.md` §1.

| DDI | Required decision (title as recorded by `UCCEP-000007`) | GD | Family | Governing owner (concern) | Disposition |
|---|---|---|---|---|---|
| DDI-01 | Single execution ownership | `GD-01` | GDR-A | `GOV-INT-001` (`CMG-DLG-16`) | **(b)** RECOGNITION |
| DDI-04 | UCCEP as consolidated execution generator | `GD-02` | GDR-A | `GOV-INT-001` (`CMG-DLG-16`) | **(d)** REJECTED |
| DDI-07 | Generator responsibilities | `GD-03` | GDR-A | `REG-AUTO-001` (`CMG-DLG-13`) | **(b)** RECOGNITION |
| DDI-11 | No-new-generators policy | `GD-04` | GDR-A | `GOV-INT-001` (`CMG-DLG-16`) | **(b)** RECOGNITION |
| DDI-02 | Ownership matrix | `GD-05` | GDR-B | `CMG-000001` (Registry, Art XV/XX) | **(b)** RECOGNITION |
| DDI-03 | Consolidation mapping | `GD-06` | GDR-B | `GOV-INT-001` (`CMG-DLG-16`) | **(b)** RECOGNITION |
| DDI-14 | Where the consolidation determination is authored | `GD-07` | GDR-B | `GOV-INT-001` (`CMG-DLG-16`) | **(b)** RECOGNITION |
| DDI-15 | `AUTHORITY = NONE` vs Registry-Owner tension (DG-6) | `GD-08` | GDR-B | the owner of each affected concern (XX.7) | **HELD** → `DEF-01` |
| DDI-05 | Reference-only policy | `GD-09` | GDR-C | `GOV-INT-001` (`CMG-DLG-16`) | **(b)** RECOGNITION |
| DDI-06 | Freeze policy | `GD-10` | GDR-C | `CEP-007` (`CMG-DLG-07`) | **(d)** REJECTED |
| DDI-10 | No-new-documents policy | `GD-11` | GDR-C | `CMG-000001` (Art LXXVI) | **(b)** RECOGNITION |
| DDI-12 | No-new-registries policy | `GD-12` | GDR-C | `CEP-002` (Art 28.3 / 8.3) | **(b)** RECOGNITION |
| DDI-13 | No-deletion policy | `GD-13` | GDR-C | `CEP-007` (`CMG-DLG-07`) | **(b)** RECOGNITION |
| DDI-08 | Migration sequence (`M-1` … `M-n`) | `GD-14` | GDR-D | `CEP-009` (`CMG-DLG-09`) | **(d)** REJECTED |
| DDI-09 | Implementation ordering | `GD-15` | GDR-D | `CEP-003` (`CMG-DLG-03`) | **(b)** RECOGNITION |
| DDI-16 | `UCCEP-F-003` record update (DG-2) | `GD-16` | GDR-E | `UCCEP-000000` / `engine/graph` | **(c)** WORK PACKAGE `OA-2` |
| DDI-17 | Retention of the `00-MASTER/**/evidence/` ignore policy | `GD-17` | GDR-E | `REG-AUTO-001` (`CMG-DLG-13`) | **(b)** RECOGNITION |
| DDI-18 | Meaning of `UCCEP-000001` … `000004` absence (OBS-2) | `GD-18` | GDR-E | `REG-AUTO-001` (`CMG-DLG-13`) | **(b)** RECOGNITION |
| DDI-19 | Realization of registers 8–11 (DG-1, OBS-16) | `GD-19` | GDR-E | `UCI-001` (`CMG-DLG-15`) | **(c)** WORK PACKAGE `WP-GDR-001` |
| DDI-20 | Off-machine existence of the OA-1 anchor (DR-1, OBS-12) | `GD-20` | GDR-E | repository operator | **(c)** WORK PACKAGE `WP-GDR-002` |
| DDI-21 | Which authority occupies Tier T1 | `GD-21` | GDR-F | **external constituent act** — none located | **HELD** → `DEF-02` |

**Totals:** 21 DDIs · 21 GDs · **19 RESOLVED** (13 × recognition, 3 × rejection, 3 × work package) · **2 HELD** with constitutional justification · **0 unaccounted**.

## 5. The two matters that are not decided, and why that is lawful

`CMG-000001` LVII.3 and XVII.4, and `CEP-002` 28.16, together provide that a matter which no located authority can decide is **held and routed to explicit ratification**, never decided by default. Two matters meet that test:

| Matter | Why no located authority can decide it |
|---|---|
| `GD-08` / DDI-15 | Four located ownership records disagree (`CMG-000001` XX.8 forbids a derived-truth artifact appearing as an Owner; `CMG-REGISTRY.json → concerns[]` records four such Owners). XX.7 provides that such a disagreement **IS a finding** to be disposed **by the owner of each affected concern, "never by this instrument"** — and Article LII.3 that audit *"SHALL emit findings and SHALL decide nothing."* A programme resolving it would be exercising four owners' jurisdictions at once. |
| `GD-21` / DDI-21 | Tier T1 is VACANT. XVII.4: resolution *"SHALL NOT skip the tier and SHALL NOT promote a lower instrument into it."* `CEP-006` names no competent authority; `UCCEP-000006` records the dependency as **ED-1** — *"external constituent act … No programme may self-ratify."* |

Concealing either would be prohibited (`CMG-000001` XV.7 / `CMG-P-06`). Both are therefore recorded as first-class Article 27 entries with a deferring condition, an owner on return, and a declared review point.

## 6. Reference convention

| Form | Meaning |
|---|---|
| `NN-NAME.md` with no directory | a sibling output of this programme, i.e. `00-MASTER/UCCEP-000008/NN-NAME.md` — **except** where the same output has already introduced the artifact under another programme's fully-qualified path, in which case the bare filename is shorthand for that path (the convention `UCCEP-000007` Output 0 §3 declares for bare filenames) |
| `<PROGRAMME-ID>/NN-NAME.md` — e.g. `UCCEP-000007/13-KNOWN-GAPS.md` | **programme-relative**: resolves under `00-MASTER/`, i.e. `00-MASTER/UCCEP-000007/13-KNOWN-GAPS.md`. Used for other programmes' outputs |
| any other path containing `/` | repository-relative from the repository root; a leading `/` marks a root-level artifact whose own name carries a two-digit prefix (e.g. `/02-CANONICAL-OWNERSHIP-MATRIX.md`) |
| `<zone>/<INSTRUMENT-ID>` with no filename — e.g. `00-CEP/CEP-002`, `00-CMG/CMG-000001` | the instrument of that id in that zone, whose full filename is given at first use |
| `<path> :: <SYMBOL>` or `<path> → <field>` | a symbol or field **within** the artifact at that path (e.g. `00-BOOK/tools/config.py :: EXCLUDE_DIR_PREFIXES`, `00-CMG/CMG-REGISTRY.json → concerns[]`) |
| a path containing `…`, `<…>`, `{…}` or `*` | a display elision or template, not a literal path |
| `DDI-n` · `OBS-n` · `DG-n` · `DR-n` | identifiers **owned by `UCCEP-000007`**, reproduced never coined |
| `CMG-*` · `CEP-*` · `UCCEP-F-*` · `WP-UCCEP-*` · `OA-n` · `C-n` · `K-n` · `X-n` · `P-n` · `VAC-01` | identifiers owned by other located instruments, reproduced never coined |
| `GD-n` · `GDR-x` · `DEF-n` · `WP-GDR-n` · `GG-n` | identifiers **coined by this programme**, scoped to this programme, allocated forward-only |

Identifiers coined here are deliberately prefix-distinct from every located set. In particular `WP-GDR-n` is **not** an addition to the `WP-UCCEP-001 … 005` set, which constraint **K-07** closes to addition, nor to `WP-UCDA-001 … 007`.

## 7. Basis for this programme's own identifier and location

Recorded here rather than assumed, because `GD-18` decides the question the identifier depends on.

| Question | Answer | Basis |
|---|---|---|
| May outputs be written at `00-MASTER/UCCEP-000008/`? | Yes | **P-5** — programme-owned outputs live under `00-MASTER/<PROGRAMME-ID>/` (`UCCEP-000006` §1). `00-MASTER/` is outside registration scope, so no identity is allocated and no register is disturbed (`REG-AUTO-001` P1/L1 are not engaged). |
| Why `000008` and not `000001`? | Programme numbering is forward-only from the highest existing (`000007`) | `GD-18`; `REG-AUTO-001` P4 (identity allocated once, never reused, renumbered or reordered) and L5 (append-only correction, never renumbering) |
| Does creating these artifacts violate the no-new-documents policy of `GD-11`? | No | `CMG-000001` LXXVI.2(c) — CREATE requires the recorded discovery of LXXVI.2(a). That discovery **is** `UCCEP-000007` Output 16 §1: every candidate host was enumerated and searched, with 0 hits; no existing owner can hold this content without a cross-programme edit barred by **X-9**. |

## 8. Reading order

`00` → `01` … `06` (the six decision families, in family order) → `07` (held matters) → `08` (where each decision goes next) → `09` (closure proof) → `10` (what remains).

A reader who needs only the dispositions can read §4 of this output and `09-TRACEABILITY-VERIFICATION.md` §1.

---

*`UCCEP-000008` Output 0. Records governance decisions rendered by located owners; creates no authority, no register, no law, and no implementation. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT (`VAC-01`), so every determination here is PROVISIONAL under `CMG-L-12`.*

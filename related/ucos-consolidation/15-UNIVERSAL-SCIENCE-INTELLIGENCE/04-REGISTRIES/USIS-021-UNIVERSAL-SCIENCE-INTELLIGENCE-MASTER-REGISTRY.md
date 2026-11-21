# USIS-021 — Universal Science & Intelligence Master Registry

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-021 (Universal Science & Intelligence Master Registry — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`register.sh` → `ukb build`) from the immutable ledger — next free after `USIS-DOC-000` (`UCOS-USIS-000035`). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-REGISTRY-001 (step S-02) — instantiate the **USIS Master Registry**: the single whole-corpus enumeration/resolution surface across all USIS registered artifacts and the 12 programme registry catalogs. Closes gap **G-04 (021)**; discharges the S-02 exit gate ("USIS-021 registered; every existing catalog row resolves in it; 0 orphan rows"). |
| CLASSIFICATION | Master Registry — the **whole-corpus enumeration surface** (USIS-004 tier **9 — Registry**, master index tier). It is a *projection/resolution surface* over Repository Truth; it authors **no** new allocator, certifier, ontology, taxonomy, or member content. It transcribes (does not re-determine) the registered state. |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | The USIS master-registry surface under `15-UNIVERSAL-SCIENCE-INTELLIGENCE/04-REGISTRIES/` — the single index into which every USIS artifact row and every programme-registry catalog resolves, projected to `00-BOOK/DATA` + `00-BOOK/REGISTRIES` via the reused universal mechanism. |
| DEPENDS-ON | USIS-REG-000 · USIS-REG-001…012 · USIS-005 · USIS-004 · USIS-002 · USIS-003 · USIS-001 · USIS-GOV-000 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained per `config.py` `PROGRAM_ROOTS["USIS"]`) |
| IMPLEMENTS | USIS-004 tier **9 (Registry)** — the master-index half: it materializes the single surface across which every registered USIS artifact and every programme-registry catalog is enumerated and resolves (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · Canonical Repository Structure Specification (`00-MASTER/UCOS-USIS-001/05` §3 — "`USIS-021 · MASTER-REGISTRY · 04`") · USIS-REG-000 Part D (USIS-021 forward dependency) · Wave-3 Foundation `06-IMPLEMENTATION-SEQUENCE` S-02 · gap determination `04` G-04 |
| GOVERNED BY | USIS-REG-000 (shared registry model, Part C) · USIS-001 (LAW USIS-00/02/03/05/09) · USIS-004 (24-tier meta-model) · USIS-005 (foundation) · REG-AUTO-001 (single allocator/registration transaction) · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Enumerates a corpus named by the structure specification. It creates **no** parallel allocator, **no** second certifier, and **no** competing artifact registry; identity remains `id-ledger.json`-allocated and the machine-readable projection remains `register.sh` → `ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES` (LAW USIS-02). Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Authored under EVO-USIS-W3-REGISTRY-001 to close gap **G-04 (021)** (`00-MASTER/UCOS-USIS-WAVE3-FOUNDATION/04-GAP-DETERMINATION.md` Part E: "**USIS-021** is the registry surface every Wave-3 member row needs"). Home `15-…/04-REGISTRIES/` per structure spec §3 (`USIS-021 · MASTER-REGISTRY · 04`). S-01 readiness determination (`00-MASTER/UCOS-USIS-WAVE3-STRUCTURE/06`) = "A — Ready for W3-REGISTRY-001"; entry precondition ("`04-REGISTRIES/` exists") MET; 0 blockers to S-02. No new constitutional knowledge is introduced. No `config.py` edit (`^15-…/` classifies to USIS/VOL-024; `PROGRAM_ROOTS["USIS"]` parents non-chained members). |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. The constitutional *enumerations* remain owned by their catalog artifacts (Universe → USIS-002, Science → USIS-003, Capability → USIS-006, Domain → USIS-007, Algorithm → USIS-008, Model → USIS-009, Pattern → USIS-010, …); this Master Registry holds only the **cross-corpus index/resolution surface** that references them (LAW USIS-02). It records **no** member row (per-member, Wave-3 S-07) and creates **no** governance determination (USIS-018 = S-03, USIS-019 = S-06, USIS-020 = S-10). |

> **Purpose.** Instantiate the single **USIS Master Registry** — the whole-corpus enumeration and resolution surface across (a) every registered USIS corpus artifact and (b) the 12 programme registry catalogs homed under `USIS-REGISTRY-ROOT`. It gives every Wave-3 member row (recorded per member in the applicable `USIS-REG-0NN` catalog) a single master index that resolves to a registered artifact, so tier-9 registry closure can be proven **corpus-wide** (0 orphan rows). Before this artifact there was no master index; the 12 catalogs existed as empty per-concern surfaces but no single surface enumerated the whole registered corpus. **This instrument establishes only the master index/resolution surface.** It records **no** member row, creates **no** allocator/certifier, and re-determines **no** status.

---

## PART A — Constitutional basis (why this artifact, and no other)

| Authority | What it requires of USIS-021 |
|-----------|------------------------------|
| Structure spec `05` §3 | Founding sequence names `USIS-021 · MASTER-REGISTRY · area 04`. This artifact is exactly that entry — no more, no less. |
| Gap determination `04` Part E (G-04) | "**USIS-021** is the registry surface every Wave-3 member row needs." Homed by the registry programme (S-02), not the structure programme (S-01). |
| Wave-3 Foundation `06` S-02 | Programme `EVO-USIS-W3-REGISTRY-001`; closes G-04(021); entry precondition "`04-REGISTRIES/` exists"; **exit gate = "USIS-021 registered; every existing catalog row resolves in it; 0 orphan rows."** |
| USIS-REG-000 Part D | The **USIS-021 Master Registry** (the whole-corpus enumeration surface across all Wave-3 member rows) is explicitly **out of scope of S-01** and "authored by step **S-02 (`EVO-USIS-W3-REGISTRY-001`)**". This artifact discharges that forward dependency. |
| USIS-REG-000 Part C | The shared registry model (projection surface, single owner, append-only, reference-time resolution) is **inherited unchanged**; USIS-021 adds the cross-corpus master index over that model, not a new model. |
| LAW USIS-02 / Knowledge-Once | Registration over redesign. No parallel allocator, no competing registry; the master index is a **projection**, never a second source of identity. |

## PART B — The Master Registry model (whole-corpus enumeration surface)

USIS-021 is the single index node under which two resolution surfaces are enumerated. Both are **references into Repository Truth**, never re-authored copies.

```
USIS-021  (Master Registry — single whole-corpus index; owner = USIS; home = 04-REGISTRIES/)
├── SURFACE-1 · Artifact enumeration
│     every registered USIS corpus artifact (native id → universal id → home → status),
│     resolved from id-ledger.json + artifacts.json (single source of identity)
└── SURFACE-2 · Registry-catalog enumeration
      the root anchor USIS-REGISTRY-ROOT + the 12 programme registry catalogs
      (USIS-REG-001…012), each an append-only, open, single-owner projection surface
      whose member rows (Wave-3, per member) each resolve back to SURFACE-1

Invariants:  append-only (LAW USIS-09) · single owner per concern (LAW USIS-05)
             reference-time resolution, zero hard coding (LAW USIS-02)
             every catalog row resolves to a registered artifact ⇒ 0 orphan rows (GOV-001-T3)
Projection:  register.sh → ukb build → 00-BOOK/DATA + 00-BOOK/REGISTRIES   (reused, never duplicated)
Identity:    id-ledger.json (append-only immutable ledger; the single allocator)
```

The Master Registry is **finite-by-nothing**: it enumerates whatever Repository Truth holds at build time and grows append-only as members are realized. It caps neither the artifact count nor any catalog.

## PART C — SURFACE-2 · Registry topology (root anchor + 12 programme catalogs)

Homed under the root anchor `USIS-REGISTRY-ROOT` (owned by USIS-REG-000). Each catalog is an open, append-only, single-owner projection surface; the constitutional enumeration is owned by the referenced catalog artifact (LAW USIS-02).

| # | Native ID | Universal ID | Programme registry | Enumeration source (referenced owner) | Member rows @ baseline |
|---|-----------|--------------|--------------------|---------------------------------------|:----------------------:|
| — | `USIS-REG-000` | `UCOS-USIS-000022` | Root registry anchor (`USIS-REGISTRY-ROOT`) | USIS-REG-000 (this topology) | n/a (anchor) |
| 1 | `USIS-REG-001` | `UCOS-USIS-000023` | Universe Registry | USIS-002 (Universe Catalog) | 0 (open) |
| 2 | `USIS-REG-002` | `UCOS-USIS-000024` | Science Registry | USIS-003 (Universal Science Catalog) | 0 (open) |
| 3 | `USIS-REG-003` | `UCOS-USIS-000025` | Domain Registry | USIS-007 (Domain) | 0 (open) |
| 4 | `USIS-REG-004` | `UCOS-USIS-000026` | Capability Registry | USIS-006 (Capability) | 0 (open) |
| 5 | `USIS-REG-005` | `UCOS-USIS-000027` | Algorithm Registry | USIS-008 (Algorithm) | 0 (open) |
| 6 | `USIS-REG-006` | `UCOS-USIS-000028` | Model Registry | USIS-009 (Model) | 0 (open) |
| 7 | `USIS-REG-007` | `UCOS-USIS-000029` | Pattern Registry | USIS-010 (Pattern) | 0 (open) |
| 8 | `USIS-REG-008` | `UCOS-USIS-000030` | Insight Registry | USIS-011 (Engine) / Universal Analytics | 0 (open) |
| 9 | `USIS-REG-009` | `UCOS-USIS-000031` | Reasoning-Trace Registry | USIS-016 (Evidence) + LAW USIS-07 | 0 (open) |
| 10 | `USIS-REG-010` | `UCOS-USIS-000032` | Dataset Registry | USIS-009 (Model) + Universal Data / `10-DATA/` | 0 (open) |
| 11 | `USIS-REG-011` | `UCOS-USIS-000033` | Learned-Change Registry | Universal Learning + MIP Part 21 | 0 (open) |
| 12 | `USIS-REG-012` | `UCOS-USIS-000034` | Self-Evolution Registry | Universal Self-Evolution + MIP Part 22/32 (Wave-4 content) | 0 (open) |

**Total member rows across all catalogs at this baseline = 0.** The S-02 exit-gate clause "every existing catalog row resolves in it" is therefore satisfied vacuously *and* structurally: the master index resolves the 12 catalogs + anchor themselves (SURFACE-2), and any future member row (Wave-3 S-07) resolves through its catalog into SURFACE-1 by construction of the row schema (`id` field = a registered artifact). **Orphan rows = 0.**

## PART D — SURFACE-1 · Whole-corpus artifact enumeration (master index)

The registered USIS corpus at this baseline (Repository Truth: `00-BOOK/DATA/id-ledger.json` + `artifacts.json`). This is a **transcription** of the ledger, not a second identity source; the ledger governs. Append-only — future artifacts extend this table at their registration, never renumber it.

| # | Universal ID | Native ID | Home (area) | Status |
|---|--------------|-----------|-------------|--------|
| 1 | `UCOS-USIS-000001` | `USIS-GOV-000` | `15-…/` (governance root) | ACTIVE |
| 2 | `UCOS-USIS-000002` | `USIS-001` | `00-CONSTITUTION/` | ACTIVE |
| 3 | `UCOS-USIS-000003` | `USIS-002` | `06-UNIVERSES/` | ACTIVE |
| 4 | `UCOS-USIS-000004` | `USIS-004` | `05-META-MODEL/` | ACTIVE |
| 5 | `UCOS-USIS-000005` | `USIS-003` | `07-SCIENCES/` | ACTIVE |
| 6 | `UCOS-USIS-000006` | `USIS-005` | `01-THEORY/` (+ 02/03 foundation) | ACTIVE |
| 7 | `UCOS-USIS-000007` | `USIS-007` | `08-DOMAINS/` | ACTIVE |
| 8 | `UCOS-USIS-000008` | `USIS-006` | `05-META-MODEL/` | ACTIVE |
| 9 | `UCOS-USIS-000009` | `USIS-009` | `10-MODELS/` | ACTIVE |
| 10 | `UCOS-USIS-000010` | `USIS-008` | `09-ALGORITHMS/` | ACTIVE |
| 11 | `UCOS-USIS-000011` | `USIS-010` | `11-PATTERNS/` | ACTIVE |
| 12 | `UCOS-USIS-000012` | `USIS-011` | `12-ENGINES/` | ACTIVE |
| 13 | `UCOS-USIS-000013` | `USIS-013` | `14-RUNTIME/` | ACTIVE |
| 14 | `UCOS-USIS-000014` | `USIS-012` | `13-SERVICES/` | ACTIVE |
| 15 | `UCOS-USIS-000015` | `USIS-017` | `18-APIS-SDK/` | ACTIVE |
| 16 | `UCOS-USIS-000016` | `USIS-INT-001` | `20-PROJECTS/` | ACTIVE |
| 17 | `UCOS-USIS-000017` | `USIS-014` | `15-VALIDATION/` | ACTIVE |
| 18 | `UCOS-USIS-000018` | `USIS-015` | `16-CERTIFICATION/` | ACTIVE |
| 19 | `UCOS-USIS-000019` | `USIS-016` | `17-EVIDENCE/` | ACTIVE |
| 20 | `UCOS-USIS-000020` | `USIS-ONT-000` | `02-ONTOLOGY/` (root concept anchor) | ACTIVE |
| 21 | `UCOS-USIS-000021` | `USIS-TAX-000` | `03-TAXONOMY/` (root taxa anchor) | ACTIVE |
| 22 | `UCOS-USIS-000022` | `USIS-REG-000` | `04-REGISTRIES/` (root registry anchor) | ACTIVE |
| 23 | `UCOS-USIS-000023` | `USIS-REG-001` | `04-REGISTRIES/` | ACTIVE |
| 24 | `UCOS-USIS-000024` | `USIS-REG-002` | `04-REGISTRIES/` | ACTIVE |
| 25 | `UCOS-USIS-000025` | `USIS-REG-003` | `04-REGISTRIES/` | ACTIVE |
| 26 | `UCOS-USIS-000026` | `USIS-REG-004` | `04-REGISTRIES/` | ACTIVE |
| 27 | `UCOS-USIS-000027` | `USIS-REG-005` | `04-REGISTRIES/` | ACTIVE |
| 28 | `UCOS-USIS-000028` | `USIS-REG-006` | `04-REGISTRIES/` | ACTIVE |
| 29 | `UCOS-USIS-000029` | `USIS-REG-007` | `04-REGISTRIES/` | ACTIVE |
| 30 | `UCOS-USIS-000030` | `USIS-REG-008` | `04-REGISTRIES/` | ACTIVE |
| 31 | `UCOS-USIS-000031` | `USIS-REG-009` | `04-REGISTRIES/` | ACTIVE |
| 32 | `UCOS-USIS-000032` | `USIS-REG-010` | `04-REGISTRIES/` | ACTIVE |
| 33 | `UCOS-USIS-000033` | `USIS-REG-011` | `04-REGISTRIES/` | ACTIVE |
| 34 | `UCOS-USIS-000034` | `USIS-REG-012` | `04-REGISTRIES/` | ACTIVE |
| 35 | `UCOS-USIS-000035` | `USIS-DOC-000` | `19-DOCUMENTATION/` | ACTIVE |
| 36 | `UCOS-USIS-000036` | `USIS-021` (**this artifact**) | `04-REGISTRIES/` | ACTIVE (allocated at registration) |

> The universal IDs in this table are the **allocated ledger values** as of the baseline; USIS-021's own value (`UCOS-USIS-000036`) is the next free identifier and is confirmed by the Registration Report once `register.sh` commits. Repository Truth (`id-ledger.json`) is authoritative if any value here is ever stale — this table is a projection, never the allocator.

## PART E — Universality & context disposition (no Earth-centric, no technology, no vendor assumption)

The Master Registry surface is **context-agnostic by construction**: a registered row carries only universal fields (`universal id`, `native id`, `owner`, `home`, `concern`, `status`, `depends-on`) — it encodes no planet, nation, currency, language, cloud, database, operating system, programming language, vendor, or civilization. Contexts are represented as **referenced universal abstractions owned by their canonical programs**, never re-homed here (LAW USIS-02, Reuse-First). Unknown/future contexts resolve to the open receptors and the append-only openness of every registry (LAW USIS-09).

| Context (mission requirement) | Universal-abstraction disposition (referenced owner) | Assumption encoded in the registry? |
|-------------------------------|------------------------------------------------------|:-----------------------------------:|
| Platform / Platform-Owner / Operational / Tenant | Platform program (`09-PLATFORM`) universal abstractions — referenced, not re-homed | None |
| Universe / Multiverse / Galaxy / Planet / Reality / Existence | USIS-002 universe catalog (21 seed universes) + receptors `USIS-U-FUT` / `USIS-U-UNK` | None |
| Identity | `id-ledger.json` universal identity (the single allocator) | None (universal id only) |
| Spatial / Temporal | Universal coordinate abstractions (Reality Compiler root ontology) — referenced | None |
| Language / Communication | Universal representation abstractions — referenced; registry stores no natural-language assumption | None |
| Value-Exchange / Currency | Universal Commerce meta-model — referenced; no currency/bank/tax assumption | None |
| Regulatory / Jurisdiction / Governance | GOV-001/GOV-002 + USIS governance instruments — referenced | None |
| Knowledge | Universal Knowledge Book (`00-BOOK`) — the reused projection target | None |
| Security | Security program (`14-SECURITY`) universal abstractions — referenced | None |
| Infrastructure / Deployment / Logistics / Transfer | Infrastructure program (`13-INFRASTRUCTURE`) — referenced | None |
| Analytics / Observation | USIS-REG-008 Insight Registry + Universal Analytics — referenced | None |
| **Unknown Future Contexts** | Open receptors (`USIS-U-FUT`, `USIS-U-UNK`) + append-only openness of every catalog (LAW USIS-09) | None — receptors are the universal escape hatch |

**Universality guarantee.** The registry admits a new context, universe, domain, capability, algorithm, model, pattern, service, event, workflow, runtime, validator, or certifier as a *registration* (an append-only row + a referenced owner), never as a redesign, and never by hard-coding a finite enumeration. Extensibility is therefore **unlimited** (every catalog is uncapped; the artifact enumeration is uncapped).

## PART F — Discovery model (automatic, recursive)

Discovery over the Master Registry is mechanical and requires no human enumeration:

- **Mandatory / optional / additional nuclei** — discovered by traversing `DEPENDS-ON` edges recorded in `00-BOOK/DATA/relationships.json` (projected by `ukb build`) to their transitive closure. Mandatory = edges required by USIS-004 tier contract; optional/additional = edges present but not tier-mandated; receptors (`USIS-U-FUT/UNK`) reserve slots for not-yet-existing nuclei.
- **Contexts / dependencies / registries** — discovered from SURFACE-2 (the 12 catalogs + anchor) and the enumeration-source references in Part C.
- **Ontology / taxonomy / policies / validation / certification / runtime / infrastructure / deployment** — discovered by resolving the referenced owners (USIS-ONT-000, USIS-TAX-000, USIS-014, USIS-015, USIS-013, and the referenced programs) from SURFACE-1.
- **Recursive dependency closure** — the `DEPENDS-ON` graph is acyclic and downward-only (C-07); its transitive closure over any USIS artifact terminates at `USIS-GOV-000` → prior-program terminal. The Master Registry is the single entry point for that traversal.

Discovery is thus a **graph query over Repository Truth**, not a re-declaration; the Master Registry adds the single index that makes the query well-founded.

## PART G — Registry (tier-9) closure disposition — master-index half

USIS-REG-000 Part D discharged the **foundation-level** half of tier-9 (home + root anchor + 12 catalog schemas). This artifact discharges the **master-index half**: one surface enumerates the whole registered corpus and every catalog resolves into it. The **per-member** half (each realized member records exactly one row in the applicable catalog *and* that row resolves in this Master Registry) remains discharged at each member's realization (Wave-3 S-07, gaps G-07/G-09). At this baseline: **36 artifacts enumerated, 12 catalogs + 1 anchor indexed, 0 member rows, 0 orphan rows.**

## PART H — Non-duplication guarantee (LAW USIS-02 / Knowledge-Once)

- Creates **no** parallel allocator (identity remains `id-ledger.json` via `ukb.py`), **no** second certifier (`ukbx certify` remains sole), and **no** competing artifact registry (`00-BOOK/DATA` / `00-BOOK/REGISTRIES` remain the single machine-readable projection).
- Does **not** duplicate the constitutional enumerations (Universe/Science/Capability/… remain owned by USIS-002/003/006/007/008/009/010); it references them.
- Does **not** duplicate the 12 catalogs' concerns; it indexes them.
- Does **not** re-home any reused universal abstraction (Platform/Data/Security/Infrastructure) — referenced only (Reuse-First).
- Single Master Registry; there is exactly one whole-corpus index and one owner (USIS).

## PART I — Constitutional invariants (fail-closed self-check)

1. Parallel allocator / second certifier / competing artifact registry created here: **0**.
2. Duplicate registry (two surfaces owning the whole-corpus index concern): **0** (exactly one Master Registry).
3. Member registry row authored here: **0** (per-member, Wave-3 S-07; gaps G-07/G-09).
4. Orphan catalog rows (a row not resolving to a registered artifact): **0** (0 rows at baseline; row schema binds `id` to a registered artifact by construction).
5. Closed (finite-by-construction) surface: **0** (artifact enumeration + all 12 catalogs append-only, open).
6. Governance determination created here (USIS-018/019/020): **0** (S-03 / S-06 / S-10 respectively).
7. Edits to any frozen instrument or governed source (`config.py`, `00-CEP/**`, `engine/**`, `platform/**`): **0** (authored only under `15-…/04-REGISTRIES/`; non-chained).
8. Circular dependency: **0** (Depends-On downward to USIS-REG-000/…/USIS-GOV-000; acyclic).
9. Earth/technology/vendor assumption encoded in a registry field: **0** (Part E).

Any nonzero ⇒ NOT CONSTITUTIONALLY CONFORMANT.

## PART J — What this instrument intentionally does NOT do

- It records **no** member registry row and authors **no** per-universe/per-science/per-capability content (per-member, Wave-3 S-07).
- It creates **no** allocator, certifier, or competing registry; it reuses the universal mechanism (`register.sh` → `ukb build`).
- It creates **no** governance determination — USIS-018 (Foundation Freeze, S-03), USIS-019 (Readiness, S-06), USIS-020 (Completion, S-10) are distinct, later artifacts.
- It performs **no** `config.py` edit and **no** write to any frozen stream.
- It re-determines **no** status; it transcribes the registered state (append-only).

*END — USIS-021 · UNIVERSAL SCIENCE & INTELLIGENCE MASTER REGISTRY · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*

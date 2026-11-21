# USIS-REG-000 — Programme Registries Home & Root Registry Anchor

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-REG-000 (Programme Registries Home & Root Registry Anchor — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — next free after `USIS-TAX-000`. Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-STRUCTURE-001 (step S-01) — materialize the `04-REGISTRIES/` canonical area home, instantiate the **root registry anchor**, and home the **12 programme registry catalogs** (retires gap G-02; discharges blocker B-3, tier-9 half). |
| CLASSIFICATION | Structural Home Anchor — the canonical materialization of the Registries area (USIS-004 tier **9 — Registry**). It establishes the **home**, the **root registry anchor**, and the constitutional model shared by the 12 programme registry catalogs (`USIS-REG-001…012`). It authors **no** member registry row (those are per-member, separately-authorized Wave-3 realizations) and **no** Master Registry (USIS-021 = step S-02). |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | The `15-UNIVERSAL-SCIENCE-INTELLIGENCE/04-REGISTRIES/` area — the programme-specific registry *catalog surface* against which engine/service contracts resolve at reference time and into which per-member tier-9 rows are recorded (projected to `00-BOOK/DATA` via the reused universal mechanism). |
| DEPENDS-ON | USIS-005 · USIS-004 · USIS-002 · USIS-003 · USIS-001 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **9 (Registry)** — materializes the home into which the tier-9 registry-membership obligation resolves and the root registry anchor governing the 12 programme registries (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · the Canonical Repository Structure Specification (`00-MASTER/UCOS-USIS-001/05` §2 — "`04-REGISTRIES/` all USIS registries …") · the USIS Registry Integration Manifest (`…/09` §2 — the 12 programme registries) · LAW USIS-00 C-00.3 (registry facet) |
| GOVERNED BY | USIS-001 (LAW USIS-00/02/03/04/05/09) · USIS-004 (24-tier meta-model) · USIS-005 (foundation) · REG-AUTO-001 (registration mechanism — the single allocator) · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Materializes a canonical area named by the structure specification and the registry integration manifest. It creates **no** parallel allocator, **no** second certifier, and **no** competing artifact registry; identity remains `id-ledger.json`-allocated and the machine-readable projection remains `ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES` (LAW USIS-02). Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Authored under EVO-USIS-W3-STRUCTURE-001 to close gap **G-02** (`00-MASTER/UCOS-USIS-WAVE3-FOUNDATION/04-GAP-DETERMINATION.md` Part C: "`04-REGISTRIES/` … unmaterialized … MANDATORY before tier 9") and blocker **B-3**. Canonical home `15-…/04-REGISTRIES/` per structure spec §2 and the 12-registry enumeration of `…/09` §2. No new constitutional knowledge is introduced. No `config.py` edit (`^15-…/` already classifies to USIS/VOL-024, line 275). |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. The constitutional *enumerations* remain owned by their catalog artifacts (Universe → USIS-002, Science → USIS-003, etc.); this area holds only the **registry-row projection surface** that references them (LAW USIS-02). The standalone USIS **Master Registry (USIS-021)** is a distinct, later artifact (step S-02) and is **not** created here. |

> **Purpose.** Materialize the canonical **`04-REGISTRIES/`** area home named by the structure specification, instantiate the single **root registry anchor**, and home the **12 programme registry catalogs** as *empty, schema-bearing row-projection surfaces* (0 member rows). This makes tier-9 **registry closure** *dischargeable* per member and gives engine/service contracts (USIS-011/012) a resolution target at reference time. Before this artifact the home did not exist, so no engine contract could resolve and no member could record a tier-9 row (USIS-004 Part D ⇒ NOT realized). **This instrument establishes only the home, the root anchor, and the 12 catalog schemas.** It records **no** member row, creates **no** allocator/certifier, and creates **no** Master Registry (USIS-021, step S-02).

---

## PART A — Constitutional basis

- **Structure spec §2** — "`04-REGISTRIES/` all USIS registries (Universe, Science, Domain, Capability, Algorithm, Model, Pattern, Insight, Reasoning-Trace, Dataset, Learned-Change, Self-Evolution)." This artifact materializes exactly that area.
- **Registry Integration Manifest (`…/09` §2)** — names the same 12 programme-specific registries under `04-REGISTRIES/` and fixes the registration mechanism (three layers: curated `config.py` rule, per-artifact metadata self-declaration, path-derived catch-all) materialized by `register.sh`.
- **USIS-004 Part C tier 9 (Registry)** — parent = Taxonomy (tier 8); closure = registry closure. USIS-011 (Engine) resolves algorithm/model/pattern members from `04-REGISTRIES/` at reference time; with the home absent the engine contract had no resolution target.
- **LAW USIS-02 / USIS-03** — registration over redesign; no parallel allocator, no competing registry. The 12 catalogs are **projections**, not a second source of identity.

## PART B — The root registry anchor and the 12 programme registries

| Field | Value |
|-------|-------|
| Root anchor id | `USIS-REGISTRY-ROOT` |
| Kind | root registry anchor — the single governance node under which the 12 programme registry catalogs are homed |
| Owner | USIS program (single canonical owner; LAW USIS-05) |
| Home | `15-…/04-REGISTRIES/` (this area) |
| Projection target (reused, never duplicated) | `ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`; identity via `id-ledger.json` |

The 12 programme registry catalogs homed under this anchor (each its own artifact, each an empty schema-bearing surface with **0 member rows** pending Wave-3):

| # | Native ID | Programme registry | Canonical enumeration source (referenced) |
|---|-----------|--------------------|-------------------------------------------|
| 1 | `USIS-REG-001` | Universe Registry | USIS-002 (Universe Catalog) |
| 2 | `USIS-REG-002` | Science Registry | USIS-003 (Universal Science Catalog) |
| 3 | `USIS-REG-003` | Domain Registry | USIS-007 (Domain) + `…/06` domain/HI catalog |
| 4 | `USIS-REG-004` | Capability Registry | USIS-006 (Capability) |
| 5 | `USIS-REG-005` | Algorithm Registry | USIS-008 (Algorithm) |
| 6 | `USIS-REG-006` | Model Registry | USIS-009 (Model) |
| 7 | `USIS-REG-007` | Pattern Registry | USIS-010 (Pattern) |
| 8 | `USIS-REG-008` | Insight Registry | USIS-011 (Engine) / Universal Analytics (`USIS-U-ANL`) |
| 9 | `USIS-REG-009` | Reasoning-Trace Registry | USIS-016 (Evidence) + LAW USIS-07 |
| 10 | `USIS-REG-010` | Dataset Registry | USIS-009 (Model) + Universal Data (`USIS-U-DAT`) / `10-DATA/` |
| 11 | `USIS-REG-011` | Learned-Change Registry | Universal Learning (`USIS-U-LRN`) + MIP Part 21 |
| 12 | `USIS-REG-012` | Self-Evolution Registry | Universal Self-Evolution (`USIS-U-EVO`) + MIP Part 22/32 (content = Wave-4; surface = open receptor) |

## PART C — Shared registry model (inherited by USIS-REG-001…012)

Every programme registry catalog is a projection surface of the canonical form:

```
{ registry: <name>, owner: USIS, home: 04-REGISTRIES/USIS-REG-0NN,
  enumeration_source: <canonical catalog/architecture artifact, by reference>,
  row_schema: <the columns a member row records at its Wave-3 realization>,
  rows: []  # 0 member rows at this baseline — Wave-3 populates append-only,
  projection: ukb build → 00-BOOK/DATA + 00-BOOK/REGISTRIES,
  closure: registry closure (tier 9) discharged per member at its realization }
```

- **Append-only / open (LAW USIS-09).** Rows are added by registration, never rewritten/renumbered/removed; every registry is uncapped.
- **Single owner (LAW USIS-05).** Each registry owns exactly one row-projection concern; the constitutional enumeration remains owned by the referenced catalog.
- **Reference-time resolution.** Engine/service contracts (USIS-011/012) resolve algorithm/model/pattern members against these catalogs at reference time, enumerating no member (zero hard coding).

## PART D — Registry (tier-9) closure disposition (foundation level only)

This artifact discharges the **foundation-level** half of tier-9 registry closure: the home, the root anchor, and the 12 catalog schemas exist and resolve. The per-member half — each realized member records exactly one row in the applicable registry, and every row resolves to a registered artifact — is **undischarged until members exist** and is proven in each member mission (gaps G-07/G-09). The **USIS-021 Master Registry** (the whole-corpus enumeration surface across all Wave-3 member rows) is explicitly **out of scope** and is authored by step **S-02 (`EVO-USIS-W3-REGISTRY-001`)**; this anchor references it as a forward dependency and does not pre-empt it.

## PART E — Non-duplication guarantee (LAW USIS-02 / Knowledge-Once)

- Creates **no** parallel allocator (identity remains `id-ledger.json` via `ukb.py`), **no** second certifier (`ukbx certify` remains sole), and **no** competing artifact registry (`00-BOOK/DATA`/`REGISTRIES` remain the single machine-readable projection).
- Does **not** duplicate the constitutional enumerations: the Universe/Science/etc. *catalogs* remain owned by USIS-002/003/006/007/008/009/010; the 12 catalogs here are **row-projection surfaces** that reference them.
- Does **not** create the Master Registry (USIS-021 = S-02).
- Single home per registry; no two catalogs own the same concern (verified in Part B mapping).

## PART F — Constitutional invariants (fail-closed self-check)

1. Parallel allocator / second certifier / competing artifact registry created here: **0**.
2. Duplicate registry (two catalogs owning one concern): **0** (12 distinct concerns, 12 distinct owners).
3. Member registry row authored here: **0** (per-member, Wave-3; gaps G-07/G-09).
4. Closed (finite-by-construction) registry: **0** (all 12 append-only, open).
5. Master Registry (USIS-021) created here: **0** (deferred to S-02).
6. Edits to any frozen instrument or governed source (`config.py`): **0** (authored only under `15-…/04-REGISTRIES/`; non-chained).
7. Circular dependency: **0** (Depends-On downward to USIS-005/004/003/002/001).

Any nonzero ⇒ NOT CONSTITUTIONALLY CONFORMANT.

## PART G — What this instrument intentionally does NOT do

- It records **no** member registry row and authors **no** per-universe/per-science/per-capability content (per-member, Wave-3).
- It creates **no** allocator, certifier, or competing registry; it reuses the universal mechanism.
- It creates **no** Master Registry (USIS-021, step S-02) and **no** governance determination (USIS-018/019/020).
- It performs **no** `config.py` edit.

*END — USIS-REG-000 · PROGRAMME REGISTRIES HOME & ROOT REGISTRY ANCHOR · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*

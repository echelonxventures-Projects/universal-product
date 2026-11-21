# 02 — WAVE 1 REUSE MATRIX

**Principle:** Reuse before creation. Knowledge Once. Zero Duplicates
(LAW USIS-02). Wave 1 creates **only** the USIS substrate content that does not
already exist; every mechanism, engine, registry, and gate below is **reused as
authority**, never re-implemented.

Legend — Disposition: **REUSE** (consume/invoke as-is) · **EXTEND** (append-only
into an existing open structure) · **REFERENCE** (link to a canonical home, never
fork) · **CREATE** (genuinely new USIS content with no canonical predecessor).

---

## 1 — Engines & tooling

| Asset | Location | Capability | Wave 1 disposition |
|---|---|---|---|
| `ukb.py` | `00-BOOK/tools/` | build · validate · enforce · search · trace · evolve · stats · exec; append-only ID/page allocation; classification; graph; registries; control tower | **REUSE** — the sole ID/registration authority |
| `ukbx.py` | `00-BOOK/tools/` | sync · twin · portal · validate · twin --check · certify (10 domains) | **REUSE** — digital twin, navigation, certification runtime |
| `register.sh` | `00-BOOK/tools/` | 10-phase atomic registration transaction + `--guard` drift gate | **REUSE** — the convergence gate for every Wave 1 commit |
| `config.py` | `00-BOOK/tools/` | CLASSIFY_RULES / CHAINS / PROGRAM_ROOTS / CROSS_PROGRAM / VOLUMES / INCLUDE_EXTENSIONS / EXCLUDE_DIR_PREFIXES | **REUSE**; **EXTEND** (append-only) only if chaining USIS-001…021 (see `04` W1-0) |
| `freeze_c4_engine.py` | `00-MASTER/UCOS-USIS-WAVE0/` | 7-stream FREEZE model (successor to C2/C3) | **REUSE** — basis for FREEZE C5 in Wave 6; unchanged in Wave 1 |
| closure engines (`closure_engine.py`, phase2/phase3) | `engine/` (`make closure*`) | UAKOS concept homing + gap closure (concepts=431, gaps=0) | **REUSE** — knowledge-closure verification |
| RIE — Repository Intelligence Engine | `intelligence/` | digital twin **of the repository** | **REFERENCE** — USIS *consumes* RIE outputs; it is NOT the subject-matter substrate and must not be duplicated (USIS-GOV-000 §5) |
| `governance_telemetry.py` | `00-BOOK/tools/` | runtime audit → `.runtime/` (gitignored) | **REUSE** — untouched |

## 2 — Registries & DATA projections

| Asset | Location | Wave 1 disposition |
|---|---|---|
| UNIVERSAL-ARTIFACT-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** (append rows for USIS-001…005 via `ukb build`) |
| UNIVERSAL-PAGE-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** (append-only page allocation) |
| KNOWLEDGE-GRAPH-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** (new USIS edges; acyclic) |
| VOLUME-REGISTRY | `00-BOOK/REGISTRIES/` | **REUSE** — VOL-024 already present; no new volume |
| CHANGE-VERSION-LINEAGE-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** (change events for new artifacts) |
| CERTIFICATION-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** (per-capability certification rows) |
| `id-ledger.json` (append-only) | `00-BOOK/DATA/` | **EXTEND** — page cursor advances from 9134; no reuse/renumber |
| artifacts/relationships/change-ledger/volumes/control-tower/certification `.json` | `00-BOOK/DATA/` | **REUSE** mechanism; regenerated deterministically each build |

## 3 — USIS-internal registries (per `USIS-009`, created under `15-…/04-REGISTRIES/`)

The 12 USIS registries (Universe, Science, Domain, Capability, Algorithm, Model,
Pattern, Insight, Reasoning-Trace, Dataset, Learned-Change, Self-Evolution) are
**CREATE** as USIS content, but each **REUSES** the universal registration
mechanism — their rows are ordinary registered artifacts/registry entries, not a
parallel registration system. Wave 1 stands up the registry *structure*
(`04-REGISTRIES/`) and the Universe/Science/Capability registries needed by
USIS-002/003/004; the remainder populate in Waves 2–4.

## 4 — Governance, evidence, validation, certification

| Asset | Reused as | Disposition |
|---|---|---|
| UCIC-001 (15-stage fail-closed) | per-capability execution model | **REUSE** |
| SCIENCE_INTELLIGENCE lifecycle (USIS-008) | per-capability lifecycle | **REUSE** |
| LAW Ω∞-000 · MIP Parts 19/20/21/25/22/32 · Universes U16/U24/U25/U26/U28 | constitutional anchors | **REFERENCE** |
| GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 | governance gates | **REUSE** |
| `ukb validate` (+ jsonschema in CI) | structural + schema validation | **REUSE** |
| `ukb enforce` | registration completeness / classification | **REUSE** |
| `ukbx validate` · `ukbx twin --check` (7) · `ukbx certify` (10 domains) | twin + certification gates | **REUSE** |
| `register.sh --guard` + `determinism-evidence/` | drift + determinism gate | **REUSE** |
| USIS-011 proof obligations (21) | fail-closed acceptance predicates | **REUSE** |
| CI `ucos-registration-gate.yml`, `ec1-ci.yml`, `determinism.yml` | independent backstop | **REUSE** |

## 5 — Substrate content Wave 1 must CREATE (no canonical predecessor)

| Wave 1 artifact | Area | Canonical home | Realizes / references |
|---|---|---|---|
| USIS-001 Constitution | `00-CONSTITUTION/` | new | LAW USIS-00; anchors MIP 19/20/21 |
| USIS-002 Universe Catalog (21) | `06-UNIVERSES/` | new | **REFERENCES** U16/U24/U25/U26/U28 (realization, not duplication) |
| USIS-003 Science Catalog (30 seed) | `07-SCIENCES/` | new | open, append-only |
| USIS-004 Capability Meta-Model (24-tier) | `05-META-MODEL/` | new | LAW USIS-08 |
| USIS-005 Theory/Ontology/Taxonomy | `01-THEORY/`, `02-ONTOLOGY/`, `03-TAXONOMY/` | new | Ontology/Taxonomy closure |

## 6 — Must-never-duplicate register (Reuse-First enforcement, LAW USIS-02)

| Concern | Canonical home (REFERENCE only) | Duplication risk |
|---|---|---|
| Data / data governance | `10-DATA/` | USIS Data Universe must reference, not re-home |
| Security | `14-SECURITY/` | USIS references security controls |
| Repository runtime / digital twin | `08-RUNTIME/`, `intelligence/` (RIE) | USIS runtime specializes; does not fork RIE |
| Simulation | Universe U26 | USIS Simulation Universe realizes U26 |
| Knowledge / Analytics / Intelligence / Evolution | U24 / U16 / U25 / U28 | USIS realizes; no competing universe |
| Registration / ID allocation | `ukb.py` + `id-ledger.json` | never a second allocator |
| Certification runtime | `ukbx certify` | never a second certifier |

Any USIS artifact that would re-home or re-implement a row above **violates LAW
USIS-02** and fails USIS-011 obligations 2/3 — it must instead carry a
`Depends-On`/reference edge to the canonical home.

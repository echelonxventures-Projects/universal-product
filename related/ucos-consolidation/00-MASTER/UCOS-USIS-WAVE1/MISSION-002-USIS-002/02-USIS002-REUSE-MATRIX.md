# 02 — USIS-002 REUSE MATRIX

**Principle:** Reuse before creation · Knowledge Once · Zero Duplicates (LAW
USIS-02). USIS-002 creates **only** the Universe-Catalog content that has no
canonical predecessor; every engine, registry, gate, and governance instrument
below is **reused as authority**, never re-implemented.

Legend — **REUSE** (invoke/consume as-is) · **EXTEND** (append-only into an
existing open structure) · **REFERENCE** (link to a canonical home, never fork) ·
**CREATE** (genuinely new USIS content with no canonical predecessor).

---

## 1 — Engines & tooling

| Asset | Location | Capability | USIS-002 disposition |
|---|---|---|---|
| `ukb.py` | `00-BOOK/tools/` | append-only ID/page allocation · classify · build · validate · enforce · graph | **REUSE** — sole ID/registration authority |
| `ukbx.py` | `00-BOOK/tools/` | sync · twin · portal · validate · twin --check · certify (10 domains) | **REUSE** — twin/navigation/certification runtime |
| `register.sh` | `00-BOOK/tools/` | 10-phase atomic registration transaction + `--guard` drift gate | **REUSE** — convergence gate for the USIS-002 commit |
| `config.py` | `00-BOOK/tools/` | CLASSIFY_RULES · CHAINS · PROGRAM_ROOTS · CROSS_PROGRAM · VOLUMES | **REUSE** (routing already covers `15-…/`); **EXTEND** (append-only) only if chaining USIS-002 into `CHAINS["USIS"]` (decision, `03` §5) |

## 2 — Universal registries & DATA projections

| Asset | Location | USIS-002 disposition |
|---|---|---|
| UNIVERSAL-ARTIFACT-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** — append rows for the Universe-Catalog artifact(s) |
| UNIVERSAL-PAGE-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** — append-only page allocation (cursor 9136→) |
| KNOWLEDGE-GRAPH-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** — new USIS-002 edges (Depends-On USIS-001; universe→MIP reference edges); acyclic |
| VOLUME-REGISTRY | `00-BOOK/REGISTRIES/` | **REUSE** — VOL-024 present; **no new volume** |
| CHANGE-VERSION-LINEAGE-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** — change/version events for the new artifact(s) |
| CERTIFICATION-REGISTRY | `00-BOOK/REGISTRIES/` | **EXTEND** — certification row for USIS-002 |
| `id-ledger.json` | `00-BOOK/DATA/` | **EXTEND** — page cursor advances from **9136**; nothing reused/renumbered |
| artifacts/relationships/change-ledger/control-tower/certification `.json` | `00-BOOK/DATA/` | **REUSE** mechanism; regenerated deterministically each build |

## 3 — USIS-internal registry (per `USIS-009` manifest)

| Asset | Home | USIS-002 disposition |
|---|---|---|
| **USIS Universe Registry** | `15-…/04-REGISTRIES/` | **CREATE** (new USIS content) — but **REUSES** the universal registration mechanism; its rows are ordinary registered artifacts/registry entries, never a parallel allocator. USIS-002 stands up this registry structure and populates the 21 seed universes. |

## 4 — Governance, validation, certification

| Asset | Reused as | Disposition |
|---|---|---|
| UCIC-001 (15-stage fail-closed) | USIS-002 execution model | **REUSE** |
| SCIENCE_INTELLIGENCE lifecycle (USIS-008) | DEFINED→…→CERTIFIED lifecycle | **REUSE** |
| USIS-001 (LAW USIS-01/02/09) | governing determination + constitutional anchor | **REFERENCE** |
| LAW Ω∞-000 · MIP Parts 19/20/21/25 · Universes U16/U24/U25/U26/U28 | realization anchors | **REFERENCE** |
| GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 | governance gates | **REUSE** |
| `ukb validate` / `ukb enforce` | structural/schema + completeness/classification | **REUSE** |
| `ukbx validate` · `ukbx twin --check` (7) · `ukbx certify` (10) | twin + certification gates | **REUSE** |
| `register.sh --guard` + `determinism-evidence/` | drift + determinism gate | **REUSE** |
| USIS-011 proof obligations (esp. 2/3 no-dup, 4 orphan, 5 acyclic, 10 registry closure, 18 byte-stable) | fail-closed acceptance predicates | **REUSE** |
| CI `ucos-registration-gate.yml` · `ec1-ci.yml` · `determinism.yml` | independent backstop | **REUSE** |

## 5 — Content USIS-002 must CREATE (no canonical predecessor)

| USIS-002 artifact | Corpus home | Realizes / references |
|---|---|---|
| Universe Catalog (21 universes) | `15-…/06-UNIVERSES/` (roadmap/plan naming; see D-1) | **REFERENCES** U16/U24/U25/U26/U28 — realization, not duplication |
| USIS Universe Registry structure | `15-…/04-REGISTRIES/` | universal registration mechanism (REUSE) applied to universe rows |

## 6 — Must-never-duplicate register (Reuse-First enforcement, LAW USIS-02)

Each seed universe that realizes an existing canonical concern **REFERENCES** it
via a `Realizes`/`Depends-On`/reference edge and must **not** re-home or fork it:

| USIS universe | Canonical home (REFERENCE only) | Duplication risk if forked |
|---|---|---|
| Universal Data (`USIS-U-DAT`) | `10-DATA/` + U07 | re-homing data governance |
| Universal Simulation (`USIS-U-SIM`) | U26 + Part 25 | competing simulation universe |
| Universal Knowledge (`USIS-U-KNW`) | U24 + Part 19 | competing knowledge registry |
| Analytics/Intelligence/Reasoning/Prediction (`USIS-U-ANL/INT/RSN/PRD`) | U16 / U25 + Part 20 | competing analytics/intelligence catalogs |
| Universal Self-Evolution (`USIS-U-EVO`) | U28 + Part 22/32 | competing evolution model |
| Security/Governance/Runtime (as domains) | `14-SECURITY/`, U03, `08-RUNTIME/` / `intelligence/` (RIE) | forking security/RIE |
| Registration / ID allocation | `ukb.py` + `id-ledger.json` | a second allocator |
| Certification runtime | `ukbx certify` | a second certifier |

Any USIS-002 row that would re-home or re-implement a target above **violates LAW
USIS-02** and fails USIS-011 obligations 2/3 — it must instead carry a
`Realizes`/`Depends-On`/reference edge to the canonical home.

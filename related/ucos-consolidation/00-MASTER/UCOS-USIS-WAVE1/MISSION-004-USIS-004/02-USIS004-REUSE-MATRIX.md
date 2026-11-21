# 02 — USIS-004 REUSE MATRIX

**Principle:** Reuse before creation · Knowledge Once · Zero Duplicates (LAW
USIS-02). USIS-004 (Universal Capability Meta-Model) creates **only** the
meta-model specification; every engine, registry, gate, law, and governance
instrument below is **reused as authority**, never re-implemented. The meta-model
itself *mandates* Reuse-First (§5) — so USIS-004 both practices and encodes it.

Legend — **REUSE** · **EXTEND** (append-only) · **REFERENCE** (link, never fork) ·
**CREATE** (new USIS content, no canonical predecessor).

---

## 1 — Engines & tooling (all REUSE)

| Asset | Location | USIS-004 disposition |
|---|---|---|
| `ukb.py` | `00-BOOK/tools/` | **REUSE** — ID/registration/classification/graph authority |
| `ukbx.py` | `00-BOOK/tools/` | **REUSE** — twin/portal/certify runtime |
| `register.sh` | `00-BOOK/tools/` | **REUSE** — 10-phase transaction + `--guard` convergence gate |
| `config.py` | `00-BOOK/tools/` | **REUSE** — `^15-…/ → USIS/USIS/VOL-024` already routes `05-META-MODEL/`; no edit expected (non-chained, program-root parenting) |

## 2 — Universal registries & DATA projections (EXTEND via reused mechanism)

| Asset | USIS-004 disposition |
|---|---|
| UNIVERSAL-ARTIFACT-REGISTRY | **EXTEND** — append row for the Meta-Model artifact |
| UNIVERSAL-PAGE-REGISTRY / `id-ledger.json` | **EXTEND** — append-only page allocation (cursor 9139→) |
| KNOWLEDGE-GRAPH-REGISTRY | **EXTEND** — new edges (Depends-On USIS-001/USIS-002; Realizes LAW USIS-08); acyclic |
| VOLUME-REGISTRY | **REUSE** — VOL-024; **no new volume** |
| CHANGE-VERSION-LINEAGE / CERTIFICATION registries | **EXTEND** — change/version + certification rows |

## 3 — Constitutional / prior USIS assets (REFERENCE)

| Asset | Disposition | Note |
|---|---|---|
| USIS-001 — **LAW USIS-08** (meta-model conformance), LAW USIS-02/04/09 | **REFERENCE** (Depends-On) | governing determination + constitutional anchor; USIS-004 operationalizes LAW USIS-08 |
| USIS-002 — Universe Catalog | **REFERENCE** (Depends-On) | the meta-model's Science tier parents to the Universal Science Universe enumerated in USIS-002 |
| **UCIC-001** (15-stage contract; Output-6 Universal Completion Definition) | **REUSE / REFERENCE** | the meta-model's conformance rule is the UCIC-001 Output-6 instantiation |
| **MIP per-part 24-field contract** | **REFERENCE** | upstream frozen anchor the 24-tier chain composes; not re-homed |
| Per-program meta-models (RUNTIME-005 · PLATFORM-005 · DATA-005 · SERVICE-005 · APPLICATION-005 · INFRASTRUCTURE-005) | **REFERENCE** (pattern precedent) | USIS-004 is the science-intelligence-substrate meta-model; it follows the established `*-005 META-MODEL` pattern without forking those program-specific models |

## 4 — Governance, validation, certification (all REUSE)

| Asset | Disposition |
|---|---|
| UCIC-001 (15-stage fail-closed) | **REUSE** — execution model |
| SCIENCE_INTELLIGENCE lifecycle (USIS-008) | **REUSE** — DEFINED→…→CERTIFIED |
| GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 | **REUSE** — governance gates |
| `ukb validate`/`enforce`, `ukbx validate`/`twin --check`/`certify`, `register.sh --guard` | **REUSE** — validation/certification/determinism gates |
| USIS-011 proof obligations (esp. 2/3 no-dup, 4 orphan, 5 acyclic, 10 registry closure, **13 capability closure**, 14 dependency closure, 18 byte-stable) | **REUSE** — fail-closed acceptance predicates |
| CI gates (`ucos-registration-gate.yml`, `ec1-ci.yml`, `determinism.yml`) | **REUSE** — independent backstop |

## 5 — Content USIS-004 must CREATE (no canonical predecessor)

| USIS-004 artifact | Corpus home | Realizes / references |
|---|---|---|
| Universal Capability Meta-Model (24-tier chain + tier contract + conformance rule + agnosticism boundary + Reuse-First + recursion) | `15-…/05-META-MODEL/` (USIS-005 §2/§3) | **REALIZES** LAW USIS-08; **REFERENCES** USIS-001/USIS-002, UCIC-001 Output-6, MIP 24-field contract |

## 6 — Must-never-duplicate register (LAW USIS-02)

The meta-model **references** and does **not** fork: UCIC-001 (execution contract);
the MIP per-part 24-field contract; the per-program `*-005` meta-models; the
universal registries and the `ukb`/`ukbx` engines. USIS-004 defines the *tier
schema* the science-intelligence substrate follows — it does not create a second
allocator, certifier, ontology-core, or a competing capability model.

## 7 — Reuse-First conclusion

All infrastructure is reusable; the sole genuinely-new content is the meta-model
specification artifact. Both hard dependencies (USIS-001, USIS-002) exist and are
reusable as authority. **No prerequisite is missing** — contrast USIS-003, whose
meta-model prerequisite (this artifact) was absent.

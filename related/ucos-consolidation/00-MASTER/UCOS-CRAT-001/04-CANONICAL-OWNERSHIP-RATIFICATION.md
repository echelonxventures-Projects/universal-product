# 04 — Canonical Ownership Ratification

| Field | Value |
|-------|-------|
| ARTIFACT ID | CRAT-004 (Canonical Ownership Ratification) |
| PROGRAM | UCOS-CRAT-001 · MISSION EIP-018C |
| STATUS | COMPLETE · AUTHORITY = NONE (DERIVED) |
| SOURCES | EKAP-003 (Canonical Ownership Matrix) · `closure.json` canonical-home register · `config.py` PROGRAM_ROOTS/CHAINS · CVER-006 |
| INVARIANT | No concept has multiple constitutional owners (`duplicate_canonical_homes = 0`). |

> **Purpose.** Ratify the Canonical Ownership Model — that every knowledge concern has exactly one canonical owner, that ownership is total and single-valued, and that reference/source artifacts are evidence-only (never owners).

---

## 1 — Program-level canonical ownership (Knowledge-Once) — ratified

| Concern | Canonical owner (program root) | Home |
|---------|-------------------------------|------|
| Constitution / supreme law | LAW Ω∞-000 · MIP `UCOS-MIP-000002` | root / 00-SOURCE (frozen) |
| Governance / execution determinations | `UCOS-GOV-*` / `UCOS-EXEC-*` (VOL-020) | 02-MASTER |
| Architecture theory | `ARCH_*` constitutions | 02-MASTER / 04-REFERENCE |
| Runtime / Platform / Data / Service / Application / Infrastructure / Security | RUNTIME / PLATFORM-GOV-000 / DATA-GOV-000 / SERVICE-GOV-000 / APP / 13-INFRA / 14-SEC roots | 08…14 |
| Ontology / Meta-models | UCKO / METACLASS families | knowledge corpus |
| Knowledge Book / registries | UKB `UCOS-BOOK-000000` | 00-BOOK |
| Digital Twin / Master Book | UKB-ADV (VOL-021) / UMB (VOL-022) | 00-BOOK/ADVANCEMENT · /MASTER-BOOK |
| **Science & Intelligence** | **`USIS-GOV-000`** (proposed) | **15-… (Wave 0)** |

Each program has exactly one `PROGRAM_ROOT` and a single acyclic `Depends-On` chain (CROSS_PROGRAM) — **zero circular ownership, zero duplicate ownership**.

## 2 — Per-dimension canonical ownership (USIS scope) — ratified

Single canonical owner per dimension (EKAP-003 §2): Canonical Owner · Constitution · Registry · Ontology · Taxonomy · Capability · Theory · Evidence · Runtime · Validation · Certification · Documentation · Implementation (referenced, never owned by the reference tier).

## 3 — Reference / source ownership rule — ratified (evidence-only)

| Artifact class | Role | Rule |
|----------------|------|------|
| `00-SOURCE/**` (frozen) | Evidence source | never implementation authority; derived concepts owned by homed family |
| `04-REFERENCE/**` | Reference/evidence | informs, never owns implementation |
| `03-CATALOGS/**` | Catalog owner | owns its canonical catalog entry |

Knowledge Assimilation Law compliance: reference/source carry no governing-determination role; UCIC Stage-3 requires a determination + anchor (EKAP-003 §3; EKAP-006).

## 4 — Ownership determination (measured)

| Metric | Value |
|--------|:-----:|
| Concepts with multiple constitutional owners | **0** (`duplicate_canonical_homes=0`) |
| Orphan concepts (no owner) | **0** (`orphan_concepts=0`) |
| Not-homed concepts | **0** (`not_homed_concepts=0`) |
| In-repo unhomed | **0** (`in_repo_unhomed=0`) |
| Program roots | 31 (acyclic) |
| No-Orphan (GOV-001-T3) | SATISFIED (CVER-006) |

**Canonical ownership is total and single-valued.**

## 5 — Determination

**The Canonical Ownership Model is RATIFIED (derived).** Every concern maps to exactly one acyclic program root; ownership is total, single-valued, and No-Orphan-compliant; reference/source artifacts are structurally evidence-only. Zero duplicate ownership, zero orphan, zero circular ownership on measured evidence.

*END — 04 · UCOS-CRAT-001 · CANONICAL OWNERSHIP RATIFICATION · AUTHORITY = NONE (DERIVED).*

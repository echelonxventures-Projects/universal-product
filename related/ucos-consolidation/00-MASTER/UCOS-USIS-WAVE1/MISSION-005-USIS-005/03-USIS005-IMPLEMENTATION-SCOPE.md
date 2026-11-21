# 03 — USIS-005 IMPLEMENTATION SCOPE DETERMINATION

**Principle:** minimal, repository-derived, No-Orphan, Zero-Duplicate. The precise
boundary below is derived from committed evidence (structure-spec §2/§3, roadmap,
USIS-004 meta-model tiers 6/7/8, USIS-011 obl 11/12).

---

## 1 — CREATE (genuinely new, no canonical predecessor)

| Artifact | Home | Content (derived from committed evidence) |
|---|---|---|
| **USIS-005 — Theory / Ontology / Taxonomy Foundation** (single artifact) | `15-…/01-THEORY/` (recommended; first of areas 01/02/03) | establishes the substrate meaning foundation: (a) the **Theory** of universal science & intelligence (explanatory foundation, area 01); (b) the **substrate Ontology** framework — concept/relation model + **Ontology Closure** rule (area 02, USIS-011 obl 11); (c) the **Taxonomy** framework — taxon→root parent rule + **Taxonomy Closure** (area 03, USIS-011 obl 12); all conforming to USIS-004 meta-model tiers 6/7/8 and referencing the U24/Part 19 knowledge ontology (LAW USIS-02). |

Recommended as **one** foundation artifact (mirroring the single-artifact
USIS-001…004 pattern; minimal surface; single canonical ownership). A 3-artifact
per-area split (01/02/03) is an admissible alternative — a **non-blocking**
authorer decision.

## 2 — MODIFY (append-only into existing open structures)

| Target | Change | Note |
|---|---|---|
| Universal registries (ARTIFACT/PAGE/KNOWLEDGE-GRAPH/CHANGE-VERSION-LINEAGE/CERTIFICATION) | **EXTEND** (append rows/edges via reused `register.sh`) | automatic; not hand-edited |
| `id-ledger.json` | **EXTEND** (append-only page allocation) | automatic |
| **`config.py`** | **NONE** | USIS-005 is non-chained; areas 01/02/03 auto-classify via the existing `^15-…/` rule. **No governed-source edit.** |

## 3 — REFERENCE ONLY (link to canonical home, never fork — LAW USIS-02)

| Reference | Canonical home |
|---|---|
| USIS-001 (LAW USIS-00/02/04/08/09) | `15-…/00-CONSTITUTION/` |
| USIS-002 (universes the ontology/taxonomy organize) | `15-…/06-UNIVERSES/` |
| USIS-004 (meta-model tiers 6/7/8 Theory/Ontology/Taxonomy) | `15-…/05-META-MODEL/` |
| USIS-011 obl 11 (Ontology Closure) / 12 (Taxonomy Closure) | operational memory |
| U24 Knowledge / MIP Part 19 knowledge ontology registry | upstream (referenced, never re-homed) |
| Repository structure (21-area tree) | committed `config.py` + physical tree |
| Structure-specification blueprint (`05-…STRUCTURE-SPECIFICATION.md`) | `00-MASTER/UCOS-USIS-001/` (operational memory) |

## 4 — OUT OF SCOPE (MUST NOT be created)

- Individual theories/ontologies/taxonomies of **specific** universes or sciences
  (per-member Wave-3 realizations discharging obl 11/12 per capability).
- Any per-universe / per-layer architecture (USIS-006…017).
- The Master Registry (USIS-021) and governance determinations (USIS-018/019/020).
- **A "repository structure specification" corpus artifact** — the structure is
  already canonically encoded in committed `config.py` + the tree; re-registering
  it would duplicate canonical knowledge (LAW USIS-02 / Knowledge-Once).
- Any `config.py` edit; any frozen-path edit; any commit/tag/push.
- USIS-005 must not populate concept/taxon **instances** — foundation/framework only.

## 5 — Expected repository impact (minimal)

| Impact | Detail |
|---|---|
| New corpus files | 1 (the Theory/Ontology/Taxonomy Foundation) under `15-…/01-THEORY/` |
| New registrations | USIS-005 (`UCOS-USIS-000006` expected, append-only) + portal page |
| Projections regenerated | `00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}` |
| Governed source | **none** (`config.py` unchanged) |
| Volumes | **no new volume** — VOL-024 reused |
| Artifact count | 1006 → **1007** |
| Frozen paths / upstream programs | **untouched** |

## 6 — Validation / certification / traceability requirements (fail-closed)

- **Validation:** `ukb validate` → `ukb enforce` (0 orphan) → `ukbx validate` →
  `ukbx twin --check` (C-07 acyclic) → `ukbx certify` (10/10). Gating USIS-011
  obligations: **2/3** (no duplicate ontology/taxonomy), **4** (0 orphans), **5**
  (acyclic), **8** (Knowledge Once), **10** (registry closure), **11** (ontology
  closure — foundation level), **12** (taxonomy closure — foundation level), **14**
  (dependency closure), **18** (byte-stable).
- **Certification:** `ukbx certify` 10 domains over scope 1007; obl 16/17 at UCIC
  Stage 9/10; FREEZE C2/C3/C4 immutable.
- **Traceability:** `Depends-On → USIS-002, USIS-004`; `Implements → USIS-004`
  (tiers 6/7/8); `Parent → USIS-GOV-000`; `Authorized-By → USIS-001`; downward,
  acyclic, complete spine to `USIS-GOV-000`.

**Scope determination: precise, minimal, and repository-derived.** One CREATE
artifact; zero MODIFY of governed source; the rest REFERENCE-ONLY or OUT-OF-SCOPE.

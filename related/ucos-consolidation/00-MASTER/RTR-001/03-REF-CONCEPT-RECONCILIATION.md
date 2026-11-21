# RTR-001 · Output 03 — REF CONCEPT RECONCILIATION

| Field | Value |
|-------|-------|
| MISSION | RTR-001 — Repository Truth Reconciliation · Concept Layer |
| AUTHORITY | **NONE — DERIVED TRUTH.** Verification only; no concept is created, homed, or implemented. |
| BASELINE | HEAD `ab78f350` |
| SCOPE | The 12 REF concept families reported by RA-002, verified against committed evidence. |
| METHOD | `git ls-files` (commit status) + `artifacts.json`/registry (registration) + `21-…` family regex + RA-002/RA-003 cross-read. |

---

## 1. Two layers must be distinguished for every REF concept

RA-002 already proved (and RA-003 corroborated) that REF knowledge lives at **two distinct layers**:

- **Artifact layer** — the physical `.md` reference-architecture constitutions. These **ARE** committed and UKB-registered (`REF-000 = UCOS-ARCH-000024`, registry row 86; `REF-DATA/EVENT/API/WORKFLOW/SERVICE/APPLICATION-001`, rows 74–80). At this layer there is **no gap** — the definitions physically exist inside Repository Truth.
- **Concept-ledger layer** — the gitignored `20/21/22` registers. `REF` is **not a recognized family** (the normalization regex enumerates 26 families; `REF`/`CAT`/`GEN` are absent). At this layer every REF concept is **un-homed / un-inventoried**.

The status verdict below is therefore always dual. The single most important fact: the concept-ledger layer is **not Repository Truth** (gitignored, AUTHORITY = NONE), so "MISSING at the concept-ledger layer" does **not** mean "lost from Repository Truth" — the authored definition is safe in a committed, registered artifact.

## 2. Verification matrix — the 12 reported concept families

Legend:
- **EXISTS** — defined in a committed, registered artifact (present in Repository Truth).
- **ALIASED** — a generic equivalent concept is already homed under another family (e.g. ARCH); the REF specialization is a named variant of it.
- **PARTIALLY HOMED** — authoritatively defined only in committed `04-REFERENCE`, but consumed/mirrored downstream (`05-GENERATION`) and/or partially covered by a generic concept; not homed as a REF concept.
- **MISSING** — present only as `04-REFERENCE` prose; no downstream mirror and no concept-ledger home.

| # | Reported family | RA-002 ref | Committed source (artifact layer) | Concept-ledger layer | **Verdict** |
|---|-----------------|:----------:|-----------------------------------|----------------------|:-----------:|
| 1 | Reference Meta-Model | M-01 · REF-000 §1 | EXISTS (REF-000, registered) | absent; no REF family | **EXISTS (artifact) / MISSING (concept-ledger)** |
| 2 | Reference Identity Model (9-field) | M-02 · §3 | EXISTS (REF-000) | absent | **EXISTS / MISSING** |
| 3 | Realization Facets (8) | M-03 · §4 | EXISTS (REF-000); consumes ARCH-INFRA/OPS/OBS/CERT/BCDR | absent as REF; ARCH concerns homed | **PARTIALLY HOMED** (ARCH concerns homed; 8-facet REF decomposition MISSING at concept-ledger) |
| 4 | Classification Model (9 classes) | M-04 · §8 | EXISTS (REF-000) | absent | **EXISTS / MISSING** |
| 5 | Lifecycle Model (8 states) | M-05 · §9 | EXISTS (REF-000) | generic ARCH lifecycle present | **ALIASED** (generic lifecycle homed; REF specialization MISSING) |
| 6 | Registry Model (6 registries) | M-06 · §10 | EXISTS as spec (REF-000); only artifact-level registry rows instantiated | absent; registries not instantiated as data | **PARTIALLY HOMED** (spec EXISTS; instances MISSING — see M-14) |
| 7 | Runtime Binding Model | M-08 · §12 | EXISTS (REF-000); enforced conceptually by GEN | absent | **PARTIALLY HOMED** (defined; mirrored in `05-GENERATION`; not concept-homed) |
| 8 | Generation-Readiness Model | M-09 · §14 | EXISTS (REF-000); consumed by GEN-000 | absent | **PARTIALLY HOMED** (REF→GEN bridge mirrored downstream) |
| 9 | Quality Model (7 dimensions) | M-10 · §15 | EXISTS (REF-000) | absent | **EXISTS / MISSING** |
| 10 | Governance Model | M-13 · §7 | EXISTS (REF-000) | largely satisfied by ARCH-GOV-001 | **ALIASED** (ARCH-GOV-001 covers structurally; REF specialization MISSING) |
| 11 | Traceability Model (7 types) | M-12 · §6 | EXISTS (REF-000) | generic traceability (MCP-006, `26-…` matrix) | **ALIASED / PARTIALLY HOMED** (generic traceability homed; REF 7-type model not concept-homed) |
| 12 | Safety Boundary Model | M-11 · §16 | EXISTS (REF-000 + mandatory AUTHORITY BOUNDARY block in all 7 REF docs) | generic governance boundary in constitution | **PARTIALLY HOMED** (boundary concept present in governance corpus; REF-scoped instance defined only in REF-000) |

### Roll-up

| Verdict | Count | Families |
|---------|:-----:|----------|
| EXISTS (artifact) / MISSING (concept-ledger) | 4 | Meta-Model, Identity, Classification, Quality |
| PARTIALLY HOMED | 5 | Realization Facets, Registry, Runtime Binding, Generation-Readiness, Safety Boundary |
| ALIASED (generic equivalent homed) | 3 | Lifecycle, Governance, Traceability |
| Outright MISSING from Repository Truth entirely | **0** | — every family is defined in a committed, registered REF artifact |

**Key result:** **not one** of the 12 families is lost from Repository Truth. All 12 are authored in committed, registered artifacts. What is missing is their representation **in the non-authoritative concept ledger**, which cannot represent them because `REF` is not an admitted family.

## 3. Concept normalization inspection (`20` / `21` / `22`)

| Register | Committed? | REF concepts present? | Finding |
|----------|:----------:|:---------------------:|---------|
| `20-CANONICAL-CONCEPT-REGISTER` | No (ignored) | 0 | 431/506 concepts across non-REF families only |
| `21-CONCEPT-NORMALIZATION-REGISTER` | No (ignored) | 0 | Family regex enumerates 26 families; **omits `REF`, `CAT`, `GEN`** |
| `22-CANONICAL-HOME-REGISTER` | No (ignored) | 0 | No REF home rows |

**Are REF concepts normalized / represented indirectly / excluded intentionally / missing?**

- **Not normalized.** `REF` is not a family in `21`, so no REF anchor can be bucketed or homed.
- **Represented indirectly — partially.** Realization patterns (SRP/RRC/ERC/ARC/WRC/SRC/AppRC) and formulas are mirrored in the committed `05-GENERATION` frameworks (RA-002 Part B / P-01…P-10). Lifecycle/Governance/Traceability have generic ARCH homes. So there is *indirect* representation for several families.
- **Excluded — by omission, not by decision.** There is no committed record of an intentional decision to exclude `REF`/`CAT`/`GEN`. RA-002 classifies the omission as the **root-cause defect (M-00)**: the engine's curated family regex simply never admitted them.
- **Missing — at the concept-ledger layer only.** True for all 12 families as REF concepts.

## 4. Knowledge-Once corroboration (RA-003)

RA-003 independently certified (READ ONLY, `04-REFERENCE` scope): **Knowledge Once HOLDS — 0 duplicate canonical homes**, under a deliberate 3-layer facet-ownership model:

```
IDENTITY   → CAT family (03-CATALOGS)   "what exists"
REALIZATION→ REF family (04-REFERENCE)  "how it is physically realized"
GENERATION → GEN family (05-GENERATION) "how it is generated"
```

This means the REF concepts are **not duplicates** and their absence from the concept ledger is **not a Knowledge-Once violation** — it is a coverage gap in a subordinate tool, not a competing/duplicate canonical store. The only residue RA-003 flagged is 2 stray `~$*.docx` Word temp files (non-knowledge) and 1 cosmetic namespace note (REF-000 registered under the ARCH universal-ID prefix).

## 5. Reconciliation of the REF finding

- RA-002's REF finding is **CORRECT and fully explained**: REF governance meta-model concepts are un-homed **at the concept-ledger layer** because `REF` is not an admitted family (M-00).
- It is **not** a Repository-Truth loss: all 12 families are committed + registered at the artifact layer, and several are indirectly represented downstream.
- Because the concept ledger is non-authoritative, homing the REF family is **not required to keep Repository Truth consistent.** It becomes required *only if* governance decides the concept ledger must be authoritative and complete (a future, separately-authorized decision — see `05-FINAL-DETERMINATION.md`).

*END — RTR-001 · Output 03 · AUTHORITY = NONE (DERIVED TRUTH). Read-only; no concept implemented or homed.*

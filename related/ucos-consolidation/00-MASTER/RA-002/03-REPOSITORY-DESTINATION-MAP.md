# RA-002 — REPOSITORY DESTINATION MAP (Output 03 of 03)

| Field | Value |
|-------|-------|
| MISSION | RA-002 — Knowledge Gap Determination (READ ONLY) |
| AUTHORITY | **NONE — DERIVED TRUTH.** All destinations/owners/waves below are *recommendations*. This document homes nothing, ratifies nothing, and authorizes no EC-series step. |
| PURPOSE | Map every concept found only in `04-REFERENCE/` to its recommended canonical destination, owner, and sequencing so a future (separately-authorized) enrichment pass can home it. |
| INPUT | `01-KNOWLEDGE-GAPS.md`, `02-MISSING-CONCEPTS.md`. |

---

## 1 — CANONICAL DESTINATION LAYERS (evidence)

| Layer code | Repository home | Role | Owner program |
|-----------|-----------------|------|---------------|
| L-CONCEPT | `00-MASTER/UAKOS-CLOSURE-002/20-CANONICAL-CONCEPT-REGISTER.md`, `22-CANONICAL-HOME-REGISTER.md` | The concept ledger — the layer where REF concepts are currently **absent** | UAKOS closure |
| L-NORM | `00-MASTER/UAKOS-CLOSURE-002/21-CONCEPT-NORMALIZATION-REGISTER.md` | Concept-family namespace definition (must admit `REF`/`CAT`/`GEN`) | UAKOS closure |
| L-GRAPH | `00-MASTER/UAKOS-CLOSURE-002/28-KNOWLEDGE-GRAPH.md`, `26-CONCEPT-TRACEABILITY-MATRIX.md` | Concept relationships + traceability | UAKOS closure |
| L-REG | `00-BOOK/REGISTRIES/` + `06-IMPLEMENTATION/UCOS-Ω∞-REGISTRY-PLATFORM.md` | Registry substrate for instantiated REF registries | Registry Platform |
| L-MASTER | `02-MASTER/UCOS-Ω∞-CONSOLIDATION-PROGRAM-MASTER-INDEX.md` | Program-level cross-reference (already has §11E) | Consolidation program |
| L-GEN | `05-GENERATION/*` | Downstream consumer that mirrors realization patterns | Generation program |
| L-SRC | `04-REFERENCE/ARCHITECTURAL-SOURCES/` | Frozen/superseded source inputs (read-only) | — |

**Note on `04-REFERENCE` itself:** it remains the **canonical owning document** for REF concepts (its artifacts are registered). The destinations below are where each concept must be *homed/indexed*, not relocated — `04-REFERENCE` files are read-only per their own Authority Boundary.

---

## 2 — DESTINATION MAP: MISSING CONCEPTS (Part A)

| ID | Concept | Canonical owner | Primary destination | Secondary destination | Priority | Depends on |
|----|---------|-----------------|---------------------|-----------------------|:--------:|-----------|
| M-00 | `REF`/`CAT`/`GEN` family namespace | UAKOS closure | L-NORM | — | **P1** | — |
| M-01 | Reference Architecture Meta-Model | REF-000 | L-CONCEPT | L-GRAPH | **P1** | M-00 |
| M-11 | Reference Safety/Authority Boundary | REF-000 | L-CONCEPT | L-MASTER | **P1** | M-00 |
| M-02 | 9-Field Identity Model | REF-000 | L-CONCEPT | L-REG | P2 | M-00, M-01 |
| M-03 | 8 Realization Facets | REF-000 | L-CONCEPT | L-MASTER | P2 | M-00, M-01 |
| M-04 | 9 Reference Classification Classes | REF-000 | L-CONCEPT (taxonomy) | — | P2 | M-00 |
| M-06 | Reference Registry Model (6 registries) | REF-000 + Registry Platform | L-REG | L-CONCEPT | P2 | M-02, M-14 |
| M-07 | Reference Certification Model | REF-000 (via ARCH-CERT-001) | L-CONCEPT | `06-IMPLEMENTATION` cert evidence | P2 | M-03 |
| M-08 | Reference Runtime Binding Model | REF-000 | L-CONCEPT | L-GEN (enforcement) | P2 | M-06 |
| M-09 | Generation-Readiness Model | REF-000 (→ GEN-000) | L-CONCEPT | L-GEN | P2 | M-03, M-08 |
| M-12 | Reference Traceability Model (7 types) | REF-000 | L-GRAPH | L-CONCEPT | P2 | M-00, M-06 |
| M-14 | Instantiated per-family realization registries | REF family + Registry Platform | L-REG | L-GEN | P2 | M-06, M-02 |
| M-05 | Reference Lifecycle Model | REF-000 | L-CONCEPT | — | P3 | M-00, M-01 |
| M-10 | Reference Quality Model (7 dims) | REF-000 | L-CONCEPT | `…54-…QUALITY-GATES.md` | P3 | M-00 |
| M-13 | Reference Governance Model | REF-000 (via ARCH-GOV-001) | L-CONCEPT | L-MASTER | P3 | M-00 |

---

## 3 — DESTINATION MAP: PARTIALLY-CANONICAL CONCEPTS (Part B)

All rows: **owner** = cited REF doc; **primary destination** = L-CONCEPT with a definition↔consumption link to L-GEN; **depends on** = M-00 + M-01.

| ID | Concept | Definition (owner) | Consumption link (already canonical) | Priority |
|----|---------|--------------------|--------------------------------------|:--------:|
| P-01 | SRP-A…SRP-G | REF-DATA-001 §2.1 | `05-GENERATION/…DATA-GENERATION-FRAMEWORK.md §2.2` | P2 |
| P-02 | RRC-1…RRC-4 | REF-DATA-001 §2.2 | `…DATA-GENERATION-FRAMEWORK.md` | P2 |
| P-03 | EVP-01…12 / ERC-1…3 | REF-EVENT-001 §2.1–2.2 | `…EVENT-GENERATION-FRAMEWORK.md` | P2 |
| P-04 | APIP-01…15 / ARC-1…3 | REF-API-001 §2.1–2.2 | `…API-GENERATION-FRAMEWORK.md` | P2 |
| P-05 | WFP-01…12 / WRC-1…4 | REF-WORKFLOW-001 §2.1–2.2 | `…WORKFLOW-GENERATION-FRAMEWORK.md` | P2 |
| P-06 | SVCP-01…09 / SRC-1…4 | REF-SERVICE-001 §2.1–2.2 | `…SERVICE-GENERATION-FRAMEWORK.md` | P2 |
| P-07 | APPP-01…09 / AppRC-1…4 | REF-APPLICATION-001 §2.1–2.2 | `…APPLICATION-GENERATION-FRAMEWORK.md` | P2 |
| P-08 | Derivation formulas | REF-EVENT/API/SERVICE/APPLICATION §2 | GEN frameworks | P2 |
| P-09 | Service 7-facet Boundary Model | REF-SERVICE-001 §3 | `…SERVICE-GENERATION-FRAMEWORK.md` | P3 |
| P-10 | App Experience/Interaction/Presentation | REF-APPLICATION-001 §3–5 | `…APPLICATION-GENERATION-FRAMEWORK.md` | P3 |

---

## 4 — DESTINATION MAP: SUPERSEDED / DEPRECATED SOURCES

| Item | Current state | Recommended disposition | Destination |
|------|---------------|-------------------------|-------------|
| `ARCHITECTURAL-SOURCES/*.docx`, root `.docx` sources | Registered as `UCOS-REF-000007…000013`, some FROZEN | Keep read-only; mark **Superseded-by-canonical-.md** in registry note | L-SRC (stay in place) |
| `UCOS Ω∞ MASTER IMPLEMENTATION PLAN v2.docx` | `.md` equivalent exists at repo root | Point registry entry to the `.md`; flag `.docx` superseded | L-SRC |
| `~$*.docx` lock files | Temp artifacts | Excluded — not knowledge | n/a |

No canonical REF/ARCH/CAT/GEN artifact requires a destination change — all are ACTIVE and correctly homed at the artifact layer.

---

## 5 — RECOMMENDED SEQUENCING (execution waves — recommendation only)

| Wave | Goal | Items | Gate |
|:----:|------|-------|------|
| **W0** | Enable homing | M-00 (admit `REF`/`CAT`/`GEN` families) | `21-CONCEPT-NORMALIZATION-REGISTER.md` updated |
| **W1** | Home the governance meta-model (root-cause) | M-01, M-11, then M-02–M-04, M-12 | REF concepts appear in `20`/`22` with a single home each |
| **W2** | Home realization patterns + link to GEN | P-01…P-08 (+ M-08, M-09) | Definition↔consumption links resolve; no drift |
| **W3** | Instantiate registries + certification/quality | M-06, M-07, M-14, M-05, M-10, M-13, P-09, P-10 | Per-family registries queryable; REF quality/cert recorded |
| **W4** | Re-run Repository-Truth determination | (validation) | `19-REPOSITORY-TRUTH-DETERMINATION.md` re-scored with REF concept layer populated |

---

## 6 — VERIFICATION HOOKS (how a future pass proves closure)

1. Grep `00-MASTER/UAKOS-CLOSURE-002/2*.md` for `REF-000`, `SRP-`, `Reference Architecture` → must return **non-zero** (currently zero).
2. `21-CONCEPT-NORMALIZATION-REGISTER.md` must list `REF`, `CAT`, `GEN` as families (currently absent).
3. Each of M-01…M-14 and P-01…P-10 must have exactly one `#Homes` entry in `22-CANONICAL-HOME-REGISTER.md`.
4. `19-REPOSITORY-TRUTH-DETERMINATION.md` concept-layer facets ("Every concept has exactly one canonical home") must move from UNPROVEN → PASS for the REF family.

---

## 7 — STANDING CAVEAT

This determination is **derived truth**, consistent with the authoritative `19-REPOSITORY-TRUTH-DETERMINATION.md` (**FAIL-CLOSED** at the concept layer) and **not** with the session-start hook's `gaps=0 / concepts=431 / CLOSED` claim, which the repository's own files contradict (`20-CANONICAL-CONCEPT-REGISTER.md`: 506 concepts / 396 homed / 110 gaps; and zero REF concepts recorded). Per the mission's "derive everything from evidence" directive, the file evidence governs.

*END — RA-002 · Output 03 · REPOSITORY DESTINATION MAP · AUTHORITY = NONE (DERIVED TRUTH). Read-only; no implementation performed. STOP.*

# 08 — Baseline Version Register

> PROGRAM **UCOS-AB-001** · PHASE-001 · ARCHITECTURE BASELINE v1.0
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Establish the register that assigns and records architecture baseline versions. Baseline v1.0 is entry #1; every future Change-Control-approved change (doc 07 step 7) appends a new immutable version here.

## 1. Versioning Scheme

| Field | Rule |
|---|---|
| Format | `vMAJOR.MINOR` (architecture baseline), independent of code/git tags |
| MAJOR | incremented by a C-AMENDMENT or C-DEFECT change to a frozen constitution/spine |
| MINOR | incremented by a C-ADDITIVE change (new member along the frozen spine) |
| Anchor | each version pins a git HEAD + foundational-corpus hash set |
| Immutability | a published version is never edited; corrections create a new version |

## 2. The Register

| Version | Date | Git anchor | Scope sealed | Authority | Status |
|---|---|---|---|---|:---:|
| **v1.0** | 2026-07-22 | `b67a720` (branch `governance-reconciliation`) | Full constitutional architecture strata B-01…B-20 (doc 01); realization substrate EC-1/EC-2 + Bands 10–12 frozen, Band 13 realization-certified (freeze pending) | AB-001 record (NONE); binding via CEP-007 | **ESTABLISHED (this program)** |
| v1.1 (reserved) | — | — | Band-13 Freeze (EC3-B13-U12) + EC-3 lane closure (MEP-05) | CEP-007 / Governance | PLANNED |
| v1.2 (reserved) | — | — | UMA instantiation (UCOS-UMA-001 → runtime) | Governance | PLANNED |
| v2.0 (reserved) | — | — | reserved for any C-AMENDMENT/C-DEFECT (requires proof + ratification) | CEP-009/006 | RESERVED |

> Reserved rows are placeholders showing the expected next increments; they assert nothing and are assigned only when the corresponding Change-Control change closes.

## 3. Version Anchoring & Reproducibility

Each version records: git HEAD, `99-FREEZE` source-hash set, guard integrity result, and the inventory snapshot (docs 02/03). A version is *reproducible*: re-deriving the inventory at the pinned anchor MUST reproduce the recorded states (doc 17 baseline record supplies the reproducibility method).

## 4. Divergence Note (fail-closed honesty)

At v1.0 establishment, `git HEAD = b67a720` while operational memory (MCP-002/005) reports realization commits through EC3-B13-U11. v1.0 anchors to the **verifiable git HEAD**; the operational-memory frontier is recorded as *derived evidence* (AUTHORITY=NONE). v1.1 will re-anchor once the HEAD/operational-memory reconciliation and Band-13 freeze are committed under the MCP-007 boot contract. No unified anchor is fabricated.

## 5. Determination

**BASELINE VERSION REGISTER IS ESTABLISHED WITH v1.0 AS ENTRY #1.** The versioning scheme, register, anchoring, and reproducibility rule are defined; future versions append immutably via Change Control (doc 07). Reserved rows document the expected path (Band-13 freeze → UMA instantiation) without asserting them.

*END — 08 · UCOS-AB-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*

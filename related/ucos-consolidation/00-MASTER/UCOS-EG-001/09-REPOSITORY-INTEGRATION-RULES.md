# 09 — Repository Integration Rules

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define the rules by which an admitted implementation integrates into the repository (UKB / registries / twin / knowledge graph) — the CG-03/CG-04 dimension in operational detail. Consumes UCIC-001 Stages 11–13 and the guard/`ukb` apparatus; adds no new mechanism.

## 1. Integration Rules (RI)

| # | Rule | Enforcement | Evidence |
|---|---|---|---|
| RI-1 | Exactly **one canonical home** per implementation (Knowledge Once) | UKB; CG-04 | duplicate-freedom check |
| RI-2 | Registration is via **REG-AUTO-001** (artifact/page/certification/lineage registries) | UCIC Stage 13 | registry diff |
| RI-3 | `ukb validate` PASS (structural/referential/append-only) | UCIC Stage 11 | validate log |
| RI-4 | `ukb enforce` PASS (registered = eligible; 0 unregistered/unclassified/invalid) | UCIC Stage 13 | enforce log |
| RI-5 | Guard integrity 10/10 CERTIFIED + **zero drift** | `register.sh --guard` | guard report |
| RI-6 | Digital Twin (`control-tower.json`) synchronized to post-impl reality | UCIC Stage 12 | twin regeneration |
| RI-7 | Knowledge Graph edges added; No-Orphan closed | UCIC Stage 11; MCP-006 | relationships diff |
| RI-8 | Additive-only: **zero writes** to `engine/**`, `platform/**`, `00-SOURCE/**`, `99-FREEZE/**`, frozen bands, `00-BOOK/**` source | CG-01; UCIC Stage 4 | forbidden-path scan |
| RI-9 | Operational memory (`00-MASTER/`) excluded from corpus (UCOS-RECON-C1) | config exclusion | enforce scope |
| RI-10 | Source never split from its REG-AUTO projections (atomic realize+sync) | UCIC Stages 4/11–13 | commit structure |

## 2. Integration Sequence (consumed from UCIC-001)

```
CERTIFIED (Stage 10)
  → Stage 11 Repository Intelligence Update (ukb build; validate; No-Orphan)
  → Stage 12 Digital Twin Update (control-tower)
  → Stage 13 Registry Update (REG-AUTO; ukb enforce)
  → Stage 14 Commit Readiness  →  EG ADMISSION (doc 08)  →  enters Repository Truth
```

## 3. Fail-Closed Integration

- Any of RI-3/RI-4/RI-5 failing ⇒ integration incomplete ⇒ not admitted (doc 08 A-6).
- A forbidden-path write (RI-8) ⇒ non-recoverable ⇒ rollback (UCIC Output 4); frozen artifacts are never mutated.
- Drift (guard ≠ zero) ⇒ DENY until reconciled.

## 4. Single-Registry / Single-Truth Preservation

Integration writes only to UKB and its derived projections (the single canonical registry). It creates no competing registry. UMA registries (once instantiated) are measurement-control, explicitly distinct from the canonical registry (AB-001 doc 10 §4; UMA doc 10 §4) — integration does not conflate them.

## 5. Determination

**REPOSITORY INTEGRATION RULES ARE DEFINED (RI-1…RI-10, fail-closed).** They govern how an admitted implementation enters UKB via the existing UCIC/REG-AUTO/guard apparatus, preserving Knowledge Once, single registry, additive-only, and zero-drift — adding no new mechanism.

*END — 09 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*

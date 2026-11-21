# 05 — CANONICAL INTEGRATION PLAN

> **Mission:** Context Assimilation · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY PLAN. **No file modifications are performed.** No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is ABSOLUTE. This plan specifies *what would be integrated where*; it does not execute any change.

---

## 1. Plan scope

For every required repository modification, specify: **Existing file · Section · Required integration · Reason · Dependencies.** Modifications are deferred to a future authorized (write-enabled) mission; this artifact is the plan only.

---

## 2. Integration plan — REUSE (reference only, no content change)

These decisions are already Repository Truth; integration = confirm the reference. **No modification required.**

| Decision | Existing file (owner) | Action |
|---|---|---|
| Universe model | `00-CEP/STAGE-02-S2-03-UNIVERSE-FOUNDATION-BINDING.md` | reference as-is |
| Registry-first | `00-CEP/STAGE-02-S2-02-REGISTRY-FEDERATION-ARCHITECTURE.md` | reference as-is |
| Canonical Ownership model | `00-MASTER/RA-003/03-KNOWLEDGE-ONCE-CERTIFICATION.md` | reference as-is |
| Platform Blueprint | `06-IMPLEMENTATION/EC2-EPIC-006-BLUEPRINT-CATALOG-IMPLEMENTATION.md` | reference as-is |
| Registry as institutional memory | `00-BOOK/MASTER-BOOK/UMB-010-LINEAGE-ARCHITECTURE.md` | reference as-is |
| Universal composition architecture | `09-PLATFORM/PLATFORM-010-UNIVERSAL-PLATFORM-COMPOSITION-ARCHITECTURE.md` | reference as-is |

---

## 3. Integration plan — EXTEND (append a section to an existing owner)

| # | Existing file | Section to add | Required integration | Reason | Dependencies |
|---|---|---|---|---|---|
| E1 | `09-PLATFORM/PLATFORM-005-UNIVERSAL-PLATFORM-META-MODEL.md` | "Meta-Platform Layer" | record the Meta-Platform architecture as the meta-layer of the platform meta-model | Meta-Platform is the meta-facet of an owned model; avoid parallel artifact | METACLASS; PLATFORM-001 |
| E2 | `09-PLATFORM/PLATFORM-010-UNIVERSAL-PLATFORM-COMPOSITION-ARCHITECTURE.md` | "Platform Builder" + "Declarative Composition" | record builder + declarative-composition semantics within composition | builder/declarative are composition facets | UCOS-Ω∞-UNIVERSAL-COMPILER; APPLICATION-FACTORY |
| E3 | `06-IMPLEMENTATION/EC2-EPIC-006-BLUEPRINT-CATALOG-IMPLEMENTATION.md` | "Blueprint-Driven Platform Composition" | bind blueprints → platform composition | blueprint owner extends to composition trigger | PLATFORM-010 |
| E4 | `06-IMPLEMENTATION/UCOS-Ω∞-FOUNDATION-ARCHITECTURE.md` | "Foundation Composition" | record foundation-composition decision | foundation owner | PLATFORM-010 |
| E5 | `00-MASTER/UCOS-USIS-WAVE1/01-WAVE1-CONTEXT-ASSIMILATION.md` | "Constitutional Reuse Gate" | formalize Reuse Gate as a facet of the Context Assimilation Gate | avoid parallel gate | CEP-001/005 |
| E6 | `09-IMPLEMENTATION-SEQUENCE-DETERMINATION.md` (+ IMG-001/IEC-001) | "Sequence Refinement" | record refined implementation sequence | sequence owner | IMG-001; IEC-001 |

*Section names are indicative; the write-enabled mission selects exact headings under each owner's existing structure.*

---

## 4. Integration plan — NEW (only where unowned)

| # | New artifact (candidate) | Precondition | Required integration | Reason | Dependencies |
|---|---|---|---|---|---|
| N1 | **Nucleus model** — candidate location `06-IMPLEMENTATION/` or ARCH family, ID to be assigned by registry | **First** confirm Nucleus is NOT a rename of Universe (S2-03) / Foundation (IMP-001). If it is → convert N1 to EXTEND. | author the single canonical Nucleus artifact + register it (Registry First) | GAP-1: no owner exists | Universe (S2-03); Foundation (IMP-001); METACLASS |
| N2 | **Nucleus ↔ Universe ownership binding** — typed REFERENCE, not a standalone doc | **After** N1 | express ownership relation as a typed cross-reference | GAP-2 dependent | N1; S2-03 |

**Constitutional guard:** N1/N2 are authored **only** if the Reuse-First check confirms no existing owner. If the Nucleus reduces to an existing concept, both collapse to EXTEND (E-series) and NEW count → 0.

---

## 5. Integration sequencing (deterministic)

```
Step 0  Reuse-First adjudication of Nucleus (is it Universe/Foundation rename?)
          ├─ YES → all decisions become REUSE/EXTEND; NEW = 0
          └─ NO  → proceed with N1 then N2
Step 1  REUSE confirmations (§2)         — no change
Step 2  EXTEND sections E1…E6 (§3)        — append to owners
Step 3  NEW N1 (Nucleus), then N2 binding — only if Step 0 = NO
Step 4  Registry update (register any new/extended artifact) — Registry First
Step 5  Re-run closure engine → regenerate Repository Truth → re-verify invariants 0
```

---

## 6. Registry-first & Knowledge-Once compliance

- Every EXTEND/NEW is registered in the appropriate MASTER-REGISTRY / `00-BOOK/REGISTRIES/` (Registry First).
- No content is duplicated across owners; each decision lands in exactly one owner (Knowledge Once).
- Post-integration, closure must still report `gap_total=0` and all invariants 0 (no regression).

---

## 7. Plan attestation

This is a **plan only**. No file was created, modified, moved, or deleted. Execution requires a separate, explicitly write-authorized mission. The plan minimizes change: **6 REUSE (no-op), 6 EXTEND, at most 2 NEW (conditional on the Nucleus adjudication).**

---
*End of 05-CANONICAL-INTEGRATION-PLAN.md*

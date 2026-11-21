# UAP-001: Universal Agnostic Architecture Principle

| Field | Value |
|-------|-------|
| Status | **DESIGN PRINCIPLE — not a certification, not a decision in the `CEP-002 Article 28` implementation-evidence sense** |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCOS-ARCHITECTURAL-OPENNESS-ASSESSMENT-REPORT.md`, `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` |
| Supersedes | none |

## Why this is not registered as a `CEP-002 Article 28` decision

Every other `adr/00NN` document this session (`0015`–`0020`) recorded a decision that was *implemented and independently verified* — each carries a `DEC-ADR-NNNN` entry in `ucda-decisions.json` with a real disposition (`IMPLEMENTED`, backed by tests). This document is different in kind: it states a **direction**, not a **change**. Giving it a decision-register entry with a disposition would imply it has, or requires, executable evidence of its own — which would misrepresent what it is. It is filed under `adr/` for discoverability alongside the decisions it will inform, not because it is one.

## Context

`UCOS-ARCHITECTURAL-OPENNESS-ASSESSMENT-REPORT.md` and its roadmap found real, mixed evidence: several dimensions (entity, context, relationship, and — scoped to `engine/uckp` — storage technology) are genuinely `CERTIFIED` open, by executable test. Others (`API/Communication`, `UI/Experience`) have no implementation surface to evaluate at all, and several classifications (`Facet`, `KnowledgeCapability`, `RelationType`/`KnowledgeKind`) are *correctly* closed, representing governed invariants rather than gaps. No single, blanket "the architecture is agnostic" claim was, or could honestly be, established — that would be exactly the fabricated certainty this session has repeatedly corrected for.

What the evidence *does* support is that where an abstraction boundary was actually built and tested (`engine/uckp/persistence.py`'s `PersistenceAdapter`), it worked, was reused across multiple technologies, and cost nothing beyond the boundary itself. That is worth stating as a preference for future work — not as a retroactive claim about the whole codebase today.

## Statement

**"UCOS Ω∞ SHALL prefer replaceable expressions over permanent implementation dependencies."**

## Explicit boundary

**This principle defines architectural direction. Individual agnostic properties require independent executable evidence.**

Concretely, this means:
- A future decision to build a new subsystem should default to asking "does this need to be swappable," the way `engine/uckp/persistence.py` already did — not because agnosticism is free, but because asking the question is.
- This principle does **not** retroactively certify any dimension the assessment report classified as `SUPPORTED`, `UNKNOWN`, or `GAP`. Those classifications stand exactly as recorded until a specific test proves otherwise.
- This principle does **not** license building an abstraction merely to satisfy a checklist (per the roadmap's Phase 2/3 findings: `ContextRegistry`, the UCDA decision register, the identity ledger, and governance artifacts were each found to have a *different* real need than storage-technology swappability, and forcing `PersistenceAdapter` onto them would not have served that need).
- This principle does **not** override an already-adjudicated, correctly-closed governed invariant (`Facet`, `KnowledgeCapability`, `RelationType`/`KnowledgeKind` — see the roadmap's Phase 6). "Prefer replaceable expressions" is not "prefer open enumerations everywhere"; a closed vocabulary that protects a real invariant (constitutional amendment discipline, knowledge-identity decidability) is not a violation of this principle — it is a case where a permanent-by-design boundary was the correct choice, and this principle does not contest that judgment.

## Consequences

Positive: future architectural decisions have a stated, named preference to weigh against, reducing the chance of accidental technology lock-in of the kind found in `KnowledgeStore`.

Neutral: no code changes, no new authority, no new store. This document changes no test's pass/fail state.

Negative: a principle with no enforcement mechanism can be ignored without consequence. This is disclosed rather than hidden — no gate, invariant, or certification currently checks conformance to this statement, and none is created by this document.

Reversible: trivially — this is a preference statement, not a constitutional amendment. Superseding it requires only a new document stating the change, not an implementation rollback.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — does not contest `UCRD-001`'s facet-closure adjudication or any other standing decision.
- [x] Rollback / migration path recorded (CC-04) — see Consequences; nothing to roll back.
- [x] Traceability links to affected artifacts recorded (CC-05) — `UCOS-ARCHITECTURAL-OPENNESS-ASSESSMENT-REPORT.md`, `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md`.
- [x] No secret material embedded (SEC-04).

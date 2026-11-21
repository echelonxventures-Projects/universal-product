# USIS-016 — Evidence Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-016 (Evidence Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Evidence (USIS-004 tier 22) |
| CANONICAL HOME (on realization) | `15-…/17-EVIDENCE/` (+ Evidence Registry; `data/_evidence/<CAP-ID>/`) |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-015 (Certification) |
| DEPENDS-ON | USIS-015 (Certification) · UCIC-001 (Output-5) · USIS-001 (LAW USIS-07) · TRACK-001 (referenced) |
| CONSTITUTIONAL ANCHOR | LAW USIS-07 (explainable provenance); TRACK-001 (fail-closed evidence); UCIC-001 Output-5 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001 + UCIC-001 + TRACK-001. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Evidence** tier — how every inference, analytic, learned change, decision, and self-evolution step in the substrate produces a durable, provenance-bearing, fail-closed evidence artifact. This blueprint specifies the evidence node shape and the traces/provenance model, binding UCIC-001 Output-5 and TRACK-001 to the substrate's explanation obligation (LAW USIS-07).

---

## 1 — Purpose
The Evidence tier is the terminal proof-bearing tier of the meta-model realization chain (tier 22). It makes the substrate's claims verifiable rather than asserted: absence of a required evidence artifact means NOT-DONE (TRACK-001). It carries the provenance and explanation traces that satisfy LAW USIS-07.

## 2 — Responsibilities
- Own the **evidence node shape**: a durable artifact carrying provenance (origin, authority, lineage) and explanation for a substrate action.
- Define the **trace model**: inference traces, analytics traces, learned-change traces, decision traces, self-evolution gate outcomes.
- Bind UCIC-001 Output-5 (universal evidence model) as the minimum evidence set every capability produces.
- Enforce **fail-closed evidence** (TRACK-001): no self-attestation substitutes for a physical evidence artifact.

## 3 — Boundaries
- **Owns:** science-intelligence evidence node shape, trace/provenance model, evidence-store homing contract.
- **Does not own:** the validation verdict (USIS-014), the certification decision (USIS-015), the traceability graph engine (MCP-006 — referenced), or the universal evidence tooling (UCIC — referenced).
- Evidence *records*; it renders no verdict or decision.

## 4 — Interfaces
Exposes: `remember · prove · explain · audit · observe · describe · discover`. Every substrate action (reason/analyze/learn/decide/self-evolve) emits a trace to the evidence store; consumers (validation, certification, audit) read evidence by contract.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` USIS-015 (Certification, whose decisions it records) and UCIC-001 Output-5 + TRACK-001. Evidence is the terminal Wave-2 realization tier; the Governance and Lifecycle tiers span it but are not Wave-2 blueprints.

## 6 — Registry model
Evidence artifacts are rows in the **Evidence Registry** (target #8), homed under `17-EVIDENCE/` and `data/_evidence/<CAP-ID>/`. Append-only, immutable once written (authoritative history is never mutated on rollback — UCIC Output-4 invariant). Provenance edges resolve into the Dependency and Traceability registries.

## 7 — Relationship model
Parent edge → Certification (USIS-015). Reference edges → MCP-006 traceability graph (Vision→Certification chain), Knowledge Object (grounded provenance), and the specific action tiers (Algorithm/Model/Runtime) that emitted each trace. Evidence closes the loop back to the capability (USIS-006).

## 8 — Lifecycle
Evidence is produced across UCIC-001 Stages 2–13 and consolidated at Stage 9 (Gate VALIDATED) and Stage 10 (certification record). An evidence artifact follows **EMITTED → CONSOLIDATED → REGISTERED → RETAINED (immutable)**. Evidence is preserved across all failures/rollbacks (fail-closed audit trail).

## 9 — Validation model
Referenced to USIS-014: an evidence bundle is valid only if every required artifact (UCIC Output-5 subset for the capability) physically exists and carries provenance + explanation (LAW USIS-07). Missing evidence ⇒ the dependent verdict/decision is fail-closed NOT-DONE.

## 10 — Certification model
Referenced to USIS-015: the certification decision is itself an evidence artifact; certification cannot be issued without the complete evidence bundle it references.

## 11 — Evidence model
This tier *is* the evidence model for the substrate (UCIC Output-5 specialized): dependency-verification, source diff, static/dynamic/test/coverage reports, determinism verification, reasoning/analytics/learning traces, certification record, repository-intelligence + twin + registry updates, traceability edges, execution log.

## 12 — Failure model
Per UCIC Output-4. Absence of any required evidence artifact ⇒ NOT-DONE (TRACK-001) ⇒ the dependent stage cannot pass. Any attempt to mutate authoritative/certified evidence on rollback ⇒ invariant violation ⇒ rejected (evidence is append-only and preserved).

## 13 — Reuse model
Reuse-First (LAW USIS-02): the UCIC-001 Output-5 evidence model, the MCP-006 traceability graph, and the platform evidence store are **referenced**, never re-implemented. This tier adds only the science-intelligence trace/provenance specialization (inference/analytics/learning/self-evolution).

## 14 — Non-goals
- Not the validation verdict (USIS-014) nor the certification decision (USIS-015).
- Not the traceability graph engine (MCP-006).
- Names no storage technology in the architecture (LAW USIS-04; current bindings live in UCIC/platform).

*END — USIS-016 · EVIDENCE ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*

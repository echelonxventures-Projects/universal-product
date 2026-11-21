# EC2-EPIC-007-DETERMINATION — Generation Requests

| Field | Value |
|-------|-------|
| ARTIFACT ID | EC2-EPIC-007-DETERMINATION |
| ARTIFACT | EC-2 Platform Program — Generation Requests Execution-Package Determination |
| PROGRAM | UCOS EC-2 Platform Realization Program |
| EPIC | EC2-EPIC-007 — Generation Requests (Wave 3; PC-06 submission + PC-07 dispatch) |
| CLASSIFICATION | Repository-derived execution-package determination — evidence-only, authority-neutral |
| STATUS | **IMPLEMENTATION AUTHORIZED** |
| BRANCH | `governance-reconciliation` |
| BASELINE COMMIT | `fc12acce61e82f2da07c2ba26442ece4c26782b1` |
| HELD AUTHORITY | ENGINEERING-EXECUTION-ONLY |

*This artifact determines the execution package for `EC2-EPIC-007`. It is subordinate to the frozen corpus (`00-BOOK/`, `00-SOURCE/`, `99-FREEZE/` — read-only, DP-03), the EC-2 Platform Realization Program, and every prior governance/execution determination. It asserts no constitutional finality; the external gates EC-1…EC-6 remain open.*

---

## 1. SCOPE DETERMINATION

`EC2-EPIC-007` realizes Program **Surface #8 Generation Requests** as the UCOS Platform **Generation Request Runtime** (`platform/generation/`, L3 Application). The capability becomes the **canonical governed entry point for all generation activity inside EC-2**: the authoritative handoff between the user interface, the generation request, and the certified EC-1 Execution Runtime.

The implementation establishes the complete request lifecycle from submission through execution dispatch while preserving all existing governance, registration, provenance, auditability, traceability, classification, observability, and certification requirements.

## 2. DEPENDENCY CLOSURE

| Declared dependency | Status | Evidence |
|---------------------|--------|----------|
| EC2-EPIC-006 Blueprint Catalog | COMPLETE | `platform/blueprints/EC2-EPIC-006-COMPLETION-REPORT.md` ("✅ COMPLETE") |
| EC2-EPIC-005 Project Management | COMPLETE | `platform/projects/EC2-EPIC-005-COMPLETION-REPORT.md` |
| EC2-EPIC-004 Workspace | COMPLETE | `platform/workspace/EC2-EPIC-004-COMPLETION-REPORT.md` |
| EC2-EPIC-002 Identity & Access | COMPLETE/CERTIFIED | tag `EC2-EPIC-002-CERTIFIED` |
| EC2-EPIC-013 Observability | COMPLETE | `platform/observability/EC2-EPIC-013-COMPLETION-REPORT.md` |
| EC2-EPIC-001 Foundation & API | COMPLETE | `platform/foundation/EC2-EPIC-001-COMPLETION-REPORT.md` |
| EC-1 factory/compiler/runtime/determinism | CERTIFIED (read-only, by `ContractRef`) | `ENGINE_CONTRACTS` in `platform/foundation/contracts.py` |

Dependency set fully closed. The GOV-002 §6 **link-4** obligation was discharged in EPIC-006 (`05-GENERATION → blueprint`); EPIC-007 **continues** that trace edge through the Request node (`blueprint → request → implementation`) — it does not reopen it.

## 3. REUSE FINDINGS (mandatory execution rules)

1. **No new capability group.** Authorization binds to the pre-existing `CapabilityGroup.GENERATION_REQUESTS` (§3.2 matrix index 6). No new authority, role, permission, or authorization logic.
2. **No new classification model.** The generation `family` is the frozen `BlueprintFamily` (the six `05-GENERATION` families), recorded read-only.
3. **No parallel framework / no duplicate registry / no alternative identity system.** The runtime composes the certified `AuthorizationService`, `WorkspaceRegistry`, `ObservabilityService`, `EventBus`, `HealthRegistry`, and Foundation `content_hash`/`ContractRef` machinery.
4. **No governance bypass.** Every governed action is fail-closed and published onto the Foundation event bus (captured as append-only L8 audit, PC-16).
5. **No EC-1 modification, no live engine import (P10).** Dispatch binds to `engine.factory.generate` / `engine.compiler.compile` / `engine.runtime.assemble` / `engine.determinism.reproduce` **by `ContractRef` only**.
6. **No frozen-corpus write (DP-03).** In-memory, deterministic, no server, no socket, no file writes.

## 4. DOMAIN DETERMINATION

Aggregate: **`GenerationRequest`** (`UCOS-GREQ-*`, content-addressed from slug + workspace + blueprint_ref + submitted_tick). Establishes: identity, ownership (`owner_subject`), provenance (`blueprint_ref` + `submitted_tick` + link-4 `RequestProvenance`), timestamps (logical ticks), classification (`family`), lifecycle state (`RequestStatus`), execution state (`ExecutionState`, derived), audit metadata (append-only `RequestEvent` log + governed events), and governance metadata (published contracts + capability group).

## 5. LIFECYCLE DETERMINATION

Deterministic state machine (`platform/generation/lifecycle.py`):

```
SUBMITTED  -> VALIDATING -> APPROVED -> QUEUED -> DISPATCHED -> RUNNING -> COMPLETED
VALIDATING -> FAILED
DISPATCHED -> RUNNING | FAILED
RUNNING    -> COMPLETED | FAILED
(SUBMITTED | VALIDATING | APPROVED | QUEUED | DISPATCHED) -> CANCELLED
COMPLETED · FAILED · CANCELLED = terminal
```

Transition rules, guard conditions, state validation, audit recording (append-only `RequestEvent`), and event generation (`generation.request.*`) are implemented and fail-closed.

## 6. DECOMPOSITION (EC2-TASK-000109…000118)

`errors → metadata → contracts → lifecycle → registry → dispatch → provenance → status → context → search → health → service → bootstrap → __init__`.

## 7. DISPATCH BOUNDARY DETERMINATION (§7)

The Generation Request is the sole authoritative handoff point:

```
User Interface → Generation Request → Execution Runtime
```

`GenerationRequestService.dispatch_request` is the **only** path that transitions a request to `DISPATCHED`, and it always records an immutable `DispatchRecord` (`UCOS-GDSP-*`) bound to the certified EC-1 execution contracts by reference. The `generation-request-dispatch-integrity` critical health check makes "no runtime bypass path" machine-checkable (a request that reached the runtime without a recorded dispatch drives UNHEALTHY).

## 8. VERDICT

**READY — IMPLEMENTATION AUTHORIZED.** All readiness conditions met: prerequisites complete, dependencies closed, architecture available (contract §2.1 #8, PC-06/PC-07, §4.3, §5), governance in force (GOV-004 lane + UCOS-EXEC-001 admission), controls operative (CI, determinism gate, TRACK-001, ≥90% coverage gate), realization template proven (six prior additive `platform/**` runtimes).

**END OF ARTIFACT — EC2-EPIC-007-DETERMINATION · IMPLEMENTATION AUTHORIZED · EVIDENCE-DERIVED · AUTHORITY-NEUTRAL**

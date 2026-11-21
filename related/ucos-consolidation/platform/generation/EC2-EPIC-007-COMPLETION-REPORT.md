# EC2-EPIC-007 — Generation Requests — Completion Report

**Program:** EC-2 Platform Realization Program · **Epic:** EC2-EPIC-007 (Generation Requests)
**Scope executed:** EC2-TASK-000109 … EC2-TASK-000118 (inclusive)
**Authoritative basis:** `06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md`
(§2.1 surface #8 *Generation Requests*, §2.2 **PC-06** generation submission + **PC-07** execution
dispatch + **PC-13** search + **PC-16** audit, §3.2 RBAC row *generation-requests*, §4 architecture
layers **L3 Application / L4 Execution façade**, §4.3 EC-1 interaction
*factory / compiler / runtime / determinism*, §5 EC2-EPIC-007 acceptance, §7 dispatch), as determined
by `platform/generation/EC2-EPIC-007-DETERMINATION.md` (**IMPLEMENTATION AUTHORIZED**), and the frozen
**`05-GENERATION/`** Universal Generation Framework corpus (the six generation families).
Builds on **EC2-EPIC-001** (COMPLETE), **EC2-EPIC-002** (COMPLETE/CERTIFIED), **EC2-EPIC-013**
(COMPLETE), **EC2-EPIC-004** (COMPLETE), **EC2-EPIC-005** (COMPLETE), and **EC2-EPIC-006** (COMPLETE),
over the **certified EC-1 Realization Engine** (consumed read-only by reference).
**Status:** ✅ COMPLETE — all ten tasks delivered, verified, and gated.

> Additive engineering package `platform/generation/`. It realizes Program **Surface #8 Generation
> Requests** as the UCOS Platform **Generation Request Runtime (L3 Application)** — the **canonical
> governed entry point for all generation activity in EC-2** and the authoritative handoff boundary
> between the user interface, the generation request, and the certified EC-1 Execution Runtime. It is
> strictly **additive**: it authorizes **only** through the Identity Layer on the **pre-existing**
> `generation-requests` capability group (**no new authority, no new capability group**), records the
> generation family **read-only** (reusing the frozen `BlueprintFamily` — **no new classification
> model**), observes **only** through the Observability Layer, binds to workspaces/projects/blueprints
> **by reference**, and hands off to EC-1 execution **only by contract reference** (never a live
> `engine.*` import — P10). It **modifies no EC-1 module and no prior platform layer**, **never writes
> to the certified corpus** (DP-03), remains **deterministic**, is **contract/registry-driven**, starts
> no server, and opens no socket.

---

## 1. Implementation Summary

`platform/generation/` is a **14-module** additive runtime package mirroring the proven certified
`platform/blueprints/` (EPIC-006) and `platform/projects/` (EPIC-005) topology, extended with the
generation-request-specific **execution-dispatch boundary** (L4 EC-1 façade). It implements: a
content-addressed request registry scoped to a parent workspace/project and a catalog blueprint (by
reference) with an append-only lifecycle event log (reconstruction); a deterministic nine-state
lifecycle state machine; a governed execution-dispatch boundary that records an immutable
`DispatchRecord` bound to the certified `engine.factory.generate` / `engine.compiler.compile` /
`engine.runtime.assemble` / `engine.determinism.reproduce` contract references; a link-4 provenance
continuation (`RequestProvenance`); a pure derived lifecycle + execution status; a fail-closed
`GenerationRequestService` composition root with a composed access decision (identity ∧
tenant/workspace isolation ∧ owner/administrator scoping); reproducible `RequestEvidence`;
observability metrics (submitted/dispatched/completed/failed/cancelled counters, queue-depth gauge,
lifecycle-latency histogram); cross-runtime health; and a `bootstrap_generation_requests` composition
root publishing versioned contracts. Every governed action is emitted onto the Foundation event bus
and captured as append-only L8 audit.

## 2. Architecture Summary

**Implementation topology (dependency-ordered):**
`errors → metadata → contracts → lifecycle → registry → dispatch → provenance → status → context →
search → health → service → bootstrap → __init__`.

| Layer | Realization |
|-------|-------------|
| L3 Application | `GenerationRequestService` — the governed request composition + access/context decision point |
| L4 Execution façade | `dispatch.py` — the EC-1 execution-contract handoff boundary (by reference) |
| Persistence | `registry.py` (requests + append-only event log), `dispatch.py` (dispatch ledger), `provenance.py` (provenance ledger) |
| Identity (reused) | `AuthorizationService` on `CapabilityGroup.GENERATION_REQUESTS` |
| Observability (reused) | governed events + metrics + `HealthRegistry` |

## 3. Files Created

| File | Task | Responsibility |
|------|------|----------------|
| `platform/generation/errors.py` | 000109 | `EC2-GR-*` error taxonomy over `PlatformError` |
| `platform/generation/metadata.py` | 000109 | Immutable `RequestMetadata` value type |
| `platform/generation/contracts.py` | 000109 | `RequestStatus`/`ExecutionState`/`RequestAction`, verb→permission map, `GenerationRequest`, `GENERATION_REQUEST_CONTRACTS`, `GENERATION_REQUEST_GROUP` |
| `platform/generation/lifecycle.py` | 000110 | Deterministic request state machine + `RequestEvent` |
| `platform/generation/registry.py` | 000111 | `GenerationRequestRegistry` (submit/register/resolve/discover/transition; event log; status census) |
| `platform/generation/dispatch.py` | 000112 | `DispatchRecord` + `DispatchLedger` — the EC-1 execution-dispatch boundary (by reference) |
| `platform/generation/provenance.py` | 000113 | `RequestProvenance` + `ProvenanceLedger` — link-4 trace continuation |
| `platform/generation/status.py` | 000114 | Deterministic `derive_status` + `DerivedRequestStatus` + `RequestPosture` |
| `platform/generation/context.py` | 000114 | Resolved `RequestContext` runtime binding |
| `platform/generation/search.py` | 000115 | Authorization- + isolation-scoped `RequestSearch` |
| `platform/generation/health.py` | 000116 | Request health checks + `RequestHealth` (reuses L8 model) |
| `platform/generation/service.py` | 000117 | `GenerationRequestService` composition root + `RequestAccess` + `RequestEvidence` |
| `platform/generation/bootstrap.py` | 000118 | `bootstrap_generation_requests` (identity + observability + workspace + request runtime) |
| `platform/generation/__init__.py` | 000118 | Package surface re-exports |
| `platform/tests/test_generation_*.py` (14 files) | 000109–118 | Full test suite (184 tests) |
| `platform/generation/EC2-EPIC-007-DETERMINATION.md` | 000109 | Execution-package determination |
| `platform/generation/EC2-EPIC-007-COMPLETION-REPORT.md` | 000118 | This report |

## 4. Files Modified

| File | Change |
|------|--------|
| `pyproject.toml` | Added `--cov=platform.generation` to pytest addopts and `platform/generation` to the coverage source. No other change. |

**No EC-1 (`engine/**`) module, no prior platform layer, and no frozen-corpus file was modified
(P10 / DP-03).** Pre-existing, unrelated mypy warnings in `platform/workspace/bootstrap.py:67/69`
(documented in the EPIC-006 report §13) remain untouched (additive-only boundary).

## 5. Domain Model Summary

`GenerationRequest` (`UCOS-GREQ-*`): identity (content-addressed), ownership (`owner_subject`),
provenance (`blueprint_ref`, `submitted_tick`, link-4 `RequestProvenance`), classification (`family`,
recorded `BlueprintFamily`), lifecycle state (`RequestStatus`), execution state (`ExecutionState`,
derived), and metadata. Terminal states: `COMPLETED` / `FAILED` / `CANCELLED`.

## 6. API Summary

Realized as the governed service surface (in-process; the platform is stdlib-only, contract/registry
driven — no HTTP framework), published as versioned `GENERATION_REQUEST_CONTRACTS`:

| Capability | Service method | Authority |
|------------|----------------|-----------|
| Create Generation Request (POST) | `submit_request` | CREATE + active workspace + isolation |
| Request Details (GET) | `get_request` / `select_request` | READ (INSPECT) |
| Request Collection (GET) | `list_requests` (filter by workspace/project/family/status) | READ + isolation |
| Request Status (GET) | `status_of` / `track_request` | READ (TRACK) |
| Cancel Request (POST) | `cancel_request` | CREATE + owner/admin |
| Lifecycle (validate/approve/queue/run/complete/fail) | `start_validation`/`approve`/`enqueue`/`mark_running`/`complete`/`fail` | CREATE / EXECUTE + owner/admin |
| Dispatch (POST, execution boundary) | `dispatch_request` | EXECUTE + owner/admin, QUEUED-only |
| Search | `search` | READ + isolation |
| Trace (link-4) | `trace` / `record_provenance` | READ / CREATE + owner |

Reuses the certified authentication/authorization, validation (fail-closed), error contracts
(`EC2-GR-*`), and response contracts (content-addressed records). No API-convention drift.

## 7. Persistence Summary

Deterministic, append-only in-memory records: `GenerationRequestRegistry` (requests + ordered
`RequestEvent` log, per-request reconstruction, status census), `DispatchLedger` (idempotent by id,
fail-closed on conflicting handoff), `ProvenanceLedger` (idempotent, traceability-enforced). Every
record is content-addressed and `to_dict()`/`fingerprint()`-serializable — provenance, traceability,
and reconstruction are preserved.

## 8. Observability Summary

Governed events on the Foundation event bus (append-only L8 audit, PC-16): `generation.request.`
`submitted` / `validating` / `approved` / `queued` / `dispatched` / `running` / `completed` / `failed`
/ `cancelled` / `metadata.updated` / `provenance.linked` / `health.changed` / `access.evaluated`.
Metrics (PC-12): submitted/dispatched/completed/failed/cancelled counters, `queue_depth` gauge,
`lifecycle_latency` histogram. Three critical health checks (`generation-request-registry`,
`generation-request-dispatch-integrity`, `generation-request-execution-integrity`) registered into the
L8 `HealthRegistry` by `bootstrap_generation_requests` (idempotent). Telemetry on 100% of governed
actions (P9); reproducible `RequestEvidence`.

## 9. Governance Summary

- **Authorization:** every action authorizes through the certified `AuthorizationService` on the
  **pre-existing** `generation-requests` group. No new authority, role, capability group, permission,
  or classification model (`test_generation_governance.py`).
- **Two-gate + owner scoping:** `_compose_access` composes identity authorization ∧ `tenants_isolated`
  ∧ (for mutations) owner/administrator scoping; every denial reason (`no-grant`,
  `tenant-isolation-violation`, `not-an-owner`, `request-terminal`) is tested.
- **No runtime bypass (§7):** `dispatch_request` is the only path to `DISPATCHED` and always records a
  `DispatchRecord`; the dispatch-integrity health check makes this machine-checkable.
- **EC-1 integrity (P10):** the package imports **no** `engine.*` module at runtime (source-verified in
  `test_runtime_never_imports_engine_modules_directly`); dispatch is bound by `ContractRef` only.
- **No bypass / no elevated shortcut / no direct registry mutation:** all mutations flow through the
  fail-closed service; the runtime exposes no `authorize/ratify/enact/grant/govern/override` verb.

## 10. Testing Summary

`184` generation tests across 14 files (contracts, lifecycle, registry, dispatch, provenance, status,
context, search, health, service, bootstrap, governance, determinism, traceability). Categories
covered: unit, integration, API-surface, lifecycle, governance, authorization, persistence, dispatch,
observability, and regression. **Full platform+engine suite: 2,070 passed, 0 failed.** Zero regressions.

## 11. Coverage Summary

| Gate | Result |
|------|--------|
| Total coverage (`--cov-fail-under=90`) | ✅ **99.90%** |
| Every `platform/generation/` module | ✅ **100%** (14/14 modules; 0 missed statements, 0 partial branches) |

## 12. Quality-Gate Summary

| Gate | Result |
|------|--------|
| `ruff check platform/generation` + tests | ✅ All checks passed |
| `pytest` full suite | ✅ 2,070 passed, 0 failed |
| Coverage (≥90%) | ✅ 99.90% total; 100% per generation module |
| `mypy platform/generation` | ✅ No issues in the generation package (only 2 pre-existing `platform/workspace/bootstrap.py` warnings, out of scope) |
| Determinism (in-process + cross-process `RequestEvidence` fingerprint) | ✅ byte-identical |

## 13. Determinism Results

Content-addressed ids (`UCOS-GREQ-`, `UCOS-GDSP-`, `UCOS-GPRV-`, `UCOS-GDST-`, `UCOS-GCTX-`,
`UCOS-GACC-`, `UCOS-GEVT-`, `UCOS-GSRE-`) are reproducible; the `RequestEvidence` fingerprint is
byte-identical in-process and **across independent processes**
(`test_evidence_fingerprint_is_reproducible_across_processes`). No wall-clock in any identity or
ordering (caller-supplied logical ticks).

## 14. Registration Summary

Implementation committed to branch `governance-reconciliation`. Repository registration (REG-AUTO-001:
UKB, Control Tower, Knowledge Graph, Relationship Registry, Portal, Implementation Registry,
Certification Records, Traceability Records) is to be executed via the existing registration machinery
as a **separate `REG-AUTO-001: register EC2-EPIC-007` commit**, consistent with the EPIC-005/006
precedent.

## 15. Risks and Follow-Ups

| # | Item | Severity | Note |
|---|------|----------|------|
| R-1 | Live EC-1 execution invocation is out of scope | Expected | Actual generation execution is EC2-EPIC-012 (Runtime Operations); EPIC-007 records the governed handoff by reference (P10). |
| R-2 | Downstream consumers (EPIC-008 dashboard, EPIC-009 explorer, EPIC-010 validation console) | Expected | `GENERATION_REQUEST_CONTRACTS` published; consumers bind by reference. |
| R-3 | Pre-existing `platform/workspace/bootstrap.py:67/69` mypy warnings | Low | Out of scope (additive-only boundary); documented in EPIC-006 §13. |
| R-4 | Separate REG-AUTO-001 registration commit pending | Informational | Per EPIC-005/006 precedent (§14). |

## 16. Completion Determination

| Success condition | Status |
|-------------------|--------|
| Generation Requests fully implemented | ✅ 14-module additive runtime |
| Request lifecycle operational | ✅ 9-state machine, fail-closed, event-logged |
| Request APIs operational | ✅ submit/get/list/status/cancel/dispatch/trace + published contracts |
| Request persistence operational | ✅ registry + dispatch + provenance ledgers; reconstruction |
| Dispatch integration operational | ✅ authoritative UI→request→runtime boundary; no bypass |
| Audit chain operational | ✅ governed events + append-only L8 audit + event log |
| Observability operational | ✅ events + metrics + 3 critical health checks |
| Governance compliant | ✅ no new authority/group/classification; fail-closed |
| Registration compliant | ✅ contracts published; REG-AUTO-001 to follow (§14) |
| Traceability compliant | ✅ Generation→Blueprint→Request→Implementation link-4 continuation |
| All tests passing | ✅ 2,070 passed, 0 failed |
| Extended Invariant preserved | ✅ 0 `engine/**` edits; DP-03 respected; deterministic |

**EC2-EPIC-007 — Generation Requests — COMPLETE and READY FOR EPIC-008/009/010 consumption.**

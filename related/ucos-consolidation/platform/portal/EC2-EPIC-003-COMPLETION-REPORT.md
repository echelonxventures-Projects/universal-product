# EC2-EPIC-003 — Portal & Navigation — Completion Report

**Program:** EC-2 Platform Realization Program · **Epic:** EC2-EPIC-003 (Portal & Navigation)
**Scope executed:** EC2-TASK-000073 · EC2-TASK-000074 · EC2-TASK-000075 · EC2-TASK-000076 ·
EC2-TASK-000077 · EC2-TASK-000078 · EC2-TASK-000079 · EC2-TASK-000080 (inclusive)
**Authoritative basis:** `06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md`
(§2.1 surface 1 *Portal*, §2.2 PC-01/PC-02/PC-12/PC-13/PC-16, §3.2 RBAC matrix, §4 architecture
layer **L1 Presentation**, §5 EC2-EPIC-003, §9 acceptance). Governed by the determination chain
`UCOS-GOV-004` → `UCOS-EXEC-001` → `UCOS-EXEC-002`. Builds on **EC2-EPIC-001 Platform Foundation**
(COMPLETE), **EC2-EPIC-002 Identity & Access** (COMPLETE/CERTIFIED), and **EC2-EPIC-013
Observability & Monitoring** (COMPLETE), over the **certified EC-1 Realization Engine**.
**Prerequisites (EXEC-002):** EPIC-001 + EPIC-002 — both **COMPLETE**.
**Status:** ✅ COMPLETE — all eight tasks delivered, verified, and gated.

> Additive engineering package `platform/portal/`. It implements the UCOS Platform
> **Portal & Navigation Layer (L1 Presentation)** — the primary authenticated entry point into
> the platform — as a strictly **additive** layer over the certified EC-1 engine and the EC-2
> Foundation, Identity, and Observability layers: it authenticates/authorizes **only** through the
> Identity Layer (no duplicate identity), observes **only** through the Observability Layer, and
> discovers **only** through the Foundation registries; it **modifies no EC-1 module and no prior
> platform layer**, **never writes to the certified corpus** (DP-03), remains **deterministic**, is
> **contract/registry-driven**, and **preserves all EC-1 certifications**. It is the deterministic
> presentation **model** — it starts no server and opens no socket.

---

## 1. Repository analysis summary (repository-first rule)

Before creating anything, the repository, EC-2 contracts, portal references, and the existing
identity/foundation/observability capabilities were inspected. Findings that governed the design:

| Inspection | Finding | Consequence |
|------------|---------|-------------|
| Program §2.1 / §4.1 | Portal is surface 1 / layer **L1 Presentation**; capabilities PC-01/02/12/13/14/16 | Portal is a consumer of prior layers; invents no governance |
| Program §3.2 | 16 capability-group rows; row 0 = *Portal / navigation* (all roles R except Integrator) | Navigation/routing derived from the §3.2 groups; Integrator is not admitted |
| Program §5 EC2-EPIC-003 | Acceptance: authenticated portal reachable · nav to all authorized surfaces · global search ≥4 entity types · accessibility checks pass | Directly encoded as acceptance tests |
| `platform/identity/` (L7) | `AuthorizationService` (session→principal→policy→decision), `CapabilityGroup`, fail-closed policy | Reused verbatim as the portal's sole access seam — **no duplicate identity** |
| `platform/observability/` (L8) | `ObservabilityService` (health endpoint G1, evidence, metric snapshot), event-bus governed-action capture | Reused for the portal's health/runtime/monitoring visibility |
| `platform/foundation/` (L4/L6) | `PlatformContext` (services, capabilities, event bus), content-addressed hashing, `ServiceDescriptor` | Reused for service discovery + capability access + deterministic ids |
| Prior epics' convention | additive package + `bootstrap_*` composition + append-only events + deterministic evidence + 100% coverage | Portal follows the identical discipline |

**No existing canon was duplicated and no governance/determination artifact was created.**

## 2. Portal architecture determination

The portal is realized as the deterministic L1 **model** composed onto a `PlatformContext`:

```
bootstrap_portal(PlatformContext)                          # composes the platform end to end
  ├── bootstrap_identity(context)      → AuthorizationService (L7)     # reused, not re-implemented
  ├── bootstrap_observability(context) → ObservabilityService (L8)     # reused, not re-implemented
  └── build_portal_service(...)        → PortalService (L1)
        ├── PortalAccessGateway   (TASK-000074)   # identity-integrated admission/authorization
        ├── NavigationModel       (TASK-000075)   # authorized surfaces by section + a11y report
        ├── Router                (TASK-000076)   # deterministic, fail-closed path→surface
        ├── WorkspaceSelector     (TASK-000077)   # portal→workspace handoff (authorization-gated)
        ├── ServiceDirectory      (TASK-000078)   # service discovery + capability access
        ├── ObservabilityView     (TASK-000078)   # health / runtime / monitoring visibility (gated)
        └── GlobalSearch          (TASK-000079)   # ≥4 entity kinds, authorization-scoped
  → publishes 7 portal contracts into the Foundation ServiceRegistry
  → emits portal.bootstrap.completed; every enter() emits portal.session.entered (observed, PC-16)
```

**Navigation is authorization-derived, not invented:** the 16 navigable `PortalSurface`s are
transcribed one-to-one from the §3.2 capability groups; a surface is visible iff the caller holds
READ on its group, resolved through the Identity Layer. Sections (`main`/`account`/`administration`/
`governance`/`observability`) directly realize the mission's Administration, Governance, and
Observability entry categories. All identities are content-addressed; sessions use a caller-supplied
logical clock (no wall-clock); every operation is fail-closed.

## 3. Files created

```
platform/portal/                                   (NEW package)
├── __init__.py                                    public API surface
├── errors.py                    TASK-000073        EC2-PORTAL-* taxonomy (roots in PlatformError)
├── contracts.py                 TASK-000073        PortalSection/PortalSurface/EntityKind + PORTAL_CONTRACTS
├── access.py                    TASK-000074        PortalAccessGateway / PortalAdmission (identity integration)
├── navigation.py                TASK-000075        NavigationModel / Navigation / AccessibilityReport
├── routing.py                   TASK-000076        Route / Router (deterministic, fail-closed)
├── workspace.py                 TASK-000077        WorkspaceSelector / WorkspaceHandoff
├── discovery.py                 TASK-000078        ServiceDirectory + ObservabilityView
├── search.py                    TASK-000079        SearchEntity/Index / GlobalSearch (≥4 kinds, PC-13)
├── service.py                   TASK-000080        PortalService / PortalView / PortalEvidence / bootstrap_portal
└── EC2-EPIC-003-COMPLETION-REPORT.md              this report

platform/tests/                                    (EXTENDED test package)
├── test_portal_contracts.py · test_portal_access.py · test_portal_navigation.py
├── test_portal_routing.py · test_portal_workspace.py · test_portal_discovery.py
├── test_portal_search.py · test_portal_service.py
```

## 4. Files modified

```
pyproject.toml   (MODIFIED)  added platform.portal to --cov and to [tool.coverage.run] source
```

No file under `engine/`, `platform/foundation/`, `platform/identity/`, `platform/observability/`,
`00-BOOK/`, `00-SOURCE/`, `99-FREEZE/`, or `02-MASTER/` was created or modified. The portal performs
**no filesystem writes** at all.

## 5. Tests created

110 tests across 8 files: contracts/vocabulary (11), access gateway (12), navigation + accessibility
(13), routing (13), workspace handoff (7), discovery + observability integration (13), global search
(12), and the composed shell + bootstrap (29).

## 6. Test results

`python -m pytest` (full workspace, coverage gate `--cov-fail-under=90`):

```
841 passed
Required test coverage of 90% reached. Total coverage: 99.81%
```

The 841 includes the full EC-1 + certification + Platform Foundation + Identity + Observability
suites (731 pre-portal) — all remain green, so **EC-1 integrity is preserved (P10)**.

## 7. Coverage results

**100% coverage on every `platform/portal` module:**

```
platform/portal/__init__.py      100%      platform/portal/navigation.py    100%
platform/portal/access.py        100%      platform/portal/routing.py       100%
platform/portal/contracts.py     100%      platform/portal/search.py        100%
platform/portal/discovery.py     100%      platform/portal/service.py       100%
platform/portal/errors.py        100%      platform/portal/workspace.py     100%
```

**Lint (ruff):** `ruff check engine platform` → **All checks passed!**
**Determinism:** the portal evidence fingerprint is identical across two independent processes
(`5c1580d46f1ddda5…`); every id is content-addressed and sessions use a logical clock.

## 8. Acceptance criteria (Program §5 EC2-EPIC-003) — status

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Authenticated portal reachable | ✅ | `PortalService.enter` admits only a valid session with READ on `portal-navigation`; `test_admin_enters_portal_with_full_navigation`, `test_integrator_cannot_enter_portal` |
| Navigation to all authorized surfaces | ✅ | `NavigationModel.build` renders exactly the authorized §3.2 surfaces; `test_navigation_filters_to_authorized_surfaces`, `test_developer_enters_with_reduced_navigation` |
| Global search returns results across ≥4 entity types | ✅ | 7 `EntityKind`s; `test_global_search_spans_at_least_four_entity_types_for_admin` (`kinds_present ≥ 4`) |
| Accessibility checks pass | ✅ | `AccessibilityReport` (labels non-empty, unique routes/keys, home present) — `test_accessibility_report_passes`, `evidence.accessibility_passed` |

### Epic invariants (§5 — all epics)
additive over EC-1 + prior layers ✅ · deterministic outputs ✅ · no frozen-corpus writes ✅ ·
least-privilege / fail-closed ✅ · append-only audit (entries observed via the event bus, PC-16) ✅ ·
no duplicate identity ✅.

## 9. Certification impact

| ID | Criterion | Impact |
|----|-----------|--------|
| PLAT-C1 | PC-01/PC-02/PC-13 demonstrably operational and access-controlled | ✅ SATISFIED — portal admission, RBAC-gated navigation/routing, and authorization-scoped search are contract-published and capability-tagged |
| P2 — Identity & Access | least-privilege honored at the presentation layer | ✅ REINFORCED — the portal adds no new authority; all access flows through the certified L7 decision point |
| P9 / OP-C3 — Observability & Audit | portal entries surfaced as governed actions | ✅ REINFORCED — `portal.session.entered` is captured by L8 as append-only telemetry |
| P10 — EC-1 Integrity Preservation | 0 EC-1/prior-layer modifications; 0 corpus writes; full suite green | ✅ SATISFIED |

The portal carries **no constitutional authority**; the external gates (EC-1…EC-6) remain open.

## 10. EC2-EPIC-003 completion determination

Proven: **the UCOS Platform Portal & Navigation Layer (L1) exists as a deterministic, additive,
fail-closed presentation model** — the authenticated entry point that renders authorization-derived
navigation to all authorized surfaces, deterministic routing, an identity-integrated access gateway,
a portal-to-workspace handoff, platform service discovery + capability access, observability
(health/runtime/monitoring) visibility, and global search across seven entity kinds, composed into a
single governed `PortalService` emitting append-only governed-action telemetry and reproducible
portal evidence. It consumes the certified EC-1 engine and the EC-2 Identity, Observability, and
Foundation layers only through published contracts and composition roots, modifies none of them, and
writes nothing to the certified corpus.

**STOP — EC2-EPIC-003 complete. EC2-TASK-000073…EC2-TASK-000080 delivered.**

# EC2-EPIC-010-DETERMINATION — Validation Console

| Field | Value |
|-------|-------|
| ARTIFACT ID | EC2-EPIC-010-DETERMINATION |
| ARTIFACT | EC-2 Platform Program — Validation Console Execution-Package Determination |
| ARTIFACT TYPE | Repository-derived execution-package determination — evidence-only, authority-neutral (no implementation, no code, no runtime, no schema binding created) |
| PROGRAM | UCOS EC-2 Platform Realization Program |
| EPIC | EC2-EPIC-010 — Validation Console (Wave 4 — Insight Consoles; Surface #9; PC-09 validation inspection) |
| CLASSIFICATION | Repository-derived execution-package determination — evidence-only, authority-neutral |
| STATUS | **IMPLEMENTATION AUTHORIZED** |
| BRANCH | `governance-reconciliation` |
| BASELINE COMMIT | `b0deb2bcca5fa4a36f4c24d6af9ad2ce758f01e7` |
| BASELINE DATE | 2026-07-17 |
| CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY | NONE |
| HELD AUTHORITY | ENGINEERING-EXECUTION-ONLY |

*This artifact determines the execution package for `EC2-EPIC-010`. It **determines only** — it performs no implementation, generates no code, creates no runtime, invents no architecture, and binds no schema. Every value below is derived from physical repository evidence at commit `b0deb2b`: the EC-2 governing contract, the EC2-POST-007 execution determination, the certified `engine/validation/` layer, the realized `platform/**` runtimes, and the per-epic determination/completion reports. It is subordinate to the frozen corpus (`00-BOOK/`, `00-SOURCE/`, `99-FREEZE/` — read-only, DP-03), the EC-2 Platform Realization Program, the certified EC-1 Realization Engine, and every prior governance/execution determination; where any statement conflicts with a higher instrument, the higher instrument governs. It carries the EC-1 provisional-state disclosure verbatim and asserts no constitutional finality; the external gates EC-1…EC-6 remain open.*

---

## 1. REPOSITORY BASELINE

| Item | Value | Evidence |
|------|-------|----------|
| Branch | `governance-reconciliation` | `git rev-parse --abbrev-ref HEAD` |
| HEAD | `b0deb2b` | `git rev-parse HEAD` |
| Working tree | CLEAN (at determination start) | `git status --porcelain` empty |
| Registration | 344/344 registered; enforcement PASSED (pre + post) | `ukb.py enforce` |
| Digital Twin | CERTIFIED (10/10 integrity domains) | `ukbx certify` |
| Test evidence | 2070 passed; 99.90% total coverage (≥90% gate) | `python -m pytest` (prior mission) |
| EC-1 integrity | 0 `engine/**` modifications (additive-only preserved) | completion reports; clean tree |
| Predecessor epic | EC2-EPIC-007 Generation Requests — COMPLETE (impl `d955dc4`, reg `b0deb2b`) | `platform/generation/EC2-EPIC-007-COMPLETION-REPORT.md` |

`EC2-EPIC-010` is the first uncompleted node on the contract critical path (§6.4: `… 007 → **010** → 011 → 012 → 014 → GO-LIVE`) and the sole remaining root that unblocks the certification→runtime spine. Consoles `008/009/010/011/012` are absent on disk; `platform/validation/` contains only this determination.

## 2. AUTHORITY

- **Program authority.** EC-2 Platform Realization Program (`06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md`): §2.1 Surface **#9 Validation Explorer**, §2.2 **PC-09** (validation inspection) + **PC-13** (search) + **PC-16** (audit), §3.2 RBAC row *validation explorer* (R for all nine users; scoped for Partner/Integrator), §4 layers **L3 Application** (console) reading through the **L4 EC-1 façade**, §4.3 interaction *Validate artifact → `validation.ValidationEngine` → `ValidationReport` + `ValidationEvidence` + `AcceptanceDecision`*, §5 EC2-EPIC-010 acceptance, §9 **P6** Validation Fidelity.
- **Execution authority.** EC2-POST-007 Execution Determination: `EC2-EPIC-010` READY · critical path TRUE · maximum dependency unlock TRUE · authorization GRANTED.
- **Lane authority.** GOV-004 authorizes the EC-2 lane; UCOS-EXEC-001 conditionally activates EC-2 execution subject to per-epic admission (EN-5); the contract Authority-Boundary §5 admission rule is satisfied because EPIC-010's dependency set is closed (§3).
- **Held authority.** ENGINEERING-EXECUTION-ONLY. This determination authorizes no constitutional step and asserts no finality.

## 3. DEPENDENCY CLOSURE ANALYSIS

| Declared dependency (contract §5) | Status | Evidence |
|-----------------------------------|--------|----------|
| EC2-EPIC-007 Generation Requests | COMPLETE | `platform/generation/EC2-EPIC-007-COMPLETION-REPORT.md` ("✅ COMPLETE"); 2070 passed |
| EC-1 Validation Layer (`engine.validation`) | CERTIFIED (read-only, by `ContractRef`) | `engine/validation/` (`contracts`, `checks`, `executor`, `evidence`, `gates`); `ContractRef("engine.validation.validate", "1.0.0")` in `platform/foundation/contracts.py::ENGINE_CONTRACTS` |
| EC2-EPIC-002 Identity & Access | COMPLETE/CERTIFIED | tag `EC2-EPIC-002-CERTIFIED`; `CapabilityGroup.VALIDATION_EXPLORER` present |
| EC2-EPIC-013 Observability & Monitoring | COMPLETE | `platform/observability/EC2-EPIC-013-COMPLETION-REPORT.md` |
| EC2-EPIC-001 Foundation & API | COMPLETE | `platform/foundation/EC2-EPIC-001-COMPLETION-REPORT.md`; `ENGINE_CONTRACTS`, `ContractRef`, `content_hash` |

**Dependency set fully closed.** Every upstream is COMPLETE/CERTIFIED. No unmet predecessor; no required invention (TP-01). The Generation→Blueprint→Request→Implementation link-4 trace (RSK-01) was discharged within EPIC-006/007 and does not bound EPIC-010 (an inspection surface). All EC-1-side inputs (`ValidationEngine`, `ValidationSubject`, `ValidationReport`, `ValidationEvidence`, `AcceptanceDecision`) are certified and available.

## 4. EXISTING VALIDATION CAPABILITIES (evidence — do not re-implement)

The certified EC-1 **Validation Layer** (`engine/validation/`, `VALIDATION_CONTRACT_VERSION = "1.0.0"`) is the sole source of validation truth. It is **read-only, additive, and fully deterministic** (identical subject ⇒ byte-identical report/evidence/decision). Public surface to be consumed **by reference only**:

| EC-1 symbol | Role | Consumed by console as |
|-------------|------|------------------------|
| `ValidationEngine` / `validate_runtime_unit` | Runs the check suite over a normalized subject → `ValidationReport` | Read-only reproduction of the authoritative report |
| `ValidationSubject` (`from_runtime_unit`) | Type-independent projection of a generated artifact | Input projection for fidelity reproduction |
| `default_checks` (Provenance, Signature, Sbom, Disclosure, DependencyClosure, ImageDigest, Identity) | The canonical acceptance checks | Rendered as findings; **never redefined** |
| `ValidationReport` / `ValidationFinding` / `Verdict` / `Severity` / `CheckStatus` | Ordered deterministic aggregate + finding taxonomy | Faithful rendering (verdict, counts, blocking/advisory failures) |
| `ValidationEvidence` / `build_validation_evidence` / `EVIDENCE_FORMAT` (`ucos-validation-evidence/1.0.0`) | Reproducible evidence document | Surfaced verbatim |
| `AcceptanceDecision` / `enforce_acceptance` | Acceptance gate outcome (accepted, verdict, blocking/advisory failures) | Surfaced verbatim |

Additionally reused from the completed platform layers: `AuthorizationService` + `CapabilityGroup.VALIDATION_EXPLORER` (identity), `ObservabilityService` + `EventBus` + `HealthRegistry` (observability/L8), `WorkspaceRegistry`/tenant isolation (workspace), `content_hash`/`canonical_json`/`ContractRef` (foundation), and the EPIC-007 `DispatchRecord`/`DispatchLedger` + `RequestProvenance` as the by-reference source of validatable targets.

## 5. REQUIRED VALIDATION CONSOLE CAPABILITIES

`EC2-EPIC-010` realizes Surface #9 as the UCOS Platform **Validation Console Runtime** (`platform/validation/`, L3 Application) — a governed, read/inspection surface that **faithfully surfaces** EC-1 validation outputs to authorized users. Required capabilities:

- **VC-1 Faithful surfacing (P6).** Present the EC-1 `ValidationReport` + `ValidationEvidence` + `AcceptanceDecision` for a target **byte-for-byte equal** to engine output (fingerprint equality), by invoking the certified deterministic `ValidationEngine` read-only over the same `ValidationSubject` — never re-deriving verdicts.
- **VC-2 Verdict & findings display.** Render verdict, counts, and blocking/advisory failures per the frozen finding taxonomy.
- **VC-3 Inspection registry.** Content-addressed, append-only inspection records bound by reference to a generation request / dispatch record, scoped to workspace/project/owner.
- **VC-4 Search & discovery (PC-13).** Authorization- and isolation-scoped search over validation records (filter by workspace/project/verdict/severity/target).
- **VC-5 Derived posture.** Deterministic derived status (`ACCEPTED` / `REJECTED` / `ACCEPTED_WITH_ADVISORIES`) as a pure function of the report.
- **VC-6 Health.** Critical checks: registry integrity, **fidelity** (surfaced report equals engine output), evidence integrity.
- **VC-7 Audit & observability (PC-16/PC-12).** Governed events + append-only L8 audit + metrics on 100% of inspections.
- **VC-8 Trace.** Continue the link-4 trace edge (Request → Artifact → **Validation**) by reference.

## 6. RUNTIME BOUNDARIES

- **L3 Application (console).** `platform/validation/` owns read/inspection business logic only; it issues **no** direct engine calls except through the L4 façade projection.
- **L4 EC-1 façade (read-only).** The only path to EC-1; binds `engine.validation` **by `ContractRef("engine.validation.validate", "1.0.0")`** (already published in `ENGINE_CONTRACTS`). No live `engine.*` import at module scope beyond the certified façade discipline used by prior epics (P10).
- **By-reference targets.** The console operates over `ValidationSubject`/`RuntimeUnit` inputs supplied **by reference** (via EPIC-007 `DispatchRecord`). It performs **no live generation or execution** — that is EPIC-012 scope. Because `ValidationEngine` is a pure deterministic function, read-only reproduction over the same subject yields the same report the engine produced (faithful surfacing, not invention).
- **In-memory, deterministic, no I/O.** No server, no socket, no file writes, no wall-clock in any identity or ordering (caller-supplied logical ticks). No frozen-corpus write (DP-03).

## 7. SECURITY REQUIREMENTS

- **Authorization.** Every action authorizes through the certified `AuthorizationService` on the **pre-existing** `CapabilityGroup.VALIDATION_EXPLORER` (§3.2). **No new authority, role, permission, capability group, or classification model.**
- **Permission profile.** READ-only (INSPECT / TRACK). No `create/execute/administer` verb; no `authorize/ratify/enact/grant/govern/override` verb exposed.
- **Isolation.** Composed access = identity authorization ∧ tenant/workspace isolation; Partner/Integrator access is workspace-scoped and tenant-isolated. Every denial reason is tested (`no-grant`, `tenant-isolation-violation`).
- **Secrets.** None; by reference only (SEC-04). Reuse of `EC2-CAP-SEC-001` posture where applicable.
- **Immutability (P7 alignment).** Surfaced records/evidence/decisions are immutable value types; **zero mutation paths** to any validation datum.

## 8. GOVERNANCE REQUIREMENTS

1. **Additive-only over EC-1 and prior platform layers.** No `engine/**` modification; no change to any completed `platform/**` layer.
2. **No duplicate validation engine.** The console **must not** implement or fork any check, verdict, gate, or evidence format; it consumes `engine.validation` verbatim (TP-01, no invention).
3. **No new capability group / no parallel identity / no parallel framework.** Reuse `VALIDATION_EXPLORER`, `AuthorizationService`, `ObservabilityService`, `EventBus`, `HealthRegistry`.
4. **Fail-closed.** Absence of grant, isolation, or evidence ⇒ DENY / NOT-SURFACED (never assumed-accepted).
5. **Provisional-state disclosure** carried verbatim; asserts no constitutional finality.
6. **TRACK-001 evidence→status.** Status is a pure function of tests/coverage/acceptance evidence; no manual override.

## 9. AUDIT REQUIREMENTS

- Every governed inspection emits a governed event onto the Foundation `EventBus`, captured as **append-only L8 audit** (PC-16): `validation.report.surfaced` / `inspected` / `evidence.rendered` / `access.evaluated`, and derived `accepted` / `rejected`.
- The inspection registry maintains an ordered, append-only record log per target (reconstruction preserved).
- No audit record or surfaced record is mutable or deletable (append-only invariant, consistent with §3.2 invariant ii).

## 10. OBSERVABILITY REQUIREMENTS

- **Events** (above) on 100% of governed actions (P9).
- **Metrics** (PC-12): `validation_reports_surfaced` / `accepted` / `rejected` counters; `blocking_failures` gauge/histogram; inspection-latency histogram (logical).
- **Health** (three critical checks registered idempotently into the L8 `HealthRegistry` by the bootstrap): `validation-console-registry`, `validation-console-fidelity` (surfaced report == engine output), `validation-console-evidence-integrity`.
- Reproducible inspection evidence (`fingerprint()`), byte-identical in-process and across processes.

## 11. DOMAIN MODEL DETERMINATION

Aggregate: **`ValidationRecord`** (`UCOS-VREP-*`, content-addressed from `target_id + blueprint_id + report fingerprint + workspace + logical tick`). Establishes: identity (content-addressed), binding (by-reference `request_ref` / `dispatch_ref` / `workspace` / `project`), ownership (`owner_subject`), the surfaced `ValidationReport` (by reference/value), `ValidationEvidence`, `AcceptanceDecision`, derived `ValidationPosture` (`ACCEPTED` / `REJECTED` / `ACCEPTED_WITH_ADVISORIES`), and audit metadata (append-only inspection events). Supporting value types: `ValidationView` / `FindingView` (render projections), `ValidationCensus` (verdict/severity counts), `ValidationHit` / `ValidationSearchResponse`. Terminal nature: a record is an immutable snapshot; re-surfacing the same subject yields an identical record (idempotent).

## 12. SERVICE LAYER DETERMINATION

`ValidationConsoleService` — fail-closed L3 composition root and the console access/context decision point. Composed access decision = identity authorization (`VALIDATION_EXPLORER`, READ) ∧ tenant/workspace isolation. Read-only methods only (no mutation). Reuses certified authentication/authorization, error contracts (`EC2-VC-*` over `PlatformError`), and content-addressed response contracts. Reproducible `ValidationConsoleEvidence`. `bootstrap_validation_console` publishes versioned `VALIDATION_CONSOLE_CONTRACTS` and registers health checks (idempotent).

## 13. API DETERMINATION

Governed in-process service surface (stdlib-only, contract/registry-driven — no HTTP framework), published as versioned `VALIDATION_CONSOLE_CONTRACTS`:

| Capability | Service method | Authority |
|------------|----------------|-----------|
| Report collection (GET) | `list_reports` (filter workspace/project/verdict/target) | READ + isolation |
| Report details (GET) | `get_report` / `select_report` | READ (INSPECT) |
| Findings (GET) | `inspect_findings` | READ (INSPECT) |
| Evidence (GET) | `view_evidence` | READ (INSPECT) |
| Acceptance decision (GET) | `acceptance_of` | READ (INSPECT) |
| Posture / status (GET) | `posture_of` / `track_validation` | READ (TRACK) |
| Search (GET) | `search` | READ + isolation |
| Trace (link-4) | `trace` | READ |

No create/execute/administer route. Reuses the certified response/error contracts; no API-convention drift.

## 14. PERSISTENCE DETERMINATION

Deterministic, append-only, in-memory: `ValidationRecordRegistry` (records + ordered inspection event log; per-target reconstruction; verdict/severity census). Every record content-addressed and `to_dict()`/`fingerprint()`-serializable. Idempotent by content hash (re-surfacing is a no-op that returns the identical record). No external store, no file writes (DP-03).

## 15. TESTING REQUIREMENTS

Full additive suite under `platform/tests/test_validation_console_*.py` covering: contracts, registry, façade/fidelity, evidence, posture/status, search, context, health, service, governance, authorization/isolation, determinism, traceability. Mandatory tests: (a) **fidelity** — surfaced report/evidence/decision equal `engine.validation` output byte-for-byte (fingerprint equality); (b) **determinism** — identical subject ⇒ byte-identical record in-process **and** across independent processes; (c) **no-mutation** — no path mutates a report/evidence/decision; (d) **P10** — runtime imports no `engine.*` module directly except by `ContractRef` (source-verified); (e) negative authorization/isolation. Targets: ≥90% total coverage gate (`--cov=platform.validation`), 100% per console module, ruff clean, full suite green with zero regressions.

## 16. REGISTRATION REQUIREMENTS

Per REG-AUTO-001 (*Artifact Creation = Artifact Registration*): this determination artifact is registered via the atomic registration transaction (`ukb build` → registries/pages/graph/control-tower; `ukb validate`; `ukb enforce`), consistent with the EPIC-005/006/007 precedent. The subsequent implementation package (`platform/validation/**` + completion report) is registered in a **separate `REG-AUTO-001: register EC2-EPIC-010` commit** at completion. Enforcement must remain PASSED (no unregistered/unclassified/invalid artifact) and the drift gate clean after each commit.

## 17. ACCEPTANCE CRITERIA (objective, fail-closed)

| # | Criterion | PASS measure |
|---|-----------|--------------|
| AC-1 | Faithful surfacing (P6) | Platform-surfaced `ValidationReport` + evidence + decision equal EC-1 output **byte-for-byte** (fingerprint equality) |
| AC-2 | Verdict & findings | Verdict, counts, and blocking/advisory failures rendered per the frozen taxonomy |
| AC-3 | Fidelity machine-checkable | `validation-console-fidelity` health check drives UNHEALTHY on any divergence |
| AC-4 | RBAC enforced | `VALIDATION_EXPLORER` READ enforced; Partner/Integrator scoped; 100% of negative-access tests denied |
| AC-5 | Read-only integrity | Zero mutation paths to reports/evidence/decisions |
| AC-6 | Determinism (P5-aligned) | Identical subject ⇒ byte-identical surfaced record across processes |
| AC-7 | Audit & observability (P9) | Governed events + append-only audit + metrics on 100% of inspections |
| AC-8 | Additive / EC-1 integrity (P10) | 0 `engine/**` edits; 0 frozen-corpus writes; EC-1 suite green; ≥90% coverage; ruff clean |

## 18. SUCCESS CRITERIA

- All EC2-TASK-000145…000152 COMPLETE with acceptance tests + coverage gate green.
- AC-1…AC-8 all PASS.
- Contract §5 EPIC-010 acceptance satisfied ("reports/evidence rendered faithfully; verdict & blocking failures displayed; matches EC-1 `ValidationReport` exactly").
- P6 (Validation Fidelity) and P10 (EC-1 Integrity Preservation) PASS.
- EPIC-011 (Certification Console & Ledger) unblocked (its sole platform predecessor closed).

## 19. RISKS

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R-1 | Fidelity drift — surfaced report diverges from engine output | High | Reproduce read-only via the certified `ValidationEngine`; assert fingerprint equality; `validation-console-fidelity` health check + test AC-1/AC-3 |
| R-2 | Temptation to add/adjust checks or verdicts | Medium | Governance §8.2: consume `engine.validation` verbatim; no check/verdict/gate/evidence redefinition (TP-01) |
| R-3 | By-reference targets — no live generation output yet (EPIC-007 dispatch is by reference; live exec is EPIC-012) | Medium (bounds, not blocks) | Console operates over supplied `ValidationSubject`/`RuntimeUnit` by reference; end-to-end live-generation validation is exercised in EPIC-012, not EPIC-010 |
| R-4 | New capability-group creep | Low | Reuse pre-existing `VALIDATION_EXPLORER`; source-verified in governance test |
| R-5 | Registration drift on commit | Low | Run atomic registration transaction; keep `signals.json`/`change-ledger.json` timestamp-only churn out of scope; guard gate must pass |
| R-6 | Accidental `engine/**` import at runtime (P10) | Low | Bind by `ContractRef`; `test_runtime_never_imports_engine_modules_directly` analogue |

No risk blocks admission.

## 20. AUTHORIZED IMPLEMENTATION SCOPE

Additive `platform/validation/` L3 runtime, decomposed as **EC2-TASK-000145…000152** (topology mirrors the certified `platform/generation/` template):

1. **TASK-000145** — `errors`, `metadata`, `contracts` (RBAC group binding to `VALIDATION_EXPLORER`; `ContractRef` to `engine.validation.validate`; view/verdict/posture types; `VALIDATION_CONSOLE_CONTRACTS`).
2. **TASK-000146** — `registry` (`ValidationRecordRegistry`; append-only inspection log; census).
3. **TASK-000147** — `facade` (read-only projection: run `ValidationEngine` over `ValidationSubject`, `build_validation_evidence`, `enforce_acceptance` — the fidelity boundary).
4. **TASK-000148** — `evidence` view + `status`/`posture` derivation.
5. **TASK-000149** — `search` (authorization + isolation scoped) + `context`.
6. **TASK-000150** — `health` (registry-integrity, fidelity, evidence-integrity checks).
7. **TASK-000151** — `service` (`ValidationConsoleService` composition root + access + reproducible evidence).
8. **TASK-000152** — `bootstrap` + `__init__` (composition root publishing versioned contracts) + full test suite + `EC2-EPIC-010-COMPLETION-REPORT.md`.

## 21. EXPLICIT NON-SCOPE

- **No live generation or EC-1 execution** (EPIC-012 Runtime Operations).
- **No certification inspection or ledger** (EPIC-011 Certification Console & Ledger).
- **No execution dashboard / artifact explorer** capabilities (EPIC-008/009).
- **No new or modified validation check, verdict, gate, severity, or evidence format** — `engine.validation` is consumed verbatim.
- **No `engine/**` modification; no fork or re-derivation of the Validation Layer.**
- **No new capability group, role, permission, or classification model.**
- **No frozen-corpus write (DP-03); no server, socket, network, or file I/O; no wall-clock in identity/ordering.**
- **No mutation path** to any surfaced report, evidence, or acceptance decision.
- **No UI/presentation (L1)** — that is later EC-2 presentation work; this epic realizes the L3 governed service surface only.

## 22. FINAL AUTHORIZATION VERDICT

**READY — IMPLEMENTATION AUTHORIZED.** All readiness conditions are met: prerequisites COMPLETE (EPIC-007) / CERTIFIED (`engine.validation`, EPIC-002); dependency set fully closed (§3); architecture available (contract §2.1 #9, PC-09/PC-13/PC-16, §4/§4.3, §5, P6); reuse anchors pre-exist (`CapabilityGroup.VALIDATION_EXPLORER`, `ContractRef("engine.validation.validate","1.0.0")`); governance in force (GOV-004 lane + UCOS-EXEC-001 admission); controls operative (CI, determinism gate, TRACK-001, ≥90% coverage gate); realization template proven (nine prior additive `platform/**` runtimes). No governance, registration, architecture, security, observability, runtime, or certification blocker remains.

*This determination authorizes no implementation work by itself; it identifies and authorizes the next target. Implementation of `EC2-EPIC-010` proceeds only under per-epic admission consistent with the standing EXEC-001 conditions: additive-only over EC-1, 0 frozen-corpus writes (DP-03), determinism/reproducibility preserved (P5), fidelity preserved (P6), EC-1 integrity preserved (P10), TRACK-001 evidence→status (fail-closed).*

**END OF ARTIFACT — EC2-EPIC-010-DETERMINATION · IMPLEMENTATION AUTHORIZED · EVIDENCE-DERIVED · AUTHORITY-NEUTRAL**

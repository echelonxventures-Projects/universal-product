# EC2-EPIC-011-DETERMINATION — Certification Console & Ledger

| Field | Value |
|-------|-------|
| ARTIFACT ID | EC2-EPIC-011-DETERMINATION |
| ARTIFACT | EC-2 Platform Program — Certification Console & Ledger Execution-Package Determination |
| ARTIFACT TYPE | Repository-derived execution-package determination — evidence-only, authority-neutral (no implementation, no code, no runtime, no schema binding created) |
| PROGRAM | UCOS EC-2 Platform Realization Program |
| EPIC | EC2-EPIC-011 — Certification Console & Ledger (Wave 4 — Insight Consoles; Surface #10; PC-10 certification inspection & ledger) |
| CLASSIFICATION | Repository-derived execution-package determination — evidence-only, authority-neutral |
| STATUS | **IMPLEMENTATION AUTHORIZED** |
| BRANCH | `governance-reconciliation` |
| BASELINE COMMIT | `1002304` |
| BASELINE DATE | 2026-07-17 |
| CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY | NONE |
| HELD AUTHORITY | ENGINEERING-EXECUTION-ONLY |

*This artifact determines the execution package for `EC2-EPIC-011`. It **determines only** — it performs no implementation, generates no code, creates no runtime, invents no architecture, and binds no schema. Every value below is derived from physical repository evidence at commit `1002304`: the EC-2 governing contract, the certified `engine/certification/` layer, the completed `platform/validation/` Validation Console (EPIC-010), the realized `platform/**` runtimes, and the per-epic determination/completion reports. It is subordinate to the frozen corpus (`00-BOOK/`, `00-SOURCE/`, `99-FREEZE/` — read-only, DP-03), the EC-2 Platform Realization Program, the certified EC-1 Realization Engine, and every prior governance/execution determination; where any statement conflicts with a higher instrument, the higher instrument governs. It carries the EC-1 provisional-state disclosure verbatim and asserts no constitutional finality; the external gates EC-1…EC-6 remain open.*

---

## 1. REPOSITORY BASELINE

| Item | Value | Evidence |
|------|-------|----------|
| Branch | `governance-reconciliation` | `git rev-parse --abbrev-ref HEAD` |
| HEAD | `1002304` | `git rev-parse HEAD` |
| Working tree | CLEAN (at determination start) | `git status --porcelain` empty |
| Verification baseline | 2379 passed; 100.00% coverage; ruff clean; governance clean; `verify.sh` PASS | prior reconciliation mission |
| EC-1 integrity | 0 `engine/**` modifications (additive-only preserved) | completion reports; clean tree |
| Predecessor epic | EC2-EPIC-010 Validation Console — COMPLETE | `platform/validation/EC2-EPIC-010-COMPLETION-REPORT.md` |

`EC2-EPIC-011` is the next uncompleted node on the contract critical path (§6.4: `… 007 → 010 → **011** → 012 → 014 → GO-LIVE`) and the sole remaining root that unblocks the runtime-operations spine (EPIC-012 depends on EPIC-011). Consoles `008/009/010` are COMPLETE; `platform/certification/` realizes Surface #10.

## 2. AUTHORITY

- **Program authority.** EC-2 Platform Realization Program (`06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md`): §2.1 Surface **#10 Certification Ledger**, §2.2 **PC-10** (certification inspection & ledger) + **PC-13** (search) + **PC-16** (audit), §3.2 RBAC row *certification ledger* (R for all nine users; `R+attest` for the Certification Authority; scoped for Partner/Integrator), §4 layers **L3 Application** (console) reading through the **L4 EC-1 façade**, §4.3 interaction *Certify validated target → `certification.CertificationEngine` → `CertificationDecision` + `CertificationRecord` + `CertificationEvidence` + ledger append*, §5 EC2-EPIC-011 acceptance ("Records/evidence rendered; ledger browsable; chain-integrity verification exposed; 0 mutation paths to records/ledger"), §9 **P6** Fidelity.
- **Execution authority.** The generation→certification→runtime spine (007→010→011→012) admits EPIC-011 once EPIC-010 is COMPLETE and the certified `engine.certification` layer is available — both satisfied.
- **Lane authority.** GOV-004 authorizes the EC-2 lane; UCOS-EXEC-001 conditionally activates EC-2 execution subject to per-epic admission; the contract Authority-Boundary admission rule is satisfied because EPIC-011's dependency set is closed (§3).
- **Held authority.** ENGINEERING-EXECUTION-ONLY. This determination authorizes no constitutional step and asserts no finality.

## 3. DEPENDENCY CLOSURE ANALYSIS

| Declared dependency (contract §5) | Status | Evidence |
|-----------------------------------|--------|----------|
| EC2-EPIC-010 Validation Console | COMPLETE | `platform/validation/EC2-EPIC-010-COMPLETION-REPORT.md`; 2379 passed / 100.00% |
| EC-1 Certification Layer (`engine.certification`) | CERTIFIED (read-only, by `ContractRef`) | `engine/certification/` (`contracts`, `criteria`, `engine`, `evidence`, `ledger`); `ContractRef("engine.certification.certify", "1.0.0")` in `platform/foundation/contracts.py::ENGINE_CONTRACTS` |
| EC-1 Validation Layer (`engine.validation`) | CERTIFIED (read-only, upstream projection) | `engine/validation/` (report + evidence the certification aggregates) |
| EC2-EPIC-002 Identity & Access | COMPLETE/CERTIFIED | `CapabilityGroup.CERTIFICATION_LEDGER` present; policy invariant ii (append-only) present |
| EC2-EPIC-013 Observability & Monitoring | COMPLETE | `platform/observability/` health model + event bus |
| EC2-EPIC-001 Foundation & API | COMPLETE | `ENGINE_CONTRACTS`, `ContractRef`, `content_hash` |

**Dependency set fully closed.** Every upstream is COMPLETE/CERTIFIED. No unmet predecessor; no required invention (TP-01). All EC-1-side inputs (`CertificationEngine`, `CertificationSubject`, `CertificationDecision`, `CertificationRecord`, `CertificationEvidence`, `CertificationLedger`) are certified and available.

## 4. EXISTING CERTIFICATION CAPABILITIES (evidence — do not re-implement)

The certified EC-1 **Certification Layer** (`engine/certification/`, `CERTIFICATION_CONTRACT_VERSION = "1.0.0"`) is the sole source of certification truth. It is **read-only, additive, and fully deterministic** (identical validation report + evidence ⇒ byte-identical decision/record/evidence and a stable `certification_id`). Public surface consumed **by reference only**:

| EC-1 symbol | Role | Consumed by console as |
|-------------|------|------------------------|
| `CertificationEngine` / `certify_validation` | Runs the criteria suite over a normalized subject → `CertificationDecision` | Read-only reproduction of the authoritative decision |
| `CertificationSubject` (`from_validation`) | Projection of the upstream `ValidationReport` + `ValidationEvidence` | Input projection for fidelity reproduction |
| `default_criteria` (disclosure, validation-accepted, evidence-present, version-pinned, validation-complete) | The canonical certification criteria | Rendered as criterion findings; **never redefined** |
| `CertificationDecision` / `CertificationFinding` / `CertificationStatus` / `CriterionSeverity` / `CriterionStatus` / `CertificationClass` | Aggregate verdict + finding taxonomy | Faithful rendering (status, counts, blocking/advisory) |
| `CertificationRecord` (`content_sha256`, `verify_integrity`) | Immutable, content-addressed record | Surfaced verbatim; integrity re-checked |
| `CertificationEvidence` / `build_certification_evidence` / `EVIDENCE_FORMAT` (`ucos-certification-evidence/1.0.0`) | Reproducible evidence document | Surfaced by reference |
| `CertificationLedger` / `CertificationLedgerEntry` (append-only, hash-chained, `verify`) | Tamper-evident register | Wrapped read-only; navigated; chain verified |

Additionally reused: `AuthorizationService` + `CapabilityGroup.CERTIFICATION_LEDGER` and policy invariant ii (identity), `ObservabilityService` + `EventBus` + `HealthRegistry` (observability/L8), tenant isolation (`platform.workspace.isolation`), `content_hash`/`ContractRef` (foundation), and the EPIC-010 `ValidationReport`/`ValidationEvidence` as the by-reference certification input.

## 5. REQUIRED CERTIFICATION CONSOLE CAPABILITIES

`EC2-EPIC-011` realizes Surface #10 as the UCOS Platform **Certification Console & Ledger Runtime** (`platform/certification/`, L3 Application) — a governed, read/inspection surface that **faithfully surfaces** EC-1 certification outputs and the append-only ledger to authorized users:

- **CC-1 Certification discovery.** Discover surfaced certifications, authorization- and isolation-scoped.
- **CC-2 Registry access.** Content-addressed, append-only console record registry (surface/register/resolve).
- **CC-3 Status inspection.** Faithful decision/criteria rendering + derived `CertificationPosture`.
- **CC-4 Evidence retrieval.** Faithful `CertificationEvidence` reference (by reference, fingerprint-verifiable).
- **CC-5 Ledger navigation (PC-10).** Read-only navigation of the append-only, hash-chained ledger; chain-integrity verification exposed.
- **CC-6 Lineage inspection.** Deterministic parent/child/ancestry lineage + re-certification history of a target.
- **CC-7 Search (PC-13).** Authorization- and isolation-scoped search over certification records.
- **CC-8 Health.** Critical checks: registry integrity, ledger-integrity, **fidelity**, evidence-integrity.
- **CC-9 Governance validation.** Deterministic compliance evaluation against the certification governance rules (record integrity, `ENGINEERING-EXECUTION-ONLY` authority, standard/version pinning, disclosure presence, status consistency).
- **CC-10 Readiness evaluation.** Deterministic completeness evaluation (readiness indicators → a fail-closed verdict).
- **CC-11 Fidelity (P6).** Present decision/record/evidence **byte-for-byte equal** to engine output; machine-checkable predicate.
- **CC-12 Trace.** Continue the link chain (Validation → Target → **Certification**) by reference.

## 6. RUNTIME BOUNDARIES

- **L3 Application (console).** `platform/certification/` owns read/inspection business logic only; it issues **no** direct engine calls except through the L4 façade projection.
- **L4 EC-1 façade (read-only).** The only path to EC-1; binds `engine.certification` **by `ContractRef("engine.certification.certify", "1.0.0")`** (already published in `ENGINE_CONTRACTS`).
- **By-reference inputs.** The console certifies over `ValidationReport` + `ValidationEvidence` supplied **by reference**. Because `CertificationEngine` is a pure deterministic function, read-only reproduction over the same validation output yields the same decision/record the engine produced (faithful surfacing, not invention).
- **Append-only ledger.** The console ledger wraps the certified append-only, hash-chained `CertificationLedger`; it exposes no update or delete. Appending is idempotent by `certification_id`.
- **In-memory, deterministic, no I/O.** No server, no socket, no file writes, no wall-clock in any identity or ordering (caller-supplied logical ticks). No frozen-corpus write (DP-03).

## 7. SECURITY REQUIREMENTS

- **Authorization.** Every action authorizes through the certified `AuthorizationService` on the **pre-existing** `CapabilityGroup.CERTIFICATION_LEDGER` (§3.2). **No new authority, role, permission, capability group, or classification model.**
- **Permission profile.** READ-only. No `create/execute/administer` verb; no `authorize/ratify/enact/grant/govern/override` verb exposed.
- **Ledger append-only invariant (§3.2 ii).** The certified policy denies every mutation of a certification record / ledger entry regardless of grant (`certification-ledger-append-only`); the console adds no mutation path.
- **Isolation.** Composed access = identity authorization ∧ tenant/workspace isolation; every denial reason is tested (`no-grant`, `tenant-isolation-violation`).
- **Secrets.** None; by reference only (SEC-04).
- **Immutability (P7 alignment).** Surfaced records/evidence/ledger entries are immutable value types; **zero mutation paths**.

## 8. GOVERNANCE REQUIREMENTS

1. **Additive-only over EC-1 and prior platform layers.** No `engine/**` modification; no change to any completed `platform/**` layer.
2. **No duplicate certification engine.** The console **must not** implement or fork any criterion, verdict, ledger rule, or evidence format; it consumes `engine.certification` verbatim (TP-01, no invention).
3. **No new capability group / no parallel identity / no parallel framework.** Reuse `CERTIFICATION_LEDGER`, `AuthorizationService`, `ObservabilityService`, `EventBus`, `HealthRegistry`, `CertificationLedger`.
4. **Fail-closed.** Absence of grant, isolation, or evidence ⇒ DENY / NOT-SURFACED.
5. **Provisional-state disclosure** carried verbatim; asserts no constitutional finality.
6. **TRACK-001 evidence→status.** Status is a pure function of tests/coverage/acceptance evidence; no manual override.

## 9. AUDIT REQUIREMENTS

- Every governed inspection emits a governed event onto the Foundation `EventBus`, captured as **append-only L8 audit** (PC-16): `certification.record.surfaced` / `inspected` / `evidence.rendered` / `ledger.viewed` / `lineage.rendered` / `searched` / `traced` / `readiness.evaluated` / `governance.validated` / `access.evaluated`, derived `certified` / `not_certified`, and `certification.ledger.appended`.
- The inspection registry maintains an ordered, append-only record log per record (reconstruction preserved); the certification ledger is append-only and hash-chained.
- No audit record, surfaced record, or ledger entry is mutable or deletable (append-only invariant, §3.2 ii).

## 10. OBSERVABILITY REQUIREMENTS

- **Events** (above) on 100% of governed actions (P9).
- **Metrics** (PC-12): `certification.records.surfaced` / `certified` / `not_certified` / `advisory` counters; `certification.records.inspections` / `certification.ledger.appends` counters; `certification.records.blocking_failures` histogram.
- **Health** (four critical checks registered idempotently into the L8 `HealthRegistry` by the bootstrap): `certification-console-registry`, `certification-console-ledger-integrity`, `certification-console-fidelity` (surfaced record == engine output), `certification-console-evidence-integrity`.
- Reproducible inspection evidence (`fingerprint()`), byte-identical in-process and across processes.

## 11. DOMAIN MODEL DETERMINATION

Aggregate: **`CertificationConsoleRecord`** (`UCOS-CREC-*`, content-addressed from engine `certification_id` + binding). Binds the certified `CertificationDecision` + immutable `CertificationRecord` + `CertificationEvidence` (and the upstream `ValidationReport` + `ValidationEvidence`) to an optional `request_ref` / `workspace` / `project` (by reference), a `tenant` boundary, and the surfacing `owner_subject`. Derived `CertificationPosture` (`CERTIFIED` / `CERTIFIED_WITH_ADVISORIES` / `NOT_CERTIFIED`). Supporting value types: `CriterionFindingView` / `CertificationSummary` / `CertificationEvidenceReference` / `CertificationTrace` (render projections), `CertificationLedgerView` / `CertificationLineageView` (ledger projections), `CertificationReadiness` / `GovernanceAssessment` (derived evaluations), `CertificationSearchResult` / `CertificationSearchResponse`, `CertificationConsoleEvidence` (runtime evidence). Terminal nature: a record is an immutable snapshot; re-surfacing the same certification yields an identical record (idempotent).

## 12. SERVICE LAYER DETERMINATION

`CertificationConsoleService` — fail-closed L3 composition root and the console access/context decision point. Composed access decision = identity authorization (`CERTIFICATION_LEDGER`, READ) ∧ tenant/workspace isolation. Read-only methods only (no mutation). Reuses certified authorization, error contracts (`EC2-CC-*` over `PlatformError`), content-addressed response contracts, and the append-only ledger. Reproducible `CertificationConsoleEvidence`. `bootstrap_certification_console` publishes versioned `CERTIFICATION_CONSOLE_CONTRACTS` and registers health checks (idempotent).

## 13. API DETERMINATION

Governed in-process service surface (stdlib-only, contract/registry-driven — no HTTP framework), published as versioned `CERTIFICATION_CONSOLE_CONTRACTS`:

| Capability | Service method | Authority |
|------------|----------------|-----------|
| Surface certification | `surface_certification` | READ + isolation |
| Record collection | `list_certifications` | READ + isolation |
| Record details | `get_certification` / `select_certification` | READ (INSPECT) |
| Summary / decision | `summary_of` / `decision_of` | READ |
| Evidence | `view_evidence` | READ (VIEW_EVIDENCE) |
| Ledger entry | `view_ledger_entry` | READ (VIEW_LEDGER) |
| Lineage | `lineage_of` | READ (VIEW_LINEAGE) |
| Posture / status | `status_of` / `track_certification` | READ (TRACK) |
| Readiness | `readiness_of` / `assess_readiness` | READ (EVALUATE_READINESS) |
| Governance | `governance_of` / `assess_governance` | READ (VALIDATE_GOVERNANCE) |
| Search | `search` | READ + isolation |
| Trace | `trace` | READ (TRACE) |

No create/execute/administer route. Reuses the certified response/error contracts; no API-convention drift.

## 14. PERSISTENCE DETERMINATION

Deterministic, append-only, in-memory: `CertificationRegistry` (records + ordered inspection event log; per-record reconstruction; status census) and `CertificationConsoleLedger` (append-only, hash-chained, idempotent by `certification_id`, tamper-evident). Every record/ledger view content-addressed and `to_dict()`/`fingerprint()`-serializable. No external store, no file writes (DP-03).

## 15. TESTING REQUIREMENTS

Full additive suite under `platform/tests/test_certification_*.py` covering: contracts, context, evidence, facade, registry, ledger, search, status/readiness/governance, health, service, governance invariants, determinism. Mandatory tests: (a) **fidelity** — surfaced decision/record/evidence equal `engine.certification` output byte-for-byte; (b) **determinism** — identical validation output ⇒ byte-identical record in-process **and** across independent processes; (c) **no-mutation** — no path mutates a record/evidence/ledger entry; the policy denies ledger mutation; (d) **ledger integrity** — chain verifies; a tampered chain drives health UNHEALTHY; (e) negative authorization/isolation. Targets: 100.00% coverage of every `platform/certification` module, ruff clean, full suite green with zero regressions.

## 16. REGISTRATION REQUIREMENTS

Per REG-AUTO-001 (*Artifact Creation = Artifact Registration*): this determination artifact and the completion report are registered via the atomic registration transaction (`register.sh --guard` → registries/pages/graph/control-tower; `ukb.py enforce`), consistent with the EPIC-007/010 precedent. Enforcement must remain PASSED (no unregistered/unclassified/invalid artifact) and the drift gate clean.

## 17. ACCEPTANCE CRITERIA (objective, fail-closed)

| # | Criterion | PASS measure |
|---|-----------|--------------|
| AC-1 | Faithful surfacing (P6) | Platform-surfaced `CertificationDecision` + record + evidence equal EC-1 output **byte-for-byte** |
| AC-2 | Records / evidence rendered | Status, counts, criteria, evidence reference rendered per the frozen taxonomy |
| AC-3 | Ledger browsable + chain verified | Ledger entries/lineage navigable; chain-integrity verification exposed; `certification-console-ledger-integrity` drives UNHEALTHY on tamper |
| AC-4 | Fidelity machine-checkable | `certification-console-fidelity` health check drives UNHEALTHY on any divergence |
| AC-5 | RBAC + append-only enforced | `CERTIFICATION_LEDGER` READ enforced; policy denies ledger mutation; 100% negative-access tests denied |
| AC-6 | Read-only integrity | Zero mutation paths to records/evidence/ledger |
| AC-7 | Determinism (P5-aligned) | Identical validation output ⇒ byte-identical surfaced record across processes |
| AC-8 | Audit & observability (P9) | Governed events + append-only audit + metrics on 100% of inspections |
| AC-9 | Additive / EC-1 integrity (P10) | 0 `engine/**` edits; 0 frozen-corpus writes; suite green; 100.00% coverage; ruff clean |

## 18. SUCCESS CRITERIA

- All EC2-TASK-000153…000161 COMPLETE with acceptance tests + coverage gate green.
- AC-1…AC-9 all PASS.
- Contract §5 EPIC-011 acceptance satisfied ("Records/evidence rendered; ledger browsable; chain-integrity verification exposed; 0 mutation paths to records/ledger").
- P6 (Fidelity) and P10 (EC-1 Integrity Preservation) PASS.
- EPIC-012 (Runtime Operations) unblocked (its sole platform predecessor closed).

## 19. RISKS

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R-1 | Fidelity drift — surfaced record diverges from engine output | High | Reproduce read-only via the certified `CertificationEngine`; assert hash equality; fidelity health check + AC-1/AC-4 |
| R-2 | Temptation to add/adjust criteria or ledger rules | Medium | Governance §8.2: consume `engine.certification` verbatim; no criterion/verdict/ledger/evidence redefinition (TP-01) |
| R-3 | Ledger mutation path | High | Wrap the certified append-only ledger read-only; no update/delete; policy invariant ii denies mutation; AC-3/AC-5/AC-6 |
| R-4 | New capability-group creep | Low | Reuse pre-existing `CERTIFICATION_LEDGER`; source-verified in governance test |
| R-5 | Registration drift on commit | Low | Run atomic registration transaction; guard gate must pass |
| R-6 | Accidental `engine/**` import at runtime (P10) | Low | Bind by `ContractRef`; façade-only EC-1 access |

No risk blocks admission.

## 20. AUTHORIZED IMPLEMENTATION SCOPE

Additive `platform/certification/` L3 runtime, decomposed as **EC2-TASK-000153…000161** (topology mirrors the certified `platform/validation/` template):

1. **TASK-000153** — `errors`, `contracts` (RBAC group binding to `CERTIFICATION_LEDGER`; `ContractRef` to `engine.certification.certify`; metadata + view/summary/trace types; `CERTIFICATION_CONSOLE_CONTRACTS`).
2. **TASK-000154** — `registry` (`CertificationRegistry`; append-only inspection log; status census).
3. **TASK-000155** — `facade` (read-only projection: run `CertificationEngine` over the validation output, `build_certification_evidence` — the fidelity boundary).
4. **TASK-000156** — `ledger` (`CertificationConsoleLedger` + `CertificationLedgerView` + `CertificationLineageView`).
5. **TASK-000157** — `context`, `evidence`, `status`/`readiness`/`governance` derivations.
6. **TASK-000158** — `search` (authorization + isolation scoped).
7. **TASK-000159** — `health` (registry-integrity, ledger-integrity, fidelity, evidence-integrity checks).
8. **TASK-000160** — `service` (`CertificationConsoleService` composition root + access + reproducible evidence).
9. **TASK-000161** — `bootstrap` + `__init__` (composition root publishing versioned contracts) + full test suite + `EC2-EPIC-011-COMPLETION-REPORT.md`.

## 21. EXPLICIT NON-SCOPE

- **No live generation or EC-1 execution** (EPIC-012 Runtime Operations).
- **No new or modified certification criterion, verdict, ledger rule, severity, or evidence format** — `engine.certification` is consumed verbatim.
- **No `engine/**` modification; no fork or re-derivation of the Certification Layer or its ledger.**
- **No new capability group, role, permission, or classification model.**
- **No frozen-corpus write (DP-03); no server, socket, network, or file I/O; no wall-clock in identity/ordering.**
- **No mutation path** to any surfaced record, evidence, or ledger entry (append-only by construction).
- **No UI/presentation (L1)** — this epic realizes the L3 governed service surface only.

## 22. FINAL AUTHORIZATION VERDICT

**READY — IMPLEMENTATION AUTHORIZED.** All readiness conditions are met: prerequisites COMPLETE (EPIC-010) / CERTIFIED (`engine.certification`, `engine.validation`, EPIC-002); dependency set fully closed (§3); architecture available (contract §2.1 #10, PC-10/PC-13/PC-16, §4/§4.3, §5, P6); reuse anchors pre-exist (`CapabilityGroup.CERTIFICATION_LEDGER`, policy invariant ii, `ContractRef("engine.certification.certify","1.0.0")`); governance in force (GOV-004 lane + UCOS-EXEC-001 admission); controls operative (CI, determinism gate, TRACK-001, coverage gate); realization template proven (ten prior additive `platform/**` runtimes, including EPIC-010). No governance, registration, architecture, security, observability, runtime, or certification blocker remains.

*This determination authorizes no implementation work by itself; it identifies and authorizes the target. Implementation of `EC2-EPIC-011` proceeds only under per-epic admission consistent with the standing EXEC-001 conditions: additive-only over EC-1, 0 frozen-corpus writes (DP-03), determinism/reproducibility preserved (P5), fidelity preserved (P6), EC-1 integrity preserved (P10), TRACK-001 evidence→status (fail-closed).*

**END OF ARTIFACT — EC2-EPIC-011-DETERMINATION · IMPLEMENTATION AUTHORIZED · EVIDENCE-DERIVED · AUTHORITY-NEUTRAL**

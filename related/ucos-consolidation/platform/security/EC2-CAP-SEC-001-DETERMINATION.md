# EC2-CAP-SEC-001 — Security Runtime — Determination

| Field | Value |
|-------|-------|
| ARTIFACT ID | EC2-CAP-SEC-001 |
| ARTIFACT | Security Runtime Capability — Runtime Realization Determination |
| ARTIFACT TYPE | Determination artifact only (no implementation, no code, no services, no directories, no schemas) |
| PROGRAM | UCOS EC-2 Platform Realization Program |
| CLASSIFICATION | Platform determination — runtime realization of the existing constitutional security architecture |
| STATUS | ACTIVE — determination only |
| BRANCH | `governance-reconciliation` |
| BASELINE DATE | 2026-07-17 |
| CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY | NONE |
| HELD AUTHORITY | ENGINEERING-EXECUTION-ONLY |
| VOLUME (per GOV-006) | VOL-006 (PLATFORM / `PLT`) — `^platform/` category mapping |

*This artifact **determines and defines only** the executable runtime realization of the **already-established** constitutional security architecture of UCOS Ω∞. It **invents no security architecture, no security model, no security domain, no security authority, and no governance structure**; it creates no runtime code, no service, no registry, no schema, and no directory beyond this file's own location. Every construct it names traces to an existing, physical repository artifact. It is subordinate to the frozen corpus (`00-SOURCE/`, `99-FREEZE/`, `00-BOOK/` — read-only, DP-03), the `UNIVERSAL-SECURITY-ARCHITECTURE-CONSTITUTION` (ARCH-SECURITY-001), the EC-2 Platform Realization Program, and the certified EC-1 Realization Engine. Where any statement would conflict with a higher instrument, the higher instrument governs and the statement is void to the extent of the conflict. This determination carries the EC-1 provisional-state disclosure (`ENGINEERING-EXECUTION-ONLY`) verbatim and asserts no constitutional finality; the external gates EC-1…EC-6 remain open.*

---

## 1. EXECUTIVE SUMMARY

EC2-CAP-SEC-001 determines how the **Universal Security Architecture Constitution** (`ARCH-SECURITY-001`) and its four reconciled subject-layer security architectures (`DATA-014`, `SERVICE-014`, `APPLICATION-013`, `INFRASTRUCTURE-013`), the Master-Book zoning overlay (`UMB-015`), and the Security Intelligence overlay (`UKB-ADV-005`) are realized as a **governed, additive, record-only platform runtime** — the **Security Runtime** — without inventing any new security architecture.

The central architectural finding, drawn directly from canon, is:

> **The constitution defines the security model; the subject-layer architectures classify and record security requirements and are explicitly `NON-ENFORCING`; each of them defers *enforcement* to a "downstream `SECURITY`/`RUNTIME` concern consumed by reference." EC2-CAP-SEC-001 IS that downstream concern — but the runtime it realizes is itself record-only, authority-neutral, and non-ratifying.**

The Security Runtime therefore does **not** re-implement authentication or authorization (already realized and certified by the Identity Layer, `EC2-EPIC-002`), does **not** implement cryptographic or secret-management products (forbidden by the constitution and every subject layer), and does **not** create a second audit-of-record (already realized by the Observability Layer, `EC2-EPIC-013`). It **composes** those certified layers and adds only the *security-specific record/observe/classify/certify* machinery that no completed layer yet provides: security **intelligence** (findings, threats, controls, exceptions, pentest/compliance/audit evidence), security **registries**, security **observability** (the `security` signal dimension), security **classification-binding** (the enforcement-by-reference seam), security **zone/control posture**, and security **certification** — all append-only, deterministic, and derived only from evidence.

**Verdict: `EC2-CAP-SEC-001 READY FOR IMPLEMENTATION`** — see §12 and the Final Certification.

---

## 2. CONSTITUTIONAL INPUTS

All inputs were read completely and are physically present and `ACTIVE`.

| # | Input | Path | Role in this determination |
|---|-------|------|----------------------------|
| I-1 | Universal Security Architecture Constitution (`ARCH-SECURITY-001`) | `02-MASTER/UCOS-Ω∞-UNIVERSAL-SECURITY-ARCHITECTURE-CONSTITUTION.md` | **Primary authority.** 21 sections; the complete security domain model, registry model (§17), observability model (§15), testing model (§16), certification model (§18), failure conditions (§19), and the determination that **no security invention is authorized** (§21). |
| I-2 | Security Architecture — Five-Zone Model (`UMB-015`) | `00-BOOK/MASTER-BOOK/UMB-015-SECURITY-ARCHITECTURE.md` | Zoning/visibility/control overlay: five zones, seven controls, security-as-Signal, secrets-by-handle (RR-07). |
| I-3 | Security Intelligence Layer (`UKB-ADV-005`) | `00-BOOK/ADVANCEMENT/UKB-ADV-005-SECURITY-INTELLIGENCE-ARCHITECTURE.md` | Entity/edge/roll-up/signal model for findings, threats, controls, exceptions, pentest, compliance/audit evidence; secret-handling defense. |
| I-4 | Universal Data Security Architecture (`DATA-014`) | `10-DATA/DATA-014-UNIVERSAL-DATA-SECURITY-ARCHITECTURE.md` | Classification-only, non-enforcing; Classification-Label / Confidentiality-Record / Integrity-Record; enforcement deferred by reference. |
| I-5 | Universal Service Security Architecture (`SERVICE-014`) | `11-SERVICE/SERVICE-014-UNIVERSAL-SERVICE-SECURITY-ARCHITECTURE.md` | Evaluative, non-enforcing; Authentication/Authorization/Confidentiality/Integrity records; reuses `DATA-014` by reference. |
| I-6 | Universal Application Security Architecture (`APPLICATION-013`) | `12-APPLICATION/APPLICATION-013-UNIVERSAL-APPLICATION-SECURITY-ARCHITECTURE.md` | Evaluative, non-enforcing; reuses `DATA-014`/`SERVICE-014` by reference. |
| I-7 | Universal Infrastructure Security Architecture (`INFRASTRUCTURE-013`) | `13-INFRASTRUCTURE/INFRASTRUCTURE-013-UNIVERSAL-INFRASTRUCTURE-SECURITY-ARCHITECTURE.md` | Evaluative, non-enforcing; Isolation/Authn/Authz/Confidentiality/Integrity facets; reuses `DATA-014`/`SERVICE-014`/`APPLICATION-013` by reference. |
| I-8 | Security finding schema | `00-BOOK/SCHEMAS/finding.schema.json` | The physical schema for `UKB-ADV-005` entities (`UCOS-FND-NNNNNN`); the vocabulary the Security Runtime records against. |

### Runtime lineage inputs (completed / certified)

| # | Lineage artifact | Path | Status | Contribution |
|---|------------------|------|--------|--------------|
| L-1 | EXEC-REG-001 — Autonomous Execution Register (RUNTIME-006) | `00-BOOK/tools/ukb.py`; `00-BOOK/tools/connectors/execution.py` | ACTIVE | Append-only, record-only, evidence-derived register pattern; shared ONE identity authority (`id-ledger category_seq`). Also carries the `security` DOMAIN-D dimension default (`APPROVED`) and the `security` signal dimension. |
| L-2 | EC2-CAP-ADMIN-001 — Administration Runtime | `platform/administration/EC2-CAP-ADMIN-001-COMPLETION-REPORT.md` | COMPLETE | **The realization template** for a "CAP" runtime: additive, record-only, authority-derived, single identity authz seam, two-gate access, reuse-map, content-addressed IDs, 100% coverage, determinism fingerprint. |
| L-3 | EC2-EPIC-003 — Portal & Navigation | `platform/portal/EC2-EPIC-003-COMPLETION-REPORT.md` | COMPLETE | Consumption-surface pattern (ZONE-4); authorization-scoped views. |
| L-4 | EC2-EPIC-004 — Workspace & Collaboration | `platform/workspace/EC2-EPIC-004-COMPLETION-REPORT.md` | COMPLETE | `platform.workspace.isolation.tenants_isolated` tenant-isolation rule (reused, not duplicated). |
| L-5 | EC2-EPIC-013 — Observability & Monitoring | `platform/observability/EC2-EPIC-013-COMPLETION-REPORT.md` | COMPLETE | L8 telemetry + hash-chained append-only `AuditTrail` (audit of record); metrics/logs/traces/health/alerting. |
| L-6 | EC2-EPIC-002 — Identity & Access | `platform/identity/EC2-EPIC-002-COMPLETION-REPORT.md` | COMPLETE / CERTIFIED | L7 `AuthorizationService` — the **single access decision point**; the enforcement seam the constitution's Authn/Authz/Identity domains already realize. |
| L-7 | EC2-EPIC-001 — Platform Foundation | `platform/foundation/EC2-EPIC-001-COMPLETION-REPORT.md` | COMPLETE | Contracts, events, identity primitives, services registry, error taxonomy, `content_hash`. |
| L-8 | GOV-006 — Repository Governance Correction | `02-MASTER/UCOS-GOV-006-REPOSITORY-GOVERNANCE-CORRECTION-IMPLEMENTATION-REPORT.md` | ACTIVE | Category→volume mapping: `^platform/` ⇒ PLATFORM / `PLT` / VOL-006. Governs how this artifact registers. |
| L-9 | EC-2 Platform Realization Program | `06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md` | ESTABLISHED / ACTIVE | The governing execution contract: 8-layer architecture, §3.2 RBAC matrix, PC-01…PC-18, P1–P10 acceptance, certification classes, provisional-state disclosure. |

---

## 3. SECURITY CANON ANALYSIS

### 3.1 The constitution defines a complete, closed model (no invention possible)

`ARCH-SECURITY-001` establishes the **Universal Security Meta-Model** (§1): `Universe → Domain → Capability → Component → Data → Event → API → Workflow → Service → Application → Integration → Security`. Every Security Control must trace to a registered Universe, Domain, Capability, and Component; **no orphan security controls** are permitted. Section 21 is explicit: *"No security invention is authorized."* Therefore any runtime realization is confined to **executing what already exists** — precisely the scope of this determination.

### 3.2 The subject layers are classification-only and defer enforcement — this is the seam

All four subject-layer architectures converge on one rule, stated near-verbatim in each:

- `DATA-014` (DZA-01/03): *"Data security classifies and records; it grants no access and enforces nothing … Any enforcement (access/encryption) is a downstream `SECURITY`/`RUNTIME` concern consumed by reference; never defined here."*
- `SERVICE-014` (SSE-03; SSE-C2): evaluative-only; *"the act of authenticating/authorizing is a downstream implementation concern."*
- `APPLICATION-013` (SEC-03/04): *"Security is a decidable predicate … it enacts nothing … grants no access, issues no credential, and enforces no policy."*
- `INFRASTRUCTURE-013` (ISEC-01/04): *"every security facet is evaluative and non-enforcing … no enforcement is enacted; no access is granted."*

The Security Runtime is the named downstream concern. **But** the constitution's own Authority Boundary constrains that runtime: registries **record and never ratify/enact** (RG-02); mutations are timestamped, attributed, queryable (RG-05); no ratify/enact operation on any identity/authorization/trust/federated relationship (AR-04). The runtime realization is therefore an **evidence-derived, append-only, record/observe/classify/certify substrate that binds classification to the *already-existing* enforcement point (Identity L7) by reference** — not a new sovereign enforcement engine.

### 3.3 The enforcement point already exists and is certified

`EC2-EPIC-002` realized the L7 `AuthorizationService` as the **single, fail-closed access decision point** over the §3.2 RBAC matrix. This is the constitution's Identity (§4), Authentication (§5), and Authorization (§6) domains, executable and certified. The Security Runtime **consumes** this seam (as `EC2-CAP-ADMIN-001` did); it introduces no second authorization logic (no duplication — Constraint 6/7).

### 3.4 The intelligence, signal, and schema spine already exist

- The `security` signal **dimension** already exists in the corpus runtime tooling (`00-BOOK/tools/connectors/base.py` `DIMENSIONS`) and as a DOMAIN-D state default in `00-BOOK/tools/ukb.py`.
- A `security` **signal producer** already exists (`00-BOOK/tools/connectors/trivy.py`) emitting `BLOCKED`/`APPROVED` states with `critical`/`high`/`medium` metrics — matching `UKB-ADV-005` §4 roll-up.
- The **finding schema** is physical (`00-BOOK/SCHEMAS/finding.schema.json`) with the exact `finding_kind` vocabulary of `UKB-ADV-005`.

The platform Security Runtime **reuses this vocabulary by reference** and maintains platform-owned, additive, in-memory/metadata registries — it must **not** write into `00-BOOK/` (DP-03). This mirrors how L8 Observability maintains its own `AuditTrail` while reusing EC-1 telemetry discipline.

---

## 4. RUNTIME SCOPE DETERMINATION

### 4.1 In scope (record-only, additive, deterministic)

1. **Security classification binding** — bind the `DATA-014`/`SERVICE-014`/`APPLICATION-013`/`INFRASTRUCTURE-013` classification records (Authentication/Authorization/Confidentiality/Integrity/Isolation/Classification-Label) to platform constructs by reference, and resolve their declared enforcement obligation to the **existing** L7 `AuthorizationService` seam.
2. **Security intelligence** — record and roll up `UKB-ADV-005` entities: Threat Models, Security Controls, Vulnerabilities/Findings, Exceptions, PenTest Results, Compliance Evidence, Audit Evidence, against the `finding.schema.json` vocabulary; automatic evidence-derived roll-up (open CRITICAL/HIGH without valid Exception ⇒ `BLOCKED`).
3. **Security registries** (§17) — the seven record-only registries: Security, Identity, Threat, Risk, Evidence, Certification, Trust — append-only, timestamped, attributed, queryable (RG-05), never ratifying (RG-02).
4. **Security observability** (§15) — emit the `security` signal dimension and security telemetry (metrics/logs/traces) **through the L8 Observability Layer**; every security event reverse-traceable to its finding (UMB-015 §5).
5. **Security zone/control posture** (`UMB-015`) — record-only evaluation of the five-zone and seven-control posture; no zone/control is a compiled ceiling (policy configuration).
6. **Security certification** (§18) — record security certification objects, rolled into program certification; never inferred from source-asset coverage (STATUS-001 §2).

### 4.2 Explicitly out of scope (reused by reference — NO new realization)

| Constitutional domain | Why out of scope for new realization | Realized/consumed via |
|-----------------------|--------------------------------------|-----------------------|
| Identity (§4), Authentication (§5), Authorization (§6) | Already realized and certified as the L7 decision point | `platform.identity.AuthorizationService` (EC2-EPIC-002) |
| Secrets (§9) | SEC-04 mandates secrets by external handle only; runtime stores none | Foundation/Identity credential-by-reference discipline; `SECRET-LEAK` finding (UKB-ADV-005 §6) recorded, value never stored |
| Cryptography (§8) | No subject layer authorizes selecting a cipher/key/product; integrity is by content hash | `platform.foundation.contracts.content_hash` (integrity); classification-only records |
| Audit of record (§12/§14) | Already realized as the hash-chained append-only audit of record | `platform.observability.AuditTrail` (EC2-EPIC-013) |
| Tenant isolation | Already realized | `platform.workspace.isolation.tenants_isolated` (EC2-EPIC-004) |
| Policy administration / audit export | Already realized | `platform.administration` (EC2-CAP-ADMIN-001) |

### 4.3 Absolute boundary restatement

No new authority · no new security model · no new security domain · no new governance structure · no ratify/enact operation · no cryptographic/secret product · no second authorization logic · no second audit-of-record · no frozen-corpus write (DP-03) · additive over EC-1 and every prior EC-2 layer · provisional-state disclosure carried.

---

## 5. RUNTIME DOMAIN DETERMINATION (Constitutional → Runtime mapping)

For every required constitutional domain: Constitution Source · Runtime Responsibility · Required Components · Required Services · Required Registries · Required Telemetry · Required Evidence · Required Readiness Gates. "By reference" means realized by an existing certified layer and consumed, not rebuilt.

| Domain | Constitution source | Runtime responsibility | Required components | Required services | Required registries | Required telemetry | Required evidence | Readiness gate |
|--------|---------------------|------------------------|---------------------|-------------------|---------------------|--------------------|-------------------|----------------|
| **Identity** | §4; §3.2 matrix | Reference the certified identity model; classify identity assurance | (by ref) `Principal`, `PrincipalRegistry` | (by ref) `AuthorizationService` | Identity Registry (S17) — record-only mirror/view | `security` signal on identity-assurance findings | Access decisions (identity evidence) reused | EC2-EPIC-002 CERTIFIED ✅ |
| **Authentication** | §5 | Classify authn posture; record assurance level | (by ref) `Session`, `SessionRegistry` | (by ref) `AuthorizationService.establish_session` | — (records into Security Registry) | authn-posture finding signals | session/decision evidence | EC2-EPIC-002 CERTIFIED ✅ |
| **Authorization** | §6; §3.2 | Bind subject-layer Authorization-Records to the L7 seam; record decisions | (by ref) `AccessDecision`, `CapabilityGroup`, `PermissionEngine`, `PolicyEngine` | (by ref) `AuthorizationService.authorize` | — | `identity.access.evaluated` audit event (reused) | authorization-derived action set | EC2-EPIC-002 CERTIFIED ✅ |
| **Trust** | §7 | Record trust boundaries/anchors/chains; preserve provisional-boundary flags (IP-05) | Trust record (record-only) | Security Runtime service (new, record-only) | **Trust Registry** (S17) | trust-relationship signals | trust records (append-only) | Foundation events ✅; SEC-REG design |
| **Cryptography** | §8 | Classify crypto posture; integrity by content hash; **select no product** | (by ref) `content_hash` | (by ref) Foundation contracts | — (Integrity-Records via SEC-CLASS) | integrity-verification signals | content-addressed integrity evidence | Foundation ✅ |
| **Secrets** | §9; SEC-04; RR-07 | Store **no** secret value; classify handles; raise `SECRET-LEAK` findings | Secret-handle classification (record-only) | (by ref) Identity credential-by-reference | Evidence Registry (leak findings, location only) | `SECRET-LEAK` finding signals | leak findings referencing location only | Identity ✅; UKB-ADV-005 §6 |
| **Privacy** | §10 | Reference `DATA-014` PII/confidentiality classification; record purpose/retention posture | (by ref) `DATA-014` Confidentiality-Record | Security Runtime service (record-only) | Security Registry | privacy-posture signals | classification records (by ref) | DATA-014 ACTIVE ✅ |
| **Threat Management** | §11; UKB-ADV-005 | Record Threat Models, correlate findings, drive roll-up, govern exceptions | Threat/Finding/Exception records (`finding.schema.json`) | **Security Intelligence service** (new, record-only) | **Threat Registry**, **Risk Registry** | Trivy/DAST/SCA `security` signals (reused dimension) | findings + roll-up state | finding.schema.json physical ✅ |
| **Security Governance** | §12 | Record policies/standards/controls/ownership/evidence; **never ratify/enact** (RG-02) | Control/Policy/Conformance records | (by ref) `platform.administration` policy | Security Registry, Evidence Registry | governed-action signals (reused L8) | append-only governance records | ADMIN-001 ✅ |
| **Security Registries** | §17 | The seven record-only registries; RG-05 mutation discipline | Registry record types | **Security Registry service** (new, record-only) | **all seven** (S17) | registry-mutation signals | append-only, attributed, queryable entries | Foundation registries ✅; SEC-REG design |
| **Security Traceability** | §14 | Backward/forward/control/evidence/risk/threat/compliance/certification traceability | Trace edges over records | Security Runtime service | (all registries) | trace-link signals | reverse-traceable finding→scan links (UMB-015 §5) | UKB-ADV-005 edges ✅ |
| **Security Observability** | §15 | Emit `security` signals + telemetry through L8; readiness fails without telemetry (PL-02) | (by ref) `MetricRegistry`, `LogBuffer`, `TraceRecorder` | (by ref) `ObservabilityService` | — | **`security` dimension** (canon) | telemetry on 100% of security actions | EC2-EPIC-013 ✅ |
| **Security Testing** | §16 | Gate merges with security/identity/authz/crypto/privacy/compliance tests (CD-02) | Test suites (`platform/tests/test_security_*`) | (by ref) pytest + coverage gate | — | test-result signals | ≥90% coverage gate, suite green | EC-2 CI discipline ✅ |
| **Security Certification** | §18 | Record security certification objects; roll into program certification | Certification records | **Security Certification service** (new, record-only) | **Certification Registry** | certification-decision signals | immutable, evidence-backed records | STATUS-001 §2 ✅ |

**Coverage:** all fourteen required constitutional domains are mapped; none is unaddressed; none requires an invented model. Nine map to existing certified layers by reference; five require net-new **record-only** runtime machinery.

---

## 6. RUNTIME DECOMPOSITION DETERMINATION

The mission's example decomposition (`SEC-IDN`, `SEC-AUTHN`, `SEC-AUTHZ`, `SEC-TRUST`, `SEC-CRYPTO`, `SEC-SECRETS`, `SEC-THREAT`, `SEC-OBS`, `SEC-REG`) is **explicitly not assumed**. Determined from canon, most of those example units would **duplicate** already-certified layers (Constraint 6) — `SEC-IDN`/`SEC-AUTHN`/`SEC-AUTHZ` are the Identity Layer; `SEC-CRYPTO`/`SEC-SECRETS` are forbidden as product realizations and reduce to classification + hashing already present. The correct decomposition is driven by **what requires net-new record-only realization** versus **what is reused by reference**.

### 6.1 Determined decomposition — EC2-CAP-SEC-001 **is decomposed** into six record-only sub-capabilities

| Sub-capability | Name | Constitutional basis | Net-new? | Notes |
|----------------|------|----------------------|----------|-------|
| **SEC-CLASS** | Security Classification Binding Runtime | §4–§11 + subject layers DATA/SERVICE/APPLICATION/INFRASTRUCTURE | Yes (record-only) | The enforcement-by-reference seam: binds classification records to the L7 decision point; enacts nothing itself. |
| **SEC-INTEL** | Security Intelligence Runtime | §11; `UKB-ADV-005`; `finding.schema.json` | Yes (record-only) | Findings/threats/controls/exceptions/pentest/compliance/audit evidence + automatic roll-up. |
| **SEC-REG** | Security Registry Runtime | §17 | Yes (record-only) | The seven registries; RG-02/RG-05 discipline. |
| **SEC-OBS** | Security Observability Runtime | §15; UMB-015 §5 | Reuse+thin | `security` signal dimension + telemetry via L8; adds security-specific signal shaping only. |
| **SEC-CERT** | Security Certification Runtime | §18 | Yes (record-only) | Security certification records; rolls into program certification. |
| **SEC-ZONE** | Zone & Control Posture Runtime | `UMB-015` §1–§2 | Yes (record-only) | Five-zone/seven-control posture evaluation, policy-configured, non-compiled. |

### 6.2 Reused-by-reference (declared non-goals — NOT sub-capabilities)

Identity/Authentication/Authorization → `platform.identity`; Secrets → SEC-04 by-reference + `SECRET-LEAK` finding; Cryptography → `content_hash` + classification-only; Audit-of-record → `platform.observability.AuditTrail`; Tenant isolation → `platform.workspace`; Policy administration/audit export → `platform.administration`.

---

## 7. DEPENDENCY DETERMINATION

### 7.1 Upstream runtime dependencies

| Dependency | Component consumed | Runtime contract | Registration requirement | Governance requirement | Telemetry requirement | Audit requirement |
|------------|--------------------|------------------|---------------------------|------------------------|-----------------------|-------------------|
| **Execution Register (EXEC-REG-001)** | `security` dimension + DOMAIN-D state | record-only signal dimension (RUNTIME-006) | none (read/emit by reference) | append-only, one identity authority | `security` signals | append-only, attributed |
| **Foundation (EC2-EPIC-001)** | `content_hash`, `EventBus`, `Principal`/`Permission`, `ServiceDescriptor`/`ServiceRegistry`, `PlatformError` | `platform_contract` / `ContractRef` (PL-05) | publish Security Runtime contracts into `ServiceRegistry` | contract-first, versioned | governed events on bus | content-addressed IDs |
| **Identity (EC2-EPIC-002)** | `AuthorizationService` (L7 seam), `AccessDecision`, `CapabilityGroup`, `PermissionEngine`, `PolicyEngine`, `SessionRegistry` | `identity.access.evaluated` audit event | none (sole decision point; no new grants) | least-privilege; §3.2 matrix unchanged | reuse access telemetry | reuse decision log |
| **Observability (EC2-EPIC-013)** | `ObservabilityService`, `AuditTrail`, `MetricRegistry`, `LogBuffer`, `TraceRecorder`, `HealthRegistry`, `AlertEngine` | governed-action telemetry contract | register health checks into L8 | audit of record is L8's, not duplicated | 100% of security actions observed | append-only hash-chained |
| **Workspace (EC2-EPIC-004)** | `platform.workspace.isolation.tenants_isolated` | tenant-isolation rule | none | cross-tenant security refused | isolation-violation signals | isolation decisions audited |
| **Administration (EC2-CAP-ADMIN-001)** | policy / audit-export surface | administration contracts | none | policy administered here, not re-invented | reuse admin telemetry | reuse admin audit |
| **Portal (EC2-EPIC-003)** | consumption/scoped-view pattern (ZONE-4) | read-only projection | none | never mutates canon | view-access signals | read access audited |

### 7.2 Dependency direction (SEC §13)

All dependencies point **inward/downward only** (AR-01). The Security Runtime depends on Foundation, Identity, Observability, Workspace, Administration, Portal, and the corpus signal spine; **nothing depends on it** yet. No cyclic or upward dependency exists. External scanner dependencies (Trivy/OWASP/ZAP/SonarQube) are consumed as **signal producers by reference**, pinned and vetted (DE-04), never embedded.

### 7.3 Dependency readiness

Every upstream runtime dependency is **COMPLETE or CERTIFIED**. There is no missing upstream layer — this is the decisive readiness fact (see §11).

---

## 8. REGISTRY DETERMINATION (§17)

The seven constitutional registries are realized as **append-only, record-only, attributed, queryable** platform registries (RG-05), each **never ratifying/enacting** (RG-02), each backed by content-addressed IDs (`content_hash`), and **none writing to `00-BOOK/`** (DP-03).

| Registry | Constitution | Records | Reuses / mirrors |
|----------|--------------|---------|------------------|
| Security Registry | §17 | security assets, controls, policies (record-only) | Foundation registry pattern |
| Identity Registry | §17; §4 | identity/assurance classifications (view over L7) | `PrincipalRegistry` (by ref) |
| Threat Registry | §17; §11 | Threat Models, correlated findings | `finding.schema.json` vocabulary |
| Risk Registry | §17 | risk classifications, exception roll-ups | UKB-ADV-005 roll-up |
| Evidence Registry | §17; §14 | pentest/compliance/audit evidence, `SECRET-LEAK` (location only) | UKB-ADV-005 §2/§6 |
| Certification Registry | §17; §18 | security certification records | STATUS-001 §2 discipline |
| Trust Registry | §17; §7 | trust boundaries/anchors/chains + provisional flags (IP-05) | Foundation events |

**No eighth registry is introduced.** IDs use new, non-colliding content-addressed prefixes (e.g. `UCOS-SFND`, `UCOS-STRUST`, `UCOS-SREG`, `UCOS-SCERT`) allocated via the reused `content_hash` — no new identity scheme or allocator (identity-preservation, per ADMIN-001 §10 pattern).

---

## 9. TELEMETRY DETERMINATION (§15)

- **Signal dimension:** the existing `security` dimension (canon: `base.py` `DIMENSIONS`, `ukb.py` DOMAIN-D) is emitted; **no new dimension is created**.
- **Transport:** all metrics/logs/traces flow through the L8 `ObservabilityService`; the Security Runtime adds no second telemetry stack.
- **Coverage:** telemetry on **100% of security actions** (P9 analogue); a security control lacking required telemetry **fails readiness** (PL-02; constitution §15).
- **Traceability:** every security event is reverse-traceable to the scan/finding that raised it (UMB-015 §5; UKB-ADV-005 edges).
- **Roll-up:** evidence-derived only (open CRITICAL/HIGH without valid Exception ⇒ `BLOCKED`); exceptions auto-expire on `expires < now`; **no security status entered by hand** (UKB-ADV-005 §4).
- **Determinism:** no wall-clock in any identity or fingerprint; caller-supplied logical `tick`/`now` (per ADMIN-001/EPIC-013 discipline).

---

## 10. TESTING DETERMINATION (§16)

Realization must ship, at minimum, the constitution's nine test facets, under the EC-2 CI discipline (`--cov-fail-under=90`, ruff clean, determinism gate):

| Facet (§16) | Test focus |
|-------------|------------|
| Security | end-to-end record/observe/certify flow |
| Penetration | pentest-evidence recording + retest state |
| Vulnerability | finding ingest, severity, SLA, roll-up to `BLOCKED` |
| Identity | classification binding to L7 (by reference; fail-closed) |
| Authorization | authorization-derived action set; no new grants |
| Cryptographic | integrity via `content_hash`; no product selection |
| Privacy | `DATA-014` confidentiality classification by reference |
| Compliance | compliance/audit-evidence recording |
| Certification | security certification records + roll-up |

Additional required suites: Registry (append-only/attributed/queryable; RG-02 non-enact), Telemetry integration (100% coverage), Determinism verification (cross-process fingerprint), EC-1/prior-layer integrity preservation (full suite green). Target: **100% module coverage** on `platform/security/**` (ADMIN-001/observability precedent).

---

## 11. CERTIFICATION DETERMINATION (§18)

Security certification reuses the EC-2 certification discipline (evidence-backed, record-only, immutable, append-only, fail-closed, non-constitutive) and maps to the program's certification classes:

| Class | Criterion | Security Runtime obligation |
|-------|-----------|-----------------------------|
| PLAT-C1 | capability operational & access-controlled | Security Runtime contracts published; authorization-scoped |
| P2 | Identity & Access | adds no authority; all access via certified L7 seam |
| P3 | Workspace/tenant integrity | cross-tenant security refused via reused isolation |
| P5 | Determinism | reproducible security evidence fingerprint |
| P9 / OP-C3 | Observability & Audit | 100% of security actions telemetered + audited (L8) |
| P10 | EC-1 integrity | 0 `engine/**` edits; 0 corpus writes; full suite green |
| §19 failure conditions | each security control has Identity/Trust/Traceability/Testing/Observability/Certification/Governance | else the control **fails generation** and produces a Gap Report |

Security certification is **never inferred from source-asset coverage** (STATUS-001 §2) and asserts **no** operational/production security of any running system beyond recorded evidence.

---

## 12. READINESS DETERMINATION

**State: `READY FOR IMPLEMENTATION`.**

### 12.1 Readiness conditions and evidence

| # | Readiness condition | Status | Evidence |
|---|---------------------|--------|----------|
| R-1 | Constitutional model complete and `ACTIVE` | ✅ | `ARCH-SECURITY-001` (21 §), 4 subject layers, `UMB-015`, `UKB-ADV-005` all `ACTIVE`/physical |
| R-2 | No invention required (closed model) | ✅ | §21 constitution; §5 mapping covers all 14 domains without new models |
| R-3 | Enforcement seam exists and is certified | ✅ | `platform.identity.AuthorizationService` (EC2-EPIC-002 CERTIFIED) |
| R-4 | Audit-of-record exists | ✅ | `platform.observability.AuditTrail` (EC2-EPIC-013 COMPLETE) |
| R-5 | Tenant isolation exists | ✅ | `platform.workspace.isolation.tenants_isolated` (EC2-EPIC-004) |
| R-6 | Policy/administration surface exists | ✅ | `platform.administration` (EC2-CAP-ADMIN-001 COMPLETE) |
| R-7 | Security signal dimension + producer exist | ✅ | `base.py` `DIMENSIONS`, `ukb.py` DOMAIN-D, `connectors/trivy.py` |
| R-8 | Finding schema physical | ✅ | `00-BOOK/SCHEMAS/finding.schema.json` |
| R-9 | Realization template proven | ✅ | `EC2-CAP-ADMIN-001` record-only CAP pattern |
| R-10 | Governance/volume mapping resolved | ✅ | GOV-006: `^platform/` ⇒ PLATFORM/VOL-006 |
| R-11 | Determinism + coverage discipline available | ✅ | EC-2 CI (`--cov-fail-under=90`, ruff, determinism gate) |
| R-12 | Boundary (record-only, non-ratifying) definable | ✅ | RG-02/AR-04/DP-03/SEC-04 encodable as in §4.3 |

**No readiness condition is unmet.** There is no missing upstream layer, no undefined schema, no unresolved authority, and no required invention.

### 12.2 Conditions that MUST hold during implementation (readiness caveats, not blockers)

1. **DP-03:** the runtime must write **nothing** to `00-BOOK/`, `00-SOURCE/`, `99-FREEZE/`, `engine/**`, or any `02-MASTER/**` artifact; it maintains platform-owned registries only.
2. **RG-02 / AR-04:** the runtime exposes **no** ratify/enact operation on identity/authorization/trust/federated relationships; all registries are record-only.
3. **No duplication:** it must consume Identity, Observability, Workspace, and Administration seams — never re-implement authentication, authorization, audit-of-record, or isolation.
4. **SEC-04 / RR-07:** it stores no secret value; secret handles are classified and leaks are recorded by location only.
5. **No product selection:** no cipher/key/IAM/PKI/DLP product is chosen (subject-layer prohibition).
6. **Provisional-state disclosure** carried on every artifact and record.

---

## 13. IMPLEMENTATION PREPARATION ROADMAP

*(Preparation only — no code, service, directory, or schema is created by this determination.)*

### 13.1 Runtime structure (proposed, additive package `platform/security/`)

```
platform/security/
  errors.py          EC2-SEC-* taxonomy over platform.foundation.errors.PlatformError
  contracts.py       versioned security contract surface + finding vocabulary refs
  classification.py  SEC-CLASS: bind DATA-014/SERVICE-014/APPLICATION-013/INFRASTRUCTURE-013 records; L7-by-reference
  intelligence.py    SEC-INTEL: findings/threats/controls/exceptions/pentest/compliance/audit + roll-up
  registries.py      SEC-REG: the seven §17 registries (append-only, RG-02/RG-05)
  observability.py   SEC-OBS: security signals/telemetry via L8 ObservabilityService
  zones.py           SEC-ZONE: UMB-015 five-zone / seven-control posture (record-only)
  certification.py   SEC-CERT: security certification records
  service.py         SecurityRuntimeService composition root + SecurityEvidence
  bootstrap.py       bootstrap_security (composes identity + observability + workspace + administration + security)
```

### 13.2 Module structure

Each module: immutable, typed, deterministic, serializable; content-addressed IDs via reused `content_hash`; fail-closed; no wall-clock in identities/fingerprints; governed events on the Foundation `EventBus`.

### 13.3 Registry structure

Seven §17 registries as append-only record stores keyed by content-addressed IDs; every mutation timestamped (logical `tick`), attributed (principal by reference), queryable; RG-02 non-enact enforced structurally (no ratify/enact method exists).

### 13.4 Telemetry structure

`security` dimension emitted through L8; metric/log/trace per security action; 100% coverage assertion; reverse-traceable finding→scan links; evidence-derived roll-up.

### 13.5 Testing structure

`platform/tests/test_security_{classification,intelligence,registries,observability,zones,certification,service,bootstrap}.py` covering §16's nine facets + registry + telemetry + determinism + EC-1 integrity; ≥90% gate, target 100% module coverage.

### 13.6 Certification structure

`SecurityEvidence` (deterministic fingerprint) → program certification roll-up mapping to PLAT-C1/P2/P3/P5/P9/OP-C3/P10; §19 failure-condition guard produces a Gap Report on any control missing a required facet.

### 13.7 Integration structure

Single `bootstrap_security(context)` composition root binding to `PlatformContext`; publishes security contracts into the `ServiceRegistry`; registers health checks into L8; authorizes exclusively through the L7 `AuthorizationService`; isolates via `tenants_isolated`; emits a deterministic `security.bootstrap.completed` event.

---

## 14. GAP ANALYSIS

| # | Gap | Severity | Resolution | Blocker? |
|---|-----|----------|------------|----------|
| G-1 | No dedicated "Security" epic in the EC-2 program's 14 epics | Informational | Security is cross-cutting by design; realized as a CAP over existing layers exactly like `EC2-CAP-ADMIN-001` | No |
| G-2 | `security` roll-up currently lives in corpus tooling (`00-BOOK/tools`), not the platform | Design | Platform runtime reuses the vocabulary/schema **by reference** and keeps its own additive registries; must not write `00-BOOK` (DP-03) | No |
| G-3 | Constitution requires enforcement "at every layer" while subject layers are non-enforcing | Resolved | Enforcement is the certified L7 seam; the Security Runtime binds classification to it by reference and records — it does not create a new enforcement engine | No |
| G-4 | Cryptography/secrets domains name mechanisms no layer authorizes building | Bounded | Realized as classification + `content_hash` integrity + secret-handle-by-reference + `SECRET-LEAK` findings; no product selected | No |
| G-5 | No `EC2-CAP-SEC-001` implementation authority statement beyond the constitution + EC-2 program | Informational | Same posture as ADMIN-001 (self-authorizing CAP over completed layers); this determination records engineering-execution readiness only, no constitutional authority | No |

**No blocking gap exists.**

---

## 15. FINAL DETERMINATION

EC2-CAP-SEC-001 is determined to be the **runtime realization of the existing constitutional security architecture** as a **governed, additive, deterministic, record-only Security Runtime** decomposed into six record-only sub-capabilities (`SEC-CLASS`, `SEC-INTEL`, `SEC-REG`, `SEC-OBS`, `SEC-CERT`, `SEC-ZONE`), composing the certified Identity, Observability, Workspace, Administration, and Foundation layers, reusing the existing `security` signal spine and `finding.schema.json` vocabulary by reference, inventing no security architecture/model/domain/authority/governance structure, and writing nothing to the frozen corpus. All fourteen constitutional security domains map to executable runtime responsibilities with complete traceability; all upstream runtime dependencies are COMPLETE or CERTIFIED; the enforcement seam, audit-of-record, isolation rule, signal dimension, and finding schema all physically exist; and the realization template is proven.

**Supporting evidence:** §2 (physical inputs + lineage), §3 (canon analysis), §5 (14/14 domain mapping), §7.3 (all dependencies COMPLETE/CERTIFIED), §12.1 (12/12 readiness conditions met), §14 (0 blocking gaps).

---

## EC2-CAP-SEC-001 READY FOR IMPLEMENTATION

*Engineering-execution readiness only. Determination artifact — no runtime code, service, directory, or schema created; no architectural invention; complete constitutional traceability; complete dependency analysis. Carries the EC-1 provisional-state disclosure verbatim; asserts no constitutional finality; the external gates EC-1…EC-6 remain open. Implementation is authorized to proceed only additively, record-only, and subordinate to every higher instrument named in the header.*

---

## STATUS-001 VALIDATION SELF-CHECK (R1–R5)

| Rule | Result | Evidence |
|------|--------|----------|
| R1 Declaration | ✅ | Determination scope + authoritative basis declared in header and §2. |
| R2 Domain isolation | ✅ | Asserts a **determination** (DOMAIN-A/engineering) only; claims no operational-security state of any running system; all source artifacts labelled INPUT, never COMPLETION. |
| R3 Claim completeness | ✅ | Supplies domain (security runtime), unit (EC2-CAP-SEC-001), evidence (physical files in §2), basis (constitution + EC-2 program + completed layers). |
| R4 Evidence physicality | ✅ | Rests on physical files: the 8 constitutional inputs, 9 lineage artifacts, and this file under `platform/security/`. |
| R5 Append-only | ✅ | New file; no constitution, frozen artifact, engine module, or numbering modified. |

**END OF ARTIFACT — EC2-CAP-SEC-001 · DETERMINATION · ACTIVE · APPEND-ONLY · AUTHORITY-NEUTRAL · READY FOR IMPLEMENTATION**

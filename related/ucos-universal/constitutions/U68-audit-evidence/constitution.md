# U68 — Audit & Evidence Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U68-audit` |
| Layer | Trust Plane (cross-cutting) |
| Domain | 08 Governance |
| Steward | `ucos:org:internal-audit-platform` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P0 (audit log, chain), P1 (evidence collectors), P5 (auditor portal, external anchoring) |
| Depends on | U65 Security (keys, signing), U13 Temporal (retention, schedules), U16 Context, U73 Infrastructure (WORM storage) |
| Depended on by | everything (L13); U74 Certification, U67 Compliance, U01 Authority (decisions), U66 Privacy (DSR evidence) |
| Master references | §19.9, §20.6, L13, §28.3 |

> Audit & Evidence owns **the immutable record of what happened and the proof that obligations are met**. **AuditRecords** are append-only, hash-chained entries for every command, decision, access, policy evaluation, AI action, approval and deployment. **Evidence** consists of immutable artefacts proving a control, test or certification criterion, produced by **EvidenceCollectors**. It also owns verification of chain integrity and controlled auditor access.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| AUD-L1 | Every state-changing command and every policy decision on restricted data produces an AuditRecord **in the same request path** (synchronous append, or the command fails). | Command bus integration; no bypass in SDK. |
| AUD-L2 | Audit records are append-only, hash-chained per (tenant, day) and anchored daily to WORM storage. | Storage permissions (no UPDATE/DELETE grant); chain verifier. |
| AUD-L3 | Audit records contain references and hashes, not sensitive values. Payload snapshots for restricted data are stored encrypted, separately, with their own retention. | Schema; DLP check on audit stream. |
| AUD-L4 | Reading audit data is itself audited. | Read path writes access records. |
| AUD-L5 | Evidence is immutable, timestamped, signed, and linked to the control, test and subject it proves. | Evidence store (content-addressed) + signature. |
| AUD-L6 | Retention of audit and evidence follows the longest applicable legal requirement and supports legal hold. | Retention rules from U66/U67; hold flags. |

---

## 2. Ontology

- **Concepts:** `AuditRecord`, `AuditChain` (per tenant per day), `ChainAnchor`, `AuditQuery` / `AuditExport`, `Evidence`, `EvidenceCollector`, `EvidencePack` (bundle for an audit or certification), `AuditorAccessGrant`.
- **Audit levels:** `standard` (all writes, auth events, decisions), `full` (adds reads of restricted data and payload snapshots), `sampled` (reads of non-restricted data at a configured rate). The level per action comes from policy obligations (U03) and the security profile (U65).

---

## 3. Objects

### 3.1 `ucos.audit.AuditRecord` (normative)
| Field | Type | Notes |
|---|---|---|
| `id` | ULID | time-ordered |
| `seq` | Integer | per chain, gapless |
| `time` | TimePoint | server time |
| `tenant` | TenantRef | `platform` for control-plane |
| `actor` | `{identity, kind, onBehalfOf?, sessionId, acr}` | |
| `action` | String | `<slug>:<Command|Query>` or system action |
| `resource` | `{type, id, version?}` | |
| `decision` | `{ effect, policies: [ids], obligations: [..] }` | |
| `result` | `success|failure|denied` + error code | |
| `contextHash` | bytes | hash of ContextEnvelope |
| `requestHash` | bytes | canonical request hash |
| `changes` | `{ fields: [names], beforeHash, afterHash }` | no values |
| `payloadRef` | EncryptedPayloadRef | 0..1 (full level only) |
| `traceId` | String | |
| `prevHash` | bytes | |
| `hash` | bytes | SHA-256(prevHash ‖ canonical(record without hash)) |

### 3.2 `ChainAnchor`
`{ tenant, day (LocalDate UTC), lastSeq, rootHash, signedBy: KeyRef (audit-chain signing key), signature, anchoredTo: [worm://…, rfc3161://tsa?], at: TimePoint }`

### 3.3 `ucos.audit.Evidence`
| Attribute | Type | Notes |
|---|---|---|
| `id` | UGID (`ucos:evidence:`) | |
| `kind` | `test-result|scan-report|config-snapshot|log-extract|attestation|document|screenshot|approval|sbom|metric-snapshot` | |
| `subject` | Reference (control, blueprint, pack, tenant, cell) | |
| `proves` | Array<{control?: ControlRef, gate?: GateRef, criterion}> | |
| `collector` | Reference→EvidenceCollector | |
| `period` | TimeRange | period it covers |
| `contentRef` | content-addressed object (sha256) | encrypted if confidential |
| `summary` | `{ result: pass|fail|partial, metrics }` | |
| `signature` | in-toto/DSSE envelope | |
| `collectedAt` | TimePoint | |
| `retention` | RetentionRuleRef | |
| `legalHold` | Boolean | |

### 3.4 `EvidenceCollector`
```yaml
id: ec.dsr-completion-log
source: query:privacy.dsr-requests(status=completed, period)
schedule: "FREQ=DAILY"           # Temporal trigger
produces: { kind: log-extract, proves: [ucos.ctrl.dsr-erasure] }
freshnessSLO: P2D                # evidence older than this → control "stale"
owner: U66-privacy
```

### 3.5 `EvidencePack`
`{ id, purpose: certification|external-audit|customer-request|regulator, scope: {tenant?, frameworks, controls, period: TimeRange}, items: [EvidenceRef], index (generated), signature, sharedWith: [AuditorAccessGrantRef], expires }`

### 3.6 `AuditorAccessGrant`
`{ auditor: IdentityRef (external, federated or invited), scope: {tenant, frameworks, period: TimeRange, evidencePacks}, validity (≤ P90D), watermark: true, approvals: DecisionRef }`

---

## 4. Commands, Queries, APIs

| Command | Notes |
|---|---|
| `Append(record)` | internal only (command bus, PDP, gateway, workflow, AI gateway); returns seq + hash |
| `AnchorChains(day)` | scheduled at 00:15 UTC; signs, writes to WORM; `audit.chain.anchored` |
| `VerifyChain(tenant, range)` | recompute hashes, verify anchors → report; scheduled daily, on demand |
| `CollectEvidence(collector)` | triggered by schedule or event |
| `AssembleEvidencePack(scope)` | for audits/certification |
| `GrantAuditorAccess`, `RevokeAuditorAccess` | |
| `PlaceLegalHold(scope)`, `ReleaseLegalHold` | level ≥ 3 (legal) |

**Queries:** `SearchAudit(filters: tenant, actor, action, resource, result, time range)` (paginated, results audited), `ResourceHistory(resourceId)`, `ActorActivity(identity, range)`, `EvidenceFor(control|gate, period)`, `ControlEvidenceStatus(tenant)` (fresh/stale/missing).

```text
GET  /v1/audit/records?tenant=&actor=&action=&resource=&from=&to=     (W16)
GET  /v1/audit/chains/{tenant}/{day}:verify
GET  /v1/audit/evidence?control=&period=        POST /v1/audit/evidence-packs
POST /v1/audit/auditor-grants                   POST /v1/audit/legal-holds
POST /v1/audit/exports   (signed, watermarked; approval required for > 10k records)
```
**Errors:** `AUD_APPEND_FAILED` (causes command failure: fail-closed), `AUD_CHAIN_BROKEN` (P1 incident), `AUD_ACCESS_DENIED`, `AUD_EXPORT_APPROVAL_REQUIRED`, `AUD_LEGAL_HOLD_ACTIVE`.

---

## 5. Rules & Architecture
- **Write path:** the command bus appends to a per-cell audit log service backed by Postgres (partitioned by tenant and day, insert-only role), with an asynchronous replica to WORM object storage (S3 Object Lock, compliance mode). Append p99 is < 5 ms. If the audit store is unavailable, writes fail closed (AUD-L1). Reads continue.
- **Chain construction:** one chain per (tenant, UTC day) per cell, so ordering stays local. The daily cell root combines the per-tenant roots (Merkle tree), so any single tenant's chain can be proven without revealing others.
- **Retention defaults** (overridden by jurisdiction rules): audit records 7 years for financial actions and 2 years otherwise; evidence for 3 audit cycles (≥ 3 years). Legal hold suspends deletion.
- **Decision tables:** `audit.read-sampling-rate`, `audit.retention-by-action-class`, `audit.export-approval-threshold`.

---

## 6. Security & Compliance
- Audit data is `confidential`. Payload snapshots are `restricted`.
- The audit-chain signing key is HSM-backed and rotated yearly, with old keys kept for verification.
- Separation of duties: platform engineers cannot read tenant audit content without a support case and tenant approval (U03 policy).
- Controls: logging and monitoring (ISO A.8.15, PCI DSS 10.x, SOC 2 CC7.2), log integrity (PCI 10.3.4), record retention (SEC 17a-4 style for brokerage tenants via WORM), and evidence for every framework in U67.

## 7. Validation & Reuse
- Universes never write their own audit tables; they use the SDK.
- Compliance controls MUST name an EvidenceCollector (gate `CMP-EVID-01`).
- Certifications reference evidence only through `Evidence` ids.

## 8. Gaps & Evolution
```prolog
gap(control_without_collector, C) :- control(C), active(C), not evidence_collector_for(C, _).
gap(evidence_stale, T, C)         :- applies(C, T), latest_evidence_age(C, T, A), freshness_slo(C, S), A > S.
gap(chain_unverified, T, D)       :- chain(T, D), not verified(T, D), age_days(D, N), N > 2.
gap(audit_level_mismatch, T)      :- tenant(T), profile(T, regulated), audit_read_level(T, sampled).
```
- **Self-healing:** if the WORM replication backlog grows, replication workers scale and alerts fire. A broken chain is a P1 incident: freeze, forensic copy, determine scope. Repair is impossible by design; a signed `ChainBreakReport` is appended instead.
- **Evolution:** public transparency-log anchoring (e.g. Sigstore Rekor-like) for tenants who need third-party verifiability.

## 9. AI
- **AI uses:** natural-language audit search ("who changed payout settings last week?"), translated into structured queries and audited. Also evidence-gap explanations and evidence-pack index drafting.
- **AI actions** are themselves audited with prompt hash, model id, tools called and output hash (master §21.5).
- **Agents** never get bulk export rights.

## 10. Operations
- **Signals:** `audit_append_latency_ms`, `audit_append_failures_total` (alert on > 0), `worm_replication_lag_s`, `chain_verify_failures_total` (must be 0), `evidence_freshness_ratio{framework}`, `auditor_sessions_active`.
- **SLOs:** append availability 99.99%; a search over 30 days of one tenant p95 < 3 s.

## 11. UI
- **Views:** master W16 (audit explorer with chain verification badges), `audit.resource.history` (timeline on every object page; the "Audit" tab), `audit.evidence.library` (by framework and control, freshness), `audit.evidence-pack.builder`, `audit.auditor.portal` (read-only, watermarked, scoped).

## 12. Scale
About 50k audit appends/s per large cell, roughly 4 billion records per day platform-wide at full scale. Hot data sits in Postgres for 90 days. Older data is Parquet in WORM object storage, queryable via Trino with tenant-scoped views. T0 for the append path.

## Appendix
- **C.** 0.1.0.

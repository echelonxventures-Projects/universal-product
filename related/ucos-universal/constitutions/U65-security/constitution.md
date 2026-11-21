# U65 — Security Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U65-security` |
| Layer | Trust Plane (cross-cutting) |
| Domain | 08 Governance |
| Steward | `ucos:org:ciso-office` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P0 (keys, classification, baselines, findings), P2 (SOC automation), P5 (continuous validation at scale) |
| Depends on | U01 Authority, U03 Policy, U09 Identity, U68 Audit, U73 Infrastructure, U57 Capability (supply chain), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | every universe (classification, encryption, controls), U67 Compliance (control implementations), U74 Certification (SEC gates) |
| Master references | §19 (whole section), L11, L19 |

> Security owns **the protection model and its machinery**: data classification, key and secret management, encryption services, security baselines and profiles, security controls (as testable objects), threat models, vulnerability and finding management, security incidents, and continuous security validation. Access rules belong to U03 Policy, identities to U09, and audit records to U68. This universe owns *what must be protected, how strongly, with which keys, and whether that is actually true*.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| SEC-L1 | Every field, object type, event and file carries a classification. Unclassified data is treated as `restricted` until classified. | META-L7; SDK defaults; DLP scan. |
| SEC-L2 | Encryption in transit (TLS 1.3 / mTLS) and at rest everywhere. `restricted` fields use application-level field encryption with tenant-scoped keys. | Admission policies, SDK `Encrypted<T>`, certification `SEC-ENC-*`. |
| SEC-L3 | Keys never leave KMS/HSM in plaintext except as short-lived DEKs in memory. Every key has an owner, purpose, rotation schedule and destruction policy. | Key registry; KMS policies. |
| SEC-L4 | No secret is stored in code, config, images, logs or tickets. Workloads get secrets through workload identity. | Secret scanning in CI, at runtime (log scrub) and in repos; gate `SEC-SECRETS-01`. |
| SEC-L5 | Critical/high vulnerabilities and findings have bounded remediation SLAs. A breach of SLA creates a mandatory gap on affected blueprints. | Finding SLA engine + U75 rules. |
| SEC-L6 | Security controls are objects with automated tests and evidence. A control without a passing test is not "implemented". | Control registry + U68 evidence. |
| SEC-L7 | Security baselines cannot be weakened by tenants. Tenants may only choose a stricter profile. | Profile ordering enforced by the composer. |

---

## 2. Ontology

- **Concepts:** `Classification` (value type), `DataClass`, `SecurityProfile`, `SecurityControl`, `Key`, `KeyPolicy`, `SecretRef`, `ThreatModel`, `Finding` (vulnerability / misconfiguration / pentest / bug bounty / detection), `SecurityIncident`, `ValidationRun` (DAST, attack simulation), `SecurityException` (= a U02 Waiver of a security gap).
- **Confidentiality levels:** `public < internal < confidential < restricted`.
- **Data classes:** `PII, SPI, PCI, PHI, FINANCIAL, CREDENTIAL, CHILD, BIOMETRIC, LOCATION, TRADE_SECRET, SECURITY_SENSITIVE` (master §19.7).
- **Security profiles (tenant-selectable, ordered):** `standard < high < regulated < sovereign`.

| Control area | standard | high | regulated | sovereign |
|---|---|---|---|---|
| Business-user MFA | TOTP or passkey | passkey | passkey + hardware for admins | hardware keys |
| Tenant isolation tier minimum | pooled | pooled | schema | dedicated-cell |
| Keys | platform-managed per tenant | per tenant | BYOK option | HYOK / in-country HSM |
| Admin session max | 12 h | 8 h | 4 h | 2 h |
| Audit read logging | sampled | full for restricted | full | full + external anchoring |
| Pen-test cadence | annual (platform) | annual | semi-annual + per major | quarterly |
| Data residency | per law | per law | strict | strict + sovereign cloud |

---

## 3. Objects

### 3.1 `Classification` (value type, amendment A-01)
`{ confidentiality, dataClasses: [..], handling?: [no-export, no-ai-training, no-log, watermark] }`

### 3.2 `ucos.security.Key`
| Attribute | Type | Notes |
|---|---|---|
| `id` | UGID (`ucos:key:`) | |
| `kind` | `kek|dek-template|signing|tls|token-signing|hmac` | |
| `scope` | `{ tenant?, purpose (field-encryption|event-encryption|backup|audit-chain|context-signing|jwt), dataClass? }` | |
| `provider` | `aws-kms|gcp-kms|azure-kv|vault-transit|hsm:<id>|byok:<tenant-kms>` | |
| `algorithm` | e.g. `AES-256-GCM`, `ECDSA-P256`, `Ed25519`, `ML-KEM-768+X25519` (hybrid) | crypto-agility id |
| `rotation` | TemporalPolicyRef / Duration (default P90D signing, P365D KEK) | |
| `state` | `pre-active|active|decrypt-only|destroyed|compromised` | |
| `externalRef` | provider key ARN/id | |
| `owner` | PartyRef | |

### 3.3 `SecretRef`
`{ id, path: vault://…, owner: capability|connector, rotation, lastRotated: TimePoint, consumers }` — secret values are never stored in UCOS objects.

### 3.4 `SecurityControl`
```yaml
id: ucos.sec.field-encryption-restricted
title: "Restricted fields are encrypted at application level with tenant keys"
area: cryptography
appliesTo: { dataClasses: [PCI, SPI, PHI, CREDENTIAL] }
profiles: [standard, high, regulated, sovereign]
implementation: [kernel.sdk.encrypted-field, U65.key-service]
tests:
  - id: test.sec.encrypted-at-rest-sample      # samples DB pages, asserts ciphertext for restricted columns
    schedule: "FREQ=DAILY"
evidenceCollector: ec.db-encryption-sampler
mappings: [PCI-DSS:3.5.1, ISO27001:A.8.24, SOC2:CC6.1, HIPAA:164.312(a)(2)(iv)]
severityIfFailing: critical
```

### 3.5 `ThreatModel`
`{ id, subject: capability|blueprint|universe, method: STRIDE|LINDDUN (privacy)|PASTA, dataFlows (diagram ref), assets, threats: [{ id, category, description, likelihood, impact, mitigations: [ControlRef], residualRisk }], reviewedBy, reviewedAt, nextReview }` — required per pack (gate `SEC-TM-001`).

### 3.6 `Finding`
| Attribute | Type | Notes |
|---|---|---|
| `id` | UGID | |
| `source` | `sca|sast|dast|container|iac|cspm|pentest|bug-bounty|detection|manual` | |
| `subject` | pack@version / image / cell / blueprint / tenant config | |
| `severity` | `critical|high|medium|low|info` (CVSS v4 + context) | |
| `exploitability` | `{ kev: bool, epss, reachable: bool }` | |
| `status` | `new|triaged|accepted-risk|in-remediation|fixed|verified|false-positive` | |
| `slaDue` | TimePoint (from decision `security.finding-sla`: critical P7D, high P30D, medium P90D) | |
| `waiver` | Reference→governance.Waiver | 0..1 |

### 3.7 `SecurityIncident`
`{ id, severity SEV1–4, category, detectedAt, declaredAt, commander, affected: {tenants, dataClasses, records}, timeline, containmentActions: [DecisionRef], notificationClocks: [SLAClockRef], status, postmortem }`. Notification clocks come from Compliance decision `compliance.breach-notification` per jurisdiction (e.g. GDPR 72 h to authority, CERT-In 6 h, DPDP "without delay").

---

## 4. Commands, Queries, APIs & Services

| Command | Notes |
|---|---|
| `ClassifyField|Type|Event` (via U04/U61 proposals) | |
| `CreateKey`, `RotateKey`, `DisableKey`, `DestroyKey` (crypto-shred; level 4 + legal-hold check) | events `security.key.*` |
| `RegisterSecret`, `RotateSecret` | |
| `RecordFinding`, `TriageFinding`, `AcceptRisk` (→ waiver) , `VerifyFix` | |
| `DeclareIncident`, `Contain(action)`, `CloseIncident` | |
| `SetSecurityProfile(tenant, profile)` | only upgrades without level-4 approval |
| `RunValidation(scope)` | DAST, attack simulation, config scan |

**Services:**
- **Key Service:**
  - `Encrypt(purpose, tenant, plaintext)` and `Decrypt`, with envelope encryption, a DEK cache of ≤ 5 min and per-request audit for restricted data;
  - `Sign`, `Verify` and `GetJWKS`;
  - `Tokenize` and `Detokenize` (format-preserving, for PAN-like data when PSP tokens are unavailable), restricted by policy.
- **Classification Service:** `ClassificationOf(type, field)`, `HandlingFor(classification) → {encrypt, mask, retention hints, logRedaction}`.
- **DLP Service:** scans logs, exports and files for patterns of restricted classes. Actions are block, redact or alert.

```text
POST /v1/security/keys            POST /v1/security/keys/{id}:rotate|:disable|:destroy
POST /v1/security/findings        POST /v1/security/findings/{id}:triage|:accept-risk|:verify
POST /v1/security/incidents       POST /v1/security/incidents/{id}/actions
GET  /v1/security/posture?tenant= (controls pass/fail, open findings, profile)
```
**Errors:** `SEC_KEY_STATE_INVALID`, `SEC_LEGAL_HOLD_BLOCKS_DESTROY`, `SEC_PROFILE_DOWNGRADE_FORBIDDEN`, `SEC_UNCLASSIFIED_DATA`, `SEC_SECRET_IN_PAYLOAD`.

---

## 5. Rules
- **Handling matrix (normative, enforced by the SDK and obligations):**

  | Class | Encrypt field | Mask in UI by default | Log | AI use | Export |
  |---|---|---|---|---|---|
  | public / internal | no | no | yes | yes | yes |
  | confidential | no (at-rest disk encryption) | partial | redacted values | tenant opt-in | policy |
  | restricted (PII high, SPI, PCI, PHI, CREDENTIAL, BIOMETRIC, CHILD) | **yes** | yes | never | only zero-retention models with tenant policy and purpose | approval + watermark |

- **Key hierarchy:** root keys in HSM → per-cell KEKs → per-tenant KEKs → per-purpose DEKs. Crypto-shredding a tenant destroys the tenant KEK. Crypto-shredding a subject (DSR) destroys the per-subject DEK, where the subject-keyed encryption mode is enabled for that data class.
- **Decision tables:** `security.finding-sla`, `security.profile-requirements` (the matrix in §2), `security.session-limits`.

---

## 6. Compliance mapping (summary)
ISO 27001 Annex A (5.x organisational, 8.x technological), SOC 2 CC6–CC7, PCI DSS v4 req. 3, 4, 6, 8, 10, 11, NIST CSF 2.0 (PR, DE, RS), HIPAA Security Rule, CERT-In directions, DORA ICT risk. Each mapping is a `ControlMapping` in U67, and evidence comes from U68.

## 7. Validation & Reuse
- Packs never implement crypto primitives. They use the SDK (`Encrypted<T>`, `security.Sign`).
- Gates `SEC-*` (master §28.2) are defined here: threat model, scans clean within SLA, SBOM, signature, secrets scan, classification complete, and encryption test.

## 8. Gaps & Evolution
```prolog
gap(unclassified_field, T, F)      :- field(T, F), not classified(F).
gap(finding_sla_breached, B, F)    :- in_blueprint_subject(B, S), finding(F, S), open(F), past_sla(F), not waived(F).
gap(control_failing, B, C)         :- applies(C, B), control_status(C, B, failing).
gap(key_rotation_overdue, K)       :- key(K), active(K), rotation_overdue(K).
gap(threat_model_stale, P)         :- pack(P), threat_model_age_days(P, D), D > 365.
gap(profile_requirement_unmet, T, R) :- tenant(T), profile(T, P), requires(P, R), not satisfied(T, R).
```
- **Self-healing (L3 runbooks):** a compromised credential triggers token revocation and session kill. A leaked secret triggers rotation plus a scan of usage. A detection on a tenant (e.g. mass export anomaly) triggers temporary read throttling and an alert.
- **Evolution:** PQC migration plan (hybrid KEX now; ML-DSA signatures for audit anchoring and JWT when the ecosystem supports it), managed through key `algorithm` ids and rotation.

## 9. AI
- **AI uses:** finding triage (reachability and exploitability summaries), threat-model drafting from manifests, detection tuning, incident timeline summarisation.
- **AI security controls:** prompt-injection isolation, output filtering, and data-class-aware routing are enforced through the AI gateway (U49) using this universe's handling matrix.
- **Agents may:** triage (propose), open incidents, and execute L3 containment runbooks.
- **Agents may not:** destroy keys, accept risk, or downgrade profiles.

## 10. Operations
- **Signals:** `findings_open{severity}`, `mttr_findings_days{severity}`, `controls_failing{area}`, `key_rotation_overdue_total`, `dlp_blocks_total`, `secrets_detected_total`, `incidents_open{sev}`.
- **SLOs:** Key Service encrypt/decrypt p99 < 3 ms (DEK cached), availability T0 at 99.99%. A security revocation is effective in ≤ 15 min.

## 11. UI
- **Views:** `security.posture` (per tenant and platform: profile, controls, findings, keys), `security.findings.board`, `security.incident.room` (timeline, clocks, actions, comms), `security.key.inventory`, `security.threat-model.editor`, `security.classification.map` (all fields by class, linked to U04).

## 12. Scale
Key operations reach about 200k/s per cell with DEK caching. Findings number in the millions (SCA). KMS has multi-region replicas where residency allows, and per-jurisdiction HSMs for sovereign tenants. T0 for key paths.

## Appendix
- **A.** Format-preserving tokenisation is needed only for non-PSP flows; confirm scope in P2.
- **B. Amendments:** A-01 confirmed (Classification ValueType). Master §19.7 gains security profiles and the handling matrix.
- **C.** 0.1.0.

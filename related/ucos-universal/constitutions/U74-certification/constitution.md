# U74 — Certification Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U74-certification` |
| Layer | L12 Certification, Evolution & Autonomy |
| Domain | 12 Architecture |
| Steward | `ucos:org:quality-certification` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P0 (gates engine, ARCH/SEC/TEST/GAP gates), P1 (CMP, A11Y, DOC, OBS), P2 (PERF, DR at scale), P3 (AI gates) |
| Depends on | U68 Audit & Evidence, U75 Gap, U65 Security, U67 Compliance, U01 Authority, U02 Governance, U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U57 Capability (pack publish), U58 Composition/U73 Infra (activation guard), U04 Meta (definition publish), U51 Agent |
| Master references | §28 (whole section), L9, L10 |

> Certification owns **the decision that something is fit to be used**: gate definitions, certification runs, certification records (signed attestations), validity and re-certification triggers, and badges. It consumes test results and evidence (U68), gaps (U75) and controls (U65/U67). It does not run business tests itself. Test harnesses run in CI and cells and report evidence. Its own output is a **signed attestation** that a stated set of criteria passed for a stated subject.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| CERT-L1 | No definition, pack, agent or blueprint becomes `Certified` unless every applicable gate passes or is waived by an authority (U01/U02). | Registry state guard. |
| CERT-L2 | Certification is evidence-based: every gate result links to Evidence ids. A result without evidence is a fail. | Gate engine. |
| CERT-L3 | Certifications expire, and are invalidated by material change. | Validity + invalidation triggers (§5.2). |
| CERT-L4 | Gate definitions are versioned definitions under Governance. Weakening a gate is a significant change. | U02 classification rule. |
| CERT-L5 | Certification records are signed (in-toto/DSSE) by the certification service key and verifiable offline. | Signing via U65. |

---

## 2. Ontology

- **Concepts:** `CertificationGate`, `GateCriterion`, `CertificationProfile` (which gates apply to which subject kind and tier), `CertificationRun`, `GateResult`, `Certification` (record), `Badge`.
- **Subject kinds:** `object-type`, `capability-pack`, `adapter`, `rule-module`, `policy-set`, `ui-view`, `agent`, `model`, `blueprint`, `cell`, `kernel-release`.
- **Gate families** (master §28.2): `ARCH`, `SEC`, `CMP`, `TEST`, `PERF`, `A11Y`, `DOC`, `OBS`, `DR`, `AI`, `GAP`, plus universe-specific gates (`ARCH-TMP-*`, `ARCH-CUR-*`, `ARCH-CTX-*`, `SEC-ID-*`, …) contributed by universe specs.

---

## 3. Objects

### 3.1 `CertificationGate`
```yaml
id: SEC-007
family: SEC
title: "No open critical or high vulnerabilities beyond SLA"
appliesTo: [capability-pack, kernel-release, blueprint]
criteria:
  - id: c1
    check: query                      # query | evidence-present | test-suite | manual-attestation
    expr: "count(findings{subject=$subject, severity in [critical,high], status!=fixed, pastSla=true}) == 0"
    evidence: { collector: ec.sca-scan, maxAge: P1D }
waivable: { maxLevelRequired: 4, maxDuration: P30D }
severity: blocking                     # blocking | advisory
version: 1.2.0
owner: U65-security
```
`check` types:
- `query`: evaluated over registry, findings and signals.
- `evidence-present`: fresh evidence exists with `summary.result=pass`.
- `test-suite`: CI or cell test run results.
- `manual-attestation`: a signed attestation by a named authority. Used sparingly, e.g. for an external pen-test sign-off.

### 3.2 `CertificationProfile`
`{ subjectKind, tier?, securityProfile?, gates: [GateRef@range], recertifyEvery: Duration }`. Examples:
- `pack.T1`: all ARCH, SEC, TEST and DOC gates; PERF at the declared scale; OBS; a pen-test attestation within P365D; recertify every P180D.
- `blueprint.regulated`: everything, plus `CMP` per framework, `DR` drills, and `GAP-000`; recertify every P90D.

### 3.3 `CertificationRun`
`{ id, subject (ref@version|hash), profile, trigger: publish|activation|schedule|invalidation|manual, startedAt: TimePoint, status: running|passed|failed|passed-with-waivers, results: [GateResult], durationS }`

### 3.4 `GateResult`
`{ gate@version, criterion, result: pass|fail|waived|not-applicable|error, evidence: [EvidenceRef], details, waiver?: WaiverRef, evaluatedAt: TimePoint }`

### 3.5 `Certification` (record)
The schema is master §28.3, extended with `profile`, `subjectDigest`, `validFrom`, `validUntil`, `invalidatedBy?: {event, at: TimePoint}`, `attestation: DSSE envelope (in-toto Statement with predicate ucos.io/certification/v1)`, and `approvedBy: DecisionRef` (required for blueprints and T0/T1 packs).

### 3.6 `Badge`
A derived display object: `{ subject, level: certified|certified-with-waivers|expired|revoked, label, validUntil: TimePoint }`. It appears on marketplace listings, Studio and registries.

---

## 4. Commands, Queries, APIs

| Command | Notes / Events |
|---|---|
| `DefineGate`, `DefineProfile` (via Governance) | |
| `StartRun(subject, profile, trigger)` | orchestrates criterion evaluations (parallel), collects evidence refs → `certification.run.completed` |
| `IssueCertification(run)` | if all blocking pass/waived; signs; for blueprints requires DecisionRef → `certification.issued` |
| `Invalidate(subject, reason)` | automatic by triggers or manual → `certification.invalidated` |
| `Revoke(certification, reason)` | authority level ≥ 3 → `certification.revoked` |
| `VerifyAttestation(bundle)` | offline-verifiable |

**Queries:** `StatusOf(subject)`, `WhyFailed(run)`, `ExpiringWithin(days)`, `CoverageByFramework(tenant)`.

```text
POST /v1/certification/runs              GET /v1/certification/runs/{id}
GET  /v1/certification/status?subject=   POST /v1/certification/attestations:verify
GET  /v1/certification/gates?family=     GET /v1/certification/expiring?days=30
```
**Errors:** `CERT_GATE_FAILED`, `CERT_EVIDENCE_MISSING`, `CERT_EVIDENCE_STALE`, `CERT_APPROVAL_REQUIRED`, `CERT_SUBJECT_CHANGED` (digest mismatch during run).

---

## 5. Rules

### 5.1 Profile selection
The subject kind, then the tier (from the blueprint or pack manifest), then the security profile, select the most specific profile. Rules live in decision table `certification.profile-selection`.

### 5.2 Invalidation triggers (normative)
| Trigger | Invalidates |
|---|---|
| Subject digest change (new version / new blueprint hash) | that subject (new run needed) |
| A pack in the blueprint revoked or certification expired | blueprint |
| New critical vulnerability past SLA in a component | pack + blueprints using it |
| Control drift to `failing` (U67) for an applicable control | blueprint |
| Waiver expired | the certification relying on it |
| Gate definition major version increased | subjects certified under the old version (grace: P30D) |
| `validUntil` reached | subject |

Invalidation of an **active** blueprint does not stop it immediately. It creates a mandatory gap with an SLA (decision `certification.invalidation-grace`, default P7D, P1D for security). The tenant and platform get alerts. An expired grace escalates to the governance authority, which decides on restriction (feature degrade or freeze of changes) and does **not** shut down automatically.

### 5.3 Run orchestration
Criteria run in parallel with a per-criterion timeout. An `error` result is retried 3 times, then becomes a fail. Runs are reproducible: the same subject digest and evidence set give the same result.

---

## 6. Security & Compliance
- The certification service key is HSM-backed. Attestations are logged to the audit store and optionally to a transparency log.
- Certification records are `internal`; tenant blueprint certifications are `confidential`.
- Supports SOC 2 CC8.1 (change authorisation evidence), ISO A.8.29 (security testing in development and acceptance), PCI DSS 6.2/11, and ISO 42001 (AI system verification) through AI gates.

## 7. Validation & Reuse
- Every universe spec contributes its gates (`ARCH-<SLUG>-nn`) to the gate registry.
- CI pipelines call `StartRun` and never decide pass or fail locally.
- Marketplace, Studio and the activation guard read `StatusOf`.

## 8. Gaps & Evolution
```prolog
gap(uncertified, S)           :- in_blueprint(S), not certified(S).
gap(certification_expiring, S):- certified(S), expires_in_days(S, N), N < 14.
gap(certification_invalidated, B) :- active_blueprint(B), invalidated(B), in_grace(B).
gap(gate_without_owner, G)    :- gate(G), not owner(G, _).
```
- **Self-healing:** scheduled re-certification runs start automatically 14 days before expiry. Passing runs renew without human action, except subjects that need a DecisionRef.
- **Evolution:** continuous certification. Certification is treated as a live state derived from continuous evidence, with runs replaced by incremental evaluation as evidence arrives.

## 9. AI
- **AI uses:** failure explanations and fix suggestions, plus evidence summarisation for approvers.
- **AI gates** (`AI-*`): eval score ≥ threshold, guardrails configured, red-team suite pass, model card present, and authority bounded (U51/U49 contribute these).
- **Agents** cannot issue or revoke certifications.

## 10. Operations
- **Signals:** `cert_runs_total{result,subjectKind}`, `cert_run_duration_s`, `certifications_expiring_30d`, `invalidations_total{trigger}`, `blueprints_in_grace`.
- **SLOs:** pack minor-version certification run p95 < 60 min (excluding long perf tests); blueprint certification p95 < 30 min given fresh evidence.

## 11. UI
- **Views:** master W6 (gates strip), `certification.run.detail` (criteria, evidence links, waivers, signature verification), `certification.registry` (by subject, with badges and expiry), `certification.gate.catalog`, `certification.expiry.calendar`.

## 12. Scale
Thousands of runs per day. Stateless orchestrator with evidence lookups. Control plane, T1. The activation guard reads `StatusOf` from a cell cache (T0).

## Appendix
- **B. Amendments:** master §28.3 Certification record gains `profile`, `subjectDigest` and DSSE attestation. §28.2 gains the invalidation-grace rule (no automatic shutdown).
- **D. Attribute definitions (A-74).** `Certification { id, subject: UGID, subjectDigest: string, profile: string, gates: [GateResult], waivers: [UGID], validFrom: TimePoint, validUntil: TimePoint, invalidatedBy?: {event, at: TimePoint}, attestation: string (DSSE envelope, in-toto predicate ucos.io/certification/v1), signedBy: UGID, approvedBy?: UGID (DecisionRecord; required for blueprints and T0/T1 packs), status: valid|expiring|invalidated|revoked }`
- **C.** 0.1.0.

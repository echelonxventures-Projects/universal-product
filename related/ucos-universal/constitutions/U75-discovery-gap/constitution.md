# U75 — Discovery & Gap Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U75-gap` |
| Layer | L12 Certification, Evolution & Autonomy |
| Domain | 12 Architecture |
| Steward | `ucos:org:platform-kernel-composer` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P0 (gap model, rule library, scans, reports), P1 (fix catalog, Studio UX), P5 (continuous discovery questions at scale) |
| Depends on | U58 Composition (engine), U05 Ontology, U57 Capability, U68 Audit (evidence status), U72 Observability (usage and runtime facts), U02 Governance (waivers), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U74 Certification (`GAP-000`), U58 (activation guard), U76 Evolution (inputs), Builder Studio, Platform Console |
| Master references | §11.6, §29.5, L10, L20 |

> Discovery & Gap owns **knowing what is missing, overlapping, conflicting, stale or wrong**: the `Gap` model and taxonomy, the **gap rule library** (contributed by every universe, curated here), scans (at composition, on change, scheduled), `GapReport`s, the **fix catalog** (machine-applicable remedies), waiver linkage, and the continuous discovery questions of master §29.5. The rules run in the Composition engine (U58). This universe owns the rules' governance, the gap lifecycle and the reporting.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| GAP-L1 | Every gap has kind, severity, subject, explanation (rule + premises) and at least one suggested fix, or `fix: manual` with owner. | Gap schema validation. |
| GAP-L2 | Severity is computed by rule, not chosen by a person. Downgrading requires a waiver (U02). | Gap severity is read-only. |
| GAP-L3 | `MANDATORY` gaps block activation and certification (L10). | `GAP-000` gate + activation guard. |
| GAP-L4 | Gap rules are tested definitions (fixture PDs and expected gaps) owned by a universe. | Rule module tests required (U58 CMP-L5). |
| GAP-L5 | Gaps are deduplicated by (kind, subject, ruleId, bindings hash) and keep a lifecycle. They are never silently dropped; a gap that disappears is `resolved` with a cause. | Gap store. |

---

## 2. Ontology

### 2.1 Gap kinds (master §11.6, normative list)
`CAPABILITY, DOMAIN, OBJECT, RELATIONSHIP, WORKFLOW, DECISION, POLICY, SECURITY_CONTROL, COMPLIANCE_CONTROL, DATA, INTEGRATION, API, UI, AI, TEST, DOCUMENTATION, OBSERVABILITY, RESILIENCE, INFRASTRUCTURE, GOVERNANCE, CERTIFICATION, TRACEABILITY, FAILURE_SCENARIO, USER_JOURNEY, PERFORMANCE, SCALABILITY, COST`, plus discovery kinds: `DUPLICATION, OVERLAP, CONFLICT, OBSOLESCENCE, UNUSED, UNDERPERFORMANCE, OPPORTUNITY`.

### 2.2 Severity
| Severity | Effect |
|---|---|
| `MANDATORY` | blocks activation/certification |
| `RECOMMENDED` | blocks certification unless waived |
| `OPTIONAL` | advisory |
| `INSIGHT` | discovery output (e.g. opportunity), feeds Evolution only |

Severity is computed by the decision table `gap.severity` over `(kind, subject tier, security profile, data classes, regulatory flag, blast radius)`, with defaults set by the contributing rule.

### 2.3 Scan types
`composition` (every compose), `on-change` (event-driven: definition published, pack revoked, refdata release, finding opened, control drift, certification expiring), `scheduled` (nightly full scan per active blueprint, weekly discovery questions), `on-demand` (Studio / CLI `ucos gaps`).

---

## 3. Objects

### 3.1 `ucos.gap.Gap`
| Attribute | Type | Notes |
|---|---|---|
| `id` | `GAP-<seq>` + UGID | |
| `kind` | GapKind | |
| `severity` | Severity (computed) | |
| `subject` | Reference (blueprint, PD, tenant, pack, type, cell, control …) | |
| `scope` | `{ tenant?, blueprint?, universe? }` | |
| `title` | LocalizedText | generated from rule template |
| `explanation` | `{ rule: RuleRef@v, bindings, premises: [fact ids / derivation refs], plain: LocalizedText }` | "Why?" |
| `fixes` | Array<FixRef + parameters> | ordered by effort |
| `owner` | PartyRef | from universe steward or tenant role mapping |
| `firstSeen`, `lastSeen` | TimePoint | |
| `status` | `open|in-progress|waived|resolved|obsolete` | |
| `resolution` | `{ cause: fixed|rule-changed|subject-removed|waived, by, at: TimePoint, evidence? }` | |
| `waiver` | WaiverRef | 0..1 |
| `dueBy` | TimePoint | from decision `gap.sla` by severity |
| `dedupKey` | hash | GAP-L5 |

### 3.2 `GapRule` (contributed in RuleModules, U58)
```yaml
id: gap.cmp.dpdp.consent-notice
module: rules.compliance.india-privacy@1.2
kind: COMPLIANCE_CONTROL
defaultSeverity: MANDATORY
datalog: |
  gap(compliance_control, T, ctrl:consent-notice) :- tenant(T), in_scope(T, jur:IN), processes(T, pii), not implemented(T, ctrl:consent-notice).
titleTemplate: "Consent notice required for India (DPDP 2023)"
explainTemplate: "DPDP 2023 applies because you operate in {jurisdiction} and process personal data. Control {control} is not implemented."
fixes: [fix.add-capability(privacy.consent), fix.configure-notice]
owner: U67-compliance
tests: [fixtures/india-basic.yaml → expect gap present; fixtures/india-with-consent.yaml → expect absent]
```

### 3.3 `Fix` (catalog)
```yaml
id: fix.add-capability
params: { capability: CapabilityRef }
effect: pd.capabilities.include += capability
effort: config           # config | ai-assisted | human-task | engineering (new pack)
automatable: true
requiresApproval: inherit # from change class of resulting proposal
preview: compose-diff     # show blueprint diff before applying
```
Seed fixes: `add-capability`, `choose-implementation`, `assign-cell`, `split-role` (SoD), `add-policy-from-template`, `apply-default-alert-policy`, `translate-keys` (AI and review), `draft-docs` (AI), `generate-tests`, `configure-calendar`, `create-tax-registration-task`, `upgrade-pack`, `request-pack-build` (engineering, routed to backlog), `request-waiver`.

### 3.4 `GapReport`
The schema is master §11.6, plus `scanType`, `snapshot`, `summary by kind × severity`, `newSinceLast`, `resolvedSinceLast` and `trend`.

### 3.5 `DiscoveryFinding` (INSIGHT-level outputs)
`{ question: what-exists|missing|duplicated|overlapping|conflicting|obsolete|insecure|non-compliant|under-governed|under-performing|should-evolve|should-retire|should-create, subject, evidence (signals, counts), suggestion, confidence }` — sent to U76 Evolution as input.

---

## 4. Commands, Queries, APIs

| Command | Notes / Events |
|---|---|
| `Scan(scope, type)` | runs rule modules via U58 engine over current facts (+ runtime facts from U72/U68) → GapReport → `gap.scan.completed` |
| `ApplyFix(gap, fix, params)` | creates change via Governance (or PD edit in Studio) → recompose → gap auto-resolves if fixed |
| `AssignGap(gap, owner)`, `CommentGap` | |
| `RequestWaiver(gap)` | delegates to U02 |
| `RegisterGapRule` (via Governance, inside a RuleModule) | |

**Queries:** `OpenGaps(scope, filters)`, `GapTrend(scope, range)`, `Why(gap)`, `WhatIfFix(gap, fix)` (compose preview), `DiscoveryAnswers(question, scope)`.

```text
POST /v1/gaps/scans                   GET  /v1/gaps?scope=&kind=&severity=&status=
GET  /v1/gaps/{id}                    GET  /v1/gaps/{id}/why
POST /v1/gaps/{id}/fixes/{fixId}:preview|:apply
POST /v1/gaps/{id}:assign|:request-waiver
GET  /v1/discovery?question=missing&scope=tenant:bazaar
```
**CLI:** `ucos gaps <blueprint|pd> [--severity mandatory] [--format json]` exits non-zero if mandatory gaps exist (used in CI).
**Errors:** `GAP_FIX_NOT_APPLICABLE`, `GAP_RULE_INVALID`, `GAP_SCAN_TIMEOUT`.

---

## 5. Rules

### 5.1 Runtime facts available to gap rules
Beyond registry facts, scans import runtime facts as EDB:
- `instance_count(Type, N)`, `usage(Capability, Calls30d)` and `slo_status(Capability, ok|burning|breached)` from U72;
- `latest_evidence_age(Control, Tenant, Age)` from U68;
- `finding(…)` from U65;
- `bundle_age_minutes(Cell, M)` from U03;
- `drift_items(Cell, N)` from U73.

### 5.2 The discovery questions (normative mapping)
| Question | Rule families |
|---|---|
| What is missing? | all `gap(missing_*)` and `required ∧ ¬available` rules |
| Duplicated / overlapping? | ontology similarity (U05), provides-collisions (U57), parallel taxonomies (U06), duplicate parties backlog (U11) |
| Conflicting? | capability conflicts, policy analyser results (U03), temporal overlaps (U13), compliance precedence conflicts |
| Violates law/architecture/security/compliance? | lint results, SEC/CMP control status, residency |
| Obsolete / unused? | `unused_type`, deprecated in use, zero-usage capabilities for 90 days |
| Under-performing? | SLO breaches, cost per outcome outliers |
| Should be created? | unresolved Studio intents, zero-result marketplace searches, repeated waivers of the same gap across tenants |

### 5.3 Decision tables
- `gap.severity`
- `gap.sla` (MANDATORY P7D in production blueprints, P1D for security; RECOMMENDED P30D)
- `gap.owner-routing` (kind × universe → steward or tenant role)

---

## 6. Security & Compliance
- Tenant gap reports are `confidential`, because they expose weaknesses. Security-kind gaps are `restricted` and visible only to security roles and the tenant security admin.
- Audit covers gap status changes and fix applications.
- Supports risk-based management of nonconformities (ISO 27001 clause 10.2) and evidence of continuous monitoring (SOC 2 CC4.1).

## 7. Validation & Reuse
- Every universe spec Section 8 contributes rules here, so the library grows with each spec.
- Rules use the shared predicate vocabulary (`required_capability`, `in_scope`, `tenant`, `applies`, `implemented`, `available`, `certified`…), documented in `spec/rules/core/vocabulary.md` (generated from the engine).
- The Studio, CLI, CI and Console all read the same reports.

## 8. Gaps about gaps
```prolog
gap(rule_without_fix, R)        :- gap_rule(R), not has_fix(R).
gap(gap_sla_breached, G)        :- gap(G), open(G), past_due(G).
gap(repeated_waiver, K, N)      :- waived_gap_kind_across_tenants(K, N), N > 20.     % signals a missing platform capability
```

**Evolution:** `repeated_waiver` and `should-create` findings feed U76 proposals, for example a new capability pack or a new default.

## 9. AI
- **AI uses:** plain-language explanations, fix ranking, clustering of gaps into work packages, and drafting AI-assisted fixes (translations, docs, tests). Those are proposals; the gap resolves only after a recompose confirms it.
- **Agents may** apply `config`-effort fixes with autonomy L2 when the resulting change class is `standard`.

## 10. Operations
- **Signals:** `gaps_open{kind,severity,tenant_tier}`, `gap_mttr_days{severity}`, `scan_duration_s{type}`, `auto_fix_success_ratio`, `waived_gaps{kind}`.
- **SLOs:** an on-change scan completes in < 2 min after the triggering event; the nightly full scan for all active blueprints completes in < 4 h.

## 11. UI
- **Views:** master W6 (gap report with fixes and waivers), master W1 (header gap counter), `gap.detail` (why chain, fixes with preview diff, history, owner), `gap.trend.dashboard`, `discovery.questions` (answers to the master §29.5 questions per scope).
- **UX:** fixes show their effort type and a preview. "Apply all config fixes" batches them into one proposal.

## 12. Scale
Millions of open and closed gaps across tenants. Gap store in control-plane Postgres, partitioned by tenant. Scans reuse composer workers. T1.

## Appendix
- **B. Amendments:** master §11.6 gains discovery kinds and `INSIGHT` severity; the fix catalog becomes a first-class object.
- **D. Attribute definitions (A-74).** `GapReport { id, scope: UGID, blueprintCandidate?: string, snapshot: string, scanType: composition|on-change|scheduled, gaps: [UGID], summary: {mandatory, recommended, optional, insight}, newSinceLast: integer, resolvedSinceLast: integer, trend: improving|stable|worsening, scannedAt: TimePoint }`
- **C.** 0.1.0.

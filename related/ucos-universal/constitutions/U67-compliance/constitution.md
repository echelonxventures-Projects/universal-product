# U67 — Compliance Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U67-compliance` |
| Layer | Trust Plane |
| Domain | 08 Governance |
| Steward | `ucos:org:grc-office` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (regulation & control library for IN/AE commerce + PCI/SOC2/ISO baseline, composition rule modules, control status), P5 (continuous compliance at scale, auditor workflows, more frameworks) |
| Depends on | U12 Geography (jurisdictions), U05 Ontology (concepts), U58 Composition (rule modules), U65 Security (controls), U66 Privacy, U68 Evidence, U74 Certification, U02 Governance, U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U58 (derivation of required controls/capabilities), U74 (CMP gates), U75 (compliance gaps), all universes (control implementations), Governance portal (W11) |
| Master references | §20 (compliance-as-code, control model, framework library), §11.3 (derivation rules) |

> Compliance owns **obligations and their satisfaction**: regulations and frameworks (as data), clauses, obligations, the **Control Library** (platform controls with implementations and tests), control mappings (control ↔ clauses), applicability rules (as composition rule modules), control status per tenant/blueprint, compliance assessments/posture, and regulatory change management. Security-specific control engineering is shared with U65; privacy obligations with U66.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| CMPL-L1 | Applicability of regulations is derived by rules from facts (jurisdiction × industry × capability × data class × scale thresholds), never chosen ad-hoc per tenant. Tenants may **add** voluntary frameworks. | Rule modules in U58; tenant PD `compliance.frameworks` additive only. |
| CMPL-L2 | One control can satisfy many clauses across frameworks (map once, satisfy many); controls are not duplicated per framework. | Control library uniqueness + ontology dedupe. |
| CMPL-L3 | A control is "implemented" only if its implementation exists in the blueprint **and** its tests pass with fresh evidence. | Status computation (§3). |
| CMPL-L4 | Regulatory changes are tracked as versioned regulation updates with effective dates; impacted tenants are identified and gaps raised ahead of effective dates. | Regulatory change workflow + Temporal triggers. |
| CMPL-L5 | Interpretations of law are recorded with author, source and review (legal accountability), not hidden in rules. | `Interpretation` objects referenced by rules. |

## 2. Objects
- **`Regulation` / `Framework`** `{ id (e.g. in-dpdp-2023, pci-dss-4.0.1, soc2-2017-tsc, iso27001-2022, eu-gpsr, in-ecommerce-rules-2020, in-legal-metrology, ae-pdpl, rbi-pa-guidelines, eu-ai-act), kind: law|regulation|standard|contractual|voluntary, issuer, jurisdictions, version, effectiveFrom: TimePoint, sunset?: TimePoint, source docs, licence (ISO texts are licensed: store references/summaries, not full text) }`
- **`Clause`** `{ regulation, ref (e.g. "S.6(1)", "Req 3.5.1", "A.8.24"), title, summary (own words), obligationRefs }`
- **`Obligation`** `{ id, clause, statement (plain), appliesWhen (CEL/Datalog facts), deadlineType? (e.g. breach notification 72h), evidenceExpectations }`
- **`Control`** — master §20.2 schema (+ U65 SecurityControl for security area): `{ id, objective, implementedBy: [capabilities/policies/workflows/views/decisions], parameters (decision refs), tests, evidenceCollectors, owner, severity, mappings: [{clause, relation: satisfies|partially|supports}] }`
- **`Interpretation`** `{ id, regulation/clause, question, position, rationale, author (legal), reviewedAt: TimePoint, jurisdictionScope, confidence }`
- **`ControlStatus`** `{ control, scope (tenant/blueprint/platform), state: implemented|failing|not-implemented|not-applicable|waived, evidenceFreshness, lastTestAt: TimePoint, waiver? }`
- **`ComplianceAssessment`** `{ framework, scope, period: TimeRange, posture % (weighted by severity), gaps, assessor (internal/external), status, evidencePack (U68) }`
- **`RegulatoryChange`** `{ regulation, change summary, effectiveFrom: TimePoint, impactedObligations, impactedTenants (computed), tasks, status }`

## 3. Status computation (normative)
```text
status(control, scope):
  if not applicable(control, scope) → not-applicable           (no mapped obligation applies)
  if waived(control, scope) ∧ waiver valid → waived
  if ∄ implementation in blueprint → not-implemented
  if any test failing ∨ evidence stale (> collector.freshnessSLO) → failing
  else implemented
posture(framework, scope) = Σ_weight(implemented)/Σ_weight(applicable)
```

## 4. Seed library (P1)
- **India commerce:** DPDP 2023 (+ Rules), IT Act 2000 & SPDI Rules, Consumer Protection (E-Commerce) Rules 2020, CCPA dark-pattern guidelines 2023, Legal Metrology (Packaged Commodities) Rules, GST Act (invoicing/e-invoicing/TCS), RBI PA/PG guidelines & card tokenisation, CERT-In directions 2022, TRAI TCCCPR.
- **UAE:** PDPL (Federal Decree-Law 45/2021), Consumer Protection Law, VAT law & FTA requirements, CBUAE payment rules, TDRA messaging.
- **Cross-industry baselines:** PCI DSS v4.0.1, SOC 2 TSC, ISO/IEC 27001:2022, ISO/IEC 27701, ISO/IEC 42001, NIST CSF 2.0 (mapping only), WCAG 2.2 AA / EN 301 549.
- P2+: EU (GDPR, DSA, GPSR, Omnibus, VAT OSS, AI Act), UK, KSA (PDPL, ZATCA), US (CCPA/CPRA, state sales tax via engine, COPPA, TCPA), sector packs (HIPAA, FINRA/SEBI, DORA).

## 5. Commands, Queries, Events, APIs
Commands: `ImportRegulation`/`PublishRegulationVersion` (governed), `DefineControl`, `MapControl`, `RecordInterpretation`, `StartAssessment`, `RecordRegulatoryChange`, `ComputeStatus(scope)` (scheduled & on events).
Queries: `ApplicableRegulations(scope)`, `ControlsFor(scope, framework?)`, `Posture(scope, framework)`, `Trace(clause)` (clause → control → implementation → tests → evidence), `UpcomingObligations(scope, horizon)`.
Events: `compliance.control.failed|recovered`, `compliance.regulation.published`, `compliance.change.effective-soon`, `compliance.assessment.completed`.
```text
GET /v1/compliance/applicable?tenant=     GET /v1/compliance/posture?tenant=&framework=
GET /v1/compliance/controls?framework=     GET /v1/compliance/trace?clause=
POST /v1/compliance/assessments            POST /v1/compliance/interpretations
```

## 6. Rule modules contributed (examples; Datalog in U58)
`rules.compliance.india-privacy`, `rules.compliance.india-payments`, `rules.compliance.india-ecommerce` (seller details display, grievance officer, return policy display, country-of-origin attribute), `rules.compliance.uae-privacy`, `rules.compliance.pci-scope` (card capability → PCI controls by SAQ type), `rules.compliance.a11y`, `rules.compliance.thresholds` (e.g. DPDP Significant Data Fiduciary if notified; e-invoicing turnover thresholds).

## 7. Security & Compliance of the universe itself
Library content `internal` (licensed standard texts never stored); tenant posture `confidential`; interpretations privileged/legal (access restricted); every change to applicability rules is a significant Governance change with legal review.

## 8. Gaps
```prolog
gap(compliance_control, S, C)   :- applies(C, S), status(C, S, not-implemented).
gap(control_failing, S, C)      :- applies(C, S), status(C, S, failing).
gap(regulatory_change_unprepared, S, R) :- regulatory_change(R), effective_within_days(R, 60), impacts(R, S), open_tasks(R, S, N), N > 0.
gap(obligation_without_control, O)      :- obligation(O), applicable_somewhere(O), not mapped_control(O, _).
gap(interpretation_stale, I)    :- interpretation(I), review_age_days(I, D), D > 365.
```

## 9. AI
Regulatory-change monitoring and summarisation (sources: gazettes, regulators' sites) → `RegulatoryChange` proposals; clause→control mapping suggestions (legal review); posture explanations; evidence-gap triage. Never auto-publishes regulations or interpretations.

## 10. Operations, UI, Scale
Signals: `posture_ratio{framework,tenant}`, `controls_failing{severity}`, `regulatory_changes_pending`, `evidence_freshness_ratio`. Views: W11 (posture bars, approvals), `compliance.framework.browser` (clauses → controls → evidence), `compliance.control.detail`, `compliance.change.tracker` (timeline of effective dates), `compliance.assessment.workspace` (auditor collaboration with U68 grants). Scale: ~50 frameworks, ~10k clauses, ~2k controls; status per tenant computed incrementally. T1.

## Appendix
- **A.** Legal ownership model for interpretations per jurisdiction (in-house counsel + external firms) — organisational decision.
- **C.** 0.1.0.

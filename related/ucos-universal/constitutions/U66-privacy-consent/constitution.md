# U66 — Privacy & Consent Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U66-privacy` |
| Layer | Trust Plane |
| Domain | 08 Governance |
| Steward | `ucos:org:dpo-office` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (purposes, notices, consent, DSR access/erasure, retention engine), P3 (DPIA tooling, RoPA generation, children's data pack), P5 (cross-border transfer registry at scale) |
| Depends on | U11 Party (ContactPoint consents, ListReferences), U04 Meta (field purposes/classification), U65 Security (crypto-shredding), U13 Temporal (deadlines, retention), U60 Workflow (DSR), U12 Geography (jurisdiction), U67 Compliance, U68 Evidence |
| Depended on by | every universe processing personal data; U40 Communication; U72 Analytics; U49 AI (training/use restrictions); U16 Context (consent snapshot) |
| Master references | §20.4–§20.5, §24.7 (DSR journey), PTY-L5 |

> Privacy owns **the lawful, purposeful and rights-respecting processing of personal data**: purposes and lawful bases, notices (versioned), consent records, records of processing (RoPA), data-subject requests (access, rectification, erasure, portability, objection, grievance/nomination), retention rules and their execution, children's data rules, cross-border transfer records, DPIAs, and cookie/tracking consent for web channels.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| PRV-L1 | Every personal-data field and every processing activity declares at least one `Purpose` with a lawful basis per jurisdiction. | META-L7 + PTY-L2; RoPA generation fails on untagged fields (gap). |
| PRV-L2 | Consent-based purposes are processed only with a valid, specific, recorded consent; withdrawal is as easy as giving and takes effect within the declared SLA. | Consent checks in Communication, Analytics, AI, Personalisation; obligations from PDP (`purpose`). |
| PRV-L3 | Data subject requests are fulfilled across all universes via the reference graph within jurisdictional deadlines, with evidence. | DSR workflow + SLA clocks + evidence collectors. |
| PRV-L4 | Retention is enforced automatically; data past retention is deleted, anonymised or crypto-shredded unless under legal hold. | Retention engine + Temporal triggers + evidence. |
| PRV-L5 | Children's data requires age-appropriate handling (verifiable parental consent, no profiling/targeted ads, restricted contact). | `isMinor` (U11) + policies + gap rules. |
| PRV-L6 | Cross-border transfers of personal data occur only with a recorded mechanism (adequacy, SCCs, consent, law-permitted) and respect localisation laws. | Transfer registry + residency rules (U73) + egress policies. |

## 2. Objects
- **`Purpose`** `{ id (e.g. order-fulfilment, fraud-prevention, marketing-email, personalisation, analytics, ai-training), description (LocalizedText, plain language), lawfulBases: [{jurisdiction, basis: contract|consent|legal-obligation|legitimate-interest|vital-interest|public-task|deemed-consent(DPDP)}], dataCategories, retentionRule, recipients/processors, transferMechanisms, requiresConsent (derived per jurisdiction), childrenAllowed }`
- **`Notice`** `{ id, tenant, version, purposes, languages (DPDP: English + 22 scheduled languages availability), content (Document), effectiveFrom: TimePoint, changeSummary }`
- **`Consent`** `{ id, party, purpose, notice@version, status: granted|denied|withdrawn|expired, channel, method (checkbox, OTP, verbal-recorded, parental), evidence (UI snapshot hash, IP hash, timestamp), validity: TimeRange, consentManager? (DPDP consent manager ref) }`
- **`ProcessingActivity`** (RoPA) — generated from graph: object types × fields × purposes × capabilities × processors (connectors) × transfers × retention.
- **`DataSubjectRequest`** `{ id, party (verified), type: access|rectification|erasure|portability|restriction|objection|withdraw-consent|grievance|nominate, jurisdiction, receivedAt: TimePoint, deadline (SLAClock), scope, status, outputs (export package/asset), evidence, exceptions (legal holds) }`
- **`RetentionRule`** `{ id, dataCategory/objectType, purpose, duration (Duration from trigger event, e.g. P8Y after invoice date), jurisdiction overrides, action: delete|anonymise|aggregate|crypto-shred, legalHoldAware }`
- **`TransferRecord`** `{ from jurisdiction/cell, to (processor/region), dataCategories, mechanism, documents, validity: TimeRange }`
- **`DPIA`** `{ subject (capability/blueprint/AI use), risks, mitigations, residual risk, approvals, review date }`
- **`CookieConsent`** (web) `{ categories: necessary|preferences|analytics|marketing, vendor list, region rules (GDPR opt-in, CCPA opt-out, GPC signal honoured) }`

## 3. Workflows
### 3.1 DSR (workflow `dsr.flow@1`, master §24.7)
receive (portal/app/email/agent) → verify identity (step-up per risk) → classify type & jurisdiction → start SLA clock (decision `privacy.dsr-deadline`: GDPR 30d (+60), CCPA 45d (+45), DPDP per rules, UAE PDPL 30d) → scope discovery via `ListReferences(party)` across universes → legal-hold & exception check (U68 holds, tax retention) → per universe: export / rectify / erase-or-minimise (each universe implements `privacy.dsr-handler` extension point) → assemble output (portable JSON/CSV + human-readable PDF) → respond → evidence.

### 3.2 Retention engine
Nightly per tenant/cell: evaluate retention rules (Temporal trigger time = anchor event + duration), batch delete/anonymise/crypto-shred, produce evidence (counts, hashes), skip held records.

## 4. Commands, Queries, Events, APIs
Commands: `DefinePurpose`, `PublishNotice`, `RecordConsent`/`WithdrawConsent`, `SubmitDSR`, `VerifyDSRIdentity`, `CompleteDSR`, `DefineRetentionRule`, `RecordTransfer`, `ApproveDPIA`.
Queries: `ConsentSnapshot(party)` (for Context), `HasConsent(party, purpose)`, `RoPA(tenant)`, `DSRStatus`, `RetentionDue(scope)`.
Events: `privacy.consent.granted|withdrawn`, `privacy.dsr.received|completed|overdue`, `privacy.retention.executed`, `privacy.notice.published`.
```text
POST /v1/privacy/consents     GET /v1/privacy/consents?party=
POST /v1/privacy/dsr          GET /v1/privacy/dsr/{id}      POST /v1/privacy/dsr/{id}:verify|:complete
GET  /v1/privacy/ropa?tenant= POST /v1/privacy/retention-rules   POST /v1/privacy/notices
```
Extension point **`privacy.dsr-handler`** (every universe holding personal data implements: `Export(party)`, `Rectify(party, changes)`, `Erase(party, mode)`); certification gate `CMP-PRV-01` checks presence.

## 5. Security & Compliance
Frameworks: GDPR, UK GDPR, DPDP Act 2023 & Rules, UAE PDPL, KSA PDPL, CCPA/CPRA, LGPD, PIPL, COPPA, ePrivacy. DPO/grievance officer contact published (DPDP). Consent evidence immutable. Purpose obligations enforced at PDP (`purpose(required)`).

## 6. Gaps
```prolog
gap(field_without_purpose, T, F)       :- field(T, F), classified(F, personal), not purpose_of(F, _).
gap(universe_without_dsr_handler, U)   :- universe_holds_personal_data(U), in_blueprint(U), not dsr_handler(U).
gap(no_notice_language, T, L)          :- tenant(T), in_scope(T, jur:IN), required_notice_language(T, L), not notice_language(T, L).
gap(dsr_overdue, R)                    :- dsr(R), open(R), past_deadline(R).
gap(transfer_without_mechanism, X)     :- personal_data_flow(X), cross_border(X), not transfer_mechanism(X).
gap(no_retention_rule, T, C)           :- tenant(T), data_category_in_use(T, C), not retention_rule(T, C).
gap(dpia_required, B)                  :- blueprint(B), high_risk_processing(B), not approved_dpia(B).
```

## 7. AI
AI use of personal data only for purposes with lawful basis; `ai-training` purpose separate and off by default; DSR discovery assistance (unstructured data search); notice plain-language drafting (legal review required); DPIA drafting assistance.

## 8. Operations, UI, Scale
Signals: `dsr_open{type}`, `dsr_time_to_complete_days`, `consent_withdrawals_total{purpose}`, `retention_records_deleted_total`, `fields_without_purpose`. Views: end-user `privacy.center` (consents, data download, delete account, grievance), `privacy.dsr.console` (DPO), `privacy.ropa.report`, `privacy.retention.rules`, `privacy.dpia.editor`, web `cookie.banner` (honest, equal-weight accept/reject). Scale: consents 10⁹; DSR volume modest; retention batch jobs per cell. T1.

## Appendix
- **D. Attribute definitions (A-74).** `ProcessingActivity { id, name: LocalizedText, controller: UGID, purposes: [UGID], dataSubjects: [string], dataCategories: [Classification], objectTypes: [string], capabilities: [string], processors: [UGID], transfers: [UGID], retention: [UGID], securityMeasures: [UGID], generatedAt: TimePoint, reviewedAt?: TimePoint, status: current|stale }` (RoPA, generated from the knowledge graph)
- **C.** 0.1.0.

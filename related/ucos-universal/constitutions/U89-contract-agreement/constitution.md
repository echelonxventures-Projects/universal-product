# U89 — Contract & Agreement Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U89-contract` |
| Layer | L5 Business Capability |
| Domain | 03 Business |
| Steward | `ucos:org:legal-ops` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 (terms acceptance, seller agreements, DPAs, e-sign), P4 (full CLM: negotiation, obligations tracking, renewals) |
| Depends on | U42 Document (templates, rendering, signatures), U11 Party, U10 Org, U13 Temporal (terms, renewals, notice periods), U60 Workflow (approvals), U01 Authority (signing authority), U67 Compliance |
| Depended on by | U25 Marketplace (seller agreements), U10 Tenant (UCOS contract, DPA), U24 Checkout (T&C acceptance), U23 Pricing (contract prices), U45 Procurement, U100 Financial Products, U83 Rental, U66 Privacy (DPAs) |
| Master references | Master mindmap "Contract & Agreement" (no U-number before A-34) |

> Contract owns **legally binding agreements and their lifecycle**: agreement templates and clause libraries, agreement instances between parties, versions and negotiation (redlines), approvals and signing authority, execution (e-signature evidence), obligations and entitlements extracted from contracts (with due dates), renewals/terminations/notice periods, and click-wrap acceptance of terms (ToS, privacy notice links, seller policies).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| CON-L1 | A signed agreement version is immutable; changes are amendments with their own execution. | Document hashing + status guard. |
| CON-L2 | Only parties with signing authority (U01) can execute on behalf of an organisation. | Authority check at sign. |
| CON-L3 | Machine-relevant terms (prices, SLAs, limits, durations, notice periods) are extracted into structured obligations consumed by other universes — no re-typing. | Obligation objects referenced by Pricing/SLA/Entitlement. |
| CON-L4 | Click-wrap acceptance records exact version, timestamp, context and identity. | Acceptance evidence (U68). |

## 2. Objects
`ClauseLibrary { clauses: [{id, text (LocalizedText), variables, fallbacks, jurisdictionVariants, risk rating}] }` · `AgreementTemplate { kind: tos|privacy-notice|seller-agreement|dpa|msa|sow|nda|lease|loan|employment|custom, clauses, variables schema, approval matrix }` · `Agreement { id, template@v, parties [{party, role, signatory}], variables, document (U42), status: draft|negotiation|approval|signing|active|expired|terminated|renewed, validity (TemporalRef), renewal: {auto, notice Duration}, governingLaw: JurisdictionRef, amendments[] }` · `Obligation { agreement, owner party, description, due: TemporalRef|Trigger, measure, status }` · `Acceptance { party, agreement/template@v, method: click|sign|implicit, at: TimePoint, contextHash }`.

## 3. Commands, Queries, Events, APIs
Commands: `DraftAgreement`, `ProposeRedline`, `ApproveAgreement`, `SendForSignature` (e-sign port), `RecordSignature`, `Activate`, `Amend`, `Renew`, `Terminate`, `RecordAcceptance`.
Queries: `ActiveAgreements(party)`, `ObligationsDue(scope, horizon)`, `CurrentTermsVersion(kind)`, `AcceptanceOf(party, kind)`.
Events: `contract.agreement.executed|renewal-due|expired|terminated`, `contract.obligation.due|breached`, `contract.terms.accepted`.
Port: `esign.provider` (DocuSign, Adobe Sign, Leegality/Digio Aadhaar e-sign, UAE Pass).

## 4. Gaps
```prolog
gap(no_current_terms, T, K) :- tenant(T), requires_terms(T, K), not active_template(T, K).
gap(dpa_missing, T)         :- tenant(T), processes_personal_data(T), not agreement(T, dpa, active).
gap(obligation_untracked, A):- agreement(A), active(A), structured_terms_expected(A), not obligations_extracted(A).
```

## 5. AI, Ops, UI, Scale
AI: clause extraction & risk flags, redline suggestions within playbook, obligation extraction (lawyer review). Signals: `contracts_active`, `renewals_due_30d`, `cycle_time_days`, `obligations_breached`. Views: `contract.repository`, `contract.editor` (clause-based with redlines), `contract.approval`, `obligation.calendar`, `terms.versions` (with acceptance stats). T2.

## Appendix
- **C.** 0.1.0.

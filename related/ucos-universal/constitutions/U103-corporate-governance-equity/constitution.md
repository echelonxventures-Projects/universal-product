# U103 — Corporate Governance & Equity Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U103-corp-gov` |
| Layer | L5 Business Capability |
| Domain | 08 Governance |
| Steward | `ucos:org:company-secretarial` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 |
| Depends on | U10 Org (legal entities, group structure), U11 Party (directors, shareholders), U89 Contract (shareholder agreements, ESOP plans), U42 Document (minutes, resolutions, filings), U13 Temporal (board calendars, filing deadlines, vesting schedules), U30 Ledger (share capital, dividends), U67 Compliance (company law), U01 Authority (board authority → UCOS authorities), U09 Identity (DIN/KYC of directors) |
| Depended on by | U01 Authority (board resolutions as evidence for authorities), U100 Financial (investor platforms), U46 Workforce (ESOP), investor-relations portals |
| Master references | APQC 12.x "Manage external relationships — investor relations, board" (A-50) |

> Corporate Governance owns **how legal entities are governed and owned**: entity registers (incorporation, registered office, statutory registers), directors/officers and their appointments, board & committee meetings (agenda, quorum, minutes, resolutions incl. circular resolutions), shareholder meetings & voting, the **capitalisation table** (share classes, issuances, transfers, convertible instruments, option pools), employee equity (ESOP grants, vesting, exercises), dividends, statutory filings and deadlines, beneficial ownership registers, and investor relations communications.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| CG-L1 | Board/shareholder decisions are valid only with quorum, eligible voters, conflict-of-interest recusal and signed minutes. | Meeting workflow guards; e-sign (U89/U42). |
| CG-L2 | The cap table is an immutable ledger of equity events; holdings are derived. | Event-sourced equity ledger (U30-backed). |
| CG-L3 | Statutory filings have jurisdiction-specific deadlines tracked by SLA clocks. | U67 rule packs (e.g. India MCA forms, UAE ROC, UK Companies House). |
| CG-L4 | Board resolutions that grant authority are linked to UCOS `Authority` objects as evidence (U01). | Resolution → Authority link. |

## 2. Objects
`LegalEntityRecord { organization (U10), incorporation, registry ids (CIN, CRN), registered office, fiscal year, statutory registers }` · `Officer { party, role (director/CEO/CFO/company secretary), appointedAt: TimePoint, resignedAt?: TimePoint, identifiers (DIN) }` · `Meeting { body: board|committee|AGM|EGM, schedule (TemporalRef), agenda, attendees, quorum, minutes (doc), resolutions }` · `Resolution { text, type (ordinary/special/circular), votes, outcome, effectiveFrom: TimePoint, links (authorities, contracts) }` · `ShareClass { rights, par value: Money }` · `EquityEvent { kind: issuance|transfer|buyback|split|conversion|grant|exercise|forfeit|cancel, instrument, holder, quantity, price: Money, at: TimePoint, approvals }` · `OptionPlan { pool size, vesting templates (Recurrence + cliff Duration) }` · `Grant { plan, grantee, quantity, vestingSchedule, exercisePrice }` · `Dividend { class, rate, recordDate: TimePoint, paymentDate: TimePoint }` · `StatutoryFiling { authority, form, period: TimeRange, dueAt: TimePoint, status, receipt }` · `BeneficialOwner { entity, party, percentage, nature of control }`.

## 3. Commands, Events, APIs
Commands: `AppointOfficer`, `ScheduleMeeting`, `RecordMinutes`, `PassResolution`, `RecordEquityEvent`, `CreateOptionPlan`, `Grant`, `Exercise`, `DeclareDividend`, `FileStatutory`.
Events: `corpgov.resolution.passed`, `corpgov.filing.due|filed`, `corpgov.equity.changed`, `corpgov.vesting.occurred`.
```text
GET /v1/corpgov/entities/{id}/cap-table?asOf=   POST /v1/corpgov/meetings   POST /v1/corpgov/resolutions   POST /v1/corpgov/equity-events
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(filing_overdue, F)    :- statutory_filing(F), open(F), past_due(F).
gap(authority_without_resolution, A) :- authority(A), level(A, L), L >= 4, holder_is_corporate(A), not resolution_evidence(A).
```
AI: minutes drafting from transcripts (secretary approval), cap-table scenario modelling (dilution, waterfall — via U54). Views: entity dashboard, board portal (papers, voting, e-sign), cap table (asOf time travel), ESOP employee portal, compliance calendar. Confidentiality: board papers `restricted`. T3.

## Appendix
- **C.** 0.1.0.

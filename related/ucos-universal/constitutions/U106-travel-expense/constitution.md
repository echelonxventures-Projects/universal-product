# U106 — Travel & Expense Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U106-travel-expense` |
| Layer | L5 Business Capability |
| Domain | 03 Business |
| Steward | `ucos:org:finance-spend` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 |
| Depends on | U30 Ledger (posting, reimbursement), U29 Payment (reimbursement payouts, corporate cards via partners), U14 Currency (FX on foreign spend), U31 Tax (input tax credit on receipts), U43 Asset + AI OCR (receipts), U53 Decision (policy limits), U60 Workflow (approvals), U13 Temporal (trip dates, submission deadlines), U46 Workforce (employees, cost centres), U81/travel pack (bookings) |
| Depended on by | U30 (accruals), U102 (spend KPIs), U98 ESG (business-travel emissions, Scope 3 cat. 6) |
| Master references | Completeness review A-53 |

> Travel & Expense owns **employee business spend**: travel requests and approvals, corporate travel booking (via travel pack/providers), expense claims (receipts, mileage, per diem), corporate card transaction matching, policy compliance and approval, reimbursement, and audit — with tax recovery and emissions capture.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| TE-L1 | Expense policy limits and rules (per diem by city, class of travel, receipt thresholds) are decision tables, versioned by validity. | U53. |
| TE-L2 | Every claim line has evidence (receipt or justified exception) and is approved by someone other than the claimant (SoD). | Workflow guards + U03 SoD. |
| TE-L3 | Reimbursements post to Ledger and pay out only after approval; duplicate receipts are blocked. | Duplicate detection (hash + fuzzy) + U30 posting. |

## 2. Objects
`TravelRequest { traveller, purpose, itinerary (TimeRange per leg, places), estimated cost: Money, approvals, bookings refs }` · `ExpenseClaim { claimant, period: TimeRange, lines [{date: LocalDate, category (taxonomy), merchant, amount: Money (original + converted), tax, receipt (U43), costCentre, project (U96), policyResult}], status }` · `MileageEntry { route (U12), distance: Quantity, rate rule }` · `PerDiem { location, days, rate rule }` · `CardTransaction { card, merchant, amount, at: TimePoint, matchedLine? }` · `Reimbursement { claim, amount, payout ref, ledger entry }`.

## 3. Commands, Events, APIs
Commands: `SubmitTravelRequest`, `Approve`, `SubmitClaim`, `ScanReceipt` (OCR), `MatchCardTransaction`, `ApproveClaim`, `Reimburse`, `AuditClaim`.
Events: `expense.claim.submitted|approved|reimbursed`, `expense.policy.violation`.
```text
POST /v1/expense/claims   POST /v1/expense/receipts:scan   POST /v1/expense/claims/{id}:approve|:reimburse   POST /v1/travel/requests
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(expense_policy_missing, T) :- tenant(T), capability(T, expense.core), not decision_version(T, expense.policy).
```
AI: receipt OCR & categorisation, duplicate/fraud detection, policy explanations. Views: mobile receipt capture, claim builder, approver inbox (U60), card reconciliation, spend analytics. T3.

## Appendix
- **C.** 0.1.0.

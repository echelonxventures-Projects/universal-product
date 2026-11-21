# U30 — Ledger & Finance Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U30-ledger` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce (finance) |
| Steward | `ucos:org:finance-ledger` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 (double-entry ledger, chart of accounts, posting rules from events, settlement & payouts accounting, invoices/receivables, period close, replay of P1 events), P4 (AP, budgets/FP&A with U102, fixed assets with U79, consolidation, revenue schedules at scale) |
| Depends on | U14 Currency (Money, FX, rounding, allocation), U13 Temporal (fiscal calendars, period close, settlement T+N, accruals), U10 Org (legal entities, functional currency), U31 Tax (liabilities), U29 Payment, U26 Order, U25 Marketplace, U84 Stored Value, U61 Event (posting sources), U68 Audit, U67 Compliance |
| Depended on by | U25 Marketplace (commissions, payouts), U27 Subscription (revenue), U84 (balances), U100 Financial Products, U106 T&E, U103 (share capital, dividends), U102 (budgets/actuals), U98 (spend-based emissions), tenant finance portal |
| Master references | §6.3 (Ledger is the only financial truth), §13.3 (money rules), A-19 (P1 replay) |

> Ledger owns **financial truth**: charts of accounts per legal entity, double-entry journals and postings, sub-ledgers (customer/receivables, seller/payables, stored value, tax, clearing accounts per PSP), **posting rules** that turn business events into journal entries, settlements and payout accounting, invoices/receivables (commercial; tax documents remain U31/U42), revenue recognition schedules, accruals, period close, reconciliation, and financial reporting (trial balance, GL, P&L, balance sheet). Payments move money (U29); the Ledger records it.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| LED-L1 | Every journal entry balances (Σ debits = Σ credits per currency) and is immutable; corrections are reversing/adjusting entries. | DB constraint + append-only tables + hash chain per entity/period. |
| LED-L2 | Balances are derived from postings; no other universe stores financial balances. | §6.3 ruling; lint for balance fields. |
| LED-L3 | Postings are produced by versioned **posting rules** from business events; manual journals require approval (SoD) and evidence. | Posting engine; manual journal workflow (U60, U01). |
| LED-L4 | Every posting is idempotent by `(sourceEventId, ruleId)`; replay of historical events reproduces identical entries (enables A-19 P1 backfill). | Unique constraint + deterministic rules. |
| LED-L5 | Closed periods are locked; late events post into the next open period with reference (or a governed reopen). | Period state machine + Temporal fiscal calendar. |
| LED-L6 | Multi-currency entries store transaction currency, functional currency amount and the rate reference used (CUR-L4). | Schema. |

## 2. Objects
`LedgerEntity { organization (legal entity), functionalCurrency, fiscalCalendar (U13), chartOfAccounts, status }` · `Account { code, name, type: asset|liability|equity|revenue|expense|contra, subtype (receivable, payable, clearing, tax-payable, deferred-revenue, stored-value-liability…), currency?, parent, dimensions allowed (store, channel, seller, cost-centre, project) }` · `JournalEntry { id, entity, period, postedAt: TimePoint, effectiveDate: LocalDate, source: {eventId, ruleId} | manual, lines [{account, debit|credit: Money, functionalAmount: Money, rateRef?, dimensions}], memo, approvals?, hash }` · `PostingRule { id, onEvent (event type + filter), lines template (account resolution by decision tables, amounts from payload paths, allocation), version, validity }` · `Invoice` (commercial receivable) `{ customer/party, lines, due: TimePoint, taxDocument (U31), status: open|partially-paid|paid|written-off }` · `Settlement { provider/seller, period: TimeRange, gross, fees, refunds, chargebacks, net: Money, payout ref (U29), status }` · `RevenueSchedule { contract/subscription/order line, performance obligations, recognition pattern (point-in-time | ratably over TimeRange), amounts per period }` · `Period { entity, range: TimeRange, state: open|closing|closed|reopened }` · `Reconciliation { account, source (bank/PSP statement), matched, unmatched, adjustments }`.

### 2.1 Seed posting rules (P2)
| Event | Debit | Credit |
|---|---|---|
| `payment.payment-intent.captured` | PSP clearing | Customer receivable / deferred order liability |
| `order.order.confirmed` (+ tax determination) | Customer receivable | Revenue (per seller: marketplace commission revenue vs agent pass-through), Tax payable |
| `fulfillment.shipment.delivered` (where revenue recognised at delivery) | Deferred revenue | Revenue |
| `payment.refund.issued` | Revenue/returns contra + Tax payable reversal | PSP clearing |
| `marketplace.payout.paid` | Seller payable | Bank/PSP payout clearing |
| `marketplace.commission.accrued` | Seller payable | Commission revenue (+ tax on commission) |
| `stored-value.instrument.issued` | Cash/clearing | Stored value liability |
| `stored-value.instrument.redeemed` | Stored value liability | Revenue/receivable |
| PSP settlement report | Bank | PSP clearing + Fees expense |

## 3. Commands, Queries, Events, APIs
Commands: `CreateLedgerEntity`, `DefineAccount`, `PublishPostingRule` (governed; tests with sample events required), `PostManualJournal` (approval), `ReverseEntry`, `ClosePeriod`, `ReopenPeriod` (level 3 authority), `ImportStatement`, `Reconcile`, `ScheduleRevenue`, `RunReplay(from, to, rules)` (A-19 backfill; dry-run diff first).
Queries: `TrialBalance(entity, asOf)`, `AccountActivity(account, range)`, `Balance(holder sub-ledger)`, `FinancialStatements(entity, period)`, `Aging(receivables|payables)`.
Events: `ledger.journal.posted`, `ledger.period.closed|reopened`, `ledger.settlement.completed`, `ledger.reconciliation.break`.
```text
POST /v1/ledger/entities   POST /v1/ledger/accounts   POST /v1/ledger/posting-rules   POST /v1/ledger/journals (manual)
POST /v1/ledger/periods/{id}:close|:reopen   GET /v1/ledger/trial-balance?entity=&asOf=   POST /v1/ledger/replays
```
Errors: `LED_UNBALANCED`, `LED_PERIOD_CLOSED`, `LED_ACCOUNT_UNKNOWN`, `LED_RULE_AMBIGUOUS`, `LED_DUPLICATE_POSTING` (idempotent skip).

## 4. Security, Compliance, Gaps
Finance data `confidential`; manual journals SoD; audit full; controls: SOX-style ITGCs, IFRS 15 revenue, IAS 21 FX, India Ind AS / Companies Act books retention (8 years), GST books, UAE corporate tax and VAT records; e-invoicing linkage via U31.
```prolog
gap(event_without_posting_rule, E) :- financial_event(E), produced_in_blueprint(E), not posting_rule_for(E).
gap(unreconciled_clearing, A)      :- account(A), subtype(A, clearing), unreconciled_older_than_days(A, 3).
gap(period_not_closed, P)          :- period(P), ended_days_ago(P, D), D > 10, not closed(P).
gap(p1_replay_pending, T)          :- tenant(T), activated_ledger(T), not replay_completed(T, p1-events).
```
AI: anomaly detection on journals, reconciliation matching suggestions (human approval), close-checklist assistant. Views: chart of accounts, journal explorer (drill to source event), posting-rule editor with test events, period close cockpit, reconciliation workbench, statements. Scale: postings ≈ 5–10 per order; partitioned by entity/period; T1 (posting async ≤ 5 s from event).

## Appendix
- **C.** 0.1.0.

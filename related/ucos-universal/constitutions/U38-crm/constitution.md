# U38 — CRM Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U38-crm` |
| Layer | L5 Business Capability |
| Domain | 06 Engagement |
| Steward | `ucos:org:engagement-crm` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 |
| Depends on | U11 Party (people, organisations, roles), U10 Org (sales teams, territories), U40 Communication (email, calls, WhatsApp logged as activities), U13 Temporal (tasks, follow-ups, meetings, forecasts by fiscal period), U23 Pricing / U21 Catalog (quotes), U89 Contract (deal close → contract), U26 Order (won deal → order), U86 Marketing (leads from campaigns), U66 Privacy (consent, lawful basis for B2B outreach) |
| Depended on by | U27 Subscription (renewals), U39 Support (account context), U102 (pipeline into forecasts), U107 Partner (deal registration), B2B composition |
| Master references | §6.2 U38, U11 (party is the golden record) |

> CRM owns **relationships and revenue pipeline**: leads, accounts and contacts *as roles on Parties* (no duplicate person store), opportunities/deals with stages, quotes (CPQ with U23), activities and tasks, territories and assignment rules, sales forecasts, account plans and customer 360 views (assembled by reference from other universes).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| CRM-L1 | Leads, contacts and accounts are Party roles; CRM never keeps its own copy of personal data. | U11 role model; lint. |
| CRM-L2 | Outreach respects consent and lawful basis per jurisdiction and channel (DPDP, GDPR legitimate interest with objection, TRAI DLT, CAN-SPAM). | U40 send-time policy checks (COM-L2). |
| CRM-L3 | Stage changes are recorded with timestamps; forecast categories derive from stage rules, not free text. | Pipeline definitions; history table. |
| CRM-L4 | Quotes use governed price lists and discount approvals (U23/U60); a won deal creates an order or a contract through their commands. | CPQ approval workflow. |

## 2. Objects
`Lead { party, source (campaign/web/import/partner), status: new|working|qualified|disqualified, score, owner }` · `Account { organization party, tier, territory, owner, hierarchy }` · `Contact { person party, account, roles (decision-maker, influencer…) }` · `Pipeline { stages [{name, probability, forecastCategory, exit criteria}] }` · `Opportunity { account, pipeline, stage, amount: Money, expectedClose: LocalDate, products [quote lines], competitors, owner, history }` · `Quote { opportunity, lines (U23 priced), discounts (approved), validUntil: TimePoint, document (U42) }` · `Activity { kind: call|email|meeting|message|note, parties, objectRefs, at: TimePoint, duration?: Duration }` · `Task { subject, due: TimePoint, owner, status }` · `Territory { rules (geo/industry/size), members }` · `Forecast { team, period (fiscal, U13), commit, bestCase, pipeline }`.

## 3. Commands, Events, APIs
Commands: `CaptureLead`, `QualifyLead` (→ account/contact/opportunity), `MoveStage`, `CreateQuote`, `RequestDiscountApproval`, `WinOpportunity` (→ U26 order or U89 contract), `LoseOpportunity`, `LogActivity`, `AssignTerritory`, `SubmitForecast`.
Events: `crm.lead.captured|qualified`, `crm.opportunity.stage-changed|won|lost`, `crm.quote.sent|accepted`.
```text
POST /v1/crm/leads   POST /v1/crm/opportunities   POST /v1/crm/opportunities/{id}:move|:win|:lose
POST /v1/crm/quotes   POST /v1/crm/activities   GET /v1/crm/forecast?team=&period=
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(won_without_fulfilment_path, T) :- tenant(T), capability(T, crm.core), not capability(T, order.core), not capability(T, contract.core).
gap(outreach_without_consent_basis, T, J) :- tenant(T), in_scope(T, J), capability(T, crm.sequences), not consent_basis_rule(T, J).
```
AI: lead scoring, next-best-action, meeting summaries into activities (with recording consent), email drafting, deal-risk signals, forecast assist. Signals: `pipeline_coverage`, `win_rate`, `sales_cycle_days`, `forecast_accuracy`. Views: pipeline board (kanban), account 360, quote builder, activity timeline, forecast roll-up. T2.

## Appendix
- **C.** 0.1.0.

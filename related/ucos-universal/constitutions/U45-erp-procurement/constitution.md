# U45 — ERP & Procurement Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U45-procurement` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-procurement` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P4 |
| Depends on | U11 Party (suppliers), U10 Org (buying entities, cost centres), U89 Contract (supplier agreements, rate cards), U20 Inventory (receipts), U30 Ledger (AP, accruals, three-way match postings), U31 Tax (input tax, withholding), U60 Workflow (approvals), U13 Temporal (lead times, delivery schedules, payment terms), U102 (budgets), U98 (supplier ESG), U90 Trade (imports) |
| Depended on by | U47 Manufacturing (material requirements), U20 Inventory (replenishment POs), U106 (non-PO spend), marketplace operator buying, B2B buyer platforms |
| Master references | §6.2 U45 |

> Procurement owns **buying from suppliers**: supplier onboarding and qualification, catalogues and rate cards (punch-out), requisitions, sourcing events (RFQ/RFP, reverse auctions), purchase orders, goods/service receipts, supplier invoices with two/three-way match, and supplier performance. AP payments are executed through U29/U30; budgets checked with U102.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| PRC-L1 | No PO without an approved requisition or contract call-off within authority limits (delegation of authority matrix). | Approval workflow + U01 limits. |
| PRC-L2 | Supplier invoices are paid only after match (PO × receipt × invoice within tolerance) or documented override. | Match engine; override approval with SoD. |
| PRC-L3 | Suppliers pass due diligence (KYB, sanctions, tax registration, ESG where required) before first PO. | Onboarding guard; U09/U67/U98 checks. |
| PRC-L4 | Payment terms and MSME payment deadlines (India MSMED Act 45 days) are tracked as Temporal deadlines. | Deadline triggers + reports. |

## 2. Objects
`Supplier { organization party, categories, qualification status, bank (verified), tax ids, risk, rating }` · `Requisition { requester, lines [{item/service, quantity, estimated price, cost centre}], need-by: LocalDate, status }` · `SourcingEvent { kind: rfq|rfp|auction, items, invited suppliers, biddingRange: TimeRange, bids, award }` · `PurchaseOrder { supplier, entity, lines, terms (Incoterms, payment terms), deliverySchedule [{date: LocalDate, quantity}], status }` · `Receipt { po, lines received, quality result, at: TimePoint }` · `SupplierInvoice { supplier, lines, tax, due: TimePoint, match result, status }` · `SupplierScorecard { period, on-time, quality, price variance }`.

## 3. Commands, Events, APIs
Commands: `OnboardSupplier`, `CreateRequisition`, `ApproveRequisition`, `RunSourcingEvent`, `AwardSourcing`, `IssuePO`, `ChangePO`, `ReceiveGoods`, `CaptureSupplierInvoice` (OCR via U42), `MatchInvoice`, `ApproveForPayment`.
Events: `procurement.po.issued|changed|closed`, `procurement.receipt.posted`, `procurement.invoice.matched|exception`.
```text
POST /v1/procurement/suppliers   POST /v1/procurement/requisitions   POST /v1/procurement/purchase-orders
POST /v1/procurement/receipts   POST /v1/procurement/supplier-invoices
```

## 4. Gaps, UI
```prolog
gap(po_without_ledger, T) :- tenant(T), capability(T, procurement.core), not capability(T, ledger.core).
gap(msme_deadline_untracked, T) :- tenant(T), in_scope(T, jur:IN), capability(T, procurement.core), not rule(T, msme-payment-deadline).
```
AI: invoice extraction, spend classification (UNSPSC), supplier risk signals, negotiation assist. Views: requisition form/catalogue, approval inbox, sourcing event room, PO workspace, invoice match exceptions, supplier portal. T2.

## Appendix
- **C.** 0.1.0.

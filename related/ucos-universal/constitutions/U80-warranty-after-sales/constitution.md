# U80 — Warranty & After-sales Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U80-warranty` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-aftersales` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 |
| Depends on | U79 Installed Base, U26 Order (proof of purchase), U18 Product (warranty defaults, spare-part relationships), U13 Temporal (coverage periods), U82 Field Service, U35 Fulfillment (RMA logistics), U29 Payment (paid repairs, extended warranty), U53 Decision, U39 Support |
| Depended on by | U21 Catalog (warranty display, extended warranty listings), U39 Support, U70 Trust (product reliability), U98 ESG (repairability) |
| Master references | Master chat "Warranty / Global Warranty Registry" (dropped in consolidation; restored by A-29) |

> After-sales owns **what happens after the sale to keep products working**: warranty definitions (manufacturer, seller, statutory, extended/protection plans), warranty coverage instances bound to units, warranty registration, claims and their adjudication, repair orders (depot/on-site), RMA (return-merchandise authorisation for repair/replace), spare parts catalogue linkage and repair pricing, and service contracts (AMC — annual maintenance contracts).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| WAR-L1 | Coverage periods are Temporal ranges anchored to explicit events (delivery, activation, registration) — never "purchase date" fields. | Schema. |
| WAR-L2 | Statutory warranty/guarantee rights per jurisdiction are always applied in addition to (never reduced by) commercial warranties. | Jurisdiction decisions (e.g. EU 2-year legal guarantee) evaluated first. |
| WAR-L3 | Claim decisions are explainable (coverage terms matched, exclusions applied) and appealable. | Decision explanations; dispute link (U71). |
| WAR-L4 | Extended warranties/protection plans sold as insurance are routed through Financial Products (U100) where regulated as insurance. | Classification rule by jurisdiction. |

## 2. Objects
- `WarrantyDefinition { id, provider: manufacturer|seller|operator|insurer, applicability (GPID/model/category), coverage: {parts, labour, accidental?, theft?}, duration: Duration, anchor: delivery|activation|registration, territories (jurisdictions), exclusions, claimLimits (count/amount), transferable: bool, serviceMode: carry-in|on-site|mail-in|replacement }`
- `Coverage { id, unit: AssetUnitRef, definition, validity: TimeRange, source: purchase|registration|plan-sale|goodwill, proof: order/document refs, status: active|expired|voided|exhausted }`
- `Claim { id, unit, coverage(s), problem: taxonomy + description + media, reportedAt, triage: diagnosis, decision: approved|rejected|partial (with explanation), resolution: repair|replace|refund|credit, repairOrder?, rma?, costAllocation: [{payer: manufacturer|seller|customer|insurer, amount}], status }`
- `RepairOrder { id, claim?, unit, location: depot|on-site (WorkOrder U82), diagnosis, parts: [{sparePart: GPID, qty, source}], labour: Duration, quote (paid repairs via U23), status }`
- `RMA { id, claim, returnShipment (U35), replacementOrder?, inspection, status }`
- `ServiceContract (AMC) { id, unit(s), plan (U19 ServicePlan), visits included, SLA (U13 SLADefinition), billing (U27), validity: TimeRange }`

## 3. Commands, Queries, Events, APIs
Commands: `DefineWarranty`, `RegisterProduct(unit, proof)` (creates coverage), `SellProtectionPlan` (via U100 if insurance), `FileClaim`, `TriageClaim`, `DecideClaim`, `CreateRepairOrder`, `IssueRMA`, `CloseClaim`, `CreateServiceContract`.
Queries: `CoverageFor(unit, at)`, `ClaimStatus`, `SparePartsFor(model)` (U18 relationships `sparePartOf`), `RepairQuote(unit, problem)`.
Events: `warranty.coverage.started|expiring|expired`, `warranty.claim.filed|decided|closed`, `warranty.repair.completed`.
```text
POST /v1/warranty/registrations   GET /v1/warranty/coverage?unit=
POST /v1/warranty/claims          POST /v1/warranty/claims/{id}:triage|:decide|:close
POST /v1/warranty/repair-orders   POST /v1/warranty/service-contracts
```

## 4. Rules
Decision tables: `warranty.claim-eligibility`, `warranty.auto-approve` (low-value, high-confidence), `warranty.cost-allocation`, `warranty.statutory-rights` (per jurisdiction × product category). Expiry reminders via Temporal triggers (renewal offers through U22/U86).

## 5. Security & Compliance
Consumer law (statutory guarantees, repair availability obligations, EU right-to-repair directive), insurance regulation for protection plans (IRDAI India, EU IDD), fraud checks on claims (U69).

## 6. Gaps
```prolog
gap(no_warranty_definition, T, P) :- tenant(T), sells(T, P), durable_good(P), not warranty_definition_for(P).
gap(statutory_rights_unmodelled, J, C) :- in_scope(_, J), category_sold(C), statutory_guarantee(J, C), not statutory_rule(J, C).
gap(protection_plan_unregulated, T) :- tenant(T), sells_protection_plans(T), insurance_regulated(T), not capability(T, financial.insurance-distribution).
```

## 7. AI & Ops & UI & Scale
AI: claim triage from photos/descriptions, fraud signals, repair diagnosis assistance. Signals: `claims_open`, `claim_tat_days`, `first_time_fix_rate`, `warranty_cost_ratio{model}`. Views: customer `my-products` (from U79) with coverage + "Get help", `claim.file` wizard, `claim.triage.console`, `repair.depot.board`, `service-contract.manager`. Scale moderate; T1.

## Appendix
- **C.** 0.1.0.

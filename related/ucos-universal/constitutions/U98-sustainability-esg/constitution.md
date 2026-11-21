# U98 — Sustainability & ESG Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U98-esg` |
| Layer | L5 Business Capability |
| Domain | 08 Governance |
| Steward | `ucos:org:sustainability` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 (platform carbon accounting starts earlier in U72/U73 as signals) |
| Depends on | U18 Product (product footprint facts, materials, repairability), U36 Logistics (transport emissions), U73 Infra (compute energy/carbon), U30 Ledger (spend-based estimates), U79 Installed Base (lifecycle, circularity), U67 Compliance (CSRD, BRSR, ISSB), U14 Units (CO2e, kWh), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U21 Catalog (eco labels), U44 Search (sustainability filters), U35 Fulfillment (green delivery options), tenant reporting |
| Master references | Master Operations "Sustainability" (A-39) |

> ESG owns **measuring and reporting environmental, social and governance impact**: emission factors and activity data, carbon accounting (Scopes 1–3; GHG Protocol), product carbon/environmental footprints and eco-labels (with evidence), packaging and EPR (extended producer responsibility) obligations, circularity (repair, resale, recycling via U79), social metrics (workforce, supply-chain due diligence), and regulatory ESG reports.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| ESG-L1 | Every environmental claim shown to consumers is backed by evidence and a recognised methodology (anti-greenwashing). | Claim objects require evidence; display guard (EU Green Claims, UK CMA, ASCI India). |
| ESG-L2 | Emissions are computed from activity data × versioned emission factors with uncertainty; restatements are versioned. | Calculation engine + factor registry. |
| ESG-L3 | ESG reports trace every figure to source data. | Lineage (U93) + evidence (U68). |

## 2. Objects
`EmissionFactor { source (DEFRA, EPA, IEA, ecoinvent licence), activity, unit, value, region, validity: TimeRange }` · `ActivityRecord { scope, category, quantity (Quantity), source refs (shipments, energy meters, purchases), period: TimeRange }` · `FootprintResult { subject (org/product/shipment/order), scope breakdown, CO2e, uncertainty, method }` · `EnvironmentalClaim { subject, claim text, standard (e.g. ISO 14021/14067), evidence, validity: TimeRange }` · `EPRObligation { jurisdiction, material category, quantities placed on market, targets, certificates }` · `ESGReport { framework (CSRD/ESRS, BRSR, ISSB S1/S2, GRI), period: TimeRange, metrics, assurance status }`.

## 3. Commands, Queries, Events, APIs
Commands: `ImportEmissionFactors`, `RecordActivity`, `ComputeFootprint`, `PublishClaim`, `RecordEPRQuantities`, `GenerateReport`.
Queries: `ProductFootprint(gpid)`, `OrderFootprint(order)`, `ScopeTotals(org, period)`.
```text
GET /v1/esg/footprint?subject=   POST /v1/esg/activities   POST /v1/esg/reports
```

## 4. Gaps, AI, Ops, UI, Scale
```prolog
gap(claim_without_evidence, C) :- environmental_claim(C), displayed(C), not evidence(C, _).
gap(epr_unregistered, T, J)    :- tenant(T), places_packaging_on_market(T, J), epr_required(J), not epr_registration(T, J).
```
AI: spend-to-emission categorisation, supplier questionnaire extraction, claim review (flagging risky wording). Views: ESG dashboard, product eco-profile (PDP badge with methodology link), delivery option CO2e, report builder. T2.

## Appendix
- **C.** 0.1.0.

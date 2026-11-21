# U90 — Global Trade & Customs Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U90-trade` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-global-trade` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 (cross-border landed cost, HS classification, customs docs for parcels, sanctions/export screening), P5 (freight, bonded warehouses, free-zone flows) |
| Depends on | U18 Product (HS codes, origin, dual-use flags), U31 Tax (import VAT/GST, IOSS), U36 Logistics (carriers, shipments), U12 Geography (customs territories, free zones), U14 Currency, U67 Compliance (export controls, sanctions), U09 Identity (screening), U77 Frame (future: off-world trade authorities), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U24 Checkout (duties display, DDP/DAP), U35 Fulfillment (docs), U45 Procurement (imports), U25 Marketplace (cross-border sellers) |
| Master references | Master Logistics "Customs, Global Trade" (no owner before A-35) |

> Global Trade owns **moving goods across customs borders lawfully**: tariff classification (HS + national extensions), country of origin & preferential origin (FTAs), landed-cost calculation (duties, import taxes, fees), Incoterms/DDP-DAP choices, customs declarations & commercial invoices, restricted/prohibited goods per destination, export controls (dual-use, ECCN/SCOMET), denied-party/sanctions screening of parties and destinations, and free-zone/bonded flows.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| TRD-L1 | No cross-border shipment is dispatched without completed screening (party + goods + destination) and required documents. | Fulfillment dispatch guard. |
| TRD-L2 | Buyers see duties/taxes or the duty-payment model (DDP vs DAP) before purchase. | Checkout requires landed-cost result for cross-border carts. |
| TRD-L3 | Classifications and origin determinations are versioned with evidence; changes don't alter past declarations. | Versioned facts. |

## 2. Objects
`CustomsTerritory { jurisdiction(s), union?, deMinimis thresholds, rules pack }` · `TariffClassification { gproduct|unit, hsCode, nationalCode per territory, evidence, confidence, approvedBy }` · `OriginDetermination { unit, countryOfOrigin, preferential: [{agreement, criterion}], evidence }` · `LandedCostQuote { lines, destination, incoterm, duties[], taxes[], fees[], total, validUntil: TimePoint }` · `TradeRestriction { territory, goods (HS/attribute rule), kind: prohibited|restricted|licence-required, licenceType }` · `ScreeningResult { subject (party/destination/goods), lists checked (OFAC, UN, EU, UK, MHA/DGFT…), result, matches, reviewer }` · `CustomsDeclaration { shipment, type (export/import/postal CN22/CN23), documents, status, broker }`.

## 3. Commands, Queries, Events, APIs
Commands: `Classify(unit)`, `DetermineOrigin`, `QuoteLandedCost`, `Screen(subject)`, `ResolveScreeningMatch`, `PrepareDeclaration`, `FileDeclaration` (broker/customs port), `RecordClearance`.
Events: `trade.screening.hit|cleared`, `trade.declaration.filed|cleared|held`.
Ports: `landed-cost.engine`, `screening.lists`, `customs.broker`, `customs.authority` (ICEGATE India, UAE Mirsal, EU ICS2/AES…).
```text
POST /v1/trade/landed-cost   POST /v1/trade/screen   POST /v1/trade/classifications   POST /v1/trade/declarations
```

## 4. Gaps
```prolog
gap(cross_border_without_landed_cost, T) :- tenant(T), ships_cross_border(T), not capability(T, trade.landed-cost).
gap(unclassified_cross_border_units, T, N) :- tenant(T), cross_border_units_without_hs(T, N), N > 0.
gap(screening_missing, T) :- tenant(T), ships_cross_border(T), not capability(T, trade.screening).
```

## 5. AI, Ops, UI, Scale
AI: HS classification suggestions (customs-broker approval for regulated), document data extraction, screening false-positive triage (human decides). Signals: `screening_hits`, `customs_hold_rate`, `duty_estimate_accuracy`. Views: `trade.classification.workbench`, `trade.screening.queue`, `checkout.duties` (landed cost display), `trade.declaration.console`. T1.

## Appendix
- **C.** 0.1.0.

# U47 — Manufacturing Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U47-manufacturing` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-manufacturing` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 |
| Depends on | U18 Product (product models, BOM attachment), U20 Inventory (materials, WIP, finished goods), U45 Procurement (purchased parts), U17 Resource (work centres, machines, operators), U13 Temporal (shift calendars, capacity, schedules), U92 IoT (machine signals), U55 Twin (lines), U30 Ledger (WIP/costing), U99 Quality & HSE (inspections, NCRs), U79 Installed Base (serials produced), U98 ESG (energy/emissions) |
| Depended on by | Industry packs (discrete, process, food, pharma GMP), make-to-order commerce, configure-to-order (U18 configurator) |
| Master references | §6.2 U47 |

> Manufacturing owns **making things**: bills of materials (engineering and manufacturing), routings and operations, work centres, production orders, material requirements planning (MRP), shop-floor execution (dispatch, start/stop, consumption, output, scrap), batch/lot genealogy, and production costing. Quality inspections and NCRs are U99; machine data is U92.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| MFG-L1 | Production consumes and produces inventory only through U20 movements with lot/serial genealogy. | Movement commands; genealogy graph. |
| MFG-L2 | BOMs and routings are versioned with effectivity (TimeRange or serial range); orders pin the versions used. | Effectivity resolution at release. |
| MFG-L3 | Regulated manufacturing (GMP, 21 CFR Part 11, ISO 13485) uses electronic batch records with e-signatures and audit trails. | Pack-level controls + U68/U09 signatures. |
| MFG-L4 | Schedules respect work-centre calendars and finite capacity where declared. | U13 capacity + scheduler. |

## 2. Objects
`BOM { product, version, effectivity: TimeRange, lines [{component, quantity: Quantity, scrap %}] }` · `Routing { product, operations [{seq, workCentre, setup: Duration, runPerUnit: Duration, instructions}] }` · `WorkCentre` (U17 resource pool) · `ProductionOrder { product, quantity, BOM@v, routing@v, due: TimePoint, status, operations progress }` · `MRPRun { horizon: TimeRange, demand, supply, planned orders/POs }` · `BatchRecord { order, lot, steps, signatures, deviations }` · `Genealogy` (lot/serial graph).

## 3. Commands, Events, APIs
Commands: `PublishBOM`, `PublishRouting`, `RunMRP`, `ReleaseOrder`, `StartOperation`, `ReportConsumption`, `ReportOutput`, `ReportScrap`, `CloseOrder`, `SignBatchStep`.
Events: `manufacturing.order.released|completed`, `manufacturing.operation.started|completed`, `manufacturing.mrp.completed`.
```text
POST /v1/mfg/boms   POST /v1/mfg/routings   POST /v1/mfg/mrp-runs   POST /v1/mfg/production-orders
POST /v1/mfg/production-orders/{id}/operations/{seq}:start|:complete
```

## 4. Gaps, UI
```prolog
gap(gmp_without_ebr, T) :- tenant(T), industry(T, pharma), capability(T, manufacturing.core), not capability(T, manufacturing.ebr).
```
AI: schedule optimisation, yield/scrap prediction, predictive maintenance via U55/U94. Views: BOM/routing editor, MRP results, production schedule (Gantt), shop-floor terminal (big-button UI), batch record, genealogy explorer. T1 for shop floor (edge mode with offline sync).

## Appendix
- **C.** 0.1.0.

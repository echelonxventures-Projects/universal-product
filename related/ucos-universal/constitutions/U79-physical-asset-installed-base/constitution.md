# U79 — Physical Asset & Installed Base Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U79-installed-base` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-assets` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 (serialised units sold, ownership, registration), P5 (enterprise asset management for own assets, maintenance plans, IoT link) |
| Depends on | U18 Product Intelligence (GPID), U34 Inventory (serials), U26 Order (sale), U11 Party (owner), U12 Geography (location), U13 Temporal (maintenance schedules), U92 IoT & Devices, U80 Warranty |
| Depended on by | U80 Warranty & After-sales, U82 Field Service, U83 Rental & Leasing, U30 Ledger (fixed assets, P2+), U55 Twin, U98 ESG (lifecycle/circularity) |
| Master references | Gap analysis A-29 ("Asset" in master Existence list; U43 is files) |

> Installed Base owns **individual physical things over their life**: each serialised unit (a specific phone, car, compressor, laptop, building elevator), its owner/custodian history, location, configuration (installed components, firmware), condition, meter readings, maintenance plans and history, and end-of-life (refurbish, resale, recycle). It covers both **customer-owned units** (sold by tenants; installed base) and **enterprise-owned assets** (EAM: fleet, machines, buildings, IT hardware). Global product facts stay in U18; stock-in-warehouse stays in U34 until sale/commissioning.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| IB-L1 | Every serialised unit has exactly one `AssetUnit` record from first known event (manufacture/receipt) to disposal; identity never changes even across owners. | Unique (GPID, serial) + UGID. |
| IB-L2 | Ownership and custody changes are events with evidence; current owner is derived. | Event-sourced custody chain. |
| IB-L3 | Personal data linked to units (owner, location) follows purpose & retention; transfers to new owners never expose previous owners' data. | Policy obligations + U66. |

## 2. Objects
- `AssetUnit { id, gproduct: GPID, serial, identifiers (IMEI, VIN, MAC — some restricted), kind: customer-owned|enterprise-owned|leased|rental-fleet, owner: PartyRef, custodian?: PartyRef, location: GeoRef, installedAt?: PlaceRef, parentUnit? (component of), components: [AssetUnitRef], configuration (firmware, installed options), condition: new|good|fair|poor|failed, meters: [{kind: hours|km|cycles|kWh, reading: Quantity, at: TimePoint}], status: in-stock|sold|installed|in-service|under-repair|retired|recycled, lifecycle dates (TemporalRefs), digitalTwin?: TwinRef, device?: DeviceRef (U92) }`
- `CustodyEvent { unit, from, to, kind: sale|transfer|lease-out|return|loan|theft-report|recovery|disposal, evidence, at: TimePoint }`
- `MaintenancePlan { id, applicability (GPID/model/category), tasks: [{name, interval: Duration|meter threshold, checklist, parts}], schedule: TemporalPolicy/Trigger }`
- `MaintenanceRecord { unit, task, performedBy, workOrder (U82), parts used, result, at: TimePoint }`
- `Disposal { unit, method: resale|refurbish|recycle|scrap|donate, certificate (e-waste compliance), at: TimePoint }`

## 3. Commands, Queries, Events, APIs
Commands: `RegisterUnit` (from receipt/sale/import/IoT provisioning), `RecordCustodyEvent`, `RecordMeterReading`, `AssignMaintenancePlan`, `RecordMaintenance`, `ReportTheft`, `RetireUnit`, `RecordDisposal`.
Queries: `UnitsOwnedBy(party)`, `UnitBySerial(gpid|scheme, serial)`, `ServiceHistory(unit)`, `DueMaintenance(scope, horizon)`, `InstalledBase(gproduct|model, region)`.
Events: `installed-base.unit.registered|transferred|maintenance-due|retired`, `installed-base.meter.recorded`.
```text
POST /v1/installed-base/units       GET /v1/installed-base/units?owner=&serial=
POST /v1/installed-base/units/{id}/custody      POST /v1/installed-base/units/{id}/meters
GET  /v1/installed-base/maintenance/due?scope=
```

## 4. Rules
Maintenance triggers via Temporal (time-based) and condition triggers (meter thresholds, IoT telemetry anomalies) → Field Service work orders (U82). Recall matching: U18 recall × installed base → owner notifications (U40) and service campaigns. Stolen-unit flags block resale/registration in marketplaces (policy).

## 5. Security & Compliance
Identifiers like IMEI/VIN are `confidential`; location of consumer units `PII:LOCATION`; e-waste rules (India E-Waste Rules 2022, EU WEEE) via Disposal certificates; right-to-repair data access (spare parts/manuals availability periods) recorded as obligations (U67).

## 6. Gaps
```prolog
gap(serialised_product_without_registration, T, P) :- tenant(T), sells_serialised(T, P), not registration_flow(T, P).
gap(maintenance_plan_missing, M) :- model(M), maintenance_required(M), not maintenance_plan(M).
gap(recall_unnotified, R, U)     :- recall(R), affects_unit(R, U), owner(U, O), not notified(O, R).
```

## 7. AI & Ops & UI & Scale
AI: predictive maintenance from meters/IoT (P5), failure-mode clustering from service history. Signals: `units_registered_total`, `maintenance_overdue_total`, `mtbf_hours{model}`. Views: `installed-base.my-products` (customer: registered devices, warranties, manuals, service requests), `asset.register` (EAM list/map), `asset.detail` (custody chain, meters, maintenance timeline, components tree), `maintenance.planner`. Scale: 10⁹ units platform-wide; partitioned by tenant; T1.

## Appendix
- **C.** 0.1.0.

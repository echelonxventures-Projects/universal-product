# U36 — Logistics Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U36-logistics` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-logistics` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 (multi-carrier rating & selection, carrier network registry, transit times from carrier APIs, tracking normalisation, pickups, NDR/RTO handling, own-fleet last mile basics), P5 (route optimisation, fleet & drivers at scale with U37) |
| Depends on | U35 Fulfillment (shipments), U12 Geography (zones, maps port, serviceability), U13 Temporal (pickup schedules, cut-offs, carrier calendars, transit durations), U62 Integration (carrier connectors), U90 Global Trade (customs docs, e-way bills), U17 Resource (vehicles, drivers), U92 IoT (telematics), U14 Units (weights, dimensions), U23 Pricing (shipping fees) |
| Depended on by | U35 (takes over `logistics.carrier` port per U35 Appendix P1), U24 Checkout (delivery options & fees), U37 Mobility, U98 ESG (transport emissions), U82 Field Service (routing) |
| Master references | §17.1 (carrier connectors), U35 Appendix P1 (migration) |

> Logistics owns **moving parcels and freight**: carrier and service registry, rate shopping and carrier selection rules, label and manifest generation, pickups, normalised tracking events and delivery exceptions (NDR — non-delivery reports, RTO), e-way bills/transport documents (with U31/U90), own-fleet routing and dispatch for last mile, and logistics performance (on-time, damage, cost per shipment).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| LOG-L1 | Carrier choice follows declared selection rules (cost, promise, performance, serviceability, restrictions like hazmat/COD) and is explainable per shipment. | Decision `logistics.carrier-selection` + stored scores. |
| LOG-L2 | Tracking events from all carriers are normalised to one canonical status model with original codes preserved. | Mapping tables per connector; unmapped code → gap. |
| LOG-L3 | Transport/legal documents (e-way bill above thresholds, dangerous goods declarations, customs) exist before dispatch where required. | Dispatch guard (FUL) + rules from U31/U90. |
| LOG-L4 | Driver and recipient personal data are minimised; live location sharing is time-boxed to active deliveries. | Purpose + Temporal validity on location sharing. |

## 2. Objects
`Carrier { id, connector (U62), services [{code, mode: surface|air|express|same-day|freight, serviceArea: zones, maxWeight, codSupported, hazmat}], calendars, performance }` · `RateQuote { shipment draft, carrier service, price: Money, transit: Duration (business), validUntil: TimePoint }` · `CarrierSelection { shipment, candidates [{service, score breakdown}], chosen, rule version }` · `Manifest { carrier, pickup location, shipments, pickupWindow: TimeRange, status }` · `TrackingEvent { shipment, canonicalStatus (created|picked-up|in-transit|out-for-delivery|delivered|exception|rto-initiated|rto-delivered|lost|damaged), carrierCode, location (U12), at: TimePoint }` · `DeliveryException (NDR) { shipment, reason, attempts, buyer action (reschedule/address correction via link), deadline: TimePoint, resolution }` · `Route { vehicle, driver, stops [{shipment/pickup, arrivalRange: TimeRange, eta: TimePoint}], optimisedAt: TimePoint }` · `TransportDocument { kind: e-way-bill|dg-declaration|cmr|awb, refs, validity: TimeRange }`.

## 3. Commands, Queries, Events, APIs
Commands: `RegisterCarrier`, `RateShop(shipment)`, `SelectCarrier`, `CreateManifest`, `SchedulePickup`, `IngestTracking` (webhook/poll), `RaiseNDR`, `ResolveNDR`, `PlanRoutes` (own fleet), `GenerateTransportDocument`.
Queries: `Rates`, `TransitTime(origin, destination, service)`, `CarrierScorecard`, `RouteStatus`.
Events: `logistics.tracking.updated`, `logistics.ndr.raised|resolved`, `logistics.pickup.completed|missed`, `logistics.route.planned`.
```text
POST /v1/logistics/rates   POST /v1/logistics/manifests   POST /v1/logistics/pickups   POST /v1/logistics/ndr/{id}:resolve
POST /v1/logistics/routes:plan   POST /hooks/carrier/{provider}
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(unmapped_carrier_status, C, Code) :- tracking_code_seen(C, Code), not canonical_mapping(C, Code).
gap(eway_bill_rule_missing, T)        :- tenant(T), in_scope(T, jur:IN), ships_goods(T), not rule(T, eway-bill-threshold).
gap(no_ndr_flow, T)                   :- tenant(T), capability(T, logistics.core), not workflow(T, ndr.flow).
```
AI: transit-time prediction, carrier performance forecasting, address quality before dispatch, route optimisation (solver pack), NDR reason classification. Signals: `on_time_delivery_ratio{carrier}`, `ndr_rate`, `rto_rate`, `cost_per_shipment`, `first_attempt_delivery_rate`. Views: carrier settings & rules, rate-shop inspector, manifest/pickup board, NDR action queue + buyer NDR page, route planner (map + timeline), carrier scorecards. T1.

## Appendix
- **C.** 0.1.0.

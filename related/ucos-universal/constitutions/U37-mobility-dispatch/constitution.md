# U37 — Mobility & Dispatch Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U37-mobility` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-mobility` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 |
| Depends on | U17 Resource (vehicles, drivers), U12 Geography (live location, geofences, maps/ETA port), U13 Temporal (shifts, scheduled rides, time-boxed location sharing), U23 Pricing (fares, surge as decision), U29 Payment, U69 Risk, U70 Trust (two-sided ratings), U92 IoT (telematics), U40 Communication (masked calling), U36 Logistics (delivery fleets) |
| Depended on by | Ride-hailing, quick-commerce delivery, courier, ambulance/field dispatch, U82 Field Service (dispatch strategy reuse) |
| Master references | §30 (Uber-like composition), U36 (fleet last mile) |

> Mobility owns **real-time matching of moving supply to demand**: trip/job requests, driver/courier availability states, matching and dispatch (broadcast, nearest, batched assignment), live tracking, ETAs, fare estimation and final fare (via U23), trip lifecycle, safety features (SOS, trip sharing, masked contact), and driver earnings statements (paid via U29/U30).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| MOB-L1 | Dispatch decisions are logged with candidates and reasons; no discrimination on protected attributes; acceptance-rate penalties follow published rules. | Dispatch log; fairness audit. |
| MOB-L2 | Location sharing is limited to the active trip window plus a short safety buffer. | Temporal validity; LOG-L4. |
| MOB-L3 | Fare estimates and surge multipliers are shown before booking; caps and regulatory fare rules (e.g., India Motor Vehicle Aggregator Guidelines 2020/2025) are enforced. | Pricing decision + jurisdiction cap rules. |
| MOB-L4 | Safety: SOS reaches responders with location; driver verification (licence, background check, vehicle docs) is valid at trip time. | U09 verification validity; SOS workflow. |

## 2. Objects
`TripRequest { rider, pickup, dropoff (U12), product (ride class/delivery), scheduledFor?: TimePoint, fareEstimate }` · `SupplyState { driver (resource), vehicle, status: offline|available|en-route|on-trip, location, at: TimePoint }` · `Dispatch { request, candidates [{driver, eta: Duration, score}], offers, assigned, strategy version }` · `Trip { request, driver, timeline (accepted, arrived, started, completed: TimePoint), route trace, fare: Money breakdown, ratings }` · `EarningsStatement { driver, period: TimeRange, trips, incentives, deductions, net }`.

## 3. Commands, Events, APIs
Commands: `RequestTrip`, `CancelTrip`, `GoOnline|Offline`, `UpdateLocation` (stream), `Dispatch`, `AcceptOffer|DeclineOffer`, `Arrive`, `StartTrip`, `CompleteTrip`, `TriggerSOS`.
Events: `mobility.trip.requested|assigned|started|completed|canceled`, `mobility.sos.triggered`.
```text
POST /v1/mobility/trips   POST /v1/mobility/trips/{id}:cancel|:start|:complete   WS /v1/mobility/stream (location, offers)
```

## 4. Gaps, UI
```prolog
gap(no_sos_flow, T) :- tenant(T), capability(T, mobility.core), passenger_transport(T), not workflow(T, sos.flow).
```
AI: demand forecasting and heatmaps, ETA models, batching/matching optimisation, fraud (GPS spoofing). Views: rider app (map, booking, live trip), driver app (offers, navigation, earnings), dispatcher console (live map, manual assign), surge/zone editor. T0 for dispatch path (cell-local).

## Appendix
- **C.** 0.1.0.

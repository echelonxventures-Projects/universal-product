# U83 — Rental & Leasing Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U83-rental` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce |
| Steward | `ucos:org:commerce-rental` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 |
| Depends on | U13 Temporal (availability, reservations, late fees timers), U79 Installed Base (rental fleet units), U17 Resource, U23 Pricing (time-based rates), U84 Stored Value (deposits) / U29 Payment (holds), U42 Document (agreements), U09 Identity (KYC/licence checks), U80 (damage/repair) |
| Depended on by | U21 Catalog (rental listings), U26 Order, industry packs (car rental, equipment, fashion rental, short-term stays via U-stays pack) |
| Master references | Gap analysis A-29; master §1 "Rental" commerce model |

> Rental owns **temporary use of physical (or digital) things for a fee**: rental products and rate plans, rental agreements, check-out/check-in with condition reports, deposits and pre-authorisations, extensions, late returns and fees, damage assessment and charges, fleet utilisation; and **leasing** (longer-term finance-like arrangements, with lease schedules; regulated finance leases route to U100).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| RNT-L1 | Rental periods and availability are Temporal reservations on specific units or pools; no double-booking. | U13 reservation atomicity. |
| RNT-L2 | Condition at check-out and check-in is recorded with evidence (photos, checklist, meters) before damage can be charged. | Damage charge requires both condition reports. |
| RNT-L3 | Deposits are held (payment pre-auth or stored value) and released/settled with an itemised statement. | Settlement workflow. |
| RNT-L4 | Eligibility checks (age, licence, KYC) required by asset class are enforced before handover. | Decision `rental.eligibility` + Identity verifications. |

## 2. Objects
`RentalProduct { listing, pool: fleet units (U79) or quantity pool, rateplans: [{unit: hour|day|sol|week|month, price via U23, minDuration, maxDuration: Duration, mileage/usage allowances}], deposit: Money|rule, eligibility: DecisionRef, bufferBetweenRentals: Duration }` ·
`RentalAgreement { id, renter: PartyRole, units, period: ReservationRef (U13), pickup/return locations, rates snapshot, deposit hold ref, terms document, status: reserved|checked-out|extended|overdue|checked-in|settled|cancelled }` ·
`ConditionReport { agreement, unit, phase: out|in, checklist, photos (Assets), meters, fuel/charge level, signedBy }` ·
`DamageAssessment { agreement, items: [{description, evidence, cost: Money (repair quote U80)}], decision, dispute? }` ·
`Lease { id, lessee, units, term: TimeRange, schedule: Recurrence (payments), residual value, buyout option, regulated: bool → U100 }`.

## 3. Commands, Queries, Events, APIs
Commands: `ReserveRental`, `CheckOut(conditionReport)`, `ExtendRental`, `CheckIn(conditionReport)`, `AssessDamage`, `SettleAgreement` (final charges − deposit), `CancelRental`, `CreateLease`.
Queries: `AvailabilityForRental(product, range, location)`, `AgreementStatement(id)`, `FleetUtilisation(scope, range)`.
Events: `rental.agreement.reserved|checked-out|overdue|checked-in|settled`, `rental.damage.assessed`.
```text
POST /v1/rental/agreements   POST /v1/rental/agreements/{id}:check-out|:extend|:check-in|:settle
GET  /v1/rental/availability?product=&from=&to=&location=
```

## 4. Rules
Late returns: Temporal deadline trigger → overdue state → late fees per decision `rental.late-fee`; extensions re-check availability; pricing picks the cheapest valid combination of rate units (e.g. 1 week vs 6 days) per decision `rental.rate-optimisation`.

## 5. Security & Compliance
Deposits under consumer law & payment rules (pre-auth expiry windows), driving licence verification (vehicle rentals), telematics data (location) purpose-limited; damage disputes via U71.

## 6. Gaps
```prolog
gap(rental_without_condition_checklist, P) :- rental_product(P), not condition_checklist(P).
gap(rental_without_deposit_policy, P) :- rental_product(P), high_value(P), not deposit_rule(P).
```

## 7. AI & Ops & UI & Scale
AI: damage detection from before/after photos, utilisation optimisation, dynamic rental pricing (bounded). Signals: `utilisation_ratio{pool}`, `overdue_total`, `damage_dispute_ratio`. Views: storefront date-range picker + rate breakdown, `rental.counter` (check-out/in mobile with camera checklist), `rental.fleet.calendar` (U13 resource grid), `rental.statement`. T1.

## Appendix
- **C.** 0.1.0.

# U105 — Workplace & Facilities Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U105-workplace` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:workplace` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 |
| Depends on | U12 Geography (sites, buildings, floors — local frames via U77), U13 Temporal (desk/room booking via AvailabilityWindow, Reservation, FindCommonAvailability, FEED), U17 Resource (rooms, desks as resources), U79 Installed Base (building assets), U82 Field Service (facility work orders), U92 IoT (occupancy sensors, access control), U09 Identity (visitors, badges), U98 ESG (energy) |
| Depended on by | U46 Workforce (hybrid work), U101 QHSE (site safety), real-estate & facility-management packs |
| Master references | APQC 10.x (manage assets — facilities) (A-52) |

> Workplace owns **the physical workplace experience and facility operations**: buildings/floors/spaces (space inventory and plans), space types and capacity, desk/room/parking booking (hot-desking), visitor management (pre-registration, check-in, badges, NDA), occupancy & utilisation, moves/adds/changes, facility service requests (cleaning, catering, maintenance → U82), and access control integration.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| WP-L1 | All bookings are Temporal reservations on space resources (no double booking; buffers; auto-release if no check-in). | U13 AV + no-show trigger. |
| WP-L2 | Visitor data is minimised, purpose-bound and auto-deleted after retention. | U66 retention rule. |
| WP-L3 | Occupancy analytics are aggregated/anonymised; individual location tracking requires explicit lawful basis. | Classification + purpose. |

## 2. Objects
`Building { site (U12 Place), floors, address, calendar (U13) }` · `Space { floor, type: desk|meeting-room|office|parking|locker|lab|common, capacity, amenities, bookable: bool, resource (U17), geometry (local frame) }` · `Booking` = U13 `Reservation` (purpose: workplace) with check-in state · `Visit { host, visitor (party, minimal), expectedAt: TimePoint, checkedInAt?: TimePoint, badge, documents (NDA via U89), status }` · `OccupancyReading { space, count, at: TimePoint, source: sensor|check-in }` · `MoveRequest`, `FacilityRequest` (→ U82 ServiceRequest).

## 3. Commands, Events, APIs
Commands: `DefineSpace`, `BookSpace` (via U13), `CheckIn`, `ReleaseNoShow` (trigger), `PreRegisterVisitor`, `CheckInVisitor`, `RequestFacilityService`.
Events: `workplace.booking.checked-in|released`, `workplace.visitor.arrived`.
```text
POST /v1/workplace/spaces   POST /v1/workplace/bookings   POST /v1/workplace/visits   GET /v1/workplace/occupancy?building=
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(bookable_space_without_resource, S) :- space(S), bookable(S), not resource_of(S, _).
```
AI: space utilisation insights, meeting-room right-sizing, visitor pre-check. Views: floor-plan booking map (accessible list alternative), visitor kiosk (U64 kiosk renderer), facilities dashboard. T3.

## Appendix
- **C.** 0.1.0.

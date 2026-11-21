# U81 — Ticketing & Events Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U81-ticketing` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce |
| Steward | `ucos:org:commerce-ticketing` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 |
| Depends on | U13 Temporal (event schedules, sales windows), U12 Geography (venues; virtual venues via U77), U21 Catalog, U23 Pricing (tiers, dynamic), U22 Offer, U24 Checkout, U29 Payment, U09 Identity (holder verification), U40 Communication, U41 Content (live streams for virtual events) |
| Depended on by | industry packs (entertainment, sports, travel/transport seats, education events, conferences, museums), U70 Trust (reviews of events) |
| Master references | Gap analysis A-29 |

> Ticketing owns **admission rights to time-and-place-bound experiences**: events and performances (sessions), venues and seat maps (reserved seating, general admission, sections, accessible seating), ticket inventory and holds, ticket types/tiers, issuance (barcodes/QR, wallet passes, NFC), transfer and authorised resale, access control (scan/validate), and capacity management — for physical, virtual and hybrid events. Transport seats (bus/train/flight) reuse the same seat-inventory model via the travel pack.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| TKT-L1 | A seat/capacity unit can be held or sold to at most one holder at a time (atomic holds with expiry). | Seat-level reservations via U13 pattern; sharded GA counters. |
| TKT-L2 | Ticket credentials are unforgeable and verifiable offline (signed tokens, rotating QR), with revocation on transfer/refund. | Signing via U65; scanner validation lists. |
| TKT-L3 | Resale/transfer follows organiser policy and jurisdictional caps (e.g. anti-scalping price caps). | Decision `ticketing.resale-policy` + compliance rules. |
| TKT-L4 | Accessible seating and companion tickets are protected inventory. | Inventory class guards. |

## 2. Objects
`Venue { place (U12) or virtual venue (U77), layout versions }` · `SeatMap { venue, sections, rows, seats (id, coordinates, class: standard|accessible|companion|obstructed, attributes), GA areas with capacity }` · `Event { id, name, performer(s), category, sessions }` · `Session { event, start/end (TemporalRef), venue+seatMap version, onSale/offSale TemporalPolicies, capacity, status }` · `TicketType { session, tier, priceRef (U23), inventory class/seat filter, limits per order, eligibility (member/presale code) }` · `TicketHold { seats|qty, holder, expiresAt: TimePoint }` · `Ticket { id, session, seat|GA, holder: PartyRef, credential: {format: qr-rotating|barcode|nfc|wallet-pass, token}, status: issued|transferred|resale-listed|scanned|refunded|void }` · `Scan { ticket, gate, at: TimePoint, result }`.

## 3. Commands, Queries, Events, APIs
Commands: `DefineVenue/SeatMap`, `CreateEvent/Session`, `DefineTicketTypes`, `HoldSeats` (best-available or pick), `IssueTickets` (on order confirmation), `TransferTicket`, `ListForResale`, `ValidateScan`, `CancelSession` (mass refund workflow).
Queries: `SeatAvailability(session)` (real-time map), `BestAvailable(session, qty, filters)`, `MyTickets(party)`.
Events: `ticketing.seats.held|released`, `ticketing.ticket.issued|transferred|scanned`, `ticketing.session.cancelled`.
```text
GET  /v1/ticketing/sessions/{id}/availability     POST /v1/ticketing/sessions/{id}/holds
POST /v1/ticketing/tickets/{id}:transfer|:resell  POST /v1/ticketing/scans
```

## 4. Rules
On-sale spikes: virtual waiting room (queue tokens, fair randomisation) before holds; bot protection; per-party limits; hold TTL decision `ticketing.hold-ttl`; dynamic pricing within organiser guardrails (U23).

## 5. Security & Compliance
Anti-bot (Better Online Ticket Sales Act-type laws), price transparency (all-in pricing), resale caps per jurisdiction, accessibility law for seating, refunds on cancellation per consumer law.

## 6. Gaps
```prolog
gap(no_accessible_inventory, S) :- session(S), venue_requires_accessible(S), not accessible_seats(S).
gap(no_waiting_room, T)        :- tenant(T), high_demand_sales(T), not capability(T, ticketing.waiting-room).
```

## 7. AI & Ops & UI & Scale
AI: demand forecasting/pricing, bot detection. Signals: `onsale_hold_latency_ms`, `queue_wait_s`, `scan_throughput`, `fraudulent_scan_attempts`. Views: interactive seat map (accessible list alternative), `waiting.room`, `my-tickets` (wallet passes), `scanner` (offline-capable mobile), `event.manager`. Scale: 100k holds/min peak per on-sale; T0 during on-sale windows.

## Appendix
- **C.** 0.1.0.

# U34 — Inventory Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U34-inventory` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-inventory` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (single & multi-location stock, reservations), P2 (transfers, cycle counts, lots/serials), P4 (forecast-driven replenishment) |
| Depends on | U21 Catalog (SellableUnit), U10 Org (stores/sites), U12 Geography, U14 Currency & Unit (quantities, packaging), U13 Temporal (reservation TTL, allocation windows) |
| Depended on by | U24 Checkout (availability, reserve), U35 Fulfillment (allocation, pick), U44 Search (in-stock facet), U45 Procurement (P4), U30 Ledger (inventory valuation, P2) |
| Master references | §6.2 U34, §13.3 (aggregate transactions), Temporal reservation pattern (U13 §5.6) |

> Inventory owns **how much of each sellable unit exists, where, in what state, and what is promised**: stock locations, stock items, quantities by state, reservations (soft holds), allocations (hard commitments to fulfilment), adjustments, transfers, lots/serials/expiry, and availability computation (ATP). It does not choose which node fulfils (U35) or buy stock (U45).

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| INV-L1 | Stock quantities change only through typed movements (receipt, adjustment, reservation, allocation, pick, ship, return, transfer) — never by overwriting a number. | Movement ledger table; balances are projections. |
| INV-L2 | Availability (ATP) = on-hand − reserved − allocated − safety stock − damaged/quarantine, per location, computed by one function. | `Availability` query only. |
| INV-L3 | Reservations expire automatically; expired reservations release stock. | Temporal triggers (U13). |
| INV-L4 | Oversell is allowed only if policy explicitly permits (backorder/pre-order) per unit/location. | Decision `inventory.oversell-policy`. |
| INV-L5 | Lot/serial/expiry tracking is mandatory where the category requires it (pharma, food, electronics serials). | Taxonomy node policy → unit flag. |

---

## 2. Objects
- **`StockLocation`** `{ id, kind: warehouse|store|dark-store|3pl|seller-site|in-transit|virtual, site: PlaceRef, organization, fulfilmentCapabilities: [ship, pickup, same-day], calendar: CalendarRef, status }`
- **`StockItem`** `{ id, unit: SellableUnitRef, location, tracking: none|lot|serial, uom: PackagingUnitRef }`
- **`StockBalance`** (projection) `{ stockItem, onHand, reserved, allocated, inbound, damaged, quarantine, safetyStock, available (ATP), version }`
- **`StockMovement`** `{ id, stockItem, type: receipt|adjustment|reserve|release|allocate|deallocate|pick|ship|return|transfer-out|transfer-in|damage|count-correction, qty (signed, Quantity), lot?, serials?, reason: taxonomy, refs: {order?, reservation?, transfer?, count?}, at, by }`
- **`StockReservation`** `{ id, stockItem | unit+locations(any-of), qty, holder: checkout|order|cart(optional), expiresAt (Temporal), status: active|converted|released|expired }`
- **`Allocation`** `{ id, fulfillmentOrderLine, stockItem, qty, lot/serial picks, status }`
- **`Lot`** `{ id, stockItem, lotNumber, manufacturedAt: TimePoint, expiresAt (TimePoint), status: ok|expired|recalled }`
- **`Transfer`**, **`CycleCount`** (P2) standard.

---

## 3. Algorithms

### 3.1 Reserve (normative; mirrors U13 §5.6)
```sql
UPDATE stock_balance
   SET reserved = reserved + :q, version = version + 1
 WHERE stock_item = :id AND version = :v
   AND (on_hand - reserved - allocated - safety_stock - damaged - quarantine) >= :q   -- unless oversell policy
```
Zero rows → retry with fresh version (max 3) → `INV_INSUFFICIENT`. Hot SKUs (flash sales): **sharded availability buckets** (stock split into N buckets per location; reserve picks random non-empty bucket; periodic rebalance) to avoid row contention.

### 3.2 Availability query
`Availability(units[], ctx)` → per unit: total ATP across locations eligible for ctx (serviceable to ship-to, channel, store pickup) + per-location detail + earliest restock (inbound) + backorder/pre-order flag. Served from a cached projection (lag p99 < 1 s), authoritative check at reserve time.

### 3.3 FEFO/FIFO picking for lots
Allocation chooses lots by `inventory.pick-strategy` (FEFO default for perishables; exclude lots expiring within `minShelfLifeAtDelivery`).

---

## 4. Commands, Queries, Events, APIs
Commands: `ReceiveStock`, `AdjustStock(reason)`, `Reserve`, `ReleaseReservation`, `ConvertReservation` (→ allocation on order confirm), `Allocate`, `Deallocate`, `RecordPick`, `RecordShip`, `RecordReturn(condition → sellable|damaged|quarantine)`, `TransferStock`, `StartCycleCount`/`SubmitCount`, `SetSafetyStock`, `QuarantineLot`, `RecallLot`.
Events: `inventory.stock.adjusted|received|reserved|released|allocated|shipped|depleted|restocked`, `inventory.lot.expired|recalled`, `inventory.balance.low` (condition trigger via Temporal: `available < threshold for PT5M`).
```text
POST /v1/inventory/movements           GET /v1/inventory/availability?units=&ctx
POST /v1/inventory/reservations        POST /v1/inventory/reservations/{id}:release|:convert
POST /v1/inventory/locations           GET /v1/inventory/balances?location=&unit=
POST /v1/inventory/transfers           POST /v1/inventory/counts
```
Errors: `INV_INSUFFICIENT`, `INV_LOCATION_INACTIVE`, `INV_TRACKING_REQUIRED` (lot/serial missing), `INV_LOT_EXPIRED`, `INV_NEGATIVE_FORBIDDEN`.

## 5. Decision tables
`inventory.oversell-policy` (backorder/pre-order per unit/category/location), `inventory.safety-stock`, `inventory.low-stock-threshold`, `inventory.pick-strategy`, `inventory.reservation-ttl` (default from checkout hold), `inventory.return-disposition`.

## 6. Security & Compliance
Sellers see only their locations/stock; adjustments above threshold need approval (shrinkage fraud); audit all adjustments; lot recall traceability (food/pharma regulations: FSSAI, FDA, EU GDP) — `RecallLot` produces affected orders list via graph.

## 7. Reuse
Checkout reserves through Inventory; Fulfillment allocates/picks/ships through Inventory; Search consumes `inventory.stock.depleted/restocked`; Ledger (P2) values inventory from movements (FIFO/weighted avg per org policy).

## 8. Gaps
```prolog
gap(no_stock_location, T)          :- tenant(T), sells_physical(T), not stock_location(T, _).
gap(tracking_required, U)          :- unit(U), category_requires_lot(U), stock_item(U, _, none).
gap(oversell_unconfigured, T)      :- tenant(T), preorders_offered(T), not oversell_policy(T).
gap(balance_drift, L)              :- location(L), balance_vs_movements_mismatch(L, N), N > 0.
```
Self-healing: nightly recomputation of balances from movements; mismatch auto-correct with audited `count-correction` when ≤ tolerance, else case.

## 9. AI
Demand forecasting & replenishment suggestions (P4), anomaly detection (shrinkage), substitution suggestions for out-of-stock at checkout. Agents may propose reorders; never adjust stock.

## 10. Operations
Signals: `reserve_latency_ms` (p99 < 50 ms), `reserve_conflicts_total`, `oos_rate{category}`, `oversell_incidents_total`, `balance_drift_total` (must be 0 after reconciliation), `expiring_lots_30d`. Runbook: hot SKU contention → enable bucket sharding.

## 11. UI
Views: `inventory.balances.grid` (by location/unit, inline adjust with reason), `inventory.movement.history`, `inventory.receive` (scan-first mobile), `inventory.count` (mobile cycle count), `inventory.transfer`, `inventory.lot.recall`, storefront `availability.badge` ("In stock", "Only 3 left" — only if true, no fake scarcity).

## 12. Scale
10⁹ stock items platform-wide; movement tables partitioned by tenant/month; balances in Postgres with cache; flash-sale sharding. T0 on reserve path.

## Appendix
- **C.** 0.1.0.

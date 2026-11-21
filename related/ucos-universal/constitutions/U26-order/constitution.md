# U26 — Order Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U26-order` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce |
| Steward | `ucos:org:commerce-order` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 |
| Depends on | U24 Checkout, U23 Pricing (quote snapshot), U22 Offer (redemptions), U29 Payment, U31 Tax (tax documents), U34 Inventory, U35 Fulfillment, U13 Temporal (return windows), U60 Workflow, U42 Document (invoices, P2), U30 Ledger (P2) |
| Depended on by | U35 Fulfillment, U30 Ledger, U25 Marketplace (seller split, payouts), U39 Support, U70 Reviews (verified purchase), U72 Analytics |
| Master references | §7.3 (Order object type), §16.1 (order lifecycle workflow), §15.4 (order.placed event) |

> Order owns **the commitment**: `Order` (buyer's confirmed purchase, possibly multi-seller), `OrderLine`, `SellerOrder` (per-seller sub-order for marketplaces), `OrderAdjustment` (post-placement price changes), `ReturnRequest`/`Exchange`, and the order lifecycle. Orders are immutable in their commercial terms: changes are recorded as amendments and adjustments, never edits of the original quote.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| ORD-L1 | An order stores the accepted PriceQuote snapshot, tax determination snapshot and offer redemptions; these are immutable. | Write guard; amendments create new adjustment records. |
| ORD-L2 | Every monetary change after placement is an `OrderAdjustment` with reason and allocation to lines, reconciled with payment/refund and (P2) ledger postings. | Schema + reconciliation job. |
| ORD-L3 | Order state transitions follow the published lifecycle (workflow `order.lifecycle`); no direct status writes. | Workflow-only commands. |
| ORD-L4 | Cancellation and returns follow policy (decision tables + jurisdiction consumer law) and are explainable to the buyer. | Decision outputs include reason text keys. |
| ORD-L5 | Order numbers are unique per tenant and human-friendly; ids are UGIDs. | Generated sequence per tenant. |

---

## 2. Objects

### 2.1 `ucos.order.Order` (master §7.3 refined)
| Attribute | Type | Notes |
|---|---|---|
| `id`, `orderNumber` | UGID, `ORD-{yyyy}-{seq:8}` | |
| `tenant`, `store?`, `channel`, `source` | refs; source: `checkout|pos|b2b-quote|subscription|agent-api|import|marketplace-api` | |
| `buyer` | PartyRoleRef | |
| `sellerOrders` | Composition→SellerOrder | 1..N |
| `currency` | iso4217 | |
| `quote` | PriceQuote snapshot (embedded, signed) | ORD-L1 |
| `taxDetermination` | TaxDeterminationRef (snapshot) | |
| `redemptions` | Array<RedemptionRef> | |
| `payments` | Array<PaymentIntentRef> | |
| `totals` | `{ subtotal, discounts, fees, shipping, tax, grandTotal, paid, refunded, balanceDue }` (Money; computed) | |
| `placedAt` | TimePoint | |
| `addresses` | `{ billing?: AddressRef, shipping per SellerOrder }` | snapshots of formatted address on shipments |
| `status` | lifecycle state | |
| `checkout` | CheckoutRef | idempotency |
| `notes`, `giftMessage` | Text | PII-tagged |

### 2.2 `SellerOrder`
`{ id, order, seller: OrgRef, lines: [OrderLine], fulfilmentOrders: [FulfillmentOrderRef], status (sub-lifecycle), commissionRef (P2), sellerTotals }`

### 2.3 `OrderLine`
`{ id, unit: SellableUnitRef, listingSnapshot: {title, sku, gpid, imageRef}, qty, unitPrice: Money (net per quote), lineDiscounts: [...], tax: {category, amount, rate refs}, lineTotal: Money, status: open|allocated|shipped|delivered|cancelled|returned|partially-returned, returnPolicy: {window: Duration (from decision), restockingFee?} }`

### 2.4 `OrderAdjustment`
`{ id, order, kind: price-correction|goodwill|cancellation|return-refund|shipping-refund|fee-waiver|chargeback, lines: [{line, amount: Money}], reason: TaxonomyNodeRef, initiatedBy, approval?: DecisionRef (above threshold), refund?: RefundRef, taxCreditNote?: TaxDocumentRef }`

### 2.5 `ReturnRequest`
`{ id, order, lines: [{line, qty, reason: taxonomy:return-reason, condition, evidence: [AssetRef]}], resolution: refund|exchange|store-credit|repair, method: pickup|drop-off|keep-it, status: requested|approved|rejected|in-transit|received|inspected|completed, refund?: RefundRef, exchangeOrder?: OrderRef, window: TemporalRef }`

---

## 3. Lifecycle
Order-level workflow is master §16.1 (`order.lifecycle@3`): `placed → confirmed → shipped → delivered → completed`, with `cancelling/cancelled`, `payment_failed`, `exception`, `return_in_progress`. Order status is **derived** from SellerOrder/line states (e.g. `partially-shipped`), rule:

```text
order.status = 
  cancelled            if all lines cancelled
  delivered            if all non-cancelled lines delivered
  partially-delivered  if some delivered
  shipped              if all non-cancelled lines shipped
  partially-shipped    if some shipped
  confirmed            if payment ok (or COD accepted) and none shipped
  placed               otherwise
completed when return windows of all delivered lines elapsed (Temporal trigger) and no open returns/disputes
```

Return workflow `return.flow@2`: request → eligibility (decision `order.return-eligibility`: window, category, condition, jurisdiction law) → approve/auto-approve → reverse logistics (U35) → receive → inspect → refund/exchange (Payment refund + OrderAdjustment + offer redemption reversal pro-rata) → close.

---

## 4. Commands, Queries, Events, APIs

| Command | Events |
|---|---|
| `PlaceOrder(source payload, idempotencyKey)` | `order.order.placed` (master §15.4 payload) |
| `ConfirmOrder` (payment ok/COD) | `order.order.confirmed` |
| `CancelOrder(lines?, reason)` / `CancelSellerOrder` | `order.order.cancelled` / `order.line.cancelled` |
| `AmendOrder` (address change before dispatch, qty reduce) | `order.order.amended` |
| `AdjustOrder(adjustment)` | `order.adjustment.created` |
| `RequestReturn`, `ApproveReturn`, `RejectReturn`, `ReceiveReturn`, `CompleteReturn` | `order.return.*` |
| `CompleteOrder` (system) | `order.order.completed` |

Queries: `GetOrder(id|number)`, `OrdersForBuyer(party, filters)`, `OrdersForSeller(seller, filters)`, `OrderTimeline(id)` (Temporal Timeline merge), `CancellationOptions(order, lines)`, `ReturnOptions(order, lines)`.

```text
POST /v1/order/orders                         GET /v1/order/orders/{id}   GET /v1/order/orders?buyer=&status=
POST /v1/order/orders/{id}:cancel|:amend|:adjust
POST /v1/order/orders/{id}/returns            POST /v1/order/returns/{id}:approve|:reject|:receive|:complete
GET  /v1/order/orders/{id}/timeline
```
Errors: `ORD_NOT_CANCELLABLE` (with reason), `ORD_RETURN_WINDOW_CLOSED`, `ORD_RETURN_NOT_ELIGIBLE`, `ORD_ADJUSTMENT_EXCEEDS_PAID`, `ORD_APPROVAL_REQUIRED`, `ORD_DUPLICATE` (idempotent replay returns existing).

---

## 5. Decision tables
`order.cancellation-policy` (by state, category, time since placement), `order.return-eligibility` (master §16.2 example `returns.window-by-category`), `order.adjustment-approval-threshold`, `order.auto-approve-return` (low value, trusted buyer), `order.goodwill-limits` (per agent role).

## 6. Security & Compliance
Buyer sees own orders; sellers see their SellerOrders (buyer contact masked; masked calling via Communication); support with purpose. Refund/adjustment above thresholds need approval (SoD). Consumer law: cancellation rights, statutory return windows override tenant policy where stricter (rule: `max(tenantWindow, statutoryWindow)` via jurisdiction decisions), invoice issuance (via Tax/Document). Retention: financial record retention per jurisdiction (often 8–10 years) — order financial fields retained; buyer PII minimised after retention.

## 7. Reuse
Fulfillment consumes `order.order.confirmed` to create FulfillmentOrders; Ledger (P2) posts from order/payment/adjustment events (P1 operates without Ledger; events retained for backfill replay when U30 activates); Marketplace computes commissions from SellerOrders.

## 8. Gaps
```prolog
gap(no_return_policy, T, C)   :- tenant(T), sells_category(T, C), not return_policy_covers(T, C).
gap(statutory_window_violation, T, J) :- tenant(T), in_scope(T, J), return_window(T, W), statutory_min(J, M), W < M.
gap(no_invoice_capability, T, J) :- tenant(T), in_scope(T, J), invoice_required(J), not capability(T, tax.invoicing).
```

## 9. AI
Support triage on order issues; return reason classification from free text/images; fraud/abuse signals on returns (P2 risk). Agent tools: `order.get`, `order.cancellation_options`, `order.request_return` (on behalf of buyer with delegation).

## 10. Operations
Signals: `orders_placed_total`, `placed_to_confirmed_seconds` (SLO p95 < 60 s), `cancellation_ratio{reason}`, `return_ratio{category}`, `adjustment_amount_total`. Runbooks: stuck orders (state age > threshold), payment-order mismatch reconciliation.

## 11. UI
Views: buyer `order.list`, `order.detail` (timeline, shipments tracking, actions: cancel/return/help), seller `sellerorder.queue` (W13), ops `order.search`, `order.timeline` (master §7.3 uiModels), `return.request` (wizard with reason, photos, method), `return.inspection` (warehouse).

## 12. Scale
Peak 3k–10k orders/min per large tenant; orders partitioned by tenant and month; read models for buyer/seller lists in OpenSearch. T1 (T0 for PlaceOrder).

## Appendix
- **B. Amendments:** note in master §32 P1 that Ledger (U30) is absent in P1 and order/payment events are replayed into it at P2 activation.
- **C.** 0.1.0.

## Appendix P1 — Phase 1 behaviour without later-phase dependencies
- **U30 Ledger (Phase 2):** see A-19 and U29 Appendix P1.
- **U42 Document:** specified for Phase 1. Invoices and credit notes are issued on order confirmation and on adjustments via U31 → U42.

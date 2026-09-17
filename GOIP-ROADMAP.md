# GOIP Ω∞ — Enterprise Capability Roadmap (Amazon · Flipkart · Paytm · Alibaba · Walmart parity)

Audit of the LUXORA codebase against the target enterprise-surface, plus the build order for closing the gap.
Everything ships into the existing LUXORA entity engine (no per-feature code — registries + Data Studio own
the data). Status legend: ✅ done · 🟡 partial · ❌ missing.

## What already exists (do NOT rebuild)

| Layer | Evidence | Notes |
|---|---|---|
| GOIP constitutional layer | `lib/goip.js` (1798 lines) + `goip_*` tables + `POST /api/goip/:capability` | 8-stage chain, 22 capabilities, 67 domains, 25 benefits, calendars/space/economic/reality registries — all `meta_lists`-seeded. |
| Offers math engine | `lib/offers.js` `HANDLERS` + `evaluate()` + `credit/debit/redeem/reverseRedemption` | GOIP registers its benefit handlers here; money lives in wallets + `coupon_redemptions`. |
| Basic search | `apiProducts` / `buildSearch` | Keyword + dept + price + rating + node facets; single LIKE-based index. |
| Payments (rails) | `lib/providers.js` + `lib/connect.js` + `tenant_gateways` | 16 gateways, 10-country availability; `pay()`/`notify()`/`ping()` via declarative specs. |
| Ledger + wallet | `wallet_entries`, `credit()`/`debit()`, `billing.js` recordUsage/invoices/creditNotes | Single-source-of-truth ledger; GOIP settlement already writes to it. |
| B2B | `contracts`, `tenders`, `rfqs`, `suppliers`, `product_suppliers` | Fixed/tiered pricing, award→auto-contract. |
| Supply (sellers) | `sellers`, `settlements`, `warehouses`, `stock_transfers`, `serialized_items` | Procurement model present; fulfilment tracking not. |

## Gap map — the four build domains

### 1 · Search / Discovery at scale
- ✅ keyword search, dept facet
- 🟡 recommendation (AI Studio local engine, view-based)
- ❌ faceted query API (brand, attribute, UOM, identity, price-band, tax-class), fuzzy/typo match, synonyms, personalization signals, merchandising boost rules, "also bought / also viewed", category deep-links, autocomplete, A/B surface
- Plan: add `lib/search.js` — in-memory inverted index over `products` (+ `variant_groups`, `attribute_defs`, `identity`), faceted result endpoint `GET /api/search?q=&facet=`, boost/merchandising `meta_lists.searchBoost`, and `ai.js` upgrades the rec engine to a co-occurrence matrix from `orders`/`view_history`.

### 2 · Logistics / Supply chain
- ✅ `warehouses`, `stock_transfers`, `serialized_items`, `returns`
- ❌ fulfilment state machine (picked/packed/label/ dispatched/shipped/delivered/failed), 3PL provider abstraction (reusing `provider_defs.kind=shipping` + `connect.js`), live tracking events (HMAC webhooks), SLA/age tracking, multi-warehouse routing + backorder, return disposition (refund/replace/restock/credit)
- Plan: `lib/logistics.js` — `shipments` table + `shipment_events` (HMAC-signed via `events.js`), `dispatch()`/`track()`/`slaBreaches()`/`returnDisposition()` APIs, warehouse routing engine, and admin console screen.

### 3 · Payments & Financial services
- ✅ payment rails, ledger, invoices, credit notes, refunds, dunning, aging
- ❌ chargebacks (`disputes` table + `dispute_state`), multi-gateway failover + auto-retry (`payment_attempts`), payout runs (batch settlement to sellers/creators via `payouts` + `payout_items`), revenue-share split, ledger reconciliation (bank-feed → ledger match/unmatch/batch), cross-border FX settlement (leveraging `fx_rates`)
- Plan: `lib/fin.js` — `disputes`, `payment_attempts`, `payouts`/`payout_items`, `recon_batches`/`recon_lines` + `settlePayout()`, `reconcile()`, `retry()` APIs and `billing.js` extension for usage-metered financial billing (per-offer/per-redemption/per-payout billing model, matching `meta_lists.goipBillingModels`).

### 4 · Marketplace & Seller ecosystem
- ✅ sellers, settlements, take-rate fields
- ❌ ad inventory (`ads`, `ad_groups`), bidding (CPC/CPM/CPA), impression/click ledger with attribution model (click/view/coupon/cross-channel), seller performance dashboard (conversion, SLA, inventory depth, ad ROI), seller onboarding/approval flow, commission auto-deduct on order + auto-invoice to seller
- Plan: `lib/marketplace.js` — `ads`/`ad_groups`/`impressions`/`clicks`/`attribution` tables + `bids` (CPC/CPM/CPA) with a simple GSP-auction ranker, `metrics()` for seller dashboards, and a settlement hook in `billing.js` that deducts take-rate on order settlement.

## Execution order (one commit each, `git status` clean at every step)

1. **This roadmap + gap analysis** ← `GOIP-ROADMAP.md` (step 1)
2. **Search/Discovery** — `lib/search.js`, `GET /api/search`, faceted + recommend engine upgrade, admin Search console
3. **Logistics** — `lib/logistics.js`, shipments/events/dispatch/track/returns routing, admin Logistics console
4. **Payments & Fin services** — `lib/fin.js`, disputes/attempts/payouts/reconciliation + billing model, admin Finance console
5. **Marketplace & Seller** — `lib/marketplace.js`, ads/bidding/attribution/seller dashboards + take-rate settlement

Each step includes: schema + seed (SQLite only; PG migrates via `migrate.js`), a registry/feature flag so the domain is OFF by default until configured, REST + admin console + Data Studio entity defs, and a test in `test/smoke.js` proving end-to-end.

## Non-goals (kept out of scope to stay shippable)
- Global distributed systems (Kafka, multi-region active-active, CDN-POPs) — LUXORA is single-node by design
- Native mobile SDKs, POS hardware, IoT edge
- ML training infrastructure (local heuristic engine only; AI Studio supports external providers)

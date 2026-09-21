# GOIP Ω∞ — Enterprise Capability Roadmap II (Amazon · Flipkart · Paytm · Alibaba · Walmart parity)

The first roadmap (`GOIP-ROADMAP.md`) closed four build domains — Search/Discovery, Logistics,
Payments & Financial services, and Marketplace/Seller. All five steps shipped; the suite is green
(450 assertions). This second roadmap audits what the five target platforms still have that LUXORA
does not, and defines the build order for closing it. Same rules: everything ships into the existing
entity engine (no per-feature code — registries + Data Studio own the data), every domain is OFF by
default until configured, and each step lands one commit with schema + seed + feature flag + REST +
admin console + Data Studio entity defs + a smoke test. Status legend: ✅ done · 🟡 partial · ❌ missing.

## What already exists (do NOT rebuild)

| Layer | Evidence | Notes |
|---|---|---|
| Search / Discovery | `lib/search.js`, `GET /api/search`, `/api/facets`, `/api/reco`, `/api/suggest` | Faceted, typo-tolerant, synonyms, boosts, co-purchase recs. |
| Logistics | `lib/logistics.js`, `shipments`/`shipment_events`, dispatch/track/SLA/return disposition | Fulfilment state machine + 3PL + warehouse routing. |
| Finance | `lib/fin.js`, `disputes`/`payment_attempts`/`payouts`/`recon_*` | Chargebacks, retries, payout runs, bank recon, FX ledger. |
| Marketplace | `lib/marketplace.js`, `ads`/`ad_events`/`attribution`/`seller_metrics` | CPC/CPM/CPA, GSP ranker, seller KPIs, take-rate settlement. |
| Flat reviews | `reviews` table, `POST /api/reviews/:id` | Rating/title/body/verified — no votes, no replies, no moderation queue. |
| Saved items | `saved_items` | Basic wishlist (save-for-later). |
| Platform billing | `subscriptions` (tenant→plan) | **This is SaaS plan billing, not customer recurring orders** — do not confuse the two. |
| Offer-abuse risk | `goip.fraudScore` / `goip.riskScore` | Scores *offer/incentive* abuse per subject, not order checkout risk. |

## Gap map — the five build domains of Roadmap II

### A · Customer Trust & Commerce Content
- 🟡 reviews: present but flat
- ❌ **Q&A on products** — Alibaba/Amazon "Customer Questions & Answers": question per product, answers,
  helpfulness votes, seller/admin can answer, moderation states
- ❌ **Rich reviews**: helpfulness votes (up/down), seller reply thread per review, moderation queue
  (pending/approved/rejected), photo/media attachment
- Plan: extend `reviews` (votes, reply, state, media) + new `qna` table family; `lib/ugc.js` owns both
  (UGC = user-generated content); storefront product page renders Q&A + rich reviews; admin
  moderation console with approve/reject.

### B · Customer Service / Support helpdesk
- ❌ `public/customer-service.html` is a static shell with **no backend at all**
- ❌ tickets (customer-facing create + status), agent queue, assignment, statuses, priorities,
  SLA timers, canned responses, satisfaction (CSAT) rating on close
- Plan: `lib/helpdesk.js` — `tickets`/`ticket_notes`/`ticket_sla`, storefront "Your Cases",
  customer-service.html becomes a real help centre, admin console queue with assign/SLA/CSAT.

### C · Retention & recurring revenue
- ❌ **Subscribe & Save** — recurring customer delivery schedules (frequency, next shipment,
  pause/skip/cancel, one-off reorder) — distinct from platform `subscriptions`; reuses `offers`
  wallet/billing for cycle charges
- ❌ **Membership program** (Prime / Flipkart Plus / Walmart+) — paid tiers, bundled benefits
  (free-shipping, early access, bonus rewards), entitlement grants ride GOIP `goip_entitlements`,
  wallet-billed
- ❌ **Address book** — multiple shipping addresses per customer with a default; checkout picks one
- Plan: `lib/recurring.js` (schedules + cycles + membership tiers), `addresses` table + checkout hook.

### D · Risk & Experimentation
- ❌ **Order fraud screening** — velocity (attempts per owner/IP/window), blocklists (card, email,
  address, IP), risk score 0–100, decision (approve / hold for review / block) at checkout with
  auto-release thresholds; admin review queue
- ❌ **A/B testing** — experiments, variants with traffic split, assignment by customer/hash,
  conversion tracking per variant, significance readout
- Plan: `lib/risk.js` (screening engine, checkpoint in `apiCheckout`), `lib/experiments.js`
  (assignment + conversion), storefront surfaces honor assigned variants.

### E · Supply-chain planning
- ❌ **Demand forecasting / replenishment** — per-SKU demand forecast (moving average + trend from
  `order_items`), reorder point, min/max levels, safety stock, lead-time awareness from
  `product_suppliers`, suggested purchase orders to the primary supplier
- Plan: `lib/planning.js` — reads existing `skus`/`inventory`/`order_items`/`product_suppliers`,
  writes `replenishments` (suggestions + PO drafts), admin Planning console.

## Execution order (one commit each, `git status` clean at every step)

1. **This roadmap + gap analysis** ← `GOIP-ROADMAP-2.md` (step 1)
2. **Customer Trust & Content** — `lib/ugc.js`: rich reviews + Q&A, moderation console, storefront UGC
3. **Support helpdesk** — `lib/helpdesk.js`: tickets, SLA, CSAT; customer-service.html becomes live
4. **Retention** — `lib/recurring.js` (Subscribe & Save + membership), address book + checkout hook
5. **Risk & Experimentation** — `lib/risk.js` checkout screening + `lib/experiments.js` A/B framework
6. **Supply-chain planning** — `lib/planning.js` forecast/reorder/suggested-PO console

Each step includes: schema + idempotent seed (SQLite only; PG migrates via `migrate.js`), a
`settings.features` flag / module so the domain is OFF by default until configured, REST routes,
storefront + admin console surfaces, Data Studio entity defs, and assertions in `test/smoke.js`
proving end-to-end.

## Non-goals (carried forward from Roadmap I)
- Global distributed systems (Kafka, multi-region active-active) — single-node by design
- Native mobile SDKs, POS hardware, IoT edge
- ML training infrastructure (local heuristic engine only; AI Studio supports external providers)

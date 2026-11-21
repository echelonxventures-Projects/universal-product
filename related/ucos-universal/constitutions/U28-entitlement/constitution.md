# U28 — Entitlement Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U28-entitlement` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce |
| Steward | `ucos:org:commerce-entitlements` |
| Version | 0.1.0 (Draft) |
| Delivery phase | **P0** (platform plans & limits for tenants — needed by tenant provisioning; quotas & metering counters; feature gating; API plans), P2 (customer-facing entitlements from subscriptions/purchases: digital content, licences, seats, memberships), P4 (licence keys, offline entitlements, token-gated entitlements via U99) |
| Depends on | U10 Org (tenants), U11 Party, U13 Temporal (validity, quota reset recurrence), U14 Unit (quota units), U72 (usage signals), U03 Policy (feature checks as attributes), U27 Subscription (P2 source of entitlements), U26 Order (P2 one-time purchases) |
| Depended on by | U10 Tenant (plan/limits), U63 API (API product plans, quotas), U57 Capability (marketplace pack licensing), U41 Media (playback rights, P4), U35 Fulfillment (digital delivery), U64 UI (feature visibility), U03 Policy (entitlement attributes in decisions) |
| Master references | §6.3 (entitlement vs permission), master §8.5 (pack licensing) |

> Entitlement owns **what a party is commercially allowed to use and how much**: plans (bundles of features + limits), entitlements granted to tenants/organisations/persons from plans, purchases, subscriptions or promotions, **quotas** and their metering/reset, **feature flags of commercial nature** (as distinct from release flags in U72), seats, licences, and the real-time `Check`/`Consume` API that every capability calls. Permissions (who may perform an action) remain U09/U03; entitlements answer *whether the customer has paid for / been granted it, and how much remains*.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| ENT-L1 | Capability code never hard-codes plan names or limits; it asks `Check(feature|quota)`. | Lint (plan-name literals); certification `ARCH-ENT-01`. |
| ENT-L2 | Every entitlement has a source (plan, subscription, order, promotion, manual grant with approval) and a validity (TimeRange). | Schema. |
| ENT-L3 | Quota consumption is atomic and idempotent; overage behaviour is declared (block, allow-and-bill, soft-warn). | Consume API with idempotency key; decision per quota. |
| ENT-L4 | Entitlement checks are fast and available: local cache with signed snapshots; fail behaviour per feature declared (fail-open for non-critical UX, fail-closed for paid/limited resources). | SDK + `failMode` declaration. |

## 2. Objects
- `Feature { id (e.g. platform.custom-domain, commerce.multi-currency, api.webhooks, media.4k), kind: boolean|tiered|quota-bound, description, owner capability }`
- `Quota { id (e.g. platform.orders-per-month, api.requests-per-minute, platform.storage-gb, platform.agents), unit (U14), resetPolicy: Recurrence | never, window: rolling Duration | calendar period, overage: block|allow-and-bill|warn, meteringSource: event-type | counter }`
- `Plan { id, name, audience: tenant|organization|person|api-client, features: [{feature, value}], quotas: [{quota, limit: Quantity}], price: (via U23/U27), validity: TimeRange, status }` — Phase 1 seed: UCOS platform plans `starter`, `growth`, `enterprise` with tenant limits (orders/month, catalog size, stores, locales, custom domains, API rpm, storage, isolation tier).
- `Entitlement { id, holder: TenantRef|OrgRef|PartyRef|APIClientRef, feature|quota|plan, value/limit, source: {kind, ref}, validity: TimeRange, status: active|suspended|expired|revoked }`
- `UsageCounter { holder, quota, period: TimeRange, used: Quantity, version }` (sharded counters for hot quotas)
- `Seat` (P2) `{ entitlement, assignee: PartyRef, assignedAt: TimePoint }`; `Licence` (P4) `{ key (hashed), entitlement, activations }`

## 3. Commands, Queries, Events, APIs
Commands: `DefinePlan`/`DefineFeature`/`DefineQuota` (governed), `Grant(holder, plan|feature|quota, source, validity)`, `Revoke`, `ChangePlan(holder, plan)` (proration via U27 P2), `Consume(holder, quota, amount, idempotencyKey)`, `ResetCounters` (Temporal recurrence), `AssignSeat` (P2).
Queries: `Check(holder, feature) → {allowed, value, reason}`, `Remaining(holder, quota)`, `EffectiveEntitlements(holder)` (merged from all sources; used by Context/Policy as attributes), `Usage(holder, range)`.
Events: `entitlement.granted|revoked|expired`, `entitlement.quota.threshold` (80%/100%), `entitlement.quota.exceeded`.
```text
GET  /v1/entitlement/check?holder=&feature=        POST /v1/entitlement/consume
GET  /v1/entitlement/holders/{id}/effective        GET  /v1/entitlement/holders/{id}/usage?quota=&from=&to=
POST /v1/entitlement/plans   POST /v1/entitlement/grants   POST /v1/entitlement/grants/{id}:revoke
```
Errors: `ENT_NOT_ENTITLED` (403 with upgrade hint key), `ENT_QUOTA_EXCEEDED` (429/402 per overage policy), `ENT_UNKNOWN_FEATURE`.

## 4. Rules & Performance
Effective value merge: highest tier wins for tiered features; quotas sum across additive sources (plan + add-on) unless `exclusive`; validity per source. SDK caches `EffectiveEntitlements` per holder (TTL 60 s, invalidated by events); `Consume` on hot quotas uses sharded counters with periodic reconciliation (pattern of U13/U34). Check p99 < 1 ms (cached), Consume p99 < 10 ms.

## 5. Security, Gaps, AI, Ops, UI
Grants above plan (manual) require approval (U01 level 2–3) and are audited. Gaps:
```prolog
gap(feature_check_missing, C, F) :- capability(C), gated_feature(C, F), not feature_defined(F).
gap(tenant_without_plan, T)      :- tenant(T), active(T), not entitlement(T, plan, _).
gap(quota_without_reset, Q)      :- quota(Q), resettable(Q), not reset_policy(Q, _).
```
Signals: `entitlement_checks_total{result}`, `quota_utilisation_ratio{quota}`, `quota_exceeded_total`. Views: Platform Console `plans.manager`, Tenant Admin `billing.plan-and-usage` (usage meters vs limits, upgrade prompts), Developer portal API plans. T0 for Check/Consume (cached).

## Appendix
- **C.** 0.1.0.

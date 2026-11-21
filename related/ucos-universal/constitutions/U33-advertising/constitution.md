# U33 — Advertising Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U33-advertising` |
| Layer | L5 Business Capability |
| Domain | 06 Engagement |
| Steward | `ucos:org:engagement-ads` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P4 |
| Depends on | U44 Search (sponsored slots), U52 Recommendation (sponsored recs), U25 Marketplace (advertisers = sellers/brands), U30 Ledger (ad spend billing, prepaid wallets via U84), U13 Temporal (flight dates, dayparting, budget pacing), U66 Privacy (consent, no sensitive targeting), U69 Risk (click fraud), U72 Observability, U86 Marketing (external ad platforms are adapters there) |
| Depended on by | Retail-media compositions, publishers/OTT (ad-supported tiers), U93 (clean-room reporting) |
| Master references | §6.2 U33, U44 (ranking transparency) |

> Advertising owns **the platform's own ad business (retail/on-platform media)**: advertisers and accounts, campaigns, ad groups, creatives, targeting (contextual, first-party audiences with consent), auctions and pricing (CPC/CPM/CPA), budget pacing, ad serving decisions in placements, measurement (impressions, clicks, attributed sales), and billing. Buying ads on *external* networks (Google, Meta) is U86 Marketing via adapters.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| ADV-L1 | Ads are always labelled "Sponsored" and separable from organic results. | UI pack contract + U44 slot types. |
| ADV-L2 | No targeting on sensitive categories or minors; personalised ads require consent where law requires (DPDP children, GDPR/ePrivacy, DSA Art. 26/28). | Audience policy checks; Cedar P-ads. |
| ADV-L3 | Auctions follow published rules (second-price/first-price with reserve, quality score); results are reproducible from logs. | Auction log with inputs; advertiser-facing transparency report. |
| ADV-L4 | Spend never exceeds budget beyond declared tolerance; invalid traffic is filtered and credited. | Pacing controller; IVT filters (U69). |

## 2. Objects
`AdvertiserAccount { organization, billing (prepaid wallet U84 / invoice U30), status }` · `Campaign { advertiser, objective, flight: TimeRange, budget {daily/total: Money}, pacing, status }` · `AdGroup { campaign, placements (search-top, PDP, home, recs, display), targeting {keywords, categories, audiences (consented), geo (U12), daypart (Temporal)}, bid {strategy, amount: Money} }` · `Creative { kind: sponsored-product|banner|video, assets (U43), review status }` · `AuctionLog { placement, request ctx (non-PII), candidates, winner, price, at: TimePoint }` · `AttributionResult { campaign, lookback: Duration, impressions, clicks, orders, revenue: Money }`.

## 3. Commands, Events, APIs
Commands: `CreateCampaign`, `CreateAdGroup`, `SubmitCreative`, `ReviewCreative`, `ServeAd(placement, ctx)` (≤ 20 ms), `RecordImpression|Click`, `Attribute`, `PauseCampaign`, `BillSpend`.
Events: `advertising.campaign.started|paused|ended`, `advertising.budget.exhausted`, `advertising.creative.rejected`.
```text
POST /v1/ads/campaigns   POST /v1/ads/ad-groups   POST /v1/ads/creatives   POST /v1/ads/serve   GET /v1/ads/reports
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(ads_without_consent_rules, T, J) :- tenant(T), in_scope(T, J), capability(T, advertising.core), personalised_ads_need_consent(J), not consent_purpose(T, ads-personalisation).
```
AI: bid optimisation, creative generation (labelled, U49 guardrails), relevance/quality scoring. Signals: `fill_rate`, `ctr`, `roas`, `ivt_rate`, `serve_latency_ms`. Views: advertiser console (campaigns, budgets, reports), creative review queue, placement manager. T1 for serving (fallback: organic only).

## Appendix
- **C.** 0.1.0.

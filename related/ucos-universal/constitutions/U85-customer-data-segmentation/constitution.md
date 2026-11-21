# U85 — Customer Data & Segmentation (CDP) Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U85-cdp` |
| Layer | L6 Intelligence |
| Domain | 03 Business |
| Steward | `ucos:org:growth-data` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 (profiles, traits, rule segments), P4 (predictive segments, real-time audiences, activation to ad platforms) |
| Depends on | U11 Party (identity of persons — CDP never duplicates PII), U61 Event (behaviour), U72 Analytics (lakehouse), U66 Privacy (consent, purposes), U53 Decision, U49/U94 (predictive traits), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U22 Offer (segment eligibility), U86 Marketing Automation, U40 Communication (audiences), U52 Recommendation, U23 Pricing (segment price lists), U33 Advertising, U44 Search (personalisation) |
| Master references | Master §6.2 references `SegmentRef` in Offer/Pricing without an owner — resolved by A-30 |

> CDP owns **unified customer understanding for activation**: behavioural event collection standards (web/app tracking plan), identity stitching of anonymous → known (device/cookie ids → Party), computed **traits** (RFM, lifetime value, preferences, propensities), **segments/audiences** (rule-based, predictive, real-time), and audience activation to internal consumers and external destinations — strictly consent-aware.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| CDP-L1 | CDP profiles reference Party (U11); they never store a second copy of names/contacts. | Schema: profile = party ref + traits. |
| CDP-L2 | Tracking collects only events in the registered tracking plan, after consent where required (analytics/marketing purposes). | SDK gate on consent; collector rejects unregistered events. |
| CDP-L3 | Traits and segments declare purpose; activation only to consumers with that purpose; external destinations require marketing consent and data-sharing basis. | Purpose check at activation. |
| CDP-L4 | No segments on sensitive attributes (health, religion, caste, sexual orientation, minors for ads) unless a lawful, declared purpose exists (generally forbidden for marketing). | Segment validator. |

## 2. Objects
`TrackingPlan { events: [{name, properties schema, purpose}] }` · `IdentityGraph { anonymousIds ↔ party links with confidence/source }` · `Trait { id, definition (SQL/metric-layer or stream expression or model), type, refresh: Recurrence | "real-time", purpose }` · `Segment { id, kind: rule|predictive|lookalike|static-list, definition (CEL over traits/events with time windows), refresh: Recurrence, size (computed), purpose, owner }` · `Audience { segment, destination: internal (offer/comm/search) | external (ads platforms via U62 connectors), syncPolicy, consentFilter }`.

## 3. Commands, Queries, Events, APIs
Commands: `PublishTrackingPlan`, `DefineTrait`, `DefineSegment`, `ActivateAudience`, `DeactivateAudience`, `MergeIdentities` (from U11 merges).
Queries: `ProfileTraits(party, purpose)`, `IsInSegment(party, segment)` (real-time, < 10 ms), `SegmentSize(def)` (preview), `Explain(party, segment)`.
Events: `cdp.segment.entered|exited` (Temporal triggers / journeys), `cdp.trait.changed`.
```text
POST /v1/cdp/events (collector)   POST /v1/cdp/segments   GET /v1/cdp/segments/{id}/size
GET /v1/cdp/profiles/{party}/traits?purpose=   POST /v1/cdp/audiences/{id}:activate
```

## 4. Gaps
```prolog
gap(segment_without_owner_universe, S) :- segment_ref_used(S), not segment(S).
gap(tracking_without_consent_gate, T) :- tenant(T), tracking_enabled(T), consent_required(T), not consent_gated_sdk(T).
gap(sensitive_segment, S) :- segment(S), uses_trait_class(S, spi), purpose(S, marketing).
```

## 5. AI, Ops, UI, Scale
AI: propensity models (U94), lookalikes, natural-language segment builder ("customers who bought electronics twice in 90 days but not in the last 30"). Signals: `events_ingested`, `identity_match_rate`, `segment_eval_latency_ms`, `audience_sync_failures`. Views: `cdp.tracking-plan`, `cdp.segment.builder` (rule UI + size preview + overlap), `cdp.profile.view` (traits with provenance, consent state), `cdp.audience.destinations`. Scale: 10⁹ events/day; profiles in ClickHouse/feature store + real-time segment membership in Redis/stream state. T1.

## Appendix
- **C.** 0.1.0.

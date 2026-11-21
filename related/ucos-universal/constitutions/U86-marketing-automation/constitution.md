# U86 — Marketing Automation Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U86-marketing` |
| Layer | L5 Business Capability |
| Domain | 03 Business |
| Steward | `ucos:org:growth-marketing` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P4 |
| Depends on | U85 CDP (segments, triggers), U40 Communication (delivery), U22 Offer (incentives), U13 Temporal (schedules, quiet hours), U60 Workflow (journeys), U72 Analytics (attribution, experiments), U66 Privacy, U33 Advertising (paid media), U87 SEO/Web Presence (landing pages) |
| Depended on by | Growth teams; U32 Loyalty; U72 dashboards |
| Master references | Master Commerce IA "Campaigns, Merchandising"; U40 "campaigns (P4)" moved here by A-31 |

> Marketing Automation owns **orchestrating marketing across channels**: campaigns (one-off and recurring), customer **journeys** (event/segment-triggered multi-step flows with waits, branches, A/B splits), content variants, frequency governance across all marketing, UTM/attribution models, landing-page linkage, budget and performance tracking. Delivery is always through Communication (U40); incentives via Offer (U22); audiences via CDP (U85).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| MKT-L1 | Marketing messages require valid marketing consent per channel and jurisdiction and honour global frequency caps. | Communication send pipeline + MKT frequency governor. |
| MKT-L2 | Journeys are workflow definitions (U60) with bounded loops, exit criteria, and goal metrics. | Journey validator. |
| MKT-L3 | Every campaign has a pre-declared goal metric (certified KPI) and holdout/control where measuring incrementality. | Schema + experiments (U72). |

## 2. Objects
`Campaign { id, goal metric, audience (segment), channels, content variants, schedule (TemporalPolicy), budget, offers, utm, status }` · `Journey { id, entry: segment-entered|event|schedule, steps: [send(template)|wait(Duration|until event)|branch(CEL)|split(A/B)|update-trait|create-offer|webhook], exit criteria, goal, holdout% }` · `AttributionModel { kind: last-touch|first-touch|linear|time-decay|data-driven, lookback Duration }` · `MarketingCalendar` (view over U13).

## 3. Commands, Queries, Events, APIs
Commands: `CreateCampaign`, `LaunchCampaign`, `PauseCampaign`, `DefineJourney`/`PublishJourney`, `EnrollParty` (system), `ExitParty`.
Queries: `CampaignPerformance`, `JourneyFunnel`, `Attribution(order|conversion)`.
Events: `marketing.campaign.launched|completed`, `marketing.journey.entered|step|converted|exited`.
```text
POST /v1/marketing/campaigns   POST /v1/marketing/campaigns/{id}:launch|:pause
POST /v1/marketing/journeys    GET /v1/marketing/journeys/{id}/funnel
```

## 4. Gaps
```prolog
gap(campaign_without_goal, C) :- campaign(C), not goal_metric(C, _).
gap(journey_unbounded, J)     :- journey(J), has_loop(J), not loop_bound(J).
```

## 5. AI, Ops, UI, Scale
AI: content generation (brand voice; human approval), send-time optimisation, next-best-action, budget pacing. Signals: `conversion_rate{campaign}`, `unsubscribe_rate`, `incremental_lift`, `frequency_cap_suppressions`. Views: `journey.canvas` (drag-and-drop on U60 designer), `campaign.builder`, `marketing.calendar`, `attribution.report`. Scale: millions of journey enrolments/day (workflow engine). T2.

## Appendix
- **C.** 0.1.0.

# U76 — Evolution Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U76-evolution` |
| Layer | L12 Evolution |
| Domain | 09 Platform |
| Steward | `ucos:org:platform-evolution` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 (insight mining, improvement proposals, deprecation lifecycle), P5 (simulation-backed proposals with U54) |
| Depends on | U72 Observability (signals), U58 Composition (gap discovery, INSIGHT gaps), U02 Governance (proposals, change process), U74 Certification, U57 Capability (versions, deprecation), U49/U51 (AI analysis agents), U54 Simulation (impact), U75 Knowledge Graph |
| Depended on by | Architecture Board (U01), pack authors, tenants (upgrade advisories), the platform's continuous-improvement loop (master §28) |
| Master references | §28 (self-evolution loop), Law L19 (no silent evolution) |

> Evolution owns **governed change to the platform itself**: insights mined from signals and gap history, improvement proposals (new capability, rule change, default change, deprecation), impact analysis, rollout plans with canaries, deprecation and sunset schedules, migration guides, and tenant upgrade advisories. Nothing evolves silently: every change is a Governance proposal with evidence.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| EVO-L1 | Every platform change originates as a proposal with evidence, impact analysis and rollback plan. | U02 proposal schema requires these fields. |
| EVO-L2 | Deprecations have a published timeline (announce → deprecated → sunset) of at least 12 months for public contracts, with migration guides. | Temporal schedule; API/event version policy. |
| EVO-L3 | AI-generated proposals are labelled and need human approval at the authority level of the change. | GEN-L2, AG-laws. |
| EVO-L4 | Rollouts use cohorts and canaries with automatic halt on SLO or certification regression. | Rollout controller + U72 SLO gates. |

## 2. Objects
`Insight { source signals/gaps, pattern, affected tenants/capabilities, confidence, at: TimePoint }` · `ImprovementProposal` (U02 Proposal kind `evolution`) `{ insight refs, change (manifest/rule/default/schema diff), impact (blast radius, tenants, simulation result), rollout plan, rollback }` · `Deprecation { subject (API/event/capability/version), announcedAt: TimePoint, deprecatedAt: TimePoint, sunsetAt: TimePoint, replacement, guide }` · `Rollout { change, cohorts [{tenants, startAt: TimePoint}], gates, status }` · `UpgradeAdvisory { tenant, blueprint, available changes, required actions, deadline: TimePoint }`.

## 3. Commands, Events, APIs
Commands: `MineInsights` (scheduled), `ProposeImprovement`, `AnalyseImpact`, `PlanRollout`, `AdvanceRollout`, `HaltRollout`, `AnnounceDeprecation`, `IssueAdvisory`.
Events: `evolution.insight.found`, `evolution.rollout.advanced|halted|completed`, `evolution.deprecation.announced|sunset`.
```text
GET /v1/evolution/insights   POST /v1/evolution/proposals   POST /v1/evolution/rollouts/{id}:advance|:halt
GET /v1/evolution/deprecations   GET /v1/evolution/advisories?tenant=
```

## 4. Gaps, UI
```prolog
gap(sunset_without_guide, D) :- deprecation(D), not migration_guide(D).
gap(tenant_on_sunset_version, T, V) :- tenant(T), uses_version(T, V), sunset_within_days(V, 90).
```
Views: insight feed, proposal impact view (diff + blast radius + simulation), rollout cockpit, deprecation calendar, tenant upgrade centre. T2.

## Appendix
- **C.** 0.1.0.

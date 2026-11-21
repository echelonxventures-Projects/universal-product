# U102 — Strategy & Performance Management Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U102-strategy` |
| Layer | L6 Intelligence / L5 |
| Domain | 03 Business |
| Steward | `ucos:org:strategy-office` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 |
| Depends on | U72 Observability & Analytics (certified metrics), U10 Org (org units), U11 Party, U13 Temporal (planning periods, cadences), U30 Ledger (budgets/actuals), U96 Collaboration (initiatives as projects), U54 Simulation (scenarios), U60 Workflow (planning cycles) |
| Depended on by | U46 Workforce (performance reviews alignment), U30 FP&A, leadership portals, U86 (campaign goals), U72 dashboards |
| Master references | APQC 1.0 "Develop Vision and Strategy" (A-49) |

> Strategy owns **direction-setting and performance management**: vision/mission statements, strategic themes, objectives & key results (OKRs), KPI scorecards (balanced scorecard), targets & thresholds, strategic initiatives/portfolios, planning cycles (annual/quarterly), scenario plans, and performance reviews of the organisation (not individual HR appraisals, which are U46).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| STR-L1 | Every KPI on a scorecard references a certified metric definition (U72); no hand-typed numbers except declared manual measures with evidence. | Schema + gap. |
| STR-L2 | Objectives, key results and initiatives are time-bound (planning period TimeRange) and owned. | Required fields. |
| STR-L3 | Cascading/alignment links are explicit (child objective → parent) to make contribution traceable. | Graph edges. |

## 2. Objects
`StrategyStatement { vision, mission, values, period: TimeRange }` · `StrategicTheme` · `Objective { title, owner (party/org unit), period: TimeRange, parent?, theme }` · `KeyResult { objective, metric (U72 MetricDefinition) | manual measure, baseline, target, direction, confidence, checkIns [{at: TimePoint, value, note}] }` · `Scorecard { org unit, perspectives (financial/customer/process/learning or custom), KPIs [{metric, target, thresholds}], period: TimeRange }` · `Initiative { objectives, project (U96), budget (U30), status, benefits }` · `PlanningCycle { cadence: Recurrence, steps (workflow), period: TimeRange }` · `Scenario { assumptions, simulation (U54), outcomes }`.

## 3. Commands, Events, APIs
Commands: `PublishStrategy`, `CreateObjective`, `AddKeyResult`, `CheckIn`, `DefineScorecard`, `LinkInitiative`, `StartPlanningCycle`, `CloseCycle`.
Events: `strategy.kr.at-risk`, `strategy.cycle.started|closed`.
```text
POST /v1/strategy/objectives   POST /v1/strategy/key-results/{id}/check-ins   GET /v1/strategy/scorecards/{orgUnit}
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(kpi_uncertified, K) :- scorecard_kpi(K), not certified_metric(K).
gap(objective_without_kr, O) :- objective(O), active(O), not key_result(O, _).
```
AI: OKR drafting quality checks (measurable, outcome-based), progress forecasting, narrative performance summaries citing metrics. Views: strategy map, OKR tree (alignment), scorecards with trend sparklines, check-in reminders (U13 REM), planning-cycle workspace. T3.

## Appendix
- **C.** 0.1.0.

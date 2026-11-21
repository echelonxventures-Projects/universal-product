# U72 — Observability & Analytics Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U72-observability` |
| Layer | L11 Operations |
| Domain | 10 Observability |
| Steward | `ucos:org:platform-sre` (observability) / `ucos:org:data-analytics` (analytics) |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (OTel pipeline, SLOs, dashboards, business signals, lakehouse CDC, basic reports, feature flags), P4 (experiments at scale, self-serve BI), P5 (AIOps) |
| Depends on | U61 Event, U57 Capability (signals in manifests), U73 Infra, U65 Security (classification/redaction), U66 Privacy (analytics consent), U13 Temporal (windows, calendars) |
| Depended on by | U02 Governance (release guards), U75 Gap (runtime facts), U74 Certification (OBS/PERF evidence), U55 Twin (P5), tenants (reports/dashboards), Console W1/W14 |
| Master references | §26 (signals, SLOs), §14.1 (ClickHouse, Iceberg), §28.2 OBS gates |

> This universe owns **seeing what happens and measuring outcomes**: signal definitions (metrics, logs, traces, business signals), SLOs and error budgets, alert rules and routing, dashboards, the analytics lakehouse (CDC + event ingestion), semantic metrics layer (governed KPI definitions), reports, feature flags and experiments. Audit records are U68 (not logs).

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| OBS-L1 | Every capability ships signal definitions, SLOs and default alerts in its manifest; missing ones block certification. | `OBS-*` gates. |
| OBS-L2 | Telemetry never contains restricted data; logs are structured and redacted at source (SDK) and at collector. | SDK log API takes typed fields with classification; collector redaction processors; DLP sampling. |
| OBS-L3 | KPIs are defined once in the semantic layer (metric definitions as code) and reused by dashboards, reports, experiments and guards. | Metric registry; dashboards reference metric ids. |
| OBS-L4 | Tenant analytics are tenant-isolated; cross-tenant aggregates follow master §20.5 (opt-in, k-anonymity, DP). | Row-level security in lakehouse views; aggregation service. |
| OBS-L5 | Experiments have pre-registered hypotheses, primary metric and stopping rules; feature flags have owners and expiry. | Experiment/flag schema + gap rules. |

## 2. Objects
- **`SignalDefinition`** `{ id (e.g. cart_conversion_ratio), kind: metric|log-event|trace-attr|business-signal, type: counter|gauge|histogram|ratio, unit, labels (bounded cardinality list), classification, source capability, description }`
- **`SLO`** `{ id, sli (good/total query), objective (e.g. 99.5%), rollingWindow: Duration (e.g. P28D), tier, burnAlerts: [{lookback: Duration (e.g. PT1H, PT6H), factor, severity}], owner, errorBudgetPolicy }`
- **`AlertRule`** `{ id, expr, for, severity, routing: on-call schedule (Temporal) | tenant contacts, runbook ref, suppression (maintenance windows via Temporal) }`
- **`Dashboard`** `{ id, audience (platform/tenant/role), panels referencing metric ids, filters (tenant-scoped automatically) }`
- **`MetricDefinition`** (semantic layer) `{ id (gmv, aov, take_rate, checkout_success), expression over lakehouse models, dimensions, grain, owner, certified: bool }`
- **`Report`** `{ id, query (metric-layer), schedule (Temporal), delivery (Communication/Document), audience, format }`
- **`FeatureFlag`** `{ key, owner, type: release|ops|permission|experiment, targeting rules (ctx CEL), default, expiresAt: TimePoint, status }`
- **`Experiment`** `{ id, hypothesis, variants (flag-based), allocation, primary metric, guardrail metrics, MDE, sample size, start/stop (Temporal), analysis method (sequential/CUPED), decision }`

## 3. Architecture
- **Telemetry:** OTel SDK in kernel & packs → OTel collectors (cell) → Mimir (metrics), Loki (logs), Tempo (traces); exemplars link metrics↔traces; tail sampling (errors & slow traces kept).
- **Business signals:** derived from domain events by stream processors (Flink) into ClickHouse (real-time) — e.g. orders/min, GMV.
- **Lakehouse:** Debezium CDC + event topics → Iceberg tables (bronze/silver/gold) on object storage per cell/residency → Trino/Spark; dbt-style models; semantic layer (metric definitions) → BI (embedded dashboards in portals) and tenant data export.
- **Flags/experiments:** OpenFeature-compatible evaluation SDK (local evaluation with streamed rules), assignment logged as events; analysis jobs produce results with confidence intervals.

## 4. Commands, Queries, Events, APIs
Commands: `DefineSLO`, `DefineAlertRule`, `PublishDashboard`, `DefineMetric` (governed for certified metrics), `ScheduleReport`, `CreateFlag`/`UpdateFlag`/`ArchiveFlag`, `StartExperiment`/`StopExperiment`/`DecideExperiment`.
Queries: `SLOStatus(scope)`, `ErrorBudget(slo)`, `QueryMetric(metricId, dims, range, filters)`, `EvaluateFlag(key, ctx)` (SDK local), `ExperimentResults(id)`.
Events: `observability.slo.burning|breached|recovered`, `observability.alert.fired|resolved`, `analytics.report.delivered`, `experiment.started|concluded`, `flag.changed`.
```text
GET /v1/obs/slos?scope=          GET /v1/obs/slos/{id}/budget
POST /v1/analytics/metrics:query  POST /v1/analytics/reports
POST /v1/flags                    POST /v1/experiments   GET /v1/experiments/{id}/results
```

## 5. Gaps
```prolog
gap(capability_without_slo, C)   :- in_blueprint(C), tier_at_least(C, t1), not slo_for(C).
gap(alert_without_runbook, A)    :- alert_rule(A), severity(A, page), not runbook(A, _).
gap(alert_without_route, A)      :- alert_rule(A), not routing(A, _).
gap(flag_expired, F)             :- feature_flag(F), past_expiry(F), not archived(F).
gap(uncertified_kpi_in_guard, G) :- release_guard(G), uses_metric(G, M), not certified_metric(M).
gap(high_cardinality_label, S)   :- signal(S), label_cardinality(S, N), N > 10000.
```

## 6. Security & Compliance
Telemetry retention: metrics 13 months (downsampled), logs 30 days hot / 1 year archive (security logs per policy), traces 7 days; analytics data follows U66 retention and consent (analytics purpose); tenant data exports watermarked; access to raw lakehouse restricted (data stewards), BI via semantic layer with RLS.

## 7. AI
AIOps (P5): anomaly detection, alert correlation, probable cause via dependency graph, remediation suggestions (W14); natural-language analytics ("GMV by seller tier last week") → metric-layer query (only certified metrics, results cite metric definitions); experiment analysis summaries.

## 8. Operations, UI, Scale
Signals about itself: `telemetry_ingest_rate`, `collector_drop_ratio` (alert > 0.1%), `lakehouse_freshness_minutes`. Views: W14 (platform twin/observability), `obs.slo.board`, `obs.alert.console`, `analytics.dashboard` (tenant), `analytics.metric.catalog`, `flags.console`, `experiments.console` (design wizard with sample-size calc, results with guardrails). Scale: billions of spans/day; per-cell stacks with global federation for platform views; lakehouse per residency region. T1 (guards T0-critical data paths cached).

## Appendix
- **B. Amendments:** master §6.2 U72 owns `MetricDefinition`, `AlertRule`, `Experiment`, `FeatureFlag` explicitly.
- **C.** 0.1.0.

# U69 — Risk Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U69-risk` |
| Layer | Trust Plane |
| Domain | 08 Governance |
| Steward | `ucos:org:risk-fraud` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 (real-time fraud/abuse scoring for login, checkout, payment, returns, promotions; rules + ML; case management for reviews), P4 (AML transaction monitoring, credit risk for U100, enterprise risk register) |
| Depends on | U94 ML Platform (models, features), U53 Decision (rules, thresholds), U16 Context (risk dimension), U61 Event (signals), U09 Identity (device/identity signals), U13 Temporal (velocity windows), U60 Workflow (review cases), U72 Observability, U67 Compliance (AML) |
| Depended on by | U16 Context (risk band), U24 Checkout (COD, step-up), U29 Payment (SCA, routing), U22 Offer (abuse), U26 Order (return abuse), U09 Identity (login risk), U25 Marketplace (seller risk), U100 Financial (credit/AML), U88 Social (spam), U84 Stored Value (gift-card abuse) |
| Master references | §7.6 (risk in context), U16 Appendix P1 (unknown band until P2) |

> Risk owns **scoring and managing risk**: risk models (rules, ML, graph-based), real-time scoring APIs, risk signals and feature definitions (with U94), velocity and link analysis, review queues and decisions, block/allow lists, chargeback/fraud feedback loops, AML transaction monitoring (P4), and the enterprise risk register (risk appetite, KRIs).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| RSK-L1 | Every automated risk decision affecting a person is explainable (top reasons), logged and contestable; adverse actions follow legal notice rules. | Decision logs + reason codes; U71 appeals. |
| RSK-L2 | Protected attributes and proxies are excluded from risk features; fairness is monitored per slice. | Feature registry classification + bias monitoring (U94). |
| RSK-L3 | Scores are inputs to decisions, never hard blocks without a decision table (thresholds governed, versioned). | U53 decisions consume scores. |
| RSK-L4 | Scoring is fail-safe: if risk is unavailable, context band = `unknown` (treated as medium) — never silently `low`. | Context resolver default (U16). |
| RSK-L5 | Fraud labels (chargebacks, confirmed abuse) feed back to models with lineage; labels are reviewed for quality. | Label pipeline (U93/U94). |

## 2. Objects
`RiskModel { id, scope: login|checkout|payment|promotion|return|account|seller|listing|transaction-aml|credit, kind: rules|ml|graph|hybrid, version, features, thresholds (DecisionRef), owner, evaluation }` · `RiskAssessment { subject (party/order/payment/session/listing), scope, score 0–100, band, reasons [{code, weight}], modelVersions, at: TimePoint, decisionRef }` · `VelocityCounter { key (card fingerprint, device, IP /24, address, phone), rollingWindow: Duration, count }` · `ReviewCase { assessment, queue, assignee, decision: approve|decline|escalate, notes, sla: SLAClockRef }` · `ListEntry { kind: block|allow|watch, key, reason, expiresAt: TimePoint }` · `AMLAlert { rule/scenario, subject, transactions, status, SAR/STR filing ref }` · `RiskRegisterItem { risk, owner, likelihood, impact, controls (U67), KRIs (U72 metrics), appetite }`.

## 3. Commands, Queries, Events, APIs
Commands: `Score(scope, subject, ctx)` (sync, p99 < 50 ms), `RecordOutcome` (labels), `OpenReview`, `DecideReview`, `AddListEntry`, `PublishRiskModel` (governed + eval), `RaiseAMLAlert`, `FileReport` (STR/SAR via authority connectors).
Events: `risk.assessment.high`, `risk.review.decided`, `risk.label.recorded`, `risk.aml.alert-raised`.
```text
POST /v1/risk/score   POST /v1/risk/outcomes   POST /v1/risk/reviews/{id}:decide   POST /v1/risk/lists
```

## 4. Gaps, Ops, UI
```prolog
gap(checkout_without_risk, T) :- tenant(T), phase_at_least(T, 2), capability(T, commerce.checkout), not capability(T, risk.core).
gap(model_without_fairness_monitor, M) :- risk_model(M), kind(M, ml), not fairness_monitor(M).
gap(aml_required, T, J) :- tenant(T), in_scope(T, J), regulated_payments_or_wallets(T), aml_applies(J), not capability(T, risk.aml).
```
Signals: `fraud_rate_bps`, `chargeback_rate`, `false_positive_rate`, `review_sla_breach`, `score_latency_ms`. Views: risk cockpit (rates, rules hit), review queue with evidence graph, rule/threshold editor (decision tables with backtesting on past events), list manager, AML case management. T0 for scoring (with `unknown` fallback).

## Appendix
- **C.** 0.1.0.

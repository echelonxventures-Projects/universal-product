# U94 — ML Platform Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U94-ml` |
| Layer | L6 Intelligence |
| Domain | 07 Intelligence |
| Steward | `ucos:org:intelligence-ml` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 (feature store, training pipelines, model registry integration, batch & online inference for fraud/risk), P4 (forecasting, recommendation models, AutoML for tenants), P5 (federated/cross-tenant learning with privacy) |
| Depends on | U93 Data (datasets, lineage), U72 Analytics (lakehouse), U49 AI/Model (unified model registry & governance — LLMs and classical ML share it), U66 Privacy (training purpose), U65 Security, U74 Certification (AI gates), U73 Infra (GPU/CPU pools), U53 Decision (model nodes), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U69 Risk/Fraud, U52 Recommendation, U44 Search ranking, U34 forecasting/replenishment, U23 dynamic pricing, U35 promise prediction, U85 predictive traits, U82 duration prediction, U98 estimates |
| Master references | §21 (AI fabric), user requirement "ML" distinct from LLM/agents (A-42) |

> ML Platform owns **predictive and statistical machine learning lifecycle** (as distinct from LLM/agent usage owned by U49–U51): feature definitions and feature store (offline/online), training datasets and labeling, training pipelines and experiments, evaluation and bias testing, model packaging, deployment for batch/online/streaming inference, monitoring (drift, performance, fairness), retraining triggers, and privacy-preserving learning (federated, differential privacy). Model *registration, governance and certification* are shared with U49's registry (one registry for all models).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| ML-L1 | Features are defined once (feature registry) with point-in-time-correct computation for training and identical logic online (no training/serving skew). | Feature store contract; skew monitors. |
| ML-L2 | Training data use requires a training purpose with lawful basis; tenant data never trains cross-tenant models without opt-in (master §20.5). | Dataset purpose check at job submission. |
| ML-L3 | Every model version has lineage (data, features, code commit, hyperparameters), evaluation report (incl. fairness slices where applicable), model card, and certification before serving. | U74 AI gates; registry requirements. |
| ML-L4 | Production models are monitored for drift and performance; breaches trigger rollback or retraining per policy, never silent degradation. | Monitoring + automated runbooks. |
| ML-L5 | Decisions using models have deterministic fallbacks (DEC-L5). | Decision model schema. |

## 2. Objects
`FeatureDefinition { id, entity (party, listing, order, device…), expression (SQL/stream), freshness: Duration, owner, classification, purpose }` · `FeatureView/Set` · `TrainingDataset { features, labels, time range, sampling, lineage }` · `LabelTask { data, guideline, annotators (human/AI), quality }` · `TrainingPipeline { steps, compute, schedule (Temporal) }` · `Experiment/Run { params, metrics, artifacts, commit (U95) }` · `ModelVersion` (registered in U49 registry: `kind: classical-ml|deep-learning|llm-finetune`, framework, signature, card, eval report, fairness report) · `Deployment { model, mode: online|batch|stream|edge, endpoint, traffic split (shadow/canary), SLO }` · `MonitorPolicy { metrics (PSI/KL drift, accuracy via delayed labels, latency), thresholds, actions }`.

## 3. Commands, Queries, Events, APIs
Commands: `DefineFeature`, `MaterializeFeatures`, `CreateTrainingDataset`, `RunTraining`, `EvaluateModel`, `RegisterModelVersion`, `RequestCertification`, `Deploy(mode, traffic)`, `Rollback`, `ScheduleRetraining`.
Queries: `OnlineFeatures(entity ids, features)` (p99 < 10 ms), `Predict(model, inputs)` (online), `ModelLineage`, `DriftStatus`.
Events: `ml.training.completed`, `ml.model.deployed|rolled-back`, `ml.drift.detected`.
```text
POST /v1/ml/features   GET /v1/ml/online-features?entity=&ids=   POST /v1/ml/trainings
POST /v1/ml/models/{id}/versions/{v}:deploy|:rollback   POST /v1/ml/predict/{deployment}
```

## 4. Gaps, AI, Ops, UI, Scale
```prolog
gap(model_without_monitoring, D) :- deployment(D), production(D), not monitor_policy(D).
gap(feature_without_owner, F)    :- feature(F), not owner(F, _).
gap(training_purpose_missing, J) :- training_job(J), uses_personal_data(J), not training_purpose(J).
```
Signals: `prediction_latency_ms`, `drift_score{model}`, `model_performance{metric}`, `training_cost`. Views: feature catalog, experiment tracker (MLflow-compatible), model registry & cards (shared with U49), deployment console (canary/shadow), monitoring dashboards. Tech defaults: Feast-compatible feature store (Redis/online + Iceberg/offline), Kubeflow/Ray for training, KServe/Ray Serve for serving, MLflow tracking. T1 (online inference T0 for fraud).

## Appendix
- **C.** 0.1.0.

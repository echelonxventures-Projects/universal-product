# U108 — Product Development, R&D & Innovation Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U108-plm` |
| Layer | L5 Business Capability |
| Domain | 03 Business |
| Steward | `ucos:org:product-engineering` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 |
| Depends on | U18 Product Intelligence (published products), U47 Manufacturing (BOM release), U42 Document (specifications, drawings), U43 Asset (CAD/3D files), U96 Collaboration (projects), U60 Workflow (stage-gates, engineering change), U101 QHSE (design controls, validation), U104 Legal & IP (patents), U93 Data (lab/test data), U13 Temporal (milestones), U54 Simulation |
| Depended on by | U47 (engineering BOM → manufacturing BOM), U18 (launch), U80 (field-failure feedback), research-lab and pharma/med-device packs |
| Master references | APQC 2.0 "Develop and manage products and services" (A-57) |

> Product Development owns **creating and changing products and services before and during their life**: idea and innovation pipeline (idea capture, scoring, portfolio), R&D projects and stage-gate processes, requirements and specifications, design items and versions (parts, assemblies, CAD/document links), engineering BOMs, prototypes, tests and validation (incl. design controls for regulated products), engineering change requests/orders (ECR/ECO), product launch readiness, and lab/experiment records (lightweight LIMS/ELN for research packs).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| PLM-L1 | Released designs are immutable revisions; changes go through ECR → ECO with impact analysis (BOMs, inventory, installed base, documents, compliance). | Workflow + graph impact (U07). |
| PLM-L2 | Regulated products (medical devices, pharma, automotive, aerospace) follow design-control processes with traceable requirements → verification → validation. | Traceability matrix; U101 + U67 (ISO 13485, 21 CFR 820, IATF 16949, AS9100). |
| PLM-L3 | Launch requires product master publication in U18 (GPID), compliance documents and service/warranty definitions. | Launch checklist gate. |

## 2. Objects
`Idea { submitter, problem, value score, status }` · `InnovationPortfolio` · `DevelopmentProject { stage-gate model, current gate, deliverables, team (U96), budget }` · `Requirement { id, text, source, verification method, links }` · `DesignItem { number, revision, kind: part|assembly|software|formula|recipe|service-blueprint, attributes, files (U43 CAD), status: in-work|released|obsolete }` · `EngineeringBOM { parent revision, components [{item rev, qty: Quantity, refDes}] }` · `Prototype`, `TestPlan`, `TestResult { requirement, result, evidence (U68) }` · `ChangeRequest (ECR)`, `ChangeOrder (ECO) { affected items, impact, effectivity: TemporalRef | serial range, approvals }` · `Experiment` / `LabRecord { protocol, samples, measurements (U14 quantities), instruments (U79/U92), results }` · `LaunchPlan { readiness checklist, market/jurisdictions, launchAt: TimePoint }`.

## 3. Commands, Events, APIs
Commands: `SubmitIdea`, `AdvanceGate`, `CreateDesignItem`, `ReleaseRevision`, `RaiseECR`, `ApproveECO`, `ReleaseToManufacturing` (EBOM → U47 MBOM), `RecordTestResult`, `RecordExperiment`, `Launch` (publish to U18).
Events: `plm.revision.released`, `plm.eco.approved`, `plm.product.launched`.
```text
POST /v1/plm/projects   POST /v1/plm/items   POST /v1/plm/items/{id}/revisions:release   POST /v1/plm/ecr   POST /v1/plm/launches
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(launch_without_master, P) :- launch_plan(P), launched(P), not gproduct_published(P).
gap(requirement_unverified, R) :- regulated_project(_, R), requirement(R), not verified(R).
```
AI: idea clustering, requirement quality checks, prior-art search assistance (U104), test-failure analysis, experiment design suggestions. Views: innovation funnel, stage-gate board, item/BOM explorer with where-used, ECO impact view, traceability matrix, ELN/lab notebook. T3.

## Appendix
- **C.** 0.1.0.

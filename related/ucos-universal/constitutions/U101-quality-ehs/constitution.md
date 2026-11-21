# U101 — Quality, Health, Safety & Environment (QHSE) Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U101-qhse` |
| Layer | L5 Business Capability |
| Domain | 08 Governance |
| Steward | `ucos:org:qhse` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 (QMS: nonconformance, CAPA, audits, document control; EHS: incidents, inspections, permits-to-work), P6 (industrial process safety, environmental permits & monitoring) |
| Depends on | U42 Document (controlled documents), U60 Workflow, U13 Temporal (inspection schedules, CAPA due dates, permit validity), U79 Installed Base (equipment), U12 Geography (sites), U11 Party, U46 Workforce (training/competence), U67 Compliance (ISO 9001/14001/45001, OSHA, Factories Act), U68 Evidence, U92 IoT (sensors), U98 ESG |
| Depended on by | U47 Manufacturing, U82 Field Service (safety checklists), U45 Procurement (supplier quality), U18 Product (quality holds/recalls), industry packs (construction, mining, pharma, food, aviation, utilities) |
| Master references | Completeness review A-48 (APQC 11.x/13.x gaps) |

> QHSE owns **quality management and occupational health, safety & environment management**: nonconformances, corrective & preventive actions (CAPA), internal/supplier/customer audits, controlled documents & SOP acknowledgement, inspections & checklists, incidents/near-misses/injuries, hazards & risk assessments (JSA/HIRA), permits-to-work, safety observations, environmental aspects/permits/monitoring, and management review — the evidence backbone for ISO 9001, ISO 14001, ISO 45001, GMP/GDP and sector safety regulation.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| QHSE-L1 | Every nonconformance and incident follows a governed lifecycle to closure with root cause and effectiveness check. | Workflow-only transitions; closure guard requires RCA + verification. |
| QHSE-L2 | Controlled documents (SOPs, work instructions) have versions, approvals, effective dates and read-and-acknowledge records; only the effective version is usable. | Document control via U42 + Temporal validity. |
| QHSE-L3 | High-risk work cannot start without a valid permit-to-work and completed isolations/checks. | Field Service/WorkOrder guard (U82) + IoT interlocks (U92). |
| QHSE-L4 | Reportable incidents start regulatory notification clocks per jurisdiction. | SLA clocks from U67 decision `qhse.reportable-incident`. |

## 2. Objects
`Nonconformance { source: inspection|audit|customer-complaint|supplier|process|product, subject (product/lot/unit/process/supplier), severity, containment, disposition (use-as-is/rework/scrap/return), status }` · `CAPA { trigger refs, problem, rootCause (5-why/fishbone/8D), actions [{owner, due: TimePoint}], effectivenessCheck: {due: TimePoint, result}, status }` · `Audit { kind: internal|supplier|customer|certification, standard, scope, schedule: Recurrence, findings [Nonconformance|Observation], report }` · `ControlledDocument { doc (U42), version, effectiveFrom: TimePoint, reviewCycle: Recurrence, acknowledgements [{person, at: TimePoint}] }` · `Inspection { template (checklist), subject, schedule: Recurrence, results, photos, failures → NC }` · `Incident { kind: injury|illness|near-miss|property-damage|environmental-release|security, at: TimePoint, site, people involved (SPI-health), severity, reportable: bool, investigation, CAPA }` · `RiskAssessment { activity/site, hazards [{hazard, likelihood, severity, controls, residual}], reviewedAt: TimePoint }` · `PermitToWork { kind: hot-work|confined-space|work-at-height|electrical|excavation, validity: TimeRange, location, isolations, approvals, status }` · `EnvironmentalAspect`, `EnvironmentalPermit { authority, limits, validity: TimeRange, monitoring schedule: Recurrence }`, `MonitoringReading`.

## 3. Commands, Events, APIs
Commands: `RaiseNonconformance`, `OpenCAPA`, `CompleteAction`, `VerifyEffectiveness`, `ScheduleAudit`, `RecordFinding`, `PublishControlledDocument`, `Acknowledge`, `RunInspection`, `ReportIncident`, `Investigate`, `IssuePermit`, `ClosePermit`, `RecordMonitoring`.
Events: `qhse.nc.raised|closed`, `qhse.capa.overdue`, `qhse.incident.reported|reportable`, `qhse.permit.issued|expired`, `qhse.limit.exceeded`.
```text
POST /v1/qhse/nonconformances  POST /v1/qhse/capas  POST /v1/qhse/audits  POST /v1/qhse/incidents  POST /v1/qhse/permits
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(capa_overdue, C)            :- capa(C), open(C), past_due(C).
gap(sop_unacknowledged, P, D)   :- person(P), role_requires_doc(P, D), effective(D), not acknowledged(P, D).
gap(high_risk_work_without_permit, W) :- work_order(W), high_risk(W), not valid_permit(W).
gap(qms_required, T)            :- tenant(T), industry_requires_qms(T), not capability(T, qhse.qms).
```
AI: root-cause suggestion from similar cases, incident narrative classification, inspection photo hazard detection (proposals). Views: QHSE dashboard (TRIR/LTIFR, NC trends, CAPA ageing), mobile inspection & incident reporting (offline, photo, geo), audit planner calendar, permit board, document control centre. T2 (permit guard path T1).

## Appendix
- **C.** 0.1.0.

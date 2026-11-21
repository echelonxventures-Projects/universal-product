# U82 — Field Service & Work Management Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U82-field-service` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-service-delivery` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 (work orders, dispatch, mobile technician, service requests catalogue), P6 (ITSM-grade request fulfilment) |
| Depends on | U19 Service Intelligence (service definitions, credentials), U17 Resource (technicians, vehicles, skills), U13 Temporal (appointments, windows, SLA clocks), U12 Geography (routing via U36), U79 Installed Base, U80 Warranty, U34 Inventory (van stock, parts), U60 Workflow, U53 Decision, U40 Communication |
| Depended on by | U80 Warranty (on-site repairs), U35 Fulfillment (service-visit fulfilment kind), U39 Support (case → work order), industry packs (home services, utilities, telecom installs, healthcare home visits, ITSM) |
| Master references | Master IA "Field Ops / Work Orders / Maintenance / Service Delivery" (no universe before A-29) |

> Field Service owns **performing services and work**: `ServiceRequest` (catalogue-driven requests from customers or employees — the ITSM "request" concept), `WorkOrder` (planned unit of work with tasks, parts, skills), scheduling & dispatch (assigning resources to time windows and routes), technician mobile execution (checklists, photos, signatures, parts consumption, time tracking), proof of service, and work order closure/billing hand-off.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| FS-L1 | Work orders are assigned only to resources with required skills/credentials valid at the scheduled time. | Dispatch filter using U19 credentials + U09 VerificationRecords. |
| FS-L2 | Appointment windows shown to customers come from Temporal availability of qualified resources; promises are measured. | Same promise discipline as FUL-L1. |
| FS-L3 | Work execution records (time, parts, photos, signature, geo stamp) are immutable once the work order is closed. | Close freezes; amendments via adjustment. |
| FS-L4 | Customer premises data and photos are purpose-limited and retention-bound. | U66 purposes. |

## 2. Objects
`ServiceCatalogItem { id, gservice (U19), audience: customer|employee, form: ViewDefinitionRef, approvals: WorkflowRef?, fulfilment: work-order|automated|task, sla: SLADefinitionRef }` · `ServiceRequest { id, item, requester, subject (unit/asset/location), answers, status, sla clock }` · `WorkOrder { id, source (request/claim/maintenance/order line), service, tasks: [{checklist, required skills, estimated Duration}], parts: [{unit, qty}], location, unit? (U79), window: ReservationRef, assigned: [ResourceRef], status: new|scheduled|dispatched|en-route|on-site|paused|completed|incomplete|cancelled, outcome, signature, photos, timeLogs, billable? }` · `DispatchPlan { date, region, assignments, routes (U36), optimisationScore }` · `TimeLog { resource, workOrder, kind: travel|work|break, range: TimeRange }`.

## 3. Commands, Queries, Events, APIs
Commands: `SubmitServiceRequest`, `CreateWorkOrder`, `ScheduleWorkOrder` (slot selection), `Dispatch(plan)`, `StartTravel`, `Arrive`, `CompleteTask`, `ConsumePart`, `CaptureSignature`, `CompleteWorkOrder`, `MarkIncomplete(reason → follow-up)`.
Queries: `AvailableWindows(service, location, range)`, `TechnicianDay(resource, date)`, `OpenWorkOrders(scope)`.
Events: `field-service.request.submitted`, `field-service.work-order.scheduled|dispatched|arrived|completed`, `field-service.part.consumed`.
```text
POST /v1/field-service/requests    POST /v1/field-service/work-orders
POST /v1/field-service/work-orders/{id}:schedule|:dispatch|:arrive|:complete
GET  /v1/field-service/windows?service=&location=&from=&to=
```

## 4. Rules
Dispatch optimisation (vehicle-routing with time windows & skills; solver pack, e.g. OR-Tools) with decision weights `field-service.dispatch-weights`; emergency jobs pre-empt per priority; customer "on my way" notifications with ETA (Communication + Logistics).

## 5. Security & Compliance
Technician sees job-limited customer data; masked calling; safety checklists for hazardous work (electrical, gas) mandatory per service credential; labour law hours limits per jurisdiction (decision with Workforce U46).

## 6. Gaps
```prolog
gap(service_without_catalog_item, T, S) :- tenant(T), offers_service(T, S), field_service(S), not catalog_item(T, S).
gap(no_skilled_resources, T, S, Z) :- tenant(T), offers_service_in_zone(T, S, Z), not qualified_resource_in_zone(T, S, Z).
```

## 7. AI & Ops & UI & Scale
AI: duration prediction, first-time-fix part recommendations, technician copilot (manuals RAG from U07). Signals: `first_time_fix_rate`, `on_time_arrival_ratio`, `utilisation{resource}`, `work_order_tat`. Views: `service.catalog` (portal), `dispatch.board` (Gantt by technician + map), technician mobile `job.run` (offline, checklists, camera, signature, parts scan), `service-request.tracker`. Scale: 10⁶ work orders/day platform; T1.

## Appendix
- **C.** 0.1.0.

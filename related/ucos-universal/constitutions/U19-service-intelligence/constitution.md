# U19 — Service Intelligence Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U19-service` |
| Layer | L3 Knowledge & Registry (global) / L5 (tenant consumption) |
| Domain | 02 Knowledge |
| Steward | `ucos:org:knowledge-services` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (registry, service models, SLA templates), P5–P6 (service-visit fulfilment, Resource scheduling at scale) |
| Depends on | U05 Ontology, U06 Taxonomy (service-category), U13 Temporal (durations, SLAs, availability), U17 Resource (P2), U14 Currency & Unit, U67 Compliance (licensed professions) |
| Depended on by | U21 Catalog (service listings), U35 Fulfillment (service-visit), U39 Support (service SLAs), U27 Subscription (service plans), industry packs (healthcare, education, home services, mobility) |
| Master references | §10.2 (services follow same pattern with GSID) |

> Service Intelligence owns the **global definition of services as products**: `GlobalService` (GSID) — what is delivered, how (delivery model), how long, by whom (required qualifications/resources), under which service-level templates and regulatory requirements; plus `ServicePlan` templates (packages/tiers) and SLA templates. Tenants sell services via Catalog listings referencing GSIDs and deliver them via Fulfillment/Resource scheduling.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| SVC-L1 | A service's duration, scheduling and SLA semantics are expressed with Temporal value types (Duration, BusinessDuration, SLADefinition templates). | META lint. |
| SVC-L2 | Services requiring licensed providers (medical, legal, financial advice, electrical work…) declare the required credential types; listings cannot publish without provider credentials verified. | GlobalService `requiredCredentials` + Catalog publish guard. |
| SVC-L3 | Service outcomes/deliverables are explicit (what the customer receives), to support consumer law and dispute resolution. | Required `deliverables` field. |

---

## 2. Objects
- **`GlobalService`** `{ id GSID (ucos:gservice:…), name, category (ucos.service-category), deliverables: [LocalizedText], deliveryModel: on-site|at-provider|remote-live|remote-async|hybrid, typicalDuration: Duration | range, schedulingMode: slot|window|on-demand|asynchronous|recurring, resourceRequirements: [{resourceType (U17), qty, skills: [taxonomy:skill], credentials: [credentialType]}], prerequisites (e.g. site survey), consumables?: [GPID], regulatory {licensedProfession?: credentialType, jurisdictionsRestricted?, consentRequired?}, slaTemplates: [SLADefinitionTemplate], cancellationNorms (reference), attributes (Attribute Registry), media, status }`
- **`ServicePlan`** (template) `{ id, service(s), tiers: [{name, inclusions, limits (e.g. visits per year), slaTemplate}], billing hint: one-time|subscription|usage }`
- **`SLADefinitionTemplate`** `{ id, metric: response|arrival|resolution|availability, target: BusinessDuration|Percentage, calendarKind: business-hours|24x7, pauseConditions }` → instantiated as U13 `SLADefinition` per tenant.
- **`CredentialType`** `{ id, name, issuingAuthorities by jurisdiction, verificationMethod, renewalPeriod }` (e.g. licensed electrician, registered medical practitioner).

## 3. Commands, Queries, Events, APIs
Commands: `ProposeGlobalService`, `PublishGlobalService`, `DefineServicePlanTemplate`, `RegisterCredentialType` (governed), `ContributeFromTenant`.
Events: `service.global.published|updated|deprecated`, `service.credential-type.registered`.
Queries: `GetGlobalService(gsid, locale)`, `SearchServices(q, category, deliveryModel)`, `RequirementsFor(gsid, jurisdiction)` (credentials, consents, resources), `SlaTemplates(gsid)`.
```text
GET /v1/service/global/{gsid}     GET /v1/service/global?q=&category=&model=
GET /v1/service/global/{gsid}/requirements?jurisdiction=
POST /v1/service/global           (proposal)
```
Errors: `SVC_CREDENTIAL_TYPE_UNKNOWN`, `SVC_RESTRICTED_IN_JURISDICTION`.

## 4. Rules
- Scheduling mode drives Fulfillment: `slot` → Temporal AvailabilityWindow on Resources; `window` → arrival window promise; `on-demand` → dispatch (U37 Mobility pattern); `asynchronous` → task/case with SLA.
- Decision tables: `service.credential-requirements` (jurisdiction × service), `service.cancellation-norms` (consumer-law defaults per jurisdiction).

## 5. Security & Compliance
Professional regulation (medical councils, bar councils, electrical licensing), consumer protection for services (cooling-off for off-premises contracts), health data (if healthcare pack). Credentials verified via U09 VerificationRecords with expiry triggers (U13).

## 6. Gaps
```prolog
gap(service_without_sla_template, S) :- global_service(S), published(S), not sla_template(S, _).
gap(unverified_provider_credential, L) :- listing(L), service_of(L, S), requires_credential(S, C), provider(L, P), not verified_credential(P, C).
gap(no_scheduling_capability, T, S) :- tenant(T), sells_service(T, S), scheduling_mode(S, slot), not capability(T, temporal.availability).
```

## 7. AI
Service description normalisation, deliverable extraction, duration estimation from historical data, credential document verification assistance (human approval).

## 8. Operations & UI & Scale
Signals: `services_published`, `credential_expiry_30d`. Views: `service.global.detail`, `service.requirements.matrix`, `service.plan.template.editor`. Scale: 10⁵–10⁶ global services; small, cached. T1.

## Appendix
- **C.** 0.1.0.

## Appendix D — Completeness extensions (amendment A-29)
- The **service request catalogue** (customer and employee/ITSM requests) is implemented by U82 `ServiceCatalogItem`, referencing GSIDs.
- **Service natures:** `on-site`, `remote-live`, `async-digital` (SaaS seats, APIs, cloud), `subscription-managed` (AMC/managed services via U27/U80), `professional` (time & materials, via U96 timesheets), `transport` (via U37/U81 seats), `hospitality-stay` (via industry pack + U13 reservations), `financial` (U100), `public-service` (government pack: permits, certificates).
- **Usage-metered services:** a `meteringDimension` (API calls, GB, minutes, kWh) is declared on GlobalService. Rating and billing are in U27 Subscription (Phase 2).
- **Outcome-based services:** an `outcome` definition with measurable KPI and evidence, priced through U23 rules.

## Appendix P1 — Phase 1 behaviour without later-phase dependencies
- **U17 Resource (Phase 2):** in Phase 1, services are sold as fixed-time slots on a store or organisation AvailabilityWindow (U13). There is no per-person or per-vehicle resource assignment. Credentials are recorded but not used for automatic matching. Migration: when U17 activates, AvailabilityWindows are re-bound to Resource calendars without changing reservation ids.

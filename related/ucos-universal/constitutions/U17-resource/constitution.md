# U17 — Resource Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U17-resource` |
| Layer | L4 Foundation |
| Domain | 01 Foundation |
| Steward | `ucos:org:foundation-resources` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 |
| Depends on | U13 Temporal (resource calendars, availability, reservations, time off), U12 Geography (location, service areas), U11 Party (people), U79 Installed Base (equipment/vehicles as units), U19 Service (skills/credentials), U46 Workforce (employment, P4), U14 Units (capacity units) |
| Depended on by | U82 Field Service, U83 Rental, U37 Mobility, U105 Workplace, U109 Contact Centre (agents capacity), U47 Manufacturing (work centres), U81 (venues), healthcare/education/hospitality packs |
| Master references | §6.2 U17, U19 Appendix P1 (migration from store-level windows) |

> Resource owns **things and people that provide capacity over time**: resources (people, vehicles, rooms, desks, machines, beds, courts, compute pools, venues), resource types and attributes, skills and credentials bindings, capacity models (units, concurrency), pools and groups, location/service areas, and the binding of each resource to its Temporal calendar and availability. Scheduling logic itself is Temporal (U13); dispatch/assignment logic lives in consuming universes (U82, U37, U109).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| RES-L1 | Every schedulable resource has exactly one resource calendar (with inheritance) and capacity model; availability is computed only by U13. | Registry constraint; TMP-L4. |
| RES-L2 | Person resources reference a Party; personal schedule details are visible only on a need-to-know basis (busy/free for others). | Policy obligations (busy-only masking). |
| RES-L3 | Assignment respects required skills/credentials valid at the time of work. | Skill/credential validity (TimeRange) check exposed to consumers. |

## 2. Objects
`ResourceType { id, kind: person|vehicle|room|desk|machine|bed|court|venue|compute|other, attributes schema, capacityModel: {unit (U14), concurrency, divisible: bool} }` · `Resource { id, type, name, party? (person), unit? (U79 asset), location/serviceArea (U12), calendar (U13), skills [{skill, level, validity: TimeRange}], credentials [VerificationRecordRef], capacity, status: active|inactive|retired }` · `ResourcePool { id, members (resources/types/rules), selection strategy: any|round-robin|least-loaded|skill-best }` · `CapacityPlan { pool, period: TimeRange, demand forecast (U94), planned capacity }`.

## 3. Commands, Queries, Events, APIs
Commands: `DefineResourceType`, `RegisterResource`, `AssignSkill`, `AttachCredential`, `SetResourceCalendar`, `DefinePool`, `RetireResource`.
Queries: `EligibleResources(requirements, time, location)` (skills/credentials/location filter → then U13 availability), `PoolCapacity(pool, range)`, `Utilisation(resource, range)`.
Events: `resource.resource.registered|retired`, `resource.skill.expiring`.
```text
POST /v1/resource/types   POST /v1/resource/resources   POST /v1/resource/pools   POST /v1/resource/eligible
```

## 4. Gaps, Ops, UI
```prolog
gap(resource_without_calendar, R) :- resource(R), schedulable(R), not calendar_of(R, _).
gap(skill_expired_in_use, R)      :- resource(R), assigned_future_work(R, W), requires_skill(W, S), not valid_skill_at(R, S, W).
```
Signals: `utilisation_ratio{type}`, `idle_capacity`, `skills_expiring_30d`. Views: resource directory, resource detail (calendar via U13 resource grid, skills, credentials), pool editor, capacity planner. T1.

## Appendix
- **C.** 0.1.0.

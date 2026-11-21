# U55 — Digital Twin Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U55-digital-twin` |
| Layer | L8 Intelligence |
| Domain | 07 Intelligence |
| Steward | `ucos:org:intelligence-twins` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 |
| Depends on | U92 IoT (telemetry), U79 Installed Base (physical units), U17 Resource, U12 Geography (indoor/outdoor spatial frames, U77 frames), U75 Knowledge Graph, U54 Simulation, U13 Temporal (time series, historical state), U94 ML (predictive models) |
| Depended on by | U47 Manufacturing (line twins), U105 Workplace (building twins), U36 (warehouse twins), U82 (predictive maintenance), U98 (energy) |
| Master references | §6.2 U55 |

> Digital Twin owns **live models of physical systems**: twin types (asset, line, building, warehouse, fleet, city zone), twin instances bound to real units and sensors, the state model (properties, relationships, telemetry bindings), historical state query (as-of), derived KPIs, and predictive/what-if overlays via U54/U94. It does not own devices (U92) or units (U79).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| TWN-L1 | Every twin property declares its source (sensor, system of record, model) and freshness objective; stale values are flagged. | Binding schema + freshness monitor. |
| TWN-L2 | Commands to physical systems go through the owning universe (U92 device commands) with safety interlocks; twins never actuate directly. | No actuation API in U55. |
| TWN-L3 | Twin spatial data uses declared frames of reference (U77), including local/indoor frames. | Frame ref required on geometry. |

## 2. Objects
`TwinType { id, properties [{name, type, unit, source kind}], relationships, telemetry schema, KPIs (CEL) }` (DTDL-compatible import/export) · `Twin { type, boundTo (unit/resource/location), frame (U77), properties state, bindings [{property, deviceStream/objectRef/model, freshnessObjective: Duration}] }` · `TwinSnapshot { twin, asOf: TimePoint, state }`.

## 3. Commands, APIs
Commands: `DefineTwinType`, `CreateTwin`, `BindProperty`, `QueryState(asOf)`, `RunWhatIf` (U54). Events: `twin.state.changed` (sampled), `twin.kpi.breached`, `twin.binding.stale`.
```text
POST /v1/twins/types   POST /v1/twins   GET /v1/twins/{id}/state?asOf=   GET /v1/twins/{id}/history?range=
```

## 4. Gaps, UI
```prolog
gap(twin_property_unbound, T, P) :- twin(T), property_of_type(T, P), not binding(T, P, _).
```
Views: 2D/3D twin viewer with live overlays, KPI board, time-scrubber for historical state. T2.

## Appendix
- **C.** 0.1.0.

# U54 — Simulation Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U54-simulation` |
| Layer | L8 Intelligence |
| Domain | 07 Intelligence |
| Steward | `ucos:org:intelligence-simulation` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 |
| Depends on | U58 Composition (blueprints to simulate), U61 Event (recorded event streams for replay), U53 Decision (rules under test), U94 ML (demand models), U13 Temporal (simulated clocks), U72 Observability, U55 Digital Twin (state), U73 (ephemeral sandboxes) |
| Depended on by | U76 Evolution (impact analysis), U02 Governance (what-if on proposals), U23/U22 (price/promo what-ifs), U74 Certification (load/chaos scenarios), U47/U36 (capacity plans) |
| Master references | §28 (evolution loop), A-63 (simulators per port are U62/packs, not this universe) |

> Simulation owns **what-if analysis on business behaviour**: scenarios, synthetic or replayed inputs, simulated clocks, models of actors (customers, carriers), runs in isolated sandboxes, and comparative results. Port simulators used for testing integrations (e.g. `payment.simulator`) are adapters owned by their universes; U54 composes them into scenarios.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| SIM-L1 | Simulations never touch production state or send real communications/payments. | Runs only in sandbox cells with simulator adapters forced (reality = `simulation` frame, U77 P-004). |
| SIM-L2 | Replayed production data is pseudonymised unless the purpose permits otherwise. | U66 purpose check; tokenisation. |
| SIM-L3 | Results record seeds, inputs and model versions so they can be reproduced. | Run manifest. |

## 2. Objects
`Scenario { baseline blueprint, changes (rules/prices/capacity), inputs: replay(range) | synthetic(generator, params), clock: {start: TimePoint, speed}, metrics }` · `SimulationRun { scenario, seed, sandbox cell, status, results, at: TimePoint }` · `Comparison { runs, metric deltas, confidence }`.

## 3. Commands, APIs
Commands: `DefineScenario`, `RunSimulation`, `CompareRuns`, `PromoteToProposal` (U02). Events: `simulation.run.completed`.
```text
POST /v1/simulation/scenarios   POST /v1/simulation/runs   GET /v1/simulation/comparisons/{id}
```

## 4. Gaps, UI
```prolog
gap(high_impact_proposal_unsimulated, P) :- proposal(P), blast_radius(P, high), not simulation_for(P).
```
Views: scenario builder, run monitor, comparison dashboard (baseline vs variant). T3.

## Appendix
- **C.** 0.1.0.

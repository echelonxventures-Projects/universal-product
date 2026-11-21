# Phase 0 spikes

Each spike settles a provisional decision before the end of Phase 0 (1 March 2027). A spike passes when every criterion holds. The result is recorded as a U01 DecisionRecord that confirms or reverses its ADR. The kits below are in the repository and run without a person or an AI writing anything new.

| Spike | Decision | Kit | Pass criteria | Due |
|---|---|---|---|---|
| **S-01** Composer Datalog engine — **passed 2026-10-03** | ADR-022 (embedded Go evaluator, accepted) | `tools/datalog.py export <pd> <dir>` writes the golden platforms' facts as Souffle `.facts`; `tools/datalog.py synth 125000 <dir>` writes ~1M synthetic facts; `tools/datalog.py oracle` is the reference result | The engine reproduces every golden blueprint exactly (same capability set and gaps as `spec/composition/golden/expected/`); < 10 s cold on 1M facts; < 1 s incremental for a one-fact change; provenance recorded for every derived fact | 2027-01-15 |
| **S-02** Identity provider | ADR-021 (Keycloak) | `tools/spikes/k6/s02-login.js` (5k logins/s across 100 tenant realms) | p99 token issue < 800 ms at 5k/s; every token's issuer matches its tenant realm; passkey registration and step-up (ACR) flows pass; token exchange (RFC 8693) for agents works | 2027-01-15 |
| **S-03** CEL parity | ADR-013 | `tools/spikes/cel-vectors.yaml` | Go and TypeScript evaluators agree on every vector (values and errors) and on 1M randomised expressions; < 50 µs per evaluation | 2027-02-01 |
| **S-04** Runtime interpretation performance | ADR-001, ADR-003 | `tools/spikes/k6/s04-addline.js` against a reference cell with the `d2c-in-ae` blueprint | 2,000 rps AddLine with p99 < 150 ms end to end for 15 minutes; no per-tenant code | 2027-02-15 |
| **S-05** Workflow engine | ADR-032 (Temporal.io) | `spec/workflows/order.lifecycle.yaml`, `spec/workflows/commerce.checkout.yaml` | Both definitions run on the engine through the interpreter workflow: durable timers (decision-driven), saga compensation, human task with SLA, version migration of running instances; ops cost estimated | 2027-02-15 |

## How to run S-01 with a candidate engine
```bash
python3 tools/datalog.py export spec/composition/golden/d2c-in-ae.pd.yaml generated/s01/d2c
python3 tools/datalog.py synth 125000 generated/s01/synth
# Load spec/rules/core/closure.dl plus the .facts directory into the engine, then compare its `required` relation
# with spec/composition/golden/expected/d2c-in-ae.blueprint.json (adapters are chosen by the engine's choice()).
```

`tools/datalog.py oracle` already runs `closure.dl` with a small reference evaluator on every CI run. It checks that the rules and the Python checker agree on all golden platforms, so the target the engine must match is itself verified.

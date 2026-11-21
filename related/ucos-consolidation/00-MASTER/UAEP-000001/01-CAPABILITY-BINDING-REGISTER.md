# Capability Binding Register

> AUTHORITY = NONE (DERIVED TRUTH). Exactly one binding per named capability,
> and the proof that every bound home resolves in Repository Truth.

| ID | Capability | Disposition | Homes | Bound to | Catalogue |
|---|---|---|---|---|---|
| `UAEP-CAP-01` | Universal Autonomous Engineering Meta-System | **COMPOSE** | 2/2 | `engine/kernel/__init__.py`, `platform/universal_pipeline/service.py` | RC-17, RC-56 |
| `UAEP-CAP-02` | Universal Autonomous Engineering Platform | **REUSE** | 1/1 | `platform/universal_pipeline/service.py` | RC-56 |
| `UAEP-CAP-03` | Universal Autonomous Pipeline Framework | **REUSE** | 2/2 | `platform/universal_pipeline/__init__.py`, `platform/universal_pipeline/catalog/uapf-pipelines.json` | RC-56 |
| `UAEP-CAP-04` | Universal Work Orchestrator | **REUSE** | 1/1 | `platform/universal_pipeline/orchestrator.py` | RC-56 |
| `UAEP-CAP-05` | Universal Integration Gateway | **REUSE** | 1/1 | `platform/universal_pipeline/gateway.py` | RC-56 |
| `UAEP-CAP-06` | Universal Meta Object Engine | **REUSE** | 1/1 | `platform/universal_pipeline/identity.py` | RC-56 |
| `UAEP-CAP-07` | Universal Registry Engine | **REUSE** | 2/2 | `platform/universal_pipeline/registry.py`, `engine/registry/__init__.py` | RC-56, RC-20 |
| `UAEP-CAP-08` | Universal Identity Engine | **REUSE** | 2/2 | `platform/universal_pipeline/identity.py`, `platform/identity/__init__.py` | RC-56, RC-44 |
| `UAEP-CAP-09` | Universal Relationship Engine | **REUSE** | 1/1 | `platform/universal_pipeline/dependencies.py` | RC-56 |
| `UAEP-CAP-10` | Universal Graph Engine | **EXTEND** | 2/2 | `engine/graph/__init__.py`, `platform/universal_pipeline/registry.py` | RC-16, RC-56 |
| `UAEP-CAP-11` | Universal Event Engine | **REUSE** | 1/1 | `platform/universal_pipeline/events.py` | RC-56 |
| `UAEP-CAP-12` | Universal State Engine | **REUSE** | 1/1 | `platform/universal_pipeline/state.py` | RC-56 |
| `UAEP-CAP-13` | Universal Policy Engine | **REUSE** | 1/1 | `platform/universal_pipeline/governance.py` | RC-56 |
| `UAEP-CAP-14` | Universal Discovery Engine | **REUSE** | 2/2 | `engine/discovery/__init__.py`, `platform/universal_pipeline/discovery.py` | RC-12, RC-56 |
| `UAEP-CAP-15` | Universal Execution Engine | **REUSE** | 1/1 | `platform/universal_pipeline/execution.py` | RC-56 |
| `UAEP-CAP-16` | Universal Repository Truth Engine | **EXTEND** | 4/4 | `platform/repository_intelligence/__init__.py`, `intelligence/rie/__init__.py`, `00-BOOK/tools/ukb.py`, `00-BOOK/DATA/id-ledger.json` | RC-50, RC-32 |

## Reuse rationale, per capability

### UAEP-CAP-01 — Universal Autonomous Engineering Meta-System

Disposition **COMPOSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented. Recorded gap: The name has no single home in the repository. Recorded as a genuine naming absence and discharged by composition, not by creating a new engine.

### UAEP-CAP-02 — Universal Autonomous Engineering Platform

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-03 — Universal Autonomous Pipeline Framework

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-04 — Universal Work Orchestrator

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-05 — Universal Integration Gateway

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-06 — Universal Meta Object Engine

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-07 — Universal Registry Engine

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-08 — Universal Identity Engine

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-09 — Universal Relationship Engine

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-10 — Universal Graph Engine

Disposition **EXTEND**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented. Recorded gap: The name 'Universal Graph Engine' has no home; the capability does, under the name 'Universal Knowledge Graph'. Recorded as a naming difference, not a missing capability.

### UAEP-CAP-11 — Universal Event Engine

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-12 — Universal State Engine

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-13 — Universal Policy Engine

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-14 — Universal Discovery Engine

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-15 — Universal Execution Engine

Disposition **REUSE**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented.

### UAEP-CAP-16 — Universal Repository Truth Engine

Disposition **EXTEND**. The bound catalogue record prohibits replacement, so this capability is bound by pointer and never re-implemented. Recorded gap: The name 'Universal Repository Truth Engine' has no single home. The capability is held by three existing owners and is bound to all of them; the absence of one merged engine is recorded rather than closed by building one.

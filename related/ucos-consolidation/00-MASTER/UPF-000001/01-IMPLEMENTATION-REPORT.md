# Universal Provider Framework — PROGRAM-003 (WAVE-2)

- Artifact: **UPF-000001**
- Authority: **NONE (DERIVED TRUTH)**
- Framework home: `engine/provider` (v1.0.0)
- Realizes over: engine/kernel (PROGRAM-002, immutable baseline)
- Verdict: **CONSTITUTIONALLY-COMPLIANT**
- Report hash: `72b4a24fb4a45c237988b0403a0bbaf41b261f2554f7d5e64335a646034e5d28`

## What was implemented

The Universal Provider Framework: the constitutional realization layer over the immutable PROGRAM-002 kernel. A provider category is a registered kernel meta-type (open set); a provider is a kernel `MetaObject` classified by its category, carrying its contract, capabilities, metadata, health and lifecycle as open attributes and its dependencies / policy / context as governed relationships. The framework modifies neither the kernel nor any other package.

## Reuse analysis (duplicate detection)

A distinct EC-2 Universal Provider Architecture exists at platform/universal_provider (Terminal-04). It is a higher-layer artifact that does not reference the PROGRAM-002 kernel and contains a closed ProviderState enum. This framework is the ENGINE-layer realization over the immutable kernel; the engine layer cannot depend on the platform layer, so the two coexist at different layers over different substrates. engine/provider imports and modifies neither the kernel nor platform/universal_provider.

## Provider responsibilities and their homes

| ID | Responsibility | Mechanism (Repository Truth) |
|---|---|---|
| UPF-R-01 | Universal Provider Contract | `engine/provider/framework.py` |
| UPF-R-02 | Universal Provider Identity | `engine/kernel/identity.py` |
| UPF-R-03 | Universal Provider Registry | `engine/kernel/registry.py` |
| UPF-R-04 | Universal Provider Classification | `engine/provider/metatypes.py` |
| UPF-R-05 | Universal Provider Discovery | `engine/provider/framework.py` |
| UPF-R-06 | Universal Provider Resolution | `engine/provider/framework.py` |
| UPF-R-07 | Universal Provider Composition | `engine/provider/framework.py` |
| UPF-R-08 | Universal Provider Lifecycle | `engine/provider/framework.py` |
| UPF-R-09 | Universal Provider Dependencies | `engine/provider/framework.py` |
| UPF-R-10 | Universal Provider Compatibility | `engine/provider/framework.py` |
| UPF-R-11 | Universal Provider Versioning | `engine/kernel/registry.py` |
| UPF-R-12 | Universal Provider Selection | `engine/provider/selection.py` |
| UPF-R-13 | Universal Provider Negotiation | `engine/provider/framework.py` |
| UPF-R-14 | Universal Provider Governance | `engine/provider/framework.py` |
| UPF-R-15 | Universal Provider Validation | `engine/provider/framework.py` |
| UPF-R-16 | Universal Provider Certification | `engine/provider/framework.py` |
| UPF-R-17 | Universal Provider Evidence | `engine/kernel/registry.py` |
| UPF-R-18 | Universal Provider Metadata | `engine/provider/framework.py` |
| UPF-R-19 | Universal Provider Health Model | `engine/provider/framework.py` |
| UPF-R-20 | Universal Provider Capability Advertisement | `engine/provider/framework.py` |
| UPF-R-21 | Universal Provider Policy Binding | `engine/provider/framework.py` |
| UPF-R-22 | Universal Provider Context Binding | `engine/provider/framework.py` |
| UPF-R-23 | Universal Provider Audit Model | `engine/kernel/registry.py` |
| UPF-R-24 | Universal Provider Traceability | `engine/provider/framework.py` |

## Universal Provider Law honoured

- Possess identity, be registered, discoverable, governed, versioned, validated, certified, traceable, replaceable, composable, evolvable — each mechanised over the kernel. No provider requires framework redesign (registration only).

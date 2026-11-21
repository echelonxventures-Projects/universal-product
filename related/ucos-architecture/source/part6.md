---

# PART VI — BUILD PRODUCTION SYSTEM

The flow "prompt → documents → code → finished platform" breaks down at this scale. Instead, UCOS **produces itself** through a constitutional production system. Humans author and ratify constitutions and meanings. Everything downstream is modeled, generated, proven and certified.

## {{§§specstack}} Specification Stack

Each specification below is a constitutional artifact set derived from this root document. Together they make up the build specification.

| # | Specification | Produced in | Built from |
| --- | --- | --- | --- |
| S1 | Universal Meta-Model Specification (object, field types, relationships, lifecycle, UGID, inheritance, composition, references) | {{Constitution & Law}} | Part II |
| S2 | Universe Specifications × 82, genome-complete | each universe | Part IV + {{§genome}} + Appendix D |
| S3 | Universe and domain catalog | {{Capability}} | {{§register}} |
| S4 | Capability catalog (every capability, with its genome) | {{Capability}} | S2 |
| S5 | Canonical object and schema registry | {{Registry}} | S2 slot B |
| S6 | Event catalog | {{Event}} | S2 slot C |
| S7 | API catalog and API meta-model | {{API}} | S2 slot C/D |
| S8 | Workflow catalog | {{Workflow}} | S2 slot C |
| S9 | Policy catalog | {{Policy}} | S2 slot C/E |
| S10 | Security control catalog | {{Security}} | S2 slot E |
| S11 | Compliance control catalog and regulation packs | {{Compliance}} | S2 slot E |
| S12 | Global product, service and offer knowledge base | {{GOKN}} | — |
| S13 | Experience / UI meta-model specification | {{Experience}} | S2 slot F |
| S14 | Data and database meta-model specification | {{Data}} | S2 slot B |
| S15 | Runtime Fabric specification (engines, enforcement points) | {{Runtime Fabric}} | {{§rules}} |
| S16 | Builder Studio specification | {{Composition}} | {{§definition}} |
| S17 | Generation specification (generators, template packs) | {{Generation}} | S5–S15 |
| S18 | AI and agent specification | {{Intelligence}} · {{Agent}} | S2 |
| S19 | Knowledge specification (ontology, graph, truth model) | {{Knowledge}} | S2 slot B |
| S20 | Testing, proof and certification specification | {{Testing & Proof}} · {{Certification}} | S2 slot I |
| S21 | Operations specification (SRE, incidents, DR, FinOps) | {{Operations}} · {{Resilience}} | S2 slot H |
| S22 | Evolution specification | {{Evolution}} | S2 slot J |

**Master views.** These are generated from the registries and never hand-maintained:

- Master constitutional index
- Universe dependency graph and universe relationship graph
- Constitutional authority graph
- The object, schema, event, API, workflow, runtime, security, compliance, certification, capability and knowledge registries
- The generation, runtime, validation, certification, evolution, autonomous-discovery, autonomous-governance and self-improvement strategies. Each is a section of S15–S22.

## {{§§chain}} Production Chain & Artifact Classes

```text
AUTHORED (human-ratified, AI-assisted)
  Universal Constitution → Universe Constitutions → Ontologies → Taxonomies → Policies
        │
MODELED (machine-readable metadata, the single source of truth)
  Canonical Objects → Schemas → Relationships → Commands & Events → API Contracts
  → Workflow & State-Machine Contracts → Decision Models → Experience (UI) Models → Genomes complete
        │
GENERATED (never edited by hand)
  Generators → Backend services · APIs · SDKs · Frontends · Mobile & multi-surface apps · Portals
             · Data stores & migrations · Wiring · Security controls · Compliance controls
             · Observability · Infrastructure · Pipelines · Documentation · Tests
        │
ASSURED & RELEASED
  Proof → Certification → Release approval → Deployment → Operation → Audit → Evolution ⟲
```

| Artifact class | Source of truth | Producer | Validator | Certifier | Repository path |
| --- | --- | --- | --- | --- | --- |
| Constitutions, laws, standards | human-authored | {{Constitution & Law}} | {{Platform Intelligence}} | ratified by {{Authority & Governance}} | `constitutions/` |
| Kernel meta-model | Part II | {{Constitution & Law}} | {{Testing & Proof}} | {{Certification}} | `kernel/` |
| Universe genome bundle | genome | owning universe | {{Platform Intelligence}} | {{Certification}} | `universes/Uxx-*/` |
| Ontology, taxonomy | genome slot B | {{Knowledge}} | {{Knowledge}} (contradiction check) | {{Certification}} | `universes/Uxx-*/ontology/` |
| Objects, schemas, events, commands, API contracts, workflows, decisions, policies, UI models | genome slots B–F | owning universe | {{Testing & Proof}} | {{Certification}} | `universes/Uxx-*/…` |
| Backend services, APIs, SDKs, UI, apps, data DDL, infrastructure, controls, observability, docs, tests | contracts | {{Generation}} | {{Testing & Proof}} | {{Certification}} | `generated/…` |
| Engines (hand-written, L15) | S15 | {{Runtime Fabric}} | {{Testing & Proof}} | {{Certification}} | `runtime/` |
| Generators and template packs (hand-written, L15) | S17 | {{Generation}} | {{Testing & Proof}} | {{Certification}} | `generators/` |
| Adapters (hand-written, L15) | provider SPIs | {{Integration}} | {{Testing & Proof}} (contract tests) | {{Certification}} | `adapters/` |
| Platform definitions | configuration | {{Composition}} | {{Platform Intelligence}} | {{Certification}} | `compositions/` |
| Proofs, certificates, evidence | runs | {{Testing & Proof}} · {{Certification}} | — | — | `certification/` |
| Gap and completeness reports | scans | {{Platform Intelligence}} | — | — | `gaps/` |
| Evolution proposals and migrations | horizon scans, findings | {{Evolution}} | {{Simulation}} | adopted by {{Authority & Governance}} | `evolution/` |

## {{§§concerns}} How Each Concern Is Produced

This section answers how backend, frontend, UI/UX, apps, APIs, wiring, hardening, data and infrastructure get built. The answer for each is: from contracts, by generators, with proof.

| Concern | Input contracts | Generated output | Assurance |
| --- | --- | --- | --- |
| **Backend** | canonical objects, commands, events, state machines, policies, decisions | command handlers, repositories, validators, event processors and enforcement-point bindings, all running on {{Runtime Fabric}} | contract, unit and integration tests; policy proofs |
| **APIs** | API contracts (genome C/D) | REST, GraphQL, gRPC and async APIs; SDKs; API docs | contract tests; backward-compatibility proofs ({{Evolution}}) |
| **Frontend · UI/UX · apps** | Experience Model, design system, locale, accessibility rules, personalization hooks | web, mobile, tablet, desktop, TV, voice and AR/VR apps, and every portal | accessibility tests, journey tests, UX experiments ({{Experimentation}}) |
| **Data** | schemas, data contracts, retention and residency | DDL, migrations, data contracts, lineage registration | data-quality tests; migration proofs |
| **Wiring** | dependency graph (genome D), event contracts, composition workflows | event subscriptions, API clients, routes, mesh configuration, enforcement-point placement, context propagation | **zero manual wiring**: {{Platform Intelligence}} proves every declared dependency is wired and every wire is declared |
| **Hardening** | security baselines (genome E), threat models, sovereignty constraints | access policies, encryption and secret references, network policies, rate limits and WAF rules, SBOMs and signed artifacts, secure defaults | SAST, DAST, continuous penetration validation, supply-chain verification, security certification |
| **Compliance** | control mappings, regulation packs | controls, evidence hooks, audit packages | compliance proofs, continuous compliance |
| **Infrastructure** | scale, HA/DR and placement models (genome H), sovereignty | infrastructure-as-code, pipelines, DR plans | chaos and DR drills ({{Resilience}}), performance proofs |
| **Observability** | monitoring model, SLOs | telemetry, dashboards, alerts, runbooks | SLO verification |
| **Documentation & tests** | genome | documentation set, test suites | documentation-completeness and coverage gates |

## {{§§repo}} Repository Structure

```text
ucos/
├── constitutions/            human-ratified constitution, universe constitutions, laws, standards
├── kernel/                   meta-model, canonical object, field types, relationship & lifecycle models, UGID
├── universes/
│   └── Uxx-<name>/           one genome bundle per universe — sole owner of its concepts
│       ├── universe.yaml     slot A
│       ├── ontology/  taxonomy/  objects/  schemas/  relationships/
│       ├── commands/  events/  apis/  workflows/  decisions/  policies/
│       ├── security/  privacy/  compliance/  audit/
│       ├── experience/  analytics/  twin/  simulation/
│       ├── operations/  tests/  proofs/  certification/  evolution/
│       └── capabilities/<capability>/   same layout, per capability
├── knowledge-graph/          graph snapshots and named sub-graphs
├── registries/               registry partitions (rendered views)
├── blueprints/               industry blueprints, reference compositions, templates
├── compositions/             tenant platform definitions — configuration only
├── runtime/                  hand-written generic engines (L15)
├── generators/               hand-written generators and template packs (L15)
├── adapters/                 hand-written provider adapters behind SPIs (L15)
├── generated/                NEVER edited by hand
│   ├── api/  sdk/  services/  workflows/  data/
│   ├── ui-models/  ui/  apps/
│   ├── security/  compliance/  observability/  infrastructure/
│   └── docs/  tests/
├── certification/            proofs, certificates, evidence packages
├── gaps/                     gap and completeness reports
└── evolution/                proposals, impact analyses, migrations
```

The source drafts put `ontology/`, `taxonomy/`, `objects/` and `events/` at the top level. Here they live **inside each universe**, because ownership is per universe (L2). Similarly, `apps/`, `services/`, `infrastructure/`, `security/` and `tests/` live under `generated/`, because they are outputs, not sources (L15).

## {{§§waves}} Build Waves (Bootstrap Order)

The dependency tiers ({{§tiers}}) describe **runtime** direction. The build order is different, because the platform must first be able to build itself (L14).

| Wave | Scope | Exit criterion |
| --- | --- | --- |
| **0 — Kernel bootstrap** | {{Constitution & Law}}, kernel, {{Registry}}, a minimal {{Runtime Fabric}}, a minimal {{Generation}}, {{Identity}}, {{Security}}, {{Policy}}, {{Authority & Governance}}, {{Audit & Evidence}}, {{Tenancy & Ecosystem}}, {{Temporal}}, {{Event}}, {{Knowledge}}, base {{Infrastructure}} | **Self-hosting proof:** the kernel is regenerated by its own generator, and the result is equivalent |
| **1 — Assurance loop** | {{Capability}}, a minimal {{Composition}}, {{Testing & Proof}}, {{Certification}}, {{Platform Intelligence}}, {{Documentation}}, {{Deployment & Release}}, {{Observability}} | Any universe can go specify → generate → prove → certify → deploy, with a gap report |
| **2 — Foundation & control** | {{Spatial}}, {{Language & Locale}}, {{Measurement}}, {{Context & Reality}}, {{Party & Organization}}, {{Legal & Agreement}}, {{Compliance}}, {{Privacy & Consent}}, {{Sovereignty & Residency}}, {{Trust & Reputation}}, {{Risk}}, {{Data}} | The Context Frame resolves for any jurisdiction, language and currency |
| **3 — Core services** | {{Workflow}}, {{Decision}}, {{Content & Media}}, {{GOKN}}, {{Value & Economics}}, {{Communication & Collaboration}}, {{Integration}}, {{API}}, {{Experience}}, {{Search & Recommendation}}, {{Intelligence}}, {{Agent}}, {{Analytics}}, {{Resilience}}, {{Operations}} | A generic app (CRUD + workflow + UI + API) is generated for any universe, with zero hand code |
| **4 — Business domains** | Plane B, ordered by the first target Blueprint. For a marketplace: Offering → Catalog → Pricing → Offer & Incentive → Transaction → Marketplace → Payment → Billing → Finance → Tax → Inventory → Logistics → Relationship → Support. Then the rest | The first reference composition passes G1–G5 |
| **5 — Autonomy & foresight** | {{Digital Twin}}, {{Simulation}}, {{Experimentation}}, {{Correction}}, full {{Evolution}}, the {{Blueprint}} library, {{Cyber-Physical}}, {{Sustainability}}, the external Capability Marketplace, extension universes | A second, *unlike* composition (for example mobility after a marketplace) is produced without new engine code |

## {{§§genproc}} Governed Generation Process

Every universe, and later every capability, goes through the same governed loop:

1. **Draft** the universe constitution and genome with the Universe Specification Directive (Appendix D).
2. **Ownership check:** every concept used must either be owned by this universe in Appendix A or be referenced by its owner. A new concept is first proposed as a new index row with one owner (L2).
3. **Platform Intelligence scan:** overlaps, dependency cycles, missing slots, hard-coding.
4. **Ratify** through {{Authority & Governance}}.
5. **Generate** with {{Generation}}.
6. **Prove and test** with {{Testing & Proof}}.
7. **Certify** with {{Certification}}.
8. **Register and publish** to {{Registry}}.
9. **Deploy to a sandbox** and compose the universe into a reference blueprint.
10. **Run completeness** ({{§completeness}}) and record the gap report.
11. **Promote**, then enter the continuous assurance loop ({{§loop}}).

No single generation pass can produce the whole Specification Stack. The stack is produced one universe at a time, in wave order, under this process. It is a multi-year engineering program, governed by the platform it builds.

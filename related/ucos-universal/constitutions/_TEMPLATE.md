# U<NN> — <Universe Name> Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U<NN>-<slug>` |
| Layer | L<n> (see master §5) |
| Domain | <01 Foundation … 12 Architecture> |
| Steward | `ucos:org:<team>` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P<n> |
| Depends on | U.., U.. |
| Depended on by | U.., U.. |
| Master references | UCOS-MASTER-ARCHITECTURE §… |

> Purpose in one paragraph: what this universe is the **only** owner of, and what it deliberately does not own.

---

## 1. Constitution, Authority, Principles & Laws
- 1.1 Mandate (owns / does not own)
- 1.2 Universe laws (`<SLUG>-L1 …`), each with an enforcement mechanism
- 1.3 Authorities (who may change definitions and data, at which level)

## 2. Ontology & Taxonomy
- 2.1 Concepts and how they relate (diagram)
- 2.2 Taxonomies / enumerations owned (with seed values)
- 2.3 External standard mappings (ISO, W3C, IETF…)

## 3. Registry Model, Canonical Objects, Schemas & Relationships
- 3.1 Registries (global vs tenant scope)
- 3.2 Object types: full attribute tables (name, type, cardinality, constraints, classification)
- 3.3 Value types
- 3.4 Relationships (type, source → target, cardinality, materialised?)
- 3.5 Identifiers & natural keys

## 4. Commands, Queries, Events, APIs & Runtime Contracts
- 4.1 Commands (name, input, preconditions, effects, events emitted, idempotency)
- 4.2 Queries
- 4.3 Events (type, trigger, payload summary, classification)
- 4.4 REST surface (paths)
- 4.5 Ports / engine contracts offered to other universes
- 4.6 Error codes

## 5. Workflows, State Machines & Rules
- 5.1 Lifecycle state machine per stateful object
- 5.2 Workflows
- 5.3 Decision tables exposed for tenant configuration (with defaults)
- 5.4 Algorithms (normative pseudo-code where behaviour must be exact)

## 6. Policies, Security, Encryption, Audit & Compliance
- 6.1 Default authorization policies (Cedar)
- 6.2 Data classification per object/field
- 6.3 Encryption & key requirements
- 6.4 Audit requirements
- 6.5 Compliance controls implemented / supported

## 7. Validation, Certification, Versioning, Dependency & Reuse Rules
- 7.1 Validation rules
- 7.2 Certification criteria specific to this universe
- 7.3 Versioning & compatibility
- 7.4 Dependency rules (what may depend on this, and how)
- 7.5 Reuse rules (how other universes MUST consume it)

## 8. Discovery, Gap Detection, Self-Healing & Evolution Rules
- 8.1 Gap rules (Datalog) contributed to the Composition Substrate
- 8.2 Health checks & self-healing actions
- 8.3 Evolution rules & known future extensions

## 9. AI & Agent Governance
- 9.1 AI uses inside this universe
- 9.2 Agent tools exposed (and authority required)
- 9.3 Prohibited autonomous actions

## 10. Digital Twin, Analytics, Monitoring & Operations
- 10.1 Signals (metrics, business signals)
- 10.2 SLOs
- 10.3 Twin representation
- 10.4 Operational runbooks (index)

## 11. UI, UX, Accessibility & Localisation
- 11.1 Views (UI meta-model ids)
- 11.2 Key UX rules
- 11.3 Accessibility & localisation specifics

## 12. Scale, Performance, DR, HA, Multi-tenant / Region / Cloud
- 12.1 Volumetrics & performance targets
- 12.2 Tenancy & residency
- 12.3 HA / DR tier, RPO / RTO
- 12.4 Caching & replication

## Appendix
- A. Open questions
- B. Amendments proposed to the master architecture (if any)
- C. Change log

# U07 — Knowledge Graph Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U07-knowledge` |
| Layer | L3 Knowledge & Registry |
| Domain | 02 Knowledge |
| Steward | `ucos:org:knowledge-graph` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (definition graph / traceability, KnowledgeObject store), P4 (RAG grounding at scale, cross-source assertions) |
| Depends on | U04 Meta, U05 Ontology, U61 Event (projections), U65 Security (classification), U68 Audit (provenance), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U58 Composition (fact source), U75 Gap, U21/U18 (product graph), U44 Search, U49/U51 AI (RAG), U55 Twin, `ucos trace`, Governance impact analysis |
| Master references | §5.4 (Neo4j control plane), §7.7 (traceability), §21.6 (RAG), §6.2 U07 |

> The Universal Knowledge Graph (UKG) owns **the connected representation of what UCOS knows**: (1) the **definition graph** — every registered artifact and relationship (types, capabilities, rules, policies, controls, tests, evidence, blueprints) used for traceability, impact analysis and composition facts; (2) **KnowledgeObjects and Assertions** — facts with provenance and trust (e.g. "brand X is owned by org Y", market intelligence, knowledge-base articles' structured facts); (3) graph projections of selected tenant instance relationships. The graph is a **projection**, never the system of record for business objects (their owning universes are).

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| KG-L1 | Graph nodes for registry artifacts are projections from authoritative registries via events; writes to those nodes only come from projectors. | Graph write ACL: projector identities only. |
| KG-L2 | Every Assertion has provenance (source, method, time, confidence) and a trust score; consumers filter by trust. | Schema. |
| KG-L3 | Tenant-scoped subgraphs are isolated; cross-tenant traversal is impossible except over `global` nodes. | Graph partitioning (database per cell + tenant label constraints) + query rewriting. |
| KG-L4 | Contradictions are detected and surfaced, never silently resolved. | Contradiction detector (§3.2). |

---

## 2. Objects
- **Node kinds:** all registry definitions (ObjectType, Capability, EventType, Command, Policy, Control, Regulation, Clause, Test, Evidence, Certification, Blueprint, PD, Cell, Concept, TaxonomyNode, GlobalProduct, Brand, Organization (global), Jurisdiction, Regulation…), plus `KnowledgeObject`.
- **`KnowledgeObject`** (master §7 Knowledge Object model) `{ id, type: fact|article|document-extract|insight|rule-of-thumb, subjectRefs, content (structured or text with embedding), classification, trustScore, lineage, validation, certification? }`
- **`Assertion`** `{ id, subject: NodeRef, predicate: RelationshipTypeRef|AttributeRef, object: NodeRef|literal, validity: TimeRange, provenance: {source, method, agent?, confidence}, trust: 0..1, status: proposed|accepted|disputed|retracted }`
- **`Contradiction`** `{ assertions: [A1, A2], kind: value-conflict|cardinality-violation|disjointness, status, resolution }`
- **`TrustModel`** `{ sourceWeights, decay (by age), corroborationBoost, stewardOverride }` → trust score.

## 3. Rules & Algorithms
### 3.1 Projection
Projectors subscribe to `meta.*`, `capability.*`, `policy.*`, `compliance.*`, `audit.evidence.*`, `certification.*`, `composition.*`, `product.global.*` etc. and upsert nodes/edges idempotently (event id + version). Lag SLO p99 < 30 s. Full rebuild possible from registries (DR).

### 3.2 Contradiction detection
On assertion accept: check functional predicates (e.g. `ownedBy` cardinality 1 at a time), disjointness from Ontology, temporal overlap of conflicting values → open `Contradiction`, lower trust of both until resolved.

### 3.3 Trust score
`trust = Σ(sourceWeight × confidence × decay(age)) normalised, + corroboration (independent sources agreeing), capped; steward override = 1.0 with reason`.

### 3.4 Query surfaces
- Cypher (internal, platform engineers) — read-only for most roles.
- **Graph API** (typed queries): `Trace(id)`, `ImpactOf(change)`, `DependentsOf(node, depth)`, `Neighbours(node, predicates, depth, tenant)`, `Path(a, b)`.
- **Datalog export** for Composition snapshot (facts EDB).
- **RAG retrieval** API for AI: `Ground(question, tenant, scopes, minTrust)` → facts + documents with citations (object ids).

## 4. Commands, Events, APIs
Commands: `ProposeAssertion`, `AcceptAssertion`, `RetractAssertion`, `ResolveContradiction`, `RebuildProjection(scope)`.
Events: `knowledge.assertion.accepted|retracted`, `knowledge.contradiction.opened|resolved`.
```text
GET  /v1/knowledge/trace/{id}              POST /v1/knowledge/impact
GET  /v1/knowledge/nodes/{id}/neighbours?predicates=&depth=
POST /v1/knowledge/assertions              POST /v1/knowledge/ground   (AI retrieval)
```

## 5. Security & Compliance
Node classification inherited from source; query results filtered by PDP (`PartialEvaluate` → graph filters); RAG never returns content above the caller's clearance; tenant subgraphs per cell (residency).

## 6. Gaps
```prolog
gap(traceability_broken, A)   :- published_artifact(A), not trace_to_constitution(A).
gap(projection_lag, P)        :- projector(P), lag_seconds(P, S), S > 300.
gap(contradiction_open, C)    :- contradiction(C), open(C), age_days(C, D), D > 14.
```

## 7. AI
Grounding for all agents and assistants (master §21.6), assertion extraction from documents (proposed, low trust until corroborated), relationship discovery suggestions.

## 8. Operations, UI, Scale
Signals: `projection_lag_s{projector}`, `assertions_total{status}`, `contradictions_open`, `ground_latency_ms` (p95 < 400 ms). Views: `knowledge.explorer` (graph browse with filters), `trace.view` (`ucos trace` visual chain), `impact.view` (used by Governance), `contradiction.queue`. Scale: control-plane Neo4j cluster (10⁸ nodes definitions + global products link layer), tenant instance graphs in cells (Postgres + recursive queries or Neo4j per cell when needed). T1.

## Appendix
- **C.** 0.1.0.

# U59 — Generation Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U59-generation` |
| Layer | L7 Composition & Generation |
| Domain | 09 Platform |
| Steward | `ucos:org:platform-generators` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 (SDKs, API/AsyncAPI docs, DDL migrations, dashboards/alerts, test skeletons, diagrams), P3 (mobile app builds, user/admin manuals with AI drafting), P4 (IaC per cell from blueprints, evidence packs) |
| Depends on | U58 Composition (blueprints), U57 Capability (manifests), U04 Meta (types → DDL/schemas), U63 API, U61 Event, U64 UI, U72 Observability, U95 Software Delivery (outputs as artifacts with provenance), U74 Certification, U49 AI (non-deterministic drafting) |
| Depended on by | Developers (SDKs), U73 (IaC), U74 (tests/evidence), app stores (mobile builds), documentation portals |
| Master references | §12.1 (interpret first, generate second; ADR-001), §12.2 (generator contract), §12.5 |

> Generation owns **producing artifacts consumed outside the runtime** from definitions and blueprints: generator definitions, generation runs and generated artifacts — client SDKs, API/event documentation, database migrations, infrastructure-as-code, dashboards and alert rules, test suites, diagrams, mobile app builds, manuals/runbooks drafts, evidence packs. The runtime itself interprets metadata (ADR-001); generation never creates tenant-specific business code.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| GEN-L1 | Deterministic generators: same inputs → byte-identical outputs (hash recorded); generators are versioned and certified. | Reproducibility check in CI; `GenerationRun.outputHash`. |
| GEN-L2 | Non-deterministic (AI-assisted) generators produce **proposals** that require review and certification; never auto-activated. | Run kind flag; Governance proposal. |
| GEN-L3 | Generated files are never edited by hand; customisation happens in definitions or templates. | `generated/` excluded from manual commits (repo policy); header markers. |
| GEN-L4 | Every artifact carries provenance (inputs, generator version, run id) and SBOM/signature when distributed. | SLSA provenance via U95. |

## 2. Objects
`GeneratorDefinition { id, version, inputs: [Blueprint sections | manifests | object types], output: {kind: npm|maven|pod|pypi|go-module|openapi|asyncapi|sql-migration|tofu|crossplane|grafana|alert-rules|test-suite|mermaid|structurizr|mobile-app|docs|evidence-pack, path}, deterministic: bool, templates, validation commands }` · `GenerationRun { generator@version, inputHashes, outputHash, artifacts [ArtifactRef (U95)], status, at: TimePoint }`.

## 3. Seed generators
| Generator | Output | Phase |
|---|---|---|
| `gen.sdk.{typescript,kotlin,swift,python,go}` | client SDKs from OpenAPI/GraphQL | P2 |
| `gen.docs.api` / `gen.docs.events` | API reference, AsyncAPI catalogue | P2 |
| `gen.ddl.postgres` | expand/contract migrations from object-type diffs (KERNEL-DESIGN §4.1) | P0–P2 |
| `gen.schema.object-types` | JSON Schemas per object type from manifests + specs (`tools/gen_object_schemas.py` seed) | P0 |
| `gen.obs.dashboards` / `gen.obs.alerts` | Grafana dashboards, alert rules from signals/SLOs | P2 |
| `gen.tests.contract` / `gen.tests.scenario` / `gen.tests.load` | contract tests, Gherkin skeletons, k6 profiles | P2 |
| `gen.diagrams` | C4/ERD/flow diagrams from the knowledge graph | P2 |
| `gen.iac.cell` | OpenTofu/Crossplane claims for cells and tenant shards | P4 |
| `gen.mobile.app` | white-label React Native/Expo builds per brand | P3 |
| `gen.docs.manuals` (AI-assisted) | user/admin manuals, runbook drafts (proposals) | P3 |
| `gen.evidence.pack` | audit evidence packs (U68) | P4 |

## 4. Commands, Events, APIs, Gaps
Commands: `RegisterGenerator`, `RunGenerator(blueprint|scope)`, `PublishArtifacts`, `VerifyReproducibility`. Events: `generation.run.completed|failed`, `generation.artifact.published`.
```text
POST /v1/generation/generators   POST /v1/generation/runs   GET /v1/generation/runs/{id}
```
```prolog
gap(sdk_outdated, B, L) :- active_blueprint(B), sdk(B, L, V), V != api_version(B).
gap(generator_nondeterministic, G) :- generator(G), deterministic(G, true), reproducibility_failed(G).
```
Views: generator registry, run history with diffs, artifact downloads (signed). T2.

## Appendix
- **C.** 0.1.0.

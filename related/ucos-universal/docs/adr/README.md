# Architecture Decision Records

Each ADR records one significant decision: its context, the alternatives considered, the consequences and how it is enforced. ADRs are immutable once accepted. A change of direction is a new ADR that supersedes the old one, approved through U02 Governance with a U01 DecisionRecord (gate `ARCH-AUTH-01`).

| ADR | Decision | Status |
|---|---|---|
| [ADR-001](ADR-001-interpret-metadata-at-runtime-generate-only-external-artifacts.md) | Interpret metadata at runtime; generate only external artifacts | Accepted (master v1.0) |
| [ADR-002](ADR-002-control-plane-data-plane-split-with-cells.md) | Control plane / data plane split with cells | Accepted (master v1.0) |
| [ADR-003](ADR-003-hybrid-physical-model-generated-tables-for-core-types-jsonb-fo.md) | Hybrid physical model: generated tables for core types, JSONB for tenant extensions | Accepted (master v1.0) |
| [ADR-004](ADR-004-temporal-is-a-foundation-universe-no-raw-start-end-dates-elsew.md) | Temporal is a foundation universe; no raw start/end dates elsewhere | Accepted (master v1.0; strengthened by A-46, A-63) |
| [ADR-005](ADR-005-single-pdp-cedar-for-rbac-abac-rebac-and-pbac.md) | Single PDP (Cedar) for RBAC, ABAC, ReBAC and PBAC | Accepted (master v1.0) |
| [ADR-006](ADR-006-composition-rules-in-datalog-over-the-knowledge-graph.md) | Composition rules in Datalog over the knowledge graph | Accepted (master v1.0) |
| [ADR-007](ADR-007-transactional-outbox-and-sagas-no-distributed-two-phase-commit.md) | Transactional outbox and sagas; no distributed two-phase commit | Accepted (master v1.0) |
| [ADR-008](ADR-008-global-product-master-separated-from-tenant-listings.md) | Global product master separated from tenant listings | Accepted (master v1.0) |
| [ADR-009](ADR-009-packs-as-signed-oci-artifacts-with-sbom-and-slsa-provenance-wa.md) | Packs as signed OCI artifacts with SBOM and SLSA provenance; WASM for in-process extensions | Accepted (master v1.0) |
| [ADR-010](ADR-010-ai-through-a-gateway-with-policy-based-routing-agents-are-iden.md) | AI through a gateway with policy-based routing; agents are identities with bounded authority | Accepted (master v1.0; detailed in U49–U51) |
| [ADR-011](ADR-011-bitemporal-canonical-objects.md) | Bitemporal canonical objects | Accepted (master v1.0) |
| [ADR-012](ADR-012-kafka-api-event-backbone-with-cloudevents-envelope.md) | Kafka-API event backbone with CloudEvents envelope | Accepted (master v1.0) |
| [ADR-013](ADR-013-cel-as-the-single-expression-language.md) | CEL as the single expression language | Accepted (A-22) |
| [ADR-014](ADR-014-frames-of-reference-u77-make-every-foundation-frame-aware.md) | Frames of reference (U77) make every foundation frame-aware | Accepted (A-23…A-28) |
| [ADR-015](ADR-015-communication-is-part-of-every-platform-s-base-set.md) | Communication is part of every platform's base set | Accepted (A-60, A-64, A-65) |
| [ADR-016](ADR-016-durable-workflow-engine-temporal-io-class-for-long-running-pro.md) | Durable workflow engine (Temporal.io class) for long-running processes | Accepted (master v1.0; U60) |
| [ADR-017](ADR-017-go-for-the-kernel-go-and-typescript-sdks-for-packs.md) | Go for the kernel; Go and TypeScript SDKs for packs | Accepted (KERNEL-DESIGN) |
| [ADR-018](ADR-018-a-reference-checker-precedes-the-production-composer.md) | A reference checker precedes the production composer | Accepted (A-66, A-69) |
| [ADR-019](ADR-019-derived-manifests-for-universes-beyond-phase-1.md) | Derived manifests for universes beyond Phase 1 | Accepted (A-69) |
| [ADR-020](ADR-020-postgres-row-level-security-as-the-tenancy-guard.md) | Postgres row-level security as the tenancy guard | Accepted (KERNEL-DESIGN §4) |
| [ADR-021](ADR-021-keycloak-is-the-reference-identity-provider.md) | Keycloak is the reference identity provider | Accepted (provisional; confirmed by spike S-02 by 2027-01-15) |
| [ADR-022](ADR-022-composer-datalog-embedded-go-evaluator-with-the-python-checker.md) | Composer Datalog: embedded Go evaluator with the Python checker as oracle | Accepted (provisional; confirmed by spike S-01 by 2027-01-15) |
| [ADR-023](ADR-023-reservation-counters-stay-in-postgres-sharded-sub-slots.md) | Reservation counters stay in Postgres (sharded sub-slots) | Accepted |
| [ADR-024](ADR-024-cells-are-provisioned-with-opentofu-modules-wrapped-by-crosspl.md) | Cells are provisioned with OpenTofu modules wrapped by Crossplane | Accepted |
| [ADR-025](ADR-025-third-party-packs-run-under-gvisor.md) | Third-party packs run under gVisor | Accepted |
| [ADR-026](ADR-026-cedar-only-openfga-is-not-adopted.md) | Cedar only; OpenFGA is not adopted | Accepted (revisit at P6) |
| [ADR-027](ADR-027-standard-code-lists-are-bundled-only-when-their-licence-allows.md) | Standard code lists are bundled only when their licence allows multi-tenant redistribution | Accepted (S-06 records the per-source outcome) |
| [ADR-028](ADR-028-a-tenant-may-span-several-residency-regions-through-multiple-c.md) | A tenant may span several residency regions through multiple cells | Accepted |
| [ADR-029](ADR-029-format-preserving-tokenisation-covers-national-ids-and-bank-ac.md) | Format-preserving tokenisation covers national IDs and bank accounts only | Accepted |
| [ADR-030](ADR-030-global-product-data-comes-from-tenant-contributions-gs1-data-p.md) | Global product data comes from tenant contributions, GS1 data pools and licensed feeds | Accepted (commercial terms before P4) |
| [ADR-031](ADR-031-in-house-tax-packs-for-india-and-uae-engine-adapters-elsewhere.md) | In-house tax packs for India and UAE; engine adapters elsewhere | Accepted |
| [ADR-032](ADR-032-temporal-io-is-the-durable-workflow-engine.md) | Temporal.io is the durable workflow engine | Accepted (confirmed by spike S-05) |
| [ADR-033](ADR-033-react-native-for-the-mobile-renderer.md) | React Native for the mobile renderer | Accepted |
| [ADR-034](ADR-034-architecture-board-composition.md) | Architecture Board composition | Accepted (structure); members named by the founders before P0 genesis |
| [ADR-035](ADR-035-legal-interpretations-are-owned-by-in-house-counsel-with-exter.md) | Legal interpretations are owned by in-house counsel with external firms per jurisdiction | Accepted (structure) |
| [ADR-036](ADR-036-continuous-integration-is-deterministic-and-needs-no-person-or.md) | Continuous integration is deterministic and needs no person or AI to run | Accepted |
| [ADR-037](ADR-037-primary-cloud-provider-for-the-first-cells.md) | Provider-agnostic cells (no primary cloud provider) | Accepted |

All open decisions raised by the specs are recorded above (ADR-021…035). Provisional ADRs name the spike that confirms or reverses them. ADR-037 settled the last open one: cells are provider-agnostic.

Template: copy any ADR and keep the same headings.

# ADR-037: Provider-agnostic cells (no primary cloud provider)

| Field | Value |
|---|---|
| Status | **Accepted** (2026-10-04; replaces the earlier proposal to choose one primary cloud provider) |
| Deciders | Founder (Bipin Kumar) |
| References | ADR-002 (cells), ADR-012 (Kafka API), ADR-021 (identity), ADR-024 (OpenTofu + Crossplane), ADR-028 (multi-region tenants), gate `ARCH-INF-01`, U73 |

## Context
The earlier version of this ADR asked which single cloud provider (AWS, Azure or Google Cloud) should host the first cells in India and the UAE. Everything above the infrastructure was already portable and behind ports. The founder decided that UCOS stays agnostic: it must not depend on any one provider. It is finished and tested locally first, and goes to production only after that.

## Decision
1. **A cell is defined by contracts, not by a provider.** A cell needs:

   | Need | Contract | Examples (none required) |
   |---|---|---|
   | Compute | any conformant Kubernetes ≥ 1.31 | kind, k3s, on-premises, any managed Kubernetes |
   | Database | PostgreSQL 16+ wire protocol, with RLS | self-operated, CloudNativePG, any managed Postgres |
   | Event bus | Kafka API (ADR-012) | Redpanda, Apache Kafka, any managed Kafka API |
   | Identity | OpenID Connect with a JWKS endpoint (ADR-021) | Keycloak, any OIDC provider |
   | Object storage | S3 API | MinIO, Ceph, any S3-compatible store |
   | Secrets | a Kubernetes Secret named `ucos-kernel-env` | any secret manager or operator that produces one |
   | Telemetry | OpenTelemetry (OTLP) and Prometheus text format | any collector or backend |

2. **The kernel image carries everything else.** `ucos-kernel` includes the spec it reads and its migrations. The image applies the schema itself (`ucos-kernel migrate`, append-only, with digests and an advisory lock). It reports readiness only when the schema is current (`/api/v1/ready`). No provider SDK is linked.
3. **Manifests are provider-neutral.** `deploy/k8s/apps/kernel` contains:
   - the Deployment, Service and PodDisruptionBudget;
   - the migration Job (an Argo CD PreSync hook);
   - a NetworkPolicy that pins ports only.

   The control plane listens on loopback inside the pod, so operators reach it through `kubectl port-forward`. Access is therefore governed by Kubernetes RBAC on every platform.
4. **Local first.** `deploy/k8s/overlays/local` is a complete cell on any local cluster. `tools/cell_smoke.sh` deploys it to kind (pinned) and runs the Phase 0 exit flow through it. CI runs the same script. Production uses the same manifests with a different overlay and different dependency endpoints.
5. **Residency is a placement rule, not a provider choice.** A cell is placed where its data must live (India, the UAE, …). Any infrastructure in that country that meets the contracts above qualifies.
6. **Provider-specific infrastructure code is optional and replaceable.** Where a cell runs on a provider, its OpenTofu or Crossplane module lives under `deploy/infra/<provider>/`. It is an adapter that produces the contracts above and nothing more. The kernel and the manifests never reference it.

## Consequences
- The open decision that blocked the first cell is gone. A cell can be provisioned anywhere the contracts hold, starting with a laptop.
- CI proves the cell on Kubernetes in every run (the `cell` job) without any cloud account.
- Production readiness is judged by the same smoke flow against the production overlay. Promotion is a human decision after local testing passes.
- Cost and credits are compared per placement when production starts. They no longer shape the architecture.

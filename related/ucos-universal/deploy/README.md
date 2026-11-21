# Deployment

| Path | What it is | Checked in CI by |
|---|---|---|
| `local/` | Development stack (Postgres, Redpanda, Keycloak with a dev realm, Temporal and its UI), images pinned by digest; the kernel schema is applied by the kernel's migrator. `make -C deploy/local up` | `docker compose config`; the **devstack** job starts it and runs `tools/devstack_smoke.sh` |
| `k8s/base`, `k8s/overlays/{dev,staging,prod}` | Cell baseline: restricted Pod Security, default-deny networking, gVisor runtime class for third-party packs (ADR-025), tier priority classes, quotas | `kubectl kustomize` + kubeconform (strict, Kubernetes 1.33) |
| `k8s/apps/kernel` | The kernel on any Kubernetes: migration Job (PreSync hook), Deployment with readiness on a current schema, PDB, Service, port-only NetworkPolicy. Needs Secret `ucos-kernel-env` and ConfigMap `ucos-kernel-config` per environment | kubeconform; the **cell** job deploys it |
| `k8s/overlays/local`, `k8s/deps/local` | A complete cell on a local cluster, with in-cluster stand-ins for Postgres, the Kafka API and OIDC. `tools/cell_smoke.sh` creates a kind cluster, deploys it and runs the Phase 0 exit flow | the **cell** job runs `tools/cell_smoke.sh` |
| `k8s/argocd` | ApplicationSet that deploys each cell from this repository (ADR-024) | kubeconform |
| `../kernel/Dockerfile.kernel` | `ucos-kernel` image (context: repository root): kernel, CLI, the spec it reads and the migrations; static, non-root, from scratch | **cell** and **devstack** jobs build and run it |
| `../kernel/Dockerfile` | `ucos` image: static, non-root, from scratch | **container** job builds and smoke-tests it; tagged releases push it to GHCR, keyless-signed with cosign, with an SPDX SBOM and SLSA provenance attestation |

**Provider-agnostic (ADR-037).** Nothing here names a cloud provider. A cell needs only the contracts in [ADR-037](../docs/adr/ADR-037-primary-cloud-provider-for-the-first-cells.md): Kubernetes, PostgreSQL 16+, the Kafka API, OIDC, the S3 API and OpenTelemetry. Where a cell runs on a particular provider, an optional adapter module under `infra/<provider>/` produces those contracts. Order of work: local cluster (`tools/cell_smoke.sh`) → staging cell → production, each promoted only after the same smoke flow passes.

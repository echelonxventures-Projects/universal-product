#!/usr/bin/env bash
# Deploys a complete cell (deploy/k8s/overlays/local) to a local Kubernetes cluster and runs the Phase 0 exit flow
# through it: same image, manifests, migration job, probes, network policies and restricted Pod Security as a real
# cell, with in-cluster stand-ins for Postgres, the Kafka API and the identity provider (ADR-037: provider-agnostic).
#
#   tools/cell_smoke.sh            create a kind cluster (pinned kind), deploy, test, delete the cluster
#   KEEP=1 tools/cell_smoke.sh     keep the cluster afterwards (kubectl --context kind-ucos-cell …)
#   CONTEXT=<ctx> tools/cell_smoke.sh   use an existing cluster instead of kind (k3d, Docker Desktop, …); the
#                                  image ucos-kernel:local must be pullable or preloaded there
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KIND_VERSION=v0.33.0
CLUSTER=ucos-cell
cd "$ROOT"

if [[ -z "${CONTEXT:-}" ]]; then
  KIND="$ROOT/.tools/bin/kind"
  if [[ ! -x "$KIND" ]] || ! "$KIND" version | grep -q "$KIND_VERSION"; then
    (cd kernel && GOBIN="$ROOT/.tools/bin" GOTOOLCHAIN=auto go install "sigs.k8s.io/kind@$KIND_VERSION")
  fi
  "$KIND" get clusters 2>/dev/null | grep -qx "$CLUSTER" || "$KIND" create cluster --name "$CLUSTER" --wait 120s
  CONTEXT="kind-$CLUSTER"
  [[ "${KEEP:-0}" == "1" ]] || DELETE_CLUSTER=1
fi
PF=()
cleanup() {
  [[ ${#PF[@]} -gt 0 ]] && kill "${PF[@]}" 2>/dev/null
  [[ "${DELETE_CLUSTER:-0}" == "1" ]] && "$KIND" delete cluster --name "$CLUSTER" >/dev/null 2>&1
  return 0
}
trap cleanup EXIT
K=(kubectl --context "$CONTEXT")

echo "cell: build the kernel image and load it into the cluster"
docker build -q -f kernel/Dockerfile.kernel -t ucos-kernel:local . >/dev/null
[[ "$CONTEXT" == "kind-$CLUSTER" ]] && "$KIND" load docker-image ucos-kernel:local --name "$CLUSTER" >/dev/null

echo "cell: apply deploy/k8s/overlays/local"
"${K[@]}" create namespace ucos-deps --dry-run=client -o yaml | "${K[@]}" apply -f - >/dev/null
"${K[@]}" -n ucos-deps create configmap keycloak-realm --from-file=deploy/local/keycloak/ --dry-run=client -o yaml | "${K[@]}" apply -f - >/dev/null
"${K[@]}" -n ucos-kernel delete job ucos-kernel-migrate --ignore-not-found >/dev/null 2>&1 || true
"${K[@]}" apply -k deploy/k8s/overlays/local >/dev/null
"${K[@]}" -n ucos-kernel rollout restart deployment/ucos-kernel >/dev/null   # same tag, freshly loaded image
"${K[@]}" -n ucos-deps rollout status statefulset/postgres --timeout=600s
"${K[@]}" -n ucos-deps rollout status statefulset/redpanda --timeout=600s
"${K[@]}" -n ucos-deps rollout status deployment/keycloak --timeout=600s
"${K[@]}" -n ucos-kernel wait --for=condition=complete job/ucos-kernel-migrate --timeout=300s \
  || { "${K[@]}" -n ucos-kernel logs job/ucos-kernel-migrate --tail=50; exit 1; }
echo "cell: schema migrated by the migration job"
"${K[@]}" -n ucos-kernel rollout status deployment/ucos-kernel --timeout=180s \
  || { "${K[@]}" -n ucos-kernel describe pods; "${K[@]}" -n ucos-kernel logs deployment/ucos-kernel --tail=50; exit 1; }
echo "cell: kernel ready (2 replicas, restricted Pod Security, default-deny network policies)"

# Operators reach the API and the loopback-only control plane through port-forwards.
forward() { "${K[@]}" -n "$1" port-forward "$2" "$3" >/dev/null 2>&1 & PF+=($!); }
POD=$("${K[@]}" -n ucos-kernel get pods -l app.kubernetes.io/name=ucos-kernel -o jsonpath='{.items[0].metadata.name}')
forward ucos-kernel "pod/$POD" 18090:8080
forward ucos-kernel "pod/$POD" 18091:8081
forward ucos-deps svc/keycloak 18180:8080
for _ in $(seq 1 30); do curl -sf http://127.0.0.1:18090/api/v1/ready >/dev/null && curl -s -o /dev/null http://127.0.0.1:18180/ && break; sleep 1; done
curl -sf http://127.0.0.1:18090/api/v1/ready >/dev/null || { echo "kernel not ready through the port-forward"; exit 1; }

P0_API=http://127.0.0.1:18090/api/v1 P0_ADMIN=http://127.0.0.1:18091 P0_CELL=local-1
P0_TOKEN_URL=http://127.0.0.1:18180/realms/ucos-dev-sample/protocol/openid-connect/token
p0_rpk() { "${K[@]}" -n ucos-deps exec redpanda-0 -- rpk "$@"; }
p0_psql() { "${K[@]}" -n ucos-deps exec postgres-0 -- psql -U postgres -d ucos -tAc "$1"; }
p0_logs() { "${K[@]}" -n ucos-kernel logs -l app.kubernetes.io/name=ucos-kernel --tail=30 --prefix; }
source tools/p0_flow.sh
p0_flow

forward ucos-kernel "pod/$POD" 19090:9090
for _ in $(seq 1 20); do m=$(curl -sf http://127.0.0.1:19090/metrics || true); [[ -n "$m" ]] && break; sleep 1; done
grep -q 'ucos_bus_operations_total{kind="command",operation="sample:CreateNote",status="201"' <<<"$m" \
  || { echo "metrics missing the commands just run:"; head -40 <<<"$m"; exit 1; }
echo "cell: Prometheus metrics exposed on :9090"
echo "cell smoke: passed"

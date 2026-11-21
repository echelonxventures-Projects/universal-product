#!/usr/bin/env bash
# Start deploy/local/compose.yaml and prove each service works. Used by the CI "devstack" job; runs locally
# with Docker. Tears everything down afterwards.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${UCOS_PG_PORT:=5433}" "${UCOS_KAFKA_PORT:=19092}" "${UCOS_KEYCLOAK_PORT:=8180}" "${UCOS_TEMPORAL_PORT:=7233}" "${UCOS_TEMPORAL_UI_PORT:=8233}"
export UCOS_PG_PORT UCOS_KAFKA_PORT UCOS_KEYCLOAK_PORT UCOS_TEMPORAL_PORT UCOS_TEMPORAL_UI_PORT
C=(docker compose -f "$ROOT/deploy/local/compose.yaml" -p ucos-smoke)
trap '"${C[@]}" down -v >/dev/null 2>&1 || true' EXIT
"${C[@]}" up -d --wait --wait-timeout 300
"${C[@]}" run --rm --build migrate >/dev/null

echo "postgres: kernel schema applied by the kernel migrator with row-level security forced"
# Every tenant table has forced RLS (partitions are reached only through their parent).
want="kernel.audit_pending kernel.audit_records kernel.cmd_idempotency kernel.object_versions kernel.objects kernel.outbox kernel.triggers packs.sample_note"
got=$("${C[@]}" exec -T postgres psql -U postgres -d ucos -tAc \
  "SELECT string_agg(n.nspname || '.' || c.relname, ' ' ORDER BY n.nspname, c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relforcerowsecurity AND NOT c.relispartition")
[[ "$got" == "$want" ]] || { echo "forced-RLS tables differ"; echo " want: $want"; echo " got:  $got"; exit 1; }

echo "redpanda: cluster healthy and a topic round-trips"
"${C[@]}" exec -T redpanda rpk topic create ucos.local.sample.note.v1 -p 3 >/dev/null
echo '{"type":"sample.note.created"}' | "${C[@]}" exec -T redpanda rpk topic produce ucos.local.sample.note.v1 >/dev/null
msg=$("${C[@]}" exec -T redpanda rpk topic consume ucos.local.sample.note.v1 -o start -n 1)
grep -q 'sample.note.created' <<<"$msg" || { echo "message did not round-trip: $msg"; exit 1; }

echo "keycloak: dev realm imported and issues tokens"
for i in $(seq 1 100); do
  code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$UCOS_KEYCLOAK_PORT/realms/ucos-dev-sample/.well-known/openid-configuration || true)
  [[ "$code" == "200" ]] && break; sleep 3
done
[[ "$code" == "200" ]] || { echo "realm not served (HTTP $code)"; "${C[@]}" ps -a; "${C[@]}" logs --tail 60 keycloak; exit 1; }
token=$(curl -s -d grant_type=password -d client_id=ucos-gateway -d client_secret=dev-only-not-a-secret \
  -d username=asha -d password=asha-dev-password \
  http://localhost:$UCOS_KEYCLOAK_PORT/realms/ucos-dev-sample/protocol/openid-connect/token | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"][:10])')
[[ -n "$token" ]] || { echo "no access token issued"; exit 1; }

echo "temporal: server serving the default namespace (checked through the UI's API)"
for i in $(seq 1 80); do
  ns=$(curl -s http://localhost:$UCOS_TEMPORAL_UI_PORT/api/v1/namespaces || true)
  grep -q '"default"' <<<"$ns" && ok=1 && break
  sleep 3
done
[[ "${ok:-0}" == "1" ]] || { echo "temporal not serving"; "${C[@]}" logs --tail 30 temporal; exit 1; }
echo "devstack smoke: all services healthy"

# ---------------------------------------------------------------- Phase 0 flow through the running kernel
if command -v go >/dev/null 2>&1; then
  echo "kernel: build and start ucos-kernel against the stack"
  (cd "$ROOT/kernel" && go build -o "$ROOT/generated/ucos-kernel" ./cmd/ucos-kernel)
  ISS=http://localhost:$UCOS_KEYCLOAK_PORT/realms/ucos-dev-sample
  UCOS_DATABASE_URL="postgres://postgres:postgres@localhost:$UCOS_PG_PORT/ucos?sslmode=disable" \
  UCOS_REPO_ROOT="$ROOT" UCOS_CELL=dev-1 UCOS_HTTP_ADDR=127.0.0.1:18080 UCOS_KAFKA_BROKERS=localhost:$UCOS_KAFKA_PORT \
  UCOS_SIGNING_SEED=$(printf '%064d' 0) UCOS_ADMIN_ADDR=127.0.0.1:18081 UCOS_ADMIN_TOKEN=dev-only-operator-token \
  UCOS_TENANTS="[{\"issuer\":\"$ISS\",\"jwksUrl\":\"$ISS/protocol/openid-connect/certs\",\"tenant\":\"ucos:tenant:sample\",\"locale\":\"en\",\"currency\":\"INR\",\"tz\":\"Asia/Kolkata\",\"reality\":\"simulated\",\"jurisdiction\":\"ucos:jur:IN\"}]" \
    "$ROOT/generated/ucos-kernel" > "$ROOT/generated/ucos-kernel.log" 2>&1 &
  KPID=$!
  trap 'kill $KPID 2>/dev/null || true; "${C[@]}" down -v >/dev/null 2>&1 || true' EXIT
  for i in $(seq 1 30); do curl -sf http://127.0.0.1:18080/api/v1/health >/dev/null && break; sleep 1; done
  curl -sf http://127.0.0.1:18080/api/v1/health >/dev/null || { cat "$ROOT/generated/ucos-kernel.log"; exit 1; }

  P0_API=http://127.0.0.1:18080/api/v1 P0_ADMIN=http://127.0.0.1:18081 P0_TOKEN_URL="$ISS/protocol/openid-connect/token" P0_CELL=dev-1
  p0_rpk() { "${C[@]}" exec -T redpanda rpk "$@"; }
  p0_psql() { "${C[@]}" exec -T postgres psql -U postgres -d ucos -tAc "$1"; }
  p0_logs() { tail -50 "$ROOT/generated/ucos-kernel.log"; }
  source "$ROOT/tools/p0_flow.sh"
  p0_flow
fi

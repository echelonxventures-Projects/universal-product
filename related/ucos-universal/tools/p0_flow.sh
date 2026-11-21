# Phase 0 exit flow against a running kernel, wherever it runs (Docker Compose or any Kubernetes).
# Sourced by tools/devstack_smoke.sh and tools/cell_smoke.sh. The caller sets:
#   P0_API (…/api/v1), P0_ADMIN (control plane base URL), P0_TOKEN_URL (OIDC token endpoint), P0_CELL
# and defines: p0_rpk <args…> (runs rpk next to the broker), p0_psql <sql> (prints one value), p0_logs (kernel logs).
# Flow: refused before activation -> compose, certify, decide, activate -> create and publish over HTTP with a
# real OIDC token -> events on the Kafka API -> audit chain verifies.

p0_flow() {
  local root; root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  local token out code body note evs n broken
  token=$(curl -s -d grant_type=password -d client_id=ucos-gateway -d client_secret=dev-only-not-a-secret \
    -d username=asha -d password=asha-dev-password "$P0_TOKEN_URL" | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])') \
    || { echo "no token from $P0_TOKEN_URL"; return 1; }
  p0_api() {
    local args=(-s -w '\n%{http_code}' -X "$1" "$P0_API$2" -H "Authorization: Bearer $token" -H 'Content-Type: application/json')
    [[ -n "${3:-}" ]] && args+=(-H "Idempotency-Key: $3")
    [[ -n "${4:-}" ]] && args+=(-d "$4")
    curl "${args[@]}"
  }
  out=$(p0_api POST /sample/notes "p0-early-$RANDOM$RANDOM" '{"title":{"en":"too early"}}'); code=${out##*$'\n'}
  if [[ "$code" == "403" && "$out" == *ACTIVATION_DENIED* ]]; then
    echo "kernel: commands refused before the tenant's blueprint is activated"
  elif [[ "$code" != "201" ]]; then
    echo "unexpected answer before activation: $out"; p0_logs; return 1
  fi

  # Compose -> certify -> activate through the operator-only control plane (A-78).
  P0_ADMIN="$P0_ADMIN" P0_CELL="$P0_CELL" python3 - "$root" "$(git -C "$root" rev-parse HEAD 2>/dev/null || printf '%040d' 0)" <<'PY' || { p0_logs; return 1; }
import json, os, sys, urllib.request, urllib.error, datetime
root, commit = sys.argv[1], sys.argv[2]
def post(path, body):
    req = urllib.request.Request(os.environ['P0_ADMIN'] + '/control/v1/' + path, json.dumps(body).encode(), method='POST',
                                 headers={'Authorization': 'Bearer dev-only-operator-token', 'Content-Type': 'application/json'})
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        sys.exit(f'control plane {path}: {e.code} {e.read().decode()}')
tenant = 'ucos:tenant:sample'
snap = post('snapshots', {'gitCommit': commit})['id']
pd = open(f'{root}/spec/composition/golden/sample-p0.pd.yaml').read()
bp = post('blueprints', {'tenant': tenant, 'snapshot': snap, 'pd': pd})
assert not bp['gaps'], bp['gaps']
first = post('certifications', {'blueprint': bp['id'], 'profile': 'blueprint'})
assert not first['passed']
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
ev = [{'gate': r['gate'], 'ref': 'p0-flow#' + r['gate'], 'collectedAt': now} for r in first['results'] if r['result'] == 'fail']
cert = post('certifications', {'blueprint': bp['id'], 'profile': 'blueprint', 'evidence': ev})
assert cert['passed'], cert['results']
dec = 'ucos:decision:p0-' + bp['id'][-12:] + '-' + now
post('decisions', {'id': dec, 'authority': 'ucos:authority:release', 'subject': bp['id'], 'decision': 'approve-activation',
                   'requestedBy': 'ucos:identity:asha', 'approvedBy': ['ucos:identity:ravi'], 'rationale': 'Phase 0 flow'})
post('activations', {'tenant': tenant, 'cell': os.environ['P0_CELL'], 'blueprint': bp['id'], 'decision': dec, 'certification': cert['id']})
print(f'kernel: blueprint {bp["id"]} composed, certified ({cert["id"]}) and activated')
PY
  sleep 3 # activation answers are cached for 2 s

  out=$(p0_api POST /sample/notes "p0-create-$RANDOM$RANDOM" '{"title":{"en":"Phase 0 exit"}}'); code=${out##*$'\n'}; body=${out%$'\n'*}
  [[ "$code" == "201" ]] || { echo "create failed: $code $body"; p0_logs; return 1; }
  note=$(python3 -c 'import sys,json;print(json.loads(sys.argv[1])["id"])' "$body")
  out=$(p0_api POST "/sample/notes/$note:publish" "p0-publish-$RANDOM$RANDOM" '{}'); code=${out##*$'\n'}
  [[ "$code" == "200" ]] || { echo "publish failed: $out"; return 1; }
  echo "kernel: note $note created and published over HTTP with an OIDC token"

  for _ in $(seq 1 30); do
    evs=$(p0_rpk topic consume "ucos.$P0_CELL.sample.note.v1" -o start -n 2 2>/dev/null || true)
    grep -q 'sample.note.published' <<<"$evs" && break; sleep 1
  done
  grep -q 'sample.note.created' <<<"$evs" && grep -q 'sample.note.published' <<<"$evs" || { echo "events missing: $evs"; p0_logs; return 1; }
  echo "kernel: events reached the Kafka API through the outbox relay"

  for _ in $(seq 1 30); do
    n=$(p0_psql "SELECT count(*) FROM kernel.audit_records WHERE tenant_id = 'ucos:tenant:sample'")
    [[ "$n" -ge 2 ]] && break; sleep 1
  done
  broken=$(p0_psql "SELECT coalesce(kernel.audit_verify('ucos:tenant:sample', (now() AT TIME ZONE 'UTC')::date)::text, 'intact')")
  [[ "$n" -ge 2 && "$broken" == "intact" ]] || { echo "audit: $n records, verify=$broken"; return 1; }
  echo "kernel: audit records sealed into a chain that verifies"
  echo "kernel: Phase 0 flow passed end to end"
}

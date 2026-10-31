#!/usr/bin/env bash
# The Master's checks, as CI runs them on every pull request (prepared for the sole writer; not installed).
# usage: ci-check.sh <master dir> <repository root>
# Exit non-zero on the first failure. Readiness is computed and written as a report; it does not fail the pull request,
# because a NO-GO verdict is expected until release.
set -euo pipefail
M="$(cd "$1" && pwd)"; R="$(cd "$2" && pwd)"
cd "$M"
eval "$(python3 -I -c "import json;g=json.load(open('gate.json'));[print('%s=%s'%(k,repr(v))) for k,v in g.items() if isinstance(v,str)]")"
echo "== 1. the committed Master equals a fresh generation"
tmp="$(mktemp -d)"; python3 -I build.py "$src2" "$src3" "$tmp" >/dev/null
cmp "$tmp/LXM-MASTER.md" out/LXM-MASTER.md && cmp "$tmp/LXM-RECONCILIATION.md" out/LXM-RECONCILIATION.md
echo "== 1b. canonical state equals the last gate outcome (no direct edits), log chain intact"
python3 -I -B -c "import sys;sys.dont_write_bytecode=True;sys.path.insert(0,'.');import assimilate as A;s=A.state_matches_log('.');c=A.verify_chain('.');print(s[1]);print(c[1]);sys.exit(0 if s[0] and c[0] else 1)"
echo "== 2. Master invariants"
python3 -I validate.py out/LXM-MASTER.md out/LXM-RECONCILIATION.md "$src2" "$src3" "$prev_matrix" "$src2_sha" "$src3_sha" | tail -1
echo "== 2b. no agent, tool, person or host named outside its registry (LXM-REQ-000239)"
python3 -I -B agnostic.py "$M"
echo "== 2c. hard-coding in the Master's own tooling (ratchet: only goes down; LXM-REQ-000240)"
python3 -I -B tooling_literals.py "$M" --baseline tooling_baseline.json
echo "== 3. tool fixtures"
for t in test_assimilate test_config_adapter test_code_adapter test_readiness test_knowledge test_agnostic test_tooling_literals; do
  python3 -I -B "$t.py" "$M" | tail -1
done
echo "== 3b. gate accuracy (ratchet: errors only go down)"
python3 -I -B gate_accuracy.py "$M" --max-errors 2 | tail -1
echo "== 3c. every source clause still expressed; small-file shards rebuild the Master"
python3 -I -B revalidate.py "$M" | head -1
python3 -I -B shard.py prove "$M"
echo "== 4. configuration conformance (ratchet: findings only go down)"
python3 -I -B config_adapter.py "$R" --baseline config_baseline.json | tail -1
echo "== 5. code conformance and traceability (ratchet), clean tree"
python3 -I -B code_adapter.py "$R" --trace trace.txt --baseline code_baseline.json | tail -1
python3 -I -B code_adapter.py "$R" --git-clean | grep -q "working tree clean" || { echo "the working tree changed during CI"; exit 1; }
echo "== all Master checks passed"

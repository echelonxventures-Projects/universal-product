#!/usr/bin/env bash
#
# UCOS Ω∞ — Repository Operations Automation (EPIC-PLAT-003, Terminal T5).
#
#   ./repo-ops.sh                 complete repository operational verification
#   ./repo-ops.sh --resume        resume, skipping stages already passed (checkpoint)
#   ./repo-ops.sh --json          also emit the machine-readable report on stdout
#
# THE one command that performs complete repository operational verification using the
# existing canonical engines. Like ./verify.sh, a brand-new terminal can run this with
# NO manual `source .../activate`: it self-heals the canonical venv (correct Python
# series + pinned toolchain), then drives the configuration-driven pipeline through the
# venv interpreter by absolute path.
#
# The pipeline is declared in $UCOS_REPO_OPS_CONFIG (default: repo-operations.json).
# Every stage delegates to existing infrastructure — verify.sh / doctor.sh, the EC-1
# Acceptance / Validation / Certification engines, the frozen-corpus guard, and the
# canonical coverage report. No parallel tooling is created.

set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=scripts/ucos-env.sh
source "scripts/ucos-env.sh"

# --- The declared re-entrancy guard (UCOS-RFP-001, CYC-RECURSE) --------------------
# THIS IS AN AGGREGATE, AND AN AGGREGATE MUST EXCLUDE ITSELF FROM ITS OWN PIPELINE.
# Every stage below delegates to existing infrastructure -- verify.sh among them -- and
# verify.sh is a DECLARED STAGE of the fixed-point pipeline. Running this command from
# inside that pipeline therefore re-executes a declared producer through an undeclared
# path, which is exactly the recursive-generator topology RFP-6 forbids.
#
# Measured, not hypothetical: UCOS-RFP-001 reported this script as CYC-PRODUCER, writing
# 00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json -- a path STAGE-NUCLEUS
# already owns -- and counted it in undeclared_producers, closing CLO-07 and CLO-09.
#
# Refusing here rather than declaring a stage is the correct remedy: the bytes are not
# authored here, they are authored by the declared producer this script invokes. Declaring
# it as a stage would put two stages in one write zone and trip CLO-11/CLO-13 instead.
# The guard name is printed because rfp_engine.py::honours_guard requires BOTH a non-zero
# exit AND the declared guard name in the output before it will record self-exclusion.
if [ -n "${UCOS_RFP_ACTIVE:-}" ]; then
  echo "repo-ops.sh: refusing to run — UCOS_RFP_ACTIVE is set." >&2
  echo "  This is an aggregate that re-executes declared pipeline stages (verify.sh among" >&2
  echo "  them). Running it inside the fixed-point pipeline is a recursive generator." >&2
  exit 3
fi

CONFIG="${UCOS_REPO_OPS_CONFIG:-$UCOS_REPO/repo-operations.json}"
CHECKPOINT="${UCOS_REPO_OPS_CHECKPOINT:-$UCOS_REPO/.runtime/repository-operations-checkpoint.json}"

# --- Stage 0: ensure the canonical environment (no activation needed) ------------
ucos_ensure_venv
PY="$(ucos_venv_python)"

ucos_log "Repository operations: $CONFIG"
exec "$PY" -m platform.repository_operations.cli \
  --config "$CONFIG" \
  --repo-root "$UCOS_REPO" \
  --checkpoint "$CHECKPOINT" \
  "$@"

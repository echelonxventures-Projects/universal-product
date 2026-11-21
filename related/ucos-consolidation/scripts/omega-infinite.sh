#!/usr/bin/env bash
# UCOS Ω∞ Phase 1 — Universal Discovery Abstraction Layer, run read-only.
#
# WHY THIS WRAPPER EXISTS, and it is not convenience. `engine/omega_infinite/__main__.py` is a real
# execution surface, and Ω-3 measures reachability from orchestration texts rather than from
# intention. A CLI that no orchestration text invokes reads as unreachable code to
# `engine/universal_discovery/graph.py`, and the `unreachable_artifacts` ratchet would refuse it —
# correctly, because an entry point nothing invokes is indistinguishable from dead code.
#
# `scripts/` is one of the four declared orchestration plane kinds (graph.ORCHESTRATION_PLANES), so
# naming the module here places the Phase 1 CLI on the `python` plane. This file is deliberately NOT
# a verify.sh stage and NOT a CI job: the Phase 1 directive forbids modifying verify.sh execution
# order and CI workflow behaviour, so the surface is registered without being wired into any gate.
#
# READ-ONLY. Issues no certification, seals no governance artifact, writes no file.
# Exit 0 = all five Phase 1 criteria hold. 1 = a criterion failed. 2 = the layer could not run.

set -euo pipefail

cd "$(dirname "$0")/.."

exec python3 -m engine.omega_infinite "$@"

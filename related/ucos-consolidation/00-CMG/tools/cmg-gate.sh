#!/usr/bin/env bash
# CMG meta-constitutional gate (CMG-000001 Article L, Article LXVI.7).
#
# This is the SINGLE gate the meta layer is permitted (LXVI.7). It adds no
# pipeline, no scheduler, and no daemon; it invokes the validator and propagates
# its exit status.
#
# Fail-closed (L.4): exit 0 only when the validator reports zero findings.
#   exit 0  zero findings
#   exit 1  one or more findings
#   exit 2  fail-closed abort (unreadable, malformed, or ambiguous input)
#
# Usage: 00-CMG/tools/cmg-gate.sh [--emit <path>]

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

# Prefer the repository virtual environment when present; otherwise any python3.
# The validator uses the standard library only, so no package is required.
if [[ -x "${REPO_ROOT}/.ec1-venv/bin/python" ]]; then
  PY="${REPO_ROOT}/.ec1-venv/bin/python"
else
  PY="$(command -v python3)"
fi

exec "${PY}" "${SCRIPT_DIR}/cmg_validate.py" --repo-root "${REPO_ROOT}" "$@"

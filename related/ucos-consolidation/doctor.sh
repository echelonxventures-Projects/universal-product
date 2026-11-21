#!/usr/bin/env bash
#
# UCOS Ω∞ — Environment Doctor.
#
#   ./doctor.sh            diagnose the canonical verification environment (read-only)
#   ./doctor.sh --fix      diagnose, then self-heal the venv + pinned toolchain
#
# Reports Python / pytest / pytest-cov / coverage / ruff and checks each against the
# repository's canonical requirements (pyproject.toml [dev] + canonical Python series).
# Exits 0 only when the environment can reproduce repository verification; non-zero
# otherwise, naming the exact defect. Never requires an activated venv.

set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=scripts/ucos-env.sh
source "scripts/ucos-env.sh"

FIX=0
[ "${1:-}" = "--fix" ] && FIX=1

ucos_log "UCOS environment doctor"
printf '   repo:             %s\n' "$UCOS_REPO" >&2
printf '   canonical Python: %s (matches CI actions/setup-python)\n' "$UCOS_PYTHON_SERIES" >&2
printf '   venv:             %s\n' "$UCOS_VENV_DIR" >&2

# --- System context (helps explain "command not found" in a fresh shell) ---------
sys_py="$(command -v python3 || true)"
printf '   system python3:   %s%s\n' "${sys_py:-<none on PATH>}" \
  "$([ -n "$sys_py" ] && printf ' (%s)' "$(python3 --version 2>&1)")" >&2

if [ "$FIX" = "1" ]; then
  ucos_ensure_venv
fi

FAILURES=0
note_fail() { ucos_err "$*"; FAILURES=$((FAILURES + 1)); }

if ! ucos_venv_present; then
  note_fail "venv not present at $UCOS_VENV_DIR — run ./bootstrap.sh (or ./doctor.sh --fix)."
  ucos_err "Doctor: ENVIRONMENT NOT READY ($FAILURES issue(s))."
  exit 1
fi

PY="$(ucos_venv_python)"
venv_series="$(ucos_venv_series || echo '?')"

# --- Version report + validation --------------------------------------------------
# Compares the actually-installed dev toolchain to the pinned expectations.
printf '\n%s\n' "----------------------------------------------------------------" >&2
printf '%-14s %-12s %-12s %s\n' "COMPONENT" "REQUIRED" "INSTALLED" "STATUS" >&2
printf '%s\n' "----------------------------------------------------------------" >&2

report_row() { printf '%-14s %-12s %-12s %s\n' "$1" "$2" "$3" "$4" >&2; }

# Python series
if [ "$venv_series" = "$UCOS_PYTHON_SERIES" ]; then
  report_row "python" "$UCOS_PYTHON_SERIES" "$venv_series" "${_UC_G}OK${_UC_0}"
else
  report_row "python" "$UCOS_PYTHON_SERIES" "$venv_series" "${_UC_R}DRIFT${_UC_0}"
  note_fail "venv Python $venv_series != canonical $UCOS_PYTHON_SERIES (run ./doctor.sh --fix)."
fi

# Pinned dev tools (single source of truth: pyproject [dev])
dist_name() { case "$1" in pytest_cov) echo "pytest-cov";; *) echo "${1//_/-}";; esac; }
while read -r name want; do
  [ -z "${name:-}" ] && continue
  pkg="$(dist_name "$name")"
  have="$("$PY" -c "from importlib import metadata; print(metadata.version('$pkg'))" 2>/dev/null || echo "-")"
  if [ "$have" = "-" ]; then
    report_row "$pkg" "$want" "<missing>" "${_UC_R}MISSING${_UC_0}"
    note_fail "$pkg is not installed in the venv (this is the '--cov unrecognized / command not found' cause)."
  elif [ "$have" = "$want" ]; then
    report_row "$pkg" "$want" "$have" "${_UC_G}OK${_UC_0}"
  else
    report_row "$pkg" "$want" "$have" "${_UC_R}DRIFT${_UC_0}"
    note_fail "$pkg $have != pinned $want (run ./doctor.sh --fix)."
  fi
done < <(ucos_expected_deps "$PY")
printf '%s\n\n' "----------------------------------------------------------------" >&2

# --- Identity (UEG-000001) --------------------------------------------------------
# Closes assessment finding F-7. Everything above this line compares VERSIONS against the
# pins, which is necessary and was never sufficient: it cannot tell whether the interpreter
# it just reported on is inside this repository, whether sys.prefix is actually the canonical
# venv, or whether a global pytest is shadowing the canonical one on PATH. Those are the
# three conditions F-2 and F-3 failed on, and a doctor that reports a healthy table while
# they are false is a doctor people stop believing.
#
# Read-only: no --gate, so the doctor's own exit status stays the doctor's determination and
# a non-blocking advisory never turns a healthy report into a failure.
if ! "$PY" -m engine.execution_environment.gate --command "./doctor.sh"; then
  note_fail "environment integrity checks refused (see the UEG-000001 report above)."
fi

if [ "$FAILURES" -eq 0 ]; then
  ucos_ok "Doctor: ENVIRONMENT READY — canonical verification is reproducible from this shell."
  exit 0
fi
ucos_err "Doctor: ENVIRONMENT NOT READY ($FAILURES issue(s)). Fix with ./doctor.sh --fix or ./bootstrap.sh."
exit 1

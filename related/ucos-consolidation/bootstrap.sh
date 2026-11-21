#!/usr/bin/env bash
#
# UCOS Ω∞ — Fresh-clone Bootstrap.
#
#   ./bootstrap.sh            create/repair the canonical venv + pinned toolchain, then
#                             validate it with the doctor
#   ./bootstrap.sh --verify   also run the full canonical verification afterwards
#
# This is the single documented workflow that turns a fresh `git clone` into a fully
# operational, verifiable checkout — no hidden knowledge, no manual activation:
#
#     git clone <repo> && cd <repo>
#     ./bootstrap.sh            # environment ready
#     ./verify.sh               # reproduce repository verification
#
# It only ever touches the disposable, .gitignored .ec1-venv; source, engine, and
# platform code are never modified.

set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=scripts/ucos-env.sh
source "scripts/ucos-env.sh"

DO_VERIFY=0
[ "${1:-}" = "--verify" ] && DO_VERIFY=1

ucos_log "Bootstrapping UCOS canonical environment"
ucos_ensure_venv

ucos_log "Validating environment (doctor)"
./doctor.sh

# UEG-000001. bootstrap is the ONLY entry point permitted to create and install, so it is
# also the one that must prove what it produced. The doctor above compares versions against
# the pins; this gate answers the questions the doctor never asked and that findings F-2 and
# F-3 actually failed on — is this interpreter inside THIS repository, is sys.prefix really
# the canonical venv, does pytest resolve here, do the required plugins IMPORT.
#
# --refresh, because the environment was just rewritten: the fingerprint cache must be
# rebuilt from a full scan rather than from a proxy that could still be describing the
# environment as it was five seconds ago.
ucos_log "Verifying environment integrity (UEG-000001)"
"$(ucos_venv_python)" -m engine.execution_environment.gate \
  --gate --refresh --evidence --command "./bootstrap.sh"

# THE COMMIT GATE IS PART OF THE ENVIRONMENT, NOT A LOCAL HABIT. `.git/hooks/` is not
# tracked, so until this ran the pre-commit gate existed only on machines whose operator
# had heard of scripts/install-hooks.sh. A clone therefore had no lint gate at all, and
# the RC-1 invariant ("verify.sh passes => pre-commit passes") held over an empty set.
# HEAD 3c1a2530 committed a file that `ruff format --check` refuses, which is what that
# gap looks like once. Installing here makes the gate a property of a bootstrapped
# checkout rather than of the person who made it.
ucos_log "Installing the canonical pre-commit hook"
./scripts/install-hooks.sh

if [ "$DO_VERIFY" = "1" ]; then
  ucos_log "Running canonical verification"
  exec ./verify.sh
fi

cat >&2 <<EOF

${_UC_G}Environment ready.${_UC_0} Next steps (no venv activation required):

  ./doctor.sh     # re-check environment health
  ./verify.sh     # lint + tests/coverage + governance enforcement
  make verify     # same, via make

EOF

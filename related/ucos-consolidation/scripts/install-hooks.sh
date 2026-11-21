#!/usr/bin/env bash
#
# UCOS Ω∞ — Git hook installer (opt-in local automation).
#
#   ./scripts/install-hooks.sh          install the canonical pre-commit hook
#   ./scripts/install-hooks.sh --uninstall  remove a hook previously installed here
#
# Installs a fast, additive pre-commit quality gate that reuses the SAME canonical
# environment as verify.sh — it sources scripts/ucos-env.sh and runs the pinned
# ruff (lint + format check) through the .ec1-venv interpreter by absolute path.
# No new tooling, no venv activation, no dependency on PATH.
#
# The hook is intentionally the *fast* subset (lint + format-check, no test run) so
# it does not slow every commit; run ./verify.sh for the full gate. Bypass a single
# commit with `git commit --no-verify`.
#
# This script only writes into .git/hooks (a local, untracked location); it never
# touches source, generated registers, or the certified corpus.

set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck source=scripts/ucos-env.sh
source "scripts/ucos-env.sh"

UNINSTALL=0
[ "${1:-}" = "--uninstall" ] && UNINSTALL=1

GIT_DIR="$(git -C "$UCOS_REPO" rev-parse --git-dir 2>/dev/null || true)"
[ -n "$GIT_DIR" ] || ucos_die "not a git repository: $UCOS_REPO"
case "$GIT_DIR" in /*) : ;; *) GIT_DIR="$UCOS_REPO/$GIT_DIR" ;; esac
HOOK_DIR="$GIT_DIR/hooks"
HOOK="$HOOK_DIR/pre-commit"

_MARK="# UCOS-MANAGED-HOOK"

if [ "$UNINSTALL" = "1" ]; then
  if [ -f "$HOOK" ] && grep -q "$_MARK" "$HOOK" 2>/dev/null; then
    rm -f "$HOOK"
    ucos_ok "Removed UCOS pre-commit hook -> $HOOK"
  else
    ucos_warn "No UCOS-managed pre-commit hook found at $HOOK (nothing to do)."
  fi
  exit 0
fi

mkdir -p "$HOOK_DIR"

# Refuse to clobber a foreign, hand-authored hook.
if [ -f "$HOOK" ] && ! grep -q "$_MARK" "$HOOK" 2>/dev/null; then
  ucos_die "A non-UCOS pre-commit hook already exists at $HOOK; refusing to overwrite. Back it up or remove it first."
fi

# MERGE DRIVERS — the other half of per-clone setup, and it belongs here rather than in
# register.sh: this script already owns what a clone must configure, and register.sh writes
# a DIFFERENT pre-commit hook, so putting git-config work there made configuring drivers
# clobber the ruff gate this installer manages.
#
# `.gitattributes` names a driver per declared merge class, and a named driver is INERT
# without `merge.<name>.driver` in this clone's own config — git falls back to a default text
# merge and says nothing. A textual merge of a DERIVED register writes a document neither
# producer would emit; a textual merge of the identity ledger can resolve a collision by
# picking a side, which UCKP-ART-05 forbids outright. Both failures are silent.
#
# Reversible: git config --unset-all merge.ucos-regenerate.driver
_repo_root="$(git rev-parse --show-toplevel)"
git config merge.ucos-regenerate.driver \
  "\"$_repo_root/00-BOOK/tools/merge-regenerate.sh\" %O %A %B %P"
git config merge.ucos-regenerate.name \
  'UCOS regenerate: resolve to one side, then regenerate (register.sh --guard refuses a stale result)'
git config merge.ucos-union-ledger.driver \
  "python3 \"$_repo_root/00-BOOK/tools/merge-union-ledger.py\" %O %A %B %P"
git config merge.ucos-union-ledger.name \
  'UCOS union ledger: union by key, REFUSE on a divergent value (identity collision, ART-05)'
ucos_ok "Configured merge drivers: ucos-regenerate, ucos-union-ledger"

cat > "$HOOK" <<'HOOK_EOF'
#!/usr/bin/env bash
# UCOS-MANAGED-HOOK — installed by scripts/install-hooks.sh. Do not edit by hand;
# re-run the installer to update. Fast additive gate: ruff lint + format check and the
# Universal ID gate, via the canonical .ec1-venv (no activation).
# Bypass with: git commit --no-verify
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
cd "$repo"
# shellcheck source=scripts/ucos-env.sh
source "scripts/ucos-env.sh"
ucos_ensure_venv >/dev/null || { ucos_err "pre-commit: environment not ready — run ./bootstrap.sh"; exit 1; }
ucos_log "pre-commit: ruff lint + format check (engine + platform)"
# SINGLE SOURCE OF TRUTH: the identical gate verify.sh Stage 1 runs (ucos_ruff_gate in
# scripts/ucos-env.sh). No duplicated verification logic — verify.sh passes => this passes.
ucos_ruff_gate
# NOTHING ENTERS HISTORY WITHOUT AN IDENTITY. UGA-INV-01 already refuses an anonymous
# object, but only when the gate is run; this makes the condition unreachable at the point
# a file would become permanent. 153ms measured, so it costs the commit nothing.
ucos_log "pre-commit: every tracked object carries a Universal ID"
ucos_identity_gate
# REPORTS, NEVER REFUSES. A constitutional registry whose whitespace churn buries its
# substance is unreviewable rather than wrong, and how a change is presented is not a
# correctness property this hook may enforce. Named at the moment it can still be split.
ucos_reformat_report
ucos_ok "pre-commit: OK"
HOOK_EOF

chmod +x "$HOOK"
ucos_ok "Installed UCOS pre-commit hook -> $HOOK"
ucos_log "It runs: ruff lint + ruff format --check, then the Universal ID gate."
ucos_log "Bypass a single commit with: git commit --no-verify"
ucos_log "Uninstall with: ./scripts/install-hooks.sh --uninstall"

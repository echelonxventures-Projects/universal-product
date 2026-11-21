#!/usr/bin/env bash
#
# UCOS Ω∞ — REG-AUTO-001 Atomic Artifact Registration Transaction
#            + UMB-IMP-001 Automatic Registration & Enforcement Realization.
#
# Realizes the governing law "Artifact Creation = Artifact Registration". Running
# this script is the single, idempotent, all-or-nothing operation that brings the
# repository's synchronized state (Artifact Registry, Execution/Control-Tower,
# Digital Twin, Traceability/Knowledge-Graph, Dependencies, Navigation Portal)
# into agreement with the physical artifacts on disk — now bracketed by two
# enforcement gates (UMB-IMP-001) so no unregistered, unclassified, or invalid
# artifact can silently enter the corpus.
#
# The transaction is COMPLETE only if every phase succeeds. If any phase fails,
# the transaction is INCOMPLETE, newly-created artifacts remain UNREGISTERED, and
# any completion claim over them is INVALID (REG-AUTO-001 §7 Atomic Creation Law).
#
# Because ukb.py allocates IDs/pages append-only from an immutable ledger and both
# engines regenerate deterministically, this script is safe to run repeatedly.
#
# Usage:
#   00-BOOK/tools/register.sh                 # run the full registration transaction
#   00-BOOK/tools/register.sh --observe        # READ-ONLY: is registration state valid?
#   00-BOOK/tools/register.sh --guard         # transaction + drift gate (CI/pre-commit)
#   00-BOOK/tools/register.sh --strict         # also fail on OTHER/MISC-classified artifacts
#   00-BOOK/tools/register.sh --install-hooks  # install the opt-in git pre-commit gate
#
# --guard additionally fails (exit 3) if, after registration, the generated DATA/
# REGISTRIES/CONTROL-TOWER/PORTAL differ from what is committed — proving an
# artifact was created or changed without its registration being committed.
#
# TWO PLANES. --observe answers "is registration state valid?"; the transaction answers
# "perform governed registration". They are different questions and must be different
# commands, because the transaction MUTATES: Phase 1 is `ukb build --mint`, which
# allocates permanent Universal IDs. CORPUS_REGISTRATION is declared in
# 00-BOOK/DATA/mutation-governance-boundary.json as governed by REG-AUTO-001 — this
# script — and explicitly NOT by verify.sh.
#
# --observe does NOT regenerate derived views in order to compare them. Regeneration
# writes, and a verification path that writes is not a verification path. Detecting
# latent divergence between committed derived views and a fresh derivation is an
# evolution-plane concern, reached through `ukb.py build` in observation mode.
# See GOVERNED-EVOLUTION-STATE-DETERMINATION.md.
#
# Standard tooling only: bash + python3 + git.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOK_DIR="$(dirname "$HERE")"
REPO="$(dirname "$BOOK_DIR")"
PY="${PYTHON:-python3}"

GUARD=0
OBSERVE=0
STRICT=0
INSTALL_HOOKS=0
PERMIT="${UKB_PERMIT:-}"
for arg in "$@"; do
  case "$arg" in
    --observe) OBSERVE=1 ;;
    --guard) GUARD=1 ;;
    --strict) STRICT=1 ;;
    --install-hooks) INSTALL_HOOKS=1 ;;
    --permit=*) PERMIT="${arg#--permit=}" ;;
    *) echo "unknown option: $arg" >&2; exit 64 ;;
  esac
done
STRICT_FLAG=""; [ "$STRICT" = "1" ] && STRICT_FLAG="--strict"

# --- Allocation authorization (UCOS-LEDGER-AUTHORITY-001) -------------------------
# Phase 1 allocates PERMANENT identifiers, and `ledger_authority.commit` requires an
# authorization for that write. Passing none is not an omission any more: ukb.py asserts
# NO_ALLOCATION, which is VERIFIED against the measured pre-image, so a transaction that
# allocates nothing completes and a transaction that would allocate is REFUSED with the
# manifest a permit must be obtained for.
#
# THIS IS WHY THE FLAG EXISTS RATHER THAN A DEFAULT. Registration is idempotent in steady
# state, so the common case needs no permit at all. The uncommon case — new artifacts, real
# identifiers — is a governed decision, and the operator supplies the permit_id that a
# reviewer bound to that exact manifest, pre-image and HEAD:
#
#   00-BOOK/tools/ukb.py build --mint --plan          # read the manifest to be authorized
#   ...record a permit in 00-BOOK/DATA/allocation-permits.json...
#   00-BOOK/tools/register.sh --permit=<permit_id>
#
# A permit that does not match the manifest is refused by binding, so forwarding one here
# can approve exactly the allocation it was issued for and no other.
PERMIT_FLAG=""; [ -n "$PERMIT" ] && PERMIT_FLAG="--permit=$PERMIT"

cd "$REPO"

# --- Opt-in commit-time gate installer (UMB-IMP-001 gate 2 / REG-AUTO-001 §16.2) --
# Writes a git pre-commit hook that runs `register.sh --guard`. It never modifies
# git config; it only creates a hook file, and only if a git work tree exists.
if [ "$INSTALL_HOOKS" = "1" ]; then
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Not a git work tree — cannot install pre-commit hook." >&2; exit 1
  fi
  HOOKS_DIR="$(git rev-parse --git-path hooks)"
  mkdir -p "$HOOKS_DIR"
  HOOK="$HOOKS_DIR/pre-commit"
  cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
# UCOS Ω∞ REG-AUTO-001/UMB-IMP-001 commit-time enforcement gate (auto-installed).
# Blocks any commit whose synchronized registers are stale or whose artifacts are
# unregistered/invalid. Remove this file to uninstall.
exec "$(git rev-parse --show-toplevel)/00-BOOK/tools/register.sh" --guard
EOF
  chmod +x "$HOOK"
  echo "Installed commit-time enforcement gate: $HOOK"

  echo "(uninstall by deleting that file; git config was not modified.)"
  exit 0
fi

# Every driver `.gitattributes` names must be configured in THIS clone, or the class it
# declares is silently a default text merge. Reported, never repaired: configuring a driver
# is the operator's opt-in act (--install-hooks), so this states the condition and leaves
# the decision where it belongs.
if [ -f .gitattributes ]; then
  MISSING=""
  for drv in $(grep -oE 'merge=[a-z-]+' .gitattributes 2>/dev/null | sed 's/merge=//' | sort -u); do
    [ "$drv" = "union" ] && continue   # git's own built-in; needs no configuration
    git config --get "merge.$drv.driver" >/dev/null 2>&1 || MISSING="$MISSING $drv"
  done
  if [ -n "$MISSING" ]; then
    echo "WARNING: .gitattributes declares merge driver(s) this clone has not configured:$MISSING" >&2
    echo "  Those paths will fall back to a DEFAULT TEXT MERGE, silently." >&2
    echo "  Configure them: bash 00-BOOK/tools/register.sh --install-hooks" >&2
  fi
fi

# ==============================================================================
# VERIFICATION PLANE — --observe. Read-only. Runs BEFORE the lock, because it takes
# no lock: it mutates nothing, so it can never race the append-only ledger.
#
# Allowed here: read, compare, validate, verify, report. Forbidden: mint, allocate,
# write a register, regenerate a derived view, update lineage, migrate.
# ==============================================================================
if [ "$OBSERVE" = "1" ]; then
  echo "== REG-AUTO-001 Registration OBSERVATION (verification plane — READ-ONLY) =="
  echo "   repo: $REPO"
  echo "   this command allocates no identity and writes nothing under version control"
  RC=0

  echo "-- Observe 1/5: ukb enforce --pre (eligibility · validity · classification)"
  "$PY" "$HERE/ukb.py" enforce --pre $STRICT_FLAG || RC=4

  # REGISTRATION PARITY (UMB-IMP-001 gate 3). The PRE gate does NOT enforce this, by design and
  # correctly: it gates whether a NEW artifact is valid and classifiable BEFORE the transaction
  # registers it, so making "unregistered" a PRE violation would refuse every artifact the very
  # transaction exists to register — Phase 0 runs before Phase 1 mints.
  #
  # Parity is the POST gate's question, and until now POST ran in exactly one place: Phase 9 of
  # the write transaction. No verification plane invoked it. `verify.sh` runs `enforce --pre`,
  # `ucos-registration-gate.yml` runs `enforce --pre`, and this observation plane ran `--pre`
  # too, so "every tracked artifact is registered" was asserted by nothing that runs on its own.
  # MEASURED CONSEQUENCE: nine artifacts were committed unregistered — including
  # final_certification_report.md — while every gate reported PASS.
  #
  # Read-only, so it belongs here: POST reads registers and appends to the gitignored runtime
  # audit log. It allocates no identity and writes nothing under version control.
  echo "-- Observe 2/5: ukb enforce (POST — registration parity: every tracked artifact registered)"
  "$PY" "$HERE/ukb.py" enforce $STRICT_FLAG || RC=4

  echo "-- Observe 3/5: ukb validate (structural + schema invariants)"
  "$PY" "$HERE/ukb.py" validate || RC=2

  echo "-- Observe 4/5: ukbx validate (signal ledger integrity)"
  "$PY" "$HERE/ukbx.py" validate || RC=2

  echo "-- Observe 5/5: ukbx twin --check (digital-twin certification)"
  "$PY" "$HERE/ukbx.py" twin --check || RC=2

  # Uncommitted synchronized state. WORKTREE-vs-INDEX only: a staged register change is
  # the registration being committed alongside the artifact that caused it, which is what
  # REG-AUTO-001 §7 requires of an atomic transaction.
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    DIRTY="$(git status --porcelain -- \
        00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL 2>/dev/null \
        | awk '{ if (substr($0,1,2) == "??" || substr($0,2,1) != " ") print }' || true)"
    if [ -n "$DIRTY" ]; then
      echo "" >&2
      echo "REGISTRATION DRIFT DETECTED — synchronized state is uncommitted:" >&2
      echo "$DIRTY" >&2
      echo "Required action: stage the regenerated registers and recommit, or revert them" >&2
      echo "if they were produced unintentionally." >&2
      RC=3
    fi
  fi

  # Identity gaps. A gap is a REG-AUTO-001 L2 violation ("Created ≡ Registered"). A gap
  # a determination has located and scheduled is governed; an undetermined gap is not.
  # Governed gaps are reported, undetermined gaps block.
  GAPS="$("$PY" - <<'GAPPY'
import json, sys, os
sys.path.insert(0, os.path.join("00-BOOK", "tools"))
try:
    import ukb
    eligible = [rel for _a, rel in ukb._iter_files()]
    reg = {a["path"] for a in json.load(open("00-BOOK/DATA/artifacts.json"))["artifacts"]}
    print(len([p for p in eligible if p not in reg]))
except Exception:
    print("-1")
GAPPY
)"
  DET="UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md"
  if [ "$GAPS" != "0" ] && [ "$GAPS" != "-1" ]; then
    echo "" >&2
    echo "IDENTITY GAP DETECTED" >&2
    echo "  Eligible but absent from the corpus register : $GAPS" >&2
    echo "  Missing  : CORPUS_REGISTRATION (by_path allocation + artifacts.json entry)" >&2
    echo "  Note     : these artifacts already hold UGA identity — they are not anonymous" >&2
    if [ -f "$REPO/$DET" ]; then
      echo "  Governed by: $DET" >&2
      echo "  Required action: obtain REG-AUTO-001 authorization to reconcile the gap;" >&2
      echo "                   allocation is irreversible and is not a remediation" >&2
      echo "                   this read-only report may authorize" >&2
      echo "  Status   : REPORTED — the gap is determined, not silent" >&2
    else
      echo "  Determination: ABSENT" >&2
      echo "  Required action: create an Evolution Determination enumerating the" >&2
      echo "                   population, then obtain REG-AUTO-001 authorization" >&2
      echo "  Status   : BLOCKING — an undetermined gap is an ungoverned gap" >&2
      RC=5
    fi
  fi

  if [ "$RC" = "0" ]; then
    echo "OBSERVATION PASSED — registration state valid; nothing minted, nothing written."
  else
    echo "OBSERVATION FAILED (exit $RC) — see remediation above." >&2
  fi
  exit "$RC"
fi

# --- Re-entrancy guard --------------------------------------------------------
# Registration regenerates .md pages under PORTAL/REGISTRIES; if an authoring hook
# fires on those creates it would re-enter this script. A lock makes any nested
# invocation an immediate no-op, and also prevents concurrent runs from racing the
# append-only ledger. The lock lives under tools/ (outside the scan and the guard
# set) so it never appears as registration drift. Stale locks (>1h) are reclaimed.
LOCK="$HERE/.register.lock"
if [ -f "$LOCK" ]; then
  if [ "$(( $(date +%s) - $(cat "$LOCK" 2>/dev/null || echo 0) ))" -lt 3600 ]; then
    echo "register.sh already running (lock $LOCK) — nested/concurrent call is a no-op."
    exit 0
  fi
fi
date +%s > "$LOCK"
cleanup() { rm -f "$LOCK"; }
trap cleanup EXIT

echo "== REG-AUTO-001 Atomic Artifact Registration Transaction (UMB-IMP-001 gated) =="
echo "   repo: $REPO"

fail() { echo "TRANSACTION INCOMPLETE — $1" >&2; echo "Artifacts remain UNREGISTERED; completion claims INVALID." >&2; exit "${2:-1}"; }

# --- Gate 0 — Pre-registration enforcement (UMB-IMP-001) --------------------------
# Blocks the transaction if any NEWLY-created (unregistered) in-scope artifact is
# invalid or unclassified — so it cannot silently enter the corpus.
echo "-- Phase 0/10: ukb enforce --pre (pre-registration eligibility/validity/classification gate)"
"$PY" "$HERE/ukb.py" enforce --pre $STRICT_FLAG || fail "pre-registration enforcement gate failed" 4

# --- Phase 1 — Foundation registration (Artifact Registry + Execution Registry +
#               Control Tower baseline + Traceability/Knowledge Graph + Deps) -----
# --mint is EXPLICIT here and nowhere else. This is the REG-AUTO-001 transaction, the
# declared authority for CORPUS_REGISTRATION mutation, so it is the one place permitted
# to allocate permanent Universal IDs and page ranges. Without the flag `ukb build`
# observes. The flag is what makes minting a decision rather than a side effect.
echo "-- Phase 1/10: ukb build --mint (allocate identity; registry, pages, graph, control tower)"
"$PY" "$HERE/ukb.py" build --mint $PERMIT_FLAG || fail "ukb build failed" 1

# --- Phase 2 — State synchronization (UMB-IMP-004): discover connectors, detect
#               change since cursor, execute, verify, audit, recover. `--due`
#               respects each connector's cadence so the transaction is cheap in
#               steady state and idempotent (no new signals => no audit growth). -
echo "-- Phase 2/10: ukbx sync --due (live connectors + auto synchronization)"
"$PY" "$HERE/ukbx.py" sync --due      || fail "state synchronization failed" 1

# --- Phase 3 — Digital Twin synchronization + Control Tower dimension refresh -----
echo "-- Phase 3/10: ukbx twin (digital twin + automated control-tower dimensions)"
"$PY" "$HERE/ukbx.py" twin            || fail "ukbx twin failed" 1

# --- Phase 4 — Navigation portal regeneration (no dead ends) ----------------------
echo "-- Phase 4/10: ukbx portal (navigation portal)"
"$PY" "$HERE/ukbx.py" portal          || fail "ukbx portal failed" 1

# --- Phase 5 — Foundation validation (append-only, no dup ids/pages, ref integrity)
echo "-- Phase 5/10: ukb validate (structural + schema invariants)"
"$PY" "$HERE/ukb.py" validate         || fail "ukb validate failed" 2

# --- Phase 6 — Twin validation (signals, provenance, secret-free) -----------------
echo "-- Phase 6/10: ukbx validate (signal ledger integrity)"
"$PY" "$HERE/ukbx.py" validate        || fail "ukbx validate failed" 2

# --- Phase 7 — Digital-Twin Certification (UKB-014 hard checks) --------------------
echo "-- Phase 7/10: ukbx twin --check (digital-twin certification)"
"$PY" "$HERE/ukbx.py" twin --check    || fail "digital-twin certification failed" 2

# --- Phase 8 — Digital-Twin Certification Runtime (UMB-IMP-006): 9 integrity
#               domains (identity/registry/traceability/knowledge-graph/change/
#               version/lineage/synchronization/twin-intelligence) over the REAL
#               state; generates evidence + append-only audit trail + report; a
#               failed domain names the exact defect and fails the transaction. --
echo "-- Phase 8/10: ukbx certify (digital-twin certification runtime — 9 integrity domains)"
"$PY" "$HERE/ukbx.py" certify         || fail "digital-twin certification runtime failed" 2

# --- Gate 9 — Post-registration enforcement (UMB-IMP-001) -------------------------
# Asserts registration completeness (every eligible file is now registered) and
# validity; records the outcome in the append-only enforcement audit log.
echo "-- Phase 9/10: ukb enforce (post-registration completeness/parity gate + audit)"
"$PY" "$HERE/ukb.py" enforce $STRICT_FLAG || fail "post-registration enforcement gate failed" 4

echo "-- Phase 10/10: transaction sealed"
echo "TRANSACTION COMPLETE — every artifact on disk is registered, classified, validated, and synchronized."

# Release the re-entrancy lock before the (optional) drift gate so it can never be
# seen as an untracked file by any tree inspection.
rm -f "$LOCK"; trap - EXIT

# --- Optional drift gate (CI / pre-commit) ----------------------------------------
if [ "$GUARD" = "1" ]; then
  echo "-- Guard: checking committed synchronized state for drift"
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "   (not a git work tree; skipping drift gate)"; exit 0
  fi
  DIRTY="$(git status --porcelain -- \
      00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL 2>/dev/null || true)"
  if [ -n "$DIRTY" ]; then
    echo "REGISTRATION DRIFT DETECTED — synchronized state was not committed:" >&2
    echo "$DIRTY" >&2
    echo "An artifact was created or modified without committing its registration." >&2
    echo "Stage the regenerated DATA/REGISTRIES/CONTROL-TOWER/PORTAL and recommit." >&2
    exit 3
  fi
  echo "Guard PASSED — repository, registry, control tower, twin, and portal are in sync."
fi

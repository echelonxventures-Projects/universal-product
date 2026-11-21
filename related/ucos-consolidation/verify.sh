#!/usr/bin/env bash
#
# UCOS Ω∞ — Canonical Verification Entry Point.
#
#   ./verify.sh              DEFAULT = --change (commit validation)
#   ./verify.sh --fast       developer feedback: lint + impact-selected tests
#   ./verify.sh --change     commit validation: impact-selected tests + every governance gate
#   ./verify.sh --integration merge validation: whole suite under the floor + every gate
#   ./verify.sh --full       release certification: --integration + registration observation
#   ./verify.sh --failfast   stop at the first failing stage
#   ./verify.sh --serial     execute every stage sequentially (scheduling only; measures the same)
#   ./verify.sh --explain    print the plan and exit, executing nothing
#
# THE DEFAULT CHANGED, AND SAYING SO IS THE POINT. It was the full certification
# contract; it is now --change. That is not a weakening by stealth, because certification
# did not become weaker — it became EXPLICIT: .github/workflows/ec1-ci.yml invokes
# `./verify.sh --full` by name, and --full runs every stage the old default ran, under the
# same 90% floor, over the same whole suite. What changed is that the command a developer
# types dozens of times a day no longer costs a release certification. A 47-minute default
# is a default people route around, and a gate that is routed around is not a gate.
#
# MODES ARE NOT DECLARED HERE. 00-MASTER/UVI-000001/uvi-declaration.json holds the
# Verification Mode Constitution — what each mode claims, what it explicitly does not
# claim, which stages it admits, whether it may reuse evidence — and the Stage Registry
# that classifies every stage below by phase, plane and dependency. This script parses its
# own flags (a shell must, before it can run anything) and UVI-L-01 measures that the flags
# it accepts and the modes the constitution declares are the same set, in both directions.
#
# WHAT SELECTS THE TESTS. --fast and --change ask engine.verification_intelligence, which
# composes five substrates the repository already publishes — object identity, ownership,
# the dependency graph, the capability catalogue and the relationship graph — and FAILS
# WIDE: any change it cannot bound (a declaration, registry, schema, config, document,
# unregistered file, or a change to the selector itself) escalates to the whole suite WITH
# coverage. A selected run is only ever a subset when the subset is provably sufficient.
# Nothing anywhere names a test file; UVI-L-06 measures that.
#
# WHAT IS NOT NEGOTIABLE. Every gate below still exists, is still owned by the same
# instrument and is still evaluated by the same command. UVI-L-04 holds the pre-existing
# contract as a ratchet: every stage the certification default ran before this rework must
# still be a declared stage AND still admitted by every certification-eligible mode.
# UVI-L-05 refuses any mode that claims more than it measures, and UVI-L-08 measures that
# sharding and concurrency change no obligation — the shards union to exactly the
# selection, and the coverage floor is evaluated once, by the coverage tool, over combined
# data.
#
# THE one repository-standard command. A brand-new terminal can run this with NO
# manual `source .../activate` and NO tribal knowledge: Stage 0 verifies the canonical
# environment (UEG-000001) and every gate then runs through the venv interpreter by
# absolute path. Exits non-zero on any failure.
#
# IT VERIFIES THE ENVIRONMENT; IT DOES NOT REPAIR IT. This script used to self-heal the venv
# and that capability moved to ./bootstrap.sh, because a command that repairs its own subject
# cannot report on it — see the Stage 0 comment for the measured reason. A refusal here names
# what was expected, what was detected, and the one command that fixes it.

set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=scripts/ucos-env.sh
source "scripts/ucos-env.sh"

MODE="change"
FULL=0
FAILFAST=0
SERIAL=0
EXPLAIN=0
_mode_set=""
_set_mode() {
  if [ -n "$_mode_set" ] && [ "$_mode_set" != "$1" ]; then
    ucos_die "modes are mutually exclusive: --$_mode_set and --$1"
  fi
  _mode_set="$1"
  MODE="$1"
}
for arg in "$@"; do
  case "$arg" in
    --full) _set_mode full; FULL=1 ;;
    --integration) _set_mode integration ;;
    --change) _set_mode change ;;
    --fast) _set_mode fast ;;
    --failfast) FAILFAST=1 ;;
    --serial) SERIAL=1 ;;
    --explain) EXPLAIN=1 ;;
    -h|--help) sed -n '3,12p' "$0"; exit 0 ;;
    *) ucos_die "unknown option: $arg (see ./verify.sh --help)" ;;
  esac
done


# --- Stage 0: UEG-000001 environment integrity gate (OBSERVE ONLY) ---------------
# THIS SCRIPT NO LONGER REPAIRS ITS OWN ENVIRONMENT, AND SAYING SO IS THE POINT.
#
# It used to call ucos_ensure_venv here, which will `rm -rf` a virtual environment whose
# Python series drifted, rebuild it, and `pip install -e ".[dev]"` — over the network. That
# is a fine thing for a setup command to do and a disqualifying thing for a verification
# command to do: the run that was supposed to DETECT drift instead erased it and reported
# green, and the canonical gate acquired a dependency on an index being reachable, so an
# offline machine got an infrastructure failure reported as a verification failure.
#
# The repair capability did not disappear; it moved to the entry point that owns it.
# ./bootstrap.sh creates and installs, ./doctor.sh --fix repairs on explicit request, and
# this path observes and refuses. UEG-000001 declares that boundary
# (00-MASTER/UEG-000001/ueg-declaration.json, separation_of_powers) and
# engine/tests/unit/test_execution_environment.py measures it over the source of THIS FILE,
# so re-adding an install here fails the suite rather than passing unnoticed.
#
# WHAT THE GATE ACTUALLY CHECKS — eight declared conditions, seven of them blocking: that
# the running interpreter belongs to THIS repository (a root misresolution once built a venv
# in the parent directory and nothing noticed for sixteen days), that sys.prefix IS the
# canonical venv rather than merely near it, that the series matches the one CI pins, that
# pytest resolves inside this environment, that pytest_cov / coverage / jsonschema actually
# IMPORT rather than merely record a version, that every pin is installed with every
# executable its own RECORD declares, and that the configuration it measured against parsed
# to a non-empty expectation. The eighth reports global shadowing and undeclared
# executables without blocking.
#
# WHY IT IS NOT A run_stage. A run_stage executes THROUGH $PY, and this gate's entire job is
# to decide whether $PY may be trusted at all — it must precede the stage machinery, not sit
# inside it. It also precedes planning, so a faulted plan cannot be caused by a broken
# interpreter and then misread as an intelligence fault. Keeping it out of run_stage
# additionally leaves the fourteen stage literals below untouched, and those literals are a
# three-reader contract: this script executes them, UAKOS-CLOSURE-008/validation-record.json
# digests them, and .github/workflows/uisd-gate.yml re-derives them.
#
# COST: measured at 0.17s cold and 0.13s warm on the assessed machine, against a declared
# budget of 5s. It writes only .ucos/ (gitignored) and reaches no network.
ucos_env_gate "./verify.sh --${MODE}"
PY="$(ucos_venv_python)"

# --- Stage 0b: compute the plan, once, before anything executes -------------------
# The whole decision — which declared stages run, which are answered from evidence,
# which this mode does not admit, what the test selection is and how it is partitioned —
# is taken here and written to a plan file the stages below read. Deciding once up front
# rather than as the run proceeds is what makes a run reproducible and what makes the
# plan digest comparable between two machines.
#
# FAIL SAFE, IN THE ONLY DIRECTION THAT IS SAFE. If planning faults, the plan file is
# empty; uvi_action then answers RUN for every stage and the pytest stage falls back to
# the whole suite under the coverage floor. An intelligence layer that cannot compute a
# plan must never be able to cause LESS verification than there would have been without
# it.
# PORTABLE TEMPLATE, NOT `mktemp -t <prefix>`. BSD mktemp treats the -t argument as a
# prefix and appends randomness; GNU mktemp treats it as a template and refuses one with
# fewer than three trailing X's. So `-t ucos-verify-plan` worked on macOS and failed on
# every Linux runner with "mktemp: too few X's in template", which is why ./verify.sh --full
# never completed a single CI run. A full template path is accepted by both.
UVI_PLAN="$(mktemp "${TMPDIR:-/tmp}/ucos-verify-plan.XXXXXX")"
UVI_PLAN_OK=1
trap 'rm -f "$UVI_PLAN"; ucos_lease_release' EXIT

# --- The working-tree lease (AEOS G-04) ------------------------------------------
# TAKEN BEFORE ANYTHING MEASURES ANYTHING. Every stage below reports on the state of this
# tree, and a report about a tree another process is editing is a report about a state
# that never existed as a whole. Not hypothetical: §14 of final_certification_report.md
# records a second agent process advancing HEAD twice and committing another session's
# uncommitted edits, and a later integration run failed test_verification_purity because
# three tracked files moved under it. Neither was a defect in the verification plane;
# both were the absence of this line.
#
# It REFUSES a live holder and RECLAIMS a dead one. Reaping another process is not a
# verification command's business, and a lease that kills is a lease that loses work;
# a lease that obeys a crashed holder forever is the lockfile people learn to delete
# reflexively, which is how a lock stops meaning anything.
ucos_lease_acquire "$MODE"
if ! "$PY" -m engine.verification_intelligence plan --mode "$MODE" --tsv --out "$UVI_PLAN" 2>/dev/null; then
  ucos_warn "verification intelligence faulted; every stage will run and the whole suite will be verified under the coverage floor"
  : > "$UVI_PLAN"
  UVI_PLAN_OK=0
fi

if [ "$EXPLAIN" = "1" ]; then
  "$PY" -m engine.verification_intelligence report --mode "$MODE"
  exit 0
fi

# The plan is looked up by the SAME literal that is passed to run_stage — which is the
# same literal 00-MASTER/UAKOS-CLOSURE-008/validation-record.json digests and that
# .github/workflows/uisd-gate.yml re-derives. One string, one stage, three readers.
# An unrecognised label answers RUN: a stage the plan does not know about must execute,
# never be silently skipped.
uvi_field() {
  [ -s "$UVI_PLAN" ] || { printf '%s' "$2"; return 0; }
  awk -F'\t' -v want="$1" -v col="$3" -v fallback="$2" '
    $4 == want { print $col; found = 1; exit }
    END { if (!found) print fallback }
  ' "$UVI_PLAN"
}
uvi_action() { uvi_field "$1" RUN 1; }
uvi_phase()  { uvi_field "$1" MAIN 2; }
uvi_digest() { uvi_field "$1" - 3; }

# Concurrency is scheduling, never scope. Every stage the registry places in PREFLIGHT or
# MAIN is either READ_ONLY or writes exclusively to gitignored paths, which is what makes
# them safe to overlap; POST and EXTENDED read what MAIN produced and therefore do not.
# Draining is automatic on a phase transition, so the barrier cannot be forgotten when a
# stage is added.
UVI_PARALLEL=1
[ "$SERIAL" = "1" ] && UVI_PARALLEL=0

STAGES_RUN=()
STAGES_FAIL=()
STAGES_SECS=()
_BG_PIDS=()
_BG_LABELS=()
_BG_LOGS=()
_BG_STARTS=()
_BG_DIGESTS=()
_BG_PHASE=""
VERIFY_START=$SECONDS

_record_result() {
  local label="$1" rc="$2" secs="$3" digest="$4"
  STAGES_RUN+=("$label")
  STAGES_SECS+=("$secs")
  if [ "$rc" -ne 0 ]; then
    ucos_err "STAGE FAILED (exit $rc): ${label}"
    STAGES_FAIL+=("$label")
  else
    ucos_ok "STAGE PASSED: ${label}"
  fi
  # The evidence registry is a cache of results, so it records what happened either way:
  # storing only passes would make a failure look like an absent measurement next run.
  # A SHARDED RUN MINTS NO EVIDENCE, and this is the load-bearing line of cross-job
  # sharding rather than a precaution. Evidence is keyed by stage label and input digest,
  # and neither depends on how the run was scheduled — so a job that ran one shard of the
  # pytest stage and exited 0 would record PASS against the SAME key a whole-suite run
  # writes, for the stage label "pytest + coverage gate (--cov-fail-under=90)", having
  # evaluated no floor at all. A later --change or --fast run may reuse a stored PASS
  # (UVI-L-09 only keeps certification-eligible modes away from reuse), and would then
  # skip the coverage gate on the strength of a shard. The floor is evaluated once, by
  # `combine`, over every shard's data; until that has happened this run knows nothing
  # about the suite, and a run that knows nothing records nothing.
  if [ -n "${UVI_SHARD:-}" ]; then
    return 0
  fi
  if [ "$digest" != "-" ] && [ -n "$digest" ] && [ "$UVI_PLAN_OK" = "1" ]; then
    "$PY" -m engine.verification_intelligence record \
      --stage-label "$label" --digest "$digest" \
      --result "$([ "$rc" -eq 0 ] && echo PASS || echo FAIL)" >/dev/null 2>&1 || true
  fi
}

uvi_drain() {
  [ "${#_BG_PIDS[@]}" -eq 0 ] && { _BG_PHASE=""; return 0; }
  local i rc
  for i in "${!_BG_PIDS[@]}"; do
    set +e
    wait "${_BG_PIDS[$i]}"
    rc=$?
    set -e
    printf '\n%s\n' "----- ${_BG_LABELS[$i]} -----" >&2
    cat "${_BG_LOGS[$i]}" >&2 || true
    local secs
    secs="$(cat "${_BG_LOGS[$i]}.secs" 2>/dev/null || true)"
    [ -n "$secs" ] || secs="$((SECONDS - _BG_STARTS[$i]))"
    rm -f "${_BG_LOGS[$i]}" "${_BG_LOGS[$i]}.secs"
    _record_result "${_BG_LABELS[$i]}" "$rc" "$secs" "${_BG_DIGESTS[$i]}"
  done
  _BG_PIDS=(); _BG_LABELS=(); _BG_LOGS=(); _BG_STARTS=(); _BG_DIGESTS=()
  _BG_PHASE=""
  if [ "$FAILFAST" = "1" ] && [ "${#STAGES_FAIL[@]}" -gt 0 ]; then
    summarize_and_exit
  fi
  return 0
}

run_stage() {
  local label="$1"; shift
  local action phase digest
  action="$(uvi_action "$label")"
  phase="$(uvi_phase "$label")"
  digest="$(uvi_digest "$label")"

  case "$action" in
    SKIP)
      ucos_log "SKIP (--${MODE} does not admit this stage, and claims nothing from it): ${label}"
      return 0
      ;;
    REUSE)
      ucos_log "REUSE (identical input already passed): ${label}"
      STAGES_RUN+=("$label")
      STAGES_SECS+=("0")
      return 0
      ;;
  esac

  # A phase transition drains whatever is still running. POST reads what MAIN produced,
  # and MAIN reads what PREFLIGHT generated, so overlapping across a boundary would be
  # reading a half-written input.
  if [ -n "$_BG_PHASE" ] && [ "$_BG_PHASE" != "$phase" ]; then
    uvi_drain
  fi

  ucos_log "STAGE: ${label}"
  local _start=$SECONDS

  if [ "$UVI_PARALLEL" = "1" ] && { [ "$phase" = "PREFLIGHT" ] || [ "$phase" = "MAIN" ]; }; then
    # The subshell records its OWN elapsed time. Measuring from launch to reap instead
    # would report the time until the barrier got to it, not the time it took: every
    # read-only gate finishes in seconds and is reaped after the pytest stage, so the
    # first version of this summary reported eleven gates at 441s each. A summary that
    # misattributes 440 seconds to a gate that took one is worse than no summary.
    local log; log="$(mktemp "${TMPDIR:-/tmp}/ucos-verify-stage.XXXXXX")"
    ( cd "$UCOS_REPO"; _s=$SECONDS; "$@"; _rc=$?; printf '%s' "$((SECONDS - _s))" > "${log}.secs"; exit "$_rc" ) > "$log" 2>&1 &
    _BG_PIDS+=("$!")
    _BG_LABELS+=("$label")
    _BG_LOGS+=("$log")
    _BG_STARTS+=("$_start")
    _BG_DIGESTS+=("$digest")
    _BG_PHASE="$phase"
    return 0
  fi

  set +e
  ( cd "$UCOS_REPO" && "$@" )
  local rc=$?
  set -e
  _record_result "$label" "$rc" "$((SECONDS - _start))" "$digest"
  # Always succeed: a non-failfast failure is recorded in STAGES_FAIL and reported by the
  # final summary. Without this, run_stage would inherit the non-zero status of the
  # short-circuited failfast test and `set -e` would abort the run before the remaining
  # stages and the summary — the opposite of the documented contract.
  if [ "$FAILFAST" = "1" ] && [ "$rc" -ne 0 ]; then
    summarize_and_exit
  fi
  return 0
}

summarize_and_exit() {
  uvi_drain
  # THE SUBJECT IS RE-MEASURED BEFORE ANY VERDICT IS ANNOUNCED, on every exit path this
  # function serves — including the --failfast ones. The lease recorded HEAD and the
  # porcelain digest at acquisition; if either moved, every stage above measured a moving
  # target and no verdict below is attributable to a commit. A green run over a tree that
  # changed underneath it is precisely the false green this file exists to prevent, so
  # the answer is VOID rather than PASS or FAIL.
  if ! ucos_lease_verify; then
    ucos_err "VERIFICATION VOID — the subject changed while it was being measured."
    exit 1
  fi
  printf '\n%s\n' "================ VERIFICATION SUMMARY ================" >&2
  local i s dur
  for i in "${!STAGES_RUN[@]}"; do
    s="${STAGES_RUN[$i]}"
    dur="${STAGES_SECS[$i]:-0}"
    if printf '%s\n' "${STAGES_FAIL[@]:-}" | grep -qxF "$s"; then
      printf '  %sFAIL%s  %-58s %4ss\n' "$_UC_R" "$_UC_0" "$s" "$dur" >&2
    else
      printf '  %sPASS%s  %-58s %4ss\n' "$_UC_G" "$_UC_0" "$s" "$dur" >&2
    fi
  done
  printf '  %-66s %4ss\n' "TOTAL (wall clock)" "$((SECONDS - VERIFY_START))" >&2
  printf '%s\n' "=====================================================" >&2
  printf '  %s\n' "MODE: --${MODE}$([ "$UVI_PARALLEL" = "1" ] && echo " (stages overlapped where the registry declares them independent)")" >&2
  if [ "$MODE" = "fast" ] || [ "$MODE" = "change" ]; then
    printf '  %s\n' "This run is a DEVELOPER mode. Unless its selection escalated it did not evaluate" >&2
    printf '  %s\n' "the coverage floor, and it is not evidence of certification: run ./verify.sh --full." >&2
  fi
  if [ "${#STAGES_FAIL[@]}" -gt 0 ]; then
    ucos_err "VERIFICATION FAILED (${#STAGES_FAIL[@]} stage(s))."
    exit 1
  fi
  ucos_ok "VERIFICATION PASSED — every stage this mode admits is green."
  exit 0
}

# --- Stage 1: ruff quality gate (lint + format-check) — CD-01 / CD-04 ------------
# Invokes the SINGLE-SOURCE-OF-TRUTH gate (ucos_ruff_gate in scripts/ucos-env.sh) so
# this canonical path runs the IDENTICAL ruff gate as the pre-commit hook — closing the
# drift that let verify.sh pass while pre-commit's `ruff format --check` failed.
run_stage "ruff lint + format-check (engine + platform)" ucos_ruff_gate

# --- Stage 1b: prerequisite generation (P0-FINAL-CONVERGENCE-001) ----------------
# The tests below READ generated artifacts that `.gitignore` excludes on the stated
# grounds that they are "regenerated each run": /knowledge/, determinism-evidence/ and
# the UAKOS-CLOSURE-002 engine outputs. Nothing re-ran them. Generation appeared in NO
# stage of this script and in no part of register.sh, so the ignore authority asserted a
# regeneration that no entry point performed. Locally that was invisible because the
# artifacts persist from earlier manual runs; on a clean checkout they simply do not
# exist, and 51 tests that pass here failed in CI — measured on a fresh clone of HEAD:
# 50 failed + 3 errors, reduced to 2 by running exactly these five producers.
#
# This stage MUST precede the pytest stage: a prerequisite generated after the gate that
# consumes it is not a prerequisite. Every write lands on an ignored path, so the stage
# cannot dirty the working tree and cannot be seen as drift by the Registration Gate.
# The producers live in scripts/generate-prerequisites.sh so this path and the stdlib-only
# constitutional gate workflows share ONE definition rather than two that can drift apart.
run_stage "prerequisite generation (knowledge · determinism · closure 1-3)" \
  env PYTHON="$PY" bash scripts/generate-prerequisites.sh

# --- Stage 2: tests + coverage gate — CD-02 (pytest addopts drive --cov ≥ 90%) ---
# Running via the venv interpreter guarantees pytest-cov is present, so the --cov
# arguments in pyproject are always recognized.
#
# THE ARGV IS NOT CHOSEN HERE ANY MORE, AND THAT IS THE POINT. It used to be assembled
# by this block: a mode test, a call to the impact engine, a shell word-split of its
# stdout into a pytest command line. Selection, escalation, coverage policy and process
# topology were four decisions taken in bash, one of them by splitting a string on
# whitespace. They are now one decision, taken once, in Stage 0b, by an engine that is
# itself tested and measured under the coverage floor — and `run-tests` executes exactly
# the plan `--explain` printed, which is what makes the plan honest rather than a
# description of something else.
#
# What that engine does with this stage, per the constitution: --integration and --full
# run the whole suite under the floor and are the only certification-eligible paths;
# --fast and --change run the selection with --no-cov so they cannot become a second
# owner of the floor; and any selection that ESCALATES runs the whole suite WITH the
# floor, exactly as the certification path would have run it. Under every mode the
# selection is partitioned into shards that run concurrently, and under the floor their
# coverage data is combined so the floor is evaluated once, over the union, by the
# coverage tool itself.
#
# The STAGE LABEL is not mode-dependent and must not become so. There is exactly one
# `run_stage "pytest + coverage gate (--cov-fail-under=90)"` line in this file, because
# platform/tests/test_canonical_validation_evidence.py derives the verification contract
# and its sha256 digest from these literals — a per-mode label would make the contract
# depend on how the run was invoked, which is precisely what a contract must not do.
PYTEST_ARGV=(-m engine.verification_intelligence run-tests --mode "$MODE")
# Cross-job sharding: this run executes ONE shard of the plan and leaves its coverage data
# for the combine job. The mode is unchanged and the plan is still computed in full — the
# job re-derives the whole partition and re-proves that it unions to the selection before
# narrowing to its own shard — so this is the same measurement, taken one part at a time.
# The STAGE LABEL below is deliberately not varied by this; see the note above.
if [ -n "${UVI_SHARD:-}" ]; then
  PYTEST_ARGV+=(--shard "$UVI_SHARD" --coverage-out "${UVI_COVERAGE_OUT:?UVI_SHARD needs UVI_COVERAGE_OUT}")
  # A plain `[ ... ] && ...` here would be the last command of this branch, so an unset
  # digest would make the `if` compound exit 1 and `set -e` would abort the whole run.
  if [ -n "${UVI_PLAN_DIGEST:-}" ]; then
    PYTEST_ARGV+=(--plan-digest "$UVI_PLAN_DIGEST")
  fi
fi
if [ "$UVI_PLAN_OK" != "1" ]; then
  # No plan was produced, so there is no selection to trust. Run everything, under the
  # floor, exactly as the certification path would.
  PYTEST_ARGV=(-m pytest)
fi
run_stage "pytest + coverage gate (--cov-fail-under=90)" "$PY" "${PYTEST_ARGV[@]}"


# --- Stage 3a: UCOS-OMEGA-001 — governance derived from executable reality --------
# WHY THIS STAGE SITS HERE, immediately after the coverage gate. The gate above reports a
# percentage; this stage governs the SET that percentage is computed over, and it is the
# stage that computed it — the same derivation that fed pytest-cov its --cov targets runs
# again here and is checked for totality. Placing it after the coverage gate means the
# denominator is verified against the tree in the same run that measured against it.
#
# WHAT IT REFUSES, one condition per phase and each the negation of that phase's criterion:
#   Ω-1  a discovered artifact that no measurement, exemption or declaration accounts for
#   Ω-2  an artifact resolving to authority = NONE without a transient declaration
#   Ω-3  a relocation that changes a governance verdict — proved by moving the largest
#        root to a root that does not exist and requiring every verdict to be unchanged
#   Ω-4  a metric worse than this repository's own best with no written justification
#   Ω-5  an artifact carrying no disposition, or more than one
#
# READ-ONLY. Writing is `make omega-seal`, never this stage, so a certification run cannot
# advance the bounds it is being measured against.
run_stage "omega gate (discovery · authority · reachability · ratchets · disposition)" \
  "$PY" -m engine.universal_discovery


# --- Stage 4: governance enforcement (UMB-IMP-001 pre-registration gate) ---------
# Read-only eligibility/validity/classification gate (same gate CI runs first).
run_stage "governance enforce --pre" "$PY" 00-BOOK/tools/ukb.py enforce --pre

# --- Stage 5: registry structural validation (schema + referential integrity) -----
# Validates emitted DATA against JSON schemas and checks structural invariants.
# This gate was wired in by CRAP-001/CAEM-001 S-2 to close the silent-failure gap
# that let 539 schema violations pass undetected through all prior gates.
run_stage "registry validate (schema + integrity)" "$PY" 00-BOOK/tools/ukb.py validate

# --- Stage 6: meta-constitutional conformance gate (CMG-000001 Article L) ---------
# The meta layer is permitted EXACTLY ONE automated realization, and Article LXVI.7
# requires it be "invoked through the corpus's existing verification entry point" —
# this stage IS that invocation. It adds no second pipeline, scheduler, or daemon
# (LXVI.7) and no second criteria set (L.2): the criteria are CMG-INV-01..12 and
# nothing else, evaluated by the validator Article L.3 names as its realization.
#
# Before this stage existed, meta-constitutional conformance was measurable but only
# on demand, so a corpus could drift into parallel authority, orphan governance, a
# dangling superior or an illegal lifecycle record and stay green through every gate.
# XLIX.7 is explicit that an unchecked obligation is of UNKNOWN compliance and SHALL
# NOT be presumed satisfied; binding the gate here converts the twelve invariants from
# on-demand measurement into continuous enforcement.
#
# Read-only and fail-closed (L.4): the validator writes nothing and reports a finding
# rather than a pass on any unparseable, missing or ambiguous input. It is deterministic
# and hermetic (L.5), so it cannot flake a verification run.
run_stage "meta-constitutional conformance (CMG-INV-01..12)" bash 00-CMG/tools/cmg-gate.sh

# --- Stage 6b: universal object governance gate (UCOS-UGA-001 UGA-INV-01..10) -----
# The gates above enforce the DOCUMENT corpus. config.INCLUDE_EXTENSIONS is
# (.md, .txt, .docx, .json), so the registration boundary never saw a thing that
# EXECUTES: at the time this stage was added, 4510 version-controlled objects —
# every engine, every test, every workflow, and all 29 producers named by the
# generated-artifact registry — carried no universal identity, no owner and no
# lifecycle. The corpus governed 1233 artifacts by naming producers that were
# themselves anonymous.
#
# This stage closes that leg. It asserts the ten universal invariants over the
# WHOLE version-controlled boundary, so a new engine, test or config file can no
# longer enter the repository unidentified, unowned, unregistered or unaudited.
#
# Read-only and fail-closed: `gate` mints nothing and writes nothing (`run` does
# that), and it reports a violation rather than a pass on any input it cannot
# measure. Deterministic and hermetic — no clock, no network — so it cannot flake.
#
# All ten invariants block. UGA-INV-06 (bootstrap path for every generated input)
# was briefly carried as a non-blocking DECLARED-OPEN condition while `realization/`
# had a declared producer but no bootstrap invocation. That gap is now discharged:
# the producer was made deterministic — its manifest sealed a per-run `action`, so it
# had no fixed point — and added to scripts/generate-prerequisites.sh. The registry's
# `bootstrap_gaps` is empty and the exemption is gone with the condition it covered.
run_stage "universal object governance (UGA-INV-01..10)" \
  "$PY" 00-MASTER/UCOS-UGA-001/uga_engine.py gate

# --- Stage 6b-ctx: universal context closure gate (UCOS-UCTX-001, every invariant) -
# The stage above governs OBJECT identity. This one governs CONTEXT authority, and it
# exists because those are different questions with different failure modes.
#
# WHAT WAS MEASURED BEFORE IT EXISTED, at fce3cb9b: `.claude/` held zero tracked files,
# `.cursor/` did not exist, all seven `.kiro/` hooks were frozen, and no CLAUDE.md,
# steering file or rules directory existed anywhere in the tree. No agent surface
# claimed authority — and none received any context either. `agents` was the single
# knowledge domain of twelve with NO declared authority.
#
# An ownerless context domain is not a safe steady state. It is the state in which the
# first hand-written agent instruction file becomes repository truth — on one branch,
# under no authority, listed in no register — and every later agent inherits it. Under
# UCKP-ART-03 that file is void the moment it restates a rule the constitution already
# holds, but "void" is a property nothing was measuring.
#
# This stage measures it. Every agent surface is now a GENERATED projection of
# 00-BOOK/DATA/context-authority.json, so a hand edit is drift (INV-CTX-07) rather than
# a new rule, and a branch or worktree carrying context the declaration does not produce
# is a refusal (INV-CTX-08 / INV-CTX-09) rather than a divergence nobody noticed.
#
# Read-only and fail-closed. The gate is a SEPARATE module from the generator on
# purpose: it reads `git status --porcelain` and the ref list, and a producer that reads
# the working tree is an undeclared observer under UGA OBS-INV-12. The generator writes
# and never observes; this gate observes and never writes.
run_stage "universal context closure (every declared context invariant)" \
  "$PY" 00-BOOK/tools/ukctx_gate.py

# --- Stage 6b-cert: context closure certification (UCOS-UCTX-001, Phase 10) -----
# The gate above measures the invariants. This one measures whether the CERTIFICATE that
# reports them is still the certificate the current measurement derives — Phase 10 of the
# context consolidation asked for CI enforcement with no bypass and no warning-only mode.
#
# --check writes nothing. It re-derives the certificate and refuses if what is on disk
# differs, which makes a stale certification a build failure rather than a document nobody
# re-read. The certificate carries no clock precisely so that this comparison is possible:
# a timestamped one would differ on every run and could never be checked at all.
run_stage "context closure certification (UCOS-UCTX-001, Phase 10 claims at fixed point)" \
  "$PY" 00-BOOK/tools/ukctx_certify.py --check

# --- Stage 6b-prop: context proposal gate (UCOS-UCTX-001 assimilation lane) -----
# Refuses when a discovered proposal fails any of the four declared gates — validate,
# duplication, overlap, verification — so a draft can never reach the authority without
# passing them in order.
#
# WHY IT PASSES WHILE THE LANE IS UNDECLARED. `proposal_lane` is not yet in
# context-authority.json, so there are no proposals and nothing is in a bad state. A stage
# that refused here would be failing the build for a subsystem the repository has
# deliberately not adopted yet. The bare CLI still reports the undeclared lane as a refusal,
# because a human asking "can you assimilate?" deserves the honest no; only --gate, whose
# question is "is any proposal wrong?", treats an empty lane as clean.
run_stage "context proposal gate (four declared gates, every discovered proposal)" \
  "$PY" 00-BOOK/tools/ukctx_assimilate.py --gate

# --- Stage 6b-prov: independent context verification (UCOS-UCTX-001, MB7) -------
# The stage above is computed BY the generator's own derivation, so it cannot detect a
# generator that is uniformly wrong. Measured: ten variants — an injected sentence, a
# reversed rule, a fabricated authority, a permuted table, a swapped authority home, a
# truncated statement, a deleted section, a dropped article — each left all fifteen
# invariants green, because all fifteen are computed from the run that produced the error.
#
# That is MB7, and it is not specific to this capability: the generated-artifact registry
# records validation_owner == owner for every entry, 13 of 33 producers have no validator
# outside their own home, and 18 of the 19 that do import or execute the producer they
# validate. Module separation is not authority separation.
#
# This stage is the independent leg. It does not import ukctx, run it, or read its source.
# It asks three questions of the emitted surfaces: does every LINE trace to a declared
# source (a reviewed template, or a string a declared authority already holds); is every
# declared RECORD projected whole rather than re-paired; is every declared OBLIGATION
# carried rather than quietly dropped. Five of the ten variants emit no undeclared text at
# all, which is why one question would not have been enough.
#
# It found two live defects on its first run, both of which the fifteen invariants had
# reported as closure: UCKP-ART-01 (Supremacy) absent from every agent surface, and all
# nineteen remaining article statements truncated at their final line.
#
# WHAT IT DOES NOT CLAIM. It does not prove the manifest's first population was right —
# that was reviewed in the commit that introduced it. It guarantees that nothing is added
# afterwards without the same review, which moves the attack from "edit one script" to
# "edit a script AND an authored instrument".
run_stage "independent context provenance (MB7)" \
  "$PY" 00-BOOK/tools/ukctx_verify.py

# --- Stage 6b-ufi: independent verification, every declared adopter (MB7 rollup) --
# The stage above closes MB7 for ONE capability. Measured across the repository, that is
# where the defect lives generally: `validation_owner` equals `owner` for every entry of
# the generated-artifact registry, NO producer has a test inside its own home, and 16 of
# 33 producers have no producer-specific validator anywhere. A verifier written 33 times
# would be 33 new things that can each be uniformly wrong, so the checks were extracted
# into one implementation (00-BOOK/tools/ufi.py) that a producer ADOPTS by declaring its
# own authorities and its own manifest.
#
# The framework shares CODE and never AUTHORITY: ufi.py holds no list of any adopter's
# authorities, surfaces or templates, and a shared authority source would be the rival
# authority UCKP-ART-03 voids.
#
# This stage carries no count and names no adopter. Adoption is adding a declaration to
# 00-BOOK/DATA/independence/, and a stage that had to be edited to admit its next adopter
# would make adoption a documentation change in three files. It fails closed on an empty
# adopter set, because a framework that passes by verifying nothing is the defect again.
#
# UCOS-UCTX-001 is deliberately verified here AND by the stage above. That is not
# redundancy to remove: it is the second invocation plane UEC-L-06 asks for, so deleting
# either leg still leaves the check running.
run_stage "independent producer verification (UFI, every declared adopter)" \
  "$PY" 00-BOOK/tools/ufi.py --all

# --- Stage 6c: autonomous universal evolution gate (UAUE-000001) ------------------
# The evolution declaration binds three of its eleven positions — Execute, Validate and
# Verify — to `./verify.sh` as their gate, and its Evolve position to `make uaue-gate`.
# Until this stage existed, that binding was a claim about a pipeline that had never heard
# of UAUE: the gate was fail-closed, deterministic and green, and it was only ever invoked
# by hand. AUE-VER-04 (governance integrity) requires that every gate a position names be
# wired into the repository's verification, and an obligation nothing evaluates is of
# UNKNOWN compliance rather than satisfied. This stage is that wiring.
#
# Every obligation is fail-closed, and the stage name deliberately carries no count: the set
# grows as more of the declaration becomes measurable, and a number in a label is a stale claim
# waiting to happen — this stage is named in the canonical validation record, so a count here
# would make every new obligation a documentation edit in three files. What the obligations are is
# the gate's own report: the declaration rehydrates; every position resolves to an owner that
# exists and binds the symbols it is read through; every canonical Article-14 stage is claimed by
# exactly one position; every dependency resolves and runs forward; conducting the same candidates
# twice produces byte-identical runs; the declared UNKNOWN subject traverses the whole loop to a
# settled, certified run requiring no new registry, authority, engine or schema; every declared
# mandatory invariant is measured against its expectation; every declared register renders bytes
# that reproduce on another process and another machine; every declared exit criterion of every
# implementation phase is measured; and — the obligation this stage is the other half of — this
# pipeline is measured to actually invoke the gate fail-closed, so deleting the stage below closes
# the gate instead of silently unbinding four positions.
#
# Read-only and hermetic. `--gate` conducts and measures; it renders nothing, mutates
# nothing outside memory, and reaches no clock and no network, so it cannot dirty the tree
# and cannot flake. Exit 1 means an obligation was refused; exit 2 means no verdict could
# be reached, which is deliberately not the same answer.
run_stage "autonomous universal evolution (UAUE gate, every declared obligation)" \
  "$PY" -m engine.uaue.gate --gate --quiet

# --- Stage 6d: evolution surface replay (UAUE-000001 derived truth) ---------------
# The nineteen files in 00-MASTER/UAUE-000001/ — the append-only history projection and
# the eighteen declared registers — are DERIVED TRUTH: the deterministic product of the
# declaration and the measured tree. This stage regenerates them in memory and compares
# the committed bytes, so a hand edit is a failure here rather than a fact anywhere.
#
# Byte comparison, not parsed comparison: a projection that only matches after
# normalisation is a projection whose canonical form nobody is holding to. The remedy for
# a drift report is never to edit the file — it is `make uaue-render`, which reproduces it
# from the declaration.
run_stage "evolution surface replay (history + 18 registers)" \
  "$PY" -m engine.uaue.gate --replay --quiet

# --- Stage 6e: universal object birth contract (UOBC-000001) ----------------------
# Identity before existence. Six identity mechanisms existed before UOBC-000001 and all
# six identify things that ALREADY EXIST — they scan the tree and name what they find,
# which makes identity a measurement of location that changes when the location does.
# This gate measures the one thing none of them measures: that every object in the birth
# ledger was identified before it was instantiated, and that no identity was replaced.
#
# The eight laws are each computed, never asserted: UOBC-L-01 identity precedes existence
# (measured against the declaration's own identity_exists flags), L-02 derived never
# counted (the ledger must not hold `category_seq`, the declared mint marker, or it would
# be a second identity authority under CAA-INV-04's own test), L-03 identity immutability
# (every recorded id is RE-DERIVED from its namespace and local name — a tampered id
# fails without needing a history), L-04 no anonymous object, L-05 no temporary identity,
# L-06 no post-creation registration, L-07 evolution under one identity, L-08 append-only
# history.
#
# Read-only and hermetic: it loads the declaration and the ledger, computes, writes
# nothing, and reads no clock and no network, so it cannot dirty the tree and cannot
# flake. Exit 1 means a law was measured and refused; exit 2 means no verdict could be
# reached, which is deliberately a different answer.
run_stage "universal object birth contract (UOBC-000001, identity before existence)" \
  "$PY" -m engine.object_birth.gate --gate --quiet

# --- Stage 6f: universal infinite scope and direction (UISD-000001) ---------------
# Whether the architecture is still capable of growing. The unboundedness property was
# certified in prose on 2026-07-23 — 16 axes in 03-CONSTITUTIONAL-UNBOUNDEDNESS-
# CERTIFICATION.md, 23 finite-assumption axes in 04-HIDDEN-FINITE-ASSUMPTION-
# CERTIFICATION.md — but that second document records in its own §4 that no exhaustive
# proof of absence was performed and confines the residual risk to the realization
# layers. A property asserted in a dated document decays; this stage computes it.
#
# What it does NOT assert, because the assertion would be false and the stage would get
# deleted rather than fixed: that no enumeration is closed anywhere. engine/uckp/facets.py
# closes 33 facets deliberately so that every vocabulary inside them stays open — closure
# of the QUESTION set is what keeps the ANSWER sets infinite. The refused condition is
# UNDISCLOSED closure: an enumeration closed while nothing states what closes it or how a
# member is admitted. Ten enumerations are disclosed; one is disclosed as unintentional
# and carries gap ISD-G-01, which is the honest answer rather than a silent pass.
#
# The eleven laws are each computed, never asserted: ISD-L-01 scope capacity, L-02 direction
# capacity (the edge schema's type must be pattern-bound, never enum-bound), L-03 the
# principle inherits its own lifecycle and holds a birth record, L-04 the lifecycle stage
# graph declares itself open AND its executable projection has not drifted, L-05 the
# evolution cycle has no terminal stage and wraps, L-06 a relationship vocabulary admits a
# new term IN MEMORY without mutating the original — openness performed, not claimed —
# L-07 no active permanence declaration (a ratchet over 15 classified sites), L-08 every
# baseline surface parses its coordinate or discloses the owner it is deferred to, L-09 no
# runtime pin and no version ceiling, L-10 the capability model declares itself non-final,
# L-11 every population whose admission path claims the change is data alone admits a
# synthetic member through that path IN MEMORY, and every component that refuses is named
# with the owner that must act — a recorded refusal is evidence, and it is held as a
# ratchet in both directions so it cannot go stale.
#
# OBSERVE MODE. It reads the declaration, reads declared files, imports located modules
# in-process, computes, and writes nothing — including to gitignored paths. No clock, no
# network, no subprocess, so it cannot dirty the tree and cannot flake. Exit 1 means a law
# was measured and refused; exit 2 means no verdict could be reached.
run_stage "universal infinite scope and direction (UISD-000001, unbounded and self-applied)" \
  "$PY" -m engine.infinite_scope.gate --quiet

# --- Stage 6g: constitutional primitive alignment (UCPA-000001) -------------------
# The root ontology was correct and unenforced. BEING, EXISTENCE, RELATIONSHIP and
# TRANSFORMATION were adjudicated and RATIFIED (UCOS-RAT-001 RAT-01/02/03, recorded at
# 01-WORKING/SUPERSESSION-REGISTER.md SUP-01/02/07), and then lived only as markdown:
# ONT-02, ONT-03 and ONT-04 appeared in no .py and no .json file anywhere in the tree. No
# gate measured them, so the canonical register's own reduction obligation was asserted
# and never computed, and an edit reinstating the superseded 5-primitive chain — or
# re-promoting BEING to an addressable layer — would have passed ./verify.sh --full.
#
# Separately, the 33-facet model (engine/uckp/facets.py) and the root primitives were
# co-resident and unreconciled: no artifact related a facet to a primitive. This stage
# carries that mapping and measures it, which is what Phase 1 Scope A asked for.
#
# It legislates NOTHING. Every primitive it names must first be found in the register that
# owns it, and the facet side is IMPORTED rather than restated, so the mapping cannot
# silently drift from the model it maps — it can only fail. A thirty-fourth facet admitted
# without a reduction closes this gate, which is correct: facets.py states that a new facet
# is a constitutional amendment, and an amendment must not pass unnoticed.
#
# The eight laws are computed, never asserted: UCPA-L-01 every bound primitive is an
# element the canonical register already declares, by id AND by element name, L-02 standing
# is read out of the ratification record rather than assumed, L-03 the facet reduction is
# total and single-valued over the live enumeration in both directions, L-04 nothing
# reduces to the axiom — RAT-01 made executable, L-05 every classified projection resolves
# and every superseded one is named by a superseding instrument that names it back, L-06
# exactly one authority and it is the one 00-MASTER/URRC-000001 already binds, L-07 the
# primitive set admits a future member — openness performed in memory, never persisted —
# L-08 the programme reduces to a primitive it declares rather than exempting itself.
#
# OBSERVE MODE. It reads the declaration, reads declared files, imports the facet model
# in-process, computes, and writes nothing — including to gitignored paths. No clock, no
# network, no subprocess, so it cannot dirty the tree and cannot flake. Exit 1 means a law
# was measured and refused; exit 2 means no verdict could be reached.
run_stage "constitutional primitive alignment (UCPA-000001, root ontology measured and reduced)" \
  "$PY" -m engine.root_ontology.gate --quiet

# --- Stage 6g2: coordinate framework alignment (UCCFA-000001) ---------------------
# The layer beside the one above. UCPA measures the four root primitives; this measures the
# five coordinates that complete LAW Ω∞-000's nine dimensions, and UCCFA-L-06 proves the two
# bindings partition those nine exactly — a dimension bound by both is the duplication
# UCKP-ART-03 makes void, and one bound by neither is a constitutional requirement nothing
# measures. It ran nowhere before: ONT-05 through ONT-10 appeared in no .py file at all.
#
# OBSERVE MODE, same as the stage above: reads the declaration and the declared registers,
# computes, writes nothing. Exit 1 means a law was refused; exit 2 means no verdict.
run_stage "coordinate framework alignment (UCCFA-000001, five coordinates measured against the register)" \
  "$PY" -m engine.coordinate_framework.gate

# --- Stage 6h: universal verification intelligence (UVI-000001) -------------------
# The stage that measures the thing deciding what the other stages do. Every gate above
# answers "is the repository compliant"; this one answers "is the verification that just
# ran the verification it claimed to be". Before it existed, the selector could have
# narrowed a run, a mode could have claimed a floor it never evaluated, a shard plan could
# have dropped a test object, and every one of those would have shown up as a faster green
# run — the most dangerous possible failure mode for a verification selector, because its
# symptom is indistinguishable from success.
#
# The ten laws are computed, never asserted: UVI-L-01 the flags this script accepts and the
# modes the constitution declares are the same set in both directions, L-02 the bare
# invocation resolves to the one declared default, L-03 the stage labels below and the
# stage registry agree exactly and in order, L-04 the ratchet — every gate the certification
# default ran before this rework is still declared AND still admitted by every
# certification-eligible mode, L-05 no mode claims more than it measures (certification
# requires the whole suite, the floor, and no evidence reuse), L-06 selection is derived
# rather than authored, measured over the engine's evaluated string constants so that a
# docstring may discuss a test file and a code path may not name one, L-07 fail wide,
# performed rather than described — three synthetic unbounded changes are put through the
# selector and each must widen, L-08 topology neutrality, performed — the suite is
# partitioned at six worker counts and every partition must be exactly the suite, L-09 no
# certification-eligible mode can reach a reuse decision at all, L-10 planning twice over
# one state produces identical bytes and no plan carries a clock or a machine path.
#
# OBSERVE MODE. It reads the declaration, this script and its own sources, plans in memory,
# and writes nothing — including to gitignored paths. No clock, no network, no subprocess,
# so it cannot dirty the tree and cannot flake. Exit 1 means a law was measured and refused;
# exit 2 means no verdict could be reached, which is deliberately a different answer.
run_stage "universal verification intelligence (UVI-000001, selection derived and assurance preserved)" \
  "$PY" -m engine.verification_intelligence.gate --gate --quiet

# --- Stage 6i: universal construct foundation (UCON-000001) -----------------------
# The gate that closes the distance between what the constitution DECLARES about unknown,
# contradictory and future constructs and what the runtime actually DOES with one.
#
# The defect it closes, measured before it existed. A construct whose classifying kind was
# unregistered raised MetaTypeUnknownError (engine/kernel/errors.py) and left no record, so
# "we governed a refusal" and "we never saw it" were the same observable state. A
# contradiction was a three-string finding recomputed on each run with no identity and no
# lifecycle (engine/knowledge/intelligence.py::ConflictFinding). An unknown was a
# coercion-failure message. So the foundational principle — any presented construct can be
# represented, governed, traced, researched and disposed without constitutional redesign —
# was true of the declarations and false of the runtime, and nothing measured the gap.
#
# The sixteen laws are computed, and several PERFORM the property rather than inspect a
# description of it: UCON-L-01 every construct carries exactly one active disposition and
# the model refuses a forged construct that does not, L-02/L-03 the rule set is total and its
# catch-all is non-destructive — ESCALATE, never REJECT, because a REJECT catch-all would
# silently discard precisely the constructs the rules failed to anticipate while reporting a
# clean fully-covered run, L-04 operators are bound two-way to the declared rules, L-05
# nothing is silently ignored, checked by arithmetic (the population cannot exceed the
# presentations) and by requiring a REJECT to remain readable, L-06 unknowns, contradictions,
# research and discovery objects are governed objects and any construct is promotable to a
# research object, L-07 recursive discovery reaches a fixed point, L-08 openness performed —
# eleven categories this repository has never modelled are registered and the package's own
# source fingerprint must be unchanged, L-09 all nine declared extension points are performed
# in memory and nothing narrows, L-10 no disposition and no reality state is terminal and
# every state strong enough to certify can still fall to one that cannot, L-11 admission and
# reality are independent — the whole 8x8 cross-product is realised and both modules are
# parsed to confirm neither imports the other, L-12 a verifier that declares no assumptions
# or no limitations is refused, L-13/L-15 two ratchets that fail in BOTH directions, on an
# undeclared guarantee claim or a stale exemption and on an undisclosed closure in governed
# scope or a stale disclosure, L-14 every reality state binds to a UCOS-CEU-001 row CEU
# actually carries rather than copying it, L-16 determinism.
#
# It also carries the extensibility audit: 1,400+ closure mechanisms across the repository,
# each joined to its declared risk tier, owner, limitation and migration path. That inventory
# MEASURES and migrates nothing — the ratchet enforces disclosure inside engine/construct/
# and a non-rising population everywhere else, because a gate demanding zero closures today
# would have been closed on the day it was written and would then have been deleted.
#
# OBSERVE MODE. Reads the declaration, the repository's committed source and its own
# fingerprint; writes nothing, including to gitignored paths, unless --evidence is passed and
# it is not. No clock, no network, no subprocess. Exit 1 means a law was measured and refused;
# exit 2 means no verdict could be reached, which is deliberately a different answer.
run_stage "universal construct foundation (UCON-000001, every construct disposed and nothing silently ignored)" \
  "$PY" -m engine.construct.gate --gate --quiet

# --- Stage 6j (MAIN): universal enforcement closure (UEC-000001) ------------------
# CLOSURE OVER THE ENFORCEMENT SURFACE ITSELF. Every stage above measures some subject.
# This one measures whether the STAGES, GATES, WORKFLOWS, ENGINES, DECLARATIONS and TESTS
# still exist, are still governed, are still invoked from two independent planes, and are
# still covered by a test.
#
# WHY IT IS HERE AND NOT ONLY IN CI. The condition it refuses was measured in an isolated
# worktree at HEAD: seven workflow files deleted — including ec1-ci.yml, the only CI invoker
# of this script — plus six fail-closed Makefile gate targets, and `uvi-gate` still exited 0,
# `uaue-gate` still exited 0, and the test suite produced a byte-identical result. UVI
# reconciles the CONTENTS of this file against the stage registry (UVI-L-03/L-04); nothing
# measured whether anything still ran it, or whether the other fifty gate targets and thirty
# workflows were still present. A CI-only gate would leave the local certification path blind
# to exactly the deletion that removes the CI gate.
#
# ROOT CAUSE it closes: the repository's one closure mechanism (REG-AUTO-001) admits
# .md/.txt/.docx/.json outside .github/ and 00-MASTER/, so 0 of its 1597 registered artifacts
# are .py or .yml. The enforcement surface is definitionally outside it. UEC is the
# complementary plane; UEC-L-10 measures that the two do not overlap.
#
# READ_ONLY. No writes at all, not even to gitignored paths: there is no --render and no
# --write, so the gate cannot drift from an artifact it emitted and cannot be satisfied by
# regenerating its own expectation. Exit 1 means a blocking law refused; exit 2 means no
# verdict could be reached (no git work tree, so the tracked-path boundary is unknown), which
# is deliberately a different answer.
run_stage "universal enforcement closure (UEC-000001, every protection governed, invoked twice and covered)" \
  "$PY" -m engine.enforcement_closure.gate --gate --quiet

# --- Stage 6k (MAIN): universal recursive knowledge foundation (URKE-000001) ------
# THE CAPABILITY THIS STAGE RUNS WAS BUILT AND NEVER INVOKED, AND SAYING SO IS THE POINT.
# A declaration, a sixteen-module engine, thirty-two laws, a 249-subject governed ledger and a
# passing suite all existed at once, and NOTHING RAN ANY OF IT: no Makefile target, no workflow,
# no stage here, and no row in UEC-000001's governed enforcement inventory. The files were
# untracked, so UEC's discovery — which quantifies over `git ls-files` — could not see them
# either. Every gate in this repository was green while thirty-two laws measured nothing, which
# is exactly the observable state UEC-L-04 exists to refuse: nothing enforces by existing.
#
# WHAT IT MEASURES. That every identified unknown becomes a governed subject carrying identity,
# a context, a state, an owner and a governing authority; that residual is representable rather
# than silently dropped; that histories are append-only and nothing admitted can disappear; that
# the vocabulary lives in the declaration rather than in the code; that no state is terminal and
# a future domain is admissible by data alone; that discovery reaches a fixed point and never
# mutates constitutional truth; that no subject exists outside governance or outside context;
# that the pipeline cannot be bypassed; that no completeness claim is declared; and that two
# measurements of one state produce identical bytes.
#
# TWO OTHER PLANES INVOKE THE SAME GATE — `make urke-gate` and
# .github/workflows/urke-gate.yml — which is what UEC-L-06 requires: with three, deleting any
# one of them leaves a signal instead of a silently smaller verification. Removing THIS line
# now fails UEC-L-02 and the workflow's own verify.sh-binding step, rather than quietly
# unbinding thirty-two laws the way it did before the stage existed.
#
# OBSERVE MODE. It reads the declaration and the repository's committed source, computes, and
# writes nothing — including to gitignored paths — because --evidence is not passed. No clock,
# no network, no subprocess, so it cannot dirty the tree and cannot flake. Exit 1 means a
# blocking law was measured and refused; exit 2 means no verdict could be reached, which is
# deliberately a different answer.
run_stage "universal recursive knowledge foundation (URKE-000001, every unknown governed and no mechanism closed against a future domain)" \
  "$PY" -m engine.recursive_knowledge.gate --gate --quiet

# --- Stage 6l (MAIN): mutation governance boundary decidability (EX-018) ---------
# THE RULES THAT DECIDE WHO MAY MUTATE WHAT WERE DECIDING NOTHING. EX-015 made the mutation
# classes declarative and EX-016 made them decidable, and then no plane in this repository
# ever called them: a search for importers of `mutation_classification` returned exactly one
# file outside the module, its own test. Neither the classifier nor its register appeared in
# UEC-000001's governed inventory, so both could have been deleted with every gate green.
#
# WHAT THAT COST, MEASURED TWICE. R-09 was first declared with NO PREDICATE, so
# `validate_rule_coverage` refused and `classify()` returned ERROR for EVERY subject in the
# corpus — 28 committed tests failed against committed source. It was then implemented and
# still could not fire: its six criteria are R-08's five plus one, R-08 was evaluated first,
# and GOVERNED_ANALYSIS claimed 0 of 6751 tracked paths. Coverage was green through both.
#
# THREE LAWS, DELIBERATELY NOT COLLAPSED. MGB-L-01 coverage (a declared rule with no predicate,
# and a predicate no rule declares). MGB-L-02 reachability (a rule shadowed by an earlier one
# can never fire, and precedence must be a total order) — the side coverage cannot see.
# MGB-L-03 population (a reachable rule that claims nothing over the live corpus, unless the
# register names it with a reason). Any two of these pass while the third fails.
#
# UNRESOLVED IS REPORTED, NOT REFUSED. 3612 of 6755 tracked paths reach the fail-closed
# terminal, almost all for one reason: they declare no Authority. That is a governance question
# with an owner, not a defect this stage may decide — refusing on it would legislate a policy
# nobody has adopted. The count prints on every run so it cannot be quietly forgotten.
#
# TWO OTHER PLANES INVOKE THE SAME GATE — `make mutation-gate` and
# .github/workflows/mutation-gate.yml — as UEC-L-06 requires. Removing this line now fails
# UEC-L-02 rather than silently unbinding the classifier again.
#
# OBSERVE MODE. Reads the register and `git ls-files`; writes nothing, takes no clock and no
# environment. Exit 1 means a law was measured and refused; exit 2 means the register was
# unreadable so no verdict could be reached — deliberately a different answer.
run_stage "mutation governance boundary decidability (EX-018, every classification rule implemented, reachable and claiming subjects)" \
  "$PY" -m platform.repository_intelligence.mutation_gate --gate --quiet

# --- Stage 6m (MAIN): mandate disposition closure (CAEM-001) ----------------------
# THE MEASUREMENT THAT PROVED THE INSTRUMENTS WERE LYING, AND THEN RAN NOTHING. This
# engine is what found the thirty concepts the disposition register reported as
# implemented while the conformance suites proved them absent: IMPLEMENTED now requires
# a code file whose PATH names the concept word for word. It discharges all 1,449
# mandates across six source documents to one of seven dispositions, and it sat invoked
# by nothing — no Makefile target, no workflow, no stage here, and no row in UEC-000001's
# governed inventory. A protection nothing invokes is indistinguishable from a protection
# that does not exist, which is the observable state UEC-L-04 exists to refuse.
#
# WHAT IT MEASURES. Four fail-closed invariants over the committed register, not the
# corpus: CAEM-INV-01 every one of the 1,449 mandates carries a disposition;
# CAEM-INV-02 the register invents no mandate the corpus does not hold; CAEM-INV-03 every
# disposition is one the register declares; CAEM-INV-04 every disposition naming an owner
# names a file that exists. The slow half — --measure, ~5k repository greps that WRITE the
# register — is an explicit regeneration, never a stage, because a stage that writes the
# artifact it measures cannot drift from it and cannot be satisfied by regenerating its
# own expectation. The stage reads what --measure produced and refuses if the two disagree.
#
# WHY IT BELONGS IN THE CONTRACT AND NOT BEHIND A FLAG. The register is committed state
# derived from the corpus, so a mandate added without re-running --measure is drift this
# stage detects at the next commit rather than at the next programme audit. It costs 0.07s
# and reads no clock, no network and no environment.
#
# TWO OTHER PLANES INVOKE THE SAME GATE — `make caem-gate` — as UEC-L-06 requires; with
# two, deleting either leaves a signal rather than silently unbinding 1,449 dispositions.
# Removing this line now fails UEC-L-02 and UEC-L-04 rather than passing unnoticed.
#
# OBSERVE MODE. Reads the corpus and the committed register; writes nothing, takes no
# clock and no subprocess. Exit 1 means an invariant was measured and refused; exit 2
# means the register was absent so no verdict could be reached — deliberately a different
# answer, because a missing register is a regeneration debt and not a compliance verdict.
run_stage "mandate disposition closure (CAEM-001, every mandate disposed and no disposition invented)" \
  "$PY" 00-MASTER/CAEM-001/caem_engine.py --gate --quiet

# --- Stage 6n (MAIN): cross-process initialization independence (BC-2) -----------
# THE PROPERTY EVERY DETERMINISM GATE ABOVE STRUCTURALLY CANNOT SEE. The double-build
# harness compiles one blueprint twice and compares the bytes, and both builds run inside
# ONE interpreter — so every module global the second build reads is already whatever the
# first one left it. That is the correct shape for PATH REPRODUCIBILITY, which this
# repository has genuinely proven, and it is blind by construction to whether a verdict
# depends on WHEN, or IN WHICH ORDER, the process was initialized. TA-26 records that the
# two are distinct properties; conflating them is the whole of the evidential error
# blocker BC-2 names, and zero of the twenty-nine gates varied initialization order.
#
# THE CONDITION IT SEES. The identifier kind space is process-global mutable module state:
# 29 core kinds fixed in an enum, and an extension space only a CALL fills. Same commit,
# zero file changes, `is_well_formed("UCOS-CLSS-8966ca9e8d02")` is False in a fresh
# interpreter and True after `engine.ceu.catalog.bootstrap()`. 43 of 72 admissible kinds
# are in that state, and until this stage existed no instrument reported it.
#
# THREE CHILD PROCESSES, NOT THREE CALLS. A (uninitialized), B (the declared bootstrap)
# and C (the same declared state reached by the reverse arrival order), each a fresh
# `sys.executable` — the only arrangement in which "before initialization" is a real state
# rather than a name for whatever the previous call left behind. Distinct pids are
# asserted, not assumed. The child is handed a source string and imports nothing of the
# harness, so scenario A's interpreter is genuinely uninitialized.
#
# WHAT IT REFUSES AND WHAT IT DISCLOSES, AND WHY BOTH. A core kind whose verdict moves
# with initialization is hidden runtime state deciding truth: REFUSED. An extension kind's
# moving is UCKP-ART-17's open extension space working exactly as declared — admitted by
# registration, unknown before it and known after it: DISCLOSED, reported with the module
# global it localises to, and it does not move the verdict. B ≠ C is refused
# unconditionally, because no arrival order is entitled to decide a declared state.
# Collapsing the two classes would leave this gate either blind or permanently red.
#
# IT REFUSES ITSELF WHEN ITS CONTROL GOES UNDETECTED. The known initialization-dependent
# subject must appear in the divergence report or the run exits 1: a comparator that
# reports clean on a known-dirty subject is worthless, and a green line from one is worse
# than no line at all.
#
# TWO OTHER PLANES INVOKE THE SAME GATE — `make determinism-init-gate` and the A2-1..A2-8
# suite in engine/tests/unit/test_reproduce.py — as UEC-L-06 requires.
#
# READ_ONLY. Three subprocesses, no clock, no network, and no write anywhere — not even to
# a gitignored path. Exit 1 means a divergence was refused or the control went undetected;
# exit 2 means a probe did not complete, so no verdict could be reached, which is
# deliberately a different answer from "measured and refused".
run_stage "cross-process initialization independence (BC-2, no verdict moves with initialization order)" \
  "$PY" -m engine.determinism.reproduce --gate --quiet

# --- Stage 7 (POST): coverage report (explicit coverage tool invocation) ---------
# The pytest stage already produced .coverage + coverage.xml; re-summarize with the
# coverage CLI to prove the coverage tool itself resolves and to surface the total.
#
# The registry classifies this stage POST and declares it depends on the pytest stage,
# which is what moved it here from immediately after that stage: POST means "reads what
# MAIN produced", and a stage that reads MAIN's output cannot overlap MAIN. Placing it
# after the last MAIN stage is what lets every gate above it run concurrently — the
# ordering is derived from the declared dependency, not from taste.
#
# The plan skips it under --fast and --change, which run --no-cov: there is no coverage
# data to summarise, and printing a stale total would be worse than printing none. A
# developer run whose selection ESCALATED is the exception — it ran under the floor, so
# the plan turns this stage back on.
# A SHARDED JOB HAS NO TOTAL TO REPORT. This stage reads the canonical `.coverage` beside
# the repository root, and a shard never writes one — its data goes to UVI_COVERAGE_OUT for
# the combine job, which runs `coverage report` itself over the combined union. Running it
# here would fail on absent data, or, worse, summarise a fragment as if it were the suite.
# The `run_stage "coverage report"` literal stays in this file either way: the verification
# contract in platform/tests/test_canonical_validation_evidence.py is derived from these
# literals, and a stage label that appeared only in some runs would make the contract
# depend on how the run was invoked.
if [ -n "${UVI_SHARD:-}" ]; then
  ucos_log "SKIP (this run measured one shard; the combine job reports the total): coverage report"
else
  run_stage "coverage report" "$PY" -m coverage report
fi

# --- Stage 7 (opt-in): full registration transaction + drift gate ----------------
# READ-ONLY. Calls register.sh --observe, the verification plane: it answers "is
# registration state valid?" by reading, and allocates nothing.
#
# It used to call --guard, which runs the full transaction — Phase 1 is `ukb build
# --mint` — and only THEN checked for drift, so it CAUSED the drift it reported. A
# --guard run over a corpus with 140 unregistered artifacts minted all 140 permanent
# identities and emitted ~140 PORTAL pages from inside ./verify.sh --full.
# CORPUS_REGISTRATION is now declared in mutation-governance-boundary.json as governed
# by REG-AUTO-001 and explicitly NOT by verify.sh. Migration is an explicit transaction.
if [ "$FULL" = "1" ]; then
  run_stage "registration observation (register.sh --observe, read-only)" \
    env PYTHON="$PY" bash 00-BOOK/tools/register.sh --observe
fi

summarize_and_exit

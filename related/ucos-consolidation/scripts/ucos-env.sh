#!/usr/bin/env bash
#
# UCOS Ω∞ — Canonical environment library (shared).
#
# This file is *sourced* by bootstrap.sh, doctor.sh, and verify.sh. It is the single
# source of truth for "what the repository-standard execution environment is" and how
# to make a fresh shell converge to it WITHOUT any manual `source .../activate` step.
#
# Root cause it eliminates (see ENVIRONMENT-SETUP.md §Root-Cause):
#   * "ruff: command not found" / "coverage: command not found"  -> tools were only on
#     PATH inside an activated venv; a fresh shell had none of them.
#   * "pytest: unrecognized arguments: --cov"                     -> pytest ran under an
#     interpreter that lacked pytest-cov (the addopts in pyproject require it).
#   * "verification depends on whether a specific venv was activated" -> everything here
#     invokes the venv interpreter by ABSOLUTE PATH (never relies on PATH/activation).
#
# Design invariants:
#   1. Never depend on PATH. Always call "$(ucos_venv_python) -m <tool>".
#   2. Never require the caller to activate a venv.
#   3. The venv (.ec1-venv) is disposable + .gitignored; it is self-healed to match the
#      canonical Python series and the pinned toolchain in pyproject.toml [dev].
#   4. Standard tooling only: bash + a Python interpreter + git.
#
# Overridable via environment (sane defaults; you should rarely need these):
#   UCOS_PYTHON           explicit interpreter to build the venv from (e.g. python3.12)
#   UCOS_PYTHON_SERIES    canonical "major.minor" the venv must match (default 3.12)
#   UCOS_VENV_DIR         venv location (default <repo>/.ec1-venv)
#   UCOS_ALLOW_RECREATE   1 (default) => auto-recreate a venv whose series drifted
#   UCOS_ALLOW_PYTHON_MISMATCH  1 => tolerate a non-canonical series instead of failing

set -euo pipefail

# --- Canonical constants ---------------------------------------------------------
# The CI toolchain (.github/workflows/*.yml) pins actions/setup-python to 3.12, so
# 3.12 is the authoritative series every local verification must reproduce.
UCOS_PYTHON_SERIES="${UCOS_PYTHON_SERIES:-3.12}"

# --- Repo + venv location --------------------------------------------------------
# THE ROOT IS RESOLVED BY GIT, AND THIS IS A CORRECTION RATHER THAN A PREFERENCE.
#
# This function used to derive the root purely from ${BASH_SOURCE[0]} on the reasoning that
# the library lives in <repo>/scripts/, so the root is one level up. That reasoning is sound
# and the implementation was not: BASH_SOURCE is a bash array, and a shell that does not
# populate it — zsh, which is the login shell on the machine this was measured on — leaves
# the expansion empty. `dirname ""` is ".", so the root resolved to the PARENT of the
# current directory.
#
# Measured consequence (UCOS-EXECUTION-ENVIRONMENT-ASSESSMENT.md F-2):
#
#     $ zsh -c 'source scripts/ucos-env.sh && ucos_ensure_venv'
#     == Installing pinned toolchain into /Users/bipin/Desktop/.ec1-venv
#
# A virtual environment was created OUTSIDE the repository and sat there unnoticed for
# sixteen days. Nothing in the repository knew it existed, because nothing could: the only
# authority on where the repository is was the thing that had just got it wrong.
#
# git rev-parse --show-toplevel asks the repository where it is, which cannot be wrong in
# the way file layout can. The BASH_SOURCE derivation is retained as a fallback for the case
# git genuinely cannot answer (git absent, or a source export with no .git), and the
# fallback is guarded so an unset BASH_SOURCE resolves through $PWD instead of through "".
ucos_repo_root() {
  local root here
  if root="$(git rev-parse --show-toplevel 2>/dev/null)" && [ -n "$root" ]; then
    printf '%s\n' "$root"
    return 0
  fi
  here="$(cd "$(dirname "${BASH_SOURCE[0]:-$PWD/scripts/ucos-env.sh}")" && pwd)"
  cd "$here/.." && pwd
}
UCOS_REPO="$(ucos_repo_root)"
UCOS_VENV_DIR="${UCOS_VENV_DIR:-$UCOS_REPO/.ec1-venv}"

# --- Logging (all diagnostics go to stderr so stdout stays clean) ----------------
if [ -t 2 ]; then
  _UC_B=$'\033[1m'; _UC_G=$'\033[32m'; _UC_Y=$'\033[33m'; _UC_R=$'\033[31m'; _UC_0=$'\033[0m'
else
  _UC_B=""; _UC_G=""; _UC_Y=""; _UC_R=""; _UC_0=""
fi
ucos_log()  { printf '%s\n' "${_UC_B}==${_UC_0} $*" >&2; }
ucos_ok()   { printf '%s\n' "${_UC_G}✓${_UC_0} $*" >&2; }
ucos_warn() { printf '%s\n' "${_UC_Y}!${_UC_0} $*" >&2; }
ucos_err()  { printf '%s\n' "${_UC_R}✗${_UC_0} $*" >&2; }
ucos_die()  { ucos_err "$*"; exit 1; }

# --- Interpreter resolution ------------------------------------------------------
# Returns the interpreter used to *build* the venv. Prefers the canonical series so a
# fresh venv matches CI. Honors UCOS_PYTHON if the caller pins one explicitly.
ucos_find_interpreter() {
  local cand series
  local -a candidates=()
  [ -n "${UCOS_PYTHON:-}" ] && candidates+=("$UCOS_PYTHON")
  candidates+=("python${UCOS_PYTHON_SERIES}" "python3" "python")

  for cand in "${candidates[@]}"; do
    command -v "$cand" >/dev/null 2>&1 || continue
    series="$("$cand" -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null || true)"
    if [ "$series" = "$UCOS_PYTHON_SERIES" ]; then
      command -v "$cand"; return 0
    fi
  done

  # No canonical interpreter found. Fall back to any python3 unless the caller has
  # asked for strict matching.
  for cand in "${candidates[@]}"; do
    command -v "$cand" >/dev/null 2>&1 || { continue; }
    if [ "${UCOS_ALLOW_PYTHON_MISMATCH:-0}" = "1" ]; then
      ucos_warn "Canonical Python ${UCOS_PYTHON_SERIES} not found; using $(command -v "$cand") ($("$cand" --version 2>&1))." >&2
      command -v "$cand"; return 0
    fi
  done

  ucos_err "No Python ${UCOS_PYTHON_SERIES} interpreter found on PATH."
  ucos_err "Install it (macOS: 'brew install python@${UCOS_PYTHON_SERIES}') or set UCOS_PYTHON=/path/to/python."
  ucos_err "To proceed with a different series anyway: UCOS_ALLOW_PYTHON_MISMATCH=1 ..."
  return 1
}

ucos_venv_python() { printf '%s\n' "$UCOS_VENV_DIR/bin/python"; }

ucos_venv_present() { [ -x "$UCOS_VENV_DIR/bin/python" ]; }

ucos_venv_series() {
  ucos_venv_present || return 1
  "$UCOS_VENV_DIR/bin/python" -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null
}

# --- Expected pinned toolchain (single source of truth = pyproject.toml [dev]) ---
# Emits "name version" lines. Uses tomllib (stdlib >=3.11).
ucos_expected_deps() {
  local py="$1"
  "$py" - "$UCOS_REPO/pyproject.toml" <<'PY'
import sys, re
try:
    import tomllib
    with open(sys.argv[1], "rb") as f:
        data = tomllib.load(f)
    deps = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
except Exception:
    deps = []
for spec in deps:
    m = re.match(r"^\s*([A-Za-z0-9_.\-]+)\s*==\s*([^\s;]+)", spec)
    if m:
        print(m.group(1).replace("-", "_").lower(), m.group(2))
PY
}

# --- Dependency verification -----------------------------------------------------
# Returns 0 iff every pinned dev tool is present at exactly the pinned version AND
# every executable that tool's own installed-files manifest declares is present in
# the venv script directory and executable.
#
# Metadata alone is NOT sufficient, and the difference is not theoretical. A pinned
# tool can be RECORDED at the correct version while its executable is absent: an
# interrupted or partially completed reinstall leaves the import package, the
# version and the dist-info intact but never writes bin/<tool>. A metadata-only
# check then reports "already present and at expected versions", ucos_install_deps
# is never invoked, and the tool fails at the point of use instead of at the point
# of verification — which is the opposite of a self-healing environment. Measured
# consequence: bin/ruff was absent while `metadata.version("ruff")` returned the
# pinned 0.8.4, so this function reported a healthy toolchain, no repair was
# attempted, and verify.sh Stage 1 failed with FileNotFoundError on every run. That
# in turn failed the fixed-point gate's CK-VERIFY and STAGE-VERIFY, and the
# resulting certifier residue closed G-15 over an otherwise convergent repository.
#
# The executable set is DERIVED from each distribution's own manifest, never listed
# here, so it needs no edit when a pin is added or changed, and it covers wheel data
# scripts that declare no console_scripts entry point. That last case is exactly the
# ruff case: ruff ships its binary as a wheel script with an EMPTY console_scripts
# group, so an entry-points-based check would miss the only executable that mattered.
ucos_deps_ok() {
  local py; py="$(ucos_venv_python)"
  [ -x "$py" ] || return 1
  local expected; expected="$(ucos_expected_deps "$py")"
  [ -n "$expected" ] || return 1
  "$py" - <<PY
import csv
import io
import os
import sys
import sysconfig
from importlib import metadata
from pathlib import Path

expected = """$expected"""
alias = {"pytest_cov": "pytest-cov"}
scripts_dir = Path(sysconfig.get_path("scripts")).resolve()
ok = True

for line in expected.strip().splitlines():
    name, want = line.split()
    pkg = alias.get(name, name.replace("_", "-"))

    # 1. the package is installed, at the pinned version
    try:
        dist = metadata.distribution(pkg)
    except Exception:
        print(f"MISSING {pkg}", file=sys.stderr)
        ok = False
        continue
    if dist.version != want:
        print(f"DRIFT {pkg}: have {dist.version} want {want}", file=sys.stderr)
        ok = False

    # 2. every executable the package itself declares is installed and usable.
    #    RECORD is read DIRECTLY rather than through Distribution.files, because
    #    Distribution.files applies skip_missing_files() and therefore silently
    #    OMITS any recorded file that is absent from disk — it hides precisely the
    #    condition this check exists to detect. Measured: with bin/ruff deleted,
    #    dist.files yielded 10 entries and none of them was the bin entry, while
    #    RECORD line 1 still read "../../../bin/ruff,sha256=...,27802040". A files()
    #    based check is therefore inert by construction.
    record = dist.read_text("RECORD")
    if record is None:
        print(f"NORECORD {pkg}: installed-files manifest absent, executables unverifiable",
              file=sys.stderr)
        ok = False
        continue
    base = Path(dist.locate_file("")).resolve()
    for row in csv.reader(io.StringIO(record)):
        if not row or not row[0]:
            continue
        try:
            located = (base / row[0]).resolve()
        except Exception:
            continue
        if located.parent != scripts_dir:
            continue
        if not located.is_file():
            print(f"NOSCRIPT {pkg}: {located} is declared by the package but absent",
                  file=sys.stderr)
            ok = False
        elif not os.access(located, os.X_OK):
            print(f"NOEXEC {pkg}: {located} is present but not executable", file=sys.stderr)
            ok = False

sys.exit(0 if ok else 1)
PY
}

# --- Install / repair the pinned toolchain --------------------------------------
# Two passes, because the ordinary install cannot repair a missing executable.
# pip treats a requirement as SATISFIED when the version metadata is present, so a
# distribution whose bin/<tool> has been lost is left untouched by `pip install -e
# '.[dev]'` — measured: with bin/ruff deleted, the editable install completed quietly
# and bin/ruff was still absent, so ucos_deps_ok failed a second time and
# ucos_ensure_venv aborted. The repair pass therefore force-reinstalls the pinned dev
# tools at their pinned versions, and runs ONLY when the first pass left the toolchain
# unhealthy, so the common case pays nothing for it. --no-deps keeps the blast radius
# to the declared pins and cannot perturb the resolved dependency set.
ucos_install_deps() {
  local py; py="$(ucos_venv_python)"
  ucos_log "Installing pinned toolchain into ${UCOS_VENV_DIR} (pip install -e '.[dev]')"
  "$py" -m pip install --disable-pip-version-check --quiet --upgrade pip >&2
  ( cd "$UCOS_REPO" && "$py" -m pip install --disable-pip-version-check --quiet -e ".[dev]" >&2 )

  ucos_env_cache_invalidate

  if ucos_deps_ok 2>/dev/null; then
    return 0
  fi

  ucos_warn "toolchain still incomplete after install (a pinned executable is missing or unusable); forcing reinstall of the pinned dev tools"
  local specs=()
  local name want
  while read -r name want; do
    [ -n "${name:-}" ] || continue
    [ -n "${want:-}" ] || continue
    specs+=("$(printf '%s' "$name" | tr '_' '-')==${want}")
  done < <(ucos_expected_deps "$py")
  if [ "${#specs[@]}" -gt 0 ]; then
    ucos_log "Forcing reinstall: ${specs[*]}"
    "$py" -m pip install --disable-pip-version-check --quiet \
      --force-reinstall --no-deps "${specs[@]}" >&2
  fi
}

# --- Ensure the venv exists, matches the canonical series, and has the toolchain -
# This is the heart of the remediation: after this returns, "$(ucos_venv_python) -m
# pytest|ruff|coverage" is guaranteed to work with the pinned versions, regardless of
# whether any venv was activated in the shell.
ucos_ensure_venv() {
  local desired="$UCOS_PYTHON_SERIES"

  if ucos_venv_present; then
    local cur; cur="$(ucos_venv_series || echo '?')"
    if [ "$cur" != "$desired" ]; then
      if [ "${UCOS_ALLOW_RECREATE:-1}" = "1" ] && [ "${UCOS_ALLOW_PYTHON_MISMATCH:-0}" != "1" ]; then
        ucos_warn "venv Python ${cur} != canonical ${desired}; recreating (.ec1-venv is disposable/.gitignored)."
        rm -rf "$UCOS_VENV_DIR"
      else
        ucos_warn "venv Python ${cur} != canonical ${desired}; continuing without recreate (UCOS_ALLOW_RECREATE=0 or mismatch tolerated)."
      fi
    fi
  fi

  if ! ucos_venv_present; then
    local interp; interp="$(ucos_find_interpreter)" || return 1
    ucos_log "Creating venv at ${UCOS_VENV_DIR} from ${interp} ($("$interp" --version 2>&1))"
    "$interp" -m venv "$UCOS_VENV_DIR"
  fi

  if ucos_deps_ok; then
    ucos_ok "Pinned toolchain already present and at expected versions."
  else
    ucos_install_deps
    ucos_deps_ok || ucos_die "Toolchain still not at pinned versions after install; see errors above."
    ucos_ok "Pinned toolchain installed."
  fi
}


# --- Canonical ruff quality gate (SINGLE SOURCE OF TRUTH) ------------------------
# The lint + format-check gate that every fast verification path must run identically:
#   * verify.sh   Stage 1 (the canonical gate)
#   * the pre-commit hook installed by scripts/install-hooks.sh
# Defining it here — the file both already source — guarantees the two paths can never
# drift (the RC-1 gate-reconciliation invariant: "verify.sh passes => pre-commit passes").
# Runs the pinned ruff via the venv interpreter by ABSOLUTE PATH (no activation, no PATH
# dependency). ruff format --check is a NON-mutating check (it never rewrites files); use
# `make format` to apply formatting.
ucos_identity_gate() {
  # NOTHING EXISTS WITHOUT A UNIVERSAL ID. UCKP-ART-05 gives every object a permanent
  # identity and UGA-INV-01 refuses any tracked file without one — but only when somebody
  # runs the gate. A file could therefore enter history anonymous and stay that way until a
  # later verify.sh noticed, which is the shape this gate closes: an anonymous object cannot
  # be COMMITTED, so the condition cannot arise rather than being detected after the fact.
  #
  # WHY NOT CALL uga_engine DIRECTLY. That is the single-source-of-truth pattern
  # ucos_ruff_gate follows, and here it is the wrong trade: `uga_engine.py gate` builds the
  # whole object graph and takes 25.9s measured, against 153ms for this. A 26-second
  # pre-commit hook is one people bypass with --no-verify, and a gate that is routinely
  # bypassed protects nothing.
  #
  # THE TWO ARE EQUIVALENT BY CONSTRUCTION, NOT BY HOPE. UGA-INV-01 reports
  # `measured=7150` and `git ls-files` tracks exactly 7150 paths: UGA's population IS the
  # tracked set, with no exclusions, so "tracked and in neither identity map" is the same
  # predicate it applies. Both reported the identical four anonymous objects when this was
  # written. UGA remains the authority: if the two ever disagree, verify.sh still refuses,
  # so the worst this fast form can do is let something through for one commit — never
  # certify something UGA would refuse.
  #
  # UCOS-CL-011 applies here too: paths are read NUL-delimited. 23 tracked paths contain
  # spaces and 117 contain characters git would escape under core.quotepath, so a
  # newline-joined or quoted listing compares escaped text against real UTF-8 keys and
  # reports false anonymity for every one of them. That error was made while measuring this
  # (121 false positives) before `-z` was used.
  local py; py="$(ucos_venv_python)"
  local repo; repo="$(git rev-parse --show-toplevel)"
  "$py" - "$repo" <<'IDENTITY_EOF'
import json
import subprocess
import sys

repo = sys.argv[1]
ledger = f"{repo}/00-BOOK/DATA/id-ledger.json"
try:
    with open(ledger, encoding="utf-8") as handle:
        document = json.load(handle)
except (OSError, json.JSONDecodeError) as exc:
    print(f"identity gate: the id ledger is unreadable ({exc})", file=sys.stderr)
    raise SystemExit(2) from None

known = set(document.get("by_object") or ()) | set(document.get("by_path") or ())
if not known:
    print("identity gate: the id ledger carries no identities", file=sys.stderr)
    raise SystemExit(2)

listing = subprocess.run(
    ["git", "-C", repo, "ls-files", "-z"], capture_output=True, check=False
)
tracked = [path for path in listing.stdout.decode("utf-8").split("\0") if path]
anonymous = sorted(path for path in tracked if path not in known)
if anonymous:
    print(
        f"identity gate: {len(anonymous)} tracked object(s) carry no Universal ID.",
        file=sys.stderr,
    )
    for path in anonymous[:20]:
        print(f"  - {path}", file=sys.stderr)
    if len(anonymous) > 20:
        print(f"  ... and {len(anonymous) - 20} more", file=sys.stderr)
    print(
        "Allocation is IRREVERSIBLE and operator-authorized: obtain a REG-AUTO-001 permit, "
        "then run `python3 00-MASTER/UCOS-UGA-001/uga_engine.py run --permit=<id>`. "
        "Diagnose with `uga_engine.py gate`.",
        file=sys.stderr,
    )
    raise SystemExit(1)
IDENTITY_EOF
}

ucos_ruff_gate() {
  # UCOS-GOV-LINT-BOUNDARY: lint scope is the git-tracked file set, not the filesystem.
  #
  # WHY: ruff receives directory arguments and walks all .py files it finds — including
  # untracked files (macOS Finder " 2" copies, ephemeral editors, generated transients).
  # An untracked file with a lint error blocks every legitimate commit regardless of
  # whether that file will ever be committed. The pre-commit hook exists to validate
  # *the intended mutation* (staged + tracked content), not arbitrary filesystem state.
  #
  # HOW: git ls-files returns only tracked paths. We filter to Python files under the
  # governed source roots (engine/ platform/) and pass them explicitly.  This preserves
  # the RC-1 invariant ("verify.sh passes ⇒ pre-commit passes") because verify.sh also
  # calls this function — both paths now operate on the identical tracked boundary.
  #
  # GOVERNANCE VISIBILITY: untracked files are NOT hidden from governance. RIB GATE-12
  # (dirty_entries_outside_generated) and VAL-02 still surface them as working-tree
  # contamination — they are classified, not silently ignored.
  #
  # IMPLEMENTATION NOTE: if no tracked Python files exist in engine/ or platform/ the
  # gate becomes a no-op and exits 0, which is correct (nothing to lint).
  #
  # UCOS-CL-011 — the plumbing is NUL-delimited end to end. The first implementation
  # joined paths with newlines and piped them to a bare `xargs`, which splits on ANY
  # whitespace: a tracked path containing a space would have been passed to ruff as two
  # nonexistent paths. 23 tracked paths contain spaces today; none is currently a .py, so
  # the defect was latent rather than active — but a gate whose correctness depends on
  # that coincidence is not a gate. It also passed `git ls-files` output straight through,
  # which lists INDEX entries: a tracked file deleted in the working tree but not yet
  # staged was handed to ruff, which fails on a missing path and would have blocked every
  # commit during an ordinary staged deletion. And it prefixed paths with
  # `sed "s|^|$repo/|"`, which corrupts any repository path containing `|`.
  #
  # All three are removed: `-z` from git, `-0` into xargs, an existence filter for the
  # deletion case, and no path rewriting at all (we cd to the repo root instead, so ruff
  # receives the repository-relative paths git actually emitted).
  local py; py="$(ucos_venv_python)"
  local repo; repo="$(git rev-parse --show-toplevel)"

  # Tracked Python under the governed source roots, NUL-delimited, filtered to paths that
  # exist on disk so a staged/unstaged deletion cannot break the gate.
  local list; list="$(mktemp)"
  # shellcheck disable=SC2016
  git -C "$repo" ls-files -z -- 'engine/*.py' 'engine/**/*.py' \
                                'platform/*.py' 'platform/**/*.py' 2>/dev/null \
    | ( cd "$repo" && while IFS= read -r -d '' f; do
          [ -f "$f" ] && printf '%s\0' "$f"
        done ) > "$list"

  if [ ! -s "$list" ]; then
    rm -f "$list"
    ucos_ok "ruff gate: no tracked Python files in engine/ or platform/ — skipping"
    return 0
  fi

  # xargs -0 handles argument-length limits and NUL delimiting. Both invocations run from
  # the repository root so the relative paths resolve, and both statuses are captured:
  # `ruff check` and `ruff format --check` each exit non-zero independently, and the gate
  # must report a failure in EITHER, not just the last one.
  local rc=0
  ( cd "$repo" && xargs -0 "$py" -m ruff check < "$list" ) || rc=1
  ( cd "$repo" && xargs -0 "$py" -m ruff format --check < "$list" ) || rc=1
  rm -f "$list"
  return "$rc"
}


# --- UCOS-GOV-REFORMAT-VISIBILITY: substance hidden inside reformatting -----------
#
# WHAT THIS REPORTS AND WHY IT DOES NOT REFUSE. A staged registry whose whitespace churn
# dwarfs its semantic change is not wrong — it is UNREVIEWABLE, which is a different and
# quieter problem. Measured on 0900cb48: 5,181 changed lines in 00-CMG/CMG-REGISTRY.json
# carrying 118 insertions and 77 deletions of substance, and inside that reformatting the
# T1 vacancy was retired. BASELINE-001's ceiling broke on exactly that retirement and
# nobody saw it for five days, because reading the diff meant reading five thousand
# re-indented lines. `git diff --ignore-all-space` shows it in seconds — if you know to
# ask, and the point of this report is that you should not have to know.
#
# It REPORTS rather than refuses, on the same determination EEG-08 records: a blocking
# check that must be suppressed to get work done is a check people delete, and splitting a
# reformat from its substance is a judgement about how to present a change, not a
# correctness property this script is entitled to enforce.
ucos_reformat_report() {
  local repo py
  repo="$(ucos_repo_root)" || return 0
  py="$(command -v git)" || return 0
  [ -n "$py" ] || return 0

  # Constitutional registries and their projections: the documents where a buried
  # semantic change costs the most, because a gate somewhere reads every field.
  local staged
  staged="$(git -C "$repo" diff --cached --name-only --diff-filter=ACM 2>/dev/null \
    | grep -E '^(00-CMG/.*\.json|00-BOOK/DATA/.*\.json|00-MASTER/.*-declaration\.json)$' || true)"
  [ -n "$staged" ] || return 0

  local noisy=""
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    local total semantic
    total="$(git -C "$repo" diff --cached --numstat -- "$f" 2>/dev/null \
      | awk '{print $1+$2}')"
    semantic="$(git -C "$repo" diff --cached --numstat --ignore-all-space -- "$f" 2>/dev/null \
      | awk '{print $1+$2}')"
    [ -n "$total" ] && [ -n "$semantic" ] || continue
    # Only interesting when there IS substance to hide and the churn buries it: a pure
    # reformat (semantic 0) hides nothing, and a small diff is readable whatever it is.
    [ "$semantic" -gt 0 ] || continue
    [ "$total" -ge 400 ] || continue
    if [ "$total" -ge $((semantic * 5)) ]; then
      noisy="${noisy}    ${f}: ${total} changed lines carry ${semantic} of substance"$'\n'
    fi
  done <<< "$staged"

  [ -n "$noisy" ] || return 0
  ucos_warn "reformat visibility: substance is buried in whitespace churn"
  printf '%s' "$noisy" >&2
  ucos_warn "  read it with: git diff --cached --ignore-all-space -- <path>"
  ucos_warn "  consider splitting the reformat from the change it carries."
  return 0
}


# --- UEG-000001 · the environment integrity gate (OBSERVE ONLY) ------------------
# THE VERIFICATION HALF OF THE SEPARATION OF POWERS. ucos_ensure_venv above is the REPAIR
# half: it deletes, creates and installs, and bootstrap.sh (plus `doctor.sh --fix`) are the
# only things allowed to call it. This function is what a verification path calls instead.
# It observes and refuses. It creates nothing, installs nothing, and reaches no network.
#
# Why the distinction is load-bearing rather than stylistic (assessment finding F-1):
# ./verify.sh used to call ucos_ensure_venv, so a run that was supposed to DETECT toolchain
# drift would instead `rm -rf` the drifted venv, rebuild it and report green — the drift
# detected was the drift erased, and the evidence went with it. It also made the canonical
# gate depend on network reachability, so an offline machine got an infrastructure failure
# reported as a verification failure.
#
# TWO LAYERS, AND THE ORDER MATTERS. The real gate is a Python module, and a Python module
# cannot report that Python is missing. So this function checks in shell exactly the one
# condition that would prevent the gate from running at all — a venv interpreter that is
# absent or not executable — and hands everything else to the module, which can actually
# introspect the interpreter it is running inside.
#
# Usage: ucos_env_gate [command-label]
# Exit: 0 valid · 1 a blocking check refused · 2 no verdict could be reached.
ucos_env_gate() {
  local label="${1:-./verify.sh}"
  local py
  py="$(ucos_venv_python)"

  if [ ! -x "$py" ]; then
    printf '\n%s\n\n' "UCOS EXECUTION ENVIRONMENT FAILURE" >&2
    printf '%s\n\n' "EEG-00 — the canonical interpreter is absent" >&2
    printf '%s\n\n    %s\n\n' "Expected:" "$py" >&2
    printf '%s\n\n    %s\n\n' "Detected:" "<no executable at that path>" >&2
    printf '%s\n\n' "Execution blocked." >&2
    printf '%s\n\n' "Repair with: ./bootstrap.sh" >&2
    return 1
  fi

  # --evidence writes .ucos/execution-evidence.json, which is what makes a certified run
  # able to say WHICH interpreter produced it (finding F-5). Both paths it writes are
  # gitignored, so the gate cannot dirty the tracked tree.
  "$py" -m engine.execution_environment.gate --gate --quiet --evidence --command "$label"
}

# --- UEG-000001 · cache invalidation after a repair ------------------------------
# The fingerprint cache decides "did the dependency state change?" from a trigger key whose
# dependency component is a directory-mtime proxy. That proxy catches every ordinary path
# through pip, and the declaration states plainly what it does not catch: an in-place edit
# inside an already-installed package. The entry points that INSTALL close that gap by
# dropping the cache outright, which is cheaper and more honest than a proxy straining to
# be exhaustive. Called by ucos_install_deps, so no caller has to remember it.
ucos_env_cache_invalidate() {
  rm -f "$UCOS_REPO/.ucos/environment-fingerprint.json" 2>/dev/null || true
}

# --- Working-tree lease (AEOS G-04) ----------------------------------------------
# WHY THIS EXISTS. Multiple agent sessions write to this tree with no lock, and it has
# corrupted a certification measurement at least twice: final_certification_report.md §14
# records a second process that "advanced HEAD twice, and committed my uncommitted edits
# into its own commit while deleting untracked files I had created", and a later
# integration run failed test_verification_purity because three tracked files moved
# under it twenty-two minutes before the run began. Neither was a defect in the
# verification plane. Both were the absence of this.
#
# WHAT A LEASE BUYS THAT A LOCK DOES NOT. Mutual exclusion is the smaller half. The
# larger half is ATTRIBUTABILITY: a measurement taken while another process mutates the
# tree is attributable to no commit, so the lease records HEAD and the porcelain digest
# at acquisition and ucos_lease_verify re-measures them at release. A run whose subject
# moved underneath it must say so rather than report a verdict about a state that never
# existed as a whole.
#
# IT REFUSES; IT DOES NOT KILL. A live holder is reported with its pid and age and the
# run stops. Reaping another process is not a verification command's business, and a
# lease that kills is a lease that loses work.
#
# STALE LEASES ARE RECLAIMED, NOT OBEYED. A lease whose pid is gone is an artifact of a
# crash, and refusing forever on it would make every crash require manual cleanup — the
# failure mode that teaches people to delete lockfiles reflexively.
UCOS_LEASE_FILE="${UCOS_LEASE_FILE:-}"

_ucos_lease_path() {
  if [ -n "$UCOS_LEASE_FILE" ]; then printf '%s\n' "$UCOS_LEASE_FILE"; return; fi
  printf '%s\n' "$(ucos_repo_root)/.ucos/verify.lease"
}

_ucos_head()      { git -C "$(ucos_repo_root)" rev-parse HEAD 2>/dev/null || printf 'none\n'; }
_ucos_porcelain() { git -C "$(ucos_repo_root)" status --porcelain 2>/dev/null | shasum -a 256 | cut -d' ' -f1; }
_ucos_lease_field() { sed -n "s/^$2=//p" "$1" 2>/dev/null | head -1; }

# LIVENESS IS `ps`, NOT `kill -0`, AND THE DIFFERENCE IS A SILENT WRONG ANSWER. `kill -0`
# fails in two unrelated ways: ESRCH (no such process) and EPERM (it exists but belongs to
# somebody else). The shell collapses both to "non-zero", so a lease held by another
# user's live run was read as stale and reclaimed underneath them — the exact corruption
# the lease exists to prevent, caused by the lease. `ps -p` answers the question actually
# being asked: does this pid exist. Measured in the failure direction against pid 1.
_ucos_pid_alive() { ps -p "$1" -o pid= >/dev/null 2>&1; }

ucos_lease_acquire() {
  local mode="${1:-unknown}" lease pid held_mode age now
  lease="$(_ucos_lease_path)"
  mkdir -p "$(dirname "$lease")" 2>/dev/null || true
  if [ -f "$lease" ]; then
    pid="$(_ucos_lease_field "$lease" pid)"
    held_mode="$(_ucos_lease_field "$lease" mode)"
    if [ -n "$pid" ] && [ "$pid" != "$$" ] && _ucos_pid_alive "$pid"; then
      now=$(date +%s); age=$(( now - $(_ucos_lease_field "$lease" epoch) ))
      ucos_err "the working tree is leased by another run."
      ucos_err "  holder      : pid $pid (--$held_mode), ${age}s ago"
      ucos_err "  lease       : $lease"
      ucos_err "  why refused : a measurement taken while another process mutates this tree is"
      ucos_err "                attributable to no commit. Wait for pid $pid, or stop it."
      exit 1
    fi
    # Only a lease held by a DIFFERENT, dead pid is a reclaim. Re-acquiring our own is
    # ordinary — reporting it as a stale reclaim would train the reader to ignore the one
    # message that means another run died holding the tree.
    if [ -n "$pid" ] && [ "$pid" != "$$" ]; then
      ucos_warn "reclaiming a stale lease from pid $pid (no longer running)"
    fi
  fi
  {
    printf 'pid=%s\n' "$$"
    printf 'mode=%s\n' "$mode"
    printf 'epoch=%s\n' "$(date +%s)"
    printf 'head=%s\n' "$(_ucos_head)"
    printf 'porcelain=%s\n' "$(_ucos_porcelain)"
  } > "$lease"
}

ucos_lease_release() {
  local lease; lease="$(_ucos_lease_path)"
  [ -f "$lease" ] || return 0
  [ "$(_ucos_lease_field "$lease" pid)" = "$$" ] && rm -f "$lease"
  return 0
}

# Re-measure the subject. Non-zero when the tree moved under the run, which makes every
# verdict this run produced unattributable — reported, never silently tolerated.
ucos_lease_verify() {
  local lease was_head was_dirty now_head now_dirty; lease="$(_ucos_lease_path)"
  [ -f "$lease" ] || return 0
  [ "$(_ucos_lease_field "$lease" pid)" = "$$" ] || return 0
  was_head="$(_ucos_lease_field "$lease" head)";      now_head="$(_ucos_head)"
  was_dirty="$(_ucos_lease_field "$lease" porcelain)"; now_dirty="$(_ucos_porcelain)"
  if [ "$was_head" != "$now_head" ] || [ "$was_dirty" != "$now_dirty" ]; then
    ucos_err "the working tree MOVED during this run — the result is attributable to no commit."
    [ "$was_head" != "$now_head" ] && ucos_err "  HEAD      : $was_head -> $now_head"
    [ "$was_dirty" != "$now_dirty" ] && ucos_err "  worktree  : porcelain digest changed"
    ucos_err "  Re-run against a tree no other process is writing."
    return 1
  fi
  return 0
}

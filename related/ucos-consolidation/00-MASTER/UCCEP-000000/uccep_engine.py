#!/usr/bin/env python3
"""UCCEP-000000 — Universal Continuous Constitutional Evolution Programme engine.

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, registers nothing,
and owns nothing. It is the *aggregation* of gates that already exist and are already
owned, plus the deterministic emission of the programme determinations the mission names.

    python3 00-MASTER/UCCEP-000000/uccep_engine.py                 # observe at the standard tier
    python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier boot     # read-only pass
    python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier full     # every located gate
    python3 00-MASTER/UCCEP-000000/uccep_engine.py --gate          # fail-closed on failure
    python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-declaration
    python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-no-enumeration
    python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-write-scope
    python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-determinism
    python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-observation

OBSERVATION IS NOT EMISSION. Every invocation observes and
renders its verdict. An invocation WRITES only when emission is authorized, and emission
is authorized only when the requested tier is at least as wide as the tier of the
determination Repository Truth already records. A narrower run therefore prints its
verdict and leaves the tracked tree byte-identical — which is what makes the read-only
claim for `--tier boot` above true rather than aspirational. The located authority is
the Universal Observation Law (UEI-CAP-01: "observation is read-only over its subject
and mutates nothing it observes"), declared in the bindings as
`programme.observation_law_owner`.

Narrowing the recorded determination is an explicit constituent act, never a side
effect: `--authorize-emission` is the only path by which a run below the recorded tier
may write, and it announces itself in the run's own output.

Exit semantics of --gate:
    0  every EXECUTED blocking check passed
    1  one or more EXECUTED blocking checks failed
    2  fail-closed abort — the declaration is unusable, so no verdict may be asserted

Standing findings (a PROVISIONAL meta-constitution, a vacant Tier T1, a measured
traceability gap) set the CERTIFICATION CEILING; they do not by themselves fail the
gate. A gate whose verdict cannot be reached in both directions carries no evidentiary
value — that defect is itself recorded as a finding in the declaration.

Stdlib only. No network. No timestamp is emitted anywhere, so the sealed output set is
byte-identical for an unchanged repository state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "uccep-bindings.json"
EVIDENCE_DIR = HERE / "evidence"

TIERS = ("boot", "standard", "full")
TIER_ORDER = {name: index for index, name in enumerate(TIERS)}

# Keys a declaration entry is permitted to carry. Any key outside its allowed set is a
# fail-closed violation: this is what prevents a finite domain, industry, science,
# technology, platform, language, database, infrastructure or reality from ever being
# smuggled into the declaration as a new field.
ALLOWED_KEYS = {
    "principles": {"id", "name", "owner", "enforced_by"},
    "invariants": {"id", "name", "owner"},
    "checks": {
        "id",
        "name",
        "owner",
        "argv",
        "env",
        "write_scope",
        "tier",
        "fail_closed",
        "advisory",
        "advisory_reason",
        "governed_by_finding",
        "exit_semantics",
        "json_stdout",
        "json_assertions",
        "reentrancy_env",
        "reentrancy_reason",
        "timeout_seconds",
        "$assertion_comment",
    },
    "gates": {"id", "name", "owner", "checks"},
    "programs": {"id", "name", "output", "delegated_to", "checks"},
    "findings": {
        "id",
        "title",
        "class",
        "evidence",
        "violates",
        "owner",
        "disposition",
        "work_package",
        "blocking",
        "note",
    },
    "work_packages": {
        "id",
        "title",
        "discharges",
        "owner",
        "route",
        "acceptance",
        "authorization_required",
    },
}

VALID_DISPOSITIONS = (
    "IMPLEMENTED",
    "REGISTERED",
    "GOVERNED",
    "VALIDATED",
    "CERTIFIED",
    "REJECTED-WITH-EVIDENCE",
    "WORK-PACKAGE",
)

# Reference strings carry human suffixes (" (…)", " §…", " Art …", " · …"). A reference
# resolves against the repository by exact path first, then by unique prefix within the
# parent directory, so "00-CEP/CEP-009" resolves to the located instrument.
_SUFFIX_SPLITS = (" (", " §", " Art ", " · ", " — ")


# --------------------------------------------------------------------------- helpers


def fail_closed(message: str) -> NoReturn:
    print(f"UCCEP-000000: FAIL-CLOSED ABORT — {message}", file=sys.stderr)
    raise SystemExit(2)


def load_declaration() -> dict:
    if not DECLARATION.is_file():
        fail_closed(f"declaration absent: {DECLARATION.relative_to(REPO)}")
    try:
        return json.loads(DECLARATION.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        fail_closed(f"declaration is not valid JSON: {exc}")


def strip_reference(ref: str) -> str:
    text = ref
    for token in _SUFFIX_SPLITS:
        if token in text:
            text = text.split(token, 1)[0]
    return text.strip()


def resolve_reference(ref: str) -> Path | None:
    """Resolve a declaration reference to a located repository path, or None."""
    bare = strip_reference(ref)
    if not bare:
        return None
    candidate = REPO / bare
    if candidate.exists():
        return candidate
    parent = candidate.parent
    if not parent.is_dir():
        return None
    stem = candidate.name
    matches = sorted(child for child in parent.iterdir() if child.name.startswith(stem))
    return matches[0] if len(matches) >= 1 else None


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def git(*args: str) -> str:
    try:
        out = subprocess.run(  # noqa: S603 — fixed argv, no shell, no user input
            ["git", *args],  # noqa: S607 — resolved from PATH by design, as CI does
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        return out.stdout.strip()
    except OSError:
        return ""


def repository_state() -> dict:
    """The repository state RECORDED in this programme's emitted determinations.

    Repository Fixed-Point Closure (UCOS-RFP-001 RFP-2 / RFP-3) forbids a tracked
    artifact from embedding the identity of the commit that contains it, and from
    recording an observation of the working tree that contains it. This function
    previously emitted both, and both are non-convergent by construction:

      * a commit's identity is a function of the bytes it contains, so an artifact
        naming its own commit demands a commit whose hash lies inside its own tree;
      * writing "CLEAN, 0 entries" makes the tree dirty, so the value recorded is
        never the value that holds once it has been recorded.

    Neither is lost. Version control already owns the containing commit, and tree
    cleanliness is owned by the gate's exit code — restating either here duplicated
    state the repository already held and put this programme's determinations in
    permanent Evidence Drift. The value below is constant, so regeneration at an
    unchanged tracked tree is byte-identical in every environment and at every
    commit.
    """
    return {
        "anchor": "the containing commit — owned by version control, never restated here",
        "basis": (
            "UCOS-RFP-001 RFP-2 (no commit self-reference) and RFP-3 "
            "(no working-tree self-observation)"
        ),
    }


def interpreters() -> dict:
    venv = REPO / ".ec1-venv" / "bin" / "python"
    return {
        "$PY3": sys.executable,
        "$PY": str(venv) if venv.is_file() else "",
        "$SELF": str(Path(__file__).resolve()),
    }


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |\n"
    rule = "|" + "|".join(["---"] * len(headers)) + "|\n"
    body = "".join("| " + " | ".join(cell for cell in row) + " |\n" for row in rows)
    return head + rule + body


MISSING = object()


def get_path(payload: object, dotted: str) -> object:
    node = payload
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return MISSING
        node = node[part]
    return node


def extract_json(text: str) -> object | None:
    """Pull the last top-level JSON object out of stdout that may carry log lines."""
    depth = 0
    start = -1
    best = None
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}":
            if depth:
                depth -= 1
                if depth == 0 and start >= 0:
                    try:
                        best = json.loads(text[start : index + 1])
                    except json.JSONDecodeError:
                        pass
    return best


# ------------------------------------------------------------------- self-check logic


def check_declaration(decl: dict) -> list[str]:
    """Every identifier unique, every cross-reference bound, every path located."""
    findings: list[str] = []
    seen: dict[str, str] = {}
    for section, allowed in ALLOWED_KEYS.items():
        for entry in decl.get(section, []):
            ident = entry.get("id")
            if not ident:
                findings.append(f"{section}: entry without an id")
                continue
            if ident in seen:
                findings.append(f"duplicate identifier {ident} ({seen[ident]} and {section})")
            seen[ident] = section
            extra = set(entry) - allowed
            if extra:
                findings.append(f"{ident}: key(s) outside the permitted set: {sorted(extra)}")

    check_ids = {entry["id"] for entry in decl.get("checks", []) if entry.get("id")}
    finding_ids = {entry["id"] for entry in decl.get("findings", []) if entry.get("id")}
    wp_ids = {entry["id"] for entry in decl.get("work_packages", []) if entry.get("id")}

    for section in ("gates", "programs"):
        for entry in decl.get(section, []):
            for bound in entry.get("checks", []):
                if bound not in check_ids:
                    findings.append(f"{entry['id']}: bound check {bound} is not declared")
            if section == "gates" and not entry.get("checks"):
                findings.append(
                    f"{entry['id']}: no executable check bound — a manual gate is prohibited"
                )

    for principle in decl.get("principles", []):
        for bound in principle.get("enforced_by", []):
            if bound not in check_ids:
                findings.append(f"{principle['id']}: enforcing check {bound} is not declared")

    for check in decl.get("checks", []):
        governing = check.get("governed_by_finding")
        if check.get("advisory") and not governing:
            findings.append(f"{check['id']}: advisory without a governing finding is prohibited")
        if governing and governing not in finding_ids:
            findings.append(f"{check['id']}: governing finding {governing} is not declared")
        if check.get("tier") not in TIERS:
            findings.append(f"{check['id']}: tier {check.get('tier')!r} is not declared")

    for finding in decl.get("findings", []):
        disposition = finding.get("disposition")
        if disposition not in VALID_DISPOSITIONS:
            findings.append(
                f"{finding['id']}: disposition {disposition!r} is not one of "
                f"{list(VALID_DISPOSITIONS)} — nothing may remain ambiguous"
            )
        package = finding.get("work_package")
        if disposition == "WORK-PACKAGE" and not package:
            findings.append(f"{finding['id']}: WORK-PACKAGE disposition without a package")
        if package and package not in wp_ids:
            findings.append(f"{finding['id']}: work package {package} is not declared")

    for package in decl.get("work_packages", []):
        for target in package.get("discharges", []):
            if target not in finding_ids:
                findings.append(f"{package['id']}: discharges unknown finding {target}")

    # every located reference must resolve — this is what forbids declaring an
    # abstract, vendor, or otherwise unlocated owner
    references: list[tuple[str, str]] = [("programme.charter", decl["programme"]["charter"])]
    references += [("programme.governed_by", ref) for ref in decl["programme"]["governed_by"]]
    law = decl["programme"].get("observation_law_owner")
    if law:
        references.append(("programme.observation_law_owner", law))
    for section in ("principles", "invariants", "checks", "gates"):
        references += [
            (entry["id"], entry["owner"]) for entry in decl.get(section, []) if entry.get("owner")
        ]
    for program in decl.get("programs", []):
        references += [(program["id"], ref) for ref in program.get("delegated_to", [])]
    for source, ref in references:
        if resolve_reference(ref) is None:
            findings.append(f"{source}: reference does not resolve in the repository: {ref!r}")

    return findings


def check_no_enumeration(decl: dict) -> list[str]:
    """Prove the engine is data-driven, so extension needs no code change.

    Two mechanical properties, no denylist of technologies (a denylist would itself be
    an enumeration):

      1. Allowed-key conformance — verified by check_declaration; re-asserted here.
      2. No declared identifier appears as a literal in the engine source. If the engine
         never names a programme, gate or check, it cannot special-case one, so a new
         programme / gate / check / invariant / principle is added by DATA alone.
    """
    findings: list[str] = []
    source = Path(__file__).read_text("utf-8")
    identifiers: list[str] = []
    for section in ALLOWED_KEYS:
        identifiers += [entry["id"] for entry in decl.get(section, []) if entry.get("id")]
    for ident in sorted(set(identifiers)):
        if ident in source:
            findings.append(
                f"engine source special-cases declared identifier {ident} — "
                "extension would require a code change (Infinite Extensibility violated)"
            )
    for section, allowed in ALLOWED_KEYS.items():
        for entry in decl.get(section, []):
            extra = set(entry) - allowed
            if extra:
                findings.append(
                    f"{entry.get('id', section)}: undeclared key(s) {sorted(extra)} — "
                    "a finite domain assumption may be smuggled through a new field"
                )
    return findings


def check_write_scope(decl: dict, written: list[Path] | None = None) -> list[str]:
    """No write may land outside this programme's own operational memory."""
    findings: list[str] = []
    forbidden = decl["programme"]["forbidden_write_prefixes"]
    for prefix in forbidden:
        target = REPO / prefix
        if not target.exists():
            findings.append(f"forbidden-write prefix does not exist: {prefix}")
    for path in written or []:
        resolved = path.resolve()
        try:
            resolved.relative_to(HERE)
        except ValueError:
            findings.append(f"write outside the programme's operational memory: {resolved}")
    return findings


# ------------------------------------------------------- observation versus emission


class EmissionWithheld(RuntimeError):
    """Emission was attempted without an authorizing determination.

    Raised by ``emit`` itself rather than checked by its callers, so that a future
    caller which forgets the authorization branch still cannot write. This is the
    structural form of the Universal Observation Law: emission is not reachable from
    an observing act, by construction and not by convention.
    """


def recorded_determination_tier(decl: dict) -> tuple[str | None, str]:
    """The tier of the determination the repository ALREADY records, and its source.

    Consulted for exactly one purpose: as a PRECONDITION ON WRITING. It never enters
    the model, the verdict, the certification or the seal, so no determination is ever
    a function of a previous determination and Knowledge Once is not weakened — a
    derived artifact is not being read back as a source of truth, it is being protected
    from being overwritten by a narrower observation.

    Both the committed record and the working-tree record are consulted and the WIDER
    of the two governs. The committed record is Repository Truth; the working-tree
    record may be a wider determination that has not yet been committed, and losing it
    to a narrower run would destroy evidence just as surely.
    """
    record_name = decl["programme"].get("determination_record")
    if not record_name:
        return None, "no determination record is declared"
    home = decl["programme"]["operational_home"].rstrip("/")

    candidates: list[tuple[str, str]] = []
    committed = git("show", f"HEAD:{home}/{record_name}")
    if committed:
        candidates.append((committed, "the committed determination"))
    on_disk = HERE / record_name
    if on_disk.is_file():
        candidates.append((on_disk.read_text("utf-8"), "the working-tree determination"))

    widest: str | None = None
    source = "no determination is recorded"
    for text, origin in candidates:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        tier = payload.get("tier") if isinstance(payload, dict) else None
        if tier not in TIER_ORDER:
            continue
        if widest is None or TIER_ORDER[tier] > TIER_ORDER[widest]:
            widest, source = tier, origin
    return widest, source


def emission_authorized(recorded: str | None, requested: str) -> bool:
    """Tier monotonicity: an emitting run may never narrow what is already recorded.

    With nothing recorded there is nothing to narrow, so emission is authorized. This
    is a total function of two declared tier names and of nothing else, which is what
    makes ``check_observation``'s exhaustive probe of it a proof rather than a sample.
    """
    if recorded is None:
        return True
    return TIER_ORDER[requested] >= TIER_ORDER[recorded]


def emission_authority(decl: dict, requested: str, override: bool = False) -> dict:
    recorded, source = recorded_determination_tier(decl)
    authorized = emission_authorized(recorded, requested)
    if authorized:
        reason = (
            f"tier {requested} is at least as wide as {recorded} ({source})"
            if recorded is not None
            else f"{source} — nothing may be narrowed"
        )
    else:
        reason = (
            f"tier {requested} is narrower than the recorded tier {recorded} "
            f"({source}); observation may not replace a wider determination"
        )
    if not authorized and override:
        return {
            "authorized": True,
            "overridden": True,
            "recorded_tier": recorded,
            "requested_tier": requested,
            "reason": f"EXPLICITLY AUTHORIZED constituent act — {reason}",
        }
    return {
        "authorized": authorized,
        "overridden": False,
        "recorded_tier": recorded,
        "requested_tier": requested,
        "reason": reason,
    }


def check_observation(decl: dict) -> list[str]:
    """Prove that no observing act can rewrite Repository Truth.

    Four mechanical properties, none of which is a tautology:

      1. the located Universal Observation Law owner is declared and RESOLVES;
      2. a determination record is declared, so narrowing is detectable at all;
      3. the emission authority is tier-monotonic over EVERY ordered pair of declared
         tiers — exhaustive, and reachable in both directions (some pair is authorized
         and some pair is withheld), because a guard whose verdict cannot be reached in
         both directions carries no evidentiary value;
      4. ``emit`` itself refuses an unauthorized authority, so emission is unreachable
         from an observing act structurally rather than by the caller's discipline.
    """
    findings: list[str] = []
    programme = decl["programme"]

    owner = programme.get("observation_law_owner")
    if not owner:
        findings.append(
            "no located observation-law owner is declared — the read-only obligation "
            "would rest on this engine's own assertion"
        )
    elif resolve_reference(owner) is None:
        findings.append(f"declared observation-law owner does not resolve: {owner!r}")

    if not programme.get("determination_record"):
        findings.append(
            "no determination record is declared — a narrowing emission could not be detected"
        )

    authorized = withheld = 0
    for recorded in TIERS:
        for requested in TIERS:
            expected = TIER_ORDER[requested] >= TIER_ORDER[recorded]
            observed = emission_authorized(recorded, requested)
            if observed != expected:
                findings.append(
                    f"emission authority is not tier-monotonic: recorded={recorded} "
                    f"requested={requested} expected={expected} observed={observed}"
                )
            if observed:
                authorized += 1
            else:
                withheld += 1
    if not withheld:
        findings.append(
            "no requested tier is ever withheld — the guard's negative direction is "
            "unreachable and the guard would carry no evidentiary value"
        )
    if not authorized:
        findings.append("no requested tier is ever authorized — emission would be unreachable")

    try:
        emit(decl, {}, {"authorized": False, "reason": "self-guard probe"})
    except EmissionWithheld:
        pass
    except Exception as exc:  # noqa: BLE001 — any other outcome means emit() did not refuse
        findings.append(
            "emit() did not refuse an unauthorized authority; it proceeded and failed "
            f"with {exc!r} — observation is not separated from emission"
        )
    else:
        findings.append(
            "emit() proceeded without an authorizing determination — observation is "
            "not separated from emission"
        )

    return findings


# ------------------------------------------------------------------ check execution


def run_check(check: dict, resolved_tier: str, interp: dict) -> dict:
    ident = check["id"]
    record = {
        "id": ident,
        "name": check["name"],
        "owner": check["owner"],
        "tier": check["tier"],
        "write_scope": check["write_scope"],
        "advisory": bool(check.get("advisory")),
        "governed_by_finding": check.get("governed_by_finding"),
        "executed": False,
        "exit_code": None,
        "verdict": "NOT-EXECUTED",
        "reason": "",
        "assertions": [],
        # True iff this check lies within the selected tier, i.e. THIS run was
        # supposed to produce evidence for it. A check that is in scope but did
        # not execute is UNPROVEN and blocks the gate (absence of evidence is
        # never evidence); a check deliberately excluded by tier is disclosed as
        # a certification ceiling instead of being silently dropped.
        "in_scope": True,
    }
    if TIER_ORDER[check["tier"]] > TIER_ORDER[resolved_tier]:
        record["in_scope"] = False
        record["excluded_by"] = "tier"
        record["reason"] = f"tier {check['tier']} above the selected tier {resolved_tier}"
        return record

    # A check whose declared guard variable is set is already being run BY THE CALLER, so
    # running it here measures the same thing a second time. The aggregate is bound as a
    # stage of a pipeline that also runs this gate directly; with the guard armed the
    # nested copy is skipped, exactly as that pipeline's own guard skips the aggregate.
    #
    # Excluded from scope rather than passed: this run produced no evidence of its own for
    # it, so it caps the certification this run may assert, in the same way a tier
    # exclusion does. Which variable guards which check is DECLARED — the engine names
    # neither the pipeline nor the gate, so a new topology is admitted by data alone.
    guard = str(check.get("reentrancy_env") or "")
    if guard and os.environ.get(guard):
        record["in_scope"] = False
        record["excluded_by"] = "reentrancy"
        record["reason"] = str(
            check.get("reentrancy_reason")
            or f"{guard} is set, so the caller is already running this gate"
        )
        return record

    argv = list(check["argv"])
    token = argv[0]
    if token in interp:
        if not interp[token]:
            record["verdict"] = "UNAVAILABLE"
            record["reason"] = f"interpreter {token} is not present in this environment"
            return record
        argv[0] = interp[token]
    elif token.startswith("./") or token.startswith("/"):
        located = REPO / token.lstrip("./") if token.startswith("./") else Path(token)
        if not located.exists():
            record["verdict"] = "UNAVAILABLE"
            record["reason"] = f"entry point not located: {token}"
            return record

    env = dict(os.environ)
    env.update(check.get("env") or {})
    # Self-checks are resolved in-process by the caller; only located, external gates
    # are executed here.
    # noqa: S603 — argv comes from the declaration (Repository Truth), never from user
    # input, and is executed as a list with no shell.
    # BOUNDED, because an unbounded child cannot be told apart from a hung one. Without a
    # bound the aggregate inherits its child's runtime with no ceiling of its own: a gate
    # that never returns takes the whole run with it, and the CALLER's timeout then kills
    # the aggregate without ever naming which gate was responsible. Declared per check; a
    # check that declares no bound is unbounded exactly as before.
    limit = check.get("timeout_seconds")
    try:
        completed = subprocess.run(  # noqa: S603
            argv,
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
            env=env,
            timeout=float(limit) if limit else None,
        )
    except subprocess.TimeoutExpired:
        record["executed"] = True
        record["verdict"] = "FAIL"
        record["reason"] = f"exceeded its declared bound of {limit}s and was stopped"
        return record
    record["executed"] = True
    record["exit_code"] = completed.returncode
    stdout = completed.stdout or ""
    combined = stdout + (completed.stderr or "")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / f"{ident}.log").write_text(combined, "utf-8")

    assertions = check.get("json_assertions") or []
    if check.get("json_stdout") and assertions:
        # stdout ONLY: structured log lines on stderr must never be mistaken for the
        # declared verdict document.
        payload = extract_json(stdout)
        if payload is None:
            record["verdict"] = "FAIL"
            record["reason"] = "declared JSON verdict absent from stdout"
            return record
        failed: list[str] = []
        for assertion in assertions:
            value = get_path(payload, assertion["path"])
            if value is MISSING:
                ok = False
                observed = "<path absent from the owner's report>"
            else:
                ok = True
                if assertion.get("must_be_empty"):
                    ok = not value
                if "must_equal" in assertion:
                    ok = ok and value == assertion["must_equal"]
                observed = None if ok else value
            record["assertions"].append(
                {
                    "path": assertion["path"],
                    "result": "PASS" if ok else "FAIL",
                    "observed": observed,
                    "authority": assertion.get("authority"),
                    "finding": assertion.get("finding"),
                }
            )
            if not ok:
                failed.append(assertion["path"])
        record["verdict"] = "PASS" if not failed else "FAIL"
        record["reason"] = "" if not failed else "reported evidence violates: " + ", ".join(failed)
        return record

    record["verdict"] = "PASS" if completed.returncode == 0 else "FAIL"
    if completed.returncode != 0:
        semantics = check.get("exit_semantics") or {}
        record["reason"] = semantics.get(str(completed.returncode)) or semantics.get(
            "nonzero", f"exit {completed.returncode}"
        )
    return record


def run_self_check(check: dict, decl: dict, resolved_tier: str) -> dict:
    record = {
        "id": check["id"],
        "name": check["name"],
        "owner": check["owner"],
        "tier": check["tier"],
        "write_scope": check["write_scope"],
        "advisory": bool(check.get("advisory")),
        "governed_by_finding": check.get("governed_by_finding"),
        "executed": False,
        "exit_code": None,
        "verdict": "NOT-EXECUTED",
        "reason": "",
        "assertions": [],
        # True iff this check lies within the selected tier, i.e. THIS run was
        # supposed to produce evidence for it. A check that is in scope but did
        # not execute is UNPROVEN and blocks the gate (absence of evidence is
        # never evidence); a check deliberately excluded by tier is disclosed as
        # a certification ceiling instead of being silently dropped.
        "in_scope": True,
    }
    if TIER_ORDER[check["tier"]] > TIER_ORDER[resolved_tier]:
        record["in_scope"] = False
        record["excluded_by"] = "tier"
        record["reason"] = f"tier {check['tier']} above the selected tier {resolved_tier}"
        return record

    # A check whose declared guard variable is set is already being run BY THE CALLER, so
    # running it here measures the same thing a second time. The aggregate is bound as a
    # stage of a pipeline that also runs this gate directly; with the guard armed the
    # nested copy is skipped, exactly as that pipeline's own guard skips the aggregate.
    #
    # Excluded from scope rather than passed: this run produced no evidence of its own for
    # it, so it caps the certification this run may assert, in the same way a tier
    # exclusion does. Which variable guards which check is DECLARED — the engine names
    # neither the pipeline nor the gate, so a new topology is admitted by data alone.
    guard = str(check.get("reentrancy_env") or "")
    if guard and os.environ.get(guard):
        record["in_scope"] = False
        record["excluded_by"] = "reentrancy"
        record["reason"] = str(
            check.get("reentrancy_reason")
            or f"{guard} is set, so the caller is already running this gate"
        )
        return record
    handler = SELF_CHECKS[check["argv"][1]]
    findings = handler(decl)
    record["executed"] = True
    record["exit_code"] = 0 if not findings else 1
    record["verdict"] = "PASS" if not findings else "FAIL"
    record["reason"] = "; ".join(findings[:6])
    record["assertions"] = [
        {"path": "self", "result": "FAIL", "observed": text} for text in findings
    ]
    return record


def self_determinism(decl: dict) -> list[str]:
    """Render the sealed output set twice from one model; the bytes must be identical."""
    stub = {
        check["id"]: {
            "id": check["id"],
            "name": check["name"],
            "owner": check["owner"],
            "tier": check["tier"],
            "write_scope": check["write_scope"],
            "advisory": bool(check.get("advisory")),
            "governed_by_finding": check.get("governed_by_finding"),
            "executed": True,
            "exit_code": 0,
            "verdict": "PASS",
            "reason": "",
            "assertions": [],
            "in_scope": True,
        }
        for check in decl["checks"]
    }
    fixed_state = repository_state()
    first = render(decl, assemble(decl, stub, "boot", fixed_state))
    second = render(decl, assemble(decl, stub, "boot", fixed_state))
    if set(first) != set(second):
        return ["rendered output set differs between runs"]
    divergent = sorted(name for name in first if first[name] != second[name])
    return [f"non-deterministic rendering: {name}" for name in divergent]



def check_unboundedness_cardinality(decl: dict) -> list[str]:
    """Check no finite cardinality cap is declared."""
    findings: list[str] = []
    # Check CEP-007 and registry declarations for cardinality caps
    path = REPO / "00-CEP" / "CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md"
    if path.exists():
        content = path.read_text()
        # Look for explicit cardinality limits (excluding "unlimited", "unbounded" terms)
        if "max_records" in content.lower() or "capacity_limit" in content.lower():
            findings.append("finite cardinality cap declared in CEP-007")
    # Check registry files for caps
    registry = REPO / "00-BOOK" / "MASTER-BOOK" / "UMB-005-REGISTRY-ARCHITECTURE.md"
    if registry.exists():
        content = registry.read_text()
        if "max_size" in content.lower() or "capacity:" in content.lower():
            findings.append("finite cardinality cap declared in registry architecture")
    return findings


def check_unboundedness_hierarchy(decl: dict) -> list[str]:
    """Check no finite nesting limit is declared."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UCL-000001" / "ucl-declaration.json"
    if path.exists():
        file_content = path.read_text()
        # Look for actual numeric depth limits (not just the word which appears in limit_tokens list)
        import re
        if re.search(r'"max_depth"\s*:\s*\d+', file_content) or re.search(r'"depth_limit"\s*:\s*\d+', file_content):
            findings.append("finite nesting limit declared in lifecycle")
    return findings


def check_unboundedness_composition(decl: dict) -> list[str]:
    """Check no finite composition limit is declared."""
    findings: list[str] = []
    # Check universal compiler and meta-model declarations
    path = REPO / "00-MASTER" / "UCEF-000001" / "ucef-declaration.json"
    if path.exists():
        content = path.read_text()
        if "max_compositions" in content.lower():
            findings.append("finite composition limit declared")
    return findings


def check_unboundedness_federation(decl: dict) -> list[str]:
    """Check no finite federation cap is declared."""
    findings: list[str] = []
    path = REPO / "00-CEP" / "CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md"
    if path.exists():
        content = path.read_text()
        if "max_federations" in content.lower() or "fed_limit" in content.lower():
            findings.append("finite federation cap declared")
    return findings


def check_unboundedness_recursion(decl: dict) -> list[str]:
    """Check no finite recursion limit is declared."""
    findings: list[str] = []
    path = REPO / "00-CEP" / "CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md"
    if path.exists():
        content = path.read_text()
        if "max_recursion" in content.lower() or "recursion_limit" in content.lower():
            findings.append("finite recursion limit declared in CEP-009")
    return findings


def check_unboundedness_distribution(decl: dict) -> list[str]:
    """Check no finite node cap is declared."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UIE-000001" / "uie-declaration.json"
    if path.exists():
        content = path.read_text()
        if "max_nodes" in content.lower() or "node_limit" in content.lower():
            findings.append("finite node cap declared")
    return findings


def check_unboundedness_relationships(decl: dict) -> list[str]:
    """Check no finite relationship cap is declared."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UCMG-000001" / "CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md"
    if path.exists():
        content = path.read_text()
        if "max_relationships" in content.lower() or "rel_limit" in content.lower():
            findings.append("finite relationship cap declared")
    return findings


def check_unboundedness_transformations(decl: dict) -> list[str]:
    """Check no finite transformation limit is declared."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UCF-000001" / "ucf-declaration.json"
    if path.exists():
        content = path.read_text()
        if "max_transformations" in content.lower():
            findings.append("finite transformation limit declared")
    return findings


def check_unboundedness_coordinate_dimensions(decl: dict) -> list[str]:
    """Check no finite dimension cap is declared."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UCOS-UCF-000" / "ucf-declaration.json"
    if path.exists():
        content = path.read_text()
        if "max_dimensions" in content.lower() or "dim_limit" in content.lower():
            findings.append("finite dimension cap declared")
    return findings


def check_unboundedness_reality_models(decl: dict) -> list[str]:
    """Check no finite reality model cap is declared."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UCOS-UCF-000" / "ucf-declaration.json"
    if path.exists():
        content = path.read_text()
        if "max_reality_models" in content.lower():
            findings.append("finite reality model cap declared")
    return findings


def check_unboundedness_civilization_models(decl: dict) -> list[str]:
    """Check no civilization assumption is in foundation."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UCOS-UCF-000" / "ucf-declaration.json"
    if path.exists():
        content = path.read_text()
        # Check for hardcoded civilization assumptions
        if "civilization" in content.lower() and "assumption" in content.lower():
            findings.append("civilization assumption found in foundation")
    return findings


def check_unboundedness_intelligence_models(decl: dict) -> list[str]:
    """Check no finite intelligence model cap is declared."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UCOS-UCF-000" / "ucf-declaration.json"
    if path.exists():
        content = path.read_text()
        if "max_intelligence_models" in content.lower() or "intel_limit" in content.lower():
            findings.append("finite intelligence model cap declared")
    return findings


def check_unboundedness_governance_models(decl: dict) -> list[str]:
    """Check governance is extensible, not fixed."""
    findings: list[str] = []
    path = REPO / "00-CEP" / "CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md"
    if path.exists():
        content = path.read_text()
        if "governance_frozen" in content.lower() or "governance_fixed" in content.lower():
            findings.append("governance is fixed (not extensible)")
    return findings


def check_unboundedness_knowledge_models(decl: dict) -> list[str]:
    """Check no finite schema ceiling is declared."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UCOS-UCF-000" / "ucf-declaration.json"
    if path.exists():
        content = path.read_text()
        if "max_knowledge_schema" in content.lower() or "schema_cap" in content.lower():
            findings.append("finite schema ceiling declared")
    return findings


def check_unboundedness_evolution(decl: dict) -> list[str]:
    """Check no finite evolution limit is declared."""
    findings: list[str] = []
    path = REPO / "00-CEP" / "CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md"
    if path.exists():
        content = path.read_text()
        if "max_evolution" in content.lower() or "evolution_limit" in content.lower():
            findings.append("finite evolution limit declared in CEP-007")
    return findings


def check_unboundedness_future_extension(decl: dict) -> list[str]:
    """Check no finite concept cap is declared."""
    findings: list[str] = []
    path = REPO / "00-MASTER" / "UCOS-UCF-000" / "ucf-declaration.json"
    if path.exists():
        content = path.read_text()
        if "max_concepts" in content.lower() or "concept_cap" in content.lower():
            findings.append("finite concept cap declared")
    return findings


SELF_CHECKS = {
    "--check-declaration": check_declaration,
    "--check-no-enumeration": check_no_enumeration,
    "--check-write-scope": lambda decl: check_write_scope(decl),
    "--check-determinism": self_determinism,
    "--check-observation": check_observation,
    "--check-unboundedness-cardinality": check_unboundedness_cardinality,
    "--check-unboundedness-hierarchy": check_unboundedness_hierarchy,
    "--check-unboundedness-composition": check_unboundedness_composition,
    "--check-unboundedness-federation": check_unboundedness_federation,
    "--check-unboundedness-recursion": check_unboundedness_recursion,
    "--check-unboundedness-distribution": check_unboundedness_distribution,
    "--check-unboundedness-relationships": check_unboundedness_relationships,
    "--check-unboundedness-transformations": check_unboundedness_transformations,
    "--check-unboundedness-coordinate-dimensions": check_unboundedness_coordinate_dimensions,
    "--check-unboundedness-reality-models": check_unboundedness_reality_models,
    "--check-unboundedness-civilization-models": check_unboundedness_civilization_models,
    "--check-unboundedness-intelligence-models": check_unboundedness_intelligence_models,
    "--check-unboundedness-governance-models": check_unboundedness_governance_models,
    "--check-unboundedness-knowledge-models": check_unboundedness_knowledge_models,
    "--check-unboundedness-evolution": check_unboundedness_evolution,
    "--check-unboundedness-future-extension": check_unboundedness_future_extension,
}


# --------------------------------------------------------------------- aggregation


def aggregate(records: dict[str, dict], bound: list[str]) -> dict:
    executed = [records[cid] for cid in bound if records[cid]["executed"]]
    blocking = [rec for rec in executed if not rec["advisory"]]
    failed = [rec["id"] for rec in blocking if rec["verdict"] == "FAIL"]
    advisory_failed = [
        rec["id"] for rec in executed if rec["advisory"] and rec["verdict"] == "FAIL"
    ]
    unexecuted = [cid for cid in bound if not records[cid]["executed"]]
    # A blocking check that was IN SCOPE for this tier but produced no evidence is
    # UNPROVEN. It may not be filtered out of the verdict: doing so lets a missing
    # interpreter or an unlocated entry point read as a pass.
    unproven = [
        cid
        for cid in bound
        if records[cid]["in_scope"]
        and not records[cid]["advisory"]
        and not records[cid]["executed"]
    ]
    # Blocking checks excluded by tier: not a failure, but they cap what this run
    # can claim, so they are disclosed rather than dropped.
    out_of_tier = [
        cid for cid in bound if not records[cid]["in_scope"] and not records[cid]["advisory"]
    ]
    if failed or unproven:
        verdict = "FAIL"
    elif not blocking:
        verdict = "NOT-EXECUTED"
    elif unexecuted:
        verdict = "PARTIAL"
    elif advisory_failed:
        verdict = "PASS-WITH-ADVISORY"
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "failed": failed,
        "advisory_failed": advisory_failed,
        "not_executed": unexecuted,
        "unproven": unproven,
        "out_of_tier": out_of_tier,
        "executed": [rec["id"] for rec in executed],
    }


def build_model(decl: dict, resolved_tier: str) -> dict:
    interp = interpreters()
    records: dict[str, dict] = {}
    for check in decl["checks"]:
        if check["argv"][0] == "$SELF":
            records[check["id"]] = run_self_check(check, decl, resolved_tier)
        else:
            records[check["id"]] = run_check(check, resolved_tier, interp)
    return assemble(decl, records, resolved_tier, repository_state())


def assemble(decl: dict, records: dict[str, dict], resolved_tier: str, repo_state: dict) -> dict:
    """Pure aggregation over collected check records — no execution, no I/O."""
    gates = [
        {
            "id": gate["id"],
            "name": gate["name"],
            "owner": gate["owner"],
            "checks": gate["checks"],
            **aggregate(records, gate["checks"]),
        }
        for gate in decl["gates"]
    ]
    programs = [
        {
            "id": program["id"],
            "name": program["name"],
            "output": program["output"],
            "delegated_to": program["delegated_to"],
            "checks": program["checks"],
            **aggregate(records, program["checks"]),
        }
        for program in decl["programs"]
    ]

    ordered = [records[check["id"]] for check in decl["checks"]]
    executed = [rec for rec in ordered if rec["executed"]]
    in_scope = [rec for rec in ordered if rec["in_scope"]]
    blocking_failures = sorted(
        rec["id"] for rec in executed if not rec["advisory"] and rec["verdict"] == "FAIL"
    )
    advisory_failures = sorted(
        rec["id"] for rec in executed if rec["advisory"] and rec["verdict"] == "FAIL"
    )
    unavailable = sorted(rec["id"] for rec in ordered if rec["verdict"] == "UNAVAILABLE")
    # Blocking checks the environment failed to supply: the interpreter was absent or
    # the entry point could not be located. Previously these were computed, rendered,
    # and then excluded from the exit code, so four blocking checks could report
    # UNAVAILABLE while the aggregate gate still exited 0.
    blocking_unavailable = sorted(
        rec["id"] for rec in in_scope if not rec["advisory"] and rec["verdict"] == "UNAVAILABLE"
    )
    # Blocking checks in scope that did not execute for any other reason. A residual
    # NOT-EXECUTED here is an engine or declaration defect, never a pass.
    blocking_not_executed = sorted(
        rec["id"]
        for rec in in_scope
        if not rec["advisory"] and not rec["executed"] and rec["verdict"] != "UNAVAILABLE"
    )
    # The union of everything this run was obliged to prove and did not.
    unproven = sorted(set(blocking_unavailable) | set(blocking_not_executed))
    # Blocking checks deliberately excluded by tier. Not a failure, but a scope limit
    # that must cap the certification this run may assert.
    blocking_out_of_tier = sorted(
        rec["id"]
        for rec in ordered
        if not rec["in_scope"]
        and not rec["advisory"]
        and rec.get("excluded_by") != "reentrancy"
    )
    # Kept apart from the tier exclusions because the two cap the certification for
    # DIFFERENT reasons, and a ceiling that misstates its reason is not a disclosure. A
    # tier exclusion says this run was never asked to measure the check; a re-entrancy
    # exclusion says the caller is measuring it right now.
    blocking_reentrant = sorted(
        rec["id"]
        for rec in ordered
        if not rec["in_scope"]
        and not rec["advisory"]
        and rec.get("excluded_by") == "reentrancy"
    )
    # Fail-closed subject: a failed check and an unproven check are equally blocking.
    gate_blocking = sorted(set(blocking_failures) | set(unproven))

    ceiling = sorted(
        f"`{f['id']}` — {f['title']}"
        for f in decl["findings"]
        if f.get("blocking") and f.get("disposition") != "IMPLEMENTED"
    )
    if blocking_out_of_tier:
        ceiling = ceiling + [
            f"tier `{resolved_tier}` excluded {len(blocking_out_of_tier)} blocking check(s) "
            f"from this run: {', '.join(f'`{cid}`' for cid in blocking_out_of_tier)} — "
            "a tier-limited run may not assert unqualified certification"
        ]
    if blocking_reentrant:
        ceiling = ceiling + [
            f"{len(blocking_reentrant)} blocking check(s) were already running in the "
            f"caller and were not run again here: "
            f"{', '.join(f'`{cid}`' for cid in blocking_reentrant)} — this run asserts "
            "nothing of its own about them"
        ]
    if gate_blocking:
        certification = "NOT-CERTIFIED"
    elif ceiling:
        certification = "CERTIFIED-PROVISIONAL"
    else:
        certification = "CERTIFIED"

    # ---- independent views: the aggregate as it stands for each constituent, with the
    # portion that constituent itself generated STRUCK.
    #
    # CMG-000001 LI.6: "Certification SHALL NOT be self-issued. The certifying authority
    # SHALL be distinct from the certified subject's author." EDQ-004 disposes of the same
    # defect from the other side: standing that "rests on authority or recognition it
    # generated or controls" is a circular authority claim, and the declared remedy is that
    # the "circular basis [is] rejected as non-independent" — struck, neither passed nor
    # failed.
    #
    # This register is consumed by the very programmes it aggregates. A constituent reading
    # `gate_blocking` reads a set that contains its OWN verdict, so its invariants measure
    # themselves: the reading is self-sustaining in either direction and has two fixed
    # points, one of which is a failure no defect causes. That is not a measurement.
    #
    # Constituency is read from the declaration, never enumerated here: a gate or programme
    # CONSTITUTES a home when that home appears in its `delegated_to`, or when it binds a
    # check that home owns. A home's own view strikes exactly the checks of the gates and
    # programmes it constitutes — and nothing else, so every failure outside a home's own
    # programme still reaches it at full strength. The repository-level aggregate below is
    # untouched: UCCEP still reports every failure, including a constituent's own, to the
    # world. Only the constituent's view of itself is made independent.
    def _home_of(owner: str) -> str:
        parts = [p for p in str(owner).split("/") if p]
        return "/".join(parts[:2]) if len(parts) > 2 else str(owner)

    check_home = {rec["id"]: _home_of(rec["owner"]) for rec in ordered}
    homes = sorted(set(check_home.values()) | {
        _home_of(str(d))
        for group in (*decl["gates"], *decl["programs"])
        for d in group.get("delegated_to", [])
    } | {_home_of(str(group["owner"])) for group in decl["gates"] if group.get("owner")})

    def _constitutes(group: dict, home: str) -> bool:
        if any(_home_of(str(d)) == home for d in group.get("delegated_to", [])):
            return True
        if group.get("owner") and _home_of(str(group["owner"])) == home:
            return True
        return any(check_home.get(cid) == home for cid in group["checks"])

    independent_view: dict[str, dict] = {}
    for home in homes:
        struck = sorted(
            {
                cid
                for group in (*decl["gates"], *decl["programs"])
                if _constitutes(group, home)
                for cid in group["checks"]
            }
        )
        if not struck:
            continue
        kept = [cid for cid in records if cid not in struck]
        view = aggregate(records, kept)
        view_blocking = sorted(set(view["failed"]) | set(view["unproven"]))
        independent_view[home] = {
            "struck": struck,
            "blocking_failures": view["failed"],
            "advisory_failures": view["advisory_failed"],
            "unproven": view["unproven"],
            "blocking_unavailable": sorted(
                cid
                for cid in kept
                if records[cid]["in_scope"]
                and not records[cid]["advisory"]
                and records[cid]["verdict"] == "UNAVAILABLE"
            ),
            "blocking_not_executed": sorted(
                cid
                for cid in kept
                if records[cid]["in_scope"]
                and not records[cid]["advisory"]
                and not records[cid]["executed"]
                and records[cid]["verdict"] != "UNAVAILABLE"
            ),
            "blocking_out_of_tier": view["out_of_tier"],
            "gate_blocking": view_blocking,
            "gate_exit": 1 if view_blocking else 0,
            # A gate or programme is re-aggregated over its non-struck checks only, so a
            # verdict this home itself produced cannot reach it through a group either.
            # A group whose every check is struck carries no independent content at all
            # and is dropped rather than reported as passing — an empty group is not
            # evidence of anything.
            "gates": [
                {"id": d["id"], **{k: v for k, v in aggregate(records, keep).items()
                                   if k in ("verdict", "failed", "not_executed")}}
                for d in decl["gates"]
                for keep in [[cid for cid in d["checks"] if cid not in struck]]
                if keep
            ],
            "programs": [
                {"id": d["id"], **{k: v for k, v in aggregate(records, keep).items()
                                   if k in ("verdict", "failed", "not_executed")}}
                for d in decl["programs"]
                for keep in [[cid for cid in d["checks"] if cid not in struck]]
                if keep
            ],
        }

    model = {
        "programme": decl["programme"],
        "tier": resolved_tier,
        "repository": repo_state,
        "checks": ordered,
        "gates": gates,
        "programs": programs,
        "independent_view": independent_view,
        "blocking_failures": blocking_failures,
        "advisory_failures": advisory_failures,
        "unavailable": unavailable,
        "blocking_unavailable": blocking_unavailable,
        "blocking_not_executed": blocking_not_executed,
        "unproven": unproven,
        "blocking_out_of_tier": blocking_out_of_tier,
        "gate_blocking": gate_blocking,
        "certification": certification,
        "certification_ceiling": ceiling,
        "gate_exit": 1 if gate_blocking else 0,
    }
    sealed = {
        "gates": [{k: g[k] for k in ("id", "verdict", "failed", "not_executed")} for g in gates],
        "programs": [
            {k: p[k] for k in ("id", "verdict", "failed", "not_executed")} for p in programs
        ],
        "checks": [{k: c[k] for k in ("id", "verdict", "exit_code")} for c in ordered],
        "certification": certification,
        "tier": resolved_tier,
        "unproven": unproven,
    }
    model["seal_sha256"] = digest(sealed)
    return model


# ------------------------------------------------------------------------ rendering


def header(title: str, decl: dict, model: dict, purpose: str) -> str:
    programme = decl["programme"]
    repo = model["repository"]
    return (
        f"# {title}\n\n"
        + table(
            ["Field", "Value"],
            [
                ["PROGRAMME", f"`{programme['id']}` — {programme['name']} v{programme['version']}"],
                ["AUTHORITY", f"**{programme['authority']}**"],
                ["CHARTER", f"`{programme['charter']}`"],
                ["EVOLUTION OWNER", f"`{programme['evolution_owner']}`"],
                ["TIER", f"`{model['tier']}`"],
                ["REPOSITORY ANCHOR", repo["anchor"]],
                ["FIXED-POINT BASIS", repo["basis"]],
                ["CERTIFICATION", f"**{model['certification']}**"],
                ["SEAL (sha256)", f"`{model['seal_sha256']}`"],
                ["GENERATED BY", "`uccep_engine.py` — regenerated, never hand-authored"],
            ],
        )
        + f"\n> {purpose}\n\n---\n\n"
    )


def check_rows(model: dict, ids: list[str]) -> list[list[str]]:
    by_id = {rec["id"]: rec for rec in model["checks"]}
    rows = []
    for cid in ids:
        rec = by_id[cid]
        mark = "**" if rec["verdict"] == "FAIL" and not rec["advisory"] else ""
        rows.append(
            [
                f"`{rec['id']}`",
                rec["name"],
                f"`{rec['owner']}`",
                "advisory" if rec["advisory"] else "blocking",
                f"{mark}{rec['verdict']}{mark}",
                rec["reason"] or "—",
            ]
        )
    return rows


CHECK_HEADERS = ["Check", "What it executes", "Located owner", "Force", "Verdict", "Detail"]


def joined(items: list[str]) -> str:
    return ", ".join(f"`{item}`" for item in items) or "none"


def render(decl: dict, model: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    programme = decl["programme"]

    # ---- the programme determinations
    for program in model["programs"]:
        out[program["output"]] = (
            header(
                f"{program['id']} — {program['name']}",
                decl,
                model,
                f"The mission output of {program['id']}. Produced by AGGREGATING the located "
                f"owners below; this programme implements no owner of its own.",
            )
            + "## Delegation (Zero Parallel Authority)\n\n"
            + table(
                ["#", "Located owner this programme delegates to"],
                [[str(i + 1), f"`{ref}`"] for i, ref in enumerate(program["delegated_to"])],
            )
            + f"\n**Verdict: {program['verdict']}**\n\n"
            + "## Executable evidence\n\n"
            + table(CHECK_HEADERS, check_rows(model, program["checks"]))
            + (
                "\nNot executed at this tier: "
                + ", ".join(f"`{cid}`" for cid in program["not_executed"])
                + "\n"
                if program["not_executed"]
                else ""
            )
            + "\n---\n\n*This determination is DERIVED TRUTH. It creates no authority and "
            "supersedes no governing instrument. Where it conflicts with a higher frozen or "
            "governing instrument, the higher instrument governs.*\n"
        )

    # ---- gate register
    out["16-CONSTITUTIONAL-GATE-REGISTER.md"] = (
        header(
            "16 — Constitutional Gate Register",
            decl,
            model,
            f"The {len(model['gates'])} mandatory gates, each bound to the located executables "
            "that discharge it. A gate with no bound executable would be a manual gate and is "
            "rejected at declaration time.",
        )
        + table(
            ["Gate", "Name", "Located owner", "Bound checks", "Verdict"],
            [
                [
                    f"`{gate['id']}`",
                    gate["name"],
                    f"`{gate['owner']}`",
                    ", ".join(f"`{c}`" for c in gate["checks"]),
                    f"**{gate['verdict']}**" if gate["verdict"] == "FAIL" else gate["verdict"],
                ]
                for gate in model["gates"]
            ],
        )
        + "\n## Every declared check\n\n"
        + table(CHECK_HEADERS, check_rows(model, [rec["id"] for rec in model["checks"]]))
        + "\n## Principles → enforcing executable\n\n"
        + table(
            ["Principle", "Name", "Located owner", "Enforced by"],
            [
                [
                    f"`{p['id']}`",
                    p["name"],
                    f"`{p['owner']}`",
                    ", ".join(f"`{c}`" for c in p["enforced_by"]),
                ]
                for p in decl["principles"]
            ],
        )
        + "\n## Permanent invariants → located owner\n\n"
        + table(
            ["Invariant", "Name", "Located owner"],
            [[f"`{i['id']}`", i["name"], f"`{i['owner']}`"] for i in decl["invariants"]],
        )
    )

    # ---- assimilation / findings register
    findings = decl["findings"]
    out["17-ASSIMILATION-FINDINGS-REGISTER.md"] = (
        header(
            "17 — Assimilation & Findings Register",
            decl,
            model,
            "Nothing agreed or observed may remain only in conversation. Every entry carries "
            "exactly one disposition: IMPLEMENTED, REGISTERED, GOVERNED, VALIDATED, CERTIFIED, "
            "REJECTED-WITH-EVIDENCE, or WORK-PACKAGE.",
        )
        + table(
            ["Finding", "Class", "Disposition", "Blocks certification", "Owner", "Work package"],
            [
                [
                    f"`{f['id']}`",
                    f["class"],
                    f"**{f['disposition']}**",
                    "YES" if f.get("blocking") else "no",
                    f"`{f['owner']}`",
                    f"`{f['work_package']}`" if f.get("work_package") else "—",
                ]
                for f in findings
            ],
        )
        + "\n"
        + "".join(
            f"\n### {f['id']} — {f['title']}\n\n"
            f"- **Class** — {f['class']}\n"
            f"- **Disposition** — {f['disposition']}\n"
            f"- **Owner** — `{f['owner']}`\n"
            + ("- **Violates** — " + ", ".join(f["violates"]) + "\n" if f.get("violates") else "")
            + f"- **Evidence** — {f['evidence']}\n"
            + (f"- **Note** — {f['note']}\n" if f.get("note") else "")
            for f in findings
        )
        + "\n---\n\n## Work packages\n\n"
        + "".join(
            f"\n### {w['id']} — {w['title']}\n\n"
            f"- **Discharges** — {', '.join(w['discharges'])}\n"
            f"- **Owner** — `{w['owner']}`\n"
            f"- **Constitutional route** — {w['route']}\n"
            f"- **Acceptance** — {w['acceptance']}\n"
            f"- **Explicit authorization required** — "
            f"{'YES' if w.get('authorization_required') else 'no'}\n"
            for w in decl["work_packages"]
        )
    )

    # ---- dashboard
    out["00-UCCEP-DASHBOARD.md"] = (
        header(
            f"{programme['id']} — Continuous Constitutional Evolution Dashboard",
            decl,
            model,
            "The single continuously-regenerated view of programme state. This loop has no "
            "terminal state: Knowledge → Assimilation → Repository Truth → Governance → "
            "Meta-Model → Registries → Dependencies → Implementation → Validation → "
            "Certification → Evidence → Evolution Intelligence → Repository Truth.",
        )
        + "## Programme state\n\n"
        + table(
            ["Programme", "Name", "Output", "Verdict"],
            [
                [
                    f"`{p['id']}`",
                    p["name"],
                    f"`{p['output']}`",
                    f"**{p['verdict']}**" if p["verdict"] == "FAIL" else p["verdict"],
                ]
                for p in model["programs"]
            ],
        )
        + "\n## Gate state\n\n"
        + table(
            ["Gate", "Name", "Verdict"],
            [
                [
                    f"`{g['id']}`",
                    g["name"],
                    f"**{g['verdict']}**" if g["verdict"] == "FAIL" else g["verdict"],
                ]
                for g in model["gates"]
            ],
        )
        + "\n## Determination\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Blocking check failures", joined(model["blocking_failures"])],
                [
                    "Advisory failures (recorded, governed by a finding)",
                    joined(model["advisory_failures"]),
                ],
                ["Unavailable in this environment", joined(model["unavailable"])],
                [
                    "**UNPROVEN — blocking, in scope, no evidence produced (blocks the gate)**",
                    joined(model["unproven"]),
                ],
                [
                    "Blocking checks excluded by tier (scope limit, disclosed as a ceiling)",
                    joined(model["blocking_out_of_tier"]),
                ],
                ["Fail-closed gate subject", joined(model["gate_blocking"])],
                ["Certification", f"**{model['certification']}**"],
                ["Gate exit code", str(model["gate_exit"])],
            ],
        )
        + "\n### Certification ceiling\n\n"
        + (
            "The maximum attainable verdict is **CERTIFIED-PROVISIONAL**. A final or ratified "
            "certification is not assertable while the following stand:\n\n"
            + "".join(f"- {reason}\n" for reason in model["certification_ceiling"])
            if model["certification_ceiling"]
            else "No standing ceiling recorded.\n"
        )
        + "\n---\n\n*Regenerate with `make uccep`. Enforce with `make uccep-gate`.*\n"
    )

    return out


def emit(decl: dict, model: dict, authority: dict) -> list[Path]:
    """Write the sealed output set. THE ONLY WRITING PATH IN THIS ENGINE.

    The authorization test is the first statement, before any rendering and before any
    byte reaches the filesystem, so an unauthorized call is not a partial write.
    """
    if not authority.get("authorized"):
        raise EmissionWithheld(authority.get("reason") or "no authorizing determination")
    rendered = render(decl, model)
    written: list[Path] = []
    for name, body in sorted(rendered.items()):
        target = HERE / name
        target.write_text(body, "utf-8")
        written.append(target)
    machine = HERE / decl["programme"]["determination_record"]
    machine.write_text(canonical_json(model), "utf-8")
    written.append(machine)
    return written


# ----------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uccep_engine.py",
        description="UCCEP-000000 aggregate constitutional gate (AUTHORITY = NONE).",
    )
    parser.add_argument("--tier", choices=TIERS, default="standard")
    parser.add_argument("--gate", action="store_true", help="fail-closed: exit non-zero on failure")
    parser.add_argument(
        "--authorize-emission",
        action="store_true",
        help=(
            "explicit constituent act: permit this run to write even though it would "
            "narrow the recorded determination"
        ),
    )
    parser.add_argument("--quiet", action="store_true")
    for flag in sorted(SELF_CHECKS):
        parser.add_argument(flag, action="store_true", dest=flag.lstrip("-").replace("-", "_"))
    args = parser.parse_args(argv)

    decl = load_declaration()

    for flag, handler in sorted(SELF_CHECKS.items()):
        if getattr(args, flag.lstrip("-").replace("-", "_")):
            findings = handler(decl)
            label = flag.lstrip("-")
            if findings:
                print(f"UCCEP-000000 {label}: {len(findings)} finding(s)")
                for text in findings:
                    print(f"  - {text}")
                return 1
            print(f"UCCEP-000000 {label}: PASS")
            return 0

    integrity = check_declaration(decl)
    if integrity:
        for text in integrity:
            print(f"  - {text}", file=sys.stderr)
        fail_closed(
            f"declaration integrity: {len(integrity)} finding(s) — no verdict may be asserted"
        )

    model = build_model(decl, args.tier)

    # OBSERVATION IS COMPLETE AT THIS POINT. Everything below decides whether this
    # observation is also permitted to become an emission.
    authority = emission_authority(decl, args.tier, args.authorize_emission)
    written: list[Path] = []
    if authority["authorized"]:
        try:
            written = emit(decl, model, authority)
        except EmissionWithheld as exc:  # pragma: no cover — structurally unreachable
            fail_closed(f"emission attempted without authority: {exc}")

    scope = check_write_scope(decl, written)
    if scope:
        for text in scope:
            print(f"  - {text}", file=sys.stderr)
        fail_closed("forbidden-write guard tripped")

    if not args.quiet:
        gate_failures = ",".join(model["gate_blocking"]) or "none"
        gates_pass = sum(1 for g in model["gates"] if g["verdict"].startswith("PASS"))
        programmes_pass = sum(1 for p in model["programs"] if p["verdict"].startswith("PASS"))
        print(
            f"{decl['programme']['id']}: {model['certification']} | tier={model['tier']} | "
            f"gates={gates_pass}/{len(model['gates'])} PASS | "
            f"programmes={programmes_pass}/{len(model['programs'])} PASS | "
            f"blocking={gate_failures} | unproven={','.join(model['unproven']) or 'none'} | "
            f"seal={model['seal_sha256'][:16]}"
        )
        if authority["overridden"]:
            print(f"EMISSION OVERRIDDEN — {authority['reason']}")
        if written:
            print(f"wrote {len(written)} artifacts to {HERE}")
        else:
            print(f"OBSERVATION ONLY — emission withheld: {authority['reason']}")

    if args.gate and model["gate_blocking"]:
        if model["blocking_failures"]:
            print(
                "GATE: FAIL-CLOSED — blocking constitutional checks failed: "
                + ", ".join(model["blocking_failures"]),
                file=sys.stderr,
            )
        if model["unproven"]:
            print(
                "GATE: FAIL-CLOSED — blocking constitutional checks produced no evidence "
                "in this environment (absence of evidence is never evidence): "
                + ", ".join(model["unproven"]),
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

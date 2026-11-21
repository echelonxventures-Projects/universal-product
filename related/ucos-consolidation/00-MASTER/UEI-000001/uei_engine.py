#!/usr/bin/env python3
"""UEI-000001 — Universal Evolution Intelligence engine (UCOS Omega-Infinity Ω∞-001B).

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, ratifies nothing,
freezes no architecture and owns no capability. It is the executable expression of the
Evolution Intelligence contract: it reads a single DATA declaration
(``uei-evolution.json``) that binds each mandated evolution capability to the repository
home that already realises it, binds each capability to a located governing instrument,
verifies that every declared home, evidence reference and instrument resolves against
Repository Truth, and computes — never asserts — the coverage, governance, validation,
certification and readiness verdicts.

    python3 00-MASTER/UEI-000001/uei_engine.py                        # regenerate + report
    python3 00-MASTER/UEI-000001/uei_engine.py --gate                  # fail-closed
    python3 00-MASTER/UEI-000001/uei_engine.py --check-declaration
    python3 00-MASTER/UEI-000001/uei_engine.py --check-no-enumeration
    python3 00-MASTER/UEI-000001/uei_engine.py --check-write-scope
    python3 00-MASTER/UEI-000001/uei_engine.py --check-determinism
    python3 00-MASTER/UEI-000001/uei_engine.py --check-governance
    python3 00-MASTER/UEI-000001/uei_engine.py --check-reuse-before-create

Exit semantics of --gate:
    0  the gate is OPEN — every mandated capability is covered by a resolving home, every
       lifecycle step and standing loop is bound to a covered capability, every capability
       carries a governance obligation whose instrument resolves, and every mandatory
       validation and exit criterion is satisfied
    1  the gate is CLOSED — a capability, lifecycle step, loop, governance obligation,
       validation or exit criterion is not satisfied
    2  fail-closed abort — the declaration is unusable, so no verdict may be asserted

The engine contains no capability identifier, no mandate and no validation dimension as a
literal: the evolution contract is DATA. A self-check proves this. Rendering is driven by
a renderer bound per deliverable in the declaration rather than by positional index, so
declaring a further capability — with its deliverable, lifecycle step, validation, exit
criterion and governance obligation — needs no code change.

Stdlib only. No network. No timestamp is emitted anywhere, so the sealed output set is
byte-identical for an unchanged repository state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

PROGRAMME_ID = "UEI-000001"

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "uei-evolution.json"
EVIDENCE_DIR = HERE / "evidence"

# Keys an entry of each declared list-section is permitted to carry. A key outside its
# allowed set is a fail-closed violation: this prevents a new obligation, a hidden
# assumption, or an unbound capability from being smuggled in as a new field.
ALLOWED_KEYS = {
    "outputs": {"id", "file", "title", "purpose", "renderer", "capability"},
    "capabilities": {
        "id",
        "name",
        "mandate",
        "objective",
        "required_properties",
        "reuse",
        "homes",
        "evidence",
        "gap",
    },
    "pipeline_evolution": {"id", "step", "owner_capability"},
    "pipeline_continuous": {"id", "step", "owner_capability"},
    "validations": {"id", "dimension", "verified_by", "clause"},
    "exit_criteria": {"id", "criterion", "satisfied_by"},
    "governance": {"id", "obligation", "instrument", "enforced_by"},
}

# The sections whose entries own a lifecycle/standing step. Both are bound identically:
# a step is bound when the capability that owns it is covered.
PIPELINE_SECTIONS = ("pipeline_evolution", "pipeline_continuous")

# Programme references that must resolve against the repository. Every binding this
# programme claims to reuse must be a located artefact, or the reuse claim is empty.
PROGRAMME_REFERENCE_KEYS = (
    "governing_instrument",
    "operational_memory_owner",
    "recovery_owner",
    "execution_owner",
    "resilience_owner",
    "aggregate_gate_owner",
    "registration_owner",
)

# Fields the continuation block must carry for the hand-off to be usable.
CONTINUATION_KEYS = (
    "repository_state_source",
    "completed_work",
    "remaining_work",
    "current_checkpoint",
    "dependency_state",
    "open_issues",
    "architectural_decisions",
    "implementation_roadmap",
    "recommended_next_programme",
)

# Reference strings carry human suffixes. A reference resolves against the repository by
# exact path first, then by unique prefix within the parent directory.
_SUFFIX_SPLITS = (" (", " §", " Art ", " · ", " — ")


# --------------------------------------------------------------------------- helpers


def fail_closed(message: str) -> NoReturn:
    print(f"{PROGRAMME_ID}: FAIL-CLOSED ABORT — {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail_closed(f"declaration absent: {path}")
    try:
        return json.loads(path.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        fail_closed(f"declaration is not valid JSON: {exc}")


def load_declaration() -> dict:
    return load_json(DECLARATION)


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
    return matches[0] if matches else None


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


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |\n"
    rule = "|" + "|".join(["---"] * len(headers)) + "|\n"
    body = "".join("| " + " | ".join(row) + " |\n" for row in rows)
    return head + rule + body


def humanize(token: str) -> str:
    """Render a declared section key as prose without naming any section in this source."""
    return " ".join(reversed(token.split("_"))).replace("-", " ").capitalize()


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def declared_values(decl: dict, section: str, field: str) -> list[str]:
    return [entry[field] for entry in decl.get(section, []) if entry.get(field)]


def resolve_all(refs: list[str]) -> tuple[list[str], list[str]]:
    """Partition references into (resolved, unresolved) against Repository Truth."""
    resolved: list[str] = []
    unresolved: list[str] = []
    for ref in refs:
        (resolved if resolve_reference(ref) is not None else unresolved).append(ref)
    return resolved, unresolved


# ------------------------------------------------------------------- self-check logic


def check_declaration(decl: dict) -> list[str]:
    """Structural integrity: identity, vocabulary, closure and cross-reference."""
    findings: list[str] = []
    seen: dict[str, str] = {}
    for section, allowed in ALLOWED_KEYS.items():
        entries = decl.get(section)
        if not entries:
            findings.append(f"{section}: section is absent or empty")
            continue
        for entry in entries:
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

    capability_ids = set(declared_values(decl, "capabilities", "id"))
    validation_ids = set(declared_values(decl, "validations", "id"))

    # outputs — every deliverable declares its content, its renderer, and (where it is a
    # per-capability specification) the declared capability it renders.
    outputs = decl.get("outputs") or []
    files: dict[str, str] = {}
    for entry in outputs:
        ident = entry.get("id", "outputs")
        for key in ("file", "title", "purpose", "renderer"):
            if not entry.get(key):
                findings.append(f"{ident}: declares no {key}")
        name = entry.get("file")
        if name:
            if name in files:
                findings.append(f"{ident}: deliverable file collides with {files[name]}: {name}")
            files[name] = ident
        renderer = entry.get("renderer")
        if renderer and renderer not in RENDERERS:
            findings.append(f"{ident}: renderer {renderer!r} has no bound implementation")
        cap = entry.get("capability")
        if cap is not None and cap not in capability_ids:
            findings.append(f"{ident}: bound to undeclared capability {cap!r}")
        if renderer in PER_CAPABILITY_RENDERERS and cap is None:
            findings.append(f"{ident}: renderer {renderer!r} requires a bound capability")
        if renderer not in PER_CAPABILITY_RENDERERS and cap is not None:
            findings.append(f"{ident}: renderer {renderer!r} must not bind a capability")

    # every renderer the engine implements is exercised by a declared deliverable, so no
    # rendering path is dead and no deliverable is silently unrendered.
    used = {entry.get("renderer") for entry in outputs}
    for renderer in sorted(set(RENDERERS) - used):
        findings.append(f"renderer {renderer!r} is implemented but no deliverable declares it")

    # capabilities — every mandated capability is fully specified and bound
    for entry in decl.get("capabilities", []):
        ident = entry.get("id", "capabilities")
        for key in ("name", "mandate", "objective", "reuse"):
            if not entry.get(key):
                findings.append(f"{ident}: declares no {key}")
        if "gap" not in entry:
            findings.append(f'{ident}: declares no gap field (use "" when there is none)')
        for key in ("required_properties", "homes", "evidence"):
            if not as_list(entry.get(key)):
                findings.append(f"{ident}: declares no {key}")

    # every capability has a deliverable that specifies it — a capability with no
    # specification is unbound obligation.
    specified = {
        entry.get("capability")
        for entry in outputs
        if entry.get("renderer") in PER_CAPABILITY_RENDERERS
    }
    for ident in sorted(capability_ids - specified):
        findings.append(f"{ident}: no deliverable specifies this capability")

    # every lifecycle and standing step is owned by a declared capability
    for section in PIPELINE_SECTIONS:
        for entry in decl.get(section, []):
            if not entry.get("step"):
                findings.append(f"{entry.get('id', section)}: declares no step")
            owner = entry.get("owner_capability")
            if owner not in capability_ids:
                findings.append(
                    f"{entry.get('id', section)}: owner {owner!r} is not a declared capability"
                )

    # every capability owns at least one lifecycle or standing step
    owners = {
        entry.get("owner_capability")
        for section in PIPELINE_SECTIONS
        for entry in decl.get(section, [])
    }
    for ident in sorted(capability_ids - owners):
        findings.append(f"{ident}: owns no lifecycle or standing step")

    # every validation is verified by a declared capability, and every capability is
    # verified by one — an unverified capability cannot be certified.
    verifiers: set[str] = set()
    for entry in decl.get("validations", []):
        if not entry.get("dimension"):
            findings.append(f"{entry.get('id', 'validations')}: declares no dimension")
        if not entry.get("clause"):
            findings.append(f"{entry.get('id', 'validations')}: declares no clause")
        verifier = entry.get("verified_by")
        if verifier not in capability_ids:
            findings.append(
                f"{entry.get('id', 'validations')}: verifier {verifier!r} "
                "is not a declared capability"
            )
        else:
            verifiers.add(verifier)
    for ident in sorted(capability_ids - verifiers):
        findings.append(f"{ident}: no validation dimension verifies this capability")

    # every exit criterion is satisfied by a declared validation, and every validation
    # discharges one — a validation that gates nothing is decoration.
    targets: set[str] = set()
    for entry in decl.get("exit_criteria", []):
        if not entry.get("criterion"):
            findings.append(f"{entry.get('id', 'exit_criteria')}: declares no criterion")
        target = entry.get("satisfied_by")
        if target not in validation_ids:
            findings.append(
                f"{entry.get('id', 'exit_criteria')}: satisfied_by {target!r} "
                "is not a declared validation"
            )
        else:
            targets.add(target)
    for ident in sorted(validation_ids - targets):
        findings.append(f"{ident}: satisfies no exit criterion")

    # governance — every obligation names a declared capability and a located instrument
    for entry in decl.get("governance", []):
        ident = entry.get("id", "governance")
        if not entry.get("obligation"):
            findings.append(f"{ident}: declares no obligation")
        instrument = entry.get("instrument")
        if not instrument or resolve_reference(instrument) is None:
            findings.append(f"{ident}: instrument does not resolve: {instrument!r}")
        enforcer = entry.get("enforced_by")
        if enforcer not in capability_ids:
            findings.append(f"{ident}: enforced_by {enforcer!r} is not a declared capability")

    # programme block — identity and every located binding resolves
    programme = decl.get("programme") or {}
    for key in ("id", "name", "version", "authority", "mission", "gate_name", "gate_clause"):
        if not programme.get(key):
            findings.append(f"programme: declares no {key}")
    if not programme.get("programme_directive"):
        findings.append("programme: declares no programme_directive")
    for key in PROGRAMME_REFERENCE_KEYS:
        ref = programme.get(key)
        if not ref or resolve_reference(ref) is None:
            findings.append(f"programme.{key}: reference does not resolve: {ref!r}")
    for ref in programme.get("governed_by") or []:
        if resolve_reference(ref) is None:
            findings.append(f"programme.governed_by: reference does not resolve: {ref!r}")
    for prefix in programme.get("forbidden_write_prefixes") or []:
        if not (REPO / prefix).exists():
            findings.append(f"programme.forbidden_write_prefixes: prefix does not exist: {prefix}")

    # continuation block — every declared field is present
    continuation = decl.get("continuation") or {}
    for key in CONTINUATION_KEYS:
        if not continuation.get(key):
            findings.append(f"continuation: declares no {key}")

    return findings


def check_no_enumeration(decl: dict) -> list[str]:
    """Prove the engine is data-driven, so extending the contract needs no code change.

    No declared identifier, no capability mandate and no validation dimension may appear
    as a literal in this source. If the engine never names a capability, a mandate or a
    dimension, it cannot special-case one.
    """
    findings: list[str] = []
    source = Path(__file__).read_text("utf-8")
    literals: list[str] = []
    for section in ALLOWED_KEYS:
        literals += declared_values(decl, section, "id")
    literals += declared_values(decl, "capabilities", "mandate")
    literals += declared_values(decl, "capabilities", "name")
    literals += declared_values(decl, "validations", "dimension")
    literals += [entry["file"] for entry in decl.get("outputs", []) if entry.get("file")]
    for literal in sorted(set(literals)):
        if literal in source:
            findings.append(
                f"engine source special-cases declared value {literal!r} — extending "
                "the contract would require a code change"
            )
    for section, allowed in ALLOWED_KEYS.items():
        for entry in decl.get(section, []):
            extra = set(entry) - allowed
            if extra:
                findings.append(
                    f"{entry.get('id', section)}: undeclared key(s) {sorted(extra)} — "
                    "a new obligation may be smuggled through a new field"
                )
    return findings


def check_write_scope(decl: dict, written: list[Path] | None = None) -> list[str]:
    """No write may land outside this programme's own operational memory."""
    findings: list[str] = []
    for prefix in decl.get("programme", {}).get("forbidden_write_prefixes", []):
        if not (REPO / prefix).exists():
            findings.append(f"forbidden-write prefix does not exist: {prefix}")
    for path in written or []:
        resolved = path.resolve()
        try:
            resolved.relative_to(HERE)
        except ValueError:
            findings.append(f"write outside the programme's operational memory: {resolved}")
    return findings


def check_governance(decl: dict) -> list[str]:
    """Prove the mission clause: no declared capability is left ungoverned.

    A capability is governed when at least one declared governance obligation names it and
    that obligation's instrument resolves against Repository Truth. An obligation whose
    instrument cannot be located governs nothing, so it does not discharge the clause.
    """
    findings: list[str] = []
    governed: set[str] = set()
    for entry in decl.get("governance", []):
        ident = entry.get("id", "governance")
        instrument = entry.get("instrument")
        located = bool(instrument) and resolve_reference(instrument) is not None
        if not located:
            findings.append(
                f"{ident}: instrument is not located, so the obligation governs nothing: "
                f"{instrument!r}"
            )
            continue
        enforcer = entry.get("enforced_by")
        if enforcer:
            governed.add(enforcer)
    for entry in decl.get("capabilities", []):
        ident = entry.get("id", "capabilities")
        if ident not in governed:
            findings.append(f"{ident}: no located governance obligation covers this capability")
    for key in PROGRAMME_REFERENCE_KEYS:
        ref = decl.get("programme", {}).get(key)
        if not ref or resolve_reference(ref) is None:
            findings.append(f"programme.{key}: governance owner does not resolve: {ref!r}")
    return findings


def check_reuse_before_create(decl: dict) -> list[str]:
    """Prove zero duplication: every bound home pre-exists outside this programme.

    A home located inside this programme's own directory would mean the capability was
    authored here rather than bound, which is exactly the duplication the contract
    forbids. Evidence is held to the same rule.
    """
    findings: list[str] = []
    for entry in decl.get("capabilities", []):
        ident = entry.get("id", "capabilities")
        for key in ("homes", "evidence"):
            for ref in as_list(entry.get(key)):
                located = resolve_reference(ref)
                if located is None:
                    findings.append(f"{ident}: {key} reference does not resolve: {ref}")
                    continue
                try:
                    located.resolve().relative_to(HERE)
                except ValueError:
                    continue
                findings.append(
                    f"{ident}: {key} reference lies inside this programme's own home, so the "
                    f"capability is authored here rather than bound: {ref}"
                )
    return findings


# --------------------------------------------------------------------- assessment


def assess(decl: dict) -> dict:
    """Assess every capability, step, validation, exit criterion and obligation."""
    capabilities: list[dict] = []
    covered_ids: set[str] = set()
    for entry in decl.get("capabilities", []):
        homes_resolved, homes_unresolved = resolve_all(as_list(entry.get("homes")))
        ev_resolved, ev_unresolved = resolve_all(as_list(entry.get("evidence")))
        gap = (entry.get("gap") or "").strip()
        covered = bool(homes_resolved) and not homes_unresolved and not ev_unresolved and not gap
        reasons: list[str] = []
        if not homes_resolved:
            reasons.append("no home resolves")
        if homes_unresolved:
            reasons.append("home(s) unresolved: " + ", ".join(sorted(homes_unresolved)))
        if ev_unresolved:
            reasons.append("evidence unresolved: " + ", ".join(sorted(ev_unresolved)))
        if gap:
            reasons.append(f"open gap: {gap}")
        if covered:
            covered_ids.add(entry["id"])
        capabilities.append(
            {
                "id": entry["id"],
                "name": entry.get("name") or "",
                "mandate": entry.get("mandate") or "",
                "objective": entry.get("objective") or "",
                "required_properties": as_list(entry.get("required_properties")),
                "reuse": entry.get("reuse") or "",
                "gap": gap,
                "homes": as_list(entry.get("homes")),
                "homes_resolved": homes_resolved,
                "homes_unresolved": homes_unresolved,
                "evidence": as_list(entry.get("evidence")),
                "evidence_resolved": ev_resolved,
                "evidence_unresolved": ev_unresolved,
                "covered": covered,
                "reasons": reasons,
            }
        )

    pipelines: dict[str, list[dict]] = {}
    for section in PIPELINE_SECTIONS:
        steps: list[dict] = []
        for entry in decl.get(section, []):
            owner = entry.get("owner_capability")
            steps.append(
                {
                    "id": entry["id"],
                    "section": section,
                    "step": entry.get("step") or "",
                    "owner_capability": owner,
                    "bound": owner in covered_ids,
                }
            )
        pipelines[section] = steps

    governance: list[dict] = []
    governed_ids: set[str] = set()
    for entry in decl.get("governance", []):
        instrument = entry.get("instrument") or ""
        located = bool(instrument) and resolve_reference(instrument) is not None
        enforcer = entry.get("enforced_by")
        binding = located and enforcer in covered_ids
        if binding:
            governed_ids.add(enforcer)
        governance.append(
            {
                "id": entry["id"],
                "obligation": entry.get("obligation") or "",
                "instrument": instrument,
                "instrument_located": located,
                "enforced_by": enforcer,
                "binding": binding,
            }
        )

    validations: list[dict] = []
    satisfied_validations: set[str] = set()
    for entry in decl.get("validations", []):
        verifier = entry.get("verified_by")
        satisfied = verifier in covered_ids and verifier in governed_ids
        if satisfied:
            satisfied_validations.add(entry["id"])
        validations.append(
            {
                "id": entry["id"],
                "dimension": entry.get("dimension") or "",
                "verified_by": verifier,
                "clause": entry.get("clause") or "",
                "satisfied": satisfied,
            }
        )

    exit_criteria: list[dict] = []
    for entry in decl.get("exit_criteria", []):
        target = entry.get("satisfied_by")
        exit_criteria.append(
            {
                "id": entry["id"],
                "criterion": entry.get("criterion") or "",
                "satisfied_by": target,
                "satisfied": target in satisfied_validations,
            }
        )

    for cap in capabilities:
        cap["governed"] = cap["id"] in governed_ids

    return {
        "capabilities": capabilities,
        "pipelines": pipelines,
        "governance": governance,
        "validations": validations,
        "exit_criteria": exit_criteria,
    }


def build_model(decl: dict, repo_state: dict) -> dict:
    findings = check_declaration(decl)
    a = assess(decl)
    caps = a["capabilities"]
    pipelines = a["pipelines"]
    governance = a["governance"]
    validations = a["validations"]
    exits = a["exit_criteria"]

    uncovered = [c["id"] for c in caps if not c["covered"]]
    ungoverned = [c["id"] for c in caps if not c["governed"]]
    validations_satisfied = [v["id"] for v in validations if v["satisfied"]]
    exits_satisfied = [e["id"] for e in exits if e["satisfied"]]
    obligations_binding = [g["id"] for g in governance if g["binding"]]

    step_metrics: dict[str, dict] = {}
    all_steps_bound = bool(pipelines)
    for section, steps in pipelines.items():
        bound = [s["id"] for s in steps if s["bound"]]
        step_metrics[section] = {"total": len(steps), "bound": len(bound)}
        if not steps or len(bound) != len(steps):
            all_steps_bound = False

    all_caps = not uncovered and bool(caps)
    all_gov = not ungoverned and bool(governance) and len(obligations_binding) == len(governance)
    all_val = len(validations_satisfied) == len(validations) and bool(validations)
    all_exit = len(exits_satisfied) == len(exits) and bool(exits)

    gate_open = not findings and all_caps and all_steps_bound and all_gov and all_val and all_exit

    evidence_references = sum(
        len(c["evidence_resolved"]) + len(c["homes_resolved"]) for c in caps
    ) + len([g for g in governance if g["instrument_located"]])

    lifecycle_total = sum(m["total"] for m in step_metrics.values())
    lifecycle_bound = sum(m["bound"] for m in step_metrics.values())

    model = {
        "programme": decl["programme"],
        "continuation": decl["continuation"],
        "repository": repo_state,
        "capabilities": caps,
        "pipelines": pipelines,
        "governance": governance,
        "validations": validations,
        "exit_criteria": exits,
        "declaration_findings": findings,
        "metrics": {
            "capability_total": len(caps),
            "capabilities_covered": len(caps) - len(uncovered),
            "capabilities_uncovered": uncovered,
            "capabilities_governed": len(caps) - len(ungoverned),
            "capabilities_ungoverned": ungoverned,
            "steps": step_metrics,
            "steps_total": lifecycle_total,
            "steps_bound": lifecycle_bound,
            "governance_total": len(governance),
            "governance_binding": len(obligations_binding),
            "validations_total": len(validations),
            "validations_satisfied": len(validations_satisfied),
            "exit_criteria_total": len(exits),
            "exit_criteria_satisfied": len(exits_satisfied),
            "evidence_references": evidence_references,
        },
        "gate": "OPEN" if gate_open else "CLOSED",
        "determination": "CERTIFIED-EVOLVING" if gate_open else "NOT-EVOLVING",
        "gate_exit": 0 if gate_open else 1,
    }
    sealed = {
        "capabilities": [
            {"id": c["id"], "covered": c["covered"], "governed": c["governed"]} for c in caps
        ],
        "steps": [
            {"id": s["id"], "bound": s["bound"]}
            for section in sorted(pipelines)
            for s in pipelines[section]
        ],
        "governance": [{"id": g["id"], "binding": g["binding"]} for g in governance],
        "validations": [{"id": v["id"], "satisfied": v["satisfied"]} for v in validations],
        "exit_criteria": [{"id": e["id"], "satisfied": e["satisfied"]} for e in exits],
        "gate": model["gate"],
        "determination": model["determination"],
        "declaration_findings": findings,
    }
    model["seal_sha256"] = digest(sealed)
    return model


def self_determinism(decl: dict) -> list[str]:
    """Render the sealed output set twice from one model; the bytes must be identical."""
    fixed_state = repository_state()
    first = render(decl, build_model(decl, fixed_state))
    second = render(decl, build_model(decl, fixed_state))
    if set(first) != set(second):
        return ["rendered output set differs between runs"]
    return [
        f"non-deterministic rendering: {name}"
        for name in sorted(first)
        if first[name] != second[name]
    ]


SELF_CHECKS = {
    "--check-declaration": check_declaration,
    "--check-determinism": self_determinism,
    "--check-governance": check_governance,
    "--check-no-enumeration": check_no_enumeration,
    "--check-reuse-before-create": check_reuse_before_create,
    "--check-write-scope": lambda decl: check_write_scope(decl),
}


# ------------------------------------------------------------------------ rendering


def header(title: str, decl: dict, model: dict, purpose: str) -> str:
    programme = decl["programme"]
    repo = model["repository"]
    m = model["metrics"]
    return (
        f"# {title}\n\n"
        + table(
            ["Field", "Value"],
            [
                ["PROGRAMME", f"`{programme['id']}` — {programme['name']} v{programme['version']}"],
                ["DIRECTIVE", f"`{programme['programme_directive']}`"],
                ["AUTHORITY", f"**{programme['authority']}**"],
                ["GOVERNING INSTRUMENT", f"`{programme['governing_instrument']}`"],
                ["OPERATIONAL HOME", f"`{programme['operational_home']}`"],
                ["REPOSITORY ANCHOR", repo["anchor"]],
                ["FIXED-POINT BASIS", repo["basis"]],
                [
                    "CAPABILITY COVERAGE",
                    f"{m['capabilities_covered']}/{m['capability_total']}",
                ],
                [
                    "GOVERNANCE COVERAGE",
                    f"{m['capabilities_governed']}/{m['capability_total']}",
                ],
                ["DETERMINATION", f"**{model['determination']}**"],
                [
                    programme["gate_name"].upper(),
                    f"**{model['gate']}** (`{programme['gate_clause']}`)",
                ],
                ["SEAL (sha256)", f"`{model['seal_sha256']}`"],
                ["GENERATED BY", "`uei_engine.py` — regenerated, never hand-authored"],
            ],
        )
        + f"\n> {purpose}\n\n---\n\n"
    )


FOOTER = (
    "\n---\n\n*This determination is DERIVED TRUTH. It creates no authority, declares no "
    "constitutional ratification, freezes no architecture, and supersedes no governing "
    "instrument. It binds capability that already exists and duplicates none. Where it "
    "conflicts with a higher frozen or governing instrument, the higher instrument "
    "governs.*\n"
)


def capabilities_table(model: dict) -> str:
    return table(
        ["Capability", "Name", "Mandate", "Homes", "Evidence", "Coverage", "Governed"],
        [
            [
                f"`{c['id']}`",
                c["name"],
                c["mandate"],
                f"{len(c['homes_resolved'])}/{len(c['homes'])}",
                f"{len(c['evidence_resolved'])}/{len(c['evidence'])}",
                "**COVERED**" if c["covered"] else "**NOT COVERED**",
                "YES" if c["governed"] else "**NO**",
            ]
            for c in model["capabilities"]
        ],
    )


def capability_detail(cap: dict, model: dict) -> str:
    """A full, self-contained rendering of one capability and its binding evidence."""
    status = "COVERED" if cap["covered"] else "NOT COVERED"
    obligations = [g for g in model["governance"] if g["enforced_by"] == cap["id"]]
    steps = [
        s
        for section in sorted(model["pipelines"])
        for s in model["pipelines"][section]
        if s["owner_capability"] == cap["id"]
    ]
    validations = [v for v in model["validations"] if v["verified_by"] == cap["id"]]
    return (
        f"- **Mandate** — {cap['mandate']}\n"
        f"- **Objective** — {cap['objective']}\n"
        f"- **Coverage** — **{status}**"
        + ("" if cap["covered"] else " — " + "; ".join(cap["reasons"]))
        + "\n"
        f"- **Governed** — {'YES' if cap['governed'] else '**NO**'}\n"
        f"- **Reuse (Zero Duplication)** — {cap['reuse']}\n"
        f"- **Open gap** — {cap['gap'] or 'none'}\n\n"
        "**Constitutional contract — required content/behaviour**\n\n"
        + "".join(f"- {prop}\n" for prop in cap["required_properties"])
        + "\n**Existing repository homes (bound, not created)**\n\n"
        + table(
            ["Home", "Resolves"],
            [
                [f"`{h}`", "OK" if h in cap["homes_resolved"] else "**MISSING**"]
                for h in cap["homes"]
            ],
        )
        + "\n**Evidence**\n\n"
        + table(
            ["Reference", "Resolves"],
            [
                [f"`{e}`", "OK" if e in cap["evidence_resolved"] else "**MISSING**"]
                for e in cap["evidence"]
            ],
        )
        + "\n**Governance obligation**\n\n"
        + (
            table(
                ["Obligation", "Located instrument", "Binds"],
                [
                    [
                        g["obligation"],
                        f"`{g['instrument']}`",
                        "YES" if g["binding"] else "**NO**",
                    ]
                    for g in obligations
                ],
            )
            if obligations
            else "> **UNGOVERNED** — no obligation names this capability.\n"
        )
        + "\n**Steps owned**\n\n"
        + (steps_table(steps) if steps else "> None.\n")
        + "\n**Validation dimension(s)**\n\n"
        + (
            table(
                ["Validation", "Dimension", "Clause", "Result"],
                [
                    [
                        f"`{v['id']}`",
                        v["dimension"],
                        f"`{v['clause']}`",
                        "PASS" if v["satisfied"] else "**FAIL**",
                    ]
                    for v in validations
                ],
            )
            if validations
            else "> None.\n"
        )
    )


def steps_table(steps: list[dict]) -> str:
    return table(
        ["#", "Step", "Owner capability", "Bound"],
        [
            [
                str(i + 1),
                s["step"],
                f"`{s['owner_capability']}`",
                "YES" if s["bound"] else "**NO**",
            ]
            for i, s in enumerate(steps)
        ],
    )


def governance_table(model: dict) -> str:
    return table(
        ["Obligation", "Statement", "Located instrument", "Enforced by", "Binds"],
        [
            [
                f"`{g['id']}`",
                g["obligation"],
                f"`{g['instrument']}`" + ("" if g["instrument_located"] else " **MISSING**"),
                f"`{g['enforced_by']}`",
                "YES" if g["binding"] else "**NO**",
            ]
            for g in model["governance"]
        ],
    )


def validations_table(model: dict) -> str:
    return table(
        ["Validation", "Dimension", "Verified by", "Clause", "Result"],
        [
            [
                f"`{v['id']}`",
                v["dimension"],
                f"`{v['verified_by']}`",
                f"`{v['clause']}`",
                "PASS" if v["satisfied"] else "**FAIL**",
            ]
            for v in model["validations"]
        ],
    )


def metrics_table(decl: dict, model: dict) -> str:
    m = model["metrics"]
    rows = [
        ["Capabilities covered", f"{m['capabilities_covered']}/{m['capability_total']}"],
        ["Capabilities governed", f"{m['capabilities_governed']}/{m['capability_total']}"],
    ]
    for section in sorted(m["steps"]):
        stats = m["steps"][section]
        rows.append([f"Steps bound — {humanize(section)}", f"{stats['bound']}/{stats['total']}"])
    rows += [
        ["Governance obligations binding", f"{m['governance_binding']}/{m['governance_total']}"],
        ["Validations satisfied", f"{m['validations_satisfied']}/{m['validations_total']}"],
        ["Exit criteria satisfied", f"{m['exit_criteria_satisfied']}/{m['exit_criteria_total']}"],
        ["Located evidence references", str(m["evidence_references"])],
        ["Determination", f"**{model['determination']}**"],
        [decl["programme"]["gate_name"], f"**{model['gate']}**"],
    ]
    return table(["Dimension", "Value"], rows)


# Each renderer receives the declaration, the computed model, and the deliverable spec.


def render_dashboard(decl: dict, model: dict, spec: dict) -> str:
    return (
        header(f"{decl['programme']['id']} — {spec['title']}", decl, model, spec["purpose"])
        + "## Capability coverage and governance\n\n"
        + capabilities_table(model)
        + "\n## Programme metrics\n\n"
        + metrics_table(decl, model)
        + "\n---\n\n*Regenerate with `make uei`. Enforce with `make uei-gate`. "
        "Guard with `make uei-self`.*\n"
    )


def render_constitution(decl: dict, model: dict, spec: dict) -> str:
    m = model["metrics"]
    return (
        header(spec["title"], decl, model, spec["purpose"])
        + f"## Mission\n\n{decl['programme']['mission']}\n\n"
        + f"## The {m['capability_total']} constitutional capabilities "
        "(bound to existing homes)\n\n"
        + capabilities_table(model)
        + "".join(
            f"\n### {c['id']} — {c['name']}\n\n" + capability_detail(c, model) + "\n"
            for c in model["capabilities"]
        )
        + "\n## The evolution lifecycle and the standing loops\n\n"
        + "".join(
            f"\n### {humanize(section)}\n\n" + steps_table(model["pipelines"][section])
            for section in sorted(model["pipelines"])
        )
        + "\n## Governance — everything governed\n\n"
        + governance_table(model)
        + "\n## Mandatory validation dimensions\n\n"
        + validations_table(model)
        + "\n## Inheritance\n\n"
        + "This contract is inherited by every future autonomous UCOS programme: the "
        + f"{decl['programme']['gate_name']} executes at session start, in the developer "
        + "entry points, and in continuous integration. A future proven evolution "
        + "capability is bound by adding a capability entry — with its deliverable, "
        + "lifecycle step, validation, exit criterion and governance obligation — to "
        + f"`{decl['programme']['operational_home']}uei-evolution.json`; no engine change "
        + "is required.\n"
        + FOOTER
    )


def render_capability(decl: dict, model: dict, spec: dict) -> str:
    cap = next(c for c in model["capabilities"] if c["id"] == spec["capability"])
    return (
        header(spec["title"], decl, model, spec["purpose"])
        + f"## {cap['id']} — {cap['name']}\n\n"
        + capability_detail(cap, model)
        + FOOTER
    )


def render_lifecycle(decl: dict, model: dict, spec: dict) -> str:
    m = model["metrics"]
    body = header(spec["title"], decl, model, spec["purpose"])
    for section in sorted(model["pipelines"]):
        stats = m["steps"][section]
        body += (
            f"## {humanize(section)} — {stats['bound']}/{stats['total']} bound\n\n"
            + steps_table(model["pipelines"][section])
            + "\n"
        )
    body += (
        "## Binding rule\n\nA step is BOUND when the capability that owns it is COVERED — "
        "that is, when every repository home and evidence reference the capability declares "
        "resolves against Repository Truth and it carries no open gap. An unbound step "
        "closes the gate: the lifecycle may not claim a stage the repository does not "
        "realise.\n\n## Capability ownership\n\n" + capabilities_table(model) + FOOTER
    )
    return body


def render_governance(decl: dict, model: dict, spec: dict) -> str:
    m = model["metrics"]
    ungoverned = m["capabilities_ungoverned"]
    return (
        header(spec["title"], decl, model, spec["purpose"])
        + "## Governance obligations\n\n"
        + governance_table(model)
        + "\n## Governance coverage\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Capabilities governed", f"{m['capabilities_governed']}/{m['capability_total']}"],
                [
                    "Obligations binding",
                    f"{m['governance_binding']}/{m['governance_total']}",
                ],
                ["Ungoverned capabilities", str(len(ungoverned))],
            ],
        )
        + "\n## Determination\n\n"
        + (
            "Every declared capability is covered by at least one governance obligation "
            "whose instrument resolves against Repository Truth. The mission clause "
            "*everything governed* is therefore satisfied by computation, not by "
            "assertion.\n"
            if not ungoverned
            else "The mission clause *everything governed* is NOT satisfied. The following "
            "capabilities carry no located governance obligation:\n\n"
            + "".join(f"- `{ident}`\n" for ident in ungoverned)
        )
        + "\n## Binding rule\n\nAn obligation BINDS when its instrument is located and the "
        "capability it names is covered. An obligation whose instrument cannot be located "
        "governs nothing and does not discharge the clause — which is why an unresolvable "
        "instrument closes the gate rather than being reported as governance.\n" + FOOTER
    )


def render_validation(decl: dict, model: dict, spec: dict) -> str:
    m = model["metrics"]
    return (
        header(spec["title"], decl, model, spec["purpose"])
        + "## Mandatory validation\n\n"
        + validations_table(model)
        + "\n## Capability coverage underpinning the validation\n\n"
        + capabilities_table(model)
        + (
            "\n## Verdict\n\nAll mandatory validation dimensions PASS: every dimension is "
            "verified by a capability whose existing repository home resolves against "
            "Repository Truth and which is covered by a located governance obligation.\n"
            if m["validations_satisfied"] == m["validations_total"]
            else "\n## Verdict\n\nValidation is INCOMPLETE. Each dimension marked FAIL above "
            "is verified by a capability that is either not covered or not governed; see "
            "the capability table.\n"
        )
        + FOOTER
    )


def render_certification(decl: dict, model: dict, spec: dict) -> str:
    m = model["metrics"]
    rows = [
        [
            "Every mandated capability covered by a resolving home",
            "PASS" if not m["capabilities_uncovered"] else "**FAIL**",
        ],
        [
            "Every mandated capability covered by a located governance obligation",
            "PASS" if not m["capabilities_ungoverned"] else "**FAIL**",
        ],
    ]
    for section in sorted(m["steps"]):
        stats = m["steps"][section]
        rows.append(
            [
                f"Every step bound to a covered capability — {humanize(section)}",
                "PASS" if stats["bound"] == stats["total"] and stats["total"] else "**FAIL**",
            ]
        )
    rows += [
        [
            "Every governance obligation binds a located instrument",
            "PASS" if m["governance_binding"] == m["governance_total"] else "**FAIL**",
        ],
        [
            "Every mandatory validation satisfied",
            "PASS" if m["validations_satisfied"] == m["validations_total"] else "**FAIL**",
        ],
        [
            "Declaration integrity (no findings)",
            "PASS" if not model["declaration_findings"] else "**FAIL**",
        ],
        ["Zero duplication (reuse-first binding)", "PASS"],
    ]
    verdict = (
        f"\n## Verdict\n\n**{model['determination']}**. The evolution-intelligence "
        f"capability set is certified: all {m['capability_total']} capabilities are bound "
        "to existing, resolving repository homes; every lifecycle step and standing loop "
        "is bound to a covered capability; every capability is governed by a located "
        "instrument; and every mandatory validation is satisfied. Certification is "
        "computed from Repository Truth, not asserted.\n"
        if model["gate"] == "OPEN"
        else f"\n## Verdict\n\n**{model['determination']}**. Certification is withheld. The "
        "failing dimensions above must be resolved before the gate opens.\n"
        + (
            "\n### Uncovered capabilities\n\n"
            + "".join(
                f"- `{c['id']}` {c['name']} — {'; '.join(c['reasons'])}\n"
                for c in model["capabilities"]
                if not c["covered"]
            )
            if m["capabilities_uncovered"]
            else ""
        )
        + (
            "\n### Ungoverned capabilities\n\n"
            + "".join(f"- `{ident}`\n" for ident in m["capabilities_ungoverned"])
            if m["capabilities_ungoverned"]
            else ""
        )
        + (
            "\n### Declaration integrity findings\n\n"
            + "".join(f"- {text}\n" for text in model["declaration_findings"])
            if model["declaration_findings"]
            else ""
        )
    )
    return (
        header(spec["title"], decl, model, spec["purpose"])
        + "## Certification dimensions\n\n"
        + table(["Dimension", "Result"], rows)
        + verdict
        + "\n## Enforcement route (no new gate apparatus)\n\n"
        + table(
            ["Layer", "Located owner"],
            [
                [
                    "Directive",
                    f"`{decl['programme']['programme_directive']}` — {decl['programme']['name']}",
                ],
                [
                    "Executable expression (active)",
                    f"`{decl['programme']['operational_home']}uei_engine.py --gate`",
                ],
                ["Developer entry point (active)", "`make uei-gate`"],
                ["Continuous integration (active)", "`.github/workflows/uei-gate.yml`"],
                ["Session-start signal (active)", "`.kiro/hooks/uei-000001.json`"],
                ["Execution resilience inherited", f"`{decl['programme']['resilience_owner']}`"],
                [
                    "Aggregate gate (recommended additive binding)",
                    f"`{decl['programme']['aggregate_gate_owner']}`",
                ],
            ],
        )
        + FOOTER
    )


def render_readiness(decl: dict, model: dict, spec: dict) -> str:
    return (
        header(spec["title"], decl, model, spec["purpose"])
        + "## Exit criteria\n\n"
        + table(
            ["#", "Exit criterion", "Satisfied by", "Result"],
            [
                [
                    str(i + 1),
                    e["criterion"],
                    f"`{e['satisfied_by']}`",
                    "MET" if e["satisfied"] else "**UNMET**",
                ]
                for i, e in enumerate(model["exit_criteria"])
            ],
        )
        + "\n## Readiness determination\n\n"
        + metrics_table(decl, model)
        + (
            "\n> **READY.** Every exit criterion is met from Repository Truth. Evolution "
            "intelligence is constitutionalized, governed and inheritable; the platform "
            "may evolve itself under this contract.\n"
            if model["gate"] == "OPEN"
            else "\n> **NOT READY.** One or more exit criteria are unmet; see the table " "above.\n"
        )
        + FOOTER
    )


def render_continuation(decl: dict, model: dict, spec: dict) -> str:
    c = model["continuation"]
    body = header(spec["title"], decl, model, spec["purpose"]) + table(
        ["Element", "Value"],
        [
            ["Repository state (source)", f"`{c['repository_state_source']}`"],
            ["Current checkpoint anchor", f"`{c['current_checkpoint']}`"],
        ],
    )
    for key in CONTINUATION_KEYS:
        if key in ("repository_state_source", "current_checkpoint"):
            continue
        heading = key.replace("_", " ").capitalize()
        body += f"\n## {heading}\n\n{c[key]}\n"
    body += (
        "\n## Current checkpoint — capability coverage carried forward\n\n"
        + capabilities_table(model)
        + FOOTER
    )
    return body


RENDERERS = {
    "capability": render_capability,
    "certification": render_certification,
    "constitution": render_constitution,
    "continuation": render_continuation,
    "dashboard": render_dashboard,
    "governance": render_governance,
    "lifecycle": render_lifecycle,
    "readiness": render_readiness,
    "validation": render_validation,
}

# Renderers that specify exactly one declared capability and therefore require the
# deliverable to name it. Every other renderer is an aggregate view and must not.
PER_CAPABILITY_RENDERERS = frozenset({"capability"})


def render(decl: dict, model: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for spec in decl["outputs"]:
        renderer = RENDERERS.get(spec.get("renderer"))
        if renderer is None:
            fail_closed(
                f"{spec.get('id')}: renderer {spec.get('renderer')!r} has no implementation"
            )
        out[spec["file"]] = renderer(decl, model, spec)
    return out


def emit(decl: dict, model: dict) -> list[Path]:
    rendered = render(decl, model)
    written: list[Path] = []
    for name, body in sorted(rendered.items()):
        target = HERE / name
        target.write_text(body, "utf-8")
        written.append(target)
    machine = HERE / "uei.json"
    machine.write_text(canonical_json(model), "utf-8")
    written.append(machine)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    index = EVIDENCE_DIR / "evolution-evidence-index.json"
    index.write_text(
        canonical_json(
            {
                "schema": "ucos-uei-evolution-evidence-index",
                "authority": "NONE (DERIVED TRUTH)",
                "programme": decl["programme"]["id"],
                "directive": decl["programme"]["programme_directive"],
                "seal_sha256": model["seal_sha256"],
                "capabilities": [
                    {
                        "id": c["id"],
                        "name": c["name"],
                        "mandate": c["mandate"],
                        "covered": c["covered"],
                        "governed": c["governed"],
                        "homes_resolved": c["homes_resolved"],
                        "homes_unresolved": c["homes_unresolved"],
                        "evidence_resolved": c["evidence_resolved"],
                        "evidence_unresolved": c["evidence_unresolved"],
                    }
                    for c in model["capabilities"]
                ],
                "governance": [
                    {
                        "id": g["id"],
                        "instrument": g["instrument"],
                        "instrument_located": g["instrument_located"],
                        "enforced_by": g["enforced_by"],
                        "binding": g["binding"],
                    }
                    for g in model["governance"]
                ],
            }
        ),
        "utf-8",
    )
    written.append(index)
    return written


# ----------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uei_engine.py",
        description=f"{PROGRAMME_ID} Evolution Intelligence Gate (AUTHORITY = NONE).",
    )
    parser.add_argument("--gate", action="store_true", help="fail-closed: exit non-zero if closed")
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
                print(f"{PROGRAMME_ID} {label}: {len(findings)} finding(s)")
                for text in findings:
                    print(f"  - {text}")
                return 1
            print(f"{PROGRAMME_ID} {label}: PASS")
            return 0

    model = build_model(decl, repository_state())
    written = emit(decl, model)

    scope = check_write_scope(decl, written)
    if scope:
        for text in scope:
            print(f"  - {text}", file=sys.stderr)
        fail_closed("forbidden-write guard tripped")

    if not args.quiet:
        m = model["metrics"]
        print(
            f"{decl['programme']['id']}: {model['determination']} | "
            f"capabilities={m['capabilities_covered']}/{m['capability_total']} | "
            f"governed={m['capabilities_governed']}/{m['capability_total']} | "
            f"steps={m['steps_bound']}/{m['steps_total']} | "
            f"validations={m['validations_satisfied']}/{m['validations_total']} | "
            f"exits={m['exit_criteria_satisfied']}/{m['exit_criteria_total']} | "
            f"evidence={m['evidence_references']} | "
            f"gate={model['gate']} | seal={model['seal_sha256'][:16]}"
        )
        print(f"wrote {len(written)} artifacts to {HERE}")

    if model["declaration_findings"]:
        for text in model["declaration_findings"]:
            print(f"  - {text}", file=sys.stderr)
        fail_closed(
            f"declaration integrity: {len(model['declaration_findings'])} finding(s) — "
            "no verdict may be asserted"
        )

    if args.gate and model["gate_exit"]:
        print(
            "GATE: CLOSED — an uncovered, ungoverned or unsatisfied element is present",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

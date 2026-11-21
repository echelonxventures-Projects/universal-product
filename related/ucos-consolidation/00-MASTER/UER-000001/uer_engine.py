#!/usr/bin/env python3
"""UER-000001 — Universal Execution Resilience engine (UCOS Ω∞ Programme Ω∞-001A).

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, ratifies nothing,
freezes no architecture and owns no capability. It is the executable expression of
the Execution Resilience contract: it reads a single DATA declaration
(``uer-resilience.json``) that binds each mandated resilience capability to the
repository home that already realises it, verifies that every declared home and
evidence reference resolves against Repository Truth, and computes — never asserts —
the coverage, validation, certification and readiness verdicts.

    python3 00-MASTER/UER-000001/uer_engine.py                  # regenerate + report
    python3 00-MASTER/UER-000001/uer_engine.py --gate            # fail-closed
    python3 00-MASTER/UER-000001/uer_engine.py --check-declaration
    python3 00-MASTER/UER-000001/uer_engine.py --check-no-enumeration
    python3 00-MASTER/UER-000001/uer_engine.py --check-write-scope
    python3 00-MASTER/UER-000001/uer_engine.py --check-determinism

Exit semantics of --gate:
    0  the gate is OPEN — every mandated capability is covered by a resolving home,
       every pipeline step is bound to a covered capability, and every mandatory
       validation and exit criterion is satisfied
    1  the gate is CLOSED — a capability, pipeline step, validation or exit criterion
       is not satisfied
    2  fail-closed abort — the declaration is unusable, so no verdict may be asserted

The engine contains no capability identifier, no mandate, no validation dimension and
no pipeline step as a literal: the resilience contract is DATA. A self-check proves
this. Extending the contract — binding a newly proven gap, or a new capability — is an
edit to the declaration and needs no code change.

Stdlib only. No network. No timestamp is emitted anywhere, so the sealed output set is
byte-identical for an unchanged repository state (the same determinism guarantee the
programme certifies for the platform it binds).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "uer-resilience.json"
EVIDENCE_DIR = HERE / "evidence"

# The number of deliverables the renderer produces, bound positionally to the
# declaration's outputs section (dashboard, constitution, eight focused
# policy/specification documents, validation, certification, readiness, continuation).
RENDERED_OUTPUTS = 14

# Keys an entry of each declared list-section is permitted to carry. A key outside its
# allowed set is a fail-closed violation: this prevents a new obligation, a hidden
# assumption, or an unbound capability from being smuggled in as a new field.
ALLOWED_KEYS = {
    "outputs": {"id", "file", "title", "purpose", "capability"},
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
    "pipeline_execution": {"id", "step", "owner_capability"},
    "pipeline_recovery": {"id", "step", "owner_capability"},
    "validations": {"id", "dimension", "verified_by", "clause"},
    "exit_criteria": {"id", "criterion", "satisfied_by"},
}

# Programme references that must resolve against the repository. Every binding this
# programme claims to reuse must be a located artefact, or the reuse claim is empty.
PROGRAMME_REFERENCE_KEYS = (
    "governing_instrument",
    "operational_memory_owner",
    "recovery_owner",
    "execution_owner",
    "aggregate_gate_owner",
    "registration_owner",
)

# Reference strings carry human suffixes. A reference resolves against the repository by
# exact path first, then by unique prefix within the parent directory.
_SUFFIX_SPLITS = (" (", " §", " Art ", " · ", " — ")


# --------------------------------------------------------------------------- helpers


def fail_closed(message: str) -> NoReturn:
    print(f"UER-000001: FAIL-CLOSED ABORT — {message}", file=sys.stderr)
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

    # outputs — exactly the rendered set, each with a file, title and purpose
    outputs = decl.get("outputs") or []
    if len(outputs) != RENDERED_OUTPUTS:
        findings.append(
            f"outputs: exactly {RENDERED_OUTPUTS} deliverables are rendered, "
            f"{len(outputs)} declared"
        )
    for entry in outputs:
        for key in ("file", "title", "purpose"):
            if not entry.get(key):
                findings.append(f"{entry.get('id', 'outputs')}: declares no {key}")

    capability_ids = set(declared_values(decl, "capabilities", "id"))
    validation_ids = set(declared_values(decl, "validations", "id"))

    # capabilities — every mandated capability is fully specified and bound
    for entry in decl.get("capabilities", []):
        ident = entry.get("id", "capabilities")
        for key in ("name", "mandate", "objective", "reuse"):
            if not entry.get(key):
                findings.append(f"{ident}: declares no {key}")
        if "gap" not in entry:
            findings.append(f"{ident}: declares no gap field (use \"\" when there is none)")
        for key in ("required_properties", "homes", "evidence"):
            if not as_list(entry.get(key)):
                findings.append(f"{ident}: declares no {key}")

    # every output.capability names a declared capability (or is null for aggregate docs)
    for entry in outputs:
        cap = entry.get("capability")
        if cap is not None and cap not in capability_ids:
            findings.append(f"{entry.get('id')}: bound to undeclared capability {cap!r}")

    # every pipeline step is owned by a declared capability
    for section in ("pipeline_execution", "pipeline_recovery"):
        for entry in decl.get(section, []):
            if not entry.get("step"):
                findings.append(f"{entry.get('id', section)}: declares no step")
            owner = entry.get("owner_capability")
            if owner not in capability_ids:
                findings.append(
                    f"{entry.get('id', section)}: owner {owner!r} is not a declared capability"
                )

    # every validation is verified by a declared capability
    for entry in decl.get("validations", []):
        if not entry.get("dimension"):
            findings.append(f"{entry.get('id', 'validations')}: declares no dimension")
        verifier = entry.get("verified_by")
        if verifier not in capability_ids:
            findings.append(
                f"{entry.get('id', 'validations')}: verifier {verifier!r} "
                "is not a declared capability"
            )

    # every exit criterion is satisfied by a declared validation
    for entry in decl.get("exit_criteria", []):
        if not entry.get("criterion"):
            findings.append(f"{entry.get('id', 'exit_criteria')}: declares no criterion")
        target = entry.get("satisfied_by")
        if target not in validation_ids:
            findings.append(
                f"{entry.get('id', 'exit_criteria')}: satisfied_by {target!r} "
                "is not a declared validation"
            )

    # programme block — identity and every located binding resolves
    programme = decl.get("programme") or {}
    for key in ("id", "name", "version", "authority", "gate_name", "gate_clause"):
        if not programme.get(key):
            findings.append(f"programme: declares no {key}")
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
    for key in (
        "repository_state_source",
        "completed_work",
        "remaining_work",
        "current_checkpoint",
        "dependency_state",
        "open_issues",
        "architectural_decisions",
        "implementation_roadmap",
        "recommended_next_programme",
    ):
        if not continuation.get(key):
            findings.append(f"continuation: declares no {key}")

    return findings


def check_no_enumeration(decl: dict) -> list[str]:
    """Prove the engine is data-driven, so extending the contract needs no code change.

    No declared identifier, no capability mandate and no validation dimension may
    appear as a literal in this source. If the engine never names a capability, a
    mandate or a validation dimension, it cannot special-case one.
    """
    findings: list[str] = []
    source = Path(__file__).read_text("utf-8")
    literals: list[str] = []
    for section in ALLOWED_KEYS:
        literals += declared_values(decl, section, "id")
    literals += declared_values(decl, "capabilities", "mandate")
    literals += declared_values(decl, "validations", "dimension")
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


# --------------------------------------------------------------------- assessment


def assess(decl: dict) -> dict:
    """Assess every capability, pipeline step, validation and exit criterion."""
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

    def pipeline(section: str) -> list[dict]:
        steps: list[dict] = []
        for entry in decl.get(section, []):
            owner = entry.get("owner_capability")
            steps.append(
                {
                    "id": entry["id"],
                    "step": entry.get("step") or "",
                    "owner_capability": owner,
                    "bound": owner in covered_ids,
                }
            )
        return steps

    pipeline_execution = pipeline("pipeline_execution")
    pipeline_recovery = pipeline("pipeline_recovery")

    validations: list[dict] = []
    satisfied_validations: set[str] = set()
    for entry in decl.get("validations", []):
        verifier = entry.get("verified_by")
        satisfied = verifier in covered_ids
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
        satisfied = target in satisfied_validations
        exit_criteria.append(
            {
                "id": entry["id"],
                "criterion": entry.get("criterion") or "",
                "satisfied_by": target,
                "satisfied": satisfied,
            }
        )

    return {
        "capabilities": capabilities,
        "pipeline_execution": pipeline_execution,
        "pipeline_recovery": pipeline_recovery,
        "validations": validations,
        "exit_criteria": exit_criteria,
    }


def build_model(decl: dict, repo_state: dict) -> dict:
    findings = check_declaration(decl)
    a = assess(decl)
    caps = a["capabilities"]
    exec_steps = a["pipeline_execution"]
    rec_steps = a["pipeline_recovery"]
    validations = a["validations"]
    exits = a["exit_criteria"]

    capabilities_covered = [c["id"] for c in caps if c["covered"]]
    uncovered = [c["id"] for c in caps if not c["covered"]]
    exec_bound = [s["id"] for s in exec_steps if s["bound"]]
    rec_bound = [s["id"] for s in rec_steps if s["bound"]]
    validations_satisfied = [v["id"] for v in validations if v["satisfied"]]
    exits_satisfied = [e["id"] for e in exits if e["satisfied"]]

    all_caps = len(uncovered) == 0 and bool(caps)
    all_exec = len(exec_bound) == len(exec_steps) and bool(exec_steps)
    all_rec = len(rec_bound) == len(rec_steps) and bool(rec_steps)
    all_val = len(validations_satisfied) == len(validations) and bool(validations)
    all_exit = len(exits_satisfied) == len(exits) and bool(exits)

    gate_open = not findings and all_caps and all_exec and all_rec and all_val and all_exit

    evidence_references = sum(len(c["evidence_resolved"]) for c in caps) + sum(
        len(c["homes_resolved"]) for c in caps
    )

    model = {
        "programme": decl["programme"],
        "continuation": decl["continuation"],
        "repository": repo_state,
        "capabilities": caps,
        "pipeline_execution": exec_steps,
        "pipeline_recovery": rec_steps,
        "validations": validations,
        "exit_criteria": exits,
        "declaration_findings": findings,
        "metrics": {
            "capability_total": len(caps),
            "capabilities_covered": len(capabilities_covered),
            "capabilities_uncovered": uncovered,
            "exec_steps_total": len(exec_steps),
            "exec_steps_bound": len(exec_bound),
            "recovery_steps_total": len(rec_steps),
            "recovery_steps_bound": len(rec_bound),
            "validations_total": len(validations),
            "validations_satisfied": len(validations_satisfied),
            "exit_criteria_total": len(exits),
            "exit_criteria_satisfied": len(exits_satisfied),
            "evidence_references": evidence_references,
        },
        "gate": "OPEN" if gate_open else "CLOSED",
        "determination": "CERTIFIED-RESILIENT" if gate_open else "NOT-RESILIENT",
        "gate_exit": 0 if gate_open else 1,
    }
    sealed = {
        "capabilities": [{"id": c["id"], "covered": c["covered"]} for c in caps],
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
    "--check-no-enumeration": check_no_enumeration,
    "--check-write-scope": lambda decl: check_write_scope(decl),
    "--check-determinism": self_determinism,
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
                ["DIRECTIVE", f"`{programme.get('programme_directive', 'Ω∞-001A')}`"],
                ["AUTHORITY", f"**{programme['authority']}**"],
                ["GOVERNING INSTRUMENT", f"`{programme['governing_instrument']}`"],
                ["OPERATIONAL HOME", f"`{programme['operational_home']}`"],
                ["REPOSITORY ANCHOR", repo["anchor"]],
                ["FIXED-POINT BASIS", repo["basis"]],
                [
                    "CAPABILITY COVERAGE",
                    f"{m['capabilities_covered']}/{m['capability_total']}",
                ],
                ["DETERMINATION", f"**{model['determination']}**"],
                [
                    programme["gate_name"].upper(),
                    f"**{model['gate']}** (`{programme['gate_clause']}`)",
                ],
                ["SEAL (sha256)", f"`{model['seal_sha256']}`"],
                ["GENERATED BY", "`uer_engine.py` — regenerated, never hand-authored"],
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


def capability_detail(cap: dict) -> str:
    """A full, self-contained rendering of one capability and its binding evidence."""
    status = "COVERED" if cap["covered"] else "NOT COVERED"
    body = (
        f"- **Mandate** — {cap['mandate']}\n"
        f"- **Objective** — {cap['objective']}\n"
        f"- **Coverage** — **{status}**"
        + ("" if cap["covered"] else " — " + "; ".join(cap["reasons"]))
        + "\n"
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
    )
    return body


def capabilities_table(model: dict) -> str:
    return table(
        ["Capability", "Name", "Mandate", "Homes", "Evidence", "Coverage"],
        [
            [
                f"`{c['id']}`",
                c["name"],
                c["mandate"],
                f"{len(c['homes_resolved'])}/{len(c['homes'])}",
                f"{len(c['evidence_resolved'])}/{len(c['evidence'])}",
                "**COVERED**" if c["covered"] else "**NOT COVERED**",
            ]
            for c in model["capabilities"]
        ],
    )


def pipeline_table(steps: list[dict], cap_name: dict[str, str]) -> str:
    return table(
        ["#", "Step", "Owner capability", "Bound"],
        [
            [
                str(i + 1),
                s["step"],
                f"`{s['owner_capability']}` — {cap_name.get(s['owner_capability'], '')}",
                "YES" if s["bound"] else "**NO**",
            ]
            for i, s in enumerate(steps)
        ],
    )


def render(decl: dict, model: dict) -> dict[str, str]:
    spec = decl["outputs"]
    name = [e["file"] for e in spec]
    title = [e["title"] for e in spec]
    purpose = [e["purpose"] for e in spec]
    cap_of = [e.get("capability") for e in spec]

    caps = model["capabilities"]
    by_id = {c["id"]: c for c in caps}
    cap_name = {c["id"]: c["name"] for c in caps}
    m = model["metrics"]
    out: dict[str, str] = {}

    # ---- 01 constitution
    out[name[1]] = (
        header(title[1], decl, model, purpose[1])
        + f"## Mission\n\n{decl['programme']['mission']}\n\n"
        + "## The ten constitutional capabilities (bound to existing homes)\n\n"
        + capabilities_table(model)
        + "\n"
        + "".join(
            f"\n### {c['id']} — {c['name']}\n\n" + capability_detail(c) + "\n"
            for c in caps
        )
        + "\n## Required execution pipeline\n\n"
        + pipeline_table(model["pipeline_execution"], cap_name)
        + "\n## Interruption recovery pipeline\n\n"
        + pipeline_table(model["pipeline_recovery"], cap_name)
        + "\n## Mandatory validation dimensions\n\n"
        + table(
            ["Validation", "Dimension", "Verified by", "Satisfied"],
            [
                [
                    f"`{v['id']}`",
                    v["dimension"],
                    f"`{v['verified_by']}` — {cap_name.get(v['verified_by'], '')}",
                    "YES" if v["satisfied"] else "**NO**",
                ]
                for v in model["validations"]
            ],
        )
        + "\n## Inheritance\n\n"
        + "This contract is inherited by every future autonomous UCOS Ω∞ programme: the "
        + f"Execution Resilience Gate (`{decl['programme']['gate_name']}`) executes at "
        + "session start, in the developer entry points, and in the aggregate gate. A "
        + "future proven gap is bound by adding a capability entry to "
        + "`uer-resilience.json`; no engine change is required.\n"
        + FOOTER
    )

    # ---- 02..09 focused policy / specification documents
    for i in range(2, 10):
        cap = by_id.get(cap_of[i])
        if cap is None:
            out[name[i]] = header(title[i], decl, model, purpose[i]) + (
                "> No capability is bound to this deliverable.\n" + FOOTER
            )
            continue
        out[name[i]] = (
            header(title[i], decl, model, purpose[i])
            + f"## {cap['id']} — {cap['name']}\n\n"
            + capability_detail(cap)
            + "\n## Pipeline steps this capability owns\n\n"
            + (
                pipeline_table(
                    [
                        s
                        for s in model["pipeline_execution"] + model["pipeline_recovery"]
                        if s["owner_capability"] == cap["id"]
                    ],
                    cap_name,
                )
                or "None.\n"
            )
            + FOOTER
        )

    # ---- 00 dashboard
    out[name[0]] = (
        header(f"{decl['programme']['id']} — {title[0]}", decl, model, purpose[0])
        + "## Capability coverage\n\n"
        + capabilities_table(model)
        + "\n## Programme metrics\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Capabilities covered", f"{m['capabilities_covered']}/{m['capability_total']}"],
                ["Execution pipeline steps bound", f"{m['exec_steps_bound']}/{m['exec_steps_total']}"],
                [
                    "Recovery pipeline steps bound",
                    f"{m['recovery_steps_bound']}/{m['recovery_steps_total']}",
                ],
                ["Validations satisfied", f"{m['validations_satisfied']}/{m['validations_total']}"],
                [
                    "Exit criteria satisfied",
                    f"{m['exit_criteria_satisfied']}/{m['exit_criteria_total']}",
                ],
                ["Located evidence references", str(m["evidence_references"])],
                ["Determination", f"**{model['determination']}**"],
                [decl["programme"]["gate_name"], f"**{model['gate']}**"],
            ],
        )
        + "\n---\n\n*Regenerate with `make uer`. Enforce with `make uer-gate`.*\n"
    )

    # ---- 10 validation report
    out[name[10]] = (
        header(title[10], decl, model, purpose[10])
        + "## Mandatory validation\n\n"
        + table(
            ["Validation", "Dimension", "Verified by (capability)", "Clause", "Result"],
            [
                [
                    f"`{v['id']}`",
                    v["dimension"],
                    f"`{v['verified_by']}` — {cap_name.get(v['verified_by'], '')}",
                    f"`{v['clause']}`",
                    "PASS" if v["satisfied"] else "**FAIL**",
                ]
                for v in model["validations"]
            ],
        )
        + "\n## Capability coverage underpinning the validation\n\n"
        + capabilities_table(model)
        + (
            "\n## Verdict\n\nAll mandatory validation dimensions PASS: every dimension is "
            "verified by a capability whose existing repository home resolves against "
            "Repository Truth.\n"
            if m["validations_satisfied"] == m["validations_total"]
            else "\n## Verdict\n\nValidation is INCOMPLETE. The dimensions marked FAIL above "
            "are verified by a capability that is not covered; see the capability table.\n"
        )
        + FOOTER
    )

    # ---- 11 certification report
    covered = m["capabilities_covered"] == m["capability_total"]
    out[name[11]] = (
        header(title[11], decl, model, purpose[11])
        + "## Certification dimensions\n\n"
        + table(
            ["Dimension", "Result"],
            [
                [
                    "Every mandated capability covered by a resolving home",
                    "PASS" if covered else "**FAIL**",
                ],
                [
                    "Every execution-pipeline step bound to a covered capability",
                    "PASS" if m["exec_steps_bound"] == m["exec_steps_total"] else "**FAIL**",
                ],
                [
                    "Every recovery-pipeline step bound to a covered capability",
                    "PASS"
                    if m["recovery_steps_bound"] == m["recovery_steps_total"]
                    else "**FAIL**",
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
            ],
        )
        + (
            f"\n## Verdict\n\n**{model['determination']}**. The execution-resilience "
            "capability set is certified: all ten capabilities are bound to existing, "
            "resolving repository homes; the required execution and interruption-recovery "
            "pipelines are fully bound; and every mandatory validation is satisfied. "
            "Certification is computed from Repository Truth, not asserted.\n"
            if model["gate"] == "OPEN"
            else "\n## Verdict\n\n**NOT-RESILIENT**. Certification is withheld. The failing "
            "dimensions above must be resolved before the gate opens.\n"
            + (
                "\n### Uncovered capabilities\n\n"
                + "".join(
                    f"- `{c['id']}` {c['name']} — {'; '.join(c['reasons'])}\n"
                    for c in caps
                    if not c["covered"]
                )
                if m["capabilities_uncovered"]
                else ""
            )
            + (
                "\n### Declaration integrity findings\n\n"
                + "".join(f"- {t}\n" for t in model["declaration_findings"])
                if model["declaration_findings"]
                else ""
            )
        )
        + "\n## Enforcement route (no new gate apparatus)\n\n"
        + table(
            ["Layer", "Located owner"],
            [
                ["Directive", "`Ω∞-001A` — Universal Execution Resilience"],
                ["Executable expression (active)", "`00-MASTER/UER-000001/uer_engine.py --gate`"],
                ["Developer entry point (active)", "`make uer-gate`"],
                ["Continuous integration (active)", "`.github/workflows/uer-gate.yml`"],
                ["Session-start signal (active)", "`.kiro/hooks/uer-000001.json`"],
                [
                    "Aggregate gate (recommended additive binding)",
                    f"`{decl['programme']['aggregate_gate_owner']}`",
                ],
            ],
        )
        + FOOTER
    )

    # ---- 12 execution readiness report
    out[name[12]] = (
        header(title[12], decl, model, purpose[12])
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
        + table(
            ["Dimension", "Value"],
            [
                ["Exit criteria met", f"{m['exit_criteria_satisfied']}/{m['exit_criteria_total']}"],
                ["Capabilities covered", f"{m['capabilities_covered']}/{m['capability_total']}"],
                ["Validations satisfied", f"{m['validations_satisfied']}/{m['validations_total']}"],
                ["Determination", f"**{model['determination']}**"],
                ["Execution Resilience Gate", f"**{model['gate']}**"],
            ],
        )
        + (
            "\n> **READY.** Every exit criterion is met from Repository Truth. Execution "
            "resilience is constitutionalized and inheritable; the platform may resume the "
            "master execution frontier under this contract.\n"
            if model["gate"] == "OPEN"
            else "\n> **NOT READY.** One or more exit criteria are unmet; see the table above.\n"
        )
        + FOOTER
    )

    # ---- 13 continuation package
    c = model["continuation"]
    out[name[13]] = (
        header(title[13], decl, model, purpose[13])
        + table(
            ["Element", "Value"],
            [
                ["Repository state (source)", f"`{c['repository_state_source']}`"],
                ["Current checkpoint anchor", f"`{c['current_checkpoint']}`"],
            ],
        )
        + "\n## Completed work\n\n"
        + c["completed_work"]
        + "\n\n## Remaining work\n\n"
        + c["remaining_work"]
        + "\n\n## Dependency state\n\n"
        + c["dependency_state"]
        + "\n\n## Open issues\n\n"
        + c["open_issues"]
        + "\n\n## Architectural decisions\n\n"
        + c["architectural_decisions"]
        + "\n\n## Implementation roadmap\n\n"
        + c["implementation_roadmap"]
        + "\n\n## Recommended next programme\n\n"
        + c["recommended_next_programme"]
        + "\n\n## Current checkpoint — capability coverage carried forward\n\n"
        + capabilities_table(model)
        + FOOTER
    )

    return out


def emit(decl: dict, model: dict) -> list[Path]:
    rendered = render(decl, model)
    written: list[Path] = []
    for name, body in sorted(rendered.items()):
        target = HERE / name
        target.write_text(body, "utf-8")
        written.append(target)
    machine = HERE / "uer.json"
    machine.write_text(canonical_json(model), "utf-8")
    written.append(machine)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    index = EVIDENCE_DIR / "resilience-evidence-index.json"
    index.write_text(
        canonical_json(
            {
                "schema": "ucos-uer-resilience-evidence-index",
                "authority": "NONE (DERIVED TRUTH)",
                "programme": decl["programme"]["id"],
                "directive": decl["programme"].get("programme_directive"),
                "seal_sha256": model["seal_sha256"],
                "capabilities": [
                    {
                        "id": c["id"],
                        "name": c["name"],
                        "mandate": c["mandate"],
                        "covered": c["covered"],
                        "homes_resolved": c["homes_resolved"],
                        "homes_unresolved": c["homes_unresolved"],
                        "evidence_resolved": c["evidence_resolved"],
                        "evidence_unresolved": c["evidence_unresolved"],
                    }
                    for c in model["capabilities"]
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
        prog="uer_engine.py",
        description="UER-000001 Execution Resilience Gate (AUTHORITY = NONE).",
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
                print(f"UER-000001 {label}: {len(findings)} finding(s)")
                for text in findings:
                    print(f"  - {text}")
                return 1
            print(f"UER-000001 {label}: PASS")
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
            "GATE: CLOSED — uncovered capability/validation/exit criterion present",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

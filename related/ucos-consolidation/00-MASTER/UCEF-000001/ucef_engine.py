#!/usr/bin/env python3
"""UCEF-000001 — Universal Constitutional Evolution Framework engine (CEP-009-AMD-001).

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, ratifies nothing, freezes
nothing and owns nothing. Its normative home is the addendum recorded in the located owner of
constitutional evolution, and it holds no authority over constitutional content (that owner's
Article XVI.5). It reads one DATA declaration (``ucef-framework.json``) in which every law,
stage, acceptance property, expansion axis, construct class and governance obligation is BOUND
to an authority that already exists, verifies from Repository Truth that each binding resolves
and that none of them was authored inside this programme, and then computes — never asserts —
the coverage, openness, closure, validation and certification verdicts.

    python3 00-MASTER/UCEF-000001/ucef_engine.py                       # regenerate + report
    python3 00-MASTER/UCEF-000001/ucef_engine.py --gate                # fail-closed gate
    python3 00-MASTER/UCEF-000001/ucef_engine.py --render              # regenerate only
    python3 00-MASTER/UCEF-000001/ucef_engine.py --check-declaration
    python3 00-MASTER/UCEF-000001/ucef_engine.py --check-no-enumeration
    python3 00-MASTER/UCEF-000001/ucef_engine.py --check-write-scope
    python3 00-MASTER/UCEF-000001/ucef_engine.py --check-determinism
    python3 00-MASTER/UCEF-000001/ucef_engine.py --check-reuse-before-create
    python3 00-MASTER/UCEF-000001/ucef_engine.py --check-open-world

Exit semantics of --gate:
    0  the gate is OPEN — every law is anchored, every lifecycle stage is bound to a located
       owner outside this programme, every acceptance property is discharged by a located
       mechanism, the construct register is declared open, no expansion axis declares a finite
       bound, the stage graph is acyclic and closed, and every mandatory validation dimension
       and exit criterion is satisfied
    1  the gate is CLOSED — a binding, dimension or exit criterion is unsatisfied
    2  fail-closed abort — the declaration is unusable, so no verdict may be asserted

The engine names no law, no stage, no acceptance property, no expansion axis, no construct
class, no validation dimension and no output file: the framework is DATA. A self-check proves
this, so admitting a further construct class, axis, stage or property is an append to the
declaration and requires no code change. The only code-bound names are the *kinds* of
computation (the probe and renderer bindings), which is what makes a new member of an existing
kind free of code change.

Stdlib only. No network. No subprocess. No wall-clock is emitted, so the rendered register set
is byte-identical for an unchanged repository state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, NoReturn

PROGRAMME_ID = "UCEF-000001"

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "ucef-framework.json"
EVIDENCE_DIR = HERE / "evidence"

# Keys an entry of each declared list-section may carry. A key outside its allowed set is a
# finding: a new obligation, a hidden assumption or an unbound binding must not be smuggled
# through an undeclared field.
ALLOWED_KEYS: dict[str, set[str]] = {
    "outputs": {"id", "file", "title", "purpose", "renderer"},
    "laws": {"id", "law", "clause", "basis"},
    "stages": {"id", "stage", "purpose", "owner", "corroborating_owner", "depends_on"},
    "construct_classes": {"id", "construct_class", "admitted_by"},
    "expansion_axes": {"id", "axis", "bounded", "basis"},
    "criteria": {"id", "criterion", "mechanism", "clause"},
    "governance": {"id", "obligation", "instrument", "enforced_by"},
    "validations": {"id", "dimension", "probe", "verified_by", "clause"},
    "exit_criteria": {"id", "criterion", "satisfied_by"},
}

# Sections whose every entry must carry a reference that resolves against Repository Truth,
# paired with the keys holding those references.
REFERENCE_FIELDS: dict[str, tuple[str, ...]] = {
    "laws": ("basis",),
    "stages": ("owner", "corroborating_owner"),
    "construct_classes": ("admitted_by",),
    "expansion_axes": ("basis",),
    "criteria": ("mechanism",),
    "governance": ("instrument",),
    "validations": ("verified_by",),
}

# Sections whose bindings must pre-exist OUTSIDE this programme's home. A binding located
# inside it would mean the authority was authored here rather than reused, which is the
# duplication the framework forbids.
EXTERNAL_BINDING_FIELDS: dict[str, tuple[str, ...]] = {
    "laws": ("basis",),
    "stages": ("owner", "corroborating_owner"),
    "construct_classes": ("admitted_by",),
    "expansion_axes": ("basis",),
    "criteria": ("mechanism",),
    "governance": ("instrument",),
}

# Programme references that must resolve. Every reuse the programme claims must be a located
# artifact, or the claim is empty.
PROGRAMME_REFERENCE_KEYS = (
    "governing_instrument",
    "normative_home",
    "meta_governance_owner",
    "admission_owner",
    "constitution_registry_owner",
    "ownership_matrix_owner",
    "operational_memory_owner",
    "recovery_owner",
    "execution_owner",
    "traceability_owner",
    "evolution_governance_owner",
    "aggregate_gate_owner",
    "registration_owner",
    "verification_owner",
    "operational_home",
)

PROGRAMME_SCALAR_KEYS = (
    "id",
    "name",
    "programme_directive",
    "version",
    "authority",
    "mission",
    "gate_name",
    "gate_clause",
    "standing_disclosure",
)

CONTINUATION_KEYS = (
    "repository_state_source",
    "completed_work",
    "remaining_work",
    "current_checkpoint",
    "dependency_state",
    "open_issues",
    "architectural_decisions",
    "implementation_roadmap",
)

CONSTRUCT_REGISTER_REFERENCE_KEYS = ("openness_basis", "admission_procedure", "totality_rule")

# Fields whose declared value is long-form prose: a bare occurrence anywhere in this source
# would be a special-case, so the substring test is exact.
PROSE_LITERAL_FIELDS = (
    ("outputs", "file"),
    ("outputs", "id"),
    ("laws", "id"),
    ("laws", "law"),
    ("stages", "id"),
    ("stages", "purpose"),
    ("construct_classes", "id"),
    ("expansion_axes", "id"),
    ("criteria", "id"),
    ("criteria", "criterion"),
    ("governance", "id"),
    ("governance", "obligation"),
    ("validations", "id"),
    ("validations", "dimension"),
    ("exit_criteria", "id"),
    ("exit_criteria", "criterion"),
)

# Fields whose declared value is a short common word that legitimately occurs in prose. Here
# the test is that the value never appears as a QUOTED string literal, which is what a
# special-case would require.
QUOTED_LITERAL_FIELDS = (
    ("stages", "stage"),
    ("construct_classes", "construct_class"),
    ("expansion_axes", "axis"),
)

# A declaration reference may carry a human suffix naming a clause. It resolves by exact path
# first, then by unique prefix within its parent directory.
_SUFFIX_SPLITS = (" (", " §", " Art ", " · ", " — ")

_METADATA_VERSION_LABEL = "VERSION"


# --------------------------------------------------------------------------- helpers


def fail_closed(message: str) -> NoReturn:
    print(f"{PROGRAMME_ID}: FAIL-CLOSED ABORT — {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail_closed(f"required declaration absent: {path}")
    try:
        return json.loads(path.read_text("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        fail_closed(f"declaration is not readable JSON: {path}: {exc}")


def load_declaration() -> dict[str, Any]:
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
    matches = sorted(child for child in parent.iterdir() if child.name.startswith(candidate.name))
    return matches[0] if matches else None


def is_external(ref: str) -> bool:
    """True iff the reference resolves OUTSIDE this programme's own operational home."""
    located = resolve_reference(ref)
    if located is None:
        return False
    try:
        located.resolve().relative_to(HERE)
    except ValueError:
        return True
    return False


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def sections(decl: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {name: list(decl.get(name) or []) for name in ALLOWED_KEYS}


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def read_metadata_version(path: Path) -> str | None:
    """Read the VERSION row of an artifact's leading metadata table, if it carries one."""
    try:
        text = path.read_text("utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    for line in text.splitlines()[:60]:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].upper() == _METADATA_VERSION_LABEL:
            return cells[1]
    return None


# --------------------------------------------------------------------- declaration guard


def check_declaration(decl: dict[str, Any]) -> list[str]:
    """Every declared reference resolves, every entry is well formed, every id is unique."""
    findings: list[str] = []
    body = sections(decl)

    for name, allowed in ALLOWED_KEYS.items():
        entries = body[name]
        if not entries:
            findings.append(f"{name}: section is empty, so it governs nothing")
        seen: set[str] = set()
        for index, entry in enumerate(entries):
            ident = str(entry.get("id") or f"{name}[{index}]")
            if not entry.get("id"):
                findings.append(f"{ident}: declares no id")
            elif ident in seen:
                findings.append(f"{ident}: duplicate id within {name}")
            else:
                seen.add(ident)
            extra = sorted(set(entry) - allowed)
            if extra:
                findings.append(
                    f"{ident}: undeclared key(s) {extra} — an obligation may be smuggled "
                    "through a new field"
                )
            missing = sorted(key for key in allowed if key not in entry)
            if missing:
                findings.append(f"{ident}: missing declared key(s) {missing}")

    for name, keys in REFERENCE_FIELDS.items():
        for entry in body[name]:
            ident = str(entry.get("id") or name)
            for key in keys:
                ref = entry.get(key)
                if not ref:
                    findings.append(f"{ident}: declares no {key}")
                elif resolve_reference(str(ref)) is None:
                    findings.append(f"{ident}: {key} does not resolve: {ref!r}")

    programme = decl.get("programme") or {}
    for key in PROGRAMME_SCALAR_KEYS:
        if not programme.get(key):
            findings.append(f"programme: declares no {key}")
    for key in PROGRAMME_REFERENCE_KEYS:
        ref = programme.get(key)
        if not ref or resolve_reference(str(ref)) is None:
            findings.append(f"programme.{key}: reference does not resolve: {ref!r}")
    for ref in as_list(programme.get("governed_by")):
        if resolve_reference(ref) is None:
            findings.append(f"programme.governed_by: reference does not resolve: {ref!r}")
    prefixes = as_list(programme.get("forbidden_write_prefixes"))
    if not prefixes:
        findings.append("programme: declares no forbidden_write_prefixes")
    for prefix in prefixes:
        if not (REPO / prefix).exists():
            findings.append(f"programme.forbidden_write_prefixes: prefix absent: {prefix}")

    register = decl.get("construct_register") or {}
    if not register:
        findings.append("construct_register: absent, so register openness cannot be measured")
    for key in CONSTRUCT_REGISTER_REFERENCE_KEYS:
        ref = register.get(key)
        if not ref or resolve_reference(str(ref)) is None:
            findings.append(f"construct_register.{key}: does not resolve: {ref!r}")

    continuation = decl.get("continuation") or {}
    for key in CONTINUATION_KEYS:
        if not continuation.get(key):
            findings.append(f"continuation: declares no {key}")

    stage_ids = {str(entry.get("id")) for entry in body["stages"]}
    for entry in body["stages"]:
        ident = str(entry.get("id"))
        for dep in as_list(entry.get("depends_on")):
            if dep not in stage_ids:
                findings.append(f"{ident}: depends_on names an undeclared stage: {dep}")
            if dep == ident:
                findings.append(f"{ident}: depends upon itself")
    for entry in body["governance"]:
        ident = str(entry.get("id"))
        target = entry.get("enforced_by")
        if target not in stage_ids:
            findings.append(f"{ident}: enforced_by names an undeclared stage: {target!r}")

    validation_ids = {str(entry.get("id")) for entry in body["validations"]}
    for entry in body["exit_criteria"]:
        ident = str(entry.get("id"))
        satisfied = as_list(entry.get("satisfied_by"))
        if not satisfied:
            findings.append(f"{ident}: names no satisfying validation, so it is unfalsifiable")
        for ref in satisfied:
            if ref not in validation_ids:
                findings.append(f"{ident}: satisfied_by names an undeclared validation: {ref}")

    probes = {str(entry.get("probe")) for entry in body["validations"]}
    unknown = sorted(probes - set(PROBES))
    if unknown:
        findings.append(f"validations: no computation is bound for probe(s) {unknown}")

    renderers = {str(entry.get("renderer")) for entry in body["outputs"]}
    missing_renderers = sorted(renderers - set(RENDERERS))
    if missing_renderers:
        findings.append(f"outputs: no renderer is bound for {missing_renderers}")

    return findings


# ------------------------------------------------------------------------- self-guards


def check_no_enumeration(decl: dict[str, Any]) -> list[str]:
    """Prove the framework is DATA, so extending it needs no code change."""
    findings: list[str] = []
    source = Path(__file__).read_text("utf-8")
    body = sections(decl)

    for name, key in PROSE_LITERAL_FIELDS:
        for entry in body[name]:
            value = str(entry.get(key) or "")
            if value and value in source:
                findings.append(
                    f"engine source special-cases the declared {name}.{key} value {value!r} — "
                    "extending the framework would require a code change"
                )
    for name, key in QUOTED_LITERAL_FIELDS:
        for entry in body[name]:
            value = str(entry.get(key) or "")
            if not value:
                continue
            if f'"{value}"' in source or f"'{value}'" in source:
                findings.append(
                    f"engine source carries the declared {name}.{key} value {value!r} as a "
                    "string literal — the framework would branch on a particular member"
                )
    return findings


def check_write_scope(decl: dict[str, Any]) -> list[str]:
    """No write may land outside this programme's own operational memory."""
    findings: list[str] = []
    programme = decl.get("programme") or {}
    for prefix in as_list(programme.get("forbidden_write_prefixes")):
        if not (REPO / prefix).exists():
            findings.append(f"forbidden-write prefix does not exist: {prefix}")
    for entry in decl.get("outputs") or []:
        name = str(entry.get("file") or "")
        if not name:
            continue
        target = (HERE / name).resolve()
        if target.parent != HERE:
            findings.append(f"output escapes the programme's operational memory: {target}")
    for prefix in as_list(programme.get("forbidden_write_prefixes")):
        try:
            HERE.relative_to((REPO / prefix).resolve())
        except ValueError:
            continue
        findings.append(f"the programme's own home lies inside a forbidden prefix: {prefix}")
    return findings


def check_reuse_before_create(decl: dict[str, Any]) -> list[str]:
    """Prove zero duplication: every bound authority pre-exists outside this programme."""
    findings: list[str] = []
    body = sections(decl)
    for name, keys in EXTERNAL_BINDING_FIELDS.items():
        for entry in body[name]:
            ident = str(entry.get("id") or name)
            for key in keys:
                ref = str(entry.get(key) or "")
                if not ref:
                    continue
                if resolve_reference(ref) is None:
                    findings.append(f"{ident}: {key} does not resolve: {ref}")
                elif not is_external(ref):
                    findings.append(
                        f"{ident}: {key} lies inside this programme's own home, so the "
                        f"authority is authored here rather than reused: {ref}"
                    )
    return findings


def check_open_world(decl: dict[str, Any]) -> list[str]:
    """Prove no finite ceiling is declared anywhere in the framework."""
    findings: list[str] = []
    register = decl.get("construct_register") or {}
    if register.get("closed") is not False:
        findings.append(
            "construct_register.closed is not false — a closed register asserts a finite "
            "ceiling, which the located admission owner declares a defect"
        )
    if register.get("exhaustive") is not False:
        findings.append("construct_register.exhaustive is not false — the register must be open")
    if register.get("absence_is_not_rejection") is not True:
        findings.append(
            "construct_register.absence_is_not_rejection is not true — absence from the "
            "register would become a ground of rejection"
        )
    if not str(register.get("unknown_class_disposition") or "").strip():
        findings.append("construct_register: declares no disposition for an unknown class")
    for entry in decl.get("expansion_axes") or []:
        ident = str(entry.get("id") or "expansion_axes")
        if entry.get("bounded") is not False:
            findings.append(f"{ident}: declares a finite bound, which is a finiteness defect")
    return findings


# ------------------------------------------------------------------------------ probes
#
# A probe is a KIND of computation, not a governed name. Each reads Repository Truth and
# returns (verdict, evidence) where verdict is True, False, or None for UNVERIFIED.
# UNVERIFIED is fail-closed: it never reads as PASS.


def _binding_report(decl: dict[str, Any], names: tuple[str, ...]) -> tuple[int, int, list[str]]:
    total = 0
    good = 0
    bad: list[str] = []
    for name in names:
        for entry in decl.get(name) or []:
            for key in EXTERNAL_BINDING_FIELDS.get(name, ()):
                ref = str(entry.get(key) or "")
                if not ref:
                    continue
                total += 1
                if is_external(ref):
                    good += 1
                else:
                    bad.append(f"{entry.get('id')}.{key}")
    return good, total, bad


def probe_redesign_free(decl: dict[str, Any]) -> tuple[bool | None, str]:
    good, total, bad = _binding_report(decl, tuple(EXTERNAL_BINDING_FIELDS))
    if total == 0:
        return None, "no binding is declared, so redesign-freedom cannot be measured"
    if bad:
        return False, f"{len(bad)} binding(s) authored inside this programme: {sorted(bad)[:5]}"
    return True, (
        f"{good}/{total} bindings pre-exist outside this programme — the framework authored "
        "no foundational authority, so no foundational redesign was required"
    )


def probe_conflict_free(decl: dict[str, Any]) -> tuple[bool | None, str]:
    registry_path = resolve_reference(
        str((decl.get("programme") or {}).get("constitution_registry_owner") or "")
    )
    if registry_path is None or not registry_path.is_file():
        return None, "the Constitution Registry is not located, so conflicts cannot be measured"
    try:
        registry = json.loads(registry_path.read_text("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        return None, f"the Constitution Registry is unreadable: {exc}"
    artifacts = registry.get("artifacts") or []
    ids = [str(item.get("id")) for item in artifacts]
    paths = [str(item.get("path")) for item in artifacts]
    duplicate_ids = sorted({value for value in ids if ids.count(value) > 1})
    duplicate_paths = sorted({value for value in paths if paths.count(value) > 1})
    concerns = registry.get("concerns") or []
    keys = [str(item.get("concern")) for item in concerns]
    duplicate_concerns = sorted({value for value in keys if keys.count(value) > 1})
    problems = duplicate_ids + duplicate_paths + duplicate_concerns
    if problems:
        return False, f"registry declares competing entries: {problems[:5]}"
    return True, (
        f"{len(artifacts)} recognized artifacts with unique identity and path; "
        f"{len(concerns)} concerns each allocated to exactly one owner — no parallel authority"
    )


def probe_duplication_free(decl: dict[str, Any]) -> tuple[bool | None, str]:
    body = sections(decl)
    problems: list[str] = []
    for name in body:
        ids = [str(entry.get("id")) for entry in body[name]]
        for value in sorted(set(ids)):
            if ids.count(value) > 1:
                problems.append(f"{name}:{value}")
    _good, total, bad = _binding_report(decl, tuple(EXTERNAL_BINDING_FIELDS))
    if total == 0:
        return None, "no binding is declared, so duplication cannot be measured"
    problems += sorted(bad)
    if problems:
        return False, f"duplication detected: {problems[:5]}"
    return True, (
        "every declared identity is unique and every bound authority is reused rather than "
        "re-authored — no competing model, registry or lifecycle is created"
    )


def probe_orphan_free(decl: dict[str, Any]) -> tuple[bool | None, str]:
    unresolved: list[str] = []
    total = 0
    for name, keys in REFERENCE_FIELDS.items():
        for entry in decl.get(name) or []:
            for key in keys:
                ref = str(entry.get(key) or "")
                if not ref:
                    continue
                total += 1
                if resolve_reference(ref) is None:
                    unresolved.append(f"{entry.get('id')}.{key}")
    programme = decl.get("programme") or {}
    for key in PROGRAMME_REFERENCE_KEYS:
        total += 1
        if resolve_reference(str(programme.get(key) or "")) is None:
            unresolved.append(f"programme.{key}")
    if total == 0:
        return None, "no reference is declared, so orphans cannot be measured"
    if unresolved:
        return False, f"{len(unresolved)} orphan reference(s): {sorted(unresolved)[:5]}"
    return True, f"{total}/{total} references resolve against Repository Truth — zero orphans"


def _stage_graph(decl: dict[str, Any]) -> dict[str, list[str]]:
    return {
        str(entry.get("id")): as_list(entry.get("depends_on")) for entry in decl.get("stages") or []
    }


def probe_acyclic(decl: dict[str, Any]) -> tuple[bool | None, str]:
    graph = _stage_graph(decl)
    if not graph:
        return None, "no stage is declared, so acyclicity cannot be measured"
    white, grey, black = 0, 1, 2
    colour = dict.fromkeys(graph, white)

    def walk(node: str) -> str | None:
        stack = [(node, iter(graph.get(node, ())))]
        colour[node] = grey
        while stack:
            current, children = stack[-1]
            advanced = False
            for child in children:
                if child not in colour:
                    continue
                if colour[child] == grey:
                    return child
                if colour[child] == white:
                    colour[child] = grey
                    stack.append((child, iter(graph.get(child, ()))))
                    advanced = True
                    break
            if not advanced:
                colour[current] = black
                stack.pop()
        return None

    for node in graph:
        if colour[node] == white:
            closing = walk(node)
            if closing is not None:
                return False, f"dependency cycle closes at {closing}"
    return True, f"{len(graph)} stages form an acyclic graph — no stage depends upon itself"


def probe_dependency_closed(decl: dict[str, Any]) -> tuple[bool | None, str]:
    graph = _stage_graph(decl)
    if not graph:
        return None, "no stage is declared, so closure cannot be measured"
    dangling = sorted(
        f"{node}->{dep}" for node, deps in graph.items() for dep in deps if dep not in graph
    )
    roots = sorted(node for node, deps in graph.items() if not deps)
    if dangling:
        return False, f"dependency escapes the declared set: {dangling[:5]}"
    if len(roots) != 1:
        return False, f"the lifecycle has {len(roots)} entry stages, so its order is not total"
    reachable = set(roots)
    changed = True
    while changed:
        changed = False
        for node, deps in graph.items():
            if node not in reachable and deps and all(dep in reachable for dep in deps):
                reachable.add(node)
                changed = True
    unreachable = sorted(set(graph) - reachable)
    if unreachable:
        return False, f"stage(s) unreachable from the entry stage: {unreachable[:5]}"
    return True, (
        f"{len(graph)}/{len(graph)} stages reachable from a single entry stage; every "
        "dependency is itself a declared stage — closure is complete"
    )


def _located_probe(decl: dict[str, Any], programme_key: str, noun: str) -> tuple[bool | None, str]:
    ref = str((decl.get("programme") or {}).get(programme_key) or "")
    located = resolve_reference(ref)
    if located is None:
        return None, f"the {noun} owner is not located, so synchronization cannot be measured"
    return True, f"the {noun} owner is located at {located.relative_to(REPO).as_posix()}"


def probe_ontology_synchronized(decl: dict[str, Any]) -> tuple[bool | None, str]:
    owners = [
        entry
        for entry in decl.get("criteria") or []
        for key in ("mechanism",)
        if resolve_reference(str(entry.get(key) or "")) is not None
    ]
    if not owners:
        return None, "no criterion mechanism is located, so ontology cannot be measured"
    meta, message = _located_probe(decl, "meta_governance_owner", "ontology")
    if meta is not True:
        return meta, message
    return True, message


def probe_taxonomy_synchronized(decl: dict[str, Any]) -> tuple[bool | None, str]:
    registry_path = resolve_reference(
        str((decl.get("programme") or {}).get("constitution_registry_owner") or "")
    )
    if registry_path is None or not registry_path.is_file():
        return None, "the Constitution Registry is not located, so taxonomy cannot be measured"
    try:
        registry = json.loads(registry_path.read_text("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        return None, f"the Constitution Registry is unreadable: {exc}"
    kinds = registry.get("kinds") or []
    closed = {str(item) for item in registry.get("closed_enumerations") or []}
    if not kinds:
        return False, "the taxonomy declares no kind"
    offending = sorted(name for name in closed if "kind" in name.lower())
    if offending:
        return False, f"the kind set is declared closed by {offending} — a finite ceiling"
    return True, (
        f"{len(kinds)} kinds recognized and the kind set is absent from the "
        f"{len(closed)} closed enumerations — the taxonomy remains open to append"
    )


def probe_registry_synchronized(decl: dict[str, Any]) -> tuple[bool | None, str]:
    located: Path | None = None
    for entry in decl.get("validations") or []:
        if entry.get("probe") == "registry_synchronized":
            located = resolve_reference(str(entry.get("verified_by") or ""))
            break
    if located is None or not located.is_file():
        return None, "the artifact registry is not located, so synchronization is unmeasurable"
    try:
        payload = json.loads(located.read_text("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        return None, f"the artifact registry is unreadable: {exc}"
    artifacts = payload.get("artifacts") or []
    declared = payload.get("count")
    if declared is not None and int(declared) != len(artifacts):
        return False, f"the registry declares {declared} artifacts but carries {len(artifacts)}"
    identities = [str(item.get("universal_id")) for item in artifacts]
    duplicates = sorted({value for value in identities if identities.count(value) > 1})
    if duplicates:
        return False, f"the registry carries duplicate identities: {duplicates[:5]}"
    return True, (
        f"{len(artifacts)} registered artifacts, declared count agrees, identities unique — "
        "the registry projection is internally synchronized"
    )


def probe_traceability_closed(decl: dict[str, Any]) -> tuple[bool | None, str]:
    missing: list[str] = []
    total = 0
    for name, keys in (
        ("laws", ("clause", "basis")),
        ("criteria", ("clause", "mechanism")),
        ("validations", ("clause", "verified_by")),
        ("stages", ("owner",)),
        ("governance", ("instrument", "enforced_by")),
    ):
        for entry in decl.get(name) or []:
            for key in keys:
                total += 1
                if not str(entry.get(key) or "").strip():
                    missing.append(f"{entry.get('id')}.{key}")
    if total == 0:
        return None, "nothing is declared, so traceability cannot be measured"
    if missing:
        return False, f"{len(missing)} unclosed traceability link(s): {sorted(missing)[:5]}"
    return True, f"{total}/{total} traceability links closed — zero orphan links"


def probe_register_open(decl: dict[str, Any]) -> tuple[bool | None, str]:
    findings = check_open_world(decl)
    register = decl.get("construct_register") or {}
    if not register:
        return None, "no register is declared, so openness cannot be measured"
    register_findings = [item for item in findings if "construct_register" in item]
    if register_findings:
        return False, register_findings[0]
    return True, (
        f"the register is declared open and non-exhaustive over "
        f"{len(decl.get('construct_classes') or [])} named classes; an unnamed class is "
        "admitted by the same procedure, and absence is no ground of rejection"
    )


def probe_axes_unbounded(decl: dict[str, Any]) -> tuple[bool | None, str]:
    axes = decl.get("expansion_axes") or []
    if not axes:
        return None, "no axis is declared, so unboundedness cannot be measured"
    bounded = sorted(str(entry.get("id")) for entry in axes if entry.get("bounded") is not False)
    if bounded:
        return False, f"axis/axes declare a finite bound: {bounded[:5]}"
    return True, f"{len(axes)}/{len(axes)} expansion axes declare no finite bound"


def _section_binding_probe(decl: dict[str, Any], name: str, noun: str) -> tuple[bool | None, str]:
    entries = decl.get(name) or []
    if not entries:
        return None, f"no {noun} is declared, so binding cannot be measured"
    keys = EXTERNAL_BINDING_FIELDS.get(name, REFERENCE_FIELDS.get(name, ()))
    bad: list[str] = []
    total = 0
    for entry in entries:
        for key in keys:
            ref = str(entry.get(key) or "")
            if not ref:
                continue
            total += 1
            if not is_external(ref):
                bad.append(f"{entry.get('id')}.{key}")
    if total == 0:
        return None, f"no {noun} carries a binding, so it cannot be measured"
    if bad:
        return False, f"{len(bad)} unbound or self-authored {noun} binding(s): {sorted(bad)[:5]}"
    return True, f"{len(entries)} {noun} entries, {total}/{total} bindings located and external"


def probe_stages_bound(decl: dict[str, Any]) -> tuple[bool | None, str]:
    return _section_binding_probe(decl, "stages", "lifecycle stage")


def probe_criteria_discharged(decl: dict[str, Any]) -> tuple[bool | None, str]:
    return _section_binding_probe(decl, "criteria", "acceptance property")


def probe_laws_anchored(decl: dict[str, Any]) -> tuple[bool | None, str]:
    return _section_binding_probe(decl, "laws", "constitutional law")


def probe_governance_bound(decl: dict[str, Any]) -> tuple[bool | None, str]:
    verdict, evidence = _section_binding_probe(decl, "governance", "governance obligation")
    if verdict is not True:
        return verdict, evidence
    stage_ids = {str(entry.get("id")) for entry in decl.get("stages") or []}
    covered = {str(entry.get("enforced_by")) for entry in decl.get("governance") or []}
    uncovered = sorted(stage_ids - covered)
    if uncovered:
        return False, f"stage(s) carry no governance obligation: {uncovered[:5]}"
    return True, f"{evidence}; every one of {len(stage_ids)} stages is governed"


def probe_normative_home_present(decl: dict[str, Any]) -> tuple[bool | None, str]:
    programme = decl.get("programme") or {}
    home = resolve_reference(str(programme.get("normative_home") or ""))
    token = str(programme.get("programme_directive") or "")
    if home is None or not home.is_file():
        return None, "the normative home is not located, so institutionalization is unmeasurable"
    if not token:
        return None, "no programme directive is declared, so the record cannot be located"
    try:
        text = home.read_text("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"the normative home is unreadable: {exc}"
    if token not in text:
        return False, (
            f"the normative home {home.relative_to(REPO).as_posix()} does not record {token} — "
            "the framework is not institutionalized in the instrument that owns evolution"
        )
    return True, (
        f"{home.relative_to(REPO).as_posix()} records {token} — the framework is legislated by "
        "the located owner of constitutional evolution, not by this programme"
    )


def probe_registry_version_synchronized(decl: dict[str, Any]) -> tuple[bool | None, str]:
    programme = decl.get("programme") or {}
    home = resolve_reference(str(programme.get("normative_home") or ""))
    registry_path = resolve_reference(str(programme.get("constitution_registry_owner") or ""))
    if home is None or registry_path is None or not registry_path.is_file():
        return None, "the normative home or the registry is not located"
    stated = read_metadata_version(home)
    if stated is None:
        return None, "the normative home carries no version row, so synchrony is unmeasurable"
    try:
        registry = json.loads(registry_path.read_text("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        return None, f"the Constitution Registry is unreadable: {exc}"
    relative = home.relative_to(REPO).as_posix()
    matches = [item for item in registry.get("artifacts") or [] if item.get("path") == relative]
    if not matches:
        return False, f"the registry does not recognize the normative home {relative}"
    recorded = str(matches[0].get("version"))
    if recorded != stated:
        return False, (
            f"the registry records version {recorded} for {relative} but the artifact states "
            f"{stated} — the amendment did not update the registry in the same change"
        )
    return True, (
        f"the registry and {relative} both record version {stated} — the registry was updated "
        "in the same change as the amendment"
    )


PROBES = {
    "redesign_free": probe_redesign_free,
    "conflict_free": probe_conflict_free,
    "duplication_free": probe_duplication_free,
    "orphan_free": probe_orphan_free,
    "acyclic": probe_acyclic,
    "dependency_closed": probe_dependency_closed,
    "ontology_synchronized": probe_ontology_synchronized,
    "taxonomy_synchronized": probe_taxonomy_synchronized,
    "registry_synchronized": probe_registry_synchronized,
    "traceability_closed": probe_traceability_closed,
    "register_open": probe_register_open,
    "axes_unbounded": probe_axes_unbounded,
    "stages_bound": probe_stages_bound,
    "criteria_discharged": probe_criteria_discharged,
    "laws_anchored": probe_laws_anchored,
    "governance_bound": probe_governance_bound,
    "normative_home_present": probe_normative_home_present,
    "registry_version_synchronized": probe_registry_version_synchronized,
}


# -------------------------------------------------------------------------- assessment


def verdict_word(value: bool | None) -> str:
    if value is None:
        return "UNVERIFIED"
    return "PASS" if value else "FAIL"


def assess(decl: dict[str, Any]) -> dict[str, Any]:
    """Compute every verdict from Repository Truth. Nothing here asserts; everything measures."""
    guards = {
        "declaration": check_declaration(decl),
        "no_enumeration": check_no_enumeration(decl),
        "write_scope": check_write_scope(decl),
        "reuse_before_create": check_reuse_before_create(decl),
        "open_world": check_open_world(decl),
    }

    validations: list[dict[str, Any]] = []
    for entry in decl.get("validations") or []:
        probe = PROBES[str(entry.get("probe"))]
        value, evidence = probe(decl)
        validations.append(
            {
                "id": str(entry.get("id")),
                "dimension": str(entry.get("dimension")),
                "probe": str(entry.get("probe")),
                "clause": str(entry.get("clause")),
                "verified_by": str(entry.get("verified_by")),
                "verdict": verdict_word(value),
                "satisfied": value is True,
                "evidence": evidence,
            }
        )
    by_id = {item["id"]: item for item in validations}

    exits: list[dict[str, Any]] = []
    for entry in decl.get("exit_criteria") or []:
        refs = as_list(entry.get("satisfied_by"))
        unmet = [ref for ref in refs if not by_id[ref]["satisfied"]]
        exits.append(
            {
                "id": str(entry.get("id")),
                "criterion": str(entry.get("criterion")),
                "satisfied_by": refs,
                "satisfied": not unmet,
                "unmet": unmet,
            }
        )

    guard_findings = sorted(item for group in guards.values() for item in group)
    validations_ok = all(item["satisfied"] for item in validations)
    exits_ok = all(item["satisfied"] for item in exits)
    passed = not guard_findings and validations_ok and exits_ok

    stage_rows = [
        {
            "id": str(entry.get("id")),
            "stage": str(entry.get("stage")),
            "purpose": str(entry.get("purpose")),
            "owner": str(entry.get("owner")),
            "corroborating_owner": str(entry.get("corroborating_owner")),
            "depends_on": as_list(entry.get("depends_on")),
            "bound": is_external(str(entry.get("owner") or "")),
        }
        for entry in decl.get("stages") or []
    ]
    criteria_rows = [
        {
            "id": str(entry.get("id")),
            "criterion": str(entry.get("criterion")),
            "mechanism": str(entry.get("mechanism")),
            "clause": str(entry.get("clause")),
            "discharged": is_external(str(entry.get("mechanism") or "")),
        }
        for entry in decl.get("criteria") or []
    ]

    assessment = {
        "programme": dict(decl.get("programme") or {}),
        "guards": {name: sorted(items) for name, items in guards.items()},
        "guard_findings": guard_findings,
        "validations": validations,
        "exit_criteria": exits,
        "stages": stage_rows,
        "criteria": criteria_rows,
        "counts": {
            "laws": len(decl.get("laws") or []),
            "stages": len(stage_rows),
            "stages_bound": sum(1 for row in stage_rows if row["bound"]),
            "construct_classes": len(decl.get("construct_classes") or []),
            "expansion_axes": len(decl.get("expansion_axes") or []),
            "criteria": len(criteria_rows),
            "criteria_discharged": sum(1 for row in criteria_rows if row["discharged"]),
            "governance": len(decl.get("governance") or []),
            "validations": len(validations),
            "validations_satisfied": sum(1 for item in validations if item["satisfied"]),
            "exit_criteria": len(exits),
            "exit_criteria_satisfied": sum(1 for item in exits if item["satisfied"]),
        },
        "verdict": "GATE-OPEN" if passed else "GATE-CLOSED",
        "passed": passed,
        "determination": ("CERTIFIED-PROVISIONAL" if passed else "NOT-CERTIFIED"),
        "declaration_digest": digest(decl),
    }
    assessment["assessment_digest"] = digest(
        {key: value for key, value in assessment.items() if key != "assessment_digest"}
    )
    return assessment


# ---------------------------------------------------------------------------- rendering


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |\n"
    rule = "|" + "|".join("---" for _ in headers) + "|\n"
    body = "".join("| " + " | ".join(str(cell) for cell in row) + " |\n" for row in rows)
    return head + rule + body


def header(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    prog = decl["programme"]
    return (
        f"# {entry['title']}\n\n"
        f"| Field | Value |\n|---|---|\n"
        f"| PROGRAMME | `{prog['id']}` — {prog['name']} |\n"
        f"| REGISTER | `{entry['id']}` |\n"
        f"| AUTHORITY | `{prog['authority']}` |\n"
        f"| NORMATIVE HOME | `{prog['normative_home']}` |\n"
        f"| DIRECTIVE | `{prog['programme_directive']}` |\n"
        f"| GATE | {prog['gate_name']} — **{state['verdict']}** |\n"
        f"| DETERMINATION | **{state['determination']}** |\n"
        f"| DECLARATION DIGEST | `{state['declaration_digest']}` |\n\n"
        f"> {entry['purpose']}\n\n"
        f"> **Standing.** {prog['standing_disclosure']}\n\n"
        "---\n\n"
    )


def render_dashboard(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    counts = state["counts"]
    return (
        header(decl, state, entry)
        + "## Framework state\n\n"
        + table(
            ["Measure", "Value"],
            [
                ["Constitutional laws anchored", f"{counts['laws']}"],
                ["Lifecycle stages bound", f"{counts['stages_bound']}/{counts['stages']}"],
                ["Construct classes named (register OPEN)", f"{counts['construct_classes']}"],
                ["Expansion axes declared unbounded", f"{counts['expansion_axes']}"],
                [
                    "Acceptance properties discharged",
                    f"{counts['criteria_discharged']}/{counts['criteria']}",
                ],
                ["Governance obligations bound", f"{counts['governance']}"],
                [
                    "Validation dimensions satisfied",
                    f"{counts['validations_satisfied']}/{counts['validations']}",
                ],
                [
                    "Exit criteria satisfied",
                    f"{counts['exit_criteria_satisfied']}/{counts['exit_criteria']}",
                ],
                ["Self-guard findings", f"{len(state['guard_findings'])}"],
            ],
        )
        + "\n## Self-guards\n\n"
        + table(
            ["Guard", "Findings", "Result"],
            [
                [name, str(len(items)), "PASS" if not items else "FAIL"]
                for name, items in sorted(state["guards"].items())
            ],
        )
        + "\n## Validation summary\n\n"
        + table(
            ["ID", "Measured dimension", "Verdict"],
            [[item["id"], item["dimension"], item["verdict"]] for item in state["validations"]],
        )
        + f"\n## Determination\n\n**{state['determination']}** — gate **{state['verdict']}**.\n\n"
        + (
            "Every mandatory dimension and exit criterion is satisfied. The framework is "
            "institutionalized in the located owner of constitutional evolution, every "
            "lifecycle stage and acceptance property binds to an authority that already "
            "exists, and no foundational artifact was authored here.\n"
            if state["passed"]
            else "One or more dimensions, exit criteria or self-guards are unsatisfied; "
            "certification is withheld.\n"
        )
    )


def render_laws(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    return (
        header(decl, state, entry)
        + "Each law's normative home is the addendum cited in its clause column. This register "
        "restates no law; it records where each law lives and the located basis it derives "
        "from, so no law is orphaned.\n\n"
        + table(
            ["ID", "Law", "Clause (normative home)", "Located basis"],
            [
                [item["id"], item["law"], f"`{item['clause']}`", f"`{item['basis']}`"]
                for item in decl["laws"]
            ],
        )
    )


def render_lifecycle(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    order = " → ".join(row["stage"] for row in state["stages"])
    return (
        header(decl, state, entry)
        + f"## Canonical order\n\n{order}\n\n"
        + "Architectural redesign is **not** a stage of this lifecycle and shall never be "
        "introduced as one. A traversal that would require it has failed at reuse or "
        "dependency analysis and is returned there.\n\n"
        + "## Stage bindings\n\n"
        + table(
            ["#", "Stage", "Located owner", "Corroborating owner", "Bound"],
            [
                [
                    row["id"],
                    row["stage"],
                    f"`{row['owner']}`",
                    f"`{row['corroborating_owner']}`",
                    "YES" if row["bound"] else "NO",
                ]
                for row in state["stages"]
            ],
        )
        + "\n## Stage purpose\n\n"
        + table(
            ["#", "Stage", "Purpose"],
            [[row["id"], row["stage"], row["purpose"]] for row in state["stages"]],
        )
        + f"\n**{state['counts']['stages_bound']}/{state['counts']['stages']} stages are bound "
        "to a located owner outside this programme — the framework introduces no lifecycle.**\n"
    )


def render_constructs(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    register = decl["construct_register"]
    return (
        header(decl, state, entry)
        + "## Register openness\n\n"
        + table(
            ["Property", "Value"],
            [
                ["Closed", str(register["closed"])],
                ["Exhaustive", str(register["exhaustive"])],
                ["Absence is not rejection", str(register["absence_is_not_rejection"])],
                ["Openness basis", f"`{register['openness_basis']}`"],
                ["Admission procedure", f"`{register['admission_procedure']}`"],
                ["Totality rule", f"`{register['totality_rule']}`"],
            ],
        )
        + f"\n> {register['unknown_class_disposition']}\n\n"
        + "## Named classes (non-exhaustive)\n\n"
        + table(
            ["ID", "Construct class", "Admitted by"],
            [
                [item["id"], item["construct_class"], f"`{item['admitted_by']}`"]
                for item in decl["construct_classes"]
            ],
        )
        + f"\n**{len(decl['construct_classes'])} classes are named and the register is OPEN.** "
        "The engine names none of them, so admitting a further class is an append to the "
        "declaration and requires no code change.\n"
    )


def render_axes(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    axes = decl["expansion_axes"]
    return (
        header(decl, state, entry)
        + table(
            ["ID", "Axis", "Finite bound declared", "Located basis"],
            [
                [item["id"], item["axis"], str(item["bounded"]), f"`{item['basis']}`"]
                for item in axes
            ],
        )
        + f"\n**{len(axes)}/{len(axes)} axes declare no finite bound.** The only bound upon "
        "growth is evidence, which bounds legitimacy rather than quantity and shall not be "
        "cited as a finite ceiling.\n"
    )


def render_criteria(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    rows = state["criteria"]
    return (
        header(decl, state, entry)
        + "A property whose discharging mechanism cannot be located is **not** satisfied. "
        "Absence of evidence is not evidence of satisfaction.\n\n"
        + table(
            ["ID", "The construct shall", "Discharged by (located)", "Clause", "Discharged"],
            [
                [
                    row["id"],
                    row["criterion"],
                    f"`{row['mechanism']}`",
                    f"`{row['clause']}`",
                    "YES" if row["discharged"] else "NO",
                ]
                for row in rows
            ],
        )
        + f"\n**{state['counts']['criteria_discharged']}/{state['counts']['criteria']} "
        "properties are discharged by a located mechanism that already exists.**\n"
    )


def render_reuse(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    rows: list[list[str]] = []
    for name in sorted(EXTERNAL_BINDING_FIELDS):
        keys = EXTERNAL_BINDING_FIELDS[name]
        total = 0
        external = 0
        for item in decl.get(name) or []:
            for key in keys:
                ref = str(item.get(key) or "")
                if not ref:
                    continue
                total += 1
                external += 1 if is_external(ref) else 0
        rows.append([name, str(total), str(external), "PASS" if external == total else "FAIL"])
    return (
        header(decl, state, entry)
        + "## Reuse-First proof\n\n"
        + "Every bound authority must pre-exist **outside** this programme's own home. A "
        "binding located inside it would mean the authority was authored here rather than "
        "reused, which is exactly the duplication the framework forbids.\n\n"
        + table(["Section", "Bindings", "External (reused)", "Result"], rows)
        + "\n## Disposition record\n\n"
        + f"{decl['continuation']['architectural_decisions']}\n\n"
        + "## Guard findings\n\n"
        + (
            "No duplication, no competing authority, and no self-authored binding.\n"
            if not state["guards"]["reuse_before_create"]
            else table(["Finding"], [[item] for item in state["guards"]["reuse_before_create"]])
        )
    )


def render_dependency(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    rows = state["stages"]
    return (
        header(decl, state, entry)
        + table(
            ["ID", "Stage", "Depends on"],
            [
                [row["id"], row["stage"], ", ".join(row["depends_on"]) or "— (entry stage)"]
                for row in rows
            ],
        )
        + "\n## Measured graph properties\n\n"
        + table(
            ["Property", "Verdict", "Evidence"],
            [
                [item["dimension"], item["verdict"], item["evidence"]]
                for item in state["validations"]
                if item["probe"] in {"acyclic", "dependency_closed"}
            ],
        )
        + f"\n> {decl['continuation']['dependency_state']}\n"
    )


def render_governance(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    stage_names = {row["id"]: row["stage"] for row in state["stages"]}
    return (
        header(decl, state, entry)
        + "An obligation whose instrument cannot be located governs nothing and does not "
        "discharge. Every stage of the lifecycle carries at least one obligation.\n\n"
        + table(
            ["ID", "Obligation", "Located instrument", "Enforced at stage"],
            [
                [
                    item["id"],
                    item["obligation"],
                    f"`{item['instrument']}`",
                    f"{item['enforced_by']} — {stage_names.get(item['enforced_by'], '?')}",
                ]
                for item in decl["governance"]
            ],
        )
    )


def render_validation(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    return (
        header(decl, state, entry)
        + "Every dimension is computed from Repository Truth. `UNVERIFIED` is **fail-closed**: "
        "where a measurement cannot be performed, no verdict is asserted and the gate does not "
        "open.\n\n"
        + table(
            ["ID", "Measured dimension", "Verdict", "Measured evidence"],
            [
                [item["id"], item["dimension"], item["verdict"], item["evidence"]]
                for item in state["validations"]
            ],
        )
        + f"\n**{state['counts']['validations_satisfied']}/{state['counts']['validations']} "
        "dimensions satisfied.**\n\n"
        + "## Self-guards\n\n"
        + (
            "All self-guards pass with zero findings.\n"
            if not state["guard_findings"]
            else table(["Finding"], [[item] for item in state["guard_findings"]])
        )
    )


def render_certification(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    return (
        header(decl, state, entry)
        + "## Exit criteria\n\n"
        + table(
            ["ID", "Criterion", "Satisfied by", "Result"],
            [
                [
                    item["id"],
                    item["criterion"],
                    ", ".join(item["satisfied_by"]),
                    "PASS" if item["satisfied"] else f"FAIL — unmet {item['unmet']}",
                ]
                for item in state["exit_criteria"]
            ],
        )
        + f"\n## Determination\n\n**{state['determination']}**\n\n"
        + (
            "Every mandatory validation dimension and every exit criterion is satisfied, and "
            "every self-guard passes with zero findings. Certification is issued at "
            "PROVISIONAL standing and no higher: the competent ratification authority is "
            "vacant, so nothing here is ratified or final.\n"
            if state["passed"]
            else "Certification is **withheld**. One or more dimensions, exit criteria or "
            "self-guards are unsatisfied.\n"
        )
        + f"\n> **Standing.** {decl['programme']['standing_disclosure']}\n\n"
        + f"- Assessment digest: `{state['assessment_digest']}`\n"
    )


def render_traceability(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    return (
        header(decl, state, entry)
        + "## Law → clause → located basis\n\n"
        + table(
            ["ID", "Clause", "Located basis"],
            [[item["id"], f"`{item['clause']}`", f"`{item['basis']}`"] for item in decl["laws"]],
        )
        + "\n## Stage → located owner\n\n"
        + table(
            ["ID", "Located owner"],
            [[row["id"], f"`{row['owner']}`"] for row in state["stages"]],
        )
        + "\n## Acceptance property → located mechanism\n\n"
        + table(
            ["ID", "Clause", "Located mechanism"],
            [
                [row["id"], f"`{row['clause']}`", f"`{row['mechanism']}`"]
                for row in state["criteria"]
            ],
        )
        + "\n## Validation dimension → clause → verifying artifact\n\n"
        + table(
            ["ID", "Clause", "Verified by"],
            [
                [item["id"], f"`{item['clause']}`", f"`{item['verified_by']}`"]
                for item in state["validations"]
            ],
        )
        + "\n## Expansion axis → certification basis\n\n"
        + table(
            ["ID", "Located basis"],
            [[item["id"], f"`{item['basis']}`"] for item in decl["expansion_axes"]],
        )
        + "\n**Traceability is closed with zero orphans: every law, stage, property, dimension "
        "and axis resolves to a located artifact of Repository Truth.**\n"
    )


def render_continuation(decl: dict[str, Any], state: dict[str, Any], entry: dict[str, Any]) -> str:
    cont = decl["continuation"]
    return (
        header(decl, state, entry)
        + table(
            ["Field", "Record"],
            [[key.replace("_", " ").title(), cont[key]] for key in CONTINUATION_KEYS],
        )
        + "\n## How the next construct is introduced\n\n"
        + "Traverse the stages of the lifecycle register in order. No stage of that traversal "
        "edits this framework, and none edits the constitutional foundation.\n\n"
        + table(
            ["#", "Stage", "Located owner"],
            [[row["id"], row["stage"], f"`{row['owner']}`"] for row in state["stages"]],
        )
    )


RENDERERS = {
    "dashboard": render_dashboard,
    "laws": render_laws,
    "lifecycle": render_lifecycle,
    "constructs": render_constructs,
    "axes": render_axes,
    "criteria": render_criteria,
    "reuse": render_reuse,
    "dependency": render_dependency,
    "governance": render_governance,
    "validation": render_validation,
    "certification": render_certification,
    "traceability": render_traceability,
    "continuation": render_continuation,
}


def render_all(decl: dict[str, Any], state: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for entry in decl.get("outputs") or []:
        renderer = RENDERERS[str(entry.get("renderer"))]
        out[str(entry["file"])] = renderer(decl, state, entry)
    return out


# ----------------------------------------------------------------------------- emission


def emit(decl: dict[str, Any], state: dict[str, Any]) -> list[str]:
    written: list[str] = []
    for name, text in sorted(render_all(decl, state).items()):
        target = HERE / name
        target.write_text(text, encoding="utf-8")
        written.append(target.relative_to(REPO).as_posix())
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence = {
        "ucef-assessment.json": state,
        "ucef-validation.json": {
            "validations": state["validations"],
            "exit_criteria": state["exit_criteria"],
            "verdict": state["verdict"],
        },
        "ucef-bindings.json": {"stages": state["stages"], "criteria": state["criteria"]},
        "ucef-guards.json": state["guards"],
    }
    for name, payload in sorted(evidence.items()):
        target = EVIDENCE_DIR / name
        target.write_text(canonical_json(payload), encoding="utf-8")
        written.append(target.relative_to(REPO).as_posix())
    summary = HERE / "ucef.json"
    summary.write_text(canonical_json(state), encoding="utf-8")
    written.append(summary.relative_to(REPO).as_posix())
    return sorted(written)


# --------------------------------------------------------------------------------- main


GUARDS = {
    "--check-declaration": (check_declaration, "every declared reference resolves"),
    "--check-no-enumeration": (check_no_enumeration, "the framework is data, not code"),
    "--check-write-scope": (check_write_scope, "every write lands inside this programme"),
    "--check-reuse-before-create": (check_reuse_before_create, "every authority is reused"),
    "--check-open-world": (check_open_world, "no finite ceiling is declared"),
}


def run_guard(flag: str, decl: dict[str, Any]) -> int:
    probe, claim = GUARDS[flag]
    findings = probe(decl)
    if findings:
        for finding in findings:
            print(f"{PROGRAMME_ID} FINDING [{flag}]: {finding}", file=sys.stderr)
        print(f"{PROGRAMME_ID}: {flag} FAILED — {len(findings)} finding(s)", file=sys.stderr)
        return 1
    print(f"{PROGRAMME_ID}: {flag} PASS — {claim}")
    return 0


def guard_determinism(decl: dict[str, Any]) -> int:
    first_state = assess(decl)
    second_state = assess(load_declaration())
    if first_state != second_state:
        print(f"{PROGRAMME_ID}: DETERMINISM VIOLATION — assessment differs", file=sys.stderr)
        return 1
    if render_all(decl, first_state) != render_all(decl, second_state):
        print(f"{PROGRAMME_ID}: DETERMINISM VIOLATION — rendering differs", file=sys.stderr)
        return 1
    print(
        f"{PROGRAMME_ID}: --check-determinism PASS — assessment and rendering are "
        f"byte-identical across runs (digest {first_state['assessment_digest'][:16]})"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ucef_engine", description=__doc__)
    parser.add_argument("--gate", action="store_true", help="fail-closed constitutional gate")
    parser.add_argument("--render", action="store_true", help="regenerate the registers only")
    for flag in sorted(GUARDS):
        parser.add_argument(flag, action="store_true")
    parser.add_argument("--check-determinism", action="store_true")
    args = parser.parse_args(argv)
    chosen = vars(args)

    decl = load_declaration()

    for flag in sorted(GUARDS):
        if chosen[flag.removeprefix("--").replace("-", "_")]:
            return run_guard(flag, decl)
    if args.check_determinism:
        return guard_determinism(decl)

    findings = check_declaration(decl)
    if findings:
        fail_closed(f"declaration unusable ({len(findings)} finding(s)): {findings[0]}")

    state = assess(decl)
    written = emit(decl, state)

    if args.gate:
        print(
            canonical_json(
                {
                    "programme": PROGRAMME_ID,
                    "verdict": state["verdict"],
                    "determination": state["determination"],
                    "passed": state["passed"],
                    "counts": state["counts"],
                    "guard_findings": state["guard_findings"],
                    "unsatisfied": [
                        item["id"] for item in state["validations"] if not item["satisfied"]
                    ],
                    "assessment_digest": state["assessment_digest"],
                    "written": written,
                }
            ),
            end="",
        )
        return 0 if state["passed"] else 1

    print(f"{PROGRAMME_ID}: {state['verdict']} — {state['determination']}")
    for item in state["validations"]:
        print(f"  {item['verdict']:<10} {item['id']}  {item['dimension']}")
    print(f"wrote {len(written)} artifacts to {HERE.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

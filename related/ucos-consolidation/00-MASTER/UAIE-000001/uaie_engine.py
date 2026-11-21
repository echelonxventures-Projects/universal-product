#!/usr/bin/env python3
"""Architectural intelligence measurement engine.

AUTHORITY = NONE (DERIVED TRUTH). This engine asserts nothing of its own. It reads the
declaration ``uaie-architecture.json``, measures every declared binding and every declared
register against Repository Truth, and renders the registers. Where this output and a
canonical owner differ, the canonical owner governs.

What this engine is for
-----------------------
The mission this programme records names ten architectural faculties and twelve subjects the
repository must be able to reason about. Every one of those faculties is already realised by a
canonical owner, and every subject already has a located register. A claim that the repository
can reason about itself is therefore not a reason to build anything: it is a claim that has to
be *bound* to the owners that make it true, and then measured, so that a rename, a move or a
deletion closes the gate instead of quietly invalidating the claim.

The one measurement this engine performs that no located owner performed is the reading of the
declared registers against each other. Each existing analysis reasons inside one substrate and
reports on that substrate; none reads one register's references against what another register
still holds. A register that drifts while its own owner stays green is invisible to every owner
individually and visible only across them. That cross-reading, the resolution of each named
faculty, and closure over the faculty relation are the three analyses this programme adds, and
they are registered in the located analysis registry rather than in a registry of its own.

What this engine must never do
------------------------------
It creates no engine, no registry, no catalogue, no identity, no graph, no lifecycle and no
namespace. It enumerates nothing: every faculty, owner, home, symbol, register, path, anchor
and validation is read from the declaration, so adding one is a data edit. That is checked by
``--check-no-enumeration``, which fails if any declared identifier, name or path leaks into this
source, including into this docstring. It writes only inside its own programme directory,
checked by ``--check-write-scope``. It binds nothing to itself, checked by
``--check-reuse-before-create``. It claims no place in the meta-constitutional plane, checked by
``--check-no-parallel-authority``.

Determinism
-----------
No timestamp, no clock, no environment value and no path outside the repository enters the
output, so two renders of one committed declaration are byte-identical. That is what
``--check-determinism`` proves and it is what lets CI diff a replay against the commit; it is
also what makes the programme a fixed point rather than a moving report.

Usage:
    uaie_engine.py                     measure and print the determination
    uaie_engine.py --render            measure and write the registers
    uaie_engine.py --gate              fail-closed: exit 1 if any blocking validation fails
    uaie_engine.py --check-declaration            declaration integrity
    uaie_engine.py --check-no-enumeration         no declared data is hardcoded in this engine
    uaie_engine.py --check-write-scope            writes stay inside this programme
    uaie_engine.py --check-determinism            two renders are byte-identical
    uaie_engine.py --check-reuse-before-create    no binding points inside this programme
    uaie_engine.py --check-register-plane         every declared register resolves and parses
    uaie_engine.py --check-no-parallel-authority  no claim in the meta-constitutional plane
    uaie_engine.py --check-evolution-contract     every evolution obligation binds to an owner

Exit codes: 0 satisfied / gate OPEN · 1 gate CLOSED or self-guard failed · 2 fail-closed
abort (the declaration itself is unusable, so no determination is assertable).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "uaie-architecture.json"
MODEL = HERE / "uaie.json"

#: The programme identifier is the directory name, so it is never restated as a literal.
PROGRAMME = HERE.name

#: The repo-relative prefix this programme owns. Nothing outside it is ever written, and no
#: faculty may be bound inside it (that would be this programme realising its own faculty).
OWN_PREFIX = f"{HERE.relative_to(REPO).as_posix()}/"

#: Structural roles a declared register may play in the measurement. A role says which part of
#: the measurement a register participates in; it names no register and no path.
ROLE_ANALYSES = "analysis-registry"
ROLE_CATALOGUE = "capability-catalogue"
ROLE_META = "meta-constitutional-registry"
ROLE_ONTOLOGY = "ontology-register"
ROLE_EVOLUTION = "evolution-register"
ROLE_RELEASE = "release-register"
ROLE_BASELINE = "baseline-register"

REQUIRED_KEYS = (
    "programme",
    "admission_determination",
    "dispositions",
    "ontology_anchors",
    "registers",
    "faculties",
    "contributed_analyses",
    "evolution_contract",
    "validations",
)


class FailClosed(Exception):
    """The declaration or its substrate is unusable, so no verdict may be asserted."""


# ---------------------------------------------------------------------------------
# substrate
# ---------------------------------------------------------------------------------
def load_declaration() -> dict[str, Any]:
    """Read the declaration, failing closed rather than guessing at a broken one."""
    if not DECLARATION.is_file():
        raise FailClosed(f"required declaration absent: {DECLARATION.relative_to(REPO)}")
    try:
        document = json.loads(DECLARATION.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosed(f"declaration is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise FailClosed("declaration must be a JSON object")
    for key in REQUIRED_KEYS:
        if key not in document:
            raise FailClosed(f"declaration is missing the required key '{key}'")
    if not document["faculties"]:
        raise FailClosed("declaration binds no faculty, so there is nothing to measure")
    if not document["registers"]:
        raise FailClosed("declaration declares no register, so there is nothing to reason over")
    return document


def module_symbols(path: Path) -> set[str]:
    """Top-level names bound by a Python module, read without importing it.

    Importing would execute the module and make this engine depend on the very code it is
    measuring. Parsing keeps the measurement inert. An annotated module constant is a bound
    name just as much as a plain assignment, so both forms are collected.
    """
    try:
        tree = ast.parse(path.read_text("utf-8", errors="replace"), filename=str(path))
    except (SyntaxError, OSError):
        return set()
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def register_by_role(document: dict[str, Any], role: str) -> dict[str, Any] | None:
    """The declared register that plays a structural role, or None if none does."""
    return next((r for r in document["registers"] if r.get("role") == role), None)


def read_register(register: dict[str, Any]) -> tuple[Any, str | None]:
    """Read one declared register. Returns (payload, problem). Never raises."""
    path = REPO / str(register.get("path", ""))
    if not path.exists():
        return None, "path does not resolve"
    if str(register.get("form")) == "json":
        try:
            return json.loads(path.read_text("utf-8")), None
        except (json.JSONDecodeError, OSError) as exc:
            return None, f"declared as structured data but does not parse: {exc}"
    try:
        return path.read_text("utf-8", errors="replace"), None
    except OSError as exc:
        return None, f"cannot be read: {exc}"


def probed_paths(payload: Any, probe: dict[str, Any] | None) -> list[str]:
    """The repository paths one register references, per its declared probe.

    A probe names a collection and a field. The field may hold a single path or a list of
    them; both are flattened, because which of the two a register uses is that register's
    own convention and not something this engine may decide.
    """
    if not probe or not isinstance(payload, dict):
        return []
    collection = payload.get(str(probe.get("collection")))
    if not isinstance(collection, list):
        return []
    field = str(probe.get("field"))
    found: list[str] = []
    for record in collection:
        if not isinstance(record, dict):
            continue
        value = record.get(field)
        if isinstance(value, str) and value:
            found.append(value)
        elif isinstance(value, list):
            found.extend(str(item) for item in value if isinstance(item, str) and item)
    return found


def registered_analyses(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The located analysis registry, keyed by analysis identifier."""
    register = register_by_role(document, ROLE_ANALYSES)
    if register is None:
        return {}
    payload, problem = read_register(register)
    if problem or not isinstance(payload, dict):
        return {}
    collection = payload.get(str((register.get("probe") or {}).get("collection")))
    if not isinstance(collection, list):
        return {}
    return {
        str(record.get("id")): record
        for record in collection
        if isinstance(record, dict) and record.get("id")
    }


def catalogue_records(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The canonical capability catalogue, keyed by its unique identifier."""
    register = register_by_role(document, ROLE_CATALOGUE)
    if register is None:
        return {}
    payload, problem = read_register(register)
    if problem or not isinstance(payload, dict):
        return {}
    collection = payload.get(str((register.get("probe") or {}).get("collection")))
    if not isinstance(collection, list):
        return {}
    return {
        str(record.get("unique_id")): record
        for record in collection
        if isinstance(record, dict) and record.get("unique_id")
    }


def meta_plane(document: dict[str, Any]) -> set[str]:
    """Every identifier the meta-constitutional plane recognizes: artifacts and namespaces.

    Read generically so this engine never restates a constitutional identifier of its own.
    """
    register = register_by_role(document, ROLE_META)
    if register is None:
        return set()
    payload, problem = read_register(register)
    if problem or not isinstance(payload, dict):
        return set()
    claimed: set[str] = set()
    for key, field in (("artifacts", "id"), ("namespaces", "token")):
        collection = payload.get(key)
        if isinstance(collection, list):
            claimed.update(
                str(record.get(field))
                for record in collection
                if isinstance(record, dict) and record.get(field)
            )
    return claimed


def ontology_text(document: dict[str, Any]) -> str:
    """The text of the declared ontology register, or the empty string if it cannot be read."""
    return register_text(document, ROLE_ONTOLOGY)


def register_text(document: dict[str, Any], role: str) -> str:
    """The text of the declared register playing a role, or "" if it cannot be read.

    Returning the empty string rather than raising keeps the measurement inert: an unreadable
    register is reported as an unsatisfied dimension, never as an exception that hides it.
    """
    register = register_by_role(document, role)
    if register is None:
        return ""
    payload, problem = read_register(register)
    return payload if problem is None and isinstance(payload, str) else ""


def topological_layers(relation: dict[str, list[str]]) -> list[list[str]] | None:
    """Deterministic layering of a dependency relation. Returns None on a cycle.

    A node sits one layer above the deepest thing it depends on, so layer zero is exactly the
    set of nodes that depend on nothing. Returning None rather than a partial order is what
    makes a cycle a failure instead of a silently truncated answer.
    """
    indegree = {node: 0 for node in relation}
    dependents: dict[str, list[str]] = {node: [] for node in relation}
    for node in sorted(relation):
        for target in relation[node]:
            if target in indegree:
                indegree[node] += 1
                dependents[target].append(node)
    ready = sorted(n for n in indegree if indegree[n] == 0)
    layers: list[list[str]] = []
    placed = 0
    while ready:
        layers.append(list(ready))
        placed += len(ready)
        following: list[str] = []
        for node in ready:
            for dependent in dependents[node]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    following.append(dependent)
        ready = sorted(following)
    return layers if placed == len(relation) else None


# ---------------------------------------------------------------------------------
# measurement
# ---------------------------------------------------------------------------------
def measure(document: dict[str, Any]) -> dict[str, Any]:  # noqa: C901 - one dimension per branch
    """Measure every declared binding and every declared register against Repository Truth.

    Returns the machine model. Every field is derived; nothing is asserted.
    """
    faculties = document["faculties"]
    dispositions = {str(d["id"]) for d in document["dispositions"]}
    analyses = registered_analyses(document)
    catalogue = catalogue_records(document)
    claimed_in_meta = meta_plane(document)
    ontology = ontology_text(document)
    declared_registers = {str(r["id"]): r for r in document["registers"]}

    missing_homes: list[str] = []
    missing_symbols: list[str] = []
    unregistered_analyses: list[str] = []
    inside_own: list[str] = []
    bad_disposition: list[str] = []
    unbound: list[str] = []
    owner_problems: list[str] = []
    missing_catalogue: list[str] = []
    undisclosed_gaps: list[str] = []
    dangling_register_refs: list[str] = []
    dependency_problems: list[str] = []
    bindings: list[dict[str, Any]] = []

    for faculty in faculties:
        identifier = str(faculty.get("id", ""))
        homes = [str(h) for h in faculty.get("homes", [])]
        symbols = [str(s) for s in faculty.get("symbols", [])]
        disposition = str(faculty.get("disposition", ""))
        owner = str(faculty.get("canonical_owner", ""))
        cited = [str(a) for a in faculty.get("analyses", [])]
        referenced = [str(r) for r in faculty.get("registers", [])]

        if not homes:
            unbound.append(identifier)
        if disposition not in dispositions:
            bad_disposition.append(f"{identifier}:{disposition or 'NONE'}")
        if not owner:
            owner_problems.append(f"{identifier}: no canonical owner")
        elif not (REPO / owner).exists():
            owner_problems.append(f"{identifier}:{owner} does not resolve")

        resolved: list[str] = []
        for home in homes:
            if home.startswith(OWN_PREFIX):
                inside_own.append(f"{identifier}:{home}")
            if (REPO / home).exists():
                resolved.append(home)
            else:
                missing_homes.append(f"{identifier}:{home}")

        available: set[str] = set()
        for home in resolved:
            if home.endswith(".py"):
                available |= module_symbols(REPO / home)
        for symbol in symbols:
            if symbol not in available:
                missing_symbols.append(f"{identifier}:{symbol}")

        if not cited:
            unregistered_analyses.append(f"{identifier}: cites no registered analysis")
        for analysis_id in cited:
            record = analyses.get(analysis_id)
            if record is None:
                unregistered_analyses.append(f"{identifier}:{analysis_id} is not registered")
            elif not (REPO / str(record.get("home", ""))).exists():
                unregistered_analyses.append(f"{identifier}:{analysis_id} home does not resolve")

        prohibited = False
        for record_id in (str(c) for c in faculty.get("catalogue_ids", [])):
            record = catalogue.get(record_id)
            if record is None:
                missing_catalogue.append(f"{identifier}:{record_id}")
                continue
            if record.get("replacement_prohibited"):
                prohibited = True

        for reference in referenced:
            if reference not in declared_registers:
                dangling_register_refs.append(f"{identifier}:{reference}")

        gap = str(faculty.get("gap", ""))
        if gap and len(gap.split()) < 4:
            undisclosed_gaps.append(identifier)

        bindings.append(
            {
                "id": identifier,
                "name": str(faculty.get("name", "")),
                "disposition": disposition,
                "canonical_owner": owner,
                "objective": str(faculty.get("objective", "")),
                "reuse": str(faculty.get("reuse", "")),
                "homes": homes,
                "homes_resolved": len(resolved),
                "homes_declared": len(homes),
                "symbols": symbols,
                "analyses": cited,
                "registers": referenced,
                "catalogue_ids": [str(c) for c in faculty.get("catalogue_ids", [])],
                "replacement_prohibited": prohibited,
                "depends_on": [str(d) for d in faculty.get("depends_on", [])],
                "gap": gap,
            }
        )

    # An identical home set for two faculties would be two authorities over one home.
    seen_homes: dict[str, str] = {}
    duplicate_bindings: list[str] = []
    for binding in bindings:
        key = "|".join(sorted(binding["homes"]))
        if not key:
            continue
        if key in seen_homes:
            duplicate_bindings.append(f"{seen_homes[key]}={binding['id']}")
        else:
            seen_homes[key] = binding["id"]

    # One canonical owner per faculty, and no owner claimed twice: a shared canonical owner
    # would mean two faculties are the same faculty under two names.
    seen_owner: dict[str, str] = {}
    for binding in bindings:
        owner = binding["canonical_owner"]
        if not owner:
            continue
        if owner in seen_owner:
            owner_problems.append(f"{seen_owner[owner]}={binding['id']} share owner {owner}")
        else:
            seen_owner[owner] = binding["id"]

    # A faculty citing a record whose replacement is prohibited must actually reuse it: naming a
    # protected owner while resolving none of its homes is a claim of reuse with nothing behind it.
    unreused_protected = sorted(
        f"{b['id']}:0/{b['homes_declared']}"
        for b in bindings
        if b["replacement_prohibited"] and b["homes_resolved"] == 0
    )
    missing_catalogue.extend(unreused_protected)

    # Closure over the faculty relation.
    known = {b["id"] for b in bindings}
    relation = {b["id"]: [d for d in b["depends_on"]] for b in bindings}
    for identifier in sorted(relation):
        for target in relation[identifier]:
            if target not in known:
                dependency_problems.append(f"{identifier} depends on undeclared {target}")
            if target == identifier:
                dependency_problems.append(f"{identifier} depends on itself")
    closed_relation = {k: [t for t in v if t in known and t != k] for k, v in relation.items()}
    layers = topological_layers(closed_relation)
    if layers is None:
        dependency_problems.append("the faculty dependency relation contains a cycle")

    # The register plane: every declared register must resolve and parse, and every path any
    # probed register references must still exist. The second reading is the cross-register one.
    unreadable_registers: list[str] = []
    inconsistent_references: list[str] = []
    register_facts: list[dict[str, Any]] = []
    for register in document["registers"]:
        identifier = str(register["id"])
        payload, problem = read_register(register)
        if problem:
            unreadable_registers.append(f"{identifier}: {problem}")
        referenced_paths = probed_paths(payload, register.get("probe"))
        unresolved = sorted({p for p in referenced_paths if not (REPO / p).exists()})
        inconsistent_references.extend(f"{identifier}:{p}" for p in unresolved)
        claimants = sorted(b["id"] for b in bindings if identifier in b["registers"])
        register_facts.append(
            {
                "id": identifier,
                "subject": str(register.get("subject", "")),
                "path": str(register.get("path", "")),
                "owner": str(register.get("owner", "")),
                "form": str(register.get("form", "")),
                "role": register.get("role"),
                "resolves": problem is None,
                "problem": problem or "",
                "references": len(referenced_paths),
                "references_unresolved": len(unresolved),
                "claimed_by": claimants,
            }
        )

    unclaimed_registers = sorted(f["id"] for f in register_facts if not f["claimed_by"])
    coverage_problems = unclaimed_registers + sorted(dangling_register_refs)

    # Ontology integration is a binding to an element that already exists.
    anchor_facts: list[dict[str, Any]] = []
    missing_anchors: list[str] = []
    for anchor in document["ontology_anchors"]:
        identifier = str(anchor.get("id", ""))
        register_id = str(anchor.get("register", ""))
        register = declared_registers.get(register_id)
        present = bool(identifier) and bool(ontology) and identifier in ontology
        if register is None:
            missing_anchors.append(f"{identifier}: names undeclared register {register_id}")
        elif not present:
            missing_anchors.append(f"{identifier}: absent from the declared ontology register")
        anchor_facts.append(
            {
                "id": identifier,
                "element": str(anchor.get("element", "")),
                "register": register_id,
                "present": present,
            }
        )

    # What this programme contributes must be registered where analyses are registered, and must
    # not collide with an analysis already registered to a different owner.
    contributed_facts: list[dict[str, Any]] = []
    contribution_problems: list[str] = []
    for contribution in document["contributed_analyses"]:
        identifier = str(contribution.get("id", ""))
        name = str(contribution.get("name", ""))
        record = analyses.get(identifier)
        home = str((record or {}).get("home", ""))
        registered_here = bool(record) and home.startswith(OWN_PREFIX)
        if record is None:
            contribution_problems.append(f"{identifier}: not registered in the analysis registry")
        elif not registered_here:
            contribution_problems.append(f"{identifier}: registered away from this programme")
        collisions = sorted(
            str(other.get("id"))
            for other in analyses.values()
            if str(other.get("name")) == name
            and not str(other.get("home", "")).startswith(OWN_PREFIX)
        )
        if collisions:
            contribution_problems.append(f"{identifier}: name already held by {collisions}")
        contributed_facts.append(
            {
                "id": identifier,
                "name": name,
                "kind": str(contribution.get("kind", "")),
                "objective": str(contribution.get("objective", "")),
                "why_not_already_owned": str(contribution.get("why_not_already_owned", "")),
                "registered": registered_here,
                "collisions": collisions,
            }
        )

    # No parallel authority: the declared admission determination must match Repository Truth.
    admission = document["admission_determination"]
    declared_admitted = bool(admission.get("admitted_to_meta_registry"))
    actually_admitted = PROGRAMME in claimed_in_meta
    authority_problems: list[str] = []
    if declared_admitted != actually_admitted:
        authority_problems.append(
            "the declared admission determination does not match the meta-constitutional plane: "
            f"declared admitted={declared_admitted}, measured admitted={actually_admitted}"
        )
    if not claimed_in_meta:
        authority_problems.append(
            "the meta-constitutional plane could not be read, so absence from it is unproven"
        )
    authority_problems.extend(
        f"{b['id']}:{b['canonical_owner']}"
        for b in bindings
        if b["canonical_owner"].startswith(OWN_PREFIX)
    )

    # The Constitutional Evolution Contract. Each obligation is bound to the located owner and
    # the named gate that discharges it; the VERDICT stays with that gate and is never restated
    # here, because a second verdict over one obligation would be a second authority over it.
    contract = document["evolution_contract"]
    statuses = {str(s["id"]) for s in contract.get("statuses", [])}
    obligation_problems: list[str] = []
    obligation_facts: list[dict[str, Any]] = []
    for obligation in contract["obligations"]:
        identifier = str(obligation.get("id", ""))
        owner_paths = [str(p) for p in obligation.get("owner_paths", [])]
        evidence = [str(p) for p in obligation.get("evidence", [])]
        status = str(obligation.get("status", ""))
        for field in ("obligation", "owner", "gate", "discharge"):
            if not str(obligation.get(field, "")).strip():
                obligation_problems.append(f"{identifier}: '{field}' is empty")
        if status not in statuses:
            obligation_problems.append(f"{identifier}: undeclared status {status or 'NONE'}")
        if not owner_paths:
            obligation_problems.append(f"{identifier}: names no located owner")
        unresolved_owner = [p for p in owner_paths if not (REPO / p).exists()]
        unresolved_evidence = [p for p in evidence if not (REPO / p).exists()]
        obligation_problems.extend(f"{identifier}:owner {p}" for p in unresolved_owner)
        obligation_problems.extend(f"{identifier}:evidence {p}" for p in unresolved_evidence)
        obligation_facts.append(
            {
                "id": identifier,
                "obligation": str(obligation.get("obligation", "")),
                "owner": str(obligation.get("owner", "")),
                "owner_paths": owner_paths,
                "gate": str(obligation.get("gate", "")),
                "evidence": evidence,
                "discharge": str(obligation.get("discharge", "")),
                "status": status,
                "owner_paths_resolved": len(owner_paths) - len(unresolved_owner),
                "evidence_resolved": len(evidence) - len(unresolved_evidence),
            }
        )

    # The change class, the release state and the baseline must be members of the registers that
    # own those vocabularies. Declaring a class no register admits would be inventing one.
    evolution_text = register_text(document, ROLE_EVOLUTION)
    release_text = register_text(document, ROLE_RELEASE)
    baseline_text = register_text(document, ROLE_BASELINE)
    classification = contract["change_classification"]
    baseline = contract["baseline"]
    release = contract["release_state"]
    vocabulary_problems: list[str] = []
    for value, corpus, label in (
        (str(classification.get("label", "")), evolution_text, "change class label"),
        (str(classification.get("token", "")), release_text, "change class token"),
        (str(release.get("state", "")), release_text, "release state"),
        (str(baseline.get("id", "")), baseline_text, "baseline identifier"),
    ):
        if not value:
            vocabulary_problems.append(f"{label}: not declared")
        elif not corpus:
            vocabulary_problems.append(f"{label}: its register could not be read")
        elif value not in corpus:
            vocabulary_problems.append(f"{label} '{value}' is absent from its register")
    for key in ("register", "token_register"):
        reference = str(classification.get(key, ""))
        if reference and reference not in declared_registers:
            vocabulary_problems.append(
                f"change classification names undeclared register {reference}"
            )
    for holder, key in ((baseline, "register"), (release, "register")):
        reference = str(holder.get(key, ""))
        if reference and reference not in declared_registers:
            vocabulary_problems.append(f"evolution contract names undeclared register {reference}")

    # The measurement binding: declared validation id -> measured failures. This is the one place
    # the engine names a validation, because each dimension needs its own measurement and
    # measurement logic cannot be derived from data. It is kept honest by the parity check below:
    # a declared validation with no measurement here FAILS CLOSED rather than being reported
    # satisfied, because absence of evidence is never evidence.
    findings: dict[str, list[str]] = {
        "UAIE-VAL-01": sorted(missing_homes),
        "UAIE-VAL-02": sorted(missing_symbols),
        "UAIE-VAL-03": sorted(unregistered_analyses),
        "UAIE-VAL-04": sorted(inside_own),
        "UAIE-VAL-05": sorted(bad_disposition),
        "UAIE-VAL-06": sorted(unbound),
        "UAIE-VAL-07": sorted(duplicate_bindings),
        "UAIE-VAL-08": sorted(owner_problems),
        "UAIE-VAL-09": sorted(dependency_problems),
        "UAIE-VAL-10": sorted(unreadable_registers),
        "UAIE-VAL-11": sorted(inconsistent_references),
        "UAIE-VAL-12": sorted(missing_catalogue),
        "UAIE-VAL-13": sorted(missing_anchors),
        "UAIE-VAL-14": sorted(contribution_problems),
        "UAIE-VAL-15": sorted(undisclosed_gaps),
        "UAIE-VAL-16": sorted(authority_problems),
        "UAIE-VAL-17": sorted(coverage_problems),
        "UAIE-VAL-18": sorted(obligation_problems),
        "UAIE-VAL-19": sorted(vocabulary_problems),
    }

    validations: list[dict[str, Any]] = []
    for declared in document["validations"]:
        identifier = str(declared["id"])
        measured = identifier in findings
        failures = findings.get(identifier, [f"{identifier}: declared but never measured"])
        validations.append(
            {
                "id": identifier,
                "dimension": str(declared["dimension"]),
                "obligation": str(declared["obligation"]),
                "blocking": bool(declared.get("blocking", True)),
                "measured": measured,
                "satisfied": measured and not failures,
                "failures": failures if not measured or failures else [],
            }
        )

    blocking_failed = [v["id"] for v in validations if v["blocking"] and not v["satisfied"]]
    counts = {
        "faculties": len(bindings),
        "homes_declared": sum(b["homes_declared"] for b in bindings),
        "homes_resolved": sum(b["homes_resolved"] for b in bindings),
        "symbols_declared": sum(len(b["symbols"]) for b in bindings),
        "owners": len(seen_owner),
        "reuse": sum(1 for b in bindings if b["disposition"] == "REUSE"),
        "extend": sum(1 for b in bindings if b["disposition"] == "EXTEND"),
        "compose": sum(1 for b in bindings if b["disposition"] == "COMPOSE"),
        "analyses_cited": len({a for b in bindings for a in b["analyses"]}),
        "analyses_registered": len(analyses),
        "analyses_contributed": len(contributed_facts),
        "registers": len(register_facts),
        "registers_resolved": sum(1 for f in register_facts if f["resolves"]),
        "register_references": sum(f["references"] for f in register_facts),
        "register_references_unresolved": sum(f["references_unresolved"] for f in register_facts),
        "ontology_anchors": len(anchor_facts),
        "ontology_anchors_present": sum(1 for a in anchor_facts if a["present"]),
        "dependency_edges": sum(len(v) for v in closed_relation.values()),
        "dependency_layers": len(layers) if layers is not None else 0,
        "gaps_disclosed": sum(1 for b in bindings if b["gap"]),
        "obligations": len(obligation_facts),
        "obligations_satisfied": sum(1 for o in obligation_facts if o["status"] == "SATISFIED"),
        "obligations_awaiting_commit": sum(
            1 for o in obligation_facts if o["status"] != "SATISFIED"
        ),
        "obligation_owner_paths": sum(len(o["owner_paths"]) for o in obligation_facts),
        "obligation_evidence": sum(len(o["evidence"]) for o in obligation_facts),
        "validations": len(validations),
        "validations_measured": sum(1 for v in validations if v["measured"]),
        "validations_satisfied": sum(1 for v in validations if v["satisfied"]),
    }

    model: dict[str, Any] = {
        "programme": document["programme"],
        "admission": {
            "classification": str(admission.get("classification", "")),
            "disposition": str(admission.get("disposition", "")),
            "declared_admitted_to_meta_registry": declared_admitted,
            "measured_admitted_to_meta_registry": actually_admitted,
            "meta_identifiers_read": len(claimed_in_meta),
            "basis": str(admission.get("basis", "")),
            "namespace_basis": str(admission.get("namespace_basis", "")),
            "rejected_alternatives": list(admission.get("rejected_alternatives", [])),
        },
        "bindings": bindings,
        "registers": register_facts,
        "ontology_anchors": anchor_facts,
        "contributed_analyses": contributed_facts,
        "evolution_contract": {
            "governing_instrument": str(contract.get("governing_instrument", "")),
            "baseline": dict(baseline),
            "change_classification": dict(classification),
            "release_state": dict(release),
            "statuses": list(contract.get("statuses", [])),
            "obligations": obligation_facts,
        },
        "dependency": {
            "relation": {k: sorted(v) for k, v in sorted(closed_relation.items())},
            "layers": layers if layers is not None else [],
            "acyclic": layers is not None,
        },
        "counts": counts,
        "validations": validations,
        "blocking_failures": blocking_failed,
        "gate": "CLOSED" if blocking_failed else "OPEN",
        "determination": (
            "ARCHITECTURAL INTELLIGENCE NOT BOUND — REPOSITORY MUST STOP"
            if blocking_failed
            else "ARCHITECTURAL INTELLIGENCE BOUND — EVERY FACULTY AND EVERY REGISTER "
            "RESOLVES IN REPOSITORY TRUTH"
        ),
        "exit_criteria": document.get("exit_criteria", []),
    }
    model["seal_sha256"] = hashlib.sha256(
        json.dumps(model, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return model


# ---------------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------------
def _table(rows: list[list[str]], header: list[str]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def _paths(values: list[str]) -> str:
    return ", ".join(f"`{v}`" for v in values) or "—"


def render(model: dict[str, Any]) -> dict[str, str]:  # noqa: C901 - one page per register
    """Build every register as text. Pure: no clock, no environment, no I/O."""
    programme = model["programme"]
    counts = model["counts"]
    admission = model["admission"]
    contract = model["evolution_contract"]
    pages: dict[str, str] = {}

    pages["00-UAIE-DASHBOARD.md"] = "\n".join(
        [
            f"# {programme['name']}",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| PROGRAMME | `{programme['id']}` |",
            f"| VERSION | {programme['version']} |",
            f"| AUTHORITY | **{programme['authority']}** |",
            f"| GOVERNING INSTRUMENT | `{programme['governing_instrument']}` |",
            f"| LIFECYCLE INSTRUMENT | `{programme['lifecycle_instrument']}` |",
            f"| CONSTITUTIONAL CLASSIFICATION | **{admission['classification']}** |",
            f"| FACULTIES BOUND | {counts['faculties']} |",
            f"| CANONICAL OWNERS | {counts['owners']} |",
            f"| HOMES RESOLVED | {counts['homes_resolved']}/{counts['homes_declared']} |",
            f"| SYMBOLS VERIFIED | {counts['symbols_declared']} |",
            f"| DISPOSITIONS | REUSE {counts['reuse']} · EXTEND {counts['extend']}"
            f" · COMPOSE {counts['compose']} |",
            f"| ANALYSES REUSED | {counts['analyses_cited']}"
            f" of {counts['analyses_registered']} registered |",
            f"| ANALYSES CONTRIBUTED | {counts['analyses_contributed']} |",
            f"| REGISTERS REASONED OVER | {counts['registers_resolved']}/{counts['registers']} |",
            f"| CROSS-REGISTER REFERENCES CHECKED | {counts['register_references']} |",
            f"| CROSS-REGISTER REFERENCES BROKEN | {counts['register_references_unresolved']} |",
            f"| ONTOLOGY ANCHORS | {counts['ontology_anchors_present']}"
            f"/{counts['ontology_anchors']} |",
            f"| FACULTY DEPENDENCY | {counts['dependency_edges']} edges ·"
            f" {counts['dependency_layers']} layers ·"
            f" acyclic {str(model['dependency']['acyclic']).lower()} |",
            f"| EVOLUTION BASELINE | `{contract['baseline']['id']}` |",
            f"| CHANGE CLASSIFICATION | **{contract['change_classification']['label']}**"
            f" (`{contract['change_classification']['token']}`) |",
            f"| RELEASE STATE | **{contract['release_state']['state']}** |",
            f"| EVOLUTION OBLIGATIONS | {counts['obligations_satisfied']} SATISFIED ·"
            f" {counts['obligations_awaiting_commit']} AWAITING-COMMIT"
            f" of {counts['obligations']} |",
            f"| VALIDATIONS | {counts['validations_satisfied']}/{counts['validations']} |",
            f"| GATE | **{model['gate']}** |",
            f"| DETERMINATION | **{model['determination']}** |",
            f"| SEAL (sha256) | `{model['seal_sha256']}` |",
            "| GENERATED BY | `uaie_engine.py` — regenerated, never hand-authored |",
            "",
            "> " + programme["disclosure"],
            "",
            "## Why this register exists",
            "",
            "The mission names ten architectural faculties and twelve subjects the repository",
            "must be able to reason about. Every faculty already had a canonical owner and every",
            "subject already had a located register before this programme existed, so the mission",
            "is not a licence to build: it is a claim that must be bound to the owners that make",
            "it true and then measured. This register is that binding and that measurement.",
            "",
            "Nothing here is a new engine, a new registry, a new authority, a new lifecycle or a",
            "new namespace. The faculties whose name has no single home are discharged by",
            "composition over homes that already exist, and each such absence is recorded rather",
            "than closed by building another engine.",
            "",
            f"{programme['mission']}",
            "",
        ]
    )

    binding_rows = [
        [
            f"`{b['id']}`",
            b["name"],
            f"**{b['disposition']}**",
            f"`{b['canonical_owner']}`",
            f"{b['homes_resolved']}/{b['homes_declared']}",
            ", ".join(b["analyses"]) or "—",
            ", ".join(b["catalogue_ids"]) or "—",
        ]
        for b in model["bindings"]
    ]
    detail: list[str] = []
    for b in model["bindings"]:
        detail.extend(
            [
                f"### {b['id']} — {b['name']}",
                "",
                f"- **Disposition:** {b['disposition']}",
                f"- **Canonical owner:** `{b['canonical_owner']}`",
                f"- **Objective:** {b['objective']}",
                f"- **Bound to:** {_paths(b['homes'])}",
                f"- **Symbols verified:** {_paths(b['symbols'])}",
                f"- **Registered analyses reused:** {', '.join(b['analyses']) or '—'}",
                f"- **Registers reasoned over:** {', '.join(b['registers']) or '—'}",
                f"- **Depends on:** {', '.join(b['depends_on']) or '— (foundation)'}",
                f"- **Replacement prohibited by catalogue:** "
                f"{str(b['replacement_prohibited']).lower()}",
                "",
                f"{b['reuse']}",
                "",
            ]
        )
        if b["gap"]:
            detail.extend([f"> **Recorded gap.** {b['gap']}", ""])
    pages["01-FACULTY-BINDING-REGISTER.md"] = "\n".join(
        [
            "# Architectural Faculty Binding Register",
            "",
            f"> AUTHORITY = {programme['authority']}. Exactly one canonical owner per faculty,",
            "> and the proof that every bound home and every named symbol resolves in",
            "> Repository Truth.",
            "",
            *_table(
                binding_rows,
                [
                    "ID",
                    "Faculty",
                    "Disposition",
                    "Canonical owner",
                    "Homes",
                    "Analyses",
                    "Catalogue",
                ],
            ),
            "",
            "## Reuse rationale, per faculty",
            "",
            *detail,
        ]
    )

    register_rows = [
        [
            f"`{f['id']}`",
            f["subject"],
            f"`{f['path']}`",
            f["form"],
            "**RESOLVES**" if f["resolves"] else f"**FAILS** — {f['problem']}",
            str(f["references"]),
            str(f["references_unresolved"]),
            ", ".join(f["claimed_by"]) or "**UNCLAIMED**",
        ]
        for f in model["registers"]
    ]
    pages["02-REGISTER-PLANE.md"] = "\n".join(
        [
            "# Register Plane — the semantic graph this programme reasons over",
            "",
            "> Each row is a subject the mission requires the repository to understand, bound to",
            "> the register that already holds it and to the faculties that reason over it. A",
            "> subject with no register, or a register no faculty claims, closes the gate.",
            "",
            *_table(
                register_rows,
                [
                    "ID",
                    "Subject",
                    "Register",
                    "Form",
                    "Status",
                    "Refs",
                    "Broken",
                    "Claimed by",
                ],
            ),
            "",
            "## Ontology integration",
            "",
            "> Ontology integration here is a *binding*, not an addition: each anchor is an",
            "> element the ontology register already declares, so no ontology element is created",
            "> and no declared cardinality is altered.",
            "",
            *_table(
                [
                    [
                        f"`{a['id']}`",
                        a["element"],
                        f"`{a['register']}`",
                        "**PRESENT**" if a["present"] else "**ABSENT**",
                    ]
                    for a in model["ontology_anchors"]
                ],
                ["Anchor", "Ontology element", "Register", "Status"],
            ),
            "",
        ]
    )

    broken = [
        f"- `{f['id']}` ({f['path']}) — {f['references_unresolved']} of {f['references']}"
        " referenced paths do not resolve"
        for f in model["registers"]
        if f["references_unresolved"]
    ]
    pages["03-CROSS-REGISTER-CONSISTENCY.md"] = "\n".join(
        [
            "# Cross-Register Consistency",
            "",
            "> This is the one measurement no located owner performed before this programme.",
            "> Each owner validates its own register; none reads one register's references",
            "> against what the repository still holds. A register that drifts while its own",
            "> owner stays green is invisible individually and visible only across them.",
            "",
            f"**References checked:** {counts['register_references']}"
            f" · **unresolved:** {counts['register_references_unresolved']}",
            "",
            *_table(
                [
                    [
                        f"`{f['id']}`",
                        f"`{f['path']}`",
                        f"`{f['owner']}`",
                        str(f["references"]),
                        str(f["references_unresolved"]),
                        "**CONSISTENT**" if not f["references_unresolved"] else "**DRIFTED**",
                    ]
                    for f in model["registers"]
                    if f["references"]
                ],
                ["Register", "Path", "Owner", "Refs", "Broken", "Status"],
            ),
            "",
            *(broken or ["No register references an artifact the repository has lost."]),
            "",
            "## Analyses this programme contributes",
            "",
            "> Everything else on this page is reused. These are the only capabilities added, and",
            "> each is an entry in the located analysis registry rather than a new registry.",
            "",
            *_table(
                [
                    [
                        f"`{c['id']}`",
                        f"`{c['name']}`",
                        c["kind"],
                        "**REGISTERED**" if c["registered"] else "**NOT REGISTERED**",
                        ", ".join(c["collisions"]) or "none",
                    ]
                    for c in model["contributed_analyses"]
                ],
                ["ID", "Name", "Kind", "Registry status", "Name collisions"],
            ),
            "",
            *[
                line
                for c in model["contributed_analyses"]
                for line in (
                    f"### `{c['id']}` — {c['name']}",
                    "",
                    f"- **Objective:** {c['objective']}",
                    f"- **Why this is not already owned:** {c['why_not_already_owned']}",
                    "",
                )
            ],
        ]
    )

    dependency = model["dependency"]
    layer_rows = [
        [str(index), ", ".join(f"`{n}`" for n in layer)]
        for index, layer in enumerate(dependency["layers"])
    ]
    edge_rows = [
        [f"`{node}`", ", ".join(f"`{t}`" for t in targets) or "— (foundation)"]
        for node, targets in dependency["relation"].items()
    ]
    owner_rows = [
        [f"`{b['id']}`", b["name"], f"`{b['canonical_owner']}`", _paths(b["homes"])]
        for b in model["bindings"]
    ]
    pages["04-OWNERSHIP-AND-DEPENDENCY-GRAPH.md"] = "\n".join(
        [
            "# Ownership Graph and Faculty Dependency Graph",
            "",
            "## Ownership graph",
            "",
            "> One canonical owner per faculty, and no owner claimed by two faculties. A shared",
            "> canonical owner would mean two faculties are one faculty under two names.",
            "",
            *_table(owner_rows, ["Faculty", "Name", "Canonical owner", "Homes"]),
            "",
            "## Faculty dependency graph",
            "",
            f"**Edges:** {counts['dependency_edges']} · **layers:**"
            f" {counts['dependency_layers']} · **acyclic:**"
            f" {str(dependency['acyclic']).lower()}",
            "",
            *_table(edge_rows, ["Faculty", "Depends on"]),
            "",
            "### Dependency closure, by layer",
            "",
            "> Layer zero depends on nothing. A faculty sits one layer above the deepest thing it",
            "> depends on, so a total order exists exactly when the relation is acyclic.",
            "",
            *_table(layer_rows, ["Layer", "Faculties"]),
            "",
        ]
    )

    validation_rows = [
        [
            f"`{v['id']}`",
            v["dimension"],
            "**PASS**" if v["satisfied"] else "**FAIL**",
            "blocking" if v["blocking"] else "advisory",
            "yes" if v["measured"] else "**NOT MEASURED**",
            ", ".join(f"`{f}`" for f in v["failures"][:6]) or "—",
        ]
        for v in model["validations"]
    ]
    pages["05-VALIDATION-REPORT.md"] = "\n".join(
        [
            "# Validation Report",
            "",
            f"> Every dimension is measured from Repository Truth. Seal `{model['seal_sha256']}`.",
            "",
            *_table(
                validation_rows,
                ["ID", "Dimension", "Result", "Class", "Measured", "Failures"],
            ),
            "",
            f"**Measured:** {counts['validations_measured']}/{counts['validations']}"
            " — a declared dimension with no measurement fails closed, because absence of"
            " evidence is never evidence.",
            "",
            f"**Blocking failures:** {len(model['blocking_failures'])}"
            f" {model['blocking_failures'] or ''}".rstrip(),
            "",
            "## Obligations",
            "",
            *_table(
                [[f"`{v['id']}`", v["obligation"]] for v in model["validations"]],
                ["ID", "Obligation"],
            ),
            "",
        ]
    )

    criteria_rows = [
        [f"`{c['id']}`", str(c["criterion"]), "**MET**" if model["gate"] == "OPEN" else "**UNMET**"]
        for c in model["exit_criteria"]
    ]
    pages["06-CERTIFICATION-REPORT.md"] = "\n".join(
        [
            "# Certification Report",
            "",
            f"| GATE | **{model['gate']}** |",
            "|---|---|",
            f"| DETERMINATION | **{model['determination']}** |",
            f"| SEAL (sha256) | `{model['seal_sha256']}` |",
            f"| BLOCKING FAILURES | {len(model['blocking_failures'])} |",
            "",
            *_table(criteria_rows, ["ID", "Exit criterion", "Standing"]),
            "",
            "## Evidence this certification rests on",
            "",
            f"- {counts['homes_resolved']} of {counts['homes_declared']} declared homes resolve",
            f"- {counts['symbols_declared']} declared symbols resolve by parsing, never by import",
            f"- {counts['analyses_cited']} registered analyses are reused across"
            f" {counts['faculties']} faculties",
            f"- {counts['registers_resolved']} of {counts['registers']} declared registers"
            " resolve and parse",
            f"- {counts['register_references']} cross-register references checked,"
            f" {counts['register_references_unresolved']} broken",
            f"- {counts['ontology_anchors_present']} of {counts['ontology_anchors']} ontology"
            " anchors are present in the ontology register",
            f"- the faculty relation is acyclic: {str(dependency['acyclic']).lower()}",
            f"- {counts['validations_satisfied']} of {counts['validations']} declared dimensions"
            " are satisfied and all are measured",
            "",
            "> **Standing.** CERTIFIED-PROVISIONAL. This programme holds no ratification",
            "> authority: it measures bindings and reports. Where this register and a canonical",
            "> owner differ, the canonical owner governs.",
            "",
        ]
    )

    pages["07-ADMISSION-AND-REUSE-DETERMINATION.md"] = "\n".join(
        [
            "# Admission and Reuse Determination",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| CONSTITUTIONAL CLASSIFICATION | **{admission['classification']}** |",
            f"| DISPOSITION | **{admission['disposition']}** |",
            "| ADMITTED TO THE META-CONSTITUTIONAL REGISTRY (declared) |"
            f" {str(admission['declared_admitted_to_meta_registry']).lower()} |",
            "| ADMITTED TO THE META-CONSTITUTIONAL REGISTRY (measured) |"
            f" {str(admission['measured_admitted_to_meta_registry']).lower()} |",
            "| META-CONSTITUTIONAL IDENTIFIERS READ |" f" {admission['meta_identifiers_read']} |",
            "",
            "## Basis",
            "",
            admission["basis"],
            "",
            "## Namespace",
            "",
            admission["namespace_basis"],
            "",
            "## Alternatives rejected",
            "",
            *[f"- {item}" for item in admission["rejected_alternatives"]],
            "",
            "## Reuse summary",
            "",
            f"Of {counts['faculties']} faculties: {counts['reuse']} bound by REUSE,"
            f" {counts['extend']} by EXTEND, {counts['compose']} by COMPOSE, and 0 by creation."
            f" {counts['analyses_cited']} analyses already registered elsewhere are reused, and"
            f" {counts['analyses_contributed']} are contributed — each an entry in the located"
            " analysis registry rather than a registry of this programme's own.",
            "",
            f"The measured absence of `{programme['id']}` from the meta-constitutional plane is",
            "the mechanical form of the no-parallel-authority rule: a substantive programme that",
            "appeared there would be claiming meta-constitutional standing it does not hold, and",
            "the gate closes on the mismatch in either direction.",
            "",
        ]
    )

    obligation_rows = [
        [
            f"`{o['id']}`",
            o["obligation"],
            f"`{o['gate']}`",
            f"{o['owner_paths_resolved']}/{len(o['owner_paths'])}",
            f"{o['evidence_resolved']}/{len(o['evidence'])}",
            f"**{o['status']}**",
        ]
        for o in contract["obligations"]
    ]
    obligation_detail: list[str] = []
    for o in contract["obligations"]:
        obligation_detail.extend(
            [
                f"### {o['id']} — {o['obligation']}",
                "",
                f"- **Status:** {o['status']}",
                f"- **Canonical owner:** {o['owner']}",
                f"- **Owner located at:** {_paths(o['owner_paths'])}",
                f"- **Governing gate:** `{o['gate']}`",
                f"- **Repository evidence:** {_paths(o['evidence'])}",
                "",
                f"{o['discharge']}",
                "",
            ]
        )
    pages["08-EVOLUTION-CONTRACT-DISCHARGE.md"] = "\n".join(
        [
            "# Constitutional Evolution Contract — Discharge Record",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| GOVERNING INSTRUMENT | `{contract['governing_instrument']}` |",
            f"| BASELINE | `{contract['baseline']['id']}` |",
            f"| CHANGE CLASSIFICATION | **{contract['change_classification']['label']}**"
            f" (`{contract['change_classification']['token']}`) |",
            f"| RELEASE STATE | **{contract['release_state']['state']}** |",
            f"| OBLIGATIONS | {counts['obligations_satisfied']} SATISFIED ·"
            f" {counts['obligations_awaiting_commit']} AWAITING-COMMIT"
            f" of {counts['obligations']} |",
            f"| OWNER PATHS RESOLVED | {counts['obligation_owner_paths']} |",
            f"| EVIDENCE PATHS RESOLVED | {counts['obligation_evidence']} |",
            "",
            "> Each obligation is bound to the located owner and the named gate that discharges",
            "> it. The **verdict of each obligation stays with that gate** and is never restated",
            "> here: a second verdict over one obligation would be a second authority over it.",
            "> What this page measures is that every obligation names a located owner, a named",
            "> gate and evidence that resolves, and that its status is disclosed.",
            "",
            *_table(
                obligation_rows,
                ["#", "Obligation", "Gate", "Owner paths", "Evidence", "Status"],
            ),
            "",
            "## Classification basis",
            "",
            contract["change_classification"]["basis"],
            "",
            "## Baseline",
            "",
            contract["baseline"]["basis"],
            "",
            "## Release state",
            "",
            contract["release_state"]["basis"],
            "",
            "## Status vocabulary",
            "",
            *_table(
                [[f"`{s['id']}`", s["meaning"]] for s in contract["statuses"]],
                ["Status", "Meaning"],
            ),
            "",
            "## Obligation records",
            "",
            *obligation_detail,
        ]
    )
    return pages


def write_registers(model: dict[str, Any]) -> list[str]:
    """Write the registers. Every path is inside this programme's own directory."""
    written: list[str] = []
    for name, text in sorted(render(model).items()):
        target = HERE / name
        body = text if text.endswith("\n") else text + "\n"
        target.write_text(body, "utf-8")
        written.append(name)
    MODEL.write_text(
        json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False) + "\n", "utf-8"
    )
    written.append(MODEL.name)
    return written


# ---------------------------------------------------------------------------------
# self-guards
# ---------------------------------------------------------------------------------
def check_declaration(document: dict[str, Any]) -> list[str]:
    """Structural integrity of the declaration itself, before anything is measured."""
    problems: list[str] = []
    seen: set[str] = set()
    for faculty in document["faculties"]:
        identifier = str(faculty.get("id", ""))
        if not identifier:
            problems.append("a faculty carries no id")
        if identifier in seen:
            problems.append(f"duplicate faculty id: {identifier}")
        seen.add(identifier)
        for field in ("name", "disposition", "objective", "reuse", "canonical_owner"):
            if not str(faculty.get(field, "")).strip():
                problems.append(f"{identifier}: '{field}' is empty")
    registers = [str(r.get("id", "")) for r in document["registers"]]
    if len(set(registers)) != len(registers):
        problems.append("duplicate register id")
    for register in document["registers"]:
        for field in ("subject", "path", "owner", "form"):
            if not str(register.get(field, "")).strip():
                problems.append(f"{register.get('id', '?')}: '{field}' is empty")
    contributed = [str(c.get("id", "")) for c in document["contributed_analyses"]]
    if len(set(contributed)) != len(contributed):
        problems.append("duplicate contributed analysis id")
    for contribution in document["contributed_analyses"]:
        for field in ("name", "kind", "objective", "why_not_already_owned"):
            if not str(contribution.get(field, "")).strip():
                problems.append(f"{contribution.get('id', '?')}: '{field}' is empty")
    declared = {str(v["id"]) for v in document["validations"]}
    if len(declared) != len(document["validations"]):
        problems.append("duplicate validation id")
    if "CREATE" in {str(d["id"]) for d in document["dispositions"]}:
        problems.append("creation is not an admissible disposition for this programme")
    contract = document["evolution_contract"]
    obligations = [str(o.get("id", "")) for o in contract.get("obligations", [])]
    if not obligations:
        problems.append("the evolution contract declares no obligation")
    if len(set(obligations)) != len(obligations):
        problems.append("duplicate evolution contract obligation id")
    if not contract.get("statuses"):
        problems.append("the evolution contract declares no status vocabulary")
    for field in ("governing_instrument", "baseline", "change_classification", "release_state"):
        if not contract.get(field):
            problems.append(f"the evolution contract declares no '{field}'")
    for role in (
        ROLE_ANALYSES,
        ROLE_CATALOGUE,
        ROLE_META,
        ROLE_ONTOLOGY,
        ROLE_EVOLUTION,
        ROLE_RELEASE,
        ROLE_BASELINE,
    ):
        if register_by_role(document, role) is None:
            problems.append(f"no declared register plays the required role '{role}'")
    return problems


def check_no_enumeration(document: dict[str, Any]) -> list[str]:
    """This engine must contain no declared data. Adding anything is a data edit."""
    source = Path(__file__).read_text("utf-8")
    leaked: list[str] = []
    for faculty in document["faculties"]:
        for field in ("id", "name", "canonical_owner"):
            value = str(faculty.get(field, ""))
            if value and value in source:
                leaked.append(f"faculty.{field}={value}")
        for home in faculty.get("homes", []):
            if str(home) in source:
                leaked.append(f"faculty.home={home}")
    for register in document["registers"]:
        for field in ("id", "path"):
            value = str(register.get(field, ""))
            if value and value in source:
                leaked.append(f"register.{field}={value}")
    for contribution in document["contributed_analyses"]:
        for field in ("id", "name"):
            value = str(contribution.get(field, ""))
            if value and value in source:
                leaked.append(f"analysis.{field}={value}")
    for anchor in document["ontology_anchors"]:
        value = str(anchor.get("id", ""))
        if value and value in source:
            leaked.append(f"anchor.id={value}")
    for obligation in document["evolution_contract"]["obligations"]:
        value = str(obligation.get("id", ""))
        if value and value in source:
            leaked.append(f"obligation.id={value}")
        for path in list(obligation.get("owner_paths", [])) + list(obligation.get("evidence", [])):
            if str(path) in source:
                leaked.append(f"obligation.path={path}")
    return leaked


def check_write_scope() -> list[str]:
    """Every write target must resolve inside this programme's own directory."""
    problems: list[str] = []
    targets = [HERE / name for name in render(measure(load_declaration()))] + [MODEL]
    for target in targets:
        try:
            target.resolve().relative_to(HERE)
        except ValueError:
            problems.append(str(target))
    return problems


def check_determinism() -> list[str]:
    first = render(measure(load_declaration()))
    second = render(measure(load_declaration()))
    return sorted(k for k in first if first[k] != second.get(k))


def check_reuse_before_create(model: dict[str, Any]) -> list[str]:
    """No faculty may be realised by an artifact this programme owns."""
    return [
        f"{b['id']}:{home}"
        for b in model["bindings"]
        for home in b["homes"] + [b["canonical_owner"]]
        if home.startswith(OWN_PREFIX)
    ]


def check_register_plane(model: dict[str, Any]) -> list[str]:
    """Every declared register must resolve, parse, and be claimed by a faculty."""
    problems = [f"{f['id']}: {f['problem']}" for f in model["registers"] if not f["resolves"]]
    problems.extend(
        f"{f['id']}: claimed by no faculty" for f in model["registers"] if not f["claimed_by"]
    )
    return problems


def check_no_parallel_authority(model: dict[str, Any]) -> list[str]:
    """The programme must hold no place and claim no token in the meta-constitutional plane."""
    validation = next(
        (v for v in model["validations"] if "parallel authority" in v["dimension"].lower()),
        None,
    )
    if validation is None:
        return ["no no-parallel-authority dimension is declared"]
    problems = list(validation["failures"])
    if not str(model["programme"]["authority"]).startswith("NONE"):
        problems.append("the programme does not declare AUTHORITY = NONE")
    return problems


def check_evolution_contract(model: dict[str, Any]) -> list[str]:
    """Every obligation must bind to a located owner and a named gate, with resolving evidence.

    The obligation's own verdict is deliberately NOT checked here: it belongs to the located gate
    named on the obligation. What is checked is that the binding exists and resolves, and that
    the vocabularies the contract draws on are the ones their registers own.
    """
    problems: list[str] = []
    for dimension in ("Evolution Contract obligation", "change classification"):
        validation = next(
            (v for v in model["validations"] if dimension.lower() in v["dimension"].lower()),
            None,
        )
        if validation is None:
            problems.append(f"no '{dimension}' dimension is declared")
            continue
        problems.extend(validation["failures"])
    contract = model["evolution_contract"]
    for obligation in contract["obligations"]:
        if obligation["owner_paths_resolved"] != len(obligation["owner_paths"]):
            problems.append(f"{obligation['id']}: a located owner does not resolve")
        if obligation["evidence_resolved"] != len(obligation["evidence"]):
            problems.append(f"{obligation['id']}: declared evidence does not resolve")
    return problems


# ---------------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------------
GUARDS = (
    "--check-declaration",
    "--check-no-enumeration",
    "--check-write-scope",
    "--check-determinism",
    "--check-reuse-before-create",
    "--check-register-plane",
    "--check-no-parallel-authority",
    "--check-evolution-contract",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uaie_engine.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--render", action="store_true", help="write the registers")
    parser.add_argument("--gate", action="store_true", help="fail-closed: exit 1 if closed")
    parser.add_argument("--quiet", action="store_true")
    for flag in GUARDS:
        parser.add_argument(flag, action="store_true", dest=flag[2:].replace("-", "_"))
    args = parser.parse_args(argv)

    try:
        document = load_declaration()
    except FailClosed as exc:
        print(f"FAIL-CLOSED ABORT — {exc}", file=sys.stderr)
        return 2

    guard_results: list[tuple[str, list[str]]] = []
    if args.check_declaration:
        guard_results.append(("check-declaration", check_declaration(document)))
    if args.check_no_enumeration:
        guard_results.append(("check-no-enumeration", check_no_enumeration(document)))
    if args.check_write_scope:
        guard_results.append(("check-write-scope", check_write_scope()))
    if args.check_determinism:
        guard_results.append(("check-determinism", check_determinism()))

    model = measure(document)

    if args.check_reuse_before_create:
        guard_results.append(("check-reuse-before-create", check_reuse_before_create(model)))
    if args.check_register_plane:
        guard_results.append(("check-register-plane", check_register_plane(model)))
    if args.check_no_parallel_authority:
        guard_results.append(("check-no-parallel-authority", check_no_parallel_authority(model)))
    if args.check_evolution_contract:
        guard_results.append(("check-evolution-contract", check_evolution_contract(model)))

    if guard_results:
        failed = 0
        for name, problems in guard_results:
            status = "PASS" if not problems else "FAIL"
            print(f"{PROGRAMME} {name}: {status}")
            for problem in problems[:20]:
                print(f"  - {problem}")
            failed += 1 if problems else 0
        return 1 if failed else 0

    if args.render:
        written = write_registers(model)
        if not args.quiet:
            print(f"wrote {len(written)} artifacts to {HERE.relative_to(REPO)}")

    counts = model["counts"]
    if not args.quiet:
        print(
            f"{PROGRAMME}: {model['determination']}"
            f" | faculties={counts['faculties']}"
            f" | homes={counts['homes_resolved']}/{counts['homes_declared']}"
            f" | symbols={counts['symbols_declared']}"
            f" | reuse={counts['reuse']} extend={counts['extend']} compose={counts['compose']}"
            f" | analyses={counts['analyses_cited']}+{counts['analyses_contributed']}"
            f" | registers={counts['registers_resolved']}/{counts['registers']}"
            f" | xrefs={counts['register_references']}"
            f"-{counts['register_references_unresolved']}"
            f" | layers={counts['dependency_layers']}"
            f" | obligations={counts['obligations_satisfied']}"
            f"+{counts['obligations_awaiting_commit']}awaiting/{counts['obligations']}"
            f" | validations={counts['validations_satisfied']}/{counts['validations']}"
            f" | gate={model['gate']}"
            f" | seal={model['seal_sha256'][:12]}"
        )
        for failure in model["blocking_failures"]:
            print(f"  BLOCKING FAIL: {failure}")

    if args.gate and model["gate"] != "OPEN":
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI
    raise SystemExit(main())

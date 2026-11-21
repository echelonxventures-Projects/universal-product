"""UISD-000001 Part 02 — the eleven laws, each with a computable check.

A law whose compliance nobody computes is manual governance, so every law in
``uisd-declaration.json`` names a check, :data:`LAW_CHECKS` implements it, and
:meth:`engine.infinite_scope.model.InfiniteScopeContract.validate` refuses to construct a
contract whose law names a missing check — or whose check no law claims.

The checks are pure functions of ``(contract, repository_root)``. They read the
declaration, read declared files, and import declared modules in-process. They read no
clock, open no socket, spawn no subprocess and write nothing, so a verdict is reproducible
and a gate built on them cannot dirty the tree.

Four checks are worth reading closely, because they are the ones that make the mission's
claims measurable rather than aspirational:

* :func:`check_scope_expansion_capacity` does **not** assert that no enumeration is
  closed. That would be false — ``engine/uckp/facets.py`` closes 33 facets on purpose so
  that every vocabulary inside them can stay open — and a false law gets disabled. It
  asserts that no enumeration is closed *silently*: each one names the invariant that
  closes it and the path by which a member is admitted.
* :func:`check_relationship_model_expands` proves openness by **performing** an extension
  in memory on every run, then proving the original vocabulary did not move. A comment
  claiming a vocabulary is append-only is not evidence; a non-mutating extension is.
* :func:`check_no_active_permanence_declaration` is a ratchet, not a search. Every located
  occurrence must already be declared with a class and a reason, so a new permanence
  declaration cannot enter the scanned roots unnoticed. Note the check's name: it avoids
  the literal token it detects, because a detector that matches its own source is its own
  first finding, and declaring an exception for it would have blunted the ratchet on the
  one file most likely to be edited.
"""

from __future__ import annotations

import ast
import copy
import importlib
import json
import os
import re
import tomllib
from collections.abc import Callable, Mapping
from typing import Any

from engine.infinite_scope import detector
from engine.infinite_scope.model import (
    AdmissionExercise,
    ExerciseConsumer,
    FreezeScan,
    InfiniteScopeContract,
    InfiniteScopeError,
)

#: Where the declaration lives, relative to the repository root.
DECLARATION_PATH = "00-MASTER/UISD-000001/uisd-declaration.json"


def repo_root() -> str:
    """Return the repository root, derived from this file's location."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_declaration(path: str | None = None) -> dict[str, Any]:
    """Load the declaration.

    Raises:
        InfiniteScopeError: the declaration is absent or unreadable. Fail closed: a
            declaration that cannot be read is not a declaration that permits everything.
    """
    target = path or os.path.join(repo_root(), DECLARATION_PATH)
    try:
        with open(target, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise InfiniteScopeError("declaration is unreadable", subject=target) from exc
    if not isinstance(doc, dict):
        raise InfiniteScopeError("declaration is not a mapping", subject=target)
    return doc


def load_contract(path: str | None = None) -> InfiniteScopeContract:
    """Rehydrate and validate the contract.

    Raises:
        InfiniteScopeError: the contract is unsound. Every reason is reported at once,
            because a half-diagnosed contract wastes a cycle.
    """
    contract = InfiniteScopeContract.from_declaration(load_declaration(path))
    problems = contract.validate(frozenset(LAW_CHECKS), frozenset(ADMISSION_FORMS))
    if problems:
        raise InfiniteScopeError("contract is unsound: " + "; ".join(problems))
    return contract


# ----------------------------------------------------------------- shared measurement


def _exists(repo: str, relpath: str) -> bool:
    """Report whether a declared repository-relative path exists."""
    return os.path.exists(os.path.join(repo, relpath))


def _read_text(repo: str, relpath: str) -> str | None:
    """Read a declared file, or return None if it cannot be read."""
    try:
        with open(os.path.join(repo, relpath), encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return None


def _read_json(repo: str, relpath: str) -> Any:
    """Read a declared JSON file, or return None if it cannot be read or parsed."""
    text = _read_text(repo, relpath)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _symbol(module_name: str, symbol_name: str) -> Any:
    """Import a declared symbol, raising ImportError or AttributeError on absence."""
    module = importlib.import_module(module_name)
    return getattr(module, symbol_name)


def candidate_files(repo: str, scan: FreezeScan) -> list[str]:
    """Return the repository-relative files the scan covers, deterministically ordered."""
    found: set[str] = set()
    for root in scan.roots:
        base = os.path.normpath(os.path.join(repo, root))
        if root in scan.root_depth_zero_only:
            try:
                names = os.listdir(base)
            except OSError:
                continue
            for name in names:
                path = os.path.join(base, name)
                if os.path.isfile(path) and os.path.splitext(name)[1] in scan.extensions:
                    found.add(os.path.relpath(path, repo).replace(os.sep, "/"))
            continue
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [
                name
                for name in dirnames
                if name not in scan.excluded_directory_names
                and not (scan.excluded_dot_directories and name.startswith("."))
            ]
            for name in filenames:
                if os.path.splitext(name)[1] in scan.extensions:
                    joined = os.path.join(dirpath, name)
                    found.add(os.path.relpath(joined, repo).replace(os.sep, "/"))
    return sorted(found)


def scan_occurrences(repo: str, scan: FreezeScan) -> dict[str, int]:
    """Count permanence-vocabulary occurrences per file across the declared roots."""
    pattern = re.compile(scan.status_pattern) if scan.status_pattern else None
    counts: dict[str, int] = {}
    for relpath in candidate_files(repo, scan):
        text = _read_text(repo, relpath)
        if text is None:
            continue
        lowered = text.lower()
        total = sum(lowered.count(phrase) for phrase in scan.phrases)
        if pattern is not None:
            total += len(pattern.findall(text))
        if total:
            counts[relpath] = total
    return counts


# --------------------------------------------------------------------------- the checks
# Each returns the violations it found. An empty tuple means the law holds.


def check_scope_expansion_capacity(contract: InfiniteScopeContract, repo: str) -> tuple[str, ...]:
    """ISD-L-01 — no enumeration is closed silently."""
    problems: list[str] = []
    if not contract.closed_enumerations:
        return (
            "no closed enumeration is disclosed; an empty disclosure list would make this "
            "law vacuous rather than satisfied",
        )
    for disclosure in contract.closed_enumerations:
        if not disclosure.closing_invariant.strip():
            problems.append(f"{disclosure.disclosure_id}: discloses no closing invariant")
        if not disclosure.admission.strip():
            problems.append(f"{disclosure.disclosure_id}: discloses no admission path")
        if not _exists(repo, disclosure.declared_at):
            problems.append(
                f"{disclosure.disclosure_id}: declared_at {disclosure.declared_at} does not exist"
            )
        if not disclosure.intentional and not disclosure.gap:
            problems.append(
                f"{disclosure.disclosure_id}: closure is not intentional and names no gap, "
                "so it is an undisclosed finite assumption"
            )
    # The law says EVERY closed enumeration, not every disclosed one. Validating only the
    # disclosures measured the list against itself and could never see the repository.
    problems.extend(_undisclosed_closure_ceiling(contract, repo))
    return tuple(problems)


def _undisclosed_closure_ceiling(contract: InfiniteScopeContract, repo: str) -> tuple[str, ...]:
    """The second half of ISD-L-01: closures the disclosure list does not cover.

    ISD-L-01 measures the disclosures. Nothing measured the gap between the disclosures and
    the repository, and the declaration says why it cannot be closed by assertion: a claim
    of exhaustiveness would be the finite assumption the principle prohibits. So this law
    does not claim exhaustiveness. It enumerates the SHAPES a closed enumeration takes in
    Python, counts the occurrences no disclosure covers, and holds that count as a
    two-sided ratchet.

    TWO-SIDED, AND THE LOWER SIDE IS THE POINT. Above the ceiling is new debt: an
    enumeration entered the tree undisclosed. Below it is debt repaid without tightening —
    slack a future regression can occupy in silence. The same discipline UEC-L-11 applies
    to its five counters, applied to this one, because a ceiling that only ever refuses
    upward is a budget rather than a ratchet.

    IT IS DELIBERATELY NOT ZERO TODAY. The measured population is in the hundreds, and a
    law that fails on the day it lands is a law somebody disables. Starting at the measured
    value makes every NEW closure fail immediately while the standing population is driven
    down by disclosure, which is the only direction the ratchet permits.
    """
    config = contract.closure_detection
    ceiling = config.get("undisclosed_ceiling")
    if not isinstance(ceiling, int):
        return ("closure_detection declares no integer undisclosed_ceiling",)
    found = detector.detect(
        repo,
        tuple(config.get("roots", ())),
        frozenset(config.get("excluded_directory_names", ())),
        tuple(config.get("excluded_path_fragments", ())),
    )
    if not found:
        return (
            "the detector located no closed enumeration at all; a detector that finds "
            "nothing is broken rather than satisfied",
        )
    disclosed = frozenset((d.declared_at, d.enumeration) for d in contract.closed_enumerations)
    open_ones = detector.undisclosed(found, disclosed)
    measured = len(open_ones)
    if measured > ceiling:
        sample = "; ".join(c.describe() for c in open_ones[:5])
        return (
            f"{measured} undisclosed closed enumeration(s) exceed the declared ceiling "
            f"{ceiling}. Each names a set whose membership can only change by editing the "
            f"module, which UCKP-ART-17 refuses. Disclose it with a closing invariant and "
            f"an admission path, or open it. First: {sample}",
        )
    if measured < ceiling:
        return (
            f"{measured} undisclosed closed enumeration(s) is BELOW the declared ceiling "
            f"{ceiling}. Debt was repaid without tightening the ratchet, leaving slack a "
            f"future regression can occupy in silence. Lower undisclosed_ceiling to "
            f"{measured}.",
        )
    return ()


def check_direction_expansion_capacity(
    contract: InfiniteScopeContract, repo: str
) -> tuple[str, ...]:
    """ISD-L-02 — the relationship type space is pattern-bound, not enumeration-bound."""
    problems: list[str] = []
    config = contract.direction_expansion
    schema_path = str(config.get("edge_schema", ""))
    schema = _read_json(repo, schema_path)
    if not isinstance(schema, dict):
        return (f"edge schema {schema_path} is absent or unparseable",)
    node: Any = schema
    for step in config.get("type_property_path", []):
        if not isinstance(node, dict) or step not in node:
            return (f"edge schema {schema_path} has no property path {step!r}",)
        node = node[step]
    if not isinstance(node, dict):
        return (f"edge schema {schema_path}: the type property is not a mapping",)
    for key in config.get("forbidden_property_keys", []):
        if key in node:
            problems.append(
                f"edge schema constrains relationship type with {key!r}, which closes the "
                "direction space"
            )
    for key in config.get("required_property_keys", []):
        if key not in node:
            problems.append(f"edge schema relationship type declares no {key!r}")
    admission = config.get("freeform_admission")
    if not isinstance(admission, dict):
        return (*problems, "no freeform admission path is declared")
    declared_at = str(admission.get("declared_at", ""))
    symbol = str(admission.get("symbol", ""))
    expected = str(admission.get("expected", ""))
    text = _read_text(repo, declared_at)
    if text is None:
        problems.append(f"freeform admission source {declared_at} is unreadable")
    elif not re.search(rf"{re.escape(symbol)}\s*=\s*[\"']{re.escape(expected)}[\"']", text):
        problems.append(
            f"{declared_at} does not bind {symbol} to {expected!r}, so a new relationship "
            "type would require a configuration edit"
        )
    return tuple(problems)


def check_principle_inherits_itself(contract: InfiniteScopeContract, repo: str) -> tuple[str, ...]:
    """ISD-L-03 — the principle is subject to its own laws and holds a birth record."""
    problems: list[str] = []
    subjects = contract.self_application.get("subject_of_own_laws")
    if not isinstance(subjects, list) or contract.artifact_id not in subjects:
        problems.append(
            f"{contract.artifact_id} does not name itself in self_application."
            "subject_of_own_laws, so the principle exempts itself"
        )
    if contract.self_application.get("declares_independent_lifecycle") is not False:
        problems.append("the principle does not declare independent_lifecycle false")
    if contract.lifecycle_inheritance.get("independent_lifecycle_defined") is not False:
        problems.append(
            "lifecycle_inheritance does not declare independent_lifecycle_defined false"
        )
    if not str(contract.lifecycle_inheritance.get("lifecycle_owner", "")).strip():
        problems.append("lifecycle_inheritance names no lifecycle owner")
    authority_over = contract.self_application.get("declares_authority_over")
    if authority_over:
        problems.append(
            f"the principle claims authority over {authority_over!r}; it is a pervasive "
            "property, not an authority layer"
        )
    identity = str(contract.self_application.get("birth_identity", ""))
    ledger_path = str(contract.self_application.get("birth_ledger", ""))
    ledger = _read_json(repo, ledger_path)
    if not isinstance(ledger, dict):
        problems.append(f"birth ledger {ledger_path} is absent or unparseable")
    elif identity not in ledger.get("births", {}):
        problems.append(f"{identity} holds no birth record, so the principle exists anonymously")
    return tuple(problems)


def check_lifecycle_applies_to_itself(
    contract: InfiniteScopeContract, repo: str
) -> tuple[str, ...]:
    """ISD-L-04 — the lifecycle stage graph is open and its projection has not drifted."""
    problems: list[str] = []
    config = contract.lifecycle_openness
    manifest_path = str(config.get("manifest", ""))
    manifest = _read_json(repo, manifest_path)
    if not isinstance(manifest, dict):
        return (f"lifecycle manifest {manifest_path} is absent or unparseable",)
    declared = manifest.get("manifest")
    if not isinstance(declared, dict):
        return (f"lifecycle manifest {manifest_path} holds no manifest block",)
    for flag, expected in dict(config.get("required_manifest_flags", {})).items():
        if declared.get(flag) != expected:
            problems.append(
                f"lifecycle manifest declares {flag}={declared.get(flag)!r}, not {expected!r}"
            )
    for field in config.get("required_manifest_fields", []):
        if not str(declared.get(field, "")).strip():
            problems.append(f"lifecycle manifest declares no {field!r}")
    module_name = str(config.get("alignment_module", ""))
    function_name = str(config.get("alignment_function", ""))
    try:
        align = _symbol(module_name, function_name)
    except (ImportError, AttributeError) as exc:
        return (*problems, f"alignment {module_name}.{function_name} is unavailable: {exc}")
    divergences = tuple(align(manifest))
    for divergence in divergences:
        problems.append(f"lifecycle projection diverges from its manifest: {divergence}")
    return tuple(problems)


def check_evolution_applies_to_itself(
    contract: InfiniteScopeContract, repo: str
) -> tuple[str, ...]:
    """ISD-L-05 — the evolution cycle has no terminal stage and returns to its first."""
    problems: list[str] = []
    config = contract.evolution_openness
    module_name = str(config.get("module", ""))
    try:
        cycle = tuple(_symbol(module_name, str(config.get("cycle_symbol", ""))))
        is_terminal = _symbol(module_name, str(config.get("terminal_predicate", "")))
        next_stage = _symbol(module_name, str(config.get("successor_function", "")))
    except (ImportError, AttributeError) as exc:
        return (f"evolution module {module_name} is unusable: {exc}",)
    minimum = int(config.get("minimum_stages", 2))
    if len(cycle) < minimum:
        problems.append(f"the evolution cycle declares {len(cycle)} stages, fewer than {minimum}")
    if not cycle:
        return tuple(problems)
    for stage in cycle:
        if is_terminal(stage):
            problems.append(f"evolution stage {stage!r} is terminal, so evolution can end")
        if next_stage(stage) not in cycle:
            problems.append(f"evolution stage {stage!r} has a successor outside the cycle")
    if next_stage(cycle[-1]) != cycle[0]:
        problems.append(
            "the last evolution stage does not return to the first, so the cycle does not wrap"
        )
    return tuple(problems)


def check_relationship_model_expands(contract: InfiniteScopeContract, repo: str) -> tuple[str, ...]:
    """ISD-L-06 — a relationship vocabulary admits a term without amendment or mutation."""
    problems: list[str] = []
    config = contract.relationship_expansion
    module_name = str(config.get("module", ""))
    probe_id = str(config.get("probe_term_id", ""))
    method_name = str(config.get("extension_method", ""))
    try:
        term_type = _symbol(module_name, str(config.get("term_symbol", "")))
    except (ImportError, AttributeError) as exc:
        return (f"relationship vocabulary module {module_name} is unusable: {exc}",)
    vocabularies = config.get("vocabularies")
    if not isinstance(vocabularies, list) or not vocabularies:
        return ("no relationship vocabulary is declared, so expansion is unmeasured",)
    for entry in vocabularies:
        symbol_name = str(entry.get("symbol", ""))
        try:
            vocabulary = _symbol(module_name, symbol_name)
            extend = getattr(vocabulary, method_name)
        except (ImportError, AttributeError) as exc:
            problems.append(f"{symbol_name}: unusable: {exc}")
            continue
        before = len(vocabulary.terms)
        baseline = entry.get("population_at_baseline")
        if isinstance(baseline, int) and before < baseline:
            problems.append(
                f"{symbol_name}: holds {before} terms, fewer than the {baseline} disclosed; "
                "an append-only vocabulary cannot shrink"
            )
        probe = term_type(
            term_id=probe_id,
            definition="in-memory probe that the vocabulary admits a term by registration",
        )
        extended = extend(probe)
        if extended is vocabulary:
            problems.append(f"{symbol_name}: extension returned the original vocabulary")
        if not extended.has(probe_id):
            problems.append(f"{symbol_name}: refused a well-formed new term, so the tier is closed")
        if vocabulary.has(probe_id):
            problems.append(f"{symbol_name}: extension mutated the original vocabulary")
        if len(extended.terms) != before + 1:
            problems.append(
                f"{symbol_name}: extension produced {len(extended.terms)} terms, not {before + 1}"
            )
    return tuple(problems)


def check_no_active_permanence_declaration(
    contract: InfiniteScopeContract, repo: str
) -> tuple[str, ...]:
    """ISD-L-07 — every permanence occurrence is a disclosed, classified, non-active site."""
    problems: list[str] = []
    scan = contract.freeze_scan
    declared = {site.path: site for site in scan.preserved_sites}
    if len(declared) != len(scan.preserved_sites):
        problems.append("freeze_scan declares the same path as a preserved site more than once")
    found = scan_occurrences(repo, scan)
    for path in sorted(found):
        if path not in declared:
            problems.append(
                f"{path}: carries {found[path]} permanence occurrence(s) and is not a declared "
                "preserved site; a new permanence declaration entered the scanned roots"
            )
    for site in scan.preserved_sites:
        if site.site_class == "A":
            problems.append(
                f"{site.site_id} ({site.path}): classified A — an active lifecycle declaration "
                "forbidding future change is not a category a site may be preserved in"
            )
        if site.site_class not in scan.classes:
            problems.append(f"{site.site_id}: class {site.site_class!r} is not declared")
        if site.site_class in scan.count_enforced_classes:
            actual = found.get(site.path, 0)
            if actual != site.occurrences:
                problems.append(
                    f"{site.site_id} ({site.path}): class {site.site_class} is count-enforced and "
                    f"carries {actual} occurrence(s), not the {site.occurrences} disclosed"
                )
    return tuple(problems)


def check_baseline_temporal_qualification(
    contract: InfiniteScopeContract, repo: str
) -> tuple[str, ...]:
    """ISD-L-08 — every baseline surface parses its coordinate or discloses that it cannot."""
    problems: list[str] = []
    if not contract.baseline_surfaces:
        return ("no baseline surface is declared, so temporal qualification is unmeasured",)
    try:
        parse = _symbol(contract.baseline_resolver_module, contract.baseline_resolver_function)
    except (ImportError, AttributeError) as exc:
        return (
            f"temporal resolver {contract.baseline_resolver_module}."
            f"{contract.baseline_resolver_function} is unavailable: {exc}",
        )
    for surface in contract.baseline_surfaces:
        if not _exists(repo, surface.surface):
            problems.append(f"{surface.surface_id}: surface {surface.surface} does not exist")
            continue
        if not surface.qualified:
            if not surface.deferred_to:
                problems.append(
                    f"{surface.surface_id}: declares no temporal coordinate and names no owner "
                    "it is deferred to, so the non-conformance is undisclosed"
                )
            if not surface.gap:
                problems.append(
                    f"{surface.surface_id}: declares no temporal coordinate and records no gap"
                )
            continue
        if not surface.sample:
            problems.append(f"{surface.surface_id}: declared qualified but carries no sample")
            continue
        try:
            parse(surface.sample, authority=contract.artifact_id)
        except Exception as exc:  # noqa: BLE001 - any refusal is the finding
            problems.append(
                f"{surface.surface_id}: declared qualified but sample {surface.sample!r} does "
                f"not parse under the temporal contract: {exc}"
            )
            continue
        text = _read_text(repo, surface.surface)
        if text is not None and surface.sample not in text:
            problems.append(
                f"{surface.surface_id}: sample {surface.sample!r} is absent from "
                f"{surface.surface}, so the disclosure describes no recorded coordinate"
            )
    return tuple(problems)


def check_technology_is_evolutionary_state(
    contract: InfiniteScopeContract, repo: str
) -> tuple[str, ...]:
    """ISD-L-09 — no runtime pin, no version ceiling, and every toolchain pin disclosed."""
    problems: list[str] = []
    config = contract.technology
    manifest_path = str(config.get("manifest", ""))
    text = _read_text(repo, manifest_path)
    if text is None:
        return (f"technology manifest {manifest_path} is unreadable",)
    try:
        manifest = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return (f"technology manifest {manifest_path} is unparseable: {exc}",)
    project = manifest.get("project", {})
    runtime = project.get("dependencies", [])
    if config.get("runtime_dependencies_must_be_empty") and runtime:
        problems.append(
            f"{manifest_path} declares {len(runtime)} runtime dependency(ies): {runtime!r}; "
            "a pinned runtime encodes a technology as constitutional truth"
        )
    requires_key = str(config.get("requires_python_key", "requires-python"))
    requirement = str(project.get(requires_key, ""))
    if not requirement:
        problems.append(f"{manifest_path} declares no {requires_key}")
    for operator in config.get("forbidden_version_operators", []):
        if operator in requirement:
            problems.append(
                f"{requires_key} is {requirement!r}, which carries {operator!r}: a ceiling or an "
                "exact pin makes the language version a constitutional truth, not a state"
            )
    disclosed = {pin.requirement for pin in contract.declared_pins}
    actual = {
        str(requirement_text)
        for group in project.get("optional-dependencies", {}).values()
        for requirement_text in group
        if "==" in str(requirement_text)
    }
    for undisclosed in sorted(actual - disclosed):
        problems.append(f"{undisclosed}: pinned in {manifest_path} and not disclosed with a reason")
    for stale in sorted(disclosed - actual):
        problems.append(f"{stale}: disclosed as a pin but no longer pinned in {manifest_path}")
    return tuple(problems)


def check_capability_seed_openness(contract: InfiniteScopeContract, repo: str) -> tuple[str, ...]:
    """ISD-L-10 — the capability model is a seed, and every enumeration names its admission."""
    problems: list[str] = []
    if contract.capability_final:
        problems.append(
            "the capability model declares itself final, which closes the capability universe"
        )
    if not contract.capability_enumerations:
        return (*problems, "no capability enumeration is declared, so openness is unmeasured")
    for enumeration in contract.capability_enumerations:
        if not enumeration.admission.strip():
            problems.append(f"{enumeration.enumeration_id}: names no admission path")
        if not _exists(repo, enumeration.declared_at):
            problems.append(
                f"{enumeration.enumeration_id}: declared_at {enumeration.declared_at} "
                "does not exist"
            )
    if not any(enumeration.open_set for enumeration in contract.capability_enumerations):
        problems.append("no declared capability enumeration is open, so the seed model cannot grow")
    return tuple(problems)


# ------------------------------------------------------- ISD-L-11 admission exercises
# check_relationship_model_expands proves openness by PERFORMING the extension in memory,
# for one population, through one mechanism. What follows generalises that to every
# population whose declared admission path claims the change is data alone — the only
# class where the claim can be falsified. An amendment-bound closure claims nothing of the
# sort and is deliberately out of scope: a law that demanded exercisability of ISD-CE-01
# would be false, and a false law gets disabled.
#
# Nothing is registered and nothing is written. Every exercise runs on a deep copy or a
# freshly constructed reader, which is what keeps this inside ISD-BND-08.


def _pointer(document: Any, pointer: str) -> Any:
    """Resolve a slash-delimited pointer into a loaded document, or return None."""
    node = document
    for token in [part for part in pointer.split("/") if part]:
        if not isinstance(node, Mapping) or token not in node:
            return None
        node = node[token]
    return node


def _synthetic_member(exercise: AdmissionExercise, population: list[Any], prefix: str) -> Any:
    """Build the probe member: a declared sibling, with the declared overrides applied.

    Deriving it from a sibling rather than writing a literal is what makes the probe
    well-formed by construction for a population this engine knows nothing about.
    """
    overrides = exercise.target.get("probe_overrides")
    if not isinstance(overrides, Mapping):
        raise InfiniteScopeError(f"{exercise.exercise_id}: target declares no probe_overrides")
    index = exercise.target.get("probe_from_sibling")
    member: Any
    if isinstance(index, int) and 0 <= index < len(population):
        member = copy.deepcopy(population[index])
    else:
        member = {}
    if not isinstance(member, dict):
        raise InfiniteScopeError(f"{exercise.exercise_id}: sibling member is not a mapping")
    member.update(copy.deepcopy(dict(overrides)))
    identifier = str(member.get(str(exercise.target.get("id_field", "id")), ""))
    if prefix and not identifier.startswith(prefix):
        raise InfiniteScopeError(
            f"{exercise.exercise_id}: probe id {identifier!r} does not carry the declared "
            f"prefix {prefix!r}, so it could collide with a real member"
        )
    return member


def _appended_document(exercise: AdmissionExercise, repo: str, prefix: str) -> Any:
    """Return a DEEP COPY of the declared document with one synthetic member appended."""
    document = _read_json(repo, exercise.declared_owner)
    if document is None:
        raise InfiniteScopeError(
            f"{exercise.exercise_id}: {exercise.declared_owner} is absent or unparseable"
        )
    mutated = copy.deepcopy(document)
    pointer = str(exercise.target.get("pointer", ""))
    population = _pointer(mutated, pointer)
    if not isinstance(population, list):
        raise InfiniteScopeError(
            f"{exercise.exercise_id}: pointer {pointer!r} does not resolve to a list"
        )
    population.append(_synthetic_member(exercise, population, prefix))
    return mutated


def form_document_append(exercise: AdmissionExercise, repo: str, prefix: str) -> Any:
    """Deliver the appended document to consumers as a plain mapping."""
    return _appended_document(exercise, repo, prefix)


def form_reader_document_append(exercise: AdmissionExercise, repo: str, prefix: str) -> Any:
    """Deliver the appended document through the owner's own declared reader.

    Distinct from :func:`form_document_append` because the reader is where that owner's
    structural validation lives: an admission this form admits has passed the owner's real
    read path, not merely a dictionary update.
    """
    mutated = _appended_document(exercise, repo, prefix)
    module = str(exercise.target.get("reader_module", ""))
    dotted = str(exercise.target.get("reader_function", ""))
    if not module or not dotted:
        raise InfiniteScopeError(f"{exercise.exercise_id}: target declares no reader")
    head, _, rest = dotted.partition(".")
    factory = _symbol(module, head)
    for attribute in [part for part in rest.split(".") if part]:
        factory = getattr(factory, attribute)
    return factory(mutated, source=f"<{exercise.exercise_id} in-memory probe>")


#: Admission form to the handler that performs it. Two-way, exactly like LAW_CHECKS: an
#: exercise naming an unimplemented form cannot be performed, and a form no exercise names
#: is dead code wearing the appearance of exercisability. Disclosed as ISD-CE-11.
ADMISSION_FORMS: dict[str, Callable[[AdmissionExercise, str, str], Any]] = {
    "document_append": form_document_append,
    "reader_document_append": form_reader_document_append,
}


def _callable_refusal(consumer: ExerciseConsumer, subject: Any) -> str:
    """Re-evaluate one importable consumer over the admitted subject."""
    try:
        function = _symbol(consumer.module, consumer.function)
    except (ImportError, AttributeError) as exc:
        return f"consumer {consumer.module}.{consumer.function} is unusable: {exc}"
    try:
        outcome = function(subject)
    except Exception as exc:  # noqa: BLE001 - any refusal is the measurement
        return f"{type(exc).__name__}: {exc}"
    if isinstance(outcome, str):
        return outcome
    if isinstance(outcome, list | tuple):
        return "; ".join(str(item) for item in outcome)
    return ""


def _population_literals(repo: str, consumer: ExerciseConsumer) -> tuple[str, ...]:
    """Locate assertions binding a literal count to the declared population.

    A static read, never an execution: the gate spawns no subprocess and runs no test. The
    subject is resolved through local bindings, so a count over a comprehension derived
    from the population is found even though the comparison names a local.
    """
    found: list[str] = []
    for relpath in consumer.paths:
        text = _read_text(repo, relpath)
        if text is None:
            found.append(f"{relpath}: declared consumer path is unreadable")
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            found.append(f"{relpath}: does not parse: {exc}")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            bound: dict[str, str] = {}
            for inner in ast.walk(node):
                if isinstance(inner, ast.Assign):
                    for target in inner.targets:
                        if isinstance(target, ast.Name):
                            bound[target.id] = ast.unparse(inner.value)
            for inner in ast.walk(node):
                located = _literal_count_subject(inner)
                if located is None:
                    continue
                subject, value = located
                trail = subject
                for _ in range(6):
                    base = trail.split("[")[0].split(".")[0].strip()
                    if base in bound and bound[base] != trail:
                        trail = bound[base]
                    else:
                        break
                if any(token in trail or token in subject for token in consumer.population_tokens):
                    found.append(
                        f"{relpath}:{inner.lineno} binds {value} to {subject!r} "
                        f"(in {node.name})"
                    )
    return tuple(found)


def _literal_count_subject(node: ast.AST) -> tuple[str, int] | None:
    """Return ``(subject, literal)`` when *node* compares a population size to an integer."""
    if not isinstance(node, ast.Compare) or len(node.ops) != 1:
        return None
    if not isinstance(node.ops[0], ast.Eq | ast.NotEq):
        return None
    for left, right in ((node.left, node.comparators[0]), (node.comparators[0], node.left)):
        if not isinstance(right, ast.Constant):
            continue
        if not isinstance(right.value, int) or isinstance(right.value, bool):
            continue
        if isinstance(left, ast.Call) and isinstance(left.func, ast.Name):
            if left.func.id == "len" and left.args:
                return ast.unparse(left.args[0]), right.value
        subject = ast.unparse(left)
        if "count" in subject.lower():
            return subject, right.value
    return None


def _consumer_refusal(consumer: ExerciseConsumer, repo: str, subject: Any) -> str:
    """Return this consumer's refusal, or an empty string when it admits."""
    if consumer.kind == "callable":
        return _callable_refusal(consumer, subject)
    if consumer.kind == "assertion_scan":
        return "; ".join(_population_literals(repo, consumer))
    return f"consumer kind {consumer.kind!r} is not a kind this law can re-evaluate"


def check_admission_path_exercisability(
    contract: InfiniteScopeContract, repo: str
) -> tuple[str, ...]:
    """ISD-L-11 — every declared data-only admission path is exercised, and refusals are named."""
    problems: list[str] = []
    if not contract.admission_exercises:
        return (
            "no admission exercise is declared, so every claim of data-only admission is "
            "unexercised and this law would be vacuous rather than satisfied",
        )
    for exercise in contract.admission_exercises:
        prefix = f"{exercise.exercise_id}"
        if not exercise.admission.strip():
            problems.append(f"{prefix}: declares no admission path")
        if not _exists(repo, exercise.declared_owner):
            problems.append(f"{prefix}: declared owner {exercise.declared_owner} does not exist")
            continue
        handler = ADMISSION_FORMS.get(exercise.form)
        if handler is None:
            problems.append(f"{prefix}: names form {exercise.form!r}, which is not implemented")
            continue
        try:
            subject = handler(exercise, repo, contract.probe_id_prefix)
        except InfiniteScopeError as exc:
            problems.append(f"{prefix}: the admission could not be performed: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - an unperformable admission is a finding
            problems.append(
                f"{prefix}: the admission could not be performed: {type(exc).__name__}: {exc}"
            )
            continue
        for consumer in exercise.consumers:
            actual = _consumer_refusal(consumer, repo, subject)
            problems.extend(_reconcile(exercise, consumer, actual))
    return tuple(problems)


def _reconcile(exercise: AdmissionExercise, consumer: ExerciseConsumer, actual: str) -> list[str]:
    """Hold the declared refusal against the measured one, as a ratchet in both directions."""
    where = f"{exercise.exercise_id} [{exercise.population_id}]"
    owner = consumer.required_owner
    if consumer.refuses_today:
        if not actual:
            return [
                f"{where}: the refusal recorded against {owner} no longer occurs, so the "
                f"record is stale and {consumer.gap} may be closed — correct the declaration"
            ]
        if consumer.expected_refusal not in actual:
            return [
                f"{where}: {owner} refuses differently from the record. "
                f"recorded {consumer.expected_refusal!r}, measured {actual!r}"
            ]
        return []
    if actual:
        return [
            f"{where}: admission {exercise.admission[:80]!r} is REFUSED by {owner} "
            f"— {actual} — and no refusal is recorded for it"
        ]
    return []


#: Law check name to implementation. Every declared law's ``check`` must appear here, and
#: every entry here must be claimed by a law, or the contract refuses to construct.
LAW_CHECKS: dict[str, Callable[[InfiniteScopeContract, str], tuple[str, ...]]] = {
    "scope_expansion_capacity": check_scope_expansion_capacity,
    "direction_expansion_capacity": check_direction_expansion_capacity,
    "principle_inherits_itself": check_principle_inherits_itself,
    "lifecycle_applies_to_itself": check_lifecycle_applies_to_itself,
    "evolution_applies_to_itself": check_evolution_applies_to_itself,
    "relationship_model_expands": check_relationship_model_expands,
    "no_active_permanence_declaration": check_no_active_permanence_declaration,
    "baseline_temporal_qualification": check_baseline_temporal_qualification,
    "technology_is_evolutionary_state": check_technology_is_evolutionary_state,
    "capability_seed_openness": check_capability_seed_openness,
    "admission_path_exercisability": check_admission_path_exercisability,
}


def assess(
    contract: InfiniteScopeContract, repo: str
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    """Measure every law, returning ``(law_id, title, violations)`` in declaration order."""
    return tuple(
        (law.law_id, law.title, LAW_CHECKS[law.check](contract, repo)) for law in contract.laws
    )

"""UCOS-UICM-000001 — measurement of actual repository state, one probe per dimension.

Every closure state in the matrix is produced here, and every one is produced by reading
the tree rather than by reading a claim about the tree. That distinction is the whole
point of the programme: the repository already contains many documents asserting that a
capability is complete, and this module's job is to be unable to repeat those assertions.

Three rules govern every probe.

**A probe that cannot execute returns BLOCKED, never a pass.** A required input that is
absent is not an absence of a problem. This is why :class:`ProbeResult` has no default
state and why the ``UNKNOWN`` state was replaced by ``BLOCKED`` in the declared
vocabulary — an unmeasurable dimension must be indistinguishable, to every downstream
consumer, from a dimension that is failing.

**Evidence is a reference, not a sentence.** Each result carries references into located
sources — a file path, a register key, an identifier, a count — so that a reader can
recompute the finding. A probe that returned only prose would be asserting rather than
measuring, and :mod:`engine.uicm.validation` refuses a closed cell whose evidence set is
empty.

**Probes bind to dimensions by declared name.** ``PROBES`` maps the probe names the
declaration uses to the functions implemented here, and
``ClosureDeclaration.require_probe_bijection`` fails closed if the two sets ever differ.
So a new dimension cannot be declared without a probe, and a probe cannot exist without a
dimension: neither half can drift into decoration.

Two probes deserve a note on what they deliberately do *not* accept.

``probe_evidence`` requires the capability to *produce* evidence. The implementation
catalogue carries an ``evidence_present`` flag and the artifact register carries an
``evidence_class`` for every file, and accepting either would close this dimension for
every capability in the repository. Both are classifications *of* an artifact, not
producers *of* evidence, so both are recorded as references and neither closes the
dimension.

``probe_certification`` requires an *instrument* that can reach a verdict. Being named in
a certification document is not a decision procedure. Accepting mentions would likewise
have closed the dimension everywhere.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from engine.uicm.matrix import CanonicalOwners
from engine.uicm.model import (
    Capability,
    ClosureDeclaration,
    ClosureError,
    ClosureState,
    DimensionDeclaration,
)

#: Identifier families a capability's own documentation may cite to evidence that its
#: architecture is declared. This is a *shape*, not a list of capabilities: it matches
#: the repository's identifier grammar and names no capability, dimension or programme.
_ARCHITECTURE_REFERENCE = re.compile(r"\b[A-Z][A-Z0-9]{1,9}(?:-[A-Z0-9]{1,12})*-\d{2,6}\b")

#: Evidence-format declarations of the form ``ucos-<something>-evidence/<version>``.
_EVIDENCE_FORMAT = re.compile(r"\"(ucos-[a-z0-9-]*evidence[a-z0-9/.-]*)\"")


class MeasurementError(ClosureError):
    """Raised when measurement cannot proceed at all."""


@dataclass(frozen=True, slots=True)
class ProbeResult:
    """One probe's finding: a state, a human-readable finding and evidence references."""

    state: ClosureState
    finding: str
    evidence: tuple[str, ...]

    @classmethod
    def closed(cls, finding: str, evidence: tuple[str, ...]) -> ProbeResult:
        """A satisfied requirement. Refused without evidence — a closed cell must prove it."""
        if not evidence:
            raise MeasurementError(f"a CLOSED result requires evidence: {finding}")
        return cls(state=ClosureState.CLOSED, finding=finding, evidence=evidence)

    @classmethod
    def open(cls, finding: str, evidence: tuple[str, ...] = ()) -> ProbeResult:
        """A measured, unsatisfied requirement."""
        return cls(state=ClosureState.OPEN, finding=finding, evidence=evidence)

    @classmethod
    def blocked(cls, finding: str, evidence: tuple[str, ...] = ()) -> ProbeResult:
        """A requirement that could not be measured, or is blocked by a dependency."""
        return cls(state=ClosureState.BLOCKED, finding=finding, evidence=evidence)


@dataclass(frozen=True, slots=True)
class RepositoryFacts:
    """Everything the probes need, measured once per run.

    Parsing every module of every capability inside every probe would re-parse the tree
    seventeen times and let two probes disagree about what they read. The facts are
    therefore derived once, and the probes are pure functions of them.
    """

    repo: Path
    owners: CanonicalOwners
    interface_surface: Mapping[str, bool]
    architecture_doc: Mapping[str, str]
    architecture_refs: Mapping[str, tuple[str, ...]]
    module_names: Mapping[str, frozenset[str]]
    evidence_formats: Mapping[str, tuple[str, ...]]
    unresolved_imports: Mapping[str, tuple[str, ...]]
    resolved_imports: Mapping[str, int]
    test_files: Mapping[str, tuple[str, ...]]
    test_cases: Mapping[str, int]
    workflow_bindings: Mapping[str, tuple[str, ...]]
    verification_bound: Mapping[str, bool]
    entrypoints: Mapping[str, tuple[str, ...]]
    implementation_present_states: frozenset[str]

    @classmethod
    def measure(
        cls,
        repo: Path,
        declaration: ClosureDeclaration,
        owners: CanonicalOwners,
        capabilities: tuple[Capability, ...],
    ) -> RepositoryFacts:
        """Derive every probe input from the tracked tree."""
        repo = Path(repo)
        tracked = set(owners.tracked)
        population = declaration.population
        extension = str(population["artifact_extension"])
        marker = str(population["package_marker"])

        interface: dict[str, bool] = {}
        arch_doc: dict[str, str] = {}
        arch_refs: dict[str, tuple[str, ...]] = {}
        modnames: dict[str, frozenset[str]] = {}
        ev_formats: dict[str, tuple[str, ...]] = {}
        unresolved: dict[str, tuple[str, ...]] = {}
        resolved: dict[str, int] = {}

        for capability in capabilities:
            init = f"{capability.location}/{marker}"
            source = _read(repo / init)
            tree = _parse(source, init)
            doc = ast.get_docstring(tree) or "" if tree is not None else ""
            arch_doc[capability.name] = doc
            arch_refs[capability.name] = tuple(sorted(set(_ARCHITECTURE_REFERENCE.findall(doc))))
            interface[capability.name] = _publishes_interface(tree)
            modnames[capability.name] = frozenset(
                path.rsplit("/", 1)[1][: -len(extension)] for path in capability.artifacts
            )
            body = "".join(_read(repo / path) for path in capability.artifacts)
            ev_formats[capability.name] = tuple(sorted(set(_EVIDENCE_FORMAT.findall(body))))
            ok, bad = _import_closure(repo, capability.artifacts, tracked, extension, marker)
            resolved[capability.name] = ok
            unresolved[capability.name] = bad

        test_files, test_cases = _attribute_tests(
            repo, declaration, tracked, extension, capabilities
        )

        workflow_bindings: dict[str, tuple[str, ...]] = {}
        verification_bound: dict[str, bool] = {}
        entrypoints: dict[str, tuple[str, ...]] = {}
        for capability in capabilities:
            workflow_bindings[capability.name] = tuple(
                sorted(
                    name
                    for name, text in owners.workflows.items()
                    if capability.name in text or capability.location in text
                )
            )
            verification_bound[capability.name] = (
                capability.name in owners.verification_text
                or f"{capability.location}/" in owners.verification_text
            )
            entrypoints[capability.name] = tuple(
                sorted(
                    command
                    for command, target in owners.entrypoints.items()
                    if _targets(target, capability.name)
                )
            )

        return cls(
            repo=repo,
            owners=owners,
            interface_surface=interface,
            architecture_doc=arch_doc,
            architecture_refs=arch_refs,
            module_names=modnames,
            evidence_formats=ev_formats,
            unresolved_imports=unresolved,
            resolved_imports=resolved,
            test_files=test_files,
            test_cases=test_cases,
            workflow_bindings=workflow_bindings,
            verification_bound=verification_bound,
            entrypoints=entrypoints,
            implementation_present_states=frozenset(
                str(state)
                for state in declaration.source("implementation_intelligence")[
                    "implementation_present_states"
                ]
            ),
        )


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _parse(source: str, path: str) -> ast.Module | None:
    if not source:
        return None
    try:
        return ast.parse(source)
    except SyntaxError as exc:
        raise MeasurementError(f"tracked module does not parse: {path}") from exc


def _publishes_interface(tree: ast.Module | None) -> bool:
    """True iff the package root publishes an explicit ``__all__`` interface surface."""
    if tree is None:
        return False
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        ):
            return True
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
        ):
            return True
    return False


def _import_targets(repo: Path, path: str) -> set[str]:
    """Absolute module targets a module imports, with relative imports normalized."""
    tree = _parse(_read(repo / path), path)
    if tree is None:
        return set()
    package = path.rsplit("/", 1)[0].replace("/", ".")
    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".")
                base = ".".join(parts[: max(len(parts) - node.level + 1, 1)])
                targets.add(f"{base}.{node.module}" if node.module else base)
            elif node.module:
                targets.add(node.module)
    return targets


def _import_closure(
    repo: Path,
    artifacts: tuple[str, ...],
    tracked: set[str],
    extension: str,
    marker: str,
) -> tuple[int, tuple[str, ...]]:
    """(resolved count, unresolved targets) over first-party imports of ``artifacts``."""
    resolved: set[str] = set()
    unresolved: set[str] = set()
    roots = {path.split("/", 1)[0] for path in tracked if "/" in path}
    for path in artifacts:
        for target in _import_targets(repo, path):
            head = target.split(".")[0]
            if head not in roots:
                continue
            base = target.replace(".", "/")
            if f"{base}{extension}" in tracked or f"{base}/{marker}" in tracked:
                resolved.add(target)
            else:
                unresolved.add(target)
    return len(resolved), tuple(sorted(unresolved))


def _attribute_tests(
    repo: Path,
    declaration: ClosureDeclaration,
    tracked: set[str],
    extension: str,
    capabilities: tuple[Capability, ...],
) -> tuple[dict[str, tuple[str, ...]], dict[str, int]]:
    """Attribute test modules to capabilities by what they import.

    Attribution by filename is the obvious approach and it is wrong here: suites in
    ``engine/tests/unit/``, ``engine/tests/contract/`` and ``engine/tests/integration/``
    exercise capabilities whose names appear nowhere in their paths, so a name heuristic
    silently reports tested capabilities as untested. A suite exercises the capability it
    imports, so imports are what is measured.
    """
    names = {capability.name for capability in capabilities}
    excluded = declaration.excluded_namespaces
    prefixes = tuple(f"{root}/{ns}/" for root in tracked_roots(tracked) for ns in excluded)
    files: dict[str, set[str]] = {name: set() for name in names}
    cases: dict[str, int] = dict.fromkeys(names, 0)
    for path in sorted(tracked):
        if not path.endswith(extension) or not path.startswith(prefixes):
            continue
        if not path.rsplit("/", 1)[1].startswith("test_"):
            continue
        attributed = {
            candidate
            for target in _import_targets(repo, path)
            for candidate in _capability_candidates(target)
            if candidate in names
        }
        if not attributed:
            continue
        count = _count_cases(repo, path)
        for name in attributed:
            files[name].add(path)
            cases[name] += count
    return {name: tuple(sorted(paths)) for name, paths in files.items()}, cases


def tracked_roots(tracked: set[str]) -> tuple[str, ...]:
    """The distinct first path segments of the tracked boundary."""
    return tuple(sorted({path.split("/", 1)[0] for path in tracked if "/" in path}))


def _capability_candidates(target: str) -> tuple[str, ...]:
    """The capability names an import target could belong to (depth 1 and depth 2)."""
    parts = target.split(".")
    return tuple(".".join(parts[:depth]) for depth in (1, 2) if len(parts) >= depth)


def _count_cases(repo: Path, path: str) -> int:
    tree = _parse(_read(repo / path), path)
    if tree is None:
        return 0
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and node.name.startswith("test_")
    )


def _targets(entrypoint_target: str, capability_name: str) -> bool:
    module = entrypoint_target.split(":")[0]
    return module == capability_name or module.startswith(f"{capability_name}.")


# --------------------------------------------------------------------------- #
# The probes. One per declared dimension, bound by declared name.              #
# --------------------------------------------------------------------------- #


def probe_existence(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Does the capability exist? Boundary membership plus a capability identity."""
    if not capability.artifacts:
        return ProbeResult.open(
            "no tracked artifact",
            ("artifact_count:0", f"location:{capability.location}"),
        )
    return ProbeResult.closed(
        f"{capability.artifact_count} tracked artifact(s) under {capability.location}",
        (
            f"boundary:{capability.location}",
            f"capability_identity:{capability.capability_id}",
            f"artifact_count:{capability.artifact_count}",
        ),
    )


def probe_architecture(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Is architecture defined? The package root must declare its own scope."""
    doc = facts.architecture_doc.get(capability.name, "")
    refs = facts.architecture_refs.get(capability.name, ())
    threshold = int(dimension.parameter("declaration_min_chars"))
    if len(doc.strip()) < threshold:
        return ProbeResult.open(
            f"package documentation is {len(doc.strip())} chars, "
            f"below the {threshold}-char declaration threshold",
            (f"architecture_chars:{len(doc.strip())}", f"threshold:{threshold}"),
        )
    return ProbeResult.closed(
        f"architecture declared in {len(doc.strip())} chars"
        + (f"; cites {', '.join(refs[:3])}" if refs else ""),
        (
            f"architecture_chars:{len(doc.strip())}",
            f"architecture_refs:{','.join(refs[:5]) or 'none'}",
        ),
    )


def probe_ownership(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Does exactly one canonical owner exist?"""
    duplicates = facts.owners.capability_identity_duplicates.get(capability.name, 0)
    implementation_rows = len(facts.owners.implementation.get(capability.location, ()))
    if duplicates != 1 or implementation_rows != 1:
        return ProbeResult.blocked(
            f"ownership is not singular: {duplicates} capability row(s), "
            f"{implementation_rows} implementation row(s)",
            (
                f"capability_rows:{duplicates}",
                f"implementation_rows:{implementation_rows}",
            ),
        )
    return ProbeResult.closed(
        f"single canonical owner {capability.canonical_owner}",
        (
            f"canonical_owner:{capability.canonical_owner}",
            f"knowledge_reference:{capability.knowledge_reference}",
            f"implementation_row:{capability.implementation_location}",
        ),
    )


def probe_identity(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Does every artifact carry a deterministic identity minted by the identity authority?"""
    if not capability.identified_artifacts:
        return ProbeResult.blocked(
            "no artifact of this capability appears in the identity register",
            (f"artifact_count:{capability.artifact_count}",),
        )
    if capability.unidentified_artifacts:
        return ProbeResult.open(
            f"{len(capability.unidentified_artifacts)} artifact(s) carry no universal identity: "
            + ", ".join(capability.unidentified_artifacts[:3]),
            tuple(f"unidentified:{path}" for path in capability.unidentified_artifacts[:5]),
        )
    return ProbeResult.closed(
        f"{len(capability.identified_artifacts)}/{capability.artifact_count} "
        "artifact(s) carry a universal identity",
        (
            f"identified:{len(capability.identified_artifacts)}",
            f"identity_sample:{capability.artifact_identities[0]}",
        ),
    )


def probe_registry(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Is the capability registered in every located register that should carry it?"""
    absent = [
        label
        for label, present in (
            ("capability register", capability.name in facts.owners.capability_identity),
            ("implementation catalogue", capability.location in facts.owners.implementation),
            ("coverage source", capability.location in facts.owners.coverage_source),
            ("coverage addopts", capability.name in facts.owners.coverage_addopts),
        )
        if not present
    ]
    if absent:
        return ProbeResult.open(
            "absent from " + ", ".join(absent),
            tuple(f"absent_from:{label}" for label in absent),
        )
    return ProbeResult.closed(
        "registered in the capability register, the implementation catalogue "
        "and the coverage denominator",
        (
            f"capability_register:{capability.capability_id}",
            f"coverage_source:{capability.location}",
            f"coverage_addopts:{capability.name}",
        ),
    )


def probe_dependency(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Are all dependencies resolved?"""
    unresolved = facts.unresolved_imports.get(capability.name, ())
    resolved = facts.resolved_imports.get(capability.name, 0)
    if unresolved:
        return ProbeResult.open(
            f"{len(unresolved)} unresolved first-party import target(s): "
            + ", ".join(unresolved[:3]),
            tuple(f"unresolved:{target}" for target in unresolved[:5]),
        )
    return ProbeResult.closed(
        f"{resolved} first-party import target(s) resolve to tracked modules",
        (f"resolved_imports:{resolved}", "unresolved_imports:0"),
    )


def probe_implementation(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Does executable implementation exist?

    The status vocabulary is declared, not assumed. The catalogue distinguishes states
    that mean implementation exists from states that mean it is merely planned, and
    treating ``CERTIFIED`` as weaker than ``IMPLEMENTED`` because it is a different
    string would report a certified capability as unimplemented.
    """
    if capability.implementation_status not in facts.implementation_present_states:
        return ProbeResult.open(
            f"implementation catalogue reports {capability.implementation_status}, "
            "which is not an implementation-present state",
            (f"implementation_status:{capability.implementation_status}",),
        )
    if not capability.artifacts:
        return ProbeResult.blocked(
            "catalogue reports implementation but the boundary carries no artifact",
            (f"implementation_status:{capability.implementation_status}",),
        )
    return ProbeResult.closed(
        f"{capability.implementation_status} with {capability.artifact_count} artifact(s)",
        (
            f"implementation_status:{capability.implementation_status}",
            f"implementation_location:{capability.implementation_location}",
            f"reuse_disposition:{capability.reuse_disposition}",
        ),
    )


def probe_contract(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Are interfaces and contracts defined?"""
    symbol = str(dimension.parameter("interface_symbol"))
    if not facts.interface_surface.get(capability.name, False):
        return ProbeResult.open(
            f"the package root publishes no {symbol} interface surface",
            (f"interface_surface:{capability.location}", f"interface_symbol:{symbol}"),
        )
    return ProbeResult.closed(
        f"the package root publishes an explicit {symbol} interface surface",
        (
            f"interface_surface:{capability.location}",
            f"module_count:{capability.artifact_count}",
        ),
    )


def probe_validation(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Can correctness be measured? A located suite must exercise the capability."""
    suites = facts.test_files.get(capability.name, ())
    if not suites:
        return ProbeResult.open(
            "no located suite imports this capability, so correctness is not measurable",
            ("suites:0",),
        )
    return ProbeResult.closed(
        f"{len(suites)} located suite(s) exercise this capability",
        (f"suites:{len(suites)}", f"suite_sample:{suites[0]}"),
    )


def probe_verification(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Can correctness be proven? Every identified artifact must carry a content digest."""
    digests = tuple(d for d in capability.artifact_digests if d)
    if not capability.identified_artifacts:
        return ProbeResult.blocked(
            "no identified artifact, so no digest exists to recompute a claim against",
            ("identified:0",),
        )
    if len(digests) != len(capability.identified_artifacts):
        return ProbeResult.open(
            f"{len(capability.identified_artifacts) - len(digests)} identified artifact(s) "
            "carry no content digest",
            (f"digests:{len(digests)}", f"identified:{len(capability.identified_artifacts)}"),
        )
    return ProbeResult.closed(
        f"{len(digests)} artifact digest(s) available for recomputation",
        (f"digests:{len(digests)}", f"digest_sample:{digests[0][:16]}"),
    )


def probe_testing(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Are behaviours tested?"""
    cases = facts.test_cases.get(capability.name, 0)
    if cases == 0:
        return ProbeResult.open(
            "no executable test case is attributed to this capability",
            (
                "test_cases:0",
                f"suites_attributed:{len(facts.test_files.get(capability.name, ()))}",
            ),
        )
    return ProbeResult.closed(
        f"{cases} executable test case(s) attributed by import",
        (f"test_cases:{cases}", f"suites:{len(facts.test_files.get(capability.name, ()))}"),
    )


def probe_coverage(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Are executable paths measured?

    Denominator membership is measured, not a percentage. A percentage is an observation
    of an execution rather than repository content, so a committed register carrying one
    would have no fixed point; the percentage remains an execution observation the gate
    reports and no committed byte holds.
    """
    in_source = capability.location in facts.owners.coverage_source
    in_addopts = capability.name in facts.owners.coverage_addopts
    if not (in_source and in_addopts):
        return ProbeResult.open(
            "outside the branch-coverage denominator, so executable paths are unmeasured",
            (f"coverage_source:{in_source}", f"coverage_addopts:{in_addopts}"),
        )
    return ProbeResult.closed(
        "inside the branch-coverage denominator",
        (
            f"coverage_source:{capability.location}",
            f"coverage_addopts:{capability.name}",
        ),
    )


def probe_determinism(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Does replay produce identical results?

    This measures whether a located instrument *asks* the replay question of this
    capability. Where nothing asks it, the honest state is OPEN by absence of an
    obligation — not CLOSED because no failure was observed. An unasked question has no
    passing answer.
    """
    markers = tuple(str(marker) for marker in dimension.parameter("replay_markers"))
    bound: list[str] = []
    if facts.verification_bound.get(capability.name, False):
        bound.append("verification entry point")
    workflows = facts.workflow_bindings.get(capability.name, ())
    replay_workflows = tuple(
        name for name in workflows if _asserts_replay(facts.owners.workflows[name], markers)
    )
    if replay_workflows:
        bound.append(f"gate {replay_workflows[0]}")
    if not bound:
        return ProbeResult.open(
            "no located instrument asks the replay question of this capability",
            (
                "replay_binding:none",
                f"workflows_searched:{len(workflows)}",
                f"markers_searched:{','.join(markers)}",
                f"verification_entry_point:{facts.verification_bound.get(capability.name, False)}",
            ),
        )
    return ProbeResult.closed(
        "replay asserted by " + "; ".join(bound),
        tuple(f"replay_binding:{item}" for item in bound),
    )


def _asserts_replay(workflow_text: str, markers: tuple[str, ...]) -> bool:
    """True iff a workflow carries any declared replay marker."""
    lowered = workflow_text.lower()
    return any(marker.lower() in lowered for marker in markers)


def probe_governance(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Are mutation boundaries controlled?"""
    art_src_status = tuple(
        str(facts.owners.artifact_identity[path].get("certification_status", ""))
        for path in capability.identified_artifacts
    )
    contracts = tuple(
        str(facts.owners.artifact_identity[path].get("validation_contract", ""))
        for path in capability.identified_artifacts
    )
    if capability.unidentified_artifacts:
        return ProbeResult.open(
            f"{len(capability.unidentified_artifacts)} artifact(s) are outside the "
            "object-governance boundary",
            tuple(f"ungoverned:{p}" for p in capability.unidentified_artifacts[:5]),
        )
    if not art_src_status or not all(art_src_status):
        return ProbeResult.blocked(
            "governance status is unavailable for this capability's artifacts",
            (f"identified:{len(capability.identified_artifacts)}",),
        )
    distinct = sorted(set(art_src_status))
    return ProbeResult.closed(
        f"every artifact governed ({', '.join(distinct)})",
        (
            f"governance_status:{','.join(distinct)}",
            f"validation_contract:{sorted(set(contracts))[0]}",
        ),
    )


def probe_evidence(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Is proof evidence generated?

    A producer is required. The catalogue's ``evidence_present`` flag and the artifact
    register's ``evidence_class`` are classifications of artifacts rather than producers
    of evidence; accepting either would close this dimension for every capability in the
    repository, which is how a measurement stops measuring anything.
    """
    producer_module = str(dimension.parameter("producer_module"))
    catalogue_field, artifact_field = (
        str(field) for field in dimension.parameter("reference_only_fields")
    )
    producers: list[str] = []
    if producer_module in facts.module_names.get(capability.name, frozenset()):
        producers.append(f"{capability.location}/{producer_module}.py")
    formats = facts.evidence_formats.get(capability.name, ())
    if formats:
        producers.append(f"emits {formats[0]}")
    if not producers:
        references = []
        rows = facts.owners.implementation.get(capability.location, ())
        if rows and rows[0].get(catalogue_field):
            references.append(f"catalogue {catalogue_field}")
        classes = sorted(
            {
                str(facts.owners.artifact_identity[p].get(artifact_field, ""))
                for p in capability.identified_artifacts
            }
        )
        if classes and classes[0]:
            references.append(f"artifact {artifact_field} {','.join(classes)}")
        return ProbeResult.open(
            "no evidence producer; classification-level references only: "
            + ("; ".join(references) or "none"),
            (
                f"producer_module_searched:{producer_module}",
                f"evidence_formats_found:{len(formats)}",
                *(f"reference_only:{item}" for item in references),
            ),
        )
    return ProbeResult.closed(
        "; ".join(producers),
        tuple(f"evidence_producer:{item}" for item in producers),
    )


def probe_certification(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Has closure been certified?

    An instrument that can reach a verdict is required. A capability named inside a
    certification document is a reference, not a decision procedure, and counting such
    mentions as certification is the unverified claim this programme exists to refuse.
    """
    instrument_module = str(dimension.parameter("instrument_module"))
    instruments: list[str] = []
    if instrument_module in facts.module_names.get(capability.name, frozenset()):
        instruments.append(f"{capability.location}/{instrument_module}.py")
    workflows = facts.workflow_bindings.get(capability.name, ())
    if workflows:
        instruments.append(f"gate {workflows[0]}")
    if not instruments:
        return ProbeResult.open(
            "no certification instrument names this capability",
            (
                f"instrument_module_searched:{instrument_module}",
                f"workflows_bound:{len(workflows)}",
                f"modules_present:{len(facts.module_names.get(capability.name, frozenset()))}",
            ),
        )
    return ProbeResult.closed(
        "; ".join(instruments),
        tuple(f"certification_instrument:{item}" for item in instruments),
    )


def probe_evolution(
    facts: RepositoryFacts, capability: Capability, dimension: DimensionDeclaration
) -> ProbeResult:
    """Can the capability evolve safely?

    Safety here means a change is *caught*: measured paths, regression cases, and a bound
    gate or published entrypoint. Any one alone is insufficient — tests nobody runs in the
    denominator do not catch a regression in coverage, and an entrypoint with no tests
    does not catch a regression at all.
    """
    net: list[str] = []
    if capability.location in facts.owners.coverage_source:
        net.append("coverage denominator")
    if facts.test_cases.get(capability.name, 0) > 0:
        net.append(f"{facts.test_cases[capability.name]} regression case(s)")
    binding = facts.workflow_bindings.get(capability.name, ()) or facts.entrypoints.get(
        capability.name, ()
    )
    if binding:
        net.append(f"bound to {binding[0]}")
    if len(net) < int(dimension.parameter("required_net_size")):
        return ProbeResult.open(
            "incomplete safety net: " + (", ".join(net) or "none"),
            tuple(f"safety_net:{item}" for item in net),
        )
    return ProbeResult.closed(
        "; ".join(net),
        tuple(f"safety_net:{item}" for item in net),
    )


Probe = Callable[[RepositoryFacts, Capability, DimensionDeclaration], ProbeResult]

#: Declared probe name -> implementation. The declaration names the probe; this maps the
#: name to the measurement. ``require_probe_bijection`` refuses any asymmetry.
PROBES: Mapping[str, Probe] = {
    "probe_existence": probe_existence,
    "probe_architecture": probe_architecture,
    "probe_ownership": probe_ownership,
    "probe_identity": probe_identity,
    "probe_registry": probe_registry,
    "probe_dependency": probe_dependency,
    "probe_implementation": probe_implementation,
    "probe_contract": probe_contract,
    "probe_validation": probe_validation,
    "probe_verification": probe_verification,
    "probe_testing": probe_testing,
    "probe_coverage": probe_coverage,
    "probe_determinism": probe_determinism,
    "probe_governance": probe_governance,
    "probe_evidence": probe_evidence,
    "probe_certification": probe_certification,
    "probe_evolution": probe_evolution,
}


def probe_names() -> tuple[str, ...]:
    """Every implemented probe name, for the bijection check."""
    return tuple(sorted(PROBES))


def measure_coordinate(
    facts: RepositoryFacts,
    capability: Capability,
    dimension: DimensionDeclaration,
) -> ProbeResult:
    """Measure one coordinate.

    A probe absent from ``PROBES`` yields BLOCKED rather than raising: an unimplemented
    probe is a dimension nobody can measure, which is exactly what BLOCKED means. The
    bijection check refuses that condition at load time; this is the second line of defence.
    """
    probe = PROBES.get(dimension.probe)
    if probe is None:
        return ProbeResult.blocked(
            f"declared probe {dimension.probe!r} is not implemented",
            (f"missing_probe:{dimension.probe}",),
        )
    return probe(facts, capability, dimension)


def measure(
    repo: Path,
    declaration: ClosureDeclaration,
    owners: CanonicalOwners,
    capabilities: tuple[Capability, ...],
) -> tuple[dict[str, tuple[ClosureState, str, tuple[str, ...]]], RepositoryFacts]:
    """Measure every coordinate of the matrix.

    Returns findings keyed by coordinate, plus the facts they were derived from. This
    deliberately does not build matrix cells: a cell is a projection of an observation, and
    a measurement that constructed cells directly would put closure state in two places.
    """
    declaration.require_probe_bijection(probe_names())
    facts = RepositoryFacts.measure(repo, declaration, owners, capabilities)
    findings: dict[str, tuple[ClosureState, str, tuple[str, ...]]] = {}
    for capability in capabilities:
        for dimension in declaration.dimensions:
            result = measure_coordinate(facts, capability, dimension)
            findings[f"{capability.name}:{dimension.id}"] = (
                result.state,
                result.finding,
                result.evidence,
            )
    return findings, facts


__all__ = [
    "PROBES",
    "MeasurementError",
    "Probe",
    "ProbeResult",
    "RepositoryFacts",
    "measure",
    "measure_coordinate",
    "probe_names",
    "tracked_roots",
]

"""UVI-000001 Part 04 — dependency-driven selection across five substrates.

Impact discovery is NOT re-implemented here. Layers 1 and 2 — "what changed" and "what
imports it" — are :mod:`engine.verification_impact`, which already owns the fail-closed
diff-base chain, the unbounded-path policy and the reverse import closure, and is
already measured under the coverage floor. Re-deriving either would be a second answer
to a question the repository answers.

What this module adds is the three substrates an import graph cannot see:

* **Ownership.** A change contributes every sibling under its owner, and their
  dependents. Files under one owner share state and lifecycle far more often than they
  share imports, and the owner is recorded truth rather than an inference.
* **Capability.** Every affected owner must resolve to a capability in the catalogue.
  An owner the catalogue does not know is not a small gap — it is an object whose blast
  radius nothing can bound, so it escalates.
* **Relationship.** ``depends_on`` and ``produces`` edges from the relationship graph,
  followed only where the far end resolves to a real object. The ``produces`` edge is
  the one that matters most: a change to a generated artifact reaches its producer, and
  no import edge connects those two.

Class-token endpoints (``owned_by → adr``, ``evidenced_by → VALIDATION``) are
deliberately NOT traversed. They are hubs joining thousands of unrelated objects, so
following them would make every change reach every object — a selector that always
escalates is not a selector, it is a slower way of running everything.

**Fail wide, never narrow.** Every condition the layers cannot bound widens the plan to
the whole suite under the coverage floor, and every widening names itself.
"""

from __future__ import annotations

from engine.verification_impact.changes import changed_paths
from engine.verification_impact.graph import ImpactError, load_graph
from engine.verification_impact.impact import UNBOUNDED_PREFIXES, analyse
from engine.verification_intelligence.evidence import resolve_prefix
from engine.verification_intelligence.model import (
    Selection,
    SelectionResult,
    VerificationIntelligenceError,
)
from engine.verification_intelligence.registry import (
    Substrates,
    TestObjectRegistry,
    build_test_registry,
    load_substrates,
)

#: Relationship kinds whose far end is a repository path rather than a class token.
#: Only these are traversable; see the module docstring for why the others are not.
PATH_BEARING_KINDS = ("depends_on", "produces")

#: The selector's own surfaces. A change here escalates, because a change to the thing
#: that decides what to verify cannot be verified by asking it what to verify — the
#: self-application clause of the declaration, enforced rather than stated.
SELF_PREFIXES: tuple[str, ...] = (
    "engine/verification_intelligence/",
    "engine/verification_impact/",
    "00-MASTER/UVI-000001/",
    "00-MASTER/UCOS-UGA-001/",
)


def unbounded_prefixes() -> tuple[str, ...]:
    """Every prefix whose change cannot be bounded by any graph in this repository."""
    return tuple(sorted(set(UNBOUNDED_PREFIXES) | set(SELF_PREFIXES)))


def _capability_location(substrates: Substrates, owner: str) -> str | None:
    """The catalogued location owning ``owner``, or None when the catalogue lacks one.

    An owner may be a subdirectory of a catalogued capability, so resolution is by
    longest catalogued prefix: a new subpackage under a known capability is attributed
    rather than escalating the whole suite for a gap that is not one.
    """
    if owner in substrates.capability_of_owner:
        return owner
    best: str | None = None
    for location in substrates.capability_of_owner:
        prefix = location.rstrip("/") + "/"
        if owner.startswith(prefix) and (best is None or len(location) > len(best)):
            best = location
    return best


def _test_mirror(location: str) -> str | None:
    """The catalogued test location that mirrors ``location``.

    ``engine/uckp`` → ``engine/tests/uckp``; ``engine`` → ``engine/tests``. The shape is
    the catalogue's, not this function's: both sides of every pair it returns are
    catalogued locations, and the caller discards any mirror the catalogue does not hold.
    """
    head, _, rest = location.partition("/")
    if not head or head == "tests" or rest.startswith("tests"):
        return None
    return f"{head}/tests/{rest}" if rest else f"{head}/tests"


def _provenance(substrates: Substrates) -> tuple[dict[str, set[str]], dict[str, tuple[str, ...]]]:
    """``artifact → producers`` and ``producer → artifacts``, from the registry itself.

    The registry records ``produces`` forward on each object; the reverse is what a
    change to a generated artifact needs in order to reach the engine that renders it.
    """
    produced_by: dict[str, set[str]] = {}
    produces: dict[str, tuple[str, ...]] = {}
    for path, entry in substrates.objects.items():
        rendered = tuple(str(item) for item in (entry.get("produces") or ()))
        if not rendered:
            continue
        produces[path] = rendered
        for artifact in rendered:
            produced_by.setdefault(artifact, set()).add(path)
    return produced_by, produces


def select(
    changed: tuple[str, ...] | None = None,
    *,
    substrates: Substrates | None = None,
    tests: TestObjectRegistry | None = None,
    base: str | None = None,
    root: str | None = None,
) -> SelectionResult:
    """Compute the verification a change requires, across all five substrates.

    Raises:
        VerificationIntelligenceError: a substrate is unusable. That is a FAULT, and
            every caller resolves a fault to the whole suite.
    """
    substrates = substrates or load_substrates(root)
    tests = tests or build_test_registry(substrates, root)

    try:
        graph = load_graph(root)
        changed_set = tuple(changed) if changed is not None else changed_paths(base, root)
    except ImpactError as exc:
        raise VerificationIntelligenceError(str(exc)) from exc

    whole_suite = tests.paths
    if not changed_set:
        # NO CHANGE STILL SELECTS NOTHING, and the unregistered objects are deliberately
        # NOT forced in here. This path claims nothing — it reports an empty selection
        # rather than a verified suite — so nothing is silently skipped by it, and a
        # contract that claims nothing cannot be made dishonest by omission.
        #
        # It is also unreachable for the case that motivated the fail-wide admission: a
        # newly written test file is untracked or modified, so `changed_paths` reports it
        # and the selection proceeds through the layered path below, where the
        # unregistered objects ARE unconditionally included.
        return SelectionResult(
            selection=Selection.IMPACT,
            test_paths=(),
            changed=(),
            affected_objects=(),
            affected_owners=(),
            affected_capabilities=(),
            affected_evidence=(),
            affected_certification=(),
            escalations=(),
            layers=(("IDENTITY", 0),),
        )

    # --- Layers 1 and 2: identity and dependency, owned by engine.verification_impact -
    report = analyse(graph, changed_set)
    # Only the escalations that name an unbounded path are carried. The rest are the
    # heuristic widenings the comment below explains are superseded here; dropping them
    # silently would be worse than honouring them, so they travel with the plan as
    # superseded reasons rather than disappearing.
    escalations = [
        reason
        for reason in report.escalations
        if any(reason.startswith(f"{path}:") for path in report.unbounded)
    ]
    superseded = tuple(r for r in report.escalations if r not in escalations)
    layers: list[tuple[str, int]] = [
        ("IDENTITY", len(report.changed)),
        ("DEPENDENCY", len(report.affected_objects)),
    ]

    # The impact engine's unbounded policy does not know about this engine's own
    # surfaces, so the self-application prefixes are applied here rather than widening
    # a shared constant that another consumer would inherit without asking.
    for path in changed_set:
        if path.startswith(SELF_PREFIXES) and not path.startswith(UNBOUNDED_PREFIXES):
            escalations.append(
                f"{path}: a change to the verification selector or its substrate cannot be "
                "bounded by the selector itself"
            )

    # The impact engine's own SCOPE is not read here, and the reason is worth stating.
    # ``analyse`` widens to INTEGRATION on two computed heuristics — a change reaching
    # more than three owners, and a bounded change reaching no test — because with only
    # an import graph to reason from, breadth is the best proxy it has for "state this
    # change might touch that imports do not show". This engine has that state: layer 3
    # expands every affected owner to its siblings and re-closes over them, layer 5
    # follows the produces edges an import graph cannot see, and the no-test case is
    # widened below on its own terms. So the proxy is superseded by the thing it was
    # proxying for, and honouring it as well would escalate almost every real change —
    # measured on this repository, a one-line edit to a widely imported module reaches
    # 50 owners and would run the whole suite forever.
    #
    # What is NOT superseded, and never can be, is ``unbounded``: a path no graph in
    # this repository can bound. No amount of extra substrate narrows that, so it is
    # the one condition read straight through.
    if not report.is_computable or escalations:
        return SelectionResult(
            selection=Selection.WHOLE_SUITE,
            test_paths=whole_suite,
            changed=report.changed,
            affected_objects=report.affected_objects,
            affected_owners=report.affected_owners,
            affected_capabilities=(),
            affected_evidence=report.affected_evidence,
            affected_certification=report.affected_certification,
            escalations=tuple(escalations),
            superseded=superseded,
            layers=tuple(layers),
        )

    affected: set[str] = set(report.affected_objects)

    # --- Layer 3: ownership -------------------------------------------------------
    # Ownership is the JOIN KEY between the dependency graph and the capability
    # catalogue: an object records its owner, and the catalogue records what capability
    # an owner realises. Two owner sets are computed and they are not interchangeable —
    # the owners of the CHANGED paths are the change site, and the owners of every
    # AFFECTED object are the blast radius. Capability resolution below applies to the
    # first, because the second is already covered precisely by the closure that
    # produced it, and demanding a catalogue entry for every owner a change happens to
    # reach escalates on programme-scoped owners that no capability claims.
    #
    # This layer contributes no tests of its own, and that is deliberate rather than an
    # omission. Test objects carry coarse owners — 238 files share the owner
    # ``engine/tests`` — so "select every test this owner owns" answers "all of them"
    # for any change inside a test tree. Two wider rules were tried and measured: owner
    # siblings plus re-closure selected 455 of 568 files for a one-line edit to a
    # sibling of a widely imported module, and owner-owned tests selected all 238 engine
    # tests for a one-line edit to one test. The precise version of what both were
    # reaching for is layer 4, which resolves ownership to a capability and uses the
    # catalogue's own test mirror.
    owners = {
        str(record.get("owner") or "")
        for path in affected
        if (record := substrates.record(path)) is not None
    }
    owners.discard("")
    changed_owners = {
        str(record.get("owner") or "")
        for path in report.changed
        if (record := substrates.record(path)) is not None
    }
    changed_owners.discard("")
    layers.append(("OWNERSHIP", len(owners)))

    # --- Layer 4: capability ------------------------------------------------------
    # The catalogue declares test capabilities alongside the capabilities they verify —
    # ``engine/uckp`` and ``engine/tests/uckp`` are both catalogued locations. That
    # correspondence is the catalogue's own vocabulary, so the mirror is derived from it
    # uniformly rather than mapped by hand, and a mirror the catalogue does not hold is
    # discarded rather than assumed. A capability with no catalogued test mirror
    # contributes nothing beyond the dependency closure and says so in the plan; an
    # owner the catalogue does not know AT THE CHANGE SITE escalates, because an object
    # whose capability cannot be established is an object whose blast radius cannot be.
    capabilities: set[str] = set()
    unmirrored: list[str] = []
    for owner in sorted(changed_owners):
        location = _capability_location(substrates, owner)
        if location is None:
            escalations.append(
                f"{owner}: the changed object's owner is absent from the capability "
                "catalogue, so its capability blast radius cannot be bounded"
            )
            continue
        capabilities.add(substrates.capability_of_owner[location])
        mirror = _test_mirror(location)
        if mirror is None or mirror not in substrates.capability_of_owner:
            unmirrored.append(location)
            continue
        affected |= {
            path
            for path in tests.objects
            if path == mirror or path.startswith(mirror.rstrip("/") + "/")
        }
    layers.append(("CAPABILITY", len(capabilities)))

    # --- Layer 5: relationship ----------------------------------------------------
    # Only the provenance edge, and only where the far end resolves to a real object. A
    # generated artifact and the engine that renders it are connected by nothing an
    # import graph can see, so a change to either must reach the other. The class-token
    # edges are not traversed, for the reason the module docstring gives.
    produced_by, produces = _provenance(substrates)
    provenance: set[str] = set()
    for path in list(affected) + list(report.changed):
        provenance |= produced_by.get(path, set())
        for artifact in produces.get(path, ()):  # what this object renders
            provenance |= produced_by.get(artifact, set())
    provenance = {path for path in provenance if substrates.record(path) is not None}
    affected |= provenance
    affected |= substrates.dependents_of(provenance)
    layers.append(("RELATIONSHIP", len(provenance)))

    if escalations:
        return SelectionResult(
            selection=Selection.WHOLE_SUITE,
            test_paths=whole_suite,
            changed=report.changed,
            affected_objects=tuple(sorted(affected)),
            affected_owners=tuple(sorted(owners)),
            affected_capabilities=tuple(sorted(capabilities)),
            affected_evidence=report.affected_evidence,
            affected_certification=report.affected_certification,
            escalations=tuple(escalations),
            superseded=superseded,
            layers=tuple(layers),
        )

    # AN UNREGISTERED TEST OBJECT IS ALWAYS SELECTED, AND CANNOT BE ANYTHING ELSE.
    #
    # Every layer above bounds a change through a substrate: the dependency graph, the
    # ownership records, the capability catalogue, the provenance edges. An object the
    # executable object registry has never heard of appears in NONE of them — it has no
    # universal id, no owner and no capability, because it has not been through
    # registration yet. So there is no layer that can decide it is unaffected, and the
    # only honest answer for a thing the selector cannot bound is the one this engine
    # already gives everywhere else: run it.
    #
    # Included rather than escalated, and that is a proportionality judgement worth
    # stating. Escalating the WHOLE suite because a new test file exists would make every
    # developer run a full run for the duration of anyone's unregistered work, and a gate
    # people route around is not a gate. Running the unregistered objects themselves is
    # exactly sufficient: it cannot under-verify, because the objects run.
    #
    # It is also self-limiting in the right direction. Once REG-AUTO-001 registers the
    # object, it acquires an owner and edges, the layers above can bound it, and it stops
    # being unconditionally selected. Nothing here needs to be undone.
    selected = tuple(
        sorted({path for path in affected if path in tests.objects} | set(tests.unregistered))
    )
    if not selected:
        # A bounded change that reaches no test is not "nothing to verify" — it is code
        # that nothing exercises, which is a coverage question and not a licence to skip.
        return SelectionResult(
            selection=Selection.WHOLE_SUITE,
            test_paths=whole_suite,
            changed=report.changed,
            affected_objects=tuple(sorted(affected)),
            affected_owners=tuple(sorted(owners)),
            affected_capabilities=tuple(sorted(capabilities)),
            affected_evidence=report.affected_evidence,
            affected_certification=report.affected_certification,
            escalations=("the change reaches no test object; widening rather than skipping",),
            superseded=superseded,
            layers=tuple(layers),
        )

    return SelectionResult(
        selection=Selection.IMPACT,
        test_paths=selected,
        changed=report.changed,
        affected_objects=tuple(sorted(affected)),
        affected_owners=tuple(sorted(owners)),
        affected_capabilities=tuple(sorted(capabilities)),
        affected_evidence=report.affected_evidence,
        affected_certification=report.affected_certification,
        escalations=(),
        superseded=superseded,
        layers=tuple(layers),
    )


def stages_reading(stages, substrates: Substrates, paths) -> tuple[str, ...]:
    """The ids of every declared stage whose read-set covers any of ``paths``, sorted.

    THIS IS THE RELATION THE COUPLING HID. ``reuse_inputs`` meant both "what this stage
    reads" and "what may be answered from cache", so the seven stages that must always
    run declared no inputs — and a change to the tree could not be related to them at
    all, even though what they read was perfectly well known. Separating the read-set
    restores the relation for all fifteen.

    It is a QUERY, not a scheduler. Nothing here decides what runs: ``./verify.sh``
    still executes the stages its mode admits, and stage-level impact selection is a
    later step. What this function establishes is that the question "which stages does
    this change reach" now has an answer for every stage rather than for eight of them.
    """
    reached: list[str] = []
    for stage in stages:
        covered = set()
        for prefix in stage.reads:
            covered |= set(resolve_prefix(substrates, prefix))
        if covered & set(paths):
            reached.append(stage.stage_id)
    return tuple(sorted(reached))

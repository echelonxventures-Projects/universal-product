"""UCON-000001 Part 09 — the sixteen laws, computed.

Every law here is *measured*, not argued. Several of them perform the thing they are about
rather than inspecting a description of it: UCON-L-08 fingerprints this package's own source,
registers categories nobody has ever declared, and fingerprints it again; UCON-L-09 performs all
nine declared extensions in memory; UCON-L-11 realises the entire disposition x reality
cross-product and then parses two modules to confirm neither can see the other. A law that only
read a declaration would be measuring the declaration's opinion of itself.

Three laws are ratchets in both directions, which is what stops them decaying into claims about
the past. UCON-L-13 fails on an undeclared occurrence of guarantee vocabulary *and* on a declared
preserved site whose occurrence has gone. UCON-L-15 fails on an undisclosed closure inside
governed scope *and* on a stale disclosure. UCON-L-04 fails on an operator a rule names but the
code lacks *and* on an operator the code has but no rule claims.

Nothing here writes, and nothing here reads a clock. The measurement is a pure function of the
repository's committed bytes, so two runs on one state produce identical output — which is itself
UCON-L-16, and it is measured rather than promised.

The binding between the laws and the checks below is two-way and enforced at load by
:meth:`Declaration.validate`. A law naming a check :data:`LAW_CHECKS` does not implement is
manual governance; a check :data:`LAW_CHECKS` implements that no law claims is dead code wearing
enforcement's costume. Both refuse the declaration outright, so the live path is never the
unmeasured one.
"""

from __future__ import annotations

import ast
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any

from engine.construct import audit, extension, reality, views
from engine.construct.declaration import Declaration, load_declaration, repo_root
from engine.construct.disposition import available_operators, select_rule
from engine.construct.model import (
    Construct,
    ConstructError,
    Evidence,
    Presentation,
)
from engine.construct.registry import ConstructRegistry
from engine.uckp.canonical import canonical_json, content_hash

#: The package whose source must not change when an unknown category is admitted (UCON-L-08).
PACKAGE = os.path.join("engine", "construct")

#: Verdicts. Two values, because a law either holds or it does not; a third would be a way of
#: not answering.
HOLDS = "HOLDS"
REFUSED = "REFUSED"


class ContractError(ConstructError):
    """A law could not be measured. A fault, and deliberately not a refusal."""


# --- the measurement workspace ----------------------------------------------------------------


@dataclass(slots=True)
class Probe:
    """The shared workspace the laws measure against.

    Not frozen: it is a workspace, and it caches the two expensive derivations — the closure
    inventory over 491 modules and the package source fingerprint — so sixteen laws do not
    recompute them sixteen times. Every registry a law mutates is a *fresh* one from
    :meth:`fresh_registry`, so no law can observe another law's leftovers.
    """

    declaration: Declaration
    repo: str
    _inventory: dict[str, Any] | None = field(default=None, repr=False)
    _fingerprint: Mapping[str, str] | None = field(default=None, repr=False)

    def fresh_registry(self) -> ConstructRegistry:
        """A registry seeded from the declaration, isolated from every other law's probe."""
        return ConstructRegistry(self.declaration)

    def inventory(self) -> dict[str, Any]:
        if self._inventory is None:
            self._inventory = audit.inventory(self.declaration, self.repo)
        return self._inventory

    def fingerprint(self) -> Mapping[str, str]:
        """A content digest per source file of this package. The UCON-L-08 baseline."""
        if self._fingerprint is None:
            self._fingerprint = _package_fingerprint(self.repo)
        return self._fingerprint

    def source(self, module: str) -> str:
        path = os.path.join(self.repo, PACKAGE, module)
        try:
            with open(path, encoding="utf-8") as handle:
                return handle.read()
        except OSError as exc:
            raise ContractError(f"cannot read {module!r} for measurement: {exc}") from exc


def _package_fingerprint(repo: str) -> Mapping[str, str]:
    base = os.path.join(repo, PACKAGE)
    if not os.path.isdir(base):
        raise ContractError(f"the package under measurement is absent: {base}")
    digests: dict[str, str] = {}
    for name in sorted(os.listdir(base)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(base, name), "rb") as handle:
            digests[name] = content_hash(handle.read().decode("utf-8"))
    return digests


def _imports(source: str) -> frozenset[str]:
    """Every module name imported by ``source``, however it was imported."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return frozenset(names)


def _hostile_presentations(declaration: Declaration) -> tuple[Presentation, ...]:
    """A spread of constructs chosen to be awkward rather than convenient.

    Every one of these is a shape that some earlier design in this repository refused, dropped or
    could not name: an unregistered category, a natural key with whitespace, a non-Latin key, a
    facet payload missing its required fields, a construct that is nothing but a request for an
    authority, and one that declares itself undecidable.
    """
    return (
        Presentation(kind="a-category-nobody-declared", natural_key="future-1"),
        Presentation(kind="entity", natural_key="a natural key with spaces and, punctuation!"),
        Presentation(kind="entity", natural_key="自然键-非拉丁文"),
        Presentation(kind="unknown", natural_key="malformed-unknown", payload={}),
        Presentation(kind="concept", natural_key="needs-an-authority", escalation_requested=True),
        Presentation(
            kind="concept",
            natural_key="no-procedure-decides-this",
            declared_undecidable=True,
        ),
        Presentation(
            kind="entity",
            natural_key="unattributed-thing",
            payload={"provenance": "unattributed"},
        ),
        Presentation(
            kind="entity",
            natural_key="waits-on-something-absent",
            dependencies=("UMK-ENTITY-000000000000",),
        ),
        Presentation(
            kind="entity",
            natural_key="claims-verification-it-cannot-support",
            reality_status="VERIFIED",
        ),
    )


# --- the laws -----------------------------------------------------------------------------------


def every_construct_is_disposed(probe: Probe) -> list[str]:
    """UCON-L-01 — every presented construct carries exactly one active disposition."""
    problems: list[str] = []
    registry = probe.fresh_registry()
    registry.present_all(_hostile_presentations(probe.declaration))
    for identity in registry.undisposed():
        problems.append(f"{identity} carries no single active disposition")
    for construct in registry.all():
        active = [record for record in construct.dispositions if record.active]
        if len(active) != 1:
            problems.append(f"{construct.identity} carries {len(active)} active dispositions")
        if construct.disposition.disposition not in probe.declaration.disposition_ids:
            problems.append(
                f"{construct.identity} carries undeclared disposition "
                f"{construct.disposition.disposition!r}"
            )
        if not construct.disposition.rule_id:
            problems.append(f"{construct.identity} carries a disposition naming no rule")

    # Non-vacuity: the invariant must be REFUSED when forged, or holding it proves nothing.
    sample = registry.all()[0]
    for forged, description in (
        ((), "no disposition at all"),
        (
            (sample.disposition, replace(sample.disposition, sequence=99)),
            "two active dispositions",
        ),
    ):
        try:
            Construct(
                presentation=sample.presentation,
                dispositions=forged,
                assessments=sample.assessments,
                kind_registered=True,
            )
        except ConstructError:
            continue
        problems.append(f"a construct with {description} was accepted by the model")
    return problems


def disposition_is_total(probe: Probe) -> list[str]:
    """UCON-L-02 — exactly one catch-all rule, and it is last."""
    problems: list[str] = []
    rules = probe.declaration.rules
    catch_alls = [rule for rule in rules if rule.catch_all]
    if len(catch_alls) != 1:
        problems.append(f"{len(catch_alls)} catch-all rules are declared; exactly one is required")
        return problems
    if rules[-1] is not catch_alls[0]:
        problems.append(
            f"the catch-all {catch_alls[0].rule_id!r} is not the last rule, so every rule after "
            "it is unreachable"
        )
    if catch_alls[0].when and any(clause.arguments for clause in catch_alls[0].when):
        problems.append(
            f"the catch-all {catch_alls[0].rule_id!r} carries a parameterised clause, so it is a "
            "condition rather than a catch-all"
        )
    # Totality, performed rather than argued. The probe is engineered to satisfy no SPECIFIC rule:
    # its kind is registered (so UCON-DR-04 stays quiet), it claims a reality state outside the
    # research trigger, and it offers no evidence (so the admitting rule stays quiet too). What is
    # left is the catch-all, and reaching it is the whole property under measurement.
    registry = probe.fresh_registry()
    bare = registry.present(
        Presentation(
            kind="entity",
            natural_key="UCON-L-02-matches-no-specific-rule",
            reality_status="THEORETICAL",
        )
    )
    if bare.disposition.rule_id != catch_alls[0].rule_id:
        problems.append(
            f"a construct engineered to match no specific rule selected "
            f"{bare.disposition.rule_id!r} rather than the catch-all "
            f"{catch_alls[0].rule_id!r}, so the totality probe is measuring the wrong thing"
        )
    if bare.disposition.disposition != catch_alls[0].disposition:
        problems.append(
            f"the catch-all assigned {bare.disposition.disposition!r} rather than the declared "
            f"{catch_alls[0].disposition!r}"
        )
    # And the engine itself must be total for any presentation, in any world.
    try:
        select_rule(
            probe.declaration,
            Presentation(kind="unregistered-in-this-world", natural_key="x"),
            _empty_context(probe),
        )
    except ConstructError as exc:
        problems.append(f"disposition is not total: {exc}")
    return problems


def catch_all_is_non_destructive(probe: Probe) -> list[str]:
    """UCON-L-03 — the catch-all disposition forecloses nothing.

    Two halves. The declared half compares the catch-all rule against the declared
    ``catch_all_disposition``, so editing the rule to REJECT fails here rather than silently
    changing what happens to every construct the rule set failed to anticipate. The structural
    half is one no declaration can fake: the catch-all disposition must be non-terminal and must
    reach every other declared disposition in a single step.
    """
    problems: list[str] = []
    declaration = probe.declaration
    catch_all = declaration.catch_all
    if catch_all.disposition != declaration.catch_all_disposition:
        problems.append(
            f"the catch-all rule assigns {catch_all.disposition!r} but the declaration requires "
            f"{declaration.catch_all_disposition!r}"
        )
    spec = declaration.disposition(catch_all.disposition)
    if spec.terminal:
        problems.append(
            f"the catch-all disposition {spec.identifier!r} is terminal, so a construct no rule "
            "anticipated would be permanently closed"
        )
    unreachable = sorted(
        set(declaration.disposition_ids) - {spec.identifier} - set(spec.successors)
    )
    if unreachable:
        problems.append(
            f"the catch-all disposition {spec.identifier!r} cannot reach "
            f"{', '.join(unreachable)} in one step, so falling through forecloses them"
        )
    return problems


def operators_are_two_way_bound(probe: Probe) -> list[str]:
    """UCON-L-04 — declared operators and implemented operators are the same set."""
    problems: list[str] = []
    declaration = probe.declaration
    implemented = available_operators()
    used = {clause.operator for rule in declaration.rules for clause in rule.when}
    for orphan in sorted(used - implemented):
        problems.append(f"operator {orphan!r} is named by a rule but not implemented")
    for orphan in sorted(implemented - used):
        problems.append(f"operator {orphan!r} is implemented but no rule claims it")
    for orphan in sorted(declaration.claimed_operators ^ implemented):
        problems.append(
            f"operator {orphan!r} differs between the declaration's claimed list and the "
            "implemented set"
        )
    # Non-vacuity: a rule naming an absent operator must be refused, not tolerated.
    forged = replace(
        declaration,
        rules=(
            *declaration.rules[:-1],
            replace(
                declaration.rules[-1],
                when=(
                    type(declaration.rules[-1].when[0])(operator="no_such_operator", arguments={}),
                ),
            ),
        ),
    )
    if not forged.validate(
        {law.check for law in declaration.laws}, implemented, views.available_selectors()
    ):
        problems.append("a rule naming an unimplemented operator was accepted by validate()")
    return problems


def nothing_is_silently_ignored(probe: Probe) -> list[str]:
    """UCON-L-05 — the population equals the presentations, whatever the dispositions were."""
    problems: list[str] = []
    registry = probe.fresh_registry()
    seeded = len(registry.all())
    hostile = _hostile_presentations(probe.declaration)
    returned = registry.present_all(hostile)
    if len(returned) != len(hostile):
        problems.append(
            f"{len(hostile)} constructs were presented and {len(returned)} were returned"
        )
    expected = {presentation.identity for presentation in hostile}
    for identity in sorted(expected):
        if not registry.has(identity):
            problems.append(f"{identity} was presented and is not in the registry")
    if len(registry.all()) != seeded + len(expected):
        problems.append(
            f"the population is {len(registry.all())}; {seeded + len(expected)} distinct "
            "identities were presented"
        )
    if registry.presented < len(registry.all()):
        problems.append(
            f"the registry holds {len(registry.all())} constructs having counted "
            f"{registry.presented} presentations, which is arithmetically impossible"
        )
    if not registry.chain_is_intact():
        problems.append("the admission journal chain is broken")
    # A rejected construct must still be readable, or a refusal is indistinguishable from a drop.
    sample = registry.get(hostile[0].identity)
    rejected = registry.redispose(
        sample.identity,
        disposition="REJECT",
        rule_id="UCON-L-05",
        rationale="measured: a rejection must leave a readable record",
    )
    if not registry.has(rejected.identity):
        problems.append("a rejected construct left no record")
    if "reference" not in reality.permitted_acts(probe.declaration, rejected):
        problems.append(
            "a rejected construct cannot be referenced, so its rejection is unreadable and "
            "therefore indistinguishable from never having been presented"
        )
    return problems


def unknown_and_contradiction_are_first_class(probe: Probe) -> list[str]:
    """UCON-L-06 — unknowns, contradictions, research and discovery objects are governed."""
    problems: list[str] = []
    registry = probe.fresh_registry()
    unknown = views.register_unknown(
        registry,
        natural_key="UCON-L-06-unknown",
        unknown_class=probe.declaration.unknown_classes[0],
        domain="measurement",
        formulation="an unknown registered by the law that measures unknowns",
    )
    other = registry.present(Presentation(kind="concept", natural_key="UCON-L-06-other"))
    contradiction = views.register_contradiction(
        registry,
        natural_key="UCON-L-06-contradiction",
        left=unknown.identity,
        right=other.identity,
        contradiction_class=probe.declaration.contradiction_classes[0],
        resolution_state=probe.declaration.resolution_states[0],
    )
    if unknown not in views.unknowns(registry):
        problems.append("a registered unknown is absent from the unknown registry")
    if contradiction not in views.contradictions(registry):
        problems.append("a registered contradiction is absent from the contradiction registry")
    if contradiction not in views.standing_contradictions(registry):
        problems.append("a contradiction in a contradicting state is not reported as standing")
    if unknown.identity not in registry.contradicted():
        problems.append(
            "a contradiction naming a construct does not put that construct in the contradicted set"
        )

    research = views.promote_to_research(registry, unknown.identity)
    if research not in views.research_objects(registry):
        problems.append("a promoted research object is absent from the research registry")
    if unknown.identity not in research.presentation.lineage.derived_from:
        problems.append("a research object does not name the construct it derives from")
    if views.promote_to_research(registry, unknown.identity).identity != research.identity:
        problems.append("promotion to research is not idempotent, so research objects multiply")
    # Promotion must work on ANY construct, not only on those the foundation anticipated.
    if not views.promote_to_research(registry, other.identity).identity:
        problems.append("an ordinary construct could not be promoted to a research object")

    discovery = views.register_discovery(
        registry,
        natural_key="UCON-L-06-discovery",
        opportunity="a discovery registered by the law that measures discoveries",
        priority=probe.declaration.priority_scale[0],
        impact=probe.declaration.impact_scale[0],
    )
    if discovery not in views.discovery_objects(registry):
        problems.append("a registered discovery object is absent from the discovery registry")
    for construct in (unknown, contradiction, research, discovery):
        if construct.disposition.disposition not in probe.declaration.disposition_ids:
            problems.append(f"{construct.kind} carries an undeclared disposition")
    return problems


def discovery_reaches_a_fixed_point(probe: Probe) -> list[str]:
    """UCON-L-07 — discovery run twice over one state mints nothing the second time."""
    problems: list[str] = []
    registry = probe.fresh_registry()
    views.register_unknown(
        registry,
        natural_key="UCON-L-07-unknown",
        unknown_class=probe.declaration.unknown_classes[0],
        domain="measurement",
        formulation="an unknown that discovery must notice",
    )
    registry.present(
        Presentation(kind="entity", natural_key="UCON-L-07-escalated", escalation_requested=True)
    )
    first = views.discover(registry)
    if not first:
        problems.append(
            "discovery minted nothing over a state containing an unattended unknown and an "
            "escalation, so the walk is vacuous"
        )
    after_first = registry.digest()
    second = views.discover(registry)
    if second:
        problems.append(
            f"discovery minted {len(second)} further objects over an unchanged state, so it does "
            "not converge"
        )
    if registry.digest() != after_first:
        problems.append("a second discovery pass changed the registry, so there is no fixed point")
    third = views.discover(registry)
    if third or registry.digest() != after_first:
        problems.append("discovery is not idempotent beyond the second pass")
    for construct in first:
        if not construct.presentation.lineage.derived_from:
            problems.append(
                f"{construct.identity} is a discovery object naming no subject, so the "
                "opportunity cannot be traced back to what raised it"
            )
    return problems


def future_kinds_need_no_redesign(probe: Probe) -> list[str]:
    """UCON-L-08 — admitting a category nobody declared changes no byte of this package.

    The strongest form of the openness claim available: register eleven categories chosen to be
    outside anything this repository has modelled, then compare the package's source fingerprint
    to the one taken before. A comment claiming the model is open is not evidence; an unchanged
    fingerprint across an admission is.
    """
    problems: list[str] = []
    before = dict(probe.fingerprint())
    registry = probe.fresh_registry()
    invented = (
        "acausal-inference-regime",
        "counterfactual-economy",
        "hyperdimensional-jurisdiction",
        "non-orientable-ontology",
        "observer-relative-mathematics",
        "post-symbolic-knowledge-form",
        "pre-geometric-locality",
        "retrocausal-governance",
        "self-modifying-physics",
        "trans-temporal-identity",
        "unnameable-category-zero",
    )
    for name in invented:
        extension.register_kind(
            registry,
            name,
            definition=f"a category declared by UCON-L-08 and unknown to this repository: {name}",
            declared_by="UCON-L-08",
        )
        if name not in registry.registered_kinds:
            problems.append(f"{name} was registered and is not reported as a registered kind")
        instance = registry.present(
            Presentation(
                kind=name,
                natural_key=f"instance-of-{name}",
                evidence=(Evidence(source="UCON-L-08", statement="an instance exists"),),
            )
        )
        if instance.disposition.disposition == "TRANSFORM":
            problems.append(
                f"an instance of the registered kind {name} was still told to transform, so "
                "registration did not take effect"
            )
        if not instance.kind_registered:
            problems.append(f"an instance of {name} does not report its kind as registered")
    after = _package_fingerprint(probe.repo)
    for name in sorted(set(before) | set(after)):
        if before.get(name) != after.get(name):
            problems.append(
                f"{name} changed while admitting categories it had never seen, so a future "
                "category is not admissible by registration alone"
            )
    return problems


def extension_points_are_exercisable(probe: Probe) -> list[str]:
    """UCON-L-09 — every declared extension point is performed in memory, and nothing narrows."""
    problems: list[str] = []
    registry = probe.fresh_registry()
    original = probe.declaration
    for point in original.extension_points:
        try:
            construct = extension.exercise(registry, point.point_id)
        except ConstructError as exc:
            problems.append(f"{point.point_id}: the declared admission failed: {exc}")
            continue
        if construct.disposition.disposition not in registry.declaration.disposition_ids:
            problems.append(
                f"{point.point_id}: the admitted construct carries no declared disposition"
            )
        if not construct.presentation.natural_key.startswith(original.probe_key_prefix):
            problems.append(
                f"{point.point_id}: the exercise key does not carry the declared probe prefix, so "
                "a probe is indistinguishable from a governed registration"
            )
        if construct.kind != point.kind:
            problems.append(
                f"{point.point_id}: declared kind {point.kind!r} but admitted {construct.kind!r}"
            )
    extended = registry.declaration
    for spec in original.kinds:
        if spec not in extended.kinds:
            problems.append(f"kind {spec.kind!r} was altered or dropped by an extension")
    for spec in original.dispositions:
        if spec not in extended.dispositions:
            problems.append(f"disposition {spec.identifier!r} was altered or dropped")
    for spec in original.reality_states:
        if spec not in extended.reality_states:
            problems.append(f"reality state {spec.identifier!r} was altered or dropped")
    if len(extended.dispositions) <= len(original.dispositions):
        problems.append("exercising the disposition extension point added no disposition")
    if len(extended.reality_states) <= len(original.reality_states):
        problems.append("exercising the reality-state extension point added no reality state")
    # Non-vacuity: adopting a narrowed declaration must be refused.
    narrowed = replace(original, dispositions=original.dispositions[:-1])
    try:
        probe.fresh_registry().adopt(narrowed)
    except ConstructError:
        pass
    else:
        problems.append("a declaration that dropped a disposition was adopted")
    return problems


def no_state_is_terminal(probe: Probe) -> list[str]:
    """UCON-L-10 — nothing is permanently closed, and falsification stays reachable."""
    problems: list[str] = []
    declaration = probe.declaration
    for spec in declaration.dispositions:
        if spec.terminal:
            problems.append(f"disposition {spec.identifier!r} is declared terminal")
        if not spec.successors:
            problems.append(
                f"disposition {spec.identifier!r} names no successor, so a construct reaching it "
                "is permanently closed"
            )
    for spec in declaration.reality_states:
        if not spec.successors:
            problems.append(
                f"reality state {spec.identifier!r} names no successor, so nothing that reached "
                "it could ever be revised"
            )
    reachable = reality.reachable_from(declaration, declaration.initial_reality_state)
    for identifier in declaration.reality_ids:
        if identifier not in reachable:
            problems.append(
                f"reality state {identifier!r} is unreachable from the declared initial state, so "
                "it is a state the framework declares and can never occupy"
            )
    # No verification is permanent: every state strong enough to certify must be able to fall to
    # a state that cannot. This is the executable form of "falsification is always available".
    for spec in declaration.reality_states:
        if "certify" not in spec.permits:
            continue
        onward = [declaration.reality(name) for name in spec.successors]
        if not any(target.permits < spec.permits for target in onward):
            problems.append(
                f"reality state {spec.identifier!r} permits certification and no successor "
                "permits strictly less, so a verification reached there could never be overturned"
            )
    return problems


def reality_is_independent_of_admission(probe: Probe) -> list[str]:
    """UCON-L-11 — the cross-product is representable and neither module can see the other.

    Three measurements. The structural one is the strongest: two modules that do not import each
    other cannot derive one answer from the other, whatever any future author intends.
    """
    problems: list[str] = []
    declaration = probe.declaration

    forbidden = (
        ("reality.py", "engine.construct.disposition"),
        ("disposition.py", "engine.construct.reality"),
    )
    for module, banned in forbidden:
        imported = _imports(probe.source(module))
        if any(name == banned or name.startswith(f"{banned}.") for name in imported):
            problems.append(
                f"{module} imports {banned}, so one of admission and reality can be derived from "
                "the other"
            )

    realized: set[tuple[str, str]] = set()
    # One registry, one construct per pair — rather than one registry per pair. The invariant
    # under measurement is that the two axes are independently settable, which a shared store
    # demonstrates just as well and at a fraction of the cost: sixty-four constructs in one
    # registry instead of sixty-four bootstraps of thirty-two.
    registry = probe.fresh_registry()
    for disposition in declaration.disposition_ids:
        for status in declaration.reality_ids:
            construct = registry.present(
                Presentation(
                    kind="entity",
                    natural_key=f"pair-{disposition}-{status}",
                    evidence=(Evidence(source="UCON-L-11", statement="a pair under measurement"),),
                )
            )
            try:
                if construct.disposition.disposition != disposition:
                    construct = registry.redispose(
                        construct.identity,
                        disposition=disposition,
                        rule_id="UCON-L-11",
                        rationale="measured: every pair must be representable",
                    )
                if construct.reality.status != status:
                    construct = registry.reassess(construct.identity, status)
            except ConstructError as exc:
                problems.append(f"({disposition}, {status}) is not representable: {exc}")
                continue
            if (
                construct.disposition.disposition == disposition
                and construct.reality.status == status
            ):
                realized.add((disposition, status))
            else:
                problems.append(
                    f"({disposition}, {status}) was requested and "
                    f"({construct.disposition.disposition}, {construct.reality.status}) resulted"
                )
    expected = len(declaration.disposition_ids) * len(declaration.reality_ids)
    if len(realized) != expected:
        problems.append(
            f"{len(realized)} of {expected} disposition/reality pairs are representable, so the "
            "two are coupled"
        )

    # The conjunction, which is what "admission does not imply truth" means operationally.
    registry = probe.fresh_registry()
    admitted = registry.present(
        Presentation(
            kind="entity",
            natural_key="admitted-but-hypothetical",
            evidence=(Evidence(source="UCON-L-11", statement="offered"),),
            reality_status="HYPOTHETICAL",
        )
    )
    if admitted.disposition.disposition != "ADMIT":
        admitted = registry.redispose(
            admitted.identity,
            disposition="ADMIT",
            rule_id="UCON-L-11",
            rationale="measured: admission must not confer truth",
        )
    if reality.permits(declaration, admitted, "certify"):
        problems.append(
            "an ADMITted construct in a hypothetical reality state may be certified, so admission "
            "implies truth"
        )
    if not reality.permits(declaration, admitted, "reference"):
        problems.append("an admitted construct cannot be referenced")
    verified = registry.reassess(admitted.identity, "THEORETICAL")
    verified = registry.reassess(verified.identity, "OBSERVED")
    verified = registry.reassess(
        verified.identity,
        "VERIFIED",
        evidence=(
            Evidence(source="independent-a", statement="confirmed"),
            Evidence(source="independent-b", statement="confirmed"),
        ),
    )
    if not reality.permits(declaration, verified, "certify"):
        problems.append(
            "an ADMITted construct in a verified reality state may not be certified, so the "
            "conjunction is not a conjunction but a veto"
        )
    if verified.disposition.disposition != "ADMIT":
        problems.append(
            "reassessing the evidence changed the disposition, so reality drives admission"
        )
    return problems


def verification_is_itself_verifiable(probe: Probe) -> list[str]:
    """UCON-L-12 — a verifier declares its assumptions and its limitations, or it is refused."""
    problems: list[str] = []
    registry = probe.fresh_registry()
    facet = probe.declaration.facet("verifier")
    for required in ("assumptions", "limitations"):
        if required not in facet.required_fields:
            problems.append(f"the verifier facet does not require {required!r}")

    verifier = extension.register_verifier(
        registry,
        natural_key="UCON-L-12-verifier",
        verifies="the disposition engine",
        assumptions=("the declaration is readable", "the rule order is as declared"),
        limitations=("decides nothing about whether a rule is correct",),
        declared_by="UCON-L-12",
        evidence=(Evidence(source="UCON-L-12", statement="registered under measurement"),),
    )
    if not verifier.presentation.payload.get("assumptions"):
        problems.append("a registered verifier carries no assumptions")
    if verifier.facet_violations:
        problems.append(
            f"a well-formed verifier reports facet violations: {verifier.facet_violations}"
        )

    # A verifier of the verifier: lineage must be expressible, or verification cannot be recursive.
    meta = extension.register_verifier(
        registry,
        natural_key="UCON-L-12-meta-verifier",
        verifies="UCON-L-12-verifier",
        assumptions=("the verifier under test declares its own assumptions",),
        limitations=("cannot decide whether those assumptions hold in the world",),
        declared_by="UCON-L-12",
        lineage_of=verifier.identity,
    )
    if verifier.identity not in meta.presentation.lineage.derived_from:
        problems.append(
            "a verifier cannot name the verifier it verifies, so lineage is not expressible"
        )

    for absent, kwargs in (
        ("assumptions", {"assumptions": (), "limitations": ("some limit",)}),
        ("limitations", {"assumptions": ("some assumption",), "limitations": ()}),
        ("assumptions", {"assumptions": ("   ",), "limitations": ("some limit",)}),
    ):
        try:
            extension.register_verifier(
                registry,
                natural_key=f"UCON-L-12-missing-{absent}-{len(problems)}",
                verifies="everything",
                declared_by="UCON-L-12",
                **kwargs,
            )
        except ConstructError:
            continue
        problems.append(f"a verifier declaring no {absent} was admitted")
    return problems


def no_completeness_claim_is_declared(probe: Probe) -> list[str]:
    """UCON-L-13 — this capability's source declares no unverifiable guarantee.

    A ratchet in both directions. An undeclared occurrence of the guarantee vocabulary is a
    violation, and a declared preserved site whose occurrence has gone is also a violation, so the
    list of exemptions cannot quietly become a list of things that used to be true. The phrases
    live in the declaration and never in this file, which is why the detector needs no exemption
    for itself.
    """
    problems: list[str] = []
    scan = probe.declaration.claim_scan
    phrases = tuple(str(phrase).lower() for phrase in (scan.get("phrases") or ()))
    if not phrases:
        problems.append(
            "the claim scan declares no phrases, which would make this law vacuous rather than "
            "satisfied"
        )
        return problems
    preserved = {
        (str(site.get("module")), str(site.get("phrase")).lower())
        for site in (scan.get("preserved_sites") or ())
    }
    extensions = tuple(str(item) for item in (scan.get("extensions") or (".py",)))
    located: set[tuple[str, str]] = set()
    for root in scan.get("roots") or ():
        base = os.path.join(probe.repo, str(root))
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(name for name in dirnames if not name.startswith((".", "__")))
            for filename in sorted(filenames):
                if not any(filename.endswith(item) for item in extensions):
                    continue
                relpath = os.path.relpath(os.path.join(dirpath, filename), probe.repo)
                with open(os.path.join(dirpath, filename), encoding="utf-8") as handle:
                    body = handle.read().lower()
                for phrase in phrases:
                    if phrase in body:
                        located.add((relpath, phrase))
                        if (relpath, phrase) not in preserved:
                            problems.append(
                                f"{relpath} declares the guarantee vocabulary {phrase!r} and no "
                                "preserved site admits it"
                            )
    for site in sorted(preserved - located):
        problems.append(
            f"a preserved site claims {site[1]!r} occurs in {site[0]} and it does not; the "
            "exemption is stale"
        )
    return problems


def vocabulary_is_not_duplicated(probe: Probe) -> list[str]:
    """UCON-L-14 — every reality state binds to a UCOS-CEU-001 row CEU actually carries.

    Imports the CEU seeds and checks against them rather than against a copy, which is the whole
    point: a copy would be a second authority over somebody else's vocabulary, and it would drift
    silently the first time CEU changed.
    """
    problems: list[str] = []
    try:
        from engine.ceu.catalog import SEED_POPULATIONS
    except ImportError as exc:  # pragma: no cover - a missing owner is a fault, not a verdict
        raise ContractError(f"the CEU vocabulary owner cannot be read: {exc}") from exc
    populations = {str(name): {str(row[0]) for row in rows} for name, rows in SEED_POPULATIONS}
    for spec in probe.declaration.reality_states:
        binding = spec.ceu_binding
        if binding is None:
            gap = spec.binding_gap or {}
            for required in ("gap_id", "finding", "referred_to", "remediation"):
                if not gap.get(required):
                    problems.append(
                        f"reality state {spec.identifier!r} binds to no CEU row and its gap "
                        f"discloses no {required}"
                    )
            continue
        population = str(binding.get("population") or "")
        member = str(binding.get("member") or "")
        if population not in populations:
            problems.append(
                f"reality state {spec.identifier!r} binds to CEU population {population!r}, "
                "which UCOS-CEU-001 does not declare"
            )
        elif member not in populations[population]:
            problems.append(
                f"reality state {spec.identifier!r} binds to {population}/{member}, which "
                "UCOS-CEU-001 does not carry"
            )
    # Non-duplication: this declaration must not restate a CEU population wholesale.
    ours = {identifier.lower() for identifier in probe.declaration.reality_ids}
    for name, members in sorted(populations.items()):
        if members and members <= ours:
            problems.append(
                f"the reality vocabulary contains the whole of the CEU population {name!r}, so it "
                "is a copy rather than a binding"
            )
    return problems


def closure_inventory_holds(probe: Probe) -> list[str]:
    """UCON-L-15 — no undisclosed closure inside governed scope, and the ratchet has not risen."""
    return audit.validate(probe.inventory())


def measurement_is_deterministic(probe: Probe) -> list[str]:
    """UCON-L-16 — two measurements of one repository state produce identical bytes."""
    problems: list[str] = []
    first = audit.inventory(probe.declaration, probe.repo)
    second = audit.inventory(probe.declaration, probe.repo)
    if audit.rendered(first) != audit.rendered(second):
        problems.append("two inventories of one repository state differ")
    if audit.digest(first) != audit.digest(second):
        problems.append("two inventories of one repository state carry different digests")

    left = probe.fresh_registry()
    right = probe.fresh_registry()
    hostile = _hostile_presentations(probe.declaration)
    left.present_all(hostile)
    right.present_all(hostile)
    if left.rendered() != right.rendered():
        problems.append("two registries built by identical calls render differently")
    if left.digest() != right.digest():
        problems.append("two registries built by identical calls carry different digests")

    body = audit.rendered(first)
    for marker in ("T00:", "T01:", "T02:", probe.repo):
        if marker and marker in body:
            problems.append(
                f"the inventory embeds {marker!r}, which is a clock reading or a machine path and "
                "makes the measurement unrepeatable elsewhere"
            )
    return problems


def _empty_context(probe: Probe):
    """A context with nothing registered — the world a rule sees when nothing else exists."""
    from engine.construct.disposition import Context

    return Context(registered_kinds=frozenset({probe.declaration.reflective_root}))


#: The implemented law checks, keyed by the name a declared law claims. Two-way bound to ``laws``
#: at load: nothing here may go unclaimed, and no law may name an absent check.
LAW_CHECKS: Mapping[str, Any] = {
    "catch_all_is_non_destructive": catch_all_is_non_destructive,
    "closure_inventory_holds": closure_inventory_holds,
    "discovery_reaches_a_fixed_point": discovery_reaches_a_fixed_point,
    "disposition_is_total": disposition_is_total,
    "every_construct_is_disposed": every_construct_is_disposed,
    "extension_points_are_exercisable": extension_points_are_exercisable,
    "future_kinds_need_no_redesign": future_kinds_need_no_redesign,
    "measurement_is_deterministic": measurement_is_deterministic,
    "no_completeness_claim_is_declared": no_completeness_claim_is_declared,
    "no_state_is_terminal": no_state_is_terminal,
    "nothing_is_silently_ignored": nothing_is_silently_ignored,
    "operators_are_two_way_bound": operators_are_two_way_bound,
    "reality_is_independent_of_admission": reality_is_independent_of_admission,
    "unknown_and_contradiction_are_first_class": unknown_and_contradiction_are_first_class,
    "verification_is_itself_verifiable": verification_is_itself_verifiable,
    "vocabulary_is_not_duplicated": vocabulary_is_not_duplicated,
}


def available_checks() -> frozenset[str]:
    """The check names this module implements — the set the declared laws are bound against."""
    return frozenset(LAW_CHECKS)


def load_contract(
    path: str | None = None, *, repository: str | None = None
) -> tuple[Declaration, Probe]:
    """Load the declaration, refuse it if incoherent, and return it with a fresh probe.

    Every available registry is supplied, so the live path is never the unmeasured one: a
    declaration loaded here has already been checked against the implemented checks, operators,
    selectors, admissions and closure detectors in both directions.
    """
    root = repository or repo_root()
    declaration = load_declaration(path, repository=root)
    declaration.require_valid(
        available_checks(),
        available_operators(),
        views.available_selectors(),
        extension.available_admissions(),
        audit.available_forms(),
    )
    return declaration, Probe(declaration=declaration, repo=root)


def measure(
    path: str | None = None, *, repository: str | None = None, laws: Iterable[str] | None = None
) -> dict[str, Any]:
    """Measure every declared law and return the report. Writes nothing; reads no clock."""
    declaration, probe = load_contract(path, repository=repository)
    selected = frozenset(laws) if laws else None
    rows: list[dict[str, Any]] = []
    for law in declaration.laws:
        if selected is not None and law.law_id not in selected:
            continue
        check = LAW_CHECKS[law.check]
        violations = [str(item) for item in check(probe)]
        rows.append(
            {
                "blocking": law.blocking,
                "check": law.check,
                "law_id": law.law_id,
                "statement": law.statement,
                "verdict": HOLDS if not violations else REFUSED,
                "violations": violations,
            }
        )
    refused = [row for row in rows if row["verdict"] == REFUSED]
    blocking = [row for row in refused if row["blocking"]]
    registry = probe.fresh_registry()
    return {
        "schema": "ucos-construct-foundation-report",
        "version": "1.0.0",
        "authority": declaration.authority,
        "declaration": declaration.artifact_id,
        "declaration_digest": content_hash(declaration.digest_payload()),
        "declaration_version": declaration.version,
        "laws": rows,
        "counts": {
            "blocking_refusals": len(blocking),
            "holds": len(rows) - len(refused),
            "laws": len(rows),
            "refused": len(refused),
        },
        "closure_inventory": probe.inventory()["counts"],
        "registry": registry.summary(),
        "registry_verification": registry.verify(),
        "discovery": views.discovery_report(registry),
        "status": "OPEN" if not blocking else "CLOSED",
        "closed_set": False,
        "upper_limit": None,
    }


def rendered(report: Mapping[str, Any]) -> str:
    return canonical_json(report)


def digest(report: Mapping[str, Any]) -> str:
    return content_hash(report)


__all__ = [
    "HOLDS",
    "LAW_CHECKS",
    "PACKAGE",
    "REFUSED",
    "ContractError",
    "Probe",
    "available_checks",
    "digest",
    "load_contract",
    "measure",
    "rendered",
]

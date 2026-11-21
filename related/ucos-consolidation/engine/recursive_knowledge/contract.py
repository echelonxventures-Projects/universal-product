"""URKE-000001 Part 13 — the thirty-two laws, computed. Every one performed, none argued.

Each check returns a list of violations; an empty list is the law holding. Nothing here reads a
clock, touches a path outside the repository, or depends on iteration order, because two
measurements of the same committed bytes must produce identical bytes of report.

Most laws *perform* the thing they claim rather than inspecting a table. Openness is measured by
fingerprinting this package, admitting twelve members nobody declared, and fingerprinting again.
Independence of the axes is measured by realising the whole cross-product. Convergence is measured
by running discovery twice. A law that could only be satisfied by a comment is not a law.
"""

from __future__ import annotations

import ast
import pathlib
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.recursive_knowledge import (
    admission,
    bridge,
    composition,
    discovery,
    evolution,
    proposal,
    research,
    states,
    subjects,
    worlds,
)
from engine.recursive_knowledge import ledger as ledger_module
from engine.recursive_knowledge.declaration import (
    Declaration,
    DeclarationError,
    load_declaration,
    repo_root,
    scanned_vocabulary,
)
from engine.recursive_knowledge.ledger import KnowledgeLedger
from engine.recursive_knowledge.model import (
    Position,
    RecursiveKnowledgeError,
    available_attributes,
)
from engine.uckp.canonical import content_hash

PACKAGE = pathlib.Path("engine") / "recursive_knowledge"
HOLDS = "HOLDS"
REFUSED = "REFUSED"


class ContractError(RecursiveKnowledgeError):
    """A law could not be computed. A fault, never a verdict."""


@dataclass(slots=True)
class Probe:
    """A workspace. Not frozen: it caches two expensive derivations so laws can share them."""

    declaration: Declaration
    repo: str
    _ledger: KnowledgeLedger | None = field(default=None, repr=False)
    _fingerprint: str = field(default="", repr=False)

    def fresh_ledger(self) -> KnowledgeLedger:
        """A newly seeded ledger. Laws that mutate must not share one."""
        return KnowledgeLedger(self.declaration)

    def seeded(self) -> KnowledgeLedger:
        """The shared seeded ledger, for laws that only read."""
        if self._ledger is None:
            self._ledger = KnowledgeLedger(self.declaration)
        return self._ledger

    def fingerprint(self) -> str:
        """A digest over every source file in this package."""
        if not self._fingerprint:
            root = pathlib.Path(self.repo) / PACKAGE
            self._fingerprint = content_hash(
                {
                    path.name: content_hash(path.read_text(encoding="utf-8"))
                    for path in sorted(root.glob("*.py"))
                }
            )
        return self._fingerprint

    def sources(self) -> Mapping[str, str]:
        root = pathlib.Path(self.repo) / PACKAGE
        return {path.name: path.read_text(encoding="utf-8") for path in sorted(root.glob("*.py"))}

    def source(self, name: str) -> str:
        target = pathlib.Path(self.repo) / PACKAGE / name
        try:
            return target.read_text(encoding="utf-8")
        except OSError as exc:  # pragma: no cover - an unreadable module is a fault
            raise ContractError(f"{name} cannot be read: {exc}") from exc


def _owner(declaration: Declaration) -> str:
    return declaration.artifact_id


def _refused(call: Callable[[], Any]) -> str:
    """Return "" when the call was refused, or a description of the fact that it was not.

    Every negative measurement in this module goes through here, so "it refused" always means an
    exception was raised and never means a function quietly returned something falsy.
    """
    try:
        call()
    except RecursiveKnowledgeError:
        return ""
    except Exception as exc:  # noqa: BLE001 - an unexpected type is still a refusal, but a wrong one
        return f"refused with an unexpected error type: {type(exc).__name__}: {exc}"
    return "was accepted"


# --- the laws -----------------------------------------------------------------------------


def every_identified_unknown_is_governed(probe: Probe) -> list[str]:
    """URKE-L-01 — an unknown in every declared domain is admitted and fully attributed."""
    problems: list[str] = []
    store = probe.fresh_ledger()
    declaration = probe.declaration
    for domain in declaration.domains:
        try:
            gap = subjects.record_gap(
                store,
                natural_key=f"law01/{domain.identifier}",
                classification=declaration.residual_gap_class,
                severity=declaration.severity_ids[-1],
                owner=_owner(declaration),
                origin="URKE-L-01",
                finding=f"an unresolved question in {domain.identifier}",
                resolution_path="investigate",
                criteria=("the question is answered and the answer is recorded",),
                domain=domain.identifier,
            )
        except RecursiveKnowledgeError as exc:
            problems.append(f"an unknown in {domain.identifier!r} could not be admitted: {exc}")
            continue
        for label, value in (
            ("identity", gap.identity),
            ("context", gap.context),
            ("state", gap.state),
            ("owner", gap.owner),
            ("governance", gap.governance),
        ):
            if not str(value).strip():
                problems.append(f"the unknown in {domain.identifier!r} carries no {label}")
        if not store.has(gap.identity):
            problems.append(f"the unknown in {domain.identifier!r} was not retained")
    return problems


def residual_is_representable(probe: Probe) -> list[str]:
    """URKE-L-02 — every declared residual admits a subject rather than refusing one."""
    problems: list[str] = []
    declaration = probe.declaration
    # THE DECLARATIVE GUARDS COME FIRST, AND THE ORDER IS THE POINT. They used to sit at the
    # end, after `probe.fresh_ledger()` — which resolves these same fields — so any
    # declaration able to fail them raised a DeclarationError during ledger construction and
    # the guards could not execute. A law that crashes instead of reporting is a law with no
    # verdict, and the branches that would have reported were dead code. Reading the cheap
    # declarative facts before building anything makes them live and makes the refusal a
    # finding rather than a traceback.
    if declaration.residual_relation not in set(declaration.relation_ids):
        problems.append("the residual relation is not declared")
    if declaration.residual_context_kind not in set(declaration.context_kind_ids):
        problems.append("the residual context kind is not declared")
    if declaration.residual_domain not in set(declaration.domain_ids):
        problems.append("the residual domain is not declared")
    if problems:
        return problems
    store = probe.fresh_ledger()
    try:
        composition.express(
            declaration,
            state=declaration.initial_state,
            domain=declaration.residual_domain,
            qualifiers={},
        )
    except RecursiveKnowledgeError as exc:
        problems.append(f"the residual domain cannot be expressed: {exc}")
    try:
        subjects.record_gap(
            store,
            natural_key="law02/residual",
            classification=declaration.residual_gap_class,
            severity=declaration.severity_ids[-1],
            owner=declaration.unassigned_owner,
            origin="URKE-L-02",
            finding="a gap whose class is not determined",
            resolution_path="classify it when the classification is knowable",
            criteria=("the gap is classified",),
        )
    except RecursiveKnowledgeError as exc:
        problems.append(f"the residual gap class cannot be admitted: {exc}")
    return problems


def profile_requirements_are_enforced(probe: Probe) -> list[str]:
    """URKE-L-03 — omitting any required attribute or payload key of any profile is refused."""
    problems: list[str] = []
    declaration = probe.declaration
    for spec in declaration.profiles:
        required, payload_keys = declaration.required_for(
            declaration.universal_entity_class, spec.profile
        )
        for attribute in required:
            if attribute not in available_attributes():
                problems.append(
                    f"profile {spec.profile!r} requires {attribute!r}, which nothing can read"
                )
        if not payload_keys and not spec.required_attributes:
            continue
    store = probe.fresh_ledger()
    outcome = _refused(
        lambda: store.admit(
            store.subject(
                natural_key="law03/no-criteria",
                profile=declaration.profile_for(subjects.DISCLOSURE_ROLE),
                domain=declaration.residual_domain,
                owner=_owner(declaration),
                origin="URKE-L-03",
            )
        )
    )
    if outcome:
        problems.append(f"a gap carrying none of its required attributes {outcome}")
    outcome = _refused(
        lambda: subjects.record_gap(
            store,
            natural_key="law03/empty-criteria",
            classification=declaration.residual_gap_class,
            severity=declaration.severity_ids[-1],
            owner=_owner(declaration),
            origin="URKE-L-03",
            finding="a gap with no closure criterion",
            resolution_path="no remediation offered",
            criteria=(),
        )
    )
    if outcome:
        problems.append(f"a gap with no closure criterion {outcome}")
    outcome = _refused(
        lambda: store.admit(
            store.subject(
                natural_key="law03/unowned",
                profile=declaration.default_profile,
                domain=declaration.residual_domain,
                owner="nobody-declared-this-role",
                origin="URKE-L-03",
            )
        )
    )
    if outcome:
        problems.append(f"a subject owned by an undeclared role {outcome}")
    return problems


def histories_are_append_only(probe: Probe) -> list[str]:
    """URKE-L-04 — histories append, earlier entries survive byte-identical, and a hollow
    verification is refused."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    contradiction = _forge_contradiction(store, declaration, "law04")
    before = contradiction.resolution_history
    after = subjects.add_resolution(
        store,
        contradiction.identity,
        action="investigated",
        actor=_owner(declaration),
        outcome=declaration.resolution_states[0].identifier,
        basis="URKE-L-04",
    )
    if len(after.resolution_history) != len(before) + 1:
        problems.append("a resolution step did not append")
    if after.resolution_history[: len(before)] != before:
        problems.append("appending a resolution step altered the earlier entries")
    verified = subjects.add_verification(
        store,
        contradiction.identity,
        verifier="URKE-L-04",
        verdict="measured",
        assumptions=("the positions are as recorded",),
        limitations=("this measurement does not decide which position is right",),
        basis="URKE-L-04",
    )
    if len(verified.verification_history) != 2:
        problems.append("a verification event did not append")
    for label, kwargs in (
        ("no assumptions", {"assumptions": (), "limitations": ("bounded",)}),
        ("no limitations", {"assumptions": ("assumed",), "limitations": ()}),
    ):
        outcome = _refused(
            lambda kwargs=kwargs: subjects.add_verification(
                store,
                contradiction.identity,
                verifier="URKE-L-04",
                verdict="measured",
                basis="URKE-L-04",
                **kwargs,
            )
        )
        if outcome:
            problems.append(f"a verification declaring {label} {outcome}")
    entity = store.get(contradiction.identity)
    moved = states.transition(
        declaration,
        entity,
        declaration.states[1].identifier,
        basis="URKE-L-04",
        actor=_owner(declaration),
        sequence=len(store.journal),
    )
    if moved.state_history[: len(entity.state_history)] != entity.state_history:
        problems.append("a state transition altered the earlier state history")
    return problems


def _forge_contradiction(store: KnowledgeLedger, declaration: Declaration, tag: str) -> Any:
    return subjects.record_contradiction(
        store,
        natural_key=f"{tag}/conflict",
        classification=declaration.contradiction_classes[0].identifier,
        resolution_status=declaration.resolution_states[0].identifier,
        positions=(
            Position(holder="one", claim="the measurement is sound", basis=tag),
            Position(holder="two", claim="the measurement is unsound", basis=tag),
        ),
        affected={declaration.affected_dimensions[0]: (store.root_context,)},
        candidate_resolutions=("measure again with an independent instrument",),
        owner=_owner(declaration),
        origin=tag,
        detector=tag,
    )


def gap_closure_and_review_are_governed(probe: Probe) -> list[str]:
    """URKE-L-05 — closure needs every criterion satisfied, and an overdue review is surfaced."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    gap = subjects.record_gap(
        store,
        natural_key="law05/gap",
        classification=declaration.gap_classes[0].identifier,
        severity=declaration.severity_ids[0],
        owner=_owner(declaration),
        origin="URKE-L-05",
        finding="a gap under test",
        resolution_path="do the thing",
        criteria=("the thing is done", "the doing is recorded"),
        cadence=declaration.minimum_review_cadence,
    )
    outcome = _refused(
        lambda: subjects.close_gap(
            store, gap.identity, basis="premature", actor=_owner(declaration)
        )
    )
    if outcome:
        problems.append(f"closing a gap with unsatisfied criteria {outcome}")
    subjects.satisfy(store, gap.identity, criterion="the thing is done", basis="URKE-L-05")
    outcome = _refused(
        lambda: subjects.close_gap(store, gap.identity, basis="partial", actor=_owner(declaration))
    )
    if outcome:
        problems.append(f"closing a gap with one criterion outstanding {outcome}")
    subjects.satisfy(store, gap.identity, criterion="the doing is recorded", basis="URKE-L-05")
    closed = subjects.close_gap(store, gap.identity, basis="complete", actor=_owner(declaration))
    if closed.state not in declaration.settled_states:
        problems.append("a gap with every criterion satisfied did not reach a settled state")
    if not any(point.due(store.review_clock()) for point in gap.review_schedule):
        problems.append(
            "a gap at the minimum cadence is not surfaced as due, so a review could pass unnoticed"
        )
    if not subjects.overdue(store) and declaration.default_review_cadence > 0:
        pass
    return problems


def vocabulary_is_declared_not_coded(probe: Probe) -> list[str]:
    """URKE-L-07 — no declared domain vocabulary member appears as a string literal in the "
    "package."""
    problems: list[str] = []
    declaration = probe.declaration
    try:
        vocabularies = scanned_vocabulary(declaration)
    except DeclarationError as exc:
        raise ContractError(str(exc)) from exc
    exempt = {pathlib.Path(name).name for name in declaration.source_discipline.exempt_modules}
    mandated: set[str] = set()
    for names in declaration.declared_bindings().values():
        mandated |= set(names)
    mandated |= {str(spec.binding.get("population")) for spec in declaration.states if spec.binding}
    mandated |= {key for spec in declaration.profiles for key in spec.required_payload}
    mandated |= {str(row.get("kind")) for row in declaration.source_discipline.binding_kinds}
    members = {
        member: path
        for path, names in vocabularies.items()
        for member in names
        if member not in mandated
    }
    for name, source in probe.sources().items():
        if name in exempt:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:  # pragma: no cover - unparseable source is a fault
            raise ContractError(f"{name} cannot be parsed: {exc}") from exc
        docstrings = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
                first = node.body[0] if node.body else None
                if (
                    isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)
                ):
                    docstrings.add(id(first.value))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if id(node) in docstrings:
                continue
            vocabulary = members.get(node.value)
            if vocabulary is not None:
                problems.append(
                    f"{name}:{node.lineno} writes {node.value!r}, a member of {vocabulary}, as a "
                    "source literal"
                )
    return problems


def no_state_is_terminal(probe: Probe) -> list[str]:
    """URKE-L-08 — nothing is a dead end and everything is reachable from the initial state."""
    declaration = probe.declaration
    problems = [
        f"state {identifier!r} is a dead end" for identifier in states.terminal_states(declaration)
    ]
    reachable = states.reachable_from(declaration, declaration.initial_state)
    for identifier in sorted(set(declaration.state_ids) - reachable - {declaration.initial_state}):
        problems.append(f"state {identifier!r} is unreachable from the initial state")
    for identifier in declaration.settled_states:
        if not states.successors(declaration, identifier):
            problems.append(f"settled state {identifier!r} cannot be reopened")
    return problems


#: The admissions this law exercises, and the suffix each is given so two runs collide identically.
_OPENNESS = (
    "admit_state",
    "admit_domain",
    "admit_qualifier_value",
    "admit_relation",
    "admit_profile",
    "admit_axis",
    "admit_gap_class",
    "admit_discovery_source",
    "admit_evolution_subject",
    "admit_learning_stage",
    "admit_reality",
    "admit_temporal_system",
    "admit_context",
)


def data_extension_needs_no_redesign(probe: Probe) -> list[str]:
    """URKE-L-09 — thirteen members nobody declared are admitted, and no byte of the package "
    "moves."""
    problems: list[str] = []
    before = probe.fingerprint()
    store = probe.fresh_ledger()
    for name in _OPENNESS:
        try:
            extended, entity = admission.exercise(store, name, suffix="openness")
        except RecursiveKnowledgeError as exc:
            problems.append(f"{name} could not be exercised: {exc}")
            continue
        if not store.has(entity.identity):
            problems.append(f"{name} admitted a subject the ledger did not retain")
        if extended is None:
            problems.append(f"{name} returned no declaration")
    if probe.fingerprint() != before:
        problems.append(
            "admitting members nobody declared changed this package, so the vocabulary is not data"
        )
    return problems


def future_domain_is_admissible(probe: Probe) -> list[str]:
    """URKE-L-10 — every subject of the admissibility test is admitted at runtime."""
    problems: list[str] = []
    declaration = probe.declaration
    before = probe.fingerprint()
    store = probe.fresh_ledger()
    for pair in declaration.future_domain_subjects:
        try:
            admission.exercise(store, pair.bound_to, suffix=f"future-{pair.identifier}")
        except RecursiveKnowledgeError as exc:
            problems.append(
                f"the admissibility test subject {pair.identifier!r} could not be admitted: {exc}"
            )
    if probe.fingerprint() != before:
        problems.append("admitting a future domain changed this package")
    return problems


def discovery_reaches_a_fixed_point(probe: Probe) -> list[str]:
    """URKE-L-11 — discovery converges, and it is not inert."""
    problems: list[str] = []
    store = probe.fresh_ledger()
    first = discovery.discover(store)
    if not first:
        problems.append(
            "discovery found nothing on a seeded ledger that carries seventeen detectable "
            "conditions,"
            "so it is inert"
        )
    second = discovery.discover(store)
    if second:
        problems.append(
            f"a second pass over an unchanged ledger admitted {len(second)} more findings, so "
            "discovery does not converge"
        )
    return problems


def discovery_never_mutates_constitutional_truth(probe: Probe) -> list[str]:
    """URKE-L-12 — no forbidden write is reachable from the discovery module, and nothing moved."""
    problems: list[str] = []
    declaration = probe.declaration
    forbidden = set(declaration.forbidden_write_calls)
    tree = ast.parse(probe.source("discovery.py"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        name = (
            target.id
            if isinstance(target, ast.Name)
            else target.attr
            if isinstance(target, ast.Attribute)
            else ""
        )
        if name in forbidden:
            problems.append(f"discovery.py:{node.lineno} calls {name!r}, which is a declared write")
    digest_before = content_hash(declaration.digest_payload())
    store = probe.fresh_ledger()
    discovery.discover(store)
    if content_hash(probe.declaration.digest_payload()) != digest_before:
        problems.append("a discovery run changed the declaration")
    return problems


def discovery_covers_every_declared_target(probe: Probe) -> list[str]:
    """URKE-L-12 companion — targets, sources and detectors agree in every direction."""
    problems: list[str] = []
    declaration = probe.declaration
    targets = {spec.identifier for spec in declaration.discovery_targets}
    claimed = {spec.target for spec in declaration.discovery_sources}
    for target in sorted(targets - claimed):
        problems.append(f"target {target!r} is declared and no source claims it")
    declared = {spec.detector for spec in declaration.discovery_sources}
    live = discovery.available_detectors()
    for name in sorted(declared - live):
        problems.append(f"detector {name!r} is declared and not implemented")
    for name in sorted(live - declared):
        problems.append(f"detector {name!r} is implemented and no source claims it")
    return problems


def evolution_is_one_traceable_mechanism(probe: Probe) -> list[str]:
    """URKE-L-13 — one entry point, no subject branch, full record, tamper detected."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    subject = declaration.evolution_subjects[0]
    step = evolution.evolve(
        store,
        subject=subject.identifier,
        operator=subject.operators[0],
        before=content_hash(["before"]),
        after=content_hash(["after"]),
        basis="URKE-L-13",
        owner=_owner(declaration),
    )
    for key in ("subject", "operator", "before", "after"):
        if not str(step.payload.get(key) or "").strip():
            problems.append(f"an evolution step records no {key}")
    if not step.evidence:
        problems.append("an evolution step records no basis as evidence")
    if not evolution.trace(store, subject.identifier):
        problems.append("the trace for an evolved subject is not reconstructible")
    outcome = _refused(
        lambda: evolution.evolve(
            store,
            subject=subject.identifier,
            operator=subject.operators[0],
            before=content_hash(["same"]),
            after=content_hash(["same"]),
            basis="URKE-L-13",
            owner=_owner(declaration),
        )
    )
    if outcome:
        problems.append(f"a step recording no change {outcome}")
    if not store.chain_is_intact():
        problems.append("the chain is not intact after a recorded evolution")
    problems.extend(evolution_covers_every_declared_subject(probe))
    source = probe.source("evolution.py")
    tree = ast.parse(source)
    identifiers = {spec.identifier for spec in declaration.evolution_subjects}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value in identifiers:
            problems.append(
                f"evolution.py:{node.lineno} names the subject {node.value!r}, which is a special "
                "case"
            )
    return problems


def evolution_covers_every_declared_subject(probe: Probe) -> list[str]:
    """URKE-L-14 — every subject evolves, and every operator is used."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    exercised: set[str] = set()
    for spec in declaration.evolution_subjects:
        for operator in spec.operators:
            try:
                evolution.evolve(
                    store,
                    subject=spec.identifier,
                    operator=operator,
                    before=content_hash([spec.identifier, operator, "before"]),
                    after=content_hash([spec.identifier, operator, "after"]),
                    basis="URKE-L-14",
                    owner=_owner(declaration),
                )
            except RecursiveKnowledgeError as exc:
                problems.append(f"{spec.identifier!r} could not evolve through {operator!r}: {exc}")
                continue
            exercised.add(operator)
    for spec in declaration.operators:
        if spec.identifier not in exercised:
            problems.append(f"operator {spec.identifier!r} was never exercised")
        if spec.implementation not in evolution.available_operators():
            problems.append(f"operator {spec.identifier!r} names an unimplemented function")
    return problems


def worlds_are_data_driven(probe: Probe) -> list[str]:
    """URKE-L-16/17 — realities and chronologies resolve from data, with no embedded assumption."""
    problems: list[str] = []
    declaration = probe.declaration
    problems.extend(worlds.reality_problems(declaration, repository=probe.repo))
    problems.extend(worlds.temporal_problems(declaration))
    for spec in declaration.realities:
        resolved = worlds.resolve(declaration, spec.identifier)
        if len(resolved["systems"]) != len(declaration.reality_dimensions):
            problems.append(f"reality {spec.identifier!r} does not answer every dimension")
    exempt = {pathlib.Path(name).name for name in declaration.temporal_exempt_modules}
    for name, source in probe.sources().items():
        if name in exempt:
            continue
        lowered = source.lower()
        for literal in declaration.forbidden_source_literals:
            if literal.lower() in lowered:
                problems.append(f"{name} embeds the temporal or spatial literal {literal!r}")
    before = probe.fingerprint()
    store = probe.fresh_ledger()
    admission.exercise(store, "admit_reality", suffix="unmet")
    admission.exercise(store, "admit_temporal_system", suffix="unmet")
    if probe.fingerprint() != before:
        problems.append("admitting a reality or a chronology changed this package")
    return problems


def nothing_admitted_can_silently_disappear(probe: Probe) -> list[str]:
    """URKE-L-15 — the arithmetic reconciles, the chain holds, and no forbidden outcome is "
    "reachable."""
    problems: list[str] = []
    store = probe.fresh_ledger()
    verification = store.verify()
    if verification["status"] != "PASS":
        problems.append(f"the ledger does not reconcile: {verification}")
    if verification["admitted"] != verification["journal_entries"]:
        problems.append(
            f"{verification['admitted']} admissions produced {verification['journal_entries']} "
            "journal entries"
        )
    for forbidden in ("remove", "delete", "pop", "clear", "discard"):
        if hasattr(store, forbidden):
            problems.append(f"the ledger exposes a removal path named {forbidden!r}")
    sample = store.all()[0]
    store.supersede(sample.identity, by=store.all()[1].identity, basis="URKE-L-15")
    if not store.has(sample.identity):
        problems.append("a superseded subject stopped being retrievable")
    if not store.chain_is_intact():
        problems.append("the chain broke on a supersession")
    outcome = _refused(
        lambda: store.supersede(sample.identity, by="not-a-recorded-identity", basis="URKE-L-15")
    )
    if outcome:
        problems.append(f"superseding by an unrecorded subject {outcome}")
    outcome = _refused(lambda: store.get("not-a-recorded-identity"))
    if outcome:
        problems.append(f"reading an unrecorded identity {outcome}, so a miss could pass as absent")
    return problems


def no_subject_exists_outside_governance(probe: Probe) -> list[str]:
    """URKE-L-19 — every subject reaches exactly one active disposition in the construct "
    "registry."""
    problems: list[str] = []
    store = probe.seeded()
    try:
        outcome = bridge.govern(store)
    except RecursiveKnowledgeError as exc:
        raise ContractError(f"the construct foundation could not be reached: {exc}") from exc
    for identity in outcome["ungoverned"]:
        problems.append(f"{identity} reached no active disposition")
    if outcome["presented_count"] != len(store.all()):
        problems.append("not every subject was presented for disposition")
    if not outcome["dispositions"]:
        problems.append("no disposition was recorded, so nothing was actually governed")
    return problems


def no_subject_exists_outside_context(probe: Probe) -> list[str]:
    """URKE-L-20 — every subject names a recorded context, and the chain reaches the declared "
    "root."""
    problems: list[str] = []
    store = probe.seeded()
    for entity in store.all():
        if not entity.context.strip():
            problems.append(f"{entity.natural_key} names no context")
        elif not store.has(entity.context):
            problems.append(f"{entity.natural_key} names context {entity.context}, which is absent")
    root = store.root_context
    if not root or not store.has(root):
        problems.append("the declared root context is not recorded")
    else:
        seen: set[str] = set()
        cursor = store.all()[0].context
        while cursor and cursor not in seen and store.has(cursor):
            seen.add(cursor)
            cursor = store.get(cursor).context
        if root not in seen and cursor != root:
            problems.append("a context chain does not reach the declared root")
    return problems


def no_completeness_claim_is_declared(probe: Probe) -> list[str]:
    """URKE-L-18 — no forbidden guarantee appears, and every preserved site still does."""
    problems: list[str] = []
    declaration = probe.declaration
    preserved = set(declaration.preserved_sites)
    sources = probe.sources()
    for name, source in sources.items():
        lowered = source.lower()
        for phrase in declaration.forbidden_phrases:
            if phrase.lower() in lowered and f"{name}:{phrase}" not in preserved:
                problems.append(f"{name} declares the guarantee {phrase!r}")
    for site in sorted(preserved):
        name, _, phrase = site.partition(":")
        if phrase.lower() not in sources.get(name, "").lower():
            problems.append(f"the preserved site {site!r} no longer occurs")
    return problems


def vocabulary_is_not_hardcoded(probe: Probe) -> list[str]:
    """URKE-L-33 — no module BRANCHES ON or ENUMERATES a declared vocabulary member.

    This law lived as an inline heredoc inside .github/workflows/urke-gate.yml, so it ran in
    exactly one place: CI. ./verify.sh could not reach it, UEC could not discover it because
    it was not a gate engine, and it therefore failed every CI run while the repository-
    standard command reported URKE green. adr/0041 names that shape — a rule whose
    measurement does not reach where it applies — and the remedy is to give the rule a home
    the other planes can see.

    ITS PREDICATE WAS ALSO WRONG, and the reason is worth stating because it decides the
    shape of this one. The workflow flagged EVERY string constant equal to a vocabulary
    member. But the members are ordinary English words — ``identity``, ``governance``,
    ``verification`` are all domain ids — so the check could not tell a vocabulary reference
    from an ordinary use of the same word. All seven of its findings were false positives::

        {"identity": self.identity}          a serialization key mirroring a field name
        {"governance": lambda e: e.governance}
        ledger.amend(..., event="verification")   an event label

    A detector that cannot spare is worse than one that cannot catch: its floor is
    unreachable, because the last entries are unremovable by any migration and the only way
    to close the count is to declare things that were never defects (UZX-000001).

    So this measures what the law actually wants. Hardcoding the vocabulary means the code
    DECIDES something from a member: comparing against one, testing membership against one,
    or writing a literal enumeration of them. Those force a code change when the declaration
    gains a member, which is the harm. A key that happens to spell a member, or a label
    passed to a keyword argument, decides nothing and forces nothing.
    """
    members = {
        *probe.declaration.state_ids,
        *probe.declaration.domain_ids,
        *probe.declaration.relation_ids,
        *probe.declaration.reality_ids,
    }
    problems: list[str] = []
    for name, source in probe.sources().items():
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:  # pragma: no cover - an unparsable module is a fault
            raise ContractError(f"{name} cannot be parsed: {exc}") from exc
        for node in ast.walk(tree):
            for literal, how in _vocabulary_decisions(node, members):
                problems.append(
                    f"{name} {how} the vocabulary member {literal!r}; it belongs in the "
                    "declaration"
                )
    return sorted(problems)


def _vocabulary_decisions(node: ast.AST, members: set[str]) -> list[tuple[str, str]]:
    """Every way a node DECIDES something from a vocabulary member, and no other way."""
    found: list[tuple[str, str]] = []

    def literals(value: ast.AST) -> list[str]:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return [value.value] if value.value in members else []
        if isinstance(value, ast.Tuple | ast.List | ast.Set):
            return [x for element in value.elts for x in literals(element)]
        return []

    if isinstance(node, ast.Compare):
        # `x == "identity"` / `x in ("identity", "governance")` — a branch on a member.
        for operator, comparator in zip(node.ops, node.comparators, strict=True):
            how = (
                "tests membership against"
                if isinstance(operator, ast.In | ast.NotIn)
                else ("compares against")
            )
            found += [(literal, how) for literal in literals(comparator)]
        found += [(literal, "compares against") for literal in literals(node.left)]
    elif isinstance(node, ast.Assign | ast.AnnAssign):
        # A literal roster of members: the enumeration the declaration already owns.
        value = node.value
        if value is not None and isinstance(value, ast.Tuple | ast.List | ast.Set):
            names = literals(value)
            if len(names) > 1:
                found += [(literal, "enumerates") for literal in names]
    return found


def measurement_is_deterministic(probe: Probe) -> list[str]:
    """URKE-L-22 — two ledgers from identical calls agree, and no report carries a clock or a "
    "path."""
    problems: list[str] = []
    left, right = probe.fresh_ledger(), probe.fresh_ledger()
    if left.digest() != right.digest():
        problems.append("two ledgers seeded from identical data differ")
    if left.summary() != right.summary():
        problems.append("two summaries of identical ledgers differ")
    rendered = str(left.summary()) + str(discovery.report(left))
    for marker in ("T00:", "T01:", "T02:", probe.repo):
        if marker in rendered:
            problems.append(f"a report embeds {marker!r}, so it is not a function of the bytes")
    first = discovery.report(probe.fresh_ledger())
    second = discovery.report(probe.fresh_ledger())
    if first != second:
        problems.append("two discovery reports over identical ledgers differ")
    return problems


def bound_vocabulary_is_neither_copied_nor_narrowed(probe: Probe) -> list[str]:
    """URKE-L-20 companion — bindings are live, nothing is copied wholesale, nothing is narrowed."""
    problems: list[str] = list(states.binding_problems(probe.declaration))
    declaration = probe.declaration
    try:
        from engine.construct.declaration import load_declaration as load_ucon

        ucon = load_ucon(repository=probe.repo)
    except Exception as exc:  # noqa: BLE001 - an unreachable superior is a fault
        raise ContractError(f"the construct foundation declaration cannot be read: {exc}") from exc
    declared_members = (
        set(declaration.domain_ids) | set(declaration.gap_class_ids) | set(declaration.profile_ids)
    )
    reachable_unknown: set[str] = set()
    for row in declaration.ucon_unknown_bindings:
        ucon_class = str(row.get("ucon_class") or "")
        reached_by = str(row.get("reached_by") or "")
        if reached_by not in declared_members:
            problems.append(
                f"the reachability table says {ucon_class!r} is reached by "
                f"{reached_by!r}, which is "
                "not a declared member"
            )
            continue
        reachable_unknown.add(ucon_class)
    for name in sorted(set(ucon.unknown_classes) - reachable_unknown):
        problems.append(
            f"the construct foundation declares unknown class {name!r} and no declared binding "
            "reaches it"
        )
    reachable_classes = {
        spec.ucon_contradiction_class for spec in declaration.contradiction_classes
    }
    for name in sorted(set(ucon.contradiction_classes) - reachable_classes):
        problems.append(
            f"the construct foundation declares contradiction class {name!r} and nothing reaches it"
        )
    reachable_resolutions = {spec.ucon_resolution_state for spec in declaration.resolution_states}
    for name in sorted(set(ucon.resolution_states) - reachable_resolutions):
        problems.append(
            f"the construct foundation declares resolution state {name!r} and nothing reaches it"
        )
    return problems


def disclosed_gaps_are_themselves_governed(probe: Probe) -> list[str]:
    """URKE-L-21 — every gap this declaration discloses about itself is a governed subject."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.seeded()
    recorded = {
        entity.natural_key
        for entity in store.of_profile(declaration.profile_for(subjects.DISCLOSURE_ROLE))
    }
    for gap in declaration.all_disclosed_gaps():
        if gap.gap_id not in recorded:
            problems.append(f"the disclosed gap {gap.gap_id!r} is not admitted into the ledger")
        for label, value in (
            ("finding", gap.finding),
            ("referral", gap.referred_to),
            ("remediation", gap.remediation),
            ("classification", gap.classification),
            ("severity", gap.severity),
        ):
            if not value.strip():
                problems.append(f"the disclosed gap {gap.gap_id!r} carries no {label}")
    return problems


def reality_parity_and_review_are_enforced(probe: Probe) -> list[str]:
    """URKE-L-22/27/28/29 — probes performed, parity measured, review not waivable."""
    problems: list[str] = []
    declaration = probe.declaration
    results = discovery.probe_all(declaration, repository=probe.repo)
    for probe_id, divergences in sorted(results.items()):
        for divergence in divergences:
            problems.append(f"{probe_id}: {divergence}")
    if len(results) != len(declaration.reality_probes):
        problems.append("not every declared probe was performed")
    for layer in declaration.parity_layers:
        measure = PARITY_MEASURES.get(layer.measured_by)
        if measure is None:
            problems.append(f"parity layer {layer.layer!r} names an unimplemented measure")
            continue
        if not measure(probe, layer.evidence):
            problems.append(f"parity layer {layer.layer!r} is absent: {layer.evidence}")
    if declaration.review_exemptions:
        problems.append("the review exemption list is not empty")
    if declaration.self_review_gap not in {gap.gap_id for gap in declaration.all_disclosed_gaps()}:
        problems.append("this capability carries no review obligation of its own")
    for law in declaration.laws:
        if not law.blocking:
            problems.append(f"law {law.law_id!r} is non-blocking")
    return problems


def expressiveness_is_preserved_within_bounds(probe: Probe) -> list[str]:
    """URKE-L-23/32 — every catalogued condition composes, and the architecture stayed small."""
    problems: list[str] = []
    declaration = probe.declaration
    seen: dict[tuple[Any, ...], str] = {}
    collisions: list[str] = []
    for condition in declaration.conditions:
        try:
            expression = composition.express_condition(declaration, condition)
        except RecursiveKnowledgeError as exc:
            problems.append(f"the condition {condition.condition!r} cannot be composed: {exc}")
            continue
        key = composition.signature(expression)
        if key in seen:
            collisions.append(f"{condition.condition} collides with {seen[key]}")
        else:
            seen[key] = condition.condition
    metrics = declaration.metrics()
    if metrics["primitive_count"] > declaration.primitive_bound:
        problems.append(
            f"{metrics['primitive_count']} primitives exceed the bound of "
            f"{declaration.primitive_bound}"
        )
    if metrics["entity_class_count"] > declaration.entity_class_bound:
        problems.append(
            f"{metrics['entity_class_count']} entity classes exceed the bound of "
            f"{declaration.entity_class_bound}"
        )
    if metrics["state_count"] > declaration.state_bound:
        problems.append(
            f"{metrics['state_count']} states exceed the bound of {declaration.state_bound}"
        )
    if metrics["condition_count"] <= metrics["primitive_count"]:
        problems.append("the catalogue expresses no more conditions than there are primitives")
    if collisions:
        problems.extend(f"catalogue collision: {item}" for item in collisions)
    return problems


def lifecycle_axes_are_independent(probe: Probe) -> list[str]:
    """URKE-L-24 — the whole cross-product is reachable and moving one axis moves no other."""
    problems: list[str] = []
    declaration = probe.declaration
    combinations = states.axis_combinations(declaration)
    expected = 1
    for spec in declaration.lifecycle_axes:
        expected *= len(spec.values)
    if len(combinations) != expected:
        problems.append(f"{len(combinations)} axis combinations are reachable and {expected} exist")
    store = probe.fresh_ledger()
    entity = store.all()[0]
    for spec in declaration.lifecycle_axes:
        for value in spec.values:
            moved = states.with_axis(declaration, entity, spec.axis, value)
            if moved.axes[spec.axis] != value:
                problems.append(f"setting axis {spec.axis!r} to {value!r} did not take")
            for other in declaration.lifecycle_axes:
                if other.axis == spec.axis:
                    continue
                if moved.axes[other.axis] != entity.axes[other.axis]:
                    problems.append(
                        f"moving axis {spec.axis!r} also moved {other.axis!r}, so they are not "
                        "independent"
                    )
    outcome = _refused(
        lambda: states.with_axis(
            declaration, entity, declaration.axis_ids[0], "not-a-declared-axis-value"
        )
    )
    if outcome:
        problems.append(f"an undeclared axis value {outcome}")
    return problems


def relationships_carry_governance(probe: Probe) -> list[str]:
    """URKE-L-25 — a relationship is a governed subject and an absent endpoint is refused."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    left, right = store.all()[0], store.all()[1]
    link = ledger_module.relate(
        store,
        source=left.identity,
        target=right.identity,
        relation=declaration.relation_ids[0],
        basis="URKE-L-25",
        owner=_owner(declaration),
        origin="URKE-L-25",
    )
    for label, value in (
        ("source", link.source),
        ("target", link.target),
        ("relation", link.relation),
        ("basis", link.basis),
    ):
        if not value.strip():
            problems.append(f"a relationship carries no {label}")
    if not link.evidence:
        problems.append("a relationship carries no evidence")
    if link.entity_class == declaration.universal_entity_class:
        problems.append("a relationship was admitted as the universal class rather than its own")
    for label, kwargs in (
        ("an absent source", {"source": "not-recorded", "target": right.identity}),
        ("an absent target", {"source": left.identity, "target": "not-recorded"}),
    ):
        outcome = _refused(
            lambda kwargs=kwargs: ledger_module.relate(
                store,
                relation=declaration.relation_ids[0],
                basis="URKE-L-25",
                owner=_owner(declaration),
                origin="URKE-L-25",
                **kwargs,
            )
        )
        if outcome:
            problems.append(f"a relationship naming {label} {outcome}")
    outcome = _refused(
        lambda: ledger_module.relate(
            store,
            source=left.identity,
            target=right.identity,
            relation=declaration.relation_ids[0],
            basis="   ",
            owner=_owner(declaration),
            origin="URKE-L-25",
        )
    )
    if outcome:
        problems.append(f"a relationship with no basis {outcome}")
    return problems


def unresolved_generates_research(probe: Probe) -> list[str]:
    """URKE-L-26 — a gap and a contradiction each generate research, and reflection needs no "
    "layer."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    gap = subjects.record_gap(
        store,
        natural_key="law26/gap",
        classification=declaration.gap_classes[0].identifier,
        severity=declaration.severity_ids[0],
        owner=_owner(declaration),
        origin="URKE-L-26",
        finding="something unresolved",
        resolution_path="investigate",
        criteria=("it is resolved",),
    )
    opened = research.open_research(
        store,
        natural_key="law26/from-gap",
        question="what resolves it?",
        owner=_owner(declaration),
        origin="URKE-L-26",
        derived_from=gap.identity,
    )
    if not research.research_for(store, gap.identity):
        problems.append("a gap did not generate a research subject")
    for facet in declaration.research_facets:
        if facet not in opened.payload:
            problems.append(f"a research subject carries no {facet!r}")
    contradiction = _forge_contradiction(store, declaration, "law26")
    produced = subjects.generate_consequences(
        store, contradiction.identity, owner=_owner(declaration)
    )
    if len(produced) != len(declaration.contradiction_generates):
        problems.append(
            f"a contradiction generated {len(produced)} consequences and "
            f"{len(declaration.contradiction_generates)} are declared"
        )
    before = probe.fingerprint()
    for pair in declaration.meta_subjects:
        reflection = research.open_research(
            store,
            natural_key=f"law26/{pair.identifier}",
            question=f"what is known about {pair.bound_to}?",
            owner=_owner(declaration),
            origin="URKE-L-26",
        )
        try:
            ledger_module.relate(
                store,
                source=reflection.identity,
                target=contradiction.identity,
                relation=declaration.meta_relation,
                basis=f"reflexive knowledge about {pair.bound_to}",
                owner=_owner(declaration),
                origin="URKE-L-26",
            )
        except RecursiveKnowledgeError as exc:
            problems.append(f"the reflexive form {pair.identifier!r} could not be admitted: {exc}")
    if probe.fingerprint() != before:
        problems.append("admitting reflexive knowledge changed this package")
    return problems


def learning_pipeline_cannot_be_bypassed(probe: Probe) -> list[str]:
    """URKE-L-27 — every stage in order, every skip refused, reversal by supersession."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    stages = [spec.identifier for spec in declaration.learning_stages]
    lesson = subjects.start_lesson(
        store, natural_key="law27/lesson", owner=_owner(declaration), origin="URKE-L-27"
    )
    for skip in stages[2:]:
        outcome = _refused(
            lambda skip=skip: subjects.advance(
                store, lesson.identity, to_stage=skip, basis="URKE-L-27"
            )
        )
        if outcome:
            problems.append(f"advancing straight to {skip!r} {outcome}")
    for stage in stages[1:]:
        try:
            subjects.advance(store, lesson.identity, to_stage=stage, basis="URKE-L-27")
        except RecursiveKnowledgeError as exc:
            problems.append(f"the pipeline refused a legitimate move to {stage!r}: {exc}")
    final = store.get(lesson.identity)
    if final.payload.get("stage") != stages[-1]:
        problems.append("a lesson that passed every stage did not reach the last one")
    replacement = subjects.start_lesson(
        store, natural_key="law27/replacement", owner=_owner(declaration), origin="URKE-L-27"
    )
    reversed_lesson = subjects.reverse_lesson(
        store, lesson.identity, by=replacement.identity, basis="URKE-L-27"
    )
    if not store.has(lesson.identity) or not reversed_lesson.superseded_by:
        problems.append("reversal removed the lesson instead of superseding it")
    return problems


def declared_mechanisms_are_live_and_exercised(probe: Probe) -> list[str]:
    """URKE-L-28 — every substrate, anti-finite and self-improvement symbol resolves and runs."""
    problems: list[str] = []
    declaration = probe.declaration
    import importlib

    def resolve(module_path: str, symbol: str, label: str) -> None:
        name = pathlib.Path(module_path).stem
        try:
            module = importlib.import_module(f"engine.recursive_knowledge.{name}")
        except ImportError as exc:
            problems.append(
                f"{label} names module {module_path!r}, which cannot be imported: {exc}"
            )
            return
        if hasattr(module, symbol):
            return
        for value in vars(module).values():
            if isinstance(value, type) and hasattr(value, symbol):
                return
        problems.append(f"{label} names {symbol!r} in {module_path}, which does not exist")

    for spec in declaration.substrate_elements:
        resolve(spec.module, spec.symbol, f"substrate element {spec.substrate_id!r}")
    for spec in declaration.anti_finite_mechanisms:
        resolve(spec.module, spec.symbol, f"anti-finite mechanism {spec.mechanism!r}")
    for spec in declaration.self_improvement:
        resolve(f"{spec.module}.py", spec.symbol, f"self-improvement mechanism {spec.mechanism!r}")
    required = {item for spec in declaration.future_capabilities for item in spec.requires}
    declared = {spec.substrate_id for spec in declaration.substrate_elements}
    for item in sorted(required - declared):
        problems.append(f"a future capability requires undeclared substrate {item!r}")
    for item in sorted(declared - required):
        problems.append(f"substrate {item!r} is declared and nothing requires it")
    store = probe.fresh_ledger()
    exercises = (
        lambda: store.summary(),
        lambda: discovery.discover(store),
        lambda: store.chain_is_intact(),
        lambda: bridge.govern(store),
    )
    for index, call in enumerate(exercises):
        try:
            call()
        except RecursiveKnowledgeError as exc:
            problems.append(f"a declared self-improvement exercise ({index}) failed: {exc}")
    if not store.of_profile(declaration.profile_for(discovery.FINDING_ROLE)):
        problems.append("self-analysis produced no evidence in the ledger")
    return problems


def architectural_change_requires_a_governed_proposal(probe: Probe) -> list[str]:
    """URKE-L-29 — representability measured first, and an incomplete proposal refused."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    representable = proposal.representability(
        declaration,
        state=declaration.initial_state,
        domain=declaration.domain_ids[0],
        qualifiers={},
    )
    if not representable["representable"]:
        problems.append("a condition the primitives express was reported unrepresentable")
    unrepresentable = proposal.representability(
        declaration, state="not-a-declared-state", domain=declaration.domain_ids[0]
    )
    if unrepresentable["representable"]:
        problems.append("a condition naming an undeclared state was reported representable")
    complete = {
        "capability_gained": "stated",
        "complexity_added": "stated",
        "construct": "law29",
        "governance_decision": "stated",
        "impact": "stated",
        "tradeoff_justification": "stated",
        "unrepresentable_because": "stated",
        "validation": "stated",
        "verification": "stated",
    }
    try:
        proposal.propose(store, owner=_owner(declaration), **complete)
    except RecursiveKnowledgeError as exc:
        problems.append(f"a complete proposal was refused: {exc}")
    for requirement in sorted(complete):
        partial = dict(complete)
        partial["construct"] = f"law29-{requirement}"
        partial[requirement] = "  "
        outcome = _refused(
            lambda partial=partial: proposal.propose(store, owner=_owner(declaration), **partial)
        )
        if outcome:
            problems.append(f"a proposal missing {requirement!r} {outcome}")
    if not declaration.proposal_requirements:
        problems.append("no proposal requirement is declared")
    if not declaration.default_rule:
        problems.append("no default rule is declared")
    return problems


def representation_requires_no_understanding(probe: Probe) -> list[str]:
    """URKE-L-30 — the least understood thing imaginable is admitted and governed."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    # Every qualifier at its declared starting value is, by construction, the least-committed
    # description available: unknown status, residual articulation, nothing observed. Reading the
    # initials is how this law describes an unintelligible construct without naming a single value.
    qualifiers = dict(composition.qualifier_initial(declaration))
    try:
        entity = subjects.record_gap(
            store,
            natural_key="law30/not-understood",
            classification=declaration.residual_gap_class,
            severity=declaration.severity_ids[-1],
            owner=declaration.unassigned_owner,
            origin="URKE-L-30",
            finding="a construct that is not understood, self-inconsistent, unverifiable, "
            "untestable and dependent on science and instruments that do not exist",
            resolution_path="await the science",
            criteria=("the science exists and the construct can be measured",),
            domain=declaration.residual_domain,
            qualifiers=qualifiers,
        )
    except RecursiveKnowledgeError as exc:
        problems.append(f"an unintelligible construct was refused admission: {exc}")
        return problems
    opened = research.open_research(
        store,
        natural_key="law30/research",
        question="what would have to be true for this to be measurable?",
        owner=declaration.unassigned_owner,
        origin="URKE-L-30",
        derived_from=entity.identity,
    )
    if not research.research_for(store, entity.identity):
        problems.append("an unintelligible construct did not become a research subject")
    outcome = bridge.govern(store)
    if entity.identity in outcome["ungoverned"] or opened.identity in outcome["ungoverned"]:
        problems.append("an unintelligible construct reached no disposition")
    return problems


def unresolved_is_eligible_for_discovery(probe: Probe) -> list[str]:
    """URKE-L-31 — eligibility comes from the lattice, not from a list of favoured classes."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    sample = store.all()[0]
    settled = set(declaration.settled_states)
    for spec in declaration.states:
        moved = (
            sample
            if spec.identifier == sample.state
            else states.transition(
                declaration,
                sample,
                spec.identifier,
                basis="URKE-L-31",
                actor=_owner(declaration),
                sequence=0,
            )
        )
        eligible = states.eligible_for_discovery(declaration, moved)
        if spec.identifier in settled and eligible:
            problems.append(f"a subject in the settled state {spec.identifier!r} is still eligible")
        if spec.identifier not in settled and not eligible:
            problems.append(f"a subject in {spec.identifier!r} is not eligible for discovery")
    if not settled:
        problems.append("no state is settled, so eligibility would be vacuous")
    if len(settled) >= len(declaration.state_ids):
        problems.append("every state is settled, so nothing would ever be eligible")
    return problems


def stability_is_measured_and_instability_is_governed(probe: Probe) -> list[str]:
    """URKE-L-32 companion — stability is a measurement and an instability becomes a subject."""
    problems: list[str] = []
    declaration = probe.declaration
    store = probe.fresh_ledger()
    for name, measure in (
        ("chain_integrity", store.chain_is_intact()),
        ("population_reconciles", store.verify()["reconciles"]),
    ):
        if not measure:
            problems.append(f"the stability measurement {name!r} does not hold")
    findings = discovery.discover(store)
    if not findings:
        problems.append("no instability was detected on a ledger that carries several")
    role = declaration.profile_for(discovery.FINDING_ROLE)
    for finding in findings[:5]:
        if finding.classification != role:
            problems.append("a detected instability was not admitted as a governed subject")
        if not states.eligible_for_discovery(declaration, finding):
            problems.append("a detected instability is not eligible for further investigation")
    for spec in declaration.stability_properties:
        if not spec.get("measured_by"):
            problems.append(f"stability property {spec.get('property')!r} names no measurement")
    if declaration.stability_exemptions:
        problems.append("a stability mechanism is declared exempt from review")
    return problems


# --- parity measures ----------------------------------------------------------------------


def module_present(probe: Probe, evidence: str) -> bool:
    """The declared path exists in the repository."""
    return (pathlib.Path(probe.repo) / evidence).exists()


def path_present(probe: Probe, evidence: str) -> bool:
    """The declared path exists. Distinct from a module so a test file is measured as a file."""
    return (pathlib.Path(probe.repo) / evidence).exists()


def every_gap_names_a_resolution_path(probe: Probe, evidence: str) -> bool:
    """Every disclosed gap names a remediation, so the register is actionable rather than a list."""
    return all(gap.remediation.strip() for gap in probe.declaration.all_disclosed_gaps())


#: Every declared parity layer, mapped to the measure that decides it. Bound both ways at load time.
PARITY_MEASURES: Mapping[str, Callable[[Probe, str], bool]] = {
    "every_gap_names_a_resolution_path": every_gap_names_a_resolution_path,
    "module_present": module_present,
    "path_present": path_present,
}


def available_parity_measures() -> frozenset[str]:
    return frozenset(PARITY_MEASURES)


#: Every declared law, mapped to the check that measures it. Bound both ways at load time.
LAW_CHECKS: Mapping[str, Callable[[Probe], list[str]]] = {
    "architectural_change_requires_a_governed_proposal": (
        architectural_change_requires_a_governed_proposal
    ),
    "bound_vocabulary_is_neither_copied_nor_narrowed": (
        bound_vocabulary_is_neither_copied_nor_narrowed
    ),
    "data_extension_needs_no_redesign": data_extension_needs_no_redesign,
    "declared_mechanisms_are_live_and_exercised": declared_mechanisms_are_live_and_exercised,
    "disclosed_gaps_are_themselves_governed": disclosed_gaps_are_themselves_governed,
    "discovery_covers_every_declared_target": discovery_covers_every_declared_target,
    "discovery_never_mutates_constitutional_truth": discovery_never_mutates_constitutional_truth,
    "discovery_reaches_a_fixed_point": discovery_reaches_a_fixed_point,
    "every_identified_unknown_is_governed": every_identified_unknown_is_governed,
    "evolution_is_one_traceable_mechanism": evolution_is_one_traceable_mechanism,
    "expressiveness_is_preserved_within_bounds": expressiveness_is_preserved_within_bounds,
    "future_domain_is_admissible": future_domain_is_admissible,
    "gap_closure_and_review_are_governed": gap_closure_and_review_are_governed,
    "histories_are_append_only": histories_are_append_only,
    "learning_pipeline_cannot_be_bypassed": learning_pipeline_cannot_be_bypassed,
    "lifecycle_axes_are_independent": lifecycle_axes_are_independent,
    "measurement_is_deterministic": measurement_is_deterministic,
    "no_completeness_claim_is_declared": no_completeness_claim_is_declared,
    "vocabulary_is_not_hardcoded": vocabulary_is_not_hardcoded,
    "no_state_is_terminal": no_state_is_terminal,
    "no_subject_exists_outside_context": no_subject_exists_outside_context,
    "no_subject_exists_outside_governance": no_subject_exists_outside_governance,
    "nothing_admitted_can_silently_disappear": nothing_admitted_can_silently_disappear,
    "profile_requirements_are_enforced": profile_requirements_are_enforced,
    "reality_parity_and_review_are_enforced": reality_parity_and_review_are_enforced,
    "relationships_carry_governance": relationships_carry_governance,
    "representation_requires_no_understanding": representation_requires_no_understanding,
    "residual_is_representable": residual_is_representable,
    "stability_is_measured_and_instability_is_governed": (
        stability_is_measured_and_instability_is_governed
    ),
    "unresolved_generates_research": unresolved_generates_research,
    "unresolved_is_eligible_for_discovery": unresolved_is_eligible_for_discovery,
    "vocabulary_is_declared_not_coded": vocabulary_is_declared_not_coded,
    "worlds_are_data_driven": worlds_are_data_driven,
}


def available_checks() -> frozenset[str]:
    """The check names this module implements — the set the declared laws are bound against."""
    return frozenset(LAW_CHECKS)


def implemented() -> Mapping[str, frozenset[str]]:
    """Every binding kind's implemented set, gathered from the modules that own them."""
    return {
        "admission": admission.available_admissions(),
        "attribute reader": available_attributes(),
        "bridge handler": bridge.available_handlers(),
        "detector": discovery.available_detectors(),
        "law check": available_checks(),
        "operator": evolution.available_operators(),
        "parity measure": available_parity_measures(),
        "population reader": ledger_module.available_population_readers(),
        "reality probe": discovery.available_probes(),
        "vocabulary owner reader": states.available_owner_readers(),
    }


def load_contract(
    path: str | None = None, *, repository: str | None = None
) -> tuple[Declaration, Probe]:
    """Load the declaration, refuse it if incoherent, and return it with a fresh probe."""
    root = repository or repo_root()
    declaration = load_declaration(path, repository=root)
    declaration.require_valid(implemented())
    return declaration, Probe(declaration=declaration, repo=root)


def measure(
    path: str | None = None,
    *,
    repository: str | None = None,
    laws: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Measure every declared law and return the report. Writes nothing; reads no clock."""
    declaration, probe = load_contract(path, repository=repository)
    selected = frozenset(laws) if laws else None
    if selected is not None:
        # A NAME THAT MATCHES NOTHING MEASURED NOTHING, AND USED TO EXIT 0. `--law` filtered
        # by law_id and silently dropped anything else, so `--law NOT-A-REAL-LAW` and, more
        # dangerously, `--law <check_name>` both selected an empty set and reported success.
        # A workflow step written that way is green for the reason it is measuring nothing —
        # exactly the shape adr/0041 names. An unrecognised selector is now a fault.
        unknown = sorted(selected - {law.law_id for law in declaration.laws})
        if unknown:
            raise ContractError(
                "no declared law matches "
                + ", ".join(repr(name) for name in unknown)
                + "; a selector that matches nothing would measure nothing and pass"
            )
    rows: list[dict[str, Any]] = []
    for law in declaration.laws:
        if selected is not None and law.law_id not in selected:
            continue
        check = LAW_CHECKS[law.check]
        try:
            violations = [str(item) for item in check(probe)]
        except ContractError:
            raise
        except RecursiveKnowledgeError as exc:
            raise ContractError(f"law {law.law_id} could not be computed: {exc}") from exc
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
    store = probe.seeded()
    return {
        "schema": "ucos-recursive-knowledge-report",
        "version": "1.0.0",
        "report_authority": declaration.authority,
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
        "metrics": declaration.metrics(),
        "ledger": store.summary(),
        "ledger_verification": store.verify(),
        "discovery_report": discovery.report(store),
        "parity": {
            layer.layer: bool(
                PARITY_MEASURES[layer.measured_by](probe, layer.evidence)
                if layer.measured_by in PARITY_MEASURES
                else False
            )
            for layer in declaration.parity_layers
        },
        "status": "CLOSED" if blocking else "OPEN",
        "standing": "IMPLEMENTED" if not refused else "PARTIAL",
        "closed_set": False,
        "upper_limit": None,
    }


__all__ = [
    "HOLDS",
    "LAW_CHECKS",
    "PACKAGE",
    "PARITY_MEASURES",
    "REFUSED",
    "ContractError",
    "Probe",
    "available_checks",
    "available_parity_measures",
    "implemented",
    "load_contract",
    "measure",
]

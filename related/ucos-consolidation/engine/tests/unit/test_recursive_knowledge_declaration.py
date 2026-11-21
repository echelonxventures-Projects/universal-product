"""URKE-000001 Part 16 — ``Declaration.validate``, arm by arm.

WHY A TABLE AND NOT EIGHTY HAND-WRITTEN TESTS.

``validate`` is one method with eighty-odd refusal arms and no early return: it collects every
incoherence it can find and reports them together. That shape is deliberate — an author fixing a
declaration wants the whole list, not the first line of it — and it means the only way to prove an
arm exists is to forge the one incoherence that reaches it. Eighty prose tests would say the same
sentence eighty times; the table says it once and names each forgery.

WHAT IS REAL AND WHAT IS FORGED.

The declaration is REAL, loaded once from ``urke-declaration.json``. The implemented binding sets
are REAL, from ``contract.implemented()``. Each case deep-replaces ONE field of that real
declaration — one row of one vocabulary, one bound, one token — and asserts the problem that
mutation ADDS. Attribution is by difference: ``_added`` subtracts the healthy declaration's problems
from the broken one's, so a case can only pass on a problem its own forgery caused.

That is why no case asserts a problem count. A forged incoherence often has consequences — emptying
the lifecycle axes also orphans every condition that names one — and a count would be asserting the
blast radius rather than the arm.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import pytest

from engine.recursive_knowledge import contract
from engine.recursive_knowledge import declaration as declaration_module
from engine.recursive_knowledge.declaration import (
    Declaration,
    DeclarationError,
    OperatorSpec,
    SubstrateElement,
    load_declaration,
    parse,
)
from engine.tests import assert_every_reason_arm_is_reachable, reason_arms

Mutation = Callable[[Declaration], Declaration]


@pytest.fixture(scope="module")
def declaration() -> Declaration:
    return load_declaration()


@pytest.fixture(scope="module")
def live() -> Mapping[str, frozenset[str]]:
    """The implemented binding sets, measured from the live package."""
    return contract.implemented()


@pytest.fixture(scope="module")
def healthy(declaration: Declaration, live: Mapping[str, frozenset[str]]) -> tuple[str, ...]:
    return tuple(declaration.validate(live))


def _added(
    broken: Declaration, live: Mapping[str, frozenset[str]], healthy: tuple[str, ...]
) -> list[str]:
    """The problems this forgery introduced, and none that the real declaration already reports."""
    return [problem for problem in broken.validate(live) if problem not in healthy]


def _swap(rows: tuple[Any, ...], index: int, **changes: Any) -> tuple[Any, ...]:
    """The row tuple with ONE row replaced. Every forgery below is one field of one row."""
    return rows[:index] + (dataclasses.replace(rows[index], **changes),) + rows[index + 1 :]


def _every(rows: tuple[Any, ...], **changes: Any) -> tuple[Any, ...]:
    """Every row replaced — for the arms that refuse the absence of a property
    across a whole set."""
    return tuple(dataclasses.replace(row, **changes) for row in rows)


def _case(name: str, mutate: Mutation, *fragments: str) -> Any:
    return pytest.param(mutate, fragments, id=name)


R = dataclasses.replace

# --------------------------------------------------------------------------- the lifecycle

STATES = [
    _case("no-state-at-all", lambda d: R(d, states=()), "no state is declared"),
    _case(
        "an-initial-state-nothing-declares",
        lambda d: R(d, initial_state="URKE-STATE-NOWHERE"),
        "the initial state 'URKE-STATE-NOWHERE' is not declared",
    ),
    _case(
        "a-state-that-declares-itself-the-end",
        lambda d: R(d, states=_swap(d.states, 0, successors=())),
        "declares no successor",
    ),
    _case(
        "a-successor-nothing-declares",
        lambda d: R(d, states=_swap(d.states, 0, successors=("URKE-STATE-NOWHERE",))),
        "names undeclared successor 'URKE-STATE-NOWHERE'",
    ),
    _case(
        "a-state-class-nothing-declares",
        lambda d: R(d, states=_swap(d.states, 0, state_class="NOTHING")),
        "names undeclared state class 'NOTHING'",
    ),
    _case(
        "a-state-bound-to-nothing-that-discloses-no-gap",
        lambda d: R(d, states=_swap(d.states, 0, binding=None, binding_gap=None)),
        "binds to no vocabulary owner and discloses no gap",
    ),
    _case(
        "a-state-bound-to-an-owner-nothing-declares",
        lambda d: R(d, states=_swap(d.states, 0, binding={"owner": "NOBODY"})),
        "binds to undeclared owner 'NOBODY'",
    ),
    _case(
        "a-state-nothing-can-reach",
        lambda d: R(d, states=_every(d.states, successors=(d.initial_state,))),
        "is unreachable from the initial state, so nothing can ever be moved into it",
    ),
    _case(
        "a-settled-state-nothing-declares",
        lambda d: R(d, settled_states=("URKE-STATE-NOWHERE",)),
        "the settled list names undeclared state 'URKE-STATE-NOWHERE'",
    ),
    _case(
        "every-state-settled",
        lambda d: R(d, settled_states=d.state_ids),
        "every state is declared settled, so nothing would ever be discovered",
    ),
    _case(
        "no-state-settled",
        lambda d: R(d, settled_states=()),
        "no state is declared settled, so nothing could ever come to rest",
    ),
]

# --------------------------------------------------------------------------- the composition

COMPOSITION = [
    _case("no-axis-at-all", lambda d: R(d, lifecycle_axes=()), "no lifecycle axis is declared"),
    _case(
        "an-axis-that-cannot-vary",
        lambda d: R(
            d, lifecycle_axes=_swap(d.lifecycle_axes, 0, values=(d.lifecycle_axes[0].initial,))
        ),
        "declares fewer than two values, so it cannot vary and records nothing",
    ),
    _case(
        "an-axis-starting-outside-its-own-values",
        lambda d: R(d, lifecycle_axes=_swap(d.lifecycle_axes, 0, initial="NOTHING")),
        "starts at 'NOTHING', which is not one of its values",
    ),
    _case(
        "a-qualifier-starting-outside-its-own-values",
        lambda d: R(d, qualifiers=_swap(d.qualifiers, 0, initial="NOTHING")),
        "starts at 'NOTHING', which is not one of",
    ),
    _case(
        "no-residual-domain",
        lambda d: R(d, residual_domain="NOTHING"),
        "the residual domain is not declared, so an unclassifiable subject has nowhere to rest",
    ),
    _case(
        "no-residual-relation",
        lambda d: R(d, residual_relation="NOTHING"),
        "the residual relation is not declared",
    ),
    _case(
        "no-default-profile",
        lambda d: R(d, default_profile="NOTHING"),
        "the default profile is not declared",
    ),
    _case(
        "a-role-naming-a-profile-nothing-declares",
        lambda d: R(d, profile_roles={"investigation": "NOTHING"}),
        "profile role 'investigation' names undeclared profile 'NOTHING'",
    ),
    _case(
        "no-profile-role-at-all",
        lambda d: R(d, profile_roles={}),
        "no profile role is declared, so no module could address a profile without hardcoding",
    ),
    _case(
        "no-universal-entity-class",
        lambda d: R(d, universal_entity_class="NOTHING"),
        "the universal entity class is not declared",
    ),
    _case(
        "no-residual-context-kind",
        lambda d: R(d, residual_context_kind="NOTHING"),
        "the residual context kind is not declared",
    ),
    _case(
        "an-empty-condition-catalogue",
        lambda d: R(d, conditions=()),
        "the condition catalogue is empty, so the claim that collapsing the taxonomy cost no "
        "expressive power would be untested",
    ),
    _case(
        "a-condition-in-a-state-nothing-declares",
        lambda d: R(d, conditions=_swap(d.conditions, 0, state="NOTHING")),
        "names undeclared state 'NOTHING'",
    ),
    _case(
        "a-condition-in-a-domain-nothing-declares",
        lambda d: R(d, conditions=_swap(d.conditions, 0, domain="NOTHING")),
        "names undeclared domain 'NOTHING'",
    ),
    _case(
        "a-condition-on-an-axis-nothing-declares",
        lambda d: R(d, conditions=_swap(d.conditions, 0, axes={"NOTHING": "x"})),
        "names undeclared axis 'NOTHING'",
    ),
    _case(
        "a-condition-setting-an-axis-to-a-value-nothing-declares",
        lambda d: R(
            d, conditions=_swap(d.conditions, 0, axes={d.lifecycle_axes[0].axis: "NOTHING"})
        ),
        "to undeclared value 'NOTHING'",
    ),
    _case(
        "a-condition-on-a-qualifier-nothing-declares",
        lambda d: R(d, conditions=_swap(d.conditions, 0, qualifiers={"NOTHING": "x"})),
        "names undeclared qualifier 'NOTHING'",
    ),
    _case(
        "a-condition-setting-a-qualifier-to-a-value-nothing-declares",
        lambda d: R(
            d,
            conditions=_swap(d.conditions, 0, qualifiers={d.qualifiers[0].qualifier: "NOTHING"}),
        ),
        "to undeclared value 'NOTHING'",
    ),
    _case(
        "a-profile-requiring-an-attribute-with-no-name",
        lambda d: R(d, profiles=_swap(d.profiles, 0, required_attributes=("  ",))),
        "requires an unnamed attribute",
    ),
]

# --------------------------------------------------------------------------- discovery

DISCOVERY = [
    _case(
        "a-discovery-target-no-source-claims",
        lambda d: R(d, discovery_sources=()),
        "is declared and no source claims it, so nothing would ever find one",
    ),
    _case(
        "a-source-claiming-a-target-nothing-declares",
        lambda d: R(d, discovery_sources=_swap(d.discovery_sources, 0, target="NOTHING")),
        "a discovery source claims undeclared target 'NOTHING'",
    ),
    _case(
        "a-source-off-the-priority-scale",
        lambda d: R(d, discovery_sources=_swap(d.discovery_sources, 0, priority="NOTHING")),
        "declares off-scale priority 'NOTHING'",
    ),
    _case(
        "a-source-off-the-impact-scale",
        lambda d: R(d, discovery_sources=_swap(d.discovery_sources, 0, impact="NOTHING")),
        "declares off-scale impact 'NOTHING'",
    ),
    _case(
        "no-forbidden-write-call",
        lambda d: R(d, forbidden_write_calls=()),
        "no forbidden write call is declared, so the discovery write-scope law would "
        "measure nothing",
    ),
]

# --------------------------------------------------------------------------- evolution

EVOLUTION = [
    _case(
        "a-subject-with-no-operator",
        lambda d: R(d, evolution_subjects=_swap(d.evolution_subjects, 0, operators=())),
        "declares no operator",
    ),
    _case(
        "a-subject-naming-an-operator-nothing-declares",
        lambda d: R(d, evolution_subjects=_swap(d.evolution_subjects, 0, operators=("NOTHING",))),
        "names undeclared operator 'NOTHING'",
    ),
    _case(
        "an-operator-no-subject-uses",
        lambda d: R(
            d,
            operators=d.operators
            + (OperatorSpec(identifier="NOTHING", definition="d", implementation="m.s"),),
        ),
        "operator 'NOTHING' is declared and no subject uses it",
    ),
    _case(
        "an-extension-point-naming-a-subject-nothing-declares",
        lambda d: R(d, extension_points=_swap(d.extension_points, 0, evolution_subject="NOTHING")),
        "names undeclared evolution subject 'NOTHING'",
    ),
    _case(
        "a-learning-reversal-nothing-implements",
        lambda d: R(d, learning_reversal_operator="NOTHING"),
        "learning reversal names undeclared operator 'NOTHING'",
    ),
    _case(
        "a-learning-pipeline-that-cannot-progress",
        lambda d: R(d, learning_stages=d.learning_stages[:1]),
        "the learning pipeline declares fewer than two stages",
    ),
    _case(
        "meta-knowledge-on-a-relation-nothing-declares",
        lambda d: R(d, meta_relation="NOTHING"),
        "meta-knowledge names undeclared relation 'NOTHING'",
    ),
    _case(
        "no-reflexive-subject",
        lambda d: R(d, meta_subjects=()),
        "no reflexive meta-knowledge subject is declared",
    ),
    _case(
        "a-capability-requiring-substrate-nothing-declares",
        lambda d: R(d, future_capabilities=_swap(d.future_capabilities, 0, requires=("NOTHING",))),
        "a future capability requires undeclared substrate element 'NOTHING'",
    ),
    _case(
        "substrate-no-capability-requires",
        lambda d: R(
            d,
            substrate_elements=d.substrate_elements
            + (SubstrateElement(substrate_id="NOTHING", mechanism="m", module="m", symbol="s"),),
        ),
        "substrate element 'NOTHING' is declared and no future capability requires it",
    ),
    _case(
        "no-anti-finite-mechanism",
        lambda d: R(d, anti_finite_mechanisms=()),
        "no anti-finite mechanism is declared",
    ),
    _case(
        "no-self-improvement-mechanism",
        lambda d: R(d, self_improvement=()),
        "no self-improvement mechanism is declared",
    ),
    _case(
        "no-proposal-requirement",
        lambda d: R(d, proposal_requirements=()),
        "no architectural proposal requirement is declared, so architecture could change with "
        "nothing to satisfy",
    ),
    _case(
        "no-default-rule",
        lambda d: R(d, default_rule=()),
        "no default rule is declared for a novel construct",
    ),
]

# --------------------------------------------------------------------------- reality and time

REALITY = [
    _case(
        "no-reality-dimension",
        lambda d: R(d, reality_dimensions=()),
        "no reality dimension is declared",
    ),
    _case(
        "a-reality-that-omits-a-declared-dimension",
        lambda d: R(d, realities=_swap(d.realities, 0, systems={})),
        "an omitted dimension is a silent default, which is what the unresolved token is for",
    ),
    _case(
        "a-reality-on-a-dimension-nothing-declares",
        lambda d: R(
            d,
            realities=_swap(d.realities, 0, systems={**d.realities[0].systems, "NOTHING": "x"}),
        ),
        "declares undeclared dimension 'NOTHING'",
    ),
    _case(
        "a-reality-bound-to-no-frame-kind-that-discloses-no-gap",
        lambda d: R(d, realities=_swap(d.realities, 0, frame_kind="", frame_kind_gap=None)),
        "binds to no frame kind and discloses no gap",
    ),
    _case(
        "no-residual-reality",
        lambda d: R(d, realities=_every(d.realities, residual=False)),
        "no reality is declared residual, so a reality nobody has met has nowhere to rest",
    ),
    _case(
        "a-root-context-that-is-not-a-reality",
        lambda d: R(d, context_root="NOTHING"),
        "the root context 'NOTHING' is not a declared reality, so the context chain would bottom "
        "out in nothing",
    ),
    _case(
        "a-temporal-system-with-no-type",
        lambda d: R(d, temporal_systems=_swap(d.temporal_systems, 0, system_type="   ")),
        "declares no system type",
    ),
    _case(
        "a-temporal-system-with-no-chronology",
        lambda d: R(d, temporal_systems=_swap(d.temporal_systems, 0, chronology_model="   ")),
        "declares no chronology model",
    ),
    _case(
        "no-disclosed-epoch-gap",
        lambda d: R(d, temporal_systems=_every(d.temporal_systems, epoch_gap=None)),
        "no temporal system discloses an epoch gap, so the residual chronology would be claiming "
        "an epoch it cannot have",
    ),
    _case(
        "no-forbidden-temporal-literal",
        lambda d: R(d, forbidden_source_literals=()),
        "no forbidden temporal literal is declared, so the temporal-assumption law would measure "
        "nothing",
    ),
]

# --------------------------------------------------------------------------- the bounds

BOUNDS = [
    _case(
        "more-primitives-than-the-bound-allows",
        lambda d: R(d, primitive_bound=1),
        "structural primitives are declared and the bound is 1",
    ),
    _case(
        "more-entity-classes-than-the-bound-allows",
        lambda d: R(d, entity_class_bound=1),
        "entity classes are declared and the bound is 1",
    ),
    _case(
        "more-states-than-the-bound-allows",
        lambda d: R(d, state_bound=1),
        "states are declared and the bound is 1",
    ),
    _case(
        "a-bound-that-forbids-the-foundation-itself",
        lambda d: R(d, primitive_bound=0, entity_class_bound=0, state_bound=0),
        "the primitive bound is 0, which forbids the foundation itself",
        "the entity class bound is 0, which forbids the foundation itself",
        "the state bound is 0, which forbids the foundation itself",
    ),
    _case(
        "no-reported-metric",
        lambda d: R(d, reported_metrics=()),
        "no complexity metric is declared for reporting",
    ),
]

# --------------------------------------------------------------------------- governance

GOVERNANCE = [
    _case(
        "an-unassigned-owner-token-that-is-not-a-role",
        lambda d: R(d, unassigned_owner="NOTHING"),
        "the unassigned owner token 'NOTHING' is not a declared role, so an unowned subject could "
        "not be admitted and would instead be dropped",
    ),
    _case("no-law-at-all", lambda d: R(d, laws=()), "no law is declared"),
    _case(
        "a-law-that-states-nothing",
        lambda d: R(d, laws=_swap(d.laws, 0, statement="   ")),
        "states nothing",
    ),
    _case("no-parity-layer", lambda d: R(d, parity_layers=()), "no parity layer is declared"),
    _case(
        "no-reality-probe",
        lambda d: R(d, reality_probes=()),
        "no reality probe is declared, so the declaration would never be compared against the "
        "measured world",
    ),
    _case(
        "no-forbidden-phrase",
        lambda d: R(d, forbidden_phrases=()),
        "no forbidden phrase is declared, so the non-goal law would be vacuous",
    ),
    _case("no-forbidden-outcome", lambda d: R(d, forbidden_outcomes=()), "no forbidden outcome"),
    _case(
        "a-one-sided-contradiction",
        lambda d: R(d, minimum_positions=1),
        "a contradiction is declared to need fewer than two positions, which would make a "
        "one-sided disagreement recordable as a contradiction",
    ),
    _case(
        "no-resolution-state-leaves-a-contradiction-standing",
        lambda d: R(d, resolution_states=_every(d.resolution_states, contradicting=False)),
        "no resolution state leaves a contradiction standing",
    ),
    _case(
        "no-resolution-state-resolves-anything",
        lambda d: R(d, resolution_states=_every(d.resolution_states, contradicting=True)),
        "no resolution state resolves a contradiction",
    ),
    _case(
        "no-residual-gap-class",
        lambda d: R(d, residual_gap_class="NOTHING"),
        "the residual gap class is not declared",
    ),
    _case(
        "a-declaration-that-closes-itself",
        lambda d: R(d, closed_set=True),
        "the declaration marks itself a closed set",
    ),
    _case(
        "a-declaration-that-declares-a-ceiling",
        lambda d: R(d, upper_limit=99),
        "the declaration declares an upper limit of 99",
    ),
    _case(
        "no-evidence-home",
        lambda d: R(d, evidence_home="   "),
        "no evidence home is declared",
    ),
    _case(
        "a-gate-with-no-verify-stage-label",
        lambda d: R(d, gate={}),
        "the gate declares no verify stage label",
    ),
]

CASES = STATES + COMPOSITION + DISCOVERY + EVOLUTION + REALITY + BOUNDS + GOVERNANCE


@pytest.mark.parametrize(("mutate", "fragments"), CASES)
def test_one_forged_incoherence_is_reported_and_named(
    declaration: Declaration,
    live: Mapping[str, frozenset[str]],
    healthy: tuple[str, ...],
    mutate: Mutation,
    fragments: tuple[str, ...],
) -> None:
    """Each case forges one incoherence and asserts the sentence ``validate`` adds because of it.

    The fragment is asserted rather than the whole problem because the arms that name a row quote
    the identifier they found, and an identifier is declared data — a test spelling one out would
    fail the day the declaration renames it, which is not the day this arm broke.
    """
    added = _added(mutate(declaration), live, healthy)

    assert added, "the forgery changed nothing, so this arm is not reached by it"
    for fragment in fragments:
        assert any(fragment in problem for problem in added), fragment


# --------------------------------------------------------------- every arm, not only the listed
#
# THE TABLE ABOVE CANNOT PROVE THE ARM IT FORGOT, and it cannot notice one ADDED after it was
# written: a new ``problems.append`` inherits the table's silence and the suite stays green over an
# incoherence nothing ever saw reported. So the same argument is made a second way, deriving BOTH
# sides — the arms from ``Declaration``'s own source by AST, the forgeries from the real
# declaration's own fields — with the driver authored once in ``engine/tests`` (UCKP-ART-03).
#
# The table stays, and is the readable half: each row says which incoherence a named arm exists to
# catch, which is a claim about intent no derived sweep can make. This is the complete half.

#: Asked, never listed: a ``_validate_*`` added to :class:`Declaration` is swept on the next run.
VALIDATION_METHODS = tuple(name for name in dir(Declaration) if name.startswith("_validate"))

#: The one arm no corruption of the DECLARATION can reach, because it does not report on the
#: declaration: it fires when the caller supplied no implemented set for a binding kind at all,
#: which is a fact about the measurement. ``test_a_binding_kind_nothing_supplied_is_not_silently_
#: satisfied`` below proves it, by supplying ``{}``. Located by its own text rather than written
#: down as a line number, so the exemption cannot drift as the file above it grows, and cannot
#: outlive the arm it excuses — delete that arm and this test fails asking why it was named.
MEASUREMENT_AND_NOT_DECLARATION = "nothing supplied the implemented set"


def test_every_incoherence_validate_can_report_is_reachable(
    declaration: Declaration, live: Mapping[str, frozenset[str]]
) -> None:
    arms = reason_arms(Declaration, methods=VALIDATION_METHODS)
    exempt = tuple(
        line
        for line, fragments in arms.items()
        if any(MEASUREMENT_AND_NOT_DECLARATION in fragment for fragment in fragments)
    )

    assert len(exempt) == 1, (
        "exactly one arm reports on the measurement rather than on the declaration; if that is no "
        f"longer true the exemption has to be re-argued, not widened — found {list(exempt)}"
    )
    assert_every_reason_arm_is_reachable(
        lambda broken: broken.validate(live),
        declaration,
        Declaration,
        declaration_module,
        contract,
        methods=VALIDATION_METHODS,
        unreachable=exempt,
    )


def test_the_declaration_the_forgeries_are_measured_against_is_itself_coherent(
    healthy: tuple[str, ...],
) -> None:
    """Otherwise every arm above is proven against a document that was already incoherent, and
    ``_added``'s subtraction is hiding the arms the real declaration already trips."""
    assert healthy == ()


def test_a_binding_kind_nothing_supplied_is_not_silently_satisfied(
    declaration: Declaration, healthy: tuple[str, ...]
) -> None:
    """An absent implemented set is a distinct fact from an empty one.

    ``None`` means no module reported on that kind at all — a measurement that did not happen —
    and it has to be reported as such, because treating it as an empty set would report every
    declared name as unimplemented and bury the fact that nothing looked.
    """
    added = _added(declaration, {}, healthy)

    kinds = sorted(declaration.declared_bindings())
    for kind in kinds:
        assert f"nothing supplied the implemented set for binding kind {kind!r}" in added
    assert len(added) == len(kinds), "an absent set must report once per kind and nothing else"


def test_a_declared_binding_no_module_implements_is_reported(
    declaration: Declaration, live: Mapping[str, frozenset[str]], healthy: tuple[str, ...]
) -> None:
    kind = "law check"
    absent = sorted(declaration.declared_bindings()[kind])[0]
    partial = {**live, kind: live[kind] - {absent}}

    assert _added(declaration, partial, healthy) == [
        f"{kind} {absent!r} is declared and not implemented"
    ]


def test_a_live_binding_no_declaration_claims_is_reported(
    declaration: Declaration, live: Mapping[str, frozenset[str]], healthy: tuple[str, ...]
) -> None:
    """The other direction, and the one a growing package reaches by accident: code that implements
    a binding the declaration never asked for is an authority nothing declared."""
    kind = "detector"
    extra = {**live, kind: live[kind] | {"engine.somewhere.undeclared"}}

    assert _added(declaration, extra, healthy) == [
        f"{kind} 'engine.somewhere.undeclared' is implemented and no declaration claims it"
    ]


# --------------------------------------------------------------------------- require_valid


def test_require_valid_is_silent_on_a_coherent_declaration(
    declaration: Declaration, live: Mapping[str, frozenset[str]]
) -> None:
    assert declaration.require_valid(live) is None


def test_a_short_problem_list_is_raised_whole(
    declaration: Declaration, live: Mapping[str, frozenset[str]]
) -> None:
    """Under eight problems there is no remainder, so the message must not claim one."""
    broken = R(declaration, closed_set=True, upper_limit=7)

    with pytest.raises(DeclarationError) as raised:
        broken.require_valid(live)

    assert "the declaration is incoherent: " in str(raised.value)
    assert "closed set" in str(raised.value)
    assert "upper limit of 7" in str(raised.value)
    assert "more)" not in str(raised.value)


def test_a_long_problem_list_is_truncated_and_says_how_much_it_hid(
    declaration: Declaration, live: Mapping[str, frozenset[str]]
) -> None:
    """``validate`` returns everything and ``require_valid`` raises one line, so the line has to
    say that it is not the whole list. An author who repaired the eight named problems and saw the
    same refusal return would otherwise have no way to know why.

    Asserted against the list ``validate`` actually returned rather than a hand-counted string, so
    the test measures the truncation and not the declaration's current shape.
    """
    broken = R(declaration, states=())
    problems = broken.validate(live)
    assert len(problems) > 8, "this forgery must overflow the head for the tail to be reachable"

    with pytest.raises(DeclarationError) as raised:
        broken.require_valid(live)

    head = "; ".join(problems[:8])
    assert str(raised.value) == (
        f"the declaration is incoherent: {head} (+{len(problems) - 8} more)"
    )


# --------------------------------------------------------------------------- the accessors

LOOKUPS = [
    ("temporal_system", "'NOTHING' is not a declared temporal system"),
    ("law", "'NOTHING' is not a declared law"),
    ("substrate", "'NOTHING' is not a declared substrate element"),
]


@pytest.mark.parametrize(("method", "message"), LOOKUPS)
def test_a_lookup_that_finds_nothing_is_a_fault_and_not_a_none(
    declaration: Declaration, method: str, message: str
) -> None:
    """Every accessor raises rather than returning ``None``.

    A ``None`` here would travel: the caller would attribute a law to a subject that has no law, and
    the refusal would surface somewhere that cannot say which identifier was missing.
    """
    with pytest.raises(DeclarationError, match=message):
        getattr(declaration, method)("NOTHING")


def test_an_admission_no_extension_point_serves_is_a_fault(declaration: Declaration) -> None:
    """This is how an admission function learns what it admits, so an unserved admission is a
    function that would otherwise have to name its own vocabulary in code."""
    with pytest.raises(DeclarationError, match="no extension point declares the admission"):
        declaration.point_for_admission("admit_nothing")


def test_a_code_role_no_profile_serves_is_a_fault(declaration: Declaration) -> None:
    with pytest.raises(DeclarationError, match="no profile role 'investigation' is declared"):
        R(declaration, profile_roles={}).profile_for("investigation")


def test_the_research_facets_are_read_from_the_profile_the_role_names(
    declaration: Declaration,
) -> None:
    """Not a constant, and not the default profile: whichever profile the ``investigation`` role
    currently names. That indirection is the only reason a module never spells a profile out."""
    named = declaration.profile_for("investigation")

    assert declaration.research_facets == declaration.profile(named).required_payload
    assert declaration.research_facets, "a research subject that must carry nothing is unbounded"


# --------------------------------------------------------------------------- disclosure sites


def test_a_gap_found_at_an_undeclared_site_cannot_be_classified(declaration: Declaration) -> None:
    """The three inline disclosure sites each need a declared source, because the source is what
    supplies the classification and the severity. Collecting a gap with neither would admit an
    unclassified subject into the ledger, which is the one thing the disclosure law measures."""
    with pytest.raises(DeclarationError, match="gap_disclosure declares no source"):
        R(declaration, gap_disclosure_sources=()).all_disclosed_gaps()


def test_every_inline_disclosure_site_contributes_to_the_collected_gaps(
    declaration: Declaration,
) -> None:
    """The stated gaps are a subset, never the whole: a state binding to no owner, a reality with an
    approximate frame and a temporal system with no epoch are disclosures too."""
    collected = declaration.all_disclosed_gaps()
    sources = {gap.source for gap in collected}

    assert len(collected) > len(declaration.disclosed_gaps)
    assert {spec.source for spec in declaration.gap_disclosure_sources} >= sources
    assert [gap.gap_id for gap in collected] == sorted(gap.gap_id for gap in collected)
    for gap in collected:
        assert gap.classification, gap.gap_id
        assert gap.severity, gap.gap_id


def test_two_conditions_are_told_apart_by_composition_and_not_by_name(
    declaration: Declaration,
) -> None:
    """The signature is what the ledger can distinguish. Two conditions differing only in the name
    someone gave them are one condition recorded twice, and the signature is what says so."""
    original = declaration.conditions[0]
    renamed = R(original, condition="SOMETHING-ELSE", named_by="somebody else")

    assert renamed.signature() == original.signature(), "a rename is not a distinction"
    assert R(original, state="NOWHERE").signature() != original.signature()
    assert original.signature()[:2] == (original.state, original.domain)
    assert original.signature()[2] == tuple(sorted(original.qualifiers.items()))
    assert original.signature()[3] == tuple(sorted(original.axes.items()))


def test_no_two_declared_conditions_share_a_signature(declaration: Declaration) -> None:
    """The claim the condition catalogue exists to test: collapsing the taxonomy into a composition
    cost no expressive power. If two declared conditions collided, it had.

    Nothing in the package calls ``signature()``, so this test is where that claim is measured
    rather than restated.
    """
    signatures = [spec.signature() for spec in declaration.conditions]
    assert len(set(signatures)) == len(signatures)


# --------------------------------------------------------------------------- parsing

MALFORMED = [
    pytest.param({}, "the declaration has no 'gate'", id="nothing-at-all"),
    pytest.param({"gate": "OPEN"}, "the declaration has no gate block", id="a-gate-that-is-a-word"),
    pytest.param(
        {"gate": {}, "source_discipline": []},
        "the declaration has no source_discipline block",
        id="a-source-discipline-that-is-a-list",
    ),
    pytest.param(
        {"gate": {}, "source_discipline": {}},
        # THE MESSAGE NAMES THE WHOLE PATH, NOT THE STEP THAT FAILED. `_node` walks
        # strategic_direction → review and reports 'strategic_direction.review' even though it
        # was the FIRST step that was absent. That is the useful end of the trade: an author
        # told "no 'strategic_direction'" learns a key is missing, while one told
        # "no 'strategic_direction.review'" learns which reader wanted it and why.
        "the declaration has no 'strategic_direction.review'",
        id="a-missing-nested-path",
    ),
]


@pytest.mark.parametrize(("document", "message"), MALFORMED)
def test_a_malformed_document_is_a_fault_that_names_what_was_missing(
    document: dict[str, Any], message: str
) -> None:
    """Every parse failure is a fault, never a verdict — and it says which node was absent, because
    "the declaration is malformed" sends an author to read four thousand lines of JSON."""
    with pytest.raises(DeclarationError, match=message):
        parse(document)


def test_a_block_that_should_be_a_list_is_refused_as_one(declaration: Declaration) -> None:
    """``_rows`` skips non-mapping members quietly, so the type of the block itself is the only
    thing left to check: a mapping where a list belongs would otherwise iterate its keys."""
    document = json.loads(Path(declaration.source).read_text(encoding="utf-8"))
    document["laws"] = {"URKE-L-01": {"statement": "s"}}

    with pytest.raises(DeclarationError, match="'laws' must be a list"):
        parse(document)


def test_a_row_that_declares_no_required_field_names_the_field_and_the_row(
    declaration: Declaration,
) -> None:
    document = json.loads(Path(declaration.source).read_text(encoding="utf-8"))
    document["laws"][0].pop("statement")

    with pytest.raises(DeclarationError, match="a law declares no 'statement'"):
        parse(document)


def test_a_single_string_where_a_list_belongs_is_read_as_a_list_of_one(
    declaration: Declaration,
) -> None:
    """A convenience with a cost: it means a one-element list can be written unbracketed, so the
    parse must not depend on the bracket to know it read a collection."""
    document = json.loads(Path(declaration.source).read_text(encoding="utf-8"))
    only = document["evolution"]["subjects"][0]["operators"][0]
    document["evolution"]["subjects"][0]["operators"] = only

    parsed = parse(document)

    assert parsed.evolution_subjects[0].operators == (only,)


# --------------------------------------------------------------------------- loading


def test_a_declaration_that_is_not_an_object_is_refused(tmp_path: Path) -> None:
    """A JSON list parses and is not a declaration. Nothing downstream would say so: ``_node``
    would report a missing key on a document that has no keys at all."""
    target = tmp_path / "urke.json"
    target.write_text("[]", encoding="utf-8")

    with pytest.raises(DeclarationError, match="the declaration is not an object"):
        load_declaration(str(target))


def test_unreadable_bytes_are_a_fault_that_quotes_the_reason(tmp_path: Path) -> None:
    """Distinguished from absence: "there is no declaration" and "the declaration is not JSON" send
    an operator to two different places, and only one of them is a bootstrap problem."""
    target = tmp_path / "urke.json"
    target.write_text("{ not json", encoding="utf-8")

    with pytest.raises(DeclarationError, match="the declaration cannot be read: "):
        load_declaration(str(target))

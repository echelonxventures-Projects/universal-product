"""UAPF-000001 — tests for the vocabulary primitive, the identity engine and the state engine.

These three are the framework's floor: every other module registers a term, mints an identity
or guards a transition through them, so a defect here is a defect everywhere. The tests
therefore concentrate on the *fail-closed* paths — an unregistered term, an unregistered kind,
an illegal transition, an exhausted retry budget — because those are the guarantees the rest of
the package relies on rather than re-checks.

Process-wide vocabularies: the registries are deliberately module-level (one namespace per
concern), so tests here use names unique to themselves and assert membership rather than
totals. Asserting a total would couple this file to every other test that registers a term.
"""

from __future__ import annotations

from platform.universal_pipeline.errors import (
    PipelineIdentityError,
    PipelineStateError,
    UniversalPipelineError,
)
from platform.universal_pipeline.identity import (
    DIGEST_WIDTH,
    IDENTITY_PREFIX,
    SEED_OBJECT_KINDS,
    Identity,
    meta_model,
    mint,
    mint_from,
    object_kind_description,
    object_kinds,
    register_object_kind,
    require_object_kind,
)
from platform.universal_pipeline.state import (
    CERTIFIED_STATE,
    DEFAULT_MAX_RETRY,
    ESCALATION_REASONS,
    EXECUTION_UNIT_STATES,
    ILLEGAL_TRANSITION_CODE,
    INITIAL_STATE,
    TERMINAL_STATES,
    is_active,
    is_legal_transition,
    is_terminal,
    legal_transitions,
    require_escalation_reason,
    require_retry_budget,
    require_state,
    require_unit_transition,
    state_machine,
)
from platform.universal_pipeline.vocabulary import VOCABULARY_FORMAT, Vocabulary, VocabularyTerm

import pytest

# --------------------------------------------------------------------------- vocabulary


def _vocab(name: str = "test-vocabulary") -> Vocabulary:
    return Vocabulary(name, error=UniversalPipelineError)


def test_vocabulary_registers_and_requires_terms() -> None:
    vocabulary = _vocab()
    declared = vocabulary.register("alpha", description="the first", attributes={"weight": 1})
    assert declared.term == "alpha"
    assert declared.attribute("weight") == 1
    assert declared.attribute("absent", "fallback") == "fallback"
    assert vocabulary.require("alpha") is declared
    assert "alpha" in vocabulary
    assert len(vocabulary) == 1
    assert vocabulary.terms() == ("alpha",)
    assert vocabulary.get("alpha") is declared
    assert vocabulary.get("missing") is None


def test_vocabulary_is_append_only_and_fail_closed() -> None:
    vocabulary = _vocab()
    vocabulary.register("alpha")
    with pytest.raises(UniversalPipelineError, match="already registered"):
        vocabulary.register("alpha")
    with pytest.raises(UniversalPipelineError, match="unregistered term"):
        vocabulary.require("beta")


@pytest.mark.parametrize("bad", ["Alpha", "alpha_beta", "", "alpha..beta", "-alpha", "alpha-"])
def test_vocabulary_refuses_malformed_terms(bad: str) -> None:
    with pytest.raises(UniversalPipelineError):
        _vocab().register(bad)


def test_vocabulary_name_and_error_type_are_validated() -> None:
    with pytest.raises(UniversalPipelineError, match="lower-case token"):
        Vocabulary("Not A Token", error=UniversalPipelineError)
    with pytest.raises(UniversalPipelineError, match="UAPF error subclass"):
        Vocabulary("fine", error=ValueError)  # type: ignore[arg-type]


def test_vocabulary_register_many_is_idempotent_over_mixed_declarations() -> None:
    vocabulary = _vocab()
    first = vocabulary.register_many(
        ["alpha", {"term": "beta", "description": "second", "attributes": {"auto": True}}]
    )
    assert [term.term for term in first] == ["alpha", "beta"]
    # A second pass over the same catalogue admits nothing new — the property a repeatable
    # discovery pass needs.
    assert vocabulary.register_many(["alpha", {"term": "beta"}]) == ()
    assert vocabulary.terms_where("auto") == ("beta",)
    assert vocabulary.require_all(["beta", "alpha", "alpha"]) == ("alpha", "beta")


def test_vocabulary_register_many_rejects_bad_shapes() -> None:
    vocabulary = _vocab()
    with pytest.raises(UniversalPipelineError, match="string or a mapping"):
        vocabulary.register_many([42])
    with pytest.raises(UniversalPipelineError, match="attributes must be a mapping"):
        vocabulary.register_many([{"term": "gamma", "attributes": "no"}])


def test_vocabulary_require_all_fails_closed_on_one_unknown_term() -> None:
    vocabulary = _vocab()
    vocabulary.register("alpha")
    with pytest.raises(UniversalPipelineError, match="unregistered term"):
        vocabulary.require_all(["alpha", "beta"])


def test_vocabulary_renders_deterministic_evidence() -> None:
    left, right = _vocab(), _vocab()
    for vocabulary in (left, right):
        vocabulary.register("beta", description="b")
        vocabulary.register("alpha", description="a")
    assert left.to_dict()["vocabulary_format"] == VOCABULARY_FORMAT
    assert left.to_dict()["term_count"] == 2
    # Registration order differs from sorted order, and the fingerprint must not notice.
    assert left.fingerprint() == right.fingerprint()
    assert [term.term for term in left.declarations()] == ["alpha", "beta"]


def test_vocabulary_term_copies_its_attributes() -> None:
    source = {"mutable": True}
    term = VocabularyTerm(vocabulary="v", term="t", attributes=source)
    source["mutable"] = False
    assert term.attribute("mutable") is True
    assert term.to_dict()["attributes"] == {"mutable": True}


# ----------------------------------------------------------------------------- identity


def test_every_seeded_object_kind_is_registered_with_its_description() -> None:
    registered = set(object_kinds())
    for kind, description in SEED_OBJECT_KINDS:
        assert kind in registered
        assert object_kind_description(kind) == description


def test_mint_is_deterministic_content_addressed_and_order_significant() -> None:
    left = mint("pipeline", "uapf.evolution", "1.0.0")
    right = mint("pipeline", "uapf.evolution", "1.0.0")
    assert left == right
    assert left.value.startswith(f"{IDENTITY_PREFIX}-PIPELINE-")
    assert len(left.digest) == DIGEST_WIDTH
    assert left.verify()
    left.require_intact()
    # Parts describe an object, so their order is significant and is not normalized away.
    assert mint("pipeline", "a", "b") != mint("pipeline", "b", "a")
    assert mint_from("pipeline", ["a", "b"]) == mint("pipeline", "a", "b")
    assert str(left) == left.value
    assert left.to_dict() == {
        "kind": "pipeline",
        "parts": ["uapf.evolution", "1.0.0"],
        "value": left.value,
    }


def test_kind_namespace_is_rendered_from_the_kind() -> None:
    assert mint("execution-unit", "u1").value.startswith(f"{IDENTITY_PREFIX}-EXECUTION-UNIT-")


def test_mint_fails_closed_on_unknown_kind_and_bad_parts() -> None:
    with pytest.raises(PipelineIdentityError, match="unregistered term"):
        mint("no-such-kind", "x")
    with pytest.raises(PipelineIdentityError, match="at least one identity part"):
        mint("pipeline")
    with pytest.raises(PipelineIdentityError, match="non-empty strings"):
        mint("pipeline", "")


def test_register_object_kind_is_append_only() -> None:
    register_object_kind("test-kind-append-only", "a kind registered by this test")
    assert "test-kind-append-only" in object_kinds()
    with pytest.raises(PipelineIdentityError, match="already registered"):
        register_object_kind("test-kind-append-only")
    require_object_kind("test-kind-append-only")


def test_hand_built_identity_is_detected_as_not_minted() -> None:
    forged = Identity(kind="pipeline", parts=("a",), value="UAPF-PIPELINE-deadbeefdeadbeefdead")
    assert not forged.verify()
    with pytest.raises(PipelineIdentityError, match="not minted"):
        forged.require_intact()


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"kind": "", "parts": ("a",), "value": "v"}, "kind is required"),
        ({"kind": "pipeline", "parts": ("a",), "value": ""}, "value is required"),
        ({"kind": "pipeline", "parts": ["a"], "value": "v"}, "must be a tuple"),
        ({"kind": "pipeline", "parts": ("",), "value": "v"}, "non-empty strings"),
    ],
)
def test_identity_validates_its_own_shape(kwargs: dict[str, object], match: str) -> None:
    with pytest.raises(PipelineIdentityError, match=match):
        Identity(**kwargs)  # type: ignore[arg-type]


def test_meta_model_is_derived_from_the_vocabulary() -> None:
    model = meta_model()
    assert model["identity_prefix"] == IDENTITY_PREFIX
    assert model["kind_count"] == len(object_kinds())
    assert [entry["kind"] for entry in model["kinds"]] == list(object_kinds())
    assert model["fingerprint"] == meta_model()["fingerprint"]


# -------------------------------------------------------------------------------- state


def test_declared_states_match_repository_truth() -> None:
    assert EXECUTION_UNIT_STATES == (
        "SPECIFIED",
        "READY",
        "EXECUTING",
        "IMPLEMENTED",
        "VALIDATED",
        "CERTIFIED",
        "FAILED",
        "BLOCKED",
        "SUPERSEDED",
        "ARCHIVED",
    )
    assert INITIAL_STATE == "SPECIFIED"
    assert CERTIFIED_STATE == "CERTIFIED"
    assert TERMINAL_STATES == frozenset({"SUPERSEDED", "ARCHIVED"})


@pytest.mark.parametrize(
    ("source", "target"),
    [
        ("SPECIFIED", "READY"),
        ("SPECIFIED", "BLOCKED"),
        ("BLOCKED", "READY"),
        ("READY", "EXECUTING"),
        ("READY", "BLOCKED"),
        ("EXECUTING", "IMPLEMENTED"),
        ("EXECUTING", "FAILED"),
        ("IMPLEMENTED", "VALIDATED"),
        ("VALIDATED", "CERTIFIED"),
        ("VALIDATED", "FAILED"),
        ("FAILED", "READY"),
        ("FAILED", "ARCHIVED"),
        ("CERTIFIED", "ARCHIVED"),
        ("SUPERSEDED", "ARCHIVED"),
    ],
)
def test_legal_transitions_from_section_two_are_permitted(source: str, target: str) -> None:
    require_unit_transition(source, target)
    assert is_legal_transition(source, target)


@pytest.mark.parametrize(
    ("source", "target"),
    [
        ("SPECIFIED", "EXECUTING"),
        ("SPECIFIED", "IMPLEMENTED"),
        ("READY", "IMPLEMENTED"),
        ("READY", "CERTIFIED"),
        ("IMPLEMENTED", "CERTIFIED"),
        ("EXECUTING", "CERTIFIED"),
        ("VALIDATED", "IMPLEMENTED"),
        ("CERTIFIED", "EXECUTING"),
        ("CERTIFIED", "READY"),
        ("BLOCKED", "EXECUTING"),
        ("ARCHIVED", "READY"),
        ("ARCHIVED", "ARCHIVED"),
    ],
)
def test_illegal_transitions_from_section_four_are_refused(source: str, target: str) -> None:
    """Every §4 illegal transition is refused *because it is absent from the §2 table*."""
    assert not is_legal_transition(source, target)
    with pytest.raises(PipelineStateError) as raised:
        require_unit_transition(source, target)
    assert raised.value.context["gate"] == ILLEGAL_TRANSITION_CODE
    assert raised.value.context["from_state"] == source


def test_any_active_state_may_be_superseded_and_archived_is_absolutely_terminal() -> None:
    for state in EXECUTION_UNIT_STATES:
        if state in TERMINAL_STATES:
            continue
        require_unit_transition(state, "SUPERSEDED")
    assert legal_transitions("ARCHIVED") == ()
    assert is_terminal("ARCHIVED")
    assert is_terminal("SUPERSEDED")
    assert is_active("READY")
    assert not is_active("ARCHIVED")


def test_unknown_states_fail_closed() -> None:
    with pytest.raises(PipelineStateError, match="unknown execution-unit state"):
        require_state("INVENTED")
    with pytest.raises(PipelineStateError):
        legal_transitions("INVENTED")
    with pytest.raises(PipelineStateError):
        is_legal_transition("READY", "INVENTED")


def test_retry_budget_is_bounded_and_exhaustion_is_an_error() -> None:
    require_retry_budget(0)
    require_retry_budget(DEFAULT_MAX_RETRY - 1)
    with pytest.raises(PipelineStateError, match="retry budget exhausted"):
        require_retry_budget(DEFAULT_MAX_RETRY)
    with pytest.raises(PipelineStateError, match="non-negative"):
        require_retry_budget(-1)
    with pytest.raises(PipelineStateError, match="max_retry must be non-negative"):
        require_retry_budget(0, max_retry=-1)
    # A zero budget means no retry is permitted at all, which must not be a special case.
    with pytest.raises(PipelineStateError, match="retry budget exhausted"):
        require_retry_budget(0, max_retry=0)


def test_only_the_four_declared_escalation_reasons_halt_autonomy() -> None:
    assert len(ESCALATION_REASONS) == 4
    for reason in ESCALATION_REASONS:
        require_escalation_reason(reason)
    with pytest.raises(PipelineStateError, match="unknown escalation reason"):
        require_escalation_reason("because-i-said-so")


def test_state_machine_projection_is_rendered_from_the_table() -> None:
    machine = state_machine()
    assert machine["authority"] == "06-IMPLEMENTATION-STATE-MACHINE.md"
    assert machine["states"] == list(EXECUTION_UNIT_STATES)
    assert machine["initial_state"] == INITIAL_STATE
    assert machine["transition_count"] == sum(
        len(legal_transitions(state)) for state in EXECUTION_UNIT_STATES
    )
    # The projection is derived, so it agrees with the guard for every declared pair.
    for row in machine["transitions"]:
        for target in row["to"]:
            require_unit_transition(row["from"], target)


def test_a_vocabulary_knows_which_classification_it_governs() -> None:
    """THE NAME IS NOT DECORATION — it is the classification the vocabulary governs, and it
    is what every refusal raised by that vocabulary reports as ``name``.

    Every other test here reaches a vocabulary through the module-level registry it belongs
    to, where the caller already knows which one it asked for, so the accessor that lets a
    HOLDER of a vocabulary say which one it is had no caller. Without it a consumer handed a
    vocabulary object can register terms into it and never find out what it classifies.
    """
    vocabulary = _vocab("test-named-vocabulary")

    assert vocabulary.name == "test-named-vocabulary"
    assert vocabulary.to_dict()["vocabulary"] == vocabulary.name

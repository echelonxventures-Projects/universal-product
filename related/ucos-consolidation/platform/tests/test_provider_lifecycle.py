"""Provider Lifecycle tests (Terminal-04).

The lifecycle's load-bearing property is that ``ACTIVE`` is unreachable except through
``CERTIFIED`` — that is how PC-11 is enforced structurally rather than by a check
someone could forget. These tests prove that by exhaustively walking the transition
map.
"""

from __future__ import annotations

import itertools
from platform.universal_provider.errors import ProviderLifecycleError
from platform.universal_provider.lifecycle import (
    GENESIS_HASH,
    LIFECYCLE_TRANSITIONS,
    SERVING_PHASES,
    TERMINAL_PHASES,
    LifecycleEntry,
    ProviderLifecycle,
    ProviderPhase,
    coerce_phase,
)

import pytest

QUALIFIED = "fixture.memo@1.0.0"


def _certified() -> ProviderLifecycle:
    lifecycle = ProviderLifecycle()
    lifecycle.declare(QUALIFIED)
    lifecycle.transition(QUALIFIED, ProviderPhase.REGISTERED)
    lifecycle.transition(QUALIFIED, ProviderPhase.VALIDATED)
    lifecycle.transition(QUALIFIED, ProviderPhase.CERTIFIED)
    return lifecycle


def test_the_transition_map_covers_every_phase() -> None:
    assert set(LIFECYCLE_TRANSITIONS) == set(ProviderPhase)
    for phase in TERMINAL_PHASES:
        assert LIFECYCLE_TRANSITIONS[phase] == frozenset()


def test_active_is_reachable_only_from_certified_or_suspended() -> None:
    predecessors = {
        phase for phase, targets in LIFECYCLE_TRANSITIONS.items() if ProviderPhase.ACTIVE in targets
    }
    assert predecessors == {ProviderPhase.CERTIFIED, ProviderPhase.SUSPENDED}


def test_certified_is_reachable_only_from_validated() -> None:
    predecessors = {
        phase
        for phase, targets in LIFECYCLE_TRANSITIONS.items()
        if ProviderPhase.CERTIFIED in targets
    }
    assert predecessors == {ProviderPhase.VALIDATED}


def test_declaration_is_idempotent_and_never_resets_state() -> None:
    lifecycle = ProviderLifecycle()
    assert lifecycle.declare(QUALIFIED) is ProviderPhase.DECLARED
    lifecycle.transition(QUALIFIED, ProviderPhase.REGISTERED)
    assert lifecycle.declare(QUALIFIED) is ProviderPhase.REGISTERED
    assert lifecycle.tracks(QUALIFIED) is True


def test_an_untracked_provider_fails_closed() -> None:
    lifecycle = ProviderLifecycle()
    assert lifecycle.tracks(QUALIFIED) is False
    with pytest.raises(ProviderLifecycleError):
        lifecycle.phase(QUALIFIED)
    with pytest.raises(ProviderLifecycleError):
        lifecycle.transition(QUALIFIED, ProviderPhase.REGISTERED)
    assert lifecycle.can_transition(QUALIFIED, ProviderPhase.REGISTERED) is False
    assert lifecycle.may_serve(QUALIFIED) is False


def test_lifecycle_state_is_version_pinned() -> None:
    lifecycle = ProviderLifecycle()
    with pytest.raises(ProviderLifecycleError) as exc:
        lifecycle.declare("fixture.memo")
    assert "version-pinned" in exc.value.message
    with pytest.raises(ProviderLifecycleError):
        lifecycle.declare("")


def test_the_happy_path_reaches_active_and_may_serve() -> None:
    lifecycle = _certified()
    assert lifecycle.may_serve(QUALIFIED) is False
    entry = lifecycle.transition(QUALIFIED, ProviderPhase.ACTIVE, reason="certified")
    assert entry.to_phase is ProviderPhase.ACTIVE
    assert lifecycle.may_serve(QUALIFIED) is True
    assert lifecycle.require_serving(QUALIFIED) is ProviderPhase.ACTIVE
    assert lifecycle.serving() == (QUALIFIED,)
    assert lifecycle.in_phase(ProviderPhase.ACTIVE) == (QUALIFIED,)


def test_activation_directly_from_registered_is_refused() -> None:
    lifecycle = ProviderLifecycle()
    lifecycle.declare(QUALIFIED)
    lifecycle.transition(QUALIFIED, ProviderPhase.REGISTERED)
    with pytest.raises(ProviderLifecycleError) as exc:
        lifecycle.transition(QUALIFIED, ProviderPhase.ACTIVE)
    assert "PC-10" in exc.value.message
    assert "active" not in exc.value.detail["allowed"]


def test_require_serving_refuses_a_non_serving_phase() -> None:
    lifecycle = _certified()
    with pytest.raises(ProviderLifecycleError) as exc:
        lifecycle.require_serving(QUALIFIED)
    assert "PC-11" in exc.value.message
    assert exc.value.detail["phase"] == "certified"


def test_suspension_is_reinstatable_and_deprecated_still_serves() -> None:
    lifecycle = _certified()
    lifecycle.transition(QUALIFIED, ProviderPhase.ACTIVE)
    lifecycle.transition(QUALIFIED, ProviderPhase.SUSPENDED)
    assert lifecycle.may_serve(QUALIFIED) is False
    lifecycle.transition(QUALIFIED, ProviderPhase.ACTIVE)
    lifecycle.transition(QUALIFIED, ProviderPhase.DEPRECATED)
    assert ProviderPhase.DEPRECATED in SERVING_PHASES
    assert lifecycle.may_serve(QUALIFIED) is True


def test_a_terminal_phase_has_no_exit() -> None:
    lifecycle = _certified()
    lifecycle.transition(QUALIFIED, ProviderPhase.RETIRED)
    for phase in ProviderPhase:
        with pytest.raises(ProviderLifecycleError) as exc:
            lifecycle.transition(QUALIFIED, phase)
        assert exc.value.detail["terminal"] is True


@pytest.mark.parametrize(
    ("source", "target"),
    [
        pair
        for pair in itertools.product(ProviderPhase, ProviderPhase)
        if pair[1] not in LIFECYCLE_TRANSITIONS[pair[0]]
    ],
)
def test_every_undeclared_transition_is_refused(
    source: ProviderPhase, target: ProviderPhase
) -> None:
    lifecycle = ProviderLifecycle()
    lifecycle.declare(QUALIFIED)
    # Walk to `source` legally where possible; otherwise the refusal is already proven.
    route = {
        ProviderPhase.DECLARED: (),
        ProviderPhase.REGISTERED: (ProviderPhase.REGISTERED,),
        ProviderPhase.REJECTED: (ProviderPhase.REJECTED,),
        ProviderPhase.VALIDATED: (ProviderPhase.REGISTERED, ProviderPhase.VALIDATED),
        ProviderPhase.CERTIFIED: (
            ProviderPhase.REGISTERED,
            ProviderPhase.VALIDATED,
            ProviderPhase.CERTIFIED,
        ),
        ProviderPhase.ACTIVE: (
            ProviderPhase.REGISTERED,
            ProviderPhase.VALIDATED,
            ProviderPhase.CERTIFIED,
            ProviderPhase.ACTIVE,
        ),
        ProviderPhase.SUSPENDED: (
            ProviderPhase.REGISTERED,
            ProviderPhase.VALIDATED,
            ProviderPhase.CERTIFIED,
            ProviderPhase.SUSPENDED,
        ),
        ProviderPhase.DEPRECATED: (
            ProviderPhase.REGISTERED,
            ProviderPhase.VALIDATED,
            ProviderPhase.CERTIFIED,
            ProviderPhase.DEPRECATED,
        ),
        ProviderPhase.RETIRED: (ProviderPhase.REGISTERED, ProviderPhase.RETIRED),
    }[source]
    for step in route:
        lifecycle.transition(QUALIFIED, step)
    assert lifecycle.phase(QUALIFIED) is source
    with pytest.raises(ProviderLifecycleError):
        lifecycle.transition(QUALIFIED, target)


def test_coerce_phase_accepts_strings_and_fails_closed() -> None:
    assert coerce_phase("ACTIVE ".strip().lower()) is ProviderPhase.ACTIVE
    assert coerce_phase(ProviderPhase.RETIRED) is ProviderPhase.RETIRED
    with pytest.raises(ProviderLifecycleError) as exc:
        coerce_phase("ascended")
    assert "active" in exc.value.detail["known"]


def test_the_ledger_is_hash_chained_and_verifiable() -> None:
    lifecycle = _certified()
    assert len(lifecycle) == 3
    assert lifecycle.verify() is True
    lifecycle.require_intact()
    entries = lifecycle.entries
    assert entries[0].previous_hash == GENESIS_HASH
    assert entries[1].previous_hash == entries[0].entry_hash
    assert entries[2].previous_hash == entries[1].entry_hash
    assert lifecycle.head_hash == entries[-1].entry_hash
    assert entries[0].recompute_hash() == entries[0].entry_hash
    assert entries[0].to_dict()["from_phase"] == "declared"


def test_a_tampered_ledger_is_detected() -> None:
    lifecycle = _certified()
    original = lifecycle.entries[1]
    lifecycle._entries[1] = LifecycleEntry(  # noqa: SLF001 - tamper simulation
        sequence=original.sequence,
        qualified_id=original.qualified_id,
        from_phase=original.from_phase,
        to_phase=ProviderPhase.ACTIVE,
        reason=original.reason,
        evidence_ref=original.evidence_ref,
        previous_hash=original.previous_hash,
        entry_hash=original.entry_hash,
    )
    assert lifecycle.verify() is False
    with pytest.raises(ProviderLifecycleError):
        lifecycle.require_intact()


def test_a_resequenced_ledger_is_detected() -> None:
    lifecycle = _certified()
    lifecycle._entries.reverse()  # noqa: SLF001 - tamper simulation
    assert lifecycle.verify() is False


def test_history_is_scoped_per_version() -> None:
    lifecycle = ProviderLifecycle()
    other = "fixture.memo@2.0.0"
    for key in (QUALIFIED, other):
        lifecycle.declare(key)
        lifecycle.transition(key, ProviderPhase.REGISTERED)
    lifecycle.transition(other, ProviderPhase.VALIDATED)
    assert len(lifecycle.history(QUALIFIED)) == 1
    assert len(lifecycle.history(other)) == 2
    assert lifecycle.phases() == {
        QUALIFIED: "registered",
        other: "validated",
    }


def test_an_empty_lifecycle_projects_the_genesis_hash() -> None:
    lifecycle = ProviderLifecycle()
    assert lifecycle.head_hash == GENESIS_HASH
    assert lifecycle.verify() is True
    payload = lifecycle.to_dict()
    assert payload["entries"] == []
    assert lifecycle.ledger_hash() == ProviderLifecycle().ledger_hash()
    assert "lifecycle_version" in lifecycle.canonical()

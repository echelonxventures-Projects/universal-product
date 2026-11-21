"""INV-AGN-02 — a new bypass is refused, and every declared capability is kept.

Two properties, and the second is what makes the first honest. A ratchet on direct callers only
means something if the provider can actually answer the questions those callers ask; before the
capability dispatch existed it declared five capabilities and delivered one, so a caller needing a
content hash had no alternative and counting it as a bypass would have charged the provider's own
gap to its callers.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from engine.omega_infinite.capability import (
    AUTHORITY_METADATA,
    CONTENT_HASHING,
    REMOTE_STORAGE,
    TRACKED_CONTENT,
    WORKING_TREE_STATE,
    CapabilityError,
    CapabilitySet,
)
from engine.omega_infinite.direct_callers import (
    DECLARED_DIRECT,
    DECLARED_DIRECT_CEILING,
    DIRECT_CALLER_CEILING,
    UCON_DECLARATION,
    _invokes_tool_directly,
    direct_callers,
    roots,
)
from engine.omega_infinite.git_provider import GitDiscoveryProvider
from engine.omega_infinite.provider import BaseProvider, ProviderError, Selector


@pytest.fixture(scope="module")
def provider():
    return GitDiscoveryProvider(root=".")


def test_no_provider_declares_a_capability_it_cannot_deliver(provider) -> None:
    """The root defect, now a refusal.

    Measured before this existed: five capabilities declared, one deliverable. AUTHORITY_METADATA
    was described in the provider's own docstring as exposed "on request", and there was no
    request to make. A declaration that costs nothing is the shape ENVELOPE_ONLY names.
    """
    assert provider.verify_capabilities() == ()


def test_every_declared_capability_returns_something(provider) -> None:
    for capability in (WORKING_TREE_STATE, CONTENT_HASHING, AUTHORITY_METADATA):
        assert provider.supply(capability, Selector(patterns=("engine/conformance/*",))) is not None


def test_a_capability_delivers_everything_its_description_claims(provider) -> None:
    """The failing case for the defect this suite did not catch the first time.

    WORKING_TREE_STATE's description promises "additions not yet indexed, AND modifications not
    yet recorded". The first implementation ran `--others` alone and reported no modifications at
    all — a capability claiming more than its method delivers, which is the ENVELOPE_ONLY shape
    this package exists to measure, written inside the package that measures it. The earlier
    tests all passed over it, because they asserted the call returned something rather than that
    it returned what was promised.

    Asserting the KEYS is what makes the promise checkable: a merged set would satisfy "returns
    something" while losing which half a path came from.
    """
    state = provider.supply(WORKING_TREE_STATE)
    assert set(state) == {"untracked", "modified"}, (
        "the description promises both halves; a result that cannot distinguish them keeps the "
        "promise only by the reader's charity"
    )


def test_an_undeclared_capability_is_refused(provider) -> None:
    """The provider answers for what it claims and refuses what it does not.

    The exception type is named rather than caught broadly: `pytest.raises(Exception)` would pass
    on a TypeError from a typo, which is how a refusal path can look tested while being broken —
    and the refusal path in `supply` WAS broken exactly that way when first written.
    """
    with pytest.raises(CapabilityError):
        provider.supply(REMOTE_STORAGE)


def test_supplying_a_declared_capability_without_a_method_is_refused() -> None:
    """The failing case that licenses the first test.

    Without this, `verify_capabilities` returning empty could mean the check is sound or that
    nothing can fail it. This constructs a provider that declares a capability and supplies no
    method, and asserts the refusal by name.
    """

    class Hollow(BaseProvider):
        def identifier(self) -> str:
            return "hollow"

        def capabilities(self) -> CapabilitySet:
            return CapabilitySet.of(TRACKED_CONTENT, CONTENT_HASHING)

    hollow = Hollow()
    assert hollow.verify_capabilities() == ("CONTENT_HASHING",)
    with pytest.raises(ProviderError, match="supplies no"):
        hollow.supply(CONTENT_HASHING)


@pytest.mark.parametrize(
    ("label", "source", "expected"),
    [
        ("inline argv", 'import subprocess\nsubprocess.run(["git", "status"])\n', True),
        ("argv in a variable", 'import subprocess\nc = ["git", "s"]\nsubprocess.run(c)\n', True),
        (
            "argv with a splat",
            'import subprocess\ndef f(*a):\n    subprocess.run(["git", *a])\n',
            True,
        ),
        ("a declaration naming it", 'PersistenceBinding("git", "p", False)\n', False),
        ("a docstring naming it", '"""we do not run git here."""\n', False),
    ],
)
def test_the_detector_separates_spawning_from_naming(tmp_path, label, source, expected) -> None:
    """Both defects this predicate had, pinned in both directions.

    It first flagged any call whose arguments held the string, so `PersistenceBinding("git", ...)`
    counted two modules as callers that spawn nothing — and a ratchet with false positives can
    never honestly reach its floor. Narrowing to "first argument of a spawn call" fixed that and
    opened a worse hole: an argv assigned to a variable escaped entirely, which is an evasion
    anyone could perform by accident.

    The cases below are the contract. A guard that can be evaded by an assignment is not a guard,
    and one that counts declarations can never be satisfied.
    """

    module = tmp_path / "subject.py"
    module.write_text(source, encoding="utf-8")
    assert _invokes_tool_directly(module) is expected, label


def test_direct_callers_may_only_fall() -> None:
    """A new module reaching past the provider is refused.

    THIS IS THE RECURRENCE GUARD. Nine execution adapters accumulated behind a contract nothing
    could fail; a direct caller costs nothing to add for the same reason, until something counts
    them. A fall must be recorded in MOVEMENTS so the ceiling tracks the work rather than drifting.
    """
    measured = direct_callers()
    assert len(measured) <= DIRECT_CALLER_CEILING, (
        "a module reached past the provider for a question it now answers. Route it through "
        "`supply`, or declare it in DECLARED_DIRECT with a reason:\n  "
        + "\n  ".join(m for m in measured)
    )


def test_a_fall_must_be_recorded() -> None:
    """The other side of the ratchet: the ceiling may not sit above the measurement."""
    measured = len(direct_callers())
    assert measured == DIRECT_CALLER_CEILING, (
        f"the ceiling is {DIRECT_CALLER_CEILING} and {measured} callers remain. A fall is welcome "
        "and must be recorded in MOVEMENTS with what was migrated and where it went."
    )


def test_declarations_are_ratcheted_too() -> None:
    """The loophole in the first ratchet, closed.

    Declaring a caller lowers the direct count without changing one line of behaviour, so a
    ratchet on that count alone can always be satisfied by writing a paragraph. Every declaration
    is a claim that the provider CANNOT answer the question — not that nobody routed it yet — and
    a claim that cheap deserves a ceiling of its own.
    """
    assert len(DECLARED_DIRECT) <= DECLARED_DIRECT_CEILING, (
        "a caller was declared rather than migrated. That is lawful when the provider genuinely "
        "cannot answer the question, and it must be recorded as a rise here rather than absorbed "
        "into a falling direct count:\n  " + "\n  ".join(sorted(DECLARED_DIRECT))
    )


def test_every_declared_exception_states_a_reason() -> None:
    """An exemption without a stated reason is a silent one."""
    assert DECLARED_DIRECT
    assert all(len(reason) > 40 for reason in DECLARED_DIRECT.values())


def test_a_declaration_naming_no_audit_root_is_a_fault_rather_than_an_empty_scan(
    tmp_path,
) -> None:
    """The roots come from the declaration that already names them, which is what stops this
    module carrying a second list of where the source is. An empty one must fault: a scan over no
    root finds no direct caller, and the ratchet would read that as a clean repository."""

    target = pathlib.Path(tmp_path) / UCON_DECLARATION
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"audit": {"roots": []}}), encoding="utf-8")
    with pytest.raises(RuntimeError, match="declares no audit roots"):
        roots(pathlib.Path(tmp_path))

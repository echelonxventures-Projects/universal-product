"""UCXI-000001 Part 16 — every location rule driven into its failing branch.

The declared catalogue passes every rule, which is the outcome we want and the outcome
that proves the least. A rule whose failing branch has never executed is a rule we are
merely *hoping* is wired up; it can carry a typo, raise instead of report, or measure the
wrong collection, and the passing suite would look identical.

The constructors in :mod:`engine.context.location` refuse most of these states, which is
the correct primary defence — so the states are presented here the way a hand-edited
catalogue, a legacy import or a future refactor would present them: as objects satisfying
the shape each check reads, and nothing more. That is the same technique
``test_registry_and_ownership`` already uses to reach the registry's own guards.

Each test asserts the check *reports* — returns a finding — rather than raising, because a
validator that crashes on bad input is a validator that cannot produce a report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from engine.context import location_assurance
from engine.context import location_assurance as assurance
from engine.context.errors import ContextValidationError
from engine.context.location import (
    FRAME_NAMESPACE,
    LOCATION,
    UNRESOLVED,
    build_frame_registry,
    empty_context_registry,
)
from engine.context.location_assurance import LOCATION_RULE_CHECKS, certify_location
from engine.registry.universal.identity import deterministic_id


@dataclass
class _Axis:
    """A resolved axis, as a check reads one."""

    axis: str
    value: str = "v"
    source_frame: str = "f"
    derived_from: tuple[str, ...] = ()

    @property
    def resolved(self) -> bool:
        return self.value != UNRESOLVED


@dataclass
class _Resolution:
    frame: str = "f"
    chain: tuple[str, ...] = ("f",)
    axes: tuple[_Axis, ...] = ()
    _digests: list[str] = field(default_factory=list)

    @property
    def resolved_axes(self) -> tuple[str, ...]:
        return tuple(a.axis for a in self.axes if a.resolved)

    @property
    def unresolved_axes(self) -> tuple[str, ...]:
        return tuple(a.axis for a in self.axes if not a.resolved)

    def get(self, axis: str) -> _Axis:
        return next(a for a in self.axes if a.axis == axis)

    def digest(self) -> str:
        return self._digests.pop(0) if self._digests else "stable"


@dataclass
class _Frame:
    key: str = "f"
    frame_kind: str = "physical"
    parent: str | None = None
    axes: dict[str, str] = field(default_factory=dict)
    universal_id: str = ""

    def __post_init__(self) -> None:
        if not self.universal_id:
            self.universal_id = deterministic_id("LOCATION", FRAME_NAMESPACE, self.key)


class _Frames:
    """The smallest object the rule checks read: frames, chains and resolutions."""

    def __init__(
        self,
        frames: tuple[_Frame, ...],
        *,
        chains: dict[str, Any] | None = None,
        resolutions: dict[str, _Resolution] | None = None,
    ) -> None:
        self._frames = {f.key: f for f in frames}
        self._chains = chains or {f.key: (f.key,) for f in frames}
        self._resolutions = resolutions or {}

    def frames(self) -> tuple[_Frame, ...]:
        return tuple(self._frames[k] for k in sorted(self._frames))

    def frame(self, key: str) -> _Frame:
        return self._frames[key]

    def chain(self, key: str) -> tuple[str, ...]:
        chain = self._chains[key]
        if isinstance(chain, Exception):
            raise chain
        return chain

    def resolve(self, key: str) -> _Resolution:
        return self._resolutions.get(key, _Resolution(frame=key, chain=self.chain(key)))

    def digest(self) -> str:
        return "stub"


def _check(rule: str, frames: Any) -> list[str]:
    return LOCATION_RULE_CHECKS[rule](frames)


# --------------------------------------------------------------------------- #
# LXV-01 — frame identity                                                      #
# --------------------------------------------------------------------------- #


def test_a_frame_whose_identifier_does_not_reproduce_is_reported():
    forged = _Frame(key="f", universal_id=deterministic_id("LOCATION", FRAME_NAMESPACE, "other"))
    findings = _check("LXV-01", _Frames((forged,)))
    assert findings and "does not reproduce" in findings[0]


def test_a_frame_carrying_a_foreign_identifier_is_reported():
    findings = _check("LXV-01", _Frames((_Frame(key="f", universal_id="NOT-A-UCOS-ID"),)))
    assert findings and "does not reproduce" in findings[0]


# --------------------------------------------------------------------------- #
# LXV-02 — the derivation graph                                                #
# --------------------------------------------------------------------------- #


def test_a_frame_declaring_an_unregistered_axis_is_reported():
    rogue = _Frame(key="f", axes={"astrology": "x"})
    findings = _check("LXV-02", _Frames((rogue,)))
    assert findings == ["f: declares 'astrology', which is not a declared axis"]


def test_a_derivation_graph_without_a_total_order_is_reported(monkeypatch):
    def no_order(**_kwargs: Any) -> list[str]:
        raise ContextValidationError("the axis derivation graph contains a cycle")

    monkeypatch.setattr(location_assurance, "axis_order", no_order)
    findings = _check("LXV-02", _Frames(()))
    assert findings and "no total order" in findings[0]


def test_a_short_axis_order_is_reported(monkeypatch):
    monkeypatch.setattr(location_assurance, "axis_order", lambda **_k: [LOCATION])
    findings = _check("LXV-02", _Frames(()))
    assert findings and "axes ordered" in findings[0]


def test_an_axis_deriving_from_an_unknown_axis_is_reported(monkeypatch):
    monkeypatch.setattr(
        location_assurance, "AXIS_DERIVATION", ((LOCATION, ()), ("calendar", ("astrology",)))
    )
    monkeypatch.setattr(location_assurance, "axis_order", lambda **_k: [LOCATION, "calendar"])
    findings = _check("LXV-02", _Frames(()))
    assert any("not a declared axis" in f for f in findings)


# --------------------------------------------------------------------------- #
# LXV-03 — frame chains                                                        #
# --------------------------------------------------------------------------- #


def test_a_chain_that_raises_is_reported_not_propagated():
    frames = _Frames((_Frame(key="f"),), chains={"f": ContextValidationError("cycle")})
    findings = _check("LXV-03", frames)
    assert findings and findings[0].startswith("f: ")


def test_a_chain_that_does_not_begin_at_its_own_frame_is_reported():
    frames = _Frames((_Frame(key="f"), _Frame(key="g")), chains={"f": ("g",), "g": ("g",)})
    assert any("does not begin at the frame itself" in f for f in _check("LXV-03", frames))


def test_a_chain_that_does_not_terminate_at_a_root_is_reported():
    child = _Frame(key="child", parent="orphan")
    frames = _Frames((child,), chains={"child": ("child",)})
    assert any("does not terminate at a root" in f for f in _check("LXV-03", frames))


# --------------------------------------------------------------------------- #
# LXV-04 — declared values                                                     #
# --------------------------------------------------------------------------- #


def test_an_empty_declared_value_is_reported():
    frames = _Frames((_Frame(key="f", axes={"calendar": "   "}),))
    assert _check("LXV-04", frames) == ["f: axis 'calendar' declares an empty value"]


def test_declaring_the_unresolved_marker_as_a_value_is_reported():
    frames = _Frames((_Frame(key="f", axes={"calendar": UNRESOLVED}),))
    findings = _check("LXV-04", frames)
    assert findings == ["f: axis 'calendar' declares the unresolved marker as a value"]


# --------------------------------------------------------------------------- #
# LXV-05 — location derivation                                                 #
# --------------------------------------------------------------------------- #


def test_a_determined_axis_resolved_without_location_is_reported():
    resolution = _Resolution(frame="f", axes=(_Axis(axis="calendar", derived_from=()),))
    frames = _Frames((_Frame(key="f"),), resolutions={"f": resolution})
    findings = _check("LXV-05", frames)
    assert any("without a location-derived chain" in f for f in findings)


def test_a_provenance_chain_that_is_not_the_declared_one_is_reported():
    resolution = _Resolution(
        frame="f", axes=(_Axis(axis="calendar", derived_from=(LOCATION, "tax")),)
    )
    frames = _Frames((_Frame(key="f"),), resolutions={"f": resolution})
    findings = _check("LXV-05", frames)
    assert any("provenance chain is not the declared one" in f for f in findings)


# --------------------------------------------------------------------------- #
# LXV-06 — the source is in the chain                                          #
# --------------------------------------------------------------------------- #


def test_a_value_sourced_from_outside_the_chain_is_reported():
    resolution = _Resolution(
        frame="f", chain=("f",), axes=(_Axis(axis="calendar", source_frame="elsewhere"),)
    )
    frames = _Frames((_Frame(key="f"),), resolutions={"f": resolution})
    findings = _check("LXV-06", frames)
    assert any("not in the frame chain" in f for f in findings)


def test_a_value_that_disagrees_with_its_declared_source_is_reported():
    frame = _Frame(key="f", axes={"calendar": "declared"})
    resolution = _Resolution(
        frame="f",
        chain=("f",),
        axes=(_Axis(axis="calendar", value="different", source_frame="f"),),
    )
    frames = _Frames((frame,), resolutions={"f": resolution})
    findings = _check("LXV-06", frames)
    assert any("does not match its declared source" in f for f in findings)


# --------------------------------------------------------------------------- #
# LXV-07 — no defaults, no fallbacks                                           #
# --------------------------------------------------------------------------- #


def test_an_axis_declared_in_the_chain_but_unresolved_is_reported():
    frame = _Frame(key="f", axes={"calendar": "c"})
    resolution = _Resolution(
        frame="f", chain=("f",), axes=(_Axis(axis="calendar", value=UNRESOLVED, source_frame=""),)
    )
    frames = _Frames((frame,), resolutions={"f": resolution})
    findings = _check("LXV-07", frames)
    assert any("declared in the chain but unresolved" in f for f in findings)


def test_an_axis_resolved_without_any_declaration_is_reported():
    """The silent-default failure this whole module exists to prevent."""
    frame = _Frame(key="f", axes={})
    resolution = _Resolution(
        frame="f", chain=("f",), axes=(_Axis(axis="calendar", value="invented", source_frame="f"),)
    )
    frames = _Frames((frame,), resolutions={"f": resolution})
    findings = _check("LXV-07", frames)
    assert any("declaring it" in finding for finding in findings)


def test_an_unresolved_axis_carrying_a_value_or_a_source_is_reported():
    frame = _Frame(key="f", axes={})

    class _Sneaky(_Axis):
        @property
        def resolved(self) -> bool:
            return False

    resolution = _Resolution(
        frame="f", chain=("f",), axes=(_Sneaky(axis="calendar", value="v", source_frame="f"),)
    )
    frames = _Frames((frame,), resolutions={"f": resolution})
    findings = _check("LXV-07", frames)
    assert any("unresolved axis carries a value" in f for f in findings)
    assert any("unresolved axis names a source frame" in f for f in findings)


# --------------------------------------------------------------------------- #
# LXV-08 — assigned identifiers                                                #
# --------------------------------------------------------------------------- #


def test_a_malformed_assigned_identifier_is_reported(monkeypatch):
    monkeypatch.setattr(
        location_assurance, "identity_tuples", lambda _f: (("LOCATION", FRAME_NAMESPACE, "k"),)
    )
    monkeypatch.setattr(location_assurance, "is_well_formed", lambda _i: False)
    findings = _check("LXV-08", _Frames(()))
    assert findings == ["k: assigned identifier is not well-formed"]


def test_two_subjects_claiming_one_identifier_are_reported(monkeypatch):
    monkeypatch.setattr(
        location_assurance,
        "identity_tuples",
        lambda _f: (
            ("LOCATION", FRAME_NAMESPACE, "a"),
            ("LOCATION", FRAME_NAMESPACE, "b"),
        ),
    )
    monkeypatch.setattr(location_assurance, "deterministic_id", lambda *_a: "UCOS-LOC-collision")
    findings = _check("LXV-08", _Frames(()))
    assert findings and "claimed by" in findings[0]


# --------------------------------------------------------------------------- #
# LXV-09 — the fixed point                                                     #
# --------------------------------------------------------------------------- #


def test_a_resolution_that_is_not_a_fixed_point_is_reported():
    drifting = _Resolution(frame="f", _digests=["first", "second"])
    frames = _Frames((_Frame(key="f"),), resolutions={"f": drifting})
    assert _check("LXV-09", frames) == ["f: resolution is not a fixed point"]


# --------------------------------------------------------------------------- #
# LXC-07 — every resolved axis is registered                                   #
# --------------------------------------------------------------------------- #


def test_an_unregistered_resolved_axis_fails_the_registration_gate(monkeypatch):
    """A projection that registered nothing must fail LXC-07, not pass vacuously."""

    real = build_frame_registry()
    monkeypatch.setattr(
        location_assurance,
        "context_registries",
        lambda *_a, **_k: {frame.key: empty_context_registry() for frame in real.frames()},
    )
    certificate = certify_location(real)
    assert "LXC-07" in certificate.failed_dimensions
    assert certificate.dimension("LXC-07").detail


@pytest.mark.parametrize("rule", sorted(LOCATION_RULE_CHECKS))
def test_every_rule_returns_a_list_over_the_declared_catalogue(rule: str):
    """No rule raises over real input, and every one returns a reportable list."""
    assert isinstance(LOCATION_RULE_CHECKS[rule](build_frame_registry()), list)


def test_an_identifier_that_reproduces_but_is_malformed_is_still_reported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A GUARD THE MINT MAKES UNREACHABLE, and that is why it is worth keeping.

    The check first asks whether the frame's identifier REPRODUCES — whether minting it again
    from the frame's key yields the same value. If it does, the identifier came from the mint,
    and a minted identifier is well-formed by construction, so the second arm can never fire
    today. It is the arm that would notice the day the mint's own output stopped satisfying
    the identity authority's shape, which is a change nothing else in this module would catch.
    """

    registry = build_frame_registry()
    monkeypatch.setattr(assurance, "is_well_formed", lambda _identifier: False)

    findings = assurance._check_frame_identity(registry)
    assert findings
    assert all("identifier is not well-formed" in f for f in findings)
    assert not any("does not reproduce" in f for f in findings)

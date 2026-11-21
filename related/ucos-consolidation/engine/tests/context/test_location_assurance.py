"""UCXI-000001 Part 16 — the rules and dimensions that measure the location architecture.

Every gate here is tested in **both** directions. A gate that has only ever been observed
to pass is indistinguishable from a gate that cannot fail, and the second one is worth
nothing. So for each rule there is a frame registry constructed to break it.
"""

from __future__ import annotations

import pytest

from engine.context.errors import ContextCertificationError
from engine.context.location import (
    AXIS_DERIVATION,
    LOCATION,
    FrameRegistry,
    ReferenceFrame,
    build_frame_registry,
    frames_from_catalog,
)
from engine.context.location_assurance import (
    FRAME_KIND_PROOF_MINIMUM,
    LOCATION_DIMENSIONS,
    LOCATION_RULE_CHECKS,
    LOCATION_RULES,
    SEVERITY_ADVISORY,
    certify_location,
    complete_frame_kinds,
    complete_frames,
    rebase_differences,
    replay_location,
    require_certified_location,
    to_document,
    validate_location,
)

_ALL_AXES = {axis: f"{axis}.authority" for axis, _ in AXIS_DERIVATION}


@pytest.fixture
def frames() -> FrameRegistry:
    return build_frame_registry()


def _complete_registry(
    *, kinds: tuple[str, ...] = ("physical", "virtual", "orbital")
) -> FrameRegistry:
    """A minimal registry in which every named kind resolves every axis."""
    payload = {
        "frames": [
            {
                "key": f"frame-{index}",
                "title": f"F{index}",
                "frame_kind": kind,
                "axes": {**_ALL_AXES, LOCATION: f"location.{index}"},
            }
            for index, kind in enumerate(kinds)
        ]
    }
    return FrameRegistry(frames_from_catalog(payload))


# --------------------------------------------------------------------------- #
# Rule-set integrity                                                           #
# --------------------------------------------------------------------------- #


def test_every_declared_rule_carries_a_check():
    assert {rule.rule_id for rule in LOCATION_RULES} == set(LOCATION_RULE_CHECKS)


def test_every_declared_dimension_is_measured(frames: FrameRegistry):
    certificate = certify_location(frames)
    assert {d.dimension_id for d in certificate.dimensions} == {d for d, _ in LOCATION_DIMENSIONS}


def test_exactly_one_rule_is_advisory():
    advisory = [r for r in LOCATION_RULES if r.severity == SEVERITY_ADVISORY]
    assert [r.rule_id for r in advisory] == ["LXV-10"]


# --------------------------------------------------------------------------- #
# The declared catalogue passes                                                #
# --------------------------------------------------------------------------- #


def test_the_declared_architecture_validates(frames: FrameRegistry):
    report = validate_location(frames)
    assert report.is_valid, [f.detail for f in report.violations]
    assert report.is_clean


def test_the_declared_architecture_certifies(frames: FrameRegistry):
    certificate = certify_location(frames)
    assert certificate.certified, certificate.failed_dimensions
    assert require_certified_location(frames) == certificate


def test_the_declared_architecture_replays(frames: FrameRegistry):
    replay = replay_location()
    assert replay["fixed_point"], replay["drifted"]
    assert replay["rebuilt_from_declaration"] is True


def test_the_report_and_the_certificate_are_deterministic(frames: FrameRegistry):
    assert validate_location(frames).content_hash == validate_location(frames).content_hash
    assert certify_location(frames).content_hash == certify_location(frames).content_hash


def test_the_certificate_carries_the_seals_it_certifies(frames: FrameRegistry):
    seals = certify_location(frames).seals
    assert set(seals) == {"frames", "validation", "registries", "architecture"}
    assert seals["frames"] == frames.digest()


def test_three_or_more_frame_kinds_resolve_completely(frames: FrameRegistry):
    assert len(complete_frame_kinds(frames)) >= FRAME_KIND_PROOF_MINIMUM


def test_the_complete_frames_are_a_subset_of_the_registered_ones(frames: FrameRegistry):
    assert set(complete_frames(frames)) <= set(frames.frame_keys())


def test_the_assurance_document_is_operational(frames: FrameRegistry):
    document = to_document(frames)
    assert document["operational"] is True
    assert document["complete_frame_kinds"]


# --------------------------------------------------------------------------- #
# Each gate can fail                                                           #
# --------------------------------------------------------------------------- #


def test_a_frame_declaring_nothing_fails_the_completeness_dimensions():
    registry = FrameRegistry([ReferenceFrame(key="empty", title="E", frame_kind="abstract")])
    certificate = certify_location(registry)
    assert not certificate.certified
    assert "LXC-03" in certificate.failed_dimensions
    assert "LXC-04" in certificate.failed_dimensions
    assert "LXC-05" in certificate.failed_dimensions


def test_a_single_frame_kind_fails_the_frame_independence_proof():
    registry = _complete_registry(kinds=("physical", "physical", "physical"))
    report = validate_location(registry)
    assert "LXV-10" in report.rules_failed()
    # advisory only: the architecture is still *valid*, just not yet proven independent
    assert report.is_valid
    assert "LXC-04" in certify_location(registry).failed_dimensions


def test_frames_that_all_resolve_alike_fail_the_rebase_dimension():
    payload = {
        "frames": [
            {"key": f"twin-{i}", "title": "T", "frame_kind": k, "axes": _ALL_AXES}
            for i, k in enumerate(("physical", "virtual", "orbital"))
        ]
    }
    registry = FrameRegistry(frames_from_catalog(payload))
    certificate = certify_location(registry)
    assert "LXC-05" in certificate.failed_dimensions
    assert rebase_differences(registry, ("twin-0", "twin-1")) == ()


def test_an_empty_registry_certifies_nothing():
    certificate = certify_location(FrameRegistry())
    assert not certificate.certified
    assert "LXC-03" in certificate.failed_dimensions
    with pytest.raises(ContextCertificationError):
        require_certified_location(FrameRegistry())


def test_a_frame_sourcing_a_value_from_outside_its_chain_is_impossible_by_construction(
    frames: FrameRegistry,
):
    """LXV-06 has no reachable failure through the public API — and that is the point.

    Resolution reads only the chain, so a value from elsewhere cannot enter. The rule
    exists to keep that true if resolution is ever changed, so the test asserts the
    property rather than manufacturing a violation the type system forbids.
    """
    assert LOCATION_RULE_CHECKS["LXV-06"](frames) == []
    for frame in frames.frames():
        resolution = frames.resolve(frame.key)
        for axis in resolution.axes:
            if axis.resolved:
                assert axis.source_frame in resolution.chain


def test_rebase_across_fewer_than_two_frames_compares_nothing(frames: FrameRegistry):
    assert rebase_differences(frames, ("planetary-a1",)) == ()
    assert rebase_differences(frames, ()) == ()


# --------------------------------------------------------------------------- #
# The derived contexts are judged by the context layer's own rules             #
# --------------------------------------------------------------------------- #


def test_every_frames_projection_satisfies_the_context_rules(frames: FrameRegistry):
    assert LOCATION_RULE_CHECKS["LXV-11"](frames) == []


def test_the_projection_check_runs_over_every_frame(frames: FrameRegistry):
    """A check that silently measured nothing would also return an empty list."""
    from engine.context.location import context_registries

    registries = context_registries(frames)
    assert set(registries) == set(frames.frame_keys())
    assert sum(len(r) for r in registries.values()) > 0


# --------------------------------------------------------------------------- #
# Metrics                                                                      #
# --------------------------------------------------------------------------- #


def test_validation_metrics_describe_the_population(frames: FrameRegistry):
    metrics = validate_location(frames).summary()
    assert metrics["frames"] == len(frames)
    assert metrics["complete_frames"] + metrics["incomplete_frames"] == len(frames)
    assert metrics["registry_digest"] == frames.digest()


def test_certification_metrics_describe_the_population(frames: FrameRegistry):
    metrics = certify_location(frames).summary()
    assert metrics["frames"] == len(frames)
    assert metrics["registered_contexts"] > 0
    assert metrics["violations"] == 0


def test_replay_over_a_supplied_registry_says_so(frames: FrameRegistry):
    replay = replay_location(frames)
    assert replay["rebuilt_from_declaration"] is False
    assert replay["fixed_point"] is True

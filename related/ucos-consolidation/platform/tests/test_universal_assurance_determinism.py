"""UCOS-EPIC-014 — Assurance reproducibility runtime tests (runtime-facing scope).

`determinism.py` exists to make the package's reproducibility claim *checkable* rather
than asserted, so the tests that matter are the ones where reproduction fails. A drifting
producer, a producer that raises, and a replay count too small to prove anything must each
be refused or reported as a shortfall — never rounded up to "reproducible".

Runtime scope only: this file exercises the replay runtime. `ReproducibilityPolicy` is
constructed but not asserted against; policy semantics belong to another session.
"""

from __future__ import annotations

import itertools
from platform.universal_assurance.determinism import (
    REPRODUCIBILITY_FORMAT,
    ReplaySample,
    ReproducibilityReport,
    canonical_bytes,
    digests_match,
    replay_digest,
    reproducibility_observations,
    verify_reproducibility,
)
from platform.universal_assurance.errors import AssuranceReproducibilityError
from platform.universal_assurance.policy import ReproducibilityPolicy

import pytest


def _stable_runner(payload=None):
    """A producer that is a pure function of nothing — the reproducible case."""
    fixed = payload if payload is not None else {"b": 2, "a": [1, 2, 3]}
    return lambda: dict(fixed)


def _drifting_runner():
    """A producer whose output changes on every call — the non-reproducible case."""
    counter = itertools.count()
    return lambda: {"value": next(counter)}


# -- the reproducible case ---------------------------------------------------


def test_a_stable_producer_is_proven_byte_identical():
    report = verify_reproducibility(
        _stable_runner(), subject_id="SUBJ-A", label="core", replays=3, required=True
    )

    assert report.byte_identical is True
    assert report.passed is True
    assert report.is_blocking_shortfall is False
    assert report.replays == 3
    assert len(report.samples) == 3
    assert len(report.distinct_digests) == 1


def test_key_order_is_not_a_difference_because_comparison_is_canonical():
    payloads = iter([{"a": 1, "b": 2}, {"b": 2, "a": 1}])

    report = verify_reproducibility(
        lambda: next(payloads), subject_id="SUBJ-A", label="core", replays=2, required=True
    )

    assert report.byte_identical is True
    assert digests_match({"a": 1, "b": 2}, {"b": 2, "a": 1}) is True


def test_the_report_is_itself_content_addressed_and_reproducible():
    first = verify_reproducibility(
        _stable_runner(), subject_id="SUBJ-A", label="core", replays=2, required=True
    )
    second = verify_reproducibility(
        _stable_runner(), subject_id="SUBJ-A", label="core", replays=2, required=True
    )

    assert first.report_sha256 == second.report_sha256
    assert first.to_dict()["reproducibility_format"] == REPRODUCIBILITY_FORMAT


def test_a_different_subject_produces_a_different_report_hash():
    left = verify_reproducibility(
        _stable_runner(), subject_id="SUBJ-A", label="core", replays=2, required=True
    )
    right = verify_reproducibility(
        _stable_runner(), subject_id="SUBJ-B", label="core", replays=2, required=True
    )

    assert left.report_sha256 != right.report_sha256


# -- the non-reproducible case (must not be rounded up to a pass) ------------


def test_a_drifting_producer_is_reported_as_a_blocking_shortfall_when_required():
    report = verify_reproducibility(
        _drifting_runner(), subject_id="SUBJ-A", label="core", replays=3, required=True
    )

    assert report.byte_identical is False
    assert report.passed is False
    assert report.is_blocking_shortfall is True
    assert len(report.distinct_digests) == 3


def test_drift_is_recorded_but_not_blocking_when_the_policy_does_not_require_identity():
    report = verify_reproducibility(
        _drifting_runner(), subject_id="SUBJ-A", label="core", replays=2, required=False
    )

    assert report.byte_identical is False
    assert report.passed is True
    assert report.is_blocking_shortfall is False


def test_observations_expose_the_numeric_facts_a_metric_can_decide():
    stable = verify_reproducibility(
        _stable_runner(), subject_id="SUBJ-A", label="core", replays=2, required=True
    )
    drifting = verify_reproducibility(
        _drifting_runner(), subject_id="SUBJ-A", label="core", replays=2, required=True
    )

    assert stable.observations() == {
        "reproducibility.replays": 2.0,
        "reproducibility.distinct_digests": 1.0,
        "reproducibility.byte_identical": 1.0,
    }
    assert drifting.observations()["reproducibility.byte_identical"] == 0.0
    assert drifting.observations()["reproducibility.distinct_digests"] == 2.0


def test_an_absent_report_fails_closed_rather_than_reporting_nothing_wrong():
    observations = reproducibility_observations(None)

    assert observations["reproducibility.byte_identical"] == 0.0
    assert observations["reproducibility.replays"] == 0.0


def test_a_present_report_delegates_to_its_own_observations():
    report = verify_reproducibility(
        _stable_runner(), subject_id="SUBJ-A", label="core", replays=2, required=True
    )

    assert reproducibility_observations(report) == report.observations()


# -- authoring faults are raised, never reported as data ---------------------


def test_a_non_callable_producer_is_an_authoring_fault():
    with pytest.raises(AssuranceReproducibilityError):
        verify_reproducibility({"not": "callable"}, subject_id="SUBJ-A", label="core")


@pytest.mark.parametrize("count", [0, 1, -1])
def test_fewer_than_two_replays_cannot_prove_anything_and_is_refused(count):
    with pytest.raises(AssuranceReproducibilityError):
        verify_reproducibility(_stable_runner(), subject_id="SUBJ-A", label="core", replays=count)


@pytest.mark.parametrize("count", [True, 2.0, "2"])
def test_a_non_integer_replay_count_is_refused(count):
    with pytest.raises(AssuranceReproducibilityError):
        verify_reproducibility(_stable_runner(), subject_id="SUBJ-A", label="core", replays=count)


def test_a_producer_that_raises_is_never_reported_as_reproducible():
    def broken():
        raise RuntimeError("the producer exploded")

    with pytest.raises(AssuranceReproducibilityError) as caught:
        verify_reproducibility(broken, subject_id="SUBJ-A", label="core", replays=2)

    assert "the producer exploded" in str(caught.value)


def test_a_producers_own_reproducibility_error_propagates_unmasked():
    """A nested assurance failure must not be re-wrapped as a generic replay failure.

    `verify_reproducibility` wraps arbitrary producer exceptions so a broken producer can
    never look clean. An `AssuranceReproducibilityError` is the one exception it must let
    through untouched — re-wrapping it would bury the inner run's label and replay index
    under this run's, and the diagnosis would point at the wrong producer.
    """
    inner = AssuranceReproducibilityError("inner replay diverged", label="inner-core")

    def nested():
        raise inner

    with pytest.raises(AssuranceReproducibilityError) as caught:
        verify_reproducibility(nested, subject_id="SUBJ-A", label="outer-core", replays=2)

    assert caught.value is inner
    assert "inner replay diverged" in str(caught.value)


def test_a_payload_that_cannot_be_canonicalized_is_a_replay_failure():
    with pytest.raises(AssuranceReproducibilityError):
        verify_reproducibility(
            lambda: {"unserializable": object()},
            subject_id="SUBJ-A",
            label="core",
            replays=2,
        )


# -- policy-sourced defaults -------------------------------------------------


def test_the_replay_count_and_requirement_come_from_the_policy_when_unstated():
    policy = ReproducibilityPolicy(replays=4, byte_identical_required=False)

    report = verify_reproducibility(
        _drifting_runner(), subject_id="SUBJ-A", label="core", policy=policy
    )

    assert report.replays == 4
    assert report.required is False
    assert report.passed is True


def test_explicit_arguments_override_the_policy():
    policy = ReproducibilityPolicy(replays=4, byte_identical_required=False)

    report = verify_reproducibility(
        _drifting_runner(),
        subject_id="SUBJ-A",
        label="core",
        policy=policy,
        replays=2,
        required=True,
    )

    assert report.replays == 2
    assert report.required is True
    assert report.is_blocking_shortfall is True


# -- primitives --------------------------------------------------------------


def test_canonical_bytes_and_replay_digest_agree_with_the_report_samples():
    payload = {"b": 1, "a": 2}

    report = verify_reproducibility(
        lambda: dict(payload), subject_id="SUBJ-A", label="core", replays=2
    )

    assert report.samples[0].digest == replay_digest(payload)
    assert report.samples[0].byte_length == len(canonical_bytes(payload))
    assert digests_match(payload, {"a": 2, "b": 1}) is True
    assert digests_match(payload, {"a": 2}) is False


def test_a_replay_sample_serializes_to_its_core():
    sample = ReplaySample(index=0, digest="a" * 64, byte_length=12)

    assert sample.to_dict() == sample.core()
    assert sample.to_dict() == {"index": 0, "digest": "a" * 64, "byte_length": 12}


def test_a_report_with_no_samples_is_vacuously_identical():
    report = ReproducibilityReport.create(
        subject_id="SUBJ-A", label="core", required=True, samples=()
    )

    assert report.replays == 0
    assert report.byte_identical is True
    assert report.distinct_digests == ()

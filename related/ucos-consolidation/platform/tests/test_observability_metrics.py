"""EC2-TASK-000179 — Platform metric registry tests."""

from __future__ import annotations

from platform.observability.contracts import MetricKind
from platform.observability.errors import MetricError
from platform.observability.metrics import MetricRegistry, MetricSample

import pytest


def test_counter_accumulates():
    reg = MetricRegistry(mirror_to_ec1=False)
    reg.counter("requests", 1.0, route="/a")
    reg.counter("requests", 2.0, route="/a")
    assert reg.value_of("requests", route="/a") == 3.0


def test_gauge_is_last_writer():
    reg = MetricRegistry(mirror_to_ec1=False)
    reg.gauge("queue_depth", 5)
    reg.gauge("queue_depth", 2)
    assert reg.value_of("queue_depth") == 2.0


def test_histogram_retains_ordered_samples():
    reg = MetricRegistry(mirror_to_ec1=False)
    reg.histogram("latency", 10.0)
    reg.histogram("latency", 20.0)
    assert reg.value_of("latency") == 30.0
    assert reg.total_count() == 2


def test_counter_rejects_negative():
    reg = MetricRegistry(mirror_to_ec1=False)
    with pytest.raises(MetricError):
        reg.counter("x", -1.0)


def test_metric_kind_conflict_is_fail_closed():
    reg = MetricRegistry(mirror_to_ec1=False)
    reg.counter("m", 1.0)
    with pytest.raises(MetricError):
        reg.gauge("m", 1.0)


def test_value_of_unknown_raises():
    reg = MetricRegistry(mirror_to_ec1=False)
    with pytest.raises(MetricError):
        reg.value_of("missing")


def test_snapshot_and_fingerprint_are_deterministic():
    a = MetricRegistry(mirror_to_ec1=False)
    b = MetricRegistry(mirror_to_ec1=False)
    for reg in (a, b):
        reg.counter("c", 1.0, k="v")
        reg.gauge("g", 3.0)
        reg.histogram("h", 7.0)
    assert a.snapshot() == b.snapshot()
    assert a.fingerprint() == b.fingerprint()


def test_snapshot_is_label_order_independent():
    a = MetricRegistry(mirror_to_ec1=False)
    b = MetricRegistry(mirror_to_ec1=False)
    a.counter("c", 1.0, x="1", y="2")
    b.counter("c", 1.0, y="2", x="1")
    assert a.fingerprint() == b.fingerprint()


def test_metric_sample_is_content_addressed():
    s1 = MetricSample.create("m", MetricKind.COUNTER, 1.0, labels={"a": "b"})
    s2 = MetricSample.create("m", MetricKind.COUNTER, 99.0, labels={"a": "b"})
    # sample_id identifies the series (name+kind+labels), not the value.
    assert s1.sample_id == s2.sample_id
    assert s1.sample_id.startswith("UCOS-MTRC-")


def test_metric_sample_rejects_bad_input():
    with pytest.raises(MetricError):
        MetricSample.create("", MetricKind.COUNTER, 1.0)


def test_mirror_to_ec1_is_reused_additively():
    from engine.foundation.obs import telemetry

    telemetry.reset_metrics()
    reg = MetricRegistry(mirror_to_ec1=True)
    reg.counter("mirrored", 1.0)
    snap = telemetry.metrics_snapshot()
    assert any("mirrored" == name for name in snap["counters"])
    telemetry.reset_metrics()


def test_a_sample_refuses_a_kind_that_is_not_a_metric_kind():
    """A KIND IS AN ENUM MEMBER, NEVER THE STRING THAT SPELLS ONE.

    Every registry path passes a real ``MetricKind``, so the guard on the sample constructor
    had no case — and it is the one place a sample built by hand or rehydrated from a
    document arrives. A raw string would enter the content-addressed ``sample_id`` and
    compare unequal to the same sample built through the registry, so two records of the same
    measurement would carry two identities.
    """
    good = MetricSample.create("test.metric", MetricKind.COUNTER, 1.0)
    assert good.kind is MetricKind.COUNTER

    with pytest.raises(MetricError, match="must be a MetricKind"):
        MetricSample.create("test.metric", "counter", 1.0)  # type: ignore[arg-type]


def test_a_series_may_not_change_kind_under_the_same_name_and_labels():
    """ONE NAME AND ONE LABEL SET IS ONE SERIES, AND ITS KIND IS PART OF WHAT IT IS.

    The gauge refusal was tested; the counter's and the histogram's were not, so two of the
    three ways to collide had never been shown to refuse. Allowing the change would silently
    reinterpret every value already recorded: a counter's monotonic total read as a gauge's
    last value, or a histogram's samples discarded because the new kind has none.
    """
    registry = MetricRegistry()
    registry.gauge("test.conflict", 5.0)

    with pytest.raises(MetricError, match="metric kind conflict"):
        registry.counter("test.conflict")
    with pytest.raises(MetricError, match="metric kind conflict"):
        registry.histogram("test.conflict", 1.0)

    # the original series is untouched by either refusal
    assert registry.value_of("test.conflict") == 5.0


def test_the_registry_counts_its_series_and_every_observation_in_them():
    """TWO DIFFERENT COUNTS, AND THE NON-HISTOGRAM ARM OF THE SECOND HAD NEVER RUN.

    ``len`` is how many series exist; ``total_count`` is how many observations they hold. A
    histogram holds one observation per sample and every other kind holds exactly one however
    many times it was written — which is why the two numbers differ, and why counting a
    counter as its VALUE rather than as one observation would make a counter incremented a
    thousand times look like a thousand measurements.
    """
    registry = MetricRegistry()
    registry.counter("test.count.counter", 7.0)
    registry.gauge("test.count.gauge", 3.0)
    registry.histogram("test.count.hist", 1.0)
    registry.histogram("test.count.hist", 2.0)

    assert len(registry) == 3
    assert registry.total_count() == 4

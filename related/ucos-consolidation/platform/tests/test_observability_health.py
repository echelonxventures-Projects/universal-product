"""EC2-TASK-000182 — Platform health registry tests (go-live G1)."""

from __future__ import annotations

from platform.observability.contracts import HealthStatus
from platform.observability.errors import HealthError
from platform.observability.health import (
    HealthCheck,
    HealthRegistry,
    HealthReport,
    HealthResult,
)

import pytest


def _registry() -> HealthRegistry:
    reg = HealthRegistry()
    reg.register(HealthCheck("api-gateway", critical=True, description="edge"))
    reg.register(HealthCheck("event-bus", critical=True))
    reg.register(HealthCheck("cache", critical=False))
    return reg


def test_all_healthy_report_is_healthy():
    reg = _registry()
    report = reg.report(
        {
            "api-gateway": HealthStatus.HEALTHY,
            "event-bus": HealthStatus.HEALTHY,
            "cache": HealthStatus.HEALTHY,
        }
    )
    assert report.healthy
    assert report.status is HealthStatus.HEALTHY


def test_missing_critical_result_is_unhealthy_fail_closed():
    reg = _registry()
    report = reg.report({"api-gateway": HealthStatus.HEALTHY})  # event-bus missing (critical)
    assert report.status is HealthStatus.UNHEALTHY


def test_missing_noncritical_result_is_degraded():
    reg = _registry()
    report = reg.report(
        {"api-gateway": HealthStatus.HEALTHY, "event-bus": HealthStatus.HEALTHY}
    )  # cache missing (non-critical)
    assert report.status is HealthStatus.DEGRADED


def test_endpoint_is_live_and_serializable():
    reg = _registry()
    endpoint = reg.endpoint(
        {
            "api-gateway": HealthStatus.HEALTHY,
            "event-bus": HealthStatus.HEALTHY,
            "cache": HealthStatus.HEALTHY,
        }
    )
    assert endpoint["healthy"] is True
    assert endpoint["status"] == "healthy"
    assert len(endpoint["checks"]) == 3
    assert endpoint["report_id"].startswith("UCOS-HRPT-")


def test_duplicate_registration_fail_closed():
    reg = HealthRegistry()
    reg.register(HealthCheck("x"))
    with pytest.raises(HealthError):
        reg.register(HealthCheck("x"))


def test_result_for_unregistered_check_rejected():
    reg = _registry()
    with pytest.raises(HealthError):
        reg.report({"nonexistent": HealthStatus.HEALTHY})


def test_report_is_deterministic_and_order_independent():
    reg = _registry()
    r1 = reg.report(
        {
            "cache": HealthStatus.HEALTHY,
            "api-gateway": HealthStatus.HEALTHY,
            "event-bus": HealthStatus.DEGRADED,
        }
    )
    r2 = reg.report(
        {
            "api-gateway": HealthStatus.HEALTHY,
            "event-bus": HealthStatus.DEGRADED,
            "cache": HealthStatus.HEALTHY,
        }
    )
    assert r1.fingerprint() == r2.fingerprint()


def test_health_result_and_check_validation():
    with pytest.raises(HealthError):
        HealthResult.create("", HealthStatus.HEALTHY)
    with pytest.raises(HealthError):
        HealthResult.create("x", "healthy")  # type: ignore[arg-type]
    with pytest.raises(HealthError):
        HealthCheck("")
    with pytest.raises(HealthError):
        HealthRegistry().register("not-a-check")  # type: ignore[arg-type]


def test_health_report_create_direct():
    report = HealthReport.create(
        (
            HealthResult.create("b", HealthStatus.HEALTHY),
            HealthResult.create("a", HealthStatus.UNHEALTHY),
        )
    )
    assert report.status is HealthStatus.UNHEALTHY
    # results sorted by name
    assert [r.name for r in report.results] == ["a", "b"]


def test_a_result_that_is_not_a_health_status_is_refused():
    """A STATUS IS AN ENUM MEMBER, NEVER THE STRING THAT SPELLS ONE.

    Every caller supplies real ``HealthStatus`` members, so the guard had no case — and it is
    what stands between the report and a status the aggregation cannot compare. ``"healthy"``
    is not ``HealthStatus.HEALTHY``: the report's overall verdict is derived by comparing
    members, so a raw string would be neither healthy nor unhealthy and the endpoint would
    publish a status nothing in the system can act on.
    """
    registry = HealthRegistry()
    registry.register(HealthCheck("test.check", description="a check"))

    assert registry.report({"test.check": HealthStatus.HEALTHY}).healthy is True

    with pytest.raises(HealthError, match="must be a HealthStatus"):
        registry.report({"test.check": "healthy"})  # type: ignore[dict-item]


def test_the_registry_serialises_the_checks_it_holds():
    """THE REGISTRATION IS EVIDENCE AND HAD NO READER.

    ``endpoint`` publishes the RESULTS; this publishes what is registered to be checked at
    all — the names, their descriptions and which of them are critical. Without it an
    evidence bundle records health verdicts with no record of what was in scope to be
    verdicted, so a check that was silently never registered is indistinguishable from one
    that passed.
    """
    registry = HealthRegistry()
    registry.register(HealthCheck("test.critical", description="must hold", critical=True))
    registry.register(HealthCheck("test.advisory", description="informational", critical=False))

    rendered = registry.to_dict()

    assert rendered["check_count"] == 2
    assert [c["name"] for c in rendered["checks"]] == ["test.advisory", "test.critical"]
    assert [c["critical"] for c in rendered["checks"]] == [False, True]

"""EC2-TASK-000183 — Platform alert engine tests (go-live G8 / acceptance P9)."""

from __future__ import annotations

from platform.observability.alerting import Alert, AlertEngine, AlertRule
from platform.observability.contracts import Severity
from platform.observability.errors import AlertError

import pytest


def test_alert_fires_on_defined_condition():
    engine = AlertEngine()
    engine.register(
        AlertRule("high-error-rate", lambda o: o.get("error_rate", 0) > 0.1, Severity.ERROR)
    )
    fired = engine.evaluate({"error_rate": 0.5})
    assert len(fired) == 1
    assert fired[0].rule_name == "high-error-rate"
    assert fired[0].severity is Severity.ERROR
    assert fired[0].alert_id.startswith("UCOS-ALRT-")


def test_alert_does_not_fire_when_condition_unmet():
    engine = AlertEngine()
    engine.register(AlertRule("r", lambda o: o.get("v", 0) > 10, Severity.WARNING))
    fired = engine.evaluate({"v": 1})
    assert fired == ()
    assert engine.fired == ()


def test_fired_log_is_append_only_and_ordered():
    engine = AlertEngine()
    engine.register(AlertRule("a", lambda o: True, Severity.WARNING))
    engine.register(AlertRule("b", lambda o: True, Severity.CRITICAL))
    engine.evaluate({})
    engine.evaluate({})
    assert [a.sequence for a in engine.fired] == [0, 1, 2, 3]


def test_rules_evaluated_in_deterministic_order():
    engine = AlertEngine()
    engine.register(AlertRule("zeta", lambda o: True, Severity.INFO))
    engine.register(AlertRule("alpha", lambda o: True, Severity.INFO))
    fired = engine.evaluate({})
    assert [a.rule_name for a in fired] == ["alpha", "zeta"]


def test_fired_at_least_threshold():
    engine = AlertEngine()
    engine.register(AlertRule("warn", lambda o: True, Severity.WARNING))
    engine.register(AlertRule("crit", lambda o: True, Severity.CRITICAL))
    engine.evaluate({})
    assert len(engine.fired_at_least(Severity.ERROR)) == 1


def test_duplicate_rule_fail_closed():
    engine = AlertEngine()
    engine.register(AlertRule("r", lambda o: True, Severity.INFO))
    with pytest.raises(AlertError):
        engine.register(AlertRule("r", lambda o: True, Severity.INFO))


def test_faulty_predicate_fails_closed():
    def boom(_o):
        raise RuntimeError("bad")

    engine = AlertEngine()
    engine.register(AlertRule("bad", boom, Severity.ERROR))
    with pytest.raises(AlertError):
        engine.evaluate({})


def test_rule_validation():
    with pytest.raises(AlertError):
        AlertRule("", lambda o: True, Severity.INFO)
    with pytest.raises(AlertError):
        AlertRule("r", "not-callable", Severity.INFO)  # type: ignore[arg-type]
    with pytest.raises(AlertError):
        AlertRule("r", lambda o: True, "info")  # type: ignore[arg-type]
    with pytest.raises(AlertError):
        AlertEngine().register("not-a-rule")  # type: ignore[arg-type]


def test_engine_fingerprint_and_alert_content_address():
    engine = AlertEngine()
    engine.register(AlertRule("r", lambda o: True, Severity.INFO))
    engine.evaluate({"k": "v"})
    a1 = Alert.create("r", Severity.INFO, 0, {"k": "v"})
    a2 = Alert.create("r", Severity.INFO, 0, {"k": "v"})
    assert a1.alert_id == a2.alert_id
    assert engine.to_dict()["fired_count"] == 1
    assert isinstance(engine.fingerprint(), str)


def test_the_engine_reports_which_rules_it_holds_and_how_many():
    """A RULE SET NOBODY CAN INSPECT IS A RULE SET NOBODY CAN AUDIT.

    Every test here evaluates rules and reads the alerts they produced, so the two readers
    that answer "is this rule registered" and "how many are" had no caller — and those are
    what a bootstrap checks before registering, and what evidence records as the alerting
    surface that was actually in force when a verdict was taken.
    """
    engine = AlertEngine()
    assert len(engine) == 0
    assert "test.rule" not in engine

    engine.register(AlertRule("test.rule", lambda o: o.get("v", 0) > 1, Severity.WARNING))

    assert "test.rule" in engine
    assert "test.absent" not in engine
    assert len(engine) == 1

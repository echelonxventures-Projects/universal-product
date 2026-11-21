"""EC2-TASK-000183 — Platform Alerting (EC2-EPIC-013).

A deterministic, fail-closed alert engine that fires alerts on **defined conditions**
(go-live condition G8 "alerts fire on defined conditions / under induced fault";
acceptance P9). Alert rules are pure predicates over an observation mapping (e.g. a
metric snapshot value or a health status), so evaluation is reproducible and depends
on no wall-clock and no external state.

Design (G8/P9 alerting; IMP-007 §5 determinism):
    * :class:`AlertRule` is an immutable named rule: a predicate over an observation
      mapping plus the :class:`~platform.observability.contracts.Severity` it raises.
    * :class:`Alert` is an immutable, content-addressed firing record (rule + the
      observed value that tripped it + a monotonic ``sequence``).
    * :class:`AlertEngine` evaluates all registered rules against an observation in
      deterministic (rule-name) order and appends fired alerts to an append-only log.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.observability.contracts import Severity
from platform.observability.errors import AlertError
from typing import Any

#: A predicate over an observation mapping; True means the alert condition is met.
AlertPredicate = Callable[[Mapping[str, Any]], bool]


@dataclass(frozen=True, slots=True)
class AlertRule:
    """An immutable named alert rule: a predicate + the severity it raises."""

    name: str
    predicate: AlertPredicate
    severity: Severity
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise AlertError("alert rule name is required")
        if not callable(self.predicate):
            raise AlertError("alert rule predicate must be callable", name=self.name)
        if not isinstance(self.severity, Severity):
            raise AlertError("alert rule severity must be a Severity", name=self.name)

    def evaluate(self, observation: Mapping[str, Any]) -> bool:
        """Return True iff the rule's condition is met for ``observation`` (fail-closed)."""
        try:
            return bool(self.predicate(observation))
        except Exception as exc:  # noqa: BLE001 — a faulty predicate must fail closed
            raise AlertError("alert predicate raised", name=self.name, detail=str(exc)) from exc


@dataclass(frozen=True, slots=True)
class Alert:
    """An immutable, content-addressed record of a fired alert."""

    rule_name: str
    severity: Severity
    sequence: int
    observation: Mapping[str, Any]
    alert_id: str = ""

    @classmethod
    def create(
        cls,
        rule_name: str,
        severity: Severity,
        sequence: int,
        observation: Mapping[str, Any],
    ) -> Alert:
        core = {
            "rule_name": rule_name,
            "severity": severity.value,
            "sequence": sequence,
            "observation": dict(observation),
        }
        return cls(
            rule_name=rule_name,
            severity=severity,
            sequence=sequence,
            observation=dict(observation),
            alert_id=f"UCOS-ALRT-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "sequence": self.sequence,
            "observation": dict(self.observation),
        }


class AlertEngine:
    """A deterministic, fail-closed alert engine with an append-only fired-alert log."""

    __slots__ = ("_rules", "_fired")

    def __init__(self) -> None:
        self._rules: dict[str, AlertRule] = {}
        self._fired: list[Alert] = []

    def register(self, rule: AlertRule) -> AlertRule:
        """Register an alert rule (fail-closed on duplicate)."""
        if not isinstance(rule, AlertRule):
            raise AlertError("register requires an AlertRule")
        if rule.name in self._rules:
            raise AlertError("alert rule already registered", name=rule.name)
        self._rules[rule.name] = rule
        return rule

    def __contains__(self, name: str) -> bool:
        return name in self._rules

    def __len__(self) -> int:
        return len(self._rules)

    @property
    def rule_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._rules))

    def evaluate(self, observation: Mapping[str, Any]) -> tuple[Alert, ...]:
        """Evaluate all rules in deterministic order; append + return fired alerts."""
        fired: list[Alert] = []
        for name in self.rule_names:
            rule = self._rules[name]
            if rule.evaluate(observation):
                alert = Alert.create(name, rule.severity, len(self._fired), observation)
                self._fired.append(alert)
                fired.append(alert)
        return tuple(fired)

    @property
    def fired(self) -> tuple[Alert, ...]:
        """An immutable snapshot of the append-only fired-alert log (in order)."""
        return tuple(self._fired)

    def fired_at_least(self, severity: Severity) -> tuple[Alert, ...]:
        """Every fired alert at ``severity`` or more severe, in order."""
        return tuple(a for a in self._fired if a.severity.at_least(severity))

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_count": len(self._rules),
            "rules": [
                {"name": r.name, "severity": r.severity.value, "description": r.description}
                for r in (self._rules[n] for n in self.rule_names)
            ],
            "fired_count": len(self._fired),
            "fired": [a.to_dict() for a in self._fired],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["AlertPredicate", "AlertRule", "Alert", "AlertEngine"]

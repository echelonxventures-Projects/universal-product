"""UCXI-000001 Part 11 — Context Validation: measuring the context set against its rules.

Validation is the surveying counterpart to the constitution's judgment: where a law
either holds or is breached, validation walks *every* rule over *every* context and
returns a complete, ordered report rather than stopping at the first problem. That is
what makes it usable in CI (one run tells you everything wrong) and in certification
(the certifier consumes a report, not a stack trace).

Twelve rules across five dimensions (classification, structure, identity, relation,
history) are declared as DATA, each bound to an executable check. Two properties are
enforced on the rule set itself at construction:

    * every declared rule has a check — an unenforced rule is not a rule;
    * every check belongs to a declared rule — a hidden check is unauditable.

Rules that measure *coverage* rather than correctness are marked ``advisory``: they are
reported and counted, and they do not by themselves invalidate a context set, because a
partially populated registry is a legitimate intermediate state. Certification applies
the stricter bar (Part 12).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from engine.context.constitution import CONTEXT_CONSTITUTION, ContextConstitution
from engine.context.errors import ContextValidationError
from engine.context.graph import ContextGraph, build_context_graph
from engine.context.model import seal
from engine.context.registry import ContextRegistry
from engine.context.resolution import resolution_report
from engine.context.taxonomy import ContextLifecycle
from engine.foundation.obs.logging import get_logger

_logger = get_logger("context.validation")

SEVERITY_VIOLATION = "violation"
SEVERITY_ADVISORY = "advisory"

DIMENSION_CLASSIFICATION = "classification"
DIMENSION_STRUCTURE = "structure"
DIMENSION_IDENTITY = "identity"
DIMENSION_RELATION = "relation"
DIMENSION_HISTORY = "history"


@dataclass(frozen=True, slots=True)
class ValidationRule:
    """One declared validation rule."""

    rule_id: str
    dimension: str
    statement: str
    severity: str = SEVERITY_VIOLATION

    def __post_init__(self) -> None:
        if self.severity not in (SEVERITY_VIOLATION, SEVERITY_ADVISORY):
            raise ContextValidationError(
                "unknown rule severity", rule_id=self.rule_id, severity=self.severity
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "dimension": self.dimension,
            "statement": self.statement,
            "severity": self.severity,
        }


@dataclass(frozen=True, slots=True)
class Finding:
    """One rule violation, attributed to the rule that found it."""

    rule_id: str
    dimension: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "dimension": self.dimension,
            "severity": self.severity,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class ContextValidationReport:
    """The complete, deterministic outcome of validating a context set."""

    rules: tuple[ValidationRule, ...]
    findings: tuple[Finding, ...]
    metrics: dict[str, Any] = field(default_factory=dict)
    content_hash: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rules", tuple(sorted(self.rules, key=lambda r: r.rule_id)))
        object.__setattr__(
            self, "findings", tuple(sorted(self.findings, key=lambda f: (f.rule_id, f.detail)))
        )
        if not self.content_hash:
            object.__setattr__(self, "content_hash", seal(self._payload()))

    def _payload(self) -> dict[str, Any]:
        return {
            "rules": [rule.to_dict() for rule in self.rules],
            "findings": [finding.to_dict() for finding in self.findings],
            "metrics": self.metrics,
        }

    @property
    def violations(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity == SEVERITY_VIOLATION)

    @property
    def advisories(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity == SEVERITY_ADVISORY)

    @property
    def is_valid(self) -> bool:
        """True iff no rule of ``violation`` severity produced a finding."""
        return not self.violations

    @property
    def is_clean(self) -> bool:
        """True iff no rule produced any finding at all (violation or advisory)."""
        return not self.findings

    def rules_failed(self) -> tuple[str, ...]:
        return tuple(sorted({finding.rule_id for finding in self.findings}))

    def by_dimension(self) -> dict[str, int]:
        counts = {
            dimension: 0
            for dimension in (
                DIMENSION_CLASSIFICATION,
                DIMENSION_STRUCTURE,
                DIMENSION_IDENTITY,
                DIMENSION_RELATION,
                DIMENSION_HISTORY,
            )
        }
        for finding in self.findings:
            counts[finding.dimension] = counts.get(finding.dimension, 0) + 1
        return counts

    def summary(self) -> dict[str, Any]:
        return {
            "rules": len(self.rules),
            "rules_failed": list(self.rules_failed()),
            "violations": len(self.violations),
            "advisories": len(self.advisories),
            "by_dimension": self.by_dimension(),
            "is_valid": self.is_valid,
            "is_clean": self.is_clean,
            "content_hash": self.content_hash,
            **self.metrics,
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload["is_valid"] = self.is_valid
        payload["is_clean"] = self.is_clean
        payload["content_hash"] = self.content_hash
        return payload


@dataclass(frozen=True, slots=True)
class ValidationSubject:
    """The material a rule is evaluated against."""

    registry: ContextRegistry
    graph: ContextGraph
    composed: Any = None
    constitution: ContextConstitution = CONTEXT_CONSTITUTION


# --------------------------------------------------------------------------- #
# The rules (DATA)                                                             #
# --------------------------------------------------------------------------- #

VALIDATION_RULES: tuple[ValidationRule, ...] = (
    ValidationRule(
        rule_id="CXV-01",
        dimension=DIMENSION_CLASSIFICATION,
        statement="Every registered context is classified by an existing taxon whose kind "
        "matches the context's kind.",
    ),
    ValidationRule(
        rule_id="CXV-02",
        dimension=DIMENSION_STRUCTURE,
        statement="Every registered context conforms to the ontological shape of its kind: "
        "required dimensions present, no undeclared dimension, types honoured.",
    ),
    ValidationRule(
        rule_id="CXV-03",
        dimension=DIMENSION_IDENTITY,
        statement="Every context identity reproduces from its identity tuple.",
    ),
    ValidationRule(
        rule_id="CXV-04",
        dimension=DIMENSION_IDENTITY,
        statement="Every context content seal reproduces from its own payload.",
    ),
    ValidationRule(
        rule_id="CXV-05",
        dimension=DIMENSION_CLASSIFICATION,
        statement="The context set complies with every law of the Context Constitution.",
    ),
    ValidationRule(
        rule_id="CXV-06",
        dimension=DIMENSION_RELATION,
        statement="Every hierarchical relation is acyclic and every graph edge resolves.",
    ),
    ValidationRule(
        rule_id="CXV-07",
        dimension=DIMENSION_RELATION,
        statement="Every relation is admissible between the kinds it connects.",
    ),
    ValidationRule(
        rule_id="CXV-08",
        dimension=DIMENSION_HISTORY,
        statement="Every context is in a legal lifecycle stage, every context is journaled, "
        "and the journal chain is intact.",
    ),
    ValidationRule(
        rule_id="CXV-09",
        dimension=DIMENSION_STRUCTURE,
        statement="Every context is bound to exactly one frame (no unbounded context).",
    ),
    ValidationRule(
        rule_id="CXV-10",
        dimension=DIMENSION_STRUCTURE,
        statement="Every asserted value carries an authority and a source.",
    ),
    ValidationRule(
        rule_id="CXV-11",
        dimension=DIMENSION_CLASSIFICATION,
        statement="Every universal context kind is present and resolvable.",
        severity=SEVERITY_ADVISORY,
    ),
    ValidationRule(
        rule_id="CXV-12",
        dimension=DIMENSION_RELATION,
        statement="No context is orphaned: every registered context participates in the graph.",
        severity=SEVERITY_ADVISORY,
    ),
)


# --------------------------------------------------------------------------- #
# The checks                                                                   #
# --------------------------------------------------------------------------- #


def _rule_classification(subject: ValidationSubject) -> list[str]:
    registry = subject.registry
    out: list[str] = []
    for record in registry.records():
        if not registry.taxonomy.has(record.taxon_id):
            out.append(f"{record.context_id}: taxon {record.taxon_id} is not classified")
            continue
        taxon = registry.taxonomy.taxon(record.taxon_id)
        if taxon.kind != record.kind:
            out.append(
                f"{record.context_id}: taxon {taxon.taxon_id} classifies {taxon.kind!r}, "
                f"context is {record.kind!r}"
            )
    return out


def _rule_shape(subject: ValidationSubject) -> list[str]:
    registry = subject.registry
    out: list[str] = []
    for record in registry.records():
        out.extend(
            registry.ontology.check_values(
                record.kind, record.value_mapping(), at=record.context_id
            )
        )
    return out


def _rule_identity(subject: ValidationSubject) -> list[str]:
    return [
        f"{record.context_id}: identity does not reproduce (expected {record.expected_identity()})"
        for record in subject.registry.records()
        if record.context_id != record.expected_identity()
    ]


def _rule_seal(subject: ValidationSubject) -> list[str]:
    return [
        f"{record.context_id}: content seal does not reproduce"
        for record in subject.registry.records()
        if record.content_hash != record.recomputed_hash()
    ]


def _rule_constitution(subject: ValidationSubject) -> list[str]:
    assessment = subject.constitution.assess(
        subject.registry, graph=subject.graph, composed=subject.composed
    )
    return list(assessment.findings())


def _rule_graph(subject: ValidationSubject) -> list[str]:
    return list(subject.graph.validate())


def _rule_relations(subject: ValidationSubject) -> list[str]:
    registry = subject.registry
    out: list[str] = []
    for edge in registry.relations():
        source = registry.find(edge.source)
        target = registry.find(edge.target)
        if source is None or target is None:
            out.append(f"{edge.edge_id}: endpoint is not registered")
            continue
        out.extend(
            f"{edge.edge_id}: {finding}"
            for finding in registry.ontology.check_relation(edge.relation, source.kind, target.kind)
        )
    return out


def _rule_history(subject: ValidationSubject) -> list[str]:
    registry = subject.registry
    out = list(registry.verify_audit())
    journaled = {entry.subject for entry in registry.audit()}
    for record in registry.records():
        if record.context_id not in journaled:
            out.append(f"{record.context_id}: no journal entry records this context")
    legal = {stage.value for stage in ContextLifecycle}
    for record in registry.records():
        if record.lifecycle.value not in legal:  # pragma: no cover - enum makes this unreachable
            out.append(f"{record.context_id}: lifecycle {record.lifecycle} is not a legal stage")
    return out


def _rule_boundedness(subject: ValidationSubject) -> list[str]:
    out: list[str] = []
    for record in subject.registry.records():
        if not record.boundary:
            out.append(f"{record.context_id}: declares no bounding frame")
    boundaries = subject.registry.bindings()
    for context_id, boundary in sorted(boundaries.items()):
        if not isinstance(boundary, str) or not boundary:
            out.append(f"{context_id}: frame binding is empty")
    return out


def _rule_provenance(subject: ValidationSubject) -> list[str]:
    out: list[str] = []
    for record in subject.registry.records():
        for value in record.values:
            if not value.source:
                out.append(f"{record.context_id}: dimension {value.dimension!r} names no source")
    return out


def _rule_universal_coverage(subject: ValidationSubject) -> list[str]:
    registry = subject.registry
    out: list[str] = []
    for kind, present in sorted(registry.universal_coverage().items()):
        if not present:
            out.append(f"universal kind {kind!r} has no active registered context")
    report = resolution_report(registry)
    for row in report["kinds"]:
        if not row["resolvable"] and registry.universal_coverage().get(row["kind"], False):
            out.append(f"universal kind {row['kind']!r} is registered but not resolvable")
    return out


def _rule_no_orphans(subject: ValidationSubject) -> list[str]:
    graph = subject.graph
    return [f"{node_id}: participates in no relation" for node_id in graph.orphans()]


#: rule id -> the check that measures it.
RULE_CHECKS: dict[str, Callable[[ValidationSubject], list[str]]] = {
    "CXV-01": _rule_classification,
    "CXV-02": _rule_shape,
    "CXV-03": _rule_identity,
    "CXV-04": _rule_seal,
    "CXV-05": _rule_constitution,
    "CXV-06": _rule_graph,
    "CXV-07": _rule_relations,
    "CXV-08": _rule_history,
    "CXV-09": _rule_boundedness,
    "CXV-10": _rule_provenance,
    "CXV-11": _rule_universal_coverage,
    "CXV-12": _rule_no_orphans,
}


class ContextValidator:
    """Runs the declared rule set over a context set.

    Construction refuses an unenforced rule or an undeclared check, so the rule set and
    its implementation cannot drift apart.
    """

    __slots__ = ("_rules", "_checks", "_constitution")

    def __init__(
        self,
        rules: tuple[ValidationRule, ...] = VALIDATION_RULES,
        checks: dict[str, Callable[[ValidationSubject], list[str]]] | None = None,
        *,
        constitution: ContextConstitution = CONTEXT_CONSTITUTION,
    ) -> None:
        resolved = RULE_CHECKS if checks is None else checks
        unenforced = [rule.rule_id for rule in rules if rule.rule_id not in resolved]
        if unenforced:
            raise ContextValidationError(
                "every validation rule must carry an executable check", rules=unenforced
            )
        undeclared = sorted(set(resolved) - {rule.rule_id for rule in rules})
        if undeclared:
            raise ContextValidationError("a check exists for an undeclared rule", checks=undeclared)
        self._rules = tuple(sorted(rules, key=lambda rule: rule.rule_id))
        self._checks = dict(resolved)
        self._constitution = constitution

    def rules(self) -> tuple[ValidationRule, ...]:
        return self._rules

    def validate(
        self,
        registry: ContextRegistry,
        *,
        graph: ContextGraph | None = None,
        composed: Any = None,
    ) -> ContextValidationReport:
        """Run every rule and return the complete report."""
        context_graph = graph if graph is not None else build_context_graph(registry)
        subject = ValidationSubject(
            registry=registry,
            graph=context_graph,
            composed=composed,
            constitution=self._constitution,
        )
        findings: list[Finding] = []
        for rule in self._rules:
            for detail in self._checks[rule.rule_id](subject):
                findings.append(
                    Finding(
                        rule_id=rule.rule_id,
                        dimension=rule.dimension,
                        severity=rule.severity,
                        detail=detail,
                    )
                )
        coverage = registry.universal_coverage()
        report = ContextValidationReport(
            rules=self._rules,
            findings=tuple(findings),
            metrics={
                "contexts": len(registry),
                "relations": len(registry.relations()),
                "kinds_registered": len(registry.kinds()),
                "universal_kinds": len(coverage),
                "universal_covered": sum(1 for present in coverage.values() if present),
                "graph_nodes": context_graph.order(),
                "graph_edges": context_graph.size(),
                "registry_seal": registry.seal(),
                "graph_seal": context_graph.seal(),
            },
        )
        _logger.info(
            "context.validation.completed",
            violations=len(report.violations),
            advisories=len(report.advisories),
        )
        return report

    def require_valid(
        self,
        registry: ContextRegistry,
        *,
        graph: ContextGraph | None = None,
        composed: Any = None,
    ) -> ContextValidationReport:
        """Fail-closed form of :meth:`validate`."""
        report = self.validate(registry, graph=graph, composed=composed)
        if not report.is_valid:
            raise ContextValidationError(
                "the context set is not valid",
                rules=list(report.rules_failed()),
                findings=[finding.detail for finding in report.violations],
            )
        return report


#: The default validator (the twelve declared rules).
VALIDATOR = ContextValidator()


def validate(
    registry: ContextRegistry,
    *,
    graph: ContextGraph | None = None,
    composed: Any = None,
) -> ContextValidationReport:
    """Validate a context set with the default rule set."""
    return VALIDATOR.validate(registry, graph=graph, composed=composed)


__all__ = [
    "SEVERITY_VIOLATION",
    "SEVERITY_ADVISORY",
    "DIMENSION_CLASSIFICATION",
    "DIMENSION_STRUCTURE",
    "DIMENSION_IDENTITY",
    "DIMENSION_RELATION",
    "DIMENSION_HISTORY",
    "ValidationRule",
    "Finding",
    "ContextValidationReport",
    "ValidationSubject",
    "VALIDATION_RULES",
    "RULE_CHECKS",
    "ContextValidator",
    "VALIDATOR",
    "validate",
]

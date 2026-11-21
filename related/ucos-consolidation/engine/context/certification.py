"""UCXI-000001 Part 12 — Context Certification: a computed verdict, never an asserted one.

Certification is the terminal question: *is this context set fit to be relied on?* The
answer is **computed** from eight measured dimensions and is reachable in both
directions — a clean set certifies, a flawed set does not — because a gate with no
reachable pass state carries no evidentiary value, and one with no reachable fail state
carries none either.

The eight dimensions:

    1. Constitution — every law of the Context Constitution holds.
    2. Validation — no rule of violation severity produced a finding.
    3. Universal coverage — all fifteen universal kinds are present and resolvable.
    4. Ontological conformance — every context matches its declared shape.
    5. Identity integrity — every identity and every content seal reproduces.
    6. Graph integrity — hierarchies acyclic, nothing unclassified, no dangling edge.
    7. Isolation — the composition is bounded and every cross-frame reference federated.
    8. Determinism — the registry, graph and composition seals reproduce on recomputation.

The certificate carries the seals of everything it certifies, so a later reader can
re-derive the verdict from the same inputs rather than trusting the certificate. It
carries **no timestamp**: an unchanged context set always produces a byte-identical
certificate, which is the property that makes drift detectable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine.context.composition import ComposedContext, compose
from engine.context.constitution import CONTEXT_CONSTITUTION, ContextConstitution
from engine.context.errors import ContextCertificationError, ContextError
from engine.context.graph import build_context_graph
from engine.context.model import Observer, content_digest, seal
from engine.context.registry import ContextRegistry
from engine.context.resolution import resolution_report
from engine.context.validation import VALIDATOR, ContextValidationReport, ContextValidator
from engine.foundation.obs.logging import get_logger

_logger = get_logger("context.certification")

#: The verdict when every dimension passes.
VERDICT_CERTIFIED = "CERTIFIED-UNIVERSAL"
#: The verdict when any dimension fails.
VERDICT_NOT_CERTIFIED = "NOT-CERTIFIED"

#: The certificate schema version (append-only, semantically versioned).
CERTIFICATE_VERSION = "1.0.0"

#: This layer creates no authority; the certificate says so in its own payload.
AUTHORITY = "NONE (DERIVED TRUTH)"


@dataclass(frozen=True, slots=True)
class CertificationDimension:
    """One measured certification dimension."""

    dimension_id: str
    statement: str
    passed: bool
    detail: str = ""
    measured: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension_id": self.dimension_id,
            "statement": self.statement,
            "passed": self.passed,
            "detail": self.detail,
            "measured": self.measured,
        }


@dataclass(frozen=True, slots=True)
class ContextCertificate:
    """The computed certification of one context set."""

    certificate_id: str
    verdict: str
    dimensions: tuple[CertificationDimension, ...]
    metrics: dict[str, Any] = field(default_factory=dict)
    seals: dict[str, str] = field(default_factory=dict)
    content_hash: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "dimensions", tuple(sorted(self.dimensions, key=lambda d: d.dimension_id))
        )
        if not self.content_hash:
            object.__setattr__(self, "content_hash", seal(self._payload()))

    def _payload(self) -> dict[str, Any]:
        return {
            "certificate_version": CERTIFICATE_VERSION,
            "certificate_id": self.certificate_id,
            "authority": AUTHORITY,
            "verdict": self.verdict,
            "dimensions": [dimension.to_dict() for dimension in self.dimensions],
            "metrics": self.metrics,
            "seals": self.seals,
        }

    @property
    def certified(self) -> bool:
        return self.verdict == VERDICT_CERTIFIED

    @property
    def failed_dimensions(self) -> tuple[str, ...]:
        return tuple(d.dimension_id for d in self.dimensions if not d.passed)

    def dimension(self, dimension_id: str) -> CertificationDimension | None:
        for dimension in self.dimensions:
            if dimension.dimension_id == dimension_id:
                return dimension
        return None

    def summary(self) -> dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "verdict": self.verdict,
            "certified": self.certified,
            "dimensions_passed": sum(1 for d in self.dimensions if d.passed),
            "dimensions_total": len(self.dimensions),
            "failed": list(self.failed_dimensions),
            "content_hash": self.content_hash,
            **self.metrics,
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload["certified"] = self.certified
        payload["content_hash"] = self.content_hash
        return payload


#: The declared dimensions (statement only; the outcome is always measured).
CERTIFICATION_DIMENSIONS: tuple[tuple[str, str], ...] = (
    ("CXC-01", "Every law of the Context Constitution holds."),
    ("CXC-02", "No validation rule of violation severity produced a finding."),
    ("CXC-03", "Every universal context kind is present and resolvable."),
    ("CXC-04", "Every context conforms to the declared ontological shape of its kind."),
    ("CXC-05", "Every context identity and content seal reproduces."),
    ("CXC-06", "The context graph is structurally intact (acyclic, classified, closed)."),
    ("CXC-07", "The composition is bounded and every cross-frame reference is federated."),
    ("CXC-08", "Registry, graph and composition seals reproduce on recomputation."),
)


def _determinism(registry: ContextRegistry, composed: ComposedContext | None) -> tuple[bool, str]:
    """Recompute the seals a second time and compare (a double-build in miniature)."""
    first_registry = registry.seal()
    second_registry = registry.seal()
    graph_first = build_context_graph(registry).seal()
    graph_second = build_context_graph(registry).seal()
    problems: list[str] = []
    if first_registry != second_registry:
        problems.append("registry seal is not stable")
    if graph_first != graph_second:
        problems.append("graph seal is not stable")
    if composed is not None:
        recomposed = compose(
            registry,
            context_ids=composed.members,
            federations=composed.federations,
            observer=composed.observer,
        )
        if recomposed.content_hash != composed.content_hash:
            problems.append("composition seal is not stable")
        if recomposed.composition_id != composed.composition_id:
            problems.append("composition identity is not stable")
    return (not problems), "; ".join(problems)


def certify(
    registry: ContextRegistry,
    *,
    composed: ComposedContext | None = None,
    validator: ContextValidator = VALIDATOR,
    constitution: ContextConstitution = CONTEXT_CONSTITUTION,
    observer: Observer | None = None,
) -> ContextCertificate:
    """Compute the certification of a context set.

    The composition is built if not supplied. A composition that *cannot* be built
    (unbounded member, isolation leak) is not an exception here: it is a failed
    isolation dimension, so the certifier always returns a verdict rather than
    propagating a refusal.
    """
    graph = build_context_graph(registry)
    isolation_detail = ""
    if composed is None:
        try:
            composed = compose(registry, observer=observer)
        except ContextError as exc:
            composed = None
            isolation_detail = str(exc)

    report: ContextValidationReport = validator.validate(registry, graph=graph, composed=composed)
    assessment = constitution.assess(registry, graph=graph, composed=composed)
    resolvability = resolution_report(registry)
    coverage = registry.universal_coverage()
    covered = sum(1 for present in coverage.values() if present)
    shape_findings = [f.detail for f in report.findings if f.rule_id == "CXV-02"]
    identity_findings = [f.detail for f in report.findings if f.rule_id in ("CXV-03", "CXV-04")]
    graph_findings = graph.validate()
    deterministic, determinism_detail = _determinism(registry, composed)

    outcomes = {
        "CXC-01": (
            assessment.compliant,
            "; ".join(law.law_id for law in assessment.violations),
            f"{sum(1 for law in assessment.laws if law.compliant)}/{len(assessment.laws)} laws",
        ),
        "CXC-02": (
            report.is_valid,
            "; ".join(finding.rule_id for finding in report.violations),
            f"{len(report.violations)} violation(s)",
        ),
        "CXC-03": (
            covered == len(coverage) and bool(coverage) and resolvability["all_resolvable"],
            "; ".join(kind for kind, present in sorted(coverage.items()) if not present),
            f"{covered}/{len(coverage)} universal kinds",
        ),
        "CXC-04": (not shape_findings, "; ".join(shape_findings[:3]), f"{len(shape_findings)}"),
        "CXC-05": (
            not identity_findings,
            "; ".join(identity_findings[:3]),
            f"{len(identity_findings)}",
        ),
        "CXC-06": (not graph_findings, "; ".join(graph_findings[:3]), f"{len(graph_findings)}"),
        "CXC-07": (
            composed is not None and composed.is_universally_complete,
            isolation_detail
            or ("" if composed is None else "; ".join(composed.missing_universal())),
            "no composition"
            if composed is None
            else f"{len(composed.members)} members / {len(composed.frames)} frames",
        ),
        "CXC-08": (deterministic, determinism_detail, "double-computed"),
    }

    dimensions = tuple(
        CertificationDimension(
            dimension_id=dimension_id,
            statement=statement,
            passed=outcomes[dimension_id][0],
            detail=outcomes[dimension_id][1],
            measured=outcomes[dimension_id][2],
        )
        for dimension_id, statement in CERTIFICATION_DIMENSIONS
    )
    missing = [
        dimension_id for dimension_id, _ in CERTIFICATION_DIMENSIONS if dimension_id not in outcomes
    ]
    if missing:  # pragma: no cover - guards a future dimension added without a measurement
        raise ContextCertificationError(
            "a certification dimension has no measurement", dimensions=missing
        )

    verdict = (
        VERDICT_CERTIFIED
        if all(dimension.passed for dimension in dimensions)
        else VERDICT_NOT_CERTIFIED
    )
    seals = {
        "registry": registry.seal(),
        "graph": graph.seal(),
        "validation": report.content_hash,
        "constitution": assessment.content_hash,
        "composition": composed.content_hash if composed else "",
    }
    certificate = ContextCertificate(
        certificate_id="UCOS-CTXCERT-" + content_digest(seals)[:12],
        verdict=verdict,
        dimensions=dimensions,
        metrics={
            "contexts": len(registry),
            "relations": len(registry.relations()),
            "kinds_registered": len(registry.kinds()),
            "universal_kinds": len(coverage),
            "universal_covered": covered,
            "future_kinds": len(registry.taxonomy.future_kinds()),
            "laws": len(assessment.laws),
            "rules": len(report.rules),
            "violations": len(report.violations),
            "advisories": len(report.advisories),
            "graph_nodes": graph.order(),
            "graph_edges": graph.size(),
            "audit_entries": len(registry.audit()),
        },
        seals=seals,
    )
    _logger.info(
        "context.certification.computed",
        verdict=verdict,
        certificate_id=certificate.certificate_id,
        failed=len(certificate.failed_dimensions),
    )
    return certificate


def require_certified(registry: ContextRegistry, **kwargs: Any) -> ContextCertificate:
    """Fail-closed form of :func:`certify`."""
    certificate = certify(registry, **kwargs)
    if not certificate.certified:
        raise ContextCertificationError(
            "the context set is not certified",
            verdict=certificate.verdict,
            failed=list(certificate.failed_dimensions),
        )
    return certificate


__all__ = [
    "VERDICT_CERTIFIED",
    "VERDICT_NOT_CERTIFIED",
    "CERTIFICATE_VERSION",
    "AUTHORITY",
    "CERTIFICATION_DIMENSIONS",
    "CertificationDimension",
    "ContextCertificate",
    "certify",
    "require_certified",
]

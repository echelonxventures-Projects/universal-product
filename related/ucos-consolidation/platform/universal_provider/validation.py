"""UPA-000008 — Provider Validation (Terminal-04).

The Provider Constitution is executable. This module carries **one gate per
constitutional article** — fourteen articles, fourteen gates — so a provider's
conformance is a measured result rather than an assurance.

    * :class:`GateStatus` / :class:`GateSeverity` — gate outcome and blocking weight.
    * :class:`ValidationSubject` — everything a gate may inspect.
    * :class:`GateResult` / :class:`ValidationReport` — content-addressed outcomes.
    * :class:`ProviderGate` — the gate protocol.
    * :func:`default_gates` — the fourteen constitutional gates, in article order.
    * :class:`ProviderValidator` — executes gates, isolating each one.

Three outcomes, deliberately: ``PASS``, ``FAIL``, and ``INDETERMINATE``. The third is
what keeps the framework honest. A provider declared in a catalog but not yet
implemented cannot demonstrate interface completeness, so the gate that measures it
returns ``INDETERMINATE`` and the report is ``INCOMPLETE`` — never ``PASSED``, and
never misreported as ``FAILED``. Absence of evidence is not evidence of correctness,
and it is not evidence of defect either.

Gates never trust a declaration they can measure instead. Interface completeness is
proven by introspecting the live object; determinism by executing a query twice and
comparing content hashes; fail-closed behaviour by attempting a refused call;
provider-agnosticism by scanning the framework's own source for the provider's
identity.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from platform.universal_provider.constitution import (
    PROVIDER_CONSTITUTION_ID,
    PROVIDER_CONSTITUTION_VERSION,
    PROVIDER_INTERFACE,
    SUBSTRATE_OPERATIONS,
    ProviderOperation,
    article,
    normalize_kind,
)
from platform.universal_provider.contracts import (
    ProviderDescriptor,
    ProviderHealth,
    ProviderQuery,
    ProviderResource,
    ProviderResponse,
    content_hash,
    provider_operations,
)
from platform.universal_provider.errors import (
    ProviderFrameworkError,
    ProviderValidationError,
)
from platform.universal_provider.lifecycle import (
    LIFECYCLE_TRANSITIONS,
    ProviderLifecycle,
    ProviderPhase,
)
from platform.universal_provider.registry import ProviderRegistry
from typing import Any

#: Semantic version of the Provider Validation contract surface.
PROVIDER_VALIDATION_VERSION = "1.0.0"

#: Effect actions that cannot honestly coexist with a determinism declaration.
MUTATING_EFFECT_ACTIONS: frozenset[str] = frozenset(
    {"write", "delete", "create", "update", "exec", "send", "publish", "mutate"}
)


class GateStatus(str, Enum):
    """The outcome of one gate."""

    PASS = "pass"  # noqa: S105 - a gate verdict, not a credential
    FAIL = "fail"
    INDETERMINATE = "indeterminate"


class GateSeverity(str, Enum):
    """Whether a failing gate blocks certification."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class ValidationStatus(str, Enum):
    """The aggregate verdict over all gates."""

    PASSED = "passed"
    INCOMPLETE = "incomplete"
    FAILED = "failed"


def framework_source_files(root: Path | None = None) -> tuple[Path, ...]:
    """Return the Provider Framework's own source files, sorted.

    Used by gate ``PV-02-KIND-OPEN`` to prove mechanically that the framework holds
    no provider-specific code.
    """
    base = root or Path(__file__).resolve().parent
    return tuple(sorted(path for path in base.glob("*.py") if path.name != "__init__.py"))


@dataclass(frozen=True, slots=True)
class ValidationSubject:
    """Everything a gate is permitted to inspect.

    ``instance`` is optional on purpose: a provider that has been declared but not yet
    implemented is a valid subject, and the gates that require a live object report
    ``INDETERMINATE`` rather than pretending.
    """

    descriptor: ProviderDescriptor
    instance: Any | None = None
    registry: ProviderRegistry | None = None
    lifecycle: ProviderLifecycle | None = None
    framework_root: Path | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.descriptor, ProviderDescriptor):
            raise ProviderValidationError(
                "a validation subject requires a ProviderDescriptor",
                {"received": type(self.descriptor).__name__},
            )

    @property
    def qualified_id(self) -> str:
        return self.descriptor.qualified_id


@dataclass(frozen=True, slots=True)
class GateResult:
    """The immutable outcome of one constitutional gate."""

    gate_id: str
    article_id: str
    status: GateStatus
    severity: GateSeverity
    summary: str
    findings: tuple[str, ...] = ()
    evidence: dict[str, Any] = field(default_factory=dict)

    @property
    def blocking_failure(self) -> bool:
        return self.status is GateStatus.FAIL and self.severity is GateSeverity.BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "article_id": self.article_id,
            "status": self.status.value,
            "severity": self.severity.value,
            "summary": self.summary,
            "findings": list(self.findings),
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The content-addressed outcome of a validation pass over one provider."""

    qualified_id: str
    descriptor_hash: str
    constitution_id: str
    constitution_version: str
    results: tuple[GateResult, ...] = ()

    @property
    def status(self) -> ValidationStatus:
        """Aggregate verdict: FAILED beats INCOMPLETE beats PASSED."""
        if any(result.blocking_failure for result in self.results):
            return ValidationStatus.FAILED
        if any(result.status is GateStatus.INDETERMINATE for result in self.results):
            return ValidationStatus.INCOMPLETE
        return ValidationStatus.PASSED

    @property
    def passed(self) -> bool:
        return self.status is ValidationStatus.PASSED

    def counts(self) -> dict[str, int]:
        return {
            "total": len(self.results),
            "pass": sum(1 for r in self.results if r.status is GateStatus.PASS),
            "fail": sum(1 for r in self.results if r.status is GateStatus.FAIL),
            "indeterminate": sum(1 for r in self.results if r.status is GateStatus.INDETERMINATE),
            "blocking_failures": sum(1 for r in self.results if r.blocking_failure),
        }

    def result(self, gate_id: str) -> GateResult:
        for candidate in self.results:
            if candidate.gate_id == gate_id:
                return candidate
        raise ProviderValidationError(
            "gate was not executed in this validation pass",
            {"gate_id": gate_id, "executed": [r.gate_id for r in self.results]},
        )

    def failures(self) -> tuple[GateResult, ...]:
        return tuple(r for r in self.results if r.status is GateStatus.FAIL)

    def indeterminate(self) -> tuple[GateResult, ...]:
        return tuple(r for r in self.results if r.status is GateStatus.INDETERMINATE)

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_version": PROVIDER_VALIDATION_VERSION,
            "qualified_id": self.qualified_id,
            "descriptor_hash": self.descriptor_hash,
            "constitution_id": self.constitution_id,
            "constitution_version": self.constitution_version,
            "status": self.status.value,
            "counts": self.counts(),
            "results": [result.to_dict() for result in self.results],
        }

    def report_hash(self) -> str:
        return content_hash(self.to_dict())


class ProviderGate(ABC):
    """One executable constitutional gate.

    ``article_id`` binds the gate to the article it proves; the gate id is read from
    the article itself, so a gate can never drift from the law it enforces.
    """

    article_id: str = ""
    severity: GateSeverity = GateSeverity.BLOCKING

    @property
    def gate_id(self) -> str:
        return article(self.article_id).gate

    @abstractmethod
    def evaluate(self, subject: ValidationSubject) -> GateResult:
        """Return this gate's outcome for ``subject``."""

    # ------------------------------------------------------------------- outcome API

    def _result(
        self,
        status: GateStatus,
        summary: str,
        findings: Sequence[str] = (),
        evidence: Mapping[str, Any] | None = None,
    ) -> GateResult:
        return GateResult(
            gate_id=self.gate_id,
            article_id=self.article_id,
            status=status,
            severity=self.severity,
            summary=summary,
            findings=tuple(findings),
            evidence=dict(evidence or {}),
        )

    def _pass(self, summary: str, evidence: Mapping[str, Any] | None = None) -> GateResult:
        return self._result(GateStatus.PASS, summary, (), evidence)

    def _fail(
        self,
        summary: str,
        findings: Sequence[str],
        evidence: Mapping[str, Any] | None = None,
    ) -> GateResult:
        return self._result(GateStatus.FAIL, summary, findings, evidence)

    def _indeterminate(
        self, summary: str, findings: Sequence[str] = (), evidence: Mapping[str, Any] | None = None
    ) -> GateResult:
        return self._result(GateStatus.INDETERMINATE, summary, findings, evidence)


class InterfaceCompleteGate(ProviderGate):
    """PC-01 — the live object implements exactly the constitutional surface."""

    article_id = "PC-01"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        descriptor = subject.descriptor
        findings: list[str] = []
        if descriptor.interface != PROVIDER_INTERFACE:
            findings.append(
                f"descriptor declares interface {descriptor.interface!r}, "
                f"not {PROVIDER_INTERFACE!r}"
            )
        if subject.instance is None:
            return self._indeterminate(
                "no live provider instance was supplied; interface completeness is unmeasured",
                findings or ("instance absent",),
                {"declared_interface": descriptor.interface},
            )
        implemented = provider_operations(subject.instance)
        expected = tuple(sorted(op.value for op in ProviderOperation))
        missing = tuple(op for op in expected if op not in implemented)
        if missing:
            findings.append(f"operations not implemented: {list(missing)}")
        if findings:
            return self._fail(
                "provider does not implement the one constitutional interface",
                findings,
                {"implemented": list(implemented), "expected": list(expected)},
            )
        return self._pass(
            "provider implements exactly the six constitutional operations",
            {"implemented": list(implemented)},
        )


class KindOpenGate(ProviderGate):
    """PC-02 — the framework holds no code specific to this provider.

    Proven mechanically: the provider's own identity must not appear as a string
    literal in any Provider Framework source file. If it does, the framework has been
    taught about a particular provider and the architecture is no longer universal.
    """

    article_id = "PC-02"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        descriptor = subject.descriptor
        findings: list[str] = []
        try:
            normalize_kind(descriptor.kind)
        except ProviderFrameworkError as exc:
            findings.append(f"kind is malformed: {exc.message}")
        provider_id = descriptor.provider_id
        needles = (f'"{provider_id}"', f"'{provider_id}'")
        offenders: list[str] = []
        scanned = 0
        for path in framework_source_files(subject.framework_root):
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:  # pragma: no cover - unreadable framework source
                findings.append(f"framework source {path.name} unreadable: {exc}")
                continue
            if any(needle in text for needle in needles):
                offenders.append(path.name)
        if offenders:
            findings.append(
                f"provider id appears as a literal in framework source: {sorted(offenders)}"
            )
        if findings:
            return self._fail(
                "provider is privileged by the framework; the kind vocabulary is not open",
                findings,
                {"scanned_files": scanned, "offenders": sorted(offenders)},
            )
        return self._pass(
            "provider kind is open data and the framework contains no reference to this provider",
            {"scanned_files": scanned, "kind": descriptor.kind},
        )


class IdentityDeclaredGate(ProviderGate):
    """PC-03 — identity is complete, and the descriptor hash is stable."""

    article_id = "PC-03"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        descriptor = subject.descriptor
        identity = descriptor.identity
        findings: list[str] = []
        if not identity.name.strip():
            findings.append("identity declares no name")
        if not identity.authority.strip():
            findings.append("identity declares no authority")
        if not descriptor.source_of_record.strip():
            findings.append("descriptor declares no source of record")
        first = descriptor.content_hash()
        second = descriptor.content_hash()
        if first != second:
            findings.append("descriptor content hash is not stable across computations")
        if findings:
            return self._fail(
                "provider identity is incompletely declared",
                findings,
                {"descriptor_hash": first},
            )
        return self._pass(
            "provider identity is complete and content-addressed",
            {
                "descriptor_hash": first,
                "qualified_id": descriptor.qualified_id,
                "authority": identity.authority,
            },
        )


class CapabilitiesDeclaredGate(ProviderGate):
    """PC-04 — every substrate operation is backed by a declared capability."""

    article_id = "PC-04"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        descriptor = subject.descriptor
        findings: list[str] = []
        for operation in SUBSTRATE_OPERATIONS:
            if not descriptor.capabilities_for(operation):
                findings.append(
                    f"no capability declared for substrate operation {operation.value!r}"
                )
        for capability in descriptor.capabilities:
            if capability.operation is ProviderOperation.QUERY and not capability.resource_kind:
                findings.append(f"query capability {capability.name!r} declares no resource kind")
            if capability.operation is ProviderOperation.QUERY and not capability.selector_keys:
                findings.append(f"query capability {capability.name!r} declares no selector keys")
        if findings:
            return self._fail(
                "capability declaration is incomplete; undeclared surface would be invocable",
                findings,
                {"declared": [c.name for c in descriptor.capabilities]},
            )
        return self._pass(
            "every substrate operation is backed by a declared capability",
            {
                "capabilities": [c.name for c in descriptor.capabilities],
                "by_operation": {
                    operation.value: [c.name for c in descriptor.capabilities_for(operation)]
                    for operation in SUBSTRATE_OPERATIONS
                },
            },
        )


class DeterminismGate(ProviderGate):
    """PC-05 — determinism is declared, and where measurable, demonstrated.

    Every deterministic query capability that needs no required selector is executed
    twice; the two responses must have identical content hashes.
    """

    article_id = "PC-05"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        descriptor = subject.descriptor
        deterministic = tuple(c for c in descriptor.capabilities if c.deterministic)
        if not deterministic:
            return self._fail(
                "provider declares no deterministic capability",
                ("at least one capability must be reproducible",),
                {"capabilities": [c.name for c in descriptor.capabilities]},
            )
        if subject.instance is None:
            return self._indeterminate(
                "determinism is declared but unmeasured without a live instance",
                ("instance absent",),
                {"deterministic": [c.name for c in deterministic]},
            )
        findings: list[str] = []
        measured: dict[str, str] = {}
        for capability in deterministic:
            if capability.operation is not ProviderOperation.QUERY:
                continue
            if capability.required_selector_keys:
                continue
            request = ProviderQuery(capability=capability.name)
            try:
                first = subject.instance.query(request)
                second = subject.instance.query(request)
            except ProviderFrameworkError as exc:
                findings.append(f"{capability.name}: query refused ({exc.code})")
                continue
            if not isinstance(first, ProviderResponse) or not isinstance(second, ProviderResponse):
                findings.append(f"{capability.name}: query did not return a ProviderResponse")
                continue
            if first.response_hash != second.response_hash:
                findings.append(f"{capability.name}: repeated query produced a different result")
                continue
            measured[capability.name] = first.response_hash
        if findings:
            return self._fail(
                "a capability declared deterministic is not reproducible",
                findings,
                {"measured": measured},
            )
        if not measured:
            return self._indeterminate(
                "determinism is declared but no capability was executable without a selector",
                ("no unconditionally executable deterministic query capability",),
                {"deterministic": [c.name for c in deterministic]},
            )
        return self._pass(
            "every measurable deterministic capability reproduced byte-identical results",
            {"measured": measured},
        )


class ProvenanceGate(ProviderGate):
    """PC-06 — declared source of record, and provenance on every returned resource."""

    article_id = "PC-06"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        descriptor = subject.descriptor
        findings: list[str] = []
        if not descriptor.source_of_record.strip():
            findings.append("descriptor declares no source of record")
        if subject.instance is None:
            if findings:
                return self._fail(
                    "provenance is not declared", findings, {"provider_id": descriptor.provider_id}
                )
            return self._indeterminate(
                "provenance is declared but unmeasured without a live instance",
                ("instance absent",),
                {"source_of_record": descriptor.source_of_record},
            )
        sampled = 0
        attested = 0
        for capability in descriptor.capabilities_for(ProviderOperation.QUERY):
            if capability.required_selector_keys:
                continue
            try:
                response = subject.instance.query(ProviderQuery(capability=capability.name))
            except ProviderFrameworkError as exc:
                findings.append(f"{capability.name}: query refused ({exc.code})")
                continue
            for resource in response.resources:
                sampled += 1
                if not isinstance(resource, ProviderResource):
                    findings.append(f"{capability.name}: non-resource value returned")
                    continue
                source = str(resource.provenance.get("source_of_record") or "").strip()
                if not source:
                    findings.append(f"{resource.resource_id}: no source of record")
                    continue
                if not resource.resource_hash:
                    findings.append(f"{resource.resource_id}: no content hash")
                    continue
                attestation = subject.instance.verify(resource.resource_id)
                if not attestation.verified:
                    findings.append(
                        f"{resource.resource_id}: attestation unverified "
                        f"({list(attestation.reasons)})"
                    )
                    continue
                attested += 1
        if findings:
            return self._fail(
                "provider output is not fully attributable",
                findings,
                {"sampled": sampled, "attested": attested},
            )
        return self._pass(
            "declared source of record, and every sampled resource is attested",
            {
                "source_of_record": descriptor.source_of_record,
                "sampled": sampled,
                "attested": attested,
            },
        )


class FailClosedGate(ProviderGate):
    """PC-07 — undeclared and absent inputs are refused, not defaulted."""

    article_id = "PC-07"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        if subject.instance is None:
            return self._indeterminate(
                "fail-closed behaviour is unmeasured without a live instance",
                ("instance absent",),
            )
        instance = subject.instance
        descriptor = subject.descriptor
        findings: list[str] = []
        probes: dict[str, str] = {}

        undeclared_capability = "gate.probe.undeclared.capability"
        try:
            instance.query(ProviderQuery(capability=undeclared_capability))
            findings.append("an undeclared capability was served instead of refused")
        except ProviderFrameworkError as exc:
            probes["undeclared_capability"] = exc.code
        except Exception as exc:  # noqa: BLE001 - an untyped escape is itself a finding
            findings.append(f"undeclared capability raised untyped {type(exc).__name__}")

        query_capabilities = descriptor.capabilities_for(ProviderOperation.QUERY)
        if query_capabilities:
            capability = query_capabilities[0]
            try:
                instance.query(
                    ProviderQuery(
                        capability=capability.name,
                        selector={"gate.probe.undeclared.selector": True},
                    )
                )
                findings.append("an undeclared selector key was accepted instead of refused")
            except ProviderFrameworkError as exc:
                probes["undeclared_selector"] = exc.code
            except Exception as exc:  # noqa: BLE001
                findings.append(f"undeclared selector raised untyped {type(exc).__name__}")
        else:
            findings.append("no query capability available to probe selector admission")

        try:
            instance.fetch("gate.probe.absent.resource")
            findings.append("an absent resource was fabricated instead of refused")
        except ProviderFrameworkError as exc:
            probes["absent_resource"] = exc.code
        except Exception as exc:  # noqa: BLE001
            findings.append(f"absent resource raised untyped {type(exc).__name__}")

        if findings:
            return self._fail("provider does not fail closed", findings, {"probes": probes})
        return self._pass(
            "every probed refusal path failed closed with a typed error", {"probes": probes}
        )


class EffectsDeclaredGate(ProviderGate):
    """PC-08 — external effects are declared, well-formed, and honest.

    A capability may not simultaneously claim determinism and declare a mutating
    effect: a mutation is not a reproducible read, and letting both stand would
    silently corrupt every determinism guarantee downstream.
    """

    article_id = "PC-08"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        descriptor = subject.descriptor
        findings: list[str] = []
        for capability in descriptor.capabilities:
            for effect in capability.effects:
                parts = effect.split(":")
                if len(parts) != 2 or not all(part.strip() for part in parts):
                    findings.append(f"{capability.name}: effect {effect!r} is not 'domain:action'")
                    continue
                action = parts[1].strip().lower()
                if capability.deterministic and action in MUTATING_EFFECT_ACTIONS:
                    findings.append(
                        f"{capability.name}: declares determinism and mutating effect {effect!r}"
                    )
        declared = descriptor.declared_effects()
        if findings:
            return self._fail(
                "declared effects are malformed or contradict a determinism claim",
                findings,
                {"declared_effects": list(declared)},
            )
        return self._pass(
            "every external effect is declared and consistent with its determinism claim",
            {"declared_effects": list(declared)},
        )


class FaultIsolationGate(ProviderGate):
    """PC-09 — a provider fault degrades its own scope and surfaces as typed."""

    article_id = "PC-09"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        if subject.instance is None:
            return self._indeterminate(
                "fault isolation is unmeasured without a live instance", ("instance absent",)
            )
        findings: list[str] = []
        evidence: dict[str, Any] = {}
        try:
            health = subject.instance.health()
        except Exception as exc:  # noqa: BLE001 - health must never raise
            return self._fail(
                "health reporting raised instead of reporting degradation",
                (f"health() raised {type(exc).__name__}",),
            )
        if not isinstance(health, ProviderHealth):
            findings.append("health() did not return a ProviderHealth")
        else:
            evidence["health_state"] = health.state.value
            evidence["checks"] = dict(health.checks)
        try:
            subject.instance.fetch("gate.probe.isolation.absent")
            findings.append("an absent fetch neither returned nor raised a typed error")
        except ProviderFrameworkError as exc:
            evidence["isolated_error_code"] = exc.code
        except Exception as exc:  # noqa: BLE001
            findings.append(
                f"a fault escaped as untyped {type(exc).__name__} instead of a framework error"
            )
        if findings:
            return self._fail("provider faults are not isolated", findings, evidence)
        return self._pass("faults surface as health degradation and typed errors", evidence)


class LifecycleGovernedGate(ProviderGate):
    """PC-10 — state is lifecycle-governed and the transition ledger is intact."""

    article_id = "PC-10"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        lifecycle = subject.lifecycle
        if lifecycle is None:
            return self._indeterminate(
                "no lifecycle authority was supplied; governance is unmeasured",
                ("lifecycle absent",),
            )
        qualified_id = subject.qualified_id
        findings: list[str] = []
        if not lifecycle.tracks(qualified_id):
            findings.append("provider is not tracked by the lifecycle authority")
        if not lifecycle.verify():
            findings.append("lifecycle ledger hash chain is broken")
        history = lifecycle.history(qualified_id) if lifecycle.tracks(qualified_id) else ()
        for entry in history:
            if entry.to_phase not in LIFECYCLE_TRANSITIONS[entry.from_phase]:
                findings.append(
                    f"ledger records an illegal transition "
                    f"{entry.from_phase.value}->{entry.to_phase.value}"
                )
        if findings:
            return self._fail(
                "provider state is not fully lifecycle-governed",
                findings,
                {"entries": len(history), "head_hash": lifecycle.head_hash},
            )
        return self._pass(
            "provider state is lifecycle-governed with an intact transition ledger",
            {
                "phase": lifecycle.phase(qualified_id).value,
                "entries": len(history),
                "head_hash": lifecycle.head_hash,
            },
        )


class CertifiableGate(ProviderGate):
    """PC-11 — the provider is on a certifiable footing: registered and version-pinned."""

    article_id = "PC-11"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        registry = subject.registry
        if registry is None:
            return self._indeterminate(
                "no registry was supplied; certifiability is unmeasured", ("registry absent",)
            )
        descriptor = subject.descriptor
        findings: list[str] = []
        evidence: dict[str, Any] = {}
        try:
            record = registry.get(descriptor.provider_id, descriptor.version)
        except ProviderFrameworkError as exc:
            return self._fail(
                "provider is not registered and therefore not certifiable",
                (exc.message,),
                {"qualified_id": descriptor.qualified_id},
            )
        evidence["registration_id"] = record.registration_id
        evidence["descriptor_hash"] = record.descriptor_hash
        if record.descriptor_hash != descriptor.content_hash():
            findings.append("descriptor under validation differs from the registered descriptor")
        lifecycle = subject.lifecycle
        if lifecycle is not None and lifecycle.tracks(descriptor.qualified_id):
            phase = lifecycle.phase(descriptor.qualified_id)
            evidence["phase"] = phase.value
            if phase in {ProviderPhase.DECLARED, ProviderPhase.REJECTED, ProviderPhase.RETIRED}:
                findings.append(f"phase {phase.value!r} is not a certifiable phase")
        if findings:
            return self._fail("provider is not certifiable", findings, evidence)
        return self._pass(
            "provider is registered, version-pinned, and in a certifiable phase", evidence
        )


class ComposabilityGate(ProviderGate):
    """PC-12 — dependencies resolve acyclically and composition is closed."""

    article_id = "PC-12"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        registry = subject.registry
        descriptor = subject.descriptor
        if registry is None:
            if not descriptor.dependencies:
                return self._pass(
                    "provider declares no dependencies and is trivially composable",
                    {"dependencies": []},
                )
            return self._indeterminate(
                "declared dependencies cannot be resolved without a registry",
                ("registry absent",),
                {"dependencies": [d.provider_id for d in descriptor.dependencies]},
            )
        try:
            order = registry.resolution_order(descriptor.provider_id)
        except ProviderFrameworkError as exc:
            return self._fail(
                "provider dependency graph does not resolve acyclically",
                (exc.message,),
                dict(exc.detail),
            )
        return self._pass(
            "dependency graph resolves acyclically in dependency-first order",
            {
                "resolution_order": [record.qualified_id for record in order],
                "dependencies": [d.provider_id for d in descriptor.dependencies],
            },
        )


class AdditiveEvolutionGate(ProviderGate):
    """PC-13 — no capability was removed within this major version line."""

    article_id = "PC-13"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        registry = subject.registry
        descriptor = subject.descriptor
        if registry is None:
            return self._indeterminate(
                "version history is unavailable without a registry", ("registry absent",)
            )
        major = descriptor.version.split(".")[0]
        offered = {c.name for c in descriptor.capabilities}
        findings: list[str] = []
        compared: list[str] = []
        for record in registry.registrations():
            if record.provider_id != descriptor.provider_id:
                continue
            if record.version.split(".")[0] != major:
                continue
            if record.version == descriptor.version:
                continue
            prior = {c.name for c in record.descriptor.capabilities}
            removed = sorted(prior - offered)
            compared.append(record.version)
            if removed:
                findings.append(f"{record.version} -> {descriptor.version} removed {removed}")
            if record.kind != descriptor.kind:
                findings.append(
                    f"{record.version} declares kind {record.kind!r}, "
                    f"{descriptor.version} declares {descriptor.kind!r}"
                )
        if findings:
            return self._fail(
                "evolution within the major version line is not additive",
                findings,
                {"compared_versions": sorted(compared)},
            )
        return self._pass(
            "evolution within the major version line is additive",
            {"compared_versions": sorted(compared), "capabilities": sorted(offered)},
        )


class ExtensibilityGate(ProviderGate):
    """PC-14 — the provider is fully expressible as data plus an entry point.

    Proven by round-tripping the descriptor through a plain mapping and comparing
    content hashes: if the round trip is lossless and the entry point is a resolvable
    string, onboarding required no framework change.
    """

    article_id = "PC-14"

    def evaluate(self, subject: ValidationSubject) -> GateResult:
        descriptor = subject.descriptor
        findings: list[str] = []
        original = descriptor.content_hash()
        try:
            rebuilt = ProviderDescriptor.from_dict(descriptor.to_dict())
        except ProviderFrameworkError as exc:
            return self._fail(
                "descriptor does not round-trip through data",
                (exc.message,),
                {"descriptor_hash": original},
            )
        if rebuilt.content_hash() != original:
            findings.append("descriptor round trip through data is lossy")
        if findings:
            return self._fail(
                "provider is not fully expressible as data",
                findings,
                {"descriptor_hash": original, "rebuilt_hash": rebuilt.content_hash()},
            )
        if not descriptor.entry_point:
            return self._indeterminate(
                "descriptor round-trips as data but names no entry point to realize it",
                ("entry_point absent: provider is declared, not yet realizable",),
                {"descriptor_hash": original},
            )
        if descriptor.entry_point.count(":") != 1:
            return self._fail(
                "entry point is not a resolvable 'module:attribute' reference",
                (f"entry_point {descriptor.entry_point!r} is malformed",),
                {"descriptor_hash": original},
            )
        return self._pass(
            "provider is expressible as data and realizable from a declared entry point",
            {"descriptor_hash": original, "entry_point": descriptor.entry_point},
        )


def default_gates() -> tuple[ProviderGate, ...]:
    """Return the fourteen constitutional gates, in article order."""
    return (
        InterfaceCompleteGate(),
        KindOpenGate(),
        IdentityDeclaredGate(),
        CapabilitiesDeclaredGate(),
        DeterminismGate(),
        ProvenanceGate(),
        FailClosedGate(),
        EffectsDeclaredGate(),
        FaultIsolationGate(),
        LifecycleGovernedGate(),
        CertifiableGate(),
        ComposabilityGate(),
        AdditiveEvolutionGate(),
        ExtensibilityGate(),
    )


class ProviderValidator:
    """Executes constitutional gates over a subject, isolating each gate.

    A gate that raises does not abort the pass: it is recorded as a blocking failure
    with the fault as its finding, so validation itself obeys PC-09.
    """

    def __init__(self, gates: Sequence[ProviderGate] | None = None) -> None:
        self._gates = tuple(gates) if gates is not None else default_gates()
        if not self._gates:
            raise ProviderValidationError("a validator requires at least one gate")
        seen: set[str] = set()
        for gate in self._gates:
            if gate.gate_id in seen:
                raise ProviderValidationError(
                    "duplicate gate id in validator", {"gate_id": gate.gate_id}
                )
            seen.add(gate.gate_id)

    @property
    def gates(self) -> tuple[ProviderGate, ...]:
        return self._gates

    def gate_ids(self) -> tuple[str, ...]:
        return tuple(gate.gate_id for gate in self._gates)

    def validate(self, subject: ValidationSubject) -> ValidationReport:
        """Execute every gate and return the content-addressed report."""
        if not isinstance(subject, ValidationSubject):
            raise ProviderValidationError(
                "validate requires a ValidationSubject", {"received": type(subject).__name__}
            )
        results: list[GateResult] = []
        for gate in self._gates:
            try:
                result = gate.evaluate(subject)
            except Exception as exc:  # noqa: BLE001 - a gate fault must not abort the pass
                result = GateResult(
                    gate_id=gate.gate_id,
                    article_id=gate.article_id,
                    status=GateStatus.FAIL,
                    severity=GateSeverity.BLOCKING,
                    summary="gate execution raised",
                    findings=(f"{type(exc).__name__}: {exc}",),
                )
            if not isinstance(result, GateResult):  # pragma: no cover - defensive
                raise ProviderValidationError(
                    "a gate must return a GateResult", {"gate_id": gate.gate_id}
                )
            results.append(result)
        return ValidationReport(
            qualified_id=subject.qualified_id,
            descriptor_hash=subject.descriptor.content_hash(),
            constitution_id=PROVIDER_CONSTITUTION_ID,
            constitution_version=PROVIDER_CONSTITUTION_VERSION,
            results=tuple(results),
        )


__all__ = [
    "MUTATING_EFFECT_ACTIONS",
    "PROVIDER_VALIDATION_VERSION",
    "AdditiveEvolutionGate",
    "CapabilitiesDeclaredGate",
    "CertifiableGate",
    "ComposabilityGate",
    "DeterminismGate",
    "EffectsDeclaredGate",
    "ExtensibilityGate",
    "FailClosedGate",
    "FaultIsolationGate",
    "GateResult",
    "GateSeverity",
    "GateStatus",
    "IdentityDeclaredGate",
    "InterfaceCompleteGate",
    "KindOpenGate",
    "LifecycleGovernedGate",
    "ProvenanceGate",
    "ProviderGate",
    "ProviderValidator",
    "ValidationReport",
    "ValidationStatus",
    "ValidationSubject",
    "default_gates",
    "framework_source_files",
]

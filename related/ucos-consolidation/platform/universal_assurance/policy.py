"""UCOS-EPIC-014 — The Universal Assurance Policy substrate (Terminal T7).

**Everything is policy driven.** The engine contains no list of validation obligations,
no list of certification criteria, no gate composition, no metric, no threshold, and no
required-evidence set. All of it is *declared* in an :class:`AssurancePolicy` document
and *bound* at run time to the reused platform engines. The code knows only the
document's **shape**; the document supplies the content. Adding an obligation, tightening
a threshold, or composing a new gate is therefore a **data change**, never a code change
(the no-enumeration discipline the constitutional programme engines enforce).

Document shape (JSON or TOML; stdlib parsing only, so the loader is vendor-neutral and
deterministic)::

    {
      "policy":     {"id", "name", "version", "authority", "fail_closed", "description"},
      "obligations":[{"id", "stage", "kind", "ref", "severity", "requires_facts", "rationale"}],
      "gates":      [{"id", "name", "stages", "obligations"}],
      "metrics":    [{"id", "stage", "observation", "comparator", "threshold",
                      "severity", "unit", "rationale"}],
      "evidence":   {"artifacts": [{"id", "stage", "name", "required"}],
                     "forbidden_write_prefixes": [...]},
      "bindings":   {"<name>": "<value>"},
      "reproducibility": {"replays", "byte_identical_required"}
    }

Every section is validated **fail-closed** against an explicit ``ALLOWED_KEYS`` set: an
unknown key, a duplicate id, an unknown stage/kind/severity/comparator, or a gate that
references an undeclared obligation is a malformed *policy* (an authoring fault) and
raises :class:`~platform.universal_assurance.errors.AssurancePolicyError`. A policy is
content-addressed via :meth:`AssurancePolicy.digest`, so every downstream plan, report,
certificate, and registry entry is anchored to the exact policy text that produced it.

An **obligation** binds to a concrete implementation in the *reused* platform by
``kind`` + ``ref``:

    * ``validation-rule`` → a rule id in :mod:`platform.universal_validation.rules`,
    * ``intelligence-dimension`` → a dimension in :mod:`platform.validation_intelligence`,
    * ``certification-criterion`` → a rule id in
      :mod:`engine.universal_certification.rules`,
    * ``certification-frame`` → a compliance frame id in
      :mod:`engine.universal_certification.compliance`.

``requires_facts`` declares the evidence an obligation needs, using the fact-address
grammar resolved by :mod:`platform.universal_assurance.planning`
(``validation.<domain>``, ``intelligence.<dimension>``, ``repository_truth``,
``observations.<key>``). An obligation whose required facts are absent is *planned and
recorded as unsatisfiable* — never silently dropped.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_assurance.contracts import (
    AssuranceStage,
    ObligationKind,
    Severity,
)
from platform.universal_assurance.errors import AssurancePolicyError
from typing import Any

from engine.universal_certification.contracts import MeasurementComparator

#: The assurance policy document format identifier.
POLICY_FORMAT = "ucos-assurance-policy/1.0.0"

#: The canonical policy shipped with the package (the default when none is supplied).
DEFAULT_POLICY_FILENAME = "ucos-assurance-policy.json"

_ROOT_KEYS = frozenset(
    {
        "$schema",
        "$comment",
        "policy",
        "obligations",
        "gates",
        "metrics",
        "evidence",
        "bindings",
        "reproducibility",
    }
)
_IDENTITY_KEYS = frozenset({"id", "name", "version", "authority", "fail_closed", "description"})
_OBLIGATION_KEYS = frozenset(
    {"id", "stage", "kind", "ref", "severity", "requires_facts", "rationale"}
)
_GATE_KEYS = frozenset({"id", "name", "stages", "obligations"})
_METRIC_KEYS = frozenset(
    {"id", "stage", "observation", "comparator", "threshold", "severity", "unit", "rationale"}
)
_EVIDENCE_KEYS = frozenset({"artifacts", "forbidden_write_prefixes"})
_ARTIFACT_KEYS = frozenset({"id", "stage", "name", "required"})
_REPRODUCIBILITY_KEYS = frozenset({"replays", "byte_identical_required"})


def _reject_unknown_keys(raw: Mapping[str, Any], allowed: frozenset[str], *, section: str) -> None:
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise AssurancePolicyError(
            "policy section declares unknown keys",
            section=section,
            unknown=unknown,
            allowed=sorted(allowed),
        )


def _require_mapping(raw: Any, *, section: str) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        raise AssurancePolicyError("policy section must be a mapping", section=section)
    return raw


def _require_list(raw: Any, *, section: str) -> list[Any]:
    if raw is None:
        return []
    if not isinstance(raw, Sequence) or isinstance(raw, str | bytes):
        raise AssurancePolicyError("policy section must be a list", section=section)
    return list(raw)


def _require_text(raw: Any, *, section: str, field_name: str) -> str:
    if not isinstance(raw, str) or not raw:
        raise AssurancePolicyError(
            "policy field must be a non-empty string", section=section, field=field_name
        )
    return raw


def _require_str_tuple(raw: Any, *, section: str, field_name: str) -> tuple[str, ...]:
    items = _require_list(raw, section=f"{section}.{field_name}")
    values: list[str] = []
    for item in items:
        if not isinstance(item, str) or not item:
            raise AssurancePolicyError(
                "policy list entries must be non-empty strings",
                section=section,
                field=field_name,
            )
        values.append(item)
    return tuple(values)


def _parse_enum(enum_cls: Any, raw: Any, *, section: str, field_name: str) -> Any:
    try:
        return enum_cls(raw)
    except ValueError as exc:
        raise AssurancePolicyError(
            "policy field declares an unsupported value",
            section=section,
            field=field_name,
            value=raw,
            supported=[member.value for member in enum_cls],
        ) from exc


@dataclass(frozen=True, slots=True)
class PolicyIdentity:
    """The identity and posture the policy asserts over itself."""

    id: str
    name: str
    version: str
    authority: str
    fail_closed: bool
    description: str = ""

    @classmethod
    def from_mapping(cls, raw: Any) -> PolicyIdentity:
        mapping = _require_mapping(raw, section="policy")
        _reject_unknown_keys(mapping, _IDENTITY_KEYS, section="policy")
        fail_closed = mapping.get("fail_closed", True)
        if not isinstance(fail_closed, bool):
            raise AssurancePolicyError(
                "policy fail_closed must be a boolean", section="policy", value=fail_closed
            )
        return cls(
            id=_require_text(mapping.get("id"), section="policy", field_name="id"),
            name=_require_text(mapping.get("name"), section="policy", field_name="name"),
            version=_require_text(mapping.get("version"), section="policy", field_name="version"),
            authority=_require_text(
                mapping.get("authority"), section="policy", field_name="authority"
            ),
            fail_closed=fail_closed,
            description=str(mapping.get("description", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "authority": self.authority,
            "fail_closed": self.fail_closed,
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class PolicyObligation:
    """A single declared assurance obligation bound to a reused implementation."""

    id: str
    stage: AssuranceStage
    kind: ObligationKind
    ref: str
    severity: Severity
    requires_facts: tuple[str, ...] = ()
    rationale: str = ""

    @classmethod
    def from_mapping(cls, raw: Any) -> PolicyObligation:
        mapping = _require_mapping(raw, section="obligations")
        _reject_unknown_keys(mapping, _OBLIGATION_KEYS, section="obligations")
        return cls(
            id=_require_text(mapping.get("id"), section="obligations", field_name="id"),
            stage=_parse_enum(
                AssuranceStage, mapping.get("stage"), section="obligations", field_name="stage"
            ),
            kind=_parse_enum(
                ObligationKind, mapping.get("kind"), section="obligations", field_name="kind"
            ),
            ref=_require_text(mapping.get("ref"), section="obligations", field_name="ref"),
            severity=_parse_enum(
                Severity, mapping.get("severity"), section="obligations", field_name="severity"
            ),
            requires_facts=_require_str_tuple(
                mapping.get("requires_facts"), section="obligations", field_name="requires_facts"
            ),
            rationale=str(mapping.get("rationale", "")),
        )

    @property
    def blocking(self) -> bool:
        return self.severity is Severity.BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stage": self.stage.value,
            "kind": self.kind.value,
            "ref": self.ref,
            "severity": self.severity.value,
            "requires_facts": list(self.requires_facts),
            "rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class PolicyGate:
    """A declared gate: a named conjunction of stages and obligations that must hold."""

    id: str
    name: str
    stages: tuple[AssuranceStage, ...]
    obligations: tuple[str, ...]

    @classmethod
    def from_mapping(cls, raw: Any) -> PolicyGate:
        mapping = _require_mapping(raw, section="gates")
        _reject_unknown_keys(mapping, _GATE_KEYS, section="gates")
        raw_stages = _require_str_tuple(mapping.get("stages"), section="gates", field_name="stages")
        stages = tuple(
            _parse_enum(AssuranceStage, value, section="gates", field_name="stages")
            for value in raw_stages
        )
        return cls(
            id=_require_text(mapping.get("id"), section="gates", field_name="id"),
            name=_require_text(mapping.get("name"), section="gates", field_name="name"),
            stages=tuple(sorted(set(stages), key=lambda s: s.order)),
            obligations=_require_str_tuple(
                mapping.get("obligations"), section="gates", field_name="obligations"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "stages": [stage.value for stage in self.stages],
            "obligations": list(self.obligations),
        }


@dataclass(frozen=True, slots=True)
class PolicyMetric:
    """A declared, decidable metric over a named run observation (measurability)."""

    id: str
    stage: AssuranceStage
    observation: str
    comparator: MeasurementComparator
    threshold: float
    severity: Severity
    unit: str = ""
    rationale: str = ""

    @classmethod
    def from_mapping(cls, raw: Any) -> PolicyMetric:
        mapping = _require_mapping(raw, section="metrics")
        _reject_unknown_keys(mapping, _METRIC_KEYS, section="metrics")
        threshold = mapping.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, int | float):
            raise AssurancePolicyError(
                "metric threshold must be numeric",
                section="metrics",
                metric=mapping.get("id"),
                value=threshold,
            )
        return cls(
            id=_require_text(mapping.get("id"), section="metrics", field_name="id"),
            stage=_parse_enum(
                AssuranceStage, mapping.get("stage"), section="metrics", field_name="stage"
            ),
            observation=_require_text(
                mapping.get("observation"), section="metrics", field_name="observation"
            ),
            comparator=_parse_enum(
                MeasurementComparator,
                mapping.get("comparator"),
                section="metrics",
                field_name="comparator",
            ),
            threshold=float(threshold),
            severity=_parse_enum(
                Severity, mapping.get("severity"), section="metrics", field_name="severity"
            ),
            unit=str(mapping.get("unit", "")),
            rationale=str(mapping.get("rationale", "")),
        )

    @property
    def blocking(self) -> bool:
        return self.severity is Severity.BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stage": self.stage.value,
            "observation": self.observation,
            "comparator": self.comparator.value,
            "threshold": self.threshold,
            "severity": self.severity.value,
            "unit": self.unit,
            "rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class PolicyEvidenceArtifact:
    """A declared evidence artifact that a stage must contribute to the bundle."""

    id: str
    stage: AssuranceStage
    name: str
    required: bool = True

    @classmethod
    def from_mapping(cls, raw: Any) -> PolicyEvidenceArtifact:
        mapping = _require_mapping(raw, section="evidence.artifacts")
        _reject_unknown_keys(mapping, _ARTIFACT_KEYS, section="evidence.artifacts")
        required = mapping.get("required", True)
        if not isinstance(required, bool):
            raise AssurancePolicyError(
                "evidence artifact 'required' must be a boolean",
                section="evidence.artifacts",
                artifact=mapping.get("id"),
            )
        return cls(
            id=_require_text(mapping.get("id"), section="evidence.artifacts", field_name="id"),
            stage=_parse_enum(
                AssuranceStage,
                mapping.get("stage"),
                section="evidence.artifacts",
                field_name="stage",
            ),
            name=_require_text(
                mapping.get("name"), section="evidence.artifacts", field_name="name"
            ),
            required=required,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stage": self.stage.value,
            "name": self.name,
            "required": self.required,
        }


@dataclass(frozen=True, slots=True)
class PolicyEvidenceRules:
    """The declared evidence-collection contract: what is required and where it may go."""

    artifacts: tuple[PolicyEvidenceArtifact, ...] = ()
    forbidden_write_prefixes: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Any) -> PolicyEvidenceRules:
        if raw is None:
            return cls()
        mapping = _require_mapping(raw, section="evidence")
        _reject_unknown_keys(mapping, _EVIDENCE_KEYS, section="evidence")
        artifacts = tuple(
            PolicyEvidenceArtifact.from_mapping(item)
            for item in _require_list(mapping.get("artifacts"), section="evidence.artifacts")
        )
        _require_unique_ids((a.id for a in artifacts), section="evidence.artifacts")
        return cls(
            artifacts=tuple(sorted(artifacts, key=lambda a: (a.stage.order, a.id))),
            forbidden_write_prefixes=_require_str_tuple(
                mapping.get("forbidden_write_prefixes"),
                section="evidence",
                field_name="forbidden_write_prefixes",
            ),
        )

    def required_artifacts(self) -> tuple[PolicyEvidenceArtifact, ...]:
        return tuple(artifact for artifact in self.artifacts if artifact.required)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "forbidden_write_prefixes": list(self.forbidden_write_prefixes),
        }


@dataclass(frozen=True, slots=True)
class ReproducibilityPolicy:
    """The declared reproducibility contract (how many replays must agree byte-for-byte)."""

    replays: int = 2
    byte_identical_required: bool = True

    @classmethod
    def from_mapping(cls, raw: Any) -> ReproducibilityPolicy:
        if raw is None:
            return cls()
        mapping = _require_mapping(raw, section="reproducibility")
        _reject_unknown_keys(mapping, _REPRODUCIBILITY_KEYS, section="reproducibility")
        replays = mapping.get("replays", 2)
        if isinstance(replays, bool) or not isinstance(replays, int) or replays < 2:
            raise AssurancePolicyError(
                "reproducibility replays must be an integer >= 2",
                section="reproducibility",
                value=replays,
            )
        required = mapping.get("byte_identical_required", True)
        if not isinstance(required, bool):
            raise AssurancePolicyError(
                "reproducibility byte_identical_required must be a boolean",
                section="reproducibility",
            )
        return cls(replays=replays, byte_identical_required=required)

    def to_dict(self) -> dict[str, Any]:
        return {
            "replays": self.replays,
            "byte_identical_required": self.byte_identical_required,
        }


def _require_unique_ids(ids: Iterable[str], *, section: str) -> None:
    """Fail closed when a policy section declares the same id twice."""
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in ids:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        raise AssurancePolicyError(
            "policy section declares duplicate ids",
            section=section,
            duplicates=sorted(duplicates),
        )


@dataclass(frozen=True, slots=True)
class AssurancePolicy:
    """The whole declarative assurance policy — the single source of assurance truth.

    Every obligation, gate, metric, required evidence artifact, binding, and
    reproducibility requirement the engine acts on comes from here. The document is
    content-addressed (:meth:`digest`), so every artifact the engine emits can be traced
    back to the exact policy text that authorized it.
    """

    identity: PolicyIdentity
    obligations: tuple[PolicyObligation, ...] = ()
    gates: tuple[PolicyGate, ...] = ()
    metrics: tuple[PolicyMetric, ...] = ()
    evidence: PolicyEvidenceRules = field(default_factory=PolicyEvidenceRules)
    bindings: Mapping[str, str] = field(default_factory=dict)
    reproducibility: ReproducibilityPolicy = field(default_factory=ReproducibilityPolicy)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> AssurancePolicy:
        """Assimilate a policy document, failing closed on any malformed section.

        Raises:
            AssurancePolicyError: if the document is not a mapping, declares an unknown
                key, omits a required field, declares a duplicate id, names an unknown
                stage/kind/severity/comparator, or composes a gate from an undeclared
                obligation.
        """
        if not isinstance(raw, Mapping):
            raise AssurancePolicyError("an assurance policy document must be a mapping")
        _reject_unknown_keys(raw, _ROOT_KEYS, section="<root>")

        identity = PolicyIdentity.from_mapping(raw.get("policy"))
        obligations = tuple(
            PolicyObligation.from_mapping(item)
            for item in _require_list(raw.get("obligations"), section="obligations")
        )
        if not obligations:
            raise AssurancePolicyError(
                "an assurance policy must declare at least one obligation",
                policy=identity.id,
            )
        _require_unique_ids((o.id for o in obligations), section="obligations")

        gates = tuple(
            PolicyGate.from_mapping(item)
            for item in _require_list(raw.get("gates"), section="gates")
        )
        _require_unique_ids((g.id for g in gates), section="gates")

        metrics = tuple(
            PolicyMetric.from_mapping(item)
            for item in _require_list(raw.get("metrics"), section="metrics")
        )
        _require_unique_ids((m.id for m in metrics), section="metrics")

        evidence = PolicyEvidenceRules.from_mapping(raw.get("evidence"))
        bindings = cls._parse_bindings(raw.get("bindings"))
        reproducibility = ReproducibilityPolicy.from_mapping(raw.get("reproducibility"))

        declared = {o.id for o in obligations}
        for gate in gates:
            dangling = sorted(set(gate.obligations) - declared)
            if dangling:
                raise AssurancePolicyError(
                    "gate references undeclared obligations",
                    section="gates",
                    gate=gate.id,
                    dangling=dangling,
                )

        return cls(
            identity=identity,
            obligations=tuple(
                sorted(obligations, key=lambda o: (o.stage.order, o.kind.order, o.id))
            ),
            gates=tuple(sorted(gates, key=lambda g: g.id)),
            metrics=tuple(sorted(metrics, key=lambda m: (m.stage.order, m.id))),
            evidence=evidence,
            bindings=bindings,
            reproducibility=reproducibility,
        )

    @staticmethod
    def _parse_bindings(raw: Any) -> dict[str, str]:
        if raw is None:
            return {}
        mapping = _require_mapping(raw, section="bindings")
        parsed: dict[str, str] = {}
        for key, value in mapping.items():
            if not isinstance(key, str) or not key:
                raise AssurancePolicyError(
                    "binding names must be non-empty strings", section="bindings"
                )
            if not isinstance(value, str) or not value:
                raise AssurancePolicyError(
                    "binding values must be non-empty strings", section="bindings", binding=key
                )
            parsed[key] = value
        return parsed

    # -- declarative lookups (the engine asks; it never enumerates) -------------

    def obligations_for(
        self,
        stage: AssuranceStage | None = None,
        *,
        kind: ObligationKind | None = None,
    ) -> tuple[PolicyObligation, ...]:
        """The declared obligations for ``stage`` and/or ``kind``, in canonical order."""
        selected = self.obligations
        if stage is not None:
            selected = tuple(o for o in selected if o.stage is stage)
        if kind is not None:
            selected = tuple(o for o in selected if o.kind is kind)
        return selected

    def obligation(self, obligation_id: str) -> PolicyObligation:
        """The obligation declared under ``obligation_id``.

        Raises:
            AssurancePolicyError: if no such obligation is declared.
        """
        for obligation in self.obligations:
            if obligation.id == obligation_id:
                return obligation
        raise AssurancePolicyError(
            "policy declares no such obligation",
            policy=self.identity.id,
            obligation=obligation_id,
        )

    def metrics_for(self, stage: AssuranceStage | None = None) -> tuple[PolicyMetric, ...]:
        """The declared metrics for ``stage`` (or all of them), in canonical order."""
        if stage is None:
            return self.metrics
        return tuple(metric for metric in self.metrics if metric.stage is stage)

    def artifacts_for(
        self, stage: AssuranceStage | None = None
    ) -> tuple[PolicyEvidenceArtifact, ...]:
        """The declared evidence artifacts for ``stage`` (or all of them)."""
        if stage is None:
            return self.evidence.artifacts
        return tuple(a for a in self.evidence.artifacts if a.stage is stage)

    def stages_declared(self) -> tuple[AssuranceStage, ...]:
        """Every stage the policy touches (via an obligation, metric, or artifact)."""
        stages: set[AssuranceStage] = {o.stage for o in self.obligations}
        stages.update(metric.stage for metric in self.metrics)
        stages.update(artifact.stage for artifact in self.evidence.artifacts)
        stages.update(stage for gate in self.gates for stage in gate.stages)
        return tuple(sorted(stages, key=lambda s: s.order))

    def binding(self, name: str, default: str | None = None) -> str:
        """The declared binding value for ``name``.

        Raises:
            AssurancePolicyError: if the binding is undeclared and no default is given.
        """
        value = self.bindings.get(name, default)
        if value is None:
            raise AssurancePolicyError(
                "policy declares no such binding", policy=self.identity.id, binding=name
            )
        return value

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_format": POLICY_FORMAT,
            "policy": self.identity.to_dict(),
            "obligations": [o.to_dict() for o in self.obligations],
            "gates": [g.to_dict() for g in self.gates],
            "metrics": [m.to_dict() for m in self.metrics],
            "evidence": self.evidence.to_dict(),
            "bindings": {key: self.bindings[key] for key in sorted(self.bindings)},
            "reproducibility": self.reproducibility.to_dict(),
        }

    def digest(self) -> str:
        """The deterministic content hash of the whole policy document."""
        return content_hash(self.to_dict())

    def counts(self) -> dict[str, int]:
        return {
            "obligations": len(self.obligations),
            "blocking_obligations": sum(1 for o in self.obligations if o.blocking),
            "gates": len(self.gates),
            "metrics": len(self.metrics),
            "artifacts": len(self.evidence.artifacts),
            "required_artifacts": len(self.evidence.required_artifacts()),
            "stages": len(self.stages_declared()),
        }


def parse_policy(raw: Mapping[str, Any]) -> AssurancePolicy:
    """Assimilate an in-memory mapping into an :class:`AssurancePolicy`."""
    return AssurancePolicy.from_mapping(raw)


def default_policy_path() -> Path:
    """The filesystem path of the canonical policy shipped with this package."""
    return package_data_path(DEFAULT_POLICY_FILENAME)


def package_data_path(filename: str) -> Path:
    """The filesystem path of a JSON document shipped in this package's ``data`` dir."""
    return Path(__file__).resolve().parent / "data" / filename


def load_policy(path: str | Path) -> AssurancePolicy:
    """Load and assimilate an assurance policy from a JSON or TOML file.

    Raises:
        AssurancePolicyError: if the file is absent, unreadable, of an unsupported type,
            or not valid JSON/TOML.
    """
    policy_path = Path(path)
    if not policy_path.is_file():
        raise AssurancePolicyError("policy file not found", path=str(policy_path))

    suffix = policy_path.suffix.lower()
    try:
        if suffix == ".json":
            raw = json.loads(policy_path.read_text(encoding="utf-8"))
        elif suffix == ".toml":
            raw = tomllib.loads(policy_path.read_text(encoding="utf-8"))
        else:
            raise AssurancePolicyError(
                "unsupported policy file type (expected .json or .toml)",
                path=str(policy_path),
                suffix=suffix,
            )
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, OSError, UnicodeDecodeError) as exc:
        raise AssurancePolicyError(
            "policy file could not be read or parsed",
            path=str(policy_path),
            detail=str(exc),
        ) from exc

    if not isinstance(raw, Mapping):
        raise AssurancePolicyError("policy root must be a mapping/table", path=str(policy_path))
    return parse_policy(raw)


def load_default_policy() -> AssurancePolicy:
    """Load the canonical assurance policy shipped with the package."""
    return load_policy(default_policy_path())


__all__ = [
    "POLICY_FORMAT",
    "DEFAULT_POLICY_FILENAME",
    "PolicyIdentity",
    "PolicyObligation",
    "PolicyGate",
    "PolicyMetric",
    "PolicyEvidenceArtifact",
    "PolicyEvidenceRules",
    "ReproducibilityPolicy",
    "AssurancePolicy",
    "parse_policy",
    "load_policy",
    "load_default_policy",
    "default_policy_path",
    "package_data_path",
]

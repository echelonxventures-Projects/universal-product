"""UCOS-EPIC-013 — the Compatibility Engine (Terminal T5).

The **Compatibility Engine** is the deliverable that reasons over *baseline↔candidate*
deltas across the three compatibility dimensions — **contract**, **runtime**, and
**version** — and determines, deterministically and fail-closed, whether a candidate is
backward-compatible with the baseline it must replace.

It is a pure computation component: every comparison is a function of its inputs (no
wall-clock, no ambient state), produces ordered
:class:`~platform.validation_intelligence.contracts.Finding` objects, and treats
*absent or malformed* evidence as a **breaking** (blocking) finding — absence of
evidence is never evidence of compatibility. Semantic-version reasoning is standard
(``major.minor.patch``): a change is breaking iff it removes a promised capability or
crosses a major version, and is compatible iff it is additive within a major line.

The three compatibility analyzers delegate to this engine; the
:class:`~platform.validation_intelligence.contracts.CompatibilityReport` is the
projection of a full run's compatibility dimensions.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from platform.validation_intelligence.contracts import (
    CompatibilityReport,
    Finding,
    FindingStatus,
    IntelligenceDimension,
    Severity,
    ValidationIntelligenceReport,
)
from platform.validation_intelligence.errors import CompatibilityError
from typing import Any

_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
_SPEC = re.compile(r"^(\^|>=|=)?\s*(\d+\.\d+\.\d+)$")


@dataclass(frozen=True, slots=True, order=True)
class SemVer:
    """An immutable, comparable ``major.minor.patch`` semantic version."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: Any) -> SemVer:
        """Parse a ``major.minor.patch`` string, raising on a malformed value."""
        parsed = cls.try_parse(value)
        if parsed is None:
            raise CompatibilityError("malformed semantic version", value=value)
        return parsed

    @classmethod
    def try_parse(cls, value: Any) -> SemVer | None:
        """Parse a semantic version, returning ``None`` on a malformed value."""
        if not isinstance(value, str):
            return None
        match = _SEMVER.match(value.strip())
        if match is None:
            return None
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def _satisfies(resolved: SemVer, spec: str) -> tuple[bool, str]:
    """Return ``(ok, reason)`` for whether ``resolved`` satisfies a version ``spec``.

    Supported spec forms (semver-safe): ``1.2.3`` / ``=1.2.3`` (exact-floor, same major),
    ``^1.2.3`` and ``>=1.2.3`` (at-least, same major). A cross-major resolution is never
    compatible; a resolution below the floor is never compatible.
    """
    match = _SPEC.match(spec.strip()) if isinstance(spec, str) else None
    if match is None:
        return False, "malformed version spec"
    operator = match.group(1) or "="
    floor = SemVer.parse(match.group(2))
    if resolved.major != floor.major:
        return False, f"major mismatch (requires {floor.major}.x, resolved {resolved})"
    if operator == "=":
        if resolved < floor:
            return False, f"resolved {resolved} is below the required floor {floor}"
        return True, "compatible"
    # "^" / ">=": at least the floor, within the same major line.
    if resolved < floor:
        return False, f"resolved {resolved} is below {operator}{floor}"
    return True, "compatible"


def _as_sequence(value: Any) -> list[Any] | None:
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return list(value)
    return None


class CompatibilityEngine:
    """Deterministic baseline↔candidate compatibility reasoning (contract/runtime/version)."""

    __slots__ = ()

    # -- contract compatibility ------------------------------------------------
    def compare_contracts(self, baseline: Any, candidate: Any) -> tuple[Finding, ...]:
        """Compare declared contract sets; a removed promise or cross-major is breaking."""
        base_list = _as_sequence(baseline)
        cand_list = _as_sequence(candidate)
        if base_list is None or cand_list is None:
            return (
                _breaking(
                    IntelligenceDimension.CONTRACT_COMPATIBILITY,
                    "contract_compatibility.evidence",
                    "baseline and/or candidate contracts are absent or malformed",
                ),
            )
        base = _index_by(base_list, "name")
        cand = _index_by(cand_list, "name")
        if base is None or cand is None:
            return (
                _breaking(
                    IntelligenceDimension.CONTRACT_COMPATIBILITY,
                    "contract_compatibility.evidence",
                    "a contract declaration is malformed (missing name)",
                ),
            )
        findings: list[Finding] = []
        for name in sorted(set(base) | set(cand)):
            findings.append(self._compare_one_contract(name, base.get(name), cand.get(name)))
        return tuple(findings)

    def _compare_one_contract(
        self, name: str, base: Mapping[str, Any] | None, cand: Mapping[str, Any] | None
    ) -> Finding:
        check_id = f"contract_compatibility.{name}"
        if base is not None and cand is None:
            return _breaking(
                IntelligenceDimension.CONTRACT_COMPATIBILITY,
                check_id,
                f"contract '{name}' was removed (breaking)",
                contract=name,
            )
        if base is None and cand is not None:
            return _compatible(
                IntelligenceDimension.CONTRACT_COMPATIBILITY,
                check_id,
                f"contract '{name}' was added (backward-compatible)",
                contract=name,
            )
        assert base is not None and cand is not None  # noqa: S101 — both-present branch
        base_ver = SemVer.try_parse(base.get("version"))
        cand_ver = SemVer.try_parse(cand.get("version"))
        if base_ver is None or cand_ver is None:
            return _breaking(
                IntelligenceDimension.CONTRACT_COMPATIBILITY,
                check_id,
                f"contract '{name}' has an absent or malformed version",
                contract=name,
            )
        if cand_ver < base_ver:
            return _breaking(
                IntelligenceDimension.CONTRACT_COMPATIBILITY,
                check_id,
                f"contract '{name}' version regressed ({base_ver} → {cand_ver})",
                contract=name,
                baseline=str(base_ver),
                candidate=str(cand_ver),
            )
        base_required = {str(x) for x in (_as_sequence(base.get("required_fields")) or [])}
        cand_required = {str(x) for x in (_as_sequence(cand.get("required_fields")) or [])}
        added_required = sorted(cand_required - base_required)
        removed_fields = sorted(base_required - cand_required)
        major_bump = cand_ver.major > base_ver.major
        # A removed promised field is breaking unless the major version was bumped.
        if removed_fields and not major_bump:
            return _breaking(
                IntelligenceDimension.CONTRACT_COMPATIBILITY,
                check_id,
                f"contract '{name}' removed required fields without a major bump",
                contract=name,
                removed_fields=removed_fields,
            )
        # A newly-required field breaks existing producers unless the major was bumped.
        if added_required and not major_bump:
            return _breaking(
                IntelligenceDimension.CONTRACT_COMPATIBILITY,
                check_id,
                f"contract '{name}' added required fields without a major bump",
                contract=name,
                added_required=added_required,
            )
        return _compatible(
            IntelligenceDimension.CONTRACT_COMPATIBILITY,
            check_id,
            f"contract '{name}' is backward-compatible ({base_ver} → {cand_ver})",
            contract=name,
        )

    # -- runtime compatibility -------------------------------------------------
    def compare_runtime(self, required: Any, provided: Any) -> tuple[Finding, ...]:
        """Compare a required runtime surface against what the candidate provides."""
        if not isinstance(required, Mapping) or not isinstance(provided, Mapping):
            return (
                _breaking(
                    IntelligenceDimension.RUNTIME_COMPATIBILITY,
                    "runtime_compatibility.evidence",
                    "required and/or provided runtime surface is absent or malformed",
                ),
            )
        findings: list[Finding] = []
        req_interfaces = {str(x) for x in (_as_sequence(required.get("interfaces")) or [])}
        prov_interfaces = {str(x) for x in (_as_sequence(provided.get("interfaces")) or [])}
        missing = sorted(req_interfaces - prov_interfaces)
        if missing:
            findings.append(
                _breaking(
                    IntelligenceDimension.RUNTIME_COMPATIBILITY,
                    "runtime_compatibility.interfaces",
                    "the candidate runtime no longer provides required interfaces",
                    missing=missing,
                )
            )
        else:
            findings.append(
                _compatible(
                    IntelligenceDimension.RUNTIME_COMPATIBILITY,
                    "runtime_compatibility.interfaces",
                    "every required runtime interface is provided",
                    interfaces=len(req_interfaces),
                )
            )
        findings.append(self._compare_runtime_abi(required.get("abi"), provided.get("abi")))
        return tuple(findings)

    def _compare_runtime_abi(self, required_abi: Any, provided_abi: Any) -> Finding:
        check_id = "runtime_compatibility.abi"
        req = SemVer.try_parse(required_abi)
        prov = SemVer.try_parse(provided_abi)
        if req is None or prov is None:
            return _breaking(
                IntelligenceDimension.RUNTIME_COMPATIBILITY,
                check_id,
                "runtime ABI version is absent or malformed",
            )
        if prov.major != req.major:
            return _breaking(
                IntelligenceDimension.RUNTIME_COMPATIBILITY,
                check_id,
                f"runtime ABI major changed ({req} → {prov})",
                required=str(req),
                provided=str(prov),
            )
        if prov < req:
            return _breaking(
                IntelligenceDimension.RUNTIME_COMPATIBILITY,
                check_id,
                f"provided runtime ABI {prov} is below the required {req}",
                required=str(req),
                provided=str(prov),
            )
        return _compatible(
            IntelligenceDimension.RUNTIME_COMPATIBILITY,
            check_id,
            f"runtime ABI is compatible ({req} → {prov})",
            required=str(req),
            provided=str(prov),
        )

    # -- version compatibility -------------------------------------------------
    def compare_versions(self, components: Any) -> tuple[Finding, ...]:
        """Check that every component's inter-component version requirement is satisfied."""
        comp_list = _as_sequence(components)
        if comp_list is None:
            return (
                _breaking(
                    IntelligenceDimension.VERSION_COMPATIBILITY,
                    "version_compatibility.evidence",
                    "components are absent or malformed",
                ),
            )
        resolved: dict[str, SemVer] = {}
        for comp in comp_list:
            if not isinstance(comp, Mapping) or not comp.get("id"):
                return (
                    _breaking(
                        IntelligenceDimension.VERSION_COMPATIBILITY,
                        "version_compatibility.evidence",
                        "a component declaration is malformed",
                        component=comp if isinstance(comp, Mapping) else None,
                    ),
                )
            version = SemVer.try_parse(comp.get("version"))
            if version is None:
                return (
                    _breaking(
                        IntelligenceDimension.VERSION_COMPATIBILITY,
                        "version_compatibility.evidence",
                        f"component '{comp['id']}' has an absent or malformed version",
                        component=str(comp["id"]),
                    ),
                )
            resolved[str(comp["id"])] = version
        findings: list[Finding] = []
        for comp in sorted(comp_list, key=lambda c: str(c["id"])):
            findings.extend(self._check_requirements(comp, resolved))
        if not findings:
            findings.append(
                _compatible(
                    IntelligenceDimension.VERSION_COMPATIBILITY,
                    "version_compatibility.no-requirements",
                    "no inter-component version requirements are declared",
                    components=len(resolved),
                )
            )
        return tuple(findings)

    def _check_requirements(
        self, comp: Mapping[str, Any], resolved: Mapping[str, SemVer]
    ) -> list[Finding]:
        comp_id = str(comp["id"])
        requires = comp.get("requires", {})
        if not isinstance(requires, Mapping):
            return [
                _breaking(
                    IntelligenceDimension.VERSION_COMPATIBILITY,
                    f"version_compatibility.{comp_id}",
                    f"component '{comp_id}' has malformed requirements",
                    component=comp_id,
                )
            ]
        findings: list[Finding] = []
        for dep_id in sorted(requires, key=str):
            spec = requires[dep_id]
            check_id = f"version_compatibility.{comp_id}->{dep_id}"
            dep_version = resolved.get(str(dep_id))
            if dep_version is None:
                findings.append(
                    _breaking(
                        IntelligenceDimension.VERSION_COMPATIBILITY,
                        check_id,
                        f"component '{comp_id}' requires unknown component '{dep_id}'",
                        component=comp_id,
                        requires=str(dep_id),
                    )
                )
                continue
            ok, reason = _satisfies(dep_version, str(spec))
            if not ok:
                findings.append(
                    _breaking(
                        IntelligenceDimension.VERSION_COMPATIBILITY,
                        check_id,
                        f"component '{comp_id}' requirement on '{dep_id}' unsatisfied: {reason}",
                        component=comp_id,
                        requires=str(dep_id),
                        spec=str(spec),
                        resolved=str(dep_version),
                    )
                )
            else:
                findings.append(
                    _compatible(
                        IntelligenceDimension.VERSION_COMPATIBILITY,
                        check_id,
                        f"component '{comp_id}' requirement on '{dep_id}' satisfied",
                        component=comp_id,
                        requires=str(dep_id),
                        spec=str(spec),
                        resolved=str(dep_version),
                    )
                )
        return findings


def _index_by(items: list[Any], key: str) -> dict[str, Mapping[str, Any]] | None:
    """Index a list of mappings by ``key`` (``None`` if any entry is malformed)."""
    indexed: dict[str, Mapping[str, Any]] = {}
    for item in items:
        if not isinstance(item, Mapping) or not item.get(key):
            return None
        indexed[str(item[key])] = item
    return indexed


def _breaking(
    dimension: IntelligenceDimension, check_id: str, message: str, **details: Any
) -> Finding:
    return Finding(
        check_id=check_id,
        dimension=dimension,
        severity=Severity.BLOCKING,
        status=FindingStatus.FAIL,
        message=message,
        details=details,
    )


def _compatible(
    dimension: IntelligenceDimension, check_id: str, message: str, **details: Any
) -> Finding:
    return Finding(
        check_id=check_id,
        dimension=dimension,
        severity=Severity.BLOCKING,
        status=FindingStatus.PASS,
        message=message,
        details=details,
    )


def build_compatibility_report(report: ValidationIntelligenceReport) -> CompatibilityReport:
    """Project the Compatibility Engine's report from a full intelligence report."""
    return CompatibilityReport.from_report(report)


__all__ = ["SemVer", "CompatibilityEngine", "build_compatibility_report"]

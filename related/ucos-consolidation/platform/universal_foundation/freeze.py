"""UCOS-UFC-001 — Foundation freeze readiness (UFC-11).

A freeze is a promise that what is frozen will not need to change. This module refuses to make
that promise on anything but measurement: each declared criterion names the *kind* of evidence
that can discharge it, and the evidence is read from the determinations that already exist —
conformance, convergence, and the composed Foundation determination itself.

Three verdicts, and the third one matters:

    ``READY``       every criterion is discharged by measured evidence.
    ``NOT-READY``   a criterion is measured and unsatisfied. The blockers name what to build.
    ``UNMEASURED``  a criterion's evidence was not gathered in this run. It is **not** a pass.
                    A freeze declared over unmeasured criteria is exactly the failure a freeze
                    is supposed to prevent, so an unmeasured criterion withholds readiness as
                    firmly as a failed one, while being reported differently so the difference
                    is visible.

This module never performs a freeze. It determines eligibility and stops; freezing is a
constituent act.
"""

from __future__ import annotations

import json
import shlex
import subprocess  # noqa: S404 - declared verification commands, never user input
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_foundation.conformance import (
    ConformanceDetermination,
    Verdict,
)
from platform.universal_foundation.convergence import ConvergenceDetermination
from platform.universal_foundation.errors import FoundationFreezeError
from typing import Any

#: The packaged catalogue directory holding the declared freeze criteria.
CATALOG_DIRNAME = "catalog"

#: The declared freeze criteria (data, not code).
DEFAULT_FREEZE_FILENAME = "foundation-freeze.json"


class CriterionKind(str, Enum):
    """The kinds of evidence a freeze criterion may be discharged by.

    The set is closed on purpose: a criterion whose evidence has no declared kind cannot be
    measured, and a criterion that cannot be measured cannot discharge a freeze.
    """

    #: Every named gate passed for every measured capability.
    GATES = "gates"
    #: No conformance probe faulted — there is no unresolved architecture.
    NO_FAULT = "no-fault"
    #: Platform maturity reached the declared threshold.
    MATURITY = "maturity"
    #: Every named platform-scoped gate passed.
    PLATFORM_GATES = "platform-gates"
    #: Zero surplus live implementations across every constitutional model.
    NO_DUPLICATES = "no-duplicates"
    #: Every named constitutional model is converged.
    MODELS_CONVERGED = "models-converged"
    #: The declared capability dependency order resolves (acyclic, every dependency known).
    DEPENDENCY_ORDER = "dependency-order"
    #: A declared verification command exits zero.
    COMMAND = "command"

    @classmethod
    def coerce(cls, value: Any, *, subject: str = "criterion kind") -> CriterionKind:
        """Coerce ``value`` to a kind, failing closed (never silently)."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise FoundationFreezeError(
                    "unknown freeze criterion kind", subject=subject, value=value
                ) from exc
        raise FoundationFreezeError("criterion kind must be a string", subject=subject)


class CriterionVerdict(str, Enum):
    """The outcome of one freeze criterion."""

    READY = "READY"
    NOT_READY = "NOT-READY"
    UNMEASURED = "UNMEASURED"

    @property
    def discharged(self) -> bool:
        """Whether this verdict discharges the criterion. Only READY does."""
        return self is CriterionVerdict.READY


@dataclass(frozen=True, slots=True)
class FreezeCriterion:
    """One declared condition a Foundation freeze requires."""

    criterion_id: str
    requirement: str
    kind: CriterionKind
    gates: tuple[str, ...] = ()
    models: tuple[str, ...] = ()
    threshold: float = 0.0
    command: str = ""
    rationale: str = ""

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> FreezeCriterion:
        """Build a validated criterion declaration (fail-closed)."""
        if not isinstance(payload, Mapping):
            raise FoundationFreezeError("criterion declaration must be a mapping")
        missing = [key for key in ("criterion_id", "requirement", "kind") if key not in payload]
        if missing:
            raise FoundationFreezeError(
                "criterion declaration is incomplete", missing=",".join(missing)
            )
        criterion_id = str(payload["criterion_id"]).strip()
        if not criterion_id:
            raise FoundationFreezeError("criterion_id must be non-empty")
        kind = CriterionKind.coerce(payload["kind"], subject=criterion_id)
        criterion = cls(
            criterion_id=criterion_id,
            requirement=str(payload["requirement"]),
            kind=kind,
            gates=tuple(str(item) for item in payload.get("gates", ())),
            models=tuple(str(item) for item in payload.get("models", ())),
            threshold=float(payload.get("threshold", 0.0)),
            command=str(payload.get("command", "")),
            rationale=str(payload.get("rationale", "")),
        )
        criterion._require_parameters()
        return criterion

    def _require_parameters(self) -> None:
        """Refuse a criterion whose kind cannot be measured from what it declares."""
        needs: dict[CriterionKind, str] = {
            CriterionKind.GATES: "gates",
            CriterionKind.PLATFORM_GATES: "gates",
            CriterionKind.MODELS_CONVERGED: "models",
            CriterionKind.COMMAND: "command",
        }
        field = needs.get(self.kind)
        if field and not getattr(self, field):
            raise FoundationFreezeError(
                f"criterion of kind '{self.kind.value}' declares no {field}",
                criterion_id=self.criterion_id,
            )
        if self.kind is CriterionKind.MATURITY and self.threshold <= 0:
            raise FoundationFreezeError(
                "maturity criterion declares no positive threshold",
                criterion_id=self.criterion_id,
            )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection."""
        return {
            "criterion_id": self.criterion_id,
            "requirement": self.requirement,
            "kind": self.kind.value,
            "gates": list(self.gates),
            "models": list(self.models),
            "threshold": self.threshold,
            "command": self.command,
            "rationale": self.rationale,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this declaration."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class CriterionResult:
    """The measured outcome of one freeze criterion, with the evidence that decided it."""

    criterion_id: str
    requirement: str
    kind: CriterionKind
    verdict: CriterionVerdict
    summary: str = ""
    blockers: tuple[str, ...] = ()
    result_id: str = ""

    @classmethod
    def create(
        cls,
        criterion: FreezeCriterion,
        verdict: CriterionVerdict,
        *,
        summary: str = "",
        blockers: Iterable[str] = (),
    ) -> CriterionResult:
        """Build a content-addressed criterion result."""
        found = tuple(sorted({str(item) for item in blockers}))
        core = {
            "criterion_id": criterion.criterion_id,
            "verdict": verdict.value,
            "blockers": list(found),
        }
        return cls(
            criterion_id=criterion.criterion_id,
            requirement=criterion.requirement,
            kind=criterion.kind,
            verdict=verdict,
            summary=summary,
            blockers=found,
            result_id=f"UCOS-UFCF-{content_hash(core)[:16]}",
        )

    @property
    def discharged(self) -> bool:
        """Whether this result discharges its criterion."""
        return self.verdict.discharged

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection."""
        return {
            "result_id": self.result_id,
            "criterion_id": self.criterion_id,
            "requirement": self.requirement,
            "kind": self.kind.value,
            "verdict": self.verdict.value,
            "summary": self.summary,
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True, slots=True)
class FreezeDetermination:
    """The immutable determination of whether the Foundation is eligible to be frozen."""

    results: tuple[CriterionResult, ...]
    conformance_id: str = ""
    convergence_id: str = ""
    maturity_percentage: float = 0.0
    determination_id: str = ""

    @classmethod
    def create(
        cls,
        results: Iterable[CriterionResult],
        *,
        conformance_id: str = "",
        convergence_id: str = "",
        maturity_percentage: float = 0.0,
    ) -> FreezeDetermination:
        """Build a content-addressed freeze determination."""
        ordered = tuple(sorted(results, key=lambda item: item.criterion_id))
        core = {
            "results": [item.result_id for item in ordered],
            "conformance": conformance_id,
            "convergence": convergence_id,
        }
        return cls(
            results=ordered,
            conformance_id=conformance_id,
            convergence_id=convergence_id,
            maturity_percentage=maturity_percentage,
            determination_id=f"UCOS-UFCZ-{content_hash(core)[:16]}",
        )

    @property
    def total(self) -> int:
        """How many criteria were declared."""
        return len(self.results)

    @property
    def ready(self) -> bool:
        """Whether every declared criterion is discharged by measured evidence."""
        return bool(self.results) and all(item.discharged for item in self.results)

    @property
    def determination(self) -> str:
        """``READY``, ``NOT-READY`` or ``UNMEASURED`` — the headline verdict.

        ``UNMEASURED`` is reported only when nothing is *failing* and the sole reason
        readiness is withheld is absent evidence, so the two situations can never be
        confused.
        """
        if self.ready:
            return CriterionVerdict.READY.value
        if any(item.verdict is CriterionVerdict.NOT_READY for item in self.results):
            return CriterionVerdict.NOT_READY.value
        return CriterionVerdict.UNMEASURED.value

    def failing(self) -> tuple[CriterionResult, ...]:
        """Every measured, unsatisfied criterion."""
        return tuple(item for item in self.results if item.verdict is CriterionVerdict.NOT_READY)

    def unmeasured(self) -> tuple[CriterionResult, ...]:
        """Every criterion whose evidence was not gathered in this run."""
        return tuple(item for item in self.results if item.verdict is CriterionVerdict.UNMEASURED)

    def blockers(self) -> tuple[str, ...]:
        """Every blocker across every criterion, prefixed by the criterion that raised it."""
        found: list[str] = []
        for item in self.results:
            if item.discharged:
                continue
            if item.blockers:
                found.extend(f"{item.criterion_id}: {blocker}" for blocker in item.blockers)
            else:
                found.append(f"{item.criterion_id}: {item.summary}")
        return tuple(found)

    def counts(self) -> dict[str, int]:
        """Headline counts of the freeze determination."""
        return {
            "criteria": self.total,
            "ready": sum(1 for item in self.results if item.discharged),
            "not_ready": len(self.failing()),
            "unmeasured": len(self.unmeasured()),
        }

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this determination."""
        return {
            "determination_id": self.determination_id,
            "determination": self.determination,
            "ready": self.ready,
            "counts": self.counts(),
            "maturity_percentage": self.maturity_percentage,
            "conformance_id": self.conformance_id,
            "convergence_id": self.convergence_id,
            "blockers": list(self.blockers()),
            "results": [item.to_dict() for item in self.results],
        }

    def summary(self) -> dict[str, Any]:
        """A compact projection without the per-blocker detail."""
        return {
            "determination_id": self.determination_id,
            "determination": self.determination,
            "ready": self.ready,
            "counts": self.counts(),
            "maturity_percentage": self.maturity_percentage,
            "results": [
                {
                    "criterion_id": item.criterion_id,
                    "verdict": item.verdict.value,
                    "requirement": item.requirement,
                    "summary": item.summary,
                }
                for item in self.results
            ],
            "blockers": list(self.blockers()),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this determination."""
        return content_hash(self.to_dict())


class FreezeCriteriaRegister:
    """A deterministic, fail-closed registry of declared freeze criteria."""

    __slots__ = ("_criteria", "_register_id")

    def __init__(
        self,
        criteria: Iterable[FreezeCriterion] = (),
        *,
        register_id: str = "foundation.freeze",
    ) -> None:
        self._criteria: dict[str, FreezeCriterion] = {}
        self._register_id = register_id.strip() or "foundation.freeze"
        for criterion in criteria:
            self.add(criterion)

    def add(self, criterion: FreezeCriterion) -> FreezeCriterion:
        """Declare ``criterion``; fail-closed on an identity collision."""
        if not isinstance(criterion, FreezeCriterion):
            raise FoundationFreezeError("register accepts only FreezeCriterion values")
        existing = self._criteria.get(criterion.criterion_id)
        if existing is not None:
            if existing.fingerprint() == criterion.fingerprint():
                return existing
            raise FoundationFreezeError(
                "criterion already declared with a different body",
                criterion_id=criterion.criterion_id,
            )
        self._criteria[criterion.criterion_id] = criterion
        return criterion

    def get(self, criterion_id: str) -> FreezeCriterion | None:
        """The declared criterion ``criterion_id``, or ``None``."""
        return self._criteria.get(criterion_id)

    def require(self, criterion_id: str) -> FreezeCriterion:
        """The declared criterion ``criterion_id`` (fail-closed)."""
        criterion = self.get(criterion_id)
        if criterion is None:
            raise FoundationFreezeError("unknown freeze criterion", criterion_id=str(criterion_id))
        return criterion

    @property
    def register_id(self) -> str:
        """The declared identity of this register."""
        return self._register_id

    @property
    def count(self) -> int:
        """How many criteria are declared."""
        return len(self._criteria)

    def ordered(self) -> tuple[FreezeCriterion, ...]:
        """Every criterion in deterministic identity order."""
        return tuple(sorted(self._criteria.values(), key=lambda item: item.criterion_id))

    def ids(self) -> tuple[str, ...]:
        """Every declared criterion identity, in order."""
        return tuple(item.criterion_id for item in self.ordered())

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> FreezeCriteriaRegister:
        """Build a register from the declared freeze document (fail-closed)."""
        if not isinstance(document, Mapping):
            raise FoundationFreezeError("freeze document must be a mapping")
        criteria = document.get("criteria")
        if not isinstance(criteria, Sequence) or isinstance(criteria, str | bytes):
            raise FoundationFreezeError("freeze document requires a 'criteria' sequence")
        register = cls(register_id=str(document.get("register_id", "")))
        for criterion in criteria:
            register.add(FreezeCriterion.from_document(criterion))
        if register.count == 0:
            raise FoundationFreezeError("freeze register declares no criterion")
        return register

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this register."""
        return {
            "register_id": self._register_id,
            "criterion_count": self.count,
            "criteria": [item.to_dict() for item in self.ordered()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this register."""
        return content_hash(self.to_dict())


def catalog_path(filename: str = DEFAULT_FREEZE_FILENAME) -> Path:
    """The packaged catalogue path for ``filename``."""
    return Path(__file__).resolve().parent / CATALOG_DIRNAME / filename


def load_freeze_criteria(path: Path | str) -> FreezeCriteriaRegister:
    """Load a declared freeze register from ``path`` (fail-closed)."""
    target = Path(path)
    try:
        document = json.loads(target.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FoundationFreezeError(
            "freeze register could not be read", path=str(target), detail=str(exc)
        ) from exc
    return FreezeCriteriaRegister.from_document(document)


def default_freeze_criteria(filename: str = DEFAULT_FREEZE_FILENAME) -> FreezeCriteriaRegister:
    """The freeze register shipped in the packaged catalogue."""
    return load_freeze_criteria(catalog_path(filename))


class FreezeReadinessEngine:
    """Measures the declared freeze criteria against the determinations that already exist."""

    __slots__ = ("_register", "_project_root", "_run_commands", "_timeout")

    def __init__(
        self,
        register: FreezeCriteriaRegister,
        *,
        project_root: Path | str = ".",
        run_commands: bool = False,
        timeout: int = 1800,
    ) -> None:
        if not isinstance(register, FreezeCriteriaRegister):
            raise FoundationFreezeError("freeze readiness requires a FreezeCriteriaRegister")
        self._register = register
        self._project_root = Path(project_root)
        self._run_commands = bool(run_commands)
        self._timeout = int(timeout)

    @property
    def register(self) -> FreezeCriteriaRegister:
        """The declared criteria this engine measures."""
        return self._register

    @property
    def runs_commands(self) -> bool:
        """Whether declared verification commands are executed in this run."""
        return self._run_commands

    def _measure_gates(
        self,
        criterion: FreezeCriterion,
        conformance: ConformanceDetermination,
        *,
        platform_scope: bool,
    ) -> CriterionResult:
        """Every named gate passed for every subject in scope."""
        blockers: list[str] = []
        measured = 0
        if platform_scope:
            index = {item.gate: item for item in conformance.platform_results}
            for gate in criterion.gates:
                result = index.get(gate)
                if result is None:
                    blockers.append(f"{gate} was not measured over the platform")
                    continue
                measured += 1
                if not result.satisfied:
                    blockers.extend(f"PLATFORM/{gate}: {finding}" for finding in result.findings)
                    if not result.findings:
                        blockers.append(f"PLATFORM/{gate}: {result.summary}")
        else:
            for capability in conformance.capabilities:
                index = capability.by_gate()
                for gate in criterion.gates:
                    result = index.get(gate)
                    if result is None:
                        blockers.append(f"{capability.capability_id}/{gate} was not measured")
                        continue
                    measured += 1
                    if not result.satisfied:
                        blockers.append(f"{capability.capability_id}/{gate}: {result.summary}")
        if measured == 0:
            return CriterionResult.create(
                criterion,
                CriterionVerdict.UNMEASURED,
                summary="no declared gate was measured; readiness is withheld",
                blockers=blockers,
            )
        if blockers:
            return CriterionResult.create(
                criterion,
                CriterionVerdict.NOT_READY,
                summary=f"{len(blockers)} gate results withhold this criterion",
                blockers=blockers,
            )
        return CriterionResult.create(
            criterion,
            CriterionVerdict.READY,
            summary=f"{measured} gate results discharge this criterion",
        )

    def _measure(
        self,
        criterion: FreezeCriterion,
        conformance: ConformanceDetermination | None,
        convergence: ConvergenceDetermination | None,
    ) -> CriterionResult:
        """Measure one criterion from the evidence available in this run."""
        kind = criterion.kind

        if kind in (
            CriterionKind.GATES,
            CriterionKind.PLATFORM_GATES,
            CriterionKind.NO_FAULT,
            CriterionKind.MATURITY,
            CriterionKind.DEPENDENCY_ORDER,
        ):
            if conformance is None:
                return CriterionResult.create(
                    criterion,
                    CriterionVerdict.UNMEASURED,
                    summary="no conformance determination was supplied",
                )

        if kind in (CriterionKind.NO_DUPLICATES, CriterionKind.MODELS_CONVERGED):
            if convergence is None:
                return CriterionResult.create(
                    criterion,
                    CriterionVerdict.UNMEASURED,
                    summary="no convergence determination was supplied",
                )

        if kind is CriterionKind.GATES:
            return self._measure_gates(criterion, conformance, platform_scope=False)

        if kind is CriterionKind.PLATFORM_GATES:
            return self._measure_gates(criterion, conformance, platform_scope=True)

        if kind is CriterionKind.NO_FAULT:
            faults = [
                f"{item.subject}/{item.gate}: {item.summary}"
                for item in conformance.failures()
                if item.verdict is Verdict.FAULT
            ]
            return CriterionResult.create(
                criterion,
                CriterionVerdict.READY if not faults else CriterionVerdict.NOT_READY,
                summary=(
                    "every constitutional probe executed to a verdict; no architecture is "
                    "unresolved"
                    if not faults
                    else f"{len(faults)} probes could not execute"
                ),
                blockers=faults,
            )

        if kind is CriterionKind.MATURITY:
            value = conformance.maturity_percentage
            met = value >= criterion.threshold
            return CriterionResult.create(
                criterion,
                CriterionVerdict.READY if met else CriterionVerdict.NOT_READY,
                summary=f"measured Foundation maturity {value}% against a {criterion.threshold}% "
                "threshold",
                blockers=()
                if met
                else tuple(
                    f"{item.capability_id}: {item.maturity_percentage}% maturity"
                    for item in conformance.capabilities
                    if item.maturity_percentage < criterion.threshold
                ),
            )

        if kind is CriterionKind.DEPENDENCY_ORDER:
            try:
                order = conformance and None
                del order
                from platform.universal_foundation.conformance import default_capability_register

                register = default_capability_register()
                resolved = register.dependency_order()
            except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
                return CriterionResult.create(
                    criterion,
                    CriterionVerdict.NOT_READY,
                    summary="the capability dependency order does not resolve",
                    blockers=(f"{type(exc).__name__}: {exc}",),
                )
            return CriterionResult.create(
                criterion,
                CriterionVerdict.READY,
                summary=f"a total dependency order over {len(resolved)} capabilities resolves "
                "with every dependency known and no cycle",
            )

        if kind is CriterionKind.NO_DUPLICATES:
            duplicates = convergence.duplicates
            return CriterionResult.create(
                criterion,
                CriterionVerdict.READY if duplicates == 0 else CriterionVerdict.NOT_READY,
                summary=f"{convergence.total} constitutional models carry {duplicates} surplus "
                "live implementations",
                blockers=tuple(
                    f"{item.model_id}/{item.locator}: {item.observed}"
                    for item in convergence.competing()
                ),
            )

        if kind is CriterionKind.MODELS_CONVERGED:
            blockers: list[str] = []
            for model_id in criterion.models:
                try:
                    model = convergence.model(model_id)
                except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
                    blockers.append(f"{model_id}: not declared ({exc})")
                    continue
                if not model.converged:
                    blockers.append(
                        f"{model_id}: {model.live_implementations} live implementations — "
                        f"{model.detail or 'a subordinate holds a competing definition'}"
                    )
            return CriterionResult.create(
                criterion,
                CriterionVerdict.READY if not blockers else CriterionVerdict.NOT_READY,
                summary=f"{len(criterion.models)} named models each have exactly one live answer"
                if not blockers
                else f"{len(blockers)} named models are not converged",
                blockers=blockers,
            )

        if kind is CriterionKind.COMMAND:
            if not self._run_commands:
                return CriterionResult.create(
                    criterion,
                    CriterionVerdict.UNMEASURED,
                    summary=f"declared command was not executed in this run: {criterion.command}",
                    blockers=(criterion.command,),
                )
            argv = shlex.split(criterion.command)
            try:
                completed = subprocess.run(  # noqa: S603 - declared command, never user input
                    argv,
                    cwd=self._project_root,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError) as exc:
                return CriterionResult.create(
                    criterion,
                    CriterionVerdict.NOT_READY,
                    summary="the declared verification command could not be executed",
                    blockers=(f"{criterion.command}: {exc}",),
                )
            if completed.returncode == 0:
                return CriterionResult.create(
                    criterion,
                    CriterionVerdict.READY,
                    summary=f"'{criterion.command}' exited 0",
                )
            tail = (completed.stdout or completed.stderr or "").strip().splitlines()[-5:]
            return CriterionResult.create(
                criterion,
                CriterionVerdict.NOT_READY,
                summary=f"'{criterion.command}' exited {completed.returncode}",
                blockers=tuple(tail) or (criterion.command,),
            )

        raise FoundationFreezeError(  # pragma: no cover - the kind set is closed
            "no measurement is bound to this criterion kind",
            criterion_id=criterion.criterion_id,
            kind=kind.value,
        )

    def measure(
        self,
        *,
        conformance: ConformanceDetermination | None = None,
        convergence: ConvergenceDetermination | None = None,
    ) -> FreezeDetermination:
        """Measure every declared criterion against the evidence supplied."""
        results = tuple(
            self._measure(criterion, conformance, convergence)
            for criterion in self._register.ordered()
        )
        return FreezeDetermination.create(
            results,
            conformance_id=conformance.determination_id if conformance else "",
            convergence_id=convergence.determination_id if convergence else "",
            maturity_percentage=conformance.maturity_percentage if conformance else 0.0,
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this engine's composition."""
        return {"register": self._register.to_dict(), "runs_commands": self._run_commands}

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this engine's composition."""
        return content_hash(self.to_dict())


def bootstrap_freeze_readiness(
    register: FreezeCriteriaRegister | Path | str | None = None,
    *,
    project_root: Path | str = ".",
    run_commands: bool = False,
) -> FreezeReadinessEngine:
    """Compose the freeze readiness engine over a declared criteria register."""
    if register is None:
        resolved = default_freeze_criteria()
    elif isinstance(register, FreezeCriteriaRegister):
        resolved = register
    else:
        resolved = load_freeze_criteria(register)
    return FreezeReadinessEngine(resolved, project_root=project_root, run_commands=run_commands)


__all__ = [
    "CATALOG_DIRNAME",
    "DEFAULT_FREEZE_FILENAME",
    "CriterionKind",
    "CriterionResult",
    "CriterionVerdict",
    "FreezeCriteriaRegister",
    "FreezeCriterion",
    "FreezeDetermination",
    "FreezeReadinessEngine",
    "bootstrap_freeze_readiness",
    "catalog_path",
    "default_freeze_criteria",
    "load_freeze_criteria",
]

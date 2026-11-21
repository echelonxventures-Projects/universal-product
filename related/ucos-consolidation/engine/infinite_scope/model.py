"""UISD-000001 Part 01 — the declaration model.

Every law, axis, disclosure and preserved site is DATA in
``00-MASTER/UISD-000001/uisd-declaration.json``. This module rehydrates that data and
refuses to construct a contract that could not be measured. It contains no law text, no
enumeration member, no path and no phrase: rehydrating a declaration that has lost a
section fails here rather than producing a gate that silently measures less.

The one structural rule worth stating, because it is the difference between this and a
checklist: :meth:`InfiniteScopeContract.validate` refuses **both** directions. A law
naming a check that does not exist is manual governance. A check that exists but no law
claims is dead code that looks like enforcement — the same defect ``GP-4`` records for a
flag that is declared and never read.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.uckp.payload import canonical_payload


class InfiniteScopeError(RuntimeError):
    """The declaration or contract is unusable. A FAULT, never a verdict."""

    def __init__(self, message: str, *, subject: str | None = None) -> None:
        super().__init__(message if subject is None else f"{message}: {subject}")
        self.subject = subject


def _require_mapping(doc: Any, section: str) -> Mapping[str, Any]:
    """Return ``doc[section]`` as a mapping, or fail closed."""
    value = doc.get(section) if isinstance(doc, Mapping) else None
    if not isinstance(value, Mapping):
        raise InfiniteScopeError("declaration section is absent or not a mapping", subject=section)
    return value


def _require_sequence(doc: Any, section: str) -> Sequence[Any]:
    """Return ``doc[section]`` as a non-string sequence, or fail closed."""
    value = doc.get(section) if isinstance(doc, Mapping) else None
    if not isinstance(value, list):
        raise InfiniteScopeError("declaration section is absent or not a list", subject=section)
    return value


def _require_text(entry: Mapping[str, Any], key: str, context: str) -> str:
    """Return a non-empty string field, or fail closed."""
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise InfiniteScopeError(f"{context}: field {key!r} is absent or empty")
    return value


@dataclass(frozen=True, slots=True)
class Law:
    """One Infinite Scope and Direction law, and the check that computes it."""

    law_id: str
    title: str
    statement: str
    check: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> Law:
        """Rehydrate a law, refusing one that names no check."""
        law_id = _require_text(entry, "id", "law")
        return cls(
            law_id=law_id,
            title=_require_text(entry, "title", law_id),
            statement=_require_text(entry, "statement", law_id),
            check=_require_text(entry, "check", law_id),
        )


@dataclass(frozen=True, slots=True)
class ExpansionAxis:
    """One axis along which capacity is declared unbounded, and the law measuring it."""

    axis_id: str
    axis: str
    capacity: str
    measured_by: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> ExpansionAxis:
        """Rehydrate an axis."""
        axis_id = _require_text(entry, "id", "axis")
        return cls(
            axis_id=axis_id,
            axis=_require_text(entry, "axis", axis_id),
            capacity=_require_text(entry, "capacity", axis_id),
            measured_by=_require_text(entry, "measured_by", axis_id),
        )


@dataclass(frozen=True, slots=True)
class ClosedEnumeration:
    """A located closed enumeration, with what closes it and how a member is admitted."""

    disclosure_id: str
    enumeration: str
    declared_at: str
    population: int | None
    closing_invariant: str
    admission: str
    intentional: bool
    gap: str | None

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> ClosedEnumeration:
        """Rehydrate a disclosure."""
        disclosure_id = _require_text(entry, "id", "closed enumeration disclosure")
        population = entry.get("population")
        if population is not None and not isinstance(population, int):
            raise InfiniteScopeError(f"{disclosure_id}: population is neither an integer nor null")
        return cls(
            disclosure_id=disclosure_id,
            enumeration=_require_text(entry, "enumeration", disclosure_id),
            declared_at=_require_text(entry, "declared_at", disclosure_id),
            population=population,
            closing_invariant=str(entry.get("closing_invariant", "")),
            admission=str(entry.get("admission", "")),
            intentional=bool(entry.get("intentional", False)),
            gap=entry.get("gap") or None,
        )


@dataclass(frozen=True, slots=True)
class PreservedSite:
    """A located permanence-vocabulary occurrence, classified and preserved."""

    site_id: str
    path: str
    site_class: str
    occurrences: int
    reason: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> PreservedSite:
        """Rehydrate a preserved site, refusing one that records no count."""
        site_id = _require_text(entry, "id", "preserved site")
        occurrences = entry.get("occurrences")
        if not isinstance(occurrences, int) or occurrences < 0:
            raise InfiniteScopeError(f"{site_id}: occurrences is not a non-negative integer")
        return cls(
            site_id=site_id,
            path=_require_text(entry, "path", site_id),
            site_class=_require_text(entry, "class", site_id),
            occurrences=occurrences,
            reason=_require_text(entry, "reason", site_id),
        )


@dataclass(frozen=True, slots=True)
class FreezeScan:
    """The scan configuration, shared verbatim with the classification register."""

    roots: tuple[str, ...]
    root_depth_zero_only: frozenset[str]
    extensions: frozenset[str]
    excluded_directory_names: frozenset[str]
    excluded_dot_directories: bool
    phrases: tuple[str, ...]
    status_pattern: str
    classes: Mapping[str, str]
    count_enforced_classes: frozenset[str]
    preserved_sites: tuple[PreservedSite, ...]

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> FreezeScan:
        """Rehydrate the scan configuration, refusing an empty pattern set."""
        phrases = tuple(str(p).lower() for p in entry.get("phrases", []))
        status_pattern = str(entry.get("status_pattern", ""))
        if not phrases and not status_pattern:
            raise InfiniteScopeError("freeze_scan declares neither phrases nor a status pattern")
        roots = tuple(str(r) for r in entry.get("roots", []))
        if not roots:
            raise InfiniteScopeError("freeze_scan declares no roots, so it would scan nothing")
        extensions = frozenset(str(e) for e in entry.get("extensions", []))
        if not extensions:
            raise InfiniteScopeError("freeze_scan declares no extensions")
        classes = _require_mapping(entry, "classes")
        return cls(
            roots=roots,
            root_depth_zero_only=frozenset(str(r) for r in entry.get("root_depth_zero_only", [])),
            extensions=extensions,
            excluded_directory_names=frozenset(
                str(d) for d in entry.get("excluded_directory_names", [])
            ),
            excluded_dot_directories=bool(entry.get("excluded_dot_directories", True)),
            phrases=phrases,
            status_pattern=status_pattern,
            classes=dict(classes),
            count_enforced_classes=frozenset(
                str(c) for c in entry.get("count_enforced_classes", [])
            ),
            preserved_sites=tuple(
                PreservedSite.of(s) for s in _require_sequence(entry, "preserved_sites")
            ),
        )


@dataclass(frozen=True, slots=True)
class BaselineSurface:
    """A baseline-bearing surface and the temporal qualification it declares."""

    surface_id: str
    surface: str
    field: str
    qualified: bool
    sample: str | None
    deferred_to: str | None
    gap: str | None

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> BaselineSurface:
        """Rehydrate a baseline surface."""
        surface_id = _require_text(entry, "id", "baseline surface")
        return cls(
            surface_id=surface_id,
            surface=_require_text(entry, "surface", surface_id),
            field=_require_text(entry, "field", surface_id),
            qualified=bool(entry.get("qualified", False)),
            sample=entry.get("sample") or None,
            deferred_to=entry.get("deferred_to") or None,
            gap=entry.get("gap") or None,
        )


@dataclass(frozen=True, slots=True)
class DeclaredPin:
    """A disclosed verification-toolchain pin and the reason it is pinned."""

    requirement: str
    scope: str
    reason: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> DeclaredPin:
        """Rehydrate a pin, refusing one with no reason."""
        requirement = _require_text(entry, "requirement", "declared pin")
        return cls(
            requirement=requirement,
            scope=_require_text(entry, "scope", requirement),
            reason=_require_text(entry, "reason", requirement),
        )


@dataclass(frozen=True, slots=True)
class CapabilityEnumeration:
    """One capability enumeration in the seed model, and its admission path."""

    enumeration_id: str
    enumeration: str
    declared_at: str
    open_set: bool
    admission: str
    gap: str | None

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> CapabilityEnumeration:
        """Rehydrate a capability enumeration."""
        enumeration_id = _require_text(entry, "id", "capability enumeration")
        return cls(
            enumeration_id=enumeration_id,
            enumeration=_require_text(entry, "enumeration", enumeration_id),
            declared_at=_require_text(entry, "declared_at", enumeration_id),
            open_set=bool(entry.get("open", False)),
            admission=str(entry.get("admission", "")),
            gap=entry.get("gap") or None,
        )


@dataclass(frozen=True, slots=True)
class ExerciseConsumer:
    """One surface re-evaluated after a synthetic member is admitted, and its owner.

    ``expected_refusal`` is the load-bearing field. A consumer that names one is DECLARED
    to refuse today, and :func:`~engine.infinite_scope.contract.check_admission_path_exercisability`
    holds that as a ratchet in both directions: the recorded refusal must still occur, and
    a refusal nobody recorded is a finding. That is what lets a refusing exercise be
    evidence rather than a red gate — and what stops the evidence from going stale, because
    the day an owner corrects the surface the recorded refusal stops occurring and the law
    refuses until the declaration is corrected too.
    """

    kind: str
    required_owner: str
    module: str
    function: str
    paths: tuple[str, ...]
    population_tokens: tuple[str, ...]
    expected_refusal: str
    gap: str

    @classmethod
    def of(cls, entry: Mapping[str, Any], context: str) -> ExerciseConsumer:
        """Rehydrate one consumer."""
        return cls(
            kind=_require_text(entry, "kind", context),
            required_owner=_require_text(entry, "required_owner", context),
            module=str(entry.get("module", "")),
            function=str(entry.get("function", "")),
            paths=tuple(str(path) for path in entry.get("paths", ())),
            population_tokens=tuple(str(token) for token in entry.get("population_tokens", ())),
            expected_refusal=str(entry.get("expected_refusal", "")),
            gap=str(entry.get("gap", "")),
        )

    @property
    def refuses_today(self) -> bool:
        """Whether this consumer is declared to refuse the admission as things stand."""
        return bool(self.expected_refusal.strip())


@dataclass(frozen=True, slots=True)
class AdmissionExercise:
    """One declared-open population, its admission path, and what re-reads it.

    The five fields a failure must name — population, declared owner, admission path,
    refusing component and required owner — are all held here or on the consumers, so an
    evidence record is a projection of the declaration and never a string assembled in the
    engine.
    """

    exercise_id: str
    population_id: str
    declared_owner: str
    admission: str
    form: str
    target: Mapping[str, Any]
    consumers: tuple[ExerciseConsumer, ...]
    expected: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> AdmissionExercise:
        """Rehydrate one exercise."""
        exercise_id = _require_text(entry, "id", "admission exercise")
        consumers = entry.get("consumers")
        if not isinstance(consumers, list):
            raise InfiniteScopeError(f"{exercise_id}: consumers is absent or not a list")
        return cls(
            exercise_id=exercise_id,
            population_id=_require_text(entry, "population_id", exercise_id),
            declared_owner=_require_text(entry, "declared_owner", exercise_id),
            admission=str(entry.get("admission", "")),
            form=_require_text(entry, "form", exercise_id),
            target=dict(_require_mapping(entry, "target")),
            consumers=tuple(ExerciseConsumer.of(item, exercise_id) for item in consumers),
            expected=_require_text(entry, "expected", exercise_id),
        )


#: Parsed fields deliberately outside the certification identity, each with the reason it
#: cannot reach a verdict. EMPTY, and that is the honest state rather than an oversight: every
#: field of :class:`InfiniteScopeContract` is a value some law reads, and the contract holds no
#: source path — it is rehydrated from an already-parsed document, so there is nothing
#: reader-dependent to exclude.
DIGEST_EXCLUSIONS: Mapping[str, str] = {}


@dataclass(frozen=True, slots=True)
class InfiniteScopeContract:
    """The rehydrated UISD-000001 declaration."""

    artifact_id: str
    name: str
    version: str
    authority: str
    laws: tuple[Law, ...]
    axes: tuple[ExpansionAxis, ...]
    closed_enumerations: tuple[ClosedEnumeration, ...]
    direction_expansion: Mapping[str, Any]
    closure_detection: Mapping[str, Any]
    lifecycle_openness: Mapping[str, Any]
    evolution_openness: Mapping[str, Any]
    relationship_expansion: Mapping[str, Any]
    freeze_scan: FreezeScan
    baseline_surfaces: tuple[BaselineSurface, ...]
    baseline_resolver_module: str
    baseline_resolver_function: str
    technology: Mapping[str, Any]
    declared_pins: tuple[DeclaredPin, ...]
    capability_final: bool
    capability_enumerations: tuple[CapabilityEnumeration, ...]
    self_application: Mapping[str, Any]
    lifecycle_inheritance: Mapping[str, Any]
    gate: Mapping[str, Any]
    probe_id_prefix: str
    admission_exercises: tuple[AdmissionExercise, ...]

    def digest_payload(self) -> dict[str, Any]:
        """This contract's certification identity: every parsed field, minus declared exclusions.

        Inclusion is the DEFAULT, derived from :func:`dataclasses.fields`, so a field added to
        this contract is inside the identity on the day it is written rather than on the day
        somebody remembers to add it to a list. Omitting one requires naming it in
        :data:`DIGEST_EXCLUSIONS` with the reason it cannot reach a verdict, and the suite fails
        in BOTH directions — on an undeclared omission and on an exclusion naming a field this
        contract no longer has.
        """
        return canonical_payload(self, exclude=tuple(DIGEST_EXCLUSIONS))

    @classmethod
    def from_declaration(cls, doc: Mapping[str, Any]) -> InfiniteScopeContract:
        """Rehydrate the contract from the declaration document."""
        if not isinstance(doc, Mapping):
            raise InfiniteScopeError("declaration is not a mapping")
        baseline = _require_mapping(doc, "baseline_temporal_requirement")
        technology = _require_mapping(doc, "technology_evolution")
        capability = _require_mapping(doc, "capability_seed_model")
        exercisability = _require_mapping(doc, "admission_exercisability")
        return cls(
            artifact_id=_require_text(doc, "artifact_id", "declaration"),
            name=_require_text(doc, "name", "declaration"),
            version=_require_text(doc, "version", "declaration"),
            authority=_require_text(doc, "authority", "declaration"),
            laws=tuple(Law.of(entry) for entry in _require_sequence(doc, "laws")),
            axes=tuple(
                ExpansionAxis.of(entry) for entry in _require_sequence(doc, "expansion_axes")
            ),
            closed_enumerations=tuple(
                ClosedEnumeration.of(entry)
                for entry in _require_sequence(doc, "closed_enumeration_disclosures")
            ),
            direction_expansion=dict(_require_mapping(doc, "direction_expansion")),
            closure_detection=dict(_require_mapping(doc, "closure_detection")),
            lifecycle_openness=dict(_require_mapping(doc, "lifecycle_openness")),
            evolution_openness=dict(_require_mapping(doc, "evolution_openness")),
            relationship_expansion=dict(_require_mapping(doc, "relationship_expansion")),
            freeze_scan=FreezeScan.of(_require_mapping(doc, "freeze_scan")),
            baseline_surfaces=tuple(
                BaselineSurface.of(entry) for entry in _require_sequence(baseline, "surfaces")
            ),
            baseline_resolver_module=_require_text(
                baseline, "coordinate_resolver_module", "baseline_temporal_requirement"
            ),
            baseline_resolver_function=_require_text(
                baseline, "coordinate_resolver_function", "baseline_temporal_requirement"
            ),
            technology=dict(technology),
            declared_pins=tuple(
                DeclaredPin.of(entry) for entry in _require_sequence(technology, "declared_pins")
            ),
            capability_final=bool(capability.get("final", True)),
            capability_enumerations=tuple(
                CapabilityEnumeration.of(entry)
                for entry in _require_sequence(capability, "enumerations")
            ),
            self_application=dict(_require_mapping(doc, "self_application")),
            lifecycle_inheritance=dict(_require_mapping(doc, "lifecycle_inheritance")),
            gate=dict(_require_mapping(doc, "gate")),
            probe_id_prefix=str(exercisability.get("probe_id_prefix", "")),
            admission_exercises=tuple(
                AdmissionExercise.of(entry)
                for entry in _require_sequence(exercisability, "exercises")
            ),
        )

    def validate(
        self,
        available_checks: Iterable[str],
        available_forms: Iterable[str] | None = None,
    ) -> tuple[str, ...]:
        """Report every reason the contract could not be measured, all at once.

        Refuses in both directions: a law whose check is missing cannot be computed, and
        a check no law claims is dead code wearing the appearance of enforcement. The same
        both-directions rule is applied to admission-exercise forms when *available_forms*
        is supplied — an exercise naming a form nothing implements cannot be performed, and
        a form no exercise names is dead code wearing the appearance of exercisability.

        *available_forms* defaults to ``None``, meaning "the caller did not supply the form
        registry, so do not measure it". :func:`~engine.infinite_scope.contract.load_contract`
        always supplies it, so the live path is never the unmeasured one.
        """
        available = frozenset(available_checks)
        problems: list[str] = []
        if not self.laws:
            problems.append("the declaration holds no law, so the gate would measure nothing")
        claimed = {law.check for law in self.laws}
        for law in self.laws:
            if law.check not in available:
                problems.append(
                    f"{law.law_id}: names check {law.check!r}, which is not implemented"
                )
        for orphan in sorted(available - claimed):
            problems.append(f"check {orphan!r} is implemented but no law claims it")
        seen: set[str] = set()
        for law in self.laws:
            if law.law_id in seen:
                problems.append(f"{law.law_id}: declared more than once")
            seen.add(law.law_id)
        law_ids = {law.law_id for law in self.laws}
        for axis in self.axes:
            if axis.measured_by not in law_ids:
                problems.append(
                    f"{axis.axis_id}: measured_by names {axis.measured_by!r}, which is not a law"
                )
        for site_class in sorted(self.freeze_scan.count_enforced_classes):
            if site_class not in self.freeze_scan.classes:
                problems.append(
                    f"freeze_scan: count-enforced class {site_class!r} is not a declared class"
                )
        problems.extend(self._exercise_problems(available_forms))
        return tuple(problems)

    def _exercise_problems(self, available_forms: Iterable[str] | None) -> list[str]:
        """Report every reason an admission exercise could not be performed."""
        problems: list[str] = []
        seen: set[str] = set()
        for exercise in self.admission_exercises:
            if exercise.exercise_id in seen:
                problems.append(f"{exercise.exercise_id}: declared more than once")
            seen.add(exercise.exercise_id)
            if exercise.expected not in ("admitted", "refused"):
                problems.append(
                    f"{exercise.exercise_id}: expected is {exercise.expected!r}, "
                    "which is neither 'admitted' nor 'refused'"
                )
            recorded = [consumer for consumer in exercise.consumers if consumer.refuses_today]
            if exercise.expected == "refused" and not recorded:
                problems.append(
                    f"{exercise.exercise_id}: expects a refusal and records none, so the "
                    "refusing component is unnamed"
                )
            if exercise.expected == "admitted" and recorded:
                problems.append(
                    f"{exercise.exercise_id}: expects admission while recording a refusal on "
                    f"{recorded[0].required_owner}"
                )
            for consumer in recorded:
                if not consumer.gap.strip():
                    problems.append(
                        f"{exercise.exercise_id}: records a refusal on "
                        f"{consumer.required_owner} and names no gap, so it is an "
                        "undisclosed finite assumption"
                    )
        if available_forms is None:
            return problems
        forms = frozenset(available_forms)
        claimed = {exercise.form for exercise in self.admission_exercises}
        for exercise in self.admission_exercises:
            if exercise.form not in forms:
                problems.append(
                    f"{exercise.exercise_id}: names form {exercise.form!r}, "
                    "which is not implemented"
                )
        for orphan in sorted(forms - claimed):
            problems.append(f"form {orphan!r} is implemented but no exercise names it")
        return problems


__all__ = [
    "AdmissionExercise",
    "BaselineSurface",
    "CapabilityEnumeration",
    "ClosedEnumeration",
    "DeclaredPin",
    "ExerciseConsumer",
    "ExpansionAxis",
    "FreezeScan",
    "InfiniteScopeContract",
    "InfiniteScopeError",
    "Law",
    "PreservedSite",
]

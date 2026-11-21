"""UCOS-NUC-001 Part 09 — constitutional validation and certification (D-20, D-21).

Two distinct questions, kept distinct because conflating them is how a repository comes
to believe it is certified:

    * **Validation** — does the population satisfy every measurable constitutional
      invariant *right now*? :func:`validate` answers this by composing the measurements
      that already exist: the ownership gate (:mod:`engine.nucleus.ownership`), lineage
      integrity (:mod:`engine.nucleus.lineage`), lifecycle completeness and fixed-point
      replay (:mod:`engine.nucleus.lifecycle`), and evolution chain continuity
      (:mod:`engine.nucleus.evolution`). It composes; it does not re-measure.
    * **Certification** — is the *validated* population admissible as a baseline?
      :func:`certify` answers this, and it is fail-closed twice over: an invalid
      population cannot be certified, and a certification is only ever issued at the
      highest verdict the repository's own authority state permits.

The verdict ceiling
-------------------
Repository truth records the Tier-1 Constitutional Authority as **VACANT** (``VAC-01``,
``CMG-OQ-02``), which caps every verdict at ``CERTIFIED-PROVISIONAL``; ``FINALIZED`` is
held by zero baselines. That ceiling is honoured here rather than engineered around: the
highest verdict this module can emit is :attr:`Verdict.CERTIFIED_PROVISIONAL`, and the
reason is recorded in the certificate. A certificate that claimed more would be a false
certificate, and a false certificate is worse than none.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from engine.context.location import FrameRegistry, build_frame_registry
from engine.nucleus import authority
from engine.nucleus.context import (
    CONTEXT_GATES,
    bind_registry,
    context_fingerprint,
    context_measurements,
    replay_in_context,
)
from engine.nucleus.errors import CertificationError
from engine.nucleus.evolution import EvolutionLedger
from engine.nucleus.lifecycle import replay as lifecycle_replay
from engine.nucleus.lineage import CERTIFIED, VALIDATED, LineageLedger, ledger_for
from engine.nucleus.ownership import enforce
from engine.nucleus.registry import NucleusRegistry
from engine.registry.universal.identity import RegistryKind, deterministic_id
from engine.uckp.canonical import content_hash

#: The authority whose vacancy caps every verdict, recorded so the cap is auditable.
AUTHORITY_VACANCY = "VAC-01/CMG-OQ-02 — Tier-1 Constitutional Authority is VACANT"

#: The namespace constitutional certificates are registered under. The namespace is this
#: layer's to choose; the identifier is not (see :attr:`Certificate.certificate_id`).
CERTIFICATE_NAMESPACE = "ucos.certification"


class Verdict(str, Enum):
    """The verdicts this module can issue. ``FINALIZED`` is deliberately absent."""

    NOT_CERTIFIED = "NOT-CERTIFIED"
    CERTIFIED_PROVISIONAL = "CERTIFIED-PROVISIONAL"


@dataclass(frozen=True, slots=True)
class Check:
    """One named constitutional check with its measured result."""

    check_id: str
    name: str
    passed: bool
    measured: Any
    expected: Any
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "name": self.name,
            "status": "PASS" if self.passed else "FAIL",
            "measured": self.measured,
            "expected": self.expected,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The composed validation result over a whole structural population."""

    checks: tuple[Check, ...]
    population: Mapping[str, int]
    ownership: Mapping[str, Any] = field(default_factory=dict)
    context: Mapping[str, Any] = field(default_factory=dict)

    @property
    def failures(self) -> tuple[Check, ...]:
        return tuple(c for c in self.checks if not c.passed)

    @property
    def passed(self) -> bool:
        return not self.failures

    @property
    def status(self) -> str:
        return "VALID" if self.passed else "INVALID"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-validation",
            "version": "1.0.0",
            "status": self.status,
            "check_count": len(self.checks),
            "failures": [c.check_id for c in self.failures],
            "checks": [c.to_dict() for c in self.checks],
            "population": {k: self.population[k] for k in sorted(self.population)},
            "ownership_gate": dict(self.ownership),
            "context": {k: self.context[k] for k in sorted(self.context)},
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class Certificate:
    """A certification of one validated population, at the highest lawful verdict."""

    subject: str
    verdict: Verdict
    validation_digest: str
    registry_digest: str
    lineage_head: str
    ceiling_reason: str
    checks: tuple[Check, ...] = ()
    context_digest: str = ""
    frame: str = ""
    context_gates: Mapping[str, Any] = field(default_factory=dict)

    @property
    def context_bound(self) -> bool:
        """True iff this certificate names the reality it was issued in."""
        return bool(self.frame)

    @property
    def certificate_id(self) -> str:
        """A deterministic identity for exactly this certification of exactly this state.

        The context digest is part of the identity: the *same* population certified under
        two reference frames is two certifications, not one reused twice. A certificate
        that did not say which reality it was issued in would be a certificate about
        nothing in particular.

        Minted **by** the single registration authority
        (:func:`engine.registry.universal.identity.deterministic_id`). Previously this
        assembled ``"UCOS-CERT-" + digest[:12]`` inline, which placed a second
        decision-maker inside the ``CERTIFICATION`` population that authority owns: the
        result was shape-valid — ``is_well_formed`` accepted it and ``parse_kind_name``
        reported ``CERTIFICATION`` — while no authority had minted it, and the registry CLI
        mints genuine ``UCOS-CERT-<12hex>`` ids into that same space. Overlapping
        population plus an independent decision is authority duplication, so only the
        *natural key* is derived here and the identifier is delegated.
        """
        return deterministic_id(
            RegistryKind.CERTIFICATION,
            CERTIFICATE_NAMESPACE,
            content_hash(
                [
                    self.subject,
                    self.verdict.value,
                    self.validation_digest,
                    self.registry_digest,
                    self.context_digest,
                ]
            ),
        )

    @property
    def certified(self) -> bool:
        return self.verdict is Verdict.CERTIFIED_PROVISIONAL

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-certificate",
            "version": "1.0.0",
            "certificate_id": self.certificate_id,
            "subject": self.subject,
            "verdict": self.verdict.value,
            "validation_digest": self.validation_digest,
            "registry_digest": self.registry_digest,
            "lineage_head": self.lineage_head,
            "verdict_ceiling": Verdict.CERTIFIED_PROVISIONAL.value,
            "ceiling_reason": self.ceiling_reason,
            "context_digest": self.context_digest,
            "frame": self.frame,
            "context_bound": self.context_bound,
            "context_gates": {k: self.context_gates[k] for k in sorted(self.context_gates)},
            "checks": [c.to_dict() for c in self.checks],
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def _withheld_ownership(registry: NucleusRegistry) -> dict[str, int]:
    """Capabilities owned by roles the ownership authority withholds ownership from.

    Derived entirely from CEU: which roles may own is
    :func:`engine.nucleus.authority.owning_roles`, discovered from the registered
    faculties. No role name appears here, so a fourth non-owning classification is covered
    the moment it is registered.
    """
    permitted = authority.owning_roles()
    counts: dict[str, int] = {}
    for capability in registry.capabilities():
        role = registry.subject_by_id(capability.owner_id).role.value
        if role not in permitted:
            counts[role] = counts.get(role, 0) + 1
    return counts


def validate(
    registry: NucleusRegistry,
    *,
    lineage: LineageLedger | None = None,
    evolution: EvolutionLedger | None = None,
    lifecycle_subjects: Sequence[str] | None = None,
    frames: FrameRegistry | None = None,
    frame_key: str | None = None,
) -> ValidationReport:
    """Measure every constitutional invariant over ``registry`` and report.

    ``lineage`` defaults to the ledger derived from the registry, so the common case
    needs no argument. ``lifecycle_subjects`` defaults to every registered nucleus, each
    of which must run the full lifecycle to a deterministic fixed point.

    ``frames`` defaults to the declared reference-frame catalogue: the context axis
    (CV-13…CV-16) is **not** optional, because nothing in this system executes outside a
    context. ``frame_key`` is optional and stronger — supplying it binds the whole
    population to that reference frame and measures the four context gates
    (CV-CONTEXT-01…04), and it also makes the lifecycle stages run *inside* that frame
    rather than in the declaration alone.

    Order matters here, and deliberately: the registry is bound **before** a ledger is
    derived from it. A ledger derived first and bound afterwards carries the same facts in
    a different order, and its head — which every certificate cites — would then depend on
    whether the population had been validated before. Binding first makes a re-validation
    byte-identical to the first one.
    """
    catalog = frames if frames is not None else build_frame_registry()
    resolution = catalog.resolve(frame_key) if frame_key is not None else None
    if resolution is not None:
        registry.bind_context(context_fingerprint(resolution))
    ledger = lineage if lineage is not None else ledger_for(registry)
    if resolution is not None:
        bind_registry(registry, ledger, resolution)
    report = enforce(registry)
    checks: list[Check] = [
        Check(
            "CV-01",
            "ownership gate FG-18 passes",
            report.passed,
            report.status,
            "PASS",
            "; ".join(report.blocking_failures),
        ),
        Check(
            "CV-02",
            "every subject record reproduces its own identity and digest",
            all(s.is_intact() for s in registry.subjects()),
            sum(1 for s in registry.subjects() if not s.is_intact()),
            0,
        ),
        Check(
            "CV-03",
            "every capability record reproduces its own identity and digest",
            all(c.is_intact() for c in registry.capabilities()),
            sum(1 for c in registry.capabilities() if not c.is_intact()),
            0,
        ),
        Check(
            "CV-04",
            "lineage chain is intact",
            ledger.is_intact(),
            ledger.is_intact(),
            True,
        ),
        Check(
            "CV-05",
            "no registered subject lacks a lineage entry",
            not ledger.unrecorded(s.universal_id for s in registry.subjects()),
            len(ledger.unrecorded(s.universal_id for s in registry.subjects())),
            0,
        ),
        Check(
            "CV-06",
            "no selection cycle in the composition graph",
            not registry.selection_cycles(),
            len(registry.selection_cycles()),
            0,
        ),
        Check(
            "CV-07",
            "no composition and no layer owns a capability",
            not any(
                not registry.subject_by_id(cap.owner_id).may_own_capability
                for cap in registry.capabilities()
            ),
            sum(
                1
                for cap in registry.capabilities()
                if not registry.subject_by_id(cap.owner_id).may_own_capability
            ),
            0,
        ),
        Check(
            "CV-08",
            "no role the ownership authority withholds ownership from owns a capability",
            not _withheld_ownership(registry),
            sum(_withheld_ownership(registry).values()),
            0,
            # Itemised per role, so the report says *which* non-owning role holds
            # something. Previously this check compared against the literal "layer",
            # which made certification a second ownership authority.
            "; ".join(
                f"{role}={count}" for role, count in sorted(_withheld_ownership(registry).items())
            ),
        ),
    ]

    subjects = (
        tuple(lifecycle_subjects)
        if lifecycle_subjects is not None
        else tuple(n.universal_id for n in registry.nuclei())
    )
    runs = [
        replay_in_context(subject, resolution)
        if resolution is not None
        else lifecycle_replay(subject)
        for subject in subjects
    ]
    checks.append(
        Check(
            "CV-09",
            "every subject's lifecycle reaches a deterministic fixed point",
            all(run["fixed_point"] for run in runs),
            sum(1 for run in runs if not run["fixed_point"]),
            0,
            f"{len(runs)} subject(s) replayed",
        )
    )
    checks.append(
        Check(
            "CV-10",
            "every subject's lifecycle completes all declared stages",
            all(run["status"] == "COMPLETE" for run in runs),
            sum(1 for run in runs if run["status"] != "COMPLETE"),
            0,
        )
    )

    # -- the context axis (D-08…D-17): everything executes in a resolved reality ---- #
    context = context_measurements(
        catalog,
        frame_key=frame_key,
        registry=registry if resolution is not None else None,
        lineage=ledger if resolution is not None else None,
        evolution=evolution,
    )
    checks.append(
        Check(
            "CV-13",
            "the location-derived context architecture validates",
            not context["validation_violations"],
            context["validation_violations"],
            0,
            "; ".join(context["validation_failures"]),
        )
    )
    checks.append(
        Check(
            "CV-14",
            "the location-derived context architecture certifies",
            context["certified"],
            context["certified"],
            True,
            "; ".join(context["certification_failures"]),
        )
    )
    checks.append(
        Check(
            "CV-15",
            "every location-determined axis resolves in every completely declared frame",
            not context["unresolved_in_complete_frames"],
            len(context["unresolved_in_complete_frames"]),
            0,
            f"{context['complete_frames']} complete frame(s), "
            f"{context['location_determined_axes']} location-determined axes",
        )
    )
    checks.append(
        Check(
            "CV-16",
            "context resolution replays to a deterministic fixed point",
            context["replay_fixed_point"],
            context["replay_fixed_point"],
            True,
            "; ".join(context["replay_drift"]),
        )
    )
    # The four constitutional context gates. They are emitted only when a frame is named,
    # because "is this population bound to *the right* reality?" is unanswerable until a
    # reality has been named — and a check that cannot be answered must not be reported as
    # though it were passed. `certify` refuses the unbound case outright.
    if resolution is not None:
        gates = context["gates"]
        for gate_id, name, _statement in CONTEXT_GATES:
            gate = gates[gate_id]
            checks.append(
                Check(
                    gate_id,
                    f"{name.lower()}: {gate['statement'].rstrip('.').lower()}",
                    gate["passed"],
                    gate["finding_count"],
                    0,
                    "; ".join(gate["findings"]),
                )
            )

    if evolution is not None:
        checks.append(
            Check(
                "CV-18",
                "no evolution was recorded outside a resolved reference frame",
                not context.get("evolutions_without_context", []),
                len(context.get("evolutions_without_context", [])),
                0,
            )
        )
        checks.append(
            Check(
                "CV-11",
                "every evolution chain is unbroken",
                all(evolution.chain_is_unbroken(s) for s in evolution.subjects()),
                sum(1 for s in evolution.subjects() if not evolution.chain_is_unbroken(s)),
                0,
            )
        )
        checks.append(
            Check(
                "CV-12",
                "no evolution lacks lineage evidence",
                not evolution.unevidenced(),
                len(evolution.unevidenced()),
                0,
            )
        )

    ledger.record(
        VALIDATED,
        subject_id="UCOS-NUC-001",
        subject_key="nucleus-ownership-authority",
        detail={"failures": [c.check_id for c in checks if not c.passed]},
    )
    return ValidationReport(
        checks=tuple(checks),
        population=registry.counts(),
        ownership=report.to_dict(),
        context=context,
    )


def certify(
    registry: NucleusRegistry,
    *,
    subject: str = "UCOS-NUC-001",
    lineage: LineageLedger | None = None,
    evolution: EvolutionLedger | None = None,
    frames: FrameRegistry | None = None,
    frame_key: str | None = None,
    require_context: bool = False,
) -> Certificate:
    """Certify a validated population, refusing an invalid one.

    ``require_context`` makes the four context gates mandatory: without a named frame
    there is nothing for Context Bound, Resolved, Verified and Registered to be true
    *of*, so an unbound request is refused rather than certified on a smaller set of
    checks. It defaults off so that certifying the architecture itself — which is
    frame-independent by construction — stays possible; a *population* certification
    should pass it on.

    Raises:
        CertificationError: validation failed, so there is nothing certifiable, or
            ``require_context`` and no frame was named. The failing check ids are carried
            on the error, so the refusal is actionable.
    """
    if require_context and not frame_key:
        raise CertificationError(
            "a context-bound certification must name its reference frame",
            subject=subject,
            failures=[gate for gate, _name, _statement in CONTEXT_GATES],
        )
    # Bind before deriving, for the same reason `validate` does: a ledger derived from an
    # unbound registry and bound afterwards holds the same entries in a different order,
    # and `lineage_head` — which this certificate cites — would then differ between the
    # first certification of a population and every later one.
    catalog = frames if frames is not None else build_frame_registry()
    if frame_key:
        registry.bind_context(context_fingerprint(catalog.resolve(frame_key)))
    ledger = lineage if lineage is not None else ledger_for(registry)
    report = validate(
        registry, lineage=ledger, evolution=evolution, frames=catalog, frame_key=frame_key
    )
    if not report.passed:
        raise CertificationError(
            "an invalid population cannot be certified",
            subject=subject,
            failures=[c.check_id for c in report.failures],
            detail=[c.to_dict() for c in report.failures],
        )
    context_digest = str(report.context.get("context_digest", ""))
    ledger.record(
        CERTIFIED,
        subject_id=subject,
        subject_key="nucleus-ownership-authority",
        detail={
            "verdict": Verdict.CERTIFIED_PROVISIONAL.value,
            "context_digest": context_digest,
            "frame": frame_key or "",
        },
    )
    return Certificate(
        subject=subject,
        verdict=Verdict.CERTIFIED_PROVISIONAL,
        validation_digest=report.digest(),
        registry_digest=registry.digest(),
        lineage_head=ledger.head,
        ceiling_reason=AUTHORITY_VACANCY,
        checks=report.checks,
        context_digest=context_digest,
        frame=frame_key or "",
        context_gates=dict(report.context.get("gates", {})),
    )


__all__ = [
    "AUTHORITY_VACANCY",
    "Verdict",
    "Check",
    "ValidationReport",
    "Certificate",
    "validate",
    "certify",
]

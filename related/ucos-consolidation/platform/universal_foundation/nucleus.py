"""UCOS-UFC-001 — Ω Nucleus completeness (UFC-17).

An **Ω Nucleus** is the complete constitutional universe of exactly one canonical concept. It
is the atomic unit of canonical ownership, and it is *not* a module, a service or a bounded
context: those are realisations of a nucleus, never the nucleus itself.

This module measures whether a registered nucleus is actually **complete** — whether every
facet its constitutional universe is required to contain resolves to real evidence. It
deliberately does **not** introduce a second registry, a second law or a second identity
space, because "what is the atomic unit of canonical ownership" is one constitutional model
and UFC-14 permits it exactly one implementation. The declared capability register **is** the
Ω Nucleus registry; this module attaches a completeness profile to every entry in it.

Three resolution kinds, declared per facet in ``catalog/foundation-nucleus.json``:

    ``DECLARATION``  a named field of the nucleus's own declaration, required to be non-empty.
    ``GATE``         a constitutional gate, required to have **passed** for this nucleus — so
                     a facet the Constitution already proves is never proven a second, weaker
                     way, and can never disagree with it.
    ``PROFILE``      a dotted path in the nucleus's declared profile, whose leaf states either
                     ``present`` with evidence or ``not-applicable`` with a rationale.

A facet that resolves is ``RESOLVED``; one declared inapplicable with a reason is
``DECLARED-ABSENT`` and is honestly complete; one that resolves to nothing at all is
``MISSING``. The distinction is the whole point: *absent* and *undeclared* are different
facts, and only the first is a determination.

UFC-17 is measured **once over the platform** rather than per capability, because completeness
is a property of the population: a Foundation with one incomplete nucleus is an incomplete
Foundation. The measurement is therefore composed exactly as the convergence measurement is —
it consumes the conformance determination and contributes one platform gate result back — so
the article joins the Constitution without the conformance engine acquiring any knowledge of
it.

Zero enumeration: no facet, capability, package or project is named in this file. The facet
population is data, and so is the population it measures.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_foundation.conformance import (
    CapabilityDeclaration,
    CapabilityRegister,
    ConformanceDetermination,
    FacetStatus,
    GateResult,
    Verdict,
    default_capability_register,
    load_capability_register,
)
from platform.universal_foundation.constitution import (
    FoundationConstitution,
    article_for_gate,
    foundation_constitution,
)
from platform.universal_foundation.errors import FoundationNucleusError
from typing import Any

#: The packaged catalogue directory holding the declared nucleus contract.
CATALOG_DIRNAME = "catalog"

#: The declared Ω Nucleus facet contract (data, not code).
DEFAULT_NUCLEUS_FILENAME = "foundation-nucleus.json"

#: The platform gate proving every registered nucleus is constitutionally complete.
GATE_NUCLEUS_COMPLETE = "FG-17-NUCLEUS-COMPLETE"


class FacetResolution(str, Enum):
    """How one facet of the nucleus contract is discharged."""

    #: A named field of the nucleus declaration, required to be non-empty.
    DECLARATION = "declaration"
    #: A constitutional gate, required to have passed for this nucleus.
    GATE = "gate"
    #: A dotted path in the nucleus's declared profile.
    PROFILE = "profile"

    @classmethod
    def coerce(cls, value: Any, *, subject: str = "facet resolution") -> FacetResolution:
        """Coerce ``value`` to a resolution kind, failing closed (never silently)."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise FoundationNucleusError(
                    "unknown facet resolution kind", subject=subject, value=value
                ) from exc
        raise FoundationNucleusError("facet resolution kind must be a string", subject=subject)


class FacetVerdict(str, Enum):
    """The outcome of resolving one facet against one nucleus."""

    #: The declared evidence resolves; the facet is realised.
    RESOLVED = "RESOLVED"
    #: The nucleus declared the facet inapplicable and said why. Honestly complete.
    DECLARED_ABSENT = "DECLARED-ABSENT"
    #: Neither realised nor declared inapplicable. The nucleus is incomplete.
    MISSING = "MISSING"

    @property
    def complete(self) -> bool:
        """Whether this verdict leaves the nucleus complete on this facet."""
        return self is not FacetVerdict.MISSING


@dataclass(frozen=True, slots=True)
class NucleusFacet:
    """One facet an Ω Nucleus's constitutional universe is required to contain."""

    facet_id: str
    name: str
    resolution: FacetResolution
    evidence: str
    rationale: str = ""

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> NucleusFacet:
        """Build a validated facet declaration (fail-closed)."""
        if not isinstance(payload, Mapping):
            raise FoundationNucleusError("facet declaration must be a mapping")
        missing = [
            key for key in ("facet_id", "name", "resolution", "evidence") if key not in payload
        ]
        if missing:
            raise FoundationNucleusError(
                "facet declaration is incomplete",
                facet_id=str(payload.get("facet_id", "")),
                missing=",".join(missing),
            )
        facet_id = str(payload["facet_id"]).strip()
        evidence = str(payload["evidence"]).strip()
        if not facet_id or not evidence:
            raise FoundationNucleusError(
                "facet declaration requires an identity and an evidence reference",
                facet_id=facet_id,
            )
        return cls(
            facet_id=facet_id,
            name=str(payload["name"]).strip(),
            resolution=FacetResolution.coerce(payload["resolution"], subject=facet_id),
            evidence=evidence,
            rationale=str(payload.get("rationale", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this facet."""
        return {
            "facet_id": self.facet_id,
            "name": self.name,
            "resolution": self.resolution.value,
            "evidence": self.evidence,
            "rationale": self.rationale,
        }


class NucleusContract:
    """The declared facet contract every Ω Nucleus must satisfy.

    Ordered by declared facet identity and fail-closed on an unknown member, so the contract is
    a registry in the constitutional sense (UFC-05) and not a list somebody iterates.
    """

    __slots__ = ("_contract_id", "_name", "_version", "_profile_field", "_facets")

    def __init__(
        self,
        contract_id: str,
        *,
        name: str = "",
        version: str = "",
        profile_field: str = "",
        facets: Iterable[NucleusFacet] = (),
    ) -> None:
        identity = str(contract_id).strip()
        if not identity:
            raise FoundationNucleusError("nucleus contract requires an identity")
        field = str(profile_field).strip()
        if not field:
            raise FoundationNucleusError(
                "nucleus contract requires a profile field name", subject=identity
            )
        self._contract_id = identity
        self._name = str(name)
        self._version = str(version)
        self._profile_field = field
        self._facets: dict[str, NucleusFacet] = {}
        for facet in facets:
            self.add(facet)

    @property
    def contract_id(self) -> str:
        """The declared identity of this contract."""
        return self._contract_id

    @property
    def name(self) -> str:
        """The declared name of this contract."""
        return self._name

    @property
    def version(self) -> str:
        """The declared semantic version of this contract."""
        return self._version

    @property
    def profile_field(self) -> str:
        """The declaration field in which a nucleus states its profile."""
        return self._profile_field

    @property
    def count(self) -> int:
        """How many facets this contract declares."""
        return len(self._facets)

    def add(self, facet: NucleusFacet) -> NucleusFacet:
        """Register a facet, refusing a conflicting redefinition (UFC-05)."""
        if not isinstance(facet, NucleusFacet):
            raise FoundationNucleusError("only a NucleusFacet may be registered")
        existing = self._facets.get(facet.facet_id)
        if existing is not None and existing != facet:
            raise FoundationNucleusError(
                "facet is already declared with a different definition", facet_id=facet.facet_id
            )
        self._facets[facet.facet_id] = facet
        return facet

    def get(self, facet_id: str) -> NucleusFacet | None:
        """The facet ``facet_id``, or ``None`` when it is not declared."""
        return self._facets.get(facet_id)

    def require(self, facet_id: str) -> NucleusFacet:
        """The facet ``facet_id``; raises when unknown (fail-closed)."""
        facet = self._facets.get(facet_id)
        if facet is None:
            raise FoundationNucleusError("unknown nucleus facet", facet_id=facet_id)
        return facet

    def ordered(self) -> tuple[NucleusFacet, ...]:
        """Every declared facet, ordered by identity — never by insertion."""
        return tuple(self._facets[key] for key in sorted(self._facets))

    def ids(self) -> tuple[str, ...]:
        """Every declared facet identity, in canonical order."""
        return tuple(sorted(self._facets))

    def gates(self) -> tuple[str, ...]:
        """Every constitutional gate this contract resolves a facet through."""
        return tuple(
            sorted(
                {
                    facet.evidence
                    for facet in self._facets.values()
                    if facet.resolution is FacetResolution.GATE
                }
            )
        )

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> NucleusContract:
        """Build a contract from a declared document (fail-closed)."""
        if not isinstance(document, Mapping):
            raise FoundationNucleusError("nucleus contract document must be a mapping")
        facets = document.get("facets")
        if not isinstance(facets, list) or not facets:
            raise FoundationNucleusError("nucleus contract declares no facet")
        return cls(
            str(document.get("contract_id", "")),
            name=str(document.get("name", "")),
            version=str(document.get("version", "")),
            profile_field=str(document.get("profile_field", "")),
            facets=(NucleusFacet.from_document(item) for item in facets),
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this contract."""
        return {
            "contract_id": self._contract_id,
            "name": self._name,
            "version": self._version,
            "profile_field": self._profile_field,
            "count": self.count,
            "facets": [facet.to_dict() for facet in self.ordered()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this contract."""
        return content_hash(self.to_dict())


def catalog_path(filename: str = DEFAULT_NUCLEUS_FILENAME) -> Path:
    """The packaged catalogue path for ``filename``."""
    return Path(__file__).resolve().parent / CATALOG_DIRNAME / filename


def load_nucleus_contract(path: Path | str) -> NucleusContract:
    """Load a declared nucleus contract from ``path`` (fail-closed)."""
    target = Path(path)
    try:
        document = json.loads(target.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FoundationNucleusError(
            "nucleus contract could not be read", path=str(target), detail=str(exc)
        ) from exc
    return NucleusContract.from_document(document)


def default_nucleus_contract(filename: str = DEFAULT_NUCLEUS_FILENAME) -> NucleusContract:
    """The nucleus contract shipped in the packaged catalogue."""
    return load_nucleus_contract(catalog_path(filename))


@dataclass(frozen=True, slots=True)
class FacetResult:
    """The measured outcome of one facet against one nucleus, with its evidence."""

    facet_id: str
    name: str
    resolution: FacetResolution
    verdict: FacetVerdict
    detail: str = ""
    result_id: str = ""

    @classmethod
    def create(
        cls,
        facet: NucleusFacet,
        verdict: FacetVerdict,
        *,
        subject: str,
        detail: str = "",
    ) -> FacetResult:
        """Build a content-addressed facet result."""
        core = {
            "facet_id": facet.facet_id,
            "subject": subject,
            "verdict": verdict.value,
            "detail": detail,
        }
        return cls(
            facet_id=facet.facet_id,
            name=facet.name,
            resolution=facet.resolution,
            verdict=verdict,
            detail=detail,
            result_id=f"UCOS-UNCF-{content_hash(core)[:16]}",
        )

    @property
    def complete(self) -> bool:
        """Whether this facet leaves the nucleus complete."""
        return self.verdict.complete

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this result."""
        return {
            "result_id": self.result_id,
            "facet_id": self.facet_id,
            "name": self.name,
            "resolution": self.resolution.value,
            "verdict": self.verdict.value,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class NucleusCompleteness:
    """Every facet result for one nucleus, and whether its universe is complete."""

    capability_id: str
    name: str
    results: tuple[FacetResult, ...]
    completeness_id: str = ""

    @classmethod
    def create(
        cls, declaration: CapabilityDeclaration, results: Iterable[FacetResult]
    ) -> NucleusCompleteness:
        """Build a content-addressed completeness record."""
        ordered = tuple(sorted(results, key=lambda item: item.facet_id))
        core = {
            "capability_id": declaration.capability_id,
            "results": [item.result_id for item in ordered],
        }
        return cls(
            capability_id=declaration.capability_id,
            name=declaration.name,
            results=ordered,
            completeness_id=f"UCOS-UNCN-{content_hash(core)[:16]}",
        )

    @property
    def complete(self) -> bool:
        """Whether no facet is missing. A nucleus is complete or it is not."""
        return all(item.complete for item in self.results)

    def missing(self) -> tuple[FacetResult, ...]:
        """Every facet that is neither realised nor declared inapplicable."""
        return tuple(item for item in self.results if not item.complete)

    def counts(self) -> dict[str, int]:
        """How many facets landed on each verdict."""
        counts = {verdict.value: 0 for verdict in FacetVerdict}
        for item in self.results:
            counts[item.verdict.value] += 1
        return counts

    @property
    def completeness_percentage(self) -> float:
        """The share of declared facets this nucleus resolved or honestly declared absent."""
        if not self.results:
            return 0.0
        complete = sum(1 for item in self.results if item.complete)
        return round(complete / len(self.results) * 100, 4)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this record."""
        return {
            "completeness_id": self.completeness_id,
            "capability_id": self.capability_id,
            "name": self.name,
            "complete": self.complete,
            "completeness_percentage": self.completeness_percentage,
            "counts": self.counts(),
            "results": [item.to_dict() for item in self.results],
        }


@dataclass(frozen=True, slots=True)
class NucleusDetermination:
    """The immutable determination of every registered nucleus against the facet contract."""

    contract_id: str
    facet_total: int
    nuclei: tuple[NucleusCompleteness, ...]
    gate_results: tuple[GateResult, ...]
    determination_id: str = ""

    @classmethod
    def create(
        cls,
        contract: NucleusContract,
        nuclei: Iterable[NucleusCompleteness],
        gate_results: Iterable[GateResult],
    ) -> NucleusDetermination:
        """Build a content-addressed nucleus determination."""
        ordered = tuple(sorted(nuclei, key=lambda item: item.capability_id))
        gates = tuple(sorted(gate_results, key=lambda item: item.gate))
        core = {
            "contract_id": contract.contract_id,
            "nuclei": [item.completeness_id for item in ordered],
            "gates": [item.result_id for item in gates],
        }
        return cls(
            contract_id=contract.contract_id,
            facet_total=contract.count,
            nuclei=ordered,
            gate_results=gates,
            determination_id=f"UCOS-UNCD-{content_hash(core)[:16]}",
        )

    @property
    def complete(self) -> bool:
        """Whether every registered nucleus is constitutionally complete."""
        return bool(self.nuclei) and all(item.complete for item in self.nuclei)

    def blockers(self) -> tuple[str, ...]:
        """``capability:facet`` for every missing facet, in canonical order."""
        return tuple(
            f"{nucleus.capability_id}:{result.facet_id}"
            for nucleus in self.nuclei
            for result in nucleus.missing()
        )

    def counts(self) -> dict[str, int]:
        """The headline population counts of this determination."""
        return {
            "nuclei": len(self.nuclei),
            "complete": sum(1 for item in self.nuclei if item.complete),
            "facets": self.facet_total,
            "missing": len(self.blockers()),
        }

    @property
    def completeness_percentage(self) -> float:
        """The share of registered nuclei that are complete."""
        if not self.nuclei:
            return 0.0
        complete = sum(1 for item in self.nuclei if item.complete)
        return round(complete / len(self.nuclei) * 100, 4)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this determination."""
        return {
            "determination_id": self.determination_id,
            "contract_id": self.contract_id,
            "complete": self.complete,
            "completeness_percentage": self.completeness_percentage,
            "counts": self.counts(),
            "blockers": list(self.blockers()),
            "nuclei": [item.to_dict() for item in self.nuclei],
            "gate_results": [item.to_dict() for item in self.gate_results],
        }

    def summary(self) -> dict[str, Any]:
        """A compact projection: the headline numbers without the per-facet detail."""
        return {
            "determination_id": self.determination_id,
            "contract_id": self.contract_id,
            "complete": self.complete,
            "completeness_percentage": self.completeness_percentage,
            "counts": self.counts(),
            "blockers": list(self.blockers()),
            "nuclei": [
                {
                    "capability_id": item.capability_id,
                    "complete": item.complete,
                    "completeness_percentage": item.completeness_percentage,
                    "counts": item.counts(),
                }
                for item in self.nuclei
            ],
            "gate_results": [item.to_dict() for item in self.gate_results],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this determination."""
        return content_hash(self.to_dict())


def _resolve_path(payload: Mapping[str, Any], path: str) -> Any:
    """Walk a dotted path through a mapping, returning ``None`` where it does not lead."""
    current: Any = payload
    for segment in path.split("."):
        if not isinstance(current, Mapping) or segment not in current:
            return None
        current = current[segment]
    return current


class NucleusCompletenessEngine:
    """Measures whether every registered Ω Nucleus contains the facets the contract requires."""

    __slots__ = ("_contract", "_register", "_constitution")

    def __init__(
        self,
        contract: NucleusContract,
        register: CapabilityRegister,
        *,
        constitution: FoundationConstitution | None = None,
    ) -> None:
        if not isinstance(contract, NucleusContract):
            raise FoundationNucleusError("nucleus completeness requires a NucleusContract")
        if not isinstance(register, CapabilityRegister):
            raise FoundationNucleusError("nucleus completeness requires a CapabilityRegister")
        self._contract = contract
        self._register = register
        self._constitution = constitution or foundation_constitution()
        for gate in contract.gates():
            article_for_gate(gate)

    @property
    def contract(self) -> NucleusContract:
        """The declared facet contract this engine measures against."""
        return self._contract

    @property
    def register(self) -> CapabilityRegister:
        """The nucleus population this engine measures. There is no second register."""
        return self._register

    @property
    def constitution(self) -> FoundationConstitution:
        """The law whose gates this contract resolves facets through."""
        return self._constitution

    # ------------------------------------------------------------- execution

    def measure_facet(
        self,
        declaration: CapabilityDeclaration,
        facet: NucleusFacet,
        gates: Mapping[str, GateResult],
    ) -> FacetResult:
        """Resolve one facet against one nucleus, containing every absence as a verdict."""
        subject = declaration.capability_id
        if facet.resolution is FacetResolution.GATE:
            result = gates.get(facet.evidence)
            if result is None:
                return FacetResult.create(
                    facet,
                    FacetVerdict.MISSING,
                    subject=subject,
                    detail=f"gate {facet.evidence} was not measured for this nucleus",
                )
            if not result.satisfied:
                return FacetResult.create(
                    facet,
                    FacetVerdict.MISSING,
                    subject=subject,
                    detail=f"gate {facet.evidence} returned {result.verdict.value}",
                )
            return FacetResult.create(
                facet,
                FacetVerdict.RESOLVED,
                subject=subject,
                detail=f"proven by {facet.evidence}",
            )

        if facet.resolution is FacetResolution.DECLARATION:
            value = _resolve_path(declaration.to_dict(), facet.evidence)
            if value in (None, "", [], {}):
                return FacetResult.create(
                    facet,
                    FacetVerdict.MISSING,
                    subject=subject,
                    detail=f"declaration field '{facet.evidence}' is absent or empty",
                )
            return FacetResult.create(
                facet,
                FacetVerdict.RESOLVED,
                subject=subject,
                detail=f"declared at '{facet.evidence}'",
            )

        entry = declaration.nucleus.get(facet.evidence)
        if entry is None:
            return FacetResult.create(
                facet,
                FacetVerdict.MISSING,
                subject=subject,
                detail=f"profile states nothing at '{facet.evidence}'",
            )
        if entry.status is FacetStatus.NOT_APPLICABLE:
            return FacetResult.create(
                facet, FacetVerdict.DECLARED_ABSENT, subject=subject, detail=entry.detail
            )
        return FacetResult.create(
            facet, FacetVerdict.RESOLVED, subject=subject, detail=entry.detail
        )

    def measure_nucleus(
        self, declaration: CapabilityDeclaration, gates: Mapping[str, GateResult]
    ) -> NucleusCompleteness:
        """Resolve every declared facet against one nucleus."""
        return NucleusCompleteness.create(
            declaration,
            (self.measure_facet(declaration, facet, gates) for facet in self._contract.ordered()),
        )

    def measure(self, *, conformance: ConformanceDetermination) -> NucleusDetermination:
        """Measure the whole population, and prove UFC-17 over it.

        The conformance determination is an *input*, not a peer measurement: every gate-resolved
        facet reads the verdict the Constitution already reached, so completeness can never
        report a facet proven that conformance reports failed.
        """
        if not isinstance(conformance, ConformanceDetermination):
            raise FoundationNucleusError(
                "nucleus completeness requires a ConformanceDetermination to resolve gate facets"
            )
        by_capability = {item.capability_id: item.by_gate() for item in conformance.capabilities}
        nuclei: list[NucleusCompleteness] = []
        for declaration in self._register.ordered():
            gates = by_capability.get(declaration.capability_id)
            if gates is None:
                raise FoundationNucleusError(
                    "registered nucleus was not measured for conformance",
                    capability_id=declaration.capability_id,
                )
            nuclei.append(self.measure_nucleus(declaration, gates))
        return NucleusDetermination.create(self._contract, nuclei, (self._gate(nuclei),))

    def _gate(self, nuclei: Iterable[NucleusCompleteness]) -> GateResult:
        """The one platform-scoped result UFC-17 contributes to the determination."""
        measured = tuple(nuclei)
        findings = tuple(
            f"{nucleus.capability_id}: {result.facet_id} {result.name} — {result.detail}"
            for nucleus in measured
            for result in nucleus.missing()
        )
        article = article_for_gate(GATE_NUCLEUS_COMPLETE)
        if not measured:
            return GateResult.create(
                GATE_NUCLEUS_COMPLETE,
                article.article_id,
                "PLATFORM",
                Verdict.FAULT,
                summary="no nucleus was measured, so completeness cannot be asserted",
            )
        if findings:
            return GateResult.create(
                GATE_NUCLEUS_COMPLETE,
                article.article_id,
                "PLATFORM",
                Verdict.FAIL,
                summary=f"{len(findings)} facets are neither realised nor declared inapplicable",
                findings=findings,
            )
        return GateResult.create(
            GATE_NUCLEUS_COMPLETE,
            article.article_id,
            "PLATFORM",
            Verdict.PASS,
            summary=(
                f"{len(measured)} nuclei each resolve every one of "
                f"{self._contract.count} declared facets"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this engine's composition."""
        return {
            "contract": self._contract.to_dict(),
            "register": self._register.to_dict(),
            "constitution": self._constitution.to_dict(),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this engine's composition."""
        return content_hash(self.to_dict())


def bootstrap_nucleus_completeness(
    contract: NucleusContract | Path | str | None = None,
    *,
    register: CapabilityRegister | Path | str | None = None,
) -> NucleusCompletenessEngine:
    """Compose the completeness engine over a declared contract and the nucleus register."""
    if contract is None:
        resolved_contract = default_nucleus_contract()
    elif isinstance(contract, NucleusContract):
        resolved_contract = contract
    else:
        resolved_contract = load_nucleus_contract(contract)

    if register is None:
        resolved_register = default_capability_register()
    elif isinstance(register, CapabilityRegister):
        resolved_register = register
    else:
        resolved_register = load_capability_register(register)
    return NucleusCompletenessEngine(resolved_contract, resolved_register)


__all__ = [
    "CATALOG_DIRNAME",
    "DEFAULT_NUCLEUS_FILENAME",
    "GATE_NUCLEUS_COMPLETE",
    "FacetResolution",
    "FacetResult",
    "FacetVerdict",
    "NucleusCompleteness",
    "NucleusCompletenessEngine",
    "NucleusContract",
    "NucleusDetermination",
    "NucleusFacet",
    "bootstrap_nucleus_completeness",
    "catalog_path",
    "default_nucleus_contract",
    "load_nucleus_contract",
]

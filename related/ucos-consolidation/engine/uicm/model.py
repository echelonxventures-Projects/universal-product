"""UCOS-UICM-000001 — the closure object model and the closure state machine.

This module is the home of exactly one of the three capabilities UICM was admitted to
create: **the closure state machine**. Discovery located no enumeration with these six
members and no transition table over them. The nearest analogues in the repository model
something else — ``engine.uaue.gate.EXIT_CLOSED`` with ``GateReport.open`` is a gate
verdict, and ``engine.uckp.validation``'s ``SATISFIED`` / ``VIOLATED`` / ``UNMEASURED``
is an invariant verdict. Neither models a closure *lifecycle*, which is what a matrix
cell needs: a cell is registered before it is measured, and measured before it is
adjudicated, and a pass state must be distinguishable from "nobody has looked yet".

Everything else in this module is a value object over declared truth. The states, the
dimensions, the population rule and the sources all live in
``00-MASTER/UCOS-UICM-000001/uicm.json``; this module holds the *types* and the
transition algebra, and :func:`ClosureDeclaration.require_state_conformance` fails closed
if the declaration and :class:`ClosureState` ever cease to describe the same set. A
vocabulary duplicated across a declaration and an enum is a vocabulary that will drift,
so the drift is measured rather than trusted (UICM-INV-01).

Two things this module deliberately does not do: it mints no identifier, and it hashes
nothing itself. Identity is read from the canonical owners named in the declaration, and
every digest is computed through :func:`engine.uckp.canonical.content_hash` — the single
serialization primitive whose non-duplication ``engine.uckp.validation`` enforces by AST
scan over every module in ``engine`` and ``platform``.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from engine.foundation.obs.errors import FoundationError
from engine.uckp.canonical import canonical_json, content_hash

#: The declaration file name, relative to the programme's operational home.
DECLARATION_FILENAME = "uicm.json"

#: The declared section carrying resolution routing: which instrument closes a gap of each
#: dimension, and which located gate validates the change. Read by the engine and
#: deliberately absent from :meth:`ClosureDeclaration.to_dict`, so the declaration digest
#: continues to identify *what closure means* rather than how a gap is routed.
RESOLUTION_SECTION = "resolution_bindings"

#: The sections a declaration must carry for the engine to run at all. A declaration
#: missing any of them is unusable, and an unusable declaration yields no verdict.
REQUIRED_SECTIONS: tuple[str, ...] = (
    "programme",
    "canonical_sources",
    "population",
    "closure_states",
    "state_rules",
    "closure_dimensions",
    "resolution_bindings",
    "lifecycle_crosswalk",
    "certification_binding",
    "gap_classification",
    "invariants",
    "record_set",
    "determinism",
    "exit_criteria",
)


class ClosureError(FoundationError):
    """Raised when closure measurement cannot proceed or a closure rule is broken."""


class ClosureDeclarationError(ClosureError):
    """Raised when the declaration is absent, unparseable or incomplete (fail closed)."""


class ClosureStateError(ClosureError):
    """Raised when a state is unknown or a transition is not declared."""


class ClosureState(str, Enum):
    """The six states a closure cell may occupy.

    The order of definition is the lifecycle order, and it is meaningful: a cell begins
    at :attr:`DISCOVERED` because an obligation exists before anyone has measured it,
    and the distinction between "not yet measured" and "measured and failing" is the
    distinction that makes an unmeasured dimension impossible to report as a pass.

    :attr:`SUPERSEDED` is terminal and historical. No state is ever edited in place: a
    state changes only because a *new* observation of the same coordinate was appended,
    and the observation it replaced becomes SUPERSEDED. That is what makes the registers
    append-only in substance rather than only in method naming — a correction adds a
    record and destroys none, so the prior reading stays readable forever.
    """

    DISCOVERED = "DISCOVERED"
    MEASURED = "MEASURED"
    OPEN = "OPEN"
    BLOCKED = "BLOCKED"
    CLOSED = "CLOSED"
    CERTIFIED = "CERTIFIED"
    SUPERSEDED = "SUPERSEDED"

    @classmethod
    def coerce(cls, value: Any) -> ClosureState:
        """Return the state named by ``value``, or fail closed.

        Coercion never guesses: an unrecognised name is an error rather than a default,
        because a defaulted state is a claim nobody measured.
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise ClosureStateError(f"unknown closure state: {value!r}") from exc
        raise ClosureStateError(f"closure state must be a string, got {type(value).__name__}")

    @property
    def ordinal(self) -> int:
        """The lifecycle position, 1-based."""
        return _STATE_ORDER.index(self) + 1

    @property
    def is_pass(self) -> bool:
        """True iff the state asserts the dimension is closed."""
        return self in _PASS_STATES

    @property
    def requires_evidence(self) -> bool:
        """True iff a cell in this state must carry a non-empty evidence digest."""
        return self is not ClosureState.DISCOVERED

    @property
    def is_terminal(self) -> bool:
        """True iff no transition leads out of this state."""
        return not _TRANSITIONS[self]

    @property
    def is_historical(self) -> bool:
        """True iff this state marks a record that a later observation replaced."""
        return self is ClosureState.SUPERSEDED

    @property
    def requires_gap(self) -> bool:
        """True iff a cell in this state must have a registered gap."""
        return self in _GAP_STATES

    def may_transition_to(self, target: ClosureState) -> bool:
        """True iff moving from this state to ``target`` is a declared transition."""
        return target in _TRANSITIONS[self]

    def require_transition_to(self, target: ClosureState) -> ClosureState:
        """Return ``target``, or fail closed if the transition is not declared."""
        if not self.may_transition_to(target):
            raise ClosureStateError(f"undeclared closure transition {self.value} -> {target.value}")
        return target


_STATE_ORDER: tuple[ClosureState, ...] = tuple(ClosureState)

_PASS_STATES: frozenset[ClosureState] = frozenset({ClosureState.CLOSED, ClosureState.CERTIFIED})

_GAP_STATES: frozenset[ClosureState] = frozenset({ClosureState.OPEN, ClosureState.BLOCKED})

#: The transition algebra. ``CERTIFIED`` is reachable only from ``CLOSED`` — certification
#: of a dimension that is not closed is the unverified claim this programme exists to
#: refuse. Every pass state can fall back to ``OPEN`` or ``BLOCKED``, because closure is a
#: measurement of the current tree and a regression must be expressible.
#: Every non-historical state may be superseded, because any reading can be replaced by a
#: later reading. ``SUPERSEDED`` alone leads nowhere: history does not move.
_TRANSITIONS: Mapping[ClosureState, frozenset[ClosureState]] = {
    ClosureState.DISCOVERED: frozenset(
        {ClosureState.MEASURED, ClosureState.BLOCKED, ClosureState.SUPERSEDED}
    ),
    ClosureState.MEASURED: frozenset(
        {
            ClosureState.OPEN,
            ClosureState.BLOCKED,
            ClosureState.CLOSED,
            ClosureState.SUPERSEDED,
        }
    ),
    ClosureState.OPEN: frozenset(
        {
            ClosureState.MEASURED,
            ClosureState.BLOCKED,
            ClosureState.CLOSED,
            ClosureState.SUPERSEDED,
        }
    ),
    ClosureState.BLOCKED: frozenset(
        {
            ClosureState.MEASURED,
            ClosureState.OPEN,
            ClosureState.CLOSED,
            ClosureState.SUPERSEDED,
        }
    ),
    ClosureState.CLOSED: frozenset(
        {
            ClosureState.CERTIFIED,
            ClosureState.OPEN,
            ClosureState.BLOCKED,
            ClosureState.SUPERSEDED,
        }
    ),
    ClosureState.CERTIFIED: frozenset(
        {ClosureState.OPEN, ClosureState.BLOCKED, ClosureState.SUPERSEDED}
    ),
    ClosureState.SUPERSEDED: frozenset(),
}

#: The historical state — a record replaced by a later observation of the same coordinate.
HISTORICAL_STATE: ClosureState = ClosureState.SUPERSEDED

PASS_STATES: tuple[str, ...] = tuple(sorted(s.value for s in _PASS_STATES))
GAP_STATES: tuple[str, ...] = tuple(sorted(s.value for s in _GAP_STATES))


def digest(payload: Any) -> str:
    """The canonical content digest, computed through the single located primitive."""
    return content_hash(payload)


@dataclass(frozen=True, slots=True)
class DimensionDeclaration:
    """One declared closure dimension: the question, its requirement and its probe."""

    id: str
    ordinal: int
    name: str
    question: str
    requirement: str
    probe: str
    evidence_kind: str
    blocking: bool
    owner_reference: str
    ucic_stages: tuple[int, ...]
    probe_parameters: Mapping[str, Any]

    def parameter(self, name: str, default: Any = None) -> Any:
        """Read a declared probe parameter, so no probe carries a literal of its own."""
        if name not in self.probe_parameters:
            if default is None:
                raise ClosureDeclarationError(
                    f"dimension {self.id}: undeclared probe parameter {name!r}"
                )
            return default
        return self.probe_parameters[name]

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> DimensionDeclaration:
        """Build a dimension from its declared record, failing closed on omissions."""
        missing = [
            key
            for key in (
                "id",
                "ordinal",
                "name",
                "question",
                "requirement",
                "probe",
                "evidence_kind",
                "blocking",
                "owner_reference",
                "ucic_stages",
                "probe_parameters",
            )
            if key not in record
        ]
        if missing:
            raise ClosureDeclarationError(
                f"dimension record is missing {', '.join(missing)}",
                dimension=str(record.get("id")),
            )
        return cls(
            id=str(record["id"]),
            ordinal=int(record["ordinal"]),
            name=str(record["name"]),
            question=str(record["question"]),
            requirement=str(record["requirement"]),
            probe=str(record["probe"]),
            evidence_kind=str(record["evidence_kind"]),
            blocking=bool(record["blocking"]),
            owner_reference=str(record["owner_reference"]),
            ucic_stages=tuple(int(s) for s in record["ucic_stages"]),
            probe_parameters=dict(record["probe_parameters"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "ordinal": self.ordinal,
            "name": self.name,
            "question": self.question,
            "requirement": self.requirement,
            "probe": self.probe,
            "evidence_kind": self.evidence_kind,
            "blocking": self.blocking,
            "owner_reference": self.owner_reference,
            "ucic_stages": list(self.ucic_stages),
            "probe_parameters": dict(self.probe_parameters),
        }


def _declared_list(
    document: Mapping[str, Any], section: str, key: str
) -> Sequence[Mapping[str, Any]]:
    """A declared list of records inside a declared section, or fail closed.

    Both levels are checked because a section that exists but carries the wrong shape is a
    declaration the engine cannot read, and reading it as empty would silently turn a
    malformed declaration into a projection that claims nothing is declared.
    """
    block = document.get(section)
    if not isinstance(block, Mapping):
        raise ClosureDeclarationError(f"declaration section {section!r} is not an object")
    records = block.get(key)
    if not isinstance(records, list) or not records:
        raise ClosureDeclarationError(f"declaration section {section!r} declares no {key!r}")
    for record in records:
        if not isinstance(record, Mapping):
            raise ClosureDeclarationError(f"{section}.{key} carries a non-object record")
    return records


@dataclass(frozen=True, slots=True)
class ResolutionBinding:
    """One declared dimension → the instrument that closes it and the gate that judges it.

    This is routing, not authority. It names no owner: an owner is a function of a path,
    and the located ownership function is applied to :meth:`resolve`'s answer, so a
    resolution owner is always *read* from the identity authority's own rule set and never
    asserted here. Nothing about a run, an attempt or an assignment can be expressed by
    this record — it is frozen, it carries no state field, and a closure remains a
    measurement rather than a report of intent.

    ``target`` may contain the declared location placeholder, which is what distinguishes a
    capability-local instrument (``{location}/__init__.py``) from a central one
    (``pyproject.toml``). The engine branches on the placeholder's presence, never on a
    dimension name, so no per-dimension exception can enter the code (UICM-INV-15).
    """

    dimension: str
    target: str
    gate: str
    why: str = ""

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> ResolutionBinding:
        """Build a binding from its declared record, failing closed on any omission."""
        missing = [key for key in ("dimension", "target", "gate") if not str(record.get(key, ""))]
        if missing:
            raise ClosureDeclarationError(
                f"resolution binding is missing {', '.join(missing)}",
                dimension=str(record.get("dimension")),
            )
        return cls(
            dimension=str(record["dimension"]),
            target=str(record["target"]),
            gate=str(record["gate"]),
            why=str(record.get("why", "")),
        )

    def is_capability_local(self, placeholder: str) -> bool:
        """True iff the declared instrument lives inside the capability's own package."""
        return placeholder in self.target

    def resolve(self, placeholder: str, location: str) -> str:
        """The instrument path for one capability.

        A capability-local target with no location to resolve against is refused rather
        than emitted with the placeholder still in it: a path that names ``{location}``
        resolves to nothing, and recording it would be a routing claim pointing nowhere.
        """
        if not self.is_capability_local(placeholder):
            return self.target
        if not location:
            raise ClosureDeclarationError(
                "capability-local resolution target has no location to resolve against",
                dimension=self.dimension,
                target=self.target,
            )
        return self.target.replace(placeholder, location)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "target": self.target,
            "gate": self.gate,
            "why": self.why,
        }


@dataclass(frozen=True, slots=True)
class StateDeclaration:
    """One declared closure state, as the declaration describes it."""

    id: str
    ordinal: int
    meaning: str
    requires_evidence: bool
    requires_gap: bool
    is_pass: bool
    may_transition_to: tuple[str, ...]

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> StateDeclaration:
        try:
            return cls(
                id=str(record["id"]),
                ordinal=int(record["ordinal"]),
                meaning=str(record["meaning"]),
                requires_evidence=bool(record["requires_evidence"]),
                requires_gap=bool(record["requires_gap"]),
                is_pass=bool(record["is_pass"]),
                may_transition_to=tuple(str(t) for t in record["may_transition_to"]),
            )
        except KeyError as exc:
            raise ClosureDeclarationError(
                f"state record is missing {exc.args[0]}", state=str(record.get("id"))
            ) from exc

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "ordinal": self.ordinal,
            "meaning": self.meaning,
            "requires_evidence": self.requires_evidence,
            "requires_gap": self.requires_gap,
            "is_pass": self.is_pass,
            "may_transition_to": list(self.may_transition_to),
        }


@dataclass(frozen=True, slots=True)
class Capability:
    """A discovered capability, every field of which is read from a canonical owner.

    ``capability_id`` is a ``UCKO-CAP-*`` value read from the capability register. UICM
    mints no capability identifier, so this class has no ``mint`` and no counter.
    """

    capability_id: str
    name: str
    location: str
    canonical_owner: str
    knowledge_reference: str
    lifecycle: str
    authority: str
    implementation_location: str
    implementation_status: str
    reuse_disposition: str
    replacement_prohibited: bool
    artifacts: tuple[str, ...]
    identified_artifacts: tuple[str, ...]
    unidentified_artifacts: tuple[str, ...]
    artifact_identities: tuple[str, ...]
    artifact_digests: tuple[str, ...]

    @property
    def artifact_count(self) -> int:
        return len(self.artifacts)

    @property
    def identity_complete(self) -> bool:
        """True iff every tracked artifact carries an identity from the identity authority."""
        return bool(self.artifacts) and not self.unidentified_artifacts

    @property
    def short_id(self) -> str:
        """The capability identity without its register prefix, for derived record ids."""
        return self.capability_id.rsplit("-", 1)[-1]

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "location": self.location,
            "canonical_owner": self.canonical_owner,
            "knowledge_reference": self.knowledge_reference,
            "lifecycle": self.lifecycle,
            "authority": self.authority,
            "implementation_location": self.implementation_location,
            "implementation_status": self.implementation_status,
            "reuse_disposition": self.reuse_disposition,
            "replacement_prohibited": self.replacement_prohibited,
            "artifact_count": self.artifact_count,
            "identified_artifacts": len(self.identified_artifacts),
            "unidentified_artifacts": list(self.unidentified_artifacts),
        }

    def digest(self) -> str:
        return digest(self.to_dict())


@dataclass(frozen=True, slots=True)
class ClosureCell:
    """One capability x dimension closure measurement.

    ``evidence`` is a tuple of references into located sources, never a prose assertion,
    and ``evidence_digest`` seals it. A cell in a state that requires evidence and
    carries none is refused by :mod:`engine.uicm.validation` (UICM-INV-04).
    """

    capability_id: str
    capability_name: str
    dimension_id: str
    state: ClosureState
    finding: str
    evidence: tuple[str, ...]
    transition: tuple[str, ...]
    observation_id: str
    observation_lineage: tuple[str, ...]

    @property
    def evidence_digest(self) -> str:
        """The seal over this cell's evidence set, or the empty string when unevidenced."""
        if not self.evidence:
            return ""
        return digest({"cell": self.key, "evidence": list(self.evidence)})

    @property
    def key(self) -> str:
        """The cell's stable coordinate in the matrix."""
        return f"{self.capability_name}:{self.dimension_id}"

    @property
    def is_pass(self) -> bool:
        return self.state.is_pass

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "dimension_id": self.dimension_id,
            "state": self.state.value,
            "finding": self.finding,
            "evidence": list(self.evidence),
            "evidence_digest": self.evidence_digest,
            "transition": list(self.transition),
            "observation_id": self.observation_id,
            "observation_lineage": list(self.observation_lineage),
        }


@dataclass(frozen=True, slots=True)
class ClosureDeclaration:
    """The parsed declaration — the single source of every enumeration UICM uses."""

    home: Path
    document: Mapping[str, Any]
    states: tuple[StateDeclaration, ...]
    dimensions: tuple[DimensionDeclaration, ...]
    resolution_bindings: tuple[ResolutionBinding, ...]

    @classmethod
    def load(cls, home: Path) -> ClosureDeclaration:
        """Read and validate the declaration at ``home``, failing closed on any defect."""
        path = Path(home) / DECLARATION_FILENAME
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ClosureDeclarationError(f"closure declaration is unreadable: {path}") from exc
        try:
            document = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ClosureDeclarationError(f"closure declaration is not valid JSON: {path}") from exc
        if not isinstance(document, dict):
            raise ClosureDeclarationError("closure declaration must be a JSON object")
        absent = [section for section in REQUIRED_SECTIONS if section not in document]
        if absent:
            raise ClosureDeclarationError(
                f"closure declaration is missing section(s): {', '.join(absent)}"
            )
        states = tuple(StateDeclaration.from_record(r) for r in document["closure_states"])
        dimensions = tuple(
            DimensionDeclaration.from_record(r) for r in document["closure_dimensions"]
        )
        if not dimensions:
            raise ClosureDeclarationError("closure declaration declares no dimension")
        bindings = tuple(
            ResolutionBinding.from_record(r)
            for r in _declared_list(document, RESOLUTION_SECTION, "bindings")
        )
        declaration = cls(
            home=Path(home),
            document=document,
            states=states,
            dimensions=dimensions,
            resolution_bindings=bindings,
        )
        declaration.require_state_conformance()
        declaration.require_unique_dimensions()
        declaration.require_resolution_totality()
        return declaration

    # -- declared vocabulary ------------------------------------------------------

    @property
    def programme_id(self) -> str:
        return str(self.document["programme"]["id"])

    @property
    def programme_version(self) -> str:
        return str(self.document["programme"]["version"])

    @property
    def dimension_ids(self) -> tuple[str, ...]:
        return tuple(d.id for d in self.dimensions)

    @property
    def state_ids(self) -> tuple[str, ...]:
        return tuple(s.id for s in self.states)

    @property
    def probe_names(self) -> tuple[str, ...]:
        return tuple(d.probe for d in self.dimensions)

    def dimension(self, dimension_id: str) -> DimensionDeclaration:
        """Return the declared dimension, or fail closed."""
        for declared in self.dimensions:
            if declared.id == dimension_id:
                return declared
        raise ClosureDeclarationError(f"undeclared closure dimension: {dimension_id!r}")

    @property
    def location_placeholder(self) -> str:
        """The declared token a capability-local resolution target substitutes."""
        token = str(self.section(RESOLUTION_SECTION).get("location_placeholder", ""))
        if not token:
            raise ClosureDeclarationError("no location placeholder is declared")
        return token

    @property
    def ownership_authority(self) -> Mapping[str, Any]:
        """The located TOTAL ownership function this projection reads owners from."""
        record = self.section(RESOLUTION_SECTION).get("ownership_authority")
        if not isinstance(record, Mapping):
            raise ClosureDeclarationError("no ownership authority is declared")
        missing = [key for key in ("home", "symbol") if not str(record.get(key, ""))]
        if missing:
            raise ClosureDeclarationError(
                f"declared ownership authority is missing {', '.join(missing)}"
            )
        return record

    def resolution_binding(self, dimension_id: str) -> ResolutionBinding:
        """Return the declared resolution binding for a dimension, or fail closed."""
        for binding in self.resolution_bindings:
            if binding.dimension == dimension_id:
                return binding
        raise ClosureDeclarationError(f"no resolution binding declares: {dimension_id!r}")

    def source(self, name: str) -> Mapping[str, Any]:
        """Return a declared canonical source record, or fail closed."""
        sources = self.document["canonical_sources"]
        if name not in sources:
            raise ClosureDeclarationError(f"undeclared canonical source: {name!r}")
        return sources[name]

    def section(self, name: str) -> Any:
        """Return a declared top-level section, or fail closed."""
        if name not in self.document:
            raise ClosureDeclarationError(f"undeclared declaration section: {name!r}")
        return self.document[name]

    @property
    def population(self) -> Mapping[str, Any]:
        return self.document["population"]

    @property
    def capability_roots(self) -> tuple[str, ...]:
        return tuple(str(r) for r in self.population["capability_roots"])

    @property
    def excluded_namespaces(self) -> frozenset[str]:
        return frozenset(str(n) for n in self.population["excluded_namespaces"])

    @property
    def invariants(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(self.document["invariants"])

    @property
    def gap_classes(self) -> Mapping[str, str]:
        """Declared gap class name -> its declared meaning."""
        return {str(r["class"]): str(r["meaning"]) for r in self.document["gap_classification"]}

    # -- conformance --------------------------------------------------------------

    def require_state_conformance(self) -> None:
        """Fail closed unless the declaration and :class:`ClosureState` agree exactly.

        A state vocabulary living in both a declaration and an enum is a vocabulary that
        will drift; this is the measurement that makes UICM-INV-01 real rather than
        documentary. Membership, pass semantics, evidence semantics, gap semantics and
        the transition algebra are all compared.
        """
        declared = {s.id for s in self.states}
        implemented = {s.value for s in ClosureState}
        if declared != implemented:
            raise ClosureDeclarationError(
                "declared closure states and the engine state machine disagree",
                declared_only=sorted(declared - implemented),
                implemented_only=sorted(implemented - declared),
            )
        for state in self.states:
            live = ClosureState.coerce(state.id)
            if state.is_pass != live.is_pass:
                raise ClosureDeclarationError(
                    f"state {state.id}: declared is_pass disagrees with the state machine"
                )
            if state.requires_evidence != live.requires_evidence:
                raise ClosureDeclarationError(
                    f"state {state.id}: declared requires_evidence disagrees with the machine"
                )
            if state.requires_gap != live.requires_gap:
                raise ClosureDeclarationError(
                    f"state {state.id}: declared requires_gap disagrees with the machine"
                )
            declared_targets = set(state.may_transition_to)
            live_targets = {t.value for t in _TRANSITIONS[live]}
            if declared_targets != live_targets:
                raise ClosureDeclarationError(
                    f"state {state.id}: declared transitions disagree with the machine",
                    declared_only=sorted(declared_targets - live_targets),
                    implemented_only=sorted(live_targets - declared_targets),
                )

    def require_unique_dimensions(self) -> None:
        """Fail closed on a duplicated dimension id, ordinal or probe."""
        for label, values in (
            ("id", [d.id for d in self.dimensions]),
            ("ordinal", [d.ordinal for d in self.dimensions]),
            ("probe", [d.probe for d in self.dimensions]),
        ):
            duplicates = sorted({v for v in values if values.count(v) > 1})
            if duplicates:
                raise ClosureDeclarationError(
                    f"duplicate dimension {label}: {duplicates}",
                )

    def require_resolution_totality(self) -> None:
        """Fail closed unless resolution routing is total, unique and deterministically ordered.

        Four defects are refused, and each would corrupt the projection differently. A
        missing dimension leaves a registered gap with nowhere to go. A duplicate names two
        instruments for one question, which is the duplicate-authority failure this
        programme exists to make impossible. An unknown dimension routes a question nobody
        declared. And an order other than the declared ordinal order would make the emitted
        projection depend on the order someone typed rather than on the standard, which is
        the difference between derived truth and a document (UICM-INV-13).
        """
        declared = [binding.dimension for binding in self.resolution_bindings]
        duplicates = sorted({d for d in declared if declared.count(d) > 1})
        if duplicates:
            raise ClosureDeclarationError(f"duplicate resolution binding: {duplicates}")
        known = set(self.dimension_ids)
        unknown = sorted(set(declared) - known)
        absent = sorted(known - set(declared))
        if unknown:
            raise ClosureDeclarationError(
                f"resolution binding names an undeclared dimension: {unknown}"
            )
        if absent:
            raise ClosureDeclarationError(f"dimension carries no resolution binding: {absent}")
        if declared != list(self.dimension_ids):
            raise ClosureDeclarationError(
                "resolution bindings are not declared in dimension ordinal order",
                declared=declared,
                expected=list(self.dimension_ids),
            )
        placeholder = self.location_placeholder
        if not self.ownership_authority:
            raise ClosureDeclarationError("the declared ownership authority carries no fields")
        for binding in self.resolution_bindings:
            if binding.is_capability_local(placeholder) and binding.target == placeholder:
                raise ClosureDeclarationError(
                    "a resolution target that is only the placeholder names no instrument",
                    dimension=binding.dimension,
                )

    def require_probe_bijection(self, implemented: Iterable[str]) -> None:
        """Fail closed unless declared probes and implemented probes are the same set.

        A declared dimension with no probe is a question nobody asks; an implemented
        probe with no dimension is a measurement nobody declared. Both are refused
        (UICM-INV-02).
        """
        available = set(implemented)
        declared = set(self.probe_names)
        if declared != available:
            raise ClosureDeclarationError(
                "declared dimensions and implemented probes are not in bijection",
                undeclared_probes=sorted(available - declared),
                unimplemented_probes=sorted(declared - available),
            )

    def to_dict(self) -> dict[str, Any]:
        """The digest surface: what closure *means*, and nothing else.

        Resolution bindings are deliberately absent. They are read by the engine and sealed
        in the gap projection they produce, but they say which instrument discharges a gap —
        not what being closed means — and a digest that moved when routing changed would
        report a change in the standard that did not happen.
        """
        return {
            "programme": dict(self.document["programme"]),
            "states": [s.to_dict() for s in self.states],
            "dimensions": [d.to_dict() for d in self.dimensions],
        }

    def digest(self) -> str:
        """The declaration digest — the identity of the standard being applied."""
        return digest(self.to_dict())


def state_counts(cells: Sequence[ClosureCell]) -> dict[str, int]:
    """Count cells per declared state, always reporting every state (zeros included)."""
    counts = {state.value: 0 for state in ClosureState}
    for cell in cells:
        counts[cell.state.value] += 1
    return counts


def canonical_document(payload: Any) -> str:
    """The canonical JSON encoding, for digesting and for replay comparison."""
    return canonical_json(payload)


__all__ = [
    "DECLARATION_FILENAME",
    "GAP_STATES",
    "HISTORICAL_STATE",
    "PASS_STATES",
    "REQUIRED_SECTIONS",
    "RESOLUTION_SECTION",
    "Capability",
    "ClosureCell",
    "ClosureDeclaration",
    "ClosureDeclarationError",
    "ClosureError",
    "ClosureState",
    "ClosureStateError",
    "DimensionDeclaration",
    "ResolutionBinding",
    "StateDeclaration",
    "canonical_document",
    "digest",
    "state_counts",
]

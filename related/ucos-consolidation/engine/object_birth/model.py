"""UOBC-000001 Part 01 — the birth object model, as shape only.

Every type here is frozen and slotted, and every collection is a tuple, so a birth
contract loaded twice is value-equal and a birth record cannot be mutated after the
fact. That is not stylistic: :class:`BirthRecord` is the evidence that an object was
identified before it existed, and evidence you can edit in place is not evidence.

The module declares no stage, no field name, no law and no namespace. Every
enumeration lives in ``00-MASTER/UOBC-000001/uobc-birth-contract.json`` and is
discovered, so admitting a future stage or a future namespace is an edit to data
rather than to control flow. Nothing below branches on a specific stage id.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class BirthError(Exception):
    """A birth obligation was refused.

    Carries the offending subject so a gate report can name what failed rather
    than only that something did.
    """

    def __init__(self, message: str, *, subject: str | None = None) -> None:
        super().__init__(message if subject is None else f"{message}: {subject}")
        self.subject = subject


@dataclass(frozen=True, slots=True)
class BirthStage:
    """One declared stage of the birth lifecycle.

    ``identity_exists`` is the load-bearing field. It records whether identity is
    already derived at this stage, and the contract's central obligation is that it
    is False for every stage before identity minting and True from that stage on.
    """

    stage_id: str
    ordinal: int
    stage: str
    duty: str
    produces: str
    identity_exists: bool

    @classmethod
    def from_declaration(cls, entry: dict[str, Any]) -> BirthStage:
        try:
            return cls(
                stage_id=str(entry["id"]),
                ordinal=int(entry["ordinal"]),
                stage=str(entry["stage"]),
                duty=str(entry["duty"]),
                produces=str(entry["produces"]),
                identity_exists=bool(entry["identity_exists"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise BirthError("stage declaration is unusable", subject=repr(entry)) from exc


@dataclass(frozen=True, slots=True)
class MandatoryField:
    """One of the fields every birth record must carry."""

    field_id: str
    field: str
    shape: str
    derived: bool
    immutable: bool
    basis: str

    @classmethod
    def from_declaration(cls, entry: dict[str, Any]) -> MandatoryField:
        try:
            return cls(
                field_id=str(entry["id"]),
                field=str(entry["field"]),
                shape=str(entry["shape"]),
                derived=bool(entry["derived"]),
                immutable=bool(entry["immutable"]),
                basis=str(entry["basis"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise BirthError("field declaration is unusable", subject=repr(entry)) from exc


@dataclass(frozen=True, slots=True)
class BirthLaw:
    """One law, and the name of the check that computes its compliance."""

    law_id: str
    title: str
    statement: str
    check: str

    @classmethod
    def from_declaration(cls, entry: dict[str, Any]) -> BirthLaw:
        try:
            return cls(
                law_id=str(entry["id"]),
                title=str(entry["title"]),
                statement=str(entry["statement"]),
                check=str(entry["check"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise BirthError("law declaration is unusable", subject=repr(entry)) from exc


@dataclass(frozen=True, slots=True)
class Namespace:
    """A declared namespace and the owner entitled to mint within it."""

    namespace: str
    owner: str
    zone: str

    @classmethod
    def from_declaration(cls, entry: dict[str, Any]) -> Namespace:
        try:
            return cls(
                namespace=str(entry["namespace"]),
                owner=str(entry["owner"]),
                zone=str(entry["zone"]),
            )
        except (KeyError, TypeError) as exc:
            raise BirthError("namespace declaration is unusable", subject=repr(entry)) from exc


@dataclass(frozen=True, slots=True)
class Boundary:
    """Something this contract refuses to do, and who does it instead."""

    boundary_id: str
    refuses: str
    owner: str

    @classmethod
    def from_declaration(cls, entry: dict[str, Any]) -> Boundary:
        try:
            return cls(
                boundary_id=str(entry["id"]),
                refuses=str(entry["refuses"]),
                owner=str(entry["owner"]),
            )
        except (KeyError, TypeError) as exc:
            raise BirthError("boundary declaration is unusable", subject=repr(entry)) from exc


@dataclass(frozen=True, slots=True)
class BirthRecord:
    """The nine mandatory fields of an object's birth, as an immutable record.

    ``universal_id`` is derived (UCKP Article 5) from ``namespace`` and the object's
    local name alone. None of the other eight fields is an identity input, which is
    exactly why ownership, state, path and content may all evolve while identity
    cannot. ``parent_identity`` is ``None`` only for a declared root object.
    """

    universal_id: str
    namespace: str
    owner: str
    creation_timestamp: str
    creation_context: tuple[tuple[str, str], ...]
    parent_identity: str | None
    lifecycle_binding: str
    initial_state: str
    certification_boundary: str

    def to_dict(self) -> dict[str, Any]:
        """Return the canonical mapping form, key-ordered for byte-stable output."""
        return {
            "universal_id": self.universal_id,
            "namespace": self.namespace,
            "owner": self.owner,
            "creation_timestamp": self.creation_timestamp,
            "creation_context": {k: v for k, v in self.creation_context},
            "parent_identity": self.parent_identity,
            "lifecycle_binding": self.lifecycle_binding,
            "initial_state": self.initial_state,
            "certification_boundary": self.certification_boundary,
        }

    @classmethod
    def from_dict(cls, entry: dict[str, Any]) -> BirthRecord:
        """Rehydrate a record, refusing anything that is not a complete birth."""
        missing = [f for f in MANDATORY_FIELD_NAMES if f not in entry]
        if missing:
            raise BirthError(
                f"birth record is missing mandatory field(s): {', '.join(missing)}",
                subject=str(entry.get("universal_id", "<anonymous>")),
            )
        context = entry["creation_context"]
        if not isinstance(context, dict):
            raise BirthError(
                "creation_context must be a mapping", subject=str(entry["universal_id"])
            )
        parent = entry["parent_identity"]
        return cls(
            universal_id=str(entry["universal_id"]),
            namespace=str(entry["namespace"]),
            owner=str(entry["owner"]),
            creation_timestamp=str(entry["creation_timestamp"]),
            creation_context=tuple(sorted((str(k), str(v)) for k, v in context.items())),
            parent_identity=None if parent is None else str(parent),
            lifecycle_binding=str(entry["lifecycle_binding"]),
            initial_state=str(entry["initial_state"]),
            certification_boundary=str(entry["certification_boundary"]),
        )


#: The nine field names, in declaration order. Derived from the dataclass so the
#: model and the completeness check can never disagree about what "complete" means.
MANDATORY_FIELD_NAMES: tuple[str, ...] = tuple(BirthRecord.__dataclass_fields__)


@dataclass(frozen=True, slots=True)
class BirthContract:
    """The whole declaration, rehydrated and self-consistent.

    Construction is the first gate: :meth:`validate` refuses a contract whose stages
    do not flip ``identity_exists`` exactly once, whose fields are not the nine the
    model declares, or whose laws name a check that does not exist.
    """

    artifact_id: str
    version: str
    authority: str
    identity_home: str
    identity_shape: str
    counter_consumed: bool
    namespace_pattern: str
    namespaces: tuple[Namespace, ...]
    stages: tuple[BirthStage, ...]
    fields: tuple[MandatoryField, ...]
    laws: tuple[BirthLaw, ...]
    identity_inputs: tuple[str, ...]
    initial_states: tuple[str, ...]
    boundaries: tuple[Boundary, ...]
    ledger_home: str
    certification_boundary: str

    @property
    def identity_stage(self) -> BirthStage:
        """The stage at which identity comes into being."""
        for stage in self.stages:
            if stage.identity_exists:
                return stage
        raise BirthError("no declared stage derives identity")

    def namespace_owner(self, namespace: str) -> str | None:
        """Return the declared owner of ``namespace``, or None if undeclared."""
        for declared in self.namespaces:
            if declared.namespace == namespace:
                return declared.owner
        return None

    def validate(self, available_checks: frozenset[str]) -> tuple[str, ...]:
        """Return the reasons this contract is unusable, empty when it is sound."""
        problems: list[str] = []

        if not self.stages:
            problems.append("the contract declares no stage")
        ordinals = [s.ordinal for s in self.stages]
        if ordinals != sorted(ordinals):
            problems.append("stages are not in ordinal order")
        if len(set(ordinals)) != len(ordinals):
            problems.append("two stages share an ordinal")

        # identity_exists must be a single monotonic flip: False* then True*.
        flips = sum(
            1
            for earlier, later in zip(self.stages, self.stages[1:], strict=False)
            if earlier.identity_exists != later.identity_exists
        )
        if self.stages and flips != 1:
            problems.append(
                f"identity_exists flips {flips} time(s); "
                "identity must come into being exactly once"
            )
        if self.stages and self.stages[0].identity_exists:
            problems.append("the first stage already holds identity, so nothing precedes existence")
        if self.stages and not self.stages[-1].identity_exists:
            problems.append("the final stage holds no identity")

        declared_fields = tuple(f.field for f in self.fields)
        if declared_fields != MANDATORY_FIELD_NAMES:
            problems.append(
                "declared fields do not match the record model: "
                f"{declared_fields} != {MANDATORY_FIELD_NAMES}"
            )

        if not self.laws:
            problems.append("the contract declares no law")
        for law in self.laws:
            if law.check not in available_checks:
                problems.append(f"{law.law_id} names check {law.check!r}, which is not implemented")

        if self.counter_consumed:
            problems.append(
                "the contract claims to consume a counter, which would be a second mint"
            )

        for required in self.identity_inputs:
            if required not in MANDATORY_FIELD_NAMES and required != "local_name":
                problems.append(f"identity input {required!r} is not a recorded field")

        if not self.initial_states:
            problems.append("the contract declares no admissible initial state")

        return tuple(problems)

    @classmethod
    def from_declaration(cls, doc: dict[str, Any]) -> BirthContract:
        """Rehydrate the contract from its declaration document."""
        try:
            plane = doc["identity_plane"]
            policy = doc["namespace_policy"]
            ledger = doc["ledger"]
            return cls(
                artifact_id=str(doc["artifact_id"]),
                version=str(doc["version"]),
                authority=str(doc["authority"]),
                identity_home=str(plane["home"]),
                identity_shape=str(plane["shape"]),
                counter_consumed=bool(plane["counter_consumed"]),
                namespace_pattern=str(policy["pattern"]),
                namespaces=tuple(
                    Namespace.from_declaration(e) for e in policy["declared_namespaces"]
                ),
                stages=tuple(BirthStage.from_declaration(e) for e in doc["stages"]),
                fields=tuple(MandatoryField.from_declaration(e) for e in doc["mandatory_fields"]),
                laws=tuple(BirthLaw.from_declaration(e) for e in doc["laws"]),
                identity_inputs=tuple(str(x) for x in doc["identity_inputs"]),
                initial_states=tuple(str(x) for x in doc["initial_states"]),
                boundaries=tuple(Boundary.from_declaration(e) for e in doc["boundaries"]),
                ledger_home=str(ledger["home"]),
                certification_boundary=str(doc["certification_boundary"]),
            )
        except (KeyError, TypeError) as exc:
            raise BirthError("birth contract declaration is unusable", subject=str(exc)) from exc

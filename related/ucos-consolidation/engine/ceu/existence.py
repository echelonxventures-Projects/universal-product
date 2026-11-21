"""UCOS-CEU-001 — the Constitutional Existence substrate. Existence precedes entity.

Repository truth before this module
-----------------------------------
The repository had an *entity* model with a fixed root: ``StructuralRole`` was a closed
three-member enum (nucleus, layer, composition), ownership was the hardcoded predicate
``self is NUCLEUS``, and topology was two fields on a record — ``composes`` and
``organizes``. A classification could not be registered, a relationship had no identity,
and a topology did not exist as a thing at all.

So three of the four constructs the constitution treats as first-class — classification,
relationship, topology — were *shapes in the source code*, and the fourth, the entity, was
the privileged root everything else hung from.

The correction: one substrate, one kind of record
-------------------------------------------------
There is exactly one registry and exactly one record type, :class:`ExistenceUnit`. A unit
declares which **form** of existence it is. A form is itself a unit. A classification is a
unit. A relationship is a unit. A topology is a unit. So all four constructs are
registered, identified, lineaged, context-bindable, supersedable and evolvable through the
*same* mechanism — not because each was given those properties, but because there is only
one mechanism to give them.

The self-describing bootstrap
-----------------------------
The recursion bottoms out the way every reflective system's does: the root form is a unit
whose form is itself. :data:`ROOT_FORM` is registered with ``form == its own key``, and
every other form is a unit of that form. Nothing is privileged by the code — the root's
*name* is a constructor argument, so even "form" is not a reserved word here.

Openness, as checkable properties
---------------------------------
* **No function in this module branches on a particular form, classification, topology or
  relationship type.** Grep for ``"entity"``, ``"nucleus"`` or ``"layer"`` and you will
  find them only in :mod:`engine.ceu.catalog`, which is DATA.
* **Every construct evolves by one mechanism.** :meth:`ExistenceRegistry.supersede` and
  :meth:`ExistenceRegistry.resurrect` take a unit — any unit — so a classification, a
  relationship type, a topology and a form all split, merge, deprecate and come back
  through the same call.
* **Relationship validity is registry-driven** (CEU-007). A relationship type constrains
  its endpoints only if it *declares* a constraint; the default is unconstrained, so the
  substrate imposes no valid-pair table of its own.
* **No ceiling.** Every document says ``closed_set: false`` and ``upper_limit: null``, and
  no count anywhere is compared against a bound.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.ceu.errors import (
    ExistenceError,
    ExistenceRegistrationError,
    RelationshipAdmissibilityError,
    RelationshipError,
    TopologyCycleError,
)
from engine.compiler.cycles import detect_cycle
from engine.registry.universal.identity import (
    RegistryKind,
    deterministic_id,
    is_well_formed,
    kind_names,
    resolve_kind_code,
)
from engine.registry.universal.identity import (
    register_kind as register_identifier_kind,
)
from engine.uckp.canonical import content_hash

#: The key of the self-describing root form. A default, not a reserved word: the registry
#: takes it as a constructor argument, so a deployment may name the root anything.
ROOT_FORM = "form"

#: The identifier code the root form is minted under.
ROOT_FORM_CODE = "FORM"

#: The namespace every existence unit is registered under unless it declares another.
EXISTENCE_NAMESPACE = "ucos.ceu"

#: Attribute keys the substrate *reads* (never branches on). A form declares its
#: identifier code; a relationship declares its type and endpoints; a classification
#: declares the faculties it holds and the classification it specializes. Any other
#: attribute is carried, unread, which is how an unknown future form stores its own shape.
ATTR_CODE = "code"
ATTR_SPECIALIZES = "specializes"
ATTR_FACULTIES = "faculties"
ATTR_RELATIONSHIP_TYPE = "relationship_type"
ATTR_SOURCE = "source"
ATTR_TARGET = "target"
ATTR_TOPOLOGIES = "topologies"
ATTR_ACYCLIC = "acyclic"
ATTR_SYMMETRIC = "symmetric"
ATTR_SOURCE_FORMS = "source_forms"
ATTR_TARGET_FORMS = "target_forms"
ATTR_SOURCE_CLASSIFICATIONS = "source_classifications"
ATTR_TARGET_CLASSIFICATIONS = "target_classifications"
ATTR_CLASSIFICATION = "classification"


@dataclass(frozen=True, slots=True)
class ExistenceUnit:
    """One unit of constitutional existence, of any form.

    The single record type of the substrate. An entity, a classification, a relationship,
    a topology, an event, an observation and a form nobody has named are all this, and
    differ only in ``form`` and in what they carry in ``attributes``.
    """

    form: str
    key: str
    title: str
    definition: str = ""
    namespace: str = EXISTENCE_NAMESPACE
    classification: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    identity_kind: str = ""
    content_hash: str = ""

    def __post_init__(self) -> None:
        for name in ("form", "key", "title"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ExistenceError("a unit must declare this field", at=name, key=self.key)
        object.__setattr__(self, "form", self.form.strip())
        object.__setattr__(self, "key", self.key.strip())
        object.__setattr__(self, "namespace", (self.namespace or EXISTENCE_NAMESPACE).strip())
        object.__setattr__(self, "attributes", _canonical(dict(self.attributes or {})))
        if not self.content_hash:
            object.__setattr__(self, "content_hash", content_hash(self._payload()))

    def _payload(self) -> dict[str, Any]:
        return {
            "form": self.form,
            "key": self.key,
            "title": self.title,
            "definition": self.definition,
            "namespace": self.namespace,
            "classification": self.classification,
            "attributes": dict(self.attributes),
        }

    def universal_id_for(self, identity_kind: str) -> str:
        """The identifier this unit is minted under, given its form's registered kind.

        ``identity_kind`` is the *name* the one identity authority knows the form by, not
        the short code — the authority owns the name→code mapping, and duplicating that
        mapping here would be a second grammar.
        """
        return deterministic_id(identity_kind, self.namespace, f"{self.form}:{self.key}")

    @property
    def universal_id(self) -> str:
        """The identifier, using the code carried on the record.

        ``identity_kind`` is stamped by the registry at registration from the unit's
        *form*, so a detached unit that was never registered has no identity — which is
        correct: AC-002 says registration is the act that creates existence.
        """
        if not self.identity_kind:
            raise ExistenceError(
                "an unregistered unit has no identity (registration creates existence)",
                form=self.form,
                key=self.key,
            )
        return self.universal_id_for(self.identity_kind)

    def attribute(self, name: str, default: Any = None) -> Any:
        return self.attributes.get(name, default)

    def tuple_attribute(self, name: str) -> tuple[str, ...]:
        """An attribute read as an ordered tuple of strings; ``()`` when absent."""
        raw = self.attributes.get(name) or ()
        if isinstance(raw, str):
            return (raw,)
        return tuple(str(item) for item in raw)

    def is_intact(self) -> bool:
        """True iff the record reproduces its own content digest."""
        return self.content_hash == content_hash(self._payload())

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload["identity_kind"] = self.identity_kind
        payload["content_hash"] = self.content_hash
        if self.identity_kind:
            payload["universal_id"] = self.universal_id
        return payload


def _canonical(value: Any) -> Any:
    """Key-sort mappings and tuple-ise sequences so two equal values hash identically."""
    if isinstance(value, Mapping):
        return {k: _canonical(value[k]) for k in sorted(value, key=str)}
    if isinstance(value, list | tuple):
        return tuple(_canonical(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """One hash-chained entry of the substrate's own journal — lineage for every unit."""

    sequence: int
    action: str
    subject: str
    content_hash: str
    prev_hash: str
    entry_hash: str = ""

    def __post_init__(self) -> None:
        if not self.entry_hash:
            object.__setattr__(self, "entry_hash", self.expected_hash())

    def expected_hash(self) -> str:
        return content_hash(
            [self.sequence, self.action, self.subject, self.content_hash, self.prev_hash]
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "action": self.action,
            "subject": self.subject,
            "content_hash": self.content_hash,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


ACTION_REGISTER = "register"
ACTION_SUPERSEDE = "supersede"
ACTION_RESURRECT = "resurrect"
ACTION_BIND_CONTEXT = "bind-context"


class ExistenceRegistry:
    """The one registry of everything that exists, in every form.

    Append-only. A unit is registered once and never rewritten; it is superseded, and a
    supersession may itself be reversed by resurrection — both recorded, neither deleting
    anything, so the lineage of a classification that split, merged and came back is fully
    readable from the journal.
    """

    __slots__ = ("_units", "_by_id", "_root_form", "_supersessions", "_audit", "_context")

    def __init__(self, *, root_form: str = ROOT_FORM, root_code: str = ROOT_FORM_CODE) -> None:
        self._units: dict[tuple[str, str], ExistenceUnit] = {}
        self._by_id: dict[str, tuple[str, str]] = {}
        # One append-only list per subject, not one mutable slot: resurrect() used to
        # mutate the sole record in place, which made the field-level state right after
        # supersede() and before resurrect() unrecoverable — only its hash survived
        # (P4-F-001). Each entry is now a new, complete snapshot; nothing already in the
        # list is ever edited (WP-UCDA-028).
        self._supersessions: dict[str, list[dict[str, Any]]] = {}
        self._audit: list[AuditEntry] = []
        self._context: dict[str, Any] = {}
        self._root_form = root_form.strip()
        if not self._root_form:
            raise ExistenceError("the root form must be named")
        self._bootstrap(root_code)

    # -- bootstrap ---------------------------------------------------------- #

    def _bootstrap(self, root_code: str) -> None:
        """Register the root form as a unit of itself — the self-describing fixed point."""
        identity_kind = _register_identity_kind(self._root_form, root_code)
        root = ExistenceUnit(
            form=self._root_form,
            key=self._root_form,
            title="Existence Form",
            definition=(
                "The form of forms. Registered as a unit of itself, so the substrate "
                "describes its own vocabulary and no form is privileged by the code."
            ),
            attributes={ATTR_CODE: root_code},
            identity_kind=identity_kind,
        )
        self._admit(root)

    @property
    def root_form(self) -> str:
        """The key of the self-describing root form."""
        return self._root_form

    # -- registration ------------------------------------------------------- #

    def register(self, unit: ExistenceUnit) -> ExistenceUnit:
        """Register one unit of existence, of any form.

        Raises:
            ExistenceRegistrationError: the form is unregistered or superseded, the
                classification is unregistered or superseded, or a *different* unit
                already holds this identity.
        """
        form = self.form_of(unit.form)
        if self.is_superseded_key(self._root_form, unit.form):
            raise ExistenceRegistrationError(
                "a superseded form admits no new units",
                form=unit.form,
                successors=list(self.successors_of_key(self._root_form, unit.form)),
            )
        if unit.classification:
            classification = self.find(unit.classification)
            if classification is None:
                raise ExistenceRegistrationError(
                    "a unit's classification must be a registered unit",
                    key=unit.key,
                    classification=unit.classification,
                )
            if self.is_superseded(unit.classification):
                raise ExistenceRegistrationError(
                    "a superseded classification admits no new units",
                    key=unit.key,
                    classification=unit.classification,
                    successors=list(self.successors_of(unit.classification)),
                )
        stamped = ExistenceUnit(
            form=unit.form,
            key=unit.key,
            title=unit.title,
            definition=unit.definition,
            namespace=unit.namespace,
            classification=unit.classification,
            attributes=unit.attributes,
            identity_kind=_authority_name(form.key),
        )
        return self._admit(stamped)

    def _admit(self, unit: ExistenceUnit) -> ExistenceUnit:
        index = (unit.form, unit.key)
        existing = self._units.get(index)
        if existing is not None:
            if existing.content_hash == unit.content_hash:
                return existing
            raise ExistenceRegistrationError(
                "a different unit is already registered under this identity",
                form=unit.form,
                key=unit.key,
            )
        identifier = unit.universal_id
        if not is_well_formed(identifier):  # pragma: no cover - the authority guarantees this
            raise ExistenceRegistrationError(
                "the minted identifier is not well formed", key=unit.key, identifier=identifier
            )
        self._units[index] = unit
        self._by_id[identifier] = index
        self._append(ACTION_REGISTER, identifier, unit.content_hash)
        return unit

    def register_all(self, units: Iterable[ExistenceUnit]) -> tuple[ExistenceUnit, ...]:
        return tuple(self.register(unit) for unit in units)

    def declare_form(
        self,
        key: str,
        *,
        title: str,
        code: str,
        definition: str = "",
        attributes: Mapping[str, Any] | None = None,
    ) -> ExistenceUnit:
        """Declare a new form of existence — the open extension point of the substrate.

        The form's identifier code is registered with the one identity authority, so units
        of a brand-new form are minted by the same authority as everything else and
        ``parse_kind_name`` stays total.
        """
        _register_identity_kind(key, code)
        payload = dict(attributes or {})
        payload[ATTR_CODE] = code
        return self.register(
            ExistenceUnit(
                form=self._root_form,
                key=key,
                title=title,
                definition=definition,
                attributes=payload,
            )
        )

    # -- lookup ------------------------------------------------------------- #

    def __len__(self) -> int:
        return len(self._units)

    def form_of(self, key: str) -> ExistenceUnit:
        """The unit declaring form ``key``, or fail closed."""
        found = self._units.get((self._root_form, str(key)))
        if found is None:
            raise ExistenceError(
                "form is not registered", form=str(key), registered=list(self.form_keys())
            )
        return found

    def has_form(self, key: str) -> bool:
        return (self._root_form, str(key)) in self._units

    def forms(self) -> tuple[ExistenceUnit, ...]:
        return self.units(form=self._root_form)

    def form_keys(self) -> tuple[str, ...]:
        return tuple(u.key for u in self.forms())

    def unit(self, form: str, key: str) -> ExistenceUnit:
        found = self._units.get((str(form), str(key)))
        if found is None:
            raise ExistenceError("unit is not registered", form=str(form), key=str(key))
        return found

    def has(self, form: str, key: str) -> bool:
        return (str(form), str(key)) in self._units

    def resolve(self, universal_id: str) -> ExistenceUnit:
        """Resolve by identifier, or fail closed."""
        index = self._by_id.get(str(universal_id))
        if index is None:
            raise ExistenceError("identifier is not registered", identifier=str(universal_id))
        return self._units[index]

    def find(self, universal_id: str) -> ExistenceUnit | None:
        index = self._by_id.get(str(universal_id))
        return self._units[index] if index is not None else None

    def units(
        self, *, form: str | None = None, classification: str | None = None
    ) -> tuple[ExistenceUnit, ...]:
        found = tuple(self._units[k] for k in sorted(self._units))
        if form is not None:
            found = tuple(u for u in found if u.form == form)
        if classification is not None:
            found = tuple(u for u in found if u.classification == classification)
        return found

    def identifiers(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_id))

    def counts(self) -> dict[str, int]:
        """The population by form — every form, including ones added at runtime."""
        counts: dict[str, int] = {}
        for unit in self._units.values():
            counts[unit.form] = counts.get(unit.form, 0) + 1
        return {k: counts[k] for k in sorted(counts)}

    def id_of(self, form: str, key: str) -> str:
        return self.unit(form, key).universal_id

    def form_id_of(self, universal_id: str) -> str | None:
        """The form key of a registered identifier, or ``None`` — the admissibility hook."""
        unit = self.find(universal_id)
        return unit.form if unit is not None else None

    # -- evolution: one mechanism for every construct (CEU-002/003/004/008) -- #

    def supersede(
        self,
        universal_id: str,
        *,
        successors: Sequence[str] = (),
        authority: str,
        note: str = "",
    ) -> dict[str, Any]:
        """Retire any unit in favour of zero or more successors.

        One call covers every construct and every shape of change: **split** (one
        superseded, several successors), **merge** (several superseded, one successor),
        **transform** (one for one), **deprecate** (no successor). Nothing is deleted —
        the unit stays registered and stays resolvable, because units already referring to
        it keep a readable lineage. What ends is its *admissibility* for new registrations.

        Raises:
            ExistenceError: the unit or a successor is unregistered, a successor is itself
                superseded, the unit would supersede itself, or it is already superseded
                differently.
        """
        subject = self.resolve(universal_id)
        chosen = tuple(dict.fromkeys(str(s) for s in successors))
        if not isinstance(authority, str) or not authority.strip():
            raise ExistenceError("a supersession must name its authority", subject=universal_id)
        if universal_id in chosen:
            raise ExistenceError("a unit may not supersede itself", subject=universal_id)
        for successor in chosen:
            self.resolve(successor)
            if self.is_superseded(successor):
                raise ExistenceError(
                    "a superseded unit may not be a successor",
                    subject=universal_id,
                    successor=successor,
                )
        record = {
            "subject": universal_id,
            "form": subject.form,
            "key": subject.key,
            "successors": list(chosen),
            "authority": authority.strip(),
            "note": note,
            "deprecated_outright": not chosen,
            "active": True,
        }
        history = self._supersessions.setdefault(universal_id, [])
        existing = history[-1] if history else None
        if existing is not None and existing["active"]:
            if {k: existing[k] for k in ("successors", "authority", "note")} == {
                "successors": list(chosen),
                "authority": authority.strip(),
                "note": note,
            }:
                return dict(existing)
            raise ExistenceError(
                "an active supersession may not be rewritten",
                subject=universal_id,
                existing=existing["successors"],
            )
        history.append(record)
        self._append(ACTION_SUPERSEDE, universal_id, content_hash(record))
        return dict(record)

    def resurrect(self, universal_id: str, *, authority: str, note: str = "") -> dict[str, Any]:
        """Return a superseded unit to admissibility (CEU-002).

        Resurrection is not an undo: the supersession stays in the journal and stays
        readable, and the resurrection is a further entry. What changes is only whether
        new units may be registered under it again — which is the whole of what
        supersession controlled.

        Raises:
            ExistenceError: the unit is unregistered, or is not currently superseded.
        """
        self.resolve(universal_id)
        history = self._supersessions.get(universal_id) or []
        latest = history[-1] if history else None
        if latest is None or not latest["active"]:
            raise ExistenceError("this unit is not superseded", subject=universal_id)
        if not isinstance(authority, str) or not authority.strip():
            raise ExistenceError("a resurrection must name its authority", subject=universal_id)
        # A new snapshot, appended — not a mutation of `latest`, which stays exactly as
        # supersede() left it, forever readable at its own position in the history.
        record = {
            **latest,
            "active": False,
            "resurrected_by": authority.strip(),
            "resurrection_note": note,
        }
        history.append(record)
        self._append(ACTION_RESURRECT, universal_id, content_hash(record))
        return dict(record)

    def _latest_supersession(self, universal_id: str) -> dict[str, Any] | None:
        history = self._supersessions.get(str(universal_id))
        return history[-1] if history else None

    def is_superseded(self, universal_id: str) -> bool:
        record = self._latest_supersession(universal_id)
        return bool(record and record["active"])

    def is_superseded_key(self, form: str, key: str) -> bool:
        unit = self._units.get((str(form), str(key)))
        return bool(unit) and self.is_superseded(unit.universal_id)

    def successors_of(self, universal_id: str) -> tuple[str, ...]:
        record = self._latest_supersession(universal_id)
        return tuple(record["successors"]) if record and record["active"] else ()

    def successors_of_key(self, form: str, key: str) -> tuple[str, ...]:
        unit = self._units.get((str(form), str(key)))
        return self.successors_of(unit.universal_id) if unit else ()

    def admissible(self, *, form: str | None = None) -> tuple[ExistenceUnit, ...]:
        """Units that still admit new registrations under them."""
        return tuple(u for u in self.units(form=form) if not self.is_superseded(u.universal_id))

    def supersessions(self) -> tuple[dict[str, Any], ...]:
        """The current state of every subject that has ever been superseded — one per subject."""
        return tuple(dict(self._supersessions[k][-1]) for k in sorted(self._supersessions))

    def supersession_history(self, universal_id: str) -> tuple[dict[str, Any], ...]:
        """Every snapshot ever recorded for one subject, oldest first — the field-level
        reconstruction `supersessions()` alone cannot give (P4-F-001, WP-UCDA-028)."""
        return tuple(dict(record) for record in self._supersessions.get(str(universal_id), []))

    # -- specialization, over any form -------------------------------------- #

    def ancestry(self, universal_id: str) -> tuple[str, ...]:
        """``universal_id`` and everything it specializes, nearest first, refusing a cycle.

        Works for any unit of any form, because ``specializes`` is an attribute rather
        than a field of a particular class — so a classification hierarchy, a form
        hierarchy and a topology hierarchy are the same traversal.
        """
        seen: set[str] = set()
        chain: list[str] = []
        cursor: str | None = str(universal_id)
        while cursor is not None:
            if cursor in seen:
                raise ExistenceError("cycle in the specialization graph", subject=str(universal_id))
            seen.add(cursor)
            unit = self.resolve(cursor)
            chain.append(cursor)
            parent = unit.attribute(ATTR_SPECIALIZES)
            cursor = str(parent) if parent else None
        return tuple(chain)

    def specializations_of(self, universal_id: str) -> tuple[str, ...]:
        self.resolve(universal_id)
        return tuple(
            sorted(
                u.universal_id
                for u in self._units.values()
                if u.universal_id != universal_id
                and universal_id in self._safe_ancestry(u.universal_id)
            )
        )

    def _safe_ancestry(self, universal_id: str) -> tuple[str, ...]:
        try:
            return self.ancestry(universal_id)
        except ExistenceError:  # pragma: no cover - a cycle is reported by `ancestry`
            return (universal_id,)

    def effective_attribute_set(self, universal_id: str, name: str) -> frozenset[str]:
        """The union of a tuple-valued attribute along the whole specialization chain.

        This is how a faculty held by a broader classification is held by its
        specializations without being restated — and it is form-agnostic, so it works for
        anything that specializes anything.
        """
        gathered: set[str] = set()
        for ancestor in self.ancestry(universal_id):
            gathered |= set(self.resolve(ancestor).tuple_attribute(name))
        return frozenset(gathered)

    def holds(self, universal_id: str, faculty: str) -> bool:
        """True iff the unit holds ``faculty`` directly or by specialization.

        The replacement for ``may_own_capability``: ownership is a registered fact about a
        classification, discoverable by query, not a predicate in the source.
        """
        return faculty in self.effective_attribute_set(universal_id, ATTR_FACULTIES)

    def holding(self, faculty: str, *, form: str | None = None) -> tuple[str, ...]:
        """Every unit holding ``faculty`` — how ownership rights are *discovered*."""
        return tuple(
            sorted(
                u.universal_id for u in self.units(form=form) if self.holds(u.universal_id, faculty)
            )
        )

    # -- context (CEU-006) --------------------------------------------------- #

    def bind_context(self, fingerprint: Mapping[str, Any]) -> dict[str, Any]:
        """Bind the whole substrate to one resolved reference frame.

        Deliberately the same contract as
        :meth:`engine.nucleus.registry.NucleusRegistry.bind_context` — one reality per
        registry, rebinding a different one refused — so the two registries cannot drift
        into two notions of what a context binding is.
        """
        frame = str(fingerprint.get("frame", "")).strip()
        digest = str(fingerprint.get("resolution_digest", "")).strip()
        if not frame or not digest:
            raise ExistenceError(
                "a context binding must name a frame and its resolution digest",
                frame=frame,
                resolution_digest=digest,
            )
        if self._context and self._context != dict(fingerprint):
            raise ExistenceError(
                "a registry is bound to one reality; rebasing produces a new registry",
                bound_to=self._context.get("frame"),
                offered=frame,
            )
        self._context = dict(fingerprint)
        self._append(ACTION_BIND_CONTEXT, frame, content_hash(dict(fingerprint)))
        return dict(self._context)

    @property
    def context(self) -> dict[str, Any]:
        return dict(self._context)

    @property
    def is_context_bound(self) -> bool:
        return bool(self._context)

    def require_context(self) -> dict[str, Any]:
        if not self._context:
            raise ExistenceError("this substrate is not bound to any reference frame")
        return dict(self._context)

    # -- the journal (lineage for every unit) -------------------------------- #

    def _append(self, action: str, subject: str, digest: str) -> AuditEntry:
        previous = self._audit[-1].entry_hash if self._audit else ""
        entry = AuditEntry(
            sequence=len(self._audit) + 1,
            action=action,
            subject=subject,
            content_hash=digest,
            prev_hash=previous,
        )
        self._audit.append(entry)
        return entry

    def audit(self, *, subject: str | None = None) -> tuple[AuditEntry, ...]:
        found = tuple(self._audit)
        if subject is not None:
            found = tuple(e for e in found if e.subject == subject)
        return found

    def verify_audit(self) -> list[str]:
        """Findings; empty means the chain reproduces end to end."""
        problems: list[str] = []
        previous = ""
        for index, entry in enumerate(self._audit, start=1):
            if entry.sequence != index:
                problems.append(f"{entry.subject}: sequence {entry.sequence} != {index}")
            if entry.prev_hash != previous:
                problems.append(f"{entry.subject}: back-link does not match")
            if entry.entry_hash != entry.expected_hash():
                problems.append(f"{entry.subject}: entry digest does not reproduce")
            previous = entry.entry_hash
        return problems

    def unlineaged(self) -> tuple[str, ...]:
        """Registered identifiers with no journal entry — must always be empty."""
        journaled = {e.subject for e in self._audit}
        return tuple(sorted(i for i in self._by_id if i not in journaled))

    # -- serialisation ------------------------------------------------------- #

    def to_document(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-existence-registry",
            "version": "1.0.0",
            "root_form": self._root_form,
            "counts": {
                "units": len(self._units),
                "forms": len(self.forms()),
                "admissible": len(self.admissible()),
                "superseded": sum(1 for h in self._supersessions.values() if h and h[-1]["active"]),
                "by_form": self.counts(),
            },
            "context": dict(self._context),
            "units": [self._units[k].to_dict() for k in sorted(self._units)],
            "supersessions": [dict(s) for s in self.supersessions()],
            # Every snapshot per subject, not only its current state — the field-level
            # history `supersessions()` alone collapses to one row per subject (P4-F-001,
            # WP-UCDA-028). Additive: existing consumers of "supersessions" are unaffected.
            "supersession_history": {
                subject: [dict(record) for record in records]
                for subject, records in sorted(self._supersessions.items())
            },
            # The whole journal, not just its head. Steering 022: Repository Truth must be
            # *sufficient* to reconstruct constitutional state, and a head alone proves the
            # chain was intact without carrying what it was a chain of.
            "audit": [entry.to_dict() for entry in self._audit],
            "audit_head": self._audit[-1].entry_hash if self._audit else "",
            "closed_set": False,
            "upper_limit": None,
        }

    def digest(self) -> str:
        return content_hash(self.to_document())

    def seal(self) -> str:
        return self.digest()

    # -- reconstruction (Steering 022) --------------------------------------- #

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> ExistenceRegistry:
        """Rebuild a registry from its own document, with no hidden runtime state.

        The reconstruction is *verbatim*, not a re-derivation: units, supersessions,
        context and the journal are loaded exactly as recorded, and the resulting digest
        must equal the source document's. Re-deriving would let the rebuilt registry
        differ from the recorded one and still look healthy — which is the failure this
        exists to make impossible.

        Bootstrapping is deliberately skipped. The root form is a *unit in the document*
        like any other, so replaying the document must reproduce it rather than a fresh
        bootstrap manufacturing a second one with its own journal entry.

        Raises:
            ExistenceError: the document is malformed, or its journal does not verify.
        """
        if not isinstance(payload, Mapping) or not isinstance(payload.get("units"), list):
            raise ExistenceError("an existence document must carry a 'units' list")
        root_form = str(payload.get("root_form", "")).strip()
        if not root_form:
            raise ExistenceError("an existence document must name its root form")

        registry = cls.__new__(cls)
        registry._units = {}
        registry._by_id = {}
        registry._supersessions = {}
        registry._audit = []
        registry._context = dict(payload.get("context") or {})
        registry._root_form = root_form

        raw_units = [u for u in payload["units"] if isinstance(u, Mapping)]
        # Forms first: a unit's identifier is minted under its *form's* registered kind,
        # so every form's code must be known to the one identity authority before any
        # unit of that form can resolve its own identity.
        for item in raw_units:
            if item.get("form") == root_form:
                _register_identity_kind(
                    str(item.get("key", "")),
                    str((item.get("attributes") or {}).get(ATTR_CODE, "")),
                )
        for item in raw_units:
            unit = ExistenceUnit(
                form=str(item["form"]),
                key=str(item["key"]),
                title=str(item["title"]),
                definition=str(item.get("definition", "")),
                namespace=str(item.get("namespace") or EXISTENCE_NAMESPACE),
                classification=str(item.get("classification", "")),
                attributes=item.get("attributes") or {},
                identity_kind=str(item.get("identity_kind", "")),
                content_hash=str(item.get("content_hash", "")),
            )
            if not unit.is_intact():
                raise ExistenceError(
                    "a recorded unit does not reproduce its own digest",
                    form=unit.form,
                    key=unit.key,
                )
            registry._units[(unit.form, unit.key)] = unit
            registry._by_id[unit.universal_id] = (unit.form, unit.key)

        history_payload = payload.get("supersession_history")
        if isinstance(history_payload, Mapping):
            for subject, records in history_payload.items():
                if isinstance(records, list):
                    registry._supersessions[str(subject)] = [
                        dict(r) for r in records if isinstance(r, Mapping)
                    ]
        else:
            # Older document, current-state summaries only (single entry per subject) —
            # every fresh registry's own to_document() output before this fix took this
            # exact shape, so this remains a faithful, lossless read of that shape.
            for record in payload.get("supersessions") or []:
                if isinstance(record, Mapping) and record.get("subject"):
                    registry._supersessions[str(record["subject"])] = [dict(record)]

        for entry in payload.get("audit") or []:
            if not isinstance(entry, Mapping):
                continue
            registry._audit.append(
                AuditEntry(
                    sequence=int(entry["sequence"]),
                    action=str(entry["action"]),
                    subject=str(entry["subject"]),
                    content_hash=str(entry["content_hash"]),
                    prev_hash=str(entry["prev_hash"]),
                    entry_hash=str(entry.get("entry_hash", "")),
                )
            )
        problems = registry.verify_audit()
        if problems:
            raise ExistenceError("the recorded journal does not verify", findings=problems[:5])
        return registry


def reconstruct(registry: ExistenceRegistry) -> dict[str, Any]:
    """Rebuild a registry from its own document and report whether truth was sufficient.

    This is Steering 022 as a measurement: if the document is sufficient, the rebuilt
    registry's digest, journal head and population all match. Any divergence names state
    that lived only in memory — the "hidden runtime state" the principle forbids.
    """
    document = registry.to_document()
    rebuilt = ExistenceRegistry.from_document(document)
    rebuilt_document = rebuilt.to_document()
    divergent = sorted(k for k in document if document[k] != rebuilt_document.get(k))
    return {
        "schema": "ucos-existence-reconstruction",
        "version": "1.0.0",
        "source_digest": registry.digest(),
        "rebuilt_digest": rebuilt.digest(),
        "source_units": len(registry),
        "rebuilt_units": len(rebuilt),
        "audit_head_matches": document["audit_head"] == rebuilt_document["audit_head"],
        "divergent_sections": divergent,
        "journal_verifies": rebuilt.verify_audit() == [],
        "reconstructed": registry.digest() == rebuilt.digest() and not divergent,
    }


def _authority_name(form_key: str) -> str:
    """The name the one identity authority knows a form by."""
    return form_key.replace("-", "_").upper()


def _register_identity_kind(key: str, code: str) -> str:
    """Make ``key`` mintable by the one identifier authority; return its authority name.

    A name the authority already knows is reused rather than re-registered, so the
    substrate adds no second grammar and claims no duplicate code. The authority owns the
    name→code mapping; this function never stores one.
    """
    name = _authority_name(key)
    if name in {k.value for k in RegistryKind} or name in kind_names():
        resolve_kind_code(name)
        return name
    register_identifier_kind(name, code)
    return name


# --------------------------------------------------------------------------- #
# Relationships — units of existence that happen to have endpoints (CEU-003)   #
# --------------------------------------------------------------------------- #


class RelationshipView:
    """Relationship reads and writes over the one registry — not a second registry.

    A relationship *type* is a unit; a relationship is a unit; a topology is a unit. This
    class holds no state of its own: it is the typed way to say "register a unit of the
    relationship form with these endpoints", and the typed way to ask the questions a
    graph is good at. Every relationship it creates is therefore identified, journaled,
    supersedable and evolvable exactly like every other unit, because it *is* one.
    """

    __slots__ = ("_registry", "_type_form", "_relationship_form", "_topology_form")

    def __init__(
        self,
        registry: ExistenceRegistry,
        *,
        type_form: str,
        relationship_form: str,
        topology_form: str,
    ) -> None:
        self._registry = registry
        self._type_form = type_form
        self._relationship_form = relationship_form
        self._topology_form = topology_form
        for form in (type_form, relationship_form, topology_form):
            registry.form_of(form)

    @property
    def registry(self) -> ExistenceRegistry:
        return self._registry

    # -- assertion ---------------------------------------------------------- #

    def relate(
        self,
        relationship_type: str,
        source: str,
        target: str,
        *,
        authority: str,
        topologies: Sequence[str] = (),
        attributes: Mapping[str, Any] | None = None,
        note: str = "",
    ) -> ExistenceUnit:
        """Assert one relationship as a registered unit of existence.

        Raises:
            RelationshipError: the type is unregistered or superseded.
            RelationshipAdmissibilityError: an endpoint is unregistered, or its form or
                classification is not admitted by the type's declared constraints.
            TopologyCycleError: the type declares itself acyclic and this closes a cycle.
        """
        declared = self._require_type(relationship_type)
        arrangement = tuple(
            dict.fromkeys((*declared.tuple_attribute(ATTR_TOPOLOGIES), *topologies))
        )
        for topology in arrangement:
            self._registry.unit(self._topology_form, topology)
        self._check_admissible(declared, source, "source")
        self._check_admissible(declared, target, "target")

        payload = dict(attributes or {})
        payload.update(
            {
                ATTR_RELATIONSHIP_TYPE: declared.key,
                ATTR_SOURCE: source,
                ATTR_TARGET: target,
                ATTR_TOPOLOGIES: arrangement,
                "authority": authority,
            }
        )
        unit = self._registry.register(
            ExistenceUnit(
                form=self._relationship_form,
                key=f"{declared.key}:{source}->{target}",
                title=f"{declared.title}: {source} → {target}",
                definition=note,
                classification=declared.universal_id,
                attributes=payload,
            )
        )
        if declared.attribute(ATTR_ACYCLIC):
            cycle = self.cycle_in(declared.key)
            if cycle:
                raise TopologyCycleError(
                    "this relationship type is acyclic and this edge closes a cycle",
                    relationship=declared.key,
                    cycle=list(cycle),
                )
        if declared.attribute(ATTR_SYMMETRIC) and source != target:
            # Registered directly rather than by recursing through `relate`: the mirror of
            # a mirror is the original, so a recursive call would never terminate. The
            # mirror skips the admissibility check too, because it was just performed on
            # the same pair in the other order — and for a symmetric type those are the
            # same question.
            mirror = dict(payload)
            mirror[ATTR_SOURCE], mirror[ATTR_TARGET] = target, source
            self._registry.register(
                ExistenceUnit(
                    form=self._relationship_form,
                    key=f"{declared.key}:{target}->{source}",
                    title=f"{declared.title}: {target} → {source}",
                    definition=note,
                    classification=declared.universal_id,
                    attributes=mirror,
                )
            )
        return unit

    def _require_type(self, key: str) -> ExistenceUnit:
        try:
            declared = self._registry.unit(self._type_form, key)
        except ExistenceError as exc:
            raise RelationshipError(
                "relationship type is not registered", relationship=key
            ) from exc
        if self._registry.is_superseded(declared.universal_id):
            raise RelationshipError(
                "a superseded relationship type admits no new relationships",
                relationship=key,
                successors=list(self._registry.successors_of(declared.universal_id)),
            )
        return declared

    def _check_admissible(self, declared: ExistenceUnit, endpoint: str, role: str) -> None:
        """Registry-driven validity (CEU-007): a constraint applies only if declared."""
        unit = self._registry.find(endpoint)
        if unit is None:
            raise RelationshipAdmissibilityError(
                "a relationship endpoint must be a registered unit",
                relationship=declared.key,
                at=role,
                endpoint=endpoint,
            )
        forms = declared.tuple_attribute(
            ATTR_SOURCE_FORMS if role == "source" else ATTR_TARGET_FORMS
        )
        if forms and unit.form not in forms:
            raise RelationshipAdmissibilityError(
                "this relationship type does not admit that form",
                relationship=declared.key,
                at=role,
                endpoint=endpoint,
                form=unit.form,
                admitted=list(forms),
            )
        classifications = declared.tuple_attribute(
            ATTR_SOURCE_CLASSIFICATIONS if role == "source" else ATTR_TARGET_CLASSIFICATIONS
        )
        if classifications and unit.classification not in classifications:
            raise RelationshipAdmissibilityError(
                "this relationship type does not admit that classification",
                relationship=declared.key,
                at=role,
                endpoint=endpoint,
                classification=unit.classification,
                admitted=list(classifications),
            )

    # -- query -------------------------------------------------------------- #

    def relationships(
        self,
        *,
        relationship_type: str | None = None,
        topology: str | None = None,
        source: str | None = None,
        target: str | None = None,
    ) -> tuple[ExistenceUnit, ...]:
        found = self._registry.units(form=self._relationship_form)
        if relationship_type is not None:
            found = tuple(
                u for u in found if u.attribute(ATTR_RELATIONSHIP_TYPE) == relationship_type
            )
        if topology is not None:
            found = tuple(u for u in found if topology in u.tuple_attribute(ATTR_TOPOLOGIES))
        if source is not None:
            found = tuple(u for u in found if u.attribute(ATTR_SOURCE) == source)
        if target is not None:
            found = tuple(u for u in found if u.attribute(ATTR_TARGET) == target)
        return found

    def neighbours(self, unit_id: str, **filters: Any) -> tuple[str, ...]:
        found = self.relationships(source=unit_id, **filters)
        return tuple(sorted({str(u.attribute(ATTR_TARGET)) for u in found}))

    def inbound(self, unit_id: str, **filters: Any) -> tuple[str, ...]:
        found = self.relationships(target=unit_id, **filters)
        return tuple(sorted({str(u.attribute(ATTR_SOURCE)) for u in found}))

    def participants(self, topology: str) -> tuple[str, ...]:
        self._registry.unit(self._topology_form, topology)
        members: set[str] = set()
        for relationship in self.relationships(topology=topology):
            members.add(str(relationship.attribute(ATTR_SOURCE)))
            members.add(str(relationship.attribute(ATTR_TARGET)))
        return tuple(sorted(members))

    def topologies_of(self, unit_id: str) -> tuple[str, ...]:
        """Every arrangement one unit participates in, simultaneously (CEU-004)."""
        arrangements: set[str] = set()
        for relationship in self.relationships():
            endpoints = (relationship.attribute(ATTR_SOURCE), relationship.attribute(ATTR_TARGET))
            if unit_id in endpoints:
                arrangements |= set(relationship.tuple_attribute(ATTR_TOPOLOGIES))
        return tuple(sorted(arrangements))

    def adjacency(self, relationship_type: str) -> dict[str, tuple[str, ...]]:
        graph: dict[str, list[str]] = {}
        for relationship in self.relationships(relationship_type=relationship_type):
            source = str(relationship.attribute(ATTR_SOURCE))
            target = str(relationship.attribute(ATTR_TARGET))
            graph.setdefault(source, []).append(target)
            graph.setdefault(target, [])
        return {k: tuple(sorted(v)) for k, v in sorted(graph.items())}

    def cycle_in(self, relationship_type: str) -> tuple[str, ...]:
        """The first cycle in one relationship type, via the one cycle detector."""
        adjacency = {k: list(v) for k, v in self.adjacency(relationship_type).items()}
        found = detect_cycle(adjacency)
        return tuple(found) if found else ()

    def reachable(self, unit_id: str, relationship_type: str) -> tuple[str, ...]:
        adjacency = self.adjacency(relationship_type)
        seen: set[str] = set()
        frontier = list(adjacency.get(unit_id, ()))
        while frontier:
            current = frontier.pop()
            if current in seen:
                continue
            seen.add(current)
            frontier.extend(adjacency.get(current, ()))
        return tuple(sorted(seen))

    def dangling(self) -> tuple[str, ...]:
        """Relationship endpoints that name no registered unit. Must always be empty."""
        missing: set[str] = set()
        for relationship in self.relationships():
            for endpoint in (
                relationship.attribute(ATTR_SOURCE),
                relationship.attribute(ATTR_TARGET),
            ):
                if self._registry.find(str(endpoint)) is None:
                    missing.add(str(endpoint))
        return tuple(sorted(missing))

    def to_document(self) -> dict[str, Any]:
        return {
            "schema": "ucos-ceu-relationships",
            "version": "1.0.0",
            "count": len(self.relationships()),
            "types": [u.key for u in self._registry.units(form=self._type_form)],
            "topologies": [u.key for u in self._registry.units(form=self._topology_form)],
            "relationships": [u.to_dict() for u in self.relationships()],
            "dangling": list(self.dangling()),
            "closed_set": False,
            "upper_limit": None,
        }

    def digest(self) -> str:
        return content_hash(self.to_document())


__all__ = [
    "ROOT_FORM",
    "ROOT_FORM_CODE",
    "EXISTENCE_NAMESPACE",
    "ATTR_CODE",
    "ATTR_SPECIALIZES",
    "ATTR_FACULTIES",
    "ATTR_RELATIONSHIP_TYPE",
    "ATTR_SOURCE",
    "ATTR_TARGET",
    "ATTR_TOPOLOGIES",
    "ATTR_ACYCLIC",
    "ATTR_SYMMETRIC",
    "ATTR_SOURCE_FORMS",
    "ATTR_TARGET_FORMS",
    "ATTR_SOURCE_CLASSIFICATIONS",
    "ATTR_TARGET_CLASSIFICATIONS",
    "ATTR_CLASSIFICATION",
    "ACTION_REGISTER",
    "ACTION_SUPERSEDE",
    "ACTION_RESURRECT",
    "ACTION_BIND_CONTEXT",
    "ExistenceUnit",
    "AuditEntry",
    "ExistenceRegistry",
    "RelationshipView",
    "reconstruct",
]

"""UCOS-NUC-001 Part 04 — the Nucleus Ownership Authority (D-04, D-05, D-06, D-07).

This is the single place a Nucleus, Layer, Composition, Capability or ownership
assignment becomes Repository Truth for *structural* purposes. It is not a second
artifact registry: identifiers come from :mod:`engine.registry.universal.identity`,
digests from :mod:`engine.uckp.canonical`, structural-role terms from
:mod:`engine.uckp.vocabulary`, and the selection graph is ordered by the single
ordering authority :mod:`engine.foundation.composition.ordering`. What is new here — and
only here — is *enforcement of the ownership law*, which nothing in the repository did
before.

Fail-closed, at the point of registration
-----------------------------------------
The law is not measured after the fact. Every one of these is refused at admission:

    * a capability whose owner is a Layer (NL-02) or a Composition (NL-03);
    * a capability with no owner — unrepresentable, the field is mandatory (NL-04);
    * a second owner for a capability that already has one, unless the assignment names
      the one it supersedes (NL-04, NL-10);
    * a subject whose declared role contradicts its derived role (NL-06);
    * a capability whose domain resolves to a registered composition (NL-07);
    * a composition selecting an unregistered subject, or selecting something that is
      not a Nucleus, or introducing a cycle (NL-08);
    * a reference to any unregistered subject (NL-09).

So "Commerce owns a capability" is not a finding to be reported later; it is a
:class:`~engine.nucleus.errors.CompositionOwnershipViolation` at the moment of the
attempt.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from engine.foundation.composition.ordering import (
    DEFAULT_STRATEGY,
    derive_order,
    unresolved_keys,
)
from engine.nucleus.catalog import seed_capabilities, seed_subjects
from engine.nucleus.errors import (
    CompositionOwnershipViolation,
    ContextBindingViolation,
    LayerOwnershipViolation,
    OwnershipViolation,
    RegistrationError,
    StructuralValidationError,
)
from engine.nucleus.law import (
    LAW_ID,
    OWNERSHIP_CLAUSES,
    StructuralRole,
    structural_role_terms,
)
from engine.nucleus.model import (
    CapabilityDeclaration,
    CapabilityRecord,
    OwnershipAssignment,
    SubjectDeclaration,
    SubjectRecord,
)
from engine.uckp.canonical import content_hash
from engine.uckp.vocabulary import Term, VocabularyRegistry, build_vocabulary_registry

#: The vocabulary identifier under which the structural roles are registered.
STRUCTURAL_ROLE_VOCABULARY = "ucos.structural-role"

#: The authority string recorded on every seed ownership assignment.
SEED_AUTHORITY = LAW_ID


class NucleusRegistry:
    """The registry of structural subjects, capabilities and ownership.

    The instance is append-only: :meth:`register_subject` and
    :meth:`register_capability` add, and ownership moves by supersession. Nothing is
    deleted, so lineage survives every change (NL-10).
    """

    __slots__ = (
        "_subjects",
        "_by_id",
        "_capabilities",
        "_assignments",
        "_vocabularies",
        "_context",
    )

    def __init__(self, *, vocabularies: VocabularyRegistry | None = None) -> None:
        # Indexed by ``(role, key)``: a layer named ``governance`` and a nucleus named
        # ``governance`` are different subjects with different identifier kinds, and
        # collapsing them into one key space would manufacture the ownership ambiguity
        # AC-011 forbids. Lookup by bare key stays available and refuses when ambiguous.
        self._subjects: dict[tuple[str, str], SubjectRecord] = {}
        self._by_id: dict[str, tuple[str, str]] = {}
        self._capabilities: dict[str, CapabilityRecord] = {}
        self._assignments: list[OwnershipAssignment] = []
        self._vocabularies = vocabularies or build_vocabulary_registry()
        self._context: dict[str, Any] = {}
        self._register_role_vocabulary()

    # -- context ------------------------------------------------------------ #

    @property
    def context(self) -> dict[str, Any]:
        """The reference-frame fingerprint this registry is bound to, or ``{}``."""
        return dict(self._context)

    @property
    def is_context_bound(self) -> bool:
        """True iff this registry has been bound to a resolved reference frame."""
        return bool(self._context)

    def bind_context(self, fingerprint: Mapping[str, Any]) -> dict[str, Any]:
        """Bind the whole registered population to one resolved reference frame.

        A registry describes one reality. Binding is therefore *once*: re-binding the
        same frame is idempotent, and re-binding a different one is refused, because a
        population whose reality can change retroactively invalidates every certificate
        and every lineage entry already issued under the old one. Moving to another frame
        is a new registry — which is exactly what a rebase produces.

        The argument is a plain mapping rather than a resolution object so this module
        keeps no dependency on the context layer: the registry records the coordinate it
        was given and refuses an unusable one; it does not resolve.

        Raises:
            ContextBindingViolation: the fingerprint names no frame or no resolution
                digest, or the registry is already bound to a different frame.
        """
        frame = str(fingerprint.get("frame", "")).strip()
        digest = str(fingerprint.get("resolution_digest", "")).strip()
        if not frame or not digest:
            raise ContextBindingViolation(
                "a context binding must name a frame and its resolution digest",
                frame=frame,
                resolution_digest=digest,
            )
        if self._context and self._context != dict(fingerprint):
            raise ContextBindingViolation(
                "a registry is bound to one reality; rebasing produces a new registry",
                bound_to=self._context.get("frame"),
                offered=frame,
            )
        self._context = dict(fingerprint)
        return dict(self._context)

    def require_context(self) -> dict[str, Any]:
        """Return the binding, or fail closed. The read every enforcing caller uses.

        Raises:
            ContextBindingViolation: the registry is unbound.
        """
        if not self._context:
            raise ContextBindingViolation(
                "this population is not bound to any reference frame",
                subjects=len(self._subjects),
            )
        return dict(self._context)

    # -- vocabulary --------------------------------------------------------- #

    def _register_role_vocabulary(self) -> None:
        """Register the structural roles through the *one* vocabulary authority.

        Article 17 requires an unknown future member to be admitted by registration.
        The roles therefore live in the vocabulary registry, not only in the enum, and
        :meth:`require_role_term` refuses an unregistered role at the point of use.
        """
        from engine.uckp.vocabulary import Vocabulary

        if self._vocabularies.get(STRUCTURAL_ROLE_VOCABULARY) is None:
            self._vocabularies.register(
                Vocabulary(
                    STRUCTURAL_ROLE_VOCABULARY,
                    "the structural role a registered constitutional subject holds",
                    tuple(
                        Term(term_id, definition) for term_id, definition in structural_role_terms()
                    ),
                )
            )

    @property
    def vocabularies(self) -> VocabularyRegistry:
        """The vocabulary registry this authority admits terms through."""
        return self._vocabularies

    def require_role_term(self, role: StructuralRole | str) -> Term:
        """Fail closed if ``role`` is not a registered structural-role term."""
        value = getattr(role, "value", role)
        return self._vocabularies.require_term(STRUCTURAL_ROLE_VOCABULARY, str(value))

    def register_role(self, term_id: str, definition: str) -> Term:
        """Admit a **future** structural role by registration (AC-009, Article 17).

        The role becomes a legal declaration value immediately. It confers no ownership
        right: only :attr:`StructuralRole.may_own_capability` grants that, and that
        remains a property of the law, not of the vocabulary.
        """
        term = Term(term_id, definition)
        self._vocabularies.extend(STRUCTURAL_ROLE_VOCABULARY, term)
        return term

    # -- subjects ----------------------------------------------------------- #

    def register_subject(self, declaration: SubjectDeclaration) -> SubjectRecord:
        """Admit one structural subject, enforcing NL-06, NL-08 and NL-09.

        Raises:
            RegistrationError: the (role, key) pair or the identity is already registered,
                or a selection names an unregistered subject.
            OwnershipViolation: a selection names a subject that is not a Nucleus.
        """
        self.require_role_term(declaration.structural_role)
        index = (declaration.structural_role.value, declaration.key)
        if index in self._subjects:
            raise RegistrationError(
                "structural subject is already registered",
                subject=declaration.key,
                role=declaration.structural_role.value,
            )
        record = SubjectRecord.of(declaration)
        if record.universal_id in self._by_id:
            existing = self._by_id[record.universal_id]
            raise RegistrationError(
                "identity collision between two structural subjects",
                subject=declaration.key,
                existing=f"{existing[0]}:{existing[1]}",
                universal_id=record.universal_id,
            )
        for selected in record.composes:
            target = self._subjects.get((StructuralRole.NUCLEUS.value, selected))
            if target is None:
                raise RegistrationError(
                    "a composition may only select a registered nucleus (NL-08)",
                    subject=record.key,
                    selects=selected,
                )
        if record.parent is not None and not self._any_role(record.parent):
            raise RegistrationError(
                "a subject's parent must itself be registered (NL-09)",
                subject=record.key,
                parent=record.parent,
            )
        self._subjects[index] = record
        self._by_id[record.universal_id] = index
        return record

    def _any_role(self, key: str) -> bool:
        return any(existing_key == key for _role, existing_key in self._subjects)

    def register_subjects(
        self, declarations: Iterable[SubjectDeclaration]
    ) -> tuple[SubjectRecord, ...]:
        """Admit many subjects in the order given."""
        return tuple(self.register_subject(d) for d in declarations)

    # -- capabilities + ownership ------------------------------------------- #

    def register_capability(
        self, declaration: CapabilityDeclaration, *, authority: str = SEED_AUTHORITY
    ) -> CapabilityRecord:
        """Admit one capability and its ownership assignment, enforcing NL-01…NL-04, NL-07.

        Raises:
            RegistrationError: the capability is already registered, or its owner is not
                a registered subject.
            LayerOwnershipViolation: the owner holds the LAYER role (NL-02).
            CompositionOwnershipViolation: the owner holds the COMPOSITION role (NL-03).
            OwnershipViolation: the capability's domain resolves to a composition (NL-07).
        """
        if declaration.key in self._capabilities:
            raise RegistrationError("capability is already registered", capability=declaration.key)
        owner = self._resolve_owner(declaration.owner, capability=declaration.key)
        self._require_lawful_owner(owner, capability=declaration.key)
        domain = declaration.key.split(".", 1)[0]
        if (StructuralRole.COMPOSITION.value, domain) in self._subjects:
            raise OwnershipViolation(
                "no capability may be specific to a composition (NL-07)",
                capability=declaration.key,
                composition=domain,
            )
        record = CapabilityRecord(
            universal_id=declaration.identity,
            key=declaration.key,
            title=declaration.title,
            owner_key=owner.key,
            owner_id=owner.universal_id,
            namespace=declaration.namespace,
            description=declaration.description,
            depends_on=declaration.depends_on,
        )
        self._capabilities[record.key] = record
        self._assignments.append(
            OwnershipAssignment(
                capability_id=record.universal_id,
                capability_key=record.key,
                owner_id=owner.universal_id,
                owner_key=owner.key,
                owner_role=owner.role,
                authority=authority,
            )
        )
        return record

    def register_capabilities(
        self, declarations: Iterable[CapabilityDeclaration], *, authority: str = SEED_AUTHORITY
    ) -> tuple[CapabilityRecord, ...]:
        return tuple(self.register_capability(d, authority=authority) for d in declarations)

    def _resolve_owner(self, key: str, *, capability: str) -> SubjectRecord:
        """Resolve a declared capability owner.

        A nucleus with this key wins, because a nucleus is the only lawful owner. If no
        nucleus carries the key, whatever subject does is returned so that
        :meth:`_require_lawful_owner` can refuse it with the clause it breaks — a refusal
        naming NL-02 is more useful than a bare "not found".
        """
        nucleus = self._subjects.get((StructuralRole.NUCLEUS.value, key))
        if nucleus is not None:
            return nucleus
        for (_role, existing_key), record in sorted(self._subjects.items()):
            if existing_key == key:
                return record
        raise RegistrationError(
            "a capability's owner must be a registered subject (NL-09)",
            capability=capability,
            owner=key,
        )

    def _require_lawful_owner(self, owner: SubjectRecord, *, capability: str) -> None:
        """Refuse an owner the ownership authority does not grant ownership to.

        The decision is the first line and nothing else: ``may_own_capability`` resolves
        through :mod:`engine.nucleus.authority` to the CEU registry, so what may own is a
        registered fact. The branches below only choose *which typed refusal* to raise for
        a role, which is reporting — and the final ``raise`` catches any role with no
        specific clause, so an owner is refused whether or not a clause names its role.
        """
        if owner.may_own_capability:
            return
        if owner.role is StructuralRole.LAYER:
            raise LayerOwnershipViolation(
                "layers own nothing; a capability's owner must be a nucleus (NL-02)",
                capability=capability,
                owner=owner.key,
                owner_role=owner.role.value,
                clause="NL-02",
            )
        if owner.role is StructuralRole.COMPOSITION:
            raise CompositionOwnershipViolation(
                "a composition selects nuclei and owns nothing (NL-03)",
                capability=capability,
                owner=owner.key,
                owner_role=owner.role.value,
                clause="NL-03",
            )
        raise OwnershipViolation(
            "only a nucleus may own a capability (NL-01)",
            capability=capability,
            owner=owner.key,
            owner_role=owner.role.value,
            clause="NL-01",
        )

    def reassign_capability(
        self, capability_key: str, *, new_owner: str, authority: str, note: str = ""
    ) -> OwnershipAssignment:
        """Move ownership by **supersession**, preserving the chain of custody (NL-10).

        Raises:
            RegistrationError: the capability or the new owner is not registered.
            OwnershipViolation: the new owner may not own a capability.
        """
        current = self.assignment_for(capability_key)
        owner = self._resolve_owner(new_owner, capability=capability_key)
        self._require_lawful_owner(owner, capability=capability_key)
        record = self._capabilities[capability_key]
        moved = OwnershipAssignment(
            capability_id=record.universal_id,
            capability_key=record.key,
            owner_id=owner.universal_id,
            owner_key=owner.key,
            owner_role=owner.role,
            authority=authority,
            supersedes=current.assignment_id,
            note=note,
        )
        self._assignments.append(moved)
        self._capabilities[capability_key] = CapabilityRecord(
            universal_id=record.universal_id,
            key=record.key,
            title=record.title,
            owner_key=owner.key,
            owner_id=owner.universal_id,
            namespace=record.namespace,
            description=record.description,
            depends_on=record.depends_on,
        )
        return moved

    # -- lookup ------------------------------------------------------------- #

    def subject(self, key: str, *, role: StructuralRole | str | None = None) -> SubjectRecord:
        """Return the registered subject for ``key``.

        With ``role`` given, the lookup is exact. Without it, a key carried by more than
        one role is **ambiguous** and is refused rather than silently resolved — a bare
        name that could mean either a layer or a nucleus is precisely the ambiguity that
        lets ownership drift.
        """
        if role is not None:
            found = self._subjects.get((StructuralRole.coerce(role, at=key).value, key))
            if found is None:
                raise RegistrationError(
                    "structural subject is not registered",
                    subject=key,
                    role=StructuralRole.coerce(role, at=key).value,
                )
            return found
        matches = [
            record
            for (_role, existing_key), record in sorted(self._subjects.items())
            if existing_key == key
        ]
        if not matches:
            raise RegistrationError("structural subject is not registered", subject=key)
        if len(matches) > 1:
            raise RegistrationError(
                "subject key is carried by more than one role; name the role",
                subject=key,
                roles=[m.role.value for m in matches],
            )
        return matches[0]

    def nucleus(self, key: str) -> SubjectRecord:
        """The nucleus registered under ``key``."""
        return self.subject(key, role=StructuralRole.NUCLEUS)

    def subject_by_id(self, universal_id: str) -> SubjectRecord:
        index = self._by_id.get(universal_id)
        if index is None:
            raise RegistrationError("no subject carries that identity", universal_id=universal_id)
        return self._subjects[index]

    def has_subject(self, key: str, *, role: StructuralRole | str | None = None) -> bool:
        if role is not None:
            return (StructuralRole.coerce(role, at=key).value, key) in self._subjects
        return self._any_role(key)

    def subjects(self, *, role: StructuralRole | str | None = None) -> tuple[SubjectRecord, ...]:
        """Every registered subject, ordered by (role, key), optionally filtered by role."""
        records = tuple(self._subjects[index] for index in sorted(self._subjects))
        if role is None:
            return records
        wanted = StructuralRole.coerce(role)
        return tuple(r for r in records if r.role is wanted)

    def nuclei(self) -> tuple[SubjectRecord, ...]:
        return self.subjects(role=StructuralRole.NUCLEUS)

    def layers(self) -> tuple[SubjectRecord, ...]:
        return self.subjects(role=StructuralRole.LAYER)

    def compositions(self) -> tuple[SubjectRecord, ...]:
        return self.subjects(role=StructuralRole.COMPOSITION)

    def capability(self, key: str) -> CapabilityRecord:
        record = self._capabilities.get(key)
        if record is None:
            raise RegistrationError("capability is not registered", capability=key)
        return record

    def capabilities(self, *, owner: str | None = None) -> tuple[CapabilityRecord, ...]:
        records = tuple(self._capabilities[key] for key in sorted(self._capabilities))
        if owner is None:
            return records
        return tuple(r for r in records if r.owner_key == owner)

    def assignments(self, *, capability_key: str | None = None) -> tuple[OwnershipAssignment, ...]:
        """Every ownership assignment ever recorded, in registration order."""
        if capability_key is None:
            return tuple(self._assignments)
        return tuple(a for a in self._assignments if a.capability_key == capability_key)

    def assignment_for(self, capability_key: str) -> OwnershipAssignment:
        """The current (latest) ownership assignment for a capability."""
        history = self.assignments(capability_key=capability_key)
        if not history:
            raise RegistrationError(
                "capability has no ownership assignment", capability=capability_key
            )
        return history[-1]

    def owner_of(self, capability_key: str) -> SubjectRecord:
        """The nucleus that owns ``capability_key``."""
        return self.subject_by_id(self.capability(capability_key).owner_id)

    # -- composition -------------------------------------------------------- #

    def selection_graph(self) -> dict[str, tuple[str, ...]]:
        """The composition selection graph: subject key → the keys it requires.

        A composition requires the nuclei it selects; a nucleus and a layer require
        nothing structurally. Keys are role-qualified so a layer and a nucleus sharing a
        name remain two distinct vertices. The graph is expressed in the shape the single
        ordering authority already consumes.
        """
        graph: dict[str, tuple[str, ...]] = {}
        for record in self.subjects():
            vertex = f"{record.role.value}:{record.key}"
            graph[vertex] = tuple(
                f"{StructuralRole.NUCLEUS.value}:{selected}" for selected in record.composes
            )
        return graph

    def composition_order(self, *, strategy: str = DEFAULT_STRATEGY) -> list[tuple[int, str]]:
        """The order in which subjects compose, derived by the *one* ordering authority.

        Reuses :func:`engine.foundation.composition.ordering.derive_order` rather than
        carrying a private topological sort, so this authority becomes one more lawful
        consumer of the single ordering mechanism instead of a seventh private one.
        """
        return derive_order(self.selection_graph(), strategy=strategy)

    def selection_cycles(self) -> tuple[str, ...]:
        """Keys the ordering authority could not place — i.e. keys inside a cycle."""
        graph = self.selection_graph()
        return tuple(unresolved_keys(graph, derive_order(graph)))

    def compose(self, composition_key: str) -> dict[str, Any]:
        """Realise a composition: its selected nuclei and the capabilities they bring.

        This is the whole of "Commerce". No commerce-specific code runs; the result is
        derived from registered nuclei and their registered capabilities. A composition
        contributes **no** capability of its own, and this method has no way to let it.
        """
        record = self.subject(composition_key, role=StructuralRole.COMPOSITION)
        selected = [self.nucleus(key) for key in record.composes]
        capabilities: list[CapabilityRecord] = []
        for nucleus in selected:
            capabilities.extend(self.capabilities(owner=nucleus.key))
        return {
            "composition": record.key,
            "composition_id": record.universal_id,
            "role": record.role.value,
            "owns_capabilities": False,
            "selected_nuclei": [
                {"key": n.key, "universal_id": n.universal_id, "concept": n.concept}
                for n in selected
            ],
            "capabilities": [
                {"key": c.key, "universal_id": c.universal_id, "owner": c.owner_key}
                for c in sorted(capabilities, key=lambda c: c.key)
            ],
            "capability_count": len(capabilities),
            "nucleus_count": len(selected),
        }

    # -- description -------------------------------------------------------- #

    def counts(self) -> dict[str, int]:
        return {
            "subjects": len(self._subjects),
            "nuclei": len(self.nuclei()),
            "layers": len(self.layers()),
            "compositions": len(self.compositions()),
            "capabilities": len(self._capabilities),
            "assignments": len(self._assignments),
        }

    def to_document(self) -> dict[str, Any]:
        """The whole registry as a deterministic, machine-readable document."""
        return {
            "schema": "ucos-nucleus-registry",
            "version": "1.0.0",
            "law_id": LAW_ID,
            "clauses": [c.clause_id for c in OWNERSHIP_CLAUSES],
            "counts": self.counts(),
            "context": dict(self._context),
            "subjects": [self._subjects[k].to_dict() for k in sorted(self._subjects)],
            "capabilities": [self._capabilities[k].to_dict() for k in sorted(self._capabilities)],
            "assignments": [a.to_dict() for a in self._assignments],
            "closed_set": False,
            "upper_limit": None,
        }

    def digest(self) -> str:
        """The content digest of the registry, via the one canonical primitive."""
        return content_hash(self.to_document())


def build_seed_registry(*, vocabularies: VocabularyRegistry | None = None) -> NucleusRegistry:
    """Build the registry seeded from the declared catalogue.

    Every seed subject and capability passes through the same admission path an
    externally declared one does, so the seed population is proof that the law is
    satisfiable — not an exemption from it.
    """
    registry = NucleusRegistry(vocabularies=vocabularies)
    registry.register_subjects(seed_subjects())
    registry.register_capabilities(seed_capabilities())
    return registry


def declarations_from_mapping(payload: Mapping[str, Any]) -> tuple[SubjectDeclaration, ...]:
    """Build subject declarations from a plain mapping (DATA-driven registration).

    The shape is ``{"subjects": [{"key": ..., "title": ..., ...}, ...]}``. This is the
    path by which an unlimited number of future nuclei, layers and compositions enter
    with no code change at all.
    """
    raw = payload.get("subjects")
    if not isinstance(raw, list):
        raise StructuralValidationError("payload must carry a 'subjects' list", at="subjects")
    out: list[SubjectDeclaration] = []
    for index, entry in enumerate(raw):
        if not isinstance(entry, Mapping):
            raise StructuralValidationError(
                "each subject must be a mapping", at=f"subjects[{index}]"
            )
        out.append(
            SubjectDeclaration(
                key=entry.get("key", ""),
                title=entry.get("title", ""),
                role=entry.get("role"),
                namespace=entry.get("namespace", "ucos.structure"),
                concept=entry.get("concept", "") or "",
                composes=tuple(entry.get("composes", ()) or ()),
                organizes=tuple(entry.get("organizes", ()) or ()),
                parent=entry.get("parent"),
                description=entry.get("description", "") or "",
                profile=entry.get("profile", {}) or {},
            )
        )
    return tuple(out)


__all__ = [
    "STRUCTURAL_ROLE_VOCABULARY",
    "SEED_AUTHORITY",
    "NucleusRegistry",
    "build_seed_registry",
    "declarations_from_mapping",
]

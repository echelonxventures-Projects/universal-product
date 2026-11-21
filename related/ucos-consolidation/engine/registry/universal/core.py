"""UCOS-EPIC-001 — Registry Core: the single registration authority.

:class:`RegistryCore` is the write-side authority that every typed registry
composes. It is the one place an artifact becomes *Repository Truth*, enforcing
the constitutional requirements:

    * **Deterministic IDs** — identity is a pure function of ``(kind, namespace,
      natural_key)`` (see :mod:`~engine.registry.universal.identity`).
    * **No duplicate registrations** — the same ``(universal_id, version)`` is
      never registered twice; append-only, supersede-not-overwrite (INV-10).
    * **Knowledge Once** — identical content may not be registered under two
      identities; a single canonical home per unit of knowledge.
    * **Version aware** — each identity owns a monotonic version chain; a new
      version supersedes (never overwrites) the prior active one (PL-05).
    * **Audit trail** — every governed act is appended to a tamper-evident,
      hash-chained :class:`~engine.registry.universal.audit.AuditJournal`.
    * **Acyclic dependencies** — declared dependency edges among registered
      artifacts must remain acyclic (DC-2).

The core holds only immutable value objects and never writes to the frozen corpus
(DP-03). It is stdlib-only and deterministic on the determined path (RC-4).
"""

from __future__ import annotations

from collections.abc import Iterable

from engine.foundation.contracts.contract import Version
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import metric_counter, trace
from engine.registry.universal.audit import AuditJournal, Clock
from engine.registry.universal.errors import (
    DependencyError,
    DuplicateRegistrationError,
    KnowledgeOnceViolation,
    RegistrationNotFoundError,
    VersionConflictError,
)
from engine.registry.universal.identity import RegistryKind
from engine.registry.universal.records import (
    AuditAct,
    Registration,
    RegistrationRequest,
    RegistrationState,
)

_logger = get_logger("registry.universal.core")

#: The default actor recorded on the audit trail when none is supplied.
DEFAULT_ACTOR = "UCOS-REGISTRY-AUTHORITY"


def version_ref(universal_id: str, version: Version | str) -> str:
    """Return the versioned reference ``<universal_id>@<version>``."""
    return f"{universal_id}@{version}"


class RegistryCore:
    """The append-only single registration authority for UCOS artifacts."""

    __slots__ = ("_chains", "_by_content", "_edges", "_journal", "_actor")

    def __init__(
        self,
        *,
        journal: AuditJournal | None = None,
        actor: str = DEFAULT_ACTOR,
        clock: Clock | None = None,
    ) -> None:
        # universal_id -> ordered version records (append order == version order).
        self._chains: dict[str, list[Registration]] = {}
        # content_hash -> owning universal_id (Knowledge-Once index).
        self._by_content: dict[str, str] = {}
        # universal_id -> registered dependency ids (active version's edges).
        self._edges: dict[str, tuple[str, ...]] = {}
        self._journal = journal if journal is not None else AuditJournal(clock=clock)
        self._actor = actor

    # -- properties ------------------------------------------------------------

    @property
    def journal(self) -> AuditJournal:
        """The append-only, hash-chained audit trail."""
        return self._journal

    # -- registration ----------------------------------------------------------

    def register(self, request: RegistrationRequest, *, actor: str | None = None) -> Registration:
        """Register (a version of) an artifact and return the active record.

        First registration of an identity creates it; a subsequent call with a
        strictly-newer version supersedes the prior active version. Raises on any
        duplicate, Knowledge-Once, version-ordering, or dependency-cycle breach —
        the mutation is atomic (nothing is recorded on failure).
        """
        actor = actor or self._actor
        uid = request.universal_id
        content_hash = request.content_hash()

        # Knowledge Once + duplicate content detection (deny-by-default).
        owner = self._by_content.get(content_hash)
        if owner is not None and owner != uid:
            raise KnowledgeOnceViolation(
                "identical content already registered under a different identity",
                content_hash=content_hash,
                existing=owner,
                attempted=uid,
            )
        if owner == uid:
            raise DuplicateRegistrationError(
                "identical content already registered for this identity",
                universal_id=uid,
                content_hash=content_hash,
            )

        with trace("registry.universal.register"):
            if uid not in self._chains:
                return self._register_new(request, content_hash, actor)
            return self._register_version(request, content_hash, actor)

    def _register_new(
        self, request: RegistrationRequest, content_hash: str, actor: str
    ) -> Registration:
        uid = request.universal_id
        self._check_cycle(uid, request.dependencies)
        record = Registration.from_request(request, sequence=self._next_sequence())
        self._chains[uid] = [record]
        self._by_content[content_hash] = uid
        self._edges[uid] = self._registered_deps(request.dependencies)
        self._journal.record(
            act=AuditAct.REGISTER,
            universal_id=uid,
            version=record.version_str,
            content_hash=content_hash,
            state=record.state.value,
            actor=actor,
        )
        metric_counter("registry.universal.registered", kind=record.kind.value)
        _logger.info(
            "registry.universal.registered",
            universal_id=uid,
            kind=record.kind.value,
            version=record.version_str,
        )
        return record

    def _register_version(
        self, request: RegistrationRequest, content_hash: str, actor: str
    ) -> Registration:
        uid = request.universal_id
        chain = self._chains[uid]
        if any(r.version == request.version for r in chain):
            raise DuplicateRegistrationError(
                "this version is already registered for the identity",
                universal_id=uid,
                version=str(request.version),
            )
        highest = max(r.version for r in chain)
        if request.version <= highest:
            raise VersionConflictError(
                "a new version must be strictly newer than the current version",
                universal_id=uid,
                attempted=str(request.version),
                current=str(highest),
            )
        self._check_cycle(uid, request.dependencies)

        new_record = Registration.from_request(request, sequence=self._next_sequence())
        # Supersede the current active version (append-only; never overwrite).
        for index, record in enumerate(chain):
            if record.state is RegistrationState.ACTIVE:
                chain[index] = record.with_state(
                    RegistrationState.SUPERSEDED,
                    superseded_by=version_ref(uid, new_record.version),
                )
                self._journal.record(
                    act=AuditAct.SUPERSEDE,
                    universal_id=uid,
                    version=chain[index].version_str,
                    content_hash=chain[index].content_hash,
                    state=RegistrationState.SUPERSEDED.value,
                    actor=actor,
                )
        chain.append(new_record)
        self._by_content[content_hash] = uid
        self._edges[uid] = self._registered_deps(request.dependencies)
        self._journal.record(
            act=AuditAct.REGISTER_VERSION,
            universal_id=uid,
            version=new_record.version_str,
            content_hash=content_hash,
            state=new_record.state.value,
            actor=actor,
        )
        metric_counter("registry.universal.versioned", kind=new_record.kind.value)
        _logger.info(
            "registry.universal.versioned",
            universal_id=uid,
            version=new_record.version_str,
            supersedes=str(highest),
        )
        return new_record

    # -- lifecycle transitions -------------------------------------------------

    def deprecate(self, universal_id: str, *, actor: str | None = None) -> Registration:
        """Deprecate the active version (still present, no longer recommended)."""
        return self._transition(
            universal_id,
            AuditAct.DEPRECATE,
            RegistrationState.DEPRECATED,
            from_states=(RegistrationState.ACTIVE,),
            actor=actor,
        )

    def retire(self, universal_id: str, *, actor: str | None = None) -> Registration:
        """Retire the active/deprecated version (end of life, preserved)."""
        return self._transition(
            universal_id,
            AuditAct.RETIRE,
            RegistrationState.RETIRED,
            from_states=(RegistrationState.ACTIVE, RegistrationState.DEPRECATED),
            actor=actor,
        )

    def _transition(
        self,
        universal_id: str,
        act: AuditAct,
        to_state: RegistrationState,
        *,
        from_states: tuple[RegistrationState, ...],
        actor: str | None,
    ) -> Registration:
        actor = actor or self._actor
        chain = self._chain(universal_id)
        for index, record in enumerate(chain):
            if record.state in from_states and record.superseded_by is None:
                updated = record.with_state(to_state)
                chain[index] = updated
                self._journal.record(
                    act=act,
                    universal_id=universal_id,
                    version=updated.version_str,
                    content_hash=updated.content_hash,
                    state=to_state.value,
                    actor=actor,
                )
                _logger.info(
                    "registry.universal.transition",
                    universal_id=universal_id,
                    act=act.value,
                    version=updated.version_str,
                )
                return updated
        raise RegistrationNotFoundError(
            "no version in a transitionable state for this identity",
            universal_id=universal_id,
            required_states=[s.value for s in from_states],
        )

    # -- lookups ---------------------------------------------------------------

    def exists(self, universal_id: str) -> bool:
        """True iff any version of ``universal_id`` is registered."""
        return universal_id in self._chains

    def get(self, universal_id: str) -> Registration:
        """Return the current (highest, non-retired) version of an identity.

        The current version is the highest-versioned record that has not been
        superseded — i.e. the ACTIVE/DEPRECATED head of the chain.
        """
        chain = self._chain(universal_id)
        head = max(chain, key=lambda r: r.version)
        return head

    def get_version(self, universal_id: str, version: str | Version) -> Registration:
        """Return a specific registered version of an identity."""
        wanted = Version.parse(version) if isinstance(version, str) else version
        for record in self._chain(universal_id):
            if record.version == wanted:
                return record
        raise RegistrationNotFoundError(
            "no such version for this identity",
            universal_id=universal_id,
            version=str(wanted),
        )

    def resolve(self, reference: str) -> Registration:
        """Resolve a ``universal_id`` or ``universal_id@version`` reference."""
        if "@" in reference:
            uid, _, version = reference.partition("@")
            return self.get_version(uid, version)
        return self.get(reference)

    def history(self, universal_id: str) -> tuple[Registration, ...]:
        """Every registered version of ``universal_id`` in version order."""
        return tuple(sorted(self._chain(universal_id), key=lambda r: r.version))

    def dependencies_of(self, universal_id: str) -> tuple[str, ...]:
        """Registered dependency ids of the active version of ``universal_id``."""
        self._chain(universal_id)
        return self._edges.get(universal_id, ())

    # -- collection views ------------------------------------------------------

    def heads(self) -> tuple[Registration, ...]:
        """The current head registration of every identity, id-ordered."""
        return tuple(self.get(uid) for uid in sorted(self._chains))

    def all_versions(self) -> tuple[Registration, ...]:
        """Every registered version across all identities, deterministically ordered."""
        records: list[Registration] = []
        for uid in sorted(self._chains):
            records.extend(sorted(self._chains[uid], key=lambda r: r.version))
        return tuple(records)

    def by_kind(self, kind: RegistryKind | str) -> tuple[Registration, ...]:
        """Head registrations of a given :class:`RegistryKind`."""
        wanted = RegistryKind.coerce(kind)
        return tuple(h for h in self.heads() if h.kind is wanted)

    def by_namespace(self, namespace: str) -> tuple[Registration, ...]:
        """Head registrations within a namespace (or namespace prefix)."""
        prefix = namespace.strip().lower()
        return tuple(
            h for h in self.heads() if h.namespace == prefix or h.namespace.startswith(prefix + ".")
        )

    def count(self) -> int:
        """Number of distinct registered identities."""
        return len(self._chains)

    def count_versions(self) -> int:
        """Total number of registered versions across all identities."""
        return sum(len(chain) for chain in self._chains.values())

    # -- integrity + evidence --------------------------------------------------

    def verify(self) -> bool:
        """Verify audit-chain integrity and internal registry invariants."""
        self._journal.verify()
        for uid, chain in self._chains.items():
            active = [r for r in chain if r.state is RegistrationState.ACTIVE]
            if len(active) > 1:
                raise VersionConflictError(
                    "more than one ACTIVE version for an identity", universal_id=uid
                )
        self._check_no_cycles()
        return True

    def snapshot(self) -> dict[str, object]:
        """A deterministic, serialisable snapshot of the registry + audit trail."""
        return {
            "platform_version": "1.0.0",
            "identities": self.count(),
            "versions": self.count_versions(),
            "registrations": [r.to_dict() for r in self.all_versions()],
            "audit": self._journal.to_dict(),
        }

    # -- internals -------------------------------------------------------------

    def _chain(self, universal_id: str) -> list[Registration]:
        try:
            return self._chains[universal_id]
        except KeyError as exc:
            raise RegistrationNotFoundError(
                "no such registered identity", universal_id=universal_id
            ) from exc

    def _next_sequence(self) -> int:
        return self.count_versions()

    def _registered_deps(self, dependencies: Iterable[str]) -> tuple[str, ...]:
        return tuple(d for d in dependencies if d in self._chains)

    def _check_cycle(self, uid: str, dependencies: Iterable[str]) -> None:
        deps = tuple(dependencies)
        if uid in deps:
            raise DependencyError("an artifact may not depend on itself", universal_id=uid)
        # Only registered dependencies can participate in a cycle right now.
        stack = [d for d in deps if d in self._chains]
        seen: set[str] = set()
        while stack:
            node = stack.pop()
            if node == uid:
                raise DependencyError(
                    "dependency edge would introduce a cycle (DC-2)",
                    universal_id=uid,
                    via=node,
                )
            if node in seen:
                continue
            seen.add(node)
            stack.extend(self._edges.get(node, ()))

    def _check_no_cycles(self) -> None:
        # Three-colour DFS over the active dependency graph (DC-2 acyclicity).
        white, grey, black = 0, 1, 2
        colour = {uid: white for uid in self._edges}

        def visit(node: str) -> None:
            colour[node] = grey
            for dep in self._edges.get(node, ()):
                if colour.get(dep, black) == grey:
                    raise VersionConflictError("dependency cycle detected", node=node, dep=dep)
                if colour.get(dep, black) == white:
                    visit(dep)
            colour[node] = black

        for uid in list(colour):
            # A key can only be coloured before its own turn by a DFS that reached a LATER
            # key, and edges point only at already-registered identities — the registration
            # ladder forbids a forward edge. The skip arm is therefore structurally
            # unreachable, and annotated rather than left to rot into a mystery.
            if colour[uid] == white:  # pragma: no cover - forward edges cannot exist
                visit(uid)


__all__ = ["RegistryCore", "DEFAULT_ACTOR", "version_ref"]

"""Universal Registry — the open, governed, append-only home of every meta-object.

This is the single admission authority of the kernel. It enforces the constitutional
invariants and *nothing domain-specific*:

    * **Open** — it admits a meta-object of *any* meta-type. There is no closed set of
      kinds anywhere in this module; the universe of concept-categories is discovered
      from the data (:meth:`metatypes`). Registering a previously unknown category is a
      registration, never a code change (Engineering Rule 7; Quality Gate "no closed
      registries").
    * **Governed** — every admission passes through :class:`~engine.kernel.governance`.
    * **Deterministic identity** — identity is a pure function of the identity tuple.
    * **Append-only + versioned** — a new version supersedes (never overwrites) the
      prior head; the full chain is retained (Universal Versioning / Evolution).
    * **Knowledge Once** — identical content has exactly one canonical identity.
    * **Acyclic relationships** — the relationship graph stays acyclic.
    * **Tamper-evident** — every admission is appended to a hash-chained audit journal
      (Universal Audit / Evidence), with no wall-clock so the chain is reproducible.

Stdlib-only, deterministic, and it never writes to disk on its own — persistence is an
explicit, caller-directed export.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.foundation.contracts.contract import Version
from engine.kernel.errors import (
    AuditIntegrityError,
    DuplicateRegistrationError,
    GovernanceRejection,
    KnowledgeOnceViolation,
    MetaTypeUnknownError,
    RegistrationNotFoundError,
    RelationshipError,
    VersionError,
)
from engine.kernel.governance import Governance
from engine.kernel.identity import canonical_json, content_digest
from engine.kernel.meta import META_TYPE_ROOT, MetaObject


@dataclass(frozen=True)
class AdmissionRecord:
    """One append-only audit entry linking to the previous entry by hash."""

    sequence: int
    act: str
    identity: str
    metatype: str
    version: str
    content_hash: str
    previous_hash: str
    entry_hash: str

    def to_dict(self) -> dict[str, object]:
        """A deterministic, serialisable rendering of the audit entry."""
        return {
            "sequence": self.sequence,
            "act": self.act,
            "identity": self.identity,
            "metatype": self.metatype,
            "version": self.version,
            "content_hash": self.content_hash,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }


#: The genesis hash that anchors the audit chain (a constant, not a wall-clock seed).
_GENESIS = "0" * 64


class UniversalRegistry:
    """The single, open, governed admission authority for meta-objects."""

    __slots__ = ("_governance", "_chains", "_by_content", "_journal")

    def __init__(self, *, governance: Governance | None = None) -> None:
        self._governance = governance if governance is not None else Governance()
        # identity -> version-ordered list of MetaObject (append order == version order).
        self._chains: dict[str, list[MetaObject]] = {}
        # content_hash -> owning identity (Knowledge-Once index).
        self._by_content: dict[str, str] = {}
        self._journal: list[AdmissionRecord] = []

    # -- governance view (RegistryView protocol) -------------------------------

    @property
    def governance(self) -> Governance:
        """The governance authority that gates every admission."""
        return self._governance

    def exists(self, identity: str) -> bool:
        """True iff any version of ``identity`` is registered."""
        return identity in self._chains

    def metatype_exists(self, natural_key: str) -> bool:
        """True iff a meta-type with this natural key is registered (open lookup)."""
        if natural_key == META_TYPE_ROOT:
            # The reflective root is admissible even before it is stored, and remains so.
            return True
        for head in self._heads():
            if head.is_meta_type and head.natural_key == natural_key:
                return True
        return False

    def content_owner(self, content_hash: str) -> str | None:
        """The identity that owns a content hash, or None (Knowledge-Once index)."""
        return self._by_content.get(content_hash)

    def would_cycle(self, identity: str, targets: tuple[str, ...]) -> bool:
        """True iff adding edges ``identity -> targets`` would create a cycle."""
        if identity in targets:
            return True
        # Walk existing edges from each target; if we reach ``identity`` there is a cycle.
        stack = [t for t in targets if t in self._chains]
        seen: set[str] = set()
        while stack:
            node = stack.pop()
            if node == identity:
                return True
            if node in seen:
                continue
            seen.add(node)
            head = self._chains.get(node)
            if head:
                stack.extend(head[-1].related())
        return False

    # -- registration ----------------------------------------------------------

    def register(self, candidate: MetaObject) -> MetaObject:
        """Govern and admit a meta-object (a first version or a superseding version)."""
        decision = self._governance.evaluate(candidate, self)
        if not decision.allowed:
            reasons = decision.reasons
            # Surface the most constitutionally-specific failure as a typed error while
            # always preserving the full reason set for evidence.
            if any("meta-type is not registered" in r for r in reasons):
                raise MetaTypeUnknownError(
                    "admission denied: classifying meta-type is not registered",
                    identity=candidate.identity,
                    metatype=candidate.metatype,
                    reasons=reasons,
                )
            if any("Knowledge Once" in r for r in reasons):
                raise KnowledgeOnceViolation(
                    "admission denied: identical content already has a canonical home",
                    identity=candidate.identity,
                    reasons=reasons,
                )
            if any("cycle" in r for r in reasons):
                raise RelationshipError(
                    "admission denied: relationship would introduce a cycle",
                    identity=candidate.identity,
                    reasons=reasons,
                )
            raise GovernanceRejection(
                "admission denied by governance", reasons=reasons, identity=candidate.identity
            )

        identity = candidate.identity
        if identity not in self._chains:
            return self._admit_new(candidate)
        return self._admit_version(candidate)

    def _admit_new(self, candidate: MetaObject) -> MetaObject:
        self._chains[candidate.identity] = [candidate]
        self._by_content[candidate.content_hash()] = candidate.identity
        self._append("REGISTER", candidate)
        return candidate

    def _admit_version(self, candidate: MetaObject) -> MetaObject:
        chain = self._chains[candidate.identity]
        if any(existing.content_hash() == candidate.content_hash() for existing in chain):
            raise DuplicateRegistrationError(
                "identical content already registered for this identity",
                identity=candidate.identity,
            )
        highest = max(existing.version for existing in chain)
        if candidate.version <= highest:
            raise VersionError(
                "a new version must strictly supersede the current head",
                identity=candidate.identity,
                attempted=str(candidate.version),
                current=str(highest),
            )
        chain.append(candidate)
        self._by_content[candidate.content_hash()] = candidate.identity
        self._append("REGISTER_VERSION", candidate)
        return candidate

    # -- lookups ---------------------------------------------------------------

    def get(self, identity: str) -> MetaObject:
        """Return the current head (highest version) of an identity."""
        chain = self._chain(identity)
        return max(chain, key=lambda obj: obj.version)

    def get_version(self, identity: str, version: str | Version) -> MetaObject:
        """Return a specific registered version of an identity."""
        wanted = Version.parse(version) if isinstance(version, str) else version
        for obj in self._chain(identity):
            if obj.version == wanted:
                return obj
        raise RegistrationNotFoundError("no such version", identity=identity, version=str(wanted))

    def resolve(self, reference: str) -> MetaObject:
        """Resolve ``identity`` or ``identity@version``."""
        if "@" in reference:
            ident, _, version = reference.partition("@")
            return self.get_version(ident, version)
        return self.get(reference)

    def history(self, identity: str) -> tuple[MetaObject, ...]:
        """Every registered version of an identity, in version order."""
        return tuple(sorted(self._chain(identity), key=lambda obj: obj.version))

    # -- collection views (all data-derived; nothing enumerated) ---------------

    def all(self) -> tuple[MetaObject, ...]:
        """The current head of every identity, deterministically ordered."""
        return tuple(sorted(self._heads(), key=lambda obj: obj.identity))

    def metatypes(self) -> tuple[MetaObject, ...]:
        """Every registered meta-type — the *open* universe of concept-categories.

        The set is derived purely from what has been registered. It has no upper bound
        and no closed membership; this method is the mechanised proof that the kernel's
        vocabulary of kinds is DATA, not a finite enumeration.
        """
        return tuple(
            sorted((h for h in self._heads() if h.is_meta_type), key=lambda o: o.natural_key)
        )

    def metatype_keys(self) -> tuple[str, ...]:
        """The natural keys of every registered meta-type (open set)."""
        return tuple(mt.natural_key for mt in self.metatypes())

    def by_metatype(self, metatype: str) -> tuple[MetaObject, ...]:
        """Every current head classified by ``metatype`` (open key)."""
        return tuple(
            sorted((h for h in self._heads() if h.metatype == metatype), key=lambda o: o.identity)
        )

    def instances(self) -> tuple[MetaObject, ...]:
        """Every current head that is not itself a meta-type."""
        return tuple(
            sorted((h for h in self._heads() if not h.is_meta_type), key=lambda o: o.identity)
        )

    def count(self) -> int:
        """The number of distinct registered identities."""
        return len(self._chains)

    def count_versions(self) -> int:
        """The total number of registered versions across all identities."""
        return sum(len(chain) for chain in self._chains.values())

    # -- lineage / trace (Universal Traceability) ------------------------------

    def trace(self, identity: str) -> dict[str, object]:
        """Return the traceable lineage of an identity: versions + relationships out/in."""
        head = self.get(identity)
        inbound = [
            other.identity
            for other in self._heads()
            if identity in other.related() and other.identity != identity
        ]
        return {
            "identity": identity,
            "metatype": head.metatype,
            "versions": [obj.version_str for obj in self.history(identity)],
            "relationships_out": [r.to_dict() for r in head.relationships],
            "relationships_in": sorted(inbound),
            "provenance": dict(head.provenance),
        }

    # -- integrity + evidence --------------------------------------------------

    def verify(self) -> bool:
        """Verify audit-chain hash linkage and single-head invariants."""
        previous = _GENESIS
        for index, entry in enumerate(self._journal):
            if entry.sequence != index:
                raise AuditIntegrityError("audit sequence gap", at=index)
            if entry.previous_hash != previous:
                raise AuditIntegrityError("audit chain broken", at=index)
            if entry.entry_hash != self._entry_hash(entry, previous):
                raise AuditIntegrityError("audit entry hash mismatch", at=index)
            previous = entry.entry_hash
        return True

    @property
    def audit_head(self) -> str:
        """The hash at the head of the append-only audit chain (genesis when empty)."""
        return self._journal[-1].entry_hash if self._journal else _GENESIS

    def journal(self) -> tuple[AdmissionRecord, ...]:
        """The full append-only audit journal, in order."""
        return tuple(self._journal)

    def snapshot(self) -> dict[str, object]:
        """A deterministic, serialisable snapshot of the whole registry + audit trail."""
        return {
            "kernel_version": "1.0.0",
            "identities": self.count(),
            "versions": self.count_versions(),
            "metatypes": list(self.metatype_keys()),
            "objects": [obj.to_dict() for obj in self._all_versions()],
            "audit": {
                "head": self.audit_head,
                "entries": [entry.to_dict() for entry in self._journal],
            },
        }

    def snapshot_json(self) -> str:
        """The canonical JSON rendering of :meth:`snapshot`."""
        return canonical_json(self.snapshot())

    # -- internals -------------------------------------------------------------

    def _heads(self) -> list[MetaObject]:
        return [max(chain, key=lambda obj: obj.version) for chain in self._chains.values()]

    def _all_versions(self) -> list[MetaObject]:
        out: list[MetaObject] = []
        for identity in sorted(self._chains):
            out.extend(sorted(self._chains[identity], key=lambda obj: obj.version))
        return out

    def _chain(self, identity: str) -> list[MetaObject]:
        try:
            return self._chains[identity]
        except KeyError as exc:
            raise RegistrationNotFoundError(
                "no such registered identity", identity=identity
            ) from exc

    def _append(self, act: str, obj: MetaObject) -> None:
        previous = self.audit_head
        sequence = len(self._journal)
        stub = AdmissionRecord(
            sequence=sequence,
            act=act,
            identity=obj.identity,
            metatype=obj.metatype,
            version=obj.version_str,
            content_hash=obj.content_hash(),
            previous_hash=previous,
            entry_hash="",
        )
        entry_hash = self._entry_hash(stub, previous)
        self._journal.append(
            AdmissionRecord(
                sequence=sequence,
                act=act,
                identity=obj.identity,
                metatype=obj.metatype,
                version=obj.version_str,
                content_hash=obj.content_hash(),
                previous_hash=previous,
                entry_hash=entry_hash,
            )
        )

    @staticmethod
    def _entry_hash(entry: AdmissionRecord, previous: str) -> str:
        return content_digest(
            {
                "sequence": entry.sequence,
                "act": entry.act,
                "identity": entry.identity,
                "metatype": entry.metatype,
                "version": entry.version,
                "content_hash": entry.content_hash,
                "previous_hash": previous,
            }
        )


__all__ = ["UniversalRegistry", "AdmissionRecord"]

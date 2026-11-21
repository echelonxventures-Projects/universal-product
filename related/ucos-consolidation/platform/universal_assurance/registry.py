"""UCOS-EPIC-014 — Certification Registry (Terminal T7).

The eighth owned capability. A certification determination that is not **registered** is
not discoverable, and an unregisterable determination is not certifiable. The
:class:`CertificationRegistry` is the append-only, hash-chained record of every
certification an assurance run produced, binding each certificate to the exact policy,
plans, and evidence bundle that authorized it.

The chain discipline is the same one the reused certification ledger and the constitutional
programme engines use: each entry hashes its own canonical core together with the previous
entry's hash, so the head hash is a commitment to the whole history and any retroactive
edit is detectable by :meth:`CertificationRegistry.verify`. Nothing can be updated or
removed — only appended.

An entry is a **full provenance chain in one record**: certification id and certificate
digest, the subject and its version, the validation and certification plan digests, the
evidence bundle id and digest, and the policy digest. Given any entry, the run that
produced it can be located and replayed.

Fail-closed: appending an entry whose certification id is already registered, or appending
onto a broken chain, raises
:class:`~platform.universal_assurance.errors.AssuranceRegistryError` — a registry that
cannot prove its own integrity never reports itself intact.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_assurance.errors import AssuranceRegistryError
from typing import Any

#: The registry snapshot format identifier.
REGISTRY_FORMAT = "ucos-assurance-certification-registry/1.0.0"

#: The genesis hash the first entry chains onto.
GENESIS_HASH = "0" * 64

#: The registered status values (derived from the certification verdict, never hand-set).
STATUS_CERTIFIED = "certified"
STATUS_NOT_CERTIFIED = "not-certified"


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    """One immutable, hash-chained certification registration."""

    sequence: int
    registry_id: str
    certification_id: str
    subject_id: str
    version: str
    status: str
    certified: bool
    certificate_sha256: str
    certificate_intact: bool
    validation_plan_sha256: str
    certification_plan_sha256: str
    validation_execution_sha256: str
    certification_execution_sha256: str
    evidence_id: str
    evidence_bundle_sha256: str
    policy_id: str
    policy_digest: str
    previous_hash: str
    entry_hash: str

    @staticmethod
    def _core(
        *,
        sequence: int,
        registry_id: str,
        certification_id: str,
        subject_id: str,
        version: str,
        status: str,
        certified: bool,
        certificate_sha256: str,
        certificate_intact: bool,
        validation_plan_sha256: str,
        certification_plan_sha256: str,
        validation_execution_sha256: str,
        certification_execution_sha256: str,
        evidence_id: str,
        evidence_bundle_sha256: str,
        policy_id: str,
        policy_digest: str,
        previous_hash: str,
    ) -> dict[str, Any]:
        return {
            "sequence": sequence,
            "registry_id": registry_id,
            "certification_id": certification_id,
            "subject_id": subject_id,
            "version": version,
            "status": status,
            "certified": certified,
            "certificate_sha256": certificate_sha256,
            "certificate_intact": certificate_intact,
            "validation_plan_sha256": validation_plan_sha256,
            "certification_plan_sha256": certification_plan_sha256,
            "validation_execution_sha256": validation_execution_sha256,
            "certification_execution_sha256": certification_execution_sha256,
            "evidence_id": evidence_id,
            "evidence_bundle_sha256": evidence_bundle_sha256,
            "policy_id": policy_id,
            "policy_digest": policy_digest,
            "previous_hash": previous_hash,
        }

    @classmethod
    def create(cls, **fields: Any) -> RegistryEntry:
        """Build an entry and chain it onto ``previous_hash``."""
        core = cls._core(**fields)
        return cls(**fields, entry_hash=content_hash(core))

    def recompute_hash(self) -> str:
        """Recompute this entry's hash from its current field values."""
        return content_hash(
            self._core(
                sequence=self.sequence,
                registry_id=self.registry_id,
                certification_id=self.certification_id,
                subject_id=self.subject_id,
                version=self.version,
                status=self.status,
                certified=self.certified,
                certificate_sha256=self.certificate_sha256,
                certificate_intact=self.certificate_intact,
                validation_plan_sha256=self.validation_plan_sha256,
                certification_plan_sha256=self.certification_plan_sha256,
                validation_execution_sha256=self.validation_execution_sha256,
                certification_execution_sha256=self.certification_execution_sha256,
                evidence_id=self.evidence_id,
                evidence_bundle_sha256=self.evidence_bundle_sha256,
                policy_id=self.policy_id,
                policy_digest=self.policy_digest,
                previous_hash=self.previous_hash,
            )
        )

    @property
    def intact(self) -> bool:
        return self.recompute_hash() == self.entry_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._core(
                sequence=self.sequence,
                registry_id=self.registry_id,
                certification_id=self.certification_id,
                subject_id=self.subject_id,
                version=self.version,
                status=self.status,
                certified=self.certified,
                certificate_sha256=self.certificate_sha256,
                certificate_intact=self.certificate_intact,
                validation_plan_sha256=self.validation_plan_sha256,
                certification_plan_sha256=self.certification_plan_sha256,
                validation_execution_sha256=self.validation_execution_sha256,
                certification_execution_sha256=self.certification_execution_sha256,
                evidence_id=self.evidence_id,
                evidence_bundle_sha256=self.evidence_bundle_sha256,
                policy_id=self.policy_id,
                policy_digest=self.policy_digest,
                previous_hash=self.previous_hash,
            ),
            "entry_hash": self.entry_hash,
        }


class CertificationRegistry:
    """**Certification Registry** — the append-only, hash-chained certification record."""

    __slots__ = ("_registry_id", "_entries")

    def __init__(self, registry_id: str, entries: Iterable[RegistryEntry] = ()) -> None:
        if not isinstance(registry_id, str) or not registry_id:
            raise AssuranceRegistryError("a certification registry requires a non-empty id")
        self._registry_id = registry_id
        self._entries: list[RegistryEntry] = list(entries)

    @property
    def registry_id(self) -> str:
        return self._registry_id

    @property
    def entries(self) -> tuple[RegistryEntry, ...]:
        return tuple(self._entries)

    @property
    def head_hash(self) -> str:
        """The hash of the most recent entry (the genesis hash when empty)."""
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def __len__(self) -> int:
        return len(self._entries)

    def register(
        self,
        *,
        certification_id: str,
        subject_id: str,
        version: str,
        certified: bool,
        certificate_sha256: str,
        certificate_intact: bool,
        validation_plan_sha256: str,
        certification_plan_sha256: str,
        validation_execution_sha256: str,
        certification_execution_sha256: str,
        evidence_id: str,
        evidence_bundle_sha256: str,
        policy_id: str,
        policy_digest: str,
    ) -> RegistryEntry:
        """Append a certification registration onto the chain (fail-closed).

        Raises:
            AssuranceRegistryError: if the certification id is already registered, the id
                is empty, or the existing chain does not verify.
        """
        if not isinstance(certification_id, str) or not certification_id:
            raise AssuranceRegistryError(
                "a registration requires a non-empty certification id",
                registry=self._registry_id,
            )
        if self.get(certification_id) is not None:
            raise AssuranceRegistryError(
                "certification is already registered (the registry is append-only)",
                registry=self._registry_id,
                certification_id=certification_id,
            )
        self.require_intact()
        entry = RegistryEntry.create(
            sequence=len(self._entries) + 1,
            registry_id=self._registry_id,
            certification_id=certification_id,
            subject_id=subject_id,
            version=version,
            status=STATUS_CERTIFIED if certified else STATUS_NOT_CERTIFIED,
            certified=certified,
            certificate_sha256=certificate_sha256,
            certificate_intact=certificate_intact,
            validation_plan_sha256=validation_plan_sha256,
            certification_plan_sha256=certification_plan_sha256,
            validation_execution_sha256=validation_execution_sha256,
            certification_execution_sha256=certification_execution_sha256,
            evidence_id=evidence_id,
            evidence_bundle_sha256=evidence_bundle_sha256,
            policy_id=policy_id,
            policy_digest=policy_digest,
            previous_hash=self.head_hash,
        )
        self._entries.append(entry)
        return entry

    # -- queries ---------------------------------------------------------------

    def get(self, certification_id: str) -> RegistryEntry | None:
        for entry in self._entries:
            if entry.certification_id == certification_id:
                return entry
        return None

    def by_subject(self, subject_id: str) -> tuple[RegistryEntry, ...]:
        return tuple(entry for entry in self._entries if entry.subject_id == subject_id)

    def by_policy(self, policy_digest: str) -> tuple[RegistryEntry, ...]:
        return tuple(entry for entry in self._entries if entry.policy_digest == policy_digest)

    def certification_ids(self) -> tuple[str, ...]:
        return tuple(entry.certification_id for entry in self._entries)

    def count_by_status(self) -> dict[str, int]:
        counts = {STATUS_CERTIFIED: 0, STATUS_NOT_CERTIFIED: 0}
        for entry in self._entries:
            counts[entry.status] = counts.get(entry.status, 0) + 1
        return counts

    def policy_drift(self, policy_digest: str) -> tuple[str, ...]:
        """Registered certifications authorized by a *different* policy text.

        Drift is not an error — it is the honest record of a policy that changed after a
        certification was issued — but certification intelligence must be able to see it.
        """
        return tuple(
            entry.certification_id
            for entry in self._entries
            if entry.policy_digest != policy_digest
        )

    # -- integrity -------------------------------------------------------------

    def verify(self) -> bool:
        """True iff every entry is intact and correctly chained to its predecessor."""
        previous = GENESIS_HASH
        for index, entry in enumerate(self._entries, start=1):
            if entry.sequence != index or entry.previous_hash != previous or not entry.intact:
                return False
            previous = entry.entry_hash
        return True

    def require_intact(self) -> None:
        """Raise :class:`AssuranceRegistryError` if the chain does not verify."""
        if not self.verify():
            raise AssuranceRegistryError(
                "certification registry chain integrity check failed",
                registry=self._registry_id,
                entries=len(self._entries),
            )

    # -- projections -----------------------------------------------------------

    def counts(self) -> dict[str, int]:
        by_status = self.count_by_status()
        return {
            "entries": len(self._entries),
            "certified": by_status.get(STATUS_CERTIFIED, 0),
            "not_certified": by_status.get(STATUS_NOT_CERTIFIED, 0),
        }

    def observations(self) -> dict[str, float]:
        """The numeric facts the policy's registry metrics are evaluated against."""
        counts = self.counts()
        return {
            "registry.entries": float(counts["entries"]),
            "registry.certified": float(counts["certified"]),
            "registry.not_certified": float(counts["not_certified"]),
            "registry.chain_intact": 1.0 if self.verify() else 0.0,
        }

    def fingerprint(self) -> str:
        """The deterministic content hash of the whole registry state."""
        return content_hash(self.snapshot())

    def snapshot(self) -> dict[str, Any]:
        """The deterministic, content-addressable snapshot written as evidence."""
        intact = self.verify()
        return {
            "registry_format": REGISTRY_FORMAT,
            "registry_id": self._registry_id,
            "head_hash": self.head_hash,
            "chain_intact": intact,
            "counts": self.counts(),
            "certification_ids": list(self.certification_ids()),
            "entries": [entry.to_dict() for entry in self._entries],
        }

    def to_dict(self) -> dict[str, Any]:
        return self.snapshot()


def entry_provenance(entry: RegistryEntry) -> Mapping[str, str]:
    """The digest chain that lets a registered certification be located and replayed."""
    return {
        "policy_digest": entry.policy_digest,
        "validation_plan_sha256": entry.validation_plan_sha256,
        "certification_plan_sha256": entry.certification_plan_sha256,
        "validation_execution_sha256": entry.validation_execution_sha256,
        "certification_execution_sha256": entry.certification_execution_sha256,
        "certificate_sha256": entry.certificate_sha256,
        "evidence_bundle_sha256": entry.evidence_bundle_sha256,
    }


__all__ = [
    "REGISTRY_FORMAT",
    "GENESIS_HASH",
    "STATUS_CERTIFIED",
    "STATUS_NOT_CERTIFIED",
    "RegistryEntry",
    "CertificationRegistry",
    "entry_provenance",
]

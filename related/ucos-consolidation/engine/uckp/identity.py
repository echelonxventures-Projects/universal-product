"""UCKP Layer Zero — Universal Identity (Article 5).

An identity that depends on where a thing is stored is not an identity; it is an
address. Article 5 therefore requires an identity that is globally unique,
immutable, canonical, persistent and independent of technology, storage,
repository and time.

The construction here satisfies all seven properties with no coordination and no
central allocator:

    * **Globally unique / canonical** — the URN ``urn:ucos:ucko:<namespace>:<local>``
      is the identity, and a namespace-qualified name collides only if two authors
      claim the same name in the same namespace, which the registry refuses.
    * **Immutable** — minting is a pure function. :meth:`UniversalIdentity.mint`
      derives both the URN and its UUID from the namespace and local name alone, so
      "minting again" cannot produce a different answer, and :meth:`verify` detects
      any post-hoc edit of either derived field.
    * **Persistent / storage- and repository-independent** — nothing in the identity
      references a path, a commit, a table, a host or a URL.
    * **Time-independent** — no clock is read. Two processes on different planets in
      different centuries mint the same identity for the same name, which is what
      makes cross-era replay possible at all.

The UUID is RFC 4122 version 5 (SHA-1 over a namespace UUID and the URN). It is a
*name-based* identifier, never a random one: a random identity would be
unreproducible, and an unreproducible identity cannot be replayed.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Any

from engine.uckp.errors import IdentityError

#: The URN scheme of every universal constitutional knowledge object.
UCKO_URN_PREFIX = "urn:ucos:ucko"

#: The root name from which the UUID namespace is derived. Declaring the *name*
#: rather than a magic UUID literal keeps the derivation auditable: anyone can
#: recompute the namespace from this string alone.
UCKP_NAMESPACE_NAME = "urn:ucos:uckp:root"

#: The name-based UUID namespace for all UCKO identities (deterministic).
UCKP_NAMESPACE_UUID = uuid.uuid5(uuid.NAMESPACE_URL, UCKP_NAMESPACE_NAME)

_NAMESPACE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,62}$")
_LOCAL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,190}$")


def urn_for(namespace: str, local_name: str) -> str:
    """Return the canonical URN for ``namespace``/``local_name`` (pure)."""
    return f"{UCKO_URN_PREFIX}:{namespace}:{local_name}"


def uuid_for(urn: str) -> str:
    """Return the deterministic name-based UUID of ``urn`` (pure)."""
    return str(uuid.uuid5(UCKP_NAMESPACE_UUID, urn))


@dataclass(frozen=True, slots=True)
class UniversalIdentity:
    """The immutable, technology-independent identity of a UCKO."""

    namespace: str
    local_name: str
    urn: str
    uuid: str

    @classmethod
    def mint(cls, namespace: str, local_name: str) -> UniversalIdentity:
        """Mint the identity for ``namespace``/``local_name``.

        Pure and total: the same arguments always yield the same identity, in every
        process, on every storage medium, at every time.
        """
        ns = str(namespace).strip()
        local = str(local_name).strip()
        if not _NAMESPACE_RE.match(ns):
            raise IdentityError(
                "identity namespace must be lowercase alphanumeric with . _ -",
                namespace=ns,
            )
        if not _LOCAL_RE.match(local):
            raise IdentityError(
                "identity local name must be alphanumeric with . _ -",
                local_name=local,
            )
        urn = urn_for(ns, local)
        return cls(namespace=ns, local_name=local, urn=urn, uuid=uuid_for(urn))

    @classmethod
    def parse(cls, urn: str) -> UniversalIdentity:
        """Reconstruct an identity from its URN (the inverse of minting)."""
        text = str(urn).strip()
        prefix = f"{UCKO_URN_PREFIX}:"
        if not text.startswith(prefix):
            raise IdentityError("not a UCKO urn", urn=text)
        remainder = text[len(prefix) :]
        namespace, separator, local = remainder.partition(":")
        if not separator:
            raise IdentityError("urn is missing a local name", urn=text)
        return cls.mint(namespace, local)

    @classmethod
    def from_dict(cls, data: Any) -> UniversalIdentity:
        if not isinstance(data, dict):
            raise IdentityError("identity record must be a mapping")
        identity = cls.mint(data.get("namespace", ""), data.get("local_name", ""))
        declared_urn = data.get("urn")
        declared_uuid = data.get("uuid")
        if declared_urn is not None and declared_urn != identity.urn:
            raise IdentityError(
                "declared urn does not match the minted identity",
                declared=str(declared_urn),
                minted=identity.urn,
            )
        if declared_uuid is not None and declared_uuid != identity.uuid:
            raise IdentityError(
                "declared uuid does not match the minted identity",
                urn=identity.urn,
            )
        return identity

    def verify(self) -> bool:
        """True iff both derived fields still match the minting function."""
        expected_urn = urn_for(self.namespace, self.local_name)
        return self.urn == expected_urn and self.uuid == uuid_for(expected_urn)

    def require_intact(self) -> None:
        """Fail closed if the identity was edited after minting."""
        if not self.verify():
            raise IdentityError("universal identity was mutated after minting", urn=self.urn)

    def require_unchanged(self, other: UniversalIdentity) -> None:
        """Fail closed if ``other`` is a different identity (Article 5: never changes)."""
        if other.urn != self.urn or other.uuid != self.uuid:
            raise IdentityError(
                "an identity may never change once minted",
                before=self.urn,
                after=other.urn,
            )

    def to_dict(self) -> dict[str, str]:
        return {
            "namespace": self.namespace,
            "local_name": self.local_name,
            "urn": self.urn,
            "uuid": self.uuid,
        }

    def __str__(self) -> str:
        return self.urn


__all__ = [
    "UCKO_URN_PREFIX",
    "UCKP_NAMESPACE_NAME",
    "UCKP_NAMESPACE_UUID",
    "UniversalIdentity",
    "urn_for",
    "uuid_for",
]

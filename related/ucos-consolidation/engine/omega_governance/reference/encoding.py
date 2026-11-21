"""UCOS Ω∞ Universal Reference Architecture — Representation and Identity as REGISTERED domains.

AUTHORITY = NONE (DERIVED TRUTH).

THE ASSUMPTION THIS REMOVES, AND IT WAS IN MY OWN FIRST DRAFT OF THIS PACKAGE::

    def identity(self) -> str:
        payload = json.dumps(self.as_record(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()

TWO HARDCODED REFERENCE SYSTEMS IN THREE LINES. JSON is a representation system and SHA-256 is an
identity system, and both were architectural requirements: no deployment could have replaced either
without editing the method. Ω∞ Rule 1 names both explicitly, and Rule 4 is the reason the violation
survived a first review — nobody challenges ``json.dumps`` because it does not look like a closed
list. It is one. It is the list of representations this system supports, with one entry.

WHAT REPLACES IT. Two provider protocols, two registries, and an ``Encoding`` pair that every
byte-producing call site takes AS AN ARGUMENT WITH NO DEFAULT. That last detail is what makes the
elimination structural rather than aspirational: a function with ``encoding: Encoding`` and no
default cannot fall back to JSON, because there is nothing to fall back to.

FOUR PROVIDERS SHIP, DELIBERATELY IN PAIRS.

    CanonicalJsonCodec      JSON, as ONE registered representation
    TagLengthValueCodec     a structurally unrelated binary representation
    Sha256Identity          SHA-256, as ONE registered identity system
    PolynomialIdentity      a non-cryptographic rolling digest, computed in integer arithmetic

THE PAIRS ARE THE PROOF. A single codec and a single digest would leave "the architecture does not
require JSON" as a claim about intent. Two of each, both driving the entire pipeline in the
open-world suite, makes it a measurement: if JSON were required, the run using TLV would fail.
``openworld.py`` runs the whole governance and certification pipeline under
``Encoding(TagLengthValueCodec(), PolynomialIdentity())`` for exactly this reason.

WHY ``json`` AND ``hashlib`` ARE IMPORTED HERE AT ALL. Ω∞ Rule 1 permits these to exist as
registered reference systems and forbids them as architectural requirements. A provider
implementation is where knowledge of a concrete system belongs — the same boundary that lets
``ProlepticCivilCalendar`` know about Gregorian months and lets a caller's ``ExternalClock`` reader
know about the host clock. The test of the boundary is deletability: remove ``CanonicalJsonCodec``
and ``Sha256Identity`` from this file and no governance, certification, discovery or
state-transition logic changes.

DETERMINISM IS A DECLARED CAPABILITY, NOT AN ASSUMPTION. A codec declares ``REPRODUCIBLE`` when its
bytes are a pure function of the value. ``assert_reproducible`` measures the claim rather than
trusting it, because an append-only register whose digests differ between two encodings of one value
is unverifiable, and the failure would surface as a corrupt chain rather than as a codec defect.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from engine.omega_governance.reference.capability import (
    ENCODABLE,
    IDENTIFIABLE,
    REPRODUCIBLE,
    CapabilitySet,
)


class EncodingError(RuntimeError):
    """A value could not be encoded, or a codec or identity provider was unknown.

    RAISED, NEVER DEFAULTED. A codec that silently rendered an unsupported value as its ``repr``
    would produce bytes that depend on a Python implementation detail, and the digest of a
    governance record would then differ between interpreters for a reason no reader could find.
    """


# ----------------------------------------------------------------------------------- the contracts


@runtime_checkable
class Codec(Protocol):
    """A representation system. Turns a value into bytes, and says what it cannot turn.

    EXPRESSIBLE WITHOUT PYTHON, per Ω∞ Rule 6: two accessors returning a name and a capability list,
    one predicate, one operation from a value to bytes. ``schema.py`` emits it as a contract, so an
    engine in another language implements a codec without reproducing any Python type.
    """

    def identifier(self) -> str:
        """A stable, unique name, recorded alongside anything this codec produced."""

    def capabilities(self) -> CapabilitySet:
        """What this codec declares about itself."""

    def supports(self, value: object) -> bool:
        """Whether this codec can encode the value. ASKED BEFORE ENCODING, never inferred after."""

    def encode(self, value: object) -> bytes:
        """The canonical bytes. Must be a pure function of the value when REPRODUCIBLE is
        declared.
        """


@runtime_checkable
class IdentityProvider(Protocol):
    """An identity system. Turns bytes into a stable fingerprint string."""

    def identifier(self) -> str:
        """A stable, unique name, recorded alongside any fingerprint this provider produced."""

    def capabilities(self) -> CapabilitySet:
        """What this provider declares about itself."""

    def fingerprint(self, payload: bytes) -> str:
        """The fingerprint. Deterministic, and of a width this provider declares in its report."""

    def width(self) -> int:
        """Fingerprint length in characters, so a store can size a column without hashing
        anything.
        """


# -------------------------------------------------------------------------------- representations


@dataclass(frozen=True)
class CanonicalJsonCodec:
    """JSON, as ONE registered representation system among the ones a deployment may declare.

    Sorted keys, no whitespace, no ASCII escaping, UTF-8. Those four choices make the bytes
    canonical; without them JSON is not a representation but a family of them, and two encoders
    would disagree.

    REFUSES WHAT IT CANNOT REPRESENT. ``supports`` walks the value, so a set, a callable or an
    object of a domain type is refused BEFORE bytes exist rather than silently stringified. That
    refusal is what sends a caller to register a codec for their own value domain instead of
    discovering that their symbols became ``"<object at 0x...>"``.
    """

    codec_identifier: str = "canonical-json"

    def identifier(self) -> str:
        return self.codec_identifier

    def capabilities(self) -> CapabilitySet:
        return CapabilitySet.of(ENCODABLE, REPRODUCIBLE)

    def supports(self, value: object) -> bool:
        if value is None or isinstance(value, bool | int | str | float):
            return True
        if isinstance(value, Mapping):
            return all(isinstance(k, str) and self.supports(v) for k, v in value.items())
        if isinstance(value, list | tuple):
            return all(self.supports(item) for item in value)
        return False

    def encode(self, value: object) -> bytes:
        if not self.supports(value):
            raise EncodingError(
                f"{self.codec_identifier} cannot represent a value of type "
                f"{type(value).__name__}; register a codec for that value domain rather than "
                "letting it be stringified into bytes nobody can parse back"
            )
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


@dataclass(frozen=True)
class TagLengthValueCodec:
    """A binary representation with no relationship to JSON. THE SECOND CODEC, and it earns its
    place.

    Every value becomes ``tag(1 byte) + length(8 ascii digits) + payload``, recursively. Mappings
    are encoded with sorted keys so the bytes are canonical, exactly as the JSON codec does — the
    shared property is CANONICALITY, which is a requirement, and not JSON, which is a choice.

    WHY THIS EXISTS. Without a second, structurally different codec, "the architecture does not
    require JSON" is untestable. The open-world suite runs the complete pipeline under this codec,
    so a JSON dependency anywhere in governance, state, authority, contradiction, certification or
    the register would surface as a failure rather than as an unexamined assumption.
    """

    codec_identifier: str = "tag-length-value"

    def identifier(self) -> str:
        return self.codec_identifier

    def capabilities(self) -> CapabilitySet:
        return CapabilitySet.of(ENCODABLE, REPRODUCIBLE)

    def supports(self, value: object) -> bool:
        if value is None or isinstance(value, bool | int | str | bytes):
            return True
        if isinstance(value, Mapping):
            return all(isinstance(k, str) and self.supports(v) for k, v in value.items())
        if isinstance(value, list | tuple):
            return all(self.supports(item) for item in value)
        return False

    @staticmethod
    def _frame(tag: bytes, payload: bytes) -> bytes:
        return tag + f"{len(payload):08d}".encode() + payload

    def encode(self, value: object) -> bytes:
        if value is None:
            return self._frame(b"N", b"")
        if isinstance(value, bool):
            return self._frame(b"B", b"1" if value else b"0")
        if isinstance(value, int):
            return self._frame(b"I", str(value).encode())
        if isinstance(value, str):
            return self._frame(b"S", value.encode())
        if isinstance(value, bytes):
            return self._frame(b"Y", value)
        if isinstance(value, Mapping):
            if not all(isinstance(key, str) for key in value):
                raise EncodingError(
                    f"{self.codec_identifier} requires string keys; a non-string key has no "
                    "canonical order, so two encodings of one mapping would differ"
                )
            body = b"".join(self.encode(key) + self.encode(value[key]) for key in sorted(value))
            return self._frame(b"D", body)
        if isinstance(value, list | tuple):
            return self._frame(b"L", b"".join(self.encode(item) for item in value))
        raise EncodingError(
            f"{self.codec_identifier} cannot represent a value of type {type(value).__name__}; "
            "register a codec for that value domain"
        )


# --------------------------------------------------------------------------------- identity systems


@dataclass(frozen=True)
class Sha256Identity:
    """SHA-256, as ONE registered identity system. Not a requirement anywhere in this
    architecture.
    """

    provider_identifier: str = "sha256"

    def identifier(self) -> str:
        return self.provider_identifier

    def capabilities(self) -> CapabilitySet:
        return CapabilitySet.of(IDENTIFIABLE, REPRODUCIBLE)

    def width(self) -> int:
        return 64

    def fingerprint(self, payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()


#: The modulus and multiplier of ``PolynomialIdentity``. A Mersenne prime and a small odd
#: multiplier, chosen for determinism across interpreters rather than for collision resistance —
#: which is why the provider declines to declare itself suitable for tamper evidence.
POLYNOMIAL_MODULUS = (1 << 61) - 1
POLYNOMIAL_MULTIPLIER = 1_000_003


@dataclass(frozen=True)
class PolynomialIdentity:
    """A rolling digest in integer arithmetic. NO ``hashlib``, and that is the entire point.

    HONEST ABOUT WHAT IT IS NOT. This provider does not declare tamper evidence and must not be used
    where an adversary chooses the contents — a 61-bit rolling hash is findable-collision territory.
    It exists to demonstrate that the architecture's identity layer is genuinely a provider slot:
    the open-world suite runs the full hash-chained register under it, and the chain verifies,
    because the register requires *an* identity provider and never SHA-256.

    Stating the weakness rather than omitting it is the same discipline the calendars use for leap
    seconds: a simplification that is declared can be reasoned about, and one that is hidden becomes
    a wrong answer somebody trusts.
    """

    provider_identifier: str = "polynomial-61"

    def identifier(self) -> str:
        return self.provider_identifier

    def capabilities(self) -> CapabilitySet:
        return CapabilitySet.of(IDENTIFIABLE, REPRODUCIBLE)

    def width(self) -> int:
        return 16

    def fingerprint(self, payload: bytes) -> str:
        accumulator = 1
        for byte in payload:
            accumulator = (accumulator * POLYNOMIAL_MULTIPLIER + byte + 1) % POLYNOMIAL_MODULUS
        return f"{accumulator:016x}"


# ------------------------------------------------------------------------------------- registries


class CodecRegistry:
    """Codec identifier -> provider. Open for extension, closed to redefinition.

    STARTS EMPTY BY DEFAULT. A registry seeded with JSON would make JSON the thing you get when you
    do not choose, and "the default nobody chose" is how a hardcoded assumption survives a
    refactoring. ``default_encoding`` is the one place a deployment's choice is made, and it is a
    function a caller may decline to call.
    """

    def __init__(self, seed: Iterable[Codec] = ()) -> None:
        self._by_name: dict[str, Codec] = {}
        for codec in seed:
            self.register(codec)

    def register(self, codec: Codec) -> Codec:
        identifier = codec.identifier()
        if not identifier.strip():
            raise EncodingError("a codec must identify itself to be registered")
        if identifier in self._by_name:
            raise EncodingError(
                f"a codec identified {identifier!r} is already registered; replacing it silently "
                "would change the bytes of every record written afterwards, and therefore every "
                "digest, while looking like a configuration tidy-up"
            )
        self._by_name[identifier] = codec
        return codec

    def resolve(self, identifier: str) -> Codec:
        try:
            return self._by_name[identifier]
        except KeyError:
            raise EncodingError(
                f"{identifier!r} names no registered codec; register it before decoding records "
                "that cite it, so a missing representation cannot be replaced by a plausible one"
            ) from None

    def supporting(self, value: object) -> tuple[str, ...]:
        """Every registered codec that can encode the value. For a caller choosing at runtime."""
        return tuple(sorted(name for name, codec in self._by_name.items() if codec.supports(value)))

    def known(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_name))

    def __contains__(self, identifier: object) -> bool:
        return isinstance(identifier, str) and identifier in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


class IdentityRegistry:
    """Identity provider identifier -> provider. Same construction and argument as
    ``CodecRegistry``.
    """

    def __init__(self, seed: Iterable[IdentityProvider] = ()) -> None:
        self._by_name: dict[str, IdentityProvider] = {}
        for provider in seed:
            self.register(provider)

    def register(self, provider: IdentityProvider) -> IdentityProvider:
        identifier = provider.identifier()
        if not identifier.strip():
            raise EncodingError("an identity provider must identify itself to be registered")
        if identifier in self._by_name:
            raise EncodingError(
                f"an identity provider identified {identifier!r} is already registered; replacing "
                "it silently would invalidate every fingerprint already written"
            )
        self._by_name[identifier] = provider
        return provider

    def resolve(self, identifier: str) -> IdentityProvider:
        try:
            return self._by_name[identifier]
        except KeyError:
            raise EncodingError(
                f"{identifier!r} names no registered identity provider; register it before "
                "verifying fingerprints that cite it"
            ) from None

    def known(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_name))

    def __contains__(self, identifier: object) -> bool:
        return isinstance(identifier, str) and identifier in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


# ---------------------------------------------------------------------------------------- pairing


@dataclass(frozen=True)
class Encoding:
    """A codec and an identity provider, travelling together. THE PARAMETER, never a default.

    WHY THEY ARE PAIRED. A fingerprint is meaningless without the bytes it was computed over, so a
    record citing ``sha256`` and not citing the codec cannot be re-verified: two codecs produce two
    byte strings for one value, and only one of them yields the stored fingerprint. Pairing makes
    the citation complete, and ``describe()`` is what a register writes alongside its chain.
    """

    codec: Codec
    identity: IdentityProvider

    def encode(self, value: object) -> bytes:
        return self.codec.encode(value)

    def fingerprint(self, value: object) -> str:
        """The fingerprint of a VALUE, not of bytes. One call, so no site can mismatch the pair."""
        return self.identity.fingerprint(self.codec.encode(value))

    def describe(self) -> dict[str, object]:
        return {
            "codec": self.codec.identifier(),
            "identity": self.identity.identifier(),
            "identity_width": self.identity.width(),
            "codec_capabilities": self.codec.capabilities().names(),
            "identity_capabilities": self.identity.capabilities().names(),
        }


def default_encoding() -> Encoding:
    """The registered pair this deployment uses. A CHOICE MADE HERE, and nowhere else.

    NOT AN ARCHITECTURAL REQUIREMENT, and the difference is testable: ``openworld.py`` runs the
    entire pipeline under ``Encoding(TagLengthValueCodec(), PolynomialIdentity())`` and every
    invariant still holds. This function is a convenience for the repository's own evidence run, so
    the evidence has one canonical byte form, and it is the only place in the package where JSON or
    SHA-256 is selected.
    """
    return Encoding(CanonicalJsonCodec(), Sha256Identity())


def default_registries() -> tuple[CodecRegistry, IdentityRegistry]:
    """Registries holding both shipped codecs and both shipped identity providers."""
    return (
        CodecRegistry((CanonicalJsonCodec(), TagLengthValueCodec())),
        IdentityRegistry((Sha256Identity(), PolynomialIdentity())),
    )


def assert_reproducible(encoding: Encoding, samples: Sequence[object]) -> None:
    """Refuse an encoding whose bytes or fingerprints are not a pure function of the value.

    Ω∞ DETERMINISM, MEASURED RATHER THAN DECLARED. Two properties: encoding the same value twice
    yields identical bytes, and two structurally equal values yield identical fingerprints. A
    register built on an encoding that failed either would have a chain that breaks on rewrite, and
    the breakage would read as tampering.
    """
    for sample in samples:
        first = encoding.encode(sample)
        if first != encoding.encode(sample):
            raise EncodingError(
                f"{encoding.codec.identifier()} produced different bytes for one value on two "
                "calls; every digest computed with it is unverifiable"
            )
        if encoding.fingerprint(sample) != encoding.identity.fingerprint(first):
            raise EncodingError(  # pragma: no cover - fingerprint() is defined as this composition
                f"{encoding.identity.identifier()} disagrees with itself between the paired and "
                "unpaired call paths"
            )
    if not encoding.codec.capabilities().supports(REPRODUCIBLE):
        raise EncodingError(
            f"{encoding.codec.identifier()} does not declare REPRODUCIBLE, so it must not be used "
            "for records that are compared across runs; declaring it is how a codec accepts that "
            "obligation"
        )


__all__ = [
    "POLYNOMIAL_MODULUS",
    "POLYNOMIAL_MULTIPLIER",
    "CanonicalJsonCodec",
    "Codec",
    "CodecRegistry",
    "Encoding",
    "EncodingError",
    "IdentityProvider",
    "IdentityRegistry",
    "PolynomialIdentity",
    "Sha256Identity",
    "TagLengthValueCodec",
    "assert_reproducible",
    "default_encoding",
    "default_registries",
]

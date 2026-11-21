"""EC3-B10-U01 — The Universal Datum construct (DMC-01).

Realizes the meta-model root concept **DMC-01 Datum** (DATA-005 §2; DATA-001 §2.1):

    the atomic unit of representation — a typed value (ENG-003) borne by an object
    (ENG-002), identified (ENG-001), classified (ENG-004).

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it *by
reference* (UDL-02 / DMI-05): identity and value-fidelity are derived through the
EC-1 certified deterministic encoding (:func:`engine.certification.contracts.canonical_json`
/ :func:`~engine.certification.contracts.content_hash`) — the same discipline that
produces every EC-1 runtime, artifact, and certification identity — so this module
introduces **no second identity scheme and no parallel value model**. It selects no
storage technology (UDL-11) and confers no authority (UDL-15).

A :class:`Datum` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001 via a deterministic id), *value-carrying*
(ENG-003), *classified* (DXH-01 kind), and holds a *forward-only lifecycle state*
(DOS-01…05, UDL-12). Constructing a :class:`Datum` enforces the meta-constraints
DMK-01/02 and the laws UDL-03/04/05/06 fail-closed: an ill-formed datum cannot be
instantiated.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from data.meta import (
    DATUM_META_CLASS,
    DATUM_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    DatumKind,
    DatumState,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined -------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Datum (mirrors EC-1 UCOS-<KIND>-<hex16>).
DATUM_ID_PREFIX = "UCOS-DATUM"

#: The map of EC-1 EL-1 primitives this construct reuses *by reference* (never
#: redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
EL1_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the datum)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity, no parallel model)",
    "ENG-004": "data.meta.DatumKind + type_tag (ENG-004 typing discipline, by reference)",
}

#: Conservative secret markers used to enforce UDL-15 / RR-07 (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "privatekey",
    "api_key",
    "apikey",
    "access_token",
    "credential",
    "-----begin",
)


class DatumError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`Datum`.

    A :class:`Datum` is fail-closed (TRACK-001): ill-formed representation is
    rejected at construction rather than admitted as an invalid datum.
    """


def _ensure_value_fidelity(value: Any) -> None:
    """Reuse ENG-003 (via EC-1 canonical encoding) to prove value fidelity (UDL-06).

    A datum's value must round-trip through the CERTIFIED EC-1 canonical encoding.
    A circular or non-encodable value cannot be a datum (also guarantees founding
    acyclicity, DMK-03 / V4).
    """
    try:
        canonical_json(value)
    except (TypeError, ValueError) as exc:  # circular ref or non-serializable
        raise DatumError(f"value is not ENG-003 value-faithful (UDL-06): {exc}") from exc


@dataclass(frozen=True, slots=True)
class Datum:
    """DMC-01 — an immutable, typed, identified, value-carrying atomic datum.

    Fields:
        type_tag: the ENG-004 Type of the datum (decidable, non-empty) — UDL-03.
        kind:     the DXH-01 classification of the datum (DMR-09 classified-by).
        value:    the ENG-003 Value the datum carries (value-faithful) — UDL-06.
        state:    the DOS-01…05 lifecycle state (forward-only) — UDL-12 (default DEFINED).
    """

    type_tag: str
    kind: DatumKind
    value: Any
    state: DatumState = DatumState.DEFINED
    #: Optional provenance references for a Derived-Datum (DMG-03); identity is
    #: *referenced, not absorbed* (DMX-02). Empty for primitive/composite data.
    derived_from: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        # DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise DatumError("datum must be typed with a non-empty ENG-004 type_tag (UDL-03)")
        # DMR-09 / DXH-01 — classified by exactly one Datum kind.
        if not isinstance(self.kind, DatumKind):
            raise DatumError("datum kind must be a DXH-01 DatumKind (DMR-09)")
        # DMK-02 / UDL-06 — value fidelity via ENG-003 (EC-1 canonical encoding).
        _ensure_value_fidelity(self.value)
        # V5 / UDL-12 — a valid lifecycle state.
        if not isinstance(self.state, DatumState):
            raise DatumError("datum state must be a DOS-01…05 DatumState (UDL-12)")
        # DMG-03 — a Derived-Datum records provenance; others carry none.
        if self.kind is DatumKind.DERIVED:
            if not self.derived_from:
                raise DatumError("a Derived-Datum must record its provenance (DMG-03)")
        elif self.derived_from:
            raise DatumError("only a Derived-Datum may declare derived_from (DMG-03)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the datum (the ENG-003 value + its type)."""
        return {
            "meta_class": DATUM_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "value": self.value,
            "derived_from": list(self.derived_from),
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the datum core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def datum_id(self) -> str:
        """The deterministic ENG-001 identity of the datum (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second
        identity scheme): identical (type, kind, value) always yields the identical
        id, so identity is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{DATUM_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (DATA-005) -----------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-01)."""
        return DATUM_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the datum participates in."""
        return DATUM_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 — the founding graph is acyclic.

        A datum is atomic; its value graph is proven acyclic by the fact that it
        successfully canonically encodes (a cycle raises at construction).
        """
        try:
            canonical_json(self.value)
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    # -- non-constitutiveness (UDL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UDL-15 / C7 — a datum confers no authority (structurally has none)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / RR-07 / C7 — True iff the datum appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — a datum redefines no EL-1 primitive (reuse-only)."""
        return False

    # -- lifecycle (UDL-12, forward-only) --------------------------------------

    def transition(self, to_state: DatumState) -> Datum:
        """Return a new datum advanced to ``to_state`` (forward-only; UDL-12).

        Raises:
            DatumError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, DatumState):
            raise DatumError("target state must be a DOS-01…05 DatumState (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise DatumError(
                f"lifecycle is forward-only (UDL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the datum."""
        return {
            "datum_id": self.datum_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "value": self.value,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "derived_from": list(self.derived_from),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_datum(
    type_tag: str,
    value: Any,
    *,
    kind: DatumKind = DatumKind.PRIMITIVE,
    state: DatumState = DatumState.DEFINED,
    derived_from: tuple[str, ...] = (),
) -> Datum:
    """Construct a well-formed :class:`Datum` (fail-closed factory)."""
    return Datum(
        type_tag=type_tag,
        kind=kind,
        value=value,
        state=state,
        derived_from=tuple(derived_from),
    )


__all__ = [
    "DATUM_ID_PREFIX",
    "EL1_REUSE",
    "DatumError",
    "Datum",
    "make_datum",
]
